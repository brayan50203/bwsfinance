import sqlite3

conn = sqlite3.connect('bws_finance.db')
cursor = conn.cursor()

print('\n🗑️  LIMPANDO TODOS OS INVESTIMENTOS...\n')

# Deletar todos os investimentos
cursor.execute('DELETE FROM investments')
deleted = cursor.rowcount
conn.commit()

print(f'✅ Deletados {deleted} investimentos')

# Verificar
cursor.execute('SELECT COUNT(*) FROM investments')
count = cursor.fetchone()[0]
print(f'📊 Restam: {count} investimentos\n')

print('✅ Banco limpo! Agora pode adicionar novos investimentos.')

conn.close()
