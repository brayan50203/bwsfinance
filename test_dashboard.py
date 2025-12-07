"""
Testar a rota do dashboard
"""
import sys
sys.path.insert(0, '.')

from app import app, get_db

with app.app_context():
    with app.test_request_context():
        from flask import session
        
        # Buscar usuário
        db = get_db()
        user = db.execute("SELECT * FROM users LIMIT 1").fetchone()
        
        if not user:
            print("❌ Nenhum usuário encontrado!")
            sys.exit(1)
        
        print(f"✅ Usuário: {user['name']}")
        
        # Simular sessão
        session['user_id'] = user['id']
        
        # Testar dashboard
        from app import dashboard
        
        print("\n🔄 Testando dashboard()...")
        
        try:
            result = dashboard()
            print("✅ Dashboard funcionou!")
            print(f"   Tipo: {type(result)}")
        except Exception as e:
            print(f"❌ Erro no dashboard:")
            print(f"   {type(e).__name__}: {e}")
            
            import traceback
            traceback.print_exc()
        
        db.close()
