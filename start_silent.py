#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BWS Finance - Silent Server Starter
Redireciona todo output para arquivo de log
"""
import os
import sys
from datetime import datetime

# Redirecionar stdout/stderr para arquivo ANTES de importar qualquer coisa
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'server_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

sys.stdout = open(log_file, 'w', encoding='utf-8')
sys.stderr = sys.stdout

# Suprimir warnings
import warnings
warnings.filterwarnings('ignore')

print(f'[{datetime.now()}] Iniciando BWS Finance...')

from app import app, init_db, seed_default_data

def main():
    # Inicializar banco se não existir
    db_path = 'bws_finance.db'
    if not os.path.exists(db_path):
        print(f'[{datetime.now()}] Criando banco de dados...')
        init_db()
        seed_default_data()
        print(f'[{datetime.now()}] Banco criado!')
    
    # Iniciar scheduler
    try:
        from scheduler import start_scheduler
        start_scheduler()
        print(f'[{datetime.now()}] Scheduler iniciado')
    except Exception as e:
        print(f'[{datetime.now()}] Erro scheduler: {e}')
    
    # Servidor
    host = '0.0.0.0'
    port = 5000
    
    print(f'[{datetime.now()}] Servidor iniciado em http://127.0.0.1:{port}')
    print(f'[{datetime.now()}] Dashboard: http://127.0.0.1:{port}/dashboard')
    print(f'[{datetime.now()}] Log: {log_file}')
    
    try:
        from waitress import serve
        serve(app, host=host, port=port, threads=8)
    except KeyboardInterrupt:
        print(f'[{datetime.now()}] Servidor parado')
    except Exception as e:
        print(f'[{datetime.now()}] Erro: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
