import sqlite3

db = sqlite3.connect('bws_finance.db')
db.row_factory = sqlite3.Row

# Ver estrutura da tabela investments
print("📋 Estrutura da tabela investments:")
columns = db.execute("PRAGMA table_info(investments)").fetchall()
for col in columns:
    print(f"  - {col['name']} ({col['type']}) {'NOT NULL' if col['notnull'] else ''} {'DEFAULT: ' + str(col['dflt_value']) if col['dflt_value'] else ''}")

print("\n📊 Investimentos existentes:")
investments = db.execute("SELECT * FROM investments LIMIT 5").fetchall()
for inv in investments:
    print(f"  ID: {inv['id']} | Nome: {inv['name']} | Tipo: {inv['investment_type']} | Valor: R$ {inv['amount']}")

db.close()
