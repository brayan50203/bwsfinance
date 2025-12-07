import sqlite3

conn = sqlite3.connect('bws_finance.db')
cursor = conn.cursor()

print('🔍 Verificando investimento problemático...\n')

# Ver o bitcoin
cursor.execute('SELECT * FROM investments WHERE id = 10')
row = cursor.fetchone()
print(f'Bitcoin encontrado:')
print(f'  ID: {row[0]}')
print(f'  Nome: {row[2]}')
print(f'  Quantidade: {row[6] if len(row) > 6 else "N/A"}')
print(f'  Valor Investido: R$ {row[3]:,.2f}')
print(f'  Valor Atual: R$ {row[4]:,.2f}')

print('\n🗑️  Deletando investimento com valor incorreto...')
cursor.execute('DELETE FROM investments WHERE id = 10')
conn.commit()

print('✅ Investimento deletado!')

# Ver novo total
cursor.execute('SELECT SUM(amount), SUM(current_value) FROM investments')
total = cursor.fetchone()
print(f'\n📊 Novo total:')
print(f'  Investido: R$ {total[0]:,.2f}')
print(f'  Atual: R$ {total[1]:,.2f}')

conn.close()
