# 🎯 Guia Completo - Instalação com CasaOS

## 📋 **Resumo do que vai ter:**

- ✅ **Debian 12 Server** (sistema operacional)
- ✅ **CasaOS** (painel web visual)
- ✅ **Docker** (automático com CasaOS)
- ✅ **BWS Finance** (container Docker)
- ✅ **WhatsApp Server** (container Docker)

---

## 🚀 **Instalação Passo a Passo**

### **ETAPA 1: Instalar Debian 12 Server**

1. Baixar ISO: https://www.debian.org/distrib/netinst
2. Instalar com:
   - SSH Server ✅
   - Utilitários básicos ✅
   - **NÃO** instalar ambiente gráfico ❌

---

### **ETAPA 2: Primeiro Acesso (via SSH)**

```bash
# Conectar via SSH
ssh usuario@IP_DO_SERVIDOR

# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar ferramentas básicas
sudo apt install -y curl wget git
```

---

### **ETAPA 3: Instalar CasaOS** ⭐

```bash
# Instalação automática (1 comando só!)
curl -fsSL https://get.casaos.io | sudo bash

# Aguardar 2-3 minutos
# Vai instalar automaticamente:
# - Docker
# - Docker Compose
# - CasaOS Dashboard
```

**Ao final da instalação vai aparecer:**
```
✅ CasaOS instalado com sucesso!
🌐 Acesse: http://IP_DO_SERVIDOR:80
👤 Crie seu usuário e senha
```

---

### **ETAPA 4: Acessar CasaOS**

1. Abra navegador: `http://IP_DO_SERVIDOR`
2. Crie usuário e senha
3. Pronto! Você está no painel 🎉

**Interface:**
- Dashboard com uso de CPU/RAM/Disco
- App Store
- Gerenciador de arquivos
- Terminal web
- Configurações

---

### **ETAPA 5: Transferir Projeto para o Servidor**

**Opção A: Via SCP (do Windows)**
```powershell
# No PowerShell do Windows
scp -r C:\App\nik0finance-base usuario@IP_SERVIDOR:/home/usuario/bws-finance
```

**Opção B: Via CasaOS Files**
1. No CasaOS, clique em **Files**
2. Upload dos arquivos
3. Criar pasta `/DATA/AppData/bws-finance`

**Opção C: Via Git (se tiver repo)**
```bash
# No servidor
cd /DATA/AppData
git clone seu-repositorio.git bws-finance
```

---

### **ETAPA 6: Configurar Variáveis de Ambiente**

```bash
# Conectar via SSH
ssh usuario@IP_SERVIDOR

# Ir para pasta do projeto
cd /DATA/AppData/bws-finance

# Criar arquivo .env
nano .env
```

**Conteúdo do `.env`:**
```env
# Token de segurança (gere um aleatório)
WHATSAPP_AUTH_TOKEN=seu_token_super_secreto_aqui_12345

# Configurações Flask
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=false

# Configurações WhatsApp
WHATSAPP_PORT=3000

# Whisper (modelo leve)
WHISPER_MODEL=tiny
WHISPER_LANGUAGE=pt

# Tesseract
TESSERACT_LANG=por
```

Salvar: `Ctrl+O` → `Enter` → `Ctrl+X`

---

### **ETAPA 7: Criar Swap (para 1GB RAM)**

```bash
# Criar swap de 2GB
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Tornar permanente
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Otimizar
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Verificar
free -h
```

---

### **ETAPA 8: Subir Containers via CasaOS**

**Método 1: Via Terminal Web do CasaOS**

1. No CasaOS, clique em **Terminal**
2. Execute:

```bash
cd /DATA/AppData/bws-finance

# Construir imagens
docker-compose build

# Subir containers
docker-compose up -d

# Ver logs
docker-compose logs -f
```

**Método 2: Via SSH**
```bash
ssh usuario@IP_SERVIDOR
cd /DATA/AppData/bws-finance
docker-compose up -d
```

---

### **ETAPA 9: Adicionar ao CasaOS Dashboard** (Opcional)

1. No CasaOS, vá em **App Store**
2. Clique em **+ Custom Install**
3. Cole este YAML:

```yaml
name: BWS Finance
services:
  bws-finance:
    image: bws-finance:latest
    restart: unless-stopped
    ports:
      - 5000:5000
    volumes:
      - /DATA/AppData/bws-finance/bws_finance.db:/app/bws_finance.db
      - /DATA/AppData/bws-finance/logs:/app/logs
    networks:
      - bws-network
  
  whatsapp-server:
    image: whatsapp-server:latest
    restart: unless-stopped
    ports:
      - 3000:3000
    volumes:
      - /DATA/AppData/bws-finance/tokens:/app/tokens
    depends_on:
      - bws-finance
    networks:
      - bws-network

networks:
  bws-network:
    driver: bridge
```

4. Clique em **Install**

---

### **ETAPA 10: Conectar WhatsApp**

```bash
# Ver logs do WhatsApp
docker-compose logs whatsapp-server

# Ou via CasaOS:
# Dashboard → Containers → whatsapp-server → Logs
```

**Vai aparecer QR Code:**
1. Abra WhatsApp no celular
2. Menu → Aparelhos conectados
3. Conectar aparelho
4. Escaneie o QR Code que apareceu nos logs

---

### **ETAPA 11: Testar Aplicação**

**Via Navegador:**
- BWS Finance: `http://IP_SERVIDOR:5000`
- WhatsApp Health: `http://IP_SERVIDOR:3000/health`

**Via WhatsApp:**
Envie mensagem para o número conectado:
```
Gastei R$ 50 no mercado hoje
```

Deve receber confirmação:
```
✅ Transação registrada!
💰 Valor: R$ 50,00
📁 Categoria: Alimentação
📅 Data: 07/11/2025
```

---

### **ETAPA 12: Configurar Firewall**

```bash
# Instalar UFW
sudo apt install -y ufw

# Permitir SSH
sudo ufw allow 22/tcp

# Permitir CasaOS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Permitir BWS Finance
sudo ufw allow 5000/tcp

# Permitir WhatsApp (opcional - só se precisar acesso externo)
sudo ufw allow 3000/tcp

# Ativar
sudo ufw enable

# Verificar
sudo ufw status
```

---

## 📊 **Gerenciamento pelo CasaOS**

### **Ver Status dos Containers**
1. CasaOS Dashboard
2. Seção **Containers**
3. Ver: CPU, RAM, Network de cada container

### **Ver Logs**
1. Click no container
2. Tab **Logs**
3. Logs em tempo real

### **Reiniciar Container**
1. Click no container
2. Botão **Restart**

### **Parar/Iniciar**
1. Click no container
2. Toggle **On/Off**

### **Terminal do Container**
1. Click no container
2. Tab **Terminal**
3. Execute comandos dentro do container

---

## 🔍 **Comandos Úteis**

### **Docker Compose**
```bash
cd /DATA/AppData/bws-finance

# Ver status
docker-compose ps

# Ver logs
docker-compose logs -f

# Reiniciar tudo
docker-compose restart

# Parar tudo
docker-compose down

# Subir novamente
docker-compose up -d

# Reconstruir (após mudanças no código)
docker-compose build
docker-compose up -d
```

### **Docker Direto**
```bash
# Listar containers
docker ps

# Logs de um container
docker logs bws-finance
docker logs whatsapp-server

# Entrar no container
docker exec -it bws-finance bash
docker exec -it whatsapp-server sh

# Ver uso de recursos
docker stats
```

---

## 🎯 **Estrutura Final**

```
/DATA/AppData/bws-finance/
├── Dockerfile                # Imagem Flask
├── Dockerfile.whatsapp       # Imagem Node.js
├── docker-compose.yml        # Orquestração
├── .env                      # Variáveis
├── .dockerignore            # Arquivos ignorados
│
├── app.py                   # Flask principal
├── bws_finance.db          # Banco de dados
├── requirements.txt        # Deps Python
├── requirements_whatsapp.txt
│
├── whatsapp_server/
│   ├── index.js
│   ├── package.json
│   └── ...
│
├── modules/
│   ├── audio_processor.py
│   ├── ocr_processor.py
│   ├── pdf_processor.py
│   └── nlp_classifier.py
│
├── logs/                   # Volume Docker
├── temp/                   # Volume Docker
└── tokens/                 # Volume Docker (sessão WhatsApp)
```

---

## ⚡ **Checklist de Instalação**

- [ ] Debian 12 instalado
- [ ] SSH configurado
- [ ] CasaOS instalado (`curl -fsSL https://get.casaos.io | sudo bash`)
- [ ] CasaOS acessível (`http://IP:80`)
- [ ] Projeto transferido para `/DATA/AppData/bws-finance`
- [ ] Arquivo `.env` criado com token
- [ ] Swap de 2GB configurado
- [ ] `docker-compose build` executado
- [ ] `docker-compose up -d` executado
- [ ] Containers rodando (verificar em CasaOS)
- [ ] QR Code do WhatsApp escaneado
- [ ] Teste de mensagem WhatsApp OK
- [ ] Firewall configurado

---

## 📱 **Interface CasaOS - O que você vai ver:**

### **Dashboard Principal**
```
┌─────────────────────────────────────────┐
│  CasaOS                        👤 User  │
├─────────────────────────────────────────┤
│  CPU: ████░░░ 45%   RAM: ██████░ 65%   │
│  Disk: ███░░░░ 30%  Network: ↑50KB ↓100│
├─────────────────────────────────────────┤
│  🐳 Containers (2)                      │
│  ┌─────────────────┬─────────────────┐ │
│  │ bws-finance     │ 🟢 Running      │ │
│  │ CPU: 5% RAM:200M│ Port: 5000      │ │
│  ├─────────────────┼─────────────────┤ │
│  │ whatsapp-server │ 🟢 Running      │ │
│  │ CPU: 3% RAM:150M│ Port: 3000      │ │
│  └─────────────────┴─────────────────┘ │
│                                         │
│  📁 Files   ⚙️  Settings   🛍️  App Store│
└─────────────────────────────────────────┘
```

---

## 🆘 **Problemas Comuns**

### **CasaOS não abre no navegador**
```bash
# Verificar se está rodando
sudo systemctl status casaos

# Reiniciar
sudo systemctl restart casaos

# Ver portas
sudo netstat -tulpn | grep 80
```

### **Container não sobe**
```bash
# Ver erro detalhado
docker-compose logs bws-finance

# Reconstruir
docker-compose build --no-cache
docker-compose up -d
```

### **Out of Memory**
```bash
# Aumentar swap para 4GB
sudo swapoff /swapfile
sudo rm /swapfile
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### **WhatsApp desconecta sozinho**
```bash
# Volume tokens precisa persistir
# Verificar em docker-compose.yml:
volumes:
  - ./tokens:/app/tokens  # ← Deve estar assim
```

---

## 🎉 **Vantagens do CasaOS**

✅ Interface visual linda  
✅ Gerenciamento fácil de containers  
✅ App Store com 1-click install  
✅ Terminal web integrado  
✅ Gerenciador de arquivos  
✅ Monitoramento em tempo real  
✅ Auto-restart de containers  
✅ Backup fácil dos volumes  
✅ Suporte a múltiplas apps  

---

## 🚀 **Próximos Passos**

1. ✅ Testar WhatsApp
2. ✅ Configurar domínio (opcional)
3. ✅ SSL via CasaOS (Let's Encrypt)
4. ✅ Backup automático do DB
5. ✅ Adicionar mais apps pelo App Store

---

Qualquer dúvida, só chamar! 🎯
