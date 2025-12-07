import sqlite3

conn = sqlite3.connect('bws_finance.db')
cursor = conn.cursor()

# Listar tabelas de categorias
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%categ%'")
tables = [row[0] for row in cursor.fetchall()]

print("Tabelas de categorias:", tables)

# Ver estrutura da tabela categories se existir
if 'categories' in tables:
    cursor.execute("PRAGMA table_info(categories)")
    print("\nEstrutura da tabela 'categories':")
    for row in cursor.fetchall():
        print(f"  {row[1]} ({row[2]})")

conn.close()
