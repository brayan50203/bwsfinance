import sqlite3

conn = sqlite3.connect('bws_finance.db')
cursor = conn.cursor()

try:
    cursor.execute('ALTER TABLE cards ADD COLUMN used_limit REAL DEFAULT 0')
    print('✅ Coluna used_limit adicionada à tabela cards')
except Exception as e:
    print(f'⚠️ Coluna já existe ou erro: {e}')

conn.commit()
conn.close()
print('✅ Alteração concluída')
