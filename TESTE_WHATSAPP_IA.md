# 🧪 Guia de Teste - IA WhatsApp

## ✅ Status dos Servidores:

- 🟢 **Flask**: http://0.0.0.0:5000 ✅ Rodando
- 🟡 **WhatsApp**: http://localhost:3000 🔄 Carregando...

---

## 📋 Passo a Passo para Testar:

### **1️⃣ Cadastrar seu WhatsApp no Sistema**

1. Abra no navegador: http://192.168.80.122:5000/settings
2. Faça login (se necessário)
3. Vá na aba **"Perfil"**
4. No campo **"Telefone"**, digite: `5511949967277` (ou seu número)
5. Clique em **"Salvar"**

### **2️⃣ Conectar WhatsApp ao Sistema**

1. Aguarde o QR Code aparecer no terminal (pode levar 1-2 minutos)
2. Abra o WhatsApp no seu celular
3. Vá em **Menu → Aparelhos Conectados**
4. Clique em **"Conectar um aparelho"**
5. Escaneie o QR Code que apareceu no terminal
6. Aguarde a mensagem: ✅ **WhatsApp Connected!**

### **3️⃣ Testar o Sistema**

#### **Teste 1: Pergunta Simples**
```
📱 Envie para: (seu próprio número)
💬 Mensagem: Quanto gastei esse mês?
```
**Resultado esperado:** IA responde com análise dos gastos

#### **Teste 2: Consulta de Saldo**
```
📱 Envie: Qual meu saldo atual?
```
**Resultado esperado:** IA mostra saldo total e por conta

#### **Teste 3: Adicionar Transação**
```
📱 Envie: Paguei R$ 25 no Uber hoje
```
**Resultado esperado:** Confirmação de transação adicionada

#### **Teste 4: Análise de Categoria**
```
📱 Envie: Onde gastei mais dinheiro?
```
**Resultado esperado:** IA mostra categoria com maior gasto

#### **Teste 5: Investimentos**
```
📱 Envie: Como estão meus investimentos?
```
**Resultado esperado:** IA mostra resumo da carteira

---

## 🔍 Como Verificar se Funcionou:

### **Logs do Flask (Terminal 1)**
Você verá mensagens como:
```
[WEBHOOK] Mensagem recebida de 5511949967277@c.us
[AI MODE] Pergunta detectada: Quanto gastei esse mês?
[AI MODE] Usuário encontrado: ID 1
[AI MODE] Resposta enviada com sucesso
```

### **Logs do WhatsApp (Terminal 2)**
Você verá:
```
📨 Mensagem recebida de 5511949967277@c.us
✅ Mensagem enviada para Flask webhook
✅ Resposta enviada pelo bot
```

### **No WhatsApp**
Você receberá uma mensagem do bot com a resposta da IA

---

## ❌ Possíveis Erros:

### **Erro: "Número não cadastrado"**
- **Causa:** Seu telefone não está no banco de dados
- **Solução:** Vá em `/settings` e adicione o telefone

### **Erro: "WhatsApp not connected"**
- **Causa:** WhatsApp não foi conectado via QR Code
- **Solução:** Escaneie o QR Code novamente

### **Erro: Sem resposta**
- **Causa:** Número não está na whitelist
- **Solução:** Edite `.env` e adicione seu número em `ALLOWED_SENDERS`

### **Erro: "Erro ao processar mensagem"**
- **Causa:** Problema na classificação ou IA
- **Solução:** Verifique logs do Flask para mais detalhes

---

## 📊 Exemplos de Perguntas que a IA Entende:

### **💰 Finanças Gerais**
- "Quanto gastei esse mês?"
- "Qual meu saldo?"
- "Quanto recebi de salário?"
- "Qual minha situação financeira?"

### **📈 Análises**
- "Onde gastei mais?"
- "Qual categoria tem mais gastos?"
- "Gastei mais que o mês passado?"
- "Qual minha previsão de saldo?"

### **💼 Investimentos**
- "Como estão meus investimentos?"
- "Quanto rendeu minha carteira?"
- "Qual minha rentabilidade?"

### **🔍 Padrões**
- "Tenho gastos suspeitos?"
- "Como é meu padrão de gastos?"
- "Onde posso economizar?"

### **💸 Adicionar Transações**
- "Paguei R$ 50 no mercado"
- "Recebi R$ 100 de freelance"
- "Gastei 30 reais na farmácia hoje"

---

## 🎯 Próximos Passos:

1. ✅ **Cadastre seu telefone** em `/settings`
2. ✅ **Conecte o WhatsApp** via QR Code
3. ✅ **Teste perguntas** básicas primeiro
4. ✅ **Teste transações** depois
5. ✅ **Explore análises** avançadas

---

## 🆘 Precisa de Ajuda?

Se encontrar problemas:
1. Verifique os logs do Flask (Terminal 1)
2. Verifique os logs do WhatsApp (Terminal 2)
3. Confirme que ambos servidores estão rodando
4. Verifique se o telefone está cadastrado corretamente
5. Teste com mensagens simples primeiro

---

**🚀 Boa sorte com os testes!**
