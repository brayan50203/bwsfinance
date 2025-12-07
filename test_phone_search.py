import sqlite3

conn = sqlite3.connect('bws_finance.db')
cursor = conn.cursor()

# Testar diferentes formatos
phones_to_test = [
    '+5511974764971',
    '5511974764971',
    '11974764971',
    '5511974764971@c.us'
]

print("=" * 60)
print("TESTANDO BUSCA DE USUÁRIO POR TELEFONE")
print("=" * 60)

for phone in phones_to_test:
    clean_number = phone.replace('@c.us', '')
    
    # Simular lógica do app.py
    result = cursor.execute('''
        SELECT id, name, phone
        FROM users
        WHERE (phone = ? OR phone = ?) AND active = 1
    ''', (clean_number, f'+{clean_number}')).fetchone()
    
    print(f"\n📱 Buscando: {phone}")
    print(f"   Limpo: {clean_number}")
    print(f"   Com +: +{clean_number}")
    print(f"   Resultado: {result}")

print("\n" + "=" * 60)
print("USUÁRIOS CADASTRADOS NO BANCO:")
print("=" * 60)
all_users = cursor.execute("SELECT id, name, phone, active FROM users").fetchall()
for user in all_users:
    print(f"  ID: {user[0][:8]}... | Nome: {user[1]} | Phone: '{user[2]}' | Ativo: {user[3]}")

conn.close()
