import sys
import traceback
from app import app, get_db

# Configurar contexto do Flask
with app.app_context():
    with app.test_request_context('/?year=2025&month=10'):
        try:
            from app import dashboard
            
            # Simular sessão de usuário
            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess['user_id'] = 1
            
            print("🧪 Testando função dashboard()...")
            result = dashboard()
            print("✅ Dashboard funcionou!")
            print(f"Tipo do resultado: {type(result)}")
            
        except Exception as e:
            print(f"❌ ERRO no dashboard:")
            print(f"Tipo: {type(e).__name__}")
            print(f"Mensagem: {e}")
            print("\n=== TRACEBACK COMPLETO ===")
            traceback.print_exc()
