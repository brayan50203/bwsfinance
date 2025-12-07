#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste específico para CEMIG e outras ações que podem estar falhando
"""

import sys
sys.path.insert(0, '.')

from services.api_connectors import InvestmentAPIFactory, Investidor10Connector, BrapiConnector, YahooFinanceConnector

def test_cemig():
    """Testa especificamente CEMIG"""
    
    print("=" * 80)
    print("🧪 TESTE ESPECÍFICO - CEMIG")
    print("=" * 80)
    
    # Diferentes variações de CEMIG
    cemig_tickers = ['CMIG4', 'CMIG3', 'CEMIG4', 'CEMIG3']
    
    for ticker in cemig_tickers:
        print(f"\n{'='*60}")
        print(f"🔍 Testando: {ticker}")
        print(f"{'='*60}\n")
        
        # Testar com o sistema de fallback
        print("📊 Usando sistema de fallback completo:")
        data = InvestmentAPIFactory.get_stock_with_fundamentals(ticker)
        
        if data and data.get('price', 0) > 0:
            print(f"\n✅ SUCESSO via fallback!")
            print(f"   💰 Preço: R$ {data['price']:.2f}")
            print(f"   🏢 Nome: {data.get('name', 'N/A')}")
        else:
            print(f"\n❌ Falhou no sistema de fallback")
            
            # Testar cada fonte individualmente
            print(f"\n📋 Testando fontes individuais:\n")
            
            # Investidor10
            print("1️⃣ Investidor10:")
            inv10 = Investidor10Connector()
            inv10_data = inv10.get_stock_data(ticker)
            if inv10_data and inv10_data.get('price', 0) > 0:
                print(f"   ✅ R$ {inv10_data['price']:.2f}")
            else:
                print(f"   ❌ Falhou")
            
            # Brapi
            print("2️⃣ Brapi:")
            brapi = BrapiConnector()
            brapi_data = brapi.get_stock_data(ticker)
            if brapi_data and brapi_data.get('price', 0) > 0:
                print(f"   ✅ R$ {brapi_data['price']:.2f}")
            else:
                print(f"   ❌ Falhou")
            
            # Yahoo Finance
            print("3️⃣ Yahoo Finance:")
            yahoo = YahooFinanceConnector()
            yahoo_data = yahoo.get_stock_data(ticker)
            if yahoo_data and yahoo_data.get('price', 0) > 0:
                print(f"   ✅ R$ {yahoo_data['price']:.2f}")
            else:
                print(f"   ❌ Falhou")
    
    print("\n" + "=" * 80)
    print("✅ TESTE CONCLUÍDO")
    print("=" * 80)

if __name__ == '__main__':
    try:
        test_cemig()
    except KeyboardInterrupt:
        print("\n\n⚠️ Teste interrompido")
    except Exception as e:
        print(f"\n\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
