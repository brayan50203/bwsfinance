# 📱 WhatsApp: Registro Automático de Transações

## 🎯 Visão Geral

O BWS Finance possui um sistema completo de **registro automático de transações via WhatsApp**. Você pode enviar mensagens de texto, áudios ou fotos de recibos e o sistema **automaticamente** identifica, classifica e registra suas transações financeiras.

---

## 🚀 Como Funciona

### 1️⃣ **Mensagens de Texto**

Envie uma mensagem simples descrevendo a transação:

**Exemplos:**
```
Paguei R$ 50,00 no mercado hoje
```
```
Gastei 150 reais no posto de gasolina
```
```
Recebi 3000 de salário
```
```
Comprei uma pizza de 45 reais ontem
```

**O que o sistema faz:**
- ✅ Extrai o **valor** (R$ 50,00, 150 reais)
- ✅ Identifica a **categoria** (mercado, gasolina, salário, pizza/alimentação)
- ✅ Detecta a **data** (hoje, ontem, ou data atual)
- ✅ Identifica se é **Receita ou Despesa**
- ✅ Escolhe **conta ou cartão** automaticamente
- ✅ Registra a transação no banco de dados
- ✅ Envia confirmação com todos os detalhes

---

### 2️⃣ **Mensagens de Áudio** 🎤

Grave um áudio dizendo a transação:

**Exemplos:**
```
[Áudio] "Ó, paguei cinquenta reais no mercado agora"
```
```
[Áudio] "Recebi dois mil de freelance"
```

**O que o sistema faz:**
1. **Transcreve** o áudio usando **Whisper AI** (OpenAI)
2. Processa o texto transcrito igual mensagem de texto
3. Registra a transação automaticamente

---

### 3️⃣ **Fotos de Recibos** 📸

Tire uma foto do recibo, nota fiscal ou comprovante:

**Exemplos:**
- 📸 Cupom fiscal do supermercado
- 📸 Recibo de restaurante
- 📸 Nota fiscal de loja
- 📸 Comprovante de transferência bancária

**O que o sistema faz:**
1. **OCR** (Optical Character Recognition) usando **Tesseract**
2. Extrai o texto da imagem
3. Identifica valores, estabelecimento, data
4. Classifica e registra automaticamente

---

### 4️⃣ **Extratos em PDF** 📄

Envie o PDF do extrato bancário ou fatura de cartão:

**O que o sistema faz:**
1. Lê o PDF e extrai todas as transações
2. Identifica múltiplos lançamentos de uma vez
3. Classifica cada transação
4. Registra todas no sistema
5. Retorna: "✅ 15 transações adicionadas do extrato!"

---

## 🤖 Inteligência Artificial

### **Classificação Automática**

O sistema usa **NLP (Natural Language Processing)** para:

#### **1. Detectar Valor Monetário**
```python
"Paguei R$ 50,00" → 50.00
"Gastei 150 reais" → 150.00
"Comprei por 45" → 45.00
```

#### **2. Identificar Categoria**
```python
"mercado" → Supermercado
"gasolina" → Combustível
"uber" → Transporte
"pizza" → Alimentação/Restaurante
"salário" → Salário
"netflix" → TV/Streaming
```

#### **3. Detectar Data**
```python
"hoje" → 2024-12-19
"ontem" → 2024-12-18
"dia 15" → 2024-12-15
(sem data) → data atual
```

#### **4. Tipo (Receita/Despesa)**
```python
"paguei", "gastei", "comprei" → Despesa
"recebi", "ganhei" → Receita
```

#### **5. Conta ou Cartão**

**Detecção Inteligente:**
- "no cartão" → Busca cartão de crédito
- "no débito" → Busca conta corrente
- "no nubank" → Busca conta/cartão Nubank
- "no inter" → Busca conta Inter
- Sem especificação → Usa conta padrão

---

## 💬 Modo de Perguntas (Chat IA)

Além de registrar transações, você pode **fazer perguntas** sobre suas finanças:

### **Exemplos de Perguntas:**

```
Quanto gastei esse mês?
```
```
Qual meu saldo?
```
```
Quanto gastei com alimentação?
```
```
Quanto recebi de salário?
```
```
Como estão meus investimentos?
```
```
Quanto lucrei com ações?
```
```
Quanto tenho em Bitcoin?
```

**Resposta da IA:**
```
📊 Resumo Financeiro - Dezembro 2024

💰 Receitas: R$ 5.000,00
💸 Despesas: R$ 3.200,00
✅ Saldo: R$ 1.800,00

📂 Maiores Gastos:
🛒 Supermercado: R$ 800,00
🚗 Combustível: R$ 600,00
🍽️ Alimentação: R$ 450,00
```

---

## ⚙️ Configuração Técnica

### **1. Arquitetura**

```
WhatsApp → Node.js (WPPConnect) → Flask (Python) → SQLite
                ↓
         [Webhook: /api/whatsapp/webhook]
                ↓
    [Processamento: Texto/Áudio/Imagem]
                ↓
    [IA: NLP Classifier + Whisper + OCR]
                ↓
           [Banco de Dados]
```

### **2. Componentes**

| Componente | Tecnologia | Função |
|------------|-----------|---------|
| **WhatsApp Bot** | WPPConnect (Node.js) | Recebe mensagens |
| **Webhook** | Flask (/api/whatsapp/webhook) | Processa mensagens |
| **NLP** | NLPClassifier (Python) | Classifica transações |
| **Áudio** | Whisper (OpenAI) | Transcreve áudio |
| **OCR** | Tesseract | Extrai texto de imagens |
| **PDF** | PyPDF2 | Lê extratos PDF |
| **IA Chat** | BWSInsightAI | Responde perguntas |

### **3. Fluxo de Processamento**

```python
# 1. WhatsApp envia mensagem → Webhook
@app.route('/api/whatsapp/webhook', methods=['POST'])
def whatsapp_webhook():
    data = request.json
    message_type = data.get('type')  # text, audio, image, document
    sender = data.get('from')        # +5511999999999
    text = data.get('text')
    
    # 2. Processar por tipo
    if message_type == 'text':
        extracted_text = text
    elif message_type == 'audio':
        extracted_text = audio_processor.transcribe(audio_url)
    elif message_type == 'image':
        extracted_text = ocr_processor.extract_text(image_url)
    
    # 3. Decidir: Pergunta ou Transação?
    if is_question(extracted_text):
        # Modo Chat IA
        ai_response = ai_chat.process_message(extracted_text)
        send_whatsapp_message(sender, ai_response)
    else:
        # Modo Transação
        result = nlp_classifier.classify(extracted_text)
        transaction_id = insert_transaction_from_whatsapp(result, sender)
        send_whatsapp_message(sender, "✅ Transação registrada!")
```

---

## 📋 Requisitos

### **Pacotes Python:**
```bash
pip install openai-whisper
pip install pytesseract
pip install pypdf2
pip install nltk
pip install spacy
pip install python-dateutil
```

### **Dependências do Sistema:**
- **Tesseract OCR**: Para processar imagens
- **FFmpeg**: Para processar áudios

**Windows:**
```powershell
# Tesseract
choco install tesseract

# FFmpeg
choco install ffmpeg
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install ffmpeg
```

---

## 🔐 Segurança

### **Autenticação**

O webhook usa **Bearer Token** para autenticação:

```python
WHATSAPP_AUTH_TOKEN = os.getenv('WHATSAPP_AUTH_TOKEN', 'change_me')

# Validar token
auth_header = request.headers.get('Authorization', '')
if not auth_header.startswith('Bearer ') or auth_header.split(' ')[1] != WHATSAPP_AUTH_TOKEN:
    return jsonify({'error': 'Unauthorized'}), 401
```

### **Variáveis de Ambiente**

```bash
# .env
WHATSAPP_AUTH_TOKEN=seu_token_secreto_aqui
WHATSAPP_SERVER_URL=http://localhost:3000
```

---

## 🧪 Como Testar

### **1. Iniciar Servidores**

```powershell
# Terminal 1: Flask (porta 80)
$env:PORT=80
python app.py

# Terminal 2: WhatsApp Bot (porta 3000)
cd whatsapp_server
npm start
```

### **2. Conectar WhatsApp**

1. Abrir: http://localhost:3000
2. Escanear QR Code com WhatsApp
3. Aguardar: "✅ WhatsApp conectado!"

### **3. Cadastrar Número**

```sql
-- Adicionar seu número ao banco de dados
UPDATE users 
SET phone = '+5511999999999' 
WHERE email = 'seu@email.com';
```

### **4. Enviar Mensagem de Teste**

Envie para o número conectado:
```
Paguei R$ 50,00 no mercado hoje
```

**Resposta esperada:**
```
✅ Transação adicionada!

💰 Valor: R$ 50,00
📅 Data: 2024-12-19
📂 Categoria: Supermercado
📝 Descrição: mercado
🏦 Conta: Conta Principal
```

---

## 🎨 Personalização

### **Adicionar Novas Categorias**

Edite `modules/nlp_classifier.py`:

```python
self.category_keywords = {
    'Supermercado': ['mercado', 'supermercado', 'feira', 'hortifruti'],
    'SuaNovaCategoria': ['palavra1', 'palavra2', 'palavra3'],
}
```

### **Ajustar Confiança**

```python
# nlp_classifier.py
if confidence < 0.7:  # Ajustar threshold
    # Usar categoria padrão "Outros"
```

### **Customizar Respostas**

```python
# app.py - whatsapp_webhook()
msg = f"✅ Transação adicionada!\n\n"
msg += f"💰 Valor: R$ {result['amount']:.2f}\n"
# Adicionar mais informações aqui
msg += f"🎯 Sua mensagem customizada"
```

---

## 📊 Logs e Debug

### **Logs do WhatsApp**

```bash
# Ver logs em tempo real
tail -f logs/whatsapp.log
```

**Exemplo de log:**
```
2024-12-19 10:30:45 - whatsapp - INFO - 📨 Webhook recebido: text de +5511999999999
2024-12-19 10:30:45 - whatsapp - INFO - 💰 Transação detectada: Paguei R$ 50,00 no mercado
2024-12-19 10:30:45 - whatsapp - INFO - ✅ Transação inserida: ID abc123
```

### **Debug Mode**

Ativar prints detalhados:

```python
# app.py - whatsapp_webhook()
print(f"\n{'='*60}")
print(f"DEBUG: Webhook recebido!")
print(f"  Data completa: {data}")
print(f"  Type: {data.get('type')}")
print(f"  From: {data.get('from')}")
print(f"  Text: {data.get('text')}")
print(f"{'='*60}\n")
```

---

## ❓ Troubleshooting

### **Problema: Transação não é registrada**

**Solução:**
1. Verificar logs: `logs/whatsapp.log`
2. Confirmar que número está cadastrado:
   ```sql
   SELECT phone FROM users WHERE phone = '+5511999999999';
   ```
3. Testar manualmente:
   ```bash
   curl -X POST http://localhost:5000/api/whatsapp/webhook \
     -H "Authorization: Bearer seu_token" \
     -H "Content-Type: application/json" \
     -d '{"type":"text","from":"+5511999999999","text":"Paguei 50 reais"}'
   ```

### **Problema: OCR não funciona**

**Solução:**
```bash
# Testar Tesseract
tesseract --version

# Se não estiver instalado (Windows):
choco install tesseract

# Linux:
sudo apt-get install tesseract-ocr tesseract-ocr-por
```

### **Problema: Whisper não transcreve áudio**

**Solução:**
```bash
# Verificar FFmpeg
ffmpeg -version

# Instalar se necessário (Windows):
choco install ffmpeg

# Linux:
sudo apt-get install ffmpeg
```

---

## 🎯 Próximos Passos

✅ **Já Implementado:**
- ✅ Registro via texto
- ✅ Registro via áudio (Whisper)
- ✅ Registro via foto (OCR)
- ✅ Registro via PDF (extratos)
- ✅ Chat IA para perguntas
- ✅ Classificação automática de categorias
- ✅ Detecção de conta/cartão

🚧 **Melhorias Futuras:**
- [ ] Confirmação antes de registrar (botões)
- [ ] Editar transação via WhatsApp
- [ ] Deletar transação via WhatsApp
- [ ] Enviar resumo diário automático
- [ ] Alertas de gastos altos
- [ ] Notificações de vencimento de boletos
- [ ] Análise de gastos por categoria via gráfico
- [ ] Suporte a múltiplos idiomas

---

## 📚 Exemplos Completos

### **Exemplo 1: Compra no Mercado**

**Mensagem:**
```
Paguei 135 reais no supermercado Extra hoje de manhã
```

**Processamento:**
```json
{
  "amount": 135.0,
  "description": "supermercado Extra",
  "category": "Supermercado",
  "type": "Despesa",
  "date": "2024-12-19",
  "confidence": 0.95
}
```

**Resposta:**
```
✅ Transação adicionada!

💰 Valor: R$ 135,00
📅 Data: 19/12/2024
📂 Categoria: Supermercado
📝 Descrição: supermercado Extra
🏦 Conta: Conta Principal
```

---

### **Exemplo 2: Salário Recebido**

**Mensagem:**
```
Recebi 5000 de salário
```

**Processamento:**
```json
{
  "amount": 5000.0,
  "description": "salário",
  "category": "Salário",
  "type": "Receita",
  "date": "2024-12-19",
  "confidence": 0.98
}
```

**Resposta:**
```
✅ Transação adicionada!

💰 Valor: R$ 5.000,00
📅 Data: 19/12/2024
📂 Categoria: Salário
📝 Descrição: salário
🏦 Conta: Conta Principal
```

---

### **Exemplo 3: Pergunta sobre Gastos**

**Mensagem:**
```
Quanto gastei com alimentação esse mês?
```

**Resposta da IA:**
```
📊 Gastos com Alimentação - Dezembro 2024

🍽️ Total: R$ 1.245,00

📈 Detalhamento:
• Restaurantes: R$ 680,00 (54.6%)
• Supermercado: R$ 435,00 (34.9%)
• Delivery: R$ 130,00 (10.5%)

💡 Dica: Seus gastos com delivery aumentaram 35% vs. mês passado.
Considere cozinhar mais em casa para economizar!
```

---

## 📞 Suporte

- **Documentação Técnica**: `AI_SYSTEM_DOCUMENTATION.md`
- **Guia de IA**: `AI_QUICKSTART.md`
- **Logs**: `logs/whatsapp.log`
- **GitHub Issues**: Reportar bugs e sugestões

---

## 🏆 Créditos

**Desenvolvido por:** Brayan Barbosa  
**Tecnologias:** Python, Flask, Node.js, WPPConnect, Whisper, Tesseract, OpenAI  
**Licença:** Projeto Portfolio (Beta)  

---

**Última Atualização:** 19/12/2024 🚀
