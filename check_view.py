import sqlite3

db = sqlite3.connect('bws_finance.db')
cursor = db.cursor()

try:
    cursor.execute('SELECT * FROM v_account_balances LIMIT 1')
    print('✅ View v_account_balances existe')
    print(f'   Colunas: {[desc[0] for desc in cursor.description]}')
except Exception as e:
    print(f'❌ Erro na view: {e}')
    print('\n🔧 Tentando criar a view...')
    
    try:
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS v_account_balances AS
            SELECT 
                a.*,
                COALESCE(SUM(CASE WHEN t.type = 'Receita' AND t.status = 'Pago' THEN t.value ELSE 0 END), 0) -
                COALESCE(SUM(CASE WHEN t.type = 'Despesa' AND t.status = 'Pago' THEN t.value ELSE 0 END), 0) as balance
            FROM accounts a
            LEFT JOIN transactions t ON a.id = t.account_id
            GROUP BY a.id
        ''')
        db.commit()
        print('✅ View criada com sucesso!')
    except Exception as e2:
        print(f'❌ Erro ao criar view: {e2}')

db.close()
