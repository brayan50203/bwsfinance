# -*- coding: utf-8 -*-
"""
Script para iniciar o servidor BWS Finance usando Waitress (production-ready)
"""
import sys
import os

# Configurar encoding para UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Importar a aplicação Flask
from app import app

# Iniciar scheduler
from scheduler import start_scheduler
start_scheduler()

print("\n" + "="*60)
print(" BWS FINANCE - SERVIDOR INICIADO")
print("="*60)
print(f" Local:    http://127.0.0.1:5000")
print(f" Network:  http://45.173.36.138:5000")
print(f" Dashboard: http://127.0.0.1:5000/dashboard")
print("="*60)
print(" Pressione CTRL+C para parar o servidor")
print("="*60 + "\n")

# Usar o servidor de desenvolvimento do Flask
# (Em produção, use waitress ou gunicorn)
try:
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True,
        use_reloader=False
    )
except KeyboardInterrupt:
    print("\n[STOP] Servidor encerrado pelo usuario")
except Exception as e:
    print(f"\n[ERRO] {e}")
    import traceback
    traceback.print_exc()
