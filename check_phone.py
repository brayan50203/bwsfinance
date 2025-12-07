import sqlite3

db = sqlite3.connect('bws_finance.db')

users = db.execute('''
    SELECT name, email, phone 
    FROM users 
    WHERE phone IS NOT NULL AND phone != ''
''').fetchall()

print("\n" + "="*60)
print("USUÁRIOS COM WHATSAPP VINCULADO:")
print("="*60)

if users:
    for u in users:
        print(f"\n👤 {u[0]}")
        print(f"   📧 {u[1]}")
        print(f"   📱 {u[2]}")
else:
    print("\n⚠️  Nenhum usuário com telefone vinculado!")

print("\n" + "="*60)
db.close()
