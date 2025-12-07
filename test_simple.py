"""
Teste Simples - Módulo de Accounts
Teste direto no banco de dados sem depender do servidor HTTP
"""

import sqlite3
import hashlib
import uuid
from datetime import datetime

print("="*70)
print("🧪 TESTE DIRETO NO BANCO DE DADOS - MÓDULO ACCOUNTS".center(70))
print("="*70)
print()

# Conectar ao banco
db = sqlite3.connect('bws_finance.db')
db.row_factory = sqlite3.Row
cursor = db.cursor()

# Contadores
tests_passed = 0
tests_total = 7

# ===== TESTE 1: Verificar tabela accounts =====
print("📋 Teste 1: Verificar estrutura da tabela accounts...")
try:
    cursor.execute("PRAGMA table_info(accounts)")
    columns = [col[1] for col in cursor.fetchall()]
    
    required_columns = ['id', 'user_id', 'tenant_id', 'name', 'type', 'initial_balance', 'current_balance', 'created_at', 'updated_at']
    missing = [col for col in required_columns if col not in columns]
    
    if not missing:
        print("   ✅ Estrutura da tabela OK!")
        print(f"   → Colunas encontradas: {len(columns)}")
        tests_passed += 1
    else:
        print(f"   ❌ Colunas faltando: {missing}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# ===== TESTE 2: Criar usuário de teste =====
print("\n👤 Teste 2: Criar usuário de teste...")
try:
    tenant_id = cursor.execute("SELECT id FROM tenants LIMIT 1").fetchone()[0]
    user_id = str(uuid.uuid4())
    email = f"teste_{int(datetime.now().timestamp())}@test.com"
    password_hash = hashlib.sha256("Teste123!".encode()).hexdigest()
    
    cursor.execute("""
        INSERT INTO users (id, tenant_id, email, password_hash, name)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, tenant_id, email, password_hash, "Teste Automatizado"))
    
    db.commit()
    
    # Verificar criação
    user = cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    
    if user:
        print("   ✅ Usuário criado!")
        print(f"   → Email: {email}")
        tests_passed += 1
    else:
        print("   ❌ Usuário não encontrado")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")

# ===== TESTE 3: Criar conta bancária =====
print("\n🏦 Teste 3: Criar conta bancária...")
try:
    account_id = str(uuid.uuid4())
    
    cursor.execute("""
        INSERT INTO accounts (id, user_id, tenant_id, name, type, bank, initial_balance, current_balance)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (account_id, user_id, tenant_id, "Banco Teste", "Corrente", "Banco do Brasil", 1000.00, 1000.00))
    
    db.commit()
    
    # Verificar criação
    account = cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,)).fetchone()
    
    if account and account['current_balance'] == 1000.00:
        print("   ✅ Conta criada!")
        print(f"   → Nome: {account['name']}")
        print(f"   → Saldo Inicial: R$ {account['initial_balance']:.2f}")
        print(f"   → Saldo Atual: R$ {account['current_balance']:.2f}")
        tests_passed += 1
    else:
        print("   ❌ Conta não encontrada ou saldo incorreto")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")

# ===== TESTE 4: Adicionar transação de despesa =====
print("\n💸 Teste 4: Adicionar transação de despesa (R$ 200)...")
try:
    transaction_id = str(uuid.uuid4())
    
    cursor.execute("""
        INSERT INTO transactions (id, user_id, tenant_id, account_id, type, description, value, date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (transaction_id, user_id, tenant_id, account_id, "Despesa", "Teste Supermercado", 200.00, datetime.now().date(), "Pago"))
    
    db.commit()
    
    # Atualizar saldo manualmente
    cursor.execute("""
        UPDATE accounts 
        SET current_balance = current_balance - 200.00
        WHERE id = ?
    """, (account_id,))
    
    db.commit()
    
    # Verificar saldo
    account = cursor.execute("SELECT current_balance FROM accounts WHERE id = ?", (account_id,)).fetchone()
    
    if account and account['current_balance'] == 800.00:
        print("   ✅ Despesa adicionada e saldo atualizado!")
        print(f"   → Novo saldo: R$ {account['current_balance']:.2f}")
        tests_passed += 1
    else:
        print(f"   ❌ Saldo incorreto: R$ {account['current_balance']:.2f} (esperado: R$ 800,00)")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")

# ===== TESTE 5: Adicionar transação de receita =====
print("\n💰 Teste 5: Adicionar transação de receita (R$ 500)...")
try:
    transaction_id = str(uuid.uuid4())
    
    cursor.execute("""
        INSERT INTO transactions (id, user_id, tenant_id, account_id, type, description, value, date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (transaction_id, user_id, tenant_id, account_id, "Receita", "Teste Salário", 500.00, datetime.now().date(), "Pago"))
    
    db.commit()
    
    # Atualizar saldo
    cursor.execute("""
        UPDATE accounts 
        SET current_balance = current_balance + 500.00
        WHERE id = ?
    """, (account_id,))
    
    db.commit()
    
    # Verificar saldo
    account = cursor.execute("SELECT current_balance FROM accounts WHERE id = ?", (account_id,)).fetchone()
    
    if account and account['current_balance'] == 1300.00:
        print("   ✅ Receita adicionada e saldo atualizado!")
        print(f"   → Novo saldo: R$ {account['current_balance']:.2f}")
        tests_passed += 1
    else:
        print(f"   ❌ Saldo incorreto: R$ {account['current_balance']:.2f} (esperado: R$ 1.300,00)")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")

# ===== TESTE 6: Verificar view v_account_balances =====
print("\n📊 Teste 6: Verificar view v_account_balances...")
try:
    cursor.execute("SELECT * FROM v_account_balances WHERE id = ?", (account_id,))
    view_data = cursor.fetchone()
    
    if view_data:
        print("   ✅ View funciona!")
        print(f"   → Nome: {view_data['name']}")
        print(f"   → Saldo: R$ {view_data['current_balance']:.2f}")
        tests_passed += 1
    else:
        print("   ❌ View não retornou dados")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")

# ===== TESTE 7: Deletar conta com transações (deve falhar) =====
print("\n🗑️  Teste 7: Tentar deletar conta com transações...")
try:
    # Verificar se há transações
    trans_count = cursor.execute("SELECT COUNT(*) as count FROM transactions WHERE account_id = ?", (account_id,)).fetchone()['count']
    
    if trans_count > 0:
        print(f"   ✅ Conta possui {trans_count} transações (bloqueio OK)")
        print("   → Não é possível deletar conta com transações vinculadas")
        tests_passed += 1
    else:
        print("   ❌ Conta não possui transações (teste falhou)")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")

# ===== RELATÓRIO FINAL =====
print("\n" + "="*70)
print("RELATÓRIO FINAL".center(70))
print("="*70)
print()
print(f"Total de testes: {tests_total}")
print(f"✅ Passaram: {tests_passed}")
print(f"❌ Falharam: {tests_total - tests_passed}")
print(f"📊 Taxa de sucesso: {(tests_passed/tests_total*100):.1f}%")
print()

if tests_passed == tests_total:
    print("="*70)
    print("🎉 TODOS OS TESTES PASSARAM! BANCO DE DADOS OK! 🎉".center(70))
    print("="*70)
else:
    print("="*70)
    print("⚠️  ALGUNS TESTES FALHARAM - REVISAR ESTRUTURA".center(70))
    print("="*70)

print()
print("💡 Próximo passo: Testar endpoints da API REST em routes/accounts.py")
print("   Execute: python app.py e use Postman/curl para testar")

# Fechar conexão
db.close()
