-- =====================================================
-- MIGRATION: INVESTMENTS MODULE
-- Descrição: Cria tabelas para gerenciar investimentos
-- Data: 2025
-- =====================================================

-- Tabela de Investimentos
CREATE TABLE IF NOT EXISTS investments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    investment_type TEXT NOT NULL CHECK(investment_type IN ('CDB', 'LCI', 'LCA', 'Tesouro Direto', 'Ações', 'Fundos', 'Poupança', 'Outro')),
    amount REAL NOT NULL DEFAULT 0, -- Valor investido inicial
    interest_rate REAL NOT NULL DEFAULT 0, -- Taxa de juros anual (%)
    interest_type TEXT NOT NULL DEFAULT 'compound' CHECK(interest_type IN ('simple', 'compound')), -- Tipo de juros
    start_date TEXT NOT NULL, -- Data de início do investimento
    maturity_date TEXT, -- Data de vencimento (NULL = sem prazo)
    current_value REAL NOT NULL DEFAULT 0, -- Valor atual (atualizado)
    total_invested REAL NOT NULL DEFAULT 0, -- Total investido (incluindo aportes)
    total_earned REAL NOT NULL DEFAULT 0, -- Total de rendimentos
    investment_status TEXT NOT NULL DEFAULT 'active' CHECK(investment_status IN ('active', 'matured', 'withdrawn', 'cancelled')),
    description TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Tabela de Histórico de Investimentos
CREATE TABLE IF NOT EXISTS investment_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    investment_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    operation_type TEXT NOT NULL CHECK(operation_type IN ('deposit', 'interest', 'withdrawal', 'adjustment')),
    amount REAL NOT NULL, -- Valor da operação
    balance_before REAL NOT NULL, -- Saldo antes
    balance_after REAL NOT NULL, -- Saldo depois
    interest_earned REAL DEFAULT 0, -- Juros ganhos na operação
    description TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (investment_id) REFERENCES investments(id) ON DELETE CASCADE
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_investments_tenant ON investments(tenant_id);
CREATE INDEX IF NOT EXISTS idx_investments_user ON investments(user_id);
CREATE INDEX IF NOT EXISTS idx_investments_status ON investments(investment_status);
CREATE INDEX IF NOT EXISTS idx_investments_type ON investments(investment_type);
CREATE INDEX IF NOT EXISTS idx_investment_history_investment ON investment_history(investment_id);
CREATE INDEX IF NOT EXISTS idx_investment_history_date ON investment_history(date);

-- View para resumo de investimentos por usuário
CREATE VIEW IF NOT EXISTS v_investments_summary AS
SELECT 
    i.user_id,
    i.tenant_id,
    COUNT(*) as total_investments,
    SUM(i.total_invested) as total_invested,
    SUM(i.current_value) as total_current_value,
    SUM(i.total_earned) as total_earned,
    ROUND((SUM(i.current_value) - SUM(i.total_invested)) * 100.0 / NULLIF(SUM(i.total_invested), 0), 2) as return_percentage
FROM investments i
WHERE i.investment_status = 'active'
GROUP BY i.user_id, i.tenant_id;

-- View para investimentos com estatísticas
CREATE VIEW IF NOT EXISTS v_investments_details AS
SELECT 
    i.*,
    (SELECT COUNT(*) FROM investment_history WHERE investment_id = i.id) as history_count,
    (SELECT SUM(amount) FROM investment_history WHERE investment_id = i.id AND operation_type = 'deposit') as total_deposits,
    (SELECT SUM(amount) FROM investment_history WHERE investment_id = i.id AND operation_type = 'withdrawal') as total_withdrawals,
    (SELECT SUM(interest_earned) FROM investment_history WHERE investment_id = i.id) as calculated_interest,
    ROUND((i.current_value - i.total_invested) * 100.0 / NULLIF(i.total_invested, 0), 2) as return_percentage,
    CAST((julianday(COALESCE(i.maturity_date, 'now')) - julianday(i.start_date)) AS INTEGER) as duration_days
FROM investments i;

-- Trigger para atualizar updated_at
CREATE TRIGGER IF NOT EXISTS trigger_investments_updated_at
AFTER UPDATE ON investments
FOR EACH ROW
BEGIN
    UPDATE investments SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

-- =====================================================
-- FIM DA MIGRATION
-- =====================================================
