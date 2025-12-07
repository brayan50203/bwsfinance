"""
API Connectors - Conexão com APIs externas para investimentos
Suporta: Yahoo Finance, CoinGecko, Tesouro Direto
"""

import requests
import json
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    filename='investments.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class APIConnector:
    """Classe base para conectores de API"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def log_api_call(self, api_name, symbol, success, error=None):
        """Registra chamadas de API no log"""
        if success:
            logging.info(f"✅ {api_name} - {symbol} - Sucesso")
        else:
            logging.error(f"❌ {api_name} - {symbol} - Erro: {error}")


class YahooFinanceConnector(APIConnector):
    """Conector para Yahoo Finance (Ações B3 e ETFs)"""
    
    BASE_URL = "https://query1.finance.yahoo.com/v7/finance/quote"
    
    def get_stock_data(self, symbol):
        """
        Busca dados de uma ação
        Args:
            symbol: código do ativo (ex: PETR4.SA)
        Returns:
            dict com price, previousClose, marketCap, etc
        """
        try:
            # Garantir que tem .SA no final
            if not symbol.endswith('.SA'):
                symbol = f"{symbol}.SA"
            
            # Detectar tipo de ativo pelo ticker original (sem .SA)
            ticker_base = symbol.replace('.SA', '').upper()
            is_fii = ticker_base.endswith('11')
            asset_type = 'FII' if is_fii else 'Ação'
            
            params = {
                'symbols': symbol,
                'fields': 'regularMarketPrice,regularMarketPreviousClose,regularMarketChange,regularMarketChangePercent,longName,shortName'
            }
            
            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'quoteResponse' in data and 'result' in data['quoteResponse']:
                results = data['quoteResponse']['result']
                if results and len(results) > 0:
                    result = results[0]
                    
                    stock_data = {
                        'symbol': symbol,
                        'name': result.get('longName') or result.get('shortName', symbol),
                        'price': result.get('regularMarketPrice', 0),
                        'previous_close': result.get('regularMarketPreviousClose', 0),
                        'change': result.get('regularMarketChange', 0),
                        'change_percent': result.get('regularMarketChangePercent', 0),
                        'asset_type': asset_type,  # 'FII' ou 'Ação'
                        'last_update': datetime.now().isoformat()
                    }
                    
                    self.log_api_call('Yahoo Finance', symbol, True)
                    return stock_data
            
            self.log_api_call('Yahoo Finance', symbol, False, 'Sem resultados')
            return None
            
        except Exception as e:
            self.log_api_call('Yahoo Finance', symbol, False, str(e))
            return None


class BrapiConnector(APIConnector):
    """Conector para Brapi - API Brasileira de Ações (fallback)"""
    
    BASE_URL = "https://brapi.dev/api/quote"
    
    def get_stock_data(self, ticker):
        """
        Busca dados de uma ação via Brapi
        Args:
            ticker: código da ação (ex: PETR4)
        Returns:
            dict com price e dados da ação
        """
        try:
            # Remover .SA se houver
            ticker = ticker.replace('.SA', '').upper()
            
            # URL da API
            url = f"{self.BASE_URL}/{ticker}"
            
            print(f"🔍 Buscando {ticker} via Brapi...")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'results' in data and len(data['results']) > 0:
                result = data['results'][0]
                
                stock_data = {
                    'symbol': ticker,
                    'name': result.get('longName', result.get('shortName', ticker)),
                    'price': result.get('regularMarketPrice', 0),
                    'previous_close': result.get('regularMarketPreviousClose', 0),
                    'change': result.get('regularMarketChange', 0),
                    'change_percent': result.get('regularMarketChangePercent', 0),
                    'market_cap': result.get('marketCap', 0),
                    'last_update': datetime.now().isoformat()
                }
                
                if stock_data['price'] > 0:
                    print(f"✅ Brapi: {ticker} = R$ {stock_data['price']:.2f}")
                    self.log_api_call('Brapi', ticker, True)
                    return stock_data
            
            self.log_api_call('Brapi', ticker, False, 'Sem resultados')
            return None
            
        except Exception as e:
            print(f"❌ Erro Brapi para {ticker}: {e}")
            self.log_api_call('Brapi', ticker, False, str(e))
            return None


class StatusInvestConnector(APIConnector):
    """Conector para Status Invest - Dados de ações brasileiras (fallback)"""
    
    BASE_URL = "https://statusinvest.com.br"
    
    def __init__(self):
        super().__init__()
        # Headers mais completos para Status Invest
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://statusinvest.com.br/',
            'Origin': 'https://statusinvest.com.br'
        })
    
    def get_stock_data(self, ticker):
        """
        Busca dados de uma ação via Status Invest
        Args:
            ticker: código da ação (ex: PETR4)
        Returns:
            dict com price e dados da ação
        """
        try:
            # Remover .SA se houver
            ticker = ticker.replace('.SA', '').upper()
            
            # Detectar se é FII ou Ação
            is_fii = ticker.endswith('11')
            asset_type = 'FII' if is_fii else 'Ação'
            
            print(f"🔍 Buscando {ticker} ({asset_type}) via Status Invest...")
            
            # API de cotação do Status Invest - diferentes endpoints para FII e Ação
            if is_fii:
                # Endpoint para FIIs
                url = f"{self.BASE_URL}/fundos-imobiliarios/companytickerprice"
                params = {
                    'ticker': ticker,
                    'type': '1'  # Tipo 1 para FIIs
                }
            else:
                # Endpoint para Ações
                url = f"{self.BASE_URL}/acao/companytickerprice"
                params = {
                    'ticker': ticker,
                    'type': '2'  # Tipo 2 para ações
                }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if isinstance(data, list) and len(data) > 0:
                result = data[0]
                
                stock_data = {
                    'symbol': ticker,
                    'name': result.get('companyName', ticker),
                    'price': result.get('price', 0),
                    'change': result.get('valorDiferenca', 0),
                    'change_percent': result.get('percentualDiferenca', 0),
                    'asset_type': asset_type,  # 'FII' ou 'Ação'
                    'last_update': datetime.now().isoformat()
                }
                
                if stock_data['price'] > 0:
                    print(f"✅ Status Invest: {ticker} = R$ {stock_data['price']:.2f}")
                    self.log_api_call('Status Invest', ticker, True)
                    return stock_data
            
            self.log_api_call('Status Invest', ticker, False, 'Sem resultados')
            return None
            
        except Exception as e:
            print(f"❌ Erro Status Invest para {ticker}: {e}")
            self.log_api_call('Status Invest', ticker, False, str(e))
            return None


class CoinGeckoConnector(APIConnector):
    """Conector para CoinGecko (Criptomoedas)"""
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    # Mapeamento de símbolos para IDs do CoinGecko
    CRYPTO_MAP = {
        'BTC': 'bitcoin',
        'BITCOIN': 'bitcoin',
        'ETH': 'ethereum',
        'ETHEREUM': 'ethereum',
        'BNB': 'binancecoin',
        'BINANCE': 'binancecoin',
        'ADA': 'cardano',
        'CARDANO': 'cardano',
        'SOL': 'solana',
        'SOLANA': 'solana',
        'XRP': 'ripple',
        'RIPPLE': 'ripple',
        'DOGE': 'dogecoin',
        'DOGECOIN': 'dogecoin',
        'DOT': 'polkadot',
        'POLKADOT': 'polkadot',
        'MATIC': 'matic-network',
        'POLYGON': 'matic-network',
        'USDT': 'tether',
        'TETHER': 'tether',
        'USDC': 'usd-coin',
        'LINK': 'chainlink',
        'CHAINLINK': 'chainlink',
        'UNI': 'uniswap',
        'UNISWAP': 'uniswap',
        'AVAX': 'avalanche-2',
        'AVALANCHE': 'avalanche-2',
        'ATOM': 'cosmos',
        'COSMOS': 'cosmos',
        'LTC': 'litecoin',
        'LITECOIN': 'litecoin',
    }
    
    def get_crypto_id(self, symbol):
        """Converte símbolo para ID do CoinGecko"""
        symbol_upper = symbol.upper().replace(' ', '')
        return self.CRYPTO_MAP.get(symbol_upper, symbol.lower())
    
    def get_crypto_data(self, symbol):
        """
        Busca dados de uma criptomoeda
        Args:
            symbol: código da cripto (ex: BTC, BITCOIN)
        Returns:
            dict com price, change_24h, market_cap, etc
        """
        try:
            crypto_id = self.get_crypto_id(symbol)
            
            # Buscar preço em BRL
            url = f"{self.BASE_URL}/simple/price"
            params = {
                'ids': crypto_id,
                'vs_currencies': 'brl',
                'include_24hr_change': 'true',
                'include_market_cap': 'true',
                'include_last_updated_at': 'true'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if crypto_id in data:
                crypto_info = data[crypto_id]
                
                crypto_data = {
                    'symbol': symbol.upper(),
                    'name': crypto_id.title(),
                    'price': crypto_info.get('brl', 0),
                    'change_24h': crypto_info.get('brl_24h_change', 0),
                    'market_cap': crypto_info.get('brl_market_cap', 0),
                    'last_update': datetime.now().isoformat()
                }
                
                self.log_api_call('CoinGecko', symbol, True)
                return crypto_data
            
            self.log_api_call('CoinGecko', symbol, False, 'Cripto não encontrada')
            return None
            
        except Exception as e:
            self.log_api_call('CoinGecko', symbol, False, str(e))
            return None
    
    def get_multiple_cryptos(self, symbols):
        """Busca múltiplas criptomoedas em uma chamada"""
        try:
            crypto_ids = [self.get_crypto_id(s) for s in symbols]
            ids_string = ','.join(crypto_ids)
            
            url = f"{self.BASE_URL}/simple/price"
            params = {
                'ids': ids_string,
                'vs_currencies': 'brl',
                'include_24hr_change': 'true',
                'include_market_cap': 'true'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = {}
            
            for symbol in symbols:
                crypto_id = self.get_crypto_id(symbol)
                if crypto_id in data:
                    results[symbol.upper()] = {
                        'symbol': symbol.upper(),
                        'name': crypto_id.title(),
                        'price': data[crypto_id].get('brl', 0),
                        'change_24h': data[crypto_id].get('brl_24h_change', 0),
                        'market_cap': data[crypto_id].get('brl_market_cap', 0),
                        'last_update': datetime.now().isoformat()
                    }
            
            return results
            
        except Exception as e:
            logging.error(f"❌ CoinGecko Multiple - Erro: {e}")
            return {}


class TesouroDirectoConnector(APIConnector):
    """Conector para Tesouro Direto"""
    
    BASE_URL = "https://www.tesourodireto.com.br/json/br/com/b3/tesourodireto/service/api/treasurybondsinfo.json"
    
    # Mapeamento de tipos de tesouro
    TESOURO_MAP = {
        'SELIC': 'Tesouro Selic',
        'PREFIXADO': 'Tesouro Prefixado',
        'IPCA': 'Tesouro IPCA+',
        'IPCA+': 'Tesouro IPCA+',
    }
    
    def get_tesouro_data(self, tipo_titulo, vencimento=None):
        """
        Busca dados do Tesouro Direto
        Args:
            tipo_titulo: SELIC, PREFIXADO, IPCA
            vencimento: ano de vencimento (opcional)
        Returns:
            dict com taxa, preço, vencimento
        """
        try:
            response = self.session.get(self.BASE_URL, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'response' in data and 'TrsrBdTradgList' in data['response']:
                bonds = data['response']['TrsrBdTradgList']
                
                tipo_busca = self.TESOURO_MAP.get(tipo_titulo.upper(), tipo_titulo)
                
                for bond in bonds:
                    nome_bond = bond.get('TrsrBd', {}).get('nm', '')
                    
                    if tipo_busca.lower() in nome_bond.lower():
                        if vencimento:
                            if str(vencimento) not in bond.get('TrsrBd', {}).get('mtrtyDt', ''):
                                continue
                        
                        tesouro_data = {
                            'name': nome_bond,
                            'tipo': tipo_titulo.upper(),
                            'price': bond.get('TrsrBd', {}).get('untrInvstmtVal', 0),
                            'taxa': bond.get('TrsrBd', {}).get('anulInvstmtRate', 0),
                            'vencimento': bond.get('TrsrBd', {}).get('mtrtyDt', ''),
                            'minimo_compra': bond.get('TrsrBd', {}).get('minInvstmtAmt', 0),
                            'last_update': datetime.now().isoformat()
                        }
                        
                        self.log_api_call('Tesouro Direto', tipo_titulo, True)
                        return tesouro_data
            
            self.log_api_call('Tesouro Direto', tipo_titulo, False, 'Título não encontrado')
            return None
            
        except Exception as e:
            self.log_api_call('Tesouro Direto', tipo_titulo, False, str(e))
            return None
    
    def get_all_bonds(self):
        """Retorna todos os títulos disponíveis"""
        try:
            response = self.session.get(self.BASE_URL, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            bonds_list = []
            
            if 'response' in data and 'TrsrBdTradgList' in data['response']:
                bonds = data['response']['TrsrBdTradgList']
                
                for bond in bonds:
                    bond_data = {
                        'name': bond.get('TrsrBd', {}).get('nm', ''),
                        'price': bond.get('TrsrBd', {}).get('untrInvstmtVal', 0),
                        'taxa': bond.get('TrsrBd', {}).get('anulInvstmtRate', 0),
                        'vencimento': bond.get('TrsrBd', {}).get('mtrtyDt', ''),
                        'minimo_compra': bond.get('TrsrBd', {}).get('minInvstmtAmt', 0),
                    }
                    bonds_list.append(bond_data)
                
                return bonds_list
            
            return []
            
        except Exception as e:
            logging.error(f"❌ Tesouro Direto - Erro ao buscar todos: {e}")
            return []


class Investidor10Connector(APIConnector):
    """Conector para Investidor10 - Dados fundamentalistas de ações B3"""
    
    BASE_URL = "https://investidor10.com.br/acoes"
    
    def __init__(self):
        super().__init__()
        # Headers específicos para o Investidor10
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://investidor10.com.br/',
        })
    
    def get_stock_data(self, ticker):
        """
        Busca dados fundamentalistas de uma ação ou FII
        Args:
            ticker: código da ação (ex: PETR4, VALE3) ou FII (ex: HGLG11, MXRF11)
        Returns:
            dict com price, P/L, Dividend Yield, ROE, etc
        """
        try:
            # Remover .SA se houver
            ticker = ticker.replace('.SA', '').upper()
            
            # Detectar se termina com 11 (pode ser FII ou unit)
            ends_with_11 = ticker.endswith('11')
            
            # Tentar primeiro como FII se termina com 11, depois como ação
            urls_to_try = []
            
            if ends_with_11:
                # Tentar FII primeiro, depois ação
                urls_to_try = [
                    (f"https://investidor10.com.br/fiis/{ticker.lower()}", "FII"),
                    (f"{self.BASE_URL}/{ticker.lower()}", "Unit/Ação")
                ]
            else:
                # Apenas ação
                urls_to_try = [
                    (f"{self.BASE_URL}/{ticker.lower()}", "Ação")
                ]
            
            response = None
            asset_type = None
            
            # Tentar cada URL até encontrar
            for url, type_name in urls_to_try:
                try:
                    print(f"🔍 Tentando {ticker} como {type_name} no Investidor10...")
                    response = self.session.get(url, timeout=10)
                    response.raise_for_status()
                    asset_type = type_name
                    print(f"✅ Encontrado como {type_name}")
                    break
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code in [404, 410]:
                        continue  # Tentar próxima URL
                    else:
                        raise  # Outro erro HTTP
            
            if not response or not response.ok:
                print(f"⚠️ {ticker} não encontrado no Investidor10")
                self.log_api_call('Investidor10', ticker, False, 'Não encontrado em nenhum endpoint')
                return None
            
            # Parse HTML com BeautifulSoup
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extrair dados da página
            stock_data = {
                'symbol': ticker,
                'name': None,
                'price': 0,
                'change_percent': 0,
                'asset_type': asset_type,  # 'FII' ou 'Ação'
                'dy': 0,  # Dividend Yield
                'pl': 0,  # P/L
                'pvp': 0,  # P/VP
                'roe': 0,  # ROE
                'roic': 0,  # ROIC
                'liq_corrente': 0,  # Liquidez Corrente
                'divida_liquida_ebitda': 0,
                'margem_liquida': 0,
                'last_update': datetime.now().isoformat()
            }
            
            # Nome da empresa (h2 com nome completo)
            name_tag = soup.find('h2')
            if name_tag:
                stock_data['name'] = name_tag.text.strip()
            else:
                # Fallback: pegar do title
                title_tag = soup.find('title')
                if title_tag:
                    stock_data['name'] = title_tag.text.split('-')[0].strip()
            
            # Preço atual - buscar pela classe 'value'
            price_tag = soup.find('span', class_='value')
            if price_tag:
                price_text = price_tag.text.strip().replace('R$', '').replace('.', '').replace(',', '.').strip()
                try:
                    stock_data['price'] = float(price_text)
                except:
                    pass
            
            # Variação percentual - buscar em cards com classe 'pl' (variação 12M)
            change_card = soup.find('div', class_='_card pl')
            if change_card:
                change_span = change_card.find('span', class_='_card-body')
                if change_span:
                    change_text = change_span.text.strip().replace('%', '').replace(',', '.').strip()
                    try:
                        stock_data['change_percent'] = float(change_text)
                    except:
                        pass
            
            # Indicadores fundamentalistas - buscar em todas as divs com classe '_card'
            cards = soup.find_all('div', class_='_card')
            
            for card in cards:
                # Pegar o título do card
                header = card.find('div', class_='_card-header')
                if not header:
                    continue
                
                title = header.text.strip().upper()
                
                # Pegar o valor do card
                body = card.find('span', class_='_card-body')
                if not body:
                    continue
                
                value_text = body.text.strip().replace('%', '').replace('R$', '').replace('.', '').replace(',', '.').strip()
                
                try:
                    value = float(value_text)
                    
                    # Mapear títulos para campos
                    if 'DY' in title or 'DIVIDEND' in title:
                        stock_data['dy'] = value
                    elif 'P/L' in title and 'EBITDA' not in title:
                        stock_data['pl'] = value
                    elif 'P/VP' in title or 'P / VP' in title:
                        stock_data['pvp'] = value
                    elif 'ROE' in title:
                        stock_data['roe'] = value
                    elif 'ROIC' in title:
                        stock_data['roic'] = value
                    elif 'LIQUIDEZ' in title and 'CORRENTE' in title:
                        stock_data['liq_corrente'] = value
                    elif 'EBITDA' in title and ('DIV' in title or 'DÍV' in title):
                        stock_data['divida_liquida_ebitda'] = value
                    elif 'MARGEM' in title and ('LÍQUIDA' in title or 'LIQUIDA' in title):
                        stock_data['margem_liquida'] = value
                except:
                    pass
            
            # Log de sucesso
            if stock_data['price'] > 0:
                print(f"✅ {ticker}: R$ {stock_data['price']:.2f} | DY: {stock_data['dy']:.2f}% | P/L: {stock_data['pl']:.2f}")
                self.log_api_call('Investidor10', ticker, True)
                return stock_data
            else:
                print(f"⚠️ {ticker}: Dados incompletos")
                self.log_api_call('Investidor10', ticker, False, 'Preço não encontrado')
                return None
            
        except requests.exceptions.HTTPError as e:
            # Erros 404/410 são esperados para ativos não listados
            if e.response.status_code in [404, 410]:
                print(f"⚠️ {ticker} não encontrado no Investidor10 (HTTP {e.response.status_code})")
            else:
                print(f"❌ Erro HTTP ao buscar {ticker} no Investidor10: {e}")
            self.log_api_call('Investidor10', ticker, False, str(e))
            return None
        except Exception as e:
            print(f"❌ Erro ao buscar {ticker} no Investidor10: {e}")
            self.log_api_call('Investidor10', ticker, False, str(e))
            return None
    
    def get_stock_fundamentals(self, ticker):
        """
        Busca APENAS dados fundamentalistas (sem preço)
        Útil para complementar dados do Yahoo Finance
        """
        data = self.get_stock_data(ticker)
        
        if not data:
            return None
        
        # Retornar apenas indicadores fundamentalistas
        return {
            'dy': data.get('dy', 0),
            'pl': data.get('pl', 0),
            'pvp': data.get('pvp', 0),
            'roe': data.get('roe', 0),
            'roic': data.get('roic', 0),
            'liq_corrente': data.get('liq_corrente', 0),
            'divida_liquida_ebitda': data.get('divida_liquida_ebitda', 0),
            'margem_liquida': data.get('margem_liquida', 0)
        }


# Factory para facilitar uso
class InvestmentAPIFactory:
    """Factory para criar conectores de API"""
    
    @staticmethod
    def get_connector(investment_type):
        """
        Retorna o conector apropriado para o tipo de investimento
        Args:
            investment_type: 'Ações', 'Criptomoedas', 'Tesouro Direto', etc
        """
        if investment_type in ['Ações', 'FII', 'ETF', 'ETFs']:
            return YahooFinanceConnector()
        elif investment_type in ['Criptomoedas', 'Crypto', 'Cripto']:
            return CoinGeckoConnector()
        elif investment_type in ['Tesouro Direto', 'Tesouro']:
            return TesouroDirectoConnector()
        else:
            return None
    
    @staticmethod
    def get_investment_data(investment_type, symbol):
        """
        Busca dados de um investimento
        Args:
            investment_type: tipo do investimento
            symbol: código/símbolo do ativo
        Returns:
            dict com dados atualizados ou None
        """
        connector = InvestmentAPIFactory.get_connector(investment_type)
        
        if not connector:
            return None
        
        if isinstance(connector, YahooFinanceConnector):
            return connector.get_stock_data(symbol)
        elif isinstance(connector, CoinGeckoConnector):
            return connector.get_crypto_data(symbol)
        elif isinstance(connector, TesouroDirectoConnector):
            return connector.get_tesouro_data(symbol)
        
        return None
    
    @staticmethod
    def get_stock_with_fundamentals(symbol):
        """
        Busca dados de ação com múltiplos fallbacks
        Prioridade: Investidor10 → Status Invest → Yahoo Finance
        Args:
            symbol: código da ação (ex: PETR4)
        Returns:
            dict com price e dados da ação
        """
        # 1ª tentativa: Investidor10 (mais completo - dados fundamentalistas)
        inv10 = Investidor10Connector()
        data = inv10.get_stock_data(symbol)
        
        if data and data.get('price', 0) > 0:
            print(f"✅ Fonte: Investidor10")
            return data
        
        # 2ª tentativa: Status Invest (brasileiro, confiável)
        print(f"⚠️ Investidor10 falhou, tentando Status Invest...")
        status = StatusInvestConnector()
        status_data = status.get_stock_data(symbol)
        
        if status_data and status_data.get('price', 0) > 0:
            print(f"✅ Fonte: Status Invest")
            return status_data
        
        # 3ª tentativa: Yahoo Finance (fallback final)
        # BRAPI DESATIVADA - estava retornando 401 Unauthorized
        print(f"⚠️ Status Invest falhou, tentando Yahoo Finance...")
        yahoo = YahooFinanceConnector()
        yahoo_data = yahoo.get_stock_data(symbol)
        
        if yahoo_data and yahoo_data.get('price', 0) > 0:
            # Tentar buscar apenas fundamentalistas do Investidor10 para complementar
            fundamentals = inv10.get_stock_fundamentals(symbol)
            
            if fundamentals:
                # Mesclar dados: preço do Yahoo + fundamentalistas do Investidor10
                yahoo_data.update(fundamentals)
            
            print(f"✅ Fonte: Yahoo Finance")
            return yahoo_data
        
        # 4ª tentativa: Se for FII, tentar com variações do ticker no Yahoo
        if symbol.upper().endswith('11'):
            print(f"⚠️ Tentando variações para FII {symbol}...")
            
            # Tentar com diferentes sufixos
            variations = [
                f"{symbol}B.SA",  # Alguns FIIs têm sufixo B
                f"{symbol}F.SA",  # Alguns FIIs têm sufixo F
            ]
            
            for variation in variations:
                print(f"   Tentando: {variation}")
                yahoo_data = yahoo.get_stock_data(variation.replace('.SA', ''))
                if yahoo_data and yahoo_data.get('price', 0) > 0:
                    print(f"✅ Fonte: Yahoo Finance ({variation})")
                    return yahoo_data
        
        print(f"❌ Todas as fontes falharam para {symbol}")
        return None
