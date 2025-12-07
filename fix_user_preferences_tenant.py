import sqlite3

conn = sqlite3.connect('bws_finance.db')
cursor = conn.cursor()

print("Verificando e corrigindo estrutura das tabelas...")

# Verificar user_preferences
cursor.execute("PRAGMA table_info(user_preferences)")
cols = [c[1] for c in cursor.fetchall()]

if 'tenant_id' not in cols:
    print("⚠️ tenant_id não existe em user_preferences")
    # Pegar tenant_id default
    cursor.execute("SELECT id FROM tenants WHERE subdomain = 'default' LIMIT 1")
    default_tenant = cursor.fetchone()
    default_tenant_id = default_tenant[0] if default_tenant else None
    
    if default_tenant_id:
        try:
            cursor.execute('ALTER TABLE user_preferences ADD COLUMN tenant_id TEXT')
            cursor.execute('UPDATE user_preferences SET tenant_id = ?', (default_tenant_id,))
            print(f"✅ Coluna tenant_id adicionada com valor padrão: {default_tenant_id}")
        except sqlite3.OperationalError as e:
            print(f"❌ Erro ao adicionar tenant_id: {e}")
    else:
        print("❌ Tenant default não encontrado")
else:
    print("✅ tenant_id já existe em user_preferences")

# Corrigir as colunas que não precisam de tenant_id em INSERT OR REPLACE
print("\n✅ Estrutura verificada!")

conn.commit()
conn.close()
