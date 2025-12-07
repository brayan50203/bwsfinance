"""
Notifications API Routes
Endpoints REST para gerenciar notificações

Endpoints:
- GET /api/notifications - Lista notificações (paginação)
- POST /api/notifications/send - Força envio de notificação
- PATCH /api/notifications/<id>/read - Marca como lida
- GET /api/notifications/health - Health check
- GET /api/notifications/settings - Preferências do usuário
- PUT /api/notifications/settings - Atualiza preferências
"""

from flask import Blueprint, request, jsonify, session
from datetime import datetime
import sqlite3
import json
import logging

# Importar service
from services.auto_notifications import notification_service

logger = logging.getLogger('notifications.routes')

# Blueprint
notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')


def get_db():
    """Retorna conexão com banco"""
    return sqlite3.connect('bws_finance.db')


def require_auth(f):
    """Decorator para exigir autenticação"""
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Não autenticado'}), 401
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


@notifications_bp.route('/', methods=['GET'])
@require_auth
def list_notifications():
    """
    Lista notificações do usuário
    
    Query params:
        - page: Página (default: 1)
        - per_page: Itens por página (default: 20)
        - status: Filtrar por status (pending, sent, failed, read)
        - event_type: Filtrar por tipo
    
    Returns:
        {
            "notifications": [...],
            "total": int,
            "page": int,
            "per_page": int,
            "pages": int
        }
    """
    user_id = session.get('user_id')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    status = request.args.get('status')
    event_type = request.args.get('event_type')
    
    db = get_db()
    cursor = db.cursor()
    
    # Query base
    query = """
        SELECT id, user_id, title, message, event_type, channel,
               priority, status, meta, created_at, sent_at, read_at
        FROM notifications
        WHERE user_id = ?
    """
    params = [user_id]
    
    # Filtros
    if status:
        query += " AND status = ?"
        params.append(status)
    
    if event_type:
        query += " AND event_type = ?"
        params.append(event_type)
    
    # Contar total
    count_query = query.replace(
        "SELECT id, user_id, title, message, event_type, channel, priority, status, meta, created_at, sent_at, read_at",
        "SELECT COUNT(*)"
    )
    cursor.execute(count_query, params)
    total = cursor.fetchone()[0]
    
    # Paginação
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([per_page, (page - 1) * per_page])
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    notifications = []
    for row in rows:
        notifications.append({
            'id': row[0],
            'user_id': row[1],
            'title': row[2],
            'message': row[3],
            'event_type': row[4],
            'channel': row[5],
            'priority': row[6],
            'status': row[7],
            'meta': json.loads(row[8]) if row[8] else None,
            'created_at': row[9],
            'sent_at': row[10],
            'read_at': row[11]
        })
    
    db.close()
    
    pages = (total + per_page - 1) // per_page
    
    return jsonify({
        'notifications': notifications,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': pages
    })


@notifications_bp.route('/send', methods=['POST'])
@require_auth
def force_send():
    """
    Força envio de notificação
    
    Body (JSON):
        {
            "user_id": "uuid",  # opcional, usa sessão se omitido
            "event_type": "invoice_due_soon",
            "channel": "whatsapp|email|both",
            "params": {
                "card_name": "Nubank",
                "amount": "1240.50",
                "due_date": "2025-11-12",
                "days": 3
            }
        }
    
    Returns:
        {"success": bool, "notification_id": int, "message": str}
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Body JSON obrigatório'}), 400
    
    # Validações
    event_type = data.get('event_type')
    if not event_type:
        return jsonify({'error': 'event_type obrigatório'}), 400
    
    user_id = data.get('user_id', session.get('user_id'))
    channel = data.get('channel', 'both')
    params = data.get('params', {})
    
    # Buscar tenant_id do usuário
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT tenant_id, name FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    
    if not row:
        db.close()
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    tenant_id, user_name = row
    db.close()
    
    # Templates de mensagens
    templates = {
        'invoice_due_soon': {
            'title': f"Fatura {params.get('card_name', 'cartão')} vence em {params.get('days', '?')} dias",
            'message': (
                f"🚨 Olá! Sua fatura do cartão *{params.get('card_name', 'seu cartão')}* "
                f"vence em *{params.get('days', '?')} dias* (R$ {params.get('amount', '0.00')}).\n\n"
                f"Deseja registrar o pagamento agora? Responda 'Sim' para marcar como pago."
            )
        },
        'monthly_spending_summary': {
            'title': 'Resumo Mensal de Gastos',
            'message': (
                f"📊 *Resumo Mensal*\n\n"
                f"Você gastou *R$ {params.get('current_total', '0.00')}* este mês.\n\n"
                f"🏆 Top 3 categorias:\n{chr(10).join(params.get('top3', []))}\n\n"
                f"📈 Variação vs mês anterior: {params.get('variation', 0):+.1f}%"
            )
        },
        'investment_alert': {
            'title': f"Alerta: {params.get('symbol', 'Ativo')} variou {params.get('percent', 0):.2f}%",
            'message': (
                f"📈 Seu ativo *{params.get('symbol', 'N/A')}* teve variação de "
                f"*{params.get('percent', 0):+.2f}%* nas últimas 24h.\n"
                f"💰 Valor atual: R$ {params.get('value', 0):.2f}\n\n"
                f"Quer ver detalhes? Acesse o painel: http://localhost:5000/investments"
            )
        },
        'low_balance': {
            'title': f"Saldo baixo: {params.get('account_name', 'conta')}",
            'message': (
                f"⚠️ *Saldo Baixo*\n\n"
                f"Sua conta *{params.get('account_name', 'N/A')}* está com "
                f"R$ {params.get('balance', 0):.2f} (abaixo do limite de R$ {params.get('threshold', 0):.2f}).\n\n"
                f"Deseja transferir fundos?"
            )
        },
        'import_confirmation': {
            'title': f"Importação concluída: {params.get('count', 0)} transações",
            'message': (
                f"✅ Importação concluída!\n\n"
                f"{params.get('count', 0)} transações foram importadas automaticamente "
                f"para sua conta *{params.get('account_name', 'N/A')}*.\n\n"
                f"Confira no painel: http://localhost:5000/dashboard"
            )
        }
    }
    
    template = templates.get(event_type)
    if not template:
        return jsonify({'error': f'Template para event_type "{event_type}" não encontrado'}), 400
    
    try:
        # Criar notificação
        notification_id = notification_service.create_notification(
            user_id=user_id,
            tenant_id=tenant_id,
            title=template['title'],
            message=template['message'],
            event_type=event_type,
            channel=channel,
            priority='medium',
            meta=params
        )
        
        # Enviar imediatamente
        success = notification_service.send_notification(notification_id)
        
        return jsonify({
            'success': success,
            'notification_id': notification_id,
            'message': 'Notificação enviada' if success else 'Falha ao enviar notificação'
        }), 200 if success else 500
        
    except Exception as e:
        logger.error(f"Erro ao forçar envio: {str(e)}")
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/<int:notification_id>/read', methods=['PATCH'])
@require_auth
def mark_as_read(notification_id):
    """
    Marca notificação como lida
    
    Args:
        notification_id: ID da notificação
    
    Returns:
        {"success": bool, "message": str}
    """
    user_id = session.get('user_id')
    
    db = get_db()
    cursor = db.cursor()
    
    # Verificar se notificação existe e pertence ao usuário
    cursor.execute("""
        SELECT id, status FROM notifications
        WHERE id = ? AND user_id = ?
    """, (notification_id, user_id))
    
    row = cursor.fetchone()
    
    if not row:
        db.close()
        return jsonify({'error': 'Notificação não encontrada'}), 404
    
    # Atualizar
    cursor.execute("""
        UPDATE notifications
        SET status = 'read', read_at = ?
        WHERE id = ?
    """, (datetime.now(), notification_id))
    
    db.commit()
    db.close()
    
    return jsonify({
        'success': True,
        'message': 'Notificação marcada como lida'
    })


@notifications_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check do serviço de notificações
    
    Returns:
        {
            "status": "healthy",
            "scheduler_running": bool,
            "jobs_count": int,
            "whatsapp_available": bool,
            "email_available": bool
        }
    """
    from services.whatsapp_sender import whatsapp_sender
    from services.email_sender import email_sender
    
    is_running = notification_service.scheduler.running if notification_service.scheduler else False
    jobs = notification_service.scheduler.get_jobs() if is_running else []
    
    return jsonify({
        'status': 'healthy',
        'scheduler_running': is_running,
        'jobs_count': len(jobs),
        'jobs': [{'name': j.name, 'next_run': str(j.next_run_time)} for j in jobs],
        'whatsapp_available': whatsapp_sender is not None,
        'email_available': email_sender is not None
    })


@notifications_bp.route('/settings', methods=['GET'])
@require_auth
def get_settings():
    """
    Busca preferências de notificação do usuário
    
    Returns:
        {"settings": {...}}
    """
    user_id = session.get('user_id')
    settings = notification_service.get_user_settings(user_id)
    
    return jsonify({'settings': settings})


@notifications_bp.route('/settings', methods=['PUT'])
@require_auth
def update_settings():
    """
    Atualiza preferências de notificação
    
    Body (JSON):
        {
            "notify_whatsapp": true,
            "notify_email": true,
            "threshold_low_balance": 100.00,
            "investment_alert_pct": 3.0,
            "do_not_disturb_start": "22:00",
            "do_not_disturb_end": "07:00",
            "invoice_alert_days": "3,1,0",
            "opt_in_whatsapp": true,
            "opt_in_email": true
        }
    
    Returns:
        {"success": bool, "message": str}
    """
    user_id = session.get('user_id')
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Body JSON obrigatório'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    # Buscar tenant_id
    cursor.execute("SELECT tenant_id FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    tenant_id = row[0] if row else None
    
    # Verificar se já existe registro
    cursor.execute("SELECT id FROM user_notifications_settings WHERE user_id = ?", (user_id,))
    exists = cursor.fetchone()
    
    if exists:
        # Update
        cursor.execute("""
            UPDATE user_notifications_settings
            SET notify_whatsapp = ?,
                notify_email = ?,
                notify_dashboard = ?,
                threshold_low_balance = ?,
                investment_alert_pct = ?,
                do_not_disturb_start = ?,
                do_not_disturb_end = ?,
                invoice_alert_days = ?,
                weekly_summary = ?,
                monthly_summary = ?,
                opt_in_whatsapp = ?,
                opt_in_email = ?,
                updated_at = ?
            WHERE user_id = ?
        """, (
            data.get('notify_whatsapp', 1),
            data.get('notify_email', 1),
            data.get('notify_dashboard', 1),
            data.get('threshold_low_balance', 100.00),
            data.get('investment_alert_pct', 3.0),
            data.get('do_not_disturb_start'),
            data.get('do_not_disturb_end'),
            data.get('invoice_alert_days', '3,1,0'),
            data.get('weekly_summary', 1),
            data.get('monthly_summary', 1),
            data.get('opt_in_whatsapp', 0),
            data.get('opt_in_email', 0),
            datetime.now(),
            user_id
        ))
    else:
        # Insert
        cursor.execute("""
            INSERT INTO user_notifications_settings (
                user_id, tenant_id,
                notify_whatsapp, notify_email, notify_dashboard,
                threshold_low_balance, investment_alert_pct,
                do_not_disturb_start, do_not_disturb_end,
                invoice_alert_days, weekly_summary, monthly_summary,
                opt_in_whatsapp, opt_in_email,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, tenant_id,
            data.get('notify_whatsapp', 1),
            data.get('notify_email', 1),
            data.get('notify_dashboard', 1),
            data.get('threshold_low_balance', 100.00),
            data.get('investment_alert_pct', 3.0),
            data.get('do_not_disturb_start'),
            data.get('do_not_disturb_end'),
            data.get('invoice_alert_days', '3,1,0'),
            data.get('weekly_summary', 1),
            data.get('monthly_summary', 1),
            data.get('opt_in_whatsapp', 0),
            data.get('opt_in_email', 0),
            datetime.now(),
            datetime.now()
        ))
    
    db.commit()
    db.close()
    
    return jsonify({
        'success': True,
        'message': 'Preferências atualizadas com sucesso'
    })


@notifications_bp.route('/run-job/<job_name>', methods=['POST'])
@require_auth
def run_job_manual(job_name):
    """
    Executa job do scheduler manualmente (para testes)
    
    Args:
        job_name: Nome do job (check_due_invoices, check_monthly_spending, etc.)
    
    Returns:
        {"success": bool, "message": str}
    """
    valid_jobs = [
        'check_due_invoices',
        'check_monthly_spending',
        'check_investment_updates',
        'check_low_balance',
        'send_periodic_reports'
    ]
    
    if job_name not in valid_jobs:
        return jsonify({
            'error': f'Job inválido. Válidos: {", ".join(valid_jobs)}'
        }), 400
    
    try:
        notification_service.run_job_now(job_name)
        return jsonify({
            'success': True,
            'message': f'Job {job_name} executado com sucesso'
        })
    except Exception as e:
        logger.error(f"Erro ao executar job {job_name}: {str(e)}")
        return jsonify({'error': str(e)}), 500
