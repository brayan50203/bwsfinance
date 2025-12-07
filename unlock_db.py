import sqlite3
import os
import time

# Fechar todas as conexões do banco
db_path = 'bws_finance.db'

print("🔒 Fechando conexões abertas...")

# Tentar conectar e fechar imediatamente
try:
    conn = sqlite3.connect(db_path, timeout=1.0)
    conn.close()
    print("✅ Conexão fechada")
except Exception as e:
    print(f"⚠️ Erro ao fechar: {e}")

# Verificar se há arquivos de lock
lock_files = ['bws_finance.db-shm', 'bws_finance.db-wal', 'bws_finance.db-journal']
for lock_file in lock_files:
    if os.path.exists(lock_file):
        try:
            os.remove(lock_file)
            print(f"🗑️ Removido: {lock_file}")
        except Exception as e:
            print(f"⚠️ Não foi possível remover {lock_file}: {e}")

print("✅ Banco de dados liberado!")
