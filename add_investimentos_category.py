import sqlite3
import uuid

db = sqlite3.connect('bws_finance.db')
tenant_id = 'f8c9a8dc-c8e9-472a-85f1-c202893033e6'

# Adicionar Investimentos como Despesa
cat_id = str(uuid.uuid4())

try:
    db.execute("""
        INSERT INTO categories (id, tenant_id, name, type, icon, created_at)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
    """, (cat_id, tenant_id, 'Investimentos', 'Despesa', '📈'))
    
    db.commit()
    print("✅ Categoria 'Investimentos' (Despesa) adicionada!")
except sqlite3.IntegrityError:
    print("⚠️  Categoria 'Investimentos' já existe!")

# Listar todas as categorias
print("\n📋 CATEGORIAS ATUAIS:\n")

despesas = db.execute("""
    SELECT name, icon 
    FROM categories 
    WHERE tenant_id = ? AND type = 'Despesa'
    ORDER BY name
""", (tenant_id,)).fetchall()

receitas = db.execute("""
    SELECT name, icon 
    FROM categories 
    WHERE tenant_id = ? AND type = 'Receita'
    ORDER BY name
""", (tenant_id,)).fetchall()

print(f"💸 DESPESAS ({len(despesas)}):")
for cat in despesas:
    print(f"   {cat[1]} {cat[0]}")

print(f"\n💰 RECEITAS ({len(receitas)}):")
for cat in receitas:
    print(f"   {cat[1]} {cat[0]}")

db.close()
