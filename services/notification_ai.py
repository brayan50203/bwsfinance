#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Notification AI - Intelligent Insights & Pattern Detection
Camada de IA para análise financeira e geração de notificações inteligentes
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
import re

logger = logging.getLogger('notification_ai')


class NotificationAI:
    """
    Sistema de IA para análise financeira e geração de insights
    """
    
    def __init__(self, db_path: str = 'bws_finance.db'):
        self.db_path = db_path
    
    def analyze_spending_patterns(self, user_id: str, days: int = 30) -> List[Dict]:
        """
        Analisa padrões de gastos e gera insights
        
        Args:
            user_id: ID do usuário
            days: Período de análise em dias
        
        Returns:
            Lista de insights detectados
        """
        insights = []
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Data inicial
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # 1. Detectar gastos duplicados
            duplicates = cursor.execute("""
                SELECT 
                    description, 
                    value, 
                    date, 
                    COUNT(*) as count
                FROM transactions
                WHERE user_id = ? 
                  AND type = 'Despesa'
                  AND date >= ?
                  AND status = 'Pago'
                GROUP BY description, value, date
                HAVING COUNT(*) > 1
            """, (user_id, start_date)).fetchall()
            
            for dup in duplicates:
                insights.append({
                    'type': 'duplicate',
                    'severity': 'medium',
                    'title': 'Possível Gasto Duplicado',
                    'message': f"Detectamos {dup['count']} transações idênticas de R$ {dup['value']:.2f} em '{dup['description']}' no dia {dup['date']}.",
                    'suggestion': "Verifique se não houve cobrança duplicada.",
                    'data': dict(dup)
                })
            
            # 2. Comparar gastos com período anterior
            comparison = self._compare_periods(user_id, days)
            if comparison:
                insights.append(comparison)
            
            # 3. Detectar categoria com maior crescimento
            category_growth = self._detect_category_growth(user_id, days)
            if category_growth:
                insights.append(category_growth)
            
            # 4. Identificar gastos incomuns
            unusual = self._detect_unusual_expenses(user_id)
            insights.extend(unusual)
            
            # 5. Verificar metas de economia
            savings_check = self._check_savings_goal(user_id)
            if savings_check:
                insights.append(savings_check)
            
            logger.info(f"[AI] {len(insights)} insights gerados para {user_id}")
            return insights
        
        except Exception as e:
            logger.error(f"[ERRO] Falha na análise de padrões: {e}")
            return []
        finally:
            conn.close()
    
    def _compare_periods(self, user_id: str, days: int) -> Optional[Dict]:
        """Compara gastos do período atual com anterior"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Período atual
            start_current = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            current = cursor.execute("""
                SELECT COALESCE(SUM(value), 0) as total
                FROM transactions
                WHERE user_id = ? 
                  AND type = 'Despesa'
                  AND date >= ?
                  AND status = 'Pago'
            """, (user_id, start_current)).fetchone()
            
            # Período anterior
            start_previous = (datetime.now() - timedelta(days=days*2)).strftime('%Y-%m-%d')
            end_previous = start_current
            previous = cursor.execute("""
                SELECT COALESCE(SUM(value), 0) as total
                FROM transactions
                WHERE user_id = ? 
                  AND type = 'Despesa'
                  AND date >= ?
                  AND date < ?
                  AND status = 'Pago'
            """, (user_id, start_previous, end_previous)).fetchone()
            
            current_total = current[0]
            previous_total = previous[0]
            
            if previous_total > 0:
                change_pct = ((current_total - previous_total) / previous_total) * 100
                
                if abs(change_pct) >= 15:  # Mudança significativa (15%+)
                    if change_pct > 0:
                        return {
                            'type': 'spending_increase',
                            'severity': 'high' if change_pct > 30 else 'medium',
                            'title': 'Aumento nos Gastos Detectado',
                            'message': f"Seus gastos aumentaram {change_pct:.1f}% em relação ao período anterior (R$ {previous_total:.2f} → R$ {current_total:.2f}).",
                            'suggestion': "Analise suas despesas recentes e identifique onde você pode economizar.",
                            'data': {
                                'current': current_total,
                                'previous': previous_total,
                                'change_pct': change_pct
                            }
                        }
                    else:
                        return {
                            'type': 'spending_decrease',
                            'severity': 'low',
                            'title': 'Parabéns! Gastos Reduzidos',
                            'message': f"Você economizou {abs(change_pct):.1f}% em relação ao período anterior (R$ {previous_total:.2f} → R$ {current_total:.2f}).",
                            'suggestion': "Continue assim! Mantenha o controle financeiro.",
                            'data': {
                                'current': current_total,
                                'previous': previous_total,
                                'change_pct': change_pct
                            }
                        }
            
            return None
        
        except Exception as e:
            logger.error(f"[ERRO] Falha ao comparar períodos: {e}")
            return None
        finally:
            conn.close()
    
    def _detect_category_growth(self, user_id: str, days: int) -> Optional[Dict]:
        """Detecta categoria com maior crescimento"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Gastos por categoria (período atual)
            start_current = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            current = cursor.execute("""
                SELECT 
                    c.name as category,
                    COALESCE(SUM(t.value), 0) as total
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = ?
                  AND t.type = 'Despesa'
                  AND t.date >= ?
                  AND t.status = 'Pago'
                GROUP BY c.name
            """, (user_id, start_current)).fetchall()
            
            # Gastos por categoria (período anterior)
            start_previous = (datetime.now() - timedelta(days=days*2)).strftime('%Y-%m-%d')
            end_previous = start_current
            previous = cursor.execute("""
                SELECT 
                    c.name as category,
                    COALESCE(SUM(t.value), 0) as total
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = ?
                  AND t.type = 'Despesa'
                  AND t.date >= ?
                  AND t.date < ?
                  AND t.status = 'Pago'
                GROUP BY c.name
            """, (user_id, start_previous, end_previous)).fetchall()
            
            # Criar mapas
            current_map = {row['category']: row['total'] for row in current}
            previous_map = {row['category']: row['total'] for row in previous}
            
            # Encontrar maior crescimento
            max_growth = None
            max_growth_pct = 0
            
            for category, current_value in current_map.items():
                previous_value = previous_map.get(category, 0)
                
                if previous_value > 0:
                    growth_pct = ((current_value - previous_value) / previous_value) * 100
                    
                    if growth_pct > max_growth_pct and growth_pct >= 30:
                        max_growth_pct = growth_pct
                        max_growth = {
                            'category': category,
                            'current': current_value,
                            'previous': previous_value,
                            'growth': growth_pct
                        }
            
            if max_growth:
                return {
                    'type': 'category_growth',
                    'severity': 'medium',
                    'title': f"Aumento em {max_growth['category']}",
                    'message': f"Seus gastos com {max_growth['category']} cresceram {max_growth['growth']:.1f}% (R$ {max_growth['previous']:.2f} → R$ {max_growth['current']:.2f}).",
                    'suggestion': f"Revise seus gastos em {max_growth['category']} e veja onde pode cortar.",
                    'data': max_growth
                }
            
            return None
        
        except Exception as e:
            logger.error(f"[ERRO] Falha ao detectar crescimento de categoria: {e}")
            return None
        finally:
            conn.close()
    
    def _detect_unusual_expenses(self, user_id: str) -> List[Dict]:
        """Detecta gastos incomuns (outliers)"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        insights = []
        
        try:
            # Buscar estatísticas dos últimos 90 dias
            stats = cursor.execute("""
                SELECT 
                    AVG(value) as avg_value,
                    MAX(value) as max_value,
                    COUNT(*) as count
                FROM transactions
                WHERE user_id = ?
                  AND type = 'Despesa'
                  AND date >= date('now', '-90 days')
                  AND status = 'Pago'
            """, (user_id,)).fetchone()
            
            if not stats or stats['count'] < 10:
                return []  # Poucos dados para análise
            
            avg = stats['avg_value']
            threshold = avg * 3  # 3x a média
            
            # Buscar gastos recentes acima do threshold
            unusual = cursor.execute("""
                SELECT *
                FROM transactions
                WHERE user_id = ?
                  AND type = 'Despesa'
                  AND value > ?
                  AND date >= date('now', '-7 days')
                  AND status = 'Pago'
                ORDER BY value DESC
                LIMIT 3
            """, (user_id, threshold)).fetchall()
            
            for expense in unusual:
                insights.append({
                    'type': 'unusual_expense',
                    'severity': 'high',
                    'title': 'Gasto Incomum Detectado',
                    'message': f"Gasto de R$ {expense['value']:.2f} em '{expense['description']}' está muito acima da sua média (R$ {avg:.2f}).",
                    'suggestion': "Confirme se este gasto estava planejado.",
                    'data': dict(expense)
                })
            
            return insights
        
        except Exception as e:
            logger.error(f"[ERRO] Falha ao detectar gastos incomuns: {e}")
            return []
        finally:
            conn.close()
    
    def _check_savings_goal(self, user_id: str) -> Optional[Dict]:
        """Verifica progresso em relação a meta de economia"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Calcular saldo do mês atual
            month_start = datetime.now().replace(day=1).strftime('%Y-%m-%d')
            
            balance = cursor.execute("""
                SELECT 
                    COALESCE(SUM(CASE WHEN type = 'Receita' THEN value ELSE 0 END), 0) as income,
                    COALESCE(SUM(CASE WHEN type = 'Despesa' THEN value ELSE 0 END), 0) as expenses
                FROM transactions
                WHERE user_id = ?
                  AND date >= ?
                  AND status = 'Pago'
            """, (user_id, month_start)).fetchone()
            
            income = balance[0]
            expenses = balance[1]
            net = income - expenses
            
            if income > 0:
                savings_rate = (net / income) * 100
                
                # Meta ideal: economizar 20%+
                if savings_rate < 10:
                    return {
                        'type': 'low_savings',
                        'severity': 'high',
                        'title': 'Taxa de Poupança Baixa',
                        'message': f"Você está economizando apenas {savings_rate:.1f}% da sua renda este mês (R$ {net:.2f} de R$ {income:.2f}).",
                        'suggestion': "Tente economizar pelo menos 20% da sua renda. Reduza gastos supérfluos.",
                        'data': {
                            'income': income,
                            'expenses': expenses,
                            'net': net,
                            'rate': savings_rate
                        }
                    }
                elif savings_rate >= 20:
                    return {
                        'type': 'good_savings',
                        'severity': 'low',
                        'title': 'Excelente Taxa de Poupança!',
                        'message': f"Parabéns! Você está economizando {savings_rate:.1f}% da sua renda (R$ {net:.2f} de R$ {income:.2f}).",
                        'suggestion': "Continue assim! Considere investir esse valor.",
                        'data': {
                            'income': income,
                            'expenses': expenses,
                            'net': net,
                            'rate': savings_rate
                        }
                    }
            
            return None
        
        except Exception as e:
            logger.error(f"[ERRO] Falha ao verificar meta de economia: {e}")
            return None
        finally:
            conn.close()
    
    def generate_monthly_report(self, user_id: str) -> Dict:
        """
        Gera relatório mensal completo com insights de IA
        
        Returns:
            Dicionário com resumo e insights
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Período: mês atual
            month_start = datetime.now().replace(day=1).strftime('%Y-%m-%d')
            
            # Resumo financeiro
            summary = cursor.execute("""
                SELECT 
                    COALESCE(SUM(CASE WHEN type = 'Receita' THEN value ELSE 0 END), 0) as income,
                    COALESCE(SUM(CASE WHEN type = 'Despesa' THEN value ELSE 0 END), 0) as expenses,
                    COUNT(CASE WHEN type = 'Despesa' THEN 1 END) as expense_count
                FROM transactions
                WHERE user_id = ?
                  AND date >= ?
                  AND status = 'Pago'
            """, (user_id, month_start)).fetchone()
            
            # Top 5 categorias
            top_categories = cursor.execute("""
                SELECT 
                    c.name,
                    SUM(t.value) as total
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = ?
                  AND t.type = 'Despesa'
                  AND t.date >= ?
                  AND t.status = 'Pago'
                GROUP BY c.name
                ORDER BY total DESC
                LIMIT 5
            """, (user_id, month_start)).fetchall()
            
            # Investimentos (variação)
            investments = cursor.execute("""
                SELECT 
                    COUNT(*) as count,
                    COALESCE(SUM(amount), 0) as invested,
                    COALESCE(SUM(current_value), 0) as current,
                    COALESCE(SUM(current_value - amount), 0) as profit
                FROM investments
                WHERE user_id = ?
                  AND (investment_status = 'active' OR investment_status IS NULL)
            """, (user_id,)).fetchone()
            
            # Insights de IA
            insights = self.analyze_spending_patterns(user_id, days=30)
            
            return {
                'summary': {
                    'income': summary['income'],
                    'expenses': summary['expenses'],
                    'balance': summary['income'] - summary['expenses'],
                    'expense_count': summary['expense_count']
                },
                'top_categories': [
                    {'name': row['name'], 'total': row['total']} 
                    for row in top_categories
                ],
                'investments': dict(investments),
                'insights': insights,
                'month': datetime.now().strftime('%B/%Y')
            }
        
        except Exception as e:
            logger.error(f"[ERRO] Falha ao gerar relatório mensal: {e}")
            return {}
        finally:
            conn.close()
    
    def suggest_budget_cuts(self, user_id: str, target_reduction: float) -> List[Dict]:
        """
        Sugere cortes no orçamento para atingir meta de redução
        
        Args:
            user_id: ID do usuário
            target_reduction: Valor alvo de redução (ex: 500.00)
        
        Returns:
            Lista de sugestões ordenadas por impacto
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        suggestions = []
        
        try:
            # Buscar categorias com maiores gastos
            categories = cursor.execute("""
                SELECT 
                    c.name,
                    SUM(t.value) as total,
                    COUNT(*) as count,
                    AVG(t.value) as avg_value
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = ?
                  AND t.type = 'Despesa'
                  AND t.date >= date('now', '-30 days')
                  AND t.status = 'Pago'
                GROUP BY c.name
                ORDER BY total DESC
            """, (user_id,)).fetchall()
            
            accumulated = 0
            
            for cat in categories:
                if accumulated >= target_reduction:
                    break
                
                # Calcular potencial de redução (15-30%)
                potential = cat['total'] * 0.20  # 20%
                
                suggestions.append({
                    'category': cat['name'],
                    'current_spending': cat['total'],
                    'suggested_reduction': potential,
                    'new_spending': cat['total'] - potential,
                    'reduction_pct': 20,
                    'tip': self._get_saving_tip(cat['name'])
                })
                
                accumulated += potential
            
            return suggestions
        
        except Exception as e:
            logger.error(f"[ERRO] Falha ao sugerir cortes: {e}")
            return []
        finally:
            conn.close()
    
    def _get_saving_tip(self, category: str) -> str:
        """Retorna dica de economia por categoria"""
        tips = {
            'Alimentação': 'Cozinhe mais em casa e reduza pedidos de delivery',
            'Transporte': 'Use transporte público ou caronas compartilhadas',
            'Lazer': 'Procure atividades gratuitas ou mais baratas',
            'Compras': 'Evite compras por impulso, faça lista antes de comprar',
            'Contas': 'Negocie planos mais baratos ou cancele serviços não essenciais',
            'Saúde': 'Use genéricos quando possível',
            'Educação': 'Busque cursos gratuitos online antes de pagar'
        }
        
        return tips.get(category, 'Avalie se este gasto é realmente necessário')
