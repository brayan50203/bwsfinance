# 🎉 BWS Finance - Sistema Online!

## ✅ Servidor Rodando

O servidor Flask está **online e funcionando** perfeitamente!

### 📍 URLs de Acesso

```
🏠 Dashboard Principal: http://127.0.0.1:5000/dashboard
🌐 Login: http://127.0.0.1:5000/
📊 Transações: http://127.0.0.1:5000/transactions
💰 Investimentos: http://127.0.0.1:5000/investments
📱 WhatsApp Health: http://127.0.0.1:5000/api/whatsapp/health
💳 API Cartões: http://127.0.0.1:5000/api/cards-list
```

### 🚀 Como Iniciar o Servidor

#### Método 1: Script Batch (Recomendado)
```batch
.\start-background.bat
```
Este método:
- Usa `pythonw.exe` (Python sem console)
- Roda em background
- Evita problemas de encoding
- Gera logs em `logs/server_*.log`

#### Método 2: PowerShell Direto
```powershell
pythonw start_silent.py
```

#### Método 3: Docker (Produção)
```bash
docker-compose up -d
```

### 🛑 Como Parar o Servidor

```powershell
taskkill /F /IM pythonw.exe
```

Ou se estiver usando Docker:
```bash
docker-compose down
```

### 📂 Arquivos Importantes

| Arquivo | Descrição |
|---------|-----------|
| `app.py` | Aplicação Flask principal |
| `start_silent.py` | Inicializador com logs |
| `start-background.bat` | Script para rodar em background |
| `scheduler.py` | Agendador de tarefas (transações recorrentes, investimentos) |
| `Dockerfile` | Container Flask |
| `Dockerfile.whatsapp` | Container Node.js WhatsApp |
| `docker-compose.yml` | Orquestração completa |

### 🔧 Solução de Problemas

#### Problema: UnicodeEncodeError no Windows
**Solução**: Usar `pythonw.exe` em vez de `python.exe`
- `pythonw.exe` = Python sem janela de console
- Evita TODOS os problemas de encoding do PowerShell

#### Problema: Porta 5000 já está em uso
```powershell
# Ver processos na porta 5000
netstat -ano | findstr :5000

# Matar processo (substitua <PID> pelo número encontrado)
taskkill /F /PID <PID>
```

#### Problema: Waitress não funciona
**Solução**: Redirecionar stdout/stderr para arquivo ANTES de importar Waitress
```python
sys.stdout = open('log.txt', 'w', encoding='utf-8')
sys.stderr = sys.stdout
```

### 📱 Integração WhatsApp

#### Status Atual
✅ Flask webhook pronto: `/api/whatsapp/webhook`  
✅ Processadores implementados (audio, OCR, PDF, NLP)  
⏳ Node.js server não iniciado (aguardando)  

#### Como Iniciar WhatsApp
```bash
cd whatsapp_server
npm install
node index.js
```

O servidor Node.js irá:
1. Conectar no WhatsApp Web via WPPConnect
2. Mostrar QR code para escanear com celular
3. Receber mensagens (texto, áudio, imagem, PDF)
4. Enviar para Flask em `/api/whatsapp/webhook`
5. Flask processa e responde

#### Tipos de Mensagem Suportados

| Tipo | Processador | Exemplo |
|------|-------------|---------|
| Texto | NLP Classifier | "Gastei R$ 50 no mercado hoje" |
| Áudio | Whisper STT | 🎤 Áudio com descrição da compra |
| Imagem | Tesseract OCR | 📸 Foto de nota fiscal |
| PDF | pdfplumber | 📄 Extrato bancário ou fatura |

### 💳 Import de Faturas de Cartão

#### Como Usar
1. Acesse: http://127.0.0.1:5000/importar-extrato
2. Selecione "Fatura de Cartão de Crédito"
3. Escolha o cartão no dropdown
4. Faça upload do PDF/CSV
5. Sistema irá:
   - Extrair transações automaticamente
   - Vincular ao `card_id` correto
   - Deduzir do limite disponível
   - Criar parcelamentos se houver

#### API Endpoint
```javascript
// Listar cartões disponíveis
GET /api/cards-list

// Resposta:
{
  "cards": [
    {
      "id": "uuid",
      "name": "Nubank Mastercard",
      "card_limit": 5000.00,
      "used_limit": 1200.00,
      "available_limit": 3800.00
    }
  ]
}
```

### 📊 Categorias Simplificadas (17 no total)

#### Receitas (6)
1. Salário
2. Freelance
3. Investimentos
4. Vendas
5. Reembolsos
6. Outros

#### Despesas (11)
1. Transporte
2. Alimentação
3. Moradia
4. Contas
5. Educação
6. Saúde
7. Lazer
8. Compras
9. Impostos
10. Débitos
11. Outros

### 🐳 Deployment Docker

#### Estrutura
```
bws-finance/
├── app.py (Flask)
├── Dockerfile (Python 3.11 + FFmpeg + Tesseract + spaCy)
├── whatsapp_server/
│   ├── index.js (Node.js + WPPConnect)
│   └── Dockerfile.whatsapp (Node 20 + Chromium)
└── docker-compose.yml (Orquestração)
```

#### Comandos
```bash
# Build e start
docker-compose up -d --build

# Ver logs
docker-compose logs -f

# Parar
docker-compose down

# Restart
docker-compose restart
```

### 🖥️ Hospedagem Recomendada

#### Hardware Mínimo
- CPU: Dual-Core 1.5GHz+
- RAM: 1GB (2GB recomendado)
- Disco: 10GB
- OS: Debian 12 Server (250MB RAM idle)

#### Painel de Gestão
- **CasaOS**: Interface web para gerenciar Docker containers
- Guia completo: `INSTALACAO_CASAOS.md` (350+ linhas)

### 🔐 Credenciais Padrão

```
Email: admin@bwsfinance.com
Senha: admin123
```

**⚠️ IMPORTANTE**: Altere as credenciais após primeiro login!

### 📝 Logs

#### Localização
```
logs/
├── server_YYYYMMDD_HHMMSS.log  # Servidor Flask
├── whatsapp.log                 # WhatsApp integration
└── scheduler.log                # Tarefas agendadas
```

#### Visualizar logs em tempo real
```powershell
# Windows
Get-Content logs\server_*.log -Wait -Tail 50

# Linux
tail -f logs/server_*.log
```

### ⏰ Tarefas Agendadas (Scheduler)

| Tarefa | Horário | Descrição |
|--------|---------|-----------|
| Transações Recorrentes | 00:01 | Gera transações mensais automaticamente |
| Atualização de Investimentos | 08:00 | Busca cotações de ações/cripto via API |

#### Executar Manualmente (Admin)
```bash
# Transações recorrentes
POST /api/recurring/execute-now

# Atualização de investimentos
POST /admin/update-investments
```

### 🎯 Próximos Passos

1. ✅ **Servidor Flask rodando** (COMPLETO)
2. ⏳ Iniciar Node.js WhatsApp server
3. ⏳ Testar mensagens WhatsApp (texto, áudio, imagem, PDF)
4. ⏳ Testar import de fatura de cartão
5. ⏳ Deploy em servidor Linux com CasaOS

### 📞 Suporte

Se encontrar problemas:
1. Verifique os logs em `logs/`
2. Confirme que porta 5000 está livre
3. Use `pythonw.exe` para evitar problemas de encoding
4. Considere usar Docker para ambiente isolado

---

**Desenvolvido com ❤️ para BWS Finance**  
Última atualização: 08/11/2025 02:08 AM
