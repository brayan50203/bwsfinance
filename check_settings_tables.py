import sqlite3

conn = sqlite3.connect('bws_finance.db')
cursor = conn.cursor()

print("Tabelas existentes:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
for table in cursor.fetchall():
    print(f"  - {table[0]}")

print("\n\nVerificando tabelas de configurações:")

# Verifica notification_settings
try:
    cursor.execute("SELECT * FROM notification_settings LIMIT 0")
    print("✅ notification_settings existe")
    cursor.execute("PRAGMA table_info(notification_settings)")
    cols = cursor.fetchall()
    print(f"   Colunas: {', '.join([c[1] for c in cols])}")
except sqlite3.OperationalError:
    print("❌ notification_settings NÃO existe")

# Verifica user_preferences
try:
    cursor.execute("SELECT * FROM user_preferences LIMIT 0")
    print("✅ user_preferences existe")
    cursor.execute("PRAGMA table_info(user_preferences)")
    cols = cursor.fetchall()
    print(f"   Colunas: {', '.join([c[1] for c in cols])}")
except sqlite3.OperationalError:
    print("❌ user_preferences NÃO existe")

# Verifica coluna phone em users
cursor.execute("PRAGMA table_info(users)")
cols = [c[1] for c in cursor.fetchall()]
if 'phone' in cols:
    print("✅ users.phone existe")
else:
    print("❌ users.phone NÃO existe")

conn.close()
