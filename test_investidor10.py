#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de teste para Investidor10 API Connector
"""

import sys
sys.path.insert(0, '.')

from services.api_connectors import Investidor10Connector, InvestmentAPIFactory

def test_investidor10():
    """Testa o conector do Investidor10"""
    print("=" * 80)
    print("🧪 TESTE DO CONECTOR INVESTIDOR10")
    print("=" * 80)
    
    # Ações para testar
    stocks = [
        'PETR4',
        'VALE3',
        'ITUB4',
        'BBDC4',
        'MGLU3',
        'WEGE3',
    ]
    
    connector = Investidor10Connector()
    
    print("\n📊 TESTANDO AÇÕES INDIVIDUAIS\n")
    
    for ticker in stocks:
        print(f"\n{'='*60}")
        print(f"🔍 Testando: {ticker}")
        print(f"{'='*60}")
        
        data = connector.get_stock_data(ticker)
        
        if data:
            print(f"\n✅ SUCESSO - {data.get('name', ticker)}")
            print(f"   💰 Preço: R$ {data.get('price', 0):.2f}")
            print(f"   📈 Variação: {data.get('change_percent', 0):+.2f}%")
            print(f"   💎 Dividend Yield: {data.get('dy', 0):.2f}%")
            print(f"   📊 P/L: {data.get('pl', 0):.2f}")
            print(f"   📈 P/VP: {data.get('pvp', 0):.2f}")
            print(f"   💪 ROE: {data.get('roe', 0):.2f}%")
            print(f"   🎯 ROIC: {data.get('roic', 0):.2f}%")
            print(f"   💧 Liquidez Corrente: {data.get('liq_corrente', 0):.2f}")
            print(f"   💳 Dív.Líq/EBITDA: {data.get('divida_liquida_ebitda', 0):.2f}")
            print(f"   📊 Margem Líquida: {data.get('margem_liquida', 0):.2f}%")
        else:
            print(f"\n❌ FALHOU - Não foi possível buscar dados de {ticker}")
    
    print("\n" + "=" * 80)
    print("🏭 TESTANDO VIA FACTORY (get_stock_with_fundamentals)")
    print("=" * 80)
    
    test_ticker = 'PETR4'
    print(f"\n🔍 Buscando {test_ticker} via Factory...")
    
    factory_data = InvestmentAPIFactory.get_stock_with_fundamentals(test_ticker)
    
    if factory_data:
        print(f"\n✅ FACTORY FUNCIONOU!")
        print(f"   Fonte: {'Investidor10' if factory_data.get('dy') else 'Yahoo Finance'}")
        print(f"   💰 Preço: R$ {factory_data.get('price', 0):.2f}")
        
        if factory_data.get('dy'):
            print(f"   💎 DY: {factory_data['dy']:.2f}%")
            print(f"   📊 P/L: {factory_data.get('pl', 0):.2f}")
            print(f"   💪 ROE: {factory_data.get('roe', 0):.2f}%")
    else:
        print(f"\n❌ Factory falhou para {test_ticker}")
    
    print("\n" + "=" * 80)
    print("✅ TESTE CONCLUÍDO")
    print("=" * 80)


if __name__ == '__main__':
    try:
        test_investidor10()
    except KeyboardInterrupt:
        print("\n\n⚠️ Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
