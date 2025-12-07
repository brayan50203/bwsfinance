#!/bin/bash
# ========================================
# 🚀 INSTALADOR ULTRA-AUTOMÁTICO NIK0 FINANCE
# Copie e cole TUDO no terminal SSH da VPS
# ========================================

set -e
echo "🚀 Iniciando instalação automática..."

# Atualizar sistema
echo "📦 Atualizando sistema..."
apt update -y && apt upgrade -y

# Instalar Python 3.11
echo "🐍 Instalando Python 3.11..."
apt install -y software-properties-common
add-apt-repository -y ppa:deadsnakes/ppa
apt update -y
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Instalar Node.js 22
echo "📗 Instalando Node.js 22..."
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt install -y nodejs

# Instalar dependências
echo "🔧 Instalando dependências..."
apt install -y tesseract-ocr tesseract-ocr-por ffmpeg git curl wget nano htop nginx certbot python3-certbot-nginx unzip

# Criar diretório
mkdir -p /app/nik0finance
cd /app/nik0finance

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║     ⚠️  ENVIE OS ARQUIVOS AGORA                           ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "No seu PC Windows, execute:"
echo ""
echo "scp -r C:\\App\\nik0finance-base\\* root@$(curl -s ifconfig.me):/app/nik0finance/"
echo ""
echo "Ou use FileZilla:"
echo "  Host: $(curl -s ifconfig.me)"
echo "  User: root"
echo "  Pasta remota: /app/nik0finance/"
echo ""
read -p "Pressione ENTER após enviar os arquivos..."

# Instalar dependências Python
echo "📦 Instalando dependências Python..."
cd /app/nik0finance
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# Criar requirements.txt se não existir
if [ ! -f "requirements.txt" ]; then
    cat > requirements.txt << 'EOF'
Flask==2.3.2
ofxparse==0.21
PyPDF2==3.0.1
pytesseract==0.3.10
python-dateutil==2.8.2
requests==2.31.0
schedule==1.2.0
Werkzeug==2.3.6
openai==1.3.5
EOF
fi

pip install -r requirements.txt

# Instalar dependências Node.js
if [ -d "whatsapp_server" ]; then
    echo "📦 Instalando dependências WhatsApp..."
    cd whatsapp_server
    npm install
    cd ..
fi

# Configurar Nginx
echo "🌐 Configurando Nginx..."
cat > /etc/nginx/sites-available/nik0finance << 'NGINX_EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;
    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    location /whatsapp/ {
        proxy_pass http://127.0.0.1:3000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /static/ {
        alias /app/nik0finance/static/;
        expires 30d;
    }
}
NGINX_EOF

rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/nik0finance /etc/nginx/sites-enabled/
nginx -t && systemctl restart nginx

# Criar serviço Flask
cat > /etc/systemd/system/nik0finance.service << 'SERVICE_EOF'
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
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# Criar serviço WhatsApp
if [ -d "/app/nik0finance/whatsapp_server" ]; then
    cat > /etc/systemd/system/nik0finance-whatsapp.service << 'WA_SERVICE_EOF'
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
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
WA_SERVICE_EOF
fi

# Iniciar serviços
systemctl daemon-reload
systemctl enable nik0finance
systemctl start nik0finance

if [ -d "/app/nik0finance/whatsapp_server" ]; then
    systemctl enable nik0finance-whatsapp
    systemctl start nik0finance-whatsapp
fi

# Aguardar 5 segundos
sleep 5

# Exibir resultado
clear
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
systemctl is-active nik0finance && echo "  ✅ Flask: Rodando" || echo "  ❌ Flask: Parado"
if [ -d "/app/nik0finance/whatsapp_server" ]; then
    systemctl is-active nik0finance-whatsapp && echo "  ✅ WhatsApp: Rodando" || echo "  ⚠️  WhatsApp: Parado"
fi
echo ""
echo "🔧 Comandos úteis:"
echo "  Ver logs:         journalctl -u nik0finance -f"
echo "  Reiniciar:        systemctl restart nik0finance"
echo "  Parar:            systemctl stop nik0finance"
echo "  Ver processos:    htop"
echo ""
echo "📱 Configure o app mobile:"
echo "  Em services/api.js altere para:"
echo "  const API_BASE_URL = 'http://$(curl -s ifconfig.me)';"
echo ""
echo "🔒 Para HTTPS (depois de configurar domínio):"
echo "  certbot --nginx -d seudominio.com"
echo ""
