"""
PDF Processor - Extrai transações de extratos bancários em PDF
"""
import logging
import pdfplumber
import re
from typing import List, Dict

logger = logging.getLogger(__name__)

class PDFProcessor:
    def extract_text(self, pdf_path: str) -> str:
        """Extrai texto completo do PDF"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = '\n'.join([page.extract_text() for page in pdf.pages])
            logger.info(f"✅ PDF extraído: {len(text)} caracteres")
            return text
        except Exception as e:
            logger.error(f"❌ Erro ao ler PDF: {e}")
            return ""
    
    def parse_bank_statement(self, text: str) -> List[Dict]:
        """Parseia extrato bancário e retorna lista de transações"""
        transactions = []
        
        # Padrão: DATA DESCRIÇÃO VALOR
        pattern = r'(\d{2}/\d{2})\s+(.+?)\s+([-]?[\d.,]+)'
        
        for match in re.finditer(pattern, text):
            date = match.group(1)
            description = match.group(2).strip()
            value = float(match.group(3).replace('.', '').replace(',', '.'))
            
            transactions.append({
                'date': date,
                'description': description,
                'value': abs(value),
                'type': 'Despesa' if value < 0 else 'Receita'
            })
        
        logger.info(f"✅ {len(transactions)} transações encontradas")
        return transactions
    
    def process_pdf(self, pdf_path: str, delete_after=True) -> List[Dict]:
        """Pipeline completo"""
        import os
        
        text = self.extract_text(pdf_path)
        transactions = self.parse_bank_statement(text)
        
        if delete_after and os.path.exists(pdf_path):
            os.remove(pdf_path)
            logger.info("🗑️ PDF removido")
        
        return transactions
