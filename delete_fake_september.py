import sqlite3

db = sqlite3.connect('bws_finance.db')
tenant_id = 'f8c9a8dc-c8e9-472a-85f1-c202893033e6'

# Buscar todas as transações de setembro para confirmar
setembro = db.execute("""
    SELECT id, date, description, value, type
    FROM transactions 
    WHERE tenant_id = ? 
    AND date LIKE '2025-09-%'
    ORDER BY date
""", (tenant_id,)).fetchall()

print(f"\n🗑️  DELETANDO {len(setembro)} TRANSAÇÕES FALSAS DE SETEMBRO...\n")

for t in setembro:
    print(f"   ❌ {t[1]} | R$ {t[3]:,.2f} | {t[2][:60]}")
    db.execute("DELETE FROM transactions WHERE id = ?", (t[0],))

db.commit()

# Verificar se foram deletadas
restantes = db.execute("""
    SELECT COUNT(*) FROM transactions 
    WHERE tenant_id = ? AND date LIKE '2025-09-%'
""", (tenant_id,)).fetchone()[0]

print(f"\n✅ Transações deletadas com sucesso!")
print(f"✅ Restantes em setembro: {restantes}")

# Mostrar totais atualizados por mês
print(f"\n📊 TOTAIS POR MÊS (após limpeza):\n")
meses = db.execute("""
    SELECT 
        strftime('%Y-%m', date) as mes,
        SUM(CASE WHEN type = 'Despesa' THEN value ELSE 0 END) as despesas,
        SUM(CASE WHEN type = 'Receita' THEN value ELSE 0 END) as receitas
    FROM transactions 
    WHERE tenant_id = ?
    GROUP BY mes
    ORDER BY mes
""", (tenant_id,)).fetchall()

for m in meses:
    saldo = m[2] - m[1]
    print(f"   {m[0]} | Desp: R$ {m[1]:10,.2f} | Rec: R$ {m[2]:10,.2f} | Saldo: R$ {saldo:10,.2f}")

db.close()
print("\n✅ Banco de dados atualizado!\n")
