import sqlite3

conn = sqlite3.connect('bws_finance.db')
cursor = conn.cursor()

# Ver todos os tenant_ids
print('\n🏢 TENANTS:')
print('-' * 80)
cursor.execute('SELECT DISTINCT tenant_id FROM users')
tenants = cursor.fetchall()
for t in tenants:
    tenant_id = t[0]
    
    # Contar usuários
    cursor.execute('SELECT COUNT(*) FROM users WHERE tenant_id = ?', (tenant_id,))
    user_count = cursor.fetchone()[0]
    
    # Contar investimentos
    cursor.execute('SELECT COUNT(*), SUM(current_value) FROM investments WHERE tenant_id = ?', (tenant_id,))
    inv_data = cursor.fetchone()
    inv_count = inv_data[0] if inv_data[0] else 0
    inv_value = inv_data[1] if inv_data[1] else 0
    
    print(f'Tenant: {tenant_id[:30]}... | {user_count} users | {inv_count} investimentos | R$ {inv_value:,.2f}')

# Ver investimentos sem tenant_id
print('\n📊 INVESTIMENTOS SEM TENANT_ID:')
print('-' * 80)
cursor.execute('SELECT COUNT(*), SUM(current_value) FROM investments WHERE tenant_id IS NULL OR tenant_id = ""')
orphan = cursor.fetchone()
if orphan[0] > 0:
    print(f'❌ {orphan[0]} investimentos órfãos | Total: R$ {orphan[1]:,.2f}')
    
    # Mostrar detalhes
    cursor.execute('SELECT id, user_id, name, current_value FROM investments WHERE tenant_id IS NULL OR tenant_id = "" LIMIT 10')
    for inv in cursor.fetchall():
        print(f'  ID {inv[0]} | User: {inv[1][:20]}... | {inv[2]:20s} | R$ {inv[3]:,.2f}')
else:
    print('✅ Todos os investimentos têm tenant_id')

conn.close()
