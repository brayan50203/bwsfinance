#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Notification Center - Core Module
Sistema completo de notificações para BWS Finance
"""

import sqlite3
import json
from datetime import datetime, time as dt_time
from typing import Dict, List, Optional, Any
from enum import Enum
import logging

# Configurar logger
logger = logging.getLogger('notification_center')
logger.setLevel(logging.INFO)


class NotificationCategory(Enum):
    """Categorias de notificações"""
    FINANCEIRO = "Financeiro"
    INVESTIMENTOS = "Investimentos"
    SISTEMA = "Sistema"
    ERRO = "Erro"
    ATUALIZACAO = "Atualização"
    IA = "IA"


class NotificationPriority(Enum):
    """Prioridades de notificações"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationChannel(Enum):
    """Canais de envio"""
    SYSTEM = "system"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    PUSH = "push"


class NotificationCenter:
    """
    Sistema central de gerenciamento de notificações
    """
    
    def __init__(self, db_path: str = 'bws_finance.db'):
        self.db_path = db_path
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Garante que as tabelas de notificações existem"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Ler e executar o schema
        try:
            with open('migrations/add_notifications_tables.sql', 'r', encoding='utf-8') as f:
                schema = f.read()
                cursor.executescript(schema)
            conn.commit()
            logger.info("[OK] Tabelas de notificações criadas/verificadas")
        except Exception as e:
            logger.error(f"[ERRO] Falha ao criar tabelas: {e}")
        finally:
            conn.close()
    
    def create_notification(
        self,
        user_id: str,
        tenant_id: str,
        title: str,
        message: str,
        category: NotificationCategory,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        channels: List[NotificationChannel] = None,
        related_type: str = None,
        related_id: str = None,
        metadata: Dict[str, Any] = None
    ) -> Optional[int]:
        """
        Cria uma nova notificação
        
        Args:
            user_id: ID do usuário
            tenant_id: ID do tenant
            title: Título da notificação
            message: Mensagem completa
            category: Categoria (enum)
            priority: Prioridade (enum)
            channels: Lista de canais para enviar (padrão: system)
            related_type: Tipo do objeto relacionado
            related_id: ID do objeto relacionado
            metadata: Dados extras em JSON
        
        Returns:
            ID da notificação criada ou None se falhar
        """
        if channels is None:
            channels = [NotificationChannel.SYSTEM]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Verificar se está em horário permitido
            if not self._is_notification_time_allowed(user_id):
                logger.info(f"[SKIP] Notificação para {user_id} fora do horário permitido")
                return None
            
            # Criar notificação principal
            cursor.execute("""
                INSERT INTO notifications (
                    user_id, tenant_id, title, message, category, 
                    priority, status, related_type, related_id, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, 'unread', ?, ?, ?)
            """, (
                user_id, tenant_id, title, message, category.value,
                priority.value, related_type, related_id,
                json.dumps(metadata) if metadata else None
            ))
            
            notification_id = cursor.lastrowid
            
            # Obter preferências do usuário
            prefs = self.get_user_preferences(user_id)
            
            # Enviar para canais externos
            for channel in channels:
                if channel == NotificationChannel.SYSTEM:
                    continue  # Sistema já está criado
                
                # Verificar se canal está habilitado
                if channel == NotificationChannel.EMAIL and not prefs.get('enable_email'):
                    continue
                if channel == NotificationChannel.WHATSAPP and not prefs.get('enable_whatsapp'):
                    continue
                if channel == NotificationChannel.PUSH and not prefs.get('enable_push'):
                    continue
                
                # Despachar para serviço externo
                self._dispatch_external(notification_id, channel, title, message, prefs)
            
            conn.commit()
            logger.info(f"[OK] Notificação #{notification_id} criada para {user_id}")
            return notification_id
            
        except Exception as e:
            conn.rollback()
            logger.error(f"[ERRO] Falha ao criar notificação: {e}")
            return None
        finally:
            conn.close()
    
    def _is_notification_time_allowed(self, user_id: str) -> bool:
        """Verifica se está no horário permitido para notificações"""
        prefs = self.get_user_preferences(user_id)
        
        if not prefs:
            return True
        
        try:
            quiet_start = dt_time.fromisoformat(prefs.get('quiet_hours_start', '22:00'))
            quiet_end = dt_time.fromisoformat(prefs.get('quiet_hours_end', '08:00'))
            now = datetime.now().time()
            
            # Se quiet_start < quiet_end (ex: 22:00 - 08:00), período cruza meia-noite
            if quiet_start < quiet_end:
                return not (quiet_start <= now <= quiet_end)
            else:
                return quiet_end <= now <= quiet_start
        except Exception as e:
            logger.warning(f"[AVISO] Erro ao verificar horário: {e}")
            return True
    
    def _dispatch_external(
        self, 
        notification_id: int, 
        channel: NotificationChannel,
        title: str,
        message: str,
        prefs: Dict
    ):
        """Despacha notificação para canal externo"""
        try:
            # Importar sender dinamicamente
            if channel == NotificationChannel.EMAIL:
                from services.email_sender import send_email_notification
                email = prefs.get('email_address')
                if email:
                    send_email_notification(email, title, message)
                    self._log_send(notification_id, 'email', 'sent')
            
            elif channel == NotificationChannel.WHATSAPP:
                # 🚨 PROTEÇÃO: Só envia se WhatsApp estiver HABILITADO e número CONFIGURADO
                if not prefs.get('enable_whatsapp'):
                    logger.info(f"[SKIP] WhatsApp desabilitado para user {user_id}")
                    return
                
                phone = prefs.get('whatsapp_number')
                if not phone or phone.strip() == '':
                    logger.warning(f"[SKIP] WhatsApp sem número configurado para user {user_id}")
                    return
                
                from services.whatsapp_sender import send_whatsapp_notification
                logger.info(f"[WHATSAPP] Enviando para {phone[:8]}****")
                success = send_whatsapp_notification(phone, f"*{title}*\n\n{message}")
                
                if success:
                    self._log_send(notification_id, 'whatsapp', 'sent')
                else:
                    self._log_send(notification_id, 'whatsapp', 'failed', 'Servidor offline ou número inválido')
            
            elif channel == NotificationChannel.PUSH:
                # TODO: Implementar Web Push
                self._log_send(notification_id, 'push', 'pending')
        
        except Exception as e:
            logger.error(f"[ERRO] Falha ao enviar por {channel.value}: {e}")
            self._log_send(notification_id, channel.value, 'failed', str(e))
    
    def _log_send(
        self, 
        notification_id: int, 
        channel: str, 
        status: str, 
        error: str = None
    ):
        """Registra log de envio"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO notification_logs (notification_id, channel, status, error_message)
                VALUES (?, ?, ?, ?)
            """, (notification_id, channel, status, error))
            conn.commit()
        except Exception as e:
            logger.error(f"[ERRO] Falha ao registrar log: {e}")
        finally:
            conn.close()
    
    def get_user_notifications(
        self, 
        user_id: str, 
        status: str = None, 
        limit: int = 50
    ) -> List[Dict]:
        """
        Busca notificações do usuário
        
        Args:
            user_id: ID do usuário
            status: Filtrar por status ('unread', 'read', 'archived')
            limit: Limite de resultados
        
        Returns:
            Lista de notificações
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            query = """
                SELECT * FROM notifications
                WHERE user_id = ?
            """
            params = [user_id]
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            notifications = [dict(row) for row in cursor.fetchall()]
            
            # Parse metadata JSON
            for notif in notifications:
                if notif.get('metadata'):
                    try:
                        notif['metadata'] = json.loads(notif['metadata'])
                    except:
                        notif['metadata'] = {}
            
            return notifications
        
        except Exception as e:
            logger.error(f"[ERRO] Falha ao buscar notificações: {e}")
            return []
        finally:
            conn.close()
    
    def mark_as_read(self, notification_id: int, user_id: str) -> bool:
        """Marca notificação como lida"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE notifications
                SET status = 'read', read_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
            """, (notification_id, user_id))
            
            conn.commit()
            return cursor.rowcount > 0
        
        except Exception as e:
            logger.error(f"[ERRO] Falha ao marcar como lida: {e}")
            return False
        finally:
            conn.close()
    
    def mark_all_as_read(self, user_id: str) -> int:
        """Marca todas notificações como lidas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE notifications
                SET status = 'read', read_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND status = 'unread'
            """, (user_id,))
            
            conn.commit()
            return cursor.rowcount
        
        except Exception as e:
            logger.error(f"[ERRO] Falha ao marcar todas como lidas: {e}")
            return 0
        finally:
            conn.close()
    
    def delete_notification(self, notification_id: int, user_id: str) -> bool:
        """Deleta notificação"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                DELETE FROM notifications
                WHERE id = ? AND user_id = ?
            """, (notification_id, user_id))
            
            conn.commit()
            return cursor.rowcount > 0
        
        except Exception as e:
            logger.error(f"[ERRO] Falha ao deletar notificação: {e}")
            return False
        finally:
            conn.close()
    
    def get_unread_count(self, user_id: str) -> int:
        """Retorna contador de não lidas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM notifications
                WHERE user_id = ? AND status = 'unread'
            """, (user_id,))
            
            return cursor.fetchone()[0]
        
        except Exception as e:
            logger.error(f"[ERRO] Falha ao contar não lidas: {e}")
            return 0
        finally:
            conn.close()
    
    def get_user_preferences(self, user_id: str) -> Dict:
        """Busca preferências do usuário"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM notification_preferences
                WHERE user_id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            return dict(row) if row else {}
        
        except Exception as e:
            logger.error(f"[ERRO] Falha ao buscar preferências: {e}")
            return {}
        finally:
            conn.close()
    
    def update_preferences(self, user_id: str, preferences: Dict) -> bool:
        """Atualiza preferências do usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Campos permitidos
            allowed_fields = [
                'enable_system', 'enable_email', 'enable_whatsapp', 'enable_push',
                'high_expense_threshold', 'investment_change_threshold',
                'quiet_hours_start', 'quiet_hours_end',
                'email_address', 'whatsapp_number',
                'daily_summary', 'weekly_report', 'monthly_report',
                'enable_ai_insights', 'enable_pattern_detection'
            ]
            
            # Construir query dinamicamente
            updates = []
            values = []
            
            for field, value in preferences.items():
                if field in allowed_fields:
                    updates.append(f"{field} = ?")
                    values.append(value)
            
            if not updates:
                return False
            
            values.append(user_id)
            
            query = f"""
                UPDATE notification_preferences
                SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """
            
            cursor.execute(query, values)
            conn.commit()
            
            return cursor.rowcount > 0
        
        except Exception as e:
            logger.error(f"[ERRO] Falha ao atualizar preferências: {e}")
            return False
        finally:
            conn.close()


# =====================================================
# FACTORY FUNCTIONS (Atalhos para criar notificações)
# =====================================================

def notify_high_expense(user_id: str, tenant_id: str, amount: float, description: str):
    """Notifica gasto alto detectado"""
    center = NotificationCenter()
    
    center.create_notification(
        user_id=user_id,
        tenant_id=tenant_id,
        title="Gasto Alto Detectado 💸",
        message=f"Foi registrado um gasto de R$ {amount:.2f} em '{description}'. Verifique se está dentro do planejado.",
        category=NotificationCategory.FINANCEIRO,
        priority=NotificationPriority.HIGH,
        channels=[NotificationChannel.SYSTEM, NotificationChannel.WHATSAPP],
        related_type='transaction',
        metadata={'amount': amount, 'description': description}
    )


def notify_investment_change(user_id: str, tenant_id: str, investment_name: str, change_pct: float):
    """Notifica mudança relevante em investimento"""
    center = NotificationCenter()
    
    emoji = "📈" if change_pct > 0 else "📉"
    signal = "+" if change_pct > 0 else ""
    
    center.create_notification(
        user_id=user_id,
        tenant_id=tenant_id,
        title=f"Investimento Atualizado {emoji}",
        message=f"Seu investimento em {investment_name} teve uma variação de {signal}{change_pct:.2f}% hoje.",
        category=NotificationCategory.INVESTIMENTOS,
        priority=NotificationPriority.NORMAL,
        channels=[NotificationChannel.SYSTEM, NotificationChannel.PUSH],
        related_type='investment',
        metadata={'investment': investment_name, 'change': change_pct}
    )


def notify_import_success(user_id: str, tenant_id: str, count: int, source: str):
    """Notifica importação bem-sucedida"""
    center = NotificationCenter()
    
    center.create_notification(
        user_id=user_id,
        tenant_id=tenant_id,
        title="Importação Concluída ✅",
        message=f"{count} transações foram importadas com sucesso de '{source}'.",
        category=NotificationCategory.SISTEMA,
        priority=NotificationPriority.NORMAL,
        channels=[NotificationChannel.SYSTEM],
        related_type='import',
        metadata={'count': count, 'source': source}
    )


def notify_api_error(user_id: str, tenant_id: str, api_name: str, error: str):
    """Notifica erro em API externa"""
    center = NotificationCenter()
    
    center.create_notification(
        user_id=user_id,
        tenant_id=tenant_id,
        title=f"Erro de Integração ⚠️",
        message=f"Não foi possível conectar com {api_name}: {error}",
        category=NotificationCategory.ERRO,
        priority=NotificationPriority.HIGH,
        channels=[NotificationChannel.SYSTEM, NotificationChannel.EMAIL],
        metadata={'api': api_name, 'error': error}
    )


def notify_ai_insight(user_id: str, tenant_id: str, insight: str, suggestion: str):
    """Notifica insight de IA"""
    center = NotificationCenter()
    
    center.create_notification(
        user_id=user_id,
        tenant_id=tenant_id,
        title="Insight Financeiro 🧠",
        message=f"{insight}\n\nSugestão: {suggestion}",
        category=NotificationCategory.IA,
        priority=NotificationPriority.NORMAL,
        channels=[NotificationChannel.SYSTEM, NotificationChannel.WHATSAPP],
        metadata={'insight': insight, 'suggestion': suggestion}
    )
