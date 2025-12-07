"""Email sender using SMTP with simple retry/backoff and Jinja2 templates.
"""
import os
import smtplib
import logging
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger('notifications.email')

SMTP_HOST = os.environ.get('SMTP_HOST', 'localhost')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASS = os.environ.get('SMTP_PASS', '')
SMTP_FROM = os.environ.get('SMTP_FROM', 'noreply@localhost')

env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), '..', 'templates', 'emails')),
                  autoescape=select_autoescape(['html','xml']))

def send_email(to, subject, html_body, retries=3):
    attempt = 0
    while attempt < retries:
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = SMTP_FROM
            msg['To'] = to
            part = MIMEText(html_body, 'html')
            msg.attach(part)

            if SMTP_PORT == 465:
                server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10)
            else:
                server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
                server.starttls()

            if SMTP_USER and SMTP_PASS:
                server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_FROM, [to], msg.as_string())
            server.quit()
            logger.info('Email sent to %s', to)
            return True
        except Exception as e:
            wait = (2 ** attempt)
            logger.warning('Email send attempt %s failed: %s - retrying in %s sec', attempt+1, e, wait)
            time.sleep(wait)
            attempt += 1
    logger.error('Email send failed after %s attempts to %s', retries, to)
    return False

def render_template(template_name, **context):
    tpl = env.get_template(template_name)
    return tpl.render(**context)
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Email Sender - Notification System
Envia notificações por e-mail com templates HTML responsivos
"""

import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

logger = logging.getLogger('email_sender')


class EmailSender:
    """Gerenciador de envio de e-mails"""
    
    def __init__(self, config_path: str = 'config/email_config.json'):
        self.config = self._load_config(config_path)
    
    def _load_config(self, path: str) -> dict:
        """Carrega configurações de e-mail"""
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Configuração padrão
        return {
            'smtp_host': os.getenv('SMTP_HOST', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', 587)),
            'smtp_user': os.getenv('SMTP_USER', ''),
            'smtp_password': os.getenv('SMTP_PASSWORD', ''),
            'from_email': os.getenv('FROM_EMAIL', 'noreply@bwsfinance.com'),
            'from_name': 'BWS Finance'
        }
    
    def send(
        self, 
        to_email: str, 
        subject: str, 
        body: str, 
        html: bool = True
    ) -> bool:
        """
        Envia e-mail
        
        Args:
            to_email: Destinatário
            subject: Assunto
            body: Corpo da mensagem (texto ou HTML)
            html: Se True, envia como HTML
        
        Returns:
            True se enviado com sucesso
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.config['from_name']} <{self.config['from_email']}>"
            msg['To'] = to_email
            
            if html:
                # Template HTML responsivo
                html_body = self._build_html_template(subject, body)
                msg.attach(MIMEText(html_body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Conectar e enviar
            with smtplib.SMTP(self.config['smtp_host'], self.config['smtp_port']) as server:
                server.starttls()
                server.login(self.config['smtp_user'], self.config['smtp_password'])
                server.send_message(msg)
            
            logger.info(f"[OK] E-mail enviado para {to_email}")
            return True
        
        except Exception as e:
            logger.error(f"[ERRO] Falha ao enviar e-mail: {e}")
            return False
    
    def _build_html_template(self, title: str, message: str) -> str:
        """Cria template HTML responsivo"""
        return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f4f4f4;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 20px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: 600;
        }}
        .logo {{
            width: 60px;
            height: 60px;
            background: white;
            border-radius: 50%;
            margin: 0 auto 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
        }}
        .content {{
            padding: 30px 20px;
        }}
        .content h2 {{
            color: #667eea;
            margin-top: 0;
        }}
        .content p {{
            margin: 15px 0;
        }}
        .button {{
            display: inline-block;
            padding: 12px 30px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            margin: 20px 0;
            font-weight: 600;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #666;
            border-top: 1px solid #e9ecef;
        }}
        @media only screen and (max-width: 600px) {{
            .container {{
                border-radius: 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">💰</div>
            <h1>BWS Finance</h1>
        </div>
        <div class="content">
            <h2>{title}</h2>
            <p>{message}</p>
            <a href="http://127.0.0.1:5000/dashboard" class="button">Abrir no Painel</a>
        </div>
        <div class="footer">
            <p>Este é um e-mail automático do BWS Finance.</p>
            <p>Você está recebendo porque habilitou notificações por e-mail.</p>
            <p>Para alterar suas preferências, acesse: <a href="http://127.0.0.1:5000/notifications/preferences">Configurações de Notificações</a></p>
        </div>
    </div>
</body>
</html>
        """


# Função de atalho
def send_email_notification(to_email: str, title: str, message: str) -> bool:
    """Envia notificação por e-mail (atalho)"""
    sender = EmailSender()
    return sender.send(to_email, title, message, html=True)
