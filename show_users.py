import sqlite3

conn = sqlite3.connect('bws_finance.db')
cursor = conn.cursor()

print('\n📋 ESTRUTURA DA TABELA USERS:')
print('-' * 80)
cursor.execute('PRAGMA table_info(users)')
for col in cursor.fetchall():
    print(f'{col[1]:20s} | {col[2]:15s}')

print('\n👥 USUÁRIOS:')
print('-' * 80)
cursor.execute('SELECT * FROM users LIMIT 2')
cols = [desc[0] for desc in cursor.description]
print('Colunas:', ', '.join(cols))
for row in cursor.fetchall():
    print(row)

conn.close()
