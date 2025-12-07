# BWS Finance - Guia de Deploy Local com Docker

## 📋 **Pré-requisitos**

1. **Docker Desktop para Windows**
   - Download: https://www.docker.com/products/docker-desktop
   - Instale e reinicie o PC
   - Certifique-se que está rodando (ícone na bandeja)

2. **Git** (opcional, para versionamento)
   - Download: https://git-scm.com/download/win

---

## 🚀 **Iniciar Sistema (Primeira vez)**

### **Passo 1: Build das imagens**
```powershell
cd C:\App\nik0finance-base
docker-compose build
```
⏱️ Demora ~5-10 minutos na primeira vez

### **Passo 2: Iniciar containers**
```powershell
docker-compose up -d
```

### **Passo 3: Verificar status**
```powershell
docker-compose ps
```

Deve mostrar:
- ✅ bws-finance-flask (running)
- ✅ bws-finance-whatsapp (running)
- ✅ bws-finance-nginx (running)

### **Passo 4: Acessar sistema**
- 🌐 **Site**: http://192.168.80.122
- 📱 **WhatsApp Health**: http://192.168.80.122/whatsapp/health
- 📊 **Dashboard**: http://192.168.80.122/dashboard

---

## 🔄 **Comandos Úteis**

### **Parar tudo**
```powershell
docker-compose down
```

### **Reiniciar tudo**
```powershell
docker-compose restart
```

### **Ver logs**
```powershell
# Todos
docker-compose logs -f

# Só Flask
docker-compose logs -f flask

# Só WhatsApp
docker-compose logs -f whatsapp
```

### **Atualizar código**
```powershell
# 1. Parar
docker-compose down

# 2. Rebuild
docker-compose build

# 3. Iniciar
docker-compose up -d
```

### **Acessar terminal do container**
```powershell
# Flask
docker exec -it bws-finance-flask bash

# WhatsApp
docker exec -it bws-finance-whatsapp sh
```

### **Limpar tudo e recomeçar**
```powershell
docker-compose down -v
docker system prune -a
docker-compose build --no-cache
docker-compose up -d
```

---

## 📊 **Monitoramento**

### **Uso de recursos**
```powershell
docker stats
```

### **Ver processos**
```powershell
docker-compose top
```

### **Health checks**
```powershell
# Flask
curl http://localhost:5000/api/whatsapp/health

# WhatsApp
curl http://localhost:3000/health

# Nginx
curl http://localhost/health
```

---

## 🔐 **Segurança**

### **Mudar senhas no `.env`**
Crie arquivo `.env` na raiz:
```env
SECRET_KEY=MUDE-ISSO-PARA-ALGO-SUPER-SEGURO
WHATSAPP_AUTH_TOKEN=seu-token-personalizado
FLASK_ENV=production
```

### **Habilitar HTTPS** (opcional)
1. Gerar certificado SSL:
```powershell
# Certificado auto-assinado (desenvolvimento)
mkdir nginx\ssl
cd nginx\ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout key.pem -out cert.pem
```

2. Descomentar bloco HTTPS no `nginx/nginx.conf`

3. Reiniciar Nginx:
```powershell
docker-compose restart nginx
```

---

## 📁 **Estrutura dos Volumes**

Os dados ficam salvos em:
- 📊 **Banco de dados**: `./bws_finance.db`
- 📝 **Logs**: `./logs/`
- 📱 **WhatsApp tokens**: `./whatsapp_server/tokens/`
- 📁 **Uploads**: `./static/uploads/`

**Backup recomendado:**
```powershell
# Criar backup
$data = Get-Date -Format "yyyyMMdd"
Copy-Item bws_finance.db "backups\bws_finance_$data.db"
```

---

## 🌐 **Adicionar Mais Aplicações**

### **Exemplo: Adicionar PostgreSQL**
Edite `docker-compose.yml`:
```yaml
  postgres:
    image: postgres:15-alpine
    container_name: bws-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: bws_finance
      POSTGRES_USER: bws
      POSTGRES_PASSWORD: senha-segura
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - bws-network

volumes:
  postgres-data:
```

### **Exemplo: Adicionar Redis (cache)**
```yaml
  redis:
    image: redis:alpine
    container_name: bws-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    networks:
      - bws-network
```

---

## 🆘 **Solução de Problemas**

### **Erro: "port is already allocated"**
```powershell
# Ver o que está usando a porta
netstat -ano | findstr :5000
netstat -ano | findstr :3000

# Matar processo
taskkill /PID <PID> /F
```

### **Erro: "Cannot connect to Docker daemon"**
- Certifique-se que Docker Desktop está rodando
- Reinicie Docker Desktop

### **Container não inicia**
```powershell
# Ver logs detalhados
docker-compose logs flask
docker-compose logs whatsapp
```

### **WhatsApp não conecta**
```powershell
# Limpar tokens
docker-compose down
Remove-Item whatsapp_server\tokens\* -Recurse -Force
docker-compose up -d
```

### **Banco corrompido**
```powershell
# Restaurar backup
docker-compose down
Copy-Item backups\bws_finance_YYYYMMDD.db bws_finance.db
docker-compose up -d
```

---

## 🚀 **Auto-start no Windows**

### **Método 1: Docker Desktop**
- Docker Desktop → Settings → General
- ✅ "Start Docker Desktop when you log in"
- ✅ Containers iniciam automaticamente

### **Método 2: Task Scheduler**
1. Abra Task Scheduler
2. Create Task
3. Name: "BWS Finance"
4. Trigger: "At startup"
5. Action: "Start a program"
   - Program: `docker-compose`
   - Arguments: `up -d`
   - Start in: `C:\App\nik0finance-base`

---

## 📈 **Escalar no Futuro**

### **Múltiplas instâncias Flask**
```yaml
  flask:
    # ... configurações existentes
    deploy:
      replicas: 3
```

### **Load Balancer**
Nginx já está configurado para isso!

### **Migrar para Kubernetes** (avançado)
- Docker Compose → Kompose → Kubernetes
- Ou usar Docker Swarm

---

## 📞 **Suporte**

**Comandos úteis para debug:**
```powershell
# Status completo
docker-compose ps
docker-compose logs --tail=50

# Reiniciar serviço específico
docker-compose restart flask

# Ver configuração
docker-compose config
```

---

**Pronto! Sistema profissional e escalável! 🎉**
