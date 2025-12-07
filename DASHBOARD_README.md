# 🚀 Dashboard Financeira BWS Finance

## 📋 Visão Geral

Dashboard financeira completa e interativa com gráficos em tempo real, indicadores inteligentes e visualização de dados financeiros.

## ✨ Funcionalidades

### 📊 Cards de Resumo
- 💰 **Renda Total** - Com variação percentual vs mês anterior
- 📉 **Custos Totais** - Tracking de despesas com tendências
- 💸 **Saldo Mensal** - Superávit/Déficit colorido
- 📈 **Investimentos** - Valor total da carteira

### 📈 Gráficos Interativos
1. **Pizza** - Distribuição de custos por categoria (top 10)
2. **Rosca** - Composição da carteira de investimentos (Renda Fixa, Ações, Cripto)
3. **Linha** - Evolução do saldo mensal (últimos 6 meses)
4. **Área** - Fluxo de caixa: Renda x Custos (dia a dia)
5. **Barras** - Rentabilidade por ativo (verde/vermelho)

### 🎯 KPIs Inteligentes
- 💵 **Taxa de Poupança** - (Saldo / Renda) × 100
  - Meta: > 20% (verde se atingida)
  
- 📊 **Taxa de Endividamento** - (Custos / Renda) × 100
  - Excelente: < 30% (verde)
  - Atenção: 30-50% (amarelo)
  - Crítico: > 50% (vermelho)
  
- 💹 **Rentabilidade Média** - Média das variações dos investimentos
  - Verde se positivo, cinza se negativo

### ⚡ Recursos Extras
- 🔄 **Auto-atualização** - Dados atualizados a cada 60 segundos
- 📱 **Responsivo** - Funciona perfeitamente em mobile
- 🎨 **Design Moderno** - TailwindCSS + gradientes suaves
- 🔔 **Estados de loading/erro** - Feedback visual completo

## 🛠️ Instalação

### Backend (Flask)
```bash
# Já está configurado! Endpoint criado em /api/dashboard
python app.py
```

### Frontend (React + Vite)
```bash
cd frontend

# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm run dev
```

## 🌐 URLs

- **Backend API**: http://localhost:5000/api/dashboard
- **Frontend Dev**: http://localhost:5173 (Vite)
- **Rota Dashboard**: http://localhost:5173/dashboard

## 📡 Estrutura da API

### GET /api/dashboard

Retorna JSON com:

```json
{
  "renda_total": 5200.00,
  "custos_total": 3400.00,
  "saldo": 1800.00,
  "renda_mes_anterior": 5000.00,
  "custos_mes_anterior": 3600.00,
  "investimentos": {
    "renda_fixa": 2000.00,
    "acoes": 1500.00,
    "criptomoedas": 1200.00
  },
  "categorias": {
    "Moradia": 1200.00,
    "Alimentação": 800.00,
    ...
  },
  "historico_saldo": [
    {"mes": "Jun", "valor": 1200},
    {"mes": "Jul", "valor": 1500},
    ...
  ],
  "fluxo_mensal": [
    {"dia": 1, "renda": 0, "custo": 50},
    {"dia": 5, "renda": 3000, "custo": 200},
    ...
  ],
  "variacao_investimentos": [
    {"nome": "Bitcoin", "variacao": 12.5},
    {"nome": "PETR4", "variacao": 3.2},
    ...
  ]
}
```

## 🎨 Tecnologias Utilizadas

### Frontend
- ⚛️ **React 18** - Framework UI
- 🎨 **TailwindCSS** - Styling
- 📊 **Recharts** - Biblioteca de gráficos
- 🎯 **Lucide React** - Ícones modernos
- 🚀 **Vite** - Build tool super rápido
- 🗺️ **React Router** - Navegação

### Backend
- 🐍 **Flask** - Framework web Python
- 💾 **SQLite** - Banco de dados
- 🔐 **Flask Sessions** - Autenticação
- 📅 **APScheduler** - Tarefas agendadas

## 📂 Estrutura de Arquivos

```
frontend/
├── src/
│   ├── pages/
│   │   ├── DashboardFinanceira.jsx ← Nova dashboard
│   │   ├── Contas_HomeStyle.jsx
│   │   └── ...
│   ├── App.jsx ← Rotas atualizadas
│   └── main.jsx
├── package.json ← Dependências adicionadas
└── ...

backend/
└── app.py ← Endpoint /api/dashboard criado
```

## 🔧 Customização

### Adicionar Novos Gráficos
Edite `DashboardFinanceira.jsx` e use os componentes do Recharts:
- `<LineChart>` - Gráficos de linha
- `<AreaChart>` - Gráficos de área
- `<BarChart>` - Gráficos de barras
- `<PieChart>` - Gráficos de pizza

### Modificar Cores
As cores estão definidas em:
```javascript
const COLORS = ['#8b5cf6', '#3b82f6', '#10b981', ...];
```

### Alterar Intervalo de Atualização
Por padrão é 60 segundos:
```javascript
const interval = setInterval(fetchData, 60000); // 60000ms = 60s
```

## 🐛 Troubleshooting

### Erro de CORS
Adicione no `app.py`:
```python
from flask_cors import CORS
CORS(app, supports_credentials=True)
```

### Gráficos não aparecem
Verifique se as dependências estão instaladas:
```bash
npm install recharts lucide-react
```

### Erro 401 (Unauthorized)
Faça login no sistema antes de acessar a dashboard.

## 📝 Notas

- Os dados são calculados **em tempo real** do banco de dados
- Transações devem estar com `status = 'Pago'` para aparecerem
- Investimentos devem estar `active` para contabilizar
- O histórico mostra os **últimos 6 meses**
- Fluxo de caixa mostra o **mês atual**

## 🎯 Próximos Passos

- [ ] Adicionar filtro de período (ano/mês)
- [ ] Exportar dashboard em PDF
- [ ] Comparação entre períodos
- [ ] Metas financeiras personalizadas
- [ ] Alertas e notificações
- [ ] Dark mode

## 📸 Preview

```
┌──────────────────────────────────────────────────────────┐
│  Dashboard Financeira                    [🔄 Atualizar]  │
├──────────────────────────────────────────────────────────┤
│  💰 Renda      📉 Custos     💸 Saldo      📈 Investim.  │
│  R$ 5.200      R$ 3.400      R$ 1.800      R$ 4.700      │
│  +4.0% ↑       +5.6% ↑       Superávit    Carteira       │
├──────────────────────────────────────────────────────────┤
│  📊 Custos            │  💼 Carteira                      │
│  [Gráfico Pizza]      │  [Gráfico Rosca]                 │
├──────────────────────────────────────────────────────────┤
│  📈 Evolução          │  💹 Rentabilidade                 │
│  [Gráfico Linha]      │  [Gráfico Barras]                │
├──────────────────────────────────────────────────────────┤
│  💵 Poupança: 22%  │  📊 Endividam.: 65%  │ 💹 Rent: +3% │
└──────────────────────────────────────────────────────────┘
```

---

**Desenvolvido para BWS Finance** 🚀
Versão: 1.0.0 | Data: Novembro 2025
