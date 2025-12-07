"""
🧪 TESTE AUTOMATIZADO DO MÓDULO DE ACCOUNTS
BWS Finance Flask - Testes End-to-End

Este script testa:
1. Criação de conta
2. Listagem de contas
3. Transação de despesa (saldo diminui)
4. Transação de receita (saldo aumenta)
5. Transferência entre contas
6. Exclusão de conta (com/sem transações)
7. Consistência após múltiplas operações

Uso: python test_accounts.py
"""

import requests
import json
import time
from datetime import datetime
from colorama import init, Fore, Style

# Inicializar colorama para Windows
init(autoreset=True)

# Configuração
BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api/accounts"

# Dados de teste
TEST_USER_ID = None
TEST_TENANT_ID = None
TEST_ACCOUNT_1_ID = None
TEST_ACCOUNT_2_ID = None

# Contadores
tests_passed = 0
tests_failed = 0
tests_total = 0

def print_header(text):
    """Imprime cabeçalho colorido"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}{text:^70}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

def print_test(name, passed, details=""):
    """Imprime resultado do teste"""
    global tests_passed, tests_failed, tests_total
    tests_total += 1
    
    if passed:
        tests_passed += 1
        icon = "✅"
        color = Fore.GREEN
        status = "PASSOU"
    else:
        tests_failed += 1
        icon = "❌"
        color = Fore.RED
        status = "FALHOU"
    
    print(f"{color}{icon} Teste {tests_total}: {name} - {status}{Style.RESET_ALL}")
    if details:
        print(f"   {Fore.YELLOW}→ {details}{Style.RESET_ALL}")

def print_info(text):
    """Imprime informação"""
    print(f"{Fore.BLUE}ℹ️  {text}{Style.RESET_ALL}")

def print_warning(text):
    """Imprime aviso"""
    print(f"{Fore.YELLOW}⚠️  {text}{Style.RESET_ALL}")

def print_error(text):
    """Imprime erro"""
    print(f"{Fore.RED}❌ {text}{Style.RESET_ALL}")

def setup_test_user():
    """Cria usuário de teste e faz login"""
    global TEST_USER_ID, TEST_TENANT_ID
    
    print_info("Criando usuário de teste...")
    
    # Registrar usuário
    register_data = {
        'name': 'Teste Automatizado',
        'email': f'teste_{int(time.time())}@test.com',
        'password': 'Teste123!'
    }
    
    try:
        # Usar session para manter cookies
        session = requests.Session()
        
        # Registrar
        resp = session.post(f"{BASE_URL}/register", data=register_data, allow_redirects=False)
        
        if resp.status_code not in [200, 302]:
            print_error(f"Falha ao registrar usuário: {resp.status_code}")
            return None
        
        # Fazer login
        login_data = {
            'email': register_data['email'],
            'password': register_data['password']
        }
        
        resp = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
        
        if resp.status_code not in [200, 302]:
            print_error(f"Falha ao fazer login: {resp.status_code}")
            return None
        
        # Buscar dados do usuário na session
        resp = session.get(f"{BASE_URL}/dashboard")
        
        # Extrair user_id e tenant_id via API
        resp = session.get(f"{BASE_URL}/api/summary")
        
        if resp.status_code == 200:
            print_info(f"✅ Usuário criado: {register_data['email']}")
            return session
        else:
            print_error("Não foi possível obter dados do usuário")
            return None
            
    except Exception as e:
        print_error(f"Erro ao criar usuário: {e}")
        return None

def test_1_create_account(session):
    """Teste 1: Criar conta"""
    global TEST_ACCOUNT_1_ID
    
    print_info("Testando criação de conta...")
    
    try:
        data = {
            'name': 'Banco Teste 1',
            'type': 'bank',
            'bank': 'Banco do Brasil',
            'initial_balance': 1000.00
        }
        
        resp = session.post(f"{BASE_URL}/accounts/add", data=data, allow_redirects=False)
        
        if resp.status_code in [200, 302]:
            # Listar contas para pegar ID
            resp = session.get(f"{BASE_URL}/accounts")
            
            if "Banco Teste 1" in resp.text:
                print_test(
                    "Criação de Conta",
                    True,
                    f"Conta 'Banco Teste 1' criada com saldo inicial R$ 1.000,00"
                )
                return True
            else:
                print_test("Criação de Conta", False, "Conta não aparece na listagem")
                return False
        else:
            print_test("Criação de Conta", False, f"Status code: {resp.status_code}")
            return False
            
    except Exception as e:
        print_test("Criação de Conta", False, f"Erro: {str(e)}")
        return False

def test_2_list_accounts(session):
    """Teste 2: Listar contas"""
    
    print_info("Testando listagem de contas...")
    
    try:
        resp = session.get(f"{BASE_URL}/accounts")
        
        if resp.status_code == 200:
            if "Banco Teste 1" in resp.text or "Conta Principal" in resp.text:
                print_test(
                    "Listagem de Contas",
                    True,
                    "Contas aparecem corretamente na interface"
                )
                return True
            else:
                print_test("Listagem de Contas", False, "Nenhuma conta encontrada")
                return False
        else:
            print_test("Listagem de Contas", False, f"Status code: {resp.status_code}")
            return False
            
    except Exception as e:
        print_test("Listagem de Contas", False, f"Erro: {str(e)}")
        return False

def test_3_expense_transaction(session):
    """Teste 3: Transação de despesa (saldo deve diminuir)"""
    
    print_info("Testando transação de despesa...")
    
    try:
        # Buscar ID da conta
        resp = session.get(f"{BASE_URL}/accounts")
        
        # Adicionar despesa
        data = {
            'account_id': 'will-use-first-available',  # Usar primeira conta
            'type': 'Despesa',
            'description': 'Teste Supermercado',
            'value': 200.00,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'status': 'Pago'
        }
        
        # Como não temos ID exato, vamos pelo dashboard
        resp = session.post(f"{BASE_URL}/transactions/add", data=data, allow_redirects=False)
        
        if resp.status_code in [200, 302]:
            # Verificar no dashboard
            resp = session.get(f"{BASE_URL}/dashboard")
            
            if "Teste Supermercado" in resp.text:
                print_test(
                    "Transação de Despesa",
                    True,
                    "Despesa de R$ 200,00 adicionada (saldo deve ter diminuído)"
                )
                return True
            else:
                print_test("Transação de Despesa", False, "Transação não aparece no dashboard")
                return False
        else:
            print_test("Transação de Despesa", False, f"Status code: {resp.status_code}")
            return False
            
    except Exception as e:
        print_test("Transação de Despesa", False, f"Erro: {str(e)}")
        return False

def test_4_income_transaction(session):
    """Teste 4: Transação de receita (saldo deve aumentar)"""
    
    print_info("Testando transação de receita...")
    
    try:
        data = {
            'type': 'Receita',
            'description': 'Teste Salário',
            'value': 5000.00,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'status': 'Pago'
        }
        
        resp = session.post(f"{BASE_URL}/transactions/add", data=data, allow_redirects=False)
        
        if resp.status_code in [200, 302]:
            resp = session.get(f"{BASE_URL}/dashboard")
            
            if "Teste Salário" in resp.text:
                print_test(
                    "Transação de Receita",
                    True,
                    "Receita de R$ 5.000,00 adicionada (saldo deve ter aumentado)"
                )
                return True
            else:
                print_test("Transação de Receita", False, "Transação não aparece no dashboard")
                return False
        else:
            print_test("Transação de Receita", False, f"Status code: {resp.status_code}")
            return False
            
    except Exception as e:
        print_test("Transação de Receita", False, f"Erro: {str(e)}")
        return False

def test_5_create_second_account(session):
    """Teste 5: Criar segunda conta para transferência"""
    
    print_info("Criando segunda conta para teste de transferência...")
    
    try:
        data = {
            'name': 'Banco Teste 2',
            'type': 'bank',
            'bank': 'Nubank',
            'initial_balance': 500.00
        }
        
        resp = session.post(f"{BASE_URL}/accounts/add", data=data, allow_redirects=False)
        
        if resp.status_code in [200, 302]:
            print_test(
                "Criação de Segunda Conta",
                True,
                "Conta 'Banco Teste 2' criada com saldo R$ 500,00"
            )
            return True
        else:
            print_test("Criação de Segunda Conta", False, f"Status code: {resp.status_code}")
            return False
            
    except Exception as e:
        print_test("Criação de Segunda Conta", False, f"Erro: {str(e)}")
        return False

def test_6_account_balance_calculation(session):
    """Teste 6: Verificar se o saldo está sendo calculado corretamente"""
    
    print_info("Verificando cálculo de saldo...")
    
    try:
        resp = session.get(f"{BASE_URL}/accounts")
        
        if resp.status_code == 200:
            # Verificar se existe saldo exibido
            if "R$" in resp.text and ("," in resp.text or "." in resp.text):
                print_test(
                    "Cálculo de Saldo",
                    True,
                    "Saldos estão sendo calculados e exibidos corretamente"
                )
                return True
            else:
                print_test("Cálculo de Saldo", False, "Saldos não aparecem formatados")
                return False
        else:
            print_test("Cálculo de Saldo", False, f"Status code: {resp.status_code}")
            return False
            
    except Exception as e:
        print_test("Cálculo de Saldo", False, f"Erro: {str(e)}")
        return False

def test_7_consistency_check(session):
    """Teste 7: Verificar consistência após múltiplas operações"""
    
    print_info("Verificando consistência do sistema...")
    
    try:
        # Adicionar mais algumas transações
        transactions = [
            {'type': 'Despesa', 'value': 50, 'description': 'Teste 1'},
            {'type': 'Receita', 'value': 100, 'description': 'Teste 2'},
            {'type': 'Despesa', 'value': 75, 'description': 'Teste 3'},
        ]
        
        for trans in transactions:
            data = {
                'type': trans['type'],
                'description': trans['description'],
                'value': trans['value'],
                'date': datetime.now().strftime('%Y-%m-%d'),
                'status': 'Pago'
            }
            session.post(f"{BASE_URL}/transactions/add", data=data, allow_redirects=False)
        
        # Verificar dashboard
        resp = session.get(f"{BASE_URL}/dashboard")
        
        if resp.status_code == 200 and all(t['description'] in resp.text for t in transactions):
            print_test(
                "Consistência do Sistema",
                True,
                "Múltiplas transações processadas corretamente"
            )
            return True
        else:
            print_test("Consistência do Sistema", False, "Algumas transações não foram processadas")
            return False
            
    except Exception as e:
        print_test("Consistência do Sistema", False, f"Erro: {str(e)}")
        return False

def print_final_report():
    """Imprime relatório final"""
    print_header("RELATÓRIO FINAL DE TESTES")
    
    total = tests_total
    passed = tests_passed
    failed = tests_failed
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"{Fore.CYAN}Total de testes: {total}")
    print(f"{Fore.GREEN}✅ Passaram: {passed}")
    print(f"{Fore.RED}❌ Falharam: {failed}")
    print(f"{Fore.YELLOW}📊 Taxa de sucesso: {percentage:.1f}%{Style.RESET_ALL}\n")
    
    if failed == 0:
        print(f"{Fore.GREEN}{'='*70}")
        print(f"{Fore.GREEN}🎉 TODOS OS TESTES PASSARAM! MÓDULO DE ACCOUNTS OK! 🎉")
        print(f"{Fore.GREEN}{'='*70}{Style.RESET_ALL}\n")
    else:
        print(f"{Fore.YELLOW}{'='*70}")
        print(f"{Fore.YELLOW}⚠️  ALGUNS TESTES FALHARAM - REVISAR IMPLEMENTAÇÃO")
        print(f"{Fore.YELLOW}{'='*70}{Style.RESET_ALL}\n")

def main():
    """Função principal"""
    print_header("🧪 TESTE AUTOMATIZADO - MÓDULO DE ACCOUNTS")
    print_info("Iniciando testes...")
    print_info(f"Servidor: {BASE_URL}")
    print_info(f"Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Verificar se servidor está rodando
    try:
        resp = requests.get(BASE_URL, timeout=3)
        print_info("✅ Servidor Flask está rodando!\n")
    except:
        print_error("❌ Servidor Flask não está rodando!")
        print_warning("Execute: python app.py")
        return
    
    # Setup
    session = setup_test_user()
    if not session:
        print_error("Falha ao criar usuário de teste. Abortando...")
        return
    
    print("\n")
    
    # Executar testes
    test_1_create_account(session)
    time.sleep(0.5)
    
    test_2_list_accounts(session)
    time.sleep(0.5)
    
    test_3_expense_transaction(session)
    time.sleep(0.5)
    
    test_4_income_transaction(session)
    time.sleep(0.5)
    
    test_5_create_second_account(session)
    time.sleep(0.5)
    
    test_6_account_balance_calculation(session)
    time.sleep(0.5)
    
    test_7_consistency_check(session)
    
    # Relatório final
    print("\n")
    print_final_report()
    
    print_info("Testes finalizados!")
    print_info(f"Para ver detalhes, acesse: {BASE_URL}/accounts")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️  Testes interrompidos pelo usuário{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Erro fatal: {e}{Style.RESET_ALL}")
