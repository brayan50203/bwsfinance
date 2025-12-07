import sqlite3
import hashlib
import uuid
from datetime import datetime

# Conectar ao banco
conn = sqlite3.connect('bws_finance.db')
cursor = conn.cursor()

# Verificar se tabela users existe
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if not cursor.fetchone():
        print("❌ Tabela 'users' não existe! Criando...")
        
        # Criar tabela users
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT,
                phone TEXT,
                active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        print("✅ Tabela 'users' criada!")
except Exception as e:
    print(f"Erro ao verificar tabela: {e}")

# Verificar se usuário já existe
phone = '+5511974764971'
cursor.execute("SELECT id, name, phone FROM users WHERE phone = ?", (phone,))
existing = cursor.fetchone()

if existing:
    print(f"✅ Usuário já cadastrado!")
    print(f"   ID: {existing[0]}")
    print(f"   Nome: {existing[1]}")
    print(f"   Phone: {existing[2]}")
else:
    print(f"📝 Cadastrando novo usuário...")
    
    # Gerar IDs
    user_id = str(uuid.uuid4())
    tenant_id = str(uuid.uuid4())
    
    # Hash da senha padrão
    password = hashlib.sha256("123456".encode()).hexdigest()
    
    # Inserir usuário
    cursor.execute('''
        INSERT INTO users (id, tenant_id, email, password, name, phone, active)
        VALUES (?, ?, ?, ?, ?, ?, 1)
    ''', (
        user_id,
        tenant_id,
        'brayan@bws.com',
        password,
        'Brayan Barbosa Lima',
        phone
    ))
    
    conn.commit()
    print(f"✅ Usuário cadastrado com sucesso!")
    print(f"   ID: {user_id}")
    print(f"   Tenant: {tenant_id}")
    print(f"   Email: brayan@bws.com")
    print(f"   Senha: 123456")
    print(f"   Phone: {phone}")

conn.close()
print("\n🎉 Pronto! Agora você pode enviar mensagens pelo WhatsApp!")
