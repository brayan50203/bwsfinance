# 🚀 INSTALAÇÃO VPS - COPIE E COLE

## ✅ PASSO A PASSO SIMPLES

### 1️⃣ Compre a VPS

**Contabo VPS S SSD** - €4.50/mês (~R$ 27/mês)
- Link: https://contabo.com/en/vps/
- Sistema: **Ubuntu 22.04 LTS**
- Você vai receber um email com:
  - IP: `123.456.789.0`
  - User: `root`
  - Senha: `abc123xyz`

---

### 2️⃣ Conecte na VPS

Abra o **PowerShell** no Windows e execute:

```powershell
ssh root@SEU_IP_AQUI
# Digite 'yes' quando perguntar
# Cole a senha (Ctrl+V)
```

---

### 3️⃣ COPIE E COLE O SCRIPT INTEIRO

No terminal SSH, copie e cole TODO este comando DE UMA VEZ:

```bash
curl -s https://raw.githubusercontent.com/SEU_USUARIO/nik0finance/main/install_vps_completo.sh | bash
```

**OU** se não tiver no GitHub, cole MANUALMENTE:

```bash
cat > install.sh << 'SCRIPT_END'
#!/bin/bash
set -e
echo "🚀 Iniciando instalação..."
apt update -y && apt upgrade -y
apt install -y software-properties-common
add-apt-repository -y ppa:deadsnakes/ppa
apt update -y
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt install -y nodejs tesseract-ocr tesseract-ocr-por ffmpeg git curl wget nano htop nginx certbot python3-certbot-nginx
mkdir -p /app/nik0finance
cd /app/nik0finance
echo "⚠️  No Windows, execute: scp -r C:\\App\\nik0finance-base\\* root@$(curl -s ifconfig.me):/app/nik0finance/"
read -p "Pressione ENTER após enviar..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
cat > requirements.txt << 'REQ'
Flask==2.3.2
ofxparse==0.21
PyPDF2==3.0.1
pytesseract==0.3.10
python-dateutil==2.8.2
requests==2.31.0
schedule==1.2.0
openai==1.3.5
REQ
pip install -r requirements.txt
[ -d "whatsapp_server" ] && cd whatsapp_server && npm install && cd ..
cat > /etc/nginx/sites-available/nik0finance << 'NGINX'
server {
    listen 80 default_server;
    server_name _;
    client_max_body_size 50M;
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    location /static/ { alias /app/nik0finance/static/; }
}
NGINX
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/nik0finance /etc/nginx/sites-enabled/
nginx -t && systemctl restart nginx
cat > /etc/systemd/system/nik0finance.service << 'SVC'
[Unit]
Description=Nik0 Finance
After=network.target
[Service]
Type=simple
User=root
WorkingDirectory=/app/nik0finance
Environment="PATH=/app/nik0finance/venv/bin"
ExecStart=/app/nik0finance/venv/bin/python app.py
Restart=always
[Install]
WantedBy=multi-user.target
SVC
systemctl daemon-reload
systemctl enable nik0finance
systemctl start nik0finance
sleep 3
echo "✅ PRONTO! Acesse: http://$(curl -s ifconfig.me)"
systemctl status nik0finance --no-pager
SCRIPT_END

chmod +x install.sh
bash install.sh
```

---

### 4️⃣ Quando o script pausar

O script vai pausar e mostrar:

```
⚠️  No Windows, execute: scp -r C:\App\nik0finance-base\* root@123.456.789.0:/app/nik0finance/
Pressione ENTER após enviar...
```

**No seu PC Windows**, abra OUTRO PowerShell e execute:

```powershell
scp -r C:\App\nik0finance-base\* root@SEU_IP_AQUI:/app/nik0finance/
```

Aguarde o upload terminar, depois volte no terminal SSH e pressione **ENTER**.

---

### 5️⃣ PRONTO! 🎉

O script vai finalizar e mostrar:

```
✅ INSTALAÇÃO CONCLUÍDA!
🌐 Acesse agora: http://123.456.789.0
```

Abra o navegador e acesse o IP!

---

## 📱 CONFIGURAR APP MOBILE

Edite `C:\App\nik0finance-mobile\services\api.js`:

```javascript
const API_BASE_URL = 'http://SEU_IP_VPS';
```

---

## 🔧 COMANDOS ÚTEIS

```bash
# Ver logs em tempo real
journalctl -u nik0finance -f

# Reiniciar app
systemctl restart nik0finance

# Ver status
systemctl status nik0finance

# Editar código
nano /app/nik0finance/app.py

# Ver processos
htop
```

---

## 🐛 SE DER ERRO

### Flask não inicia

```bash
# Ver logs
journalctl -u nik0finance -n 50

# Testar manualmente
cd /app/nik0finance
source venv/bin/activate
python app.py
```

### Banco de dados não encontrado

```bash
# Verificar se existe
ls -la /app/nik0finance/bws_finance.db

# Se não existir, envie do Windows
scp C:\App\nik0finance-base\bws_finance.db root@SEU_IP:/app/nik0finance/
```

### Porta 80 ocupada

```bash
# Ver quem está usando
lsof -i :80

# Parar o processo
systemctl stop apache2  # ou nginx
systemctl restart nik0finance
```

---

## 🔒 ATIVAR HTTPS (OPCIONAL)

Depois de configurar domínio:

```bash
certbot --nginx -d seudominio.com.br
```

Pronto! Certificado SSL gratuito instalado.

---

## 💾 BACKUP AUTOMÁTICO

```bash
# Criar script
cat > /root/backup.sh << 'BACKUP'
#!/bin/bash
tar -czf /root/backup-$(date +%Y%m%d).tar.gz /app/nik0finance/bws_finance.db
find /root/backup-*.tar.gz -mtime +7 -delete
BACKUP

chmod +x /root/backup.sh

# Agendar backup diário às 3h
crontab -e
# Adicione: 0 3 * * * /root/backup.sh
```

---

## 📊 MONITORAR RECURSOS

```bash
# Ver uso de RAM/CPU
htop

# Ver espaço em disco
df -h

# Ver logs Nginx
tail -f /var/log/nginx/access.log
```

---

## 🎯 RESUMO

1. Compre VPS (Contabo €4.50/mês)
2. SSH: `ssh root@IP`
3. Cole o script inteiro
4. Quando pausar, envie arquivos: `scp -r C:\App\nik0finance-base\* root@IP:/app/nik0finance/`
5. Pressione ENTER
6. Acesse: `http://SEU_IP`

**PRONTO!** Sistema rodando na VPS! 🚀

---

Precisa de ajuda? Veja os logs:
```bash
journalctl -u nik0finance -f
```
