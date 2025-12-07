# 🔄 Migração Windows → CasaOS

Guia passo-a-passo para migrar o BWS Finance do Windows para CasaOS.

---

## 📊 **Situação Atual**

- ✅ BWS Finance rodando no Windows
- ✅ Docker Compose configurado
- ✅ Banco SQLite com dados
- ✅ WhatsApp configurado

**Meta:** Mover tudo para CasaOS sem perder dados.

---

## 🎯 **Estratégia de Migração**

### **Fase 1: Preparação (Windows)**
### **Fase 2: Transferência**
### **Fase 3: Instalação (CasaOS)**
### **Fase 4: Validação**
### **Fase 5: Limpeza**

---

## 📦 **FASE 1: Preparação (Windows)**

### **1.1 Parar serviços**

```powershell
cd C:\App\nik0finance-base

# Parar tudo
docker-compose down

# Ou manualmente
Get-Process -Name node -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force
```

### **1.2 Backup do banco de dados**

```powershell
# Criar pasta de backup
mkdir C:\App\nik0finance-base\backup

# Copiar banco
Copy-Item bws_finance.db backup\bws_finance_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').db

# Verificar
Get-ChildItem backup\
```

### **1.3 Backup dos tokens WhatsApp**

```powershell
# Comprimir tokens
cd whatsapp_server
Compress-Archive -Path tokens\ -DestinationPath ..\backup\whatsapp_tokens.zip

# Voltar
cd ..
```

### **1.4 Criar pacote completo**

```powershell
# Excluir node_modules e __pycache__ (serão recriados)
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force __pycache__ -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force whatsapp_server\node_modules -ErrorAction SilentlyContinue

# Criar arquivo compactado
cd C:\App
tar -czf bws-finance-completo.tar.gz nik0finance-base\

# Verificar tamanho
Get-Item bws-finance-completo.tar.gz | Select-Object Name, @{Name="Size(MB)";Expression={[math]::Round($_.Length/1MB,2)}}
```

---

## 🚀 **FASE 2: Transferência**

### **Opção A: Via WinSCP (Recomendado)**

#### **2.A.1 Instalar WinSCP**

```powershell
# Download: https://winscp.net/eng/download.php
# Ou via Chocolatey:
choco install winscp
```

#### **2.A.2 Conectar no CasaOS**

1. Abra WinSCP
2. Preencha:
   - **Host**: IP do CasaOS (ex: 192.168.1.100)
   - **User**: seu usuário SSH
   - **Password**: sua senha
   - **Port**: 22
3. Click **Login**

#### **2.A.3 Transferir arquivo**

1. Navegue até `C:\App\`
2. Arraste `bws-finance-completo.tar.gz` para `/tmp/` no CasaOS
3. Aguarde upload (pode demorar dependendo do tamanho)

### **Opção B: Via SCP (Linha de comando)**

```powershell
# Instalar OpenSSH (se não tiver)
Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0

# Transferir
scp C:\App\bws-finance-completo.tar.gz usuario@IP_CASAOS:/tmp/

# Exemplo:
scp C:\App\bws-finance-completo.tar.gz brayan@192.168.1.100:/tmp/
```

### **Opção C: Via Samba (Compartilhamento de rede)**

#### **No CasaOS:**

```bash
# Instalar Samba
sudo apt update
sudo apt install samba -y

# Criar compartilhamento
sudo mkdir -p /DATA/Share
sudo chmod 777 /DATA/Share

# Configurar
sudo nano /etc/samba/smb.conf
```

Adicione:

```ini
[Share]
path = /DATA/Share
browseable = yes
read only = no
guest ok = yes
```

Reinicie:

```bash
sudo systemctl restart smbd
```

#### **No Windows:**

1. Abra `\\IP_CASAOS\Share` no Explorer
2. Arraste `bws-finance-completo.tar.gz`

---

## 🏠 **FASE 3: Instalação (CasaOS)**

### **3.1 SSH no CasaOS**

```bash
ssh usuario@IP_CASAOS
```

### **3.2 Extrair arquivos**

```bash
# Criar diretório
sudo mkdir -p /DATA/AppData/bws-finance

# Extrair
cd /DATA/AppData
sudo tar -xzf /tmp/bws-finance-completo.tar.gz

# Renomear se necessário
sudo mv nik0finance-base bws-finance

# Verificar
ls -la bws-finance/
```

### **3.3 Ajustar permissões**

```bash
# Dar ownership ao seu usuário
sudo chown -R $USER:$USER /DATA/AppData/bws-finance

# Ajustar permissões
chmod -R 755 /DATA/AppData/bws-finance

# Criar diretórios que faltam
cd /DATA/AppData/bws-finance
mkdir -p logs temp static/uploads
```

### **3.4 Restaurar tokens WhatsApp**

```bash
cd /DATA/AppData/bws-finance

# Se fez backup dos tokens
unzip backup/whatsapp_tokens.zip -d whatsapp_server/

# Ajustar permissões
chmod -R 755 whatsapp_server/tokens/
```

### **3.5 Configurar .env**

```bash
nano .env
```

Cole suas configurações:

```env
SECRET_KEY=seu-secret-key-copiado-do-windows
WHATSAPP_AUTH_TOKEN=bws_finance_token_55653
FLASK_ENV=production

# Copie todas as outras variáveis do seu .env Windows
```

### **3.6 Usar docker-compose do CasaOS**

```bash
# Copiar versão CasaOS
cp docker-compose.casaos.yml docker-compose.yml

# Ou se quiser manter os dois
# Use: docker-compose -f docker-compose.casaos.yml
```

### **3.7 Build e iniciar**

```bash
cd /DATA/AppData/bws-finance

# Build (primeira vez demora)
docker-compose build

# Iniciar
docker-compose up -d

# Ver logs
docker-compose logs -f
```

---

## ✅ **FASE 4: Validação**

### **4.1 Verificar containers**

```bash
docker ps

# Deve mostrar 3 containers rodando:
# - bws-nginx
# - bws-finance-backend
# - bws-whatsapp-server
```

### **4.2 Testar acesso web**

No navegador do Windows:

```
http://IP_CASAOS:8080
```

Deve abrir a página de login.

### **4.3 Testar login**

Use suas credenciais existentes:
- Email: `brayan@bws.com`
- Senha: `123456` (ou a que você configurou)

### **4.4 Verificar dados**

- ✅ Transações aparecem?
- ✅ Contas aparecem?
- ✅ Dashboard funciona?
- ✅ Gráficos carregam?

### **4.5 Testar WhatsApp**

```bash
# Ver logs WhatsApp
docker logs bws-whatsapp-server -f
```

Se QR code aparecer, escaneie novamente.

Se token foi preservado, deve conectar automaticamente.

### **4.6 Enviar mensagem teste**

Do seu celular, envie para o bot:
```
Olá
```

Deve responder com menu.

### **4.7 Testar transação via WhatsApp**

```
Gastei 50 reais no mercado
```

Verifique se aparece no dashboard web.

---

## 🧹 **FASE 5: Limpeza**

### **5.1 No CasaOS: Limpar arquivos temporários**

```bash
# Remover arquivo transferido
sudo rm /tmp/bws-finance-completo.tar.gz

# Limpar Docker
docker system prune -f
```

### **5.2 No Windows: Desativar (não deletar ainda)**

```powershell
cd C:\App\nik0finance-base

# Parar tudo
docker-compose down

# Renomear pasta (backup temporário)
cd C:\App
Rename-Item nik0finance-base nik0finance-base.OLD
```

### **5.3 Aguardar período de teste (7 dias)**

Use apenas o CasaOS por 1 semana.

Se tudo funcionar perfeitamente:

```powershell
# Depois de 7 dias, pode deletar
Remove-Item -Recurse -Force C:\App\nik0finance-base.OLD
```

---

## 🔄 **Rollback (Se algo der errado)**

### **Voltar para Windows**

```powershell
# Restaurar nome original
cd C:\App
Rename-Item nik0finance-base.OLD nik0finance-base

# Iniciar
cd nik0finance-base
docker-compose up -d
```

### **Restaurar backup banco**

```powershell
cd C:\App\nik0finance-base

# Copiar backup
Copy-Item backup\bws_finance_backup_YYYYMMDD_HHMMSS.db bws_finance.db

# Reiniciar
docker-compose restart bws-backend
```

---

## 📊 **Comparação Pós-Migração**

| Aspecto | Windows (Antes) | CasaOS (Depois) |
|---------|-----------------|-----------------|
| **Consumo energia** | ~150-300W | ~10-30W |
| **Disponibilidade** | Quando PC ligado | 24/7 |
| **Performance** | Boa | Excelente |
| **Gerenciamento** | Docker Desktop | Interface CasaOS |
| **Outras apps** | Conflitos possíveis | Isoladas |
| **Backup** | Manual | Automatizável |
| **Acesso** | LAN | LAN + VPN/Cloud |

---

## 🎯 **Checklist Final**

Antes de considerar migração completa:

- [ ] CasaOS acessível via http://IP:8080
- [ ] Login funciona
- [ ] Dashboard carrega dados corretos
- [ ] Transações aparecem
- [ ] Contas listadas corretamente
- [ ] WhatsApp conecta
- [ ] Bot responde mensagens
- [ ] Transações via WhatsApp funcionam
- [ ] AI analisa gastos
- [ ] Gráficos funcionam
- [ ] Upload de comprovantes funciona
- [ ] Notificações funcionam (se configuradas)
- [ ] Testado por 7+ dias sem problemas

---

## 💡 **Dicas Finais**

1. **Mantenha backup do Windows por 30 dias**
2. **Configure backup automático no CasaOS**
3. **Documente suas senhas e configs**
4. **Teste tudo antes de deletar Windows**
5. **Configure VPN se quiser acesso externo**
6. **Use domínio local (.local) para facilitar**
7. **Monitore logs primeiros dias**

---

## 🆘 **Suporte Durante Migração**

### **Problemas comuns:**

**1. Banco não abre no CasaOS**
```bash
# Verificar permissões
ls -la bws_finance.db
# Deve ser seu usuário, não root

# Corrigir
sudo chown $USER:$USER bws_finance.db
chmod 644 bws_finance.db
```

**2. WhatsApp não conecta**
```bash
# Limpar tokens e reconectar
rm -rf whatsapp_server/tokens/*
docker restart bws-whatsapp-server
docker logs bws-whatsapp-server -f
# Escanear novo QR
```

**3. Porta 8080 ocupada**
```bash
# Ver quem usa
sudo netstat -tlnp | grep 8080

# Mudar porta no docker-compose.yml
ports:
  - "8081:80"  # Usar 8081
```

---

**Migração completa! Bem-vindo ao CasaOS! 🎉**

Agora você tem:
- ✅ Sistema rodando 24/7
- ✅ Baixo consumo de energia
- ✅ Fácil de gerenciar
- ✅ Pronto para adicionar mais apps
