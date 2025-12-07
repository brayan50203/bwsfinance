# ⚙️ Guia de Configuração Pós-Instalação - BWS Finance (CasaOS)

## 🎯 Visão Geral

Este guia cobre todas as configurações necessárias após instalar o BWS Finance no CasaOS.

---

## 1️⃣ Primeiro Acesso

### 1.1 Criar conta de administrador

1. Acesse: `http://ip-do-casaos:5000`
2. Clique em **"Criar Conta"**
3. Preencha:
   - Nome completo
   - Email
   - Telefone (com código do país: +5511999999999)
   - Senha (mínimo 8 caracteres)
4. Clique em **"Cadastrar"**

### 1.2 Login inicial

1. Faça login com email e senha
2. Você será redirecionado para o Dashboard

---

## 2️⃣ Configurar WhatsApp

### 2.1 Conectar dispositivo

1. Acesse: `http://ip-do-casaos:3000`
2. Clique em **"Start Session"** ou acesse:
   ```
   http://ip-do-casaos:3000/api/bws-finance/start-session
   ```
3. Um QR Code será exibido
4. No seu celular:
   - Abra WhatsApp
   - Vá em **Menu (⋮)** → **Aparelhos conectados**
   - Clique em **"Conectar um aparelho"**
   - Escaneie o QR Code

### 2.2 Verificar conexão

```bash
curl http://localhost:3000/api/bws-finance/status
```

Resposta esperada:
```json
{
  "state": "CONNECTED",
  "session": "bws-finance",
  "phone": "+5511999999999"
}
```

### 2.3 Testar envio

```bash
curl -X POST http://localhost:3000/api/sendText \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -d '{
    "session": "bws-finance",
    "phone": "5511999999999",
    "message": "Teste do BWS Finance! 🚀"
  }'
```

---

## 3️⃣ Configurar Preferências de Notificações

### 3.1 Via Interface Web

1. Acesse: `http://ip-do-casaos:5000/settings`
2. Vá para aba **"Notificações"**
3. Configure:
   - ✅ **Notificar via WhatsApp**
   - ✅ **Notificar via Email**
   - ✅ **Notificar no Dashboard**
   - **Saldo baixo (alerta):** R$ 100,00
   - **Variação investimentos (alerta):** 3%
   - **Não perturbar:** 22:00 - 07:00
   - **Dias de alerta de fatura:** 3, 1, 0 (dias antes)

4. **⚠️ IMPORTANTE:** Marque os opt-ins:
   - ✅ **Aceito receber notificações via WhatsApp**
   - ✅ **Aceito receber notificações via Email**

5. Clique em **"Salvar Preferências"**

### 3.2 Via API

```bash
curl -X PUT http://localhost:5000/api/notifications/settings \
  -H "Content-Type: application/json" \
  -H "Cookie: session=SEU_SESSION_ID" \
  -d '{
    "notify_whatsapp": true,
    "notify_email": true,
    "notify_dashboard": true,
    "threshold_low_balance": 100.00,
    "investment_alert_pct": 3.0,
    "do_not_disturb_start": "22:00",
    "do_not_disturb_end": "07:00",
    "invoice_alert_days": "3,1,0",
    "opt_in_whatsapp": true,
    "opt_in_email": true
  }'
```

---

## 4️⃣ Cadastrar Contas e Cartões

### 4.1 Adicionar conta bancária

1. Vá em **"Contas"** → **"Nova Conta"**
2. Preencha:
   - Nome: Nubank
   - Tipo: Conta Corrente
   - Saldo inicial: R$ 1.500,00
   - Banco: 260 - Nu Pagamentos S.A.
3. Clique em **"Salvar"**

### 4.2 Adicionar cartão de crédito

1. Vá em **"Cartões"** → **"Novo Cartão"**
2. Preencha:
   - Nome: Nubank Mastercard
   - Limite: R$ 5.000,00
   - Dia de fechamento: 10
   - Dia de vencimento: 17
   - Bandeira: Mastercard
3. Clique em **"Salvar"**

### 4.3 Configurar day_of_month nas contas

**⚠️ IMPORTANTE:** Para notificações de faturas funcionarem, configure o `due_day`:

```sql
-- Via SQLite (se necessário)
UPDATE cards SET due_day = 17 WHERE name = 'Nubank Mastercard';
```

Ou via interface:
1. Edite o cartão
2. Campo **"Dia de vencimento"**: 17
3. Salvar

---

## 5️⃣ Testar Notificações

### 5.1 Testar alerta de saldo baixo

```bash
curl -X POST http://localhost:5000/api/notifications/send \
  -H "Content-Type: application/json" \
  -H "Cookie: session=SEU_SESSION_ID" \
  -d '{
    "event_type": "low_balance",
    "channel": "both",
    "params": {
      "account_name": "Nubank",
      "balance": 50.00,
      "threshold": 100.00
    }
  }'
```

**Você deve receber:**
- WhatsApp: "⚠️ Saldo Baixo..."
- Email: Template HTML com detalhes

### 5.2 Testar alerta de fatura

```bash
curl -X POST http://localhost:5000/api/notifications/send \
  -H "Content-Type: application/json" \
  -H "Cookie: session=SEU_SESSION_ID" \
  -d '{
    "event_type": "invoice_due_soon",
    "channel": "both",
    "params": {
      "card_name": "Nubank Mastercard",
      "amount": "1240.50",
      "due_date": "2025-11-17",
      "days": 3
    }
  }'
```

### 5.3 Forçar execução de job do scheduler

```bash
# Executar check de saldos baixos
curl -X POST http://localhost:5000/api/notifications/run-job/check_low_balance \
  -H "Cookie: session=SEU_SESSION_ID"

# Executar check de faturas vencendo
curl -X POST http://localhost:5000/api/notifications/run-job/check_due_invoices \
  -H "Cookie: session=SEU_SESSION_ID"
```

---

## 6️⃣ Configurar Scheduler (Horários)

### 6.1 Verificar jobs ativos

```bash
curl http://localhost:5000/api/notifications/health | jq '.jobs'
```

Resposta esperada:
```json
{
  "jobs": [
    {
      "name": "Verificar faturas vencendo",
      "next_run": "2025-11-11 09:00:00"
    },
    {
      "name": "Verificar saldos baixos",
      "next_run": "2025-11-11 06:00:00"
    },
    {
      "name": "Verificar atualizações de investimentos",
      "next_run": "2025-11-11 08:05:00"
    },
    {
      "name": "Verificar gastos mensais",
      "next_run": "2025-11-11 07:00:00"
    },
    {
      "name": "Enviar relatórios periódicos",
      "next_run": "2025-11-17 18:00:00"
    }
  ]
}
```

### 6.2 Ajustar timezone

Se os horários estiverem errados, configure timezone no `docker-compose.yml`:

```yaml
services:
  bws-backend:
    environment:
      - TZ=America/Sao_Paulo  # Adicionar esta linha
```

Depois:
```bash
docker compose down
docker compose up -d
```

---

## 7️⃣ Backup Automático

### 7.1 Configurar backup diário

Edite o crontab do CasaOS:

```bash
crontab -e
```

Adicione:
```cron
# Backup diário do BWS Finance às 02:00
0 2 * * * docker exec bws-finance-backend sqlite3 /app/bws_finance.db ".backup /app/data/backup_$(date +\%Y\%m\%d).db"

# Limpar backups antigos (manter 30 dias)
0 3 * * * find /DATA/AppData/bws-finance/data -name "backup_*.db" -mtime +30 -delete

# Backup semanal completo (domingos às 03:00)
0 3 * * 0 tar -czf /DATA/Backups/bws-finance/backup_completo_$(date +\%Y\%m\%d).tar.gz -C /DATA/AppData bws-finance
```

### 7.2 Backup manual

```bash
# Backup do banco
docker exec bws-finance-backend sqlite3 /app/bws_finance.db ".backup /app/data/backup_manual_$(date +%Y%m%d).db"

# Backup completo da aplicação
tar -czf ~/backup_bws_$(date +%Y%m%d).tar.gz /DATA/AppData/bws-finance
```

### 7.3 Restaurar backup

```bash
# Parar serviços
docker compose down

# Restaurar banco
cp /DATA/AppData/bws-finance/data/backup_20251110.db \
   /DATA/AppData/bws-finance/bws_finance.db

# Reiniciar
docker compose up -d
```

---

## 8️⃣ Segurança e HTTPS

### 8.1 Configurar Nginx Proxy Manager

1. Instale **Nginx Proxy Manager** pelo CasaOS App Store
2. Acesse: `http://192.168.80.132:81`
3. Login padrão:
   - Email: `admin@example.com`
   - Senha: `changeme`
4. Troque a senha imediatamente

### 8.2 Criar Proxy Host

1. Vá em **"Proxy Hosts"** → **"Add Proxy Host"**
2. **Details:**
   - Domain Names: `bws.seudominio.com`
   - Scheme: `http`
   - Forward Hostname/IP: `bws-finance-backend`
   - Forward Port: `5000`
   - ✅ Block Common Exploits
   - ✅ Websockets Support
3. **SSL:**
   - ✅ Force SSL
   - SSL Certificate: **Request a new SSL Certificate**
   - ✅ Force SSL
   - ✅ HTTP/2 Support
   - Email: `seu-email@dominio.com`
   - ✅ I Agree to the Let's Encrypt Terms of Service
4. Clique em **"Save"**

Agora acesse: `https://bws.seudominio.com`

### 8.3 Configurar CORS no backend

Edite `.env`:
```env
ALLOWED_ORIGINS=https://bws.seudominio.com,http://localhost:5173
```

---

## 9️⃣ Monitoramento

### 9.1 Logs em tempo real

```bash
# Todos os serviços
docker compose logs -f

# Apenas backend
docker compose logs -f bws-backend

# Apenas WhatsApp
docker compose logs -f bws-whatsapp
```

### 9.2 Dashboard de métricas

Acesse: `http://192.168.80.132:5000/api/notifications/health`

Resposta:
```json
{
  "status": "healthy",
  "scheduler_running": true,
  "jobs_count": 5,
  "whatsapp_available": true,
  "email_available": true,
  "jobs": [...]
}
```

### 9.3 Recursos do sistema

```bash
# CPU e RAM
docker stats bws-finance-backend bws-whatsapp-server

# Espaço em disco
df -h /DATA/AppData/bws-finance

# Tamanho do banco
du -sh /DATA/AppData/bws-finance/bws_finance.db
```

---

## 🔟 Manutenção Regular

### 10.1 Atualizar aplicação

```bash
cd /DATA/AppData/bws-finance

# Backup antes de atualizar
tar -czf ~/backup_pre_update_$(date +%Y%m%d).tar.gz .

# Atualizar código (se usar Git)
git pull origin main

# Rebuild
docker compose build

# Reiniciar
docker compose down
docker compose up -d
```

### 10.2 Limpar logs antigos

```bash
# Logs maiores que 100MB
find /DATA/AppData/bws-finance/logs -type f -size +100M -delete

# Logs mais antigos que 30 dias
find /DATA/AppData/bws-finance/logs -type f -mtime +30 -delete

# Rotação de logs (adicionar ao crontab)
0 0 * * * find /DATA/AppData/bws-finance/logs -name "*.log" -exec gzip {} \; -exec mv {}.gz {}.$(date +\%Y\%m\%d).gz \;
```

### 10.3 Otimizar banco de dados

```bash
# Vacuum (compactar)
docker exec bws-finance-backend sqlite3 /app/bws_finance.db "VACUUM;"

# Reindexar
docker exec bws-finance-backend sqlite3 /app/bws_finance.db "REINDEX;"

# Verificar integridade
docker exec bws-finance-backend sqlite3 /app/bws_finance.db "PRAGMA integrity_check;"
```

---

## ✅ Checklist de Configuração Completa

- [ ] Conta de administrador criada
- [ ] WhatsApp conectado e status "CONNECTED"
- [ ] Preferências de notificações configuradas
- [ ] Opt-in WhatsApp e Email marcados
- [ ] Pelo menos 1 conta bancária cadastrada
- [ ] Pelo menos 1 cartão com due_day configurado
- [ ] Teste de notificação enviado e recebido
- [ ] Scheduler ativo com 5 jobs
- [ ] Backup automático configurado
- [ ] HTTPS configurado (se domínio disponível)
- [ ] Logs sendo monitorados

---

## 📞 Próximos Passos

Agora que tudo está configurado:

1. **Use o sistema diariamente:**
   - Registre transações
   - Acompanhe saldo e faturas
   - Monitore investimentos

2. **Receba notificações automáticas:**
   - Faturas vencendo (3, 1, 0 dias antes)
   - Saldos baixos (quando < R$ 100)
   - Resumos mensais (domingos 18:00)

3. **Personalize:**
   - Ajuste horários do scheduler (services/auto_notifications.py)
   - Crie templates customizados (templates/emails/)
   - Configure categorias e tags

---

**🎉 Pronto! Seu BWS Finance está totalmente configurado e funcionando!**

Para suporte: veja `TROUBLESHOOTING_CASAOS.md`
