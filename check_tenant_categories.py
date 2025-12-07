import sqlite3

conn = sqlite3.connect('bws_finance.db')
cursor = conn.cursor()

# Verificar usuários
users = cursor.execute('SELECT id, name, tenant_id FROM users').fetchall()
print('Usuários:')
for u in users:
    print(f'  {u[1]} - tenant_id: {u[2]}')

# Verificar categorias
cats = cursor.execute('SELECT COUNT(*) as total, tenant_id FROM categories GROUP BY tenant_id').fetchall()
print('\nCategorias por tenant:')
for c in cats:
    print(f'  tenant_id "{c[1]}": {c[0]} categorias')

conn.close()
