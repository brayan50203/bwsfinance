-- =====================================================
-- VIEW: v_account_balances
-- Calcula saldo atual baseado em transações
-- =====================================================

CREATE VIEW IF NOT EXISTS v_account_balances AS
SELECT 
    a.id,
    a.user_id,
    a.tenant_id,
    a.name,
    a.type,
    a.bank,
    a.initial_balance,
    a.current_balance,
    a.currency,
    a.active,
    a.created_at,
    a.updated_at,
    COUNT(t.id) as total_transactions,
    COALESCE(SUM(CASE WHEN t.type = 'Receita' THEN t.value ELSE 0 END), 0) as total_income,
    COALESCE(SUM(CASE WHEN t.type = 'Despesa' THEN t.value ELSE 0 END), 0) as total_expense,
    (a.initial_balance + 
     COALESCE(SUM(CASE WHEN t.type = 'Receita' THEN t.value ELSE 0 END), 0) - 
     COALESCE(SUM(CASE WHEN t.type = 'Despesa' THEN t.value ELSE 0 END), 0)) as calculated_balance
FROM accounts a
LEFT JOIN transactions t ON a.id = t.account_id AND t.status = 'Pago'
WHERE a.active = 1
GROUP BY a.id, a.user_id, a.tenant_id, a.name, a.type, a.bank, 
         a.initial_balance, a.current_balance, a.currency, a.active, 
         a.created_at, a.updated_at;
