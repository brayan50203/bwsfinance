"""
MÓDULO DE TRANSAÇÕES RECORRENTES
API REST para gerenciar transações automáticas (salário, aluguel, assinaturas, etc)
"""

from flask import Blueprint, request, jsonify, session
import sqlite3
import uuid
from datetime import datetime, timedelta
from functools import wraps

recurring_bp = Blueprint('recurring', __name__, url_prefix='/api/recurring')

# =====================================================
# HELPERS
# =====================================================

def get_db():
    """Conecta ao banco de dados"""
    db = sqlite3.connect('bws_finance.db')
    db.row_factory = sqlite3.Row
    return db

def require_auth(f):
    """Decorator para exigir autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Buscar user_id da sessão ou query string (para testes)
        user_id = session.get('user_id') or request.args.get('user_id')
        tenant_id = session.get('tenant_id') or request.args.get('tenant_id')
        
        if not user_id:
            return jsonify({'error': 'Authentication required', 'code': 'AUTH_REQUIRED'}), 401
        
        # Injetar no request context
        request.user_id = user_id
        request.tenant_id = tenant_id
        
        return f(*args, **kwargs)
    return decorated_function

# =====================================================
# CRUD DE TRANSAÇÕES RECORRENTES
# =====================================================

@recurring_bp.route('', methods=['GET'])
@require_auth
def list_recurring():
    """
    Lista todas as transações recorrentes do usuário
    
    Query params:
    - status: active|inactive (opcional)
    - type: Receita|Despesa (opcional)
    """
    db = get_db()
    
    # Filtros
    status_filter = request.args.get('status')
    type_filter = request.args.get('type')
    
    query = """
        SELECT 
            r.*,
            a.name as account_name,
            cr.name as card_name,
            c.name as category_name,
            c.icon as category_icon,
            c.color as category_color
        FROM recurring_transactions r
        LEFT JOIN accounts a ON r.account_id = a.id
        LEFT JOIN cards cr ON r.card_id = cr.id
        LEFT JOIN categories c ON r.category_id = c.id
        WHERE r.user_id = ? AND r.tenant_id = ?
    """
    
    params = [request.user_id, request.tenant_id]
    
    if status_filter:
        query += " AND r.active = ?"
        params.append(1 if status_filter == 'active' else 0)
    
    if type_filter:
        query += " AND r.type = ?"
        params.append(type_filter)
    
    query += " ORDER BY r.next_execution DESC"
    
    recurrings = db.execute(query, params).fetchall()
    db.close()
    
    return jsonify({
        'success': True,
        'data': [dict(r) for r in recurrings],
        'count': len(recurrings)
    })

@recurring_bp.route('/<recurring_id>', methods=['GET'])
@require_auth
def get_recurring(recurring_id):
    """Busca uma transação recorrente específica"""
    db = get_db()
    
    recurring = db.execute("""
        SELECT 
            r.*,
            a.name as account_name,
            c.name as category_name
        FROM recurring_transactions r
        LEFT JOIN accounts a ON r.account_id = a.id
        LEFT JOIN categories c ON r.category_id = c.id
        WHERE r.id = ? AND r.user_id = ? AND r.tenant_id = ?
    """, (recurring_id, request.user_id, request.tenant_id)).fetchone()
    
    db.close()
    
    if not recurring:
        return jsonify({'error': 'Recurring transaction not found', 'code': 'NOT_FOUND'}), 404
    
    return jsonify({
        'success': True,
        'data': dict(recurring)
    })

@recurring_bp.route('', methods=['POST'])
@require_auth
def create_recurring():
    """
    Cria nova transação recorrente
    
    Body (JSON):
    {
        "account_id": "uuid",
        "category_id": "uuid",
        "type": "Receita|Despesa",
        "description": "string",
        "value": float,
        "frequency": "daily|weekly|monthly|yearly",
        "day_of_execution": int (1-31 para mensal, 1-7 para semanal),
        "start_date": "YYYY-MM-DD",
        "end_date": "YYYY-MM-DD" (opcional)
    }
    """
    data = request.get_json()
    
    # Validações
    required_fields = ['account_id', 'type', 'description', 'value', 'frequency', 'day_of_execution', 'start_date']
    missing_fields = [f for f in required_fields if f not in data]
    
    if missing_fields:
        return jsonify({
            'error': f'Missing required fields: {", ".join(missing_fields)}',
            'code': 'VALIDATION_ERROR'
        }), 400
    
    # Validar tipo
    if data['type'] not in ['Receita', 'Despesa']:
        return jsonify({'error': 'Type must be Receita or Despesa', 'code': 'INVALID_TYPE'}), 400
    
    # Validar frequência
    valid_frequencies = ['daily', 'weekly', 'monthly', 'yearly']
    if data['frequency'] not in valid_frequencies:
        return jsonify({
            'error': f'Frequency must be one of: {", ".join(valid_frequencies)}',
            'code': 'INVALID_FREQUENCY'
        }), 400
    
    # Validar valor
    try:
        value = float(data['value'])
        if value <= 0:
            raise ValueError()
    except:
        return jsonify({'error': 'Value must be a positive number', 'code': 'INVALID_VALUE'}), 400
    
    # Validar conta OU cartão pertence ao usuário
    db = get_db()
    
    account_id = data.get('account_id')
    card_id = data.get('card_id')
    
    if not account_id and not card_id:
        db.close()
        return jsonify({'error': 'Either account_id or card_id is required', 'code': 'VALIDATION_ERROR'}), 400
    
    if account_id:
        account = db.execute(
            "SELECT id FROM accounts WHERE id = ? AND user_id = ? AND tenant_id = ?",
            (account_id, request.user_id, request.tenant_id)
        ).fetchone()
        
        if not account:
            db.close()
            return jsonify({'error': 'Account not found or not owned by user', 'code': 'INVALID_ACCOUNT'}), 404
    
    if card_id:
        card = db.execute(
            "SELECT id FROM cards WHERE id = ? AND user_id = ? AND tenant_id = ?",
            (card_id, request.user_id, request.tenant_id)
        ).fetchone()
        
        if not card:
            db.close()
            return jsonify({'error': 'Card not found or not owned by user', 'code': 'INVALID_CARD'}), 404
    
    # Calcular next_execution
    start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
    next_execution = calculate_next_execution(start_date, data['frequency'], data['day_of_execution'])
    
    # Criar recorrência
    recurring_id = str(uuid.uuid4())
    
    db.execute("""
        INSERT INTO recurring_transactions (
            id, user_id, tenant_id, account_id, card_id, category_id,
            type, description, value, frequency, day_of_execution,
            start_date, end_date, next_execution, active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, (
        recurring_id,
        request.user_id,
        request.tenant_id,
        data.get('account_id'),
        data.get('card_id'),
        data.get('category_id'),
        data['type'],
        data['description'],
        value,
        data['frequency'],
        data['day_of_execution'],
        data['start_date'],
        data.get('end_date'),
        next_execution.strftime('%Y-%m-%d')
    ))
    
    db.commit()
    db.close()
    
    return jsonify({
        'success': True,
        'message': 'Recurring transaction created successfully',
        'data': {
            'id': recurring_id,
            'next_execution': next_execution.strftime('%Y-%m-%d')
        }
    }), 201

@recurring_bp.route('/<recurring_id>', methods=['PUT'])
@require_auth
def update_recurring(recurring_id):
    """
    Atualiza transação recorrente
    
    Campos editáveis:
    - description, value, frequency, day_of_execution, end_date
    """
    data = request.get_json()
    
    db = get_db()
    
    # Verificar se existe e pertence ao usuário
    recurring = db.execute(
        "SELECT * FROM recurring_transactions WHERE id = ? AND user_id = ? AND tenant_id = ?",
        (recurring_id, request.user_id, request.tenant_id)
    ).fetchone()
    
    if not recurring:
        db.close()
        return jsonify({'error': 'Recurring transaction not found', 'code': 'NOT_FOUND'}), 404
    
    # Construir UPDATE dinâmico
    update_fields = []
    params = []
    
    if 'description' in data:
        update_fields.append("description = ?")
        params.append(data['description'])
    
    if 'value' in data:
        try:
            value = float(data['value'])
            if value <= 0:
                raise ValueError()
            update_fields.append("value = ?")
            params.append(value)
        except:
            db.close()
            return jsonify({'error': 'Value must be a positive number', 'code': 'INVALID_VALUE'}), 400
    
    if 'frequency' in data:
        if data['frequency'] not in ['daily', 'weekly', 'monthly', 'yearly']:
            db.close()
            return jsonify({'error': 'Invalid frequency', 'code': 'INVALID_FREQUENCY'}), 400
        update_fields.append("frequency = ?")
        params.append(data['frequency'])
    
    if 'day_of_execution' in data:
        update_fields.append("day_of_execution = ?")
        params.append(data['day_of_execution'])
    
    if 'end_date' in data:
        update_fields.append("end_date = ?")
        params.append(data['end_date'])
    
    if not update_fields:
        db.close()
        return jsonify({'error': 'No fields to update', 'code': 'NO_CHANGES'}), 400
    
    # Recalcular next_execution se frequência ou dia mudou
    if 'frequency' in data or 'day_of_execution' in data:
        start_date = datetime.strptime(recurring['start_date'], '%Y-%m-%d')
        frequency = data.get('frequency', recurring['frequency'])
        day = data.get('day_of_execution', recurring['day_of_execution'])
        next_exec = calculate_next_execution(start_date, frequency, day)
        
        update_fields.append("next_execution = ?")
        params.append(next_exec.strftime('%Y-%m-%d'))
    
    # Executar UPDATE
    update_fields.append("updated_at = CURRENT_TIMESTAMP")
    params.extend([recurring_id, request.user_id, request.tenant_id])
    
    query = f"UPDATE recurring_transactions SET {', '.join(update_fields)} WHERE id = ? AND user_id = ? AND tenant_id = ?"
    
    db.execute(query, params)
    db.commit()
    db.close()
    
    return jsonify({
        'success': True,
        'message': 'Recurring transaction updated successfully'
    })

@recurring_bp.route('/<recurring_id>', methods=['DELETE'])
@require_auth
def delete_recurring(recurring_id):
    """Desativa transação recorrente (soft delete)"""
    db = get_db()
    
    # Verificar se existe
    recurring = db.execute(
        "SELECT id FROM recurring_transactions WHERE id = ? AND user_id = ? AND tenant_id = ?",
        (recurring_id, request.user_id, request.tenant_id)
    ).fetchone()
    
    if not recurring:
        db.close()
        return jsonify({'error': 'Recurring transaction not found', 'code': 'NOT_FOUND'}), 404
    
    # Soft delete
    db.execute(
        "UPDATE recurring_transactions SET active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (recurring_id,)
    )
    
    db.commit()
    db.close()
    
    return jsonify({
        'success': True,
        'message': 'Recurring transaction deactivated successfully'
    }), 204

@recurring_bp.route('/<recurring_id>/activate', methods=['POST'])
@require_auth
def activate_recurring(recurring_id):
    """Reativa transação recorrente"""
    db = get_db()
    
    recurring = db.execute(
        "SELECT id FROM recurring_transactions WHERE id = ? AND user_id = ? AND tenant_id = ?",
        (recurring_id, request.user_id, request.tenant_id)
    ).fetchone()
    
    if not recurring:
        db.close()
        return jsonify({'error': 'Recurring transaction not found', 'code': 'NOT_FOUND'}), 404
    
    db.execute(
        "UPDATE recurring_transactions SET active = 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (recurring_id,)
    )
    
    db.commit()
    db.close()
    
    return jsonify({
        'success': True,
        'message': 'Recurring transaction activated successfully'
    })

# =====================================================
# LÓGICA DE EXECUÇÃO AUTOMÁTICA
# =====================================================

def calculate_next_execution(start_date, frequency, day_of_execution):
    """
    Calcula próxima data de execução baseado na frequência
    
    Args:
        start_date: Data inicial
        frequency: daily|weekly|monthly|yearly
        day_of_execution: Dia específico (1-31 para mensal, 1-7 para semanal)
    
    Returns:
        datetime object
    """
    today = datetime.now().date()
    
    if frequency == 'daily':
        # Próximo dia
        next_date = today + timedelta(days=1)
    
    elif frequency == 'weekly':
        # Próximo dia da semana (1=Segunda, 7=Domingo)
        days_ahead = day_of_execution - today.isoweekday()
        if days_ahead <= 0:
            days_ahead += 7
        next_date = today + timedelta(days=days_ahead)
    
    elif frequency == 'monthly':
        # Próximo dia do mês
        next_month = today.month + 1 if today.month < 12 else 1
        next_year = today.year if today.month < 12 else today.year + 1
        
        # Ajustar para último dia do mês se necessário
        import calendar
        max_day = calendar.monthrange(next_year, next_month)[1]
        day = min(day_of_execution, max_day)
        
        next_date = datetime(next_year, next_month, day).date()
    
    elif frequency == 'yearly':
        # Mesmo dia, próximo ano
        next_date = datetime(today.year + 1, start_date.month, start_date.day).date()
    
    else:
        next_date = today
    
    return datetime.combine(next_date, datetime.min.time())

def execute_recurring_transactions():
    """
    Processa todas as transações recorrentes que devem ser executadas hoje
    
    Chamado pelo agendador (APScheduler)
    """
    db = get_db()
    today = datetime.now().date().strftime('%Y-%m-%d')
    
    # Buscar recorrências para executar hoje
    recurrings = db.execute("""
        SELECT * FROM recurring_transactions
        WHERE active = 1
        AND next_execution <= ?
        AND (end_date IS NULL OR end_date >= ?)
    """, (today, today)).fetchall()
    
    executed_count = 0
    
    for recurring in recurrings:
        try:
            # Criar transação
            transaction_id = str(uuid.uuid4())
            
            db.execute("""
                INSERT INTO transactions (
                    id, user_id, tenant_id, account_id, category_id,
                    type, description, value, date, status, paid_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pago', CURRENT_TIMESTAMP)
            """, (
                transaction_id,
                recurring['user_id'],
                recurring['tenant_id'],
                recurring['account_id'],
                recurring['category_id'],
                recurring['type'],
                f"{recurring['description']} (Recorrente)",
                recurring['value'],
                today
            ))
            
            # Atualizar saldo da conta manualmente (mesma conexão)
            if recurring['type'] == 'Receita':
                db.execute("""
                    UPDATE accounts 
                    SET current_balance = current_balance + ?
                    WHERE id = ?
                """, (recurring['value'], recurring['account_id']))
            else:  # Despesa
                db.execute("""
                    UPDATE accounts 
                    SET current_balance = current_balance - ?
                    WHERE id = ?
                """, (recurring['value'], recurring['account_id']))
            
            # Calcular próxima execução
            start_date = datetime.strptime(recurring['start_date'], '%Y-%m-%d')
            next_exec = calculate_next_execution(start_date, recurring['frequency'], recurring['day_of_execution'])
            
            # Atualizar recurring
            db.execute("""
                UPDATE recurring_transactions
                SET next_execution = ?, last_execution = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (next_exec.strftime('%Y-%m-%d'), today, recurring['id']))
            
            executed_count += 1
            
        except Exception as e:
            print(f"❌ Erro ao executar recorrência {recurring['id']}: {e}")
            continue
    
    db.commit()
    db.close()
    
    print(f"✅ Executadas {executed_count} transações recorrentes")
    return executed_count
