import sqlite3

# Conectar ao banco
conn = sqlite3.connect('bws_finance.db')
cursor = conn.cursor()

# Verificar estrutura da tabela
print("=== ESTRUTURA DA TABELA INVESTMENTS ===")
columns = cursor.execute('PRAGMA table_info(investments)').fetchall()
column_names = [col[1] for col in columns]
print("Colunas:", column_names)
print("\nColuna 'quantity' existe?", "quantity" in column_names)

# Ver dados de PETR4
print("\n=== INVESTIMENTOS PETR4 ===")
rows = cursor.execute('SELECT id, name, amount, current_value FROM investments WHERE name LIKE "%PETR%"').fetchall()
for row in rows:
    print(f"ID {row[0]}: {row[1]} - Amount: R$ {row[2]:.2f}, Current: R$ {row[3]:.2f}")

conn.close()
