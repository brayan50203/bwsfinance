"""
Adiciona coluna payment_method à tabela transactions
"""
import sqlite3

def add_payment_method_column():
    conn = sqlite3.connect('bws_finance.db')
    cursor = conn.cursor()
    
    try:
        # Verificar se a coluna já existe
        cursor.execute("PRAGMA table_info(transactions)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'payment_method' not in columns:
            print("Adicionando coluna payment_method...")
            cursor.execute("""
                ALTER TABLE transactions 
                ADD COLUMN payment_method TEXT DEFAULT 'debito'
            """)
            conn.commit()
            print("✅ Coluna payment_method adicionada com sucesso!")
        else:
            print("ℹ️  Coluna payment_method já existe.")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    add_payment_method_column()
