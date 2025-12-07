# Dockerfile - BWS Finance Backend
FROM python:3.11-slim

# Informações
LABEL maintainer="Brayan <brayan@bws.com>"
LABEL description="BWS Finance - Sistema Financeiro Pessoal"
LABEL version="2.0"

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    tesseract-ocr \
    tesseract-ocr-por \
    git \
    curl \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Diretório de trabalho
WORKDIR /app

# Copiar requirements primeiro (cache Docker)
COPY requirements.txt ./
RUN test -f requirements_whatsapp.txt && cp requirements_whatsapp.txt . || true

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt
RUN test -f requirements_whatsapp.txt && pip install --no-cache-dir -r requirements_whatsapp.txt || true

# Instalar Spacy português (se necessário)
RUN pip list | grep -q spacy && python -m spacy download pt_core_news_sm || true

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p logs temp tokens static/uploads

# Variáveis de ambiente
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expor porta
EXPOSE 5000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Comando de inicialização com gunicorn (produção)
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "info"]
