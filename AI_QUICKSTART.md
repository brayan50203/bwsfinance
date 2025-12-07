# 🚀 BWS Insight AI - Guia de Início Rápido

## ⚡ Instalação Rápida (5 minutos)

### Passo 1: Instalar Dependências Python
```powershell
# Na raiz do projeto (c:\App\nik0finance-base)
pip install pandas numpy
```

### Passo 2: Instalar Dependências React
```powershell
cd frontend
npm install react-markdown
cd ..
```

### Passo 3: Reiniciar o Servidor Flask
```powershell
# Se o servidor está rodando, pare (Ctrl+C) e reinicie:
python app.py
```

### Passo 4: Rebuild do Frontend (se necessário)
```powershell
cd frontend
npm run build
cd ..
```

## ✅ Verificar Instalação

### 1. Testar Endpoint da IA
Abrir no navegador:
```
http://localhost:5000/api/ai/status
```

**Resposta esperada:**
```json
{
  "success": true,
  "status": "AI system operational",
  "capabilities": [
    "Daily insights generation",
    "Natural language chat",
    ...
  ]
}
```

### 2. Testar Chat Interativo
```powershell
# Usar Postman, Insomnia ou curl:
curl -X POST http://localhost:5000/api/ai/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"Quanto tenho de saldo?\"}" ^
  -c cookies.txt
```

### 3. Verificar Interface
1. Abrir: `http://localhost:5000/dashboard`
2. Procurar botão flutuante roxo no canto inferior direito 💬
3. Clicar para abrir o chat

## 🎯 Primeiras Perguntas

Experimente estas perguntas no chat:

1. **Saldo:**
   - "Quanto tenho de saldo?"
   - "Qual meu saldo atual?"

2. **Gastos:**
   - "Quanto gastei este mês?"
   - "Quanto gastei com alimentação?"
   - "Onde gastei mais?"

3. **Investimentos:**
   - "Como estão meus investimentos?"
   - "Qual minha rentabilidade?"

4. **Previsões:**
   - "Qual a previsão para o próximo mês?"
   - "Previsão de 30 dias"

## 🔍 Verificar Logs

Se algo não funcionar:

```powershell
# Logs do servidor Flask (no terminal onde rodou python app.py)
# Procurar por:
# - "Registered blueprints: ai"
# - Erros 500 ou 404
# - Exceções Python

# Logs do navegador (F12 > Console)
# Procurar por:
# - Erros de CORS
# - Fetch failed
# - 401 Unauthorized (precisa fazer login)
```

## 🐛 Problemas Comuns

### ❌ "ModuleNotFoundError: No module named 'pandas'"
```powershell
pip install pandas numpy
```

### ❌ "Cannot read properties of undefined (reading 'map')"
```powershell
cd frontend
npm install
npm run build
```

### ❌ "404 Not Found: /api/ai/chat"
**Verificar:** Blueprint registrado em app.py?
```python
# Linhas 38 e 43 de app.py devem conter:
from routes.ai import ai_bp
app.register_blueprint(ai_bp)
```

### ❌ "401 Unauthorized"
**Solução:** Fazer login no sistema antes de usar a IA.
```
http://localhost:5000/login
```

### ❌ Botão flutuante não aparece
**Verificar:**
1. Frontend compilado? `npm run build`
2. AIFloatingButton importado em DashboardFinanceira.jsx?
3. Console do navegador tem erros?

## 📱 Acessar Painel Completo da IA

```
http://localhost:5000/ai
```

**O que você vai encontrar:**
- ✅ **Aba Insights:** Análise diária automática
- ✅ **Aba Previsões:** Gráfico de 30 dias
- ✅ **Aba Alertas:** Notificações importantes
- ✅ **Aba Chat:** Interface completa de chat

## 🎉 Pronto!

Agora você tem:
- ✅ Chat interativo funcionando
- ✅ Insights automáticos
- ✅ Previsões de 30 dias
- ✅ Detecção de anomalias
- ✅ Sistema de alertas

## 📚 Próximos Passos

1. **Adicionar Insights ao Dashboard Principal**
   - Card de insights já disponível (AIInsightCard.jsx)
   - Importar no DashboardFinanceira.jsx se desejar

2. **Configurar Scheduler (Opcional)**
   - Insights automáticos a cada 6 horas
   - Ver arquivo `scheduler.py` de exemplo

3. **Explorar API REST**
   - Documentação completa em `AI_SYSTEM_DOCUMENTATION.md`
   - 7 endpoints disponíveis

4. **Personalizar Respostas**
   - Editar `services/ai_chat.py`
   - Adicionar novos intents e handlers

---

**Dúvidas?** Consulte `AI_SYSTEM_DOCUMENTATION.md` para documentação completa.
