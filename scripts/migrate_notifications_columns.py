"""
Migração: Adicionar colunas faltantes na tabela notifications
"""
import sqlite3

def migrate():
    conn = sqlite3.connect('bws_finance.db')
    cursor = conn.cursor()
    
    try:
        # Adicionar event_type (equivalente a category)
        try:
            cursor.execute("ALTER TABLE notifications ADD COLUMN event_type TEXT")
            print("✅ Coluna event_type adicionada")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("⚠️  Coluna event_type já existe")
            else:
                raise
        
        # Adicionar meta (equivalente a metadata)
        try:
            cursor.execute("ALTER TABLE notifications ADD COLUMN meta TEXT")
            print("✅ Coluna meta adicionada")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("⚠️  Coluna meta já existe")
            else:
                raise
        
        # Adicionar retry_count
        try:
            cursor.execute("ALTER TABLE notifications ADD COLUMN retry_count INTEGER DEFAULT 0")
            print("✅ Coluna retry_count adicionada")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("⚠️  Coluna retry_count já existe")
            else:
                raise
        
        # Adicionar error_message
        try:
            cursor.execute("ALTER TABLE notifications ADD COLUMN error_message TEXT")
            print("✅ Coluna error_message adicionada")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("⚠️  Coluna error_message já existe")
            else:
                raise
        
        # Adicionar scheduled_at
        try:
            cursor.execute("ALTER TABLE notifications ADD COLUMN scheduled_at DATETIME")
            print("✅ Coluna scheduled_at adicionada")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("⚠️  Coluna scheduled_at já existe")
            else:
                raise
        
        # Criar tabela user_notifications_settings
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_notifications_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL UNIQUE,
            tenant_id TEXT,
            notify_whatsapp INTEGER DEFAULT 1,
            notify_email INTEGER DEFAULT 1,
            notify_dashboard INTEGER DEFAULT 1,
            threshold_low_balance REAL DEFAULT 100.00,
            investment_alert_pct REAL DEFAULT 3.0,
            do_not_disturb_start TIME,
            do_not_disturb_end TIME,
            invoice_alert_days TEXT DEFAULT '3,1,0',
            weekly_summary INTEGER DEFAULT 1,
            monthly_summary INTEGER DEFAULT 1,
            opt_in_whatsapp INTEGER DEFAULT 0,
            opt_in_email INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        print("✅ Tabela user_notifications_settings criada")
        
        # Criar tabela notification_logs
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notification_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            notification_id INTEGER NOT NULL,
            channel TEXT NOT NULL,
            status TEXT NOT NULL,
            response_data TEXT,
            error_message TEXT,
            attempt_number INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        print("✅ Tabela notification_logs criada")
        
        conn.commit()
        print("\n🎉 Migração completa!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
