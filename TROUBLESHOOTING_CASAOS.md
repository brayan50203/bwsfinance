# 🔧 Troubleshooting BWS Finance no CasaOS

## 🚨 Problemas Comuns e Soluções

### 1. Container não inicia

**Sintomas:**
- Container aparece como "Exited" no CasaOS
- Erro ao acessar http://192.168.80.132:5000

**Soluções:**

```bash
# Ver logs detalhados
cd /DATA/AppData/bws-finance
docker compose logs bws-backend

# Verificar se portas estão em uso
sudo netstat -tulpn | grep -E ':(5000|3000)'

# Matar processos na porta (se necessário)
sudo fuser -k 5000/tcp
sudo fuser -k 3000/tcp

# Rebuild completo
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

---

### 2. Erro: "Database is locked"

**Sintomas:**
- Erro 500 ao acessar páginas
- Logs mostram "database is locked"

**Soluções:**

```bash
# Parar containers
docker compose down

# Verificar processos usando o banco
lsof /DATA/AppData/bws-finance/bws_finance.db

# Remover lock file
rm -f /DATA/AppData/bws-finance/bws_finance.db-wal
rm -f /DATA/AppData/bws-finance/bws_finance.db-shm

# Verificar integridade do banco
sqlite3 /DATA/AppData/bws-finance/bws_finance.db "PRAGMA integrity_check;"

# Reiniciar
docker compose up -d
```

---

### 3. WhatsApp desconectado

**Sintomas:**
- QR Code não aparece
- WhatsApp mostra "Disconnected"
- Notificações não chegam

**Soluções:**

```bash
# Limpar sessão do WhatsApp
docker compose down
rm -rf /DATA/AppData/bws-finance/tokens/*
docker compose up -d

# Aguardar 30 segundos e acessar
curl http://localhost:3000/api/bws-finance/start-session

# Escanear novo QR Code
# Abra: http://192.168.80.132:3000

# Verificar status
curl http://localhost:3000/api/bws-finance/status
```

**Prevenir desconexões:**
- Mantenha celular conectado à internet
- Não faça logout do WhatsApp no celular
- Configure reconnect automático no .env:

```env
WHATSAPP_AUTO_RECONNECT=true
```

---

### 4. Emails não são enviados

**Sintomas:**
- Notificações por email falham
- Logs mostram "SMTP Authentication Error"

**Soluções:**

**Gmail:**
1. Habilite "App Passwords":
   - Acesse: https://myaccount.google.com/apppasswords
   - Crie um novo App Password
   - Use no .env (16 dígitos sem espaços)

```env
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop  # Seu App Password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

2. Verifique 2FA está habilitado na conta Google

**Outlook:**
```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=seu-email@outlook.com
SMTP_PASSWORD=sua-senha
```

**Testar SMTP manualmente:**
```bash
docker exec -it bws-finance-backend python << EOF
from services.email_sender import EmailSender
sender = EmailSender()
result = sender.send(
    to_email='seu-email@test.com',
    subject='Teste',
    body='<h1>Teste de email</h1>',
    html=True
)
print('Enviado:', result)
EOF
```

---

### 5. Scheduler não executa jobs

**Sintomas:**
- Notificações automáticas não chegam
- Jobs não aparecem no /health

**Soluções:**

```bash
# Verificar se scheduler está ativo
curl http://localhost:5000/api/notifications/health | jq

# Deve mostrar:
# {
#   "scheduler_running": true,
#   "jobs_count": 5,
#   ...
# }

# Se scheduler_running: false, verificar logs
docker compose logs bws-backend | grep -i scheduler

# Forçar execução manual de job
curl -X POST http://192.168.80.132:5000/api/notifications/run-job/check_low_balance \
  -H "Cookie: session=SEU_SESSION_ID"

# Reiniciar backend
docker compose restart bws-backend
```

**Verificar timezone do container:**
```bash
docker exec bws-finance-backend date
# Se estiver errado, adicionar ao docker-compose.yml:
# environment:
#   - TZ=America/Sao_Paulo
```

---

### 6. Permissões negadas (Permission Denied)

**Sintomas:**
- Erro ao criar arquivos
- Logs mostram "Permission denied"

**Soluções:**

```bash
# Ajustar permissões
sudo chown -R 1000:1000 /DATA/AppData/bws-finance
sudo chmod -R 755 /DATA/AppData/bws-finance

# Verificar usuário do container
docker exec bws-finance-backend id
# Deve mostrar: uid=1000

# Se necessário, rebuildar com usuário correto no Dockerfile:
# USER 1000:1000
```

---

### 7. Banco de dados corrompido

**Sintomas:**
- Erro "database disk image is malformed"
- Crash ao acessar páginas

**Soluções:**

```bash
# 1. Backup do banco atual
cp /DATA/AppData/bws-finance/bws_finance.db /tmp/bws_finance_backup.db

# 2. Tentar reparar
sqlite3 /DATA/AppData/bws-finance/bws_finance.db << EOF
PRAGMA integrity_check;
REINDEX;
VACUUM;
.quit
EOF

# 3. Se falhar, restaurar do backup automático
ls -lah /DATA/AppData/bws-finance/data/backup_*.db

# Copiar backup mais recente
cp /DATA/AppData/bws-finance/data/backup_20251110.db \
   /DATA/AppData/bws-finance/bws_finance.db

# 4. Reiniciar
docker compose restart bws-backend
```

**Prevenir corrupção:**
- Configure backups automáticos (veja seção Backups)
- Use WAL mode (já habilitado por padrão)
- Evite desligar servidor abruptamente

---

### 8. Containers consumindo muita RAM

**Sintomas:**
- CasaOS lento
- Out of Memory errors
- Swap usage alto

**Soluções:**

**Limitar recursos no docker-compose.yml:**
```yaml
services:
  bws-backend:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '1.0'
        reservations:
          memory: 256M
```

**Limpar cache do Docker:**
```bash
docker system prune -a
docker volume prune
```

**Verificar uso de recursos:**
```bash
docker stats bws-finance-backend bws-whatsapp-server
```

---

### 9. Notificações duplicadas

**Sintomas:**
- Recebe mesma notificação múltiplas vezes
- Jobs executam mais de uma vez

**Soluções:**

```bash
# Verificar se há múltiplas instâncias rodando
docker ps | grep bws-finance

# Parar todas
docker compose down

# Limpar containers órfãos
docker container prune

# Iniciar apenas uma instância
docker compose up -d

# Verificar jobs do scheduler
```bash
curl http://192.168.80.132:5000/api/notifications/health | jq '.jobs'
```

**Esperado:**
```

---

### 10. Erro 502 Bad Gateway (com Nginx)

**Sintomas:**
- Acesso via domínio retorna 502
- Acesso direto via IP:5000 funciona

**Soluções:**

**Nginx Proxy Manager config:**
```nginx
# Proxy Host settings
location / {
    proxy_pass http://bws-finance-backend:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 300;
}
```

**Verificar rede Docker:**
```bash
# Listar redes
docker network ls

# Inspecionar rede do bws-finance
docker network inspect bws-network

# Conectar Nginx à rede do bws-finance
docker network connect bws-network nginx-proxy-manager
```

---

## 🔍 Comandos Úteis de Diagnóstico

### Verificar saúde dos serviços
```bash
# Health check do backend
curl -f http://192.168.80.132:5000/api/notifications/health

# Health check do WhatsApp
curl -f http://localhost:3000/health

# Status dos containers
docker compose ps

# Logs em tempo real
docker compose logs -f --tail=50

# Logs de um serviço específico
docker compose logs -f bws-backend
```

### Verificar conectividade
```bash
# Backend pode acessar WhatsApp?
docker exec bws-finance-backend curl http://bws-whatsapp-server:3000/health

# WhatsApp pode acessar Backend?
docker exec bws-whatsapp-server curl http://bws-backend:5000/api/notifications/health
```

### Inspecionar banco de dados
```bash
# Conectar ao SQLite
docker exec -it bws-finance-backend sqlite3 /app/bws_finance.db

# Listar tabelas
.tables

# Ver estrutura
.schema notifications

# Contar notificações
SELECT COUNT(*) FROM notifications;

# Ver últimas notificações
SELECT id, event_type, status, created_at FROM notifications ORDER BY created_at DESC LIMIT 10;

# Sair
.quit
```

### Monitorar recursos
```bash
# CPU e Memória em tempo real
docker stats

# Espaço em disco
df -h /DATA/AppData/bws-finance

# Tamanho do banco
du -sh /DATA/AppData/bws-finance/bws_finance.db
```

---

## 📞 Quando pedir ajuda

Se os problemas persistirem, colete estas informações antes de abrir issue:

```bash
# 1. Versão do CasaOS
casaos -v

# 2. Versão do Docker
docker --version

# 3. Logs completos
docker compose logs > logs_completos.txt

# 4. Configuração (sem senhas)
cat .env | grep -v PASSWORD | grep -v TOKEN | grep -v KEY

# 5. Status do sistema
docker compose ps
docker stats --no-stream

# 6. Health checks
curl http://192.168.80.132:5000/api/notifications/health > health.json
```

Envie esses arquivos ao abrir issue no GitHub.

---

## 🛠️ Reset completo (último recurso)

**⚠️ ATENÇÃO: Isso apagará todos os dados!**

```bash
# Parar tudo
docker compose down -v

# Remover dados
rm -rf /DATA/AppData/bws-finance

# Reinstalar
curl -fsSL https://raw.githubusercontent.com/seu-repo/install-casaos.sh | bash
```

**Backup antes de resetar:**
```bash
# Backup do banco
cp /DATA/AppData/bws-finance/bws_finance.db ~/backup_bws_$(date +%Y%m%d).db

# Backup completo
tar -czf ~/backup_bws_completo_$(date +%Y%m%d).tar.gz /DATA/AppData/bws-finance
```
