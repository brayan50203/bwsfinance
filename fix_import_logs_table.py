import sqlite3

db = sqlite3.connect('bws_finance.db')

try:
    # Verificar estrutura atual
    print("📋 Estrutura atual da tabela import_logs:")
    columns = db.execute("PRAGMA table_info(import_logs)").fetchall()
    for col in columns:
        print(f"  - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
    
    # Adicionar coluna card_id se não existir
    try:
        db.execute("ALTER TABLE import_logs ADD COLUMN card_id TEXT")
        print("\n✅ Coluna card_id adicionada!")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("\n⚠️  Coluna card_id já existe")
        else:
            raise
    
    # Precisamos recriar a tabela para tornar account_id opcional
    print("\n🔄 Recriando tabela import_logs com account_id opcional...")
    
    # 1. Criar nova tabela com estrutura correta
    db.execute("""
        CREATE TABLE IF NOT EXISTS import_logs_new (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            account_id TEXT,
            card_id TEXT,
            file_name TEXT NOT NULL,
            file_type TEXT NOT NULL,
            total_transactions INTEGER DEFAULT 0,
            imported_transactions INTEGER DEFAULT 0,
            duplicated_transactions INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (tenant_id) REFERENCES tenants(id),
            FOREIGN KEY (account_id) REFERENCES accounts(id),
            FOREIGN KEY (card_id) REFERENCES cards(id)
        )
    """)
    
    # 2. Copiar dados antigos
    db.execute("""
        INSERT INTO import_logs_new 
        SELECT id, user_id, tenant_id, account_id, NULL as card_id, 
               file_name, file_type, total_transactions, 
               imported_transactions, duplicated_transactions, created_at
        FROM import_logs
    """)
    
    # 3. Remover tabela antiga
    db.execute("DROP TABLE import_logs")
    
    # 4. Renomear nova tabela
    db.execute("ALTER TABLE import_logs_new RENAME TO import_logs")
    
    db.commit()
    print("✅ Tabela import_logs atualizada com sucesso!")
    
    # Verificar nova estrutura
    print("\n📋 Nova estrutura da tabela import_logs:")
    columns = db.execute("PRAGMA table_info(import_logs)").fetchall()
    for col in columns:
        print(f"  - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
