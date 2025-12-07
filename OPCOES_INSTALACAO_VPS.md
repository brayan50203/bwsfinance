# 🚀 OPÇÕES DE INSTALAÇÃO NA VPS

Você tem 2 formas de instalar:

---

## 📦 OPÇÃO 1: VIA GITHUB (Mais Fácil - Recomendado)

### ✅ Vantagens
- ✅ Não precisa fazer upload manual
- ✅ Atualização fácil (`git pull`)
- ✅ Backup automático no GitHub
- ✅ Mais profissional

### ⚠️ Requisito
- Precisa subir o código no GitHub primeiro

---

### Passo a Passo:

#### 1️⃣ Subir código no GitHub

No Windows:
```powershell
cd C:\App\nik0finance-base

# Inicializar Git (se ainda não tiver)
git init
git add .
git commit -m "Initial commit"

# Criar repositório no GitHub.com
# Depois linkar:
git remote add origin https://github.com/SEU_USUARIO/nik0finance.git
git branch -M main
git push -u origin main
```

**OU** use o GitHub Desktop (mais fácil):
1. Baixe: https://desktop.github.com/
2. Abra o GitHub Desktop
3. File → Add Local Repository → Selecione `C:\App\nik0finance-base`
4. Publish repository

#### 2️⃣ Conectar na VPS
```bash
ssh root@SEU_IP_VPS
```

#### 3️⃣ Copiar e colar o script:

```bash
curl -o install.sh https://raw.githubusercontent.com/SEU_USUARIO/nik0finance/main/install_vps_github.sh
nano install.sh
# Altere a linha 15: GITHUB_REPO="https://github.com/SEU_USUARIO/nik0finance.git"
# Ctrl+O, Enter, Ctrl+X
chmod +x install.sh
bash install.sh
```

#### 4️⃣ PRONTO!

Acesse: `http://SEU_IP`

**Para atualizar depois:**
```bash
cd /app/nik0finance
git pull
systemctl restart nik0finance
```

---

## 📁 OPÇÃO 2: VIA SCP (Sem GitHub)

### ✅ Vantagens
- ✅ Não precisa GitHub
- ✅ Mais privado (código não fica público)

### ⚠️ Desvantagem
- ⚠️ Precisa fazer upload manual (5-10 minutos)

---

### Passo a Passo:

#### 1️⃣ Conectar na VPS
```bash
ssh root@SEU_IP_VPS
```

#### 2️⃣ Copiar e colar o script preparador:

```bash
cat > prepare.sh << 'END'
#!/bin/bash
apt update -y && apt upgrade -y
apt install -y software-properties-common
add-apt-repository -y ppa:deadsnakes/ppa
apt update -y
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt install -y nodejs tesseract-ocr tesseract-ocr-por ffmpeg nginx certbot python3-certbot-nginx
mkdir -p /app/nik0finance
echo "✅ Sistema preparado!"
echo "Agora envie os arquivos do Windows:"
echo "scp -r C:\\App\\nik0finance-base\\* root@$(curl -s ifconfig.me):/app/nik0finance/"
END

chmod +x prepare.sh
bash prepare.sh
```

#### 3️⃣ Fazer upload (no Windows)

```powershell
scp -r C:\App\nik0finance-base\* root@SEU_IP:/app/nik0finance/
```

⏱️ **Aguarde 5-10 minutos** (vai enviar ~300 MB)

#### 4️⃣ Continuar instalação na VPS

```bash
cd /app/nik0finance
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd whatsapp_server && npm install && cd ..

# Configurar Nginx
cat > /etc/nginx/sites-available/nik0finance << 'NGINX'
server {
    listen 80 default_server;
    server_name _;
    client_max_body_size 50M;
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
    }
    location /static/ { alias /app/nik0finance/static/; }
}
NGINX
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/nik0finance /etc/nginx/sites-enabled/
systemctl restart nginx

# Criar serviço
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

echo "✅ PRONTO!"
```

---

## 🎯 QUAL ESCOLHER?

| Critério | GitHub | SCP |
|----------|--------|-----|
| **Facilidade** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Velocidade** | ⭐⭐⭐⭐⭐ (30s) | ⭐⭐ (10 min) |
| **Privacidade** | ⭐⭐⭐ (público*) | ⭐⭐⭐⭐⭐ |
| **Atualização** | ⭐⭐⭐⭐⭐ (`git pull`) | ⭐⭐ (upload manual) |
| **Backup** | ⭐⭐⭐⭐⭐ (GitHub) | ⭐⭐ (manual) |

\*Pode criar repositório privado no GitHub (grátis)

---

## 💡 MINHA RECOMENDAÇÃO

### Use GITHUB se:
- ✅ Quer facilidade máxima
- ✅ Quer atualizar com 1 comando
- ✅ Quer backup automático
- ✅ Não se importa de usar GitHub

### Use SCP se:
- ✅ Não quer mexer com GitHub
- ✅ Quer 100% privado
- ✅ Vai instalar uma vez só

---

## 🔒 GITHUB PRIVADO (RECOMENDADO)

Para manter código privado no GitHub:

1. Ao criar repositório, marque **Private**
2. OU tornar privado depois:
   - Vá em Settings → Danger Zone
   - Change visibility → Make private

**Com repositório privado:**
- ✅ Código não fica público
- ✅ Continua tendo todas as vantagens
- ✅ Grátis no GitHub

---

## 📝 RESUMO RÁPIDO

### GitHub (30 segundos):
```bash
# Na VPS:
curl -o install.sh https://raw.githubusercontent.com/SEU_USUARIO/nik0finance/main/install_vps_github.sh
nano install.sh  # Altere a URL do GitHub
bash install.sh
```

### SCP (10 minutos):
```bash
# Na VPS: preparar
bash prepare.sh

# No Windows: enviar
scp -r C:\App\nik0finance-base\* root@IP:/app/nik0finance/

# Na VPS: instalar
bash final_install.sh
```

---

**Recomendo GitHub!** Mais rápido, fácil e profissional. 🚀
