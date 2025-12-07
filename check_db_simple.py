import sqlite3

# Conectar ao banco
conn = sqlite3.connect('bws_finance.db')
cursor = conn.cursor()

# Listar tabelas
print("=" * 50)
print("TABELAS NO BANCO DE DADOS:")
print("=" * 50)
tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
for table in tables:
    print(f"  - {table[0]}")

print("\n" + "=" * 50)
print("VERIFICANDO TABELA 'users':")
print("=" * 50)

# Tentar diferentes nomes de colunas
try:
    users = cursor.execute("SELECT * FROM users LIMIT 5").fetchall()
    print(f"Total de usuários: {len(users)}")
    
    # Pegar nomes das colunas
    cols = [description[0] for description in cursor.description]
    print(f"Colunas: {cols}")
    
    for user in users:
        print(f"\nUsuário: {dict(zip(cols, user))}")
        
except Exception as e:
    print(f"Erro ao consultar users: {e}")

conn.close()
