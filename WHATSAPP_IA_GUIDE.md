# 🤖 Sistema de Notificações IA via WhatsApp - BWS Finance

## 📋 Visão Geral

Sistema completo que integra:
- **Notificações Inteligentes** → Detecta padrões financeiros
- **IA via WhatsApp** → Processa áudio, imagens, PDFs e texto
- **Análise em Tempo Real** → Insights automáticos sobre gastos

---

## 🏗️ Arquitetura

```
┌─────────────────┐
│   BWS Finance   │
│   (Flask App)   │
└────────┬────────┘
         │
         │ 1. Detecta evento (gasto alto, investimento)
         ↓
┌─────────────────────┐
│ Notification Center │ ← Sistema de notificações
│ + Notification AI   │
└────────┬────────────┘
         │
         │ 2. Envia notificação
         ↓
┌─────────────────────┐
│  WhatsApp Sender    │ ← services/whatsapp_sender.py
└────────┬────────────┘
         │
         │ 3. POST /send
         ↓
┌─────────────────────┐
│  Node.js Server     │ ← whatsapp_server/index.js
│   (WPPConnect)      │
└────────┬────────────┘
         │
         │ 4. Envia via WhatsApp Web
         ↓
    📱 WhatsApp
         │
         │ 5. Usuário responde (áudio/texto/foto)
         ↓
┌─────────────────────┐
│  Node.js Server     │
│  onMessage()        │
└────────┬────────────┘
         │
         │ 6. POST /api/whatsapp/webhook
         ↓
┌─────────────────────┐
│   Flask Webhook     │ ← app.py
│  + IA Processamento │
└────────┬────────────┘
         │
         │ 7. Salva transação
         ↓
    🗄️ Database
```

---

## 📦 Componentes Necessários

### 1️⃣ Servidor Node.js (WhatsApp)
**Localização:** `whatsapp_server/`

✅ **Já existe!** (`index.js`)

**Funções:**
- Conecta ao WhatsApp Web via QR Code
- Recebe mensagens (texto, áudio, imagem, PDF)
- Envia notificações via API `/send`
- Encaminha para Flask via webhook

### 2️⃣ Processadores de IA (Python)
**Localização:** `modules/`

Precisam ser criados:

#### a) **Audio Processor** - Transcreve áudio para texto
```python
# modules/audio_processor.py
# Usa Whisper ou Vosk para speech-to-text
```

#### b) **OCR Processor** - Extrai texto de imagens
```python
# modules/ocr_processor.py
# Usa Tesseract ou EasyOCR
```

#### c) **PDF Processor** - Extrai dados de extratos PDF
```python
# modules/pdf_processor.py
# Usa PyPDF2 + regex para identificar transações
```

#### d) **NLP Classifier** - Classifica texto em transações
```python
# modules/nlp_classifier.py
# Usa regex + padrões para extrair:
# - Valor (R$ 50,00)
# - Data (hoje, ontem, 15/11)
# - Categoria (mercado, restaurante)
# - Tipo (paguei = despesa, recebi = receita)
```

### 3️⃣ Sistema de Notificações
**Localização:** `services/`

✅ **Já existe!**
- `notification_center.py` - Gerencia notificações
- `notification_ai.py` - Análise de padrões
- `whatsapp_sender.py` - Envia via WhatsApp

### 4️⃣ Integração Flask
**Localização:** `app.py`

Adicionar rotas:
- `POST /api/whatsapp/webhook` - Recebe do Node.js
- `GET /api/whatsapp/health` - Status do sistema

---

## 🚀 Como Funcionar

### **Fluxo 1: Sistema → WhatsApp (Notificações)**

1. **Evento acontece** (ex: gasto acima de R$ 500)
2. **Notification AI** detecta e cria notificação
3. **Notification Center** verifica preferências do usuário
4. Se WhatsApp habilitado → chama `WhatsAppSender.send()`
5. **Node.js** recebe e envia pelo WhatsApp Web
6. Usuário recebe: *"💸 Alerta: Você gastou R$ 520,00 no Mercado hoje!"*

### **Fluxo 2: WhatsApp → Sistema (IA)**

1. Usuário envia: 🎤 **Áudio**: *"Paguei 50 reais no mercado hoje"*
2. **Node.js** recebe, salva áudio em `/temp`
3. Chama Flask: `POST /api/whatsapp/webhook` com payload
4. **AudioProcessor** transcreve: "paguei 50 reais no mercado hoje"
5. **NLPClassifier** extrai:
   ```json
   {
     "amount": 50.00,
     "type": "Despesa",
     "category": "Supermercado",
     "date": "2025-11-09",
     "description": "Mercado",
     "confidence": 0.85
   }
   ```
6. Flask salva no banco de dados
7. Responde ao Node.js com confirmação
8. Node.js envia ao usuário: *"✅ Transação adicionada! R$ 50,00 - Supermercado"*

---

## 🛠️ Instalação e Configuração

### **Passo 1: Instalar Node.js e Dependências**

```powershell
# Navegar para pasta do WhatsApp
cd whatsapp_server

# Instalar dependências
npm install

# Criar pasta temp
mkdir ../temp
```

### **Passo 2: Instalar Bibliotecas Python**

```powershell
# Voltar para raiz
cd ..

# Instalar dependências de IA
pip install openai-whisper  # Transcrição de áudio
pip install pytesseract     # OCR
pip install pillow          # Processamento de imagem
pip install PyPDF2          # Leitura de PDF
pip install python-dateutil # Parsing de datas
```

### **Passo 3: Configurar .env**

```env
# WhatsApp
WHATSAPP_SERVER_URL=http://localhost:3000
WHATSAPP_AUTH_TOKEN=seu_token_secreto_aqui
WHATSAPP_SERVER_PORT=3000
FLASK_URL=http://localhost:5000

# Opcional: Limitar remetentes
ALLOWED_SENDERS=5511999999999,5511888888888
```

### **Passo 4: Iniciar Servidores**

```powershell
# Terminal 1: Node.js WhatsApp Server
cd whatsapp_server
node index.js

# Escanear QR Code com WhatsApp

# Terminal 2: Flask Server
cd ..
python app.py
```

---

## 📱 Uso

### **Enviar via WhatsApp (IA):**

#### **Texto:**
```
"Paguei R$ 120,00 no posto de gasolina hoje"
"Recebi R$ 5000 de salário dia 5"
"Gastei 45 reais no almoço ontem"
```

#### **Áudio:** 🎤
*Grave áudio dizendo:* "Paguei cinquenta reais no Uber hoje"

#### **Foto de Nota Fiscal:** 📸
*Tire foto da nota → sistema extrai valor automaticamente*

#### **PDF de Extrato:** 📄
*Envie extrato do banco → sistema importa todas transações*

### **Receber Notificações:**

Sistema envia automaticamente:
- 💸 **Gasto alto:** "Você gastou R$ 520,00 no Mercado!"
- 📈 **Investimento:** "PETR4 subiu 3,5%! Lucro: R$ 120,00"
- 🔁 **Duplicata:** "Detectamos possível gasto duplicado"
- 📊 **Relatório:** "Seu resumo mensal: +15% de gastos"
- 💡 **Insights:** "Categoria 'Restaurante' cresceu 40%"

---

## 🧪 Testar Funcionalidades

### **1. Testar envio de notificação:**

```python
# No Python console
from services.whatsapp_sender import send_whatsapp_notification

send_whatsapp_notification(
    to_number="+5511999999999",
    message="🎉 Teste de notificação do BWS Finance!"
)
```

### **2. Testar webhook (simular WhatsApp):**

```powershell
# Enviar POST manualmente
curl -X POST http://localhost:5000/api/whatsapp/webhook `
  -H "Authorization: Bearer seu_token_secreto_aqui" `
  -H "Content-Type: application/json" `
  -d '{
    "from": "+5511999999999",
    "type": "text",
    "text": "Paguei R$ 50,00 no mercado hoje"
  }'
```

---

## ⚙️ Configurações de Notificações

Acesse: **http://localhost:5000/settings**

Na aba **🔔 Notificações**:
1. ✅ Habilitar **WhatsApp**
2. Adicionar número: `+55 11 99999-9999`
3. Configurar limites de alerta
4. Ativar **IA Insights**
5. Salvar

---

## 🎯 Próximos Passos

Agora vou criar os módulos de IA que faltam. Deseja que eu implemente:

1. **AudioProcessor** - Transcrição de áudio
2. **OCRProcessor** - Extração de texto de imagens
3. **PDFProcessor** - Leitura de extratos
4. **NLPClassifier** - Classificação inteligente

Ou prefere testar primeiro com o servidor Node.js?
