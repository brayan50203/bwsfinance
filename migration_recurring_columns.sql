-- =====================================================
-- MIGRATION: Adicionar colunas faltantes em recurring_transactions
-- =====================================================

-- Adicionar day_of_execution (alias para day_of_month)
ALTER TABLE recurring_transactions ADD COLUMN day_of_execution INTEGER DEFAULT 1;

-- Adicionar next_execution (alias para next_date)
ALTER TABLE recurring_transactions ADD COLUMN next_execution DATE;

-- Adicionar last_execution
ALTER TABLE recurring_transactions ADD COLUMN last_execution DATE;

-- Adicionar updated_at
ALTER TABLE recurring_transactions ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP;

-- Copiar dados existentes
UPDATE recurring_transactions 
SET day_of_execution = day_of_month,
    next_execution = next_date
WHERE day_of_execution IS NULL OR next_execution IS NULL;

-- Trigger para atualizar updated_at
CREATE TRIGGER IF NOT EXISTS update_recurring_timestamp 
AFTER UPDATE ON recurring_transactions
FOR EACH ROW
BEGIN
    UPDATE recurring_transactions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
