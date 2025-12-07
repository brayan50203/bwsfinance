import sqlite3

conn = sqlite3.connect('bws_finance.db')
cursor = conn.cursor()

print("=== Estrutura da tabela CARDS ===")
cursor.execute("PRAGMA table_info(cards)")
for row in cursor.fetchall():
    print(f"  {row[1]} ({row[2]})")

conn.close()
