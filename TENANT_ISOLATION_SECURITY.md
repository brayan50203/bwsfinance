# 🔒 Isolamento de Dados entre Contas (Multi-Tenant Security)

## 📋 Visão Geral

O sistema BWS Finance implementa **isolamento total de dados entre tenants** (contas diferentes), garantindo que:
- ✅ Conta A **nunca** vê dados da Conta B
- ✅ Conta B **nunca** vê dados da Conta A
- ✅ Cada usuário vê apenas seus próprios dados financeiros
- ✅ A IA respeita o isolamento em todas as operações

---

## 🔐 Como Funciona o Isolamento

### 1. **Identificação de Tenant**

Cada usuário pertence a um **tenant** (empresa/conta). O tenant_id é capturado na sessão durante o login:

```python
# No login (app.py)
session['user_id'] = user['id']
session['tenant_id'] = user['tenant_id']  # ← Identificador único da conta
```

### 2. **Filtros em Todas as Queries**

**TODAS** as consultas ao banco de dados incluem filtro por `tenant_id`:

#### Banco Principal (bws_finance.db)
```sql
-- Exemplo: Buscar transações
SELECT * FROM transactions
WHERE user_id = ? AND tenant_id = ?  -- ← Duplo filtro

-- Exemplo: Buscar contas
SELECT * FROM accounts
WHERE user_id = ? AND tenant_id = ?

-- Exemplo: Buscar investimentos
SELECT * FROM investments
WHERE user_id = ? AND tenant_id = ?
```

#### Banco da IA (ai_history.db)
```sql
-- Histórico de conversas
SELECT * FROM ai_conversations
WHERE user_id = ? AND tenant_id = ?  -- ← Isolamento garantido

-- Insights gerados
SELECT * FROM ai_insights
WHERE user_id = ? AND tenant_id = ?
```

---

## 🛡️ Implementação no Sistema de IA

### **Arquivo: routes/ai.py**

Todos os endpoints da IA capturam tenant_id da sessão:

```python
@ai_bp.route('/chat', methods=['POST'])
@login_required_api
def chat_with_ai():
    user_id = session.get('user_id')
    tenant_id = session.get('tenant_id')  # ← Captura tenant
    
    # IA é inicializada com tenant_id
    ai = BWSInsightAI(user_id=user_id, tenant_id=tenant_id)
    
    # Todas as operações usam esse tenant_id
    financial_data = ai.fetch_financial_data(session=request.cookies)
```

**7 Endpoints Protegidos:**
- ✅ `/api/ai/chat` - Chat isolado por tenant
- ✅ `/api/ai/insight` - Insights isolados por tenant
- ✅ `/api/ai/history` - Histórico isolado por tenant
- ✅ `/api/ai/alerts` - Alertas isolados por tenant
- ✅ `/api/ai/predict` - Previsões isoladas por tenant
- ✅ `/api/ai/summary` - Análise isolada por tenant
- ✅ `/api/ai/status` - Status (não usa dados sensíveis)

### **Arquivo: services/ai_core.py**

A classe `BWSInsightAI` armazena tenant_id como propriedade:

```python
class BWSInsightAI:
    def __init__(self, base_url, user_id, tenant_id):
        self.user_id = user_id
        self.tenant_id = tenant_id  # ← Armazenado na instância
        
    def save_conversation(self, user_message, ai_response, context=None):
        cursor.execute("""
            INSERT INTO ai_conversations (user_id, tenant_id, ...)
            VALUES (?, ?, ...)
        """, (self.user_id, self.tenant_id, ...))  # ← Sempre usa tenant_id
        
    def get_conversation_history(self, limit=10):
        cursor.execute("""
            SELECT * FROM ai_conversations
            WHERE user_id = ? AND tenant_id = ?  # ← Filtro duplo
            ORDER BY timestamp DESC
            LIMIT ?
        """, (self.user_id, self.tenant_id, limit))
```

---

## 🧪 Cenários de Teste

### Cenário 1: Usuário da Conta A pergunta "Qual meu saldo?"

```
1. Login: session['tenant_id'] = 'conta_a'
2. Chat: POST /api/ai/chat
3. IA busca: SELECT * FROM accounts WHERE tenant_id = 'conta_a'
4. Resultado: Apenas dados da Conta A
```

### Cenário 2: Usuário da Conta B pergunta "Qual meu saldo?"

```
1. Login: session['tenant_id'] = 'conta_b'
2. Chat: POST /api/ai/chat
3. IA busca: SELECT * FROM accounts WHERE tenant_id = 'conta_b'
4. Resultado: Apenas dados da Conta B
```

### Cenário 3: Tentativa de Ataque (sem tenant_id na query)

```sql
-- ❌ Query VULNERÁVEL (não usada no sistema)
SELECT * FROM ai_conversations WHERE user_id = 'user_a'

-- ✅ Query SEGURA (usada no sistema)
SELECT * FROM ai_conversations 
WHERE user_id = 'user_a' AND tenant_id = 'conta_a'
```

---

## 📊 Estrutura das Tabelas da IA

### Tabela: ai_conversations
```sql
CREATE TABLE ai_conversations (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,          -- ID do usuário
    tenant_id TEXT NOT NULL,        -- ID da conta (isolamento)
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    context TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Índices para performance
    INDEX idx_tenant_user (tenant_id, user_id)
);
```

### Tabela: ai_insights
```sql
CREATE TABLE ai_insights (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,          -- ID do usuário
    tenant_id TEXT NOT NULL,        -- ID da conta (isolamento)
    insight_type TEXT NOT NULL,
    insight_text TEXT NOT NULL,
    data TEXT,
    severity TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Índices para performance
    INDEX idx_tenant_user (tenant_id, user_id)
);
```

---

## 🔍 Checklist de Segurança

### ✅ Backend (Python/Flask)

- [x] `session['tenant_id']` capturado no login
- [x] Decorator `@login_required_api` em todas as rotas AI
- [x] `tenant_id` passado para BWSInsightAI()
- [x] Todas as queries SQL filtram por tenant_id
- [x] `save_conversation()` salva com tenant_id
- [x] `get_conversation_history()` filtra por tenant_id
- [x] `save_insight()` salva com tenant_id
- [x] APIs REST (/api/dashboard, /api/accounts) já isoladas

### ✅ Banco de Dados

- [x] Coluna `tenant_id` em todas as tabelas
- [x] Índices compostos (tenant_id, user_id)
- [x] Constraints NOT NULL em tenant_id
- [x] Queries sempre incluem WHERE tenant_id = ?

### ✅ Machine Learning

- [x] ML Engine não acessa banco diretamente
- [x] Recebe dados já filtrados do ai_core
- [x] Análises baseadas apenas em dados do tenant
- [x] Anomalias detectadas por tenant
- [x] Previsões calculadas por tenant

---

## 🚨 Regras de Ouro

### 1. **NUNCA faça query sem tenant_id**
```python
# ❌ ERRADO
cursor.execute("SELECT * FROM ai_conversations WHERE user_id = ?", (user_id,))

# ✅ CORRETO
cursor.execute("""
    SELECT * FROM ai_conversations 
    WHERE user_id = ? AND tenant_id = ?
""", (user_id, tenant_id))
```

### 2. **SEMPRE capture tenant_id da sessão**
```python
# ✅ CORRETO
user_id = session.get('user_id')
tenant_id = session.get('tenant_id')  # ← Obrigatório
```

### 3. **SEMPRE passe tenant_id para a IA**
```python
# ✅ CORRETO
ai = BWSInsightAI(user_id=user_id, tenant_id=tenant_id)
```

### 4. **SEMPRE use @login_required_api**
```python
# ✅ CORRETO
@ai_bp.route('/chat', methods=['POST'])
@login_required_api  # ← Obrigatório
def chat_with_ai():
    ...
```

---

## 🧪 Como Testar o Isolamento

### Teste Manual

1. **Criar 2 contas diferentes:**
   - Conta A: user1@teste.com
   - Conta B: user2@teste.com

2. **Login na Conta A:**
   ```
   POST /login
   { "email": "user1@teste.com", "password": "..." }
   ```

3. **Fazer perguntas à IA:**
   ```
   POST /api/ai/chat
   { "message": "Qual meu saldo?" }
   ```

4. **Verificar resposta:**
   - Deve mostrar apenas dados da Conta A

5. **Logout e Login na Conta B:**
   ```
   GET /logout
   POST /login
   { "email": "user2@teste.com", "password": "..." }
   ```

6. **Fazer mesma pergunta:**
   ```
   POST /api/ai/chat
   { "message": "Qual meu saldo?" }
   ```

7. **Verificar resposta:**
   - Deve mostrar apenas dados da Conta B
   - **NÃO deve mostrar dados da Conta A**

### Teste Automatizado

Execute o script de teste:
```powershell
python test_tenant_isolation.py
```

**Resultado esperado:**
```
✅ Testes aprovados: 4/4
🎉 ISOLAMENTO DE DADOS: 100% SEGURO
✅ Tenant A não acessa dados do Tenant B
✅ Tenant B não acessa dados do Tenant A
✅ Todas as queries filtram por tenant_id
```

---

## 📈 Arquitetura de Segurança

```
┌─────────────────────────────────────────────────────┐
│                    USUÁRIO                          │
│              (Login com credenciais)                │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│                 FLASK SESSION                       │
│        user_id = 123, tenant_id = 'conta_a'        │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│              @login_required_api                    │
│         Verifica se usuário está logado             │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│               ROTAS DA IA (routes/ai.py)            │
│   Captura: user_id + tenant_id da sessão           │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│         BWSInsightAI (services/ai_core.py)          │
│   Armazena: self.tenant_id = tenant_id             │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│              BANCO DE DADOS                         │
│  WHERE user_id = ? AND tenant_id = ?               │
│  ↓                                                  │
│  Retorna apenas dados do tenant específico          │
└─────────────────────────────────────────────────────┘
```

---

## 🎯 Garantias de Segurança

### ✅ O que ESTÁ protegido:

1. **Conversas com a IA** - Isoladas por tenant
2. **Histórico de chat** - Isolado por tenant
3. **Insights gerados** - Isolados por tenant
4. **Análises de ML** - Baseadas apenas em dados do tenant
5. **Previsões** - Calculadas apenas com dados do tenant
6. **Anomalias** - Detectadas apenas nos dados do tenant
7. **Dados financeiros** - Já isolados no banco principal

### ✅ O que NÃO pode acontecer:

- ❌ Tenant A ver saldo do Tenant B
- ❌ Tenant A ver transações do Tenant B
- ❌ Tenant A ver conversas com IA do Tenant B
- ❌ Tenant A ver insights do Tenant B
- ❌ Tenant A ver investimentos do Tenant B
- ❌ Vazamento de dados entre contas

---

## 🔐 Conclusão

**O sistema BWS Finance implementa isolamento de dados em TODAS as camadas:**

✅ **Camada de Autenticação:** Session com tenant_id  
✅ **Camada de Rotas:** Decorator @login_required_api  
✅ **Camada de Lógica:** BWSInsightAI com tenant_id  
✅ **Camada de Dados:** Queries com WHERE tenant_id = ?  
✅ **Camada de ML:** Análises isoladas por tenant  

**RESULTADO:** Isolamento 100% garantido entre Conta A e Conta B! 🎉🔒
