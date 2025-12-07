#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste rápido do sistema de fallback SEM BRAPI
"""

import sys
sys.path.insert(0, '.')

from services.api_connectors import InvestmentAPIFactory

def test_without_brapi():
    """Testa o sistema sem Brapi"""
    
    print("=" * 80)
    print("🧪 TESTE SISTEMA SEM BRAPI")
    print("=" * 80)
    print("\n📊 Ordem de fallback: Investidor10 → Status Invest → Yahoo Finance\n")
    
    # Testar ações populares
    stocks = ['PETR4', 'VALE3', 'ITUB4', 'CMIG4', 'MGLU3']
    
    success = 0
    failed = 0
    
    for ticker in stocks:
        print(f"\n{'='*60}")
        print(f"🔍 Testando: {ticker}")
        print(f"{'='*60}\n")
        
        data = InvestmentAPIFactory.get_stock_with_fundamentals(ticker)
        
        if data and data.get('price', 0) > 0:
            success += 1
            print(f"\n✅ {ticker}: R$ {data['price']:.2f}")
        else:
            failed += 1
            print(f"\n❌ {ticker}: FALHOU")
    
    # Resumo
    print("\n" + "=" * 80)
    print("📊 RESUMO")
    print("=" * 80)
    print(f"\n✅ Sucesso: {success}/{len(stocks)} ({success/len(stocks)*100:.1f}%)")
    print(f"❌ Falhas: {failed}/{len(stocks)}")
    print(f"\n💡 Brapi: DESATIVADA (401 Unauthorized)")
    print(f"✅ Sistema funcionando apenas com:")
    print(f"   1️⃣ Investidor10 (primário)")
    print(f"   2️⃣ Status Invest (secundário)")
    print(f"   3️⃣ Yahoo Finance (terciário)")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    try:
        test_without_brapi()
    except KeyboardInterrupt:
        print("\n\n⚠️ Teste interrompido")
    except Exception as e:
        print(f"\n\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
