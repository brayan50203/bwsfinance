import sqlite3

db = sqlite3.connect('bws_finance.db')
db.row_factory = sqlite3.Row

# Verificar se tabela installments existe
tables = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='installments'").fetchall()
print(f"Tabela installments existe: {len(tables) > 0}")

if len(tables) > 0:
    # Verificar estrutura
    columns = db.execute("PRAGMA table_info(installments)").fetchall()
    print("\nColunas da tabela installments:")
    for col in columns:
        print(f"  - {col['name']} ({col['type']})")
    
    # Contar registros
    count = db.execute("SELECT COUNT(*) as total FROM installments").fetchone()
    print(f"\nTotal de parcelas: {count['total']}")

db.close()
