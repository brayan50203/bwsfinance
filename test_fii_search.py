import sys
sys.path.append('.')

from services.api_connectors import InvestmentAPIFactory

# Testar busca de FIIs
fiis = ['HGLG11', 'MXRF11', 'KNCR11', 'VISC11']

print("=== TESTANDO BUSCA DE FIIs ===\n")

api_factory = InvestmentAPIFactory()

for fii in fiis:
    print(f"\n{'='*60}")
    print(f"Testando: {fii}")
    print('='*60)
    
    result = api_factory.get_stock_with_fundamentals(fii)
    
    if result and result.get('price'):
        print(f"✅ SUCESSO!")
        print(f"   Preço: R$ {result['price']:.2f}")
        print(f"   DY: {result.get('dy', 0):.2f}%")
        print(f"   P/VP: {result.get('pvp', 0):.2f}")
    else:
        print(f"❌ FALHOU - Não foi possível buscar dados")

print("\n" + "="*60)
print("Teste concluído!")
