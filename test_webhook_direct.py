"""
Script para testar se mensagens estão chegando no webhook
"""
import requests
import json

url = "http://localhost:5000/api/whatsapp/webhook"
headers = {
    "Authorization": "Bearer bws_finance_token_55653",
    "Content-Type": "application/json"
}

# Teste 1: Mensagem de texto simples
payload = {
    "from": "+5511974764971",
    "type": "text",
    "text": "oi teste do script python",
    "timestamp": 1234567890
}

print("=" * 60)
print("TESTANDO WEBHOOK DO WHATSAPP")
print("=" * 60)
print(f"\nURL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print("\nEnviando...")

try:
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    print(f"\n✅ Status: {response.status_code}")
    print(f"Resposta: {response.json()}")
except Exception as e:
    print(f"\n❌ Erro: {e}")
