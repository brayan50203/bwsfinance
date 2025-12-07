# 🚀 GUIA DE DEPLOY NA VPS

## 📋 PASSO A PASSO

### 1️⃣ COMPRAR VPS

Recomendado: **Contabo VPS S SSD** (€4.50/mês = ~R$ 27/mês)
- Link: https://contabo.com/en/vps/
- Escolha: **Ubuntu 22.04 LTS**

### 2️⃣ CONECTAR NA VPS

No Windows (PowerShell):
```powershell
ssh root@SEU_IP_VPS
# Digite a senha que recebeu por email
```

### 3️⃣ FAZER UPLOAD DO SCRIPT

**Opção A - Copiar e colar:**
```bash
nano deploy_vps.sh
# Cole o conteúdo do arquivo deploy_vps.sh
# Ctrl+O para salvar, Ctrl+X para sair
chmod +x deploy_vps.sh
```

**Opção B - Via SCP (do Windows):**
```powershell
scp C:\App\nik0finance-base\deploy_vps.sh root@SEU_IP_VPS:/root/
```

### 4️⃣ EXECUTAR INSTALAÇÃO

```bash
bash deploy_vps.sh
```

O script vai:
- ✅ Atualizar sistema
- ✅ Instalar Python 3.11
- ✅ Instalar Node.js 22
- ✅ Instalar Tesseract, FFmpeg, Nginx
- ✅ Criar diretórios
- ⏸️ **PAUSAR para você fazer upload dos arquivos**
- ✅ Instalar dependências Python
- ✅ Instalar dependências Node.js
- ✅ Configurar Nginx
- ✅ Criar serviços systemd
- ✅ Iniciar tudo automaticamente

### 5️⃣ FAZER UPLOAD DOS ARQUIVOS

Quando o script pausar, faça upload:

**Opção A - Via SCP (Windows PowerShell):**
```powershell
scp -r C:\App\nik0finance-base\* root@SEU_IP_VPS:/app/nik0finance/
```

**Opção B - Via FileZilla:**
1. Host: `SEU_IP_VPS`
2. User: `root`
3. Senha: (da VPS)
4. Upload toda pasta `C:\App\nik0finance-base\` para `/app/nik0finance/`

**Opção C - Via Git:**
```bash
cd /app/nik0finance
git clone https://github.com/SEU_USUARIO/seu-repo.git .
```

### 6️⃣ CONTINUAR INSTALAÇÃO

Depois do upload, pressione ENTER no script.

### 7️⃣ PRONTO!

Acesse: `http://SEU_IP_VPS`

---

## 🔧 COMANDOS ÚTEIS

```bash
# Ver logs em tempo real
journalctl -u nik0finance -f

# Ver logs WhatsApp
journalctl -u nik0finance-whatsapp -f

# Reiniciar serviços
systemctl restart nik0finance
systemctl restart nik0finance-whatsapp

# Parar serviços
systemctl stop nik0finance
systemctl stop nik0finance-whatsapp

# Ver status
systemctl status nik0finance
systemctl status nik0finance-whatsapp

# Editar app.py
nano /app/nik0finance/app.py

# Ver processos
htop
```

---

## 🌐 CONFIGURAR DOMÍNIO (Opcional)

### 1. Comprar domínio
- Registro.br: ~R$ 40/ano
- Hostinger: ~R$ 30/ano

### 2. Apontar DNS
No painel do domínio, crie registro A:
```
Tipo: A
Nome: @
Valor: SEU_IP_VPS
TTL: 3600
```

### 3. Ativar HTTPS
```bash
certbot --nginx -d seudominio.com.br
```

O Certbot vai:
- Gerar certificado SSL grátis
- Configurar Nginx automaticamente
- Renovar certificado automaticamente

Pronto! Acesse: `https://seudominio.com.br`

---

## 📱 CONFIGURAR APP MOBILE

Edite no app mobile: `services/api.js`

```javascript
// Se usar IP
const API_BASE_URL = 'http://SEU_IP_VPS';

// Se usar domínio
const API_BASE_URL = 'https://seudominio.com.br';
```

---

## 🔒 SEGURANÇA (Importante!)

### 1. Mudar porta SSH
```bash
nano /etc/ssh/sshd_config
# Mude "Port 22" para "Port 2222"
systemctl restart sshd
```

### 2. Criar firewall
```bash
apt install -y ufw
ufw allow 2222/tcp  # Nova porta SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

### 3. Criar usuário não-root
```bash
adduser nik0admin
usermod -aG sudo nik0admin
```

### 4. Desabilitar login root
```bash
nano /etc/ssh/sshd_config
# Adicione: PermitRootLogin no
systemctl restart sshd
```

---

## 📊 MONITORAMENTO

### Uso de recursos
```bash
# Ver uso de RAM/CPU
htop

# Ver espaço em disco
df -h

# Ver processos Python
ps aux | grep python

# Ver processos Node
ps aux | grep node
```

### Logs importantes
```bash
# Logs Flask
tail -f /var/log/syslog | grep nik0finance

# Logs Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

## 🐛 TROUBLESHOOTING

### App não abre
```bash
# Verificar se serviço está rodando
systemctl status nik0finance

# Ver logs de erro
journalctl -u nik0finance -n 50

# Reiniciar
systemctl restart nik0finance
```

### Porta 80 já em uso
```bash
# Ver quem está usando
lsof -i :80

# Matar processo
kill -9 PID_DO_PROCESSO
```

### Banco de dados não encontrado
```bash
cd /app/nik0finance
ls -la bws_finance.db

# Se não existir, copie do Windows
scp C:\App\nik0finance-base\bws_finance.db root@SEU_IP_VPS:/app/nik0finance/
```

### WhatsApp não conecta
```bash
# Ver logs
journalctl -u nik0finance-whatsapp -f

# Reiniciar
systemctl restart nik0finance-whatsapp

# Verificar porta
lsof -i :3000
```

---

## 📦 BACKUP AUTOMÁTICO

Crie script de backup:
```bash
nano /root/backup.sh
```

Conteúdo:
```bash
#!/bin/bash
tar -czf /root/backup-$(date +%Y%m%d).tar.gz /app/nik0finance/bws_finance.db
# Manter apenas últimos 7 backups
find /root/backup-*.tar.gz -mtime +7 -delete
```

Agende no cron:
```bash
crontab -e
# Adicione: 0 3 * * * /root/backup.sh  # Todo dia às 3h
```

---

## 🚀 MELHORIAS FUTURAS

### 1. Usar PostgreSQL em vez de SQLite
```bash
apt install -y postgresql
# Migrar dados do SQLite para PostgreSQL
```

### 2. Adicionar Redis para cache
```bash
apt install -y redis-server
# Configurar cache no Flask
```

### 3. Load balancer com múltiplas instâncias
```bash
# Rodar 2+ processos Flask
# Nginx distribui requisições
```

---

## 💰 CUSTOS MENSAIS ESTIMADOS

| Item | Preço |
|------|-------|
| VPS Contabo | R$ 27 |
| Domínio .br | R$ 3 (R$ 40/ano) |
| SSL Certificado | R$ 0 (Let's Encrypt grátis) |
| **TOTAL** | **R$ 30/mês** |

---

## 📞 SUPORTE

Se tiver problemas:
1. Veja logs: `journalctl -u nik0finance -f`
2. Verifique status: `systemctl status nik0finance`
3. Teste manualmente: `cd /app/nik0finance && python3 app.py`

---

**✨ Instalação 100% automatizada!**

Basta executar `bash deploy_vps.sh` e seguir as instruções.
