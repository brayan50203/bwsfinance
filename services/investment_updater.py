"""
Módulo de Atualização Automática de Investimentos
Atualiza cotações de ações, ETFs, criptomoedas e Tesouro Direto
usando APIs gratuitas (Yahoo Finance, CoinGecko, Tesouro Transparente)
"""

import sqlite3
import logging
import yfinance as yf
import requests
from datetime import datetime
from typing import Dict, Optional, List
import os

# ===============================================
# CONFIGURAÇÃO DE LOGS
# ===============================================

# Garantir que o diretório de logs existe
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'investments.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ===============================================
# CONEXÃO COM BANCO DE DADOS
# ===============================================

def get_db_connection():
    """Conecta ao banco de dados SQLite"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bws_finance.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# ===============================================
# FUNÇÕES DE ATUALIZAÇÃO POR TIPO
# ===============================================

def update_stock_br(ticker: str, initial_value: float) -> Optional[Dict]:
    """
    Atualiza cotação de ações brasileiras (B3)
    
    Args:
        ticker: Código da ação (ex: PETR4, VALE3, ITUB4)
        initial_value: Valor inicial investido
    
    Returns:
        Dict com current_value e percent_change, ou None se falhar
    """
    try:
        # Adicionar .SA para ações brasileiras no Yahoo Finance
        symbol = f"{ticker}.SA" if not ticker.endswith('.SA') else ticker
        
        stock = yf.Ticker(symbol)
        data = stock.history(period='1d')
        
        if data.empty:
            logger.warning(f"⚠️ Nenhum dado encontrado para {ticker}")
            return None
        
        current_price = data['Close'].iloc[-1]
        
        # Calcular valor atual baseado no investimento inicial
        # Assumindo que o usuário comprou na data de criação
        info = stock.info
        shares_owned = initial_value / info.get('previousClose', current_price)
        current_value = shares_owned * current_price
        
        percent_change = ((current_value - initial_value) / initial_value) * 100
        
        logger.info(f"✅ {ticker} atualizado: R$ {current_value:.2f} ({percent_change:+.2f}%)")
        
        return {
            'current_value': round(current_value, 2),
            'percent_change': round(percent_change, 2),
            'current_price': round(current_price, 2)
        }
        
    except Exception as e:
        logger.error(f"🔴 Falha ao atualizar {ticker}: {str(e)}")
        return None

def update_crypto(crypto_symbol: str, initial_value: float) -> Optional[Dict]:
    """
    Atualiza cotação de criptomoedas via CoinGecko
    
    Args:
        crypto_symbol: Símbolo da cripto (ex: BTC, ETH, SOL)
        initial_value: Valor inicial investido
    
    Returns:
        Dict com current_value e percent_change, ou None se falhar
    """
    try:
        # Mapeamento de símbolos comuns
        crypto_map = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'BNB': 'binancecoin',
            'SOL': 'solana',
            'ADA': 'cardano',
            'XRP': 'ripple',
            'DOT': 'polkadot',
            'DOGE': 'dogecoin',
            'AVAX': 'avalanche-2',
            'MATIC': 'matic-network'
        }
        
        crypto_id = crypto_map.get(crypto_symbol.upper(), crypto_symbol.lower())
        
        # API CoinGecko (gratuita, sem chave necessária)
        url = f"https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': crypto_id,
            'vs_currencies': 'brl',
            'include_24hr_change': 'true'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if crypto_id not in data:
            logger.warning(f"⚠️ Cripto {crypto_symbol} não encontrada")
            return None
        
        current_price_brl = data[crypto_id]['brl']
        
        # Calcular valor atual (assumindo que comprou na data de criação)
        # Simplificação: usar valor inicial como base
        percent_change = data[crypto_id].get('brl_24h_change', 0)
        current_value = initial_value * (1 + percent_change / 100)
        
        logger.info(f"✅ {crypto_symbol} atualizado: R$ {current_value:.2f} ({percent_change:+.2f}%)")
        
        return {
            'current_value': round(current_value, 2),
            'percent_change': round(percent_change, 2),
            'current_price': round(current_price_brl, 2)
        }
        
    except Exception as e:
        logger.error(f"🔴 Falha ao atualizar cripto {crypto_symbol}: {str(e)}")
        return None

def update_tesouro_direto(bond_type: str, initial_value: float) -> Optional[Dict]:
    """
    Atualiza títulos do Tesouro Direto
    
    Args:
        bond_type: Tipo do título (ex: Tesouro Selic, Tesouro IPCA+)
        initial_value: Valor inicial investido
    
    Returns:
        Dict com current_value e percent_change, ou None se falhar
    """
    try:
        # API Tesouro Transparente (gratuita)
        url = "https://www.tesourotransparente.gov.br/ckan/api/3/action/datastore_search"
        params = {
            'resource_id': 'e4f90175-6b6e-4e15-9d8a-8d6861e441aa',
            'limit': 100
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        
        # Procurar título específico
        records = data.get('result', {}).get('records', [])
        
        # Simplificação: aplicar taxa Selic média (6% ao ano)
        # Em produção, você buscaria a taxa real do título específico
        annual_rate = 6.0  # Taxa estimada
        days_invested = 30  # Assumindo 1 mês (simplificação)
        daily_rate = (1 + annual_rate / 100) ** (1 / 365) - 1
        
        current_value = initial_value * ((1 + daily_rate) ** days_invested)
        percent_change = ((current_value - initial_value) / initial_value) * 100
        
        logger.info(f"✅ {bond_type} atualizado: R$ {current_value:.2f} ({percent_change:+.2f}%)")
        
        return {
            'current_value': round(current_value, 2),
            'percent_change': round(percent_change, 2),
            'current_price': round(current_value, 2)
        }
        
    except Exception as e:
        logger.error(f"🔴 Falha ao atualizar Tesouro {bond_type}: {str(e)}")
        return None

def update_generic_investment(investment_name: str, initial_value: float) -> Optional[Dict]:
    """
    Atualização genérica para investimentos sem API específica
    Mantém o valor atual ou aplica taxa conservadora
    """
    try:
        # Aplicar taxa conservadora (0.5% ao mês = ~6% ao ano)
        monthly_rate = 0.005
        current_value = initial_value * (1 + monthly_rate)
        percent_change = monthly_rate * 100
        
        logger.info(f"ℹ️ {investment_name} atualizado (estimativa): R$ {current_value:.2f}")
        
        return {
            'current_value': round(current_value, 2),
            'percent_change': round(percent_change, 2),
            'current_price': round(current_value, 2)
        }
        
    except Exception as e:
        logger.error(f"🔴 Falha ao atualizar {investment_name}: {str(e)}")
        return None

# ===============================================
# FUNÇÃO PRINCIPAL DE ATUALIZAÇÃO
# ===============================================

def update_all_investments() -> Dict[str, int]:
    """
    Atualiza todos os investimentos do banco de dados
    
    Returns:
        Dict com contadores de sucesso, falhas e total
    """
    logger.info("=" * 60)
    logger.info("💰 Atualização de investimentos iniciada...")
    logger.info("=" * 60)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    stats = {
        'total': 0,
        'success': 0,
        'failed': 0,
        'skipped': 0
    }
    
    try:
        # Buscar todos os investimentos ativos
        investments = cursor.execute("""
            SELECT id, name, investment_type, amount, current_value
            FROM investments
            WHERE investment_status = 'active' OR investment_status IS NULL
        """).fetchall()
        
        stats['total'] = len(investments)
        
        if stats['total'] == 0:
            logger.info("ℹ️ Nenhum investimento ativo encontrado")
            return stats
        
        logger.info(f"📊 Total de investimentos a atualizar: {stats['total']}")
        
        for investment in investments:
            inv_id = investment['id']
            inv_name = investment['name']
            inv_type = investment['investment_type'] or 'Outro'
            initial_amount = investment['amount'] or 0
            
            result = None
            
            # Identificar tipo e chamar API apropriada
            if inv_type.lower() in ['ação', 'acao', 'stock', 'ações']:
                # Extrair ticker do nome (ex: "Petrobras PETR4" -> "PETR4")
                ticker = inv_name.split()[-1].upper()
                result = update_stock_br(ticker, initial_amount)
                
            elif inv_type.lower() in ['cripto', 'criptomoeda', 'crypto']:
                # Extrair símbolo (ex: "Bitcoin BTC" -> "BTC")
                symbol = inv_name.split()[-1].upper()
                result = update_crypto(symbol, initial_amount)
                
            elif inv_type.lower() in ['tesouro', 'tesouro direto', 'renda fixa']:
                result = update_tesouro_direto(inv_name, initial_amount)
                
            elif inv_type.lower() in ['etf']:
                # ETFs também usam Yahoo Finance
                ticker = inv_name.split()[-1].upper()
                result = update_stock_br(ticker, initial_amount)
                
            else:
                # Tipo não reconhecido, usar atualização genérica
                result = update_generic_investment(inv_name, initial_amount)
            
            # Atualizar no banco se obteve resultado
            if result:
                cursor.execute("""
                    UPDATE investments
                    SET current_value = ?
                    WHERE id = ?
                """, (result['current_value'], inv_id))
                
                stats['success'] += 1
            else:
                stats['failed'] += 1
        
        conn.commit()
        
        logger.info("=" * 60)
        logger.info(f"✅ Atualização concluída!")
        logger.info(f"   Total: {stats['total']} | Sucesso: {stats['success']} | Falhas: {stats['failed']}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"🔴 Erro crítico na atualização: {str(e)}")
        conn.rollback()
        
    finally:
        conn.close()
    
    return stats

# ===============================================
# FUNÇÃO PARA ATUALIZAÇÃO MANUAL
# ===============================================

def update_single_investment(investment_id: str) -> bool:
    """
    Atualiza um investimento específico
    
    Args:
        investment_id: ID do investimento
    
    Returns:
        True se sucesso, False caso contrário
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        investment = cursor.execute("""
            SELECT id, name, investment_type, amount
            FROM investments
            WHERE id = ? AND (investment_status = 'active' OR investment_status IS NULL)
        """, (investment_id,)).fetchone()
        
        if not investment:
            logger.warning(f"⚠️ Investimento {investment_id} não encontrado")
            return False
        
        inv_name = investment['name']
        inv_type = investment['investment_type'] or 'Outro'
        initial_amount = investment['amount'] or 0
        
        result = None
        
        # Lógica similar à update_all_investments
        if inv_type.lower() in ['ação', 'acao', 'stock']:
            ticker = inv_name.split()[-1].upper()
            result = update_stock_br(ticker, initial_amount)
        elif inv_type.lower() in ['cripto', 'criptomoeda', 'crypto']:
            symbol = inv_name.split()[-1].upper()
            result = update_crypto(symbol, initial_amount)
        elif inv_type.lower() in ['tesouro', 'tesouro direto', 'renda fixa']:
            result = update_tesouro_direto(inv_name, initial_amount)
        else:
            result = update_generic_investment(inv_name, initial_amount)
        
        if result:
            cursor.execute("""
                UPDATE investments
                SET current_value = ?
                WHERE id = ?
            """, (result['current_value'], investment_id))
            
            conn.commit()
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"🔴 Erro ao atualizar investimento {investment_id}: {str(e)}")
        return False
        
    finally:
        conn.close()

# ===============================================
# TESTE DO MÓDULO
# ===============================================

if __name__ == "__main__":
    print("🧪 Testando módulo de atualização de investimentos...\n")
    update_all_investments()
