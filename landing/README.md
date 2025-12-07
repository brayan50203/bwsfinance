# BWS Finance - Landing Page 🌐

Página inicial do BWS Finance servida na porta 80.

## 🚀 Como Iniciar

### Método 1: Porta 80 (Requer Admin)
```bash
# Clique direito em start-landing.bat
# Selecione "Executar como administrador"
```

### Método 2: Porta 8080 (Sem Admin)
```bash
# Edite landing_server.py
# Altere: PORT = 80 para PORT = 8080
python landing_server.py
```

## 🔗 Acesso

- **Local**: http://localhost
- **Rede**: http://192.168.80.122

## 📁 Estrutura

```
landing/
  └── index.html      # Página inicial moderna com Tailwind CSS
landing_server.py     # Servidor HTTP Python
start-landing.bat     # Script de inicialização (Windows)
```

## ✨ Recursos da Landing Page

- ✅ Design moderno com gradientes e animações
- ✅ Responsivo (mobile-first)
- ✅ 9 cards de recursos principais
- ✅ Seção de estatísticas
- ✅ Seção sobre o projeto
- ✅ CTA (Call-to-Action) destacado
- ✅ Links para sistema principal (porta 5000)
- ✅ Footer com navegação

## 🎨 Tecnologias

- HTML5 semântico
- Tailwind CSS (CDN)
- Animações CSS customizadas
- Python HTTP Server

## 🔧 Troubleshooting

### Porta 80 em uso?
```bash
# Verifique processos usando a porta 80
netstat -ano | findstr :80

# Encerre o processo (substitua PID)
taskkill /PID <PID> /F
```

### Preferir outra porta?
Altere `PORT = 80` em `landing_server.py` para qualquer porta disponível (ex: 8080, 3001, 8000).

## 📝 Notas

- Porta 80 é a porta padrão HTTP (não precisa especificar na URL)
- Requer privilégios administrativos no Windows
- O servidor é single-threaded (adequado para landing page estática)
