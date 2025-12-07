"""
Script para testar a rota /investments diretamente
"""
import sys
sys.path.insert(0, '.')

from app import app, get_db

# Simular contexto da aplicação
with app.app_context():
    # Simular request context
    with app.test_request_context():
        # Simular sessão de usuário
        from flask import session
        
        # Buscar primeiro usuário do banco
        db = get_db()
        user = db.execute("SELECT * FROM users LIMIT 1").fetchone()
        
        if not user:
            print("❌ Nenhum usuário encontrado no banco!")
            print("   Crie um usuário primeiro em /register")
            sys.exit(1)
        
        print(f"✅ Usuário encontrado: {user['name']} ({user['email']})")
        
        # Simular sessão
        session['user_id'] = user['id']
        session['user_email'] = user['email']
        
        # Importar e executar a função da rota
        from app import investments_page
        
        print("\n🔄 Tentando executar investments_page()...")
        
        try:
            result = investments_page()
            print("✅ Função executou SEM ERRO!")
            print(f"   Tipo de retorno: {type(result)}")
            
            if hasattr(result, 'status_code'):
                print(f"   Status code: {result.status_code}")
            
        except Exception as e:
            print(f"❌ ERRO ao executar investments_page():")
            print(f"   {type(e).__name__}: {e}")
            
            import traceback
            print("\n📋 Traceback completo:")
            traceback.print_exc()
        
        db.close()
