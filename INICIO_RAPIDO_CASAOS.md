# 🚀 INÍCIO RÁPIDO - CasaOS

Guia express para instalar o BWS Finance no CasaOS.

---

## ⚡ **3 Passos Simples**

### **1️⃣ Transferir Arquivos (Windows → CasaOS)**

```powershell
# No Windows, criar pacote
cd C:\App\nik0finance-base
tar -czf bws-finance.tar.gz *

# Transferir via WinSCP para CasaOS:
# - Destino: /DATA/AppData/bws-finance/
```

### **2️⃣ Extrair e Configurar (CasaOS)**

```bash
# SSH no CasaOS
ssh usuario@IP_CASAOS

# Extrair
cd /DATA/AppData
sudo tar -xzf bws-finance.tar.gz

# Ajustar permissões
sudo chown -R $USER:$USER bws-finance
cd bws-finance
```

### **3️⃣ Instalar no CasaOS**

**Via Interface (FÁCIL):**
1. Abra CasaOS: `http://IP_CASAOS`
2. App Store → **+ Custom Install**
3. Cole conteúdo de `docker-compose.casaos.yml`
4. Click **Install**
5. Aguarde build (~5 min)
6. Acesse: `http://IP_CASAOS:8080`

**Via Terminal (AVANÇADO):**
```bash
cd /DATA/AppData/bws-finance
docker-compose -f docker-compose.casaos.yml up -d
```

---

## 🎯 **O que você precisa:**

### **Hardware:**
- 💻 PC antigo / Raspberry Pi / Mini PC
- 💾 4GB RAM mínimo (8GB ideal)
- 💿 32GB armazenamento (SSD recomendado)
- 🌐 Conexão ethernet

### **Software:**
- 🐧 Linux (Ubuntu/Debian)
- 🏠 CasaOS instalado: `curl -fsSL https://get.casaos.io | sudo bash`
- 🔧 WinSCP (Windows) para transferir arquivos

---

## 📁 **Arquivos Importantes Criados:**

| Arquivo | Descrição |
|---------|-----------|
| `docker-compose.casaos.yml` | ⭐ Config otimizada para CasaOS |
| `INSTALACAO_CASAOS.md` | 📘 Guia completo de instalação |
| `MIGRACAO_WINDOWS_CASAOS.md` | 🔄 Como migrar do Windows |
| `INICIO_RAPIDO_CASAOS.md` | ⚡ Este guia (início rápido) |

---

## ✅ **Checklist Rápido:**

- [ ] CasaOS instalado no servidor
- [ ] Arquivos transferidos para `/DATA/AppData/bws-finance/`
- [ ] Permissões ajustadas (`chown`)
- [ ] App instalada via CasaOS interface
- [ ] Acessível em `http://IP:8080`
- [ ] WhatsApp QR code escaneado
- [ ] Login funciona
- [ ] Dados migrados (se aplicável)

---

## 🔗 **URLs Importantes:**

```
🏠 CasaOS Dashboard:  http://IP_CASAOS
💰 BWS Finance:       http://IP_CASAOS:8080
📊 Dashboard:         http://IP_CASAOS:8080/dashboard
💬 WhatsApp Chat:     http://IP_CASAOS:8080/whatsapp-chat
```

---

## 🆘 **Comandos Úteis:**

```bash
# Ver logs
docker logs bws-finance-backend -f
docker logs bws-whatsapp-server -f

# Reiniciar
docker restart bws-finance-backend

# Status
docker ps

# Parar tudo
docker-compose -f docker-compose.casaos.yml down

# Iniciar tudo
docker-compose -f docker-compose.casaos.yml up -d
```

---

## 💡 **Diferenças vs Windows:**

| Item | Windows | CasaOS |
|------|---------|--------|
| **Porta** | 80 ou 5000 | 8080 |
| **Caminho** | `C:\App\nik0finance-base\` | `/DATA/AppData/bws-finance/` |
| **Gerenciamento** | Docker Desktop | CasaOS Web UI |
| **Disponibilidade** | Quando PC ligado | 24/7 |
| **Consumo** | ~150W | ~10W |

---

## 🎯 **Próximos Passos Após Instalação:**

1. ✅ Teste login
2. ✅ Configure WhatsApp (QR code)
3. ✅ Migre dados (se vindo do Windows)
4. ✅ Configure backup automático
5. ✅ Teste por 7 dias
6. ✅ Adicione outras apps no CasaOS

---

## 📚 **Documentação Completa:**

- **Instalação detalhada**: `INSTALACAO_CASAOS.md`
- **Migração do Windows**: `MIGRACAO_WINDOWS_CASAOS.md`
- **Deploy local Docker**: `DEPLOY_LOCAL_DOCKER.md`
- **Adicionar mais apps**: `COMO_ADICIONAR_MAIS_APPS.md`

---

**Tudo pronto! Em 10 minutos seu sistema está no ar! 🚀**

**Dúvidas?** Consulte os guias detalhados acima.
