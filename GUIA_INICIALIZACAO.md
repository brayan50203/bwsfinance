# 🚀 BWS Finance - Guia Completo de Inicialização

## ✅ **SISTEMA IMPLEMENTADO**

### 1. **Flask (Backend + API + IA)**
- ✅ Rota de cadastro: `/register-whatsapp`
- ✅ API de registro: `/api/register` (POST)
- ✅ Webhook WhatsApp: `/api/whatsapp/webhook`
- ✅ Auto-registro de números com instrução de cadastro

### 2. **Bot WhatsApp v3.0**
- ✅ WPPConnect configurado
- ✅ Logs detalhados
- ✅ Filtros (grupos, mensagens próprias)
- ✅ Integração com Flask

### 3. **Página de Cadastro**
- ✅ Interface moderna: `templates/register_whatsapp.html`
- ✅ Validação em tempo real
- ✅ Formatação automática de WhatsApp

---

## 🔧 **COMO INICIAR TUDO**

### **OPÇÃO 1: Inicialização Manual (Recomendado)**

#### **Passo 1: Flask**
```powershell
cd C:\App\nik0finance-base
python app.py
```
✅ Deve exibir: `[FLASK] Acessível em: http://0.0.0.0:5000`

#### **Passo 2: Bot WhatsApp** (em OUTRA janela PowerShell)
```powershell
cd C:\App\nik0finance-base\whatsapp_server
node index_v3.js
```
✅ Deve exibir QR code
✅ Escaneie com WhatsApp
✅ Aguarde "WhatsApp CONECTADO!"

---

### **OPÇÃO 2: Usar Scripts .bat**

1. **START_IMPROVED.bat** - Bot melhorado (precisa reinstalar WPPConnect)
2. **START_BOT_MANUAL.bat** - Bot v3 simples

**Execute um dos .bat** clicando duas vezes.

---

## 📱 **COMO USAR**

### **Para CADASTRAR novo usuário:**

1. Acesse: http://192.168.80.122:5000/register-whatsapp
2. Preencha:
   - Nome completo
   - Email
   - WhatsApp (com +55)
   - Senha (mín. 6 caracteres)
3. Clique em "Cadastrar e Ativar WhatsApp"
4. Pronto! Agora pode usar o WhatsApp

### **Para TESTAR o bot:**

1. Certifique-se que está cadastrado
2. Envie mensagem para: **+5511947626417**
3. Exemplos:
   - "Quanto gastei este mês?"
   - "Gastei 50 reais no mercado"
   - "Quanto tenho nas contas?"

---

## ⚠️ **PROBLEMAS CONHECIDOS**

### **1. Bot não recebe mensagens**
**Causa**: WPPConnect/Venom têm problemas com WhatsApp Web atual

**Solução temporária**: Use a interface web
- Acesse: http://192.168.80.122:5000/whatsapp-chat
- Funciona igual ao WhatsApp mas pelo navegador

### **2. Flask encerra sozinho**
**Causa**: Erro no Python ou porta já em uso

**Solução**:
```powershell
# Matar processos Python
Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force

# Reiniciar Flask
cd C:\App\nik0finance-base
python app.py
```

### **3. Bot não conecta (QR não aparece)**
**Causa**: Sessão antiga travada

**Solução**:
```powershell
# Limpar sessão
Remove-Item C:\App\nik0finance-base\whatsapp_server\tokens\bwsfinance-v3 -Recurse -Force

# Reiniciar bot
cd C:\App\nik0finance-base\whatsapp_server
node index_v3.js
```

---

## 🔗 **URLs IMPORTANTES**

- 🏠 **Site Principal**: http://192.168.80.122:5000
- 📝 **Cadastro WhatsApp**: http://192.168.80.122:5000/register-whatsapp
- 💬 **Chat Web**: http://192.168.80.122:5000/whatsapp-chat
- 📊 **Dashboard**: http://192.168.80.122:5000/dashboard

---

## 📞 **CONTATOS**

- **Bot WhatsApp**: +5511947626417
- **Seu WhatsApp**: +5511974764971 (Brayan)
- **Email**: brayan@bws.com
- **Senha**: 123456

---

## 🆘 **EM CASO DE ERRO**

### **Erro: "número não cadastrado"**
→ Acesse `/register-whatsapp` e cadastre

### **Erro: "Cannot find module '@wppconnect-team/wppconnect'"**
→ Execute:
```powershell
cd C:\App\nik0finance-base\whatsapp_server
npm install @wppconnect-team/wppconnect --save
```

### **Erro: "Port 5000 already in use"**
→ Mate processos:
```powershell
Get-Process -Name python | Stop-Process -Force
```

### **Bot conecta mas não responde mensagens**
→ Use: http://192.168.80.122:5000/whatsapp-chat

---

## ✨ **FEATURES IMPLEMENTADAS**

### **Sistema de Cadastro:**
- ✅ Validação de campos
- ✅ Formatação automática de telefone
- ✅ Verificação de duplicidade
- ✅ Criação automática de conta padrão
- ✅ Hash de senha seguro

### **Bot WhatsApp:**
- ✅ Detecção automática de número não cadastrado
- ✅ Mensagem com instruções de cadastro
- ✅ Filtro de grupos e mensagens próprias
- ✅ Logs detalhados para debug
- ✅ Heartbeat de conexão

### **Integração Flask:**
- ✅ Webhook seguro (Bearer token)
- ✅ Busca de usuário por WhatsApp
- ✅ Processamento por IA
- ✅ Suporte a texto, áudio, imagem, PDF

---

## 🎯 **PRÓXIMOS PASSOS**

1. ✅ Cadastrar seu número (se ainda não fez)
2. ✅ Testar envio de mensagem
3. ⏳ Aguardar correção do WPPConnect para recepção automática
4. 💡 Usar interface web como alternativa

---

**Criado em**: 30/11/2025  
**Versão**: 4.0 - Improved  
**Status**: ✅ Funcionando (com workaround para recepção)
