# 🚀 DEPLOY IMEDIATO - Nik0Finance

## ✅ GitHub Configurado!

Seu código está em: **https://github.com/brayan50203/bwsfinance**

---

## 📋 PRÓXIMOS PASSOS

### 1️⃣ Comprar VPS (5 minutos)

**OPÇÃO A - Contabo (Recomendado)**
- Acesse: https://contabo.com/en/vps/
- Escolha: **VPS S SSD** (€4.50/mês = ~R$ 27/mês)
- Sistema: **Ubuntu 22.04 LTS**
- Anote: IP e senha root (enviados por email)

**OPÇÃO B - Oracle Cloud (GRÁTIS)**
- Acesse: https://cloud.oracle.com/
- Crie conta gratuita
- Crie instância: **VM.Standard.A1.Flex** (ARM, 24GB RAM, FREE)
- ⚠️ Performance irregular, mas 100% gratuito

---

### 2️⃣ Conectar na VPS (30 segundos)

**Windows (PowerShell):**
```powershell
ssh root@SEU_IP_VPS
# Digite a senha quando pedir
```

**Primeira vez:** Digite `yes` quando perguntar sobre fingerprint

---

### 3️⃣ Instalar Tudo Automaticamente (5 minutos)

**Cole este comando completo na VPS:**

```bash
curl -o install.sh https://raw.githubusercontent.com/brayan50203/bwsfinance/main/install_vps_github.sh && bash install.sh
```

**O que vai acontecer:**
1. ✅ Atualiza sistema Ubuntu
2. ✅ Instala Python 3.11
3. ✅ Instala Node.js 22
4. ✅ Instala Tesseract OCR (ler PDFs)
5. ✅ Instala FFmpeg (áudios WhatsApp)
6. ✅ Clona código do GitHub automaticamente
7. ✅ Instala todas dependências Python
8. ✅ Instala todas dependências Node.js
9. ✅ Configura Nginx (web server)
10. ✅ Configura autostart (reinicia sozinho)

**Tempo total:** ~5 minutos

---

### 4️⃣ Acessar Sistema (IMEDIATO)

Abra navegador em:
```
http://SEU_IP_VPS
```

**Login padrão:**
- **Usuário:** `admin@nik0finance.com`
- **Senha:** `admin123`

⚠️ **Mude a senha imediatamente após primeiro login!**

---

## 🔧 Comandos Úteis na VPS

### Ver se está rodando:
```bash
systemctl status nik0finance
systemctl status nik0whatsapp
```

### Ver logs em tempo real:
```bash
# Flask
journalctl -u nik0finance -f

# WhatsApp
journalctl -u nik0whatsapp -f
```

### Reiniciar serviços:
```bash
systemctl restart nik0finance
systemctl restart nik0whatsapp
```

### Parar serviços:
```bash
systemctl stop nik0finance
systemctl stop nik0whatsapp
```

### Atualizar código (quando fizer mudanças):
```bash
cd /root/nik0finance
git pull
systemctl restart nik0finance
systemctl restart nik0whatsapp
```

---

## 📱 Configurar WhatsApp Bot

1. Acesse: `http://SEU_IP_VPS/whatsapp-qrcode`
2. Escaneie QR Code com WhatsApp
3. Pronto! Bot ativo

**Comandos WhatsApp:**
- Envie áudio: "Gastei 50 reais no mercado"
- Envie texto: "Despesa: 100 - Supermercado - Débito"
- Consulta: "Saldo"
- Listar: "Últimas transações"

---

## 🌐 Configurar Domínio (OPCIONAL)

### 1. Comprar domínio:
- Registro.br: ~R$ 40/ano
- Godaddy: ~R$ 50/ano

### 2. Configurar DNS:
Crie registro **A**:
```
Nome: @
Tipo: A
Valor: SEU_IP_VPS
TTL: 3600
```

### 3. Configurar SSL (HTTPS):
```bash
# Na VPS, execute:
apt install certbot python3-certbot-nginx -y
certbot --nginx -d seudominio.com.br
```

Pronto! Acesse: `https://seudominio.com.br`

---

## 🔒 Segurança Essencial

### Mudar senha root da VPS:
```bash
passwd
```

### Criar novo usuário admin:
```bash
adduser deploy
usermod -aG sudo deploy
```

### Configurar firewall:
```bash
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw enable
```

---

## 📊 App Mobile (Já Criado!)

O app está em: `C:\App\nik0finance-mobile`

**Para gerar APK:**
```bash
cd C:\App\nik0finance-mobile
npm install -g eas-cli
eas login
eas build --platform android
```

**Para testar agora:**
```bash
npm start
# Escaneie QR Code com Expo Go
```

---

## 💰 Custos Mensais

| Item | Preço | Necessário? |
|------|-------|-------------|
| VPS Contabo | €4.50 (~R$ 27) | ✅ SIM |
| Domínio | R$ 3.33 (40/12) | ❌ OPCIONAL |
| SSL | GRÁTIS (Let's Encrypt) | ✅ SE TEM DOMÍNIO |
| **TOTAL MÍNIMO** | **R$ 27/mês** | |

**Oracle Free:** R$ 0/mês (mas menos estável)

---

## 🆘 Troubleshooting

### Sistema não abre no navegador?
```bash
# Verificar se Nginx está rodando
systemctl status nginx

# Verificar se Flask está rodando
systemctl status nik0finance

# Ver logs de erro
journalctl -u nik0finance -n 50
```

### Erro "Connection Refused"?
```bash
# Verificar firewall
ufw status

# Liberar porta 80
ufw allow 80
```

### WhatsApp desconecta?
```bash
# Ver logs
journalctl -u nik0whatsapp -n 100

# Reiniciar
systemctl restart nik0whatsapp

# Gerar novo QR Code
curl http://localhost:3000/api/whatsapp/qr
```

### Importação de PDF não funciona?
```bash
# Verificar Tesseract
tesseract --version

# Se não instalou, reinstalar
apt install tesseract-ocr tesseract-ocr-por -y
```

---

## 📞 Suporte

**Repositório:** https://github.com/brayan50203/bwsfinance

**Documentação completa:**
- `AI_QUICKSTART.md` - Guia rápido IA
- `CASAOS_QUICK_START.md` - Deploy alternativo
- `DASHBOARD_README.md` - Dashboard investidor10
- `GPT_ASSISTANT_README.md` - Assistente GPT

---

## ✨ Funcionalidades Instaladas

✅ Dashboard financeiro completo
✅ Gestão de contas e cartões
✅ Transações com parcelamento
✅ Importação OFX/CSV/PDF automática
✅ OCR para ler extratos em PDF
✅ Categorização automática com IA
✅ WhatsApp Bot (voz + texto)
✅ Transações recorrentes
✅ Análise de investimentos
✅ Integração Investidor10
✅ App mobile React Native
✅ API REST completa
✅ Multi-usuário (tenants)
✅ Backup automático

---

## 🚀 DEPLOY RÁPIDO (RESUMO)

```bash
# 1. Compre VPS Contabo
# 2. SSH root@IP_VPS
# 3. Execute:
curl -o install.sh https://raw.githubusercontent.com/brayan50203/bwsfinance/main/install_vps_github.sh && bash install.sh

# 4. Acesse: http://IP_VPS
# 5. Login: admin@nik0finance.com / admin123
```

**Tempo total:** 10 minutos (5 comprar VPS + 5 instalar)

---

**✅ Tudo pronto! Basta seguir os passos acima.**
