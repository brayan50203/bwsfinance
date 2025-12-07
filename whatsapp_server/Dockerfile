# Usar Node 22 Alpine (mais leve)
FROM node:22-alpine

# Informações
LABEL maintainer="Brayan <brayan@bws.com>"
LABEL description="BWS Finance - WhatsApp Bot"

# Instalar dependências necessárias
RUN apk add --no-cache \
    chromium \
    nss \
    freetype \
    harfbuzz \
    ca-certificates \
    ttf-freefont \
    python3 \
    make \
    g++

# Definir Chromium como executável do Puppeteer
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true

# Definir diretório de trabalho
WORKDIR /app

# Copiar package.json
COPY package*.json ./

# Instalar dependências
RUN npm install --production

# Copiar código
COPY . .

# Criar diretório de tokens
RUN mkdir -p tokens

# Expor porta
EXPOSE 3000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/health', (res) => process.exit(res.statusCode === 200 ? 0 : 1))"

# Comando de inicialização
CMD ["node", "index_v3.js"]
