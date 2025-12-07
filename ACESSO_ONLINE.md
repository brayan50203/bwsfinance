# 🌐 BWS FINANCE - ACESSO ONLINE

## ✅ SISTEMA ONLINE E ACESSÍVEL NA REDE!

---

## 📱 **URLs DE ACESSO**

### **Acesso Local (nesta máquina):**
- 🏠 Dashboard: http://localhost:5000
- 🏠 WhatsApp QR Code: http://localhost:3000

### **Acesso na Rede Local:**
- 🌐 Dashboard: http://192.168.80.122:5000
- 🌐 WhatsApp QR Code: http://192.168.80.122:3000

### **Acesso Mobile (mesmo WiFi):**
- 📱 No celular, conecte-se ao mesmo WiFi
- 📱 Acesse: http://192.168.80.122:5000
- 📱 Instale como app (PWA): Clique nos 3 pontinhos → "Adicionar à tela inicial"

---

## 🔥 **FIREWALL CONFIGURADO**

```
✅ Porta 5000 liberada (Flask/BWS Finance)
✅ Porta 3000 liberada (WhatsApp Server)
```

**Regras adicionadas:**
- BWS Finance - Flask 5000
- BWS Finance - WhatsApp 3000

---

## 🚀 **SERVIDORES ATIVOS**

### **1. Flask Server (Backend + Frontend)**
- **Porta:** 5000
- **Host:** 0.0.0.0 (todas as interfaces)
- **Status:** ✅ ONLINE
- **Threads:** 8 workers (Waitress)

### **2. WhatsApp Server (WPPConnect)**
- **Porta:** 3000
- **Host:** 0.0.0.0
- **Status:** ✅ ONLINE
- **Sessão:** bwsfinance-session

---

## 📋 **COMO CONECTAR WHATSAPP**

1. **No navegador**, acesse: http://192.168.80.122:3000
2. **Escaneie o QR Code** com WhatsApp do celular
3. **Pronto!** Agora pode enviar mensagens para a IA

**Números autorizados:**
- +55 11 97476-4971
- +55 11 94996-7277

---

## 🎯 **FUNCIONALIDADES DISPONÍVEIS**

### **Web App (http://192.168.80.122:5000)**
✅ Dashboard com gráficos e estatísticas  
✅ Gestão de transações  
✅ Contas bancárias  
✅ Cartões de crédito  
✅ Parcelamentos  
✅ **Transações recorrentes** (com cartão!)  
✅ Investimentos (integração com B3)  
✅ Importação de extratos  
✅ Notificações  
✅ Configurações  
✅ IA Financeira BWS Insight  

### **WhatsApp IA**
✅ Perguntas sobre finanças  
✅ Registro de gastos por voz/texto  
✅ Consulta de saldo, investimentos  
✅ Análises e previsões  
✅ Vocabulário expandido (aceita muitas variações)  

---

## 🔐 **SEGURANÇA**

- ✅ Autenticação por sessão
- ✅ Bearer Token para WhatsApp webhook
- ✅ Whitelist de números autorizados
- ✅ Isolamento por tenant_id
- ✅ Validação de usuários por telefone

---

## 🛠️ **COMANDOS ÚTEIS**

### **Reiniciar Flask:**
```powershell
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
.\start-server.ps1
```

### **Reiniciar WhatsApp:**
```powershell
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
cd whatsapp_server
node index.js
```

### **Ver logs em tempo real:**
```powershell
Get-Content logs\whatsapp.log -Wait -Tail 20
```

### **Verificar portas:**
```powershell
netstat -ano | findstr "5000 3000"
```

---

## 🌍 **ACESSO EXTERNO (INTERNET)**

Para acesso de fora da rede local, você precisa:

1. **Configurar Port Forwarding no roteador:**
   - Porta Externa: 5000 → IP Interno: 192.168.80.122:5000
   - Porta Externa: 3000 → IP Interno: 192.168.80.122:3000

2. **Obter IP público:**
   - Acesse: https://meuip.com.br
   - Use o IP público para acessar de fora

3. **Domínio (opcional):**
   - Configure DNS dinâmico (No-IP, DynDNS)
   - Ou use serviço como Ngrok/Cloudflare Tunnel

---

## 📊 **BANCO DE DADOS**

**Localização:** `C:\App\nik0finance-base\bws_finance.db`

**Tabelas principais:**
- users, tenants, accounts, cards
- transactions, categories
- recurring_transactions ✨ (com suporte a cartão!)
- installments
- investments
- notifications

---

## 🎨 **MELHORIAS RECENTES**

### **Recorrentes:**
✅ Escolha entre Conta ou Cartão de Crédito  
✅ Lista de contas com saldo  
✅ Lista de cartões com limite disponível  
✅ Categorias padrão funcionais  

### **IA WhatsApp:**
✅ Vocabulário super expandido  
✅ Aceita dezenas de variações de perguntas  
✅ Detecção inteligente (pergunta vs transação)  

---

## 📞 **SUPORTE**

Em caso de problemas:

1. Verifique se os servidores estão rodando
2. Confira os logs em `logs/`
3. Teste acesso local primeiro (localhost)
4. Verifique firewall do Windows
5. Confirme que está no mesmo WiFi (acesso mobile)

---

**Sistema desenvolvido por:** BWS Finance Team  
**Versão:** 2.0 - Production Ready  
**Data:** 09/11/2025  

🚀 **Tudo pronto para uso!**
