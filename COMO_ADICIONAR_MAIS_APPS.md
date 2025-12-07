# 🚀 Como Adicionar Novas Aplicações ao Seu Servidor Docker

Este guia mostra como hospedar **múltiplas aplicações** no mesmo servidor usando Docker + Nginx.

---

## 📋 **Estrutura Atual**

```
C:\App\
├── nik0finance-base\          # BWS Finance (porta 80)
│   ├── docker-compose.yml
│   ├── nginx/
│   └── ...
│
├── segunda-aplicacao\          # Próxima app (porta 8080)
│   ├── docker-compose.yml
│   └── ...
│
└── terceira-aplicacao\         # Próxima app (porta 8081)
    └── ...
```

---

## 🎯 **Opção 1: Adicionar ao Mesmo Docker Compose (Simples)**

### **Exemplo: Adicionar um Blog WordPress**

1. **Edite `docker-compose.yml`:**

```yaml
version: '3.8'

services:
  # ... serviços existentes (nginx, bws-backend, whatsapp-server)

  # ========================================
  # NOVO: WordPress
  # ========================================
  wordpress:
    image: wordpress:latest
    container_name: meu-blog
    restart: unless-stopped
    ports:
      - "8080:80"
    environment:
      WORDPRESS_DB_HOST: wordpress-db
      WORDPRESS_DB_USER: wordpress
      WORDPRESS_DB_PASSWORD: senha-segura-123
      WORDPRESS_DB_NAME: wordpress
    volumes:
      - wordpress_data:/var/www/html
    networks:
      - bws-network
    depends_on:
      - wordpress-db

  wordpress-db:
    image: mysql:8.0
    container_name: wordpress-mysql
    restart: unless-stopped
    environment:
      MYSQL_DATABASE: wordpress
      MYSQL_USER: wordpress
      MYSQL_PASSWORD: senha-segura-123
      MYSQL_ROOT_PASSWORD: senha-root-456
    volumes:
      - wordpress_db:/var/lib/mysql
    networks:
      - bws-network

volumes:
  # ... volumes existentes
  wordpress_data:
  wordpress_db:
```

2. **Crie arquivo Nginx: `nginx/conf.d/blog.conf`:**

```nginx
server {
    listen 80;
    server_name blog.local localhost:8080;

    location / {
        proxy_pass http://wordpress:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. **Reinicie:**

```powershell
docker-compose down
docker-compose up -d
```

4. **Acesse:**
- Blog: http://192.168.80.122:8080
- Finance: http://192.168.80.122 (porta 80)

---

## 🎯 **Opção 2: Docker Compose Separado (Recomendado para produção)**

### **Exemplo: API Node.js separada**

1. **Crie pasta nova:**

```powershell
mkdir C:\App\minha-api-nodejs
cd C:\App\minha-api-nodejs
```

2. **Crie `Dockerfile`:**

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --production
COPY . .
EXPOSE 4000
CMD ["node", "server.js"]
```

3. **Crie `docker-compose.yml`:**

```yaml
version: '3.8'

services:
  api-nodejs:
    build: .
    container_name: minha-api
    restart: unless-stopped
    ports:
      - "4000:4000"
    environment:
      NODE_ENV: production
      PORT: 4000
    networks:
      - bws-network

networks:
  bws-network:
    external: true  # Usa a rede do BWS Finance
```

4. **Inicie:**

```powershell
docker-compose up -d
```

5. **Adicione ao Nginx do BWS Finance:**

Crie `C:\App\nik0finance-base\nginx\conf.d\minha-api.conf`:

```nginx
server {
    listen 80;
    server_name api.local localhost:4000;

    location / {
        proxy_pass http://minha-api:4000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

6. **Reinicie Nginx:**

```powershell
cd C:\App\nik0finance-base
docker-compose restart nginx
```

---

## 🎯 **Opção 3: Nginx Centralizado (Melhor para múltiplas apps)**

### **Estrutura recomendada:**

```
C:\Docker\
├── nginx\                     # Nginx central
│   ├── docker-compose.yml
│   ├── nginx.conf
│   └── conf.d\
│       ├── finance.conf
│       ├── blog.conf
│       └── api.conf
│
├── apps\
│   ├── bws-finance\
│   │   └── docker-compose.yml
│   ├── blog\
│   │   └── docker-compose.yml
│   └── api\
│       └── docker-compose.yml
```

### **1. Crie Nginx centralizado:**

`C:\Docker\nginx\docker-compose.yml`:

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    container_name: nginx-gateway
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./conf.d:/etc/nginx/conf.d:ro
      - ./ssl:/etc/nginx/ssl:ro
    networks:
      - frontend

networks:
  frontend:
    driver: bridge
```

### **2. Configure cada app para usar a rede:**

Em cada `docker-compose.yml` das apps:

```yaml
networks:
  frontend:
    external: true
  backend:
    driver: bridge
```

### **3. Inicie Nginx primeiro:**

```powershell
cd C:\Docker\nginx
docker network create frontend
docker-compose up -d
```

### **4. Inicie cada app:**

```powershell
cd C:\Docker\apps\bws-finance
docker-compose up -d

cd C:\Docker\apps\blog
docker-compose up -d
```

---

## 📦 **Templates Prontos**

### **Node.js + Express API**

```yaml
services:
  nodejs-app:
    image: node:18-alpine
    working_dir: /app
    volumes:
      - ./:/app
    command: npm start
    ports:
      - "3000:3000"
    networks:
      - bws-network
```

### **Python Flask/Django API**

```yaml
services:
  python-app:
    image: python:3.11-slim
    working_dir: /app
    volumes:
      - ./:/app
    command: flask run --host=0.0.0.0
    ports:
      - "5001:5000"
    networks:
      - bws-network
```

### **PHP + Apache**

```yaml
services:
  php-app:
    image: php:8.2-apache
    volumes:
      - ./src:/var/www/html
    ports:
      - "8081:80"
    networks:
      - bws-network
```

### **PostgreSQL Database**

```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: meu_banco
      POSTGRES_USER: usuario
      POSTGRES_PASSWORD: senha
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - bws-network

volumes:
  postgres_data:
```

### **Redis Cache**

```yaml
services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - bws-network

volumes:
  redis_data:
```

---

## 🔧 **Comandos Úteis**

### **Listar todas apps rodando:**
```powershell
docker ps
```

### **Ver todas redes:**
```powershell
docker network ls
```

### **Conectar app à rede:**
```powershell
docker network connect bws-network nome-container
```

### **Ver uso de recursos:**
```powershell
docker stats
```

### **Backup de volume:**
```powershell
docker run --rm -v nome_volume:/data -v ${PWD}:/backup alpine tar czf /backup/backup.tar.gz /data
```

### **Restaurar volume:**
```powershell
docker run --rm -v nome_volume:/data -v ${PWD}:/backup alpine tar xzf /backup/backup.tar.gz -C /
```

---

## 🌐 **Domínios Locais (opcional)**

### **Configurar hosts do Windows:**

1. Abra como Administrador:
   ```
   C:\Windows\System32\drivers\etc\hosts
   ```

2. Adicione:
   ```
   192.168.80.122  finance.local
   192.168.80.122  blog.local
   192.168.80.122  api.local
   ```

3. Acesse:
   - http://finance.local
   - http://blog.local
   - http://api.local

---

## 📊 **Monitoramento (opcional)**

### **Adicionar Portainer (Interface Gráfica):**

```yaml
services:
  portainer:
    image: portainer/portainer-ce:latest
    container_name: portainer
    restart: unless-stopped
    ports:
      - "9000:9000"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - portainer_data:/data
    networks:
      - bws-network

volumes:
  portainer_data:
```

Acesse: http://192.168.80.122:9000

### **Adicionar Grafana + Prometheus (avançado):**

Consulte: https://github.com/stefanprodan/dockprom

---

## 🎯 **Boas Práticas**

1. ✅ **Use `.env` para senhas** (nunca comite no Git)
2. ✅ **Separe redes** (frontend/backend) para segurança
3. ✅ **Use volumes nomeados** para dados persistentes
4. ✅ **Defina `restart: unless-stopped`** para auto-restart
5. ✅ **Configure health checks** em produção
6. ✅ **Documente as portas** usadas por cada app
7. ✅ **Faça backup regular** dos volumes
8. ✅ **Use imagens oficiais** quando possível
9. ✅ **Fixe versões** (ex: `node:18` em vez de `node:latest`)
10. ✅ **Configure logs** (`docker-compose logs -f`)

---

## 📝 **Checklist para Nova Aplicação**

- [ ] Criar pasta da aplicação
- [ ] Criar `Dockerfile` (se necessário)
- [ ] Criar `docker-compose.yml`
- [ ] Definir porta única (8080, 8081, etc.)
- [ ] Adicionar à rede `bws-network`
- [ ] Criar configuração Nginx em `nginx/conf.d/`
- [ ] Reiniciar Nginx: `docker-compose restart nginx`
- [ ] Testar acesso: `curl http://localhost:PORTA`
- [ ] Documentar porta usada
- [ ] Configurar backup (se tiver banco de dados)

---

**Pronto! Seu servidor local pode hospedar quantas aplicações você quiser! 🚀**
