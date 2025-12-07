with open('app.py', 'a', encoding='utf-8') as f:
    f.write("""

@app.route('/transactions')
@login_required  
def transactions():
    user = get_current_user()
    db = get_db()
    transactions = db.execute(\"\"\"
        SELECT t.*, a.name as account_name 
        FROM transactions t
        LEFT JOIN accounts a ON t.account_id = a.id
        WHERE t.user_id = ? AND t.tenant_id = ?
        ORDER BY t.date DESC LIMIT 50
    \"\"\", (user['id'], user['tenant_id'])).fetchall()
    accounts = db.execute("SELECT * FROM accounts WHERE user_id = ? AND tenant_id = ?", (user['id'], user['tenant_id'])).fetchall()
    total_income = sum(float(t['amount']) for t in transactions if t['type'] == 'income')
    total_expense = sum(float(t['amount']) for t in transactions if t['type'] == 'expense')
    balance = total_income - total_expense
    db.close()
    return render_template('transactions.html', user=user, transactions=[dict(t) for t in transactions], accounts=[dict(a) for a in accounts], total_income=total_income, total_expense=total_expense, balance=balance)
""")
print('✅ Rota adicionada!')
