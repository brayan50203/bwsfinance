#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste do sistema de fallback: Investidor10 → Brapi → Yahoo Finance
"""

import sys
sys.path.insert(0, '.')

from services.api_connectors import InvestmentAPIFactory

def test_fallback_system():
    """Testa o sistema de fallback com múltiplas fontes"""
    
    print("=" * 80)
    print("🔄 TESTE DO SISTEMA DE FALLBACK - 3 FONTES")
    print("=" * 80)
    print("\n📊 Prioridade: Investidor10 → Brapi → Yahoo Finance\n")
    
    # Testar diversas ações
    stocks = [
        'PETR4',  # Deve funcionar no Investidor10
        'VALE3',  # Deve funcionar no Investidor10
        'VALE5',  # Falha no Investidor10, deve tentar Brapi
        'ITUB4',  # Deve funcionar no Investidor10
        'MGLU3',  # Deve funcionar no Investidor10
        'ABCD4',  # Ação inexistente - deve falhar em todas
    ]
    
    results = {
        'success': [],
        'failed': [],
        'sources': {
            'Investidor10': 0,
            'Brapi': 0,
            'Yahoo Finance': 0
        }
    }
    
    for ticker in stocks:
        print(f"\n{'='*60}")
        print(f"🔍 Testando: {ticker}")
        print(f"{'='*60}\n")
        
        data = InvestmentAPIFactory.get_stock_with_fundamentals(ticker)
        
        if data and data.get('price', 0) > 0:
            results['success'].append(ticker)
            print(f"\n✅ SUCESSO: {ticker}")
            print(f"   💰 Preço: R$ {data['price']:.2f}")
            print(f"   🏢 Nome: {data.get('name', 'N/A')}")
            
            # Detectar fonte pela presença de dados fundamentalistas
            if data.get('dy', 0) > 0 or data.get('pl', 0) > 0:
                results['sources']['Investidor10'] += 1
            elif data.get('market_cap', 0) > 0:
                results['sources']['Brapi'] += 1
            else:
                results['sources']['Yahoo Finance'] += 1
        else:
            results['failed'].append(ticker)
            print(f"\n❌ FALHOU: {ticker}")
    
    # Resumo final
    print("\n" + "=" * 80)
    print("📊 RESUMO DO TESTE")
    print("=" * 80)
    
    print(f"\n✅ Sucessos ({len(results['success'])}):")
    for ticker in results['success']:
        print(f"   - {ticker}")
    
    print(f"\n❌ Falhas ({len(results['failed'])}):")
    for ticker in results['failed']:
        print(f"   - {ticker}")
    
    print(f"\n📈 DISTRIBUIÇÃO POR FONTE:")
    for source, count in results['sources'].items():
        if count > 0:
            print(f"   {source}: {count} ações")
    
    total = len(stocks)
    success_rate = len(results['success']) / total * 100
    
    print(f"\n🎯 TAXA DE SUCESSO: {len(results['success'])}/{total} ({success_rate:.1f}%)")
    
    print("\n" + "=" * 80)
    print("✅ TESTE CONCLUÍDO")
    print("=" * 80)

if __name__ == '__main__':
    try:
        test_fallback_system()
    except KeyboardInterrupt:
        print("\n\n⚠️ Teste interrompido")
    except Exception as e:
        print(f"\n\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
