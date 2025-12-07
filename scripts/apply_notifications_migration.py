"""
Script para aplicar migração das tabelas de notificações
"""
import sqlite3
import os

def apply_migration():
    db_path = 'bws_finance.db'
    migration_path = 'migrations/create_notifications_tables.sql'
    
    if not os.path.exists(db_path):
        print(f"❌ Database não encontrado: {db_path}")
        return False
    
    if not os.path.exists(migration_path):
        print(f"❌ Arquivo de migração não encontrado: {migration_path}")
        return False
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Ler e executar script SQL
        with open(migration_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        cursor.executescript(sql_script)
        conn.commit()
        
        # Verificar tabelas criadas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%notif%'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print("✅ Migração aplicada com sucesso!")
        print(f"📋 Tabelas criadas: {', '.join(tables)}")
        
        # Verificar estrutura da tabela notifications
        cursor.execute("PRAGMA table_info(notifications)")
        columns = cursor.fetchall()
        print(f"\n📊 Estrutura da tabela 'notifications':")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao aplicar migração: {str(e)}")
        return False

if __name__ == '__main__':
    apply_migration()
