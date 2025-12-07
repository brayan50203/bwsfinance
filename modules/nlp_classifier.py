"""
NLP Classifier - Extrai informações financeiras de texto usando IA e regras
"""
import re
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class NLPClassifier:
    def __init__(self):
        # Categorias e keywords (expandidas)
        self.categories = {
            'Alimentação': ['mercado', 'supermercado', 'padaria', 'restaurante', 'ifood', 'delivery', 
                           'lanche', 'pizza', 'comida', 'alimento', 'alimentação', 'alimentacao',
                           'feira', 'açougue', 'hortifruti', 'burguer', 'mcdonald', 'bk', 'subway', 
                           'starbucks', 'café', 'bar', 'churrasco', 'refeição', 'refeicao'],
            'Transporte': ['uber', '99', 'gasolina', 'combustível', 'posto', 'estacionamento', 'pedágio',
                          'taxi', 'ônibus', 'onibus', 'metro', 'metrô', 'trem', 'brt', 'moto', 'carro'],
            'Moradia': ['aluguel', 'condomínio', 'condominio', 'luz', 'água', 'agua', 'internet', 'iptu',
                       'energia', 'enel', 'copel', 'cemig', 'wifi', 'net', 'vivo', 'oi', 'tim'],
            'Saúde': ['farmácia', 'farmacia', 'médico', 'medico', 'consulta', 'remédio', 'remedio', 
                     'hospital', 'dentista', 'exame', 'plano de saúde', 'plano de saude', 'unimed'],
            'Lazer': ['cinema', 'netflix', 'spotify', 'show', 'festa', 'viagem', 'disney', 'youtube',
                     'prime', 'hbo', 'game', 'jogo', 'parque', 'diversão', 'divertimento'],
            'Educação': ['curso', 'livro', 'faculdade', 'escola', 'mensalidade', 'universidade',
                        'colégio', 'colegio', 'udemy', 'alura', 'material escolar'],
            'Compras': ['loja', 'roupa', 'amazon', 'shopee', 'mercado livre', 'magazine', 'casas bahia',
                       'americanas', 'shein', 'aliexpress', 'compra', 'shopping'],
            'Serviços': ['conta', 'fatura', 'assinatura', 'mensalidade', 'taxa', 'tarifa', 'serviço',
                        'servico', 'manutenção', 'manutencao', 'reparo', 'conserto']
        }
        
        # Contas bancárias
        self.accounts = {
            'nubank': 'Nubank',
            'itau': 'Itaú',
            'itaú': 'Itaú',
            'bradesco': 'Bradesco',
            'inter': 'Inter',
            'picpay': 'PicPay',
            'mercado pago': 'Mercado Pago',
            'santander': 'Santander'
        }
    
    def extract_amount(self, text: str) -> Optional[float]:
        """Extrai valor monetário do texto"""
        patterns = [
            # R$ 50,00 ou R$ 50.00
            r'R\$\s?([\d.]+[,]\d{2})',
            # 50,00 reais
            r'([\d.]+[,]\d{2})\s?reais?',
            # R$ 50 (sem centavos)
            r'R\$\s?([\d.]+)(?![,\d])',
            # 50 reais (sem centavos)
            r'([\d.]+)\s?reais?',
            # Apenas números soltos como "gastei 300"
            r'(?:paguei|gastei|comprei|recebi|ganhei)\s+.*?([\d.]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value_str = match.group(1)
                # Remove pontos de milhar e troca vírgula por ponto
                value_str = value_str.replace('.', '').replace(',', '.')
                try:
                    return float(value_str)
                except:
                    continue
        
        return None
    
    def extract_date(self, text: str) -> Optional[str]:
        """Extrai e normaliza data do texto"""
        text_lower = text.lower()
        today = datetime.now()
        
        # Hoje, ontem, anteontem
        if 'hoje' in text_lower:
            return today.strftime('%Y-%m-%d')
        elif 'ontem' in text_lower:
            return (today - timedelta(days=1)).strftime('%Y-%m-%d')
        elif 'anteontem' in text_lower:
            return (today - timedelta(days=2)).strftime('%Y-%m-%d')
        
        # Dia X
        day_match = re.search(r'dia\s+(\d{1,2})', text_lower)
        if day_match:
            day = int(day_match.group(1))
            return f"{today.year}-{today.month:02d}-{day:02d}"
        
        # Formato DD/MM ou DD/MM/YYYY
        date_match = re.search(r'(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?', text)
        if date_match:
            day, month = int(date_match.group(1)), int(date_match.group(2))
            year = int(date_match.group(3)) if date_match.group(3) else today.year
            if year < 100:
                year += 2000
            return f"{year}-{month:02d}-{day:02d}"
        
        # Padrão: hoje
        return today.strftime('%Y-%m-%d')
    
    def extract_category(self, text: str) -> str:
        """Classifica categoria baseado em keywords"""
        text_lower = text.lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return category
        
        return 'Outros'
    
    def extract_account(self, text: str) -> Optional[str]:
        """Identifica conta bancária"""
        text_lower = text.lower()
        
        for keyword, account_name in self.accounts.items():
            if keyword in text_lower:
                return account_name
        
        return None
    
    def classify(self, text: str) -> Dict:
        """Pipeline completo de classificação"""
        print(f"\n{'='*60}")
        print(f"🧠 NLP CLASSIFIER - Classificando texto:")
        print(f"{'='*60}")
        print(f"📝 Texto: {text}")
        print(f"{'='*60}")
        
        logger.info(f"🧠 Classificando: {text[:100]}...")
        
        amount = self.extract_amount(text)
        date = self.extract_date(text)
        category = self.extract_category(text)
        account = self.extract_account(text)
        
        print(f"💰 Valor extraído: {amount}")
        print(f"📅 Data extraída: {date}")
        print(f"📂 Categoria extraída: {category}")
        print(f"🏦 Conta extraída: {account}")
        print(f"{'='*60}\n")
        
        result = {
            'amount': amount,
            'date': date,
            'category': category,
            'account': account,
            'description': text[:200],
            'type': 'Despesa',  # Padrão
            'confidence': 0.5
        }
        
        # Calcular confiança
        if result['amount']:
            result['confidence'] += 0.3
        if result['category'] != 'Outros':
            result['confidence'] += 0.2
        
        logger.info(f"✅ Classificação: {result}")
        return result
