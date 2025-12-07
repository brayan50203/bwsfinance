-- =====================================================
-- MIGRATION: Adicionar coluna updated_at na tabela accounts
-- Data: 2025-10-26
-- =====================================================

-- Adicionar coluna updated_at
ALTER TABLE accounts ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP;

-- Criar trigger para atualizar updated_at automaticamente
CREATE TRIGGER IF NOT EXISTS update_accounts_timestamp 
AFTER UPDATE ON accounts
FOR EACH ROW
BEGIN
    UPDATE accounts SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Atualizar contas existentes com a data atual
UPDATE accounts SET updated_at = created_at WHERE updated_at IS NULL;
