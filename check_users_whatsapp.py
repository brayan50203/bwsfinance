import sqlite3

db = sqlite3.connect('bws_finance.db')
db.row_factory = sqlite3.Row

users = db.execute('SELECT id, name, email, phone FROM users LIMIT 10').fetchall()

print("\n" + "="*60)
print("USUÁRIOS CADASTRADOS NO SISTEMA:")
print("="*60)

if users:
    for u in users:
        whatsapp = u['phone'] or 'NÃO VINCULADO'
        print(f"\n👤 {u['name']}")
        print(f"   📧 Email: {u['email']}")
        print(f"   📱 WhatsApp: {whatsapp}")
else:
    print("\n⚠️  Nenhum usuário cadastrado!")
    print("\n📋 Acesse http://localhost:5000/register para criar conta")

print("\n" + "="*60)
db.close()
