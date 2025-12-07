"""
Investment Calculator - Cálculos de rentabilidade e métricas
"""

from datetime import datetime, timedelta
import math

class InvestmentCalculator:
    """Calculadora de métricas de investimentos"""
    
    @staticmethod
    def calculate_profitability(initial_value, current_value):
        """
        Calcula rentabilidade percentual
        Args:
            initial_value: valor investido
            current_value: valor atual
        Returns:
            float: rentabilidade em %
        """
        if initial_value == 0:
            return 0.0
        
        return ((current_value - initial_value) / initial_value) * 100
    
    @staticmethod
    def calculate_profit_amount(initial_value, current_value):
        """
        Calcula lucro/prejuízo em R$
        Args:
            initial_value: valor investido
            current_value: valor atual
        Returns:
            float: lucro em R$
        """
        return current_value - initial_value
    
    @staticmethod
    def calculate_average_price(total_invested, quantity):
        """
        Calcula preço médio de compra
        Args:
            total_invested: valor total investido
            quantity: quantidade de ativos
        Returns:
            float: preço médio
        """
        if quantity == 0:
            return 0.0
        
        return total_invested / quantity
    
    @staticmethod
    def calculate_days_held(purchase_date):
        """
        Calcula dias desde a compra
        Args:
            purchase_date: data da compra (string ou datetime)
        Returns:
            int: número de dias
        """
        if isinstance(purchase_date, str):
            purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d')
        
        today = datetime.now()
        delta = today - purchase_date
        return delta.days
    
    @staticmethod
    def calculate_annualized_return(initial_value, current_value, days_held):
        """
        Calcula retorno anualizado
        Args:
            initial_value: valor inicial
            current_value: valor atual
            days_held: dias de investimento
        Returns:
            float: retorno anualizado em %
        """
        if initial_value == 0 or days_held == 0:
            return 0.0
        
        # Fórmula: ((valor_final / valor_inicial) ^ (365 / dias)) - 1) * 100
        ratio = current_value / initial_value
        exponent = 365 / days_held
        annualized = (math.pow(ratio, exponent) - 1) * 100
        
        return annualized
    
    @staticmethod
    def calculate_portfolio_metrics(investments):
        """
        Calcula métricas do portfólio completo
        Args:
            investments: lista de dicts com investments
        Returns:
            dict com métricas agregadas
        """
        total_invested = 0
        total_current = 0
        best_performer = None
        worst_performer = None
        best_profit_pct = -float('inf')
        worst_profit_pct = float('inf')
        
        for inv in investments:
            invested = inv.get('amount', 0)
            current = inv.get('current_value', 0)
            
            total_invested += invested
            total_current += current
            
            if invested > 0:
                profit_pct = ((current - invested) / invested) * 100
                
                if profit_pct > best_profit_pct:
                    best_profit_pct = profit_pct
                    best_performer = inv
                
                if profit_pct < worst_profit_pct:
                    worst_profit_pct = profit_pct
                    worst_performer = inv
        
        total_profit = total_current - total_invested
        total_profit_pct = ((total_current - total_invested) / total_invested * 100) if total_invested > 0 else 0
        
        return {
            'total_invested': total_invested,
            'total_current': total_current,
            'total_profit': total_profit,
            'total_profit_pct': total_profit_pct,
            'best_performer': best_performer,
            'worst_performer': worst_performer,
            'count': len(investments)
        }
    
    @staticmethod
    def calculate_allocation(investments):
        """
        Calcula distribuição por tipo de ativo
        Args:
            investments: lista de investimentos
        Returns:
            dict com percentual por tipo
        """
        allocation = {}
        total = 0
        
        for inv in investments:
            inv_type = inv.get('investment_type', 'Outro')
            value = inv.get('current_value', 0)
            
            if inv_type not in allocation:
                allocation[inv_type] = 0
            
            allocation[inv_type] += value
            total += value
        
        # Converter para percentual
        if total > 0:
            for key in allocation:
                allocation[key] = (allocation[key] / total) * 100
        
        return allocation
    
    @staticmethod
    def calculate_risk_level(investments):
        """
        Calcula nível de risco do portfólio
        Returns:
            string: 'Baixo', 'Médio', 'Alto'
        """
        allocation = InvestmentCalculator.calculate_allocation(investments)
        
        # Pesos de risco por tipo
        risk_weights = {
            'Criptomoedas': 3,
            'Ações': 2,
            'FII': 2,
            'ETF': 2,
            'Tesouro Direto': 1,
            'CDB': 1,
            'LCI': 1,
            'LCA': 1,
            'Poupança': 0.5,
            'Fundos': 1.5,
            'Outro': 1
        }
        
        weighted_risk = 0
        for inv_type, percentage in allocation.items():
            weight = risk_weights.get(inv_type, 1)
            weighted_risk += (percentage / 100) * weight
        
        if weighted_risk < 1.2:
            return 'Baixo'
        elif weighted_risk < 2.0:
            return 'Médio'
        else:
            return 'Alto'
    
    @staticmethod
    def calculate_diversification_score(investments):
        """
        Calcula score de diversificação (0-100)
        Quanto mais distribuído entre tipos, maior o score
        """
        allocation = InvestmentCalculator.calculate_allocation(investments)
        
        if not allocation:
            return 0
        
        # Calcular entropy (diversidade)
        entropy = 0
        for percentage in allocation.values():
            if percentage > 0:
                p = percentage / 100
                entropy -= p * math.log2(p)
        
        # Normalizar para 0-100
        max_entropy = math.log2(len(allocation)) if len(allocation) > 1 else 1
        score = (entropy / max_entropy) * 100 if max_entropy > 0 else 0
        
        return round(score, 2)
    
    @staticmethod
    def get_diversification_recommendation(score):
        """Retorna recomendação baseada no score de diversificação"""
        if score >= 75:
            return "Excelente diversificação! Seu portfólio está bem distribuído."
        elif score >= 50:
            return "Boa diversificação, mas considere expandir para mais tipos de ativos."
        elif score >= 25:
            return "Diversificação moderada. Recomendamos adicionar outros tipos de investimentos."
        else:
            return "⚠️ Baixa diversificação! Seu portfólio está muito concentrado em poucos ativos."
