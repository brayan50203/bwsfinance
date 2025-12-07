import sqlite3
import uuid

db = sqlite3.connect('bws_finance.db')
cursor = db.cursor()

tenant_id = 'f8c9a8dc-c8e9-472a-85f1-c202893033e6'

# Categorias de Despesa
expense_categories = [
    ('Alimentação', 'Despesa', '🍔'),
    ('Transporte', 'Despesa', '🚗'),
    ('Moradia', 'Despesa', '🏠'),
    ('Saúde', 'Despesa', '⚕️'),
    ('Educação', 'Despesa', '📚'),
    ('Lazer', 'Despesa', '🎬'),
    ('Roupas', 'Despesa', '👕'),
    ('Beleza', 'Despesa', '💄'),
    ('Eletrônicos', 'Despesa', '💻'),
    ('Serviços', 'Despesa', '🔧'),
    ('Impostos', 'Despesa', '📋'),
    ('Empréstimos', 'Despesa', '💰'),
    ('Outros Despesa', 'Despesa', '📦'),
]

# Categorias de Receita
income_categories = [
    ('Salário', 'Receita', '💼'),
    ('Freelance', 'Receita', '🎨'),
    ('Investimentos', 'Receita', '📈'),
    ('Aluguel', 'Receita', '🏘️'),
    ('Prêmios', 'Receita', '🏆'),
    ('Presentes', 'Receita', '🎁'),
    ('Reembolso', 'Receita', '💵'),
    ('Outros Receita', 'Receita', '📦'),
]

print('🔧 Criando categorias padrão...\n')

# Verificar se já existem
existing = cursor.execute('SELECT name FROM categories WHERE tenant_id=?', (tenant_id,)).fetchall()
existing_names = [e[0] for e in existing]

# Inserir categorias de despesa
for name, cat_type, icon in expense_categories:
    if name not in existing_names or (name == 'Outros' and cat_type == 'expense'):
        category_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT OR REPLACE INTO categories (id, tenant_id, name, type, icon, created_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        ''', (category_id, tenant_id, name, cat_type, icon))
        print(f'  ✅ {icon} {name} ({cat_type})')

# Inserir categorias de receita
for name, cat_type, icon in income_categories:
    if name not in existing_names:
        category_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO categories (id, tenant_id, name, type, icon, created_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        ''', (category_id, tenant_id, name, cat_type, icon))
        print(f'  ✅ {icon} {name} ({cat_type})')

db.commit()

# Verificar resultado
total = cursor.execute('SELECT COUNT(*) FROM categories WHERE tenant_id=?', (tenant_id,)).fetchone()[0]
print(f'\n✅ Total de categorias criadas: {total}')

db.close()
