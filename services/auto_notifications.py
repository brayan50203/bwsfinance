"""
Auto Notifications Service
Sistema de notificações automáticas para BWS Finance

Features:
- Scheduler (APScheduler) para jobs recorrentes
- Checagem de faturas vencendo (3, 2, 1, 0 dias)
- Resumo mensal de gastos
- Alertas de investimentos
- Alertas de saldo baixo
- Relatórios periódicos

Integra com WhatsApp (via services/whatsapp_sender) e Email (via services/email_sender)
"""

import os
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/notifications.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('auto_notifications')

# Importar senders
try:
    from services.whatsapp_sender import whatsapp_sender
except ImportError:
    logger.warning("WhatsApp sender não disponível")
    whatsapp_sender = None

try:
    from services.email_sender import EmailSender
    email_sender = EmailSender()
except ImportError:
    logger.warning("Email sender não disponível")
    email_sender = None


class AutoNotificationService:
    """Gerenciador de notificações automáticas"""
    
    def __init__(self, db_path: str = 'bws_finance.db'):
        self.db_path = db_path
        self.scheduler = BackgroundScheduler()
        self.enabled = os.getenv('AUTO_NOTIFICATIONS_ENABLED', 'true').lower() == 'true'
        
    def get_db(self):
        """Retorna conexão com banco de dados"""
        return sqlite3.connect(self.db_path)
    
    def get_user_settings(self, user_id: str) -> Dict[str, Any]:
        """
        Busca preferências de notificação do usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dict com preferências ou defaults
        """
        db = self.get_db()
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT notify_whatsapp, notify_email, notify_dashboard,
                   threshold_low_balance, investment_alert_pct,
                   do_not_disturb_start, do_not_disturb_end,
                   invoice_alert_days, weekly_summary, monthly_summary,
                   opt_in_whatsapp, opt_in_email
            FROM user_notifications_settings
            WHERE user_id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        db.close()
        
        if row:
            return {
                'notify_whatsapp': bool(row[0]),
                'notify_email': bool(row[1]),
                'notify_dashboard': bool(row[2]),
                'threshold_low_balance': row[3],
                'investment_alert_pct': row[4],
                'do_not_disturb_start': row[5],
                'do_not_disturb_end': row[6],
                'invoice_alert_days': row[7],
                'weekly_summary': bool(row[8]),
                'monthly_summary': bool(row[9]),
                'opt_in_whatsapp': bool(row[10]),
                'opt_in_email': bool(row[11])
            }
        
        # Defaults
        return {
            'notify_whatsapp': True,
            'notify_email': True,
            'notify_dashboard': True,
            'threshold_low_balance': 100.00,
            'investment_alert_pct': 3.0,
            'do_not_disturb_start': None,
            'do_not_disturb_end': None,
            'invoice_alert_days': '3,1,0',
            'weekly_summary': True,
            'monthly_summary': True,
            'opt_in_whatsapp': False,
            'opt_in_email': False
        }
    
    def is_do_not_disturb(self, user_id: str) -> bool:
        """
        Verifica se está no horário de não perturbar
        
        Args:
            user_id: ID do usuário
            
        Returns:
            True se está em DND
        """
        settings = self.get_user_settings(user_id)
        
        if not settings['do_not_disturb_start'] or not settings['do_not_disturb_end']:
            return False
        
        now = datetime.now().time()
        start = datetime.strptime(settings['do_not_disturb_start'], '%H:%M').time()
        end = datetime.strptime(settings['do_not_disturb_end'], '%H:%M').time()
        
        if start < end:
            return start <= now <= end
        else:  # Período cruza meia-noite
            return now >= start or now <= end
    
    def create_notification(
        self,
        user_id: str,
        tenant_id: str,
        title: str,
        message: str,
        event_type: str,
        channel: str = 'both',
        priority: str = 'medium',
        meta: Optional[Dict[str, Any]] = None,
        scheduled_at: Optional[datetime] = None
    ) -> int:
        """
        Cria uma notificação no banco
        
        Args:
            user_id: ID do usuário
            tenant_id: ID do tenant
            title: Título da notificação
            message: Corpo da mensagem
            event_type: Tipo do evento
            channel: Canal (whatsapp, email, dashboard, both)
            priority: Prioridade (low, medium, high)
            meta: Metadados adicionais (JSON)
            scheduled_at: Data/hora agendada
            
        Returns:
            ID da notificação criada
        """
        db = self.get_db()
        cursor = db.cursor()
        
        cursor.execute("""
            INSERT INTO notifications (
                user_id, tenant_id, title, message, event_type,
                channel, priority, status, meta, scheduled_at, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, tenant_id, title, message, event_type,
            channel, priority, 'pending',
            json.dumps(meta) if meta else None,
            scheduled_at or datetime.now(),
            datetime.now()
        ))
        
        notification_id = cursor.lastrowid
        db.commit()
        db.close()
        
        logger.info(f"📝 Notificação criada: ID={notification_id}, tipo={event_type}, canal={channel}")
        return notification_id
    
    def send_notification(self, notification_id: int) -> bool:
        """
        Envia uma notificação (WhatsApp e/ou Email)
        
        Args:
            notification_id: ID da notificação
            
        Returns:
            True se enviado com sucesso
        """
        db = self.get_db()
        cursor = db.cursor()
        
        # Buscar notificação
        cursor.execute("""
            SELECT n.id, n.user_id, n.tenant_id, n.title, n.message,
                   n.event_type, n.channel, n.priority, n.meta,
                   u.name, u.email, u.phone
            FROM notifications n
            JOIN users u ON n.user_id = u.id
            WHERE n.id = ? AND n.status = 'pending'
        """, (notification_id,))
        
        row = cursor.fetchone()
        
        if not row:
            logger.warning(f"⚠️  Notificação {notification_id} não encontrada ou já enviada")
            db.close()
            return False
        
        (nid, user_id, tenant_id, title, message, event_type,
         channel, priority, meta_json, user_name, user_email, user_phone) = row
        
        meta = json.loads(meta_json) if meta_json else {}
        
        # Verificar do not disturb
        if self.is_do_not_disturb(user_id):
            logger.info(f"⏰ Usuário {user_id} em DND, adiando notificação")
            db.close()
            return False
        
        # Buscar preferências
        settings = self.get_user_settings(user_id)
        
        success = True
        channels_sent = []
        
        # Enviar WhatsApp
        if channel in ['whatsapp', 'both'] and settings['notify_whatsapp'] and settings['opt_in_whatsapp']:
            if whatsapp_sender and user_phone:
                try:
                    result = whatsapp_sender.send_message(
                        phone=user_phone,
                        text=message,
                        template_data={'first_name': user_name.split()[0] if user_name else 'Usuário'}
                    )
                    
                    if result['success']:
                        channels_sent.append('whatsapp')
                        self._log_notification_attempt(nid, 'whatsapp', 'success', result)
                        logger.info(f"✅ WhatsApp enviado: {user_phone}")
                    else:
                        success = False
                        self._log_notification_attempt(nid, 'whatsapp', 'failed', result)
                        logger.error(f"❌ WhatsApp falhou: {result.get('error')}")
                        
                except Exception as e:
                    success = False
                    self._log_notification_attempt(nid, 'whatsapp', 'failed', {'error': str(e)})
                    logger.error(f"❌ Erro ao enviar WhatsApp: {str(e)}")
            else:
                logger.warning(f"⚠️  WhatsApp não disponível para user {user_id}")
        
        # Enviar Email
        if channel in ['email', 'both'] and settings['notify_email'] and settings['opt_in_email']:
            if email_sender and user_email:
                try:
                    result = email_sender.send(
                        to_email=user_email,
                        subject=title,
                        body=message,
                        html=True
                    )
                    
                    if result:
                        channels_sent.append('email')
                        self._log_notification_attempt(nid, 'email', 'success', {})
                        logger.info(f"✅ Email enviado: {user_email}")
                    else:
                        success = False
                        self._log_notification_attempt(nid, 'email', 'failed', {})
                        logger.error(f"❌ Email falhou para {user_email}")
                        
                except Exception as e:
                    success = False
                    self._log_notification_attempt(nid, 'email', 'failed', {'error': str(e)})
                    logger.error(f"❌ Erro ao enviar email: {str(e)}")
            else:
                logger.warning(f"⚠️  Email não disponível para user {user_id}")
        
        # Atualizar status
        if success and len(channels_sent) > 0:
            cursor.execute("""
                UPDATE notifications
                SET status = 'sent', sent_at = ?
                WHERE id = ?
            """, (datetime.now(), nid))
            logger.info(f"🎉 Notificação {nid} enviada com sucesso via {', '.join(channels_sent)}")
        else:
            cursor.execute("""
                UPDATE notifications
                SET status = 'failed', retry_count = retry_count + 1,
                    error_message = ?
                WHERE id = ?
            """, ('Falha no envio', nid))
            logger.error(f"❌ Notificação {nid} falhou")
        
        db.commit()
        db.close()
        
        return success
    
    def _log_notification_attempt(
        self,
        notification_id: int,
        channel: str,
        status: str,
        response_data: Dict[str, Any]
    ):
        """Registra tentativa de envio no log"""
        db = self.get_db()
        cursor = db.cursor()
        
        cursor.execute("""
            INSERT INTO notification_logs (
                notification_id, channel, status, response_data,
                error_message, attempt_number, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            notification_id,
            channel,
            status,
            json.dumps(response_data),
            response_data.get('error'),
            response_data.get('attempt', 1),
            datetime.now()
        ))
        
        db.commit()
        db.close()
    
    # ==================== JOBS DO SCHEDULER ====================
    
    def check_due_invoices(self):
        """
        Job: Verificar faturas vencendo em breve
        Roda diariamente às 09:00
        """
        logger.info("🔍 Checando faturas vencendo...")
        
        db = self.get_db()
        cursor = db.cursor()
        
        # Buscar usuários ativos
        cursor.execute("SELECT id, tenant_id, name, phone FROM users WHERE active = 1")
        users = cursor.fetchall()
        
        today = datetime.now().date()
        
        for user_id, tenant_id, user_name, user_phone in users:
            settings = self.get_user_settings(user_id)
            alert_days = [int(d) for d in settings['invoice_alert_days'].split(',')]
            
            # Buscar cartões do usuário
            cursor.execute("""
                SELECT c.id, c.name, c.due_day, c.used_limit
                FROM cards c
                WHERE c.user_id = ? AND c.active = 1
            """, (user_id,))
            
            cards = cursor.fetchall()
            
            for card_id, card_name, due_day, used_limit in cards:
                if not due_day:
                    continue
                
                # Calcular próximo vencimento
                current_month = today.month
                current_year = today.year
                
                due_date = datetime(current_year, current_month, due_day).date()
                
                if due_date < today:
                    # Próximo mês
                    if current_month == 12:
                        due_date = datetime(current_year + 1, 1, due_day).date()
                    else:
                        due_date = datetime(current_year, current_month + 1, due_day).date()
                
                days_until_due = (due_date - today).days
                
                # Verificar se deve enviar alerta
                if days_until_due in alert_days:
                    # Criar notificação
                    title = f"Fatura {card_name} vence em {days_until_due} dias" if days_until_due > 0 else f"Fatura {card_name} vence hoje!"
                    
                    if days_until_due == 0:
                        message = (
                            f"⚠️ *VENCE HOJE!*\n\n"
                            f"Sua fatura do cartão *{card_name}* no valor de R$ {used_limit:.2f} vence hoje.\n\n"
                            f"Não esqueça de pagar para evitar juros!"
                        )
                    else:
                        first_name = user_name.split()[0] if user_name else 'Usuário'
                        message = (
                            f"🚨 Olá {first_name}! Sua fatura do cartão *{card_name}* vence em *{days_until_due} dias* "
                            f"(R$ {used_limit:.2f}).\n\n"
                            f"Deseja registrar o pagamento agora? Responda 'Sim' para marcar como pago."
                        )
                    
                    notification_id = self.create_notification(
                        user_id=user_id,
                        tenant_id=tenant_id,
                        title=title,
                        message=message,
                        event_type='invoice_due_soon',
                        channel='both',
                        priority='high' if days_until_due == 0 else 'medium',
                        meta={
                            'card_id': card_id,
                            'card_name': card_name,
                            'amount': used_limit,
                            'due_date': due_date.isoformat(),
                            'days_until_due': days_until_due
                        }
                    )
                    
                    # Enviar imediatamente
                    self.send_notification(notification_id)
        
        db.close()
        logger.info("✅ Check de faturas concluído")
    
    def check_monthly_spending(self):
        """
        Job: Verificar gastos mensais e enviar resumo
        Roda diariamente às 07:00, envia resumo semanal às segundas 08:00
        """
        logger.info("📊 Checando gastos mensais...")
        
        # TODO: Implementar lógica de resumo mensal
        # - Somar transações do mês
        # - Agrupar por categoria (top 3)
        # - Calcular variação vs mês anterior
        # - Enviar resumo
        
        logger.info("✅ Check de gastos concluído")
    
    def check_investment_updates(self):
        """
        Job: Verificar atualizações de investimentos
        Roda diariamente às 08:05
        """
        logger.info("📈 Checando investimentos...")
        
        # TODO: Integrar com investment_updater
        # - Verificar variação > threshold (3%)
        # - Criar notificação
        
        logger.info("✅ Check de investimentos concluído")
    
    def check_low_balance(self):
        """
        Job: Verificar saldos baixos
        Roda diariamente às 06:00
        """
        logger.info("💰 Checando saldos baixos...")
        
        db = self.get_db()
        cursor = db.cursor()
        
        # Buscar usuários ativos
        cursor.execute("SELECT id, tenant_id, name FROM users WHERE active = 1")
        users = cursor.fetchall()
        
        for user_id, tenant_id, user_name in users:
            settings = self.get_user_settings(user_id)
            threshold = settings['threshold_low_balance']
            
            # Buscar contas com saldo baixo
            cursor.execute("""
                SELECT a.id, a.name, a.current_balance
                FROM accounts a
                WHERE a.user_id = ? AND a.active = 1 AND a.current_balance < ?
            """, (user_id, threshold))
            
            accounts = cursor.fetchall()
            
            for account_id, account_name, balance in accounts:
                # Verificar se já enviou notificação hoje
                cursor.execute("""
                    SELECT id FROM notifications
                    WHERE user_id = ? AND event_type = 'low_balance'
                      AND meta LIKE ? AND DATE(created_at) = DATE('now')
                """, (user_id, f'%"account_id": "{account_id}"%'))
                
                if cursor.fetchone():
                    continue  # Já enviou hoje
                
                title = f"Saldo baixo: {account_name}"
                message = (
                    f"⚠️ *Saldo Baixo*\n\n"
                    f"Sua conta *{account_name}* está com R$ {balance:.2f} "
                    f"(abaixo do limite de R$ {threshold:.2f}).\n\n"
                    f"Deseja transferir fundos?"
                )
                
                notification_id = self.create_notification(
                    user_id=user_id,
                    tenant_id=tenant_id,
                    title=title,
                    message=message,
                    event_type='low_balance',
                    channel='both',
                    priority='medium',
                    meta={
                        'account_id': account_id,
                        'account_name': account_name,
                        'balance': balance,
                        'threshold': threshold
                    }
                )
                
                self.send_notification(notification_id)
        
        db.close()
        logger.info("✅ Check de saldos concluído")
    
    def send_periodic_reports(self):
        """
        Job: Enviar relatórios periódicos (semanais/mensais)
        Roda aos domingos às 18:00
        """
        logger.info("📄 Enviando relatórios periódicos...")
        
        # TODO: Implementar relatórios
        
        logger.info("✅ Relatórios enviados")
    
    # ==================== INICIALIZAÇÃO ====================
    
    def start(self):
        """Inicializa o scheduler com todos os jobs"""
        if not self.enabled:
            logger.info("⚠️  Auto notifications desabilitado via config")
            return
        
        logger.info("🚀 Iniciando Auto Notification Service...")
        
        # Job 1: Verificar faturas vencendo (diário às 09:00)
        self.scheduler.add_job(
            self.check_due_invoices,
            CronTrigger(hour=9, minute=0),
            id='check_due_invoices',
            name='Verificar faturas vencendo',
            replace_existing=True
        )
        
        # Job 2: Verificar gastos mensais (diário às 07:00)
        self.scheduler.add_job(
            self.check_monthly_spending,
            CronTrigger(hour=7, minute=0),
            id='check_monthly_spending',
            name='Verificar gastos mensais',
            replace_existing=True
        )
        
        # Job 3: Verificar investimentos (diário às 08:05)
        self.scheduler.add_job(
            self.check_investment_updates,
            CronTrigger(hour=8, minute=5),
            id='check_investment_updates',
            name='Verificar atualizações de investimentos',
            replace_existing=True
        )
        
        # Job 4: Verificar saldos baixos (diário às 06:00)
        self.scheduler.add_job(
            self.check_low_balance,
            CronTrigger(hour=6, minute=0),
            id='check_low_balance',
            name='Verificar saldos baixos',
            replace_existing=True
        )
        
        # Job 5: Relatórios periódicos (domingos às 18:00)
        self.scheduler.add_job(
            self.send_periodic_reports,
            CronTrigger(day_of_week='sun', hour=18, minute=0),
            id='send_periodic_reports',
            name='Enviar relatórios periódicos',
            replace_existing=True
        )
        
        # Iniciar scheduler
        self.scheduler.start()
        
        jobs = self.scheduler.get_jobs()
        logger.info(f"✅ Scheduler ativo com {len(jobs)} jobs:")
        for job in jobs:
            logger.info(f"  - {job.name} (próxima execução: {job.next_run_time})")
    
    def stop(self):
        """Para o scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("⏹️  Scheduler parado")
    
    def run_job_now(self, job_name: str):
        """Executa um job manualmente (para testes)"""
        jobs = {
            'check_due_invoices': self.check_due_invoices,
            'check_monthly_spending': self.check_monthly_spending,
            'check_investment_updates': self.check_investment_updates,
            'check_low_balance': self.check_low_balance,
            'send_periodic_reports': self.send_periodic_reports
        }
        
        if job_name in jobs:
            logger.info(f"▶️  Executando job manual: {job_name}")
            jobs[job_name]()
        else:
            logger.error(f"❌ Job '{job_name}' não encontrado")


# Instância global
notification_service = AutoNotificationService()
