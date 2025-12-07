# 🔔 Sistema de Notificações Inteligentes - BWS Finance

## 📋 Visão Geral

Sistema completo e modular de notificações com IA integrada ao BWS Finance, suportando múltiplos canais (Sistema, E-mail, WhatsApp, Push) e análise inteligente de padrões financeiros.

---

## 🏗️ Arquitetura

### Módulos Criados

```
services/
├── notification_center.py      # Core do sistema de notificações
├── notification_ai.py          # IA para análise e insights
├── email_sender.py            # Envio por e-mail (SMTP)
└── whatsapp_sender.py         # Envio via WhatsApp (WPPConnect)

migrations/
└── add_notifications_tables.sql  # Schema das tabelas

templates/
└── notification_preferences.html  # Interface de configurações

scripts/
└── apply_notification_migration.py  # Script de migração

config/
└── email_config.json  # Configurações SMTP
```

### Tabelas do Banco de Dados

#### **notifications**
```sql
- id (PK)
- user_id
- tenant_id
- title
- message
- category (Financeiro, Investimentos, Sistema, Erro, Atualização, IA)
- priority (low, normal, high, urgent)
- status (unread, read, archived)
- channel (system, email, whatsapp, push)
- related_type (transaction, investment, import, backup)
- related_id
- metadata (JSON)
- created_at
- read_at
- sent_at
```

#### **notification_preferences**
```sql
- id (PK)
- user_id (UNIQUE)
- tenant_id
- enable_system, enable_email, enable_whatsapp, enable_push
- high_expense_threshold (R$)
- investment_change_threshold (%)
- quiet_hours_start, quiet_hours_end
- email_address, whatsapp_number
- daily_summary, weekly_report, monthly_report
- enable_ai_insights, enable_pattern_detection
- created_at, updated_at
```

#### **notification_logs**
```sql
- id (PK)
- notification_id (FK)
- channel (email, whatsapp, push)
- status (pending, sent, delivered, failed, blocked)
- error_message
- sent_at, delivered_at
```

---

## 🚀 Instalação e Configuração

### 1. Aplicar Migração do Banco

```bash
python scripts/apply_notification_migration.py
```

Isso criará:
- Tabelas `notifications`, `notification_preferences`, `notification_logs`
- Preferências padrão para todos os usuários existentes
- Índices para performance

### 2. Configurar E-mail (Opcional)

Edite `config/email_config.json`:

```json
{
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_user": "seu@email.com",
    "smtp_password": "sua_senha_de_app",
    "from_email": "noreply@bwsfinance.com",
    "from_name": "BWS Finance"
}
```

**Para Gmail:**
1. Acesse https://myaccount.google.com/apppasswords
2. Crie uma "Senha de app"
3. Use essa senha no `smtp_password`

**Ou use variáveis de ambiente:**
```bash
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USER=seu@email.com
export SMTP_PASSWORD=sua_senha_de_app
export FROM_EMAIL=noreply@bwsfinance.com
```

### 3. Configurar WhatsApp (Opcional)

O servidor WhatsApp já deve estar rodando. Verifique:
```bash
# Checar status
curl http://localhost:3000/health

# Iniciar se necessário
cd whatsapp_server
node index.js
```

### 4. Reiniciar Servidor Flask

```bash
# Parar servidor existente
taskkill /F /IM pythonw.exe

# Iniciar novamente
.\start-background.bat
```

---

## 📡 API REST

### Endpoints Disponíveis

#### GET `/api/notifications`
Lista notificações do usuário

**Query params:**
- `status` (opcional): `unread`, `read`, `archived`
- `limit` (opcional): Número máximo de resultados (padrão: 50)

**Resposta:**
```json
{
  "success": true,
  "notifications": [
    {
      "id": 1,
      "title": "Gasto Alto Detectado 💸",
      "message": "Foi registrado um gasto de R$ 850.00 em 'Mercado Livre'...",
      "category": "Financeiro",
      "priority": "high",
      "status": "unread",
      "created_at": "2025-11-08 10:30:00",
      "metadata": {"amount": 850.0, "description": "Mercado Livre"}
    }
  ],
  "unread_count": 3
}
```

#### POST `/api/notifications`
Cria nova notificação

**Body:**
```json
{
  "title": "Título da notificação",
  "message": "Mensagem completa",
  "category": "FINANCEIRO",
  "priority": "HIGH",
  "channels": ["system", "whatsapp"],
  "related_type": "transaction",
  "related_id": "uuid",
  "metadata": {}
}
```

#### PATCH `/api/notifications/{id}/read`
Marca notificação como lida

#### PATCH `/api/notifications/read-all`
Marca todas notificações como lidas

#### DELETE `/api/notifications/{id}`
Deleta notificação

#### GET `/api/notifications/preferences`
Busca preferências do usuário

#### PUT `/api/notifications/preferences`
Atualiza preferências

**Body:**
```json
{
  "enable_email": true,
  "enable_whatsapp": false,
  "high_expense_threshold": 500.0,
  "investment_change_threshold": 5.0,
  "quiet_hours_start": "22:00",
  "quiet_hours_end": "08:00",
  "email_address": "seu@email.com",
  "whatsapp_number": "+5511999999999",
  "enable_ai_insights": true
}
```

#### GET `/api/notifications/ai-insights`
Retorna insights de IA

**Query params:**
- `days` (opcional): Período de análise em dias (padrão: 30)

**Resposta:**
```json
{
  "success": true,
  "insights": [
    {
      "type": "spending_increase",
      "severity": "high",
      "title": "Aumento nos Gastos Detectado",
      "message": "Seus gastos aumentaram 25.3% em relação ao período anterior...",
      "suggestion": "Analise suas despesas recentes...",
      "data": {}
    }
  ],
  "count": 5
}
```

#### GET `/api/notifications/monthly-report`
Gera relatório mensal completo

---

## 🧠 Sistema de IA

### Análises Automáticas

O sistema de IA (`notification_ai.py`) detecta automaticamente:

1. **Gastos Duplicados**
   - Identifica transações idênticas (valor, descrição, data)
   - Sugere verificação de cobranças duplicadas

2. **Comparação de Períodos**
   - Compara gastos do período atual com anterior
   - Alerta sobre aumentos >15%
   - Parabeniza por reduções

3. **Crescimento por Categoria**
   - Detecta categoria com maior crescimento (>30%)
   - Sugere cortes específicos

4. **Gastos Incomuns (Outliers)**
   - Identifica gastos 3x acima da média
   - Alerta para confirmação

5. **Taxa de Poupança**
   - Calcula % de economia da renda
   - Alerta se <10%, parabeniza se >20%

### Insights Inteligentes

```python
from services.notification_ai import NotificationAI

ai = NotificationAI()

# Análise de padrões (últimos 30 dias)
insights = ai.analyze_spending_patterns(user_id='uuid', days=30)

# Relatório mensal completo
report = ai.generate_monthly_report(user_id='uuid')

# Sugestões de corte de gastos
suggestions = ai.suggest_budget_cuts(user_id='uuid', target_reduction=500.0)
```

---

## 📨 Canais de Notificação

### 1. Sistema (Dashboard)
✅ **Sempre ativo**
- Sino com contador de não lidas
- Dropdown interativo
- Marcar como lida/deletar
- Atualização automática a cada 30s

### 2. E-mail
📧 **Configurável**
- Templates HTML responsivos
- Botão "Abrir no Painel"
- Logo BWS Finance
- Links de configurações

### 3. WhatsApp
📱 **Configurável**
- Mensagens formatadas com *negrito*
- Botões interativos (opcional)
- Resposta por voz (integração com IA existente)
- Confirmações automáticas

### 4. Push (Web)
🔔 **Em desenvolvimento**
- Service Worker
- Notificações nativas do navegador
- Click para abrir dashboard

---

## 🎯 Eventos que Geram Notificações

### Automáticos

| Evento | Categoria | Canais | Condição |
|--------|-----------|--------|----------|
| Gasto alto | Financeiro | Sistema + WhatsApp | Valor ≥ threshold |
| Variação de investimento | Investimentos | Sistema + Push | Mudança ≥ threshold |
| Importação concluída | Sistema | Sistema | Sempre |
| Erro de API | Erro | Sistema + E-mail | Sempre |
| Gasto duplicado | IA | Sistema + WhatsApp | Detectado pela IA |
| Aumento de gastos | IA | Sistema | Crescimento >15% |
| Taxa de poupança baixa | IA | Sistema + E-mail | <10% da renda |

### Manuais (via API)

```python
from services.notification_center import (
    notify_high_expense,
    notify_investment_change,
    notify_import_success,
    notify_api_error,
    notify_ai_insight
)

# Gasto alto
notify_high_expense(user_id, tenant_id, amount=850.0, description="Mercado Livre")

# Investimento
notify_investment_change(user_id, tenant_id, investment_name="BTC", change_pct=12.5)

# Importação
notify_import_success(user_id, tenant_id, count=45, source="Nubank")

# Erro API
notify_api_error(user_id, tenant_id, api_name="Pluggy", error="Timeout")

# Insight de IA
notify_ai_insight(user_id, tenant_id, 
                  insight="Você economizou 23% este mês", 
                  suggestion="Continue assim!")
```

---

## 🎨 Interface do Usuário

### Sino de Notificações

Aparece no canto superior direito de todas as páginas:
- 🔔 (sem badge) = Nenhuma notificação não lida
- 🔔 **3** = 3 notificações não lidas (badge vermelho pulsante)

### Dropdown

Ao clicar no sino:
- Lista das últimas 10 notificações
- Marcador visual para não lidas (fundo azul)
- Botões "Marcar como lida" / "Deletar"
- Link "Marcar todas como lidas"
- Link para ⚙️ Configurações

### Tela de Configurações

`/notifications/preferences`

Seções:
1. **Canais de Envio** - Ativar/desativar cada canal
2. **Limites de Alertas** - Definir thresholds personalizados
3. **Horário Permitido** - Quiet hours (ex: 22:00 - 08:00)
4. **Contatos** - E-mail e WhatsApp para envio externo
5. **Relatórios Automáticos** - Diário, semanal, mensal
6. **IA** - Ativar insights e detecção de padrões

---

## 🔐 Segurança

### Autenticação
- Todas as rotas exigem `@login_required`
- Notificações isoladas por `user_id` e `tenant_id`

### Validação
- Campos obrigatórios validados
- Enums para categorias e prioridades
- Sanitização de entrada

### Logs
- Toda tentativa de envio externo é registrada em `notification_logs`
- Status: `pending`, `sent`, `delivered`, `failed`, `blocked`
- Rastreabilidade completa

### Horário Permitido
- Sistema respeita `quiet_hours` automaticamente
- Não envia notificações externas fora do horário
- Notificações do sistema sempre criadas (mas não enviadas externamente)

---

## 📊 Exemplos de Uso

### 1. Criar Notificação Simples

```python
from services.notification_center import NotificationCenter, NotificationCategory, NotificationPriority

center = NotificationCenter()

notification_id = center.create_notification(
    user_id='user-uuid',
    tenant_id='tenant-uuid',
    title='Backup Concluído',
    message='Backup diário realizado com sucesso às 03:00.',
    category=NotificationCategory.SISTEMA,
    priority=NotificationPriority.LOW
)
```

### 2. Notificação Multi-Canal

```python
from services.notification_center import NotificationCenter, NotificationChannel

center = NotificationCenter()

center.create_notification(
    user_id='user-uuid',
    tenant_id='tenant-uuid',
    title='Transação de Alto Valor',
    message='Foi detectado um gasto de R$ 2.500,00 no cartão ****1234.',
    category=NotificationCategory.FINANCEIRO,
    priority=NotificationPriority.URGENT,
    channels=[
        NotificationChannel.SYSTEM,
        NotificationChannel.EMAIL,
        NotificationChannel.WHATSAPP
    ]
)
```

### 3. Buscar Notificações Não Lidas

```python
center = NotificationCenter()

unread = center.get_user_notifications(
    user_id='user-uuid',
    status='unread',
    limit=10
)

print(f"Você tem {len(unread)} notificações não lidas")
```

### 4. Análise de IA

```python
from services.notification_ai import NotificationAI

ai = NotificationAI()

# Insights dos últimos 30 dias
insights = ai.analyze_spending_patterns(user_id='user-uuid', days=30)

for insight in insights:
    print(f"{insight['title']}: {insight['message']}")
    print(f"Sugestão: {insight['suggestion']}\n")
```

### 5. Relatório Mensal Automático

```python
from services.notification_ai import NotificationAI
from services.notification_center import notify_ai_insight

ai = NotificationAI()
report = ai.generate_monthly_report(user_id='user-uuid')

# Enviar resumo via notificação
summary = f"Resumo de {report['month']}:\n"
summary += f"Renda: R$ {report['summary']['income']:.2f}\n"
summary += f"Gastos: R$ {report['summary']['expenses']:.2f}\n"
summary += f"Saldo: R$ {report['summary']['balance']:.2f}\n"

notify_ai_insight(
    user_id='user-uuid',
    tenant_id='tenant-uuid',
    insight=summary,
    suggestion="Veja os detalhes completos no dashboard"
)
```

---

## 🧪 Testes

### Testar API REST

```bash
# Listar notificações
curl http://127.0.0.1:5000/api/notifications

# Criar notificação
curl -X POST http://127.0.0.1:5000/api/notifications \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Teste",
    "message": "Mensagem de teste",
    "category": "SISTEMA",
    "priority": "NORMAL"
  }'

# Buscar insights de IA
curl http://127.0.0.1:5000/api/notifications/ai-insights?days=30

# Relatório mensal
curl http://127.0.0.1:5000/api/notifications/monthly-report
```

### Testar Notificações no Dashboard

1. Acesse http://127.0.0.1:5000/dashboard
2. Crie uma transação com valor alto (>R$ 500)
3. Verifique o sino 🔔 no canto superior direito
4. Deve aparecer badge vermelho com contador
5. Clique no sino para ver o dropdown

### Testar Configurações

1. Acesse http://127.0.0.1:5000/notifications/preferences
2. Altere canais, thresholds, horários
3. Clique em "💾 Salvar Configurações"
4. Deve mostrar "✅ Salvo!" em verde

---

## 🔧 Troubleshooting

### Notificações não aparecem no sino

1. Verificar se servidor está rodando:
   ```bash
   curl http://127.0.0.1:5000/api/notifications
   ```

2. Verificar console do navegador (F12) para erros JavaScript

3. Verificar se tabelas foram criadas:
   ```bash
   sqlite3 bws_finance.db "SELECT COUNT(*) FROM notifications"
   ```

### E-mails não são enviados

1. Verificar configurações em `config/email_config.json`

2. Testar SMTP manualmente:
   ```python
   from services.email_sender import send_email_notification
   send_email_notification('teste@email.com', 'Teste', 'Mensagem de teste')
   ```

3. Verificar logs:
   ```bash
   grep "email_sender" logs/server_*.log
   ```

### WhatsApp não envia

1. Verificar se servidor Node.js está rodando:
   ```bash
   curl http://localhost:3000/health
   ```

2. Verificar QR code foi escaneado

3. Testar envio direto:
   ```python
   from services.whatsapp_sender import send_whatsapp_notification
   send_whatsapp_notification('+5511999999999', 'Teste')
   ```

### IA não gera insights

1. Verificar se há dados suficientes (mínimo 10 transações)

2. Testar diretamente:
   ```python
   from services.notification_ai import NotificationAI
   ai = NotificationAI()
   insights = ai.analyze_spending_patterns('user-uuid', days=30)
   print(len(insights))
   ```

3. Verificar logs:
   ```bash
   grep "notification_ai" logs/server_*.log
   ```

---

## 📈 Roadmap

### Fase 1 ✅ (Completo)
- [x] Core de notificações
- [x] API REST completa
- [x] Interface com sino e dropdown
- [x] Sistema de preferências
- [x] Multi-canal (sistema, e-mail, WhatsApp)
- [x] IA para análise de padrões
- [x] Integração com transações e investimentos

### Fase 2 🔄 (Em andamento)
- [ ] Web Push notifications (Service Worker)
- [ ] Notificações agendadas (cron jobs)
- [ ] Resumos diários/semanais/mensais automáticos
- [ ] Templates de e-mail personalizáveis
- [ ] WhatsApp com botões interativos
- [ ] Resposta por voz no WhatsApp (transcrição + IA)

### Fase 3 📋 (Planejado)
- [ ] Integração com Telegram
- [ ] Notificações push mobile (PWA)
- [ ] Dashboard de analytics de notificações
- [ ] Machine Learning para predição de gastos
- [ ] Alertas de meta de economia
- [ ] Notificações de vencimento de contas

---

## 📝 Licença

Este módulo faz parte do BWS Finance e segue a mesma licença do projeto principal.

---

## 👥 Contribuindo

Para adicionar novos tipos de notificações:

1. Adicione função helper em `services/notification_center.py`:
```python
def notify_my_event(user_id, tenant_id, param1, param2):
    center = NotificationCenter()
    center.create_notification(
        user_id=user_id,
        tenant_id=tenant_id,
        title="Título do Evento",
        message=f"Mensagem com {param1} e {param2}",
        category=NotificationCategory.SISTEMA,
        priority=NotificationPriority.NORMAL,
        channels=[NotificationChannel.SYSTEM],
        metadata={'param1': param1, 'param2': param2}
    )
```

2. Importe e use onde o evento ocorre:
```python
from services.notification_center import notify_my_event

# No evento
notify_my_event(user['id'], user['tenant_id'], valor1, valor2)
```

---

**Desenvolvido com ❤️ para BWS Finance**  
Última atualização: 08/11/2025
