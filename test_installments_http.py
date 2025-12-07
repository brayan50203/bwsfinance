"""
Testes HTTP da API REST de Parcelamentos
Testa os 7 endpoints via requests HTTP
"""

import requests
import json
from colorama import Fore, Style, init
from datetime import datetime, timedelta
import uuid

init(autoreset=True)

BASE_URL = "http://localhost:5000"
session = requests.Session()

# Variáveis globais para armazenar IDs
user_id = None
tenant_id = None
account_id = None
card_id = None
category_id = None
installment_id = None

def print_test(name):
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"[TESTE] {name}")
    print(f"{'='*60}{Style.RESET_ALL}")

def print_success(message):
    print(f"{Fore.GREEN}✅ PASSOU{Style.RESET_ALL} - {message}")

def print_error(message):
    print(f"{Fore.RED}❌ FALHOU{Style.RESET_ALL} - {message}")

def print_info(message):
    print(f"{Fore.YELLOW}ℹ️  {message}{Style.RESET_ALL}")

# ==================== SETUP ====================

print_test("SETUP: Criar usuário e dados de teste")

try:
    # Registrar usuário
    response = session.post(f"{BASE_URL}/register", data={
        'name': 'Teste Installments',
        'email': f'teste.installments.{uuid.uuid4().hex[:8]}@bws.com',
        'password': 'senha123',
        'tenant_subdomain': f'tenant-inst-{uuid.uuid4().hex[:6]}'
    }, allow_redirects=False)
    
    if response.status_code in [200, 302]:
        print_success("Usuário registrado e logado")
        
        # Pegar user_id da sessão (via endpoint de teste)
        response = session.get(f"{BASE_URL}/api/summary")
        if response.status_code == 200:
            data = response.json()
            user_id = data.get('user_id')
            print_info(f"User ID: {user_id}")
        
        # Criar conta via API
        response = session.post(f"{BASE_URL}/api/accounts", json={
            'name': 'Conta Teste Parcelamentos',
            'type': 'Corrente',
            'initial_balance': 10000.00
        })
        
        if response.status_code == 201:
            account_id = response.json()['account']['id']
            print_success(f"Conta criada: {account_id}")
        else:
            print_error(f"Erro ao criar conta: {response.text}")
    
    else:
        print_error(f"Erro no registro: {response.status_code}")
        print(response.text)
        exit(1)

except Exception as e:
    print_error(f"Erro no setup: {str(e)}")
    exit(1)

# ==================== TESTE 1: Criar Parcelamento ====================

print_test("TESTE 1: POST /api/installments - Criar parcelamento de R$ 3.000 em 10x")

try:
    first_due_date = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
    
    response = session.post(f"{BASE_URL}/api/installments", json={
        'description': 'Notebook Dell Inspiron 15',
        'total_amount': 3000.00,
        'installment_count': 10,
        'interest_rate': 0,
        'first_due_date': first_due_date,
        'account_id': account_id
    })
    
    if response.status_code == 201:
        data = response.json()
        installment_id = data['installment_id']
        transaction_ids = data['transaction_ids']
        
        if len(transaction_ids) == 10:
            print_success(f"Parcelamento criado com 10 transações")
            print_info(f"ID: {installment_id[:8]}...")
            print_info(f"Mensagem: {data['message']}")
        else:
            print_error(f"Esperado 10 transações, recebeu {len(transaction_ids)}")
    else:
        print_error(f"Status {response.status_code}: {response.text}")

except Exception as e:
    print_error(f"Exceção: {str(e)}")

# ==================== TESTE 2: Listar Parcelamentos ====================

print_test("TESTE 2: GET /api/installments - Listar parcelamentos")

try:
    response = session.get(f"{BASE_URL}/api/installments")
    
    if response.status_code == 200:
        data = response.json()
        installments = data['installments']
        
        if len(installments) > 0:
            installment = installments[0]
            print_success(f"Encontrados {len(installments)} parcelamento(s)")
            print_info(f"Descrição: {installment['description']}")
            print_info(f"Total: R$ {installment['total_amount']:.2f}")
            print_info(f"Parcelas: {installment['installment_count']}x R$ {installment['installment_value']:.2f}")
            print_info(f"Status: {installment['current_status']}")
        else:
            print_error("Nenhum parcelamento encontrado")
    else:
        print_error(f"Status {response.status_code}: {response.text}")

except Exception as e:
    print_error(f"Exceção: {str(e)}")

# ==================== TESTE 3: Detalhes do Parcelamento ====================

print_test("TESTE 3: GET /api/installments/:id - Buscar detalhes com transações")

try:
    response = session.get(f"{BASE_URL}/api/installments/{installment_id}")
    
    if response.status_code == 200:
        data = response.json()
        installment = data['installment']
        transactions = installment['transactions']
        
        if len(transactions) == 10:
            print_success(f"Parcelamento com {len(transactions)} transações")
            
            # Verificar primeira e última parcela
            first = transactions[0]
            last = transactions[-1]
            
            print_info(f"Primeira parcela: {first['installment_number']}/10 - R$ {first['value']:.2f} - {first['due_date']}")
            print_info(f"Última parcela: {last['installment_number']}/10 - R$ {last['value']:.2f} - {last['due_date']}")
            
            # Verificar soma total
            total = sum(t['value'] for t in transactions)
            if abs(total - 3000.00) < 0.01:
                print_success(f"Soma das parcelas: R$ {total:.2f} (correto)")
            else:
                print_error(f"Soma incorreta: R$ {total:.2f} (esperado R$ 3000.00)")
        else:
            print_error(f"Esperado 10 transações, recebeu {len(transactions)}")
    else:
        print_error(f"Status {response.status_code}: {response.text}")

except Exception as e:
    print_error(f"Exceção: {str(e)}")

# ==================== TESTE 4: Cronograma de Pagamento ====================

print_test("TESTE 4: GET /api/installments/:id/schedule - Ver cronograma")

try:
    response = session.get(f"{BASE_URL}/api/installments/{installment_id}/schedule")
    
    if response.status_code == 200:
        data = response.json()
        schedule = data['schedule']
        summary = data['summary']
        
        print_success(f"Cronograma carregado com {len(schedule)} parcelas")
        print_info(f"Total de parcelas: {summary['total_installments']}")
        print_info(f"Pagas: {summary['paid_installments']}")
        print_info(f"Pendentes: {summary['pending_installments']}")
        print_info(f"Total pago: R$ {summary['total_paid']:.2f}")
        print_info(f"Total pendente: R$ {summary['total_pending']:.2f}")
        
        # Verificar que todas estão pendentes
        if summary['pending_installments'] == 10 and summary['paid_installments'] == 0:
            print_success("Todas as 10 parcelas estão pendentes (correto)")
        else:
            print_error("Estado inesperado das parcelas")
    else:
        print_error(f"Status {response.status_code}: {response.text}")

except Exception as e:
    print_error(f"Exceção: {str(e)}")

# ==================== TESTE 5: Atualizar Parcelamento ====================

print_test("TESTE 5: PUT /api/installments/:id - Atualizar descrição")

try:
    response = session.put(f"{BASE_URL}/api/installments/{installment_id}", json={
        'description': 'Notebook Dell Inspiron 15 (i7, 16GB, 512GB SSD)'
    })
    
    if response.status_code == 200:
        print_success("Descrição atualizada")
        
        # Verificar alteração
        response = session.get(f"{BASE_URL}/api/installments/{installment_id}")
        if response.status_code == 200:
            new_desc = response.json()['installment']['description']
            if '(i7, 16GB, 512GB SSD)' in new_desc:
                print_success(f"Descrição confirmada: {new_desc}")
            else:
                print_error(f"Descrição não atualizada: {new_desc}")
    else:
        print_error(f"Status {response.status_code}: {response.text}")

except Exception as e:
    print_error(f"Exceção: {str(e)}")

# ==================== TESTE 6: Pagar Todas as Parcelas ====================

print_test("TESTE 6: POST /api/installments/:id/pay-all - Pagar todas")

try:
    # Verificar saldo antes
    response = session.get(f"{BASE_URL}/api/accounts/{account_id}")
    balance_before = response.json()['account']['current_balance']
    print_info(f"Saldo antes: R$ {balance_before:.2f}")
    
    # Pagar todas
    response = session.post(f"{BASE_URL}/api/installments/{installment_id}/pay-all")
    
    if response.status_code == 200:
        data = response.json()
        print_success(data['message'])
        print_info(f"Parcelas pagas: {data['transactions_paid']}")
        print_info(f"Valor total: R$ {data['total_amount']:.2f}")
        
        # Verificar saldo depois
        response = session.get(f"{BASE_URL}/api/accounts/{account_id}")
        balance_after = response.json()['account']['current_balance']
        print_info(f"Saldo depois: R$ {balance_after:.2f}")
        
        expected_balance = balance_before - 3000.00
        if abs(balance_after - expected_balance) < 0.01:
            print_success(f"Saldo atualizado corretamente (R$ {balance_before:.2f} → R$ {balance_after:.2f})")
        else:
            print_error(f"Saldo incorreto: R$ {balance_after:.2f} (esperado R$ {expected_balance:.2f})")
        
        # Verificar cronograma atualizado
        response = session.get(f"{BASE_URL}/api/installments/{installment_id}/schedule")
        if response.status_code == 200:
            summary = response.json()['summary']
            if summary['paid_installments'] == 10 and summary['pending_installments'] == 0:
                print_success("Todas as 10 parcelas marcadas como pagas")
            else:
                print_error(f"Estado inesperado: {summary['paid_installments']}/10 pagas")
    else:
        print_error(f"Status {response.status_code}: {response.text}")

except Exception as e:
    print_error(f"Exceção: {str(e)}")

# ==================== TESTE 7: Criar Parcelamento com Juros ====================

print_test("TESTE 7: POST /api/installments - Parcelamento com 2.5% de juros")

try:
    first_due_date = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')
    
    response = session.post(f"{BASE_URL}/api/installments", json={
        'description': 'Empréstimo Pessoal',
        'total_amount': 1000.00,
        'installment_count': 5,
        'interest_rate': 2.5,  # 2.5% ao mês
        'first_due_date': first_due_date,
        'account_id': account_id
    })
    
    if response.status_code == 201:
        data = response.json()
        installment_id_2 = data['installment_id']
        
        # Verificar cálculo de juros
        # total_com_juros = 1000 * (1 + 0.025 * 5) = 1000 * 1.125 = 1125
        # parcela = 1125 / 5 = 225
        
        if '225.00' in data['message']:
            print_success(f"Juros calculado corretamente: {data['message']}")
            
            # Verificar no cronograma
            response = session.get(f"{BASE_URL}/api/installments/{installment_id_2}/schedule")
            if response.status_code == 200:
                schedule = response.json()['schedule']
                first_installment_value = schedule[0]['value']
                
                if abs(first_installment_value - 225.00) < 0.01:
                    print_success(f"Valor da parcela: R$ {first_installment_value:.2f} (correto)")
                else:
                    print_error(f"Valor da parcela incorreto: R$ {first_installment_value:.2f} (esperado R$ 225.00)")
        else:
            print_error(f"Valor de parcela inesperado: {data['message']}")
    else:
        print_error(f"Status {response.status_code}: {response.text}")

except Exception as e:
    print_error(f"Exceção: {str(e)}")

# ==================== TESTE 8: Cancelar Parcelamento ====================

print_test("TESTE 8: DELETE /api/installments/:id - Cancelar parcelamento")

try:
    # Criar novo parcelamento para cancelar
    first_due_date = (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d')
    
    response = session.post(f"{BASE_URL}/api/installments", json={
        'description': 'Compra para Cancelar',
        'total_amount': 600.00,
        'installment_count': 6,
        'interest_rate': 0,
        'first_due_date': first_due_date,
        'account_id': account_id
    })
    
    if response.status_code == 201:
        installment_id_3 = response.json()['installment_id']
        print_info(f"Parcelamento criado: {installment_id_3[:8]}...")
        
        # Cancelar
        response = session.delete(f"{BASE_URL}/api/installments/{installment_id_3}")
        
        if response.status_code == 200:
            data = response.json()
            print_success(data['message'])
            
            # Verificar status
            response = session.get(f"{BASE_URL}/api/installments/{installment_id_3}")
            if response.status_code == 200:
                status = response.json()['installment']['current_status']
                if status == 'cancelled':
                    print_success(f"Status alterado para 'cancelled'")
                else:
                    print_error(f"Status inesperado: {status}")
            
            # Verificar que transações foram deletadas
            response = session.get(f"{BASE_URL}/api/installments/{installment_id_3}/schedule")
            if response.status_code == 200:
                summary = response.json()['summary']
                if summary['total_installments'] == 0:
                    print_success("Todas as transações pendentes foram deletadas")
                else:
                    print_error(f"Ainda existem {summary['total_installments']} transações")
        else:
            print_error(f"Status {response.status_code}: {response.text}")
    else:
        print_error(f"Erro ao criar parcelamento: {response.text}")

except Exception as e:
    print_error(f"Exceção: {str(e)}")

# ==================== RESUMO ====================

print(f"\n{Fore.CYAN}{'='*60}")
print(f"RESUMO DOS TESTES HTTP")
print(f"{'='*60}{Style.RESET_ALL}")
print(f"{Fore.GREEN}✅ Todos os testes foram executados!{Style.RESET_ALL}")
print(f"{Fore.YELLOW}ℹ️  Verifique os resultados acima para detalhes{Style.RESET_ALL}")
print()
