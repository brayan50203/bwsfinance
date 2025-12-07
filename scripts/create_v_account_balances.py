import sqlite3
import os

DB = os.path.join(os.path.dirname(__file__), '..', 'bws_finance.db')
DB = os.path.abspath(DB)
print('Using DB:', DB)

sql = '''
CREATE VIEW IF NOT EXISTS v_account_balances AS
SELECT 
    a.id,
    a.user_id,
    a.tenant_id,
    a.name,
    a.type,
    a.initial_balance,
    a.initial_balance + COALESCE(
        (SELECT SUM(CASE 
            WHEN t.type = 'Receita' THEN t.value
            WHEN t.type = 'Despesa' THEN -t.value
            ELSE 0
        END)
        FROM transactions t
        WHERE t.account_id = a.id AND t.status = 'Pago'),
        0
    ) as current_balance
FROM accounts a
WHERE a.active = 1;
'''

conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.executescript(sql)
conn.commit()
print('v_account_balances view created or already exists')

# Confirm
cur.execute("SELECT name FROM sqlite_master WHERE type='view' AND name='v_account_balances'")
print('Exists:', cur.fetchone() is not None)
conn.close()
