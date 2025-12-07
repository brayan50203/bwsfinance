# 🔧 INSTRUÇÕES PARA TESTAR PÁGINA DE RECORRENTES

## 📋 PROBLEMA ATUAL
- Contas e cartões não aparecem nos selects da página /recurring
- Categorias não estão carregando

## ✅ SOLUÇÃO APLICADA

### Correções no JavaScript (recurring.html):

1. **loadAccounts()** - Agora aceita tanto array direto quanto objeto com `success`
2. **loadCards()** - Corrigido para usar resposta da API `/api/cards`
3. **loadCategories()** - Adaptado para múltiplos formatos de resposta
4. **Logs adicionados** - Console.log para debug

### APIs criadas (app.py):

1. **GET /api/cards** - Retorna cartões do usuário logado
2. **GET /api/categories** - Retorna categorias do tenant

---

## 🧪 COMO TESTAR

### 1. **Acesse a página:**
```
http://192.168.80.122:5000/recurring
```

### 2. **Abra o Console do Navegador (F12)**
- Chrome/Edge: F12 → Console
- Procure por mensagens:
  - ✅ Contas carregadas: X
  - ✅ Cartões carregados: X  
  - ✅ Categorias carregadas: X

### 3. **Clique em "Nova Transação Recorrente"**
Deve aparecer modal com:
- ✅ Select de Contas (com nomes e saldos)
- ✅ Select de Cartões (se escolher tipo "Cartão")
- ✅ Select de Categorias (após escolher Receita/Despesa)

### 4. **Verificar erros**
Se aparecer erro no console:
- ❌ 401 Unauthorized = Não está logado
- ❌ 404 Not Found = Rota não existe
- ❌ TypeError = Problema no JavaScript

---

## 🐛 SE AINDA NÃO FUNCIONAR

### Teste as APIs manualmente:

**1. Abra Console do navegador (F12) e execute:**

```javascript
// Testar Contas
fetch('/api/accounts')
  .then(r => r.json())
  .then(d => console.log('Contas:', d));

// Testar Cartões  
fetch('/api/cards')
  .then(r => r.json())
  .then(d => console.log('Cartões:', d));

// Testar Categorias
fetch('/api/categories')
  .then(r => r.json())
  .then(d => console.log('Categorias:', d));
```

**2. Se retornar 401 (Unauthorized):**
- Faça login primeiro em: http://192.168.80.122:5000/login
- Email: brayanbarbosa84@gmail.com
- Senha: [sua senha]

**3. Se retornar 404:**
- Servidor não tem a rota
- Confirmar que app.py foi salvo com as novas rotas
- Reiniciar servidor: `.\start-server.ps1`

---

## 📊 DADOS NO BANCO

Confirmado que existem:
- ✅ 17 contas
- ✅ 2 cartões (Itau, itau)
- ✅ 17 categorias (11 despesas + 6 receitas)

---

## 🔄 FLUXO CORRETO

1. Usuário faz login → Session criada
2. Acessa /recurring → Página carrega
3. JavaScript executa:
   - loadAccounts() → GET /api/accounts → Preenche select
   - loadCards() → GET /api/cards → Preenche select  
   - loadCategories() → GET /api/categories → Guarda array
4. Usuário clica "Nova Transação"
5. Modal abre com selects preenchidos
6. Escolhe tipo (Receita/Despesa) → updateCategoryOptions() filtra categorias

---

## ✅ CHECKLIST FINAL

- [ ] Servidor Flask rodando (http://192.168.80.122:5000)
- [ ] Usuário logado na aplicação
- [ ] Console do navegador aberto (F12)
- [ ] Acessar /recurring
- [ ] Ver logs de carregamento no console
- [ ] Clicar em "Nova Transação"
- [ ] Verificar se selects estão populados

---

**Última atualização:** 09/11/2025 - Correções aplicadas no recurring.html e app.py
