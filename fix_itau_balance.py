import sqlite3

db = sqlite3.connect('bws_finance.db')
cursor = db.cursor()

# ID da conta Itau
itau_id = '2447222e-7c61-4ecf-b063-e2ba6e101b67'

# Buscar transações totais
transactions_sum = cursor.execute("""
    SELECT SUM(CASE WHEN type = 'Receita' THEN value ELSE -value END)
    FROM transactions
    WHERE account_id = ?
    AND status = 'Pago'
""", (itau_id,)).fetchone()[0] or 0

print(f"\n📊 ANÁLISE DA CONTA ITAU:\n")
print(f"   Total de transações: R$ {transactions_sum:,.2f}")
print(f"   Saldo real atual: R$ 2.585,10")
print(f"   Saldo inicial necessário: R$ {2585.10 - transactions_sum:,.2f}")

# Calcular saldo inicial correto
saldo_inicial_correto = 2585.10 - transactions_sum

# Atualizar conta Itau
cursor.execute("""
    UPDATE accounts 
    SET initial_balance = ?,
        current_balance = ?
    WHERE id = ?
""", (saldo_inicial_correto, 2585.10, itau_id))

db.commit()

print(f"\n✅ CONTA ITAU ATUALIZADA:")
print(f"   Saldo Inicial: R$ {saldo_inicial_correto:,.2f}")
print(f"   Saldo Atual: R$ 2.585,10")

db.close()
print("\n✅ Recarregue a página de contas!\n")
