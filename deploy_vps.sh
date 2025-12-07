#!/bin/bash

# ========================================
# 🚀 INSTALADOR AUTOMÁTICO NIK0 FINANCE
# ========================================
# Execute este script na VPS Ubuntu 22.04
# Comando: bash deploy_vps.sh

set -e  # Para se houver erro

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║        🚀 NIK0 FINANCE - INSTALAÇÃO AUTOMÁTICA           ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# ========================================
# 1. ATUALIZAR SISTEMA
# ========================================
echo "📦 [1/10] Atualizando sistema..."
apt update -y
apt upgrade -y
echo "✅ Sistema atualizado!"
echo ""

# ========================================
# 2. INSTALAR PYTHON 3.11
# ========================================
echo "🐍 [2/10] Instalando Python 3.11..."
apt install -y software-properties-common
add-apt-repository -y ppa:deadsnakes/ppa
apt update -y
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
echo "✅ Python 3.11 instalado!"
python3 --version
echo ""

# ========================================
# 3. INSTALAR NODE.JS 22
# ========================================
echo "📗 [3/10] Instalando Node.js 22..."
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt install -y nodejs
echo "✅ Node.js instalado!"
node --version
npm --version
echo ""

# ========================================
# 4. INSTALAR DEPENDÊNCIAS DO SISTEMA
# ========================================
echo "🔧 [4/10] Instalando dependências (Tesseract, FFmpeg, etc)..."
apt install -y \
    tesseract-ocr \
    tesseract-ocr-por \
    ffmpeg \
    git \
    curl \
    wget \
    nano \
    htop \
    nginx \
    certbot \
    python3-certbot-nginx
echo "✅ Dependências instaladas!"
echo ""

# ========================================
# 5. CRIAR DIRETÓRIO DO PROJETO
# ========================================
echo "📁 [5/10] Criando diretório do projeto..."
mkdir -p /app/nik0finance
cd /app/nik0finance
echo "✅ Diretório criado: /app/nik0finance"
echo ""

# ========================================
# 6. CLONAR/COPIAR PROJETO
# ========================================
echo "📥 [6/10] Preparando para upload do projeto..."
echo ""
echo "⚠️  ATENÇÃO: Agora você precisa fazer upload dos arquivos!"
echo ""
echo "Opção A - Via SCP (do seu PC Windows):"
echo "  scp -r C:\\App\\nik0finance-base\\* root@SEU_IP_VPS:/app/nik0finance/"
echo ""
echo "Opção B - Via Git:"
echo "  cd /app/nik0finance"
echo "  git clone https://github.com/SEU_USUARIO/nik0finance.git ."
echo ""
echo "Opção C - Via FTP (FileZilla):"
echo "  Host: SEU_IP_VPS"
echo "  User: root"
echo "  Upload tudo para: /app/nik0finance/"
echo ""
read -p "Pressione ENTER depois de fazer upload dos arquivos..."
echo ""

# ========================================
# 7. INSTALAR DEPENDÊNCIAS PYTHON
# ========================================
echo "📦 [7/10] Instalando dependências Python..."
cd /app/nik0finance
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt || pip install Flask ofxparse PyPDF2 pytesseract python-dateutil requests schedule
echo "✅ Dependências Python instaladas!"
echo ""

# ========================================
# 8. INSTALAR DEPENDÊNCIAS NODE.JS
# ========================================
echo "📦 [8/10] Instalando dependências Node.js..."
if [ -d "whatsapp_server" ]; then
    cd /app/nik0finance/whatsapp_server
    npm install
    echo "✅ Dependências Node.js instaladas!"
else
    echo "⚠️  Pasta whatsapp_server não encontrada, pulando..."
fi
echo ""

# ========================================
# 9. CONFIGURAR NGINX
# ========================================
echo "🌐 [9/10] Configurando Nginx..."
cat > /etc/nginx/sites-available/nik0finance << 'EOF'
server {
    listen 80;
    server_name _;

    # Flask Backend
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket para WhatsApp
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts maiores para uploads
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        client_max_body_size 50M;
    }

    # WhatsApp Server
    location /whatsapp/ {
        proxy_pass http://127.0.0.1:3000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # Static files
    location /static/ {
        alias /app/nik0finance/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

ln -sf /etc/nginx/sites-available/nik0finance /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx
echo "✅ Nginx configurado!"
echo ""

# ========================================
# 10. CRIAR SERVIÇOS SYSTEMD
# ========================================
echo "⚙️  [10/10] Criando serviços systemd..."

# Serviço Flask
cat > /etc/systemd/system/nik0finance.service << EOF
[Unit]
Description=Nik0 Finance Flask App
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/app/nik0finance
Environment="PATH=/app/nik0finance/venv/bin"
ExecStart=/app/nik0finance/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Serviço WhatsApp (se existir)
if [ -d "/app/nik0finance/whatsapp_server" ]; then
    cat > /etc/systemd/system/nik0finance-whatsapp.service << EOF
[Unit]
Description=Nik0 Finance WhatsApp Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/app/nik0finance/whatsapp_server
ExecStart=/usr/bin/node index_v3.js
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
fi

systemctl daemon-reload
systemctl enable nik0finance
systemctl start nik0finance

if [ -d "/app/nik0finance/whatsapp_server" ]; then
    systemctl enable nik0finance-whatsapp
    systemctl start nik0finance-whatsapp
fi

echo "✅ Serviços criados e iniciados!"
echo ""

# ========================================
# FINALIZAÇÃO
# ========================================
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║              ✅ INSTALAÇÃO CONCLUÍDA!                     ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Acesse agora: http://$(curl -s ifconfig.me)"
echo ""
echo "📊 Status dos serviços:"
systemctl status nik0finance --no-pager | grep Active
if [ -d "/app/nik0finance/whatsapp_server" ]; then
    systemctl status nik0finance-whatsapp --no-pager | grep Active
fi
echo ""
echo "🔧 Comandos úteis:"
echo "  • Ver logs Flask:     journalctl -u nik0finance -f"
echo "  • Ver logs WhatsApp:  journalctl -u nik0finance-whatsapp -f"
echo "  • Reiniciar Flask:    systemctl restart nik0finance"
echo "  • Parar tudo:         systemctl stop nik0finance nik0finance-whatsapp"
echo ""
echo "🔒 Para ativar HTTPS (depois de configurar domínio):"
echo "  certbot --nginx -d seudominio.com"
echo ""
echo "📱 Não esqueça de configurar o IP no app mobile!"
echo "  Edite: services/api.js"
echo "  const API_BASE_URL = 'http://$(curl -s ifconfig.me)';"
echo ""
