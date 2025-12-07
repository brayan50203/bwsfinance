"""
Verificar dados no banco
"""
import sqlite3

db = sqlite3.connect('bws_finance.db')
db.row_factory = sqlite3.Row

# Contas
contas = db.execute('SELECT * FROM accounts').fetchall()
print(f'\n📊 Contas: {len(contas)}')
for c in contas:
    print(f'  - {c["name"]} ({c["type"]}) - ID: {c["id"][:8]}...')

# Cartões
cartoes = db.execute('SELECT * FROM cards').fetchall()
print(f'\n💳 Cartões: {len(cartoes)}')
for c in cartoes:
    print(f'  - {c["name"]} - ID: {c["id"][:8]}...')
    print(f'    Colunas: {c.keys()}')

# Categorias
categorias = db.execute('SELECT * FROM categories ORDER BY type, name').fetchall()
print(f'\n📂 Categorias: {len(categorias)}')
for c in categorias:
    print(f'  - [{c["type"]}] {c["icon"]} {c["name"]} - ID: {c["id"][:8]}...')

# Usuários
usuarios = db.execute('SELECT * FROM users').fetchall()
print(f'\n👥 Usuários: {len(usuarios)}')
for u in usuarios:
    print(f'  - {u["name"]} ({u["email"]}) - ID: {u["id"][:8]}...')

db.close()
