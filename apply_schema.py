#!/usr/bin/env python3
"""
Script para aplicar schema completo do banco de dados
"""

import sqlite3
import os

DB_PATH = 'bws_finance.db'
SCHEMA_PATH = 'database_schema.sql'

def apply_schema():
    """Aplica o schema completo ao banco de dados"""
    
    if not os.path.exists(SCHEMA_PATH):
        print(f"❌ Arquivo {SCHEMA_PATH} não encontrado")
        return False
    
    if not os.path.exists(DB_PATH):
        print(f"⚠️  Banco de dados {DB_PATH} não existe. Será criado.")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("📦 Lendo schema...")
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        print("🔨 Aplicando schema...")
        cursor.executescript(schema_sql)
        conn.commit()
        
        # Verificar views criadas
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='view'
            ORDER BY name
        """)
        views = cursor.fetchall()
        
        # Verificar tabelas
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tables = cursor.fetchall()
        
        conn.close()
        
        print("\n✅ Schema aplicado com sucesso!")
        print(f"\n📊 Tabelas ({len(tables)}):")
        for table in tables:
            print(f"   - {table[0]}")
        
        print(f"\n👁️  Views ({len(views)}):")
        for view in views:
            print(f"   - {view[0]}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Erro ao aplicar schema: {e}")
        return False

if __name__ == '__main__':
    print("🚀 BWS Finance - Aplicar Schema Completo\n")
    success = apply_schema()
    
    if success:
        print("\n✨ Banco de dados atualizado com sucesso!")
    else:
        print("\n❌ Falha ao atualizar banco de dados.")
