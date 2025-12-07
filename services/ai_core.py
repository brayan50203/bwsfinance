"""
BWS Insight AI - Motor Principal da Inteligência Artificial
Sistema autônomo de análise financeira integrado ao BWSFinance
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests
from collections import defaultdict

class BWSInsightAI:
    """Motor principal da IA de análise financeira"""
    
    def __init__(self, base_url: str = "http://localhost:5000", user_id: str = None, tenant_id: str = None):
        self.base_url = base_url
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.db_path = "ai_history.db"
        self._init_database()
        
    def _init_database(self):
        """Inicializa banco de dados para histórico da IA"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                tenant_id TEXT,
                user_message TEXT,
                ai_response TEXT,
                context TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                tenant_id TEXT,
                insight_type TEXT,
                insight_text TEXT,
                data JSON,
                severity TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def fetch_financial_data(self, session=None) -> Dict[str, Any]:
        """Coleta todos os dados financeiros das APIs"""
        data = {}
        
        try:
            # Dashboard summary
            response = requests.get(f"{self.base_url}/api/dashboard", cookies=session)
            if response.status_code == 200:
                data['dashboard'] = response.json()
            
            # Accounts
            response = requests.get(f"{self.base_url}/api/accounts", cookies=session)
            if response.status_code == 200:
                data['accounts'] = response.json()
            
            # Investments
            response = requests.get(f"{self.base_url}/api/investments", cookies=session)
            if response.status_code == 200:
                data['investments'] = response.json()
            
        except Exception as e:
            print(f"Erro ao buscar dados: {e}")
        
        return data
    
    def fetch_financial_data_direct(self, user_id: str, tenant_id: str) -> Dict[str, Any]:
        """Coleta dados financeiros diretamente do banco de dados (para WhatsApp)"""
        data = {}
        
        try:
            import sqlite3
            from datetime import datetime
            
            conn = sqlite3.connect('bws_finance.db')
            conn.row_factory = sqlite3.Row
            
            # Resumo Dashboard
            year = datetime.now().year
            month = datetime.now().month
            
            summary = conn.execute("""
                SELECT 
                    COALESCE(SUM(CASE WHEN type = 'Receita' THEN value ELSE 0 END), 0) as renda_total,
                    COALESCE(SUM(CASE WHEN type = 'Despesa' THEN value ELSE 0 END), 0) as custos_total
                FROM transactions
                WHERE user_id = ? AND tenant_id = ? AND status = 'Pago'
                AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
            """, (user_id, tenant_id, str(year), f"{month:02d}")).fetchone()
            
            data['dashboard'] = dict(summary) if summary else {}
            data['dashboard']['saldo'] = data['dashboard'].get('renda_total', 0) - data['dashboard'].get('custos_total', 0)
            
            # Contas
            accounts = conn.execute("""
                SELECT * FROM v_account_balances
                WHERE user_id = ? AND tenant_id = ?
            """, (user_id, tenant_id)).fetchall()
            
            data['accounts'] = [dict(acc) for acc in accounts]
            
            # Investimentos
            investments = conn.execute("""
                SELECT 
                    id, asset_name, asset_type, quantity, 
                    purchase_price, current_price, current_value,
                    total_invested, profit_loss, profit_loss_percentage,
                    purchase_date, last_updated
                FROM investments
                WHERE user_id = ? AND tenant_id = ?
                AND (status = 'active' OR status IS NULL)
            """, (user_id, tenant_id)).fetchall()
            
            data['investments'] = [dict(inv) for inv in investments]
            
            # Calcular totais de investimentos
            total_invested = sum(inv.get('total_invested', 0) or 0 for inv in data['investments'])
            total_current = sum(inv.get('current_value', 0) or 0 for inv in data['investments'])
            total_profit = total_current - total_invested
            
            data['dashboard']['total_investido'] = total_invested
            data['dashboard']['valor_atual_investimentos'] = total_current
            data['dashboard']['lucro_investimentos'] = total_profit
            
            # Transações recentes
            recent = conn.execute("""
                SELECT t.*, c.name as category_name
                FROM transactions t
                LEFT JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = ? AND t.tenant_id = ?
                ORDER BY t.date DESC
                LIMIT 10
            """, (user_id, tenant_id)).fetchall()
            
            data['recent_transactions'] = [dict(trans) for trans in recent]
            
            conn.close()
            
        except Exception as e:
            print(f"Erro ao buscar dados direto: {e}")
        
        return data
    
    def generate_daily_insight(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera insight automático diário"""
        insights = []
        
        dashboard = financial_data.get('dashboard', {})
        
        # Análise de saldo
        saldo = dashboard.get('saldo', 0)
        renda = dashboard.get('renda_total', 0)
        custos = dashboard.get('custos_total', 0)
        
        if saldo < 0:
            insights.append({
                'type': 'alert',
                'severity': 'high',
                'icon': '⚠️',
                'title': 'Saldo Negativo',
                'message': f'Seu saldo está negativo em R$ {abs(saldo):.2f}. Considere reduzir gastos ou buscar receitas extras.'
            })
        elif saldo > 0 and renda > 0:
            taxa_poupanca = (saldo / renda) * 100
            if taxa_poupanca >= 20:
                insights.append({
                    'type': 'success',
                    'severity': 'low',
                    'icon': '💰',
                    'title': 'Parabéns! Você está poupando bem',
                    'message': f'Sua taxa de poupança é de {taxa_poupanca:.1f}%, acima da meta de 20%!'
                })
            else:
                insights.append({
                    'type': 'warning',
                    'severity': 'medium',
                    'icon': '💡',
                    'title': 'Oportunidade de Economia',
                    'message': f'Sua taxa de poupança é de {taxa_poupanca:.1f}%. Tente alcançar 20% para uma saúde financeira melhor.'
                })
        
        # Análise de investimentos
        investimentos = dashboard.get('investimentos', {})
        total_investido = sum(investimentos.values())
        
        if total_investido > 0:
            insights.append({
                'type': 'info',
                'severity': 'low',
                'icon': '📈',
                'title': 'Carteira de Investimentos',
                'message': f'Você tem R$ {total_investido:.2f} investidos. Continue diversificando sua carteira!'
            })
        elif renda > 0 and saldo > renda * 0.5:
            insights.append({
                'type': 'suggestion',
                'severity': 'low',
                'icon': '💼',
                'title': 'Sugestão de Investimento',
                'message': f'Você tem R$ {saldo:.2f} disponível. Que tal começar a investir uma parte?'
            })
        
        # Análise de endividamento
        if renda > 0:
            taxa_endividamento = (custos / renda) * 100
            if taxa_endividamento > 70:
                insights.append({
                    'type': 'alert',
                    'severity': 'high',
                    'icon': '🚨',
                    'title': 'Alto Endividamento',
                    'message': f'Seus custos representam {taxa_endividamento:.1f}% da sua renda. Cuidado com as dívidas!'
                })
        
        # Análise de categorias
        categorias = dashboard.get('categorias', {})
        if categorias:
            maior_gasto = max(categorias.items(), key=lambda x: x[1])
            total_custos = sum(categorias.values())
            percentual = (maior_gasto[1] / total_custos * 100) if total_custos > 0 else 0
            
            insights.append({
                'type': 'info',
                'severity': 'low',
                'icon': '📊',
                'title': 'Maior Categoria de Gasto',
                'message': f'{maior_gasto[0]} representa {percentual:.1f}% dos seus gastos (R$ {maior_gasto[1]:.2f})'
            })
        
        return {
            'generated_at': datetime.now().isoformat(),
            'insights': insights,
            'summary': {
                'saldo': saldo,
                'renda': renda,
                'custos': custos,
                'investimentos': total_investido,
                'total_insights': len(insights)
            }
        }
    
    def predict_future_balance(self, financial_data: Dict[str, Any], days: int = 30) -> Dict[str, Any]:
        """Prevê saldo futuro baseado em médias móveis"""
        dashboard = financial_data.get('dashboard', {})
        historico = dashboard.get('historico_saldo', [])
        
        if len(historico) < 3:
            return {
                'error': 'Dados insuficientes para previsão',
                'message': 'É necessário ter pelo menos 3 meses de histórico'
            }
        
        # Calcular média de variação mensal
        variacoes = []
        for i in range(1, len(historico)):
            variacao = historico[i]['valor'] - historico[i-1]['valor']
            variacoes.append(variacao)
        
        media_variacao = sum(variacoes) / len(variacoes)
        saldo_atual = dashboard.get('saldo', 0)
        
        # Projetar para os próximos dias
        meses_futuros = days / 30
        saldo_previsto = saldo_atual + (media_variacao * meses_futuros)
        
        # Análise de tendência
        if media_variacao > 0:
            tendencia = 'positiva'
            emoji = '📈'
            mensagem = f'Tendência positiva! Seu saldo pode chegar a R$ {saldo_previsto:.2f} em {days} dias.'
        elif media_variacao < 0:
            tendencia = 'negativa'
            emoji = '📉'
            mensagem = f'Atenção! Seu saldo pode cair para R$ {saldo_previsto:.2f} em {days} dias.'
        else:
            tendencia = 'estável'
            emoji = '➡️'
            mensagem = f'Saldo estável. Previsão de R$ {saldo_previsto:.2f} em {days} dias.'
        
        return {
            'saldo_atual': saldo_atual,
            'saldo_previsto': saldo_previsto,
            'media_variacao_mensal': media_variacao,
            'tendencia': tendencia,
            'dias': days,
            'emoji': emoji,
            'mensagem': mensagem,
            'confianca': min(len(historico) * 10, 100)  # Confiança baseada em histórico
        }
    
    def detect_anomalies(self, financial_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detecta gastos anormais e padrões incomuns"""
        anomalies = []
        dashboard = financial_data.get('dashboard', {})
        
        # Comparar com mês anterior
        custos_atual = dashboard.get('custos_total', 0)
        custos_anterior = dashboard.get('custos_mes_anterior', 0)
        
        if custos_anterior > 0:
            variacao = ((custos_atual - custos_anterior) / custos_anterior) * 100
            
            if variacao > 30:
                anomalies.append({
                    'type': 'spike',
                    'category': 'custos',
                    'severity': 'high',
                    'message': f'Seus gastos aumentaram {variacao:.1f}% em relação ao mês anterior!',
                    'valor_atual': custos_atual,
                    'valor_anterior': custos_anterior,
                    'variacao_percentual': variacao
                })
            elif variacao < -30:
                anomalies.append({
                    'type': 'drop',
                    'category': 'custos',
                    'severity': 'low',
                    'message': f'Parabéns! Seus gastos caíram {abs(variacao):.1f}% em relação ao mês anterior.',
                    'valor_atual': custos_atual,
                    'valor_anterior': custos_anterior,
                    'variacao_percentual': variacao
                })
        
        # Detectar categorias com gastos muito altos
        categorias = dashboard.get('categorias', {})
        total_custos = sum(categorias.values())
        
        for categoria, valor in categorias.items():
            percentual = (valor / total_custos * 100) if total_custos > 0 else 0
            if percentual > 40:
                anomalies.append({
                    'type': 'concentration',
                    'category': categoria,
                    'severity': 'medium',
                    'message': f'A categoria "{categoria}" representa {percentual:.1f}% dos seus gastos totais.',
                    'valor': valor,
                    'percentual': percentual
                })
        
        return anomalies
    
    def save_conversation(self, user_message: str, ai_response: str, context: Dict = None):
        """Salva conversa no histórico"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO ai_conversations (user_id, tenant_id, user_message, ai_response, context)
            VALUES (?, ?, ?, ?, ?)
        """, (
            self.user_id,
            self.tenant_id,
            user_message,
            ai_response,
            json.dumps(context) if context else None
        ))
        
        conn.commit()
        conn.close()
    
    def save_insight(self, insight_type: str, insight_text: str, data: Dict = None, severity: str = 'low'):
        """Salva insight gerado"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO ai_insights (user_id, tenant_id, insight_type, insight_text, data, severity)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            self.user_id,
            self.tenant_id,
            insight_type,
            insight_text,
            json.dumps(data) if data else None,
            severity
        ))
        
        conn.commit()
        conn.close()
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict]:
        """Recupera histórico de conversas"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM ai_conversations
            WHERE user_id = ? AND tenant_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (self.user_id, self.tenant_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
