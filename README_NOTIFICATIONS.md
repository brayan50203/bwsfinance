# 📢 Sistema de Notificações Automáticas - BWS Finance

## 🎯 Visão Geral

Sistema completo de notificações automáticas para o BWS Finance, integrando:
- ⏰ **Scheduler** (APScheduler) para jobs recorrentes
- 📱 **WhatsApp** via WPPConnect/Baileys (local)
- 📧 **Email** via SMTP com templates HTML responsivos
- 🔔 **Dashboard** de notificações in-app
- ⚙️ **Preferências** por usuário (opt-in, horários DND, thresholds)

---

## 🚀 Instalação e Configuração

### 1. Instalar Dependências

```bash
pip install apscheduler requests jinja2 python-dotenv
```

### 2. Aplicar Migração do Banco

```bash
python scripts/migrate_notifications_columns.py
```

Isso criará:
- Tabela `notifications`
- Tabela `user_notifications_settings`
- Tabela `notification_logs`

### 3. Configurar Variáveis de Ambiente

Copie `.env.example` para `.env` e preencha:

```env
# Auto Notifications
AUTO_NOTIFICATIONS_ENABLED=true

# WhatsApp
WHATSAPP_ENABLED=true
WHATSAPP_SERVER_URL=http://localhost:3000
WHATSAPP_AUTH_TOKEN=sua_chave_secreta
WHATSAPP_SESSION_NAME=bws-finance

# SMTP Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=senha_de_app_do_gmail
SMTP_FROM=noreply@bwsfinance.com

# Defaults
NOTIFY_DEFAULT_LOW_BALANCE=100.00
NOTIFY_INVEST_PCT=3.0
```

**⚠️ Importante: Para Gmail, use Senha de App (não sua senha normal)**

Como gerar senha de app no Gmail:
1. Acesse: https://myaccount.google.com/apppasswords
2. Selecione "App: Mail" e "Device: Other"
3. Copie a senha gerada (16 caracteres)

### 4. Iniciar Servidor WhatsApp (Opcional)

Se quiser usar WhatsApp:

```bash
# Clone WPPConnect ou Baileys
git clone https://github.com/wppconnect-team/wppconnect-server.git
cd wppconnect-server
npm install
npm start
```

Acesse: http://localhost:3000 e escaneie QR code.

### 5. Iniciar Flask

```bash
python app.py
```

O scheduler iniciará automaticamente! ✅

---

## 📊 Arquitetura

### Estrutura de Arquivos

```
services/
├── auto_notifications.py       # Core do scheduler + jobs
├── whatsapp_sender.py           # Cliente WhatsApp
└── email_sender.py              # Cliente SMTP

routes/
└── notifications.py             # API REST

templates/
└── emails/
    ├── invoice_due.html         # Template fatura vencendo
    ├── monthly_summary.html     # Template resumo mensal
    └── low_balance.html         # Template saldo baixo

migrations/
├── create_notifications_tables.sql
└── scripts/migrate_notifications_columns.py
```

### Fluxo de Funcionamento

```
Scheduler (APScheduler)
   ↓
Jobs executam checks (faturas, saldos, etc)
   ↓
Criação de notificação no DB (status='pending')
   ↓
Envio via WhatsApp e/ou Email
   ↓
Atualização de status (sent/failed) + logs
```

---

## 🔔 Tipos de Notificações

### 1. **invoice_due_soon** - Fatura Vencendo

**Quando:** 3, 2, 1 e 0 dias antes do vencimento (configurável)

**Canais:** WhatsApp + Email

**Template WhatsApp:**
```
🚨 Olá João! Sua fatura do cartão *Nubank* vence em *3 dias* (R$ 1.240,50).

Deseja registrar o pagamento agora? Responda 'Sim' para marcar como pago.
```

**Como testar:**
```bash
curl -X POST http://localhost:5000/api/notifications/send \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "invoice_due_soon",
    "channel": "both",
    "params": {
      "card_name": "Nubank",
      "amount": "1240.50",
      "due_date": "2025-11-12",
      "days": 3
    }
  }'
```

---

### 2. **monthly_spending_summary** - Resumo Mensal

**Quando:** Semanalmente (segundas 08:00) ou mensalmente (dia 1)

**Canais:** Email (principal) + WhatsApp (resumo curto)

**Template WhatsApp:**
```
📊 *Resumo Mensal*

Você gastou *R$ 3.480,00* este mês.

🏆 Top 3 categorias:
- Supermercado R$ 1.240
- Transporte R$ 900
- Streaming R$ 150

📈 Variação vs mês anterior: +12.5%
```

**Como testar:**
```bash
curl -X POST http://localhost:5000/api/notifications/send \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "monthly_spending_summary",
    "channel": "email",
    "params": {
      "current_total": "3480.00",
      "top3": ["Supermercado R$ 1240", "Transporte R$ 900", "Streaming R$ 150"],
      "variation": 12.5
    }
  }'
```

---

### 3. **investment_alert** - Alerta de Investimento

**Quando:** Variação > threshold configurado (padrão: 3%)

**Canais:** WhatsApp + Email

**Template:**
```
📈 Seu ativo *PETR4* teve variação de *+5.23%* nas últimas 24h.
💰 Valor atual: R$ 38.450,00

Quer ver detalhes? Acesse o painel: http://localhost:5000/investments
```

**Como testar:**
```bash
curl -X POST http://localhost:5000/api/notifications/send \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "investment_alert",
    "channel": "whatsapp",
    "params": {
      "symbol": "PETR4",
      "percent": 5.23,
      "value": 38450.00
    }
  }'
```

---

### 4. **low_balance** - Saldo Baixo

**Quando:** Diariamente às 06:00 (se saldo < threshold)

**Canais:** WhatsApp + Email

**Template:**
```
⚠️ *Saldo Baixo*

Sua conta *Itaú Corrente* está com R$ 45,80 (abaixo do limite de R$ 100,00).

Deseja transferir fundos?
```

**Como testar:**
```bash
curl -X POST http://localhost:5000/api/notifications/send \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "low_balance",
    "channel": "both",
    "params": {
      "account_name": "Itaú Corrente",
      "balance": 45.80,
      "threshold": 100.00
    }
  }'
```

---

### 5. **import_confirmation** - Importação Concluída

**Quando:** Após importação automática de extrato

**Canais:** WhatsApp (notificação rápida)

**Template:**
```
✅ Importação concluída!

35 transações foram importadas automaticamente para sua conta *Nubank*.

Confira no painel: http://localhost:5000/dashboard
```

---

## ⚙️ API REST

### Base URL
```
http://localhost:5000/api/notifications
```

### Endpoints

#### 1. **GET /** - Listar Notificações

Lista notificações do usuário logado com paginação.

**Query Params:**
- `page`: Página (default: 1)
- `per_page`: Itens por página (default: 20)
- `status`: Filtrar por status (pending, sent, failed, read)
- `event_type`: Filtrar por tipo

**Exemplo:**
```bash
curl http://localhost:5000/api/notifications?page=1&per_page=10&status=sent
```

**Response:**
```json
{
  "notifications": [
    {
      "id": 123,
      "user_id": "uuid",
      "title": "Fatura Nubank vence em 3 dias",
      "message": "...",
      "event_type": "invoice_due_soon",
      "channel": "both",
      "priority": "medium",
      "status": "sent",
      "meta": {"card_name": "Nubank", "amount": 1240.50},
      "created_at": "2025-11-10 09:00:00",
      "sent_at": "2025-11-10 09:00:05",
      "read_at": null
    }
  ],
  "total": 50,
  "page": 1,
  "per_page": 10,
  "pages": 5
}
```

---

#### 2. **POST /send** - Forçar Envio

Envia notificação imediatamente (útil para testes).

**Body:**
```json
{
  "event_type": "invoice_due_soon",
  "channel": "both",
  "params": {
    "card_name": "Nubank",
    "amount": "1240.50",
    "due_date": "2025-11-12",
    "days": 3
  }
}
```

**Response:**
```json
{
  "success": true,
  "notification_id": 124,
  "message": "Notificação enviada"
}
```

---

#### 3. **PATCH /<id>/read** - Marcar como Lida

Marca notificação como lida.

**Exemplo:**
```bash
curl -X PATCH http://localhost:5000/api/notifications/123/read
```

**Response:**
```json
{
  "success": true,
  "message": "Notificação marcada como lida"
}
```

---

#### 4. **GET /health** - Health Check

Verifica status do serviço.

**Response:**
```json
{
  "status": "healthy",
  "scheduler_running": true,
  "jobs_count": 5,
  "jobs": [
    {"name": "Verificar faturas vencendo", "next_run": "2025-11-11 09:00:00"}
  ],
  "whatsapp_available": true,
  "email_available": true
}
```

---

#### 5. **GET /settings** - Preferências

Busca preferências do usuário.

**Response:**
```json
{
  "settings": {
    "notify_whatsapp": true,
    "notify_email": true,
    "threshold_low_balance": 100.00,
    "investment_alert_pct": 3.0,
    "do_not_disturb_start": "22:00",
    "do_not_disturb_end": "07:00",
    "invoice_alert_days": "3,1,0",
    "opt_in_whatsapp": true,
    "opt_in_email": true
  }
}
```

---

#### 6. **PUT /settings** - Atualizar Preferências

Atualiza preferências de notificação.

**Body:**
```json
{
  "notify_whatsapp": true,
  "notify_email": false,
  "threshold_low_balance": 200.00,
  "do_not_disturb_start": "23:00",
  "do_not_disturb_end": "08:00",
  "opt_in_whatsapp": true,
  "opt_in_email": false
}
```

---

#### 7. **POST /run-job/<job_name>** - Executar Job Manual

Executa job do scheduler manualmente (para testes).

**Jobs válidos:**
- `check_due_invoices`
- `check_monthly_spending`
- `check_investment_updates`
- `check_low_balance`
- `send_periodic_reports`

**Exemplo:**
```bash
curl -X POST http://localhost:5000/api/notifications/run-job/check_due_invoices
```

---

## 🕐 Schedule dos Jobs

| Job | Horário | Descrição |
|-----|---------|-----------|
| check_due_invoices | 09:00 diário | Verifica faturas vencendo em 3, 2, 1, 0 dias |
| check_monthly_spending | 07:00 diário | Calcula gastos do mês, envia resumo semanal |
| check_investment_updates | 08:05 diário | Verifica variação de investimentos > threshold |
| check_low_balance | 06:00 diário | Alerta contas com saldo < limite |
| send_periodic_reports | Dom 18:00 | Relatórios semanais/mensais |

**Próximas execuções:** Verifique em `/api/notifications/health`

---

## 🧪 Como Testar Localmente

### 1. Testar Notificação Individual

```bash
# Fatura vencendo
curl -X POST http://localhost:5000/api/notifications/send \
  -H "Content-Type: application/json" \
  -d '{"event_type": "invoice_due_soon", "channel": "whatsapp", "params": {"card_name": "Nubank", "amount": "1240.50", "days": 3}}'
```

### 2. Executar Job Manualmente

```bash
curl -X POST http://localhost:5000/api/notifications/run-job/check_due_invoices
```

### 3. Verificar Logs

```bash
tail -f logs/notifications.log
```

Você verá:
```
2025-11-10 09:00:00 - auto_notifications - INFO - 🔍 Checando faturas vencendo...
2025-11-10 09:00:01 - auto_notifications - INFO - 📝 Notificação criada: ID=124, tipo=invoice_due_soon
2025-11-10 09:00:02 - notifications.whatsapp - INFO - ✅ WhatsApp enviado: +5511999887766
2025-11-10 09:00:03 - auto_notifications - INFO - ✅ Check de faturas concluído
```

### 4. Verificar no Banco

```bash
python -c "import sqlite3; db = sqlite3.connect('bws_finance.db'); c = db.cursor(); c.execute('SELECT id, title, status, channel FROM notifications ORDER BY created_at DESC LIMIT 5'); print('\n'.join([str(r) for r in c.fetchall()]))"
```

---

## ⚠️ Troubleshooting

### WhatsApp não está enviando

**Verificar conexão:**
```bash
curl http://localhost:3000/api/status/bws-finance
```

Se desconectado:
1. Acesse http://localhost:3000
2. Reescaneie QR code
3. Teste envio novamente

**Mock mode (desenvolvimento):**
```env
WHATSAPP_ENABLED=false
```

Isso simulará envios (logs apenas).

---

### Email não está enviando

**Erros comuns:**
- Gmail bloqueando: Use senha de app (não senha normal)
- Firewall bloqueando porta 587
- SMTP_USER incorreto

**Testar SMTP manualmente:**
```python
import smtplib
from email.mime.text import MIMEText

msg = MIMEText("Test")
msg['Subject'] = 'Test'
msg['From'] = 'seu_email@gmail.com'
msg['To'] = 'destino@example.com'

with smtplib.SMTP('smtp.gmail.com', 587) as server:
    server.starttls()
    server.login('seu_email@gmail.com', 'sua_senha_de_app')
    server.send_message(msg)
    print("✅ Email enviado!")
```

---

### Jobs não estão rodando

**Verificar scheduler:**
```bash
curl http://localhost:5000/api/notifications/health
```

Se `scheduler_running: false`:
```env
AUTO_NOTIFICATIONS_ENABLED=true
```

Reinicie o Flask.

---

## 🔐 Segurança e Privacidade

### Opt-in Obrigatório

Para enviar WhatsApp, o usuário **deve** aceitar (LGPD compliance):

```sql
UPDATE user_notifications_settings
SET opt_in_whatsapp = 1
WHERE user_id = 'uuid-do-usuario';
```

### Do Not Disturb (DND)

Usuários podem configurar horário de silêncio:

```json
{
  "do_not_disturb_start": "22:00",
  "do_not_disturb_end": "07:00"
}
```

Notificações **não serão enviadas** neste período.

### Rate Limiting

Para evitar spam, considere limitar:
- Máximo 10 notificações/dia por usuário
- Máximo 1 notificação do mesmo tipo/dia

(Implementação futura)

---

## 📈 Métricas e Monitoramento

### Logs Estruturados

Formato:
```
TIMESTAMP - LOGGER - LEVEL - MESSAGE
```

**Locais:**
- `logs/notifications.log` (todas notificações)
- Console (durante desenvolvimento)

### Banco de Dados

Tabela `notification_logs`:
- Cada tentativa de envio registrada
- Status (success, failed, retry)
- Response data (JSON)
- Timestamps

**Consultar taxa de sucesso:**
```sql
SELECT 
  channel,
  status,
  COUNT(*) as total
FROM notification_logs
WHERE DATE(created_at) = DATE('now')
GROUP BY channel, status;
```

---

## 🚀 Próximos Passos (Roadmap)

### Fase 2: Machine Learning
- Aprender horários preferidos do usuário
- Sugerir categorias com base em histórico
- Predição de gastos futuros

### Fase 3: Canais Adicionais
- SMS (Twilio)
- Push Notifications (PWA)
- Telegram
- Discord

### Fase 4: Regras Customizadas
- Criar notificações personalizadas
- Triggers configuráveis (ex: "se gasto > R$ 500 em 'Lazer', avisar")

---

## 🤝 Contribuindo

Para adicionar novos tipos de notificação:

1. Adicionar template em `templates/emails/`
2. Criar job em `services/auto_notifications.py`
3. Adicionar template WhatsApp em `services/whatsapp_sender.py`
4. Documentar aqui no README

---

## 📝 Licença

MIT License - BWS Finance 2025

---

## 🆘 Suporte

- Issues: https://github.com/seu-repo/issues
- Docs: http://localhost:5000/docs/notifications (em breve)
- Email: suporte@bwsfinance.com

---

**Desenvolvido com ❤️ para o BWS Finance**
