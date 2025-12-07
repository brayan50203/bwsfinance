"""
Cadastrar usuário Brayan no sistema
"""
import sqlite3
import uuid
from werkzeug.security import generate_password_hash

# Conectar ao banco
db = sqlite3.connect('bws_finance.db')
db.row_factory = sqlite3.Row

# Pegar tenant padrão
tenant = db.execute('SELECT id FROM tenants WHERE subdomain = "default"').fetchone()
if tenant:
    tenant_id = tenant['id']
else:
    tenant_id = str(uuid.uuid4())
    db.execute('INSERT INTO tenants (id, name, subdomain) VALUES (?, ?, ?)', 
               (tenant_id, 'Default', 'default'))

# Dados do usuário
name = 'Brayan Barbosa Lima'
email = 'brayan@bws.com'
phone = '+5511974764971'
password = '123456'

# Verificar se já existe
existing = db.execute('SELECT id FROM users WHERE email = ? OR phone = ?', (email, phone)).fetchone()

if existing:
    print(f'✅ Usuário já existe!')
    print(f'   Atualizando dados...')
    
    # Atualizar
    password_hash = generate_password_hash(password)
    db.execute('''
        UPDATE users 
        SET name = ?, phone = ?, password_hash = ?, active = 1
        WHERE id = ?
    ''', (name, phone, password_hash, existing['id']))
    user_id = existing['id']
else:
    print(f'✅ Criando novo usuário...')
    
    # Criar usuário
    user_id = str(uuid.uuid4())
    password_hash = generate_password_hash(password)
    
    db.execute('''
        INSERT INTO users (id, tenant_id, email, password_hash, name, phone, active)
        VALUES (?, ?, ?, ?, ?, ?, 1)
    ''', (user_id, tenant_id, email, password_hash, name, phone))
    
    # Criar conta padrão
    account_id = str(uuid.uuid4())
    db.execute('''
        INSERT INTO accounts (id, user_id, tenant_id, name, type, initial_balance)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (account_id, user_id, tenant_id, 'Conta Principal', 'Corrente', 0))

db.commit()
db.close()

print('')
print('='*60)
print('USUÁRIO CADASTRADO COM SUCESSO!')
print('='*60)
print(f'Nome:     {name}')
print(f'WhatsApp: {phone}')
print(f'Email:    {email}')
print(f'Senha:    {password}')
print('='*60)
print('')
print('Agora você pode:')
print('1. Enviar mensagem para: +5511947626417')
print('2. Acessar: http://192.168.80.122:5000')
print('')
