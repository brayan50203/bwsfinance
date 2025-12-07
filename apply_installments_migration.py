import sqlite3

db = sqlite3.connect('bws_finance.db')
cursor = db.cursor()

# Criar tabela installments
cursor.execute("""
CREATE TABLE IF NOT EXISTS installments (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    account_id TEXT,
    card_id TEXT,
    category_id TEXT,
    description TEXT NOT NULL,
    total_amount REAL NOT NULL,
    installment_count INTEGER NOT NULL,
    installment_value REAL NOT NULL,
    interest_rate REAL DEFAULT 0,
    first_due_date DATE NOT NULL,
    current_status TEXT DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

print("✅ Tabela installments criada!")

# Criar índices
cursor.execute("CREATE INDEX IF NOT EXISTS idx_installments_user ON installments(user_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_installments_tenant ON installments(tenant_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_installments_status ON installments(current_status)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_installment ON transactions(installment_id)")

print("✅ Índices criados!")

# Criar trigger
cursor.execute("""
CREATE TRIGGER IF NOT EXISTS update_installments_timestamp 
AFTER UPDATE ON installments
FOR EACH ROW
BEGIN
    UPDATE installments SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END
""")

print("✅ Trigger criado!")

# Criar view
cursor.execute("""
CREATE VIEW IF NOT EXISTS v_installments_summary AS
SELECT 
    i.id,
    i.user_id,
    i.tenant_id,
    i.description,
    i.total_amount,
    i.installment_count,
    i.installment_value,
    i.first_due_date,
    i.current_status,
    i.created_at,
    a.name as account_name,
    c.name as card_name,
    cat.name as category_name,
    cat.icon as category_icon,
    COUNT(t.id) as total_transactions,
    COALESCE(SUM(t.value), 0) as total_paid
FROM installments i
LEFT JOIN accounts a ON i.account_id = a.id
LEFT JOIN cards c ON i.card_id = c.id
LEFT JOIN categories cat ON i.category_id = cat.id
LEFT JOIN transactions t ON t.installment_id = i.id
GROUP BY i.id
""")

print("✅ View criada!")

db.commit()
db.close()

print("\n🎉 Migration de parcelamentos concluída!")
