"""
Script para testar/criar usuário de teste
"""
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

# Configurações do usuário de teste
TEST_EMAIL = "admin@bws.com"
TEST_PASSWORD = "123456"
TEST_NAME = "Admin BWS"

conn = sqlite3.connect('bws_finance.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Verificar se usuário existe
user = cursor.execute('SELECT * FROM users WHERE email = ?', (TEST_EMAIL,)).fetchone()

if user:
    print(f"✅ Usuário já existe: {user['name']} ({user['email']})")
    print(f"   ID: {user['id']}")
    print(f"   Tenant: {user['tenant_id']}")
    
    # Testar senha
    if check_password_hash(user['password_hash'], TEST_PASSWORD):
        print(f"✅ Senha correta: {TEST_PASSWORD}")
    else:
        print(f"❌ Senha incorreta. Atualizando para: {TEST_PASSWORD}")
        new_hash = generate_password_hash(TEST_PASSWORD)
        cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (new_hash, user['id']))
        conn.commit()
        print("✅ Senha atualizada!")
else:
    print(f"❌ Usuário não existe. Criando...")
    
    # Criar tenant
    tenant_id = str(uuid.uuid4())
    cursor.execute('''
        INSERT INTO tenants (id, name, active, created_at)
        VALUES (?, ?, 1, datetime('now'))
    ''', (tenant_id, TEST_NAME))
    
    # Criar usuário
    user_id = str(uuid.uuid4())
    password_hash = generate_password_hash(TEST_PASSWORD)
    
    cursor.execute('''
        INSERT INTO users (id, tenant_id, name, email, password_hash, phone, is_admin, active, created_at)
        VALUES (?, ?, ?, ?, ?, ?, 1, 1, datetime('now'))
    ''', (user_id, tenant_id, TEST_NAME, TEST_EMAIL, password_hash, '+5500000000000'))
    
    conn.commit()
    print(f"✅ Usuário criado com sucesso!")
    print(f"   Email: {TEST_EMAIL}")
    print(f"   Senha: {TEST_PASSWORD}")

conn.close()

print("\n" + "="*60)
print("🔐 CREDENCIAIS DE TESTE")
print("="*60)
print(f"Email: {TEST_EMAIL}")
print(f"Senha: {TEST_PASSWORD}")
print("="*60)
print(f"\n🌐 Acesse: http://localhost/login")
print(f"🌐 Ou: http://localhost:80/login")
print(f"🌐 Ou: http://192.168.80.132/login")
