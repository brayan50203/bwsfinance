# 🤖 BWS Insight AI - Sistema de IA Autônoma para Análise Financeira

## 📋 Visão Geral

O **BWS Insight AI** é um assistente financeiro inteligente integrado ao sistema BWSFinance. Ele analisa automaticamente seus dados financeiros, gera insights personalizados, detecta anomalias, faz previsões e responde perguntas em linguagem natural.

## ✨ Principais Funcionalidades

### 1. **Chat Interativo com IA**
- Responde perguntas em português sobre suas finanças
- Processamento de linguagem natural
- Respostas formatadas em Markdown com emojis

**Exemplos de perguntas:**
- "Quanto tenho de saldo?"
- "Quanto gastei este mês?"
- "Quanto gastei com alimentação?"
- "Como estão meus investimentos?"
- "Me mostre onde gastei mais"
- "Qual a previsão para o próximo mês?"

### 2. **Insights Diários Automatizados**
- Análise automática da situação financeira
- Classificação por severidade (baixa, média, alta)
- Alertas sobre situações críticas

**Tipos de insights:**
- ⚠️ Saldo negativo
- 💰 Taxa de poupança
- 📊 Desempenho de investimentos
- 💳 Taxa de endividamento
- 🎯 Gastos por categoria

### 3. **Previsões Financeiras**
- Previsão de saldo futuro (7, 15, 30 dias)
- Baseado em média móvel dos últimos meses
- Indicador de confiança da previsão

### 4. **Detecção de Anomalias**
- Identifica picos de gastos (>30% variação)
- Detecta concentração excessiva em categorias
- Alerta sobre padrões incomuns

### 5. **Sistema de Alertas**
- Notificações de alta prioridade
- Filtro de alertas críticos
- Histórico de alertas

## 🏗️ Arquitetura do Sistema

### Backend (Python/Flask)

```
services/
├── ai_core.py       # Motor principal da IA
│   ├── BWSInsightAI           # Classe principal
│   ├── fetch_financial_data() # Coleta dados das APIs
│   ├── generate_daily_insight() # Gera insights
│   ├── predict_future_balance() # Previsões
│   └── detect_anomalies()      # Detecta anomalias
│
├── ai_chat.py       # Processador de chat
│   ├── AIChat                 # Classe de chat
│   ├── process_message()      # Processa mensagens
│   └── detect_intent()        # Detecta intenções
│
routes/
└── ai.py            # Rotas REST da IA
    ├── GET  /api/ai/insight   # Insights do dia
    ├── POST /api/ai/chat      # Chat interativo
    ├── GET  /api/ai/history   # Histórico de chat
    ├── GET  /api/ai/alerts    # Alertas críticos
    ├── GET  /api/ai/predict   # Previsões
    ├── GET  /api/ai/summary   # Análise completa
    └── GET  /api/ai/status    # Status do sistema
```

### Frontend (React)

```
frontend/src/
├── components/
│   ├── AIFloatingButton.jsx  # Botão flutuante
│   ├── AIChat.jsx            # Interface de chat
│   └── AIInsightCard.jsx     # Card de insights
│
└── pages/
    └── AIPanel.jsx           # Painel completo da IA
```

### Database

```sql
-- ai_history.db

CREATE TABLE ai_conversations (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    tenant_id INTEGER NOT NULL,
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    context TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ai_insights (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    tenant_id INTEGER NOT NULL,
    insight_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    data TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🚀 Instalação e Configuração

### 1. Instalar Dependências do Backend

```powershell
# Na raiz do projeto
pip install -r requirements_ai.txt
```

**Pacotes necessários:**
- `pandas>=2.0.0` - Análise de dados
- `numpy>=1.24.0` - Computação numérica

### 2. Instalar Dependências do Frontend

```powershell
cd frontend
npm install
```

**Novo pacote adicionado:**
- `react-markdown` - Renderização de Markdown no chat

### 3. Registro do Blueprint (já configurado)

O blueprint da IA já está registrado em `app.py`:

```python
from routes.ai import ai_bp
app.register_blueprint(ai_bp)
```

### 4. Inicialização Automática

O banco de dados `ai_history.db` é criado automaticamente na primeira execução.

## 📡 API Endpoints

### **GET /api/ai/insight**
Retorna insights diários com anomalias e previsões.

**Resposta:**
```json
{
  "success": true,
  "insights": [
    {
      "type": "balance",
      "severity": "high",
      "title": "Atenção: Saldo Negativo",
      "message": "Seu saldo está negativo em R$ 1.234,56..."
    }
  ],
  "anomalies": [...],
  "predictions": [...]
}
```

### **POST /api/ai/chat**
Processa mensagem do usuário e retorna resposta da IA.

**Request:**
```json
{
  "message": "Quanto gastei com alimentação?"
}
```

**Resposta:**
```json
{
  "success": true,
  "ai_response": "📊 **Gastos com Alimentação**\n\nEste mês você gastou **R$ 1.234,56** com alimentação...",
  "intent": "gastos",
  "context": {...}
}
```

### **GET /api/ai/history?limit=10**
Retorna histórico de conversas.

### **GET /api/ai/alerts**
Retorna apenas alertas de alta prioridade.

### **GET /api/ai/predict?days=30**
Retorna previsão de saldo para N dias.

### **GET /api/ai/summary**
Retorna análise completa (insights + anomalias + previsões + resumo).

### **GET /api/ai/status**
Verifica status e capacidades do sistema.

## 🎯 Sistema de Detecção de Intenções

O chat utiliza regex para detectar a intenção do usuário:

| Intenção | Padrões | Exemplo |
|----------|---------|---------|
| **saldo** | `quanto.*tenho`, `qual.*saldo` | "Quanto tenho de saldo?" |
| **gastos** | `quanto.*gastei`, `gastei.*com` | "Quanto gastei com alimentação?" |
| **receitas** | `recebi`, `renda`, `ganhos` | "Quanto recebi este mês?" |
| **investimentos** | `investimento`, `ações`, `carteira` | "Como estão meus investimentos?" |
| **previsao** | `previsão`, `futuro`, `próximo` | "Qual a previsão para o próximo mês?" |
| **comparacao** | `comparar`, `diferença`, `vs` | "Compare este mês com o anterior" |
| **categoria** | `onde gastei`, `categorias` | "Onde gastei mais?" |

## 🧮 Algoritmos de Análise

### 1. **Previsão de Saldo (Moving Average)**

```python
def predict_future_balance(data, days=30):
    # Usa média móvel dos últimos 6 meses
    # Considera tendência de receitas e gastos
    # Retorna valor previsto + % de confiança
```

**Confiança:**
- 80-100%: Muitos dados históricos
- 60-79%: Dados moderados
- 40-59%: Poucos dados

### 2. **Detecção de Anomalias**

```python
def detect_anomalies(data):
    # Anomalia 1: Variação > 30% nos gastos
    if variation > 0.3:
        return "Pico de gastos detectado"
    
    # Anomalia 2: Concentração > 40% em uma categoria
    if category_percent > 40:
        return "Gastos concentrados em alimentação"
```

### 3. **Geração de Insights**

Verifica automaticamente:
- ✅ Saldo atual (negativo = alerta HIGH)
- ✅ Taxa de poupança (< 20% = alerta MEDIUM)
- ✅ Investimentos (sem ativos = alerta MEDIUM)
- ✅ Endividamento (> 50% = alerta HIGH)
- ✅ Top 3 categorias de gastos

## 🎨 Interface do Usuário

### 1. **Botão Flutuante (AIFloatingButton)**
- Fixo no canto inferior direito
- Ícone: 💬 (fechado) / ❌ (aberto)
- Gradiente roxo → Vermelho quando ativo
- Indicador verde pulsante

### 2. **Chat (AIChat)**
- Mensagens do usuário (azul, direita)
- Mensagens da IA (cinza, esquerda)
- Suporte a Markdown
- Perguntas rápidas na primeira interação
- Auto-scroll para novas mensagens
- Indicador de "digitando..."

### 3. **Card de Insights (AIInsightCard)**
- Colorido por severidade:
  - 🟢 Verde: Baixa
  - 🟡 Amarelo: Média
  - 🔴 Vermelho: Alta
- Expansível (clique para ver detalhes)
- Seções: Insights / Previsões / Anomalias

### 4. **Painel Completo (AIPanel)**
- 4 abas:
  - **Insights do Dia**: Análise atual
  - **Previsões**: Gráfico de 30 dias
  - **Alertas**: Lista de alertas críticos
  - **Chat com IA**: Chat completo
- Status em tempo real
- Gráficos interativos

## 🔒 Segurança

- ✅ Todas as rotas protegidas com `@login_required_api`
- ✅ Validação de `user_id` e `tenant_id` via sessão
- ✅ Isolamento de dados por tenant
- ✅ Sanitização de inputs
- ✅ CORS configurado apenas para localhost

## 📊 Fontes de Dados

A IA consome dados de:

1. **GET /api/dashboard** - Resumo financeiro
2. **GET /api/accounts** - Saldo de contas
3. **GET /api/investments** - Carteira de investimentos

Todos os dados são do tenant e usuário autenticado.

## 🔄 Melhorias Futuras (Roadmap)

### Curto Prazo
- [ ] Scheduler para insights automáticos (6 em 6 horas)
- [ ] Cache de respostas frequentes (Redis)
- [ ] Exportar conversas em PDF
- [ ] Notificações push no navegador

### Médio Prazo
- [ ] Machine Learning com Scikit-Learn
  - [ ] Regressão linear para previsões avançadas
  - [ ] Clustering de padrões de gastos
  - [ ] Classificação de transações
- [ ] Análise de sentimento nos gastos
- [ ] Sugestões de economia personalizadas
- [ ] Comparação com médias de mercado

### Longo Prazo
- [ ] Entrada de voz (Speech-to-Text)
- [ ] Respostas em áudio (Text-to-Speech)
- [ ] Integração com WhatsApp/Telegram
- [ ] Relatórios automáticos por email
- [ ] Deep Learning para detecção de fraudes

## 🐛 Troubleshooting

### Erro: "IA não responde"
**Solução:** Verificar se o servidor Flask está rodando.

```powershell
# Verificar logs
python app.py
```

### Erro: "ModuleNotFoundError: No module named 'pandas'"
**Solução:** Instalar dependências.

```powershell
pip install -r requirements_ai.txt
```

### Erro: "Cannot read properties of undefined"
**Solução:** Instalar dependências do frontend.

```powershell
cd frontend
npm install
```

### Erro: "Database locked"
**Solução:** Fechar outras conexões ao banco.

```powershell
python unlock_db.py
```

### Chat não exibe Markdown
**Solução:** Verificar se `react-markdown` está instalado.

```powershell
cd frontend
npm install react-markdown
```

## 📈 Métricas de Performance

- **Tempo de resposta do chat:** < 500ms
- **Geração de insights:** < 2 segundos
- **Previsões (30 dias):** < 1 segundo
- **Detecção de anomalias:** < 500ms

## 🎓 Como Usar

### 1. Abrir o Dashboard
```
http://localhost:5000/dashboard
```

### 2. Clicar no Botão Flutuante (canto inferior direito)

### 3. Fazer Perguntas
- "Quanto gastei este mês?"
- "Como estão meus investimentos?"
- "Qual a previsão para 30 dias?"

### 4. Visualizar Insights
- Card com análise automática no topo
- Colorido por severidade
- Clique para expandir detalhes

### 5. Acessar Painel Completo
```
http://localhost:5000/ai
```

## 📝 Exemplos de Uso

### Exemplo 1: Consultar Saldo
```
Usuário: "Quanto tenho de saldo?"

IA: "💰 Seu Saldo Atual

Você tem R$ 1.234,56 de saldo total.

📊 Detalhes:
• Conta Corrente: R$ 800,00
• Poupança: R$ 434,56

Saldo: Positivo ✅"
```

### Exemplo 2: Analisar Gastos
```
Usuário: "Quanto gastei com alimentação?"

IA: "📊 Gastos com Alimentação

Este mês você gastou R$ 567,89 com alimentação.

Isso representa 23,4% dos seus gastos totais.

Comparado com o mês anterior: +12,3% 📈"
```

### Exemplo 3: Previsão
```
Usuário: "Qual a previsão para o próximo mês?"

IA: "🔮 Previsão Financeira

Baseado no seu histórico:

Em 30 dias: R$ 2.345,67 (85% confiança)

Tendência: Saldo crescente 📈"
```

## 🏆 Personalidade da IA

- ✅ Amigável e profissional
- ✅ Usa emojis contextuais
- ✅ Respostas formatadas em Markdown
- ✅ Tom de consultor financeiro pessoal
- ✅ Linguagem clara e objetiva
- ✅ Incentiva boas práticas financeiras

## 📞 Suporte

Em caso de dúvidas ou problemas:
1. Verificar logs do servidor Flask
2. Consultar console do navegador (F12)
3. Testar endpoints via Postman/Insomnia
4. Verificar permissões de acesso ao banco

---

**BWS Insight AI** - Seu consultor financeiro inteligente 🤖💰
