#!/usr/bin/env python
"""
Iniciar servidor simples
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("\n[INIT] Importando app...")
from app import app

print(f"[OK] App importada! Routes: {len(list(app.url_map.iter_rules()))}")
print("\n" + "="*60)
print("🚀 BWS Finance - Servidor iniciado!")
print("="*60)
print("📍 http://localhost:5000")
print("="*60 + "\n")

# Tentar iniciar com o servidor mais simples possível
if __name__ == '__main__':
    try:
        print("[INIT] Iniciando Flask app.run()...")
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=False,
            use_reloader=False,
            use_debugger=False,
            threaded=True
        )
    except Exception as e:
        print(f"[ERRO] {e}")
        import traceback
        traceback.print_exc()
