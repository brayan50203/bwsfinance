# 🚀 INSTALAÇÃO VPS - Comando Direto

## ⚠️ IMPORTANTE: Repositório Privado

Como seu repositório GitHub é privado, o acesso via `curl` não funciona diretamente.

---

## 📋 SOLUÇÃO 1: Copiar Script Manualmente (MAIS RÁPIDO)

### 1️⃣ Na VPS, crie o arquivo:

```bash
nano install.sh
```

### 2️⃣ Cole TODO este conteúdo:

```bash
#!/bin/bash
set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║        🚀 NIK0 FINANCE - INSTALAÇÃO COMPLETA             ║"
echo "╚════════════════════════════════════════════════════════════╝"

# Configuração do repositório (PRIVADO - precisa autenticação)
GITHUB_USER="brayan50203"
GITHUB_REPO="bwsfinance"

echo "📦 Atualizando sistema..."
apt update && apt upgrade -y

echo "🐍 Instalando Python 3.11..."
add-apt-repository ppa:deadsnakes/ppa -y
apt install python3.11 python3.11-venv python3.11-dev python3-pip -y
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

echo "📦 Instalando Node.js 22..."
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt install nodejs -y

echo "📝 Instalando Tesseract OCR..."
apt install tesseract-ocr tesseract-ocr-por -y

echo "🎵 Instalando FFmpeg..."
apt install ffmpeg -y

echo "🌐 Instalando Nginx..."
apt install nginx -y

echo "🔧 Instalando Git..."
apt install git -y

echo ""
echo "⚠️  ATENÇÃO: Repositório privado!"
echo "Você tem 2 opções:"
echo ""
echo "OPÇÃO A - Token GitHub (Recomendado):"
echo "1. Vá em: https://github.com/settings/tokens"
echo "2. Gere novo token (classic) com permissão 'repo'"
echo "3. Cole o token aqui quando pedir"
echo ""
echo "OPÇÃO B - SSH Key:"
echo "1. Adicione chave SSH da VPS no GitHub"
echo ""
read -p "Pressione ENTER para continuar e inserir token..." 

echo ""
echo "Cole seu GitHub Personal Access Token:"
read -s GITHUB_TOKEN

echo ""
echo "📥 Clonando projeto do GitHub..."
cd /root
git clone https://${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${GITHUB_REPO}.git nik0finance

if [ ! -d "nik0finance" ]; then
    echo "❌ Erro ao clonar repositório!"
    echo "Verifique se o token está correto e tem permissão 'repo'"
    exit 1
fi

cd nik0finance

echo "📦 Instalando dependências Python..."
python3 -m pip install --upgrade pip
pip install -r requirements.txt

echo "📦 Instalando dependências Node.js..."
cd whatsapp_server
npm install
cd ..

echo "⚙️ Configurando Nginx..."
cat > /etc/nginx/sites-available/nik0finance << 'EOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

ln -sf /etc/nginx/sites-available/nik0finance /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

echo "🚀 Criando serviço Flask..."
cat > /etc/systemd/system/nik0finance.service << EOF
[Unit]
Description=Nik0Finance Flask App
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/nik0finance
Environment="PATH=/usr/bin"
ExecStart=/usr/bin/python3 /root/nik0finance/app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "🚀 Criando serviço WhatsApp..."
cat > /etc/systemd/system/nik0whatsapp.service << EOF
[Unit]
Description=Nik0Finance WhatsApp Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/nik0finance/whatsapp_server
ExecStart=/usr/bin/node /root/nik0finance/whatsapp_server/index_v3.js
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Iniciando serviços..."
systemctl daemon-reload
systemctl enable nik0finance nik0whatsapp
systemctl start nik0finance nik0whatsapp

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                   ✅ INSTALAÇÃO CONCLUÍDA!                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Acesse: http://$(curl -s ifconfig.me)"
echo "👤 Login: admin@nik0finance.com"
echo "🔑 Senha: admin123"
echo ""
echo "📊 Status dos serviços:"
systemctl status nik0finance --no-pager -l
echo ""
systemctl status nik0whatsapp --no-pager -l
```

### 3️⃣ Salve e execute:

Pressione `CTRL+X`, depois `Y`, depois `ENTER`

```bash
chmod +x install.sh
bash install.sh
```

### 4️⃣ Quando pedir o token GitHub:

1. Vá em: https://github.com/settings/tokens
2. Clique em "Generate new token (classic)"
3. Dê um nome: `VPS Deploy`
4. Marque apenas: **☑ repo** (Full control of private repositories)
5. Clique em "Generate token"
6. **COPIE O TOKEN** (só aparece uma vez!)
7. Cole na VPS quando pedir

---

## 📋 SOLUÇÃO 2: Tornar Repositório Público (MAIS SIMPLES)

Se não se importa que o código seja público:

1. Vá em: https://github.com/brayan50203/bwsfinance/settings
2. Role até o final
3. Clique em "Change visibility" → "Make public"
4. Confirme

Depois na VPS:
```bash
curl -o install.sh https://raw.githubusercontent.com/brayan50203/bwsfinance/main/install_vps_github.sh && bash install.sh
```

---

## 📋 SOLUÇÃO 3: Upload Manual (ALTERNATIVA)

No Windows, envie os arquivos:
```powershell
scp -r C:\App\nik0finance-base root@SEU_IP_VPS:/root/nik0finance
```

Depois na VPS:
```bash
cd /root/nik0finance
bash install_vps_completo.sh
```

---

## 🔐 Importante sobre Tokens GitHub

- ⚠️ **NUNCA compartilhe** seu token com ninguém
- 🔒 Tokens dão acesso ao seu GitHub
- ⏰ Você pode definir expiração (recomendado: 30 dias)
- 🗑️ Pode deletar o token depois da instalação

---

## ✅ Próximos Passos Após Instalação

1. Acesse: `http://SEU_IP_VPS`
2. Login: `admin@nik0finance.com` / `admin123`
3. Mude a senha imediatamente!

---

**Escolha a SOLUÇÃO 1 (mais segura) ou SOLUÇÃO 2 (mais rápida)!**
