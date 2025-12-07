-- Migration: Create notifications and user_notifications_settings tables
-- Date: 2025-11-10
-- Description: Sistema de notificações automáticas (WhatsApp + Email)

-- Tabela principal de notificações
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    tenant_id TEXT,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    event_type TEXT NOT NULL, -- invoice_due_soon, monthly_spending_summary, investment_threshold, low_balance, import_confirmation, system_alert
    meta TEXT, -- JSON com payload específico do evento
    channel TEXT NOT NULL, -- 'whatsapp', 'email', 'dashboard', 'both'
    priority TEXT DEFAULT 'medium', -- low, medium, high
    status TEXT DEFAULT 'pending', -- pending, sent, failed, read
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    scheduled_at DATETIME,
    sent_at DATETIME,
    read_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications(status);
CREATE INDEX IF NOT EXISTS idx_notifications_event_type ON notifications(event_type);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notifications_scheduled_at ON notifications(scheduled_at);

-- Tabela de preferências de notificações por usuário
CREATE TABLE IF NOT EXISTS user_notifications_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL UNIQUE,
    tenant_id TEXT,
    notify_whatsapp INTEGER DEFAULT 1, -- 0=false, 1=true
    notify_email INTEGER DEFAULT 1,
    notify_dashboard INTEGER DEFAULT 1,
    threshold_low_balance REAL DEFAULT 100.00,
    investment_alert_pct REAL DEFAULT 3.0,
    do_not_disturb_start TIME, -- ex: 22:00
    do_not_disturb_end TIME, -- ex: 07:00
    invoice_alert_days TEXT DEFAULT '3,1,0', -- dias antes do vencimento (3 dias, 1 dia, dia do vencimento)
    weekly_summary INTEGER DEFAULT 1,
    monthly_summary INTEGER DEFAULT 1,
    opt_in_whatsapp INTEGER DEFAULT 0, -- Consent para WhatsApp (LGPD compliance)
    opt_in_email INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_user_notifications_settings_user_id ON user_notifications_settings(user_id);

-- Tabela de log de envios (auditoria)
CREATE TABLE IF NOT EXISTS notification_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    notification_id INTEGER NOT NULL,
    channel TEXT NOT NULL,
    status TEXT NOT NULL, -- success, failed, retry
    response_data TEXT, -- JSON com resposta do gateway
    error_message TEXT,
    attempt_number INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (notification_id) REFERENCES notifications(id)
);

CREATE INDEX IF NOT EXISTS idx_notification_logs_notification_id ON notification_logs(notification_id);
CREATE INDEX IF NOT EXISTS idx_notification_logs_status ON notification_logs(status);
