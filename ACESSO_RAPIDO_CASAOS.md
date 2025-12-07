# 🚀 Acesso Rápido - BWS Finance no CasaOS

## 📍 IP do Servidor: `192.168.80.132`

---

## 🔗 Links Diretos

### 💼 Dashboard Principal
```
http://192.168.80.132:5000
```
**Login:** Crie sua conta no primeiro acesso

---

### 💬 WhatsApp - Conexão QR Code
```
http://192.168.80.132:3000
```
**Uso:** Escanear QR Code com WhatsApp do celular

---

### ⚕️ Health Check (API)
```
http://192.168.80.132:5000/api/notifications/health
```
**Retorna:** Status do sistema e scheduler

---

## 🧪 Testes Rápidos via Terminal

### ✅ Verificar se está rodando:
```bash
curl http://192.168.80.132:5000/api/notifications/health
```

### 📊 Ver jobs do scheduler:
```bash
curl http://192.168.80.132:5000/api/notifications/health | jq '.jobs'
```

### 📧 Testar notificação de saldo baixo:
```bash
curl -X POST http://192.168.80.132:5000/api/notifications/send \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "low_balance",
    "channel": "both",
    "params": {
      "account_name": "Nubank",
      "balance": 45.00,
      "threshold": 100.00
    }
  }'
```

### 💳 Testar notificação de fatura vencendo:
```bash
curl -X POST http://192.168.80.132:5000/api/notifications/send \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "invoice_due",
    "channel": "both",
    "params": {
      "card_name": "Visa Platinum",
      "amount": 1250.00,
      "due_date": "2024-11-15",
      "days_until_due": 3
    }
  }'
```

### 🔧 Executar job manualmente:
```bash
# Verificar saldo baixo
curl -X POST http://192.168.80.132:5000/api/notifications/run-job/check_low_balance

# Verificar faturas vencendo
curl -X POST http://192.168.80.132:5000/api/notifications/run-job/check_due_invoices

# Verificar investimentos
curl -X POST http://192.168.80.132:5000/api/notifications/run-job/check_investment_updates

# Verificar gastos mensais
curl -X POST http://192.168.80.132:5000/api/notifications/run-job/check_monthly_spending

# Enviar relatório periódico
curl -X POST http://192.168.80.132:5000/api/notifications/run-job/send_periodic_reports
```

---

## 📱 Acessar do Celular

### Android/iOS:
1. Conecte-se à mesma rede Wi-Fi
2. Abra o navegador
3. Digite: `http://192.168.80.132:5000`
4. Salve na tela inicial para app-like

### PWA (Progressive Web App):
1. Acesse pelo Chrome/Edge
2. Menu → "Instalar aplicativo"
3. Ícone será adicionado à tela inicial

---

## 🐳 Gerenciar Docker (via SSH)

### Ver status dos containers:
```bash
cd /DATA/AppData/bws-finance
docker compose ps
```

### Ver logs:
```bash
# Todos os serviços
docker compose logs -f

# Apenas backend
docker compose logs -f bws-backend

# Apenas WhatsApp
docker compose logs -f bws-whatsapp
```

### Reiniciar serviços:
```bash
docker compose restart
```

### Parar/Iniciar:
```bash
docker compose stop
docker compose start
```

### Atualizar código:
```bash
git pull
docker compose build
docker compose up -d
```

---

## ⚙️ Configurações Importantes

### 🔐 Variáveis de Ambiente
Editar: `/DATA/AppData/bws-finance/.env`

```bash
nano /DATA/AppData/bws-finance/.env
```

**Variáveis principais:**
- `SECRET_KEY` - Chave de segurança Flask
- `WHATSAPP_AUTH_TOKEN` - Token de autenticação WhatsApp
- `SMTP_*` - Configurações de email
- `NOTIFY_*` - Habilitadores de notificações

### 📝 Preferências de Notificação
Acesse: `http://192.168.80.132:5000/settings`

**Configure:**
- ✉️ Opt-in WhatsApp
- 📧 Opt-in Email
- 🔔 Limites de saldo baixo
- 💳 Dias de alerta de fatura
- ⏰ Horário "Não Perturbar"

---

## 📅 Scheduler - Horários Padrão

| Job | Horário | Descrição |
|-----|---------|-----------|
| `check_due_invoices` | **09:00** diário | Verifica faturas vencendo |
| `check_low_balance` | **06:00** diário | Verifica saldo baixo |
| `check_investment_updates` | **08:05** diário | Atualiza cotações de investimentos |
| `check_monthly_spending` | **07:00** diário | Analisa gastos mensais |
| `send_periodic_reports` | **Dom 18:00** | Relatório semanal |

---

## 🔍 Diagnóstico Rápido

### ❌ Se não carregar dashboard:
```bash
# Verificar containers
docker compose ps

# Ver logs de erro
docker compose logs --tail=50 bws-backend
```

### ❌ WhatsApp desconectado:
```bash
# Limpar sessão
rm -rf /DATA/AppData/bws-finance/tokens/*

# Reiniciar WhatsApp
docker compose restart bws-whatsapp

# Acessar e escanear novamente
# http://192.168.80.132:3000
```

### ❌ Email não envia:
```bash
# Testar SMTP
docker compose exec bws-backend python -c "
from services.email_sender import EmailSender
sender = EmailSender()
print(sender.test_connection())
"
```

### ❌ Banco de dados travado:
```bash
# Parar tudo
docker compose down

# Remover WAL
rm /DATA/AppData/bws-finance/bws_finance.db-wal

# Iniciar novamente
docker compose up -d
```

---

## 🆘 Suporte

### 📖 Documentação Completa:
- `DEPLOY_CASAOS.md` - Instalação completa
- `SETUP_GUIDE_CASAOS.md` - Configuração pós-instalação
- `TROUBLESHOOTING_CASAOS.md` - Resolução de problemas
- `DEPLOY_CHECKLIST.md` - Checklist de verificação

### 🐛 Problemas Comuns:
Consulte: `TROUBLESHOOTING_CASAOS.md`

### 💬 Ajuda:
- GitHub Issues: `https://github.com/seu-repo/bws-finance/issues`
- Email: `suporte@bws.com`

---

## 📊 Status do Sistema

### Última Atualização: 10/11/2025
### Versão: 2.0.0
### IP Servidor: `192.168.80.132`

**Sistema:**
- ✅ Backend rodando na porta 5000
- ✅ WhatsApp rodando na porta 3000
- ✅ Scheduler ativo com 5 jobs
- ✅ Notificações WhatsApp + Email habilitadas
- ✅ PWA instalável

---

**🎉 Tudo configurado e pronto para uso!**
