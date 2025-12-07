import sqlite3

conn = sqlite3.connect('bws_finance.db')
cursor = conn.cursor()

print("=" * 60)
print("ATUALIZANDO TELEFONE DO USUÁRIO")
print("=" * 60)

# Verificar estado atual
user = cursor.execute("SELECT id, name, email, phone FROM users WHERE email = 'brayan@bws.com'").fetchone()

if user:
    print(f"\n📱 Usuário encontrado:")
    print(f"   ID: {user[0]}")
    print(f"   Nome: {user[1]}")
    print(f"   Email: {user[2]}")
    print(f"   Telefone ATUAL: '{user[3]}'")
    
    # Atualizar para formato correto
    correct_phone = '+5511974764971'
    cursor.execute("UPDATE users SET phone = ? WHERE id = ?", (correct_phone, user[0]))
    conn.commit()
    
    # Verificar atualização
    updated = cursor.execute("SELECT phone FROM users WHERE id = ?", (user[0],)).fetchone()
    print(f"\n✅ Telefone ATUALIZADO para: '{updated[0]}'")
else:
    print("\n❌ Usuário não encontrado!")

conn.close()
print("\n" + "=" * 60)
print("CONCLUÍDO!")
print("=" * 60)
