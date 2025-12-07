# 📱 WhatsApp Integration - BWSFinance

Integração **100% local e gratuita** entre WhatsApp e BWSFinance para registro automático de transações via mensagens de texto, áudio, imagens e PDFs.

## 🎯 Funcionalidades

✅ **Mensagens de Texto**: "Paguei R$ 50 no mercado hoje"
✅ **Áudios**: Transcrição automática com Whisper
✅ **Imagens**: OCR de notas fiscais e comprovantes
✅ **PDFs**: Extração de extratos bancários
✅ **IA Local**: Classificação automática de categorias
✅ **Zero Custo**: Todas as ferramentas são gratuitas

## 📋 Requisitos do Sistema

### Software Necessário

```bash
# Python 3.10+
python --version

# Node.js 16+
node --version

# FFmpeg (conversão de áudio)
ffmpeg -version

# Tesseract OCR (extração de texto de imagens)
tesseract --version
```

## 🚀 Instalação Completa

### 1. Instalar Dependências do Sistema

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install -y \
    python3-pip \
    nodejs npm \
    ffmpeg \
    tesseract-ocr \
    tesseract-ocr-por \
    git
```

**Windows:**
```powershell
# Instalar via Chocolatey
choco install python nodejs ffmpeg tesseract

# Ou baixar manualmente:
# Python: https://python.org
# Node.js: https://nodejs.org
# FFmpeg: https://ffmpeg.org
# Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
```

**macOS:**
```bash
brew install python node ffmpeg tesseract tesseract-lang
```

### 2. Clonar e Configurar Projeto

```bash
cd c:/App/nik0finance-base

# Criar ambiente virtual Python
python -m venv venv

# Ativar (Linux/Mac)
source venv/bin/activate

# Ativar (Windows)
.\venv\Scripts\activate

# Instalar dependências Python
pip install -r requirements_whatsapp.txt
```

### 3. Instalar Dependências Python

Criar `requirements_whatsapp.txt`:

```txt
flask==3.0.0
python-dotenv==1.0.0
pillow==10.1.0
pytesseract==0.3.10
pdfplumber==0.10.3
openai-whisper==20231117
requests==2.31.0
```

```bash
pip install -r requirements_whatsapp.txt
```

### 4. Instalar Modelo Whisper

```bash
# Download automático no primeiro uso
# Ou manual:
python -c "import whisper; whisper.load_model('small')"
```

### 5. Configurar Node.js Server

```bash
cd whatsapp_server
npm install
cd ..
```

### 6. Configurar Variáveis de Ambiente

Copiar `.env.example` para `.env`:

```bash
cp .env.example .env
```

Editar `.env` e configurar:

```env
# Gerar token seguro
WHATSAPP_AUTH_TOKEN=seu_token_secreto_aqui_12345

# Opcional: Limitar remetentes
ALLOWED_SENDERS=+5511999999999
```

## 🎬 Execução

### Opção 1: Manual (Dois Terminais)

**Terminal 1 - Flask:**
```bash
source venv/bin/activate  # ou .\venv\Scripts\activate no Windows
python app.py
```

**Terminal 2 - Node.js:**
```bash
cd whatsapp_server
node index.js
```

### Opção 2: Script Automático (Linux/Mac)

```bash
chmod +x scripts/run_all.sh
./scripts/run_all.sh
```

### Opção 3: PM2 (Produção)

```bash
# Instalar PM2
npm install -g pm2

# Iniciar serviços
pm2 start ecosystem.config.js

# Ver logs
pm2 logs

# Parar
pm2 stop all
```

## 📱 Primeiro Uso - Conectar WhatsApp

1. Inicie o servidor Node.js
2. Um **QR Code** aparecerá no terminal
3. Abra WhatsApp no celular → ⋮ → Aparelhos conectados → Conectar aparelho
4. Escaneie o QR Code
5. Aguarde mensagem de conexão bem-sucedida

## 💬 Como Usar

### Mensagens de Texto

Envie mensagens naturais:

```
Paguei R$ 50,00 no mercado hoje
Gastei 120 reais no Uber ontem
Recebi R$ 1.500,00 de salário dia 5
Aluguel de R$ 800 pago em 01/11/2025
```

### Mensagens de Áudio

Grave um áudio falando:
> "Oi, gastei cinquenta reais no posto de gasolina hoje"

O sistema vai:
1. Baixar o áudio
2. Converter para WAV
3. Transcrever com Whisper
4. Extrair informações
5. Criar transação
6. Enviar confirmação

### Imagens (Notas Fiscais)

Tire foto ou envie imagem de:
- Nota fiscal
- Comprovante de pagamento
- Recibo

O OCR vai extrair:
- Valor total
- Data
- CNPJ/CPF
- Descrição

### PDFs (Extratos Bancários)

Envie extrato bancário em PDF e o sistema vai:
1. Extrair todas as transações
2. Criar múltiplas entradas no banco
3. Classificar automaticamente

## 🧠 Inteligência Artificial

### Extração de Valores

Reconhece formatos:
- `R$ 1.234,56`
- `1234,56 reais`
- `50 reais`
- `cinquenta reais` (por extenso via áudio)

### Extração de Datas

Interpreta:
- `hoje` → data atual
- `ontem` → data de ontem
- `dia 5` → dia 5 do mês atual
- `05/11` → 05 de novembro
- `05/11/2025` → data completa

### Classificação de Categorias

Keywords automáticas:

| Categoria | Keywords |
|-----------|----------|
| 🍽️ Alimentação | mercado, supermercado, ifood, restaurante, padaria |
| 🚗 Transporte | uber, 99, gasolina, combustível, posto |
| 🏠 Moradia | aluguel, condomínio, luz, água, internet |
| ⚕️ Saúde | farmácia, médico, remédio, consulta |
| 🎮 Lazer | cinema, netflix, spotify, viagem |
| 📚 Educação | curso, livro, faculdade, mensalidade |

### Identificação de Contas

Reconhece:
- Nubank, Itaú, Bradesco, Inter
- PicPay, Mercado Pago
- Santander, Banrisul

## 🔧 Troubleshooting

### WhatsApp não conecta

```bash
# Limpar sessão
rm -rf whatsapp_server/tokens

# Reiniciar
node whatsapp_server/index.js
```

### Whisper muito lento

```bash
# Usar modelo menor
# Em .env:
WHISPER_MODEL_SIZE=tiny

# Ou instalar Vosk como fallback
pip install vosk
```

### OCR não funciona

```bash
# Verificar Tesseract
tesseract --version

# Instalar idioma português
sudo apt install tesseract-ocr-por
```

### Erro de permissão

```bash
# Dar permissão à pasta temp
chmod 777 temp
chmod 777 logs
```

## 📊 Logs

Ver logs em tempo real:

```bash
# WhatsApp
tail -f logs/whatsapp.log

# Flask
tail -f logs/flask.log

# Node.js
cd whatsapp_server && npm run dev
```

## 🔐 Segurança

✅ **Tudo Local**: Nenhum dado sai da sua máquina
✅ **Token de Autenticação**: Protege comunicação Node ↔ Flask
✅ **Lista de Permitidos**: Configure `ALLOWED_SENDERS`
✅ **Auto-cleanup**: Arquivos temporários são apagados

### Recomendações:

1. **NÃO exponha** portas 3000 e 5000 na internet
2. Use **VPN** ou **SSH tunnel** para acesso remoto
3. Troque `WHATSAPP_AUTH_TOKEN` para valor seguro
4. Backup regular do banco SQLite

## 🎓 Exemplos de Uso

### Caso 1: Compra no Mercado

**Usuário envia:**
> "Gastei R$ 87,50 no Carrefour hoje"

**Sistema responde:**
```
✅ Transação adicionada!

💰 Valor: R$ 87,50
📅 Data: 2025-11-07
📂 Categoria: Alimentação
📝 Descrição: Gastei R$ 87,50 no Carrefour hoje
```

### Caso 2: Áudio de Despesa

**Usuário grava:**
> 🎤 "Oi, paguei cinquenta reais no posto Shell ontem"

**Sistema:**
1. Transcreve: "paguei cinquenta reais no posto Shell ontem"
2. Extrai: R$ 50,00 + ontem + Transporte
3. Cria transação
4. Confirma por WhatsApp

### Caso 3: Foto de Nota Fiscal

**Usuário envia foto da nota**

**OCR detecta:**
- Valor: R$ 234,90
- Data: 06/11/2025
- CNPJ: XX.XXX.XXX/0001-XX

**Sistema cria transação automaticamente**

## 🚀 Próximos Passos

- [ ] Aprendizado de máquina personalizado
- [ ] Comandos via WhatsApp (`/saldo`, `/extrato`)
- [ ] Gráficos enviados por imagem
- [ ] Multi-usuário com telefone
- [ ] Integração com Open Banking

## 📞 Suporte

Problemas? Abra uma issue ou consulte:
- Logs em `logs/whatsapp.log`
- Documentação do Whisper: https://github.com/openai/whisper
- WPPConnect docs: https://wppconnect.io

---

**Feito com ❤️ para BWSFinance**
