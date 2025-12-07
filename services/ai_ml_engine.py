"""
BWS Insight AI - Machine Learning Engine
Algoritmos avançados de ML para análise preditiva e detecção de padrões
"""

import numpy as np
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

class MLFinancialEngine:
    """Motor de Machine Learning para análise financeira"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.regression_model = Ridge(alpha=1.0)
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.clustering_model = KMeans(n_clusters=3, random_state=42)
        
    def advanced_balance_prediction(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """
        Previsão avançada de saldo usando Regressão Linear
        Retorna previsões para 7, 15, 30, 60 e 90 dias
        """
        if not historical_data or len(historical_data) < 3:
            return {
                'predictions': [],
                'confidence': 'low',
                'trend': 'insufficient_data',
                'accuracy_score': 0
            }
        
        try:
            # Preparar dados para ML
            X = np.array([[i] for i in range(len(historical_data))])
            y = np.array([item.get('balance', 0) for item in historical_data])
            
            # Treinar modelo
            self.regression_model.fit(X, y)
            
            # Fazer previsões
            future_days = [7, 15, 30, 60, 90]
            predictions = []
            
            for days in future_days:
                future_idx = len(historical_data) + days
                predicted_value = self.regression_model.predict([[future_idx]])[0]
                
                # Calcular intervalo de confiança
                residuals = y - self.regression_model.predict(X)
                std_error = np.std(residuals)
                confidence_interval = 1.96 * std_error  # 95% de confiança
                
                predictions.append({
                    'days': days,
                    'predicted_balance': round(predicted_value, 2),
                    'confidence_min': round(predicted_value - confidence_interval, 2),
                    'confidence_max': round(predicted_value + confidence_interval, 2),
                    'date': (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
                })
            
            # Calcular tendência
            slope = self.regression_model.coef_[0]
            if slope > 10:
                trend = 'growing'
                trend_emoji = '📈'
            elif slope < -10:
                trend = 'declining'
                trend_emoji = '📉'
            else:
                trend = 'stable'
                trend_emoji = '➡️'
            
            # Score R² (qualidade do modelo)
            score = self.regression_model.score(X, y)
            
            return {
                'predictions': predictions,
                'confidence': 'high' if score > 0.8 else 'medium' if score > 0.5 else 'low',
                'trend': trend,
                'trend_emoji': trend_emoji,
                'accuracy_score': round(score * 100, 1),
                'slope_per_day': round(slope, 2)
            }
            
        except Exception as e:
            print(f"Erro na previsão ML: {e}")
            return {
                'predictions': [],
                'confidence': 'error',
                'trend': 'unknown',
                'accuracy_score': 0
            }
    
    def detect_spending_anomalies_ml(self, transactions: List[Dict]) -> List[Dict]:
        """
        Detecção de anomalias usando Isolation Forest
        Identifica transações suspeitas ou padrões incomuns
        """
        if not transactions or len(transactions) < 5:
            return []
        
        try:
            # Preparar features
            features = []
            transaction_list = []
            
            for t in transactions:
                amount = abs(t.get('amount', 0))
                # Extrair dia da semana e hora (se disponível)
                date_str = t.get('date', '')
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    day_of_week = date_obj.weekday()
                except:
                    day_of_week = 0
                
                features.append([amount, day_of_week])
                transaction_list.append(t)
            
            X = np.array(features)
            
            # Treinar detector de anomalias
            self.anomaly_detector.fit(X)
            
            # Detectar anomalias (-1 = anomalia, 1 = normal)
            predictions = self.anomaly_detector.predict(X)
            
            # Retornar transações anômalas
            anomalies = []
            for idx, pred in enumerate(predictions):
                if pred == -1:
                    transaction = transaction_list[idx]
                    anomalies.append({
                        'transaction': transaction,
                        'reason': 'Valor fora do padrão habitual',
                        'amount': transaction.get('amount', 0),
                        'date': transaction.get('date', ''),
                        'category': transaction.get('category', 'Unknown'),
                        'severity': 'high' if abs(transaction.get('amount', 0)) > 1000 else 'medium'
                    })
            
            return anomalies
            
        except Exception as e:
            print(f"Erro na detecção de anomalias: {e}")
            return []
    
    def cluster_spending_patterns(self, transactions: List[Dict]) -> Dict[str, Any]:
        """
        Agrupa transações em padrões de gastos usando K-Means
        Identifica 3 grupos: Gastos Pequenos, Médios e Grandes
        """
        if not transactions or len(transactions) < 3:
            return {
                'clusters': [],
                'analysis': 'Dados insuficientes'
            }
        
        try:
            # Preparar dados
            amounts = np.array([[abs(t.get('amount', 0))] for t in transactions])
            
            # Treinar clustering
            self.clustering_model.fit(amounts)
            
            # Obter labels
            labels = self.clustering_model.predict(amounts)
            cluster_centers = self.clustering_model.cluster_centers_
            
            # Analisar clusters
            clusters_info = []
            for i in range(3):
                cluster_transactions = [t for idx, t in enumerate(transactions) if labels[idx] == i]
                cluster_amount = cluster_centers[i][0]
                
                if cluster_amount < 50:
                    cluster_name = "💵 Gastos Pequenos"
                    description = "Compras do dia a dia, lanches, transporte"
                elif cluster_amount < 200:
                    cluster_name = "💳 Gastos Médios"
                    description = "Compras no supermercado, refeições, combustível"
                else:
                    cluster_name = "💰 Gastos Grandes"
                    description = "Contas fixas, eletrônicos, serviços caros"
                
                clusters_info.append({
                    'name': cluster_name,
                    'description': description,
                    'avg_amount': round(cluster_amount, 2),
                    'count': len(cluster_transactions),
                    'percentage': round(len(cluster_transactions) / len(transactions) * 100, 1),
                    'total': round(sum(abs(t.get('amount', 0)) for t in cluster_transactions), 2)
                })
            
            # Ordenar por valor médio
            clusters_info.sort(key=lambda x: x['avg_amount'])
            
            return {
                'clusters': clusters_info,
                'analysis': f"Seus gastos estão distribuídos em {len(clusters_info)} padrões distintos",
                'recommendation': self._get_cluster_recommendation(clusters_info)
            }
            
        except Exception as e:
            print(f"Erro no clustering: {e}")
            return {
                'clusters': [],
                'analysis': f'Erro: {str(e)}'
            }
    
    def _get_cluster_recommendation(self, clusters: List[Dict]) -> str:
        """Gera recomendação baseada nos clusters"""
        if not clusters:
            return ""
        
        # Verificar concentração de gastos grandes
        large_spending = next((c for c in clusters if "Grandes" in c['name']), None)
        if large_spending and large_spending['percentage'] > 40:
            return "⚠️ Atenção: 40% das suas transações são de alto valor. Considere revisar gastos fixos."
        
        small_spending = next((c for c in clusters if "Pequenos" in c['name']), None)
        if small_spending and small_spending['percentage'] > 60:
            return "✅ Bom! Maior parte dos gastos são pequenas compras. Mantenha o controle!"
        
        return "💡 Seus gastos estão bem distribuídos entre diferentes faixas de valor."
    
    def predict_next_month_expenses(self, historical_expenses: List[float]) -> Dict[str, Any]:
        """
        Prevê gastos do próximo mês usando histórico
        """
        if len(historical_expenses) < 3:
            return {
                'predicted_expenses': 0,
                'confidence': 'low',
                'message': 'Histórico insuficiente'
            }
        
        try:
            # Usar os últimos 6 meses (se disponível)
            recent_data = historical_expenses[-6:]
            
            X = np.array([[i] for i in range(len(recent_data))])
            y = np.array(recent_data)
            
            model = LinearRegression()
            model.fit(X, y)
            
            # Prever próximo mês
            next_idx = len(recent_data)
            predicted = model.predict([[next_idx]])[0]
            
            # Calcular tendência
            avg_last_3 = np.mean(recent_data[-3:])
            variation = ((predicted - avg_last_3) / avg_last_3) * 100 if avg_last_3 > 0 else 0
            
            return {
                'predicted_expenses': round(predicted, 2),
                'confidence': 'high' if len(recent_data) >= 6 else 'medium',
                'variation_percent': round(variation, 1),
                'trend': 'increasing' if variation > 5 else 'decreasing' if variation < -5 else 'stable',
                'avg_last_3_months': round(avg_last_3, 2)
            }
            
        except Exception as e:
            print(f"Erro na previsão de gastos: {e}")
            return {
                'predicted_expenses': 0,
                'confidence': 'error',
                'message': str(e)
            }
    
    def analyze_investment_risk(self, portfolio: List[Dict]) -> Dict[str, Any]:
        """
        Analisa risco do portfólio de investimentos
        Calcula volatilidade e diversificação
        """
        if not portfolio:
            return {
                'risk_level': 'unknown',
                'diversification_score': 0,
                'recommendation': 'Sem investimentos para analisar'
            }
        
        try:
            # Calcular diversificação (número de ativos diferentes)
            num_assets = len(portfolio)
            total_value = sum(p.get('current_value', 0) for p in portfolio)
            
            # Calcular concentração (maior ativo / total)
            if total_value > 0:
                max_asset_value = max(p.get('current_value', 0) for p in portfolio)
                concentration = (max_asset_value / total_value) * 100
            else:
                concentration = 0
            
            # Calcular volatilidade baseada em variações
            returns = []
            for asset in portfolio:
                invested = asset.get('total_invested', 0)
                current = asset.get('current_value', 0)
                if invested > 0:
                    ret = ((current - invested) / invested) * 100
                    returns.append(ret)
            
            if returns:
                volatility = np.std(returns)
            else:
                volatility = 0
            
            # Classificar risco
            if volatility > 20 or concentration > 50:
                risk_level = 'high'
                risk_emoji = '🔴'
            elif volatility > 10 or concentration > 30:
                risk_level = 'medium'
                risk_emoji = '🟡'
            else:
                risk_level = 'low'
                risk_emoji = '🟢'
            
            # Score de diversificação (0-100)
            diversification_score = min(100, (num_assets * 10) + (100 - concentration))
            
            # Recomendação
            if concentration > 50:
                recommendation = "⚠️ Carteira muito concentrada. Considere diversificar em mais ativos."
            elif num_assets < 3:
                recommendation = "💡 Aumente a diversificação adicionando mais ativos ao portfólio."
            elif volatility > 15:
                recommendation = "📊 Alta volatilidade detectada. Considere adicionar ativos mais estáveis."
            else:
                recommendation = "✅ Portfólio bem diversificado e com risco controlado!"
            
            return {
                'risk_level': risk_level,
                'risk_emoji': risk_emoji,
                'diversification_score': round(diversification_score, 1),
                'concentration_percent': round(concentration, 1),
                'volatility': round(volatility, 2),
                'num_assets': num_assets,
                'recommendation': recommendation
            }
            
        except Exception as e:
            print(f"Erro na análise de risco: {e}")
            return {
                'risk_level': 'error',
                'diversification_score': 0,
                'recommendation': f'Erro: {str(e)}'
            }
    
    def smart_budget_recommendation(self, income: float, current_expenses: Dict[str, float]) -> Dict[str, Any]:
        """
        Recomenda orçamento inteligente baseado na regra 50/30/20
        50% Necessidades, 30% Desejos, 20% Poupança/Investimentos
        """
        if income <= 0:
            return {
                'recommendation': 'Renda não informada',
                'budget': {}
            }
        
        # Orçamento ideal (50/30/20)
        ideal_budget = {
            'necessidades': income * 0.50,
            'desejos': income * 0.30,
            'poupanca': income * 0.20
        }
        
        # Calcular gastos atuais
        total_expenses = sum(current_expenses.values())
        
        # Classificar categorias
        needs_categories = ['Alimentação', 'Transporte', 'Saúde', 'Moradia', 'Educação']
        wants_categories = ['Lazer', 'Entretenimento', 'Viagens', 'Compras']
        
        current_needs = sum(v for k, v in current_expenses.items() if any(cat in k for cat in needs_categories))
        current_wants = sum(v for k, v in current_expenses.items() if any(cat in k for cat in wants_categories))
        current_savings = income - total_expenses
        
        # Comparar com ideal
        analysis = []
        
        # Necessidades
        if current_needs > ideal_budget['necessidades']:
            diff = current_needs - ideal_budget['necessidades']
            analysis.append(f"⚠️ Necessidades: R$ {diff:.2f} acima do ideal (50%)")
        else:
            analysis.append(f"✅ Necessidades: Dentro do orçamento ideal")
        
        # Desejos
        if current_wants > ideal_budget['desejos']:
            diff = current_wants - ideal_budget['desejos']
            analysis.append(f"⚠️ Desejos: R$ {diff:.2f} acima do ideal (30%)")
        else:
            analysis.append(f"✅ Desejos: Dentro do orçamento ideal")
        
        # Poupança
        savings_percent = (current_savings / income * 100) if income > 0 else 0
        if savings_percent < 20:
            analysis.append(f"🎯 Meta de poupança: Aumentar de {savings_percent:.1f}% para 20%")
        else:
            analysis.append(f"🎉 Poupança: Excelente! {savings_percent:.1f}% da renda")
        
        return {
            'ideal_budget': {
                'necessidades': round(ideal_budget['necessidades'], 2),
                'desejos': round(ideal_budget['desejos'], 2),
                'poupanca': round(ideal_budget['poupanca'], 2)
            },
            'current_distribution': {
                'necessidades': round(current_needs, 2),
                'desejos': round(current_wants, 2),
                'poupanca': round(current_savings, 2)
            },
            'analysis': analysis,
            'savings_rate': round(savings_percent, 1)
        }
