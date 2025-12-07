# 🚀 BWS FINANCE - GUIA DE INICIALIZAÇÃO

## 📋 Scripts Disponíveis

### ⭐ RECOMENDADO - Tudo Integrado na Porta 80
**Arquivo:** `START_TUDO_INTEGRADO.bat`  
**Descrição:** Inicia o sistema completo com landing page integrada  
**Requer:** Executar como Administrador  
**Acesso:**
- 🏠 Landing Page: http://localhost
- 🔐 Login: http://localhost/login
- 📊 Dashboard: http://localhost/dashboard
- 📱 WhatsApp: http://localhost:3000

**Funcionalidade:**
- Landing page bonita para visitantes não autenticados
- Redireciona automaticamente para dashboard se estiver logado
- Todos os recursos do sistema na mesma porta

---

### 🎯 Opção 2 - Sistema Completo (3 Serviços Separados)
**Arquivo:** `START_COMPLETO_PORTA_80.bat`  
**Descrição:** Inicia landing page, Flask e WhatsApp em portas separadas  
**Requer:** Executar como Administrador  
**Acesso:**
- 🏠 Landing: http://localhost (porta 80)
- 📊 Sistema: http://localhost:5000
- 📱 WhatsApp: http://localhost:3000

---

### 🔧 Opção 3 - Porta 8080 (Sem Admin)
**Arquivo:** `START_TUDO_8080.bat`  
**Descrição:** Sistema na porta 8080 - não precisa de administrador  
**Requer:** Apenas duplo clique  
**Acesso:**
- 📊 Sistema: http://localhost:8080
- 📱 WhatsApp: http://localhost:3000

---

### 🎨 Opção 4 - Porta 80 Simples
**Arquivo:** `START_TUDO_PORTA_80.bat`  
**Descrição:** Flask e WhatsApp na porta 80 (sem landing separada)  
**Requer:** Executar como Administrador  
**Acesso:**
- 📊 Sistema: http://localhost
- 📱 WhatsApp: http://localhost:3000

---

## 🎯 Qual Escolher?

### Para PRODUÇÃO ou DEMONSTRAÇÃO:
✅ Use `START_TUDO_INTEGRADO.bat`
- Mais profissional com landing page
- Tudo na porta 80
- Experiência completa

### Para DESENVOLVIMENTO:
✅ Use `START_TUDO_8080.bat`
- Não precisa de admin
- Mais rápido de iniciar
- Fácil de reiniciar

### Para TESTE RÁPIDO:
✅ Use `START_TUDO_PORTA_80.bat`
- Simples e direto
- Sem landing page separada

---

## 📱 Acessar de Outros Dispositivos

Todos os serviços podem ser acessados pela rede local usando o IP do seu PC:
- http://192.168.80.132 (substitua pelo seu IP)
- http://192.168.80.132:5000 (se usando porta 5000)
- http://192.168.80.132:3000 (WhatsApp Bot)

Para descobrir seu IP: `ipconfig` no PowerShell

---

## 🛑 Parar os Serviços

### Método 1 - Fechar Janelas
Feche as janelas do CMD/PowerShell que abriram

### Método 2 - PowerShell
```powershell
Get-Process -Name python,node | Stop-Process -Force
```

### Método 3 - Task Manager
- Ctrl + Shift + Esc
- Encerrar processos: python.exe e node.exe

---

## 🔧 Troubleshooting

### Porta 80 em uso?
- Feche Skype, Apache, IIS ou outros servidores
- Ou use a versão porta 8080

### Erro de permissão?
- Clique com botão direito → "Executar como Administrador"

### WhatsApp não conecta?
- Aguarde 30 segundos após iniciar
- Verifique se apareceu QR code no terminal
- Escaneie com WhatsApp do celular

### Flask não inicia?
- Verifique se tem Python instalado: `python --version`
- Instale dependências: `pip install -r requirements.txt`

---

## 💡 Dicas

1. **Landing Page Automática**: A página inicial é exibida automaticamente para visitantes. Quando você faz login, é redirecionado para o dashboard.

2. **Modo Offline**: O sistema funciona como PWA (Progressive Web App) - pode ser instalado no celular!

3. **WhatsApp IA**: Depois de conectar, você pode adicionar transações via WhatsApp usando voz ou texto.

4. **Multi-tenant**: Cada usuário tem seus próprios dados isolados.

---

## 🎨 Customização

### Mudar Porta do Flask
Edite a variável de ambiente antes de rodar:
```batch
set PORT=8080
python app.py
```

### Desabilitar Landing Page
No `app.py`, linha 260-268, mude para:
```python
return redirect(url_for('login'))
```

---

**Desenvolvido com 💙 por Brayan Barbosa Lima**
