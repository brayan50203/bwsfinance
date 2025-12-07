import sqlite3

conn = sqlite3.connect('bws_finance.db')
cursor = conn.cursor()

# Ver total
cursor.execute('SELECT COUNT(*) FROM investments')
print(f'\n✅ Total de investimentos: {cursor.fetchone()[0]}\n')

# Ver detalhes
cursor.execute('SELECT id, user_id, name, amount, current_value FROM investments')
print('📊 Investimentos cadastrados:')
print('-' * 80)

total_amount = 0
total_current = 0

for row in cursor.fetchall():
    inv_id, user_id, name, amount, current = row
    total_amount += amount if amount else 0
    total_current += current if current else 0
    print(f'ID: {inv_id:3d} | User: {user_id[:8]}... | {name:30s} | Investido: R$ {amount:12.2f} | Atual: R$ {current:12.2f}')

print('-' * 80)
print(f'TOTAL INVESTIDO: R$ {total_amount:,.2f}')
print(f'TOTAL ATUAL: R$ {total_current:,.2f}')

conn.close()
