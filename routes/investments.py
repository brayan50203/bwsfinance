"""
Módulo de Investimentos
REST API para gerenciar investimentos e calcular rendimentos
"""

from flask import Blueprint, request, jsonify, session
from datetime import datetime, timedelta
import sqlite3
from functools import wraps

investments_bp = Blueprint('investments', __name__)

# Constante do banco
DB_PATH = 'bws_finance.db'

def require_auth(f):
    """Decorator para exigir autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Não autenticado'}), 401
        return f(*args, **kwargs)
    return decorated_function

def calculate_simple_interest(principal, rate, days):
    """
    Calcula juros simples
    J = P * i * t
    """
    years = days / 365.0
    interest = principal * (rate / 100) * years
    return interest

def calculate_compound_interest(principal, rate, days):
    """
    Calcula juros compostos
    M = P * (1 + i)^t
    J = M - P
    """
    years = days / 365.0
    final_amount = principal * ((1 + rate / 100) ** years)
    interest = final_amount - principal
    return interest

def calculate_investment_value(investment):
    """
    Calcula o valor atual de um investimento baseado em juros
    """
    principal = investment['total_invested']
    rate = investment['interest_rate']
    interest_type = investment['interest_type']
    start_date = datetime.fromisoformat(investment['start_date'])
    days = (datetime.now() - start_date).days
    
    if days <= 0:
        return principal
    
    if interest_type == 'simple':
        interest = calculate_simple_interest(principal, rate, days)
    else:  # compound
        interest = calculate_compound_interest(principal, rate, days)
    
    return principal + interest

# =====================================================
# ENDPOINTS
# =====================================================

@investments_bp.route('/api/investments', methods=['GET'])
@require_auth
def list_investments():
    """Lista todos os investimentos do usuário"""
    try:
        user_id = session['user_id']
        tenant_id = session['tenant_id']
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Buscar investimentos com estatísticas
        cursor.execute("""
            SELECT * FROM v_investments_details
            WHERE user_id = ? AND tenant_id = ?
            ORDER BY created_at DESC
        """, (user_id, tenant_id))
        
        investments = [dict(row) for row in cursor.fetchall()]
        
        # Calcular valor atual baseado em juros
        for inv in investments:
            if inv['investment_status'] == 'active':
                calculated_value = calculate_investment_value(inv)
                inv['calculated_current_value'] = round(calculated_value, 2)
                inv['calculated_earned'] = round(calculated_value - inv['total_invested'], 2)
        
        conn.close()
        
        return jsonify({
            'investments': investments,
            'total': len(investments)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@investments_bp.route('/api/investments/<int:investment_id>', methods=['GET'])
@require_auth
def get_investment(investment_id):
    """Busca detalhes de um investimento específico"""
    try:
        user_id = session['user_id']
        tenant_id = session['tenant_id']
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM v_investments_details
            WHERE id = ? AND user_id = ? AND tenant_id = ?
        """, (investment_id, user_id, tenant_id))
        
        investment = cursor.fetchone()
        
        if not investment:
            conn.close()
            return jsonify({'error': 'Investimento não encontrado'}), 404
        
        investment = dict(investment)
        
        # Calcular valor atual
        if investment['investment_status'] == 'active':
            calculated_value = calculate_investment_value(investment)
            investment['calculated_current_value'] = round(calculated_value, 2)
            investment['calculated_earned'] = round(calculated_value - investment['total_invested'], 2)
        
        conn.close()
        
        return jsonify(investment), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@investments_bp.route('/api/investments', methods=['POST'])
@require_auth
def create_investment():
    """Cria um novo investimento"""
    try:
        user_id = session['user_id']
        tenant_id = session['tenant_id']
        data = request.json
        
        # Validação
        required = ['name', 'investment_type', 'amount', 'interest_rate', 'start_date']
        if not all(field in data for field in required):
            return jsonify({'error': 'Campos obrigatórios faltando'}), 400
        
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({'error': 'Valor deve ser positivo'}), 400
        
        interest_rate = float(data['interest_rate'])
        if interest_rate < 0:
            return jsonify({'error': 'Taxa de juros não pode ser negativa'}), 400
        
        # Tipos válidos
        valid_types = ['CDB', 'LCI', 'LCA', 'Tesouro Direto', 'Ações', 'Fundos', 'Poupança', 'Outro']
        if data['investment_type'] not in valid_types:
            return jsonify({'error': 'Tipo de investimento inválido'}), 400
        
        # Tipo de juros (default: compound)
        interest_type = data.get('interest_type', 'compound')
        if interest_type not in ['simple', 'compound']:
            return jsonify({'error': 'Tipo de juros inválido'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Inserir investimento
        cursor.execute("""
            INSERT INTO investments (
                tenant_id, user_id, name, investment_type, amount,
                interest_rate, interest_type, start_date, maturity_date,
                current_value, total_invested, total_earned,
                investment_status, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tenant_id,
            user_id,
            data['name'],
            data['investment_type'],
            amount,
            interest_rate,
            interest_type,
            data['start_date'],
            data.get('maturity_date'),
            amount,  # current_value inicial = amount
            amount,  # total_invested inicial = amount
            0,  # total_earned inicial = 0
            'active',
            data.get('description', '')
        ))
        
        investment_id = cursor.lastrowid
        
        # Registrar no histórico
        cursor.execute("""
            INSERT INTO investment_history (
                investment_id, date, operation_type, amount,
                balance_before, balance_after, interest_earned, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            investment_id,
            data['start_date'],
            'deposit',
            amount,
            0,
            amount,
            0,
            'Investimento inicial'
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'id': investment_id,
            'message': 'Investimento criado com sucesso'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@investments_bp.route('/api/investments/<int:investment_id>', methods=['PUT'])
@require_auth
def update_investment(investment_id):
    """Atualiza um investimento"""
    try:
        user_id = session['user_id']
        tenant_id = session['tenant_id']
        data = request.json
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se existe e pertence ao usuário
        cursor.execute("""
            SELECT * FROM investments
            WHERE id = ? AND user_id = ? AND tenant_id = ?
        """, (investment_id, user_id, tenant_id))
        
        investment = cursor.fetchone()
        if not investment:
            conn.close()
            return jsonify({'error': 'Investimento não encontrado'}), 404
        
        # Atualizar campos permitidos
        update_fields = []
        values = []
        
        if 'name' in data:
            update_fields.append('name = ?')
            values.append(data['name'])
        
        if 'description' in data:
            update_fields.append('description = ?')
            values.append(data['description'])
        
        if 'interest_rate' in data:
            rate = float(data['interest_rate'])
            if rate < 0:
                conn.close()
                return jsonify({'error': 'Taxa de juros não pode ser negativa'}), 400
            update_fields.append('interest_rate = ?')
            values.append(rate)
        
        if 'maturity_date' in data:
            update_fields.append('maturity_date = ?')
            values.append(data['maturity_date'])
        
        if 'investment_status' in data:
            valid_statuses = ['active', 'matured', 'withdrawn', 'cancelled']
            if data['investment_status'] not in valid_statuses:
                conn.close()
                return jsonify({'error': 'Status inválido'}), 400
            update_fields.append('investment_status = ?')
            values.append(data['investment_status'])
        
        if not update_fields:
            conn.close()
            return jsonify({'error': 'Nenhum campo para atualizar'}), 400
        
        values.extend([investment_id, user_id, tenant_id])
        
        cursor.execute(f"""
            UPDATE investments
            SET {', '.join(update_fields)}
            WHERE id = ? AND user_id = ? AND tenant_id = ?
        """, values)
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Investimento atualizado com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@investments_bp.route('/api/investments/<int:investment_id>', methods=['DELETE'])
@require_auth
def delete_investment(investment_id):
    """Deleta (cancela) um investimento"""
    try:
        user_id = session['user_id']
        tenant_id = session['tenant_id']
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se existe
        cursor.execute("""
            SELECT * FROM investments
            WHERE id = ? AND user_id = ? AND tenant_id = ?
        """, (investment_id, user_id, tenant_id))
        
        investment = cursor.fetchone()
        if not investment:
            conn.close()
            return jsonify({'error': 'Investimento não encontrado'}), 404
        
        # Marcar como cancelado ao invés de deletar
        cursor.execute("""
            UPDATE investments
            SET investment_status = 'cancelled'
            WHERE id = ? AND user_id = ? AND tenant_id = ?
        """, (investment_id, user_id, tenant_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Investimento cancelado com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@investments_bp.route('/api/investments/<int:investment_id>/history', methods=['GET'])
@require_auth
def get_investment_history(investment_id):
    """Busca o histórico de um investimento"""
    try:
        user_id = session['user_id']
        tenant_id = session['tenant_id']
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Verificar se o investimento pertence ao usuário
        cursor.execute("""
            SELECT id FROM investments
            WHERE id = ? AND user_id = ? AND tenant_id = ?
        """, (investment_id, user_id, tenant_id))
        
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Investimento não encontrado'}), 404
        
        # Buscar histórico
        cursor.execute("""
            SELECT * FROM investment_history
            WHERE investment_id = ?
            ORDER BY date DESC, created_at DESC
        """, (investment_id,))
        
        history = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'history': history,
            'total': len(history)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@investments_bp.route('/api/investments/<int:investment_id>/deposit', methods=['POST'])
@require_auth
def deposit_investment(investment_id):
    """Adiciona valor a um investimento (aporte)"""
    try:
        user_id = session['user_id']
        tenant_id = session['tenant_id']
        data = request.json
        
        if 'amount' not in data:
            return jsonify({'error': 'Campo amount obrigatório'}), 400
        
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({'error': 'Valor deve ser positivo'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Buscar investimento
        cursor.execute("""
            SELECT * FROM investments
            WHERE id = ? AND user_id = ? AND tenant_id = ? AND investment_status = 'active'
        """, (investment_id, user_id, tenant_id))
        
        investment = cursor.fetchone()
        if not investment:
            conn.close()
            return jsonify({'error': 'Investimento não encontrado ou inativo'}), 404
        
        investment = dict(investment)
        
        # Atualizar valores
        new_current_value = investment['current_value'] + amount
        new_total_invested = investment['total_invested'] + amount
        
        cursor.execute("""
            UPDATE investments
            SET current_value = ?,
                total_invested = ?
            WHERE id = ?
        """, (new_current_value, new_total_invested, investment_id))
        
        # Registrar no histórico
        cursor.execute("""
            INSERT INTO investment_history (
                investment_id, date, operation_type, amount,
                balance_before, balance_after, interest_earned, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            investment_id,
            data.get('date', datetime.now().isoformat()),
            'deposit',
            amount,
            investment['current_value'],
            new_current_value,
            0,
            data.get('description', 'Aporte adicional')
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Aporte realizado com sucesso',
            'new_value': new_current_value
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@investments_bp.route('/api/investments/<int:investment_id>/withdraw', methods=['POST'])
@require_auth
def withdraw_investment(investment_id):
    """Resgata valor de um investimento"""
    try:
        user_id = session['user_id']
        tenant_id = session['tenant_id']
        data = request.json
        
        if 'amount' not in data:
            return jsonify({'error': 'Campo amount obrigatório'}), 400
        
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({'error': 'Valor deve ser positivo'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Buscar investimento
        cursor.execute("""
            SELECT * FROM investments
            WHERE id = ? AND user_id = ? AND tenant_id = ? AND investment_status = 'active'
        """, (investment_id, user_id, tenant_id))
        
        investment = cursor.fetchone()
        if not investment:
            conn.close()
            return jsonify({'error': 'Investimento não encontrado ou inativo'}), 404
        
        investment = dict(investment)
        
        # Verificar se há saldo suficiente
        if amount > investment['current_value']:
            conn.close()
            return jsonify({'error': 'Saldo insuficiente no investimento'}), 400
        
        # Atualizar valores
        new_current_value = investment['current_value'] - amount
        
        # Se resgatar tudo, marcar como withdrawn
        new_status = 'withdrawn' if new_current_value == 0 else 'active'
        
        cursor.execute("""
            UPDATE investments
            SET current_value = ?,
                investment_status = ?
            WHERE id = ?
        """, (new_current_value, new_status, investment_id))
        
        # Registrar no histórico
        cursor.execute("""
            INSERT INTO investment_history (
                investment_id, date, operation_type, amount,
                balance_before, balance_after, interest_earned, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            investment_id,
            data.get('date', datetime.now().isoformat()),
            'withdrawal',
            amount,
            investment['current_value'],
            new_current_value,
            0,
            data.get('description', 'Resgate parcial' if new_current_value > 0 else 'Resgate total')
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Resgate realizado com sucesso',
            'new_value': new_current_value,
            'status': new_status
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@investments_bp.route('/api/investments/<int:investment_id>/calculate-interest', methods=['POST'])
@require_auth
def calculate_interest(investment_id):
    """Calcula e aplica os juros acumulados"""
    try:
        user_id = session['user_id']
        tenant_id = session['tenant_id']
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Buscar investimento
        cursor.execute("""
            SELECT * FROM investments
            WHERE id = ? AND user_id = ? AND tenant_id = ? AND investment_status = 'active'
        """, (investment_id, user_id, tenant_id))
        
        investment = cursor.fetchone()
        if not investment:
            conn.close()
            return jsonify({'error': 'Investimento não encontrado ou inativo'}), 404
        
        investment = dict(investment)
        
        # Calcular juros
        principal = investment['total_invested']
        rate = investment['interest_rate']
        interest_type = investment['interest_type']
        start_date = datetime.fromisoformat(investment['start_date'])
        days = (datetime.now() - start_date).days
        
        if days <= 0:
            conn.close()
            return jsonify({'error': 'Investimento ainda não rendeu'}), 400
        
        if interest_type == 'simple':
            interest = calculate_simple_interest(principal, rate, days)
        else:  # compound
            interest = calculate_compound_interest(principal, rate, days)
        
        new_current_value = principal + interest
        new_total_earned = interest
        
        # Atualizar investimento
        cursor.execute("""
            UPDATE investments
            SET current_value = ?,
                total_earned = ?
            WHERE id = ?
        """, (new_current_value, new_total_earned, investment_id))
        
        # Registrar no histórico
        cursor.execute("""
            INSERT INTO investment_history (
                investment_id, date, operation_type, amount,
                balance_before, balance_after, interest_earned, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            investment_id,
            datetime.now().isoformat(),
            'interest',
            interest,
            investment['current_value'],
            new_current_value,
            interest,
            f'Juros {interest_type} de {days} dias'
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Juros calculados e aplicados',
            'interest_earned': round(interest, 2),
            'new_value': round(new_current_value, 2),
            'days': days
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@investments_bp.route('/api/quote/<ticker>', methods=['GET'])
def get_quote(ticker):
    """
    Busca cotação em tempo real de um ativo (ação, cripto, etc)
    Rota pública (não requer autenticação) para uso no formulário
    """
    try:
        from services.api_connectors import InvestmentAPIFactory
        
        # Remover espaços
        ticker = ticker.strip().upper()
        
        # Detectar tipo de ativo
        crypto_keywords = ['BITCOIN', 'BTC', 'ETHEREUM', 'ETH', 'BNB', 'CARDANO', 'ADA', 
                          'SOLANA', 'SOL', 'XRP', 'RIPPLE', 'DOGE', 'DOGECOIN', 
                          'USDT', 'USDC', 'MATIC', 'POLYGON']
        
        is_crypto = any(keyword in ticker for keyword in crypto_keywords)
        
        if is_crypto:
            # Buscar como criptomoeda
            data = InvestmentAPIFactory.get_investment_data('Criptomoedas', ticker)
        else:
            # Buscar como ação com múltiplos fallbacks
            data = InvestmentAPIFactory.get_stock_with_fundamentals(ticker)
        
        if not data or not data.get('price') or data.get('price', 0) <= 0:
            return jsonify({
                'success': False,
                'error': 'Ativo não encontrado ou cotação indisponível'
            }), 404
        
        # Determinar tipo de ativo
        asset_type = data.get('asset_type', '')  # 'FII', 'Ação', etc
        
        # Se não veio asset_type, tentar detectar pelo ticker
        if not asset_type:
            if is_crypto:
                asset_type = 'crypto'
            elif ticker.endswith('11'):
                asset_type = 'FII'
            else:
                asset_type = 'Ação'
        
        return jsonify({
            'success': True,
            'ticker': ticker,
            'name': data.get('name', ticker),
            'price': round(data.get('price', 0), 2),
            'change': round(data.get('change', 0), 2),
            'change_percent': round(data.get('change_percent', 0), 2),
            'type': 'crypto' if is_crypto else 'stock',
            'asset_type': asset_type,  # 'FII', 'Ação', 'crypto'
            'currency': 'BRL'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao buscar cotação: {str(e)}'
        }), 500
