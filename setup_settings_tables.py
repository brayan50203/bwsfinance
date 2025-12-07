import sqlite3

conn = sqlite3.connect('bws_finance.db')
cursor = conn.cursor()

print("Verificando notification_preferences:")
cursor.execute("PRAGMA table_info(notification_preferences)")
cols = cursor.fetchall()
for col in cols:
    print(f"  {col[1]} ({col[2]})")

print("\n\nCriando/Atualizando tabela notification_settings...")

# Criar tabela notification_settings se não existir
cursor.execute('''
CREATE TABLE IF NOT EXISTS notification_settings (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    user_id TEXT NOT NULL UNIQUE,
    email_enabled INTEGER DEFAULT 1,
    whatsapp_enabled INTEGER DEFAULT 1,
    push_enabled INTEGER DEFAULT 1,
    high_spending INTEGER DEFAULT 1,
    bill_due INTEGER DEFAULT 1,
    investment_update INTEGER DEFAULT 1,
    weekly_report INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
''')

# Adicionar colunas faltantes em user_preferences se necessário
try:
    cursor.execute('ALTER TABLE user_preferences ADD COLUMN save_history INTEGER DEFAULT 1')
    print("✅ Coluna save_history adicionada")
except sqlite3.OperationalError:
    print("⚠️ Coluna save_history já existe")

try:
    cursor.execute('ALTER TABLE user_preferences ADD COLUMN allow_cookies INTEGER DEFAULT 1')
    print("✅ Coluna allow_cookies adicionada")
except sqlite3.OperationalError:
    print("⚠️ Coluna allow_cookies já existe")

conn.commit()

print("\n✅ Tabelas de configurações prontas!")
print("\nVerificando notification_settings:")
cursor.execute("PRAGMA table_info(notification_settings)")
cols = cursor.fetchall()
for col in cols:
    print(f"  {col[1]} ({col[2]})")

conn.close()
