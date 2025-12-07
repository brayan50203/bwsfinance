"""
BWS Finance - Backend Flask
Base: nik0finance
Melhorado com: Multi-tenant, Contas, Cartões, Parcelamentos, Recorrências
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
import sqlite3
import uuid
import os
import requests
import re
from dotenv import load_dotenv

# Importar serviços de investimentos
from services.api_connectors import InvestmentAPIFactory
from services.investment_calculator import InvestmentCalculator
from services.investment_ai_advisor import InvestmentAIAdvisor
from utils.formatters import format_brl

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['DATABASE'] = 'bws_finance.db'

# Configuração de sessão - Ficar logado por 30 dias
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
app.config['SESSION_COOKIE_SECURE'] = False  # True se usar HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Registrar filtro customizado BRL
app.jinja_env.filters['brl'] = format_brl

# Registrar blueprints de API
from routes.accounts import accounts_bp
from routes.recurring import recurring_bp
from routes.installments import installments_bp
from routes.investments import investments_bp
from routes.bank_import import import_bp

# AI blueprint - carregamento opcional (requer sklearn/scipy)
# try:
#     from routes.ai import ai_bp
#     app.register_blueprint(ai_bp)
#     print("✅ AI routes loaded")
# except ImportError as e:
#     print(f"⚠️ AI routes disabled (missing dependencies: {e})")
print("⚠️ AI routes disabled for faster startup")

app.register_blueprint(accounts_bp)
app.register_blueprint(recurring_bp)
app.register_blueprint(installments_bp)
app.register_blueprint(investments_bp)
app.register_blueprint(import_bp)

# WhatsApp GPT Integration
from routes.whatsapp_gpt import whatsapp_gpt_bp
app.register_blueprint(whatsapp_gpt_bp)

# Notifications System
from routes.notifications import notifications_bp
app.register_blueprint(notifications_bp)
print("✅ Notifications routes loaded")

# Auto Notifications Service (Scheduler)
from services.auto_notifications import notification_service
notification_service.start()
print("✅ Auto Notifications Scheduler started")

# =====================================================
# DATABASE HELPERS
# =====================================================

def get_db():
    """Conecta ao banco de dados SQLite"""
    db = sqlite3.connect(app.config['DATABASE'], timeout=30.0, check_same_thread=False)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA journal_mode=WAL')  # Write-Ahead Logging para melhor concorrência
    return db

def init_db():
    """Inicializa o banco de dados com o schema"""
    with app.app_context():
        db = get_db()
        with open('database_schema.sql', 'r', encoding='utf-8') as f:
            db.executescript(f.read())
        db.commit()
        db.close()
        print("✅ Database initialized!")

def seed_default_data():
    """Popula dados iniciais (tenant padrão, categorias padrão)"""
    db = get_db()
    
    # Tenant padrão
    tenant_id = str(uuid.uuid4())
    db.execute(
        "INSERT OR IGNORE INTO tenants (id, name, subdomain) VALUES (?, ?, ?)",
        (tenant_id, 'BWS Finance', 'default')
    )
    
    # Categorias padrão
    default_categories = [
        # Receitas
        (str(uuid.uuid4()), tenant_id, 'Salário', 'Receita', '💼', '#10b981'),
        (str(uuid.uuid4()), tenant_id, '13º Salário', 'Receita', '🎁', '#10b981'),
        (str(uuid.uuid4()), tenant_id, 'Férias', 'Receita', '🏖️', '#10b981'),
        (str(uuid.uuid4()), tenant_id, 'Freelance', 'Receita', '💻', '#3b82f6'),
        (str(uuid.uuid4()), tenant_id, 'Bônus', 'Receita', '🏆', '#8b5cf6'),
        (str(uuid.uuid4()), tenant_id, 'Comissão', 'Receita', '💵', '#059669'),
        (str(uuid.uuid4()), tenant_id, 'Investimentos', 'Receita', '📈', '#8b5cf6'),
        (str(uuid.uuid4()), tenant_id, 'Dividendos', 'Receita', '💰', '#10b981'),
        (str(uuid.uuid4()), tenant_id, 'Aluguel Recebido', 'Receita', '🏘️', '#059669'),
        (str(uuid.uuid4()), tenant_id, 'Venda', 'Receita', '🏷️', '#0891b2'),
        (str(uuid.uuid4()), tenant_id, 'Reembolso', 'Receita', '↩️', '#6366f1'),
        (str(uuid.uuid4()), tenant_id, 'Prêmio', 'Receita', '🎰', '#a855f7'),
        (str(uuid.uuid4()), tenant_id, 'Empréstimo Recebido', 'Receita', '🤝', '#6b7280'),
        (str(uuid.uuid4()), tenant_id, 'Outros', 'Receita', '�', '#6b7280'),
        
        # Despesas - Essenciais
        (str(uuid.uuid4()), tenant_id, 'Alimentação', 'Despesa', '🍔', '#ef4444'),
        (str(uuid.uuid4()), tenant_id, 'Supermercado', 'Despesa', '🛒', '#f97316'),
        (str(uuid.uuid4()), tenant_id, 'Restaurante', 'Despesa', '🍽️', '#f59e0b'),
        (str(uuid.uuid4()), tenant_id, 'Lanche', 'Despesa', '🥪', '#fbbf24'),
        (str(uuid.uuid4()), tenant_id, 'Delivery', 'Despesa', '🛵', '#fb923c'),
        
        # Transporte
        (str(uuid.uuid4()), tenant_id, 'Transporte', 'Despesa', '🚗', '#f59e0b'),
        (str(uuid.uuid4()), tenant_id, 'Combustível', 'Despesa', '⛽', '#ea580c'),
        (str(uuid.uuid4()), tenant_id, 'Uber/Taxi', 'Despesa', '🚕', '#f59e0b'),
        (str(uuid.uuid4()), tenant_id, 'Estacionamento', 'Despesa', '🅿️', '#f97316'),
        (str(uuid.uuid4()), tenant_id, 'Manutenção Carro', 'Despesa', '🔧', '#dc2626'),
        (str(uuid.uuid4()), tenant_id, 'IPVA', 'Despesa', '📄', '#b91c1c'),
        (str(uuid.uuid4()), tenant_id, 'Seguro Carro', 'Despesa', '🛡️', '#991b1b'),
        
        # Moradia
        (str(uuid.uuid4()), tenant_id, 'Aluguel', 'Despesa', '🏠', '#ec4899'),
        (str(uuid.uuid4()), tenant_id, 'Condomínio', 'Despesa', '🏢', '#db2777'),
        (str(uuid.uuid4()), tenant_id, 'IPTU', 'Despesa', '📋', '#be185d'),
        (str(uuid.uuid4()), tenant_id, 'Água', 'Despesa', '💧', '#0ea5e9'),
        (str(uuid.uuid4()), tenant_id, 'Luz', 'Despesa', '💡', '#facc15'),
        (str(uuid.uuid4()), tenant_id, 'Gás', 'Despesa', '🔥', '#f97316'),
        (str(uuid.uuid4()), tenant_id, 'Internet', 'Despesa', '🌐', '#3b82f6'),
        (str(uuid.uuid4()), tenant_id, 'Telefone', 'Despesa', '📱', '#6366f1'),
        (str(uuid.uuid4()), tenant_id, 'TV/Streaming', 'Despesa', '📺', '#8b5cf6'),
        (str(uuid.uuid4()), tenant_id, 'Manutenção Casa', 'Despesa', '🔨', '#dc2626'),
        
        # Saúde
        (str(uuid.uuid4()), tenant_id, 'Saúde', 'Despesa', '🏥', '#14b8a6'),
        (str(uuid.uuid4()), tenant_id, 'Plano de Saúde', 'Despesa', '⚕️', '#0d9488'),
        (str(uuid.uuid4()), tenant_id, 'Farmácia', 'Despesa', '💊', '#06b6d4'),
        (str(uuid.uuid4()), tenant_id, 'Consulta Médica', 'Despesa', '👨‍⚕️', '#0891b2'),
        (str(uuid.uuid4()), tenant_id, 'Exames', 'Despesa', '🔬', '#0e7490'),
        (str(uuid.uuid4()), tenant_id, 'Dentista', 'Despesa', '🦷', '#06b6d4'),
        (str(uuid.uuid4()), tenant_id, 'Academia', 'Despesa', '💪', '#10b981'),
        
        # Educação
        (str(uuid.uuid4()), tenant_id, 'Educação', 'Despesa', '📚', '#6366f1'),
        (str(uuid.uuid4()), tenant_id, 'Mensalidade Escola', 'Despesa', '🎓', '#4f46e5'),
        (str(uuid.uuid4()), tenant_id, 'Curso', 'Despesa', '📖', '#5b21b6'),
        (str(uuid.uuid4()), tenant_id, 'Material Escolar', 'Despesa', '✏️', '#7c3aed'),
        (str(uuid.uuid4()), tenant_id, 'Livros', 'Despesa', '📕', '#8b5cf6'),
        
        # Lazer e Entretenimento
        (str(uuid.uuid4()), tenant_id, 'Lazer', 'Despesa', '🎮', '#a855f7'),
        (str(uuid.uuid4()), tenant_id, 'Cinema', 'Despesa', '🎬', '#9333ea'),
        (str(uuid.uuid4()), tenant_id, 'Viagem', 'Despesa', '✈️', '#c026d3'),
        (str(uuid.uuid4()), tenant_id, 'Show/Evento', 'Despesa', '🎤', '#a855f7'),
        (str(uuid.uuid4()), tenant_id, 'Hobby', 'Despesa', '🎨', '#d946ef'),
        (str(uuid.uuid4()), tenant_id, 'Pet', 'Despesa', '🐾', '#f59e0b'),
        (str(uuid.uuid4()), tenant_id, 'Presente', 'Despesa', '🎁', '#ec4899'),
        
        # Vestuário e Beleza
        (str(uuid.uuid4()), tenant_id, 'Roupas', 'Despesa', '👔', '#ec4899'),
        (str(uuid.uuid4()), tenant_id, 'Calçados', 'Despesa', '👟', '#db2777'),
        (str(uuid.uuid4()), tenant_id, 'Beleza', 'Despesa', '💅', '#f472b6'),
        (str(uuid.uuid4()), tenant_id, 'Cabelereiro', 'Despesa', '💇', '#be185d'),
        
        # Impostos e Taxas
        (str(uuid.uuid4()), tenant_id, 'Imposto', 'Despesa', '💸', '#dc2626'),
        (str(uuid.uuid4()), tenant_id, 'Taxa Bancária', 'Despesa', '🏦', '#b91c1c'),
        (str(uuid.uuid4()), tenant_id, 'Multa', 'Despesa', '⚠️', '#991b1b'),
        
        # Dívidas
        (str(uuid.uuid4()), tenant_id, 'Empréstimo', 'Despesa', '💳', '#7c3aed'),
        (str(uuid.uuid4()), tenant_id, 'Financiamento', 'Despesa', '🏦', '#6366f1'),
        (str(uuid.uuid4()), tenant_id, 'Cartão de Crédito', 'Despesa', '💳', '#8b5cf6'),
        
        # Outros
        (str(uuid.uuid4()), tenant_id, 'Doação', 'Despesa', '❤️', '#f43f5e'),
        (str(uuid.uuid4()), tenant_id, 'Outros', 'Despesa', '�', '#6b7280'),
    ]
    
    for cat in default_categories:
        db.execute(
            "INSERT OR IGNORE INTO categories (id, tenant_id, name, type, icon, color) VALUES (?, ?, ?, ?, ?, ?)",
            cat
        )
    
    db.commit()
    db.close()
    print("✅ Default data seeded!")

# =====================================================
# AUTHENTICATION DECORATORS
# =====================================================

def login_required(f):
    """Decorator para rotas que requerem autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa fazer login primeiro', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Retorna dados do usuário atual"""
    if 'user_id' not in session:
        return None
    
    db = get_db()
    user = db.execute(
        "SELECT id, tenant_id, email, name, is_admin, password_hash as password, phone FROM users WHERE id = ?",
        (session['user_id'],)
    ).fetchone()
    db.close()
    
    return dict(user) if user else None

# =====================================================
# TEMPLATE FILTERS
# =====================================================

@app.template_filter('brl')
def format_brl(value):
    """Formata número para padrão brasileiro (ex: 1234.56 -> 1.234,56)"""
    try:
        if value is None:
            return '0,00'
        
        # Converter para float se for string
        if isinstance(value, str):
            value = float(value)
        
        # Formatar com 2 casas decimais
        formatted = f"{float(value):,.2f}"
        
        # Substituir vírgula e ponto (formato americano -> brasileiro)
        formatted = formatted.replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')
        
        return formatted
    except (ValueError, TypeError):
        return '0,00'

# =====================================================
# AUTHENTICATION ROUTES
# =====================================================

@app.route('/')
def index():
    """Página inicial - Landing Page ou Dashboard"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    # Mostra landing page para visitantes
    try:
        return render_template('landing.html')
    except:
        # Fallback para login se landing.html não existir
        return redirect(url_for('login'))

@app.route('/test')
def test_page():
    """Página de teste do sistema"""
    return render_template('test_page.html')

@app.route('/test-edit-button')
def test_edit_button():
    """Página de teste do botão editar"""
    from flask import send_file
    return send_file('test_edit_button.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login de usuário"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email = ? AND active = 1",
            (email,)
        ).fetchone()
        db.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session.permanent = True  # Sessão permanente (30 dias)
            session['user_id'] = user['id']
            session['tenant_id'] = user['tenant_id']
            session['user_name'] = user['name']
            session['is_admin'] = user['is_admin']
            flash(f'Bem-vindo(a), {user["name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email ou senha incorretos', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Cadastro de novo usuário"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        db = get_db()
        
        # Verificar se email já existe
        existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            flash('Este email já está cadastrado', 'error')
            return render_template('register.html')
        
        # Pegar tenant padrão
        tenant = db.execute("SELECT id FROM tenants WHERE subdomain = 'default'").fetchone()
        tenant_id = tenant['id'] if tenant else str(uuid.uuid4())
        
        # Criar usuário
        user_id = str(uuid.uuid4())
        password_hash = generate_password_hash(password)
        
        db.execute(
            "INSERT INTO users (id, tenant_id, email, password_hash, name) VALUES (?, ?, ?, ?, ?)",
            (user_id, tenant_id, email, password_hash, name)
        )
        
        # Criar conta padrão
        account_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO accounts (id, user_id, tenant_id, name, type, initial_balance) VALUES (?, ?, ?, ?, ?, ?)",
            (account_id, user_id, tenant_id, 'Conta Principal', 'Corrente', 0)
        )
        
        db.commit()
        db.close()
        
        flash('Cadastro realizado com sucesso! Faça login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Logout do usuário"""
    session.clear()
    flash('Você saiu da sua conta', 'info')
    return redirect(url_for('login'))

@app.route('/offline.html')
def offline():
    """Página offline para PWA"""
    return render_template('offline.html')

@app.route('/settings')
@login_required
def settings():
    """Página de configurações do perfil"""
    user = get_current_user()
    return render_template('settings.html', user=user)

@app.route('/whatsapp-chat')
@login_required
def whatsapp_chat_page():
    """Página de chat WhatsApp"""
    return render_template('whatsapp_chat.html')

@app.route('/register-whatsapp')
def register_whatsapp_page():
    """Página de cadastro com WhatsApp"""
    return render_template('register_whatsapp.html')

# =====================================================
# API DE REGISTRO COM WHATSAPP
# =====================================================

@app.route('/api/register', methods=['POST'])
def api_register_with_whatsapp():
    """Registrar novo usuário com WhatsApp"""
    try:
        data = request.json
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        whatsapp = data.get('whatsapp', '').strip()
        password = data.get('password', '')
        
        # Validações
        if not name or not email or not whatsapp or not password:
            return jsonify({'error': 'Todos os campos são obrigatórios'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Senha deve ter no mínimo 6 caracteres'}), 400
        
        # Formatar WhatsApp
        phone = whatsapp.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        if not phone.startswith('+'):
            phone = '+' + phone
        
        db = get_db()
        
        # Verificar se email já existe
        existing_email = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing_email:
            return jsonify({'error': 'Este email já está cadastrado'}), 400
        
        # Verificar se WhatsApp já existe
        existing_phone = db.execute("SELECT id FROM users WHERE phone = ?", (phone,)).fetchone()
        if existing_phone:
            return jsonify({'error': 'Este WhatsApp já está cadastrado'}), 400
        
        # Pegar ou criar tenant padrão
        tenant = db.execute("SELECT id FROM tenants WHERE subdomain = 'default'").fetchone()
        if not tenant:
            tenant_id = str(uuid.uuid4())
            db.execute(
                "INSERT INTO tenants (id, name, subdomain) VALUES (?, ?, ?)",
                (tenant_id, 'Default', 'default')
            )
        else:
            tenant_id = tenant['id']
        
        # Criar usuário
        user_id = str(uuid.uuid4())
        password_hash = generate_password_hash(password)
        
        db.execute(
            """INSERT INTO users 
               (id, tenant_id, email, password_hash, name, phone, active) 
               VALUES (?, ?, ?, ?, ?, ?, 1)""",
            (user_id, tenant_id, email, password_hash, name, phone)
        )
        
        # Criar conta padrão
        account_id = str(uuid.uuid4())
        db.execute(
            """INSERT INTO accounts 
               (id, user_id, tenant_id, name, type, initial_balance) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (account_id, user_id, tenant_id, 'Conta Principal', 'Corrente', 0)
        )
        
        db.commit()
        db.close()
        
        print(f"✅ Novo usuário cadastrado via WhatsApp:")
        print(f"   Nome: {name}")
        print(f"   Email: {email}")
        print(f"   WhatsApp: {phone}")
        print(f"   User ID: {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Cadastro realizado com sucesso!',
            'user_id': user_id,
            'whatsapp': phone
        }), 201
        
    except Exception as e:
        print(f"❌ Erro ao registrar usuário: {str(e)}")
        return jsonify({'error': f'Erro ao cadastrar: {str(e)}'}), 500

# =====================================================
# API DE CONFIGURAÇÕES
# =====================================================

@app.route('/api/update-profile', methods=['POST'])
@login_required
def api_update_profile():
    """Atualizar informações do perfil"""
    try:
        data = request.json
        user = get_current_user()
        db = get_db()
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        
        if not name or not email:
            return jsonify({'success': False, 'message': 'Nome e email são obrigatórios'}), 400
        
        # Verifica se o email já está em uso por outro usuário
        existing = db.execute(
            'SELECT id FROM users WHERE email = ? AND id != ?',
            (email, user['id'])
        ).fetchone()
        
        if existing:
            return jsonify({'success': False, 'message': 'Email já está em uso'}), 400
        
        db.execute('''
            UPDATE users 
            SET name = ?, email = ?, phone = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (name, email, phone, user['id']))
        db.commit()
        
        return jsonify({'success': True, 'message': 'Perfil atualizado com sucesso'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/change-password', methods=['POST'])
@login_required
def api_change_password():
    """Alterar senha do usuário"""
    try:
        data = request.json
        user = get_current_user()
        db = get_db()
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        if not all([current_password, new_password, confirm_password]):
            return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios'}), 400
        
        if new_password != confirm_password:
            return jsonify({'success': False, 'message': 'As senhas não coincidem'}), 400
        
        if len(new_password) < 6:
            return jsonify({'success': False, 'message': 'A senha deve ter no mínimo 6 caracteres'}), 400
        
        # Verifica senha atual
        if not check_password_hash(user['password'], current_password):
            return jsonify({'success': False, 'message': 'Senha atual incorreta'}), 401
        
        # Atualiza senha
        new_password_hash = generate_password_hash(new_password)
        db.execute(
            'UPDATE users SET password = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (new_password_hash, user['id'])
        )
        db.commit()
        
        return jsonify({'success': True, 'message': 'Senha alterada com sucesso'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/notification-settings', methods=['GET', 'POST'])
@login_required
def api_notification_settings():
    """Gerenciar configurações de notificações"""
    try:
        user = get_current_user()
        db = get_db()
        
        if request.method == 'GET':
            # Buscar configurações atuais
            settings = db.execute('''
                SELECT 
                    email_enabled, whatsapp_enabled, push_enabled,
                    high_spending, bill_due, investment_update, weekly_report
                FROM notification_settings
                WHERE user_id = ?
            ''', (user['id'],)).fetchone()
            
            if not settings:
                # Criar configurações padrão
                db.execute('''
                    INSERT INTO notification_settings (user_id, email_enabled, whatsapp_enabled, push_enabled)
                    VALUES (?, 1, 1, 1)
                ''', (user['id'],))
                db.commit()
                
                return jsonify({
                    'email_enabled': True,
                    'whatsapp_enabled': True,
                    'push_enabled': True,
                    'high_spending': True,
                    'bill_due': True,
                    'investment_update': True,
                    'weekly_report': True
                })
            
            return jsonify(dict(settings))
        
        elif request.method == 'POST':
            data = request.json
            
            db.execute('''
                INSERT OR REPLACE INTO notification_settings (
                    user_id, email_enabled, whatsapp_enabled, push_enabled,
                    high_spending, bill_due, investment_update, weekly_report
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user['id'],
                data.get('email_enabled', True),
                data.get('whatsapp_enabled', True),
                data.get('push_enabled', True),
                data.get('high_spending', True),
                data.get('bill_due', True),
                data.get('investment_update', True),
                data.get('weekly_report', True)
            ))
            db.commit()
            
            return jsonify({'success': True, 'message': 'Configurações salvas'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/appearance-settings', methods=['GET', 'POST'])
@login_required
def api_appearance_settings():
    """Gerenciar configurações de aparência"""
    try:
        user = get_current_user()
        db = get_db()
        
        if request.method == 'GET':
            settings = db.execute('''
                SELECT dark_mode, compact_dashboard, show_balance
                FROM user_preferences
                WHERE user_id = ?
            ''', (user['id'],)).fetchone()
            
            if not settings:
                return jsonify({
                    'dark_mode': False,
                    'compact_dashboard': False,
                    'show_balance': True
                })
            
            return jsonify(dict(settings))
        
        elif request.method == 'POST':
            data = request.json
            
            # Verificar se registro existe
            existing = db.execute('SELECT id FROM user_preferences WHERE user_id = ?', (user['id'],)).fetchone()
            
            if existing:
                db.execute('''
                    UPDATE user_preferences 
                    SET dark_mode = ?, compact_dashboard = ?, show_balance = ?
                    WHERE user_id = ?
                ''', (
                    data.get('dark_mode', False),
                    data.get('compact_dashboard', False),
                    data.get('show_balance', True),
                    user['id']
                ))
            else:
                db.execute('''
                    INSERT INTO user_preferences (
                        user_id, tenant_id, dark_mode, compact_dashboard, show_balance
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    user['id'],
                    user['tenant_id'],
                    data.get('dark_mode', False),
                    data.get('compact_dashboard', False),
                    data.get('show_balance', True)
                ))
            db.commit()
            
            return jsonify({'success': True, 'message': 'Preferências salvas'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/privacy-settings', methods=['GET', 'POST'])
@login_required
def api_privacy_settings():
    """Gerenciar configurações de privacidade"""
    try:
        user = get_current_user()
        db = get_db()
        
        if request.method == 'GET':
            settings = db.execute('''
                SELECT save_history, allow_cookies
                FROM user_preferences
                WHERE user_id = ?
            ''', (user['id'],)).fetchone()
            
            if not settings:
                return jsonify({
                    'save_history': True,
                    'allow_cookies': True
                })
            
            return jsonify(dict(settings))
        
        elif request.method == 'POST':
            data = request.json
            
            # Verificar se registro existe
            existing = db.execute('SELECT id FROM user_preferences WHERE user_id = ?', (user['id'],)).fetchone()
            
            if existing:
                db.execute('''
                    UPDATE user_preferences 
                    SET save_history = ?, allow_cookies = ?
                    WHERE user_id = ?
                ''', (
                    data.get('save_history', True),
                    data.get('allow_cookies', True),
                    user['id']
                ))
            else:
                db.execute('''
                    INSERT INTO user_preferences (
                        user_id, tenant_id, save_history, allow_cookies
                    ) VALUES (?, ?, ?, ?)
                ''', (
                    user['id'],
                    user['tenant_id'],
                    data.get('save_history', True),
                    data.get('allow_cookies', True)
                ))
            db.commit()
            
            return jsonify({'success': True, 'message': 'Configurações de privacidade salvas'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# =====================================================
# DASHBOARD
# =====================================================

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal (estilo nik0finance melhorado)"""
    user = get_current_user()
    db = get_db()
    
    # Filtros
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    
    # Resumo financeiro
    summary = db.execute("""
        SELECT 
            COALESCE(SUM(CASE WHEN type = 'Receita' AND is_fixed = 1 THEN value ELSE 0 END), 0) as renda_fixa,
            COALESCE(SUM(CASE WHEN type = 'Receita' AND is_fixed = 0 THEN value ELSE 0 END), 0) as renda_variavel,
            COALESCE(SUM(CASE WHEN type = 'Receita' THEN value ELSE 0 END), 0) as renda_total,
            COALESCE(SUM(CASE WHEN type = 'Despesa' AND is_fixed = 1 THEN value ELSE 0 END), 0) as custo_fixo,
            COALESCE(SUM(CASE WHEN type = 'Despesa' AND is_fixed = 0 THEN value ELSE 0 END), 0) as custo_variavel,
            COALESCE(SUM(CASE WHEN type = 'Despesa' THEN value ELSE 0 END), 0) as custo_total
        FROM transactions
        WHERE user_id = ? AND tenant_id = ? AND status = 'Pago'
        AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
    """, (user['id'], user['tenant_id'], str(year), f"{month:02d}")).fetchone()
    
    summary_dict = dict(summary) if summary else {
        'renda_fixa': 0, 'renda_variavel': 0, 'renda_total': 0,
        'custo_fixo': 0, 'custo_variavel': 0, 'custo_total': 0,
        'saldo_mensal': 0
    }
    if summary:
        summary_dict['saldo_mensal'] = summary_dict['renda_total'] - summary_dict['custo_total']
    
    # Transações de receita
    rendas = db.execute("""
        SELECT t.*, c.name as category_name, c.icon as category_icon, c.color as category_color,
               a.name as account_name
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        LEFT JOIN accounts a ON t.account_id = a.id
        WHERE t.user_id = ? AND t.tenant_id = ? AND t.type = 'Receita'
        AND strftime('%Y', t.date) = ? AND strftime('%m', t.date) = ?
        ORDER BY t.date DESC
    """, (user['id'], user['tenant_id'], str(year), f"{month:02d}")).fetchall()
    
    # Transações de despesa
    custos = db.execute("""
        SELECT t.*, c.name as category_name, c.icon as category_icon, c.color as category_color,
               a.name as account_name, card.name as card_name
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        LEFT JOIN accounts a ON t.account_id = a.id
        LEFT JOIN cards card ON t.card_id = card.id
        WHERE t.user_id = ? AND t.tenant_id = ? AND t.type = 'Despesa'
        AND strftime('%Y', t.date) = ? AND strftime('%m', t.date) = ?
        ORDER BY t.date DESC
    """, (user['id'], user['tenant_id'], str(year), f"{month:02d}")).fetchall()
    
    # Períodos disponíveis para filtro
    periods = db.execute("""
        SELECT DISTINCT strftime('%Y', date) as year, strftime('%m', date) as month
        FROM transactions
        WHERE user_id = ? AND tenant_id = ?
        ORDER BY year DESC, month DESC
    """, (user['id'], user['tenant_id'])).fetchall()
    
    # Saldos das contas
    accounts = db.execute("""
        SELECT * FROM v_account_balances
        WHERE user_id = ? AND tenant_id = ?
    """, (user['id'], user['tenant_id'])).fetchall()
    
    # Categorias para o formulário de adicionar transação
    categories = db.execute("""
        SELECT * FROM categories
        WHERE tenant_id = ?
        ORDER BY type, name
    """, (user['tenant_id'],)).fetchall()
    
    # Cartões de crédito para o formulário de adicionar transação
    cards = db.execute("""
        SELECT id, name, limit_amount, COALESCE(used_limit, 0) as used_limit
        FROM cards
        WHERE user_id = ? AND tenant_id = ? AND active = 1
        ORDER BY name
    """, (user['id'], user['tenant_id'])).fetchall()
    
    # Próximas parcelas a vencer (próximos 30 dias)
    upcoming_installments = []
    
    # Resumo de Investimentos (APENAS ATIVOS)
    investments_summary = db.execute("""
        SELECT 
            COUNT(*) as total_investments,
            COALESCE(SUM(amount), 0) as total_invested,
            COALESCE(SUM(current_value), 0) as total_current,
            MAX(created_at) as last_update
        FROM investments
        WHERE user_id = ? AND tenant_id = ? 
        AND (investment_status = 'active' OR investment_status IS NULL)
    """, (user['id'], user['tenant_id'])).fetchone()
    
    inv_summary = {
        'total_investments': 0,
        'total_invested': 0,
        'total_current': 0,
        'profit_loss': 0,
        'profit_percent': 0,
        'last_update': None
    }
    
    if investments_summary and investments_summary['total_investments'] > 0:
        inv_summary = dict(investments_summary)
        inv_summary['profit_loss'] = inv_summary['total_current'] - inv_summary['total_invested']
        inv_summary['profit_percent'] = (inv_summary['profit_loss'] / inv_summary['total_invested'] * 100) if inv_summary['total_invested'] > 0 else 0
    
    # === DADOS PARA GRÁFICOS ===
    
    # Gráfico 1: Custos por categoria (mês atual)
    custos_por_categoria_data = db.execute("""
        SELECT c.name, SUM(t.value) as total
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ? AND t.tenant_id = ? AND t.type = 'Despesa' AND t.status = 'Pago'
        AND strftime('%Y', t.date) = ? AND strftime('%m', t.date) = ?
        GROUP BY c.name
        ORDER BY total DESC
        LIMIT 10
    """, (user['id'], user['tenant_id'], str(year), f"{month:02d}")).fetchall()
    
    custos_por_categoria = {row['name']: float(row['total']) for row in custos_por_categoria_data}
    
    # Gráfico 2: Evolução mensal (últimos 6 meses)
    evolucao_mensal = []
    meses_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    for i in range(5, -1, -1):
        mes_ref = month - i
        ano_ref = year
        
        if mes_ref <= 0:
            mes_ref += 12
            ano_ref -= 1
        
        dados_mes = db.execute("""
            SELECT 
                COALESCE(SUM(CASE WHEN type = 'Receita' THEN value ELSE 0 END), 0) as renda,
                COALESCE(SUM(CASE WHEN type = 'Despesa' THEN value ELSE 0 END), 0) as custo
            FROM transactions
            WHERE user_id = ? AND tenant_id = ? AND status = 'Pago'
            AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
        """, (user['id'], user['tenant_id'], str(ano_ref), f"{mes_ref:02d}")).fetchone()
        
        renda_mes = float(dados_mes['renda']) if dados_mes else 0
        custo_mes = float(dados_mes['custo']) if dados_mes else 0
        
        evolucao_mensal.append({
            'mes': meses_nomes[mes_ref - 1],
            'renda': renda_mes,
            'custo': custo_mes,
            'saldo': renda_mes - custo_mes
        })
    
    db.close()
    
    return render_template('dashboard.html',
                         user=user,
                         summary=summary_dict,
                         rendas=[dict(r) for r in rendas],
                         custos=[dict(c) for c in custos],
                         periods=[dict(p) for p in periods],
                         accounts=[dict(a) for a in accounts],
                         categories=[dict(c) for c in categories],
                         cards=[dict(card) for card in cards],
                         upcoming_installments=upcoming_installments,
                         investments_summary=inv_summary,
                         current_year=year,
                         current_month=month,
                         custos_por_categoria=custos_por_categoria,
                         evolucao_mensal=evolucao_mensal)

@app.route('/transactions')
@login_required
def all_transactions():
    """Página com TODAS as transações com filtros"""
    user = get_current_user()
    db = get_db()
    
    # Pegar filtros da query string
    type_filter = request.args.get('type', '')
    category_filter = request.args.get('category', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    # Montar query base
    query = """
        SELECT 
            t.id,
            t.description,
            t.value,
            t.type,
            t.date,
            t.account_id,
            t.category_id,
            t.is_fixed,
            t.card_id,
            c.name as category_name,
            c.icon as category_icon,
            cards.name as card_name
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        LEFT JOIN cards ON t.card_id = cards.id
        WHERE t.user_id = ? AND t.tenant_id = ?
    """
    
    params = [user['id'], user['tenant_id']]
    
    # Aplicar filtros
    if type_filter:
        query += " AND t.type = ?"
        params.append(type_filter)
    
    if category_filter:
        query += " AND t.category_id = ?"
        params.append(category_filter)
    
    if start_date:
        query += " AND t.date >= ?"
        params.append(start_date)
    
    if end_date:
        query += " AND t.date <= ?"
        params.append(end_date)
    
    query += " ORDER BY t.date DESC, t.created_at DESC"
    
    transactions = db.execute(query, params).fetchall()
    
    # Calcular totais
    total_receitas = sum(float(t['value']) for t in transactions if t['type'] == 'Receita')
    total_despesas = sum(float(t['value']) for t in transactions if t['type'] == 'Despesa')
    total_transactions = len(transactions)
    
    # Buscar categorias para o filtro
    categories = db.execute("""
        SELECT id, name, icon, type FROM categories
        WHERE tenant_id = ? AND parent_id IS NULL
        ORDER BY type, name
    """, (user['tenant_id'],)).fetchall()
    
    # Buscar contas para o modal de edição
    accounts = db.execute("""
        SELECT id, name FROM accounts
        WHERE user_id = ? AND tenant_id = ?
        ORDER BY name
    """, (user['id'], user['tenant_id'])).fetchall()
    
    db.close()
    
    return render_template('all_transactions.html',
                         transactions=[dict(t) for t in transactions],
                         total_transactions=total_transactions,
                         total_receitas=total_receitas,
                         total_despesas=total_despesas,
                         categories=[dict(c) for c in categories],
                         accounts=[dict(a) for a in accounts])

# =====================================================
# ACCOUNTS (CONTAS BANCÁRIAS)
# =====================================================

@app.route('/accounts')
@login_required
def accounts():
    """Lista todas as contas"""
    user = get_current_user()
    db = get_db()
    
    accounts = db.execute("""
        SELECT * FROM v_account_balances
        WHERE user_id = ? AND tenant_id = ?
        ORDER BY name ASC
    """, (user['id'], user['tenant_id'])).fetchall()
    

    # Calcular saldo total de todas as contas
    total_balance = sum(float(a['balance']) if a['balance'] else 0 for a in accounts)
    db.close()
    
    return render_template('accounts.html',
                         accounts=[dict(a) for a in accounts],
                         total_balance=total_balance)

@app.route('/accounts/add', methods=['POST'])
@login_required
def add_account():
    """Adiciona nova conta"""
    try:
        user = get_current_user()
        
        # Log dos dados recebidos
        print(f"[DEBUG] Form data: {dict(request.form)}")
        print(f"[DEBUG] JSON data: {request.get_json()}")
        print(f"[DEBUG] Content-Type: {request.content_type}")
        
        # Tentar pegar dados do form ou JSON
        if request.is_json:
            data = request.get_json()
            name = data.get('name')
            acc_type = data.get('type', 'Corrente')
            bank = data.get('bank', '')
            initial_balance = float(data.get('initial_balance', 0) or 0)
        else:
            name = request.form.get('name')
            acc_type = request.form.get('type', 'Corrente')
            bank = request.form.get('bank', '')
            initial_balance = float(request.form.get('initial_balance', 0) or 0)
        
        print(f"[DEBUG] Parsed - name: {name}, type: {acc_type}, bank: {bank}, balance: {initial_balance}")
        
        if not name:
            raise ValueError("Nome da conta é obrigatório")
        
        db = get_db()
        account_id = str(uuid.uuid4())
        
        db.execute("""
            INSERT INTO accounts (id, user_id, tenant_id, name, type, bank, initial_balance, current_balance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (account_id, user['id'], user['tenant_id'], name, acc_type, bank, initial_balance, initial_balance))
        
        db.commit()
        db.close()
        
        # Se for requisição AJAX, retorna JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes.accept_json:
            return jsonify({
                'success': True,
                'message': f'Conta "{name}" criada com sucesso!',
                'account_id': account_id
            })
        
        flash(f'Conta "{name}" criada com sucesso!', 'success')
        return redirect(url_for('accounts'))
    except Exception as e:
        print(f"[ERRO] add_account: {e}")
        import traceback
        traceback.print_exc()
        
        # Se for requisição AJAX, retorna JSON com erro
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes.accept_json:
            return jsonify({
                'success': False,
                'message': f'Erro ao criar conta: {str(e)}'
            }), 500
        
        flash(f'Erro ao criar conta: {str(e)}', 'error')
        return redirect(url_for('accounts'))

@app.route('/accounts/edit', methods=['POST'])
@login_required
def edit_account():
    """Edita uma conta existente"""
    try:
        user = get_current_user()
        
        account_id = request.form.get('account_id')
        name = request.form.get('name')
        acc_type = request.form.get('type')
        initial_balance = float(request.form.get('initial_balance', 0) or 0)
        
        db = get_db()
        
        # Obter saldo inicial antigo para recalcular
        old_account = db.execute("""
            SELECT initial_balance, current_balance FROM accounts 
            WHERE id = ? AND user_id = ?
        """, (account_id, user['id'])).fetchone()
        
        if old_account:
            # Calcular a diferença e ajustar o saldo atual
            balance_diff = initial_balance - old_account['initial_balance']
            new_current_balance = old_account['current_balance'] + balance_diff
            
            db.execute("""
                UPDATE accounts 
                SET name = ?, type = ?, initial_balance = ?, current_balance = ?
                WHERE id = ? AND user_id = ?
            """, (name, acc_type, initial_balance, new_current_balance, account_id, user['id']))
            
            db.commit()
            
            # Se for requisição AJAX, retorna JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes.accept_json:
                return jsonify({
                    'success': True,
                    'message': f'Conta "{name}" atualizada com sucesso!'
                })
            
            flash(f'Conta "{name}" atualizada com sucesso!', 'success')
        else:
            # Se for requisição AJAX, retorna JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes.accept_json:
                return jsonify({
                    'success': False,
                    'message': 'Conta não encontrada!'
                }), 404
            
            flash('Conta não encontrada!', 'error')
        
        db.close()
    except Exception as e:
        print(f"[ERRO] edit_account: {e}")
        import traceback
        traceback.print_exc()
        
        # Se for requisição AJAX, retorna JSON com erro
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes.accept_json:
            return jsonify({
                'success': False,
                'message': f'Erro ao editar conta: {str(e)}'
            }), 500
        
        flash(f'Erro ao editar conta: {str(e)}', 'error')
    return redirect(url_for('accounts'))

# =====================================================
# CARDS (CARTÕES DE CRÉDITO)
# =====================================================

@app.route('/cards')
@login_required
def cards():
    """Lista todos os cartões"""
    user = get_current_user()
    db = get_db()
    
    cards_list = db.execute("""
        SELECT c.*, a.name as account_name
        FROM cards c
        LEFT JOIN accounts a ON c.account_id = a.id
        WHERE c.user_id = ? AND c.tenant_id = ? AND c.active = 1
        ORDER BY c.name
    """, (user['id'], user['tenant_id'])).fetchall()
    
    # Pegar contas para o form
    accounts = db.execute("""
        SELECT id, name FROM accounts
        WHERE user_id = ? AND tenant_id = ? AND active = 1
    """, (user['id'], user['tenant_id'])).fetchall()
    
    db.close()
    
    return render_template('cards.html',
                         user=user,
                         cards=[dict(c) for c in cards_list],
                         accounts=[dict(a) for a in accounts])

@app.route('/cards/add', methods=['POST'])
@login_required
def add_card():
    """Adiciona novo cartão"""
    user = get_current_user()
    
    account_id = request.form.get('account_id')
    name = request.form.get('name')
    last_digits = request.form.get('last_digits')
    brand = request.form.get('brand')
    limit_amount = float(request.form.get('limit_amount', 0))
    closing_day = int(request.form.get('closing_day'))
    due_day = int(request.form.get('due_day'))
    
    db = get_db()
    card_id = str(uuid.uuid4())
    
    db.execute("""
        INSERT INTO cards (id, account_id, user_id, tenant_id, name, last_digits, brand, limit_amount, closing_day, due_day)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (card_id, account_id, user['id'], user['tenant_id'], name, last_digits, brand, limit_amount, closing_day, due_day))
    
    db.commit()
    db.close()
    
    flash(f'Cartão "{name}" adicionado com sucesso!', 'success')
    return redirect(url_for('cards'))

@app.route('/cards/edit', methods=['POST'])
@login_required
def edit_card():
    """Edita um cartão existente"""
    user = get_current_user()
    
    card_id = request.form.get('card_id')
    account_id = request.form.get('account_id')
    name = request.form.get('name')
    last_digits = request.form.get('last_digits')
    brand = request.form.get('brand')
    limit_amount = float(request.form.get('limit_amount', 0))
    closing_day = int(request.form.get('closing_day'))
    due_day = int(request.form.get('due_day'))
    
    db = get_db()
    
    db.execute("""
        UPDATE cards 
        SET account_id = ?, name = ?, last_digits = ?, brand = ?, 
            limit_amount = ?, closing_day = ?, due_day = ?
        WHERE id = ? AND user_id = ?
    """, (account_id, name, last_digits, brand, limit_amount, closing_day, due_day, card_id, user['id']))
    
    db.commit()
    db.close()
    
    flash(f'Cartão "{name}" atualizado com sucesso!', 'success')
    return redirect(url_for('cards'))

# =====================================================
# IMPORTAÇÃO DE EXTRATOS
# =====================================================

@app.route('/api/accounts-list')
@login_required
def api_accounts_list():
    """API para listar contas em JSON"""
    user = get_current_user()
    db = get_db()
    
    accounts = db.execute("""
        SELECT id, name, type, current_balance
        FROM accounts
        WHERE user_id = ? AND tenant_id = ?
        ORDER BY name ASC
    """, (user['id'], user['tenant_id'])).fetchall()
    
    db.close()
    
    return jsonify({
        'success': True,
        'accounts': [dict(a) for a in accounts]
    })

@app.route('/api/cards-list')
@login_required
def api_cards_list():
    """API para listar cartões de crédito em JSON"""
    user = get_current_user()
    db = get_db()
    
    cards = db.execute("""
        SELECT c.id, c.name, c.last_digits, c.brand, c.limit_amount, 
               COALESCE(c.used_limit, 0) as used_limit,
               a.name as account_name
        FROM cards c
        LEFT JOIN accounts a ON c.account_id = a.id
        WHERE c.user_id = ? AND c.tenant_id = ? AND c.active = 1
        ORDER BY c.name ASC
    """, (user['id'], user['tenant_id'])).fetchall()
    
    db.close()
    
    return jsonify({
        'success': True,
        'cards': [dict(c) for c in cards]
    })

@app.route('/api/cards', methods=['GET'])
@login_required
def api_cards():
    """API padrão para cartões (usada pelo frontend)"""
    try:
        user = get_current_user()
        db = get_db()
        
        cards = db.execute("""
            SELECT 
                c.id, 
                c.name, 
                c.last_digits, 
                c.brand, 
                c.limit_amount, 
                COALESCE(c.used_limit, 0) as used_limit,
                c.closing_day,
                c.due_day,
                c.active,
                a.name as account_name
            FROM cards c
            LEFT JOIN accounts a ON c.account_id = a.id
            WHERE c.user_id = ? AND c.tenant_id = ?
            ORDER BY c.name ASC
        """, (user['id'], user['tenant_id'])).fetchall()
        
        db.close()
        
        # Converter para dict e adicionar campos calculados
        cards_list = []
        for c in cards:
            card_dict = dict(c)
            card_dict['limit'] = card_dict.get('limit_amount', 0)
            card_dict['available_limit'] = (card_dict.get('limit_amount', 0) - card_dict.get('used_limit', 0))
            cards_list.append(card_dict)
        
        return jsonify({
            'success': True,
            'cards': cards_list
        })
    except Exception as e:
        print(f"❌ Erro em /api/cards: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'cards': []
        }), 500

@app.route('/api/categories', methods=['GET'])
@login_required
def api_categories():
    """API para listar categorias"""
    user = get_current_user()
    db = get_db()
    
    categories = db.execute("""
        SELECT id, name, type, icon, color
        FROM categories
        WHERE tenant_id = ?
        ORDER BY type, name ASC
    """, (user['tenant_id'],)).fetchall()
    
    db.close()
    
    return jsonify({
        'success': True,
        'categories': [dict(c) for c in categories]
    })

@app.route('/importar-extrato')
@login_required
def importar_extrato_page():
    """Página de importação de extratos bancários e faturas"""
    user = get_current_user()
    return render_template('importar_extrato.html', user=user)

# =====================================================
# INSTALLMENTS (PARCELAMENTOS)
# =====================================================

@app.route('/test-apis')
@login_required
def test_apis_page():
    """Página de teste de APIs"""
    return render_template('test_apis.html')

@app.route('/debug-apis')
@login_required
def debug_apis_page():
    """Página de debug detalhado das APIs"""
    return render_template('debug_apis.html')

@app.route('/recurring')
@login_required
def recurring_page():
    """Página de transações recorrentes"""
    user = get_current_user()
    return render_template('recurring.html', user=user)

@app.route('/installments')
@login_required
def installments_page():
    """Página de parcelamentos"""
    user = get_current_user()
    status = request.args.get('status', 'active')
    
    db = get_db()
    
    # Buscar parcelamentos
    query = """
        SELECT * FROM v_installments_summary
        WHERE user_id = ? AND tenant_id = ?
    """
    params = [user['id'], user['tenant_id']]
    
    if status != 'all':
        query += " AND current_status = ?"
        params.append(status)
    
    query += " ORDER BY first_due_date DESC"
    
    installments = db.execute(query, params).fetchall()
    
    # Buscar contas, cartões e categorias para o modal
    accounts = db.execute("""
        SELECT id, name FROM accounts
        WHERE user_id = ? AND tenant_id = ? AND active = 1
    """, (user['id'], user['tenant_id'])).fetchall()
    
    cards = db.execute("""
        SELECT id, name FROM cards
        WHERE user_id = ? AND tenant_id = ? AND active = 1
    """, (user['id'], user['tenant_id'])).fetchall()
    
    categories = db.execute("""
        SELECT id, name, icon FROM categories
        WHERE type = 'Despesa'
    """).fetchall()
    
    db.close()
    
    return render_template('installments.html',
                         user=user,
                         installments=[dict(i) for i in installments],
                         accounts=[dict(a) for a in accounts],
                         cards=[dict(c) for c in cards],
                         categories=[dict(cat) for cat in categories],
                         status=status,
                         now=datetime.now(),
                         timedelta=timedelta)

@app.route('/installments/<installment_id>')
@login_required
def installment_details(installment_id):
    """Detalhes e cronograma de um parcelamento"""
    user = get_current_user()
    
    db = get_db()
    
    # Buscar parcelamento
    installment = db.execute("""
        SELECT * FROM v_installments_summary
        WHERE id = ? AND user_id = ? AND tenant_id = ?
    """, (installment_id, user['id'], user['tenant_id'])).fetchone()
    
    if not installment:
        flash('Parcelamento não encontrado', 'error')
        return redirect(url_for('installments_page'))
    
    # Buscar cronograma
    schedule = db.execute("""
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
    """, (installment_id,)).fetchall()
    
    # Calcular resumo
    paid_installments = sum(1 for item in schedule if item['status'] == 'Pago')
    pending_installments = sum(1 for item in schedule if item['status'] == 'Pendente')
    total_paid = sum(item['value'] for item in schedule if item['status'] == 'Pago')
    total_pending = sum(item['value'] for item in schedule if item['status'] == 'Pendente')
    
    summary = {
        'total_installments': len(schedule),
        'paid_installments': paid_installments,
        'pending_installments': pending_installments,
        'total_paid': total_paid,
        'total_pending': total_pending
    }
    
    db.close()
    
    return render_template('installment_details.html',
                         user=user,
                         installment=dict(installment),
                         schedule=[dict(s) for s in schedule],
                         summary=summary)

@app.route('/installments/create', methods=['POST'])
@login_required
def create_installment_web():
    """Cria parcelamento via formulário web"""
    user = get_current_user()
    
    try:
        description = request.form.get('description')
        total_amount = float(request.form.get('total_amount'))
        installment_count = int(request.form.get('installment_count'))
        interest_rate = float(request.form.get('interest_rate', 0))
        first_due_date = request.form.get('first_due_date')
        account_id = request.form.get('account_id') or None
        card_id = request.form.get('card_id') or None
        category_id = request.form.get('category_id') or None
        
        # Chamar API REST
        import requests
        response = requests.post(f'http://localhost:5000/api/installments', json={
            'description': description,
            'total_amount': total_amount,
            'installment_count': installment_count,
            'interest_rate': interest_rate,
            'first_due_date': first_due_date,
            'account_id': account_id,
            'card_id': card_id,
            'category_id': category_id
        }, cookies=request.cookies)
        
        if response.status_code == 201:
            data = response.json()
            flash(data['message'], 'success')
        else:
            error_data = response.json()
            flash(f'Erro: {error_data.get("error", "Falha ao criar parcelamento")}', 'error')
    
    except Exception as e:
        flash(f'Erro ao criar parcelamento: {str(e)}', 'error')
    
    return redirect(url_for('installments_page'))

# =====================================================
# INVESTMENTS (INVESTIMENTOS)
# =====================================================

@app.route('/investments')
@login_required
def investments_page():
    """Página de listagem de investimentos"""
    try:
        user = get_current_user()
        db = get_db()
        
        # Buscar todos os investimentos ativos
        investments = db.execute("""
            SELECT 
                id,
                name,
                investment_type,
                amount,
                current_value,
                investment_status,
                created_at,
                quantity,
                (current_value - amount) as profit,
                CASE 
                    WHEN amount > 0 THEN ((current_value - amount) / amount * 100)
                    ELSE 0
                END as profit_percent
            FROM investments
            WHERE user_id = ? AND tenant_id = ? AND (investment_status = 'active' OR investment_status IS NULL)
            ORDER BY current_value DESC
        """, (user['id'], user['tenant_id'])).fetchall()
        
        # Organizar investimentos por tipo
        investments_by_type = {
            'acao': [],
            'cripto': [],
            'tesouro': [],
            'etf': [],
            'fii': [],
            'outros': []
        }
        
        all_investments_list = []
        
        for inv in investments:
            inv_dict = dict(inv)
            all_investments_list.append(inv_dict)
            inv_type = inv_dict.get('investment_type', '').lower()
            
            if 'acao' in inv_type or 'stock' in inv_type:
                investments_by_type['acao'].append(inv_dict)
            elif 'cripto' in inv_type or 'crypto' in inv_type:
                investments_by_type['cripto'].append(inv_dict)
            elif 'tesouro' in inv_type or 'treasury' in inv_type:
                investments_by_type['tesouro'].append(inv_dict)
            elif 'etf' in inv_type:
                investments_by_type['etf'].append(inv_dict)
            elif 'fii' in inv_type or 'fundo' in inv_type:
                investments_by_type['fii'].append(inv_dict)
            else:
                investments_by_type['outros'].append(inv_dict)
        
        # Calcular resumo geral com valores seguros
        summary = {
            'total_investments': len(all_investments_list),
            'total_invested': sum(float(inv.get('amount', 0) or 0) for inv in all_investments_list),
            'total_current': sum(float(inv.get('current_value', 0) or 0) for inv in all_investments_list),
        }
        
        summary['profit_loss'] = summary['total_current'] - summary['total_invested']
        summary['profit_percent'] = (summary['profit_loss'] / summary['total_invested'] * 100) if summary['total_invested'] > 0 else 0
        
        # Última atualização
        last_update = db.execute("""
            SELECT MAX(created_at) as last_update FROM investments WHERE user_id = ?
        """, (user['id'],)).fetchone()
        
        summary['last_update'] = last_update['last_update'] if last_update and last_update['last_update'] else None
        
        db.close()
        
        return render_template('investments.html', 
                             user=user,
                             investments_by_type=investments_by_type,
                             all_investments=all_investments_list,
                             summary=summary)
    
    except Exception as e:
        print(f"❌ Erro na página de investimentos: {e}")
        import traceback
        traceback.print_exc()
        
        # Retornar com dados vazios em caso de erro
        return render_template('investments.html', 
                             user=get_current_user(),
                             investments_by_type={'acao': [], 'cripto': [], 'tesouro': [], 'etf': [], 'fii': [], 'outros': []},
                             all_investments=[],
                             summary={
                                 'total_investments': 0,
                                 'total_invested': 0,
                                 'total_current': 0,
                                 'profit_loss': 0,
                                 'profit_percent': 0,
                                 'last_update': None
                             })

@app.route('/investments/add', methods=['POST'])
@login_required
def add_investment():
    """Adiciona novo investimento (compra ou venda)"""
    user = get_current_user()
    
    operation_type = request.form.get('operation_type', 'compra')  # compra ou venda
    name = request.form.get('name')
    investment_type = request.form.get('investment_type')
    amount = float(request.form.get('amount', 0))
    current_value = float(request.form.get('current_value', 0))
    quantity = float(request.form.get('quantity', 1))
    other_costs = float(request.form.get('other_costs', 0))
    start_date_str = request.form.get('start_date')
    
    # Usar data fornecida ou data atual
    if start_date_str:
        start_date = start_date_str
    else:
        start_date = datetime.now().strftime('%Y-%m-%d')
    
    db = get_db()
    
    try:
        # SEMPRE CRIAR UM NOVO REGISTRO para cada compra
        # Isso permite ter múltiplas linhas do mesmo ativo com preços diferentes
        
        if operation_type == 'venda':
            # Para venda: buscar investimentos do mesmo ativo para reduzir
            existing = db.execute("""
                SELECT id, amount, current_value, quantity FROM investments 
                WHERE user_id = ? AND tenant_id = ? AND name = ? AND investment_type = ? AND investment_status = 'active'
                ORDER BY start_date ASC
                LIMIT 1
            """, (user['id'], user['tenant_id'], name, investment_type)).fetchone()
            
            if not existing:
                flash('Erro: Não é possível vender um ativo que você não possui!', 'error')
                db.close()
                return redirect(url_for('investments_page'))
            
            # Reduzir quantidade do investimento mais antigo
            new_quantity = existing['quantity'] - quantity
            new_amount = existing['amount'] - amount
            new_current_value = existing['current_value'] - current_value
            
            if new_quantity <= 0 or new_current_value <= 0:
                # Vendeu tudo deste registro - marcar como vendido
                db.execute("""
                    UPDATE investments 
                    SET current_value = 0, quantity = 0, investment_status = 'sold', updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (existing['id'],))
                flash_msg = f'Venda total registrada: {name} - R$ {current_value:.2f}'
            else:
                # Vendeu parcialmente
                db.execute("""
                    UPDATE investments 
                    SET amount = ?, current_value = ?, quantity = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (new_amount, new_current_value, new_quantity, existing['id']))
                flash_msg = f'Venda parcial registrada: {name} - R$ {current_value:.2f}'
        else:
            # COMPRA: Verificar se já existe posição do mesmo ativo (APENAS NOME, ignora tipo)
            existing = db.execute("""
                SELECT id, amount, current_value, quantity, start_date, investment_type FROM investments 
                WHERE user_id = ? AND tenant_id = ? AND name = ? AND investment_status = 'active'
                ORDER BY start_date ASC
                LIMIT 1
            """, (user['id'], user['tenant_id'], name)).fetchone()
            
            # Buscar cotação atual para calcular current_value
            from services.api_connectors import InvestmentAPIFactory
            
            try:
                print(f"🔍 Buscando cotação atual de {name}...")
                api_factory = InvestmentAPIFactory()
                market_data = api_factory.get_stock_with_fundamentals(name)
                
                if market_data and market_data.get('price'):
                    # Cotação atual × quantidade TOTAL
                    new_total_quantity = (existing['quantity'] if existing else 0) + quantity
                    real_current_value = market_data['price'] * new_total_quantity
                    print(f"✅ {name}: Qtd {new_total_quantity} × R$ {market_data['price']:.2f} = R$ {real_current_value:.2f}")
                else:
                    # Se não conseguir buscar, usa o valor investido
                    real_current_value = (existing['current_value'] if existing else 0) + amount
                    print(f"⚠️ Não foi possível buscar cotação de {name}, usando valor investido")
            except Exception as e:
                print(f"❌ Erro ao buscar cotação: {e}")
                real_current_value = (existing['current_value'] if existing else 0) + amount
            
            if existing:
                # JÁ EXISTE - SOMAR na posição existente
                new_quantity = existing['quantity'] + quantity
                new_amount = existing['amount'] + amount
                
                print(f"🔄 ATUALIZANDO posição existente:")
                print(f"   ID: {existing['id']}")
                print(f"   Nome: {name}")
                print(f"   Tipo antigo: {existing['investment_type']} → Tipo novo: {investment_type}")
                print(f"   Antes: {existing['quantity']} unidades - R$ {existing['amount']:.2f}")
                print(f"   Adicionando: {quantity} unidades - R$ {amount:.2f}")
                print(f"   Depois: {new_quantity} unidades - R$ {new_amount:.2f}")
                
                db.execute("""
                    UPDATE investments 
                    SET amount = ?, current_value = ?, quantity = ?, investment_type = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (new_amount, real_current_value, new_quantity, investment_type, existing['id']))
                
                flash_msg = f'✅ Posição atualizada: {name} - Total {new_quantity} unidade(s) - Valor médio R$ {(new_amount/new_quantity):.2f}'
            else:
                # NÃO EXISTE - CRIAR NOVO
                print(f"➕ CRIANDO nova posição:")
                print(f"   Nome: {name}")
                print(f"   Tipo: {investment_type}")
                print(f"   Quantidade: {quantity} unidades")
                print(f"   Valor: R$ {amount:.2f}")
                
                db.execute("""
                    INSERT INTO investments (user_id, tenant_id, name, investment_type, amount, current_value, quantity, start_date, investment_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active')
                """, (user['id'], user['tenant_id'], name, investment_type, amount, real_current_value, quantity, start_date))
                
                flash_msg = f'✅ Nova posição criada: {name} - {quantity} unidade(s) - R$ {real_current_value:.2f}'
        
        db.commit()
        flash(flash_msg, 'success')
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao adicionar investimento: {e}")
        flash('Erro ao adicionar investimento. Tente novamente.', 'error')
    finally:
        db.close()
    
    return redirect(url_for('investments_page'))

@app.route('/investments/<int:investment_id>')
@login_required
def investment_details(investment_id):
    """Página de detalhes de um investimento"""
    user = get_current_user()
    return render_template('investment_details.html', user=user, investment_id=investment_id)

# =====================================================
# ATUALIZAÇÃO DE COTAÇÕES
# =====================================================

def extract_ticker(name):
    """Extrai o ticker do nome do investimento"""
    # Remove espaços e converte para maiúsculo
    name_upper = name.upper().strip()
    
    # Padrões de ticker brasileiro (PETR4, VALE3, etc)
    match = re.search(r'\b([A-Z]{4}\d{1,2})\b', name_upper)
    if match:
        return match.group(1)
    
    # Se não encontrar padrão, retorna o nome limpo
    words = name_upper.split()
    if words:
        return words[0]
    
    return name_upper

def get_stock_price(ticker):
    """Busca cotação de ação brasileira via API Brapi"""
    try:
        # API Brapi - Cotações B3
        url = f"https://brapi.dev/api/quote/{ticker}?token=demo"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if 'results' in data and len(data['results']) > 0:
                price = data['results'][0].get('regularMarketPrice', 0)
                return float(price) if price else None
    except Exception as e:
        print(f"❌ Erro ao buscar cotação de {ticker}: {e}")
    
    return None

def get_crypto_price(crypto_name):
    """Busca cotação de criptomoeda via CoinGecko"""
    try:
        # Mapear nomes comuns para IDs CoinGecko
        crypto_map = {
            'BITCOIN': 'bitcoin',
            'BTC': 'bitcoin',
            'ETHEREUM': 'ethereum',
            'ETH': 'ethereum',
            'BNB': 'binancecoin',
            'CARDANO': 'cardano',
            'ADA': 'cardano',
            'SOLANA': 'solana',
            'SOL': 'solana',
            'XRP': 'ripple',
            'RIPPLE': 'ripple',
            'DOGE': 'dogecoin',
            'DOGECOIN': 'dogecoin'
        }
        
        crypto_id = crypto_map.get(crypto_name.upper(), crypto_name.lower())
        
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=brl"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if crypto_id in data and 'brl' in data[crypto_id]:
                return float(data[crypto_id]['brl'])
    except Exception as e:
        print(f"❌ Erro ao buscar cotação de {crypto_name}: {e}")
    
    return None

@app.route('/investments/update-quotes', methods=['POST'])
@login_required
def update_investment_quotes():
    """Atualiza cotações de todos os investimentos ativos usando API real"""
    user = get_current_user()
    db = get_db()
    
    updated = 0
    errors = 0
    
    try:
        # Usar o novo serviço de API
        from services.api_connectors import InvestmentAPIFactory
        
        # Buscar investimentos ativos COM quantidade
        investments = db.execute("""
            SELECT id, name, investment_type, amount, current_value, quantity
            FROM investments 
            WHERE user_id = ? AND tenant_id = ? AND investment_status = 'active'
        """, (user['id'], user['tenant_id'])).fetchall()
        
        for inv in investments:
            # Converter Row para dict
            inv_dict = dict(inv)
            
            # Para ações, tentar Investidor10 primeiro (dados fundamentalistas + preço)
            api_data = None
            
            if inv_dict['investment_type'] in ['Ações', 'FII', 'ETF', 'ETFs', 'Stock', 'Stocks', 'Ação']:
                print(f"📊 Buscando {inv_dict['name']} via Investidor10...")
                api_data = InvestmentAPIFactory.get_stock_with_fundamentals(inv_dict['name'])
            
            # Para outros tipos ou se Investidor10 falhou, usar factory padrão
            if not api_data:
                api_data = InvestmentAPIFactory.get_investment_data(
                    inv_dict['investment_type'], 
                    inv_dict['name']
                )
            
            if not api_data:
                # Tentar detectar se é cripto mesmo que tipo esteja errado
                crypto_keywords = ['BITCOIN', 'BTC', 'ETHEREUM', 'ETH', 'CRYPTO', 'CRIPTO', 
                                 'BNB', 'CARDANO', 'ADA', 'SOLANA', 'SOL', 'XRP', 'RIPPLE', 
                                 'DOGE', 'DOGECOIN', 'USDT', 'USDC', 'MATIC', 'POLYGON']
                
                name_upper = inv_dict['name'].upper()
                is_crypto = any(keyword in name_upper for keyword in crypto_keywords)
                
                if is_crypto:
                    api_data = InvestmentAPIFactory.get_investment_data('Criptomoedas', inv_dict['name'])
                    print(f"🔍 Detectado como cripto: {inv_dict['name']}")
            
            if not api_data:
                errors += 1
                print(f"⚠️ Não foi possível buscar dados: {inv_dict['name']}")
                continue
            
            # Pegar o preço correto da API
            new_price = api_data.get('price', 0)
            
            if new_price and new_price > 0:
                # CORREÇÃO: Usar a quantidade REAL do banco de dados
                # Se não tiver quantidade, calcular baseado no valor investido original
                quantity_owned = inv_dict.get('quantity', 1)
                
                if not quantity_owned or quantity_owned <= 0:
                    # Fallback: calcular quantidade baseado no investimento original
                    # Assumir que o preço médio de compra = amount / quantidade
                    # Se amount = 1000 e current_value = 1200, assumir quantidade = 1
                    quantity_owned = 1
                
                # Novo valor atual = quantidade real × preço atual da API
                new_current_value = quantity_owned * new_price
                
                # Atualizar no banco
                db.execute("""
                    UPDATE investments 
                    SET current_value = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (new_current_value, inv_dict['id']))
                
                updated += 1
                
                # Calcular rentabilidade para exibir
                profit_pct = ((new_current_value - inv_dict['amount']) / inv_dict['amount'] * 100) if inv_dict['amount'] > 0 else 0
                
                # NOTIFICAÇÃO: Variação relevante de investimento
                from services.notification_center import notify_investment_change, NotificationCenter
                center = NotificationCenter()
                prefs = center.get_user_preferences(user['id'])
                threshold = prefs.get('investment_change_threshold', 5.0)
                
                if abs(profit_pct) >= threshold:
                    notify_investment_change(user['id'], user['tenant_id'], inv_dict['name'], profit_pct)
                
                print(f"✅ {inv_dict['name']}: Qtd {quantity_owned} × R$ {new_price:.2f} = R$ {new_current_value:.2f} ({profit_pct:+.2f}%)")
            else:
                errors += 1
                print(f"⚠️ Preço inválido para: {inv_dict['name']}")
        
        db.commit()
        
        return jsonify({
            'success': True,
            'updated': updated,
            'errors': errors,
            'message': f'{updated} investimentos atualizados com sucesso!'
        })
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao atualizar cotações: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

# =====================================================
# TRANSACTIONS (TRANSAÇÕES)
# =====================================================

@app.route('/transactions/add', methods=['POST'])
@login_required
def add_transaction():
    """Adiciona nova transação"""
    user = get_current_user()
    
    account_id = request.form.get('account_id')
    category_id = request.form.get('category_id') or None
    payment_method = request.form.get('payment_method', 'debito')
    card_id = request.form.get('card_id') or None
    trans_type = request.form.get('type')
    description = request.form.get('description')
    value = float(request.form.get('value'))
    date = request.form.get('date')
    is_fixed = request.form.get('is_fixed') == 'on'
    status = request.form.get('status', 'Pago')
    installments = int(request.form.get('installments', 1))
    
    # Se o método de pagamento for crédito, card_id é obrigatório
    if payment_method == 'credito' and not card_id:
        flash('Selecione um cartão de crédito para transações no crédito!', 'error')
        return redirect(url_for('dashboard'))
    
    db = get_db()
    
    # Se for parcelado (mais de 1x), criar as parcelas
    if installments > 1 and payment_method == 'credito':
        installment_id = str(uuid.uuid4())
        installment_value = value / installments
        
        # Criar o registro de parcelamento
        db.execute("""
            INSERT INTO installments (id, user_id, tenant_id, description, total_value, installment_count, category_id, card_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (installment_id, user['id'], user['tenant_id'], description, value, installments, category_id, card_id, datetime.now()))
        
        # Criar cada parcela como uma transação
        from dateutil.relativedelta import relativedelta
        base_date = datetime.strptime(date, '%Y-%m-%d')
        
        for i in range(installments):
            transaction_id = str(uuid.uuid4())
            installment_date = (base_date + relativedelta(months=i)).strftime('%Y-%m-%d')
            installment_desc = f"{description} - Parcela {i+1}/{installments}"
            installment_status = 'Pago' if i == 0 else 'Pendente'
            
            db.execute("""
                INSERT INTO transactions (id, user_id, tenant_id, account_id, category_id, card_id, type, description, value, date, status, is_fixed, payment_method, installment_id, installment_number, paid_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (transaction_id, user['id'], user['tenant_id'], account_id, category_id, card_id, trans_type, installment_desc, installment_value, installment_date, installment_status, is_fixed, payment_method, installment_id, i+1, datetime.now() if installment_status == 'Pago' else None))
        
        # Deduzir do limite do cartão apenas o valor total (não por parcela)
        if card_id and trans_type == 'Despesa':
            db.execute("""
                UPDATE cards 
                SET used_limit = COALESCE(used_limit, 0) + ?
                WHERE id = ? AND user_id = ?
            """, (value, card_id, user['id']))
        
        flash(f'Compra parcelada em {installments}x de R$ {installment_value:.2f}!', 'success')
    else:
        # Transação à vista (sem parcelamento)
        transaction_id = str(uuid.uuid4())
        
        db.execute("""
            INSERT INTO transactions (id, user_id, tenant_id, account_id, category_id, card_id, type, description, value, date, status, is_fixed, payment_method, paid_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (transaction_id, user['id'], user['tenant_id'], account_id, category_id, card_id, trans_type, description, value, date, status, is_fixed, payment_method, datetime.now() if status == 'Pago' else None))
        
        # Se a transação for com cartão e for despesa, deduzir do limite disponível
        if card_id and trans_type == 'Despesa':
            db.execute("""
                UPDATE cards 
                SET used_limit = COALESCE(used_limit, 0) + ?
                WHERE id = ? AND user_id = ?
            """, (value, card_id, user['id']))
        
        flash(f'Transação "{description}" adicionada!', 'success')
    
    db.commit()
    db.close()
    
    # INTEGRAÇÃO: Atualizar saldo da conta
    from routes.accounts import update_account_balance_after_transaction
    update_account_balance_after_transaction(transaction_id)
    
    # NOTIFICAÇÃO: Gasto alto detectado
    if trans_type == 'Despesa':
        from services.notification_center import notify_high_expense, NotificationCenter
        center = NotificationCenter()
        prefs = center.get_user_preferences(user['id'])
        threshold = prefs.get('high_expense_threshold', 500.0)
        
        if value >= threshold:
            notify_high_expense(user['id'], user['tenant_id'], value, description)
    
    flash(f'Transação "{description}" adicionada!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/transactions/edit', methods=['POST'])
@login_required
def edit_transaction():
    """Edita uma transação existente"""
    user = get_current_user()
    
    transaction_id = request.form.get('transaction_id')
    account_id = request.form.get('account_id')
    category_id = request.form.get('category_id') or None
    payment_method = request.form.get('payment_method', 'debito')
    card_id = request.form.get('card_id') or None
    trans_type = request.form.get('type')
    description = request.form.get('description')
    value = float(request.form.get('value'))
    date = request.form.get('date')
    is_fixed = request.form.get('is_fixed') == 'on'
    
    # Se o método de pagamento for crédito, card_id é obrigatório
    if payment_method == 'credito' and not card_id:
        flash('Selecione um cartão de crédito para transações no crédito!', 'error')
        return redirect(url_for('dashboard'))
    
    db = get_db()
    
    # Buscar transação antiga para ajustar limite de cartão se necessário
    old_transaction = db.execute("""
        SELECT card_id, type, value 
        FROM transactions 
        WHERE id = ? AND user_id = ?
    """, (transaction_id, user['id'])).fetchone()
    
    if not old_transaction:
        flash('Transação não encontrada!', 'error')
        return redirect(url_for('dashboard'))
    
    # Restaurar limite do cartão antigo se havia
    if old_transaction['card_id'] and old_transaction['type'] == 'Despesa':
        db.execute("""
            UPDATE cards 
            SET used_limit = COALESCE(used_limit, 0) - ?
            WHERE id = ? AND user_id = ?
        """, (old_transaction['value'], old_transaction['card_id'], user['id']))
    
    # Atualizar a transação
    db.execute("""
        UPDATE transactions 
        SET account_id = ?, category_id = ?, card_id = ?, type = ?, 
            description = ?, value = ?, date = ?, is_fixed = ?, 
            payment_method = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND user_id = ?
    """, (account_id, category_id, card_id, trans_type, description, value, 
          date, is_fixed, payment_method, transaction_id, user['id']))
    
    # Deduzir do novo cartão se for crédito e despesa
    if card_id and trans_type == 'Despesa':
        db.execute("""
            UPDATE cards 
            SET used_limit = COALESCE(used_limit, 0) + ?
            WHERE id = ? AND user_id = ?
        """, (value, card_id, user['id']))
    
    db.commit()
    db.close()
    
    # INTEGRAÇÃO: Atualizar saldo da conta
    from routes.accounts import update_account_balance_after_transaction
    update_account_balance_after_transaction(transaction_id)
    
    flash(f'Transação "{description}" atualizada!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/transactions/delete/<transaction_id>', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    """Deleta transação"""
    user = get_current_user()
    db = get_db()
    
    # Buscar dados da transação antes de deletar (para restaurar limite do cartão)
    transaction = db.execute("""
        SELECT account_id, card_id, type, value 
        FROM transactions 
        WHERE id = ? AND user_id = ?
    """, (transaction_id, user['id'])).fetchone()
    
    if not transaction:
        flash('Transação não encontrada!', 'error')
        return redirect(url_for('dashboard'))
    
    account_id = transaction['account_id']
    card_id = transaction['card_id']
    trans_type = transaction['type']
    value = transaction['value']
    
    # Se a transação era com cartão e despesa, devolver o limite
    if card_id and trans_type == 'Despesa':
        db.execute("""
            UPDATE cards 
            SET used_limit = COALESCE(used_limit, 0) - ?
            WHERE id = ? AND user_id = ?
        """, (value, card_id, user['id']))
    
    # Deletar a transação
    db.execute("DELETE FROM transactions WHERE id = ? AND user_id = ?", (transaction_id, user['id']))
    db.commit()
    db.close()
    
    # INTEGRAÇÃO: Recalcular saldo da conta
    if account_id:
        from routes.accounts import recalculate_account_balance
        recalculate_account_balance(account_id)
    
    flash('Transação excluída!', 'success')
    return redirect(url_for('dashboard'))

# =====================================================
# API ENDPOINTS (JSON)
# =====================================================

@app.route('/api/summary')
@login_required
def api_summary():
    """Retorna resumo financeiro (API)"""
    user = get_current_user()
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    
    db = get_db()
    summary = db.execute("""
        SELECT 
            COALESCE(SUM(CASE WHEN type = 'Receita' AND is_fixed = 1 THEN value ELSE 0 END), 0) as renda_fixa,
            COALESCE(SUM(CASE WHEN type = 'Receita' AND is_fixed = 0 THEN value ELSE 0 END), 0) as renda_variavel,
            COALESCE(SUM(CASE WHEN type = 'Receita' THEN value ELSE 0 END), 0) as renda_total,
            COALESCE(SUM(CASE WHEN type = 'Despesa' AND is_fixed = 1 THEN value ELSE 0 END), 0) as custo_fixo,
            COALESCE(SUM(CASE WHEN type = 'Despesa' AND is_fixed = 0 THEN value ELSE 0 END), 0) as custo_variavel,
            COALESCE(SUM(CASE WHEN type = 'Despesa' THEN value ELSE 0 END), 0) as custo_total
        FROM transactions
        WHERE user_id = ? AND tenant_id = ? AND status = 'Pago'
        AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
    """, (user['id'], user['tenant_id'], str(year), f"{month:02d}")).fetchone()
    
    db.close()
    
    if summary:
        data = dict(summary)
        data['saldo_mensal'] = data['renda_total'] - data['custo_total']
        return jsonify(data)
    else:
        return jsonify({
            'renda_fixa': 0, 'renda_variavel': 0, 'renda_total': 0,
            'custo_fixo': 0, 'custo_variavel': 0, 'custo_total': 0,
            'saldo_mensal': 0
        })

@app.route('/api/dashboard')
@login_required
def api_dashboard():
    """Retorna dados completos para o dashboard financeiro"""
    user = get_current_user()
    db = get_db()
    
    # Mês atual e anterior
    hoje = datetime.now()
    ano_atual = hoje.year
    mes_atual = hoje.month
    
    # Calcular mês anterior
    if mes_atual == 1:
        mes_anterior = 12
        ano_anterior = ano_atual - 1
    else:
        mes_anterior = mes_atual - 1
        ano_anterior = ano_atual
    
    # === RESUMO FINANCEIRO MÊS ATUAL ===
    summary_atual = db.execute("""
        SELECT 
            COALESCE(SUM(CASE WHEN type = 'Receita' THEN value ELSE 0 END), 0) as renda_total,
            COALESCE(SUM(CASE WHEN type = 'Despesa' THEN value ELSE 0 END), 0) as custos_total
        FROM transactions
        WHERE user_id = ? AND tenant_id = ? AND status = 'Pago'
        AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
    """, (user['id'], user['tenant_id'], str(ano_atual), f"{mes_atual:02d}")).fetchone()
    
    # === RESUMO FINANCEIRO MÊS ANTERIOR ===
    summary_anterior = db.execute("""
        SELECT 
            COALESCE(SUM(CASE WHEN type = 'Receita' THEN value ELSE 0 END), 0) as renda_total,
            COALESCE(SUM(CASE WHEN type = 'Despesa' THEN value ELSE 0 END), 0) as custos_total
        FROM transactions
        WHERE user_id = ? AND tenant_id = ? AND status = 'Pago'
        AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
    """, (user['id'], user['tenant_id'], str(ano_anterior), f"{mes_anterior:02d}")).fetchone()
    
    renda_total = float(summary_atual['renda_total'])
    custos_total = float(summary_atual['custos_total'])
    saldo = renda_total - custos_total
    
    renda_mes_anterior = float(summary_anterior['renda_total'])
    custos_mes_anterior = float(summary_anterior['custos_total'])
    
    # === INVESTIMENTOS ===
    investments_data = db.execute("""
        SELECT investment_type, SUM(COALESCE(current_value, amount)) as total
        FROM investments
        WHERE user_id = ? AND tenant_id = ? AND (investment_status = 'active' OR investment_status IS NULL)
        GROUP BY investment_type
    """, (user['id'], user['tenant_id'])).fetchall()
    
    investimentos = {}
    for inv in investments_data:
        tipo = inv['investment_type'] or 'Outros'
        # Mapear tipos para categorias
        if tipo.lower() in ['tesouro direto', 'cdb', 'lci', 'lca', 'poupança']:
            categoria = 'renda_fixa'
        elif tipo.lower() in ['ações', 'acoes', 'ação', 'acao', 'fii', 'fiis']:
            categoria = 'acoes'
        elif tipo.lower() in ['bitcoin', 'ethereum', 'cripto', 'criptomoedas']:
            categoria = 'criptomoedas'
        else:
            categoria = 'outros'
        
        if categoria not in investimentos:
            investimentos[categoria] = 0
        investimentos[categoria] += float(inv['total'])
    
    # === CATEGORIAS DE DESPESAS ===
    categorias_data = db.execute("""
        SELECT c.name, SUM(t.value) as total
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ? AND t.tenant_id = ? AND t.type = 'Despesa' AND t.status = 'Pago'
        AND strftime('%Y', t.date) = ? AND strftime('%m', t.date) = ?
        GROUP BY c.name
        ORDER BY total DESC
        LIMIT 10
    """, (user['id'], user['tenant_id'], str(ano_atual), f"{mes_atual:02d}")).fetchall()
    
    categorias = {row['name']: float(row['total']) for row in categorias_data}
    
    # === HISTÓRICO DE SALDO (últimos 6 meses) ===
    historico_saldo = []
    meses_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    for i in range(5, -1, -1):
        mes_ref = mes_atual - i
        ano_ref = ano_atual
        
        if mes_ref <= 0:
            mes_ref += 12
            ano_ref -= 1
        
        saldo_mes = db.execute("""
            SELECT 
                COALESCE(SUM(CASE WHEN type = 'Receita' THEN value ELSE 0 END), 0) -
                COALESCE(SUM(CASE WHEN type = 'Despesa' THEN value ELSE 0 END), 0) as saldo
            FROM transactions
            WHERE user_id = ? AND tenant_id = ? AND status = 'Pago'
            AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
        """, (user['id'], user['tenant_id'], str(ano_ref), f"{mes_ref:02d}")).fetchone()
        
        historico_saldo.append({
            'mes': meses_nomes[mes_ref - 1],
            'valor': float(saldo_mes['saldo'])
        })
    
    # === FLUXO MENSAL (por dia do mês atual) ===
    fluxo_data = db.execute("""
        SELECT 
            CAST(strftime('%d', date) AS INTEGER) as dia,
            SUM(CASE WHEN type = 'Receita' THEN value ELSE 0 END) as renda,
            SUM(CASE WHEN type = 'Despesa' THEN value ELSE 0 END) as custo
        FROM transactions
        WHERE user_id = ? AND tenant_id = ? AND status = 'Pago'
        AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
        GROUP BY dia
        ORDER BY dia
    """, (user['id'], user['tenant_id'], str(ano_atual), f"{mes_atual:02d}")).fetchall()
    
    fluxo_mensal = [{'dia': row['dia'], 'renda': float(row['renda']), 'custo': float(row['custo'])} for row in fluxo_data]
    
    # === VARIAÇÃO DE INVESTIMENTOS (top 10) ===
    variacao_investments = db.execute("""
        SELECT 
            name,
            amount,
            current_value,
            CASE 
                WHEN amount > 0 THEN ROUND(((current_value - amount) / amount) * 100, 2)
                ELSE 0
            END as variacao
        FROM investments
        WHERE user_id = ? AND tenant_id = ? 
        AND (investment_status = 'active' OR investment_status IS NULL)
        AND current_value IS NOT NULL
        ORDER BY ABS(variacao) DESC
        LIMIT 10
    """, (user['id'], user['tenant_id'])).fetchall()
    
    variacao_investimentos = [{'nome': row['name'], 'variacao': float(row['variacao'])} for row in variacao_investments]
    
    db.close()
    
    return jsonify({
        'renda_total': renda_total,
        'custos_total': custos_total,
        'saldo': saldo,
        'renda_mes_anterior': renda_mes_anterior,
        'custos_mes_anterior': custos_mes_anterior,
        'investimentos': investimentos,
        'categorias': categorias,
        'historico_saldo': historico_saldo,
        'fluxo_mensal': fluxo_mensal,
        'variacao_investimentos': variacao_investimentos
    })

@app.route('/api/recurring/execute-now', methods=['POST'])
@login_required
def execute_recurring_now():
    """Executa transações recorrentes manualmente (ADMIN apenas)"""
    user = get_current_user()
    
    if not user or not user.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    from scheduler import trigger_manual_execution
    count = trigger_manual_execution()
    
    return jsonify({
        'success': True,
        'message': f'{count} transações recorrentes executadas',
        'count': count
    })

@app.route('/admin/update-investments', methods=['POST'])
@login_required
def admin_update_investments():
    """Atualiza investimentos manualmente (admin)"""
    user = get_current_user()
    
    if not user or not user.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    from scheduler import trigger_investments_update
    stats = trigger_investments_update()
    
    return jsonify({
        'success': True,
        'message': f'Investimentos atualizados: {stats["success"]} sucesso, {stats["failed"]} falhas',
        'stats': stats
    })


# Edit investment route - REGISTERED EARLY
@app.route('/investments/edit/<int:investment_id>', methods=['POST'])
@login_required
def edit_investment_v2(investment_id):
    """Editar investimento existente"""
    try:
        user = get_current_user()
        data = request.get_json()
        
        # Extrair dados do formulário
        name = data.get('name')
        investment_type = data.get('investment_type')
        quantity = float(data.get('quantity', 1))
        amount = float(data.get('amount', 0))
        description = data.get('description', '')
        
        db = get_db()
        
        # Verificar se investimento existe e pertence ao usuário
        inv = db.execute("""
            SELECT id FROM investments 
            WHERE id = ? AND user_id = ? AND tenant_id = ?
        """, (investment_id, user['id'], user['tenant_id'])).fetchone()
        
        if not inv:
            db.close()
            return jsonify({'success': False, 'error': 'Investimento não encontrado'}), 404
        
        # Atualizar investimento
        db.execute("""
            UPDATE investments 
            SET name = ?, 
                investment_type = ?, 
                quantity = ?,
                amount = ?,
                description = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND user_id = ? AND tenant_id = ?
        """, (name, investment_type, quantity, amount, description, 
              investment_id, user['id'], user['tenant_id']))
        
        db.commit()
        db.close()
        
        print(f"✅ Investimento {investment_id} atualizado: {name} - Qtd: {quantity} - R$ {amount:.2f}")
        
        return jsonify({
            'success': True, 
            'message': 'Investimento atualizado com sucesso!',
            'investment': {
                'id': investment_id,
                'name': name,
                'type': investment_type,
                'quantity': quantity,
                'amount': amount
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Erro ao editar investimento: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# Compatibility: add delete routes BEFORE main so they are registered when app starts
@app.route('/investments/delete', methods=['POST'])
@login_required
def delete_investment_v2():
    """Compat route that accepts JSON body with {'id': <investment_id>}"""
    user = get_current_user()
    data = request.get_json() or {}
    investment_id = data.get('id')

    if not investment_id:
        return jsonify({'success': False, 'error': 'Missing id'}), 400

    try:
        db = get_db()
        # verify ownership
        inv = db.execute("SELECT id FROM investments WHERE id = ? AND user_id = ? AND tenant_id = ?",
                         (investment_id, user['id'], user['tenant_id'])).fetchone()
        if not inv:
            db.close()
            return jsonify({'success': False, 'error': 'Investimento não encontrado'}), 404

        db.execute("DELETE FROM investments WHERE id = ? AND user_id = ? AND tenant_id = ?",
                   (investment_id, user['id'], user['tenant_id']))
        db.commit()
        db.close()
        return jsonify({'success': True, 'message': 'Investimento excluído com sucesso!'}), 200
    except Exception as e:
        print(f"❌ Erro ao deletar investimento (v2): {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/investments/delete/<int:investment_id>', methods=['POST'])
@login_required
def delete_investment_by_id_v2(investment_id):
    """Delete by id route (POST). Registered early so front-end calls succeed."""
    user = get_current_user()
    try:
        db = get_db()
        inv = db.execute("SELECT id FROM investments WHERE id = ? AND user_id = ? AND tenant_id = ?",
                         (investment_id, user['id'], user['tenant_id'])).fetchone()
        if not inv:
            db.close()
            return jsonify({'success': False, 'error': 'Investimento não encontrado'}), 404

        db.execute("DELETE FROM investments WHERE id = ? AND user_id = ? AND tenant_id = ?",
                   (investment_id, user['id'], user['tenant_id']))
        db.commit()
        db.close()
        return jsonify({'success': True, 'message': 'Investimento excluído com sucesso!'}), 200
    except Exception as e:
        print(f"❌ Erro ao deletar investimento by id (v2): {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================
# WHATSAPP INTEGRATION
# =====================================================

import logging

# Configurar logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/whatsapp.log'),
        logging.StreamHandler()
    ]
)

whatsapp_logger = logging.getLogger('whatsapp')

# Carregar processadores sob demanda
audio_proc = None
ocr_proc = None
pdf_proc = None
nlp = None

def get_audio_processor():
    global audio_proc
    if audio_proc is None:
        from modules.audio_processor import AudioProcessor
        audio_proc = AudioProcessor(whisper_model='tiny')
    return audio_proc

def get_ocr_processor():
    global ocr_proc
    if ocr_proc is None:
        from modules.ocr_processor import OCRProcessor
        # Configurar caminho do Tesseract no Windows
        tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if os.path.exists(tesseract_path):
            ocr_proc = OCRProcessor(language='por', tesseract_cmd=tesseract_path)
        else:
            ocr_proc = OCRProcessor(language='por')
    return ocr_proc

def get_pdf_processor():
    global pdf_proc
    if pdf_proc is None:
        from modules.pdf_processor import PDFProcessor
        pdf_proc = PDFProcessor()
    return pdf_proc

def get_nlp_classifier():
    global nlp
    if nlp is None:
        from modules.nlp_classifier import NLPClassifier
        nlp = NLPClassifier()
    return nlp

WHATSAPP_SERVER_URL = os.getenv('WHATSAPP_SERVER_URL', 'http://localhost:3000')
WHATSAPP_AUTH_TOKEN = os.getenv('WHATSAPP_AUTH_TOKEN', 'change_me')

def get_user_by_whatsapp(whatsapp_number):
    """Busca usuário pelo número de WhatsApp"""
    try:
        db = get_db()
        # Remove @c.us se existir
        clean_number = whatsapp_number.replace('@c.us', '')
        
        whatsapp_logger.info(f"🔍 Buscando usuário:")
        whatsapp_logger.info(f"   Original: {whatsapp_number}")
        whatsapp_logger.info(f"   Limpo: {clean_number}")
        whatsapp_logger.info(f"   Com +: +{clean_number}")
        
        # Tentar buscar com e sem o sinal de +
        user = db.execute('''
            SELECT id, tenant_id, email, name, phone
            FROM users
            WHERE (phone = ? OR phone = ?) AND active = 1
        ''', (clean_number, f'+{clean_number}')).fetchone()
        
        if user:
            whatsapp_logger.info(f"✅ Usuário encontrado: {dict(user)['name']} ({dict(user)['phone']})")
        else:
            whatsapp_logger.warning(f"❌ Usuário NÃO encontrado!")
            # Mostrar todos os usuários para debug
            all_users = db.execute("SELECT phone FROM users WHERE active = 1").fetchall()
            whatsapp_logger.warning(f"   Phones cadastrados: {[u[0] for u in all_users]}")
        
        db.close()
        return dict(user) if user else None
    except Exception as e:
        whatsapp_logger.error(f"Erro ao buscar usuário: {e}")
        return None

@app.route('/api/whatsapp/webhook', methods=['POST'])
def whatsapp_webhook():
    """Recebe mensagens do WhatsApp via Node.js server"""
    try:
        # Validar token
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer ') or auth_header.split(' ')[1] != WHATSAPP_AUTH_TOKEN:
            whatsapp_logger.warning("⛔ Token inválido")
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.json
        print(f"\n{'='*60}")
        print(f"DEBUG: Webhook recebido!")
        print(f"  Data completa: {data}")
        print(f"  Type: {data.get('type')}")
        print(f"  From: {data.get('from')}")
        print(f"  Text: {data.get('text')}")
        print(f"{'='*60}\n")
        
        whatsapp_logger.info(f"📨 Webhook recebido: {data.get('type')} de {data.get('from')}")
        
        message_type = data.get('type')
        text = data.get('text', '')
        media_url = data.get('media_url')
        audio_base64 = data.get('audio_base64')
        image_base64 = data.get('image_base64')
        sender = data.get('from')
        
        # Processar diferentes tipos
        extracted_text = None
        
        if message_type == 'text':
            extracted_text = text
            print(f"DEBUG: Tipo 'text' detectado, extracted_text = '{extracted_text}'")
            
        elif message_type == 'audio':
            whatsapp_logger.info(f"🎤 Processando áudio...")
            
            try:
                if audio_base64:
                    whatsapp_logger.info(f"   📦 Base64 recebido: {len(audio_base64)} caracteres")
                    
                    # Salvar áudio temporário
                    import base64
                    import tempfile
                    
                    audio_bytes = base64.b64decode(audio_base64)
                    whatsapp_logger.info(f"   📦 Áudio decodificado: {len(audio_bytes)} bytes")
                    
                    with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_audio:
                        temp_audio.write(audio_bytes)
                        temp_audio_path = temp_audio.name
                    
                    whatsapp_logger.info(f"   💾 Áudio salvo em: {temp_audio_path}")
                    
                    # Processar com Whisper
                    whatsapp_logger.info(f"   🤖 Inicializando Whisper...")
                    audio_processor = get_audio_processor()
                    
                    whatsapp_logger.info(f"   🎯 Transcrevendo áudio...")
                    extracted_text = audio_processor.process_audio(temp_audio_path)
                    
                    whatsapp_logger.info(f"   ✅ Texto extraído: '{extracted_text}'")
                    
                    # Limpar arquivo temporário
                    try:
                        os.remove(temp_audio_path)
                        whatsapp_logger.info(f"   🗑️ Arquivo temporário removido")
                    except:
                        pass
                    
                elif media_url:
                    whatsapp_logger.info(f"   🌐 Usando URL: {media_url}")
                    # Fallback para URL (método antigo)
                    audio_processor = get_audio_processor()
                    extracted_text = audio_processor.process_audio(media_url)
                else:
                    whatsapp_logger.error("❌ Áudio sem base64 ou URL")
                    return jsonify({'success': False, 'message': 'Áudio inválido'}), 400
                    
            except Exception as e:
                import traceback
                whatsapp_logger.error(f"❌ Erro ao processar áudio: {e}")
                whatsapp_logger.error(f"   Traceback: {traceback.format_exc()}")
                send_whatsapp_message(sender, "❌ Erro ao processar áudio. Tente enviar como texto.")
                return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500
            
        elif message_type == 'image':
            whatsapp_logger.info(f"🖼️ Processando imagem...")
            
            try:
                if image_base64:
                    # Salvar imagem temporária
                    import base64
                    import tempfile
                    from PIL import Image
                    import io
                    
                    image_bytes = base64.b64decode(image_base64)
                    image = Image.open(io.BytesIO(image_bytes))
                    
                    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_image:
                        image.save(temp_image.name, 'JPEG')
                        temp_image_path = temp_image.name
                    
                    whatsapp_logger.info(f"✅ Imagem salva em: {temp_image_path}")
                    
                    # Processar com OCR
                    ocr_processor = get_ocr_processor()
                    extracted_text = ocr_processor.process_image(temp_image_path)
                    
                    # Limpar arquivo temporário
                    try:
                        os.remove(temp_image_path)
                    except:
                        pass
                    
                    whatsapp_logger.info(f"✅ Texto extraído da imagem: {extracted_text}")
                    
                elif media_url:
                    # Fallback para URL (método antigo)
                    ocr_processor = get_ocr_processor()
                    extracted_text = ocr_processor.process_image(media_url)
                else:
                    whatsapp_logger.error("❌ Imagem sem base64 ou URL")
                    return jsonify({'success': False, 'message': 'Imagem inválida'}), 400
                    
            except Exception as e:
                whatsapp_logger.error(f"❌ Erro ao processar imagem: {e}")
                send_whatsapp_message(sender, "❌ Erro ao processar imagem. Tente enviar texto descrevendo a transação.")
                return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500
            
        elif message_type == 'document':
            if media_url and media_url.endswith('.pdf'):
                whatsapp_logger.info(f"📄 Processando PDF: {media_url}")
                pdf_processor = get_pdf_processor()
                transactions = pdf_processor.process_pdf(media_url)
                
                if transactions:
                    # Inserir múltiplas transações
                    for trans in transactions:
                        insert_transaction_from_whatsapp(trans, sender)
                    
                    response_msg = f"✅ {len(transactions)} transações adicionadas do extrato!"
                    send_whatsapp_message(sender, response_msg)
                    
                    return jsonify({
                        'success': True,
                        'message': response_msg,
                        'transactions': len(transactions)
                    })
        
        whatsapp_logger.info(f"📝 Texto extraído: '{extracted_text}'")
        whatsapp_logger.info(f"📋 Tipo de mensagem: {message_type}")
        
        # Se não temos texto, retornar erro específico
        if not extracted_text:
            whatsapp_logger.warning(f"⚠️ Nenhum texto foi extraído! Tipo: {message_type}")
            return jsonify({'success': False, 'message': f'Não foi possível extrair texto da mensagem tipo: {message_type}'})
        
        # Se temos texto extraído, processar com IA
        if extracted_text:
            # Verificar se é uma pergunta ou comando de transação
            # Perguntas têm palavras interrogativas OU são sobre consulta/análise
            text_lower = extracted_text.lower()
            
            # PRIORIDADE 1: Verificar se é PERGUNTA primeiro (mais específico)
            question_keywords = [
                'quanto gastei', 'quanto recebi', 'quanto ganhei', 'quanto saiu', 'quanto entrou',
                'qual meu', 'qual o', 'qual é', 'como está', 'como estão', 'onde gastei', 
                'quando gastei', 'por que', 'porque', 'qual o saldo', 'quanto tenho', 
                'minha situação', 'meu saldo', 'minhas', 'meus investimentos', 'meus gastos',
                'quanto está', 'análise', 'resumo', 'total gasto', 'total recebido',
                'quanto de', 'quanto tem', 'tem disponível', 'saldo', 'patrimônio', 'balanço',
                'minhas receitas', 'meus ganhos', 'meu patrimônio', 'minha carteira',
                'investimentos', 'ações', 'fundos', 'aplicações', 'portfolio', 'rentabilidade',
                'quanto lucrei', 'quanto rendeu', 'performance', 'valorização',
                'previsão', 'expectativa', 'projeção', 'vai sobrar', 'vai faltar',
                'comparação', 'comparar', 'mês passado', 'anterior', 'diferença',
                'categoria', 'onde gasto mais', 'tipo de gasto', 'distribuição'
            ]
            has_question_word = any(word in text_lower for word in question_keywords) or '?' in text_lower
            
            # PRIORIDADE 2: Verificar se é TRANSAÇÃO (ação + valor)
            # Transações têm verbos de ação no passado + valor numérico
            transaction_verbs = [
                'paguei ', 'gastei ', 'comprei ', 'recebi ', 'ganhei ', 'vendi ',
                'desembolsei ', 'tirei ', 'saquei ', 'transferi ', 'depositei ',
                'pago ', 'gasto ', 'compro '
            ]
            has_transaction_verb = any(verb in text_lower for verb in transaction_verbs)
            
            # Verificar se tem valor monetário (R$, reais, ou número)
            has_money_symbol = 'r$' in text_lower or 'reais' in text_lower or 'real' in text_lower
            has_value = any(char.isdigit() for char in text_lower)
            
            # Decisão: Pergunta tem prioridade se detectada
            # Transação precisa de verbo de ação + valor
            is_question = has_question_word
            is_transaction = (not is_question) and has_transaction_verb and has_value
            
            # FALLBACK: Se não é nem pergunta nem transação, tratar como pergunta genérica
            # Isso inclui mensagens simples como "oi", "olá", "teste", etc.
            if not is_question and not is_transaction:
                whatsapp_logger.info(f"💭 Mensagem genérica detectada, tratando como pergunta: {extracted_text}")
                is_question = True
            
            if is_question:
                # ========================================
                # MODO PERGUNTA: Usar IA do BWS Finance
                # ========================================
                whatsapp_logger.info(f"💬 Pergunta detectada: {extracted_text}")
                
                try:
                    # Buscar usuário pelo número de WhatsApp
                    user = get_user_by_whatsapp(sender)
                    
                    # DESABILITADO: Permitir qualquer número (usar usuário padrão se não encontrado)
                    if not user:
                        # Usar usuário padrão do Brayan
                        whatsapp_logger.info(f"⚠️ Número {sender} não cadastrado, usando usuário padrão")
                        db = get_db()
                        user = db.execute('''
                            SELECT * FROM users 
                            WHERE phone = '+5511974764971' OR email = 'brayan@bws.com'
                            LIMIT 1
                        ''').fetchone()
                        db.close()
                        
                        if not user:
                            msg = "⚠️ Erro: Usuário padrão não encontrado. Execute: python cadastrar_brayan.py"
                            send_whatsapp_message(sender, msg)
                            return jsonify({'success': False, 'message': msg})
                    
                    # Importar IA
                    from services.ai_core import BWSInsightAI
                    from services.ai_chat import AIChat
                    
                    # Inicializar IA
                    ai = BWSInsightAI(user_id=user['id'], tenant_id=user['tenant_id'])
                    chat = AIChat(ai)
                    
                    # Buscar dados financeiros do usuário
                    financial_data = ai.fetch_financial_data_direct(user['id'], user['tenant_id'])
                    
                    # Processar mensagem com IA
                    ai_response = chat.process_message(extracted_text, financial_data)
                    
                    whatsapp_logger.info(f"🤖 Resposta da IA: {ai_response[:100]}...")
                    
                    # Enviar resposta
                    send_whatsapp_message(sender, ai_response)
                    
                    return jsonify({
                        'success': True,
                        'message': ai_response,
                        'mode': 'ai_chat'
                    })
                    
                except Exception as e:
                    whatsapp_logger.error(f"❌ Erro na IA: {e}")
                    msg = "❌ Erro ao processar pergunta. Tente novamente!"
                    send_whatsapp_message(sender, msg)
                    return jsonify({'success': False, 'message': str(e)})
            
            elif is_transaction:
                # ========================================
                # MODO TRANSAÇÃO: Classificar e inserir
                # ========================================
                whatsapp_logger.info(f"💰 Transação detectada: {extracted_text}")
                
                # Buscar usuário primeiro
                user = get_user_by_whatsapp(sender)
                
                # DESABILITADO: Usar usuário padrão se não encontrado
                if not user:
                    whatsapp_logger.info(f"⚠️ Número {sender} não cadastrado, usando usuário padrão para transação")
                    db = get_db()
                    user = db.execute('''
                        SELECT * FROM users 
                        WHERE phone = '+5511974764971' OR email = 'brayan@bws.com'
                        LIMIT 1
                    ''').fetchone()
                    db.close()
                    
                    if not user:
                        msg = "⚠️ Erro: Usuário padrão não encontrado."
                        send_whatsapp_message(sender, msg)
                        return jsonify({'success': False, 'message': msg})
                
                nlp_classifier = get_nlp_classifier()
                result = nlp_classifier.classify(extracted_text)
                
                # Adicionar user_id, tenant_id e texto original ao result
                result['user_id'] = user['id']
                result['tenant_id'] = user['tenant_id']
                result['original_text'] = extracted_text  # Para análise de conta/cartão
                
                if result.get('amount'):
                    # Inserir transação (agora retorna tupla com payment_info)
                    transaction_result = insert_transaction_from_whatsapp(result, sender)
                    
                    if transaction_result:
                        if isinstance(transaction_result, tuple):
                            transaction_id, payment_info = transaction_result
                        else:
                            transaction_id = transaction_result
                            payment_info = None
                        
                        msg = f"✅ Transação adicionada!\n\n"
                        msg += f"💰 Valor: R$ {result['amount']:.2f}\n"
                        msg += f"📅 Data: {result['date']}\n"
                        msg += f"📂 Categoria: {result['category']}\n"
                        msg += f"📝 Descrição: {result['description']}\n"
                        
                        # Informar onde foi lançado
                        if payment_info:
                            if payment_info['type'] == 'card':
                                msg += f"💳 Cartão: {payment_info['name']}\n"
                            else:
                                msg += f"🏦 Conta: {payment_info['name']}\n"
                        
                        if result.get('confidence', 0) < 0.7:
                            msg += f"\n⚠️ Confiança baixa. Verifique os dados!"
                        
                        send_whatsapp_message(sender, msg)
                        
                        return jsonify({
                            'success': True,
                            'message': msg,
                            'transaction_id': transaction_id,
                            'mode': 'transaction'
                        })
                else:
                    # Não conseguiu extrair valor
                    msg = "⚠️ Não consegui identificar o valor da transação.\n\n"
                    msg += "📝 Exemplos de uso:\n"
                    msg += "• Transação: 'Paguei R$ 50,00 no mercado hoje'\n"
                    msg += "• Pergunta: 'Quanto gastei esse mês?'\n"
                    msg += "• Pergunta: 'Qual meu saldo?'"
                    
                    send_whatsapp_message(sender, msg)
                    
                    return jsonify({
                        'success': False,
                        'message': msg
                    })
        
        return jsonify({'success': False, 'message': 'Tipo não suportado'})
        
    except Exception as e:
        whatsapp_logger.error(f"❌ Erro no webhook: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({'error': str(e)}), 500

def get_smart_account_or_card(db, user_id: str, tenant_id: str, transaction_text: str, transaction_type: str):
    """
    Seleciona conta ou cartão inteligentemente baseado em:
    1. Palavras-chave na mensagem (ex: "no cartão", "no débito", "no nubank")
    2. Configuração padrão do usuário
    3. Conta com maior saldo (fallback)
    
    Retorna: dict com 'type' ('account' ou 'card'), 'id', 'name'
    """
    text_lower = transaction_text.lower()
    
    # ESTRATÉGIA 1: Detecção por palavras-chave
    # Cartões
    card_keywords = [
        'cartão', 'cartao', 'crédito', 'credito', 'no cartao', 'no credito',
        'mastercard', 'visa', 'elo', 'amex', 'hipercard'
    ]
    
    # Contas específicas
    bank_names = {
        'nubank': ['nubank', 'roxinho', 'nu'],
        'inter': ['inter', 'laranja'],
        'itau': ['itau', 'itaú'],
        'bradesco': ['bradesco'],
        'santander': ['santander'],
        'caixa': ['caixa', 'cef'],
        'bb': ['banco do brasil', 'bb'],
        'picpay': ['picpay'],
        'mercado pago': ['mercado pago', 'mercadopago']
    }
    
    # Verificar se mencionou cartão
    mentioned_card = any(keyword in text_lower for keyword in card_keywords)
    
    # Verificar se mencionou banco específico
    mentioned_bank = None
    for bank, keywords in bank_names.items():
        if any(keyword in text_lower for keyword in keywords):
            mentioned_bank = bank
            break
    
    # Se mencionou cartão E não mencionou débito
    if mentioned_card and 'débito' not in text_lower and 'debito' not in text_lower:
        # Buscar cartão
        card = None
        
        if mentioned_bank:
            # Buscar cartão do banco mencionado
            card = db.execute("""
                SELECT id, name FROM cards
                WHERE user_id = ? AND tenant_id = ? AND active = 1
                AND LOWER(name) LIKE ?
                LIMIT 1
            """, (user_id, tenant_id, f'%{mentioned_bank}%')).fetchone()
        
        if not card:
            # Buscar cartão com maior limite disponível
            card = db.execute("""
                SELECT id, name, (limit_amount - COALESCE(used_limit, 0)) as available
                FROM cards
                WHERE user_id = ? AND tenant_id = ? AND active = 1
                ORDER BY available DESC
                LIMIT 1
            """, (user_id, tenant_id)).fetchone()
        
        if card:
            return {'type': 'card', 'id': card['id'], 'name': card['name']}
    
    # Se mencionou banco específico, buscar conta
    if mentioned_bank:
        account = db.execute("""
            SELECT id, name FROM accounts
            WHERE user_id = ? AND tenant_id = ? AND active = 1
            AND LOWER(name) LIKE ?
            LIMIT 1
        """, (user_id, tenant_id, f'%{mentioned_bank}%')).fetchone()
        
        if account:
            return {'type': 'account', 'id': account['id'], 'name': account['name']}
    
    # ESTRATÉGIA 2: Buscar conta/cartão padrão configurado
    # (Por enquanto, vamos pular isso e ir direto para fallback)
    
    # ESTRATÉGIA 3: Fallback - conta com maior saldo
    account = db.execute("""
        SELECT id, name, current_balance
        FROM accounts
        WHERE user_id = ? AND tenant_id = ? AND active = 1
        ORDER BY current_balance DESC
        LIMIT 1
    """, (user_id, tenant_id)).fetchone()
    
    if account:
        return {'type': 'account', 'id': account['id'], 'name': account['name']}
    
    # Se não tem nenhuma conta, retornar None para criar uma nova
    return None

def insert_transaction_from_whatsapp(data: dict, sender: str) -> str:
    """Insere transação no banco vinda do WhatsApp"""
    try:
        db = get_db()
        
        # Usar user_id e tenant_id do data (já adicionados no webhook)
        user_id = data.get('user_id')
        tenant_id = data.get('tenant_id')
        
        if not user_id or not tenant_id:
            whatsapp_logger.error("❌ user_id ou tenant_id não fornecidos")
            return None
        
        user = {'id': user_id, 'tenant_id': tenant_id}
        
        # Usar seleção inteligente de conta/cartão
        original_text = data.get('original_text', data.get('description', ''))
        payment_method = get_smart_account_or_card(db, user['id'], user['tenant_id'], original_text, data.get('type', 'Despesa'))
        
        if not payment_method:
            # Criar conta padrão WhatsApp se não existe nenhuma
            account_id = str(uuid.uuid4())
            db.execute("""
                INSERT INTO accounts (id, user_id, tenant_id, name, type, initial_balance, current_balance)
                VALUES (?, ?, ?, 'WhatsApp', 'Corrente', 0, 0)
            """, (account_id, user['id'], user['tenant_id']))
            payment_method = {'type': 'account', 'id': account_id, 'name': 'WhatsApp'}
        
        account_id = payment_method['id'] if payment_method['type'] == 'account' else None
        card_id = payment_method['id'] if payment_method['type'] == 'card' else None
        
        # Buscar categoria
        category_name = data.get('category', 'Outros')
        print(f"\n{'='*60}")
        print(f"🔍 BUSCANDO CATEGORIA NO BANCO:")
        print(f"{'='*60}")
        print(f"📂 Nome buscado: '{category_name}'")
        print(f"🏢 Tenant ID: {user['tenant_id']}")
        
        category = db.execute("""
            SELECT id, name FROM categories
            WHERE name = ? AND tenant_id = ?
            LIMIT 1
        """, (category_name, user['tenant_id'])).fetchone()
        
        if category:
            print(f"✅ Categoria encontrada: {dict(category)}")
            category_id = category['id']
        else:
            print(f"❌ Categoria NÃO encontrada no banco!")
            print(f"📋 Verificando todas as categorias do tenant...")
            all_categories = db.execute("""
                SELECT name FROM categories WHERE tenant_id = ?
            """, (user['tenant_id'],)).fetchall()
            print(f"   Categorias disponíveis: {[c['name'] for c in all_categories]}")
            
            # Criar categoria se não existir
            print(f"➕ Criando nova categoria: '{category_name}'")
            category_id = str(uuid.uuid4())
            db.execute("""
                INSERT INTO categories (id, name, type, tenant_id, icon, color)
                VALUES (?, ?, 'Despesa', ?, '📦', '#808080')
            """, (category_id, category_name, user['tenant_id']))
            print(f"✅ Categoria criada: {category_id}")
        
        print(f"{'='*60}\n")
        
        # Inserir transação
        transaction_id = str(uuid.uuid4())
        
        # Se for cartão, inserir em installments (parcela única)
        if card_id:
            db.execute("""
                INSERT INTO installments (
                    id, user_id, tenant_id, card_id, category_id,
                    description, installment_number, total_installments,
                    value, due_date, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, 1, 1, ?, ?, 'Pendente', CURRENT_TIMESTAMP)
            """, (
                transaction_id,
                user['id'],
                user['tenant_id'],
                card_id,
                category_id,
                f"{data.get('description', 'Via WhatsApp')} - {payment_method['name']}",
                data.get('amount', 0),
                data.get('date', datetime.now().strftime('%Y-%m-%d'))
            ))
            
            # Atualizar limite usado do cartão
            db.execute("""
                UPDATE cards
                SET used_limit = COALESCE(used_limit, 0) + ?
                WHERE id = ?
            """, (data.get('amount', 0), card_id))
            
        else:
            # Inserir em transactions (conta bancária)
            db.execute("""
                INSERT INTO transactions (
                    id, user_id, tenant_id, account_id, category_id,
                    description, value, type, date, status, is_fixed, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pago', 0, CURRENT_TIMESTAMP)
            """, (
                transaction_id,
                user['id'],
                user['tenant_id'],
                account_id,
                category_id,
                f"{data.get('description', 'Via WhatsApp')} - {payment_method['name']}",
                data.get('amount', 0),
                data.get('type', 'Despesa'),
                data.get('date', datetime.now().strftime('%Y-%m-%d'))
            ))
            
            # Atualizar saldo da conta
            if data.get('type') == 'Receita':
                db.execute("""
                    UPDATE accounts
                    SET current_balance = current_balance + ?
                    WHERE id = ?
                """, (data.get('amount', 0), account_id))
            else:  # Despesa
                db.execute("""
                    UPDATE accounts
                    SET current_balance = current_balance - ?
                    WHERE id = ?
                """, (data.get('amount', 0), account_id))
        
        db.commit()
        db.close()
        
        whatsapp_logger.info(f"✅ Transação inserida: {transaction_id} ({payment_method['type']}: {payment_method['name']})")
        
        # Retornar ID e informações do método de pagamento
        return (transaction_id, payment_method)
        
    except Exception as e:
        whatsapp_logger.error(f"❌ Erro ao inserir transação: {e}")
        import traceback
        traceback.print_exc()
        return None

def send_whatsapp_message(to: str, message: str):
    """Envia mensagem via Node.js server"""
    try:
        response = requests.post(
            f"{WHATSAPP_SERVER_URL}/send",
            json={
                'to': to,
                'message': message,
                'token': WHATSAPP_AUTH_TOKEN
            },
            timeout=10
        )
        
        if response.ok:
            whatsapp_logger.info(f"✅ Mensagem enviada para {to}")
        else:
            whatsapp_logger.error(f"❌ Erro ao enviar: {response.text}")
            
    except Exception as e:
        whatsapp_logger.error(f"❌ Erro ao enviar mensagem: {e}")

@app.route('/api/whatsapp/health')
def whatsapp_health():
    """Health check do sistema WhatsApp"""
    return jsonify({
        'status': 'ok',
        'whatsapp_server': WHATSAPP_SERVER_URL,
        'processors': {
            'audio': audio_proc is not None,
            'ocr': ocr_proc is not None,
            'pdf': pdf_proc is not None,
            'nlp': nlp is not None
        }
    })

@app.route('/api/whatsapp/chat', methods=['POST'])
@login_required
def whatsapp_chat():
    """
    Endpoint para testar chat via WhatsApp sem depender do recebimento automático.
    O usuário envia mensagem e recebe resposta instantânea.
    """
    try:
        data = request.json
        message_text = data.get('message', '').strip()
        
        if not message_text:
            return jsonify({'success': False, 'message': 'Mensagem vazia'}), 400
        
        user = get_current_user()
        
        # Processar mensagem
        text_lower = message_text.lower()
        
        # Detectar tipo
        question_keywords = [
            'quanto gastei', 'quanto recebi', 'qual', 'como está',
            'onde gastei', 'quanto tenho', 'saldo', 'minhas', 'meus',
            'análise', 'resumo', 'total', 'investimentos'
        ]
        
        has_question = any(word in text_lower for word in question_keywords) or '?' in text_lower
        
        transaction_verbs = ['paguei', 'gastei', 'comprei', 'recebi', 'ganhei']
        has_transaction_verb = any(verb in text_lower for verb in transaction_verbs)
        has_value = any(char.isdigit() for char in text_lower)
        
        is_transaction = has_transaction_verb and has_value
        
        if is_transaction:
            # Processar como transação
            nlp_classifier = get_nlp_classifier()
            result = nlp_classifier.classify(message_text)
            result['user_id'] = user['id']
            result['tenant_id'] = user['tenant_id']
            result['original_text'] = message_text
            
            if result.get('amount'):
                transaction_result = insert_transaction_from_whatsapp(result, user.get('phone', ''))
                
                if transaction_result:
                    if isinstance(transaction_result, tuple):
                        transaction_id, payment_info = transaction_result
                    else:
                        transaction_id = transaction_result
                        payment_info = None
                    
                    msg = f"✅ Transação adicionada!\n\n"
                    msg += f"💰 Valor: R$ {result['amount']:.2f}\n"
                    msg += f"📅 Data: {result['date']}\n"
                    msg += f"📂 Categoria: {result['category']}\n"
                    msg += f"📝 Descrição: {result['description']}\n"
                    
                    if payment_info:
                        if payment_info['type'] == 'card':
                            msg += f"💳 Cartão: {payment_info['name']}\n"
                        else:
                            msg += f"🏦 Conta: {payment_info['name']}\n"
                    
                    return jsonify({
                        'success': True,
                        'response': msg,
                        'type': 'transaction'
                    })
        
        # Processar como pergunta (padrão)
        from services.ai_core import BWSInsightAI
        from services.ai_chat import AIChat
        
        ai = BWSInsightAI(user_id=user['id'], tenant_id=user['tenant_id'])
        chat = AIChat(ai)
        financial_data = ai.fetch_financial_data_direct(user['id'], user['tenant_id'])
        ai_response = chat.process_message(message_text, financial_data)
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'type': 'question'
        })
        
    except Exception as e:
        print(f"Erro em whatsapp_chat: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500



@app.route('/investments/edit', methods=['POST'])
@login_required
def edit_investment():
    user = get_current_user()
    data = request.get_json()
    
    investment_id = data.get('id')
    name = data.get('name')
    inv_type = data.get('type')
    amount = float(data.get('amount', 0))
    
    db = get_db()
    db.execute("""
        UPDATE investments 
        SET name = ?, type = ?, invested_value = ?, current_value = ?
        WHERE id = ? AND user_id = ? AND tenant_id = ?
    """, (name, inv_type, amount, amount, investment_id, user['id'], user['tenant_id']))
    
    db.commit()
    db.close()
    
    return jsonify({'success': True, 'message': 'Investimento atualizado!'})

@app.route('/investments/delete', methods=['POST'])
@login_required
def delete_investment():
    """Rota antiga - mantida para compatibilidade"""
    user = get_current_user()
    data = request.get_json()
    
    investment_id = data.get('id')
    
    db = get_db()
    db.execute("""
        DELETE FROM investments 
        WHERE id = ? AND user_id = ? AND tenant_id = ?
    """, (investment_id, user['id'], user['tenant_id']))
    
    db.commit()
    db.close()
    
    return jsonify({'success': True, 'message': 'Investimento excluído!'})

@app.route('/investments/delete/<int:investment_id>', methods=['POST', 'GET'])
@login_required
def delete_investment_by_id(investment_id):
    """Deleta um investimento específico pelo ID"""
    print(f"🗑️ Chamando delete_investment_by_id com ID: {investment_id}")
    print(f"📊 Método HTTP: {request.method}")
    
    user = get_current_user()
    print(f"👤 Usuário: {user['id'] if user else 'None'}")
    
    try:
        db = get_db()
        
        # Verificar se o investimento existe e pertence ao usuário
        investment = db.execute("""
            SELECT name FROM investments 
            WHERE id = ? AND user_id = ? AND tenant_id = ?
        """, (investment_id, user['id'], user['tenant_id'])).fetchone()
        
        if not investment:
            db.close()
            return jsonify({'success': False, 'error': 'Investimento não encontrado'}), 404
        
        # Deletar o investimento
        db.execute("""
            DELETE FROM investments 
            WHERE id = ? AND user_id = ? AND tenant_id = ?
        """, (investment_id, user['id'], user['tenant_id']))
        
        db.commit()
        db.close()
        
        print(f"✅ Investimento deletado com sucesso!")
        return jsonify({'success': True, 'message': 'Investimento excluído com sucesso!'}), 200
        
    except Exception as e:
        print(f"❌ Erro ao deletar investimento: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/test-delete/<int:test_id>')
def test_delete_route(test_id):
    """Rota de teste para verificar se o Flask está capturando IDs na URL"""
    return jsonify({
        'success': True,
        'message': f'Rota de teste funcionando! ID recebido: {test_id}',
        'url': request.url,
        'path': request.path
    })

# =====================================================
# NOTIFICATIONS SYSTEM
# =====================================================

from services.notification_center import (
    NotificationCenter, 
    NotificationCategory, 
    NotificationPriority,
    NotificationChannel
)

@app.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications():
    """Lista notificações do usuário"""
    user = get_current_user()
    
    status = request.args.get('status')  # 'unread', 'read', 'archived'
    limit = request.args.get('limit', 50, type=int)
    
    center = NotificationCenter()
    notifications = center.get_user_notifications(user['id'], status=status, limit=limit)
    unread_count = center.get_unread_count(user['id'])
    
    return jsonify({
        'success': True,
        'notifications': notifications,
        'unread_count': unread_count
    })

@app.route('/api/notifications', methods=['POST'])
@login_required
def create_notification_api():
    """Cria nova notificação (admin ou sistema)"""
    user = get_current_user()
    data = request.json
    
    # Validar campos obrigatórios
    if not data.get('title') or not data.get('message'):
        return jsonify({'error': 'Title and message are required'}), 400
    
    center = NotificationCenter()
    
    # Parsear categoria e prioridade
    try:
        category = NotificationCategory[data.get('category', 'SISTEMA').upper()]
        priority = NotificationPriority[data.get('priority', 'NORMAL').upper()]
    except KeyError:
        return jsonify({'error': 'Invalid category or priority'}), 400
    
    # Parsear canais
    channels = []
    for ch in data.get('channels', ['system']):
        try:
            channels.append(NotificationChannel[ch.upper()])
        except KeyError:
            pass
    
    notification_id = center.create_notification(
        user_id=user['id'],
        tenant_id=user['tenant_id'],
        title=data['title'],
        message=data['message'],
        category=category,
        priority=priority,
        channels=channels,
        related_type=data.get('related_type'),
        related_id=data.get('related_id'),
        metadata=data.get('metadata')
    )
    
    if notification_id:
        return jsonify({'success': True, 'id': notification_id}), 201
    else:
        return jsonify({'error': 'Failed to create notification'}), 500

@app.route('/api/notifications/<int:notification_id>/read', methods=['PATCH'])
@login_required
def mark_notification_read(notification_id):
    """Marca notificação como lida"""
    user = get_current_user()
    
    center = NotificationCenter()
    success = center.mark_as_read(notification_id, user['id'])
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Notification not found'}), 404

@app.route('/api/notifications/read-all', methods=['PATCH', 'POST'])
@app.route('/api/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Marca todas notificações como lidas"""
    user = get_current_user()
    
    center = NotificationCenter()
    count = center.mark_all_as_read(user['id'])
    
    return jsonify({'success': True, 'count': count})

@app.route('/api/notifications/<int:notification_id>', methods=['DELETE'])
@login_required
def delete_notification_api(notification_id):
    """Deleta notificação"""
    user = get_current_user()
    
    center = NotificationCenter()
    success = center.delete_notification(notification_id, user['id'])
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Notification not found'}), 404

@app.route('/api/notifications/preferences', methods=['GET'])
@login_required
def get_notification_preferences():
    """Busca preferências de notificações"""
    user = get_current_user()
    
    center = NotificationCenter()
    prefs = center.get_user_preferences(user['id'])
    
    return jsonify({'success': True, 'preferences': prefs})

@app.route('/api/notifications/preferences', methods=['PUT'])
@login_required
def update_notification_preferences():
    """Atualiza preferências de notificações"""
    user = get_current_user()
    data = request.json
    
    center = NotificationCenter()
    success = center.update_preferences(user['id'], data)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to update preferences'}), 500

@app.route('/notifications/preferences')
@login_required
def notification_preferences_page():
    """Página de configurações de notificações"""
    user = get_current_user()
    
    center = NotificationCenter()
    prefs = center.get_user_preferences(user['id'])
    
    return render_template('notification_preferences.html', user=user, preferences=prefs)

@app.route('/api/notifications/ai-insights', methods=['GET'])
@login_required
def get_ai_insights():
    """Retorna insights de IA sobre finanças"""
    user = get_current_user()
    
    from services.notification_ai import NotificationAI
    
    ai = NotificationAI()
    days = request.args.get('days', 30, type=int)
    insights = ai.analyze_spending_patterns(user['id'], days=days)
    
    return jsonify({
        'success': True,
        'insights': insights,
        'count': len(insights)
    })

@app.route('/api/notifications/monthly-report', methods=['GET'])
@login_required
def get_monthly_report():
    """Gera relatório mensal com IA"""
    user = get_current_user()
    
    from services.notification_ai import NotificationAI
    
    ai = NotificationAI()
    report = ai.generate_monthly_report(user['id'])
    
    return jsonify({
        'success': True,
        'report': report
    })

# =====================================================
# API SETTINGS / PROFILE
# =====================================================

@app.route('/api/profile', methods=['GET', 'PUT'])
@login_required
def api_profile():
    """API para gerenciar perfil do usuário"""
    user = get_current_user()
    db = get_db()
    
    if request.method == 'GET':
        # Buscar dados do perfil
        profile = db.execute("""
            SELECT name, email, phone, birthdate, bio, avatar 
            FROM users WHERE id = ?
        """, (user['id'],)).fetchone()
        
        return jsonify({
            'success': True,
            'profile': dict(profile) if profile else {}
        })
    
    elif request.method == 'PUT':
        # Atualizar perfil
        data = request.json
        
        try:
            db.execute("""
                UPDATE users 
                SET name = ?, phone = ?, birthdate = ?, bio = ?
                WHERE id = ?
            """, (
                data.get('name'),
                data.get('phone'),
                data.get('birthdate'),
                data.get('bio'),
                user['id']
            ))
            db.commit()
            
            return jsonify({
                'success': True,
                'message': 'Perfil atualizado com sucesso!'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Erro ao atualizar perfil: {str(e)}'
            }), 500

@app.route('/api/preferences', methods=['GET', 'PUT'])
@login_required
def api_preferences():
    """API para gerenciar preferências do usuário"""
    user = get_current_user()
    db = get_db()
    
    if request.method == 'GET':
        # Buscar preferências
        prefs = db.execute("""
            SELECT language, currency, timezone, dark_mode, compact_dashboard,
                   show_balance, save_search_history, allow_analytics
            FROM user_preferences WHERE user_id = ?
        """, (user['id'],)).fetchone()
        
        if not prefs:
            # Criar preferências padrão
            db.execute("""
                INSERT INTO user_preferences (user_id, tenant_id, language, currency, timezone)
                VALUES (?, ?, 'pt-BR', 'BRL', 'America/Sao_Paulo')
            """, (user['id'], user['tenant_id']))
            db.commit()
            
            prefs = db.execute("""
                SELECT language, currency, timezone, dark_mode, compact_dashboard,
                       show_balance, save_search_history, allow_analytics
                FROM user_preferences WHERE user_id = ?
            """, (user['id'],)).fetchone()
        
        return jsonify({
            'success': True,
            'preferences': dict(prefs) if prefs else {}
        })
    
    elif request.method == 'PUT':
        # Atualizar preferências
        data = request.json
        
        try:
            db.execute("""
                UPDATE user_preferences 
                SET language = ?, currency = ?, timezone = ?, 
                    dark_mode = ?, compact_dashboard = ?,
                    show_balance = ?, save_search_history = ?, allow_analytics = ?
                WHERE user_id = ?
            """, (
                data.get('language', 'pt-BR'),
                data.get('currency', 'BRL'),
                data.get('timezone', 'America/Sao_Paulo'),
                data.get('dark_mode', False),
                data.get('compact_dashboard', False),
                data.get('show_balance', True),
                data.get('save_search_history', True),
                data.get('allow_analytics', False),
                user['id']
            ))
            db.commit()
            
            return jsonify({
                'success': True,
                'message': 'Preferências atualizadas com sucesso!'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Erro ao atualizar preferências: {str(e)}'
            }), 500

@app.route('/api/account/delete', methods=['POST'])
@login_required
def api_delete_account():
    """API para excluir conta do usuário"""
    user = get_current_user()
    db = get_db()
    data = request.json
    
    password = data.get('password')
    
    if not password:
        return jsonify({
            'success': False,
            'message': 'Senha obrigatória para confirmar exclusão'
        }), 400
    
    # Verificar senha
    user_data = db.execute("SELECT password FROM users WHERE id = ?", (user['id'],)).fetchone()
    
    if not check_password_hash(user_data['password'], password):
        return jsonify({
            'success': False,
            'message': 'Senha incorreta'
        }), 401
    
    try:
        # Excluir dados relacionados (em ordem de dependências)
        db.execute("DELETE FROM transactions WHERE user_id = ?", (user['id'],))
        db.execute("DELETE FROM investments WHERE user_id = ?", (user['id'],))
        db.execute("DELETE FROM accounts WHERE user_id = ?", (user['id'],))
        db.execute("DELETE FROM cards WHERE user_id = ?", (user['id'],))
        db.execute("DELETE FROM notifications WHERE user_id = ?", (user['id'],))
        db.execute("DELETE FROM notification_preferences WHERE user_id = ?", (user['id'],))
        db.execute("DELETE FROM user_preferences WHERE user_id = ?", (user['id'],))
        db.execute("DELETE FROM users WHERE id = ?", (user['id'],))
        db.commit()
        
        # Limpar sessão
        session.clear()
        
        return jsonify({
            'success': True,
            'message': 'Conta excluída com sucesso'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao excluir conta: {str(e)}'
        }), 500

# =====================================================
# MAIN
# =====================================================

if __name__ == '__main__':
    # Criar banco se não existir
    if not os.path.exists(app.config['DATABASE']):
        print("🔨 Creating database...")
        init_db()
        seed_default_data()
    
    # Iniciar scheduler de transações recorrentes
    from scheduler import start_scheduler
    start_scheduler()
    
    print("[START] BWS Finance Flask Server...")
    print("[LOCAL] http://localhost:5000")
    print("[EXTERNAL] http://45.173.36.138:5000")

    # DEBUG: listar todas as rotas registradas para verificar url_map
    try:
        print('\n=== Registered routes (app.url_map) ===')
        for rule in sorted(app.url_map.iter_rules(), key=lambda r: (r.rule, r.endpoint)):
            methods = ','.join(sorted(rule.methods)) if rule.methods else ''
            print(f"{rule.rule} -> endpoint: {rule.endpoint} (methods: {methods})")
        print('=== End routes ===\n')
    except Exception as e:
        print('Erro ao imprimir url_map:', e)
    
    print("[OK] WhatsApp Integration: Ready!")
    print("[DASHBOARD] http://localhost:5000/dashboard")
    print("=" * 50)
    
    try:
        # Porta pode ser configurada via variável de ambiente
        port = int(os.environ.get('PORT', 80))
        print(f"[FLASK] Iniciando servidor na porta {port}...")
        print(f"[FLASK] Acessível em: http://0.0.0.0:{port} e http://192.168.80.132:{port}")
        # Use environ to allow CLI override
        if __name__ == '__main__':
            app.run(
                debug=False, 
                host='0.0.0.0',  # Aceita conexões de qualquer IP da rede
                port=port, 
                threaded=True, 
                use_reloader=False,
                use_evalex=False,
                use_debugger=False
            )
    except Exception as e:
        print(f"[ERRO] Falha ao iniciar servidor: {e}")
        import traceback
        traceback.print_exc()
