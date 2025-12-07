#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste de múltiplas ações para verificar quais funcionam
"""

import sys
sys.path.insert(0, '.')

from services.api_connectors import Investidor10Connector, YahooFinanceConnector, InvestmentAPIFactory

def test_multiple_stocks():
    """Testa diversas ações populares"""
    
    # Lista expandida de ações populares B3
    stocks = [
        # Bancos
        'ITUB4', 'BBDC4', 'BBAS3', 'SANB11',
        # Petróleo e Energia
        'PETR4', 'PETR3', 'ELET3', 'ELET6',
        # Mineração
        'VALE3', 'VALE5',
        # Varejo
        'MGLU3', 'LREN3', 'AMER3', 'VVAR3',
        # Indústria
        'WEGE3', 'EMBR3', 'KLBN11',
        # Telecom
        'VIVT3', 'TIMS3',
        # Alimentos
        'JBSS3', 'BEEF3', 'BRFS3',
        # Outras
        'SUZB3', 'RENT3', 'RADL3', 'HAPV3'
    ]
    
    print("=" * 80)
    print("🧪 TESTE DE MÚLTIPLAS AÇÕES - INVESTIDOR10 vs YAHOO FINANCE")
    print("=" * 80)
    
    inv10 = Investidor10Connector()
    yahoo = YahooFinanceConnector()
    
    results = {
        'inv10_success': [],
        'inv10_failed': [],
        'yahoo_success': [],
        'yahoo_failed': [],
        'both_success': [],
        'both_failed': []
    }
    
    for ticker in stocks:
        print(f"\n{'='*60}")
        print(f"🔍 Testando: {ticker}")
        print(f"{'='*60}")
        
        # Testar Investidor10
        inv10_data = inv10.get_stock_data(ticker)
        inv10_ok = inv10_data and inv10_data.get('price', 0) > 0
        
        # Testar Yahoo Finance
        yahoo_data = yahoo.get_stock_data(ticker)
        yahoo_ok = yahoo_data and yahoo_data.get('price', 0) > 0
        
        # Categorizar resultados
        if inv10_ok and yahoo_ok:
            results['both_success'].append(ticker)
            print(f"✅✅ AMBOS FUNCIONARAM")
            print(f"   Investidor10: R$ {inv10_data['price']:.2f}")
            print(f"   Yahoo Finance: R$ {yahoo_data['price']:.2f}")
        elif inv10_ok:
            results['inv10_success'].append(ticker)
            print(f"✅❌ SÓ INVESTIDOR10")
            print(f"   Investidor10: R$ {inv10_data['price']:.2f}")
        elif yahoo_ok:
            results['yahoo_success'].append(ticker)
            print(f"❌✅ SÓ YAHOO FINANCE")
            print(f"   Yahoo Finance: R$ {yahoo_data['price']:.2f}")
        else:
            results['both_failed'].append(ticker)
            print(f"❌❌ AMBOS FALHARAM")
    
    # Resumo final
    print("\n" + "=" * 80)
    print("📊 RESUMO DOS TESTES")
    print("=" * 80)
    
    print(f"\n✅✅ Funcionam em AMBAS ({len(results['both_success'])}):")
    for ticker in results['both_success']:
        print(f"   - {ticker}")
    
    print(f"\n✅❌ Apenas INVESTIDOR10 ({len(results['inv10_success'])}):")
    for ticker in results['inv10_success']:
        print(f"   - {ticker}")
    
    print(f"\n❌✅ Apenas YAHOO FINANCE ({len(results['yahoo_success'])}):")
    for ticker in results['yahoo_success']:
        print(f"   - {ticker}")
    
    print(f"\n❌❌ FALHARAM em ambas ({len(results['both_failed'])}):")
    for ticker in results['both_failed']:
        print(f"   - {ticker}")
    
    # Estatísticas
    total = len(stocks)
    inv10_total = len(results['both_success']) + len(results['inv10_success'])
    yahoo_total = len(results['both_success']) + len(results['yahoo_success'])
    
    print(f"\n📈 ESTATÍSTICAS:")
    print(f"   Total testado: {total}")
    print(f"   Investidor10: {inv10_total}/{total} ({inv10_total/total*100:.1f}%)")
    print(f"   Yahoo Finance: {yahoo_total}/{total} ({yahoo_total/total*100:.1f}%)")
    print(f"   Cobertura total: {total - len(results['both_failed'])}/{total} ({(total - len(results['both_failed']))/total*100:.1f}%)")
    
    print("\n" + "=" * 80)
    print("✅ TESTE CONCLUÍDO")
    print("=" * 80)

if __name__ == '__main__':
    try:
        test_multiple_stocks()
    except KeyboardInterrupt:
        print("\n\n⚠️ Teste interrompido")
    except Exception as e:
        print(f"\n\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
