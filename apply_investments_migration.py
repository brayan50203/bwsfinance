#!/usr/bin/env python3
"""
Script para aplicar a migração do módulo de Investimentos
"""

import sqlite3
import os

DB_PATH = 'bws_finance.db'

def apply_migration():
    """Aplica a migração de investimentos"""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Banco de dados não encontrado: {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("📦 Aplicando migração de Investimentos...")
        
        # Ler o arquivo SQL de migração
        with open('migration_investments.sql', 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # Executar a migração
        cursor.executescript(migration_sql)
        conn.commit()
        
        # Verificar se as tabelas foram criadas
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('investments', 'investment_history')
        """)
        tables = cursor.fetchall()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='view' AND name IN ('v_investments_summary', 'v_investments_details')
        """)
        views = cursor.fetchall()
        
        print("\n✅ Migração aplicada com sucesso!")
        print(f"\n📊 Tabelas criadas: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")
        
        print(f"\n👁️  Views criadas: {len(views)}")
        for view in views:
            print(f"   - {view[0]}")
        
        # Mostrar estrutura da tabela investments
        cursor.execute("PRAGMA table_info(investments)")
        columns = cursor.fetchall()
        
        print("\n📋 Estrutura da tabela 'investments':")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Erro ao aplicar migração: {e}")
        return False

if __name__ == '__main__':
    print("🚀 BWS Finance - Migração de Investimentos\n")
    success = apply_migration()
    
    if success:
        print("\n✨ Migração concluída! Agora você pode usar o módulo de Investimentos.")
    else:
        print("\n❌ Falha na migração. Verifique os erros acima.")
