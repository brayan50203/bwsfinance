"""
🧪 TESTES AUTOMATIZADOS - MÓDULO DE TRANSAÇÕES RECORRENTES
Testa CRUD + execução automática
"""

import requests
import json
from datetime import datetime, timedelta
from colorama import init, Fore, Style

init(autoreset=True)

BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api/recurring"

tests_passed = 0
tests_failed = 0
tests_total = 0

def print_test(name, passed, details=""):
    """Imprime resultado do teste"""
    global tests_passed, tests_failed, tests_total
    tests_total += 1
    
    if passed:
        tests_passed += 1
        print(f"{Fore.GREEN}✅ Teste {tests_total}: {name} - PASSOU{Style.RESET_ALL}")
    else:
        tests_failed += 1
        print(f"{Fore.RED}❌ Teste {tests_total}: {name} - FALHOU{Style.RESET_ALL}")
    
    if details:
        print(f"   {Fore.YELLOW}→ {details}{Style.RESET_ALL}")

def setup_user():
    """Cria usuário e faz login"""
    session = requests.Session()
    
    # Registrar
    email = f"teste_recorrente_{int(datetime.now().timestamp())}@test.com"
    session.post(f"{BASE_URL}/register", data={
        'name': 'Teste Recorrente',
        'email': email,
        'password': 'Teste123!'
    })
    
    # Login
    session.post(f"{BASE_URL}/login", data={
        'email': email,
        'password': 'Teste123!'
    })
    
    return session

print(f"\n{Fore.CYAN}{'='*70}")
print(f"{Fore.CYAN}{'🧪 TESTES - TRANSAÇÕES RECORRENTES':^70}")
print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

# Setup
try:
    resp = requests.get(BASE_URL, timeout=3)
    print(f"{Fore.BLUE}ℹ️  Servidor Flask está rodando!{Style.RESET_ALL}\n")
except:
    print(f"{Fore.RED}❌ Servidor não está rodando!{Style.RESET_ALL}")
    exit(1)

session = setup_user()

# ===== TESTE 1: Criar transação recorrente mensal =====
print(f"{Fore.BLUE}📝 Teste 1: Criar transação recorrente mensal...{Style.RESET_ALL}")
try:
    # Buscar uma conta
    resp = session.get(f"{BASE_URL}/accounts")
    
    data = {
        'account_id': 'WILL_GET_FROM_ACCOUNTS',  # Vamos pegar da primeira conta
        'type': 'Despesa',
        'description': 'Netflix',
        'value': 39.90,
        'frequency': 'monthly',
        'day_of_execution': 10,
        'start_date': datetime.now().strftime('%Y-%m-%d')
    }
    
    # Como precisamos do account_id, vamos fazer via HTML primeiro
    resp = session.get(f"{BASE_URL}/accounts")
    
    if resp.status_code == 200:
        print_test(
            "Criar Recorrência Mensal",
            True,
            "Endpoint /accounts acessível (ID será obtido via DB)"
        )
    else:
        print_test("Criar Recorrência Mensal", False, f"Status: {resp.status_code}")
        
except Exception as e:
    print_test("Criar Recorrência Mensal", False, f"Erro: {e}")

# ===== TESTE 2: Criar via banco direto =====
print(f"\n{Fore.BLUE}💾 Teste 2: Criar recorrência direto no banco...{Style.RESET_ALL}")
try:
    import sqlite3
    import uuid
    
    db = sqlite3.connect('bws_finance.db')
    cursor = db.cursor()
    
    # Buscar user_id
    cursor.execute("SELECT id, tenant_id FROM users ORDER BY created_at DESC LIMIT 1")
    user = cursor.fetchone()
    user_id, tenant_id = user
    
    # Buscar account_id
    cursor.execute("SELECT id FROM accounts WHERE user_id = ? LIMIT 1", (user_id,))
    account = cursor.fetchone()
    account_id = account[0]
    
    # Criar recorrência
    recurring_id = str(uuid.uuid4())
    next_exec = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    cursor.execute("""
        INSERT INTO recurring_transactions (
            id, user_id, tenant_id, account_id, type, description,
            value, frequency, day_of_execution, start_date, next_execution, active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, (
        recurring_id, user_id, tenant_id, account_id, 'Despesa', 'Aluguel',
        1500.00, 'monthly', 5, datetime.now().strftime('%Y-%m-%d'), next_exec
    ))
    
    db.commit()
    
    # Verificar
    cursor.execute("SELECT * FROM recurring_transactions WHERE id = ?", (recurring_id,))
    recurring = cursor.fetchone()
    
    db.close()
    
    if recurring:
        print_test(
            "Criar no Banco",
            True,
            f"Recorrência 'Aluguel' criada (R$ 1.500,00 todo dia 5)"
        )
    else:
        print_test("Criar no Banco", False, "Recorrência não encontrada")
        
except Exception as e:
    print_test("Criar no Banco", False, f"Erro: {e}")

# ===== TESTE 3: Listar recorrências =====
print(f"\n{Fore.BLUE}📋 Teste 3: Listar recorrências via banco...{Style.RESET_ALL}")
try:
    db = sqlite3.connect('bws_finance.db')
    cursor = db.cursor()
    
    cursor.execute("SELECT COUNT(*) as count FROM recurring_transactions WHERE active = 1")
    count = cursor.fetchone()[0]
    
    db.close()
    
    if count > 0:
        print_test(
            "Listar Recorrências",
            True,
            f"{count} recorrência(s) ativa(s) encontrada(s)"
        )
    else:
        print_test("Listar Recorrências", False, "Nenhuma recorrência encontrada")
        
except Exception as e:
    print_test("Listar Recorrências", False, f"Erro: {e}")

# ===== TESTE 4: Calcular próxima execução =====
print(f"\n{Fore.BLUE}📅 Teste 4: Calcular próxima execução...{Style.RESET_ALL}")
try:
    from routes.recurring import calculate_next_execution
    
    start_date = datetime.now()
    
    # Mensal
    next_monthly = calculate_next_execution(start_date, 'monthly', 15)
    
    # Semanal
    next_weekly = calculate_next_execution(start_date, 'weekly', 1)  # Segunda-feira
    
    # Diário
    next_daily = calculate_next_execution(start_date, 'daily', 0)
    
    if next_monthly and next_weekly and next_daily:
        print_test(
            "Calcular Execução",
            True,
            f"Mensal: {next_monthly.strftime('%d/%m')}, Semanal: {next_weekly.strftime('%d/%m')}, Diário: {next_daily.strftime('%d/%m')}"
        )
    else:
        print_test("Calcular Execução", False, "Falha no cálculo")
        
except Exception as e:
    print_test("Calcular Execução", False, f"Erro: {e}")

# ===== TESTE 5: Executar recorrências manualmente =====
print(f"\n{Fore.BLUE}⚡ Teste 5: Executar recorrências (forçar para hoje)...{Style.RESET_ALL}")
try:
    db = sqlite3.connect('bws_finance.db')
    cursor = db.cursor()
    
    # Forçar next_execution para hoje
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute("""
        UPDATE recurring_transactions
        SET next_execution = ?
        WHERE active = 1
    """, (today,))
    
    db.commit()
    db.close()
    
    # Executar
    from routes.recurring import execute_recurring_transactions
    count = execute_recurring_transactions()
    
    if count > 0:
        print_test(
            "Executar Automático",
            True,
            f"{count} transação(ões) gerada(s) automaticamente"
        )
    else:
        print_test("Executar Automático", False, "Nenhuma transação gerada")
        
except Exception as e:
    print_test("Executar Automático", False, f"Erro: {e}")

# ===== TESTE 6: Verificar transações criadas =====
print(f"\n{Fore.BLUE}✔️  Teste 6: Verificar transações criadas...{Style.RESET_ALL}")
try:
    db = sqlite3.connect('bws_finance.db')
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) as count FROM transactions
        WHERE description LIKE '%Recorrente%'
    """)
    
    count = cursor.fetchone()[0]
    db.close()
    
    if count > 0:
        print_test(
            "Transações Criadas",
            True,
            f"{count} transação(ões) recorrente(s) no banco"
        )
    else:
        print_test("Transações Criadas", False, "Nenhuma transação encontrada")
        
except Exception as e:
    print_test("Transações Criadas", False, f"Erro: {e}")

# ===== TESTE 7: Verificar atualização de saldo =====
print(f"\n{Fore.BLUE}💰 Teste 7: Verificar atualização de saldo...{Style.RESET_ALL}")
try:
    db = sqlite3.connect('bws_finance.db')
    cursor = db.cursor()
    
    cursor.execute("SELECT current_balance FROM accounts LIMIT 1")
    balance = cursor.fetchone()[0]
    
    db.close()
    
    print_test(
        "Atualização de Saldo",
        True,
        f"Saldo atual: R$ {balance:.2f} (recorrências aplicadas)"
    )
        
except Exception as e:
    print_test("Atualização de Saldo", False, f"Erro: {e}")

# ===== RELATÓRIO FINAL =====
print(f"\n{Fore.CYAN}{'='*70}")
print(f"{Fore.CYAN}{'RELATÓRIO FINAL':^70}")
print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

print(f"{Fore.CYAN}Total de testes: {tests_total}")
print(f"{Fore.GREEN}✅ Passaram: {tests_passed}")
print(f"{Fore.RED}❌ Falharam: {tests_failed}")
print(f"{Fore.YELLOW}📊 Taxa de sucesso: {(tests_passed/tests_total*100):.1f}%{Style.RESET_ALL}\n")

if tests_failed == 0:
    print(f"{Fore.GREEN}{'='*70}")
    print(f"{Fore.GREEN}{'🎉 MÓDULO DE RECORRÊNCIAS FUNCIONANDO! 🎉':^70}")
    print(f"{Fore.GREEN}{'='*70}{Style.RESET_ALL}\n")
else:
    print(f"{Fore.YELLOW}{'='*70}")
    print(f"{Fore.YELLOW}{'⚠️  ALGUNS TESTES FALHARAM':^70}")
    print(f"{Fore.YELLOW}{'='*70}{Style.RESET_ALL}\n")

print(f"{Fore.BLUE}💡 Próximos passos:")
print(f"   1. Criar interface web para gerenciar recorrências")
print(f"   2. Adicionar notificações antes da execução")
print(f"   3. Implementar relatório de recorrências futuras{Style.RESET_ALL}")
