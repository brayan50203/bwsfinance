#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Teste - Sistema de Notificações IA via WhatsApp
"""

import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_nlp():
    """Testar classificador NLP"""
    print("\n" + "="*60)
    print("🧠 TESTE 1: Classificador NLP")
    print("="*60)
    
    from modules.nlp_classifier import NLPClassifier
    
    nlp = NLPClassifier()
    
    test_cases = [
        "Paguei R$ 50,00 no mercado hoje",
        "Recebi 5000 reais de salário dia 5",
        "Gastei 45 no almoço ontem",
        "Comprei gasolina por R$ 120",
        "Fiz freelance e ganhei R$ 800 dia 10 de novembro",
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n📝 Caso {i}: {text}")
        result = nlp.classify(text)
        
        print(f"   💰 Valor: R$ {result['amount']}")
        print(f"   📂 Tipo: {result['type']}")
        print(f"   🏷️ Categoria: {result['category']}")
        print(f"   📅 Data: {result['date']}")
        print(f"   ✅ Confiança: {result['confidence']:.0%}")
    
    print("\n✅ Teste NLP concluído!")


def test_notification_center():
    """Testar central de notificações"""
    print("\n" + "="*60)
    print("🔔 TESTE 2: Central de Notificações")
    print("="*60)
    
    try:
        from services.notification_center import NotificationCenter
        
        # Simular usuário
        user_id = "test-user-001"
        tenant_id = "test-tenant-001"
        
        center = NotificationCenter()
        
        # Criar notificação de teste
        print("\n📤 Criando notificação de teste...")
        
        notif_id = center.create_notification(
            user_id=user_id,
            tenant_id=tenant_id,
            title="🎉 Teste de Notificação",
            message="Esta é uma notificação de teste do sistema!",
            category="system",
            priority="high",
            channels=['system']
        )
        
        if notif_id:
            print(f"✅ Notificação criada: {notif_id}")
        else:
            print("❌ Falha ao criar notificação")
        
        print("\n✅ Teste de notificação concluído!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()


def test_whatsapp_sender():
    """Testar envio via WhatsApp"""
    print("\n" + "="*60)
    print("📱 TESTE 3: WhatsApp Sender")
    print("="*60)
    
    try:
        from services.whatsapp_sender import WhatsAppSender
        
        sender = WhatsAppSender()
        
        print("\n📋 Configuração:")
        print(f"   Server URL: {sender.server_url}")
        print(f"   Token: {'*' * len(sender.auth_token)}")
        
        # Teste de conexão (sem enviar de verdade)
        print("\n⚠️  Para testar envio real, configure um número válido")
        print("   e descomente a linha de envio no código")
        
        # Descomentar para testar de verdade:
        # test_number = "+5511999999999"  # Seu número
        # success = sender.send(test_number, "🎉 Teste do BWS Finance!")
        # print(f"{'✅' if success else '❌'} Envio: {success}")
        
        print("\n✅ Teste WhatsApp Sender concluído!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()


def test_notification_ai():
    """Testar IA de análise"""
    print("\n" + "="*60)
    print("🤖 TESTE 4: Notification AI")
    print("="*60)
    
    try:
        from services.notification_ai import NotificationAI
        
        # Simular usuário
        user_id = "test-user-001"
        tenant_id = "test-tenant-001"
        
        ai = NotificationAI()
        
        print("\n📊 Testando análise de padrões...")
        
        # Simular análise (precisa de dados no banco)
        print("   ⚠️  Requer dados reais no banco para análise completa")
        print("   Execute após adicionar transações")
        
        print("\n✅ Teste Notification AI concluído!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()


def check_dependencies():
    """Verificar dependências instaladas"""
    print("\n" + "="*60)
    print("📦 Verificando Dependências")
    print("="*60)
    
    dependencies = {
        'flask': 'Flask',
        'requests': 'Requests',
        'sqlite3': 'SQLite3 (built-in)',
    }
    
    optional = {
        'whisper': 'OpenAI Whisper (áudio)',
        'PIL': 'Pillow (imagens)',
        'pytesseract': 'Tesseract OCR',
        'PyPDF2': 'PyPDF2 (PDFs)',
    }
    
    print("\n✅ Dependências Obrigatórias:")
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"   ✓ {name}")
        except ImportError:
            print(f"   ✗ {name} - FALTANDO!")
    
    print("\n⭐ Dependências Opcionais (para IA completa):")
    for module, name in optional.items():
        try:
            __import__(module)
            print(f"   ✓ {name}")
        except ImportError:
            print(f"   ✗ {name} - não instalado")
    
    print("\n💡 Para instalar opcionais:")
    print("   pip install openai-whisper pillow pytesseract PyPDF2")


def main():
    """Executar todos os testes"""
    print("\n" + "="*60)
    print("🚀 BWS Finance - Teste Completo")
    print("   Sistema de Notificações IA + WhatsApp")
    print("="*60)
    
    check_dependencies()
    
    test_nlp()
    test_notification_center()
    test_whatsapp_sender()
    test_notification_ai()
    
    print("\n" + "="*60)
    print("✅ TODOS OS TESTES CONCLUÍDOS!")
    print("="*60)
    print("\n📚 Próximos passos:")
    print("   1. Configure .env com WHATSAPP_AUTH_TOKEN")
    print("   2. Inicie o servidor WhatsApp: cd whatsapp_server && node index.js")
    print("   3. Escaneie QR Code")
    print("   4. Envie mensagem de teste")
    print("   5. Acesse http://localhost:5000/settings para configurar")
    print("\n")


if __name__ == '__main__':
    main()
