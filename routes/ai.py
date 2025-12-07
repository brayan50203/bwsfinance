"""
BWS Insight AI - Rotas REST
Endpoints da API da Inteligência Artificial
"""

from flask import Blueprint, request, jsonify, session
from services.ai_core import BWSInsightAI
from services.ai_chat import AIChat
from functools import wraps

# Criar Blueprint
ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

def login_required_api(f):
    """Decorator para verificar autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Não autorizado'}), 401
        return f(*args, **kwargs)
    return decorated_function

@ai_bp.route('/insight', methods=['GET'])
@login_required_api
def get_daily_insight():
    """
    GET /api/ai/insight
    Retorna insight diário automático
    """
    try:
        user_id = session.get('user_id')
        tenant_id = session.get('tenant_id')
        
        # Inicializar IA
        ai = BWSInsightAI(user_id=user_id, tenant_id=tenant_id)
        
        # Buscar dados financeiros
        financial_data = ai.fetch_financial_data(session=request.cookies)
        
        if not financial_data:
            return jsonify({'error': 'Não foi possível buscar dados financeiros'}), 500
        
        # Gerar insights
        insights = ai.generate_daily_insight(financial_data)
        
        # Detectar anomalias
        anomalies = ai.detect_anomalies(financial_data)
        
        # Previsão de saldo
        prediction = ai.predict_future_balance(financial_data, days=30)
        
        return jsonify({
            'success': True,
            'insights': insights,
            'anomalies': anomalies,
            'prediction': prediction,
            'generated_at': insights['generated_at']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/chat', methods=['POST'])
@login_required_api
def chat_with_ai():
    """
    POST /api/ai/chat
    Processa mensagem do usuário e retorna resposta da IA
    
    Body: {
        "message": "Quanto gastei com alimentação?"
    }
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Mensagem vazia'}), 400
        
        user_id = session.get('user_id')
        tenant_id = session.get('tenant_id')
        
        # Inicializar IA
        ai = BWSInsightAI(user_id=user_id, tenant_id=tenant_id)
        chat = AIChat(ai)
        
        # Buscar dados financeiros
        financial_data = ai.fetch_financial_data(session=request.cookies)
        
        # Processar mensagem
        ai_response = chat.process_message(user_message, financial_data)
        
        return jsonify({
            'success': True,
            'user_message': user_message,
            'ai_response': ai_response,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/history', methods=['GET'])
@login_required_api
def get_conversation_history():
    """
    GET /api/ai/history?limit=10
    Retorna histórico de conversas com a IA
    """
    try:
        user_id = session.get('user_id')
        tenant_id = session.get('tenant_id')
        limit = request.args.get('limit', 10, type=int)
        
        ai = BWSInsightAI(user_id=user_id, tenant_id=tenant_id)
        history = ai.get_conversation_history(limit=limit)
        
        return jsonify({
            'success': True,
            'history': history,
            'total': len(history)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/alerts', methods=['GET'])
@login_required_api
def get_alerts():
    """
    GET /api/ai/alerts
    Retorna alertas e avisos importantes
    """
    try:
        user_id = session.get('user_id')
        tenant_id = session.get('tenant_id')
        
        ai = BWSInsightAI(user_id=user_id, tenant_id=tenant_id)
        financial_data = ai.fetch_financial_data(session=request.cookies)
        
        # Detectar anomalias (alertas)
        anomalies = ai.detect_anomalies(financial_data)
        
        # Filtrar apenas alertas de alta severidade
        alerts = [a for a in anomalies if a.get('severity') in ['high', 'medium']]
        
        return jsonify({
            'success': True,
            'alerts': alerts,
            'total': len(alerts)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/predict', methods=['GET'])
@login_required_api
def predict_future():
    """
    GET /api/ai/predict?days=30
    Retorna previsão de saldo futuro
    """
    try:
        user_id = session.get('user_id')
        tenant_id = session.get('tenant_id')
        days = request.args.get('days', 30, type=int)
        
        ai = BWSInsightAI(user_id=user_id, tenant_id=tenant_id)
        financial_data = ai.fetch_financial_data(session=request.cookies)
        
        prediction = ai.predict_future_balance(financial_data, days=days)
        
        return jsonify({
            'success': True,
            'prediction': prediction
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/summary', methods=['GET'])
@login_required_api
def get_ai_summary():
    """
    GET /api/ai/summary
    Retorna resumo completo com todos os insights, alertas e previsões
    """
    try:
        user_id = session.get('user_id')
        tenant_id = session.get('tenant_id')
        
        ai = BWSInsightAI(user_id=user_id, tenant_id=tenant_id)
        financial_data = ai.fetch_financial_data(session=request.cookies)
        
        # Gerar todos os dados
        insights = ai.generate_daily_insight(financial_data)
        anomalies = ai.detect_anomalies(financial_data)
        prediction = ai.predict_future_balance(financial_data, days=30)
        
        # Dashboard data
        dashboard = financial_data.get('dashboard', {})
        
        return jsonify({
            'success': True,
            'summary': {
                'saldo': dashboard.get('saldo', 0),
                'renda': dashboard.get('renda_total', 0),
                'custos': dashboard.get('custos_total', 0),
                'investimentos': sum(dashboard.get('investimentos', {}).values())
            },
            'insights': insights['insights'],
            'anomalies': anomalies,
            'prediction': prediction,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/status', methods=['GET'])
def ai_status():
    """
    GET /api/ai/status
    Verifica status da IA (não requer autenticação)
    """
    return jsonify({
        'success': True,
        'name': 'BWS Insight AI',
        'version': '1.0.0',
        'status': 'operational',
        'capabilities': [
            'Análise financeira automática',
            'Previsão de saldo futuro',
            'Detecção de anomalias',
            'Chat em linguagem natural',
            'Geração de insights diários',
            'Alertas inteligentes'
        ]
    })
