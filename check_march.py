import sqlite3

db = sqlite3.connect('bws_finance.db')
tenant_id = 'f8c9a8dc-c8e9-472a-85f1-c202893033e6'

# Buscar transações absurdas de março
marco = db.execute("""
    SELECT id, date, description, value, type
    FROM transactions 
    WHERE tenant_id = ? 
    AND date LIKE '2025-03-%'
    ORDER BY value DESC
    LIMIT 20
""", (tenant_id,)).fetchall()

print("\n📊 TOP 20 TRANSAÇÕES DE MARÇO (verificar se são falsas):\n")
total_marco = 0
for t in marco:
    print(f"   {t[1]} | R$ {t[3]:15,.2f} | {t[2][:50]}")
    total_marco += t[3]

print(f"\n💰 Total top 20: R$ {total_marco:,.2f}")

# Verificar se há valores acima de 100 mil (absurdos)
absurdos = db.execute("""
    SELECT id, date, description, value
    FROM transactions 
    WHERE tenant_id = ? 
    AND date LIKE '2025-03-%'
    AND value > 100000
""", (tenant_id,)).fetchall()

if absurdos:
    print(f"\n🚨 VALORES ABSURDOS (> R$ 100.000):")
    for a in absurdos:
        print(f"   {a[1]} | R$ {a[3]:,.2f} | {a[2]}")
    
    print("\n❓ Deseja deletar TODAS as transações de março? (executar delete_fake_march.py)")

db.close()
