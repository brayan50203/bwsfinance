# BWS Finance - Deploy Guide

## 📦 **Arquivos para Deploy**

✅ **Criados:**
- `Procfile` - Comando para iniciar o servidor
- `runtime.txt` - Versão do Python
- `requirements.txt` - Atualizado com gunicorn

## 🚀 **Deploy no Render.com**

### **Passo 1: Preparar GitHub**

1. Crie um repositório no GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - BWS Finance"
   git branch -M main
   git remote add origin https://github.com/SEU_USUARIO/bws-finance.git
   git push -u origin main
   ```

### **Passo 2: Deploy no Render**

1. Acesse: https://render.com
2. Crie conta (pode usar GitHub)
3. Clique em **"New +"** → **"Web Service"**
4. Conecte seu repositório GitHub
5. Configure:
   - **Name**: bws-finance
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Plan**: Free

### **Passo 3: Variáveis de Ambiente**

No Render, adicione estas variáveis:

```
FLASK_ENV=production
SECRET_KEY=seu-secret-key-super-seguro-aqui-12345
WHATSAPP_AUTH_TOKEN=bws_finance_token_55653
```

### **Passo 4: Deploy!**

- Clique em **"Create Web Service"**
- Aguarde ~5 minutos
- Seu site estará online! 🎉

---

## 🔧 **Alternativa: Railway.app**

1. Acesse: https://railway.app
2. Login com GitHub
3. **New Project** → **Deploy from GitHub repo**
4. Selecione seu repositório
5. Railway detecta automaticamente Python
6. Adicione as mesmas variáveis de ambiente
7. Deploy automático!

---

## 📱 **E o WhatsApp Bot?**

O bot precisa rodar localmente (no seu PC) porque:
- Precisa escanear QR code
- WPPConnect não funciona bem em servidores cloud

**Solução:**
1. Mantenha o bot rodando no seu PC
2. Configure Flask hospedado para receber webhooks
3. Bot local chama Flask na nuvem

**OU use ngrok** para expor bot local:
```bash
ngrok http 3000
```

---

## 🌐 **Domínio Personalizado** (Opcional)

Render permite domínio grátis:
- `seu-app.onrender.com`

Para domínio próprio:
- Configure DNS apontando para Render
- SSL automático e grátis

---

## 📊 **Banco de Dados**

**Opção 1: SQLite** (arquivos)
- Funciona no Render
- Limitado (dados podem ser perdidos)

**Opção 2: PostgreSQL** (Recomendado)
- Render oferece PostgreSQL grátis
- Mais robusto e confiável
- Precisaria migrar de SQLite

---

## 🎯 **Próximos Passos**

1. ✅ Criar repositório GitHub
2. ✅ Fazer push do código
3. ✅ Criar conta no Render
4. ✅ Deploy
5. ✅ Testar online
6. ✅ Configurar domínio (opcional)

**Quer que eu te ajude com algum desses passos?** 🚀
