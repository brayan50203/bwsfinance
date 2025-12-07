"""
Testes do Módulo de Parcelamentos
Testa diretamente no banco de dados (sem HTTP)
"""

import sqlite3
import uuid
from datetime import datetime, timedelta
from colorama import Fore, Style, init

init(autoreset=True)

def get_db():
    db = sqlite3.connect('bws_finance.db')
    db.row_factory = sqlite3.Row
    return db

def print_test(name, success, details=""):
    status = f"{Fore.GREEN}✅ PASSOU" if success else f"{Fore.RED}❌ FALHOU"
    print(f"{status} - {name}")
    if details:
        print(f"   {Fore.YELLOW}{details}")

# Setup: Criar usuário e conta de teste
db = get_db()
cursor = db.cursor()

# Limpar dados de teste antigos
cursor.execute("DELETE FROM transactions WHERE description LIKE '%TESTE%'")
cursor.execute("DELETE FROM installments WHERE description LIKE '%TESTE%'")
cursor.execute("DELETE FROM accounts WHERE name = 'Conta Teste Installments'")
cursor.execute("DELETE FROM users WHERE email = 'teste.installments@bws.com'")
db.commit()

# Criar tenant
tenant_id = str(uuid.uuid4())
cursor.execute("""
    INSERT OR IGNORE INTO tenants (id, name, subdomain, active)
    VALUES (?, ?, ?, ?)
""", (tenant_id, 'Tenant Teste', 'teste', 1))

# Criar usuário
user_id = str(uuid.uuid4())
cursor.execute("""
    INSERT INTO users (id, tenant_id, name, email, password_hash, active)
    VALUES (?, ?, ?, ?, ?, ?)
""", (user_id, tenant_id, 'Usuário Teste', 'teste.installments@bws.com', 'hash123', 1))

# Criar conta
account_id = str(uuid.uuid4())
cursor.execute("""
    INSERT INTO accounts (id, user_id, tenant_id, name, type, initial_balance, current_balance)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", (account_id, user_id, tenant_id, 'Conta Teste Installments', 'Corrente', 5000.00, 5000.00))

# Criar categoria
cursor.execute("SELECT id FROM categories WHERE name = 'Eletrônicos' LIMIT 1")
category = cursor.fetchone()
category_id = category['id'] if category else None

db.commit()

print(f"\n{Fore.CYAN}{'='*60}")
print(f"{Fore.CYAN}TESTES DO MÓDULO DE PARCELAMENTOS")
print(f"{Fore.CYAN}{'='*60}\n")

# ==================== TESTE 1: Criar Parcelamento ====================
print(f"{Fore.MAGENTA}[TESTE 1] Criar parcelamento de R$ 3.000 em 10x")

installment_id = str(uuid.uuid4())
first_due_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')

cursor.execute("""
    INSERT INTO installments (
        id, user_id, tenant_id, account_id, category_id,
        description, total_amount, installment_count, installment_value,
        interest_rate, first_due_date, current_status, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    installment_id,
    user_id,
    tenant_id,
    account_id,
    category_id,
    'Notebook Dell TESTE',
    3000.00,
    10,
    300.00,  # 3000 / 10
    0,
    first_due_date,
    'active',
    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
))

db.commit()

cursor.execute("SELECT * FROM installments WHERE id = ?", (installment_id,))
installment = cursor.fetchone()

test1 = (
    installment is not None and
    installment['total_amount'] == 3000.00 and
    installment['installment_count'] == 10 and
    installment['current_status'] == 'active'
)

print_test(
    "Criar registro de parcelamento",
    test1,
    f"ID: {installment_id[:8]}..., 10x R$ 300.00"
)

# ==================== TESTE 2: Gerar Transações das Parcelas ====================
print(f"\n{Fore.MAGENTA}[TESTE 2] Gerar 10 transações automaticamente")

from dateutil.relativedelta import relativedelta

transaction_ids = []
first_due = datetime.strptime(first_due_date, '%Y-%m-%d')

for i in range(1, 11):
    due_date = first_due + relativedelta(months=(i - 1))
    
    # Última parcela pode ter ajuste de centavos
    if i == 10:
        cursor.execute("""
            SELECT COALESCE(SUM(value), 0) as total_paid
            FROM transactions
            WHERE installment_id = ?
        """, (installment_id,))
        total_paid = cursor.fetchone()['total_paid']
        value = round(3000.00 - total_paid, 2)
    else:
        value = 300.00
    
    transaction_id = str(uuid.uuid4())
    description = f"Notebook Dell TESTE ({i}/10)"
    
    cursor.execute("""
        INSERT INTO transactions (
            id, user_id, tenant_id, account_id, category_id,
            type, description, value, date, due_date, status,
            installment_id, installment_number, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        transaction_id,
        user_id,
        tenant_id,
        account_id,
        category_id,
        'Despesa',
        description,
        value,
        due_date.strftime('%Y-%m-%d'),
        due_date.strftime('%Y-%m-%d'),
        'Pendente',
        installment_id,
        i,
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    
    transaction_ids.append(transaction_id)

db.commit()

cursor.execute("""
    SELECT COUNT(*) as total FROM transactions
    WHERE installment_id = ?
""", (installment_id,))
count = cursor.fetchone()['total']

cursor.execute("""
    SELECT SUM(value) as total_value FROM transactions
    WHERE installment_id = ?
""", (installment_id,))
total_value = cursor.fetchone()['total_value']

test2 = count == 10 and abs(total_value - 3000.00) < 0.01

print_test(
    "Gerar 10 transações com valores corretos",
    test2,
    f"Transações: {count}, Total: R$ {total_value:.2f}"
)

# ==================== TESTE 3: Verificar Saldo da Conta ====================
print(f"\n{Fore.MAGENTA}[TESTE 3] Verificar que saldo NÃO mudou (parcelas pendentes)")

cursor.execute("SELECT current_balance FROM accounts WHERE id = ?", (account_id,))
balance = cursor.fetchone()['current_balance']

test3 = balance == 5000.00

print_test(
    "Saldo da conta permanece inalterado",
    test3,
    f"Saldo: R$ {balance:.2f} (esperado R$ 5000.00)"
)

# ==================== TESTE 4: Pagar Primeira Parcela ====================
print(f"\n{Fore.MAGENTA}[TESTE 4] Pagar primeira parcela (R$ 300)")

cursor.execute("""
    UPDATE transactions
    SET status = 'Pago', paid_at = ?
    WHERE installment_id = ? AND installment_number = 1
""", (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), installment_id))

# Atualizar saldo da conta
cursor.execute("""
    UPDATE accounts
    SET current_balance = current_balance - 300.00
    WHERE id = ?
""", (account_id,))

db.commit()

cursor.execute("SELECT current_balance FROM accounts WHERE id = ?", (account_id,))
new_balance = cursor.fetchone()['current_balance']

cursor.execute("""
    SELECT status, paid_at FROM transactions
    WHERE installment_id = ? AND installment_number = 1
""", (installment_id,))
first_transaction = cursor.fetchone()

test4 = (
    new_balance == 4700.00 and
    first_transaction['status'] == 'Pago' and
    first_transaction['paid_at'] is not None
)

print_test(
    "Pagar primeira parcela atualiza saldo",
    test4,
    f"Novo saldo: R$ {new_balance:.2f} (esperado R$ 4700.00)"
)

# ==================== TESTE 5: Pagar Todas as Parcelas ====================
print(f"\n{Fore.MAGENTA}[TESTE 5] Pagar todas as parcelas restantes")

cursor.execute("""
    SELECT SUM(value) as total_pending FROM transactions
    WHERE installment_id = ? AND status = 'Pendente'
""", (installment_id,))
total_pending = cursor.fetchone()['total_pending']

cursor.execute("""
    UPDATE transactions
    SET status = 'Pago', paid_at = ?
    WHERE installment_id = ? AND status = 'Pendente'
""", (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), installment_id))

cursor.execute("""
    UPDATE accounts
    SET current_balance = current_balance - ?
    WHERE id = ?
""", (total_pending, account_id))

db.commit()

cursor.execute("SELECT current_balance FROM accounts WHERE id = ?", (account_id,))
final_balance = cursor.fetchone()['current_balance']

cursor.execute("""
    SELECT COUNT(*) as paid_count FROM transactions
    WHERE installment_id = ? AND status = 'Pago'
""", (installment_id,))
paid_count = cursor.fetchone()['paid_count']

expected_balance = 5000.00 - 3000.00  # 2000.00

test5 = paid_count == 10 and abs(final_balance - expected_balance) < 0.01

print_test(
    "Todas as 10 parcelas pagas, saldo final correto",
    test5,
    f"Parcelas pagas: {paid_count}/10, Saldo final: R$ {final_balance:.2f} (esperado R$ {expected_balance:.2f})"
)

# ==================== TESTE 6: View de Resumo ====================
print(f"\n{Fore.MAGENTA}[TESTE 6] Verificar view v_installments_summary")

cursor.execute("""
    SELECT * FROM v_installments_summary
    WHERE id = ?
""", (installment_id,))
summary = cursor.fetchone()

test6 = (
    summary is not None and
    summary['total_amount'] == 3000.00 and
    summary['total_paid'] == 3000.00
)

print_test(
    "View v_installments_summary mostra dados corretos",
    test6,
    f"Total: R$ {summary['total_amount']:.2f}, Pago: R$ {summary['total_paid']:.2f}"
)

# ==================== TESTE 7: Cancelar Parcelamento (com parcelas já pagas) ====================
print(f"\n{Fore.MAGENTA}[TESTE 7] Criar novo parcelamento e cancelar")

# Criar novo parcelamento
installment_id_2 = str(uuid.uuid4())
cursor.execute("""
    INSERT INTO installments (
        id, user_id, tenant_id, account_id, category_id,
        description, total_amount, installment_count, installment_value,
        interest_rate, first_due_date, current_status, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    installment_id_2,
    user_id,
    tenant_id,
    account_id,
    category_id,
    'Celular Samsung TESTE',
    1200.00,
    4,
    300.00,
    0,
    first_due_date,
    'active',
    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
))

# Gerar 4 transações
for i in range(1, 5):
    transaction_id = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO transactions (
            id, user_id, tenant_id, account_id, type, description, value,
            date, due_date, status, installment_id, installment_number, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        transaction_id, user_id, tenant_id, account_id, 'Despesa',
        f'Celular Samsung TESTE ({i}/4)', 300.00,
        datetime.now().strftime('%Y-%m-%d'),
        datetime.now().strftime('%Y-%m-%d'),
        'Pendente', installment_id_2, i,
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))

db.commit()

# Pagar primeira parcela
cursor.execute("""
    UPDATE transactions
    SET status = 'Pago', paid_at = ?
    WHERE installment_id = ? AND installment_number = 1
""", (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), installment_id_2))

db.commit()

# Cancelar parcelamento (deve manter a parcela paga e deletar as pendentes)
cursor.execute("""
    DELETE FROM transactions
    WHERE installment_id = ? AND status = 'Pendente'
""", (installment_id_2,))

deleted_count = cursor.rowcount

cursor.execute("""
    UPDATE installments
    SET current_status = 'cancelled', updated_at = ?
    WHERE id = ?
""", (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), installment_id_2))

db.commit()

cursor.execute("""
    SELECT COUNT(*) as remaining FROM transactions
    WHERE installment_id = ?
""", (installment_id_2,))
remaining = cursor.fetchone()['remaining']

cursor.execute("""
    SELECT current_status FROM installments WHERE id = ?
""", (installment_id_2,))
status = cursor.fetchone()['current_status']

test7 = (
    deleted_count == 3 and
    remaining == 1 and
    status == 'cancelled'
)

print_test(
    "Cancelar parcelamento mantém parcela paga e deleta pendentes",
    test7,
    f"Deletadas: {deleted_count}, Restantes: {remaining}, Status: {status}"
)

# ==================== TESTE 8: Parcelamento com Juros ====================
print(f"\n{Fore.MAGENTA}[TESTE 8] Criar parcelamento com 2.5% de juros")

# Calcular valor com juros: 1000 * (1 + 0.025 * 5) / 5 = 1125 / 5 = 225
installment_id_3 = str(uuid.uuid4())
cursor.execute("""
    INSERT INTO installments (
        id, user_id, tenant_id, account_id, category_id,
        description, total_amount, installment_count, installment_value,
        interest_rate, first_due_date, current_status, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    installment_id_3,
    user_id,
    tenant_id,
    account_id,
    category_id,
    'Curso Python TESTE',
    1000.00,
    5,
    225.00,  # (1000 * 1.125) / 5
    2.5,
    first_due_date,
    'active',
    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
))

db.commit()

cursor.execute("""
    SELECT total_amount, installment_value, interest_rate FROM installments
    WHERE id = ?
""", (installment_id_3,))
installment_with_interest = cursor.fetchone()

test8 = (
    installment_with_interest['interest_rate'] == 2.5 and
    installment_with_interest['installment_value'] == 225.00
)

print_test(
    "Parcelamento com juros calculado corretamente",
    test8,
    f"Total: R$ {installment_with_interest['total_amount']:.2f}, Parcela: R$ {installment_with_interest['installment_value']:.2f} (juros: {installment_with_interest['interest_rate']}%)"
)

# ==================== RESUMO FINAL ====================
tests = [test1, test2, test3, test4, test5, test6, test7, test8]
passed = sum(tests)
total = len(tests)
percentage = (passed / total) * 100

print(f"\n{Fore.CYAN}{'='*60}")
print(f"{Fore.CYAN}RESUMO DOS TESTES")
print(f"{Fore.CYAN}{'='*60}")
print(f"Total de testes: {total}")
print(f"{Fore.GREEN}Passou: {passed}")
print(f"{Fore.RED}Falhou: {total - passed}")
print(f"{Fore.YELLOW}Taxa de sucesso: {percentage:.1f}%")

if percentage == 100:
    print(f"\n{Fore.GREEN}🎉 TODOS OS TESTES PASSARAM! 🎉")
else:
    print(f"\n{Fore.RED}⚠️ ALGUNS TESTES FALHARAM ⚠️")

db.close()
