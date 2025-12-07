import sqlite3

db = sqlite3.connect('bws_finance.db')

# Verificar categorias
tenant_id = 'f8c9a8dc-c8e9-472a-85f1-c202893033e6'
cats = db.execute('SELECT name, type FROM categories WHERE tenant_id=?', (tenant_id,)).fetchall()

print(f'\n✅ Total de categorias: {len(cats)}')
if cats:
    print('\n📋 Categorias (primeiras 15):')
    for c in cats[:15]:
        print(f'  {c[1]}: {c[0]}')
else:
    print('\n❌ NENHUMA CATEGORIA ENCONTRADA!')

# Verificar transações do cartão
card_id = '2c2ad806-15c3-43a9-857e-43ed331e1b81'
trans = db.execute('SELECT COUNT(*) FROM transactions WHERE card_id=?', (card_id,)).fetchone()[0]
print(f'\n💳 Transações existentes no cartão: {trans}')

# Verificar últimas transações importadas
recent = db.execute('''
    SELECT description, amount, date, category 
    FROM transactions 
    WHERE card_id=? 
    ORDER BY created_at DESC 
    LIMIT 5
''', (card_id,)).fetchall()

if recent:
    print('\n📊 Últimas 5 transações do cartão:')
    for t in recent:
        print(f'  {t[2]} - {t[0]}: R$ {t[1]} ({t[3]})')

db.close()
