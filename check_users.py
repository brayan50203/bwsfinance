import sqlite3

conn = sqlite3.connect('bws_finance.db')
cursor = conn.cursor()

# Ver usuários
print('\n👥 USUÁRIOS:')
print('-' * 80)
cursor.execute('SELECT id, username, email FROM users')
users = cursor.fetchall()
for u in users:
    print(f'ID: {u[0][:20]}... | Username: {u[1]:20s} | Email: {u[2]}')

# Ver tenant_id dos investimentos
print('\n📊 INVESTIMENTOS POR USUÁRIO:')
print('-' * 80)
cursor.execute('''
    SELECT u.username, u.id, COUNT(i.id) as total, SUM(i.current_value) as valor
    FROM users u
    LEFT JOIN investments i ON i.user_id = u.id
    GROUP BY u.id
''')
for row in cursor.fetchall():
    username, user_id, total, valor = row
    valor_fmt = f"R$ {valor:,.2f}" if valor else "R$ 0,00"
    print(f'{username:20s} | {user_id[:20]}... | {total} investimentos | {valor_fmt}')

# Ver se tem campo tenant_id na tabela investments
print('\n📋 ESTRUTURA DA TABELA INVESTMENTS:')
print('-' * 80)
cursor.execute('PRAGMA table_info(investments)')
for col in cursor.fetchall():
    print(f'{col[1]:20s} | {col[2]:10s} | NOT NULL: {col[3]} | Default: {col[4]}')

conn.close()
