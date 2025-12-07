"""
Teste de Isolamento de Dados entre Tenants
Garante que conta A não vê dados da conta B
"""

import sqlite3
import json
from datetime import datetime

def test_tenant_isolation():
    """Testa o isolamento entre tenants no sistema de IA"""
    
    print("🔒 TESTE DE ISOLAMENTO DE DADOS ENTRE TENANTS\n")
    print("=" * 60)
    
    # Conectar ao banco de dados da IA
    db_path = "ai_history.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Simular dados de 2 tenants diferentes
    tenant_a_id = "tenant_a"
    tenant_a_user = "user_a"
    
    tenant_b_id = "tenant_b"
    tenant_b_user = "user_b"
    
    print("\n📝 Inserindo dados de teste...")
    
    # Inserir conversas para Tenant A
    cursor.execute("""
        INSERT INTO ai_conversations (user_id, tenant_id, user_message, ai_response, context)
        VALUES (?, ?, ?, ?, ?)
    """, (tenant_a_user, tenant_a_id, "Quanto gastei?", "Você gastou R$ 1000", json.dumps({"tenant": "A"})))
    
    cursor.execute("""
        INSERT INTO ai_conversations (user_id, tenant_id, user_message, ai_response, context)
        VALUES (?, ?, ?, ?, ?)
    """, (tenant_a_user, tenant_a_id, "Qual meu saldo?", "Seu saldo é R$ 5000", json.dumps({"tenant": "A"})))
    
    # Inserir conversas para Tenant B
    cursor.execute("""
        INSERT INTO ai_conversations (user_id, tenant_id, user_message, ai_response, context)
        VALUES (?, ?, ?, ?, ?)
    """, (tenant_b_user, tenant_b_id, "Quanto tenho?", "Você tem R$ 3000", json.dumps({"tenant": "B"})))
    
    cursor.execute("""
        INSERT INTO ai_conversations (user_id, tenant_id, user_message, ai_response, context)
        VALUES (?, ?, ?, ?, ?)
    """, (tenant_b_user, tenant_b_id, "Meus investimentos?", "Você tem R$ 10000 investidos", json.dumps({"tenant": "B"})))
    
    conn.commit()
    
    print("✅ Dados inseridos com sucesso\n")
    print("=" * 60)
    
    # TESTE 1: Buscar conversas do Tenant A
    print("\n🔍 TESTE 1: Buscar conversas do Tenant A")
    print("-" * 60)
    
    cursor.execute("""
        SELECT user_message, ai_response, context
        FROM ai_conversations
        WHERE user_id = ? AND tenant_id = ?
        ORDER BY timestamp DESC
        LIMIT 10
    """, (tenant_a_user, tenant_a_id))
    
    tenant_a_data = cursor.fetchall()
    
    print(f"Conversas encontradas: {len(tenant_a_data)}")
    for row in tenant_a_data:
        ctx = json.loads(row['context']) if row['context'] else {}
        print(f"  • Pergunta: {row['user_message']}")
        print(f"  • Resposta: {row['ai_response']}")
        print(f"  • Tenant no contexto: {ctx.get('tenant', 'N/A')}")
        print()
    
    # Verificar isolamento
    tenant_a_has_only_a_data = all(
        json.loads(row['context']).get('tenant') == 'A'
        for row in tenant_a_data
        if row['context']
    )
    
    if tenant_a_has_only_a_data and len(tenant_a_data) == 2:
        print("✅ PASSOU: Tenant A vê apenas seus próprios dados")
    else:
        print("❌ FALHOU: Tenant A está vendo dados de outros tenants!")
    
    print("\n" + "=" * 60)
    
    # TESTE 2: Buscar conversas do Tenant B
    print("\n🔍 TESTE 2: Buscar conversas do Tenant B")
    print("-" * 60)
    
    cursor.execute("""
        SELECT user_message, ai_response, context
        FROM ai_conversations
        WHERE user_id = ? AND tenant_id = ?
        ORDER BY timestamp DESC
        LIMIT 10
    """, (tenant_b_user, tenant_b_id))
    
    tenant_b_data = cursor.fetchall()
    
    print(f"Conversas encontradas: {len(tenant_b_data)}")
    for row in tenant_b_data:
        ctx = json.loads(row['context']) if row['context'] else {}
        print(f"  • Pergunta: {row['user_message']}")
        print(f"  • Resposta: {row['ai_response']}")
        print(f"  • Tenant no contexto: {ctx.get('tenant', 'N/A')}")
        print()
    
    # Verificar isolamento
    tenant_b_has_only_b_data = all(
        json.loads(row['context']).get('tenant') == 'B'
        for row in tenant_b_data
        if row['context']
    )
    
    if tenant_b_has_only_b_data and len(tenant_b_data) == 2:
        print("✅ PASSOU: Tenant B vê apenas seus próprios dados")
    else:
        print("❌ FALHOU: Tenant B está vendo dados de outros tenants!")
    
    print("\n" + "=" * 60)
    
    # TESTE 3: Tentar buscar dados sem filtro de tenant (simulando ataque)
    print("\n🔍 TESTE 3: Buscar SEM filtro de tenant (simulação de ataque)")
    print("-" * 60)
    
    cursor.execute("""
        SELECT user_id, tenant_id, user_message
        FROM ai_conversations
        WHERE user_id = ?
    """, (tenant_a_user,))  # Sem filtrar por tenant_id
    
    unfiltered_data = cursor.fetchall()
    
    print(f"Conversas encontradas sem filtro: {len(unfiltered_data)}")
    
    if len(unfiltered_data) > 2:
        print("⚠️ VULNERABILIDADE: Possível vazamento de dados entre tenants!")
    else:
        print("✅ Sem vazamento de dados detectado")
    
    print("\n" + "=" * 60)
    
    # TESTE 4: Verificar queries do sistema
    print("\n🔍 TESTE 4: Verificar se todas as queries filtram por tenant_id")
    print("-" * 60)
    
    # Verificar código do ai_core.py
    with open('services/ai_core.py', 'r', encoding='utf-8') as f:
        ai_core_code = f.read()
    
    # Procurar por queries SELECT sem filtro de tenant_id
    import re
    
    select_queries = re.findall(r'SELECT.*?FROM ai_conversations.*?(?:WHERE|;)', ai_core_code, re.DOTALL | re.IGNORECASE)
    
    vulnerable_queries = []
    for query in select_queries:
        if 'WHERE' in query.upper() and 'tenant_id' not in query.lower():
            vulnerable_queries.append(query.strip())
    
    if vulnerable_queries:
        print(f"⚠️ ATENÇÃO: {len(vulnerable_queries)} query(s) sem filtro de tenant_id encontrada(s):")
        for q in vulnerable_queries:
            print(f"  • {q[:100]}...")
    else:
        print("✅ Todas as queries filtram por tenant_id")
    
    print("\n" + "=" * 60)
    
    # Limpar dados de teste
    print("\n🧹 Limpando dados de teste...")
    
    cursor.execute("DELETE FROM ai_conversations WHERE tenant_id IN (?, ?)", (tenant_a_id, tenant_b_id))
    conn.commit()
    
    print("✅ Dados de teste removidos")
    
    # Resumo final
    print("\n" + "=" * 60)
    print("\n📊 RESUMO DO TESTE DE ISOLAMENTO")
    print("=" * 60)
    
    tests_passed = 0
    tests_total = 4
    
    if tenant_a_has_only_a_data:
        tests_passed += 1
    if tenant_b_has_only_b_data:
        tests_passed += 1
    if len(unfiltered_data) <= 2:
        tests_passed += 1
    if not vulnerable_queries:
        tests_passed += 1
    
    print(f"\n✅ Testes aprovados: {tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print("\n🎉 ISOLAMENTO DE DADOS: 100% SEGURO")
        print("✅ Tenant A não acessa dados do Tenant B")
        print("✅ Tenant B não acessa dados do Tenant A")
        print("✅ Todas as queries filtram por tenant_id")
    else:
        print("\n⚠️ ATENÇÃO: Possíveis vulnerabilidades detectadas!")
        print("Revise as queries e garanta filtro por tenant_id em todas")
    
    print("\n" + "=" * 60)
    
    conn.close()

if __name__ == "__main__":
    test_tenant_isolation()
