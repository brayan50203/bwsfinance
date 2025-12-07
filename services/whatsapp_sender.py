"""Simple WhatsApp sender that calls a Node WPPConnect/Baileys server via HTTP webhook.
If the Node server is not configured or offline, logs and simulates send for local testing.
"""
import os
import requests
import logging

logger = logging.getLogger('notifications.whatsapp')

WHATSAPP_SERVER_URL = os.environ.get('WHATSAPP_SERVER_URL', 'http://localhost:3000')
WHATSAPP_AUTH_TOKEN = os.environ.get('WHATSAPP_AUTH_TOKEN', '')

def send_message(phone, text, template_data=None):
    """Send a WhatsApp message via the configured Node server.

    Returns True on success, False on failure (simulated send returns True).
    """
    url = f"{WHATSAPP_SERVER_URL.rstrip('/')}/send-message"
    headers = {}
    if WHATSAPP_AUTH_TOKEN:
        headers['Authorization'] = f"Bearer {WHATSAPP_AUTH_TOKEN}"

    payload = {
        'phone': phone,
        'text': text,
        'template_data': template_data or {}
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        if resp.status_code == 200:
            logger.info('WhatsApp send OK to %s', phone)
            return True
        else:
            logger.error('WhatsApp server returned %s: %s', resp.status_code, resp.text)
            return False
    except requests.exceptions.RequestException as e:
        logger.warning('WhatsApp server unavailable, simulating send to %s: %s', phone, e)
        # simulate for local tests
        logger.info('SIMULATED WhatsApp -> %s : %s', phone, text)
        return True
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WhatsApp Sender - Notification System
Envia notificações via WhatsApp usando WPPConnect ou API Meta
"""

import requests
import os
import logging
from typing import Optional

logger = logging.getLogger('whatsapp_sender')


class WhatsAppSender:
    """Gerenciador de envio via WhatsApp"""
    
    def __init__(self):
        self.server_url = os.getenv('WHATSAPP_SERVER_URL', 'http://localhost:3000')
        self.auth_token = os.getenv('WHATSAPP_AUTH_TOKEN', 'change_me')
    
    def send(self, to_number: str, message: str) -> bool:
        """
        Envia mensagem via WhatsApp
        
        Args:
            to_number: Número do destinatário (formato: +5511999999999)
            message: Mensagem de texto
        
        Returns:
            True se enviado com sucesso
        """
        try:
            # 🚨 VALIDAÇÃO: Verificar se número não está vazio
            if not to_number or to_number.strip() == '':
                logger.error("[ERRO] Número vazio, não enviando")
                return False
            
            # Formatar número (remover espaços e caracteres especiais)
            phone = to_number.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').replace('.', '')
            
            # 🚨 VALIDAÇÃO: Verificar se tem dígitos suficientes
            digits_only = ''.join(filter(str.isdigit, phone))
            if len(digits_only) < 10:
                logger.error(f"[ERRO] Número inválido (poucos dígitos): {to_number}")
                return False
            
            # Se não começar com +, adicionar +55 (Brasil)
            if not phone.startswith('+'):
                phone = f'+55{phone}'
            
            logger.info(f"[WHATSAPP] Tentando enviar para {phone[:8]}****")
            
            # Enviar via servidor Node.js (WPPConnect)
            response = requests.post(
                f"{self.server_url}/send",
                json={
                    'to': phone,
                    'message': message,
                    'token': self.auth_token
                },
                timeout=10
            )
            
            if response.ok:
                logger.info(f"[OK] WhatsApp enviado para {phone}")
                return True
            else:
                logger.error(f"[ERRO] WhatsApp falhou: {response.text}")
                return False
        
        except requests.exceptions.ConnectionError:
            logger.warning("[AVISO] Servidor WhatsApp offline")
            return False
        except Exception as e:
            logger.error(f"[ERRO] Falha ao enviar WhatsApp: {e}")
            return False
    
    def send_with_button(
        self, 
        to_number: str, 
        message: str, 
        button_text: str, 
        button_url: str
    ) -> bool:
        """
        Envia mensagem com botão interativo
        
        Args:
            to_number: Número do destinatário
            message: Texto da mensagem
            button_text: Texto do botão
            button_url: URL do botão
        
        Returns:
            True se enviado com sucesso
        """
        try:
            phone = to_number.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            if not phone.startswith('+'):
                phone = f'+55{phone}'
            
            response = requests.post(
                f"{self.server_url}/send-button",
                json={
                    'to': phone,
                    'message': message,
                    'button': {
                        'text': button_text,
                        'url': button_url
                    },
                    'token': self.auth_token
                },
                timeout=10
            )
            
            if response.ok:
                logger.info(f"[OK] WhatsApp com botão enviado para {phone}")
                return True
            else:
                logger.error(f"[ERRO] WhatsApp com botão falhou: {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"[ERRO] Falha ao enviar WhatsApp com botão: {e}")
            return False


# Função de atalho
def send_whatsapp_notification(to_number: str, message: str) -> bool:
    """Envia notificação via WhatsApp (atalho)"""
    sender = WhatsAppSender()
    return sender.send(to_number, message)


def send_whatsapp_with_action(
    to_number: str, 
    message: str, 
    action_text: str = "Ver no Painel",
    action_url: str = "http://127.0.0.1:5000/dashboard"
) -> bool:
    """Envia notificação com botão de ação"""
    sender = WhatsAppSender()
    return sender.send_with_button(to_number, message, action_text, action_url)
