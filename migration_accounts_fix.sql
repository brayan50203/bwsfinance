-- =====================================================
-- MIGRATION: Finalizar módulo ACCOUNTS
-- Data: 2025-10-26
-- Descrição: Corrigir schema de accounts e integração com transactions
-- =====================================================

-- PASSO 1: Drop views que dependem de transactions
DROP VIEW IF EXISTS v_dashboard_summary;
DROP VIEW IF EXISTS v_account_balances;
DROP VIEW IF EXISTS v_card_invoice;
DROP VIEW IF EXISTS v_transactions_grouped;
DROP VIEW IF EXISTS v_available_periods;

-- PASSO 2: Recriar tabela accounts com schema correto
CREATE TABLE IF NOT EXISTS accounts_new (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  tenant_id TEXT NOT NULL,
  name TEXT NOT NULL,
  type TEXT NOT NULL DEFAULT 'bank',  -- bank, card, wallet, investment, reserve
  currency TEXT NOT NULL DEFAULT 'BRL',
  initial_balance NUMERIC DEFAULT 0,
  current_balance NUMERIC DEFAULT 0,  -- calculado/atualizado pelo backend
  bank TEXT,                          -- nome do banco (opcional)
  metadata TEXT,                      -- json string opcional
  active INTEGER DEFAULT 1,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

-- PASSO 3: Copiar dados existentes
INSERT INTO accounts_new (id, user_id, tenant_id, name, type, currency, initial_balance, current_balance, bank, metadata, active, created_at, updated_at)
SELECT 
    id, 
    user_id, 
    tenant_id, 
    name, 
    COALESCE(type, 'bank'), 
    COALESCE(currency, 'BRL'),
    COALESCE(initial_balance, 0),
    COALESCE(current_balance, initial_balance, 0),
    bank,
    metadata,
    COALESCE(active, 1),
    COALESCE(created_at, datetime('now')),
    COALESCE(updated_at, datetime('now'))
FROM accounts
WHERE EXISTS (SELECT 1 FROM accounts);

-- PASSO 4: Substituir tabela
DROP TABLE IF EXISTS accounts;
ALTER TABLE accounts_new RENAME TO accounts;

-- PASSO 5: Recriar índices
CREATE INDEX IF NOT EXISTS idx_accounts_user ON accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_accounts_tenant ON accounts(tenant_id);
CREATE INDEX IF NOT EXISTS idx_accounts_active ON accounts(active);

-- PASSO 6: Garantir que transactions tem account_id
-- Primeiro verificar se transactions existe
CREATE TABLE IF NOT EXISTS transactions_temp AS SELECT * FROM transactions WHERE 1=0;

-- Se transactions existe, copiar para temp
INSERT INTO transactions_temp SELECT * FROM transactions WHERE EXISTS (SELECT 1 FROM sqlite_master WHERE type='table' AND name='transactions');

-- Recriar transactions com schema correto
DROP TABLE IF EXISTS transactions;
CREATE TABLE transactions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    account_id TEXT NOT NULL,  -- OBRIGATÓRIO agora
    category_id TEXT,
    card_id TEXT,
    type TEXT CHECK(type IN ('Receita', 'Despesa', 'Transferência')) NOT NULL,
    description TEXT NOT NULL,
    value REAL NOT NULL,
    date DATE NOT NULL,
    due_date DATE,
    paid_at DATETIME,
    status TEXT CHECK(status IN ('Pendente', 'Pago', 'Atrasado', 'Cancelado')) DEFAULT 'Pendente',
    is_fixed INTEGER DEFAULT 0,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE RESTRICT,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE SET NULL
);

-- Copiar dados de volta
INSERT INTO transactions 
SELECT 
    id, user_id, tenant_id, 
    account_id,
    category_id, card_id, type, description, value, date, due_date, paid_at, status, is_fixed, notes, created_at, updated_at
FROM transactions_temp
WHERE EXISTS (SELECT 1 FROM transactions_temp);

DROP TABLE IF EXISTS transactions_temp;

-- Recriar índices de transactions
CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_tenant ON transactions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);

-- PASSO 7: Recriar views
CREATE VIEW v_account_balances AS
SELECT 
    a.id,
    a.user_id,
    a.tenant_id,
    a.name,
    a.type,
    a.bank,
    a.currency,
    a.initial_balance,
    a.initial_balance + COALESCE(
        (SELECT SUM(CASE 
            WHEN t.type = 'Receita' THEN t.value
            WHEN t.type = 'Despesa' THEN -t.value
            ELSE 0
        END)
        FROM transactions t
        WHERE t.account_id = a.id 
        AND t.status = 'Pago'),
        0
    ) as current_balance,
    a.active,
    a.created_at,
    a.updated_at,
    (SELECT COUNT(*) FROM transactions WHERE account_id = a.id) as transaction_count
FROM accounts a;

CREATE VIEW v_dashboard_summary AS
SELECT 
    t.user_id,
    t.tenant_id,
    strftime('%Y', t.date) as year,
    strftime('%m', t.date) as month,
    SUM(CASE WHEN t.type = 'Receita' AND t.is_fixed = 1 THEN t.value ELSE 0 END) as renda_fixa,
    SUM(CASE WHEN t.type = 'Receita' AND t.is_fixed = 0 THEN t.value ELSE 0 END) as renda_variavel,
    SUM(CASE WHEN t.type = 'Receita' THEN t.value ELSE 0 END) as renda_total,
    SUM(CASE WHEN t.type = 'Despesa' AND t.is_fixed = 1 THEN t.value ELSE 0 END) as custo_fixo,
    SUM(CASE WHEN t.type = 'Despesa' AND t.is_fixed = 0 THEN t.value ELSE 0 END) as custo_variavel,
    SUM(CASE WHEN t.type = 'Despesa' THEN t.value ELSE 0 END) as custo_total,
    SUM(CASE WHEN t.type = 'Receita' THEN t.value ELSE 0 END) - 
    SUM(CASE WHEN t.type = 'Despesa' THEN t.value ELSE 0 END) as saldo_mensal
FROM transactions t
WHERE t.status = 'Pago'
GROUP BY t.user_id, t.tenant_id, year, month;

-- PASSO 8: Trigger para atualizar updated_at
DROP TRIGGER IF EXISTS update_accounts_timestamp;
CREATE TRIGGER update_accounts_timestamp 
AFTER UPDATE ON accounts
FOR EACH ROW
BEGIN
    UPDATE accounts SET updated_at = datetime('now') WHERE id = OLD.id;
END;

-- =====================================================
-- FIM DA MIGRATION
-- =====================================================
