"""
Investment AI Advisor - Inteligência Artificial para análise e recomendações
"""

from datetime import datetime, timedelta
import statistics
from services.investment_calculator import InvestmentCalculator

class InvestmentAIAdvisor:
    """IA para análise de investimentos e geração de insights"""
    
    def __init__(self, investments, history_data=None):
        """
        Args:
            investments: lista de investimentos atuais
            history_data: histórico de valores (opcional)
        """
        self.investments = investments
        self.history = history_data or []
        self.calculator = InvestmentCalculator()
    
    def generate_insights(self):
        """
        Gera insights automáticos baseados nos dados
        Returns:
            list de dicts com insights
        """
        insights = []
        
        # Análise de portfólio
        portfolio_metrics = self.calculator.calculate_portfolio_metrics(self.investments)
        
        # Insight 1: Performance geral
        if portfolio_metrics['total_profit_pct'] > 0:
            insights.append({
                'type': 'success',
                'icon': '📈',
                'title': 'Portfolio em alta!',
                'message': f"Seu portfólio está com rentabilidade de {portfolio_metrics['total_profit_pct']:.2f}%, " +
                          f"um lucro de R$ {portfolio_metrics['total_profit']:.2f}."
            })
        elif portfolio_metrics['total_profit_pct'] < -5:
            insights.append({
                'type': 'warning',
                'icon': '⚠️',
                'title': 'Atenção ao desempenho',
                'message': f"Seu portfólio está {abs(portfolio_metrics['total_profit_pct']):.2f}% negativo. " +
                          "Considere revisar suas posições."
            })
        
        # Insight 2: Melhor e pior ativo
        if portfolio_metrics['best_performer']:
            best = portfolio_metrics['best_performer']
            best_profit = ((best['current_value'] - best['amount']) / best['amount'] * 100) if best['amount'] > 0 else 0
            
            insights.append({
                'type': 'info',
                'icon': '🏆',
                'title': 'Melhor desempenho',
                'message': f"{best['name']} está com {best_profit:.2f}% de rentabilidade!"
            })
        
        if portfolio_metrics['worst_performer']:
            worst = portfolio_metrics['worst_performer']
            worst_profit = ((worst['current_value'] - worst['amount']) / worst['amount'] * 100) if worst['amount'] > 0 else 0
            
            if worst_profit < -10:
                insights.append({
                    'type': 'warning',
                    'icon': '📉',
                    'title': 'Ativo em queda',
                    'message': f"{worst['name']} está com {abs(worst_profit):.2f}% de prejuízo. Avalie sua estratégia."
                })
        
        # Insight 3: Diversificação
        diversification_score = self.calculator.calculate_diversification_score(self.investments)
        allocation = self.calculator.calculate_allocation(self.investments)
        
        if diversification_score < 25:
            # Encontrar tipo dominante
            dominant_type = max(allocation.items(), key=lambda x: x[1])
            insights.append({
                'type': 'warning',
                'icon': '⚠️',
                'title': 'Baixa diversificação',
                'message': f"{dominant_type[1]:.1f}% do seu portfólio está em {dominant_type[0]}. " +
                          "Considere diversificar para reduzir riscos."
            })
        elif diversification_score > 75:
            insights.append({
                'type': 'success',
                'icon': '✨',
                'title': 'Excelente diversificação',
                'message': f"Seu portfólio está bem distribuído (score: {diversification_score:.0f}/100)."
            })
        
        # Insight 4: Risco do portfólio
        risk_level = self.calculator.calculate_risk_level(self.investments)
        if risk_level == 'Alto':
            insights.append({
                'type': 'warning',
                'icon': '🎲',
                'title': 'Portfólio de alto risco',
                'message': "Você possui muitos ativos de alta volatilidade. Considere balancear com ativos de renda fixa."
            })
        elif risk_level == 'Baixo':
            insights.append({
                'type': 'info',
                'icon': '🛡️',
                'title': 'Portfólio conservador',
                'message': "Seu portfólio é de baixo risco. Se busca maior rentabilidade, considere diversificar para renda variável."
            })
        
        # Insight 5: Análise de tendência (se houver histórico)
        if self.history:
            trend_insight = self._analyze_trend()
            if trend_insight:
                insights.append(trend_insight)
        
        # Insight 6: Tempo de investimento
        old_investments = [inv for inv in self.investments 
                          if self.calculator.calculate_days_held(inv.get('start_date', datetime.now())) > 365]
        
        if old_investments:
            insights.append({
                'type': 'info',
                'icon': '⏳',
                'title': 'Investimentos de longo prazo',
                'message': f"Você possui {len(old_investments)} investimento(s) com mais de 1 ano. " +
                          "Parabéns pela disciplina!"
            })
        
        return insights
    
    def _analyze_trend(self):
        """Analisa tendência baseada no histórico"""
        if len(self.history) < 7:
            return None
        
        # Pegar últimos 30 dias
        recent_history = sorted(self.history, key=lambda x: x['date'])[-30:]
        
        if len(recent_history) < 7:
            return None
        
        # Calcular variação média
        values = [h['total_value'] for h in recent_history]
        
        # Regressão linear simples
        n = len(values)
        x = list(range(n))
        
        # Calcular slope (inclinação)
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(values)
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return None
        
        slope = numerator / denominator
        
        # Calcular variação percentual
        first_value = values[0]
        last_value = values[-1]
        variation_pct = ((last_value - first_value) / first_value * 100) if first_value > 0 else 0
        
        if slope > 0 and variation_pct > 5:
            return {
                'type': 'success',
                'icon': '📊',
                'title': 'Tendência positiva',
                'message': f"Seu portfólio cresceu {variation_pct:.2f}% nos últimos {len(recent_history)} dias. Continue assim!"
            }
        elif slope < 0 and variation_pct < -5:
            return {
                'type': 'warning',
                'icon': '📉',
                'title': 'Tendência negativa',
                'message': f"Seu portfólio caiu {abs(variation_pct):.2f}% nos últimos {len(recent_history)} dias. " +
                          "Monitore seus ativos."
            }
        
        return None
    
    def get_rebalance_recommendations(self):
        """
        Sugere rebalanceamento do portfólio
        Returns:
            list de recomendações
        """
        recommendations = []
        allocation = self.calculator.calculate_allocation(self.investments)
        
        # Recomendações baseadas em alocação
        for inv_type, percentage in allocation.items():
            if inv_type == 'Criptomoedas' and percentage > 30:
                recommendations.append({
                    'action': 'reduce',
                    'asset_type': 'Criptomoedas',
                    'current': percentage,
                    'target': 20,
                    'reason': 'Alta volatilidade e concentração de risco'
                })
            
            if inv_type in ['CDB', 'LCI', 'LCA', 'Tesouro Direto', 'Poupança'] and percentage < 20:
                recommendations.append({
                    'action': 'increase',
                    'asset_type': 'Renda Fixa',
                    'current': percentage,
                    'target': 30,
                    'reason': 'Aumentar segurança e previsibilidade'
                })
            
            if inv_type == 'Ações' and percentage > 50:
                recommendations.append({
                    'action': 'reduce',
                    'asset_type': 'Ações',
                    'current': percentage,
                    'target': 40,
                    'reason': 'Diversificar para reduzir volatilidade'
                })
        
        return recommendations
    
    def predict_next_month(self):
        """
        Previsão simples para o próximo mês baseada em tendências
        Returns:
            dict com previsão otimista, realista e pessimista
        """
        if len(self.history) < 14:
            return None
        
        recent_values = sorted(self.history, key=lambda x: x['date'])[-30:]
        values = [h['total_value'] for h in recent_values]
        
        # Calcular média de crescimento diário
        daily_changes = []
        for i in range(1, len(values)):
            change = (values[i] - values[i-1]) / values[i-1] * 100 if values[i-1] > 0 else 0
            daily_changes.append(change)
        
        if not daily_changes:
            return None
        
        avg_daily_change = statistics.mean(daily_changes)
        std_dev = statistics.stdev(daily_changes) if len(daily_changes) > 1 else 0
        
        current_value = values[-1]
        
        # Projeção para 30 dias
        realistic = current_value * (1 + avg_daily_change/100) ** 30
        optimistic = current_value * (1 + (avg_daily_change + std_dev)/100) ** 30
        pessimistic = current_value * (1 + (avg_daily_change - std_dev)/100) ** 30
        
        return {
            'current': current_value,
            'realistic': realistic,
            'optimistic': optimistic,
            'pessimistic': pessimistic,
            'variation_realistic': ((realistic - current_value) / current_value * 100),
            'variation_optimistic': ((optimistic - current_value) / current_value * 100),
            'variation_pessimistic': ((pessimistic - current_value) / current_value * 100)
        }
    
    def get_concentration_risk(self):
        """Identifica concentração excessiva em um único ativo"""
        if not self.investments:
            return None
        
        total_value = sum(inv['current_value'] for inv in self.investments)
        
        for inv in self.investments:
            percentage = (inv['current_value'] / total_value * 100) if total_value > 0 else 0
            
            if percentage > 40:
                return {
                    'type': 'warning',
                    'icon': '⚠️',
                    'title': 'Concentração de risco',
                    'message': f"{inv['name']} representa {percentage:.1f}% do seu portfólio. " +
                              "Considere reduzir a posição para mitigar riscos."
                }
        
        return None
    
    def get_top_recommendations(self, limit=5):
        """
        Retorna as principais recomendações da IA
        Args:
            limit: número máximo de recomendações
        Returns:
            list de recomendações priorizadas
        """
        all_recommendations = []
        
        # Adicionar insights
        insights = self.generate_insights()
        all_recommendations.extend(insights)
        
        # Adicionar recomendação de concentração
        concentration = self.get_concentration_risk()
        if concentration:
            all_recommendations.append(concentration)
        
        # Priorizar por tipo (warning > info > success)
        priority = {'warning': 1, 'info': 2, 'success': 3}
        all_recommendations.sort(key=lambda x: priority.get(x.get('type', 'info'), 2))
        
        return all_recommendations[:limit]
