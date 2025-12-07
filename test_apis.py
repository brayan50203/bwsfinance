"""
Testar APIs de contas, cartões e categorias
"""
import requests
import json

BASE_URL = "http://localhost:5000"

# ID do usuário logado (Brayan)
USER_ID = "33756b13-8daf-4972-a180-aa9e3818701a"

print("🧪 Testando APIs...\n")

# 1. Contas
print("📊 1. Testando /api/accounts")
try:
    response = requests.get(f"{BASE_URL}/api/accounts", params={"user_id": USER_ID})
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Contas: {len(data.get('accounts', []))}")
        for acc in data.get('accounts', [])[:3]:
            print(f"      - {acc['name']}")
    else:
        print(f"   ❌ Erro: {response.text}")
except Exception as e:
    print(f"   ❌ Exceção: {e}")

print()

# 2. Cartões
print("💳 2. Testando /api/cards")
try:
    response = requests.get(f"{BASE_URL}/api/cards", params={"user_id": USER_ID})
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Cartões: {len(data.get('cards', []))}")
        for card in data.get('cards', []):
            print(f"      - {card['name']}")
    else:
        print(f"   ❌ Erro: {response.text}")
except Exception as e:
    print(f"   ❌ Exceção: {e}")

print()

# 3. Categorias
print("📂 3. Testando /api/categories")
try:
    response = requests.get(f"{BASE_URL}/api/categories", params={"user_id": USER_ID})
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Categorias: {len(data.get('categories', []))}")
        receitas = [c for c in data.get('categories', []) if c['type'] == 'Receita']
        despesas = [c for c in data.get('categories', []) if c['type'] == 'Despesa']
        print(f"      - Receitas: {len(receitas)}")
        print(f"      - Despesas: {len(despesas)}")
    else:
        print(f"   ❌ Erro: {response.text}")
except Exception as e:
    print(f"   ❌ Exceção: {e}")
