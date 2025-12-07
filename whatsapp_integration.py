# WhatsApp Integration - Adicionar ao final do app.py

# =====================================================
# WHATSAPP INTEGRATION
# =====================================================

import logging
from modules.audio_processor import AudioProcessor
from modules.ocr_processor import OCRProcessor
from modules.pdf_processor import PDFProcessor
from modules.nlp_classifier import NLPClassifier
import requests

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/whatsapp.log'),
        logging.StreamHandler()
    ]
)

whatsapp_logger = logging.getLogger('whatsapp')

# Inicializar processadores
audio_proc = AudioProcessor(whisper_model='small')
ocr_proc = OCRProcessor(language='por')
pdf_proc = PDFProcessor()
nlp = NLPClassifier()

WHATSAPP_SERVER_URL = os.getenv('WHATSAPP_SERVER_URL', 'http://localhost:3000')
WHATSAPP_AUTH_TOKEN = os.getenv('WHATSAPP_AUTH_TOKEN', 'change_me')

@app.route('/api/whatsapp/webhook', methods=['POST'])
def whatsapp_webhook():
    """
    Recebe mensagens do WhatsApp via Node.js server
    
    Payload esperado:
    {
        "from": "+5511999999999",
        "type": "text|audio|image|document",
        "text": "...",
        "media_url": "/path/to/file",
        "filename": "file.ext"
    }
    """
    try:
        # Validar token
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer ') or auth_header.split(' ')[1] != WHATSAPP_AUTH_TOKEN:
            whatsapp_logger.warning("⛔ Token inválido")
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.json
        whatsapp_logger.info(f"📨 Webhook recebido: {data.get('type')} de {data.get('from')}")
        
        message_type = data.get('type')
        text = data.get('text', '')
        media_url = data.get('media_url')
        sender = data.get('from')
        
        # Processar diferentes tipos
        extracted_text = None
        
        if message_type == 'text':
            extracted_text = text
            
        elif message_type == 'audio':
            whatsapp_logger.info(f"🎤 Processando áudio: {media_url}")
            extracted_text = audio_proc.process_audio(media_url)
            
        elif message_type == 'image':
            whatsapp_logger.info(f"🖼️ Processando imagem: {media_url}")
            extracted_text = ocr_proc.process_image(media_url)
            
        elif message_type == 'document':
            if media_url and media_url.endswith('.pdf'):
                whatsapp_logger.info(f"📄 Processando PDF: {media_url}")
                transactions = pdf_proc.process_pdf(media_url)
                
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
        
        # Se temos texto extraído, classificar e inserir
        if extracted_text:
            result = nlp.classify(extracted_text)
            
            if result.get('amount'):
                # Inserir transação
                transaction_id = insert_transaction_from_whatsapp(result, sender)
                
                if transaction_id:
                    msg = f"✅ Transação adicionada!\n\n"
                    msg += f"💰 Valor: R$ {result['amount']:.2f}\n"
                    msg += f"📅 Data: {result['date']}\n"
                    msg += f"📂 Categoria: {result['category']}\n"
                    msg += f"📝 Descrição: {result['description']}\n"
                    
                    if result.get('confidence', 0) < 0.7:
                        msg += f"\n⚠️ Confiança baixa. Verifique os dados!"
                    
                    send_whatsapp_message(sender, msg)
                    
                    return jsonify({
                        'success': True,
                        'message': msg,
                        'transaction_id': transaction_id
                    })
            else:
                # Não conseguiu extrair valor
                msg = "⚠️ Não consegui identificar o valor da transação.\n"
                msg += "Envie assim: 'Paguei R$ 50,00 no mercado hoje'"
                
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

def insert_transaction_from_whatsapp(data: dict, sender: str) -> str:
    """Insere transação no banco vindapor WhatsApp"""
    try:
        db = get_db()
        
        # Buscar usuário pelo telefone (implementar associação)
        # Por enquanto, usar primeiro usuário
        user = db.execute("SELECT * FROM users LIMIT 1").fetchone()
        
        if not user:
            whatsapp_logger.error("❌ Nenhum usuário encontrado")
            return None
        
        # Buscar conta padrão ou criar
        account = db.execute("""
            SELECT id FROM accounts
            WHERE user_id = ? AND tenant_id = ?
            LIMIT 1
        """, (user['id'], user['tenant_id'])).fetchone()
        
        if not account:
            # Criar conta padrão
            account_id = str(uuid.uuid4())
            db.execute("""
                INSERT INTO accounts (id, user_id, tenant_id, name, type, initial_balance, current_balance)
                VALUES (?, ?, ?, 'WhatsApp', 'Corrente', 0, 0)
            """, (account_id, user['id'], user['tenant_id']))
        else:
            account_id = account['id']
        
        # Buscar categoria
        category = db.execute("""
            SELECT id FROM categories
            WHERE name = ? AND tenant_id = ? AND parent_id IS NULL
            LIMIT 1
        """, (data.get('category', 'Outros'), user['tenant_id'])).fetchone()
        
        category_id = category['id'] if category else None
        
        # Inserir transação
        transaction_id = str(uuid.uuid4())
        
        db.execute("""
            INSERT INTO transactions (
                id, user_id, tenant_id, account_id, category_id,
                description, value, type, date, is_fixed, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, CURRENT_TIMESTAMP)
        """, (
            transaction_id,
            user['id'],
            user['tenant_id'],
            account_id,
            category_id,
            data.get('description', 'Via WhatsApp'),
            data.get('amount', 0),
            data.get('type', 'Despesa'),
            data.get('date', datetime.now().strftime('%Y-%m-%d'))
        ))
        
        db.commit()
        db.close()
        
        whatsapp_logger.info(f"✅ Transação inserida: {transaction_id}")
        return transaction_id
        
    except Exception as e:
        whatsapp_logger.error(f"❌ Erro ao inserir transação: {e}")
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
            'audio': audio_proc.whisper_loaded or audio_proc.vosk_loaded,
            'ocr': True,
            'pdf': True,
            'nlp': True
        }
    })
