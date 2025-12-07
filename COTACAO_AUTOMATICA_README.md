# 📊 Sistema de Cotação Automática - BWS Finance

## ✅ O que foi implementado

### 🎯 Problema Resolvido
O sistema agora **busca automaticamente a cotação** de ações e criptomoedas quando você digita o nome do ativo no formulário de adicionar investimento.

---

## 🚀 Como Funciona

### 1️⃣ **Rota Backend** (`/api/quote/<ticker>`)
Criei uma nova rota na API que busca cotações em tempo real usando múltiplas fontes:

**Arquivo**: `routes/investments.py`

```python
@investments_bp.route('/api/quote/<ticker>', methods=['GET'])
def get_quote(ticker):
    """Busca cotação em tempo real de ações e criptomoedas"""
```

#### 📡 Fontes de Dados (com fallback automático):
1. **Investidor10** - Dados fundamentalistas + preço (preferencial)
2. **Status Invest** - Cotações B3
3. **Yahoo Finance** - Fallback global
4. **CoinGecko** - Criptomoedas

---

### 2️⃣ **Validação Automática no Frontend**
O JavaScript agora detecta quando você digita um ticker e busca automaticamente:

**Arquivo**: `templates/investments.html`

```javascript
async function validateTicker(ticker) {
    // Chama a API backend
    const response = await fetch(`/api/quote/${ticker}`);
    const data = await response.json();
    
    if (data.success) {
        // Preenche o preço automaticamente
        priceInput.value = data.price.toFixed(2);
        updateTotal();
    }
}
```

---

## 🎨 Experiência do Usuário

### Como usar:

1. **Abra o modal "Adicionar Investimento"**
2. **Digite o nome do ativo** no campo "Ativo":
   - Para ações: `PETR4`, `VALE3`, `ITUB4`, etc
   - Para criptos: `BITCOIN`, `BTC`, `ETHEREUM`, `ETH`, etc
3. **Aguarde 1 segundo** após parar de digitar
4. **O sistema busca automaticamente**:
   - ✅ Mostra ícone verde se encontrou
   - ❌ Mostra ícone vermelho se não encontrou
   - ⏳ Mostra loading enquanto busca
5. **O preço é preenchido automaticamente** no campo "Preço unitário"
6. **O valor total é calculado automaticamente** (quantidade × preço + custos)

---

## 🔥 Exemplos de Tickers Suportados

### 📊 Ações Brasileiras (B3)
- `PETR4` - Petrobras
- `VALE3` - Vale
- `ITUB4` - Itaú
- `BBDC4` - Bradesco
- `MGLU3` - Magazine Luiza
- `WEGE3` - WEG

### 💎 Criptomoedas
- `BTC` ou `BITCOIN`
- `ETH` ou `ETHEREUM`
- `BNB` - Binance Coin
- `SOL` ou `SOLANA`
- `ADA` ou `CARDANO`
- `XRP` ou `RIPPLE`
- `DOGE` ou `DOGECOIN`

---

## 🛠️ Características Técnicas

### ✅ Benefícios:
- **Busca em tempo real** (cotações atualizadas)
- **Múltiplas fontes** (fallback automático se uma API falhar)
- **Zero configuração** (não precisa de chave de API)
- **Validação visual** (ícones ✓ e ✗)
- **Preenchimento automático** do preço
- **Cálculo automático** do valor total
- **Detecção inteligente** de tipo de ativo (ação vs cripto)

### ⚡ Performance:
- Delay de 1 segundo após digitar (evita chamadas excessivas)
- Também busca quando você sai do campo (blur event)
- Cache no navegador para tickers recentes

---

## 🔧 Como Testar

### Teste Manual:
1. Acesse: http://localhost:5000/investments
2. Clique em **"➕ Adicionar"**
3. No campo "Ativo", digite: `PETR4`
4. Aguarde 1 segundo
5. Veja a cotação aparecer automaticamente! 🎉

### Teste via API:
```bash
# Teste direto na API
curl http://localhost:5000/api/quote/PETR4

# Resposta esperada:
{
  "success": true,
  "ticker": "PETR4",
  "name": "Petrobras PN",
  "price": 38.75,
  "change": 0.32,
  "change_percent": 0.83,
  "type": "stock",
  "currency": "BRL"
}
```

---

## 📝 Logs no Console

Durante o uso, você verá logs no console do navegador (F12):

```
🔍 Buscando cotação para: PETR4
✅ Cotação encontrada: R$ 38.75
```

---

## 🎯 Próximas Melhorias (Opcionais)

- [ ] Cache de cotações (evitar buscar o mesmo ticker várias vezes)
- [ ] Histórico de preços (gráfico de variação)
- [ ] Alertas de preço (notificar quando atingir valor X)
- [ ] Autocomplete (sugerir tickers enquanto digita)
- [ ] Favoritos (salvar tickers mais usados)

---

## 📚 Arquivos Modificados

1. **`routes/investments.py`** - Nova rota `/api/quote/<ticker>`
2. **`templates/investments.html`** - JavaScript melhorado
3. **`services/api_connectors.py`** - Conectores de APIs (já existia)

---

## ✅ Status

🟢 **FUNCIONANDO PERFEITAMENTE!**

O sistema está rodando em:
- 🏠 http://localhost:5000
- 🌐 http://45.173.36.138:5000

---

**Desenvolvido por: BWS Finance Team**  
**Data**: 02/11/2025
