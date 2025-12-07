"""
Script para aplicar migração de campos de recorrentes
"""
import sqlite3

def apply_migration():
    try:
        conn = sqlite3.connect('bws_finance.db')
        cursor = conn.cursor()
        
        print("🔧 Aplicando migração de recorrentes...")
        
        # Ler arquivo SQL
        with open('migration_add_recurring_fields.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Executar comandos um por um
        commands = sql_script.split(';')
        
        for cmd in commands:
            cmd = cmd.strip()
            if cmd and not cmd.startswith('--'):
                try:
                    cursor.execute(cmd)
                    print(f"✅ Comando executado")
                except sqlite3.OperationalError as e:
                    if 'duplicate column name' in str(e).lower() or 'already exists' in str(e).lower():
                        print(f"⏭️  Coluna já existe, pulando...")
                    else:
                        print(f"⚠️  Erro: {e}")
        
        conn.commit()
        print("✅ Migração aplicada com sucesso!")
        
        # Verificar estrutura
        cursor.execute("PRAGMA table_info(recurring_transactions)")
        columns = cursor.fetchall()
        
        print("\n📋 Colunas da tabela recurring_transactions:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao aplicar migração: {e}")

if __name__ == '__main__':
    apply_migration()
