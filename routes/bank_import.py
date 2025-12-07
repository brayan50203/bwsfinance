"""
Rotas de Importação de Extratos Bancários
Blueprint Flask para /api/import/*
"""

from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
from functools import wraps

# Importar módulo de importação
from services.bank_importer import BankStatementImporter, detect_file_type

# Configuração
UPLOAD_FOLDER = 'temp_uploads'
ALLOWED_EXTENSIONS = {'ofx', 'csv', 'pdf', 'json'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Criar pasta de uploads se não existir
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Blueprint
import_bp = Blueprint('import', __name__, url_prefix='/api/import')


def login_required_api(f):
    """Decorator para verificar login em rotas API"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Não autenticado'}), 401
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_db():
    """Importa e retorna conexão com banco de dados"""
    import sqlite3
    conn = sqlite3.connect('bws_finance.db')
    conn.row_factory = sqlite3.Row
    return conn


@import_bp.route('/manual', methods=['POST'])
@login_required_api
def import_manual():
    """
    POST /api/import/manual
    Upload e processamento de arquivo de extrato
    
    Form Data:
        file: arquivo (OFX, CSV, PDF)
        account_id: ID da conta destino
        auto_categorize: true/false (categorização automática)
    """
    user_id = session.get('user_id')
    tenant_id = session.get('tenant_id')
    
    print(f"🔍 DEBUG - Import Manual Request:")
    print(f"  User ID: {user_id}")
    print(f"  Tenant ID: {tenant_id}")
    print(f"  Files: {list(request.files.keys())}")
    print(f"  Form: {dict(request.form)}")
    
    # Validar arquivo
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Nome de arquivo vazio'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': f'Formato não suportado. Use: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
    
    # Validar conta ou cartão
    import_type = request.form.get('import_type', 'account')
    account_id = request.form.get('account_id')
    card_id = request.form.get('card_id')
    
    if import_type == 'card':
        if not card_id:
            return jsonify({'success': False, 'error': 'ID do cartão não informado'}), 400
        
        print(f"  Card ID: {card_id}")
        
        # Verificar se o cartão pertence ao usuário
        db = get_db()
        card = db.execute("""
            SELECT id FROM cards 
            WHERE id = ? AND user_id = ? AND tenant_id = ?
        """, (card_id, user_id, tenant_id)).fetchone()
        
        if not card:
            db.close()
            print(f"  ❌ Cartão não encontrado!")
            return jsonify({'success': False, 'error': 'Cartão não encontrado ou sem permissão'}), 404
        
        print(f"  ✅ Cartão validado: {card_id}")
        account_id = None  # Importação para cartão não usa account_id
        
    else:
        if not account_id:
            return jsonify({'success': False, 'error': 'ID da conta não informado'}), 400
        
        print(f"  Account ID: {account_id}")
        
        # Verificar se a conta pertence ao usuário
        db = get_db()
        account = db.execute("""
            SELECT id FROM accounts 
            WHERE id = ? AND user_id = ? AND tenant_id = ?
        """, (account_id, user_id, tenant_id)).fetchone()
        
        if not account:
            db.close()
            print(f"  ❌ Conta não encontrada!")
            return jsonify({'success': False, 'error': 'Conta não encontrada ou sem permissão'}), 404
        
        print(f"  ✅ Conta validada: {account_id}")
    
    # Salvar arquivo temporariamente
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{filename}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    
    print(f"  💾 Salvando arquivo: {filename}")
    
    try:
        file.save(file_path)
        print(f"  ✅ Arquivo salvo em: {file_path}")
        
        # Detectar tipo de arquivo
        file_type = detect_file_type(filename)
        print(f"  📄 Tipo detectado: {file_type}")
        
        # Inicializar importador
        importer = BankStatementImporter(user_id, tenant_id)
        print(f"  🔧 Importador inicializado")
        
        # Processar arquivo
        transactions = []
        
        if file_type == 'ofx':
            print(f"  📖 Processando OFX...")
            transactions = importer.parse_ofx(file_path)
        elif file_type == 'csv':
            print(f"  📖 Processando CSV...")
            transactions = importer.parse_csv(file_path)
        elif file_type == 'pdf':
            print(f"  📖 Processando PDF...")
            transactions = importer.parse_pdf(file_path)
        else:
            print(f"  ❌ Formato não suportado: {file_type}")
            return jsonify({'success': False, 'error': 'Formato de arquivo não suportado'}), 400
        
        print(f"  📊 Transações extraídas: {len(transactions)}")
        
        if not transactions:
            return jsonify({
                'success': False,
                'error': 'Nenhuma transação encontrada no arquivo',
                'details': importer.errors
            }), 400
        
        # Importar transações
        auto_categorize = request.form.get('auto_categorize', 'true').lower() == 'true'
        
        # Se for cartão, passar card_id nas transações
        if import_type == 'card':
            # Adicionar card_id em cada transação
            for txn in transactions:
                txn['card_id'] = card_id
                txn['payment_method'] = 'credit_card'
            result = importer.import_transactions(transactions, None, db, auto_categorize)
        else:
            result = importer.import_transactions(transactions, account_id, db, auto_categorize)
            
            # Atualizar saldo da conta (apenas para contas bancárias)
            from routes.accounts import recalculate_account_balance
            recalculate_account_balance(account_id)
        
        # Registrar log de importação
        import_id = str(uuid.uuid4())
        log_account_id = account_id if import_type == 'account' else None
        log_card_id = card_id if import_type == 'card' else None
        db.execute("""
            INSERT INTO import_logs (
                id, user_id, tenant_id, account_id, card_id,
                file_name, file_type, total_transactions, 
                imported_transactions, duplicated_transactions, 
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            import_id, user_id, tenant_id, log_account_id, log_card_id,
            filename, file_type, result['total'],
            result['imported'], result['duplicated']
        ))
        db.commit()
        
        # Notificar IA
        target_id = card_id if import_type == 'card' else account_id
        _notify_ai_import(user_id, tenant_id, target_id, result)
        
        return jsonify({
            'success': True,
            'message': f'✅ Importação concluída! {result["imported"]} transações adicionadas.',
            'stats': result,
            'import_id': import_id
        }), 200
        
    except Exception as e:
        print(f"  ❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Erro ao processar arquivo: {str(e)}'}), 500
    
    finally:
        # Limpar arquivo temporário
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        db.close()


@import_bp.route('/status', methods=['GET'])
@login_required_api
def import_status():
    """
    GET /api/import/status
    Retorna histórico de importações do usuário
    """
    user_id = session.get('user_id')
    tenant_id = session.get('tenant_id')
    
    db = get_db()
    
    # Buscar últimas importações
    imports = db.execute("""
        SELECT 
            i.id, i.file_name, i.file_type, 
            i.total_transactions, i.imported_transactions, 
            i.duplicated_transactions, i.created_at,
            a.name as account_name
        FROM import_logs i
        LEFT JOIN accounts a ON i.account_id = a.id
        WHERE i.user_id = ? AND i.tenant_id = ?
        ORDER BY i.created_at DESC
        LIMIT 10
    """, (user_id, tenant_id)).fetchall()
    
    db.close()
    
    return jsonify({
        'success': True,
        'imports': [dict(imp) for imp in imports]
    }), 200


@import_bp.route('/preview', methods=['POST'])
@login_required_api
def import_preview():
    """
    POST /api/import/preview
    Pré-visualização de transações do arquivo (sem salvar)
    
    Form Data:
        file: arquivo (OFX, CSV, PDF)
    """
    user_id = session.get('user_id')
    tenant_id = session.get('tenant_id')
    
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    
    if not allowed_file(file.filename):
        return jsonify({'error': f'Formato não suportado'}), 400
    
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{filename}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    
    try:
        file.save(file_path)
        
        file_type = detect_file_type(filename)
        importer = BankStatementImporter(user_id, tenant_id)
        
        transactions = []
        
        if file_type == 'ofx':
            transactions = importer.parse_ofx(file_path)
        elif file_type == 'csv':
            transactions = importer.parse_csv(file_path)
        elif file_type == 'pdf':
            transactions = importer.parse_pdf(file_path)
        
        return jsonify({
            'success': True,
            'file_type': file_type,
            'total': len(transactions),
            'transactions': transactions[:50],  # Primeiras 50
            'errors': importer.errors
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass


def _notify_ai_import(user_id: str, tenant_id: str, account_id: str, result: dict):
    """Notifica a IA sobre nova importação para gerar insights"""
    try:
        from services.ai_core import BWSInsightAI
        
        db = get_db()
        
        # Buscar nome da conta
        account = db.execute("SELECT name FROM accounts WHERE id = ?", (account_id,)).fetchone()
        account_name = account['name'] if account else 'Conta'
        
        db.close()
        
        # Gerar insight automático
        ai = BWSInsightAI(base_url='http://localhost:5000', user_id=user_id, tenant_id=tenant_id)
        
        insight_text = f"""📥 Nova importação de extrato bancário detectada!

🏦 Conta: {account_name}
📊 Total de transações: {result['total']}
✅ Importadas: {result['imported']}
⚠️ Duplicadas: {result['duplicated']}
❌ Erros: {result['errors']}

💡 Recomendação: Revise as transações importadas e confirme se as categorizações automáticas estão corretas."""
        
        ai.save_insight(
            insight_type='import_notification',
            insight_text=insight_text,
            severity='info',
            data={'account_id': account_id, 'stats': result}
        )
        
    except Exception as e:
        print(f"Erro ao notificar IA: {e}")


# Registrar blueprint no app principal
def register_import_routes(app):
    """Registra as rotas de importação no app Flask"""
    app.register_blueprint(import_bp)
