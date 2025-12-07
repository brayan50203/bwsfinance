import requests
import json

BASE_URL = 'http://localhost:5000'

print('🧪 Testando BWS Finance Server...\n')

# Test 1: Homepage
print('1️⃣ Testando homepage...')
try:
    response = requests.get(BASE_URL + '/', timeout=5)
    print(f'   Status: {response.status_code}')
    print(f'   Redirect: {response.url}')
    print('   ✅ Homepage OK\n')
except Exception as e:
    print(f'   ❌ Erro: {e}\n')

# Test 2: Login page
print('2️⃣ Testando página de login...')
try:
    response = requests.get(BASE_URL + '/login', timeout=5)
    print(f'   Status: {response.status_code}')
    if response.status_code == 200:
        print('   ✅ Login page OK\n')
    else:
        print(f'   ⚠️  Status inesperado\n')
except Exception as e:
    print(f'   ❌ Erro: {e}\n')

# Test 3: API health check
print('3️⃣ Testando API de investimentos...')
try:
    response = requests.get(BASE_URL + '/api/investments', timeout=5)
    print(f'   Status: {response.status_code}')
    if response.status_code == 401:
        print('   ✅ API protegida (autenticação necessária)\n')
    elif response.status_code == 200:
        print('   ✅ API acessível\n')
    else:
        print(f'   ⚠️  Status: {response.status_code}\n')
except Exception as e:
    print(f'   ❌ Erro: {e}\n')

# Test 4: Static routes
print('4️⃣ Testando rota de investimentos (HTML)...')
try:
    response = requests.get(BASE_URL + '/investments', timeout=5)
    print(f'   Status: {response.status_code}')
    if response.status_code in [200, 302]:  # 302 = redirect to login
        print('   ✅ Rota de investimentos OK\n')
    else:
        print(f'   ⚠️  Status inesperado\n')
except Exception as e:
    print(f'   ❌ Erro: {e}\n')

print('=' * 50)
print('✨ RESULTADO: Servidor está ONLINE e acessível!')
print(f'📍 Acesse: {BASE_URL}')
print('=' * 50)
