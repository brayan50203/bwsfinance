"""
Remove categorias duplicadas/específicas e deixa apenas as principais mais genéricas
"""
import sqlite3

conn = sqlite3.connect('bws_finance.db')
cursor = conn.cursor()

# Tenant ID do usuário
TENANT_ID = 'f2ac3497-e8a9-4593-bfe3-7fef2fc2ae18'

print("🔄 Limpando categorias antigas...")

# Deletar TODAS as categorias antigas
cursor.execute("DELETE FROM categories WHERE tenant_id = ?", (TENANT_ID,))
print(f"   ✅ {cursor.rowcount} categorias antigas removidas")

conn.commit()
conn.close()

print("\n✅ Banco limpo! Agora vamos popular com categorias genéricas...")
