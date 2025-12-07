import sqlite3
from datetime import datetime

db = sqlite3.connect('bws_finance.db')
tenant_id = 'f8c9a8dc-c8e9-472a-85f1-c202893033e6'

# Consultar transações de setembro de 2025
print("\n" + "="*80)
print("📊 ANÁLISE DO GRÁFICO - PICO DE SETEMBRO 2025")
print("="*80)

# Buscar todas as transações de setembro
setembro = db.execute("""
    SELECT date, description, value, type, category_id
    FROM transactions 
    WHERE tenant_id = ? 
    AND date LIKE '2025-09-%'
    ORDER BY value DESC
""", (tenant_id,)).fetchall()

if not setembro:
    print("\n❌ Nenhuma transação encontrada em setembro de 2025")
else:
    print(f"\n✅ {len(setembro)} transações em setembro:")
    
    total_despesas = sum([t[2] for t in setembro if t[3] == 'Despesa'])
    total_receitas = sum([t[2] for t in setembro if t[3] == 'Receita'])
    
    print(f"\n💰 TOTAIS:")
    print(f"   Despesas: R$ {total_despesas:,.2f}")
    print(f"   Receitas: R$ {total_receitas:,.2f}")
    print(f"   Saldo:    R$ {total_receitas - total_despesas:,.2f}")
    
    print(f"\n📋 TOP 10 MAIORES VALORES:")
    for i, t in enumerate(setembro[:10], 1):
        emoji = "💸" if t[3] == "Despesa" else "💵"
        print(f"   {i:2}. {emoji} {t[0]} | R$ {t[2]:10,.2f} | {t[1][:50]}")
    
    # Agrupar por data
    print(f"\n📅 DISTRIBUIÇÃO POR DIA:")
    by_date = {}
    for t in setembro:
        date = t[0]
        if date not in by_date:
            by_date[date] = {'despesas': 0, 'receitas': 0, 'count': 0}
        by_date[date]['count'] += 1
        if t[3] == 'Despesa':
            by_date[date]['despesas'] += t[2]
        else:
            by_date[date]['receitas'] += t[2]
    
    for date in sorted(by_date.keys()):
        d = by_date[date]
        print(f"   {date} | {d['count']:2} trans | Desp: R$ {d['despesas']:8,.2f} | Rec: R$ {d['receitas']:8,.2f}")

# Verificar se há valores extremos ou erros de lançamento
print(f"\n🔍 VERIFICANDO ANOMALIAS:")
anomalias = db.execute("""
    SELECT date, description, value, type
    FROM transactions 
    WHERE tenant_id = ? 
    AND date LIKE '2025-09-%'
    AND value > 5000
""", (tenant_id,)).fetchall()

if anomalias:
    print(f"\n⚠️  VALORES ACIMA DE R$ 5.000:")
    for a in anomalias:
        print(f"   {a[0]} | R$ {a[2]:,.2f} | {a[1]}")
else:
    print("   ✅ Nenhum valor extremo detectado")

db.close()
print("\n" + "="*80 + "\n")
