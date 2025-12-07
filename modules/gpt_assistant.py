"""
GPT Finance Assistant - Assistente Financeiro com IA (inspirado no Pixzinho Bot)
Conversação natural via WhatsApp usando OpenAI GPT
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, Optional, List
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# =========================================
# CONFIGURAÇÃO
# =========================================

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
USE_GPT = bool(OPENAI_API_KEY)  # Só ativa se tiver chave

if USE_GPT:
    try:
        from openai import OpenAI
        client_gpt = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("✅ GPT integrado e pronto!")
    except ImportError:
        USE_GPT = False
        logger.warning("⚠️ Módulo openai não instalado. Usando modo fallback.")
else:
    logger.info("ℹ️ OPENAI_API_KEY não configurada. Usando modo fallback.")


# =========================================
# SISTEMA DE PROMPTS (inspirado no Pixzinho)
# =========================================

SYSTEM_PROMPT = """Você é o BWS Finance Assistant, um assistente financeiro pessoal via WhatsApp.

**SUA PERSONALIDADE:**
- Amigável, prestativo e profissional
- Usa emojis para deixar a conversa mais leve 😊
- Explica conceitos financeiros de forma simples
- Motiva o usuário a ter disciplina financeira

**SUAS CAPACIDADES:**
1. Registrar transações (receitas e despesas)
2. Consultar saldo e extratos
3. Dar dicas financeiras personalizadas
4. Alertar sobre gastos altos
5. Sugerir economias e investimentos
6. Lembrar vencimentos e metas

**COMO PROCESSAR MENSAGENS:**
- Se a mensagem menciona gasto/compra → EXTRAIR dados e registrar despesa
- Se menciona recebimento/salário → EXTRAIR dados e registrar receita  
- Se é pergunta sobre saldo/extrato → CONSULTAR dados
- Se pede dica/ajuda → DAR conselho financeiro
- Se é casual/saudação → RESPONDER amigavelmente

**FORMATO DE EXTRAÇÃO (quando for transação):**
Retorne JSON puro sem markdown:
{
    "intent": "transaction",
    "type": "Despesa" ou "Receita",
    "amount": valor numérico,
    "description": descrição clara,
    "category": categoria identificada,
    "date": "YYYY-MM-DD",
    "account": nome da conta (se mencionado),
    "confidence": 0.0 a 1.0
}

**FORMATO DE RESPOSTA (outras mensagens):**
{
    "intent": "query" | "advice" | "greeting" | "help",
    "response": "sua resposta amigável aqui",
    "action": ação sugerida (opcional)
}

**EXEMPLOS:**
Usuário: "Gastei 45 reais no mercado hoje"
Você: {"intent": "transaction", "type": "Despesa", "amount": 45.0, "description": "Compra no mercado", "category": "Alimentação", "date": "2025-11-09", "confidence": 0.95}

Usuário: "quanto gastei esse mês?"  
Você: {"intent": "query", "response": "Vou consultar seus gastos do mês! 📊", "action": "get_monthly_expenses"}

Usuário: "oi"
Você: {"intent": "greeting", "response": "Olá! 👋 Como posso ajudar com suas finanças hoje?"}

**IMPORTANTE:** 
- Seja SEMPRE objetivo e preciso na extração
- Use português do Brasil
- Data de hoje: {today}
- Em caso de dúvida, pergunte ao usuário
"""

# =========================================
# GPT FINANCE ASSISTANT
# =========================================

class GPTFinanceAssistant:
    """Assistente financeiro com GPT para conversação natural"""
    
    def __init__(self):
        self.use_gpt = USE_GPT
        self.conversation_history: Dict[str, List] = {}  # Histórico por usuário
        self.max_history = 10  # Últimas 10 mensagens
        
    def process_message(self, text: str, user_id: str = 'default') -> Dict:
        """
        Processa mensagem do usuário com GPT
        
        Args:
            text: Mensagem do usuário
            user_id: ID do usuário (número WhatsApp)
            
        Returns:
            Dict com intent e dados extraídos
        """
        logger.info(f"🤖 Processando mensagem com GPT: {text[:100]}...")
        
        if not self.use_gpt:
            return self._fallback_processing(text)
        
        try:
            # Preparar histórico
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            
            history = self.conversation_history[user_id]
            
            # Construir mensagens
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT.format(today=datetime.now().strftime('%Y-%m-%d'))}
            ]
            
            # Adicionar histórico recente
            messages.extend(history[-self.max_history:])
            
            # Adicionar mensagem atual
            messages.append({"role": "user", "content": text})
            
            # Chamar GPT
            response = client_gpt.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            assistant_message = response.choices[0].message.content
            logger.info(f"✅ Resposta GPT: {assistant_message[:200]}...")
            
            # Atualizar histórico
            history.append({"role": "user", "content": text})
            history.append({"role": "assistant", "content": assistant_message})
            
            # Limpar histórico antigo
            if len(history) > self.max_history * 2:
                self.conversation_history[user_id] = history[-self.max_history * 2:]
            
            # Parse resposta
            result = self._parse_gpt_response(assistant_message)
            result['raw_response'] = assistant_message
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro no GPT: {e}")
            return self._fallback_processing(text)
    
    def _parse_gpt_response(self, response: str) -> Dict:
        """Parse da resposta do GPT"""
        try:
            # Tentar extrair JSON da resposta
            # GPT pode retornar JSON puro ou com markdown ```json
            response = response.strip()
            
            if response.startswith('```'):
                # Remover markdown
                lines = response.split('\n')
                json_lines = [l for l in lines if l and not l.startswith('```')]
                response = '\n'.join(json_lines)
            
            data = json.loads(response)
            
            # Validar campos obrigatórios
            if 'intent' not in data:
                data['intent'] = 'unknown'
            
            return data
            
        except json.JSONDecodeError:
            # Se não for JSON válido, interpretar como resposta de texto
            return {
                'intent': 'response',
                'response': response,
                'confidence': 0.5
            }
    
    def _fallback_processing(self, text: str) -> Dict:
        """Processamento fallback sem GPT (usando NLP básico)"""
        from modules.nlp_classifier import NLPClassifier
        
        classifier = NLPClassifier()
        result = classifier.classify(text)
        
        # Adaptar formato
        if result['amount']:
            return {
                'intent': 'transaction',
                'type': result['type'],
                'amount': result['amount'],
                'description': result['description'],
                'category': result['category'],
                'date': result['date'],
                'account': result['account'],
                'confidence': result['confidence'],
                'response': f"✅ Entendi! Registrei: {result['type']} de R$ {result['amount']:.2f} em {result['category']}"
            }
        else:
            return {
                'intent': 'unknown',
                'response': '❓ Desculpe, não entendi. Pode reformular?\n\nExemplo: "Gastei 50 reais no mercado hoje"',
                'confidence': 0.3
            }
    
    def generate_financial_tip(self, user_data: Dict) -> str:
        """Gera dica financeira personalizada com GPT"""
        if not self.use_gpt:
            return self._fallback_tip()
        
        try:
            prompt = f"""Com base nos dados financeiros do usuário, dê UMA dica curta e prática:

Dados:
- Despesas do mês: R$ {user_data.get('expenses', 0):.2f}
- Receitas do mês: R$ {user_data.get('income', 0):.2f}
- Categoria com mais gastos: {user_data.get('top_category', 'N/A')}
- Saldo: R$ {user_data.get('balance', 0):.2f}

Dê uma dica motivacional e prática em até 3 linhas. Use emojis."""

            response = client_gpt.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar dica: {e}")
            return self._fallback_tip()
    
    def _fallback_tip(self) -> str:
        """Dica genérica sem GPT"""
        tips = [
            "💡 Dica: Anote TODOS os gastos, até os pequenos! Eles fazem diferença no fim do mês.",
            "📊 Que tal definir uma meta de economia? Mesmo R$ 50/mês já é um começo!",
            "🎯 Separe 10% da sua renda para investimentos. Seu futuro agradece!",
            "💳 Evite compras por impulso. Espere 24h antes de decidir se realmente precisa.",
            "🏦 Mantenha uma reserva de emergência de pelo menos 3 meses de despesas."
        ]
        import random
        return random.choice(tips)
    
    def clear_history(self, user_id: str):
        """Limpa histórico de conversa do usuário"""
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]
            logger.info(f"🗑️ Histórico limpo para {user_id}")


# =========================================
# INSTÂNCIA GLOBAL
# =========================================

gpt_assistant = GPTFinanceAssistant()


# =========================================
# FUNÇÕES AUXILIARES
# =========================================

def process_whatsapp_message(text: str, user_id: str) -> Dict:
    """
    Função principal para processar mensagem do WhatsApp
    
    Args:
        text: Mensagem do usuário
        user_id: Número do WhatsApp
        
    Returns:
        Dict com dados processados
    """
    return gpt_assistant.process_message(text, user_id)


def generate_tip(user_data: Dict) -> str:
    """Gera dica financeira para o usuário"""
    return gpt_assistant.generate_financial_tip(user_data)


def clear_user_history(user_id: str):
    """Limpa histórico de conversa"""
    gpt_assistant.clear_history(user_id)


# =========================================
# TESTE
# =========================================

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    print("🤖 Testando GPT Finance Assistant\n")
    print(f"GPT ativo: {USE_GPT}\n")
    
    test_messages = [
        "Olá!",
        "Gastei 150 reais no supermercado hoje",
        "Quanto gastei esse mês?",
        "Me dá uma dica financeira"
    ]
    
    for msg in test_messages:
        print(f"👤 Usuário: {msg}")
        result = process_whatsapp_message(msg, "test_user")
        print(f"🤖 Resposta: {json.dumps(result, indent=2, ensure_ascii=False)}")
        print("-" * 50)
