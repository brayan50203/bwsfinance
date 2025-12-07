# 🚀 Início Rápido - WhatsApp Local

## ⚡ 3 Comandos para Começar

### 1️⃣ Instalar Tudo
```powershell
.\INSTALAR_WHATSAPP_LOCAL.bat
```

### 2️⃣ Iniciar Servidores
```powershell
.\START_WHATSAPP_LOCAL.bat
```

### 3️⃣ Conectar WhatsApp
1. Abrir: http://localhost:3000
2. Escanear QR Code
3. Pronto! ✅

---

## 📱 Cadastrar seu WhatsApp

```powershell
python
```

```python
from app import get_db

db = get_db()
db.execute("UPDATE users SET phone = '+5511999999999' WHERE email = 'seu@email.com'")
db.commit()
db.close()
print("✅ WhatsApp cadastrado!")
exit()
```

---

## 🧪 Testar

Envie mensagem para o número conectado:

```
Paguei R$ 50,00 no mercado
```

**Resposta esperada:**
```
✅ Transação adicionada!

💰 Valor: R$ 50,00
📅 Data: 04/12/2025
📂 Categoria: Supermercado
📝 Descrição: mercado
🏦 Conta: Conta Principal
```

---

## 🎯 O que você pode fazer

### ✍️ Registrar Gastos
```
Gastei 150 reais na farmácia
Paguei 80 no uber
Comprei gasolina por 300
```

### 💰 Registrar Receitas
```
Recebi 5000 de salário
Ganhei 300 de freelance
```

### 💬 Fazer Perguntas
```
Quanto gastei esse mês?
Qual meu saldo?
Como estão meus investimentos?
```

### 🎤 Enviar Áudio
Grave dizendo: "Paguei cinquenta reais no mercado"

### 📸 Enviar Foto
Tire foto do recibo e envie

---

## 🔧 Requisitos Mínimos

- ✅ Windows 10/11
- ✅ Python 3.11+
- ✅ Node.js 18+
- ✅ 2 GB de RAM livre
- ✅ 1 GB de espaço em disco

**Opcional para funcionalidades extras:**
- Tesseract (para fotos de recibos)
- FFmpeg (para mensagens de áudio)

---

## ❓ Problemas Comuns

### Erro: "Tesseract não encontrado"
```powershell
choco install tesseract
```

### Erro: "FFmpeg não encontrado"
```powershell
choco install ffmpeg
```

### Porta 80 em uso
```powershell
# Usar porta 8080
$env:PORT=8080
python app.py
```

### WhatsApp desconecta
- Manter celular com internet
- Não usar WhatsApp Web em outro PC simultaneamente

---

## 📚 Documentação

- **WHATSAPP_LOCAL_SETUP.md** - Configuração completa
- **WHATSAPP_REGISTRO_AUTOMATICO.md** - Como funciona
- **WHATSAPP_FLUXO_DIAGRAMA.md** - Arquitetura

---

## 🎉 Pronto!

Seu sistema está **100% local** e funcionando!

**Suporte:** Consulte os arquivos `.md` para mais detalhes.

---

**Atualizado:** 04/12/2025 🚀
