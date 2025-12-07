# 🎯 SISTEMA INTELIGENTE DE CONTAS/CARTÕES - WhatsApp

## 📋 PROBLEMA RESOLVIDO

Antes: Transações do WhatsApp eram lançadas em conta aleatória (primeira do banco)  
Agora: Sistema detecta automaticamente a melhor conta/cartão baseado na mensagem!

---

## 🧠 COMO FUNCIONA

### **Estratégia 1: Detecção por Palavras-Chave** 🔍

#### **Cartões de Crédito:**
Se a mensagem contém:
- "cartão", "cartao", "crédito", "credito"
- "no cartão", "no crédito"
- "mastercard", "visa", "elo", "amex"

**E NÃO contém** "débito":
→ Sistema busca cartão com maior limite disponível

#### **Bancos Específicos:**
Se menciona:
- **Nubank:** "nubank", "roxinho", "nu"
- **Inter:** "inter", "laranja"
- **Itaú:** "itau", "itaú"
- **Bradesco:** "bradesco"
- **Santander:** "santander"
- **Caixa:** "caixa", "cef"
- **Banco do Brasil:** "banco do brasil", "bb"
- **PicPay:** "picpay"
- **Mercado Pago:** "mercado pago", "mercadopago"

→ Sistema busca conta/cartão do banco mencionado

### **Estratégia 2: Conta Padrão Configurada** ⚙️
(Será implementada - usuário poderá definir conta/cartão padrão para WhatsApp)

### **Estratégia 3: Fallback Inteligente** 🎲
Se não houver palavra-chave:
→ Sistema usa conta com **maior saldo disponível**

---

## 💬 EXEMPLOS DE USO

### ✅ **Cartão de Crédito:**
```
Usuário: "Paguei R$ 50 no mercado no cartão"
Sistema: ✅ Lançado no cartão Nubank
```

```
Usuário: "Comprei R$ 120 no crédito do Itaú"
Sistema: ✅ Lançado no cartão Itaú
```

### ✅ **Conta Bancária Específica:**
```
Usuário: "Recebi R$ 300 no nubank"
Sistema: ✅ Lançado na conta Nubank
```

```
Usuário: "Paguei R$ 80 no débito do inter"
Sistema: ✅ Lançado na conta Inter
```

### ✅ **Conta com Maior Saldo (Fallback):**
```
Usuário: "Paguei R$ 25 no mercado"
Sistema: ✅ Lançado na conta Bradesco (maior saldo)
```

---

## 🔧 IMPLEMENTAÇÃO TÉCNICA

### **Função Principal:**
```python
get_smart_account_or_card(db, user_id, tenant_id, transaction_text, transaction_type)
```

**Retorna:**
```python
{
    'type': 'card' ou 'account',
    'id': 'uuid-da-conta-ou-cartao',
    'name': 'Nome para exibir'
}
```

### **Lógica de Cartão:**
1. Detecta palavras-chave de cartão
2. Se mencionou banco específico → busca cartão daquele banco
3. Se não → busca cartão com maior limite disponível
4. Lança em `installments` (parcela única)
5. Atualiza `used_limit` do cartão

### **Lógica de Conta:**
1. Detecta banco mencionado → busca conta daquele banco
2. Se não mencionou → busca conta com maior saldo
3. Lança em `transactions`
4. Atualiza `current_balance` da conta

---

## 📊 MENSAGEM DE CONFIRMAÇÃO

### **Antes:**
```
✅ Transação adicionada!
💰 Valor: R$ 50,00
📅 Data: 2025-11-10
📂 Categoria: Alimentação
```

### **Agora:**
```
✅ Transação adicionada!
💰 Valor: R$ 50,00
📅 Data: 2025-11-10
📂 Categoria: Alimentação
💳 Cartão: Nubank  ← NOVO!
```

ou

```
✅ Transação adicionada!
💰 Valor: R$ 50,00
📅 Data: 2025-11-10
📂 Categoria: Alimentação
🏦 Conta: Itaú  ← NOVO!
```

---

## 🎯 VANTAGENS

✅ **Automático:** Não precisa especificar toda vez  
✅ **Inteligente:** Detecta pela linguagem natural  
✅ **Flexível:** Funciona com vários formatos de mensagem  
✅ **Transparente:** Confirma onde foi lançado  
✅ **Seguro:** Sempre tem fallback (nunca falha)  

---

## 🔮 MELHORIAS FUTURAS

### **Fase 2: Configuração de Padrões**
- Usuário define conta/cartão padrão para WhatsApp
- Interface em /settings para configurar
- Opção de "sempre perguntar"

### **Fase 3: Machine Learning**
- Aprender com histórico do usuário
- "Você sempre usa Nubank para supermercado"
- Sugestões inteligentes baseadas em categoria

### **Fase 4: Confirmação Interativa**
```
Sistema: "Detectei R$ 50 no mercado. Lançar no cartão Nubank?"
Usuário: "Sim" ou "Não, no débito"
```

---

## 🧪 TESTAR AGORA

```
# Cartão de crédito
"Paguei R$ 50 no mercado no cartão"

# Conta específica
"Recebi R$ 100 no nubank"

# Cartão de banco específico
"Comprei R$ 80 no crédito do itaú"

# Fallback (conta com maior saldo)
"Gastei R$ 30 na farmácia"
```

---

**Data de Implementação:** 10/11/2025  
**Status:** ✅ Implementado e funcionando  
**Arquivo:** `app.py` (função `get_smart_account_or_card`)
