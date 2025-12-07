"""
WhatsApp GPT Integration API
Endpoint para receber mensagens do WhatsApp e processar com GPT
"""
from flask import Blueprint, request, jsonify, session
import sqlite3
import logging
from datetime import datetime
from modules.gpt_assistant import process_whatsapp_message, generate_tip
from modules.nlp_classifier import NLPClassifier

whatsapp_gpt_bp = Blueprint('whatsapp_gpt', __name__, url_prefix='/api/whatsapp')
logger = logging.getLogger(__name__)

# =========================================
# HELPERS
# =========================================

def get_db():
    """Conecta ao banco de dados"""
    db = sqlite3.connect('bws_finance.db')
    db.row_factory = sqlite3.Row
    return db

def get_user_by_phone(phone: str):
    """Busca usuário pelo telefone do WhatsApp"""
    db = get_db()
    # Normalizar telefone (remover caracteres especiais)
    phone_clean = ''.join(filter(str.isdigit, phone))
    
    user = db.execute(
        "SELECT * FROM users WHERE phone LIKE ? AND active = 1",
        (f'%{phone_clean[-9:]}%',)  # Últimos 9 dígitos
    ).fetchone()
    db.close()
    
    return dict(user) if user else None

# =========================================
# ENDPOINTS
# =========================================

@whatsapp_gpt_bp.route('/message', methods=['POST'])
def process_message():
    """
    Processa mensagem do WhatsApp com GPT
    
    Body esperado:
    {
        "phone": "5511999999999",
        "message": "Gastei 50 reais no mercado",
        "timestamp": "2025-11-09T10:30:00"
    }
    """
    try:
        data = request.json
        phone = data.get('phone', '').strip()
        message = data.get('message', '').strip()
        
        if not phone or not message:
            return jsonify({
                'success': False,
                'error': 'Phone e message são obrigatórios'
            }), 400
        
        logger.info(f"📱 Mensagem de {phone}: {message[:100]}...")
        
        # Buscar usuário
        user = get_user_by_phone(phone)
        if not user:
            return jsonify({
                'success': False,
                'error': 'Usuário não encontrado. Cadastre-se em http://192.168.80.122:5000/register',
                'response': f"""❌ Ops! Número não cadastrado.

📲 Para usar o assistente, cadastre-se em:
http://192.168.80.122:5000/register

Use este número no campo telefone: {phone}

Até já! 👋"""
            })
        
        logger.info(f"✅ Usuário encontrado: {user['name']} (ID: {user['id']})")
        
        # Processar mensagem com GPT
        result = process_whatsapp_message(message, phone)
        
        logger.info(f"🤖 Intent detectado: {result.get('intent')}")
        
        # ===================================
        # PROCESSAR INTENT
        # ===================================
        
        intent = result.get('intent', 'unknown')
        response_text = result.get('response', '')
        
        # 1. TRANSAÇÃO (Despesa ou Receita)
        if intent == 'transaction':
            transaction_result = create_transaction(user, result)
            
            if transaction_result['success']:
                response_text = f"""✅ Transação registrada com sucesso!

💰 **Tipo:** {result['type']}
💵 **Valor:** R$ {result['amount']:.2f}
📁 **Categoria:** {result.get('category', 'Outros')}
📅 **Data:** {result.get('date', datetime.now().strftime('%d/%m/%Y'))}
📝 **Descrição:** {result.get('description', 'N/A')}

Quer ver seu saldo? Digite: *saldo*
Relatório do mês? Digite: *extrato*"""
            else:
                response_text = f"❌ Erro ao registrar: {transaction_result.get('error', 'Erro desconhecido')}"
        
        # 2. CONSULTA (Saldo, Extrato, etc)
        elif intent == 'query':
            action = result.get('action')
            
            if action == 'get_monthly_expenses':
                summary = get_monthly_summary(user)
                response_text = format_monthly_summary(summary)
            
            elif action == 'get_balance':
                balance = get_account_balance(user)
                response_text = format_balance(balance)
            
            else:
                # Resposta genérica do GPT
                pass
        
        # 3. DICA FINANCEIRA
        elif intent == 'advice':
            user_data = get_user_financial_data(user)
            tip = generate_tip(user_data)
            response_text = f"💡 **Dica Personalizada:**\n\n{tip}"
        
        # 4. SAUDAÇÃO/AJUDA
        elif intent in ['greeting', 'help']:
            if not response_text:
                response_text = f"""👋 Olá, **{user['name']}**! 

Sou seu assistente financeiro BWS. Como posso ajudar?

📝 **Comandos:**
• Registrar gasto: "Gastei 50 reais no mercado"
• Ver saldo: "saldo" ou "quanto tenho?"
• Extrato mensal: "extrato" ou "quanto gastei?"
• Dica financeira: "dica" ou "me ajuda"

💬 Ou apenas converse naturalmente comigo!"""
        
        # 5. DESCONHECIDO
        else:
            if not response_text:
                response_text = """❓ Desculpe, não entendi completamente.

Tente:
• "Gastei X reais em Y"
• "Recebi X reais"
• "Quanto gastei esse mês?"
• "Me dá uma dica"

Ou me pergunte algo! 😊"""
        
        return jsonify({
            'success': True,
            'response': response_text,
            'intent': intent,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar mensagem: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'response': '❌ Erro interno. Tente novamente em alguns instantes.'
        }), 500

# =========================================
# FUNÇÕES AUXILIARES
# =========================================

def create_transaction(user: dict, data: dict) -> dict:
    """Cria transação no banco de dados"""
    try:
        db = get_db()
        
        # Buscar categoria
        category = db.execute(
            "SELECT id FROM categories WHERE name = ? AND tenant_id = ? LIMIT 1",
            (data.get('category', 'Outros'), user['tenant_id'])
        ).fetchone()
        
        category_id = category['id'] if category else None
        
        # Buscar conta padrão do usuário
        account = db.execute(
            "SELECT id FROM accounts WHERE user_id = ? AND tenant_id = ? LIMIT 1",
            (user['id'], user['tenant_id'])
        ).fetchone()
        
        if not account:
            return {'success': False, 'error': 'Nenhuma conta encontrada'}
        
        # Inserir transação
        import uuid
        transaction_id = str(uuid.uuid4())
        
        db.execute("""
            INSERT INTO transactions (
                id, user_id, tenant_id, type, value, description, 
                category_id, account_id, date, status, is_fixed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            transaction_id,
            user['id'],
            user['tenant_id'],
            data['type'],
            data['amount'],
            data.get('description', '')[:200],
            category_id,
            account['id'],
            data.get('date', datetime.now().strftime('%Y-%m-%d')),
            'Pago',
            0
        ))
        
        db.commit()
        db.close()
        
        return {'success': True, 'transaction_id': transaction_id}
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar transação: {e}")
        return {'success': False, 'error': str(e)}

def get_monthly_summary(user: dict) -> dict:
    """Retorna resumo financeiro do mês"""
    db = get_db()
    
    summary = db.execute("""
        SELECT 
            SUM(CASE WHEN type = 'Receita' THEN value ELSE 0 END) as income,
            SUM(CASE WHEN type = 'Despesa' THEN value ELSE 0 END) as expenses,
            COUNT(*) as total_transactions
        FROM transactions
        WHERE user_id = ? AND tenant_id = ?
        AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
        AND status = 'Pago'
    """, (user['id'], user['tenant_id'])).fetchone()
    
    db.close()
    return dict(summary) if summary else {'income': 0, 'expenses': 0, 'total_transactions': 0}

def get_account_balance(user: dict) -> dict:
    """Retorna saldo das contas"""
    db = get_db()
    
    accounts = db.execute("""
        SELECT name, current_balance
        FROM v_account_balances
        WHERE user_id = ? AND tenant_id = ?
    """, (user['id'], user['tenant_id'])).fetchall()
    
    db.close()
    return [dict(acc) for acc in accounts]

def get_user_financial_data(user: dict) -> dict:
    """Dados financeiros para dicas personalizadas"""
    summary = get_monthly_summary(user)
    
    db = get_db()
    top_category = db.execute("""
        SELECT c.name, SUM(t.value) as total
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ? AND t.type = 'Despesa'
        AND strftime('%Y-%m', t.date) = strftime('%Y-%m', 'now')
        GROUP BY c.name
        ORDER BY total DESC
        LIMIT 1
    """, (user['id'],)).fetchone()
    db.close()
    
    return {
        'income': summary.get('income', 0),
        'expenses': summary.get('expenses', 0),
        'balance': summary.get('income', 0) - summary.get('expenses', 0),
        'top_category': top_category['name'] if top_category else 'N/A'
    }

def format_monthly_summary(summary: dict) -> str:
    """Formata resumo mensal"""
    income = summary.get('income', 0)
    expenses = summary.get('expenses', 0)
    balance = income - expenses
    
    return f"""📊 **Resumo do Mês:**

💰 **Receitas:** R$ {income:.2f}
💸 **Despesas:** R$ {expenses:.2f}
{'📈' if balance >= 0 else '📉'} **Saldo:** R$ {balance:.2f}

📝 **Transações:** {summary.get('total_transactions', 0)}

{'✅ Parabéns! Você está no azul!' if balance >= 0 else '⚠️ Atenção aos gastos!'}"""

def format_balance(accounts: list) -> str:
    """Formata saldo das contas"""
    if not accounts:
        return "📭 Nenhuma conta cadastrada."
    
    total = sum(acc['current_balance'] for acc in accounts)
    
    text = "💳 **Suas Contas:**\n\n"
    for acc in accounts:
        text += f"🏦 **{acc['name']}:** R$ {acc['current_balance']:.2f}\n"
    
    text += f"\n💰 **Total:** R$ {total:.2f}"
    
    return text


# =========================================
# COMANDO PARA TESTAR
# =========================================

@whatsapp_gpt_bp.route('/test', methods=['GET'])
def test_endpoint():
    """Endpoint de teste"""
    return jsonify({
        'status': 'ok',
        'message': 'WhatsApp GPT API está funcionando!',
        'endpoint': '/api/whatsapp/message'
    })
