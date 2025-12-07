"""
Migração: Criar tabela de logs de importação
"""
import sqlite3

def create_import_logs_table():
    conn = sqlite3.connect('bws_finance.db')
    cursor = conn.cursor()
    
    try:
        print("📦 Criando tabela import_logs...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS import_logs (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                tenant_id TEXT NOT NULL,
                account_id TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_type TEXT NOT NULL,
                total_transactions INTEGER DEFAULT 0,
                imported_transactions INTEGER DEFAULT 0,
                duplicated_transactions INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
                FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
            )
        """)
        
        # Criar índices para performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_import_logs_user 
            ON import_logs(user_id, tenant_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_import_logs_date 
            ON import_logs(created_at DESC)
        """)
        
        conn.commit()
        print("✅ Tabela import_logs criada com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    create_import_logs_table()
