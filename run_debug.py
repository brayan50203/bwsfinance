#!/usr/bin/env python
"""
Iniciar servidor com logging detalhado
"""
import sys
import os
import logging

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("[INIT] Importando app...")
from app import app

print(f"[OK] App importada! Routes: {len(list(app.url_map.iter_rules()))}")

# Verificar config
print(f"[CONFIG] Debug: {app.debug}")
print(f"[CONFIG] Testing: {app.testing}")
print(f"[CONFIG] Secret: {'SET' if app.secret_key else 'NOT SET'}")

print("\n" + "="*60)
print("🚀 BWS Finance - Iniciando servidor...")
print("="*60)

if __name__ == '__main__':
    try:
        print("[INIT] app.run(host=127.0.0.1, port=5000, debug=False, use_reloader=False)...")
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=False,
            use_reloader=False,
            use_debugger=False,
            use_evalex=False,
            threaded=True,
            #ssl_context='adhoc'  # Desabilitado
        )
        print("[OK] app.run() retornou normalmente")
    except Exception as e:
        print(f"[ERRO CRÍTICO] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
