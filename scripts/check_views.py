import sqlite3
import os

DB = os.path.join(os.path.dirname(__file__), '..', 'bws_finance.db')
DB = os.path.abspath(DB)
print('Checking DB:', DB)
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("SELECT name, type, sql FROM sqlite_master WHERE type IN ('view','table') ORDER BY type, name;")
rows = cur.fetchall()
views = [r for r in rows if r[1] == 'view']
print('\nViews found:')
for v in views:
    print('-', v[0])

found = any(v[0] == 'v_account_balances' for v in views)
print('\nHas v_account_balances:', found)

if found:
    cur.execute("SELECT sql FROM sqlite_master WHERE type='view' AND name='v_account_balances'")
    print('\nSQL for v_account_balances:\n')
    print(cur.fetchone()[0])

conn.close()
