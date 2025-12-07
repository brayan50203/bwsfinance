# 🚀 WhatsApp - Guia Rápido

## Como Usar em 3 Passos

### 1️⃣ Registrar Gasto
Envie uma mensagem simples:
```
Paguei 50 reais no mercado
```

### 2️⃣ Registrar Receita
```
Recebi 3000 de salário
```

### 3️⃣ Fazer Perguntas
```
Quanto gastei esse mês?
```

---

## 📱 Tipos de Mensagem Suportados

### ✍️ Texto
```
Gastei R$ 150 na farmácia
Comprei uma pizza de 45 reais
Paguei 80 no uber
```

### 🎤 Áudio
Grave dizendo:
> "Paguei cinquenta reais no posto"

### 📸 Foto
Tire foto do recibo e envie

### 📄 PDF
Envie extrato bancário em PDF

---

## 💡 Exemplos Práticos

| O que você quer | Mensagem |
|----------------|----------|
| Registrar compra | `Gastei 100 reais no mercado` |
| Registrar salário | `Recebi 5000 de salário` |
| Pagar conta | `Paguei 200 de luz` |
| Abastecer carro | `Gastei 300 em gasolina` |
| Almoço fora | `Paguei 35 no restaurante` |
| Ver saldo | `Qual meu saldo?` |
| Ver gastos | `Quanto gastei esse mês?` |
| Ver investimentos | `Como estão meus investimentos?` |

---

## ⚡ Atalhos

### Palavras-chave para Categorias

| Palavra | Categoria Detectada |
|---------|-------------------|
| mercado, supermercado | 🛒 Supermercado |
| gasolina, posto, combustível | ⛽ Combustível |
| uber, taxi, 99 | 🚕 Transporte |
| restaurante, almoço, jantar | 🍽️ Alimentação |
| farmácia, remédio | 💊 Saúde |
| luz, energia | 💡 Contas |
| água | 💧 Contas |
| internet, wifi | 🌐 Contas |
| netflix, spotify, amazon | 📺 Streaming |
| academia, gym | 💪 Saúde |
| salário | 💼 Receita |

### Palavras-chave para Contas/Cartões

| Palavra | Detectado |
|---------|-----------|
| "no cartão" | Cartão de crédito |
| "no débito" | Conta corrente |
| "no nubank" | Conta/Cartão Nubank |
| "no inter" | Conta Inter |

**Exemplo:**
```
Paguei 50 reais no mercado no cartão do nubank
```
→ Detecta: Valor, Categoria, Cartão Nubank

---

## 🎯 Dicas para Mensagens Eficazes

### ✅ Boas Mensagens
```
✅ Gastei 50 reais no mercado hoje
✅ Paguei R$ 135,00 na farmácia
✅ Comprei gasolina por 300
✅ Recebi 3000 de salário
```

### ❌ Mensagens Ruins
```
❌ Fui ao mercado (sem valor)
❌ Paguei conta (qual conta? quanto?)
❌ Gastei dinheiro (quanto? onde?)
```

---

## 🔧 Configuração Inicial

### 1. Cadastrar seu WhatsApp

Execute no terminal:
```bash
python -c "from app import get_db; db = get_db(); db.execute('UPDATE users SET phone = \"+5511999999999\" WHERE email = \"seu@email.com\"'); db.commit(); print('✅ WhatsApp cadastrado!')"
```

### 2. Iniciar Servidores

```powershell
# Iniciar tudo de uma vez
START_TUDO_INTEGRADO.bat
```

Ou separadamente:
```powershell
# Terminal 1: Flask
$env:PORT=80
python app.py

# Terminal 2: WhatsApp
cd whatsapp_server
npm start
```

### 3. Conectar WhatsApp

1. Abrir: http://localhost:3000
2. Escanear QR Code
3. Aguardar: "✅ Conectado!"

### 4. Testar

Envie: `Paguei 50 reais no mercado`

---

## ❓ FAQ

**P: Posso enviar áudio?**  
R: Sim! O sistema transcreve automaticamente com Whisper AI.

**P: Funciona com fotos de recibo?**  
R: Sim! Usa OCR (Tesseract) para extrair texto da imagem.

**P: Posso enviar extrato em PDF?**  
R: Sim! O sistema extrai todas as transações automaticamente.

**P: Como fazer perguntas?**  
R: Basta enviar qualquer pergunta como "Quanto gastei?" ou "Qual meu saldo?"

**P: Preciso especificar a categoria?**  
R: Não! A IA detecta automaticamente baseado em palavras-chave.

**P: E se eu não quiser usar a IA?**  
R: Você pode desabilitar nas configurações, mas perderá a detecção automática.

**P: Posso usar em múltiplos telefones?**  
R: Sim! Cada usuário pode cadastrar seu próprio número de WhatsApp.

---

## 🆘 Problemas Comuns

### "Transação não foi registrada"

**Solução:**
1. Verificar se seu número está cadastrado
2. Verificar logs: `logs/whatsapp.log`
3. Incluir valor na mensagem: `Paguei R$ 50`

### "OCR não funciona"

**Solução:**
```bash
# Instalar Tesseract
choco install tesseract
```

### "Áudio não transcreve"

**Solução:**
```bash
# Instalar FFmpeg
choco install ffmpeg
```

---

## 📚 Documentação Completa

Para mais detalhes técnicos, veja:
- `WHATSAPP_REGISTRO_AUTOMATICO.md` - Documentação completa
- `AI_SYSTEM_DOCUMENTATION.md` - Sistema de IA
- `AI_QUICKSTART.md` - Guia rápido da IA

---

**Desenvolvido por:** Brayan Barbosa  
**Versão:** 1.0 (Beta)  
**Última Atualização:** 19/12/2024 🚀
