"""
Script de teste para verificar categorização do WhatsApp
"""
from modules.nlp_classifier import NLPClassifier

# Criar classifier
nlp = NLPClassifier()

# Casos de teste
test_cases = [
    "Paguei R$ 50,00 no mercado hoje",
    "Gastei 150 reais no uber",
    "Comprei uma pizza por R$ 45",
    "Paguei 200 reais na farmácia",
    "Gastei R$ 80 na Netflix",
    "Comprei um livro por 35 reais",
    "Paguei R$ 1200 de aluguel",
    "Gastei 300 na loja de roupa"
]

print("\n" + "="*80)
print("TESTE DE CATEGORIZAÇÃO - NLP CLASSIFIER")
print("="*80 + "\n")

for i, text in enumerate(test_cases, 1):
    print(f"\n{'─'*80}")
    print(f"Teste {i}: {text}")
    print(f"{'─'*80}")
    
    result = nlp.classify(text)
    
    print(f"\n✅ RESULTADO:")
    print(f"   💰 Valor: R$ {result['amount']:.2f}" if result['amount'] else "   ❌ Valor não detectado")
    print(f"   📅 Data: {result['date']}")
    print(f"   📂 Categoria: {result['category']}")
    print(f"   📝 Descrição: {result['description']}")
    print(f"   📊 Confiança: {result['confidence']:.2%}")

print("\n" + "="*80)
print("FIM DOS TESTES")
print("="*80 + "\n")
