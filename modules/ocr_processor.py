"""
OCR Processor Module
Extrai texto de imagens usando Tesseract OCR

Features:
- Processa imagens (JPG, PNG, etc)
- Usa Tesseract OCR (local e gratuito)
- Pré-processamento de imagem para melhor qualidade
- Retorna texto extraído
"""

import os
import logging
from typing import Optional
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract

# Configurar logging
logger = logging.getLogger(__name__)

class OCRProcessor:
    def __init__(self, language='por', tesseract_cmd=None):
        """
        Inicializa o processador OCR
        
        Args:
            language: Idioma do Tesseract (por, eng, etc)
            tesseract_cmd: Caminho do executável do Tesseract (opcional)
        """
        self.language = language
        
        # Configurar caminho do Tesseract se fornecido
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
        # Testar se Tesseract está instalado
        try:
            version = pytesseract.get_tesseract_version()
            logger.info(f"✅ Tesseract {version} detectado")
        except Exception as e:
            logger.error(f"❌ Tesseract não encontrado: {e}")
            logger.info("📥 Instale com: sudo apt install tesseract-ocr tesseract-ocr-por")
    
    def preprocess_image(self, image_path: str) -> Optional[Image.Image]:
        """
        Pré-processa imagem para melhorar OCR
        
        Args:
            image_path: Caminho da imagem
            
        Returns:
            Objeto PIL Image processado
        """
        try:
            # Abrir imagem
            img = Image.open(image_path)
            
            # Converter para escala de cinza
            img = img.convert('L')
            
            # Aumentar contraste
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)
            
            # Aumentar nitidez
            img = img.filter(ImageFilter.SHARPEN)
            
            # Binarização (thresholding)
            threshold = 150
            img = img.point(lambda p: p > threshold and 255)
            
            logger.info("✅ Imagem pré-processada")
            return img
            
        except Exception as e:
            logger.error(f"❌ Erro ao pré-processar imagem: {e}")
            return None
    
    def extract_text(self, image_path: str, preprocess: bool = True) -> Optional[str]:
        """
        Extrai texto de imagem usando OCR
        
        Args:
            image_path: Caminho da imagem
            preprocess: Se True, aplica pré-processamento
            
        Returns:
            Texto extraído ou None
        """
        logger.info(f"🖼️ Extraindo texto de: {image_path}")
        
        try:
            # Pré-processar se solicitado
            if preprocess:
                img = self.preprocess_image(image_path)
                if img is None:
                    # Fallback: tentar sem pré-processamento
                    img = Image.open(image_path)
            else:
                img = Image.open(image_path)
            
            # Configuração do Tesseract
            custom_config = r'--oem 3 --psm 6'
            # OEM 3: Default, based on what is available
            # PSM 6: Assume a single uniform block of text
            
            # Executar OCR
            text = pytesseract.image_to_string(
                img,
                lang=self.language,
                config=custom_config
            )
            
            # Limpar texto
            text = text.strip()
            
            if text:
                logger.info(f"✅ Texto extraído: {len(text)} caracteres")
                logger.debug(f"   Preview: {text[:200]}...")
                return text
            else:
                logger.warning("⚠️ Nenhum texto encontrado na imagem")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro no OCR: {e}")
            return None
    
    def extract_structured_data(self, image_path: str) -> dict:
        """
        Extrai dados estruturados de nota fiscal/comprovante
        
        Args:
            image_path: Caminho da imagem
            
        Returns:
            Dicionário com dados extraídos
        """
        text = self.extract_text(image_path)
        
        if not text:
            return {
                'success': False,
                'text': None,
                'data': {}
            }
        
        # Tentar extrair informações comuns
        import re
        
        data = {}
        
        # Valor total
        valor_patterns = [
            r'(?:total|valor|R\$)\s*:?\s*R?\$?\s*([\d.,]+)',
            r'R\$\s*([\d.,]+)',
            r'([\d]+[.,][\d]{2})\s*(?:reais|BRL)?'
        ]
        
        for pattern in valor_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data['valor'] = match.group(1).replace('.', '').replace(',', '.')
                break
        
        # Data
        data_patterns = [
            r'(\d{2}[/-]\d{2}[/-]\d{4})',
            r'(\d{2}[/-]\d{2}[/-]\d{2})'
        ]
        
        for pattern in data_patterns:
            match = re.search(pattern, text)
            if match:
                data['data'] = match.group(1)
                break
        
        # CPF/CNPJ
        cpf_pattern = r'\d{3}\.\d{3}\.\d{3}-\d{2}'
        cnpj_pattern = r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}'
        
        cpf_match = re.search(cpf_pattern, text)
        cnpj_match = re.search(cnpj_pattern, text)
        
        if cnpj_match:
            data['cnpj'] = cnpj_match.group(0)
        elif cpf_match:
            data['cpf'] = cpf_match.group(0)
        
        return {
            'success': True,
            'text': text,
            'data': data
        }
    
    def process_image(self, image_path: str, delete_after: bool = True) -> Optional[str]:
        """
        Pipeline completo: extrai texto de imagem
        
        Args:
            image_path: Caminho da imagem
            delete_after: Se True, apaga imagem após processamento
            
        Returns:
            Texto extraído ou None
        """
        result = self.extract_structured_data(image_path)
        
        # Cleanup
        if delete_after:
            try:
                if os.path.exists(image_path):
                    os.remove(image_path)
                    logger.info("🗑️ Imagem removida")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao remover imagem: {e}")
        
        return result.get('text')

# =========================================
# Uso Standalone
# =========================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    processor = OCRProcessor(language='por')
    
    # Teste
    test_image = "temp/test_image.jpg"
    if os.path.exists(test_image):
        result = processor.extract_structured_data(test_image)
        print(f"\n📝 Resultado:")
        print(f"   Sucesso: {result['success']}")
        print(f"   Dados: {result['data']}")
        print(f"   Texto: {result['text'][:200]}...")
    else:
        print(f"❌ Imagem de teste não encontrada: {test_image}")
