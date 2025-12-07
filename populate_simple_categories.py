"""
Popula categorias GENÉRICAS no BWS Finance
Categorias simples e diretas, sem subdivisões específicas
"""
import sqlite3
import uuid

DB_PATH = 'bws_finance.db'
TENANT_ID = 'f2ac3497-e8a9-4593-bfe3-7fef2fc2ae18'

def create_category(name, type_, icon):
    """Cria uma categoria simples (sem subcategorias)"""
    conn = sqlite3.connect(DB_PATH)
    category_id = str(uuid.uuid4())
    
    conn.execute("""
        INSERT INTO categories (id, tenant_id, name, type, icon, parent_id, active, created_at)
        VALUES (?, ?, ?, ?, ?, NULL, 1, CURRENT_TIMESTAMP)
    """, (category_id, TENANT_ID, name, type_, icon))
    
    conn.commit()
    conn.close()
    print(f"✅ {icon} {name} ({type_})")

print("="*50)
print("💰 CATEGORIAS DE RECEITAS:")
print("="*50)

create_category("Salário", "Receita", "💼")
create_category("Freelance", "Receita", "💻")
create_category("Vendas", "Receita", "💸")
create_category("Investimentos", "Receita", "📈")
create_category("Reembolso", "Receita", "💰")
create_category("Outros", "Receita", "🎁")

print("\n" + "="*50)
print("💳 CATEGORIAS DE DESPESAS:")
print("="*50)

create_category("Alimentação", "Despesa", "🍽️")
create_category("Transporte", "Despesa", "🚗")
create_category("Moradia", "Despesa", "🏠")
create_category("Saúde", "Despesa", "⚕️")
create_category("Educação", "Despesa", "📚")
create_category("Lazer", "Despesa", "🎮")
create_category("Compras", "Despesa", "🛍️")
create_category("Serviços", "Despesa", "📱")
create_category("Impostos", "Despesa", "🧾")
create_category("Investimentos", "Despesa", "📊")
create_category("Outros", "Despesa", "💸")

print("\n" + "="*50)
print("✅ CATEGORIAS CRIADAS COM SUCESSO!")
print("="*50)

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
receitas = conn.execute("SELECT COUNT(*) as total FROM categories WHERE type = 'Receita' AND tenant_id = ?", (TENANT_ID,)).fetchone()
despesas = conn.execute("SELECT COUNT(*) as total FROM categories WHERE type = 'Despesa' AND tenant_id = ?", (TENANT_ID,)).fetchone()
conn.close()

print(f"\n📊 RESUMO:")
print(f"   💰 Receitas: {receitas['total']} categorias")
print(f"   💳 Despesas: {despesas['total']} categorias")
print(f"   📂 Total: {receitas['total'] + despesas['total']} categorias")
