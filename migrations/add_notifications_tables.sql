-- =====================================================
-- NOTIFICATIONS SYSTEM - DATABASE SCHEMA
-- =====================================================

-- Tabela de notificações
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    category TEXT NOT NULL, -- 'Financeiro', 'Investimentos', 'Sistema', 'Erro', 'Atualização'
    priority TEXT DEFAULT 'normal', -- 'low', 'normal', 'high', 'urgent'
    status TEXT DEFAULT 'unread', -- 'unread', 'read', 'archived'
    channel TEXT DEFAULT 'system', -- 'system', 'email', 'whatsapp', 'push'
    related_type TEXT, -- 'transaction', 'investment', 'import', 'backup'
    related_id TEXT, -- ID do objeto relacionado
    metadata TEXT, -- JSON com dados extras
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    read_at DATETIME,
    sent_at DATETIME
);

-- Tabela de preferências de notificações por usuário
CREATE TABLE IF NOT EXISTS notification_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL UNIQUE,
    tenant_id TEXT NOT NULL,
    
    -- Canais ativos
    enable_system BOOLEAN DEFAULT 1,
    enable_email BOOLEAN DEFAULT 1,
    enable_whatsapp BOOLEAN DEFAULT 0,
    enable_push BOOLEAN DEFAULT 1,
    
    -- Limites de alertas
    high_expense_threshold REAL DEFAULT 500.0, -- Valor que gera alerta de gasto alto
    investment_change_threshold REAL DEFAULT 5.0, -- % de mudança que gera alerta
    
    -- Horários permitidos
    quiet_hours_start TEXT DEFAULT '22:00',
    quiet_hours_end TEXT DEFAULT '08:00',
    
    -- Contatos externos
    email_address TEXT,
    whatsapp_number TEXT,
    
    -- Frequência de resumos
    daily_summary BOOLEAN DEFAULT 1,
    weekly_report BOOLEAN DEFAULT 1,
    monthly_report BOOLEAN DEFAULT 1,
    
    -- IA e análises
    enable_ai_insights BOOLEAN DEFAULT 1,
    enable_pattern_detection BOOLEAN DEFAULT 1,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de logs de envio de notificações externas
CREATE TABLE IF NOT EXISTS notification_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    notification_id INTEGER NOT NULL,
    channel TEXT NOT NULL, -- 'email', 'whatsapp', 'push'
    status TEXT NOT NULL, -- 'pending', 'sent', 'delivered', 'failed', 'blocked'
    error_message TEXT,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    delivered_at DATETIME,
    FOREIGN KEY (notification_id) REFERENCES notifications(id) ON DELETE CASCADE
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notifications_category ON notifications(category, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notification_logs_status ON notification_logs(status, sent_at DESC);

-- Inserir preferências padrão para usuários existentes
INSERT OR IGNORE INTO notification_preferences (user_id, tenant_id)
SELECT id, tenant_id FROM users;
