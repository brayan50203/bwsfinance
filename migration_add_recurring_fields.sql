-- =====================================================
-- MIGRATION: Adicionar campos para execução de recorrentes
-- =====================================================

-- Adicionar day_of_execution se não existir
ALTER TABLE recurring_transactions ADD COLUMN day_of_execution INTEGER DEFAULT 1;

-- Adicionar day_of_week se não existir
ALTER TABLE recurring_transactions ADD COLUMN day_of_week INTEGER;

-- Adicionar next_execution se não existir
ALTER TABLE recurring_transactions ADD COLUMN next_execution DATE;

-- Adicionar last_execution se não existir
ALTER TABLE recurring_transactions ADD COLUMN last_execution DATE;

-- Adicionar updated_at se não existir
ALTER TABLE recurring_transactions ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP;

-- Atualizar next_execution para registros existentes (usar next_date se existir)
UPDATE recurring_transactions 
SET next_execution = COALESCE(next_execution, next_date, date('now'))
WHERE next_execution IS NULL;

-- Criar trigger para updated_at
DROP TRIGGER IF EXISTS trigger_recurring_updated;
CREATE TRIGGER trigger_recurring_updated
AFTER UPDATE ON recurring_transactions
FOR EACH ROW
BEGIN
    UPDATE recurring_transactions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
