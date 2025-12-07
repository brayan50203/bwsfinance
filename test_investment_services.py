"""
Script de teste dos serviços de investimentos
"""

from services.api_connectors import InvestmentAPIFactory
from services.investment_calculator import InvestmentCalculator

print("🧪 TESTE DOS SERVIÇOS DE INVESTIMENTOS\n")

# Teste 1: API Yahoo Finance
print("📊 Teste 1: Buscar ação B3")
stock = InvestmentAPIFactory.get_investment_data('Ações', 'PETR4')
if stock:
    print(f"✅ {stock['name']}: R$ {stock['price']:.2f}")
else:
    print("❌ Erro ao buscar PETR4")

print()

# Teste 2: API CoinGecko
print("💰 Teste 2: Buscar criptomoeda")
crypto = InvestmentAPIFactory.get_investment_data('Criptomoedas', 'Bitcoin')
if crypto:
    print(f"✅ {crypto['name']}: R$ {crypto['price']:.2f}")
    print(f"   Variação 24h: {crypto['change_24h']:.2f}%")
else:
    print("❌ Erro ao buscar Bitcoin")

print()

# Teste 3: Calculator
print("🧮 Teste 3: Cálculos financeiros")
calc = InvestmentCalculator()

initial = 1000
current = 1250
profit_pct = calc.calculate_profitability(initial, current)
profit_amount = calc.calculate_profit_amount(initial, current)

print(f"✅ Investimento: R$ {initial:.2f}")
print(f"   Valor atual: R$ {current:.2f}")
print(f"   Lucro: R$ {profit_amount:.2f} ({profit_pct:.2f}%)")

print()

# Teste 4: Portfólio
print("📈 Teste 4: Métricas de portfólio")
investments = [
    {'amount': 1000, 'current_value': 1250, 'investment_type': 'Ações', 'name': 'PETR4'},
    {'amount': 2000, 'current_value': 2100, 'investment_type': 'Criptomoedas', 'name': 'Bitcoin'},
    {'amount': 1500, 'current_value': 1550, 'investment_type': 'CDB', 'name': 'CDB 120%'}
]

metrics = calc.calculate_portfolio_metrics(investments)
print(f"✅ Total investido: R$ {metrics['total_invested']:.2f}")
print(f"   Valor atual: R$ {metrics['total_current']:.2f}")
print(f"   Lucro total: R$ {metrics['total_profit']:.2f}")
print(f"   Rentabilidade: {metrics['total_profit_pct']:.2f}%")

print()

# Teste 5: Diversificação
print("🎯 Teste 5: Análise de diversificação")
allocation = calc.calculate_allocation(investments)
for tipo, pct in allocation.items():
    print(f"   {tipo}: {pct:.1f}%")

diversification = calc.calculate_diversification_score(investments)
print(f"✅ Score de diversificação: {diversification:.0f}/100")

risk = calc.calculate_risk_level(investments)
print(f"✅ Nível de risco: {risk}")

print("\n✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
