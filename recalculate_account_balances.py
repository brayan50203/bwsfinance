import sqlite3

db = sqlite3.connect('bws_finance.db')
cursor = db.cursor()
tenant_id = 'f8c9a8dc-c8e9-472a-85f1-c202893033e6'

print("\n🔄 RECALCULANDO SALDOS DAS CONTAS...\n")

# Buscar todas as contas
accounts = cursor.execute("""
    SELECT id, name, initial_balance 
    FROM accounts 
    WHERE tenant_id = ?
""", (tenant_id,)).fetchall()

for account in accounts:
    account_id = account[0]
    account_name = account[1]
    initial_balance = account[2] or 0
    
    # Calcular saldo real baseado nas transações
    transactions = cursor.execute("""
        SELECT SUM(CASE WHEN type = 'Receita' THEN value ELSE -value END)
        FROM transactions
        WHERE account_id = ?
        AND status = 'Pago'
    """, (account_id,)).fetchone()
    
    transaction_total = transactions[0] or 0
    new_balance = initial_balance + transaction_total
    
    print(f"📊 {account_name}")
    print(f"   Saldo Inicial: R$ {initial_balance:,.2f}")
    print(f"   Transações: R$ {transaction_total:,.2f}")
    print(f"   Saldo Calculado: R$ {new_balance:,.2f}")
    
    # Verificar saldo atual no banco
    current = cursor.execute("SELECT current_balance FROM accounts WHERE id = ?", (account_id,)).fetchone()
    if current:
        print(f"   Saldo no Banco: R$ {current[0]:,.2f}")
    
    # Atualizar saldo
    cursor.execute("""
        UPDATE accounts 
        SET current_balance = ?
        WHERE id = ?
    """, (new_balance, account_id))
    
    print(f"   ✅ Atualizado!\n")

db.commit()
db.close()

print("✅ Todos os saldos recalculados!\n")
