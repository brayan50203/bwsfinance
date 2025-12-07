import sqlite3

db = sqlite3.connect('bws_finance.db')
tenant_id = 'f8c9a8dc-c8e9-472a-85f1-c202893033e6'

# Buscar contas
print("\n🏦 CONTAS:")
accounts = db.execute("""
    SELECT id, name
    FROM accounts 
    WHERE tenant_id = ?
""", (tenant_id,)).fetchall()

for a in accounts:
    print(f"\n  {a[1]}")
    print(f"    ID: {a[0]}")
    
    # Buscar transações absurdas desta conta (> R$ 100.000)
    absurdas = db.execute("""
        SELECT id, date, description, value
        FROM transactions
        WHERE account_id = ?
        AND value > 100000
        ORDER BY value DESC
    """, (a[0],)).fetchall()
    
    if absurdas:
        print(f"    🚨 TRANSAÇÕES ABSURDAS:")
        for t in absurdas:
            print(f"       {t[1]} | R$ {t[3]:,.2f} | {t[2][:50]}")
    
    print()

db.close()
