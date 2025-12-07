"""
Teste de busca de SANEPR11
"""
from services.api_connectors import InvestmentAPIFactory

print("=" * 60)
print("🔍 TESTANDO BUSCA DE SANEPR11")
print("=" * 60)

ticker = "SANEPR11"

print(f"\n1️⃣ Tentando buscar {ticker} com fallbacks...")
data = InvestmentAPIFactory.get_stock_with_fundamentals(ticker)

if data:
    print(f"\n✅ SUCESSO! Dados encontrados:")
    print(f"   Símbolo: {data.get('symbol')}")
    print(f"   Nome: {data.get('name')}")
    print(f"   Preço: R$ {data.get('price', 0):.2f}")
    print(f"   Tipo: {data.get('asset_type', 'N/A')}")
    print(f"   Variação: {data.get('change_percent', 0):.2f}%")
else:
    print(f"\n❌ FALHOU! Nenhuma fonte conseguiu retornar dados para {ticker}")
    print("\nTentando buscar manualmente...")
    
    # Teste direto Yahoo Finance
    from services.api_connectors import YahooFinanceConnector
    yahoo = YahooFinanceConnector()
    
    variations = [
        "SANEPR11",
        "SANEPR11.SA",
        "SANEPR11B",
        "SANEPR11B.SA"
    ]
    
    for var in variations:
        print(f"\n   Testando: {var}")
        result = yahoo.get_stock_data(var.replace('.SA', ''))
        if result and result.get('price', 0) > 0:
            print(f"   ✅ ENCONTRADO! R$ {result['price']:.2f}")
            break
        else:
            print(f"   ❌ Não encontrado")

print("\n" + "=" * 60)
