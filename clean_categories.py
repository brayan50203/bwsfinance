import sqlite3

conn = sqlite3.connect('bws_finance.db')
cursor = conn.cursor()

TENANT_ID = 'f2ac3497-e8a9-4593-bfe3-7fef2fc2ae18'

print("Limpando categorias antigas...")
cursor.execute("DELETE FROM categories WHERE tenant_id = ?", (TENANT_ID,))
print(f"Removidas: {cursor.rowcount} categorias")

conn.commit()
conn.close()
print("Banco limpo!")
