"""
BWS Insight AI - Processador de Chat Natural
Interpreta perguntas do usuário e responde com contexto financeiro
"""

import re
from typing import Dict, Any, List
from datetime import datetime
from services.ai_ml_engine import MLFinancialEngine

class AIChat:
    """Processador de linguagem natural para chat financeiro"""
    
    def __init__(self, ai_core):
        self.ai_core = ai_core
        self.ml_engine = MLFinancialEngine()  # Motor de Machine Learning
        self.intents = self._load_intents()
    
    def _load_intents(self) -> Dict:
        """Define intenções e padrões de reconhecimento"""
        return {
            'saldo': {
                'patterns': [
                    r'quanto.*tenho',
                    r'qual.*saldo',
                    r'meu saldo',
                    r'quanto.*disponível',
                    r'quanto.*sobrou',
                    r'saldo',
                    r'tem.*disponível',
                    r'quanto.*tem.*conta',
                    r'dinheiro.*disponível',
                    r'saldo.*conta',
                    r'tenho.*dinheiro',
                    r'quanto.*resta',
                    r'saldo.*atual',
                    r'balanço',
                    r'patrimônio',
                    r'capital.*disponível',
                    r'quanto.*de.*dinheiro',
                    r'total.*disponível'
                ],
                'handler': self._handle_balance_query
            },
            'gastos': {
                'patterns': [
                    r'quanto.*gastei',
                    r'gastos.*total',
                    r'despesas',
                    r'quanto.*gast.*(?P<categoria>\w+)',
                    r'gastei.*com.*(?P<categoria>\w+)',
                    r'onde.*gastei',
                    r'quanto.*saiu',
                    r'quanto.*desembolsei',
                    r'total.*gasto',
                    r'total.*despesa',
                    r'minhas.*despesas',
                    r'meus.*gastos',
                    r'quanto.*paguei',
                    r'pagamentos.*fiz',
                    r'quanto.*consumi',
                    r'consumo.*total',
                    r'quanto.*tirei',
                    r'saques',
                    r'debitos',
                    r'débitos',
                    r'gastos.*do.*m(ê|e)s',
                    r'gastei.*no.*m(ê|e)s',
                    r'despesa.*m(ê|e)s',
                    r'quanto.*sai',
                    r'valor.*gasto'
                ],
                'handler': self._handle_expenses_query
            },
            'receitas': {
                'patterns': [
                    r'quanto.*recebi',
                    r'receitas',
                    r'renda',
                    r'ganhos',
                    r'quanto.*ganhei',
                    r'quanto.*entrou',
                    r'minhas.*receitas',
                    r'total.*recebi',
                    r'rendimentos',
                    r'lucros',
                    r'entradas',
                    r'creditos',
                    r'créditos',
                    r'recebi.*quanto',
                    r'dinheiro.*entrou',
                    r'dinheiro.*recebi',
                    r'salario',
                    r'salário',
                    r'quanto.*entra',
                    r'receita.*do.*m(ê|e)s',
                    r'ganho.*do.*m(ê|e)s'
                ],
                'handler': self._handle_income_query
            },
            'investimentos': {
                'patterns': [
                    r'investimentos',
                    r'carteira',
                    r'quanto.*investi',
                    r'rentabilidade',
                    r'rendeu',
                    r'meus.*investimentos',
                    r'como.*est(á|a).*investimento',
                    r'aplica(ç|c)(ões|oes)',
                    r'portf(ó|o)lio',
                    r'a(ç|c)(ões|oes)',
                    r'ações',
                    r'fundos',
                    r'renda.*fixa',
                    r'tesouro',
                    r'cdb',
                    r'quanto.*apliquei',
                    r'lucro.*investimento',
                    r'rendimento.*investimento',
                    r'valoriza(ç|c)(ã|a)o',
                    r'como.*t(á|a).*investindo',
                    r'quanto.*rende',
                    r'performance.*investimento',
                    r'minhas.*a(ç|c)(ões|oes)',
                    r'bolsa',
                    r'b3',
                    r'ativos',
                    r'quanto.*lucrei',
                    r'ganho.*investimento'
                ],
                'handler': self._handle_investments_query
            },
            'previsao': {
                'patterns': [
                    r'previsão',
                    r'futuro',
                    r'próxim',
                    r'vai.*sobrar',
                    r'vai.*faltar',
                    r'previs(ã|a)o',
                    r'o.*que.*vem',
                    r'vai.*ter',
                    r'expectativa',
                    r'proje(ç|c)(ã|a)o',
                    r'quanto.*vou.*ter',
                    r'vai.*gastar'
                ],
                'handler': self._handle_prediction_query
            },
            'comparacao': {
                'patterns': [
                    r'compar',
                    r'mês.*passado',
                    r'anterior',
                    r'gastei.*mais',
                    r'gastei.*menos',
                    r'compara(ç|c)(ã|a)o',
                    r'm(ê|e)s.*passado',
                    r'm(ê|e)s.*anterior',
                    r'diferen(ç|c)a',
                    r'gastei.*mais.*que',
                    r'gastei.*menos.*que',
                    r'evolu(ç|c)(ã|a)o.*gasto',
                    r'como.*foi.*antes',
                    r'versus',
                    r'vs'
                ],
                'handler': self._handle_comparison_query
            },
            'categoria': {
                'patterns': [
                    r'maior.*gasto',
                    r'onde.*gastei.*mais',
                    r'categoria.*maior',
                    r'qual.*categoria',
                    r'tipo.*gasto',
                    r'gasto.*por.*categoria',
                    r'categorias',
                    r'distribui(ç|c)(ã|a)o.*gasto',
                    r'em.*que.*gasto.*mais',
                    r'principal.*despesa',
                    r'que.*tipo.*gasto'
                ],
                'handler': self._handle_category_query
            },
            'anomalias': {
                'patterns': [
                    r'anomalia',
                    r'suspeito',
                    r'incomum',
                    r'gasto.*estranho',
                    r'transaç.*suspeita',
                    r'algo.*errado',
                    r'algo.*suspeito',
                    r'fora.*padr(ã|a)o',
                    r'gasto.*alto',
                    r'gasto.*diferente',
                    r'movimenta(ç|c)(ã|a)o.*estranha'
                ],
                'handler': self._handle_anomaly_query
            },
            'padroes': {
                'patterns': [
                    r'padr(ão|ao|ões|oes)',
                    r'como.*gasto',
                    r'meu.*comportamento',
                    r'análise.*gastos'
                ],
                'handler': self._handle_patterns_query
            },
            'risco': {
                'patterns': [
                    r'risco',
                    r'diversifica',
                    r'portf(ó|o)lio',
                    r'segur.*investimento'
                ],
                'handler': self._handle_risk_query
            },
            'orcamento': {
                'patterns': [
                    r'or(ç|c)amento',
                    r'quanto.*devo.*gastar',
                    r'budget',
                    r'planejamento'
                ],
                'handler': self._handle_budget_query
            },
            'economia': {
                'patterns': [
                    r'economizar',
                    r'poupar',
                    r'guardar.*dinheiro',
                    r'dicas.*economia'
                ],
                'handler': self._handle_savings_tips
            }
        }
    
    def process_message(self, user_message: str, financial_data: Dict[str, Any]) -> str:
        """Processa mensagem do usuário e retorna resposta"""
        message_lower = user_message.lower()
        
        # Detectar intenção
        intent = self._detect_intent(message_lower)
        
        if intent:
            handler = self.intents[intent]['handler']
            response = handler(message_lower, financial_data)
        else:
            response = self._handle_unknown(message_lower, financial_data)
        
        # Salvar conversa
        self.ai_core.save_conversation(user_message, response, {'intent': intent})
        
        return response
    
    def _detect_intent(self, message: str) -> str:
        """Detecta intenção da mensagem"""
        for intent, config in self.intents.items():
            for pattern in config['patterns']:
                if re.search(pattern, message, re.IGNORECASE):
                    return intent
        return None
    
    def _handle_balance_query(self, message: str, data: Dict) -> str:
        """Responde sobre saldo"""
        dashboard = data.get('dashboard', {})
        saldo = dashboard.get('saldo', 0)
        renda = dashboard.get('renda_total', 0)
        custos = dashboard.get('custos_total', 0)
        
        if saldo >= 0:
            emoji = '💰'
            status = 'positivo'
        else:
            emoji = '⚠️'
            status = 'negativo'
        
        response = f"{emoji} Seu saldo atual é de **R$ {saldo:.2f}** ({status}).\n\n"
        response += f"📊 **Resumo do mês:**\n"
        response += f"• Receitas: R$ {renda:.2f}\n"
        response += f"• Despesas: R$ {custos:.2f}\n"
        
        if renda > 0:
            taxa_poupanca = (saldo / renda * 100) if saldo > 0 else 0
            response += f"\n💡 Você está poupando {taxa_poupanca:.1f}% da sua renda."
        
        return response
    
    def _handle_expenses_query(self, message: str, data: Dict) -> str:
        """Responde sobre gastos"""
        dashboard = data.get('dashboard', {})
        custos = dashboard.get('custos_total', 0)
        custos_anterior = dashboard.get('custos_mes_anterior', 0)
        categorias = dashboard.get('categorias', {})
        
        # Verificar se pergunta por categoria específica
        categoria_match = re.search(r'(?:com|em|de)\s+(\w+)', message)
        if categoria_match and categorias:
            categoria_busca = categoria_match.group(1).lower()
            categoria_encontrada = None
            
            for cat, valor in categorias.items():
                if categoria_busca in cat.lower():
                    categoria_encontrada = (cat, valor)
                    break
            
            if categoria_encontrada:
                cat, valor = categoria_encontrada
                percentual = (valor / custos * 100) if custos > 0 else 0
                return f"💸 Você gastou **R$ {valor:.2f}** com **{cat}** este mês.\n\nIsso representa {percentual:.1f}% do total de despesas."
        
        response = f"💸 Seus gastos totais este mês: **R$ {custos:.2f}**\n\n"
        
        if custos_anterior > 0:
            variacao = ((custos - custos_anterior) / custos_anterior) * 100
            if variacao > 0:
                response += f"📈 Aumento de {variacao:.1f}% em relação ao mês passado.\n\n"
            else:
                response += f"📉 Redução de {abs(variacao):.1f}% em relação ao mês passado! 👏\n\n"
        
        if categorias:
            response += "**Maiores gastos:**\n"
            top_3 = sorted(categorias.items(), key=lambda x: x[1], reverse=True)[:3]
            for i, (cat, valor) in enumerate(top_3, 1):
                percentual = (valor / custos * 100) if custos > 0 else 0
                response += f"{i}. {cat}: R$ {valor:.2f} ({percentual:.1f}%)\n"
        
        return response
    
    def _handle_income_query(self, message: str, data: Dict) -> str:
        """Responde sobre receitas"""
        dashboard = data.get('dashboard', {})
        renda = dashboard.get('renda_total', 0)
        renda_anterior = dashboard.get('renda_mes_anterior', 0)
        
        response = f"💵 Sua renda total este mês: **R$ {renda:.2f}**\n\n"
        
        if renda_anterior > 0:
            variacao = ((renda - renda_anterior) / renda_anterior) * 100
            if variacao > 0:
                response += f"📈 Aumento de {variacao:.1f}% em relação ao mês passado!\n"
            elif variacao < 0:
                response += f"📉 Redução de {abs(variacao):.1f}% em relação ao mês passado.\n"
        
        return response
    
    def _handle_investments_query(self, message: str, data: Dict) -> str:
        """Responde sobre investimentos"""
        dashboard = data.get('dashboard', {})
        investments_list = data.get('investments', [])
        
        # Calcular totais
        total_invested = dashboard.get('total_investido', 0)
        total_current = dashboard.get('valor_atual_investimentos', 0)
        total_profit = dashboard.get('lucro_investimentos', 0)
        quantidade = dashboard.get('quantidade_investimentos', 0)
        
        if quantidade == 0 or not investments_list:
            return "📊 Você ainda não possui investimentos registrados.\n\n💡 Que tal começar a investir? Uma boa meta é investir 10-20% da sua renda mensal."
        
        response = f"📈 **Carteira de Investimentos**\n\n"
        response += f"💰 Total investido: **R$ {total_invested:.2f}**\n"
        response += f"💵 Valor atual: **R$ {total_current:.2f}**\n"
        
        if total_profit > 0:
            percentual = (total_profit / total_invested * 100) if total_invested > 0 else 0
            response += f"📊 Lucro: **R$ {total_profit:.2f}** (+{percentual:.2f}%)\n"
        elif total_profit < 0:
            percentual = (abs(total_profit) / total_invested * 100) if total_invested > 0 else 0
            response += f"📉 Prejuízo: **R$ {abs(total_profit):.2f}** (-{percentual:.2f}%)\n"
        
        response += f"\n📦 **{quantidade} investimentos ativos:**\n"
        
        # Mostrar até 5 investimentos
        for inv in investments_list[:5]:
            nome = inv.get('name', 'N/A')
            tipo = inv.get('investment_type', 'N/A')
            valor = inv.get('current_value', 0)
            response += f"• {nome} ({tipo}): R$ {valor:.2f}\n"
        
        if len(investments_list) > 5:
            response += f"\n... e mais {len(investments_list) - 5} investimentos"
        
        return response
    
    def _handle_prediction_query(self, message: str, data: Dict) -> str:
        """Responde sobre previsões"""
        previsao = self.ai_core.predict_future_balance(data, days=30)
        
        if 'error' in previsao:
            return f"⚠️ {previsao['message']}"
        
        return f"{previsao['emoji']} **Previsão para os próximos 30 dias:**\n\n" + previsao['mensagem'] + f"\n\n📊 Confiança da previsão: {previsao['confianca']}%"
    
    def _handle_comparison_query(self, message: str, data: Dict) -> str:
        """Responde sobre comparações"""
        dashboard = data.get('dashboard', {})
        custos = dashboard.get('custos_total', 0)
        custos_anterior = dashboard.get('custos_mes_anterior', 0)
        renda = dashboard.get('renda_total', 0)
        renda_anterior = dashboard.get('renda_mes_anterior', 0)
        
        response = "📊 **Comparativo com mês anterior:**\n\n"
        
        if custos_anterior > 0:
            var_custos = ((custos - custos_anterior) / custos_anterior) * 100
            if var_custos > 0:
                response += f"💸 Gastos: +{var_custos:.1f}% (R$ {custos:.2f} vs R$ {custos_anterior:.2f})\n"
            else:
                response += f"💸 Gastos: {var_custos:.1f}% (R$ {custos:.2f} vs R$ {custos_anterior:.2f}) 👏\n"
        
        if renda_anterior > 0:
            var_renda = ((renda - renda_anterior) / renda_anterior) * 100
            if var_renda > 0:
                response += f"💵 Receitas: +{var_renda:.1f}% (R$ {renda:.2f} vs R$ {renda_anterior:.2f})\n"
            else:
                response += f"💵 Receitas: {var_renda:.1f}% (R$ {renda:.2f} vs R$ {renda_anterior:.2f})\n"
        
        return response
    
    def _handle_category_query(self, message: str, data: Dict) -> str:
        """Responde sobre categorias"""
        dashboard = data.get('dashboard', {})
        categorias = dashboard.get('categorias', {})
        
        if not categorias:
            return "📊 Não há gastos registrados por categoria este mês."
        
        maior = max(categorias.items(), key=lambda x: x[1])
        total = sum(categorias.values())
        percentual = (maior[1] / total * 100) if total > 0 else 0
        
        response = f"🏆 **Maior categoria de gasto:**\n\n"
        response += f"📌 **{maior[0]}**: R$ {maior[1]:.2f} ({percentual:.1f}% do total)\n\n"
        
        response += "**Top 5 categorias:**\n"
        top_5 = sorted(categorias.items(), key=lambda x: x[1], reverse=True)[:5]
        for i, (cat, valor) in enumerate(top_5, 1):
            perc = (valor / total * 100) if total > 0 else 0
            response += f"{i}. {cat}: R$ {valor:.2f} ({perc:.1f}%)\n"
        
        return response
    
    def _handle_unknown(self, message: str, data: Dict) -> str:
        """Resposta padrão para perguntas não reconhecidas"""
        dashboard = data.get('dashboard', {})
        saldo = dashboard.get('saldo', 0)
        
        response = "🤔 Desculpe, não entendi sua pergunta.\n\n"
        response += "Você pode me perguntar sobre:\n\n"
        response += "**💰 Básico:**\n"
        response += "• \"Qual meu saldo?\"\n"
        response += "• \"Quanto gastei este mês?\"\n"
        response += "• \"Onde gastei mais?\"\n\n"
        response += "**📈 Investimentos:**\n"
        response += "• \"Como estão meus investimentos?\"\n"
        response += "• \"Qual o risco do meu portfólio?\"\n\n"
        response += "**🔮 Previsões (ML):**\n"
        response += "• \"Qual a previsão para o próximo mês?\"\n"
        response += "• \"Gastei mais que o mês passado?\"\n\n"
        response += "**🧠 Inteligência Avançada:**\n"
        response += "• \"Detecte anomalias nos meus gastos\"\n"
        response += "• \"Analise meus padrões de gastos\"\n"
        response += "• \"Me sugira um orçamento\"\n"
        response += "• \"Como posso economizar?\"\n"
        
        if saldo != 0:
            response += f"\n\n💡 **Rápido:** Seu saldo atual é R$ {saldo:.2f}"
        
        return response
    
    def _handle_anomaly_query(self, message: str, data: Dict) -> str:
        """Detecta anomalias usando Machine Learning"""
        dashboard = data.get('dashboard', {})
        transactions = dashboard.get('transactions', [])
        
        if not transactions:
            return "📊 Não há transações suficientes para análise de anomalias."
        
        anomalies = self.ml_engine.detect_spending_anomalies_ml(transactions)
        
        if not anomalies:
            return "✅ **Nenhuma anomalia detectada!**\n\nTodas as suas transações estão dentro dos padrões normais de gastos. Continue assim! 👏"
        
        response = f"🔍 **Detecção de Anomalias (ML)**\n\n"
        response += f"Encontrei **{len(anomalies)}** transaç{'ão' if len(anomalies) == 1 else 'ões'} suspeita{'s' if len(anomalies) > 1 else ''}:\n\n"
        
        for idx, anomaly in enumerate(anomalies[:5], 1):  # Limitar a 5
            t = anomaly['transaction']
            response += f"{idx}. 🚨 **R$ {abs(t.get('amount', 0)):.2f}** - {t.get('category', 'N/A')}\n"
            response += f"   📅 {t.get('date', 'N/A')} - {anomaly['reason']}\n\n"
        
        if len(anomalies) > 5:
            response += f"_...e mais {len(anomalies) - 5} transações suspeitas_\n\n"
        
        response += "💡 **Recomendação:** Revise essas transações para confirmar se são gastos válidos."
        
        return response
    
    def _handle_patterns_query(self, message: str, data: Dict) -> str:
        """Analisa padrões de gastos com clustering"""
        dashboard = data.get('dashboard', {})
        transactions = dashboard.get('transactions', [])
        
        if not transactions:
            return "📊 Não há transações suficientes para análise de padrões."
        
        clustering_result = self.ml_engine.cluster_spending_patterns(transactions)
        
        response = f"🧠 **Análise de Padrões de Gastos (ML)**\n\n"
        response += f"{clustering_result['analysis']}\n\n"
        
        for cluster in clustering_result['clusters']:
            response += f"**{cluster['name']}**\n"
            response += f"• Valor médio: R$ {cluster['avg_amount']:.2f}\n"
            response += f"• {cluster['count']} transações ({cluster['percentage']}%)\n"
            response += f"• Total: R$ {cluster['total']:.2f}\n"
            response += f"• {cluster['description']}\n\n"
        
        response += f"💡 {clustering_result['recommendation']}"
        
        return response
    
    def _handle_risk_query(self, message: str, data: Dict) -> str:
        """Analisa risco do portfólio"""
        investments_data = data.get('investments', {})
        portfolio = investments_data.get('investments', []) if isinstance(investments_data, dict) else []
        
        if not portfolio:
            return "📊 Você não possui investimentos para análise de risco.\n\n💡 Considere começar a investir para diversificar suas finanças!"
        
        risk_analysis = self.ml_engine.analyze_investment_risk(portfolio)
        
        response = f"🎯 **Análise de Risco do Portfólio**\n\n"
        response += f"{risk_analysis['risk_emoji']} **Nível de Risco:** {risk_analysis['risk_level'].upper()}\n"
        response += f"📊 **Score de Diversificação:** {risk_analysis['diversification_score']}/100\n\n"
        
        response += f"**Detalhes:**\n"
        response += f"• Número de ativos: {risk_analysis['num_assets']}\n"
        response += f"• Concentração: {risk_analysis['concentration_percent']}%\n"
        response += f"• Volatilidade: {risk_analysis['volatility']:.2f}%\n\n"
        
        response += f"💡 **Recomendação:**\n{risk_analysis['recommendation']}"
        
        return response
    
    def _handle_budget_query(self, message: str, data: Dict) -> str:
        """Recomenda orçamento inteligente (regra 50/30/20)"""
        dashboard = data.get('dashboard', {})
        renda = dashboard.get('renda_total', 0)
        categorias = dashboard.get('categorias', {})
        
        if renda <= 0:
            return "💰 Para criar um orçamento, preciso saber sua renda mensal.\n\n💡 Adicione suas receitas no sistema!"
        
        budget_rec = self.ml_engine.smart_budget_recommendation(renda, categorias)
        
        response = f"📊 **Orçamento Inteligente (Regra 50/30/20)**\n\n"
        response += f"💵 Sua renda: R$ {renda:.2f}\n\n"
        
        response += f"**Orçamento Ideal:**\n"
        response += f"• 🏠 Necessidades (50%): R$ {budget_rec['ideal_budget']['necessidades']:.2f}\n"
        response += f"• 🎉 Desejos (30%): R$ {budget_rec['ideal_budget']['desejos']:.2f}\n"
        response += f"• 💰 Poupança (20%): R$ {budget_rec['ideal_budget']['poupanca']:.2f}\n\n"
        
        response += f"**Situação Atual:**\n"
        response += f"• Necessidades: R$ {budget_rec['current_distribution']['necessidades']:.2f}\n"
        response += f"• Desejos: R$ {budget_rec['current_distribution']['desejos']:.2f}\n"
        response += f"• Poupança: R$ {budget_rec['current_distribution']['poupanca']:.2f}\n"
        response += f"• Taxa de poupança: {budget_rec['savings_rate']:.1f}%\n\n"
        
        response += f"**Análise:**\n"
        for analysis_item in budget_rec['analysis']:
            response += f"• {analysis_item}\n"
        
        return response
    
    def _handle_savings_tips(self, message: str, data: Dict) -> str:
        """Dá dicas personalizadas de economia"""
        dashboard = data.get('dashboard', {})
        categorias = dashboard.get('categorias', {})
        renda = dashboard.get('renda_total', 0)
        custos = dashboard.get('custos_total', 0)
        
        if not categorias:
            return "💡 Para dar dicas personalizadas, preciso de mais dados sobre seus gastos."
        
        # Identificar maiores gastos
        top_categories = sorted(categorias.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Calcular taxa de poupança
        savings_rate = ((renda - custos) / renda * 100) if renda > 0 else 0
        
        response = f"💡 **Dicas Personalizadas de Economia**\n\n"
        
        # Dicas baseadas na taxa de poupança
        if savings_rate < 10:
            response += "🚨 **Atenção:** Sua taxa de poupança está muito baixa ({:.1f}%).\n\n".format(savings_rate)
            response += "**Ação Urgente:**\n"
            response += "1. Revise todos os gastos não essenciais\n"
            response += "2. Considere cancelar serviços pouco usados\n"
            response += "3. Estabeleça um limite diário de gastos\n\n"
        elif savings_rate < 20:
            response += "⚠️ Sua taxa de poupança é de {:.1f}%. Meta ideal: 20%.\n\n".format(savings_rate)
        else:
            response += "🎉 Parabéns! Você está poupando {:.1f}% da renda!\n\n".format(savings_rate)
        
        # Dicas baseadas nas maiores categorias
        response += "**Onde você pode economizar:**\n\n"
        
        for idx, (cat, valor) in enumerate(top_categories, 1):
            perc = (valor / custos * 100) if custos > 0 else 0
            response += f"{idx}. **{cat}** (R$ {valor:.2f} - {perc:.1f}%)\n"
            
            # Dicas específicas por categoria
            if 'alimenta' in cat.lower():
                response += "   💡 Cozinhe mais em casa, leve marmita\n"
                response += "   💡 Faça lista de compras e evite desperdício\n"
            elif 'transporte' in cat.lower():
                response += "   💡 Considere transporte público ou carona\n"
                response += "   💡 Avalie apps de mobilidade mais baratos\n"
            elif 'lazer' in cat.lower():
                response += "   💡 Procure atividades gratuitas ou mais baratas\n"
                response += "   💡 Aproveite promoções e descontos\n"
            elif 'compras' in cat.lower():
                response += "   💡 Espere 24h antes de compras impulsivas\n"
                response += "   💡 Use a regra: preciso ou quero?\n"
            else:
                response += "   💡 Renegocie valores e compare preços\n"
            
            response += "\n"
        
        # Dica de desafio
        economia_mensal = renda * 0.05  # 5% da renda
        response += f"🎯 **Desafio do Mês:**\n"
        response += f"Tente economizar R$ {economia_mensal:.2f} (5% da renda).\n"
        response += f"Em 12 meses, você terá R$ {economia_mensal * 12:.2f}!\n\n"
        
        response += "💪 **Lembre-se:** Pequenas economias diárias fazem grande diferença no longo prazo!"
        
        return response
