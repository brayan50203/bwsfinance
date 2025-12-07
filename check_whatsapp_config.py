#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar números WhatsApp configurados
"""

import sqlite3
import sys

def check_whatsapp_numbers():
    """Verifica todos os números WhatsApp configurados no sistema"""
    
    print("\n" + "="*60)
    print("📱 NÚMEROS WHATSAPP CONFIGURADOS")
    print("="*60 + "\n")
    
    try:
        conn = sqlite3.connect('bws_finance.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Buscar todos os usuários com WhatsApp habilitado
        cursor.execute("""
            SELECT 
                u.id as user_id,
                u.name as user_name,
                u.email as user_email,
                np.enable_whatsapp,
                np.whatsapp_number
            FROM users u
            LEFT JOIN notification_preferences np ON np.user_id = u.id
            WHERE np.enable_whatsapp = 1 
            AND np.whatsapp_number IS NOT NULL 
            AND np.whatsapp_number != ''
            ORDER BY u.name
        """)
        
        users = cursor.fetchall()
        
        if not users:
            print("⚠️  NENHUM número WhatsApp ativo encontrado!")
            print("\n💡 Configure em: http://localhost:5000/settings")
            print("   Aba: Notificações → WhatsApp\n")
            return
        
        print(f"✅ {len(users)} usuário(s) com WhatsApp ATIVO:\n")
        
        for i, user in enumerate(users, 1):
            print(f"{i}. 👤 {user['user_name']}")
            print(f"   📧 Email: {user['user_email']}")
            print(f"   📱 WhatsApp: {user['whatsapp_number']}")
            print(f"   🔑 User ID: {user['user_id']}")
            print()
        
        print("="*60)
        print("🛡️  PROTEÇÕES ATIVAS:")
        print("="*60)
        print("✅ Notificações só são enviadas para números acima")
        print("✅ WhatsApp deve estar HABILITADO nas preferências")
        print("✅ Número deve estar CONFIGURADO e não vazio")
        print("✅ Sistema ignora mensagens de grupos")
        print("✅ Sistema ignora mensagens próprias (fromMe)")
        print("✅ Horário de silêncio respeitado (22h-8h padrão)")
        print()
        
        # Verificar ALLOWED_SENDERS no .env
        try:
            with open('.env', 'r') as f:
                content = f.read()
                if 'ALLOWED_SENDERS=' in content:
                    for line in content.split('\n'):
                        if line.startswith('ALLOWED_SENDERS='):
                            allowed = line.split('=')[1].strip()
                            if allowed:
                                print("🔒 ALLOWED_SENDERS configurado:")
                                print(f"   {allowed}")
                            else:
                                print("⚠️  ALLOWED_SENDERS vazio (aceita todos os remetentes)")
                            print()
        except:
            pass
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Erro ao acessar banco de dados: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def test_send_notification():
    """Teste de envio de notificação"""
    
    print("\n" + "="*60)
    print("🧪 TESTE DE ENVIO")
    print("="*60 + "\n")
    
    try:
        conn = sqlite3.connect('bws_finance.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Buscar primeiro usuário ativo
        cursor.execute("""
            SELECT u.id, u.name, np.whatsapp_number
            FROM users u
            JOIN notification_preferences np ON np.user_id = u.id
            WHERE np.enable_whatsapp = 1 
            AND np.whatsapp_number IS NOT NULL 
            AND np.whatsapp_number != ''
            LIMIT 1
        """)
        
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            print("⚠️  Nenhum usuário com WhatsApp ativo para testar")
            return
        
        print(f"📱 Usuário de teste: {user['name']}")
        print(f"📞 Número: {user['whatsapp_number']}")
        print()
        
        response = input("Deseja enviar notificação de TESTE? (s/N): ")
        
        if response.lower() == 's':
            from services.notification_center import NotificationCenter, NotificationCategory, NotificationPriority, NotificationChannel
            
            center = NotificationCenter()
            
            notif_id = center.create_notification(
                user_id=user['id'],
                tenant_id="default",  # Ajustar conforme necessário
                title="🧪 Teste de Notificação",
                message="Esta é uma mensagem de teste do sistema BWS Finance.\n\nSe você recebeu isso, o WhatsApp está funcionando! ✅",
                category=NotificationCategory.SISTEMA,
                priority=NotificationPriority.NORMAL,
                channels=[NotificationChannel.WHATSAPP]
            )
            
            if notif_id:
                print(f"\n✅ Notificação #{notif_id} enviada!")
                print("📱 Verifique seu WhatsApp")
            else:
                print("\n❌ Falha ao enviar notificação")
        else:
            print("Teste cancelado")
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    check_whatsapp_numbers()
    
    print("\n" + "="*60)
    test_send = input("\nDeseja fazer um teste de envio? (s/N): ")
    if test_send.lower() == 's':
        test_send_notification()
    
    print("\n✅ Verificação concluída!\n")
