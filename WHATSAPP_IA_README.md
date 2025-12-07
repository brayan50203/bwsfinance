# 🤖 Integração IA + WhatsApp - Estilo Pixzinho Bot

## 🎯 O que foi implementado:

Inspirado no **Pixzinho Bot**, agora o BWS Finance tem um **assistente financeiro inteligente via WhatsApp** que usa a **IA já existente no sistema** para responder perguntas em linguagem natural!

## ✨ Funcionalidades:

### 💬 **Modo Pergunta (IA Conversacional)**
Faça perguntas naturais e receba respostas inteligentes:

**Exemplos:**
```
📱 Você: Quanto gastei esse mês?
🤖 IA: Você gastou R$ 2.450,00 este mês. Isso é 15% a mais que o mês passado.

📱 Você: Qual meu saldo atual?
🤖 IA: Seu saldo total é R$ 5.230,45. Você tem 3 contas ativas.

📱 Você: Quanto recebi de salário?
🤖 IA: Você recebeu R$ 5.000,00 de salário este mês.

📱 Você: Onde gastei mais?
🤖 IA: Sua maior categoria de gastos foi Alimentação com R$ 850,00 (34,7% do total).

📱 Você: Como estão meus investimentos?
🤖 IA: Seus investimentos totalizam R$ 12.450,00 com rentabilidade de +8,5% no período.
```

### 💰 **Modo Transação (Lançamento Rápido)**
Adicione gastos/receitas rapidamente:

**Exemplos:**
```
📱 Você: Paguei R$ 50,00 no mercado hoje
🤖 IA: ✅ Transação adicionada!
       💰 Valor: R$ 50,00
       📅 Data: 09/11/2025
       📂 Categoria: Supermercado
```

## 🧠 Como funciona:

### **1. Detecção Inteligente**
O sistema detecta automaticamente se é:
- ❓ **Pergunta**: Palavras-chave como "quanto", "qual", "como", "onde", "?"
- 💸 **Transação**: Textos com valores (R$, reais, etc)

### **2. Processamento por IA**

#### Para **Perguntas**:
```python
# 1. Busca usuário pelo WhatsApp
user = get_user_by_whatsapp(sender)

# 2. Carrega dados financeiros do banco
financial_data = ai.fetch_financial_data_direct(user_id, tenant_id)

# 3. Processa com IA (services/ai_chat.py)
ai_response = chat.process_message(texto, financial_data)

# 4. Envia resposta
send_whatsapp_message(sender, ai_response)
```

#### Para **Transações**:
```python
# 1. Classifica com NLP
result = nlp_classifier.classify(texto)

# 2. Extrai: valor, data, categoria, descrição
# 3. Insere no banco de dados
# 4. Confirma no WhatsApp
```

## 📋 Pré-requisitos:

### **1. Cadastrar WhatsApp no Sistema**
1. Acesse: http://192.168.80.122:5000/settings
2. Vá em **Perfil**
3. Adicione seu número no campo **Telefone**: `5511949967277`
4. Salve

### **2. Autorizar Número no WhatsApp Server**
Edite o arquivo `.env`:
```env
ALLOWED_SENDERS=5511974764971,5511949967277
```

### **3. Iniciar Servidores**
```bash
# Terminal 1: Flask
.\start-server.ps1

# Terminal 2: WhatsApp
cd whatsapp_server
.\start-whatsapp.bat
```

## 🔧 Arquitetura:

```
┌─────────────────┐
│   WhatsApp      │
│   (Usuário)     │
└────────┬────────┘
         │ Mensagem
         ▼
┌─────────────────┐
│  WPPConnect     │◄──── Node.js (porta 3000)
│  (index.js)     │
└────────┬────────┘
         │ POST /api/whatsapp/webhook
         ▼
┌─────────────────┐
│  Flask Backend  │◄──── Python (porta 5000)
│  (app.py)       │
└────────┬────────┘
         │
         ├──► É Pergunta?
         │    └──► ai_chat.py
         │         └──► ai_core.py (fetch_financial_data_direct)
         │              └──► Resposta Inteligente
         │
         └──► É Transação?
              └──► nlp_classifier.py
                   └──► INSERT database
                        └──► Confirmação
```

## 🎓 Capacidades da IA:

### **Análises Disponíveis:**
- ✅ Saldo total e por conta
- ✅ Gastos totais e por categoria
- ✅ Receitas e entradas
- ✅ Investimentos e rentabilidade
- ✅ Comparação com mês anterior
- ✅ Previsão de saldo futuro
- ✅ Detecção de anomalias
- ✅ Padrões de consumo
- ✅ Dicas de economia
- ✅ Alertas de riscos

### **Módulos de IA:**
- `services/ai_core.py` - Motor principal
- `services/ai_chat.py` - Processador de linguagem natural
- `services/ai_ml_engine.py` - Machine Learning
- `modules/nlp_classifier.py` - Classificador de transações

## 💡 Exemplos de Uso Avançado:

### **Análises Complexas:**
```
📱 Você: Gastei mais que o mês passado?
🤖 IA: Sim, você gastou R$ 2.450,00 este mês contra R$ 2.100,00 no mês anterior.
       Isso representa um aumento de 16,7%.

📱 Você: Qual minha previsão de saldo?
🤖 IA: Com base nos seus padrões, seu saldo previsto para final do mês é R$ 3.780,00.

📱 Você: Tenho gastos suspeitos?
🤖 IA: Detectei uma transação de R$ 1.500,00 em "Outros" que está 300% acima da média.
       Verifique se está correta.
```

### **Dicas Financeiras:**
```
📱 Você: Como posso economizar?
🤖 IA: Analisando seus gastos, você pode economizar R$ 350,00/mês:
       • Alimentação fora: -R$ 200,00 (cozinhar mais em casa)
       • Assinaturas: -R$ 150,00 (cancelar serviços não usados)
```

## 🔒 Segurança:

- ✅ **Whitelist de números** (ALLOWED_SENDERS)
- ✅ **Autenticação por número de telefone** cadastrado
- ✅ **Token Bearer** para comunicação Flask ↔ Node.js
- ✅ **Apenas mensagens privadas** (grupos bloqueados)
- ✅ **Não processa mensagens próprias** (fromMe)
- ✅ **Validação de usuário** antes de responder
- ✅ **Logs detalhados** de todas as interações

## 📊 Diferenças do Pixzinho Bot Original:

| Recurso | Pixzinho Bot | BWS Finance IA |
|---------|--------------|----------------|
| **Integração** | WhatsApp apenas | WhatsApp + Web App |
| **IA** | GPT API | IA Própria + ML local |
| **Dados** | Limitado | Acesso completo ao banco |
| **Dashboard** | ❌ Não | ✅ Sim (web completo) |
| **Offline** | ❌ Não | ✅ PWA funciona offline |
| **Custo** | Requer OpenAI API | 100% Gratuito (local) |
| **Investimentos** | ❌ Básico | ✅ Cotações em tempo real |
| **Recorrentes** | ❌ Limitado | ✅ Scheduler automático |

## 🚀 Próximas Melhorias:

- [ ] Adicionar suporte a GPT-4 opcional
- [ ] Gráficos via WhatsApp (imagens)
- [ ] Notificações proativas (alertas automáticos)
- [ ] Comandos rápidos (/saldo, /gastos)
- [ ] Histórico de conversas na web
- [ ] Análise de voz mais avançada
- [ ] Integração com banco de dados vetorial

## 📝 Status:

✅ **FUNCIONANDO** - Sistema operacional e testado!

🌐 **Servidores:**
- Flask: http://0.0.0.0:5000 ✅
- WhatsApp: http://localhost:3000 ✅

📱 **WhatsApp:** Conectado e pronto para receber mensagens!
🤖 **IA:** Carregada e processando perguntas!

---

**Desenvolvido com 💙 para BWS Finance**
Inspirado no conceito do Pixzinho Bot, mas com IA 100% local e integrada! 🚀
