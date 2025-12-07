#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para adicionar coluna quantity à tabela investments
"""

import sqlite3
import os

def add_quantity_column():
    """Adiciona coluna quantity se não existir"""
    db_path = 'bws_finance.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se coluna já existe
        cursor.execute("PRAGMA table_info(investments)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'quantity' in columns:
            print("✅ Coluna 'quantity' já existe!")
            return True
        
        # Adicionar coluna quantity
        print("📝 Adicionando coluna 'quantity' à tabela investments...")
        cursor.execute("""
            ALTER TABLE investments 
            ADD COLUMN quantity REAL DEFAULT 1
        """)
        
        # Atualizar investimentos existentes com quantity = 1
        cursor.execute("""
            UPDATE investments 
            SET quantity = 1 
            WHERE quantity IS NULL
        """)
        
        conn.commit()
        print("✅ Coluna 'quantity' adicionada com sucesso!")
        print("✅ Investimentos existentes atualizados com quantity = 1")
        
        # Verificar resultado
        cursor.execute("PRAGMA table_info(investments)")
        columns_after = [col[1] for col in cursor.fetchall()]
        print(f"\n📊 Colunas na tabela investments: {', '.join(columns_after)}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao adicionar coluna: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🔧 Iniciando migração do banco de dados...\n")
    success = add_quantity_column()
    
    if success:
        print("\n✅ Migração concluída com sucesso!")
        print("🚀 Você pode reiniciar o servidor agora.")
    else:
        print("\n❌ Migração falhou. Verifique os erros acima.")
