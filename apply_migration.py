"""
Script para aplicar migration de accounts
"""
import sqlite3
import os
import shutil
from datetime import datetime

DB_FILE = 'bws_finance.db'
MIGRATION_FILE = 'migration_accounts_fix.sql'
BACKUP_FILE = f'bws_finance_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'

def apply_migration():
    print("🔧 Aplicando migration de Accounts...")
    
    # 1. Backup
    if os.path.exists(DB_FILE):
        print(f"📦 Criando backup: {BACKUP_FILE}")
        shutil.copy2(DB_FILE, BACKUP_FILE)
    
    # 2. Conectar ao banco
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 3. Ler e aplicar migration
    print("📝 Lendo migration SQL...")
    with open(MIGRATION_FILE, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    print("⚙️ Executando migration...")
    try:
        cursor.executescript(sql_script)
        conn.commit()
        print("✅ Migration aplicada com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao aplicar migration: {e}")
        conn.rollback()
        return False
    
    # 4. Verificar resultado
    print("\n🔍 Verificando estrutura:")
    
    # Ver colunas de accounts
    cursor.execute("PRAGMA table_info(accounts)")
    columns = cursor.fetchall()
    print("\n📊 Colunas de accounts:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # Ver view v_account_balances
    print("\n📊 View v_account_balances:")
    try:
        cursor.execute("SELECT * FROM v_account_balances LIMIT 0")
        view_columns = [desc[0] for desc in cursor.description]
        for col in view_columns:
            print(f"  - {col}")
    except Exception as e:
        print(f"  ❌ Erro: {e}")
    
    # Ver triggers
    print("\n🔧 Triggers:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger'")
    triggers = cursor.fetchall()
    for trigger in triggers:
        print(f"  - {trigger[0]}")
    
    conn.close()
    print("\n✅ Migration finalizada!")
    print(f"💾 Backup salvo em: {BACKUP_FILE}")
    return True

if __name__ == '__main__':
    if not os.path.exists(MIGRATION_FILE):
        print(f"❌ Arquivo {MIGRATION_FILE} não encontrado!")
        exit(1)
    
    apply_migration()
