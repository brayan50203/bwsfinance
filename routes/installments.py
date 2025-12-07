"""
Módulo de Parcelamentos/Installments
Blueprint REST API para gerenciar parcelamentos (compras divididas em múltiplas parcelas)

Funcionalidades:
- Criar parcelamento (gera N transações automaticamente)
- Listar parcelamentos
- Detalhes de parcelamento
- Atualizar parcelamento
- Cancelar parcelamento (deleta parcelas não pagas)
- Pagar todas as parcelas
- Ver cronograma de pagamento
"""

from flask import Blueprint, request, jsonify, session
import sqlite3
import uuid
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

installments_bp = Blueprint('installments', __name__)

def get_db():
    """Conecta ao banco de dados"""
    db = sqlite3.connect('bws_finance.db')
    db.row_factory = sqlite3.Row
    return db

def require_auth():
    """Extrai user_id da sessão ou query string"""
    user_id = session.get('user_id') or request.args.get('user_id')
    if not user_id:
        return None
    return user_id

def calculate_installment_value(total_amount, installment_count, interest_rate=0):
    """
    Calcula o valor de cada parcela com juros simples
    
    Args:
        total_amount: Valor total da compra
        installment_count: Número de parcelas
        interest_rate: Taxa de juros mensal (ex: 2.5 para 2.5%)
    
    Returns:
        float: Valor de cada parcela
    """
    if interest_rate > 0:
        # Juros simples: valor_parcela = (total * (1 + taxa * periodo)) / parcelas
        total_with_interest = total_amount * (1 + (interest_rate / 100) * installment_count)
        return round(total_with_interest / installment_count, 2)
    else:
        return round(total_amount / installment_count, 2)

def generate_installment_transactions(db, installment_id, installment_data):
    """
    Gera N transações para o parcelamento
    
    Args:
        db: Conexão do banco de dados
        installment_id: ID do grupo de parcelamento
        installment_data: Dicionário com dados do parcelamento
    
    Returns:
        list: Lista de IDs das transações criadas
    """
    cursor = db.cursor()
    transaction_ids = []
    
    first_due_date = datetime.strptime(installment_data['first_due_date'], '%Y-%m-%d')
    installment_value = installment_data['installment_value']
    card_id = installment_data.get('card_id')
    
    # Se tem cartão, deduzir o valor total do limite disponível
    if card_id:
        total_amount = installment_data['total_amount']
        cursor.execute("""
            UPDATE cards 
            SET used_limit = COALESCE(used_limit, 0) + ?
            WHERE id = ?
        """, (total_amount, card_id))
    
    for i in range(1, installment_data['installment_count'] + 1):
        # Calcula a data de vencimento de cada parcela (mensal)
        due_date = first_due_date + relativedelta(months=(i - 1))
        
        # Ajuste para última parcela (pode ter centavos a mais devido a arredondamento)
        if i == installment_data['installment_count']:
            # Recalcula para garantir que soma total = total_amount
            cursor.execute("""
                SELECT COALESCE(SUM(value), 0) as total_paid
                FROM transactions
                WHERE installment_id = ?
            """, (installment_id,))
            total_paid = cursor.fetchone()['total_paid']
            installment_value = round(installment_data['total_amount'] - total_paid, 2)
        
        transaction_id = str(uuid.uuid4())
        description = f"{installment_data['description']} ({i}/{installment_data['installment_count']})"
        
        cursor.execute("""
            INSERT INTO transactions (
                id, user_id, tenant_id, account_id, card_id, category_id,
                type, description, value, date, due_date, status, 
                installment_id, installment_number, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            transaction_id,
            installment_data['user_id'],
            installment_data['tenant_id'],
            installment_data.get('account_id'),
            installment_data.get('card_id'),
            installment_data.get('category_id'),
            'Despesa',
            description,
            installment_value,
            due_date.strftime('%Y-%m-%d'),
            due_date.strftime('%Y-%m-%d'),
            'Pendente',
            installment_id,
            i,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        transaction_ids.append(transaction_id)
    
    db.commit()
    return transaction_ids

# ==================== ENDPOINTS ====================

@installments_bp.route('/api/installments', methods=['POST'])
def create_installment():
    """
    POST /api/installments
    Cria um parcelamento e gera as transações automaticamente
    
    Body:
    {
        "description": "Notebook Dell",
        "total_amount": 3000.00,
        "installment_count": 10,
        "interest_rate": 0,  // opcional, juros mensal em %
        "first_due_date": "2025-01-15",
        "account_id": "uuid",  // opcional
        "card_id": "uuid",  // opcional
        "category_id": "uuid"  // opcional
    }
    """
    user_id = require_auth()
    if not user_id:
        return jsonify({'error': 'Não autenticado'}), 401
    
    data = request.get_json()
    
    # Validações
    if not data.get('description'):
        return jsonify({'error': 'Descrição é obrigatória'}), 400
    
    if not data.get('total_amount') or data['total_amount'] <= 0:
        return jsonify({'error': 'Valor total deve ser maior que zero'}), 400
    
    if not data.get('installment_count') or data['installment_count'] < 2:
        return jsonify({'error': 'Número de parcelas deve ser no mínimo 2'}), 400
    
    if not data.get('first_due_date'):
        return jsonify({'error': 'Data do primeiro vencimento é obrigatória'}), 400
    
    # Calcular valor da parcela
    installment_value = calculate_installment_value(
        data['total_amount'],
        data['installment_count'],
        data.get('interest_rate', 0)
    )
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Buscar tenant_id do usuário
        cursor.execute("SELECT tenant_id FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        tenant_id = user['tenant_id']
        
        # Validar account_id (se fornecido)
        if data.get('account_id'):
            cursor.execute("""
                SELECT id FROM accounts 
                WHERE id = ? AND user_id = ? AND tenant_id = ?
            """, (data['account_id'], user_id, tenant_id))
            if not cursor.fetchone():
                return jsonify({'error': 'Conta não encontrada ou não pertence ao usuário'}), 404
        
        # Validar card_id (se fornecido)
        if data.get('card_id'):
            cursor.execute("""
                SELECT id FROM cards 
                WHERE id = ? AND user_id = ? AND tenant_id = ?
            """, (data['card_id'], user_id, tenant_id))
            if not cursor.fetchone():
                return jsonify({'error': 'Cartão não encontrado ou não pertence ao usuário'}), 404
        
        # Validar category_id (se fornecido)
        if data.get('category_id'):
            cursor.execute("""
                SELECT id FROM categories WHERE id = ?
            """, (data['category_id'],))
            if not cursor.fetchone():
                return jsonify({'error': 'Categoria não encontrada'}), 404
        
        # Criar registro do parcelamento
        installment_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO installments (
                id, user_id, tenant_id, account_id, card_id, category_id,
                description, total_amount, installment_count, installment_value,
                interest_rate, first_due_date, current_status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            installment_id,
            user_id,
            tenant_id,
            data.get('account_id'),
            data.get('card_id'),
            data.get('category_id'),
            data['description'],
            data['total_amount'],
            data['installment_count'],
            installment_value,
            data.get('interest_rate', 0),
            data['first_due_date'],
            'active',
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        # Gerar transações
        installment_data = {
            'user_id': user_id,
            'tenant_id': tenant_id,
            'account_id': data.get('account_id'),
            'card_id': data.get('card_id'),
            'category_id': data.get('category_id'),
            'description': data['description'],
            'total_amount': data['total_amount'],
            'installment_count': data['installment_count'],
            'installment_value': installment_value,
            'first_due_date': data['first_due_date']
        }
        
        transaction_ids = generate_installment_transactions(db, installment_id, installment_data)
        
        db.commit()
        
        return jsonify({
            'success': True,
            'installment_id': installment_id,
            'transaction_ids': transaction_ids,
            'message': f'Parcelamento criado com {data["installment_count"]} parcelas de R$ {installment_value:.2f}'
        }), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@installments_bp.route('/api/installments', methods=['GET'])
def list_installments():
    """
    GET /api/installments?status=active&limit=20&offset=0
    Lista parcelamentos do usuário
    """
    user_id = require_auth()
    if not user_id:
        return jsonify({'error': 'Não autenticado'}), 401
    
    status = request.args.get('status', 'active')
    limit = int(request.args.get('limit', 20))
    offset = int(request.args.get('offset', 0))
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Buscar tenant_id
        cursor.execute("SELECT tenant_id FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        tenant_id = user['tenant_id']
        
        # Buscar parcelamentos
        query = """
            SELECT * FROM v_installments_summary
            WHERE user_id = ? AND tenant_id = ?
        """
        params = [user_id, tenant_id]
        
        if status:
            query += " AND current_status = ?"
            params.append(status)
        
        query += " ORDER BY first_due_date DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        installments = [dict(row) for row in cursor.fetchall()]
        
        return jsonify({
            'success': True,
            'installments': installments,
            'count': len(installments)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@installments_bp.route('/api/installments/<installment_id>', methods=['GET'])
def get_installment(installment_id):
    """
    GET /api/installments/:id
    Busca detalhes de um parcelamento específico com todas as transações
    """
    user_id = require_auth()
    if not user_id:
        return jsonify({'error': 'Não autenticado'}), 401
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Buscar tenant_id
        cursor.execute("SELECT tenant_id FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        tenant_id = user['tenant_id']
        
        # Buscar parcelamento
        cursor.execute("""
            SELECT * FROM v_installments_summary
            WHERE id = ? AND user_id = ? AND tenant_id = ?
        """, (installment_id, user_id, tenant_id))
        
        installment = cursor.fetchone()
        if not installment:
            return jsonify({'error': 'Parcelamento não encontrado'}), 404
        
        # Buscar transações do parcelamento
        cursor.execute("""
            SELECT 
                id, description, value, due_date, paid_at, status, installment_number
            FROM transactions
            WHERE installment_id = ?
            ORDER BY installment_number ASC
        """, (installment_id,))
        
        transactions = [dict(row) for row in cursor.fetchall()]
        
        result = dict(installment)
        result['transactions'] = transactions
        
        return jsonify({
            'success': True,
            'installment': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@installments_bp.route('/api/installments/<installment_id>', methods=['PUT'])
def update_installment(installment_id):
    """
    PUT /api/installments/:id
    Atualiza informações do parcelamento (apenas descrição e status)
    Não permite alterar valores/parcelas após criação
    """
    user_id = require_auth()
    if not user_id:
        return jsonify({'error': 'Não autenticado'}), 401
    
    data = request.get_json()
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Buscar tenant_id
        cursor.execute("SELECT tenant_id FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        tenant_id = user['tenant_id']
        
        # Verificar se parcelamento existe e pertence ao usuário
        cursor.execute("""
            SELECT id FROM installments
            WHERE id = ? AND user_id = ? AND tenant_id = ?
        """, (installment_id, user_id, tenant_id))
        
        if not cursor.fetchone():
            return jsonify({'error': 'Parcelamento não encontrado'}), 404
        
        # Atualizar apenas campos permitidos
        updates = []
        params = []
        
        if 'description' in data:
            updates.append("description = ?")
            params.append(data['description'])
        
        if 'current_status' in data and data['current_status'] in ['active', 'cancelled']:
            updates.append("current_status = ?")
            params.append(data['current_status'])
        
        if not updates:
            return jsonify({'error': 'Nenhum campo válido para atualizar'}), 400
        
        updates.append("updated_at = ?")
        params.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        params.append(installment_id)
        
        query = f"UPDATE installments SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Parcelamento atualizado com sucesso'
        }), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@installments_bp.route('/api/installments/<installment_id>', methods=['DELETE'])
def cancel_installment(installment_id):
    """
    DELETE /api/installments/:id
    Cancela parcelamento e deleta todas as parcelas NÃO PAGAS
    Parcelas já pagas são mantidas
    """
    user_id = require_auth()
    if not user_id:
        return jsonify({'error': 'Não autenticado'}), 401
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Buscar tenant_id
        cursor.execute("SELECT tenant_id FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        tenant_id = user['tenant_id']
        
        # Verificar se parcelamento existe e buscar card_id
        cursor.execute("""
            SELECT id, card_id FROM installments
            WHERE id = ? AND user_id = ? AND tenant_id = ?
        """, (installment_id, user_id, tenant_id))
        
        installment = cursor.fetchone()
        if not installment:
            return jsonify({'error': 'Parcelamento não encontrado'}), 404
        
        card_id = installment['card_id']
        
        # Se tem cartão, calcular valor a devolver (soma das parcelas pendentes)
        if card_id:
            cursor.execute("""
                SELECT COALESCE(SUM(value), 0) as total_pending
                FROM transactions
                WHERE installment_id = ? AND status = 'Pendente'
            """, (installment_id,))
            total_pending = cursor.fetchone()['total_pending']
            
            # Devolver o limite do cartão
            if total_pending > 0:
                cursor.execute("""
                    UPDATE cards 
                    SET used_limit = COALESCE(used_limit, 0) - ?
                    WHERE id = ?
                """, (total_pending, card_id))
        
        # Deletar transações pendentes
        cursor.execute("""
            DELETE FROM transactions
            WHERE installment_id = ? AND status = 'Pendente'
        """, (installment_id,))
        
        deleted_count = cursor.rowcount
        
        # Marcar parcelamento como cancelado
        cursor.execute("""
            UPDATE installments
            SET current_status = 'cancelled', updated_at = ?
            WHERE id = ?
        """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), installment_id))
        
        db.commit()
        
        return jsonify({
            'success': True,
            'message': f'Parcelamento cancelado. {deleted_count} parcelas pendentes foram deletadas.'
        }), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@installments_bp.route('/api/installments/<installment_id>/pay-all', methods=['POST'])
def pay_all_installments(installment_id):
    """
    POST /api/installments/:id/pay-all
    Marca todas as parcelas pendentes como pagas e atualiza saldo da conta
    """
    user_id = require_auth()
    if not user_id:
        return jsonify({'error': 'Não autenticado'}), 401
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Buscar tenant_id
        cursor.execute("SELECT tenant_id FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        tenant_id = user['tenant_id']
        
        # Verificar se parcelamento existe
        cursor.execute("""
            SELECT account_id FROM installments
            WHERE id = ? AND user_id = ? AND tenant_id = ?
        """, (installment_id, user_id, tenant_id))
        
        installment = cursor.fetchone()
        if not installment:
            return jsonify({'error': 'Parcelamento não encontrado'}), 404
        
        account_id = installment['account_id']
        
        # Buscar transações pendentes
        cursor.execute("""
            SELECT id, value FROM transactions
            WHERE installment_id = ? AND status = 'Pendente'
        """, (installment_id,))
        
        pending_transactions = cursor.fetchall()
        
        if not pending_transactions:
            return jsonify({'message': 'Não há parcelas pendentes'}), 200
        
        # Marcar todas como pagas
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        total_paid = 0
        
        for transaction in pending_transactions:
            cursor.execute("""
                UPDATE transactions
                SET status = 'Pago', paid_at = ?
                WHERE id = ?
            """, (now, transaction['id']))
            total_paid += transaction['value']
        
        # Atualizar saldo da conta (se houver)
        if account_id:
            cursor.execute("""
                UPDATE accounts
                SET current_balance = current_balance - ?
                WHERE id = ?
            """, (total_paid, account_id))
        
        db.commit()
        
        return jsonify({
            'success': True,
            'message': f'{len(pending_transactions)} parcelas pagas. Total: R$ {total_paid:.2f}',
            'transactions_paid': len(pending_transactions),
            'total_amount': total_paid
        }), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@installments_bp.route('/api/installments/<installment_id>/schedule', methods=['GET'])
def get_installment_schedule(installment_id):
    """
    GET /api/installments/:id/schedule
    Retorna o cronograma de pagamento com datas e valores
    """
    user_id = require_auth()
    if not user_id:
        return jsonify({'error': 'Não autenticado'}), 401
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Buscar tenant_id
        cursor.execute("SELECT tenant_id FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        tenant_id = user['tenant_id']
        
        # Verificar se parcelamento existe
        cursor.execute("""
            SELECT * FROM installments
            WHERE id = ? AND user_id = ? AND tenant_id = ?
        """, (installment_id, user_id, tenant_id))
        
        installment = cursor.fetchone()
        if not installment:
            return jsonify({'error': 'Parcelamento não encontrado'}), 404
        
        # Buscar todas as transações do parcelamento
        cursor.execute("""
            SELECT 
                installment_number,
                description,
                value,
                due_date,
                status,
                paid_at
            FROM transactions
            WHERE installment_id = ?
            ORDER BY installment_number ASC
        """, (installment_id,))
        
        schedule = [dict(row) for row in cursor.fetchall()]
        
        # Calcular totais
        total_paid = sum(item['value'] for item in schedule if item['status'] == 'Pago')
        total_pending = sum(item['value'] for item in schedule if item['status'] == 'Pendente')
        
        return jsonify({
            'success': True,
            'installment': dict(installment),
            'schedule': schedule,
            'summary': {
                'total_installments': len(schedule),
                'paid_installments': sum(1 for item in schedule if item['status'] == 'Pago'),
                'pending_installments': sum(1 for item in schedule if item['status'] == 'Pendente'),
                'total_paid': total_paid,
                'total_pending': total_pending
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()
