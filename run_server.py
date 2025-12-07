#!/usr/bin/env python
"""
Iniciar servidor BWS Finance com Waitress (compatível com Windows)
"""
import sys
import os
import traceback

# Adicionar diretório ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("\n[INIT] Carregando Flask app...")
    from app import app
    print("[OK] Flask app carregado com sucesso!")
    
    print("[INIT] Carregando Waitress...")
    from waitress import serve
    print("[OK] Waitress carregado com sucesso!")
    
    print("\n" + "="*60)
    print("🚀 BWS Finance - Iniciando com Waitress...")
    print("="*60)
    print("📍 Servidor rodando em: http://localhost:5000")
    print("📍 Login: http://localhost:5000/login")
    print("📍 Dashboard: http://localhost:5000/dashboard")
    print("="*60 + "\n")
    
    # Iniciar servidor Waitress
    print("[INIT] Iniciando servidor Waitress na porta 5000...")
    serve(app, host='127.0.0.1', port=5000, threads=4)
    
except Exception as e:
    print(f"\n[ERRO] Falha ao iniciar servidor:")
    print(f"[ERROR] {type(e).__name__}: {e}")
    traceback.print_exc()
    sys.exit(1)
