# 🏠 Deploy BWS Finance no CasaOS

## 📋 Pré-requisitos

1. **CasaOS instalado** (versão 0.4.0+)
2. **Docker e Docker Compose** (já inclusos no CasaOS)
3. **Acesso SSH** ao servidor CasaOS (opcional, mas recomendado)
4. **Portas disponíveis:** 5000 (backend), 3000 (WhatsApp), 5173 (frontend)

---

## 🚀 Método 1: Deploy via App Store do CasaOS (Recomendado)

### Passo 1: Criar arquivo de configuração do app

1. Acesse seu CasaOS via navegador: `http://ip-do-servidor`
2. Vá em **App Store** → **Custom Install**
3. Use o arquivo `casaos-app.yaml` (veja abaixo)

### Passo 2: Arquivo `casaos-app.yaml`

Crie este arquivo na raiz do projeto:

```yaml
name: bws-finance
services:
  bws-backend:
    image: bws-finance-backend:latest
    deploy:
      resources:
        reservations:
          memory: 512M
    network_mode: bridge
    ports:
      - target: 5000
        published: "5000"
        protocol: tcp
    restart: unless-stopped
    volumes:
      - type: bind
        source: /DATA/AppData/bws-finance/data
        target: /app/data
      - type: bind
        source: /DATA/AppData/bws-finance/logs
        target: /app/logs
    x-casaos:
      envs:
        - container: SECRET_KEY
          description: Chave secreta do Flask (mínimo 32 caracteres)
        - container: WHATSAPP_AUTH_TOKEN
          description: Token de autenticação do WhatsApp
        - container: SMTP_USER
          description: Usuário do email (ex: seu-email@gmail.com)
        - container: SMTP_PASSWORD
          description: Senha do email ou App Password
        - container: SMTP_HOST
          description: Servidor SMTP (ex: smtp.gmail.com)
          default: smtp.gmail.com
        - container: SMTP_PORT
          description: Porta SMTP
          default: "587"
      ports:
        - container: "5000"
          description:
            en_us: Backend Web UI Port
            pt_br: Porta da Interface Web
      volumes:
        - container: /app/data
          description:
            en_us: Database and persistent data
            pt_br: Banco de dados e dados persistentes
        - container: /app/logs
          description:
            en_us: Application logs
            pt_br: Logs da aplicação
    container_name: bws-finance-backend
    
  bws-whatsapp:
    image: wppconnect/wppconnect-server:latest
    deploy:
      resources:
        reservations:
          memory: 256M
    network_mode: bridge
    ports:
      - target: 21465
        published: "3000"
        protocol: tcp
    restart: unless-stopped
    volumes:
      - type: bind
        source: /DATA/AppData/bws-finance/whatsapp
        target: /home/node/app/tokens
    container_name: bws-finance-whatsapp

x-casaos:
  architectures:
    - amd64
    - arm64
  main: bws-backend
  description:
    en_us: Personal finance management system with automatic notifications via WhatsApp and Email
    pt_br: Sistema de gestão financeira pessoal com notificações automáticas via WhatsApp e Email
  tagline:
    en_us: Complete financial control
    pt_br: Controle financeiro completo
  developer: BWS Team
  author: BWS Team
  icon: https://raw.githubusercontent.com/your-repo/icon.png
  thumbnail: https://raw.githubusercontent.com/your-repo/thumbnail.png
  title:
    en_us: BWS Finance
  category: Finance
  port_map: "5000"
```

### Passo 3: Build da imagem Docker

Via SSH no servidor CasaOS:

```bash
# Clonar repositório (ou enviar via FTP)
cd /DATA/AppData
git clone https://github.com/seu-usuario/bws-finance.git
cd bws-finance

# Build da imagem
docker build -t bws-finance-backend:latest .

# Verificar imagem
docker images | grep bws-finance
```

### Passo 4: Instalar via App Store

1. No CasaOS, vá em **App Store** → **Custom Install**
2. Cole o conteúdo do `casaos-app.yaml`
3. Clique em **Install**
4. Configure as variáveis de ambiente quando solicitado

---

## 🔧 Método 2: Deploy via Docker Compose (Manual)

### Passo 1: Preparar diretórios

Via SSH no servidor CasaOS:

```bash
# Criar diretórios
mkdir -p /DATA/AppData/bws-finance/{data,logs,whatsapp,frontend}
cd /DATA/AppData/bws-finance

# Clonar ou copiar código
git clone https://github.com/seu-usuario/bws-finance.git .

# Copiar .env
cp .env.example .env
nano .env  # Editar configurações
```

### Passo 2: Configurar `.env`

Edite o arquivo `.env` com suas credenciais:

```bash
nano /DATA/AppData/bws-finance/.env
```

**Mínimo obrigatório:**

```env
SECRET_KEY=seu-secret-key-random-32-chars-min
WHATSAPP_AUTH_TOKEN=seu-token-whatsapp
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-ou-app-password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

### Passo 3: Build e Start

```bash
cd /DATA/AppData/bws-finance

# Build das imagens
docker compose build

# Iniciar serviços
docker compose up -d

# Verificar status
docker compose ps

# Ver logs
docker compose logs -f
```

### Passo 4: Acessar aplicação

- **Backend:** `http://ip-do-casaos:5000`
- **WhatsApp QR Code:** `http://ip-do-casaos:3000`

---

## 📱 Configurar WhatsApp

### Passo 1: Gerar QR Code

1. Acesse `http://ip-do-casaos:3000`
2. Endpoint: `/api/bws-finance/start-session`
3. Copie o QR Code

**Usando curl:**

```bash
curl -X POST http://localhost:3000/api/bws-finance/start-session \
  -H "Authorization: Bearer seu-token-aqui"
```

### Passo 2: Escanear QR Code

1. Abra WhatsApp no celular
2. Vá em **Configurações** → **Aparelhos conectados**
3. Clique em **Conectar um aparelho**
4. Escaneie o QR Code exibido

### Passo 3: Verificar conexão

```bash
curl http://localhost:3000/api/bws-finance/status \
  -H "Authorization: Bearer seu-token-aqui"
```

Resposta esperada:
```json
{
  "state": "CONNECTED",
  "session": "bws-finance"
}
```

---

## 📧 Configurar Email (Gmail)

### Opção 1: App Password (Recomendado)

1. Acesse [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Crie um novo App Password
3. Use no `.env`:

```env
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # App Password de 16 dígitos
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

### Opção 2: Conta com 2FA desabilitado (Não recomendado)

```env
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-normal
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

**⚠️ Importante:** Habilite "Acesso a apps menos seguros" nas configurações do Gmail.

---

## 🔍 Verificar funcionamento

### Health Check

```bash
curl http://192.168.80.132:5000/api/notifications/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "scheduler_running": true,
  "jobs_count": 5,
  "whatsapp_available": true,
  "email_available": true
}
```

### Testar notificação manual

```bash
curl -X POST http://192.168.80.132:5000/api/notifications/send \
  -H "Content-Type: application/json" \
  -H "Cookie: session=seu-session-id" \
  -d '{
    "event_type": "low_balance",
    "channel": "whatsapp",
    "params": {
      "account_name": "Teste",
      "balance": 50.00,
      "threshold": 100.00
    }
  }'
```

---

## 🎛️ Gerenciamento via CasaOS UI

### Parar serviços

1. Acesse CasaOS UI
2. Vá em **Apps**
3. Clique em **BWS Finance**
4. Clique em **Stop**

### Ver logs

1. Acesse CasaOS UI
2. Vá em **Apps** → **BWS Finance**
3. Clique em **Logs**

### Atualizar configurações

1. Acesse CasaOS UI
2. Vá em **Apps** → **BWS Finance**
3. Clique em **Settings**
4. Edite variáveis de ambiente
5. Clique em **Save & Restart**

---

## 🔄 Atualizar aplicação

### Via Git Pull

```bash
cd /DATA/AppData/bws-finance

# Parar containers
docker compose down

# Atualizar código
git pull origin main

# Rebuild
docker compose build

# Iniciar novamente
docker compose up -d
```

### Via CasaOS UI

1. Vá em **App Store**
2. Procure **BWS Finance**
3. Clique em **Update**

---

## 🛡️ Segurança

### 1. Firewall

Certifique-se de que apenas as portas necessárias estão expostas:

```bash
# Verificar portas abertas
sudo ufw status

# Abrir apenas portas necessárias
sudo ufw allow 5000/tcp  # Backend
sudo ufw allow 3000/tcp  # WhatsApp (apenas se acesso externo necessário)
```

### 2. HTTPS via Reverse Proxy

Use **Nginx Proxy Manager** (disponível no CasaOS App Store):

1. Instale **Nginx Proxy Manager**
2. Crie proxy host:
   - **Domain:** `bws.seudominio.com`
   - **Forward:** `http://bws-finance-backend:5000`
   - **SSL:** Habilite Let's Encrypt
3. Acesse via `https://bws.seudominio.com`

### 3. Backup automático

Adicione ao cron do CasaOS:

```bash
# Editar crontab
crontab -e

# Backup diário às 02:00
0 2 * * * docker exec bws-finance-backend sqlite3 /app/data/bws_finance.db ".backup /app/data/backup_$(date +\%Y\%m\%d).db"

# Limpar backups antigos (manter últimos 7 dias)
0 3 * * * find /DATA/AppData/bws-finance/data -name "backup_*.db" -mtime +7 -delete
```

---

## 📊 Monitoramento

### Ver estatísticas de uso

```bash
# CPU e memória
docker stats bws-finance-backend bws-finance-whatsapp

# Logs em tempo real
docker compose logs -f --tail=50

# Verificar jobs do scheduler
curl http://192.168.80.132:5000/api/notifications/health | jq '.jobs'
```

---

## 🐛 Troubleshooting

### Container não inicia

```bash
# Ver logs detalhados
docker compose logs bws-backend

# Verificar permissões
sudo chown -R 1000:1000 /DATA/AppData/bws-finance

# Rebuild completo
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

### WhatsApp desconecta

```bash
# Limpar sessão e reconectar
docker compose down
rm -rf /DATA/AppData/bws-finance/whatsapp/*
docker compose up -d

# Gerar novo QR Code
curl -X POST http://localhost:3000/api/bws-finance/start-session
```

### Email não envia

```bash
# Testar SMTP manualmente
docker exec -it bws-finance-backend python -c "
from services.email_sender import EmailSender
sender = EmailSender()
result = sender.send('seu-email@gmail.com', 'Teste', 'Corpo do teste')
print('Enviado:', result)
"
```

### Banco de dados corrompido

```bash
# Restaurar do backup
docker exec bws-finance-backend cp /app/data/backup_20251110.db /app/data/bws_finance.db

# Verificar integridade
docker exec bws-finance-backend sqlite3 /app/data/bws_finance.db "PRAGMA integrity_check;"
```

---

## 📞 Suporte

- **Documentação:** `README_NOTIFICATIONS.md`
- **Issues:** GitHub Issues
- **Logs:** `/DATA/AppData/bws-finance/logs/`

---

## 🎉 Pronto!

Sua instância do BWS Finance está rodando no CasaOS! 🚀

Acesse:
- **Dashboard:** `http://192.168.80.132:5000`
- **WhatsApp:** `http://192.168.80.132:3000`
- **Health Check:** `http://192.168.80.132:5000/api/notifications/health`
