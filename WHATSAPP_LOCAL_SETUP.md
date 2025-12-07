# 🏠 WhatsApp 100% Local - Configuração

## 🎯 Objetivo

Sistema de registro automático de transações via WhatsApp **totalmente local**, sem depender de APIs externas ou internet para processar mensagens.

---

## 📦 O que precisa instalar

### 1. **Python (já instalado)**
```powershell
python --version
# Python 3.11+
```

### 2. **Node.js (já instalado)**
```powershell
node --version
# v18+
```

### 3. **Tesseract OCR (para imagens)**
```powershell
# Instalar com Chocolatey
choco install tesseract

# OU baixar direto:
# https://github.com/UB-Mannheim/tesseract/wiki
# Instalar em: C:\Program Files\Tesseract-OCR
```

### 4. **FFmpeg (para áudios)**
```powershell
# Instalar com Chocolatey
choco install ffmpeg

# OU baixar direto:
# https://www.gyan.dev/ffmpeg/builds/
# Extrair e adicionar ao PATH
```

### 5. **Whisper Offline (modelo local)**
```bash
pip install openai-whisper
```

### 6. **spaCy (NLP local)**
```bash
pip install spacy
python -m spacy download pt_core_news_sm
```

---

## 🔧 Configuração Local

### 1. Instalar Dependências Python

```powershell
cd c:\App\nik0finance-base

pip install openai-whisper
pip install pytesseract
pip install spacy
pip install python-dateutil
pip install pillow

# Baixar modelo português do spaCy
python -m spacy download pt_core_news_sm
```

### 2. Configurar Tesseract

```powershell
# Adicionar ao PATH (se não estiver)
$env:PATH += ";C:\Program Files\Tesseract-OCR"

# Testar
tesseract --version
```

### 3. Baixar Modelo Whisper (LOCAL)

O Whisper baixa modelos na primeira execução. Para usar totalmente local:

```python
# Modelos disponíveis (tamanho vs precisão):
# tiny     - 75 MB  - rápido, menos preciso
# base     - 142 MB - bom equilíbrio
# small    - 466 MB - boa precisão
# medium   - 1.5 GB - alta precisão
# large    - 2.9 GB - máxima precisão

# Recomendado: base (bom equilíbrio)
python
>>> import whisper
>>> model = whisper.load_model("base")
>>> # Modelo será salvo em: C:\Users\<user>\.cache\whisper
```

### 4. Configurar WhatsApp Server

```powershell
cd whatsapp_server
npm install
```

---

## 🚀 Iniciar Sistema Local

### Script Automático (RECOMENDADO)

Crie o arquivo `START_WHATSAPP_LOCAL.bat`:

```batch
@echo off
echo ========================================
echo  WhatsApp BWS Finance - LOCAL
echo ========================================
echo.

REM Verificar Tesseract
where tesseract >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERRO] Tesseract nao encontrado!
    echo Execute: choco install tesseract
    pause
    exit /b 1
)

REM Verificar FFmpeg
where ffmpeg >nul 2>nul
if %errorlevel% neq 0 (
    echo [AVISO] FFmpeg nao encontrado. Audio pode nao funcionar.
    echo Execute: choco install ffmpeg
)

REM Iniciar Flask (porta 80)
echo.
echo [1/2] Iniciando Flask Server (porta 80)...
start "BWS Finance Flask" cmd /k "cd /d %~dp0 && set PORT=80 && python app.py"

REM Aguardar Flask iniciar
timeout /t 5 /nobreak >nul

REM Iniciar WhatsApp Server (porta 3000)
echo [2/2] Iniciando WhatsApp Server (porta 3000)...
start "WhatsApp Server" cmd /k "cd /d %~dp0\whatsapp_server && npm start"

echo.
echo ========================================
echo  Servidores iniciados!
echo ========================================
echo.
echo  Flask:    http://localhost:80
echo  WhatsApp: http://localhost:3000
echo.
echo  Aguarde 10 segundos e abra:
echo  http://localhost:3000
echo.
echo  Escaneie o QR Code com seu WhatsApp
echo ========================================
echo.

timeout /t 3

REM Abrir navegador automaticamente
start http://localhost:3000

exit
```

### Iniciar Manualmente

```powershell
# Terminal 1: Flask
$env:PORT=80
python app.py

# Terminal 2: WhatsApp
cd whatsapp_server
npm start
```

---

## 📱 Conectar WhatsApp

1. **Abrir**: http://localhost:3000
2. **Escanear QR Code** com WhatsApp do celular
3. **Aguardar**: "✅ WhatsApp connected!"

---

## 🧪 Testar Sistema Local

### 1. Cadastrar seu WhatsApp

```powershell
python
```

```python
from app import get_db

db = get_db()

# Substituir pelo SEU número (formato: +5511999999999)
seu_numero = "+5511999999999"
seu_email = "seu@email.com"

db.execute(
    "UPDATE users SET phone = ? WHERE email = ?",
    (seu_numero, seu_email)
)

db.commit()
db.close()

print(f"✅ WhatsApp {seu_numero} cadastrado!")
```

### 2. Enviar Mensagem de Teste

**Enviar para o número conectado:**
```
Paguei R$ 50,00 no mercado hoje
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

### 3. Testar Áudio (LOCAL)

Grave um áudio dizendo:
> "Paguei cinquenta reais no posto de gasolina"

**O sistema irá:**
1. Usar Whisper LOCAL para transcrever
2. Processar com NLP local
3. Registrar automaticamente

### 4. Testar Foto (LOCAL)

Tire uma foto de um recibo e envie.

**O sistema irá:**
1. Usar Tesseract LOCAL para OCR
2. Extrair texto da imagem
3. Classificar e registrar

---

## 🔍 Verificar se está 100% Local

### Checar Processos

```powershell
# Verificar se Whisper está usando modelo local
Get-ChildItem $env:USERPROFILE\.cache\whisper

# Deve mostrar algo como:
# base.pt (142 MB)
```

### Desconectar Internet e Testar

```powershell
# Desabilitar adaptador de rede
Disable-NetAdapter -Name "Wi-Fi" -Confirm:$false

# Testar mensagem via WhatsApp
# (WhatsApp Web precisa de internet, mas o processamento é local)

# Reabilitar
Enable-NetAdapter -Name "Wi-Fi" -Confirm:$false
```

---

## ⚙️ Configurações Locais

### 1. Modelo Whisper (tamanho vs velocidade)

Edite `modules/audio_processor.py`:

```python
class AudioProcessor:
    def __init__(self, whisper_model='base'):  # Mudar aqui
        # Opções: tiny, base, small, medium, large
        self.model = whisper.load_model(whisper_model)
```

**Recomendações:**
- **tiny**: Rápido (2-3s), menos preciso
- **base**: Equilibrado (3-5s), boa precisão ✅ RECOMENDADO
- **small**: Lento (5-10s), alta precisão

### 2. Tesseract (idioma)

Edite `modules/ocr_processor.py`:

```python
class OCRProcessor:
    def __init__(self, language='por'):  # Português
        self.language = language
```

### 3. spaCy (modelo NLP)

```python
# modules/nlp_classifier.py
import spacy

nlp = spacy.load('pt_core_news_sm')  # Modelo local português
```

---

## 📊 Performance Local

| Componente | Tempo | Usa Internet? |
|------------|-------|---------------|
| **NLP Classifier** | 50-100ms | ❌ Não |
| **Whisper (tiny)** | 2-3s | ❌ Não |
| **Whisper (base)** | 3-5s | ❌ Não |
| **Whisper (small)** | 5-10s | ❌ Não |
| **Tesseract OCR** | 500ms-1s | ❌ Não |
| **spaCy NLP** | 50ms | ❌ Não |
| **Banco de Dados** | 10-50ms | ❌ Não |

**Total: 100% Local!** ✅

---

## 🛠️ Estrutura de Arquivos Local

```
c:\App\nik0finance-base\
│
├── app.py                      # Flask server
├── whatsapp_server/           
│   ├── index_v3.js            # WhatsApp bot
│   └── package.json
│
├── modules/                    # Processadores locais
│   ├── nlp_classifier.py      # NLP local (spaCy)
│   ├── audio_processor.py     # Whisper local
│   ├── ocr_processor.py       # Tesseract local
│   └── pdf_processor.py       # PyPDF2 local
│
├── models/                     # Modelos baixados
│   └── (spaCy baixa aqui)
│
└── C:\Users\<user>\.cache\whisper\  # Modelos Whisper
    ├── tiny.pt    (75 MB)
    ├── base.pt    (142 MB)
    └── small.pt   (466 MB)
```

---

## 🔐 Dados 100% Locais

### Banco de Dados
```
c:\App\nik0finance-base\bws_finance.db
```

### Arquivos de Mídia
```
c:\App\nik0finance-base\uploads\
├── audios\      # Áudios do WhatsApp
├── images\      # Fotos de recibos
└── pdfs\        # Extratos PDF
```

### Logs
```
c:\App\nik0finance-base\logs\
└── whatsapp.log  # Logs locais
```

**Tudo fica no seu computador!** 🔒

---

## 📱 WhatsApp Web (Única Dependência Externa)

⚠️ **IMPORTANTE:** O WhatsApp Web **precisa de internet** para funcionar, pois é uma limitação do próprio WhatsApp.

**Mas:**
- ✅ Todo o **processamento** é local
- ✅ Todos os **modelos de IA** são locais
- ✅ Todo o **banco de dados** é local
- ✅ Todos os **arquivos** ficam locais

**Fluxo:**
```
WhatsApp (internet) → WhatsApp Web → Seu PC (100% local)
```

---

## 🚀 Iniciar Agora

### Opção 1: Script Automático
```powershell
.\START_WHATSAPP_LOCAL.bat
```

### Opção 2: Manual
```powershell
# Terminal 1
$env:PORT=80
python app.py

# Terminal 2
cd whatsapp_server
npm start
```

### Opção 3: Porta 8080 (sem admin)
```powershell
# Terminal 1
$env:PORT=8080
python app.py

# Terminal 2
cd whatsapp_server
npm start
```

---

## ✅ Checklist de Verificação

Antes de usar, confirme:

- [ ] Python instalado
- [ ] Node.js instalado
- [ ] Tesseract instalado (`tesseract --version`)
- [ ] FFmpeg instalado (`ffmpeg -version`)
- [ ] Dependências Python instaladas (`pip install -r requirements.txt`)
- [ ] Modelo Whisper baixado (primeira execução baixa automático)
- [ ] Modelo spaCy português (`python -m spacy download pt_core_news_sm`)
- [ ] WhatsApp Server rodando (http://localhost:3000)
- [ ] Flask rodando (http://localhost:80 ou 8080)
- [ ] QR Code escaneado com WhatsApp
- [ ] Número cadastrado no banco de dados

---

## 🎉 Pronto!

Seu sistema WhatsApp agora está **100% local**:

✅ **Sem APIs externas**  
✅ **Sem dependência de internet** (exceto WhatsApp Web)  
✅ **Todos os dados no seu PC**  
✅ **Modelos de IA locais**  
✅ **Processamento local**  

**É só conectar e usar!** 🚀

---

**Última Atualização:** 04/12/2025 🏠
