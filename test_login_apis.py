"""
Simular login e testar APIs como navegador
"""
import requests
import json

BASE_URL = "http://localhost:5000"

# Criar sessão (simula navegador)
session = requests.Session()

print("🔐 1. Fazendo login...")
login_data = {
    "email": "brayanbarbosa84@gmail.com",
    "password": "senha123"  # Ajuste se necessário
}

response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
print(f"   Status: {response.status_code}")

if response.status_code in [200, 302]:
    print("   ✅ Login OK!")
    
    # Testar APIs
    print("\n📊 2. Testando /api/accounts")
    response = session.get(f"{BASE_URL}/api/accounts")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Tipo de resposta: {type(data)}")
        if isinstance(data, list):
            print(f"   ✅ Array com {len(data)} contas")
            if len(data) > 0:
                print(f"   Exemplo: {data[0].get('name', 'N/A')}")
        elif isinstance(data, dict):
            print(f"   Chaves: {data.keys()}")
    else:
        print(f"   ❌ Erro: {response.text[:200]}")
    
    print("\n💳 3. Testando /api/cards")
    response = session.get(f"{BASE_URL}/api/cards")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Tipo de resposta: {type(data)}")
        if isinstance(data, dict) and 'cards' in data:
            print(f"   ✅ {len(data['cards'])} cartões")
            if len(data['cards']) > 0:
                print(f"   Exemplo: {data['cards'][0].get('name', 'N/A')}")
        elif isinstance(data, list):
            print(f"   ✅ Array com {len(data)} cartões")
    else:
        print(f"   ❌ Erro: {response.text[:200]}")
    
    print("\n📂 4. Testando /api/categories")
    response = session.get(f"{BASE_URL}/api/categories")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Tipo de resposta: {type(data)}")
        if isinstance(data, dict) and 'categories' in data:
            print(f"   ✅ {len(data['categories'])} categorias")
        elif isinstance(data, list):
            print(f"   ✅ Array com {len(data)} categorias")
    else:
        print(f"   ❌ Erro: {response.text[:200]}")
    
else:
    print(f"   ❌ Login falhou! Status: {response.status_code}")
    print(f"   Resposta: {response.text[:200]}")
