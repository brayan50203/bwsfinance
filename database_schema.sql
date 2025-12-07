-- =====================================================
-- SCHEMA NIK0FINANCE MELHORADO
-- Base: nik0finance original
-- Adicionado: Contas, Cartões, Parcelamentos, Recorrências
-- =====================================================

-- TENANTS (Empresas/Organizações)
CREATE TABLE IF NOT EXISTS tenants (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    subdomain TEXT UNIQUE,
    active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- USUÁRIOS (melhorado)
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    is_admin BOOLEAN DEFAULT 0,
    two_factor_secret TEXT,
    two_factor_enabled BOOLEAN DEFAULT 0,
    active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_users_tenant ON users(tenant_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- CONTAS BANCÁRIAS (NOVA)
CREATE TABLE IF NOT EXISTS accounts (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    name TEXT NOT NULL,
    type TEXT CHECK(type IN ('Corrente', 'Poupança', 'Investimento', 'Carteira')) DEFAULT 'Corrente',
    bank TEXT,
    initial_balance REAL DEFAULT 0,
    current_balance REAL DEFAULT 0,
    currency TEXT DEFAULT 'BRL',
    active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_accounts_user ON accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_accounts_tenant ON accounts(tenant_id);

-- CATEGORIAS (NOVA)
CREATE TABLE IF NOT EXISTS categories (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    name TEXT NOT NULL,
    type TEXT CHECK(type IN ('Receita', 'Despesa')) NOT NULL,
    icon TEXT,
    color TEXT,
    parent_id TEXT,
    active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_categories_tenant ON categories(tenant_id);
CREATE INDEX IF NOT EXISTS idx_categories_type ON categories(type);

-- CARTÕES DE CRÉDITO (NOVA)
CREATE TABLE IF NOT EXISTS cards (
    id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    name TEXT NOT NULL,
    last_digits TEXT,
    brand TEXT CHECK(brand IN ('Visa', 'Mastercard', 'Elo', 'Amex', 'Hipercard', 'Outro')),
    limit_amount REAL,
    closing_day INTEGER CHECK(closing_day BETWEEN 1 AND 31),
    due_day INTEGER CHECK(due_day BETWEEN 1 AND 31),
    active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_cards_user ON cards(user_id);
CREATE INDEX IF NOT EXISTS idx_cards_account ON cards(account_id);

-- TRANSAÇÕES (melhorada do nik0finance original)
CREATE TABLE IF NOT EXISTS transactions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    account_id TEXT NOT NULL,
    category_id TEXT,
    card_id TEXT,
    type TEXT CHECK(type IN ('Receita', 'Despesa', 'Transferência')) NOT NULL,
    description TEXT NOT NULL,
    value REAL NOT NULL,
    date DATE NOT NULL,
    due_date DATE,
    paid_at DATETIME,
    status TEXT CHECK(status IN ('Pendente', 'Pago', 'Atrasado', 'Cancelado')) DEFAULT 'Pendente',
    is_fixed BOOLEAN DEFAULT 0,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_tenant ON transactions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);

-- TRANSAÇÕES RECORRENTES (NOVA)
CREATE TABLE IF NOT EXISTS recurring_transactions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    account_id TEXT NOT NULL,
    category_id TEXT,
    card_id TEXT,
    type TEXT CHECK(type IN ('Receita', 'Despesa')) NOT NULL,
    description TEXT NOT NULL,
    value REAL NOT NULL,
    frequency TEXT CHECK(frequency IN ('daily', 'weekly', 'monthly', 'yearly')) DEFAULT 'monthly',
    start_date DATE NOT NULL,
    end_date DATE,
    next_date DATE NOT NULL,
    day_of_month INTEGER,
    is_fixed BOOLEAN DEFAULT 1,
    active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_recurring_user ON recurring_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_recurring_next_date ON recurring_transactions(next_date);

-- PARCELAMENTOS (NOVA)
CREATE TABLE IF NOT EXISTS installments (
    id TEXT PRIMARY KEY,
    transaction_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    description TEXT NOT NULL,
    installment_number INTEGER NOT NULL,
    total_installments INTEGER NOT NULL,
    value REAL NOT NULL,
    due_date DATE NOT NULL,
    paid BOOLEAN DEFAULT 0,
    paid_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_installments_transaction ON installments(transaction_id);
CREATE INDEX IF NOT EXISTS idx_installments_user ON installments(user_id);
CREATE INDEX IF NOT EXISTS idx_installments_due_date ON installments(due_date);

-- INVESTIMENTOS (NOVA)
CREATE TABLE IF NOT EXISTS investments (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    account_id TEXT NOT NULL,
    type TEXT CHECK(type IN ('Ações', 'Fundos', 'CDB', 'LCI', 'LCA', 'Tesouro Direto', 'Poupança', 'Cripto', 'Outro')) NOT NULL,
    name TEXT NOT NULL,
    ticker TEXT,
    quantity REAL,
    average_price REAL,
    invested_amount REAL NOT NULL,
    current_value REAL,
    profit_loss REAL,
    profit_loss_percent REAL,
    purchase_date DATE,
    maturity_date DATE,
    active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_investments_user ON investments(user_id);
CREATE INDEX IF NOT EXISTS idx_investments_type ON investments(type);

-- METAS FINANCEIRAS (NOVA)
CREATE TABLE IF NOT EXISTS goals (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    target_amount REAL NOT NULL,
    current_amount REAL DEFAULT 0,
    deadline DATE,
    status TEXT CHECK(status IN ('active', 'completed', 'cancelled')) DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_goals_user ON goals(user_id);
CREATE INDEX IF NOT EXISTS idx_goals_status ON goals(status);

-- NOTIFICAÇÕES (NOVA)
CREATE TABLE IF NOT EXISTS notifications (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    type TEXT CHECK(type IN ('bill_due', 'goal_reached', 'card_limit', 'low_balance', 'recurring_created', 'investment_alert')) NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    read BOOLEAN DEFAULT 0,
    link TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(read);

-- INTEGRAÇÕES BANCÁRIAS (NOVA)
CREATE TABLE IF NOT EXISTS integrations (
    id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    provider TEXT CHECK(provider IN ('Pluggy', 'OpenFinance', 'Manual')) DEFAULT 'Manual',
    item_id TEXT,
    access_token TEXT,
    status TEXT CHECK(status IN ('active', 'error', 'disconnected')) DEFAULT 'active',
    last_sync DATETIME,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_integrations_account ON integrations(account_id);

-- =====================================================
-- VIEWS PARA FACILITAR CONSULTAS
-- =====================================================

-- Dashboard Summary (estilo nik0finance)
CREATE VIEW IF NOT EXISTS v_dashboard_summary AS
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

-- Saldo por Conta
CREATE VIEW IF NOT EXISTS v_account_balances AS
SELECT 
    a.id,
    a.user_id,
    a.tenant_id,
    a.name,
    a.type,
    a.initial_balance,
    a.initial_balance + COALESCE(
        (SELECT SUM(CASE 
            WHEN t.type = 'Receita' THEN t.value
            WHEN t.type = 'Despesa' THEN -t.value
            ELSE 0
        END)
        FROM transactions t
        WHERE t.account_id = a.id AND t.status = 'Pago'),
        0
    ) as current_balance
FROM accounts a
WHERE a.active = 1;

-- Fatura do Cartão
CREATE VIEW IF NOT EXISTS v_card_invoice AS
SELECT 
    c.id as card_id,
    c.user_id,
    c.tenant_id,
    c.name as card_name,
    strftime('%Y', t.date) as year,
    strftime('%m', t.date) as month,
    SUM(t.value) as total_spent,
    c.limit_amount,
    c.limit_amount - SUM(t.value) as available_limit,
    COUNT(t.id) as transaction_count
FROM cards c
LEFT JOIN transactions t ON t.card_id = c.id AND t.status IN ('Pendente', 'Pago')
WHERE c.active = 1
GROUP BY c.id, year, month;
