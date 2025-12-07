"""
Módulo de Contas (Accounts)
Gerencia contas bancárias, carteira, investimentos
Integrado com transações para cálculo de saldo
"""

from flask import Blueprint, request, jsonify, session
from functools import wraps
import sqlite3
import uuid
from datetime import datetime
from decimal import Decimal

accounts_bp = Blueprint('accounts', __name__, url_prefix='/api/accounts')

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
    def decorated(*args, **kwargs):
        # Para desenvolvimento, aceita user_id via query/body
        # Em produção, extrair de JWT token
        user_id = request.args.get('user_id')
        
        # Se não veio por query string, tentar session
        if not user_id and 'user_id' in session:
            user_id = session.get('user_id')
        
        # Se ainda não tem, tentar JSON (apenas para POST/PUT)
        if not user_id and request.method in ['POST', 'PUT', 'PATCH']:
            try:
                if request.is_json and request.json:
                    user_id = request.json.get('user_id')
            except:
                pass
        
        if not user_id:
            return jsonify({'error': 'Unauthorized', 'message': 'user_id required'}), 401
        
        request.user_id = user_id
        
        # Buscar tenant_id do usuário
        db = get_db()
        user = db.execute("SELECT tenant_id FROM users WHERE id = ?", (request.user_id,)).fetchone()
        db.close()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        request.tenant_id = user['tenant_id']
        return f(*args, **kwargs)
    
    return decorated

def recalculate_account_balance(account_id):
    """
    Recalcula o saldo atual de uma conta baseado em:
    - initial_balance
    - soma de transações pagas (Receita = +, Despesa = -)
    """
    db = get_db()
    
    # Buscar saldo inicial
    account = db.execute("SELECT initial_balance FROM accounts WHERE id = ?", (account_id,)).fetchone()
    
    if not account:
        db.close()
        return None
    
    initial = Decimal(str(account['initial_balance']))
    
    # Calcular soma de transações pagas
    result = db.execute("""
        SELECT 
            COALESCE(SUM(CASE 
                WHEN type = 'Receita' THEN value
                WHEN type = 'Despesa' THEN -value
                ELSE 0
            END), 0) as total
        FROM transactions
        WHERE account_id = ? AND status = 'Pago'
    """, (account_id,)).fetchone()
    
    transactions_sum = Decimal(str(result['total']))
    new_balance = initial + transactions_sum
    
    # Atualizar current_balance
    db.execute(
        "UPDATE accounts SET current_balance = ?, updated_at = ? WHERE id = ?",
        (float(new_balance), datetime.now().isoformat(), account_id)
    )
    db.commit()
    db.close()
    
    return float(new_balance)

# =====================================================
# ENDPOINTS
# =====================================================

@accounts_bp.route('', methods=['GET'])
@require_auth
def list_accounts():
    """
    GET /api/accounts?user_id=xxx
    Lista todas as contas do usuário
    """
    db = get_db()
    
    accounts = db.execute("""
        SELECT * FROM v_account_balances
        WHERE user_id = ? AND tenant_id = ? AND active = 1
        ORDER BY created_at DESC
    """, (request.user_id, request.tenant_id)).fetchall()
    
    db.close()
    
    return jsonify([dict(acc) for acc in accounts]), 200

@accounts_bp.route('/<account_id>', methods=['GET'])
@require_auth
def get_account(account_id):
    """
    GET /api/accounts/:id
    Retorna detalhes de uma conta específica
    """
    db = get_db()
    
    account = db.execute("""
        SELECT * FROM v_account_balances
        WHERE id = ? AND user_id = ? AND tenant_id = ?
    """, (account_id, request.user_id, request.tenant_id)).fetchone()
    
    db.close()
    
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    
    return jsonify(dict(account)), 200

@accounts_bp.route('', methods=['POST'])
@require_auth
def create_account():
    """
    POST /api/accounts
    Body: {
        "name": "Nubank",
        "type": "bank",
        "currency": "BRL",
        "initial_balance": 1000,
        "bank": "Nubank",
        "metadata": {}
    }
    """
    data = request.json
    
    # Validações
    if not data.get('name'):
        return jsonify({'error': 'Validation error', 'field': 'name', 'message': 'Name is required'}), 400
    
    account_type = data.get('type', 'bank')
    if account_type not in ['bank', 'card', 'wallet', 'investment', 'reserve']:
        return jsonify({'error': 'Invalid type', 'message': 'Type must be: bank, card, wallet, investment, or reserve'}), 400
    
    # Criar conta
    account_id = str(uuid.uuid4())
    initial_balance = float(data.get('initial_balance', 0))
    
    db = get_db()
    
    try:
        db.execute("""
            INSERT INTO accounts (id, user_id, tenant_id, name, type, currency, initial_balance, current_balance, bank, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            account_id,
            request.user_id,
            request.tenant_id,
            data['name'],
            account_type,
            data.get('currency', 'BRL'),
            initial_balance,
            initial_balance,  # current_balance = initial no início
            data.get('bank'),
            data.get('metadata')
        ))
        
        db.commit()
        
        # Buscar conta criada
        account = db.execute("SELECT * FROM v_account_balances WHERE id = ?", (account_id,)).fetchone()
        db.close()
        
        return jsonify(dict(account)), 201
    
    except sqlite3.IntegrityError as e:
        db.close()
        return jsonify({'error': 'Database error', 'message': str(e)}), 409

@accounts_bp.route('/<account_id>', methods=['PUT'])
@require_auth
def update_account(account_id):
    """
    PUT /api/accounts/:id
    Body: campos updatable: name, type, currency, bank, metadata, initial_balance
    """
    data = request.json
    db = get_db()
    
    # Verificar ownership
    account = db.execute(
        "SELECT * FROM accounts WHERE id = ? AND user_id = ? AND tenant_id = ?",
        (account_id, request.user_id, request.tenant_id)
    ).fetchone()
    
    if not account:
        db.close()
        return jsonify({'error': 'Account not found or unauthorized'}), 404
    
    # Campos updatable
    updates = []
    params = []
    
    if 'name' in data:
        updates.append("name = ?")
        params.append(data['name'])
    
    if 'type' in data:
        if data['type'] not in ['bank', 'card', 'wallet', 'investment', 'reserve']:
            db.close()
            return jsonify({'error': 'Invalid type'}), 400
        updates.append("type = ?")
        params.append(data['type'])
    
    if 'currency' in data:
        updates.append("currency = ?")
        params.append(data['currency'])
    
    if 'bank' in data:
        updates.append("bank = ?")
        params.append(data['bank'])
    
    if 'metadata' in data:
        updates.append("metadata = ?")
        params.append(data['metadata'])
    
    # Se initial_balance mudou, ajustar current_balance
    if 'initial_balance' in data:
        old_initial = Decimal(str(account['initial_balance']))
        new_initial = Decimal(str(data['initial_balance']))
        diff = new_initial - old_initial
        
        new_current = Decimal(str(account['current_balance'])) + diff
        
        updates.append("initial_balance = ?")
        params.append(float(new_initial))
        updates.append("current_balance = ?")
        params.append(float(new_current))
    
    if not updates:
        db.close()
        return jsonify({'error': 'No fields to update'}), 400
    
    updates.append("updated_at = ?")
    params.append(datetime.now().isoformat())
    params.append(account_id)
    
    # Executar update
    query = f"UPDATE accounts SET {', '.join(updates)} WHERE id = ?"
    db.execute(query, params)
    db.commit()
    
    # Retornar conta atualizada
    updated = db.execute("SELECT * FROM v_account_balances WHERE id = ?", (account_id,)).fetchone()
    db.close()
    
    return jsonify(dict(updated)), 200

@accounts_bp.route('/<account_id>', methods=['DELETE'])
@require_auth
def delete_account(account_id):
    """
    DELETE /api/accounts/:id
    Só permite se não houver transações vinculadas
    """
    db = get_db()
    
    # Verificar ownership
    account = db.execute(
        "SELECT * FROM accounts WHERE id = ? AND user_id = ? AND tenant_id = ?",
        (account_id, request.user_id, request.tenant_id)
    ).fetchone()
    
    if not account:
        db.close()
        return jsonify({'error': 'Account not found or unauthorized'}), 404
    
    # Verificar transações vinculadas
    transactions = db.execute(
        "SELECT id, description, value, date FROM transactions WHERE account_id = ? LIMIT 5",
        (account_id,)
    ).fetchall()
    
    if transactions:
        db.close()
        return jsonify({
            'error': 'Cannot delete account with transactions',
            'message': 'Move or delete transactions first',
            'sample_transactions': [dict(t) for t in transactions]
        }), 409
    
    # Deletar conta (soft delete)
    db.execute("UPDATE accounts SET active = 0, updated_at = ? WHERE id = ?", 
               (datetime.now().isoformat(), account_id))
    db.commit()
    db.close()
    
    return jsonify({'message': 'Account deleted successfully'}), 200

@accounts_bp.route('/<account_id>/transactions', methods=['GET'])
@require_auth
def get_account_transactions(account_id):
    """
    GET /api/accounts/:id/transactions?date_from=&date_to=&page=1&limit=50
    Lista transações de uma conta
    """
    db = get_db()
    
    # Verificar ownership
    account = db.execute(
        "SELECT id FROM accounts WHERE id = ? AND user_id = ? AND tenant_id = ?",
        (account_id, request.user_id, request.tenant_id)
    ).fetchone()
    
    if not account:
        db.close()
        return jsonify({'error': 'Account not found'}), 404
    
    # Filtros
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 50))
    offset = (page - 1) * limit
    
    # Query base
    query = """
        SELECT t.*, c.name as category_name, c.icon as category_icon, c.color as category_color
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.account_id = ?
    """
    params = [account_id]
    
    if date_from:
        query += " AND t.date >= ?"
        params.append(date_from)
    
    if date_to:
        query += " AND t.date <= ?"
        params.append(date_to)
    
    query += " ORDER BY t.date DESC, t.created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    transactions = db.execute(query, params).fetchall()
    
    # Total count
    count_query = "SELECT COUNT(*) as total FROM transactions WHERE account_id = ?"
    count_params = [account_id]
    
    if date_from:
        count_query += " AND date >= ?"
        count_params.append(date_from)
    if date_to:
        count_query += " AND date <= ?"
        count_params.append(date_to)
    
    total = db.execute(count_query, count_params).fetchone()['total']
    
    db.close()
    
    return jsonify({
        'transactions': [dict(t) for t in transactions],
        'pagination': {
            'page': page,
            'limit': limit,
            'total': total,
            'pages': (total + limit - 1) // limit
        }
    }), 200

@accounts_bp.route('/<account_id>/recalculate', methods=['POST'])
@require_auth
def recalculate_balance(account_id):
    """
    POST /api/accounts/:id/recalculate
    Força recálculo do saldo (útil para debug/manutenção)
    """
    db = get_db()
    
    # Verificar ownership
    account = db.execute(
        "SELECT id FROM accounts WHERE id = ? AND user_id = ? AND tenant_id = ?",
        (account_id, request.user_id, request.tenant_id)
    ).fetchone()
    
    if not account:
        db.close()
        return jsonify({'error': 'Account not found'}), 404
    
    # Recalcular
    new_balance = recalculate_account_balance(account_id)
    
    if new_balance is None:
        return jsonify({'error': 'Failed to recalculate'}), 500
    
    return jsonify({
        'message': 'Balance recalculated successfully',
        'new_balance': new_balance
    }), 200

# =====================================================
# FUNÇÃO AUXILIAR PARA INTEGRAÇÃO COM TRANSACTIONS
# =====================================================

def update_account_balance_after_transaction(transaction_id):
    """
    Chamada após CREATE/UPDATE/DELETE de transaction
    Atualiza o current_balance da(s) conta(s) envolvida(s)
    """
    db = get_db()
    
    # Buscar transação
    transaction = db.execute(
        "SELECT account_id, type, value, status FROM transactions WHERE id = ?",
        (transaction_id,)
    ).fetchone()
    
    if not transaction:
        db.close()
        return
    
    # Se for transferência, tem 2 contas (implementar depois)
    # Por ora, atualizar apenas a conta principal
    account_id = transaction['account_id']
    
    db.close()
    
    # Recalcular saldo
    recalculate_account_balance(account_id)

# Exportar para uso em outros módulos
__all__ = ['accounts_bp', 'update_account_balance_after_transaction', 'recalculate_account_balance']
