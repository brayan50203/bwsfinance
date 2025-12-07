import sqlite3

conn = sqlite3.connect('bws_finance.db')
cur = conn.cursor()

# Verificar se tabela existe
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notifications'")
result = cur.fetchone()

if result:
    print(f"✅ Tabela 'notifications' já existe!")
    cur.execute("PRAGMA table_info(notifications)")
    columns = cur.fetchall()
    print("\nColunas existentes:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
else:
    print("❌ Tabela 'notifications' não existe")

conn.close()
