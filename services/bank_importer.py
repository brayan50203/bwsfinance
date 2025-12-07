"""
Módulo de Importação de Extratos Bancários - BWS Finance
Suporta: OFX, CSV, PDF e APIs bancárias
"""

import csv
import re
import io
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import xml.etree.ElementTree as ET

# Bibliotecas para PDF (instalar: pip install PyMuPDF pypdf2)
try:
    import fitz  # PyMuPDF
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

try:
    from PyPDF2 import PdfReader
    PYPDF2_SUPPORT = True
except ImportError:
    PYPDF2_SUPPORT = False


class BankStatementImporter:
    """Classe principal para importação de extratos bancários"""
    
    def __init__(self, user_id: str, tenant_id: str):
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.transactions = []
        self.errors = []
        self.stats = {
            'total': 0,
            'imported': 0,
            'duplicated': 0,
            'errors': 0
        }
    
    def parse_ofx(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse arquivo OFX (Open Financial Exchange)
        Formato padrão usado por bancos brasileiros
        """
        transactions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Remover header SGML se existir
            if 'OFXHEADER' in content:
                content = content.split('<OFX>')[1]
                content = '<OFX>' + content
            
            # Parse XML
            root = ET.fromstring(content)
            
            # Encontrar transações
            for stmttrn in root.findall('.//STMTTRN'):
                transaction = {}
                
                # Tipo de transação
                trntype = stmttrn.find('TRNTYPE')
                transaction['type'] = 'Receita' if trntype is not None and trntype.text in ['CREDIT', 'DEP'] else 'Despesa'
                
                # Data
                dtposted = stmttrn.find('DTPOSTED')
                if dtposted is not None:
                    date_str = dtposted.text[:8]  # YYYYMMDD
                    transaction['date'] = datetime.strptime(date_str, '%Y%m%d').strftime('%Y-%m-%d')
                
                # Valor
                trnamt = stmttrn.find('TRNAMT')
                if trnamt is not None:
                    amount = float(trnamt.text)
                    transaction['value'] = abs(amount)
                    if amount < 0:
                        transaction['type'] = 'Despesa'
                
                # Descrição
                memo = stmttrn.find('MEMO')
                if memo is not None:
                    transaction['description'] = memo.text.strip()
                else:
                    transaction['description'] = 'Transação importada'
                
                # ID único (FITID)
                fitid = stmttrn.find('FITID')
                if fitid is not None:
                    transaction['external_id'] = fitid.text
                
                transactions.append(transaction)
            
            self.stats['total'] = len(transactions)
            return transactions
            
        except Exception as e:
            self.errors.append(f"Erro ao processar OFX: {str(e)}")
            return []
    
    def parse_csv(self, file_path: str, delimiter: str = ',') -> List[Dict[str, Any]]:
        """
        Parse arquivo CSV
        Tenta detectar automaticamente as colunas: data, descrição, valor
        """
        transactions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Detectar delimitador
                sample = f.read(1024)
                f.seek(0)
                
                if sample.count(';') > sample.count(','):
                    delimiter = ';'
                
                reader = csv.DictReader(f, delimiter=delimiter)
                
                for row in reader:
                    transaction = self._parse_csv_row(row)
                    if transaction:
                        transactions.append(transaction)
            
            self.stats['total'] = len(transactions)
            return transactions
            
        except Exception as e:
            self.errors.append(f"Erro ao processar CSV: {str(e)}")
            return []
    
    def _parse_csv_row(self, row: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Interpreta uma linha do CSV e converte para transação"""
        transaction = {}
        
        # Mapear colunas comuns (case-insensitive)
        row_lower = {k.lower().strip(): v for k, v in row.items()}
        
        # DEBUG: Mostrar colunas disponíveis e valores da primeira linha
        if not hasattr(self, '_columns_logged'):
            print(f"\n{'='*60}")
            print(f"📋 DEBUG CSV - Colunas detectadas:")
            print(f"{'='*60}")
            for col_name, col_value in row_lower.items():
                print(f"  '{col_name}' = '{col_value}'")
            print(f"{'='*60}\n")
            self._columns_logged = True
        
        # Data - busca exata primeiro, depois parcial
        date_keys = ['data', 'date', 'dt', 'datetime', 'data lancamento', 'data lançamento', 
                     'data transacao', 'data transação', 'data movimento']
        for key in date_keys:
            if key in row_lower:
                date_str = row_lower[key]
                transaction['date'] = self._parse_date(date_str)
                break
        
        # Se não encontrou, busca parcial (qualquer coluna que contenha "data" ou "date")
        if 'date' not in transaction:
            for key in row_lower.keys():
                if 'data' in key or 'date' in key:
                    date_str = row_lower[key]
                    transaction['date'] = self._parse_date(date_str)
                    print(f"✓ Data encontrada na coluna: '{key}'")
                    break
        
        # Descrição
        desc_keys = ['descricao', 'descrição', 'description', 'historico', 'histórico', 'memo',
                     'descricão', 'histórico completo', 'lançamento', 'lancamento']
        for key in desc_keys:
            if key in row_lower:
                transaction['description'] = row_lower[key].strip()
                break
        
        # Se não encontrou, busca parcial
        if 'description' not in transaction:
            for key in row_lower.keys():
                if any(word in key for word in ['descri', 'histor', 'memo', 'lanc']):
                    transaction['description'] = row_lower[key].strip()
                    print(f"✓ Descrição encontrada na coluna: '{key}'")
                    break
        
        # Valor
        value_keys = ['valor', 'value', 'amount', 'vlr', 'quantia', 'valor lancamento',
                      'valor lançamento', 'vl lancamento', 'vl lançamento']
        for key in value_keys:
            if key in row_lower:
                value_str = row_lower[key]
                transaction['value'] = self._parse_currency(value_str)
                break
        
        # Se não encontrou, busca parcial
        if 'value' not in transaction:
            for key in row_lower.keys():
                if any(word in key for word in ['valor', 'value', 'vlr', 'amount', 'quantia']):
                    value_str = row_lower[key]
                    transaction['value'] = self._parse_currency(value_str)
                    print(f"✓ Valor encontrado na coluna: '{key}'")
                    break
        
        # Tipo (crédito/débito)
        type_keys = ['tipo', 'type', 'operacao', 'operação']
        transaction['type'] = 'Despesa'  # Padrão
        
        for key in type_keys:
            if key in row_lower:
                type_val = row_lower[key].lower()
                if 'credito' in type_val or 'credit' in type_val or 'entrada' in type_val:
                    transaction['type'] = 'Receita'
                break
        
        # Verificar se valor é negativo (indica despesa)
        if 'value' in transaction and transaction['value'] < 0:
            transaction['value'] = abs(transaction['value'])
            transaction['type'] = 'Despesa'
        
        # Validar campos obrigatórios
        if 'date' in transaction and 'value' in transaction and 'description' in transaction:
            return transaction
        
        # DEBUG: Mostrar por que a linha foi rejeitada
        if not hasattr(self, '_rejection_logged'):
            missing = []
            if 'date' not in transaction:
                missing.append('data')
            if 'value' not in transaction:
                missing.append('valor')
            if 'description' not in transaction:
                missing.append('descrição')
            print(f"⚠️  Linha rejeitada - Campos faltando: {', '.join(missing)}")
            self._rejection_logged = True
        
        return None
    
    def parse_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse arquivo PDF de extrato bancário
        Usa expressões regulares para extrair dados
        """
        if not PDF_SUPPORT and not PYPDF2_SUPPORT:
            self.errors.append("Suporte a PDF não instalado. Execute: pip install PyMuPDF pypdf2")
            return []
        
        transactions = []
        text = ""
        
        try:
            # Tentar com PyMuPDF primeiro (melhor para extratos)
            if PDF_SUPPORT:
                doc = fitz.open(file_path)
                for page in doc:
                    text += page.get_text()
                doc.close()
            
            # Fallback para PyPDF2
            elif PYPDF2_SUPPORT:
                reader = PdfReader(file_path)
                for page in reader.pages:
                    text += page.extract_text()
            
            # Detectar padrões de transações
            # Formato comum: DD/MM/YYYY DESCRICAO R$ 1.234,56
            pattern = r'(\d{2}/\d{2}/\d{4})\s+(.+?)\s+R?\$?\s*([\d.,]+)'
            matches = re.findall(pattern, text, re.MULTILINE)
            
            for match in matches:
                date_str, description, value_str = match
                
                try:
                    transaction = {
                        'date': self._parse_date(date_str),
                        'description': description.strip()[:100],
                        'value': self._parse_currency(value_str),
                        'type': 'Despesa'  # Padrão, pode ser refinado
                    }
                    
                    # Detectar se é receita por palavras-chave
                    desc_lower = description.lower()
                    if any(word in desc_lower for word in ['credito', 'deposito', 'salario', 'pix recebido', 'transferencia recebida']):
                        transaction['type'] = 'Receita'
                    
                    transactions.append(transaction)
                except:
                    continue
            
            self.stats['total'] = len(transactions)
            return transactions
            
        except Exception as e:
            self.errors.append(f"Erro ao processar PDF: {str(e)}")
            return []
    
    def _parse_date(self, date_str: str) -> str:
        """Converte string de data para formato YYYY-MM-DD"""
        date_str = date_str.strip()
        
        # Formatos comuns brasileiros
        formats = [
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%Y-%m-%d',
            '%d/%m/%y',
            '%Y%m%d'
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except:
                continue
        
        # Fallback: hoje
        return datetime.now().strftime('%Y-%m-%d')
    
    def _parse_currency(self, value_str: str) -> float:
        """Converte string de valor para float"""
        # Remove símbolos e espaços
        value_str = value_str.replace('R$', '').replace('$', '').strip()
        
        # Formato brasileiro: 1.234,56 -> 1234.56
        if ',' in value_str and '.' in value_str:
            value_str = value_str.replace('.', '').replace(',', '.')
        elif ',' in value_str:
            value_str = value_str.replace(',', '.')
        
        try:
            return abs(float(value_str))
        except:
            return 0.0
    
    def import_transactions(self, transactions: List[Dict[str, Any]], account_id: str, db_connection, auto_categorize: bool = True):
        """
        Importa transações para o banco de dados
        
        Args:
            transactions: Lista de transações a importar
            account_id: ID da conta bancária destino (ou None para cartões)
            db_connection: Conexão com banco de dados
            auto_categorize: Se True, tenta categorizar automaticamente
        """
        # Comentado temporariamente - usar AIChat se necessário
        # from services.ai_chat import FinancialChatProcessor
        
        # Detectar se é import de cartão (transações têm card_id)
        is_card_import = transactions and 'card_id' in transactions[0]
        card_id = transactions[0].get('card_id') if is_card_import else None
        
        print(f"\n💾 INICIANDO IMPORTAÇÃO:")
        print(f"  Total de transações: {len(transactions)}")
        print(f"  Account ID: {account_id}")
        print(f"  Card ID: {card_id}")
        print(f"  Auto-categorizar: {auto_categorize}")
        
        imported = 0
        duplicated = 0
        errors = 0
        
        for idx, trans in enumerate(transactions, 1):
            try:
                print(f"\n  📝 Transação {idx}/{len(transactions)}:")
                print(f"     {trans['date']} - {trans['description']}: R$ {trans['value']}")
                
                # Extrair card_id da transação (se houver)
                trans_card_id = trans.get('card_id')
                trans_account_id = account_id if not trans_card_id else None
                
                # Verificar duplicatas
                if trans_card_id:
                    # Duplicata por card_id
                    existing = db_connection.execute("""
                        SELECT id FROM transactions 
                        WHERE user_id = ? AND card_id = ? 
                        AND date = ? AND value = ? AND description = ?
                    """, (self.user_id, trans_card_id, trans['date'], trans['value'], trans['description'])).fetchone()
                else:
                    # Duplicata por account_id
                    existing = db_connection.execute("""
                        SELECT id FROM transactions 
                        WHERE user_id = ? AND account_id = ? 
                        AND date = ? AND value = ? AND description = ?
                    """, (self.user_id, trans_account_id, trans['date'], trans['value'], trans['description'])).fetchone()
                
                if existing:
                    duplicated += 1
                    print(f"     ⚠️ DUPLICADA (já existe: {existing[0]})")
                    continue
                
                # Categorizar automaticamente
                category_id = None
                if auto_categorize:
                    category_id = self._auto_categorize(trans['description'], trans['type'], db_connection)
                    if category_id:
                        print(f"     ✅ Categoria: {category_id}")
                    else:
                        print(f"     ⚠️ Sem categoria automática")
                
                # Obter payment_method da transação ou usar padrão
                payment_method = trans.get('payment_method', 'credit_card' if trans_card_id else 'debito')
                
                # Inserir transação
                transaction_id = str(uuid.uuid4())
                db_connection.execute("""
                    INSERT INTO transactions (
                        id, user_id, tenant_id, account_id, card_id, category_id, 
                        type, description, value, date, status, 
                        is_fixed, payment_method, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    transaction_id, self.user_id, self.tenant_id, trans_account_id, trans_card_id, category_id,
                    trans['type'], trans['description'], trans['value'], trans['date'], 'Pago',
                    0, payment_method
                ))
                
                imported += 1
                print(f"     ✅ IMPORTADA (ID: {transaction_id[:8]}...)")
                
            except Exception as e:
                errors += 1
                print(f"     ❌ ERRO: {str(e)}")
                self.errors.append(f"Erro ao importar '{trans.get('description', 'N/A')}': {str(e)}")
        
        db_connection.commit()
        
        # Atualizar estatísticas
        self.stats['imported'] = imported
        self.stats['duplicated'] = duplicated
        self.stats['errors'] = errors
        
        print(f"\n📊 RESULTADO DA IMPORTAÇÃO:")
        print(f"  ✅ Importadas: {imported}")
        print(f"  ⚠️  Duplicadas: {duplicated}")
        print(f"  ❌ Erros: {errors}")
        print(f"  📋 Total processado: {len(transactions)}\n")
        
        return {
            'success': True,
            'imported': imported,
            'duplicated': duplicated,
            'errors': errors,
            'total': len(transactions)
        }
    
    def _auto_categorize(self, description: str, trans_type: str, db_connection) -> Optional[str]:
        """Categoriza transação automaticamente baseado em palavras-chave"""
        desc_lower = description.lower()
        
        # Mapeamento de palavras-chave para categorias
        keywords_map = {
            'Receita': {
                'salario': ['salario', 'salário', 'vencimento', 'remuneracao'],
                'freelance': ['freelance', 'freela', 'projeto'],
                'investimento': ['dividendo', 'rendimento', 'juros'],
            },
            'Despesa': {
                'alimentacao': ['mercado', 'supermercado', 'ifood', 'restaurante', 'padaria', 'lanche'],
                'transporte': ['uber', '99', 'taxi', 'combustivel', 'gasolina', 'posto'],
                'saude': ['farmacia', 'hospital', 'clinica', 'medico', 'consulta'],
                'educacao': ['faculdade', 'curso', 'escola', 'livro'],
                'lazer': ['cinema', 'netflix', 'spotify', 'jogo'],
            }
        }
        
        # Buscar categoria correspondente
        if trans_type in keywords_map:
            for category_name, keywords in keywords_map[trans_type].items():
                if any(keyword in desc_lower for keyword in keywords):
                    # Buscar ID da categoria no banco
                    category = db_connection.execute("""
                        SELECT id FROM categories 
                        WHERE tenant_id = ? AND type = ? AND LOWER(name) LIKE ?
                    """, (self.tenant_id, trans_type, f'%{category_name}%')).fetchone()
                    
                    if category:
                        return category['id']
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da importação"""
        return {
            'stats': self.stats,
            'errors': self.errors
        }


def detect_file_type(filename: str) -> str:
    """Detecta o tipo de arquivo pelo nome"""
    filename_lower = filename.lower()
    
    if filename_lower.endswith('.ofx'):
        return 'ofx'
    elif filename_lower.endswith('.csv'):
        return 'csv'
    elif filename_lower.endswith('.pdf'):
        return 'pdf'
    elif filename_lower.endswith('.json'):
        return 'json'
    else:
        return 'unknown'
