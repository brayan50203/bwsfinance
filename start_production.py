#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BWS Finance - Production Server Starter
Usa Waitress WSGI server para evitar problemas do Flask dev server
"""
import os
import sys

# Forçar UTF-8 no stdout/stderr
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Suprimir todos os warnings
import warnings
warnings.filterwarnings('ignore')

from app import app, init_db, seed_default_data

def main():
    # Inicializar banco se não existir
    db_path = 'bws_finance.db'
    if not os.path.exists(db_path):
        print('[DB] Criando banco de dados...')
        init_db()
        seed_default_data()
        print('[DB] Banco criado com sucesso!')
    
    # Iniciar scheduler
    try:
        from scheduler import start_scheduler
        start_scheduler()
        print('[SCHEDULER] Iniciado com sucesso')
    except Exception as e:
        print(f'[SCHEDULER] Erro: {e}')
    
    # Iniciar servidor Waitress
    host = '0.0.0.0'
    port = 5000
    
    print('=' * 60)
    print('[BWS FINANCE] Servidor Iniciado!')
    print(f'[LOCAL] http://127.0.0.1:{port}')
    print(f'[NETWORK] http://45.173.36.138:{port}')
    print(f'[DASHBOARD] http://127.0.0.1:{port}/dashboard')
    print('=' * 60)
    print('[INFO] Pressione CTRL+C para parar o servidor')
    print('=' * 60)
    
    try:
        from waitress import serve
        serve(app, host=host, port=port, threads=8, _quiet=True)
    except KeyboardInterrupt:
        print('\n[STOP] Servidor parado pelo usuario')
    except Exception as e:
        print(f'[ERROR] {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
