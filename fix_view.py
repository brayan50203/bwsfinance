import sqlite3

db = sqlite3.connect('bws_finance.db')
cursor = db.cursor()

print('🔧 Recriando view v_account_balances...')

try:
    # Dropar view antiga
    cursor.execute('DROP VIEW IF EXISTS v_account_balances')
    print('✅ View antiga removida')
    
    # Criar view nova
    cursor.execute('''
        CREATE VIEW v_account_balances AS
        SELECT 
            a.*,
            (
                a.initial_balance + 
                COALESCE(SUM(CASE WHEN t.type = 'Receita' AND t.status = 'Pago' THEN t.value ELSE 0 END), 0) -
                COALESCE(SUM(CASE WHEN t.type = 'Despesa' AND t.status = 'Pago' THEN t.value ELSE 0 END), 0)
            ) as balance
        FROM accounts a
        LEFT JOIN transactions t ON a.id = t.account_id
        GROUP BY a.id, a.user_id, a.tenant_id, a.name, a.type, a.initial_balance, a.current_balance
    ''')
    db.commit()
    print('✅ View v_account_balances criada com sucesso!')
    
    # Testar
    cursor.execute('SELECT * FROM v_account_balances LIMIT 1')
    print(f'✅ Teste OK - Colunas: {[desc[0] for desc in cursor.description]}')
    
except Exception as e:
    print(f'❌ Erro: {e}')
    db.rollback()

db.close()
