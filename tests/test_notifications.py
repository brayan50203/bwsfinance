"""
Testes unitários para o Sistema de Notificações
"""

import pytest
import sqlite3
import os
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Importar módulos a testar
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.auto_notifications import AutoNotificationService
from services.whatsapp_sender import WhatsAppSender
from services.email_sender import EmailSender


# ==================== FIXTURES ====================

@pytest.fixture
def test_db():
    """Cria banco de teste temporário"""
    db_path = 'test_notifications.db'
    
    # Criar tabelas
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        tenant_id TEXT,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        event_type TEXT NOT NULL,
        meta TEXT,
        channel TEXT NOT NULL,
        priority TEXT DEFAULT 'medium',
        status TEXT DEFAULT 'pending',
        retry_count INTEGER DEFAULT 0,
        error_message TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        scheduled_at DATETIME,
        sent_at DATETIME,
        read_at DATETIME
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT,
        email TEXT,
        phone TEXT,
        active INTEGER DEFAULT 1
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_notifications_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL UNIQUE,
        notify_whatsapp INTEGER DEFAULT 1,
        notify_email INTEGER DEFAULT 1,
        threshold_low_balance REAL DEFAULT 100.00,
        investment_alert_pct REAL DEFAULT 3.0,
        opt_in_whatsapp INTEGER DEFAULT 1,
        opt_in_email INTEGER DEFAULT 1
    )
    """)
    
    # Inserir usuário de teste
    cursor.execute("""
        INSERT INTO users (id, name, email, phone, active)
        VALUES ('test-user-123', 'João Silva', 'joao@test.com', '+5511999887766', 1)
    """)
    
    # Inserir settings de teste
    cursor.execute("""
        INSERT INTO user_notifications_settings (user_id, notify_whatsapp, notify_email, opt_in_whatsapp, opt_in_email)
        VALUES ('test-user-123', 1, 1, 1, 1)
    """)
    
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Limpar
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def notification_service(test_db):
    """Instância de AutoNotificationService com DB de teste"""
    service = AutoNotificationService(db_path=test_db)
    service.enabled = False  # Desabilitar scheduler em testes
    return service


@pytest.fixture
def mock_whatsapp():
    """Mock do WhatsAppSender"""
    with patch('services.whatsapp_sender.whatsapp_sender') as mock:
        mock.send_message = Mock(return_value={
            'success': True,
            'message_id': 'test-msg-123',
            'timestamp': datetime.utcnow().isoformat()
        })
        yield mock


@pytest.fixture
def mock_email():
    """Mock do EmailSender"""
    with patch('services.email_sender.email_sender') as mock:
        mock.send = Mock(return_value=True)
        yield mock


# ==================== TESTES ====================

def test_create_notification(notification_service, test_db):
    """Testa criação de notificação no banco"""
    notification_id = notification_service.create_notification(
        user_id='test-user-123',
        tenant_id='test-tenant',
        title='Test Notification',
        message='This is a test',
        event_type='test_event',
        channel='both',
        priority='high',
        meta={'test_key': 'test_value'}
    )
    
    assert notification_id > 0
    
    # Verificar no banco
    db = sqlite3.connect(test_db)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM notifications WHERE id = ?", (notification_id,))
    row = cursor.fetchone()
    
    assert row is not None
    assert row[1] == 'test-user-123'  # user_id
    assert row[3] == 'Test Notification'  # title
    assert row[5] == 'test_event'  # event_type
    
    db.close()


def test_get_user_settings(notification_service):
    """Testa busca de preferências do usuário"""
    settings = notification_service.get_user_settings('test-user-123')
    
    assert settings['notify_whatsapp'] is True
    assert settings['notify_email'] is True
    assert settings['opt_in_whatsapp'] is True
    assert settings['threshold_low_balance'] == 100.00


def test_get_user_settings_default(notification_service):
    """Testa defaults quando usuário não tem settings"""
    settings = notification_service.get_user_settings('non-existent-user')
    
    # Deve retornar defaults
    assert settings['notify_whatsapp'] is True
    assert settings['threshold_low_balance'] == 100.00
    assert settings['investment_alert_pct'] == 3.0


def test_send_notification_whatsapp(notification_service, test_db, mock_whatsapp):
    """Testa envio de notificação via WhatsApp"""
    # Criar notificação
    notification_id = notification_service.create_notification(
        user_id='test-user-123',
        tenant_id='test-tenant',
        title='Test WhatsApp',
        message='Test message',
        event_type='test_event',
        channel='whatsapp',
        priority='medium'
    )
    
    # Mock dos senders
    with patch('services.auto_notifications.whatsapp_sender', mock_whatsapp):
        with patch('services.auto_notifications.email_sender', None):
            success = notification_service.send_notification(notification_id)
    
    assert success is True
    mock_whatsapp.send_message.assert_called_once()
    
    # Verificar status no banco
    db = sqlite3.connect(test_db)
    cursor = db.cursor()
    cursor.execute("SELECT status, sent_at FROM notifications WHERE id = ?", (notification_id,))
    row = cursor.fetchone()
    
    assert row[0] == 'sent'
    assert row[1] is not None
    
    db.close()


def test_send_notification_both_channels(notification_service, test_db, mock_whatsapp, mock_email):
    """Testa envio via WhatsApp E Email"""
    notification_id = notification_service.create_notification(
        user_id='test-user-123',
        tenant_id='test-tenant',
        title='Test Both',
        message='Test message',
        event_type='test_event',
        channel='both',
        priority='medium'
    )
    
    # Mock dos senders
    with patch('services.auto_notifications.whatsapp_sender', mock_whatsapp):
        with patch('services.auto_notifications.email_sender', mock_email):
            success = notification_service.send_notification(notification_id)
    
    assert success is True
    mock_whatsapp.send_message.assert_called_once()
    mock_email.send.assert_called_once()


def test_whatsapp_sender_normalize_phone():
    """Testa normalização de número de telefone"""
    sender = WhatsAppSender()
    
    # Testes de normalização
    assert sender._normalize_phone('+5511999887766') == '5511999887766'
    assert sender._normalize_phone('11999887766') == '5511999887766'
    assert sender._normalize_phone('(11) 99988-7766') == '5511999887766'
    assert sender._normalize_phone('11 9 9988 7766') == '5511999887766'


def test_whatsapp_sender_format_message():
    """Testa formatação de template"""
    sender = WhatsAppSender()
    
    template = "Olá {name}! Você tem R$ {amount:.2f} de saldo."
    data = {'name': 'João', 'amount': 1234.56}
    
    result = sender._format_message(template, data)
    assert result == "Olá João! Você tem R$ 1234.56 de saldo."


def test_whatsapp_sender_mock_mode():
    """Testa modo mock (WhatsApp desabilitado)"""
    sender = WhatsAppSender()
    sender.enabled = False
    
    result = sender.send_message('+5511999887766', 'Test message')
    
    assert result['success'] is True
    assert result['mock'] is True
    assert 'message_id' in result


def test_notification_priority_levels(notification_service, test_db):
    """Testa criação com diferentes níveis de prioridade"""
    for priority in ['low', 'medium', 'high']:
        notification_id = notification_service.create_notification(
            user_id='test-user-123',
            tenant_id='test-tenant',
            title=f'Test {priority}',
            message='Test',
            event_type='test_event',
            channel='dashboard',
            priority=priority
        )
        
        db = sqlite3.connect(test_db)
        cursor = db.cursor()
        cursor.execute("SELECT priority FROM notifications WHERE id = ?", (notification_id,))
        row = cursor.fetchone()
        
        assert row[0] == priority
        db.close()


def test_notification_meta_json(notification_service, test_db):
    """Testa armazenamento de metadados JSON"""
    meta_data = {
        'card_name': 'Nubank',
        'amount': 1240.50,
        'due_date': '2025-11-12',
        'days': 3
    }
    
    notification_id = notification_service.create_notification(
        user_id='test-user-123',
        tenant_id='test-tenant',
        title='Test Meta',
        message='Test',
        event_type='invoice_due_soon',
        channel='both',
        meta=meta_data
    )
    
    db = sqlite3.connect(test_db)
    cursor = db.cursor()
    cursor.execute("SELECT meta FROM notifications WHERE id = ?", (notification_id,))
    row = cursor.fetchone()
    
    stored_meta = json.loads(row[0])
    assert stored_meta == meta_data
    
    db.close()


# ==================== TESTES DE INTEGRAÇÃO ====================

def test_full_notification_flow(notification_service, test_db, mock_whatsapp, mock_email):
    """Teste completo: criar → enviar → verificar status"""
    # 1. Criar
    notification_id = notification_service.create_notification(
        user_id='test-user-123',
        tenant_id='test-tenant',
        title='Integration Test',
        message='Full flow test',
        event_type='test_event',
        channel='both',
        priority='high',
        meta={'test': True}
    )
    
    assert notification_id > 0
    
    # 2. Enviar
    with patch('services.auto_notifications.whatsapp_sender', mock_whatsapp):
        with patch('services.auto_notifications.email_sender', mock_email):
            success = notification_service.send_notification(notification_id)
    
    assert success is True
    
    # 3. Verificar
    db = sqlite3.connect(test_db)
    cursor = db.cursor()
    cursor.execute("""
        SELECT status, sent_at, title, message, event_type, channel, priority
        FROM notifications
        WHERE id = ?
    """, (notification_id,))
    row = cursor.fetchone()
    
    assert row[0] == 'sent'
    assert row[1] is not None
    assert row[2] == 'Integration Test'
    assert row[3] == 'Full flow test'
    assert row[4] == 'test_event'
    assert row[5] == 'both'
    assert row[6] == 'high'
    
    db.close()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
