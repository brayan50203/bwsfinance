# 🧪 Guia Rápido de Testes - Sistema de Notificações

## ⚡ Quick Start (3 minutos)

### 1. Configurar ambiente

```powershell
# Copiar .env
copy .env.example .env

# Editar .env e configurar:
# - SMTP_USER=seu_email@gmail.com
# - SMTP_PASSWORD=sua_senha_de_app
# - WHATSAPP_ENABLED=false (se não tiver servidor WhatsApp)
```

### 2. Aplicar migração

```powershell
python scripts/migrate_notifications_columns.py
```

### 3. Iniciar servidor

```powershell
python app.py
```

Você verá:
```
✅ Notifications routes loaded
✅ Auto Notifications Scheduler started
🚀 Iniciando Auto Notification Service...
✅ Scheduler ativo com 5 jobs:
  - Verificar faturas vencendo (próxima execução: 2025-11-11 09:00:00)
  ...
```

---

## 📋 Testes Rápidos (copiar e colar)

### Health Check

```powershell
curl http://localhost:5000/api/notifications/health
```

**Esperado:**
```json
{
  "status": "healthy",
  "scheduler_running": true,
  "jobs_count": 5,
  "whatsapp_available": true,
  "email_available": true
}
```

---

### Testar Notificação de Fatura

```powershell
curl -X POST http://localhost:5000/api/notifications/send `
  -H "Content-Type: application/json" `
  -d '{
    "event_type": "invoice_due_soon",
    "channel": "email",
    "params": {
      "card_name": "Nubank",
      "amount": "1240.50",
      "due_date": "2025-11-15",
      "days": 3
    }
  }'
```

**Esperado:**
```json
{
  "success": true,
  "notification_id": 1,
  "message": "Notificação enviada"
}
```

**Verificar email:** Você deve receber um email no endereço configurado em SMTP_USER!

---

### Testar Notificação de Saldo Baixo

```powershell
curl -X POST http://localhost:5000/api/notifications/send `
  -H "Content-Type: application/json" `
  -d '{
    "event_type": "low_balance",
    "channel": "email",
    "params": {
      "account_name": "Itaú Corrente",
      "balance": 45.80,
      "threshold": 100.00
    }
  }'
```

---

### Testar Resumo Mensal

```powershell
curl -X POST http://localhost:5000/api/notifications/send `
  -H "Content-Type: application/json" `
  -d '{
    "event_type": "monthly_spending_summary",
    "channel": "email",
    "params": {
      "current_total": "3480.00",
      "top3": [
        {"name": "Supermercado", "amount": "1240.00"},
        {"name": "Transporte", "amount": "900.00"},
        {"name": "Streaming", "amount": "150.00"}
      ],
      "variation": 12.5
    }
  }'
```

---

### Listar Notificações Enviadas

```powershell
curl http://localhost:5000/api/notifications?page=1&per_page=5&status=sent
```

**Esperado:**
```json
{
  "notifications": [
    {
      "id": 1,
      "title": "Fatura Nubank vence em 3 dias",
      "message": "...",
      "event_type": "invoice_due_soon",
      "status": "sent",
      "created_at": "2025-11-10 10:30:00",
      "sent_at": "2025-11-10 10:30:02"
    }
  ],
  "total": 1,
  "page": 1,
  "pages": 1
}
```

---

### Executar Job Manualmente

```powershell
# Verificar faturas vencendo
curl -X POST http://localhost:5000/api/notifications/run-job/check_due_invoices

# Verificar saldos baixos
curl -X POST http://localhost:5000/api/notifications/run-job/check_low_balance
```

---

### Verificar Preferências do Usuário

```powershell
curl http://localhost:5000/api/notifications/settings
```

**Esperado:**
```json
{
  "settings": {
    "notify_whatsapp": true,
    "notify_email": true,
    "threshold_low_balance": 100.00,
    "investment_alert_pct": 3.0,
    "opt_in_whatsapp": false,
    "opt_in_email": false
  }
}
```

---

### Atualizar Preferências

```powershell
curl -X PUT http://localhost:5000/api/notifications/settings `
  -H "Content-Type: application/json" `
  -d '{
    "notify_email": true,
    "threshold_low_balance": 200.00,
    "opt_in_email": true
  }'
```

---

## 🔍 Verificar Logs

### Logs de Notificações

```powershell
# Ver últimas 20 linhas
Get-Content -Tail 20 logs/notifications.log

# Acompanhar em tempo real
Get-Content -Wait logs/notifications.log
```

**O que procurar:**
- ✅ = Sucesso
- ❌ = Erro
- 📝 = Notificação criada
- 🔍 = Job iniciado

---

### Verificar no Banco de Dados

```powershell
python -c "import sqlite3; db = sqlite3.connect('bws_finance.db'); c = db.cursor(); c.execute('SELECT id, title, status, channel, sent_at FROM notifications ORDER BY created_at DESC LIMIT 5'); [print(f\"ID: {r[0]} | {r[1][:30]}... | Status: {r[2]} | Canal: {r[3]} | Enviado: {r[4]}\") for r in c.fetchall()]"
```

---

## 🧪 Testes Unitários (pytest)

### Instalar pytest

```powershell
pip install pytest pytest-mock
```

### Executar testes

```powershell
pytest tests/test_notifications.py -v
```

**Esperado:**
```
tests/test_notifications.py::test_create_notification PASSED
tests/test_notifications.py::test_get_user_settings PASSED
tests/test_notifications.py::test_send_notification_whatsapp PASSED
tests/test_notifications.py::test_full_notification_flow PASSED
...

========== 15 passed in 2.34s ==========
```

---

## 📱 Testar WhatsApp (se configurado)

### 1. Verificar servidor WhatsApp

```powershell
curl http://localhost:3000/api/status/bws-finance
```

Se desconectado:
- Acesse http://localhost:3000
- Reescaneie QR code

### 2. Enviar teste via WhatsApp

```powershell
curl -X POST http://localhost:5000/api/notifications/send `
  -H "Content-Type: application/json" `
  -d '{
    "event_type": "low_balance",
    "channel": "whatsapp",
    "params": {
      "account_name": "Nubank",
      "balance": 25.50,
      "threshold": 100.00
    }
  }'
```

Você deve receber a mensagem no WhatsApp! 📱

---

## 🐛 Troubleshooting Comum

### Email não está enviando

**Verificar:**
```powershell
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('SMTP_USER:', os.getenv('SMTP_USER')); print('SMTP_HOST:', os.getenv('SMTP_HOST'))"
```

**Se Gmail:**
- Use senha de app (não senha normal)
- Gere em: https://myaccount.google.com/apppasswords

---

### Scheduler não está rodando

**Verificar:**
```powershell
curl http://localhost:5000/api/notifications/health
```

Se `scheduler_running: false`:
- Verifique `.env`: `AUTO_NOTIFICATIONS_ENABLED=true`
- Reinicie o servidor

---

### Jobs não executam no horário

Jobs rodam no timezone do servidor. Para forçar execução:

```powershell
curl -X POST http://localhost:5000/api/notifications/run-job/check_due_invoices
```

---

## 📊 Métricas de Sucesso

### Taxa de Entrega

```sql
SELECT 
  channel,
  status,
  COUNT(*) as total,
  ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM notifications), 2) as percentage
FROM notifications
WHERE DATE(created_at) = DATE('now')
GROUP BY channel, status
ORDER BY total DESC;
```

### Notificações por Tipo

```sql
SELECT 
  event_type,
  COUNT(*) as total,
  AVG(CASE WHEN status = 'sent' THEN 1 ELSE 0 END) as success_rate
FROM notifications
GROUP BY event_type
ORDER BY total DESC;
```

---

## ✅ Checklist de Validação

Antes de considerar o módulo pronto:

- [ ] Health check retorna `healthy`
- [ ] Email de teste recebido com template correto
- [ ] Notificação aparece em `/api/notifications`
- [ ] Logs em `logs/notifications.log` estão funcionando
- [ ] Scheduler mostra 5 jobs ativos
- [ ] Preferências podem ser atualizadas via API
- [ ] WhatsApp envia (se configurado)
- [ ] Jobs manuais executam com sucesso
- [ ] Testes unitários passam (pytest)

---

## 🎓 Próximos Passos

Após validar tudo:

1. **Configurar cartões de teste** com vencimento próximo
2. **Aguardar execução automática** (às 09:00 para faturas)
3. **Testar do-not-disturb** (configurar DND e verificar)
4. **Integrar com frontend** (criar página de notificações)
5. **Adicionar novos tipos** de notificações customizadas

---

## 📚 Referências

- Documentação completa: `README_NOTIFICATIONS.md`
- Templates de email: `templates/emails/`
- Código fonte: `services/auto_notifications.py`
- API: `routes/notifications.py`

---

**💡 Dica:** Use Postman ou Insomnia para salvar essas requisições e testar mais facilmente!
