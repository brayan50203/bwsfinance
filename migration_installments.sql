-- =====================================================
-- MIGRATION: Criar tabela de parcelamentos (installments)
-- Data: 2025-10-26
-- =====================================================

-- Tabela principal de grupos de parcelamento
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
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'completed', 'cancelled')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE SET NULL,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE SET NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_installments_user ON installments(user_id);
CREATE INDEX IF NOT EXISTS idx_installments_tenant ON installments(tenant_id);
CREATE INDEX IF NOT EXISTS idx_installments_status ON installments(status);
CREATE INDEX IF NOT EXISTS idx_transactions_installment ON transactions(installment_id);

-- Trigger para atualizar updated_at
CREATE TRIGGER IF NOT EXISTS update_installments_timestamp 
AFTER UPDATE ON installments
FOR EACH ROW
BEGIN
    UPDATE installments SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- View para listar parcelas com informações agregadas
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
    i.status,
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
GROUP BY i.id, i.user_id, i.tenant_id, i.description, i.total_amount, 
         i.installment_count, i.installment_value, i.first_due_date, i.status, i.created_at,
         a.name, c.name, cat.name, cat.icon;
