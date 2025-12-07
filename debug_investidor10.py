#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para debugar a estrutura do HTML do Investidor10
"""

import requests
from bs4 import BeautifulSoup

def debug_investidor10():
    """Debug da estrutura HTML"""
    ticker = 'PETR4'
    url = f"https://investidor10.com.br/acoes/{ticker.lower()}"
    
    print(f"🔍 Analisando estrutura de: {url}\n")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {response.status_code}\n")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Salvar HTML para análise
        with open('investidor10_debug.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        
        print("✅ HTML salvo em: investidor10_debug.html")
        
        # Buscar título/nome
        print("\n📋 BUSCANDO NOME DA EMPRESA:")
        titles = soup.find_all(['h1', 'h2', 'title'])
        for title in titles[:3]:
            print(f"   - {title.name}: {title.text.strip()[:100]}")
        
        # Buscar preço
        print("\n💰 BUSCANDO PREÇO:")
        # Tentar diferentes classes comuns
        price_classes = ['value', 'price', 'cotacao', '_card', 'ticker-price']
        for cls in price_classes:
            elements = soup.find_all(class_=lambda x: x and cls in x.lower())
            if elements:
                print(f"\n   Classe '{cls}':")
                for elem in elements[:5]:
                    print(f"      - {elem.get('class')}: {elem.text.strip()[:100]}")
        
        # Buscar spans com valores
        print("\n📊 SPANS COM NÚMEROS:")
        spans = soup.find_all('span')
        for span in spans[:20]:
            text = span.text.strip()
            if any(c.isdigit() for c in text) and len(text) < 30:
                print(f"   - Class: {span.get('class')} | Text: {text}")
        
        print("\n" + "="*60)
        print("✅ Análise concluída. Verifique investidor10_debug.html")

if __name__ == '__main__':
    debug_investidor10()
