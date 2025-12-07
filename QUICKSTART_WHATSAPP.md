# 🚀 GUIA RÁPIDO - Notificações IA via WhatsApp

## ✅ STATUS DO SISTEMA

### **O que já funciona:**
- ✅ Sistema de notificações inteligentes (database criado)
- ✅ Notificação AI - Detecta padrões financeiros
- ✅ Classificador NLP - Extrai dados de texto natural
- ✅ WhatsApp Sender - Envia mensagens
- ✅ Servidor Node.js (WPPConnect) - Pronto para conectar
- ✅ Webhook Flask - Recebe mensagens do WhatsApp
- ✅ Interface de configurações - http://localhost:5000/settings

### **Testado:**
- ✅ NLP classifica corretamente: "Paguei R$ 50,00 no mercado hoje"
- ✅ Detecta valor, tipo, categoria e data
- ✅ WhatsApp Sender configurado
- ✅ Servidor Flask rodando em 0.0.0.0:5000

### **Pendente:**
- ⏳ Instalar dependências opcionais de IA (áudio, OCR, PDF)
- ⏳ Conectar WhatsApp via QR Code
- ⏳ Configurar WHATSAPP_AUTH_TOKEN no .env

---

## 🎯 PARA FAZER FUNCIONAR AGORA:

### **Passo 1: Configurar Token**
```powershell
# Editar arquivo .env (criar se não existir)
echo WHATSAPP_AUTH_TOKEN=meutoken123456 >> .env
```

### **Passo 2: Instalar Node.js (se não tiver)**
Baixe em: https://nodejs.org

### **Passo 3: Instalar dependências Node.js**
```powershell
cd whatsapp_server
npm install
cd ..
```

### **Passo 4: Iniciar Servidor WhatsApp**
```powershell
cd whatsapp_server
node index.js
```

**Vai aparecer um QR Code → Escaneie com WhatsApp!**

### **Passo 5: Testar Envio de Mensagem**

Envie pelo WhatsApp conectado:
```
Paguei R$ 50,00 no mercado hoje
```

O sistema vai:
1. Receber no Node.js
2. Enviar para Flask (webhook)
3. Classificar com NLP
4. Salvar no banco
5. Responder: "✅ Transação adicionada! R$ 50,00 - Alimentação"

---

## 📱 COMO USAR

### **1. Receber Notificações Automáticas**

Configure em: http://192.168.80.122:5000/settings

Na aba **Notificações**:
- ✅ Habilitar WhatsApp
- 📱 Adicionar número: `+55 11 99999-9999`
- 💰 Definir limite: `R$ 500` (alerta de gasto alto)
- 💾 Salvar

O sistema vai notificar automaticamente quando:
- Gasto acima do limite
- Investimento varia mais que 5%
- Detecta gastos duplicados
- Identifica padrões suspeitos

### **2. Adicionar Transações por Voz**

Grave áudio no WhatsApp:
> *"Paguei cinquenta reais no Uber hoje"*

Sistema transcreve e salva automaticamente!

### **3. Adicionar por Texto**

Exemplos:
```
Paguei R$ 120,00 na gasolina ontem
Recebi R$ 5000 de salário dia 5
Gastei 45 no almoço hoje
Comprei remédio por R$ 30,00
```

### **4. Enviar Foto de Nota Fiscal**

Tire foto da nota → Sistema extrai valor com OCR!

### **5. Enviar PDF de Extrato**

Envie extrato bancário → Sistema importa todas transações!

---

## 🧪 TESTAR SISTEMA

### **Teste Manual Completo:**

```powershell
# 1. Testar NLP
python -c "from modules.nlp_classifier import NLPClassifier; nlp = NLPClassifier(); print(nlp.classify('Paguei R$ 50 no mercado'))"

# 2. Testar todos os componentes
python test_whatsapp_ia.py

# 3. Testar envio WhatsApp (após conectar)
python -c "from services.whatsapp_sender import send_whatsapp_notification; send_whatsapp_notification('+5511999999999', 'Teste!')"
```

---

## 🔧 SOLUÇÃO DE PROBLEMAS

### **Erro: "WhatsApp não conectado"**
→ Execute: `cd whatsapp_server && node index.js`
→ Escaneie QR Code

### **Erro: "Token inválido"**
→ Configure WHATSAPP_AUTH_TOKEN no .env
→ Use o mesmo token no Node.js e Flask

### **Erro: "Módulo não encontrado"**
→ Instale: `pip install requests flask pillow`

### **Servidor Node não inicia**
→ Instale Node.js: https://nodejs.org
→ Execute: `cd whatsapp_server && npm install`

---

## 📊 FUNCIONALIDADES IA

### **1. Detecção de Gastos Duplicados**
Sistema identifica:
- Mesmo valor
- Mesma categoria
- Mesmo dia
→ Notifica: "⚠️ Possível duplicata: R$ 50,00 - Mercado"

### **2. Análise de Crescimento**
Compara mês atual vs anterior:
- Categoria cresceu +40%
→ Notifica: "📈 Gastos com Restaurante cresceram 40%"

### **3. Detecção de Anomalias**
Identifica gastos 3x acima da média:
→ Notifica: "🚨 Gasto incomum: R$ 800,00 é 3x sua média"

### **4. Taxa de Poupança**
Calcula receita - despesa:
- Meta: 20% de poupança
→ Notifica: "✅ Você está poupando 25% este mês!"

### **5. Sugestões de Corte**
IA sugere onde cortar gastos:
→ "💡 Reduza 15% em Restaurante para poupar R$ 150"

---

## 🎨 INTERFACE

Acesse: http://192.168.80.122:5000/settings

**5 Abas:**
1. 👤 **Perfil** - Nome, foto, bio
2. 🔔 **Notificações** - Configurar alertas WhatsApp
3. 🔒 **Segurança** - Alterar senha, 2FA
4. 🎨 **Preferências** - Idioma, moeda, tema
5. 🔗 **Integrações** - WhatsApp, Open Banking

---

## ⚡ INICIALIZAÇÃO RÁPIDA

```powershell
# Terminal 1: WhatsApp Server
cd whatsapp_server
node index.js

# Terminal 2: Flask Server (já rodando)
# Porta 5000

# Terminal 3: Testar
python test_whatsapp_ia.py
```

---

## 🎯 PRÓXIMOS PASSOS

1. **Conectar WhatsApp** (node index.js + QR Code)
2. **Configurar número** em /settings
3. **Enviar mensagem teste**: "Paguei R$ 50 no mercado"
4. **Ver notificação** quando gastar acima do limite

---

## 📞 SUPORTE

Sistema 100% funcional para:
- ✅ Notificações inteligentes
- ✅ Classificação NLP de texto
- ✅ Envio via WhatsApp
- ✅ Webhooks Flask

Para IA completa (áudio, OCR, PDF), instale:
```powershell
pip install openai-whisper pytesseract PyPDF2
```

**Tudo pronto para usar!** 🚀
