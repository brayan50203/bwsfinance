# ✅ Checklist de Deploy - BWS Finance no CasaOS

Use este checklist para garantir que todos os passos foram executados corretamente.

---

## 📋 PRÉ-INSTALAÇÃO

- [ ] CasaOS instalado e acessível via navegador
- [ ] Docker e Docker Compose funcionando
- [ ] Portas 5000 e 3000 disponíveis
- [ ] Pelo menos 1GB de espaço em disco livre
- [ ] Acesso SSH ao servidor (recomendado)
- [ ] App Password do Gmail criado (se usar Gmail)
- [ ] Domínio configurado (opcional, para HTTPS)

---

## 🚀 INSTALAÇÃO

### Método Escolhido:
- [ ] **Opção A:** Instalação automática (`install-casaos.sh`)
- [ ] **Opção B:** Docker Compose manual
- [ ] **Opção C:** CasaOS App Store

### Passos Executados:
- [ ] Código baixado/clonado
- [ ] Arquivo `.env` criado e configurado
- [ ] SECRET_KEY gerado (mínimo 32 caracteres)
- [ ] WHATSAPP_AUTH_TOKEN configurado
- [ ] SMTP configurado (host, port, user, password)
- [ ] Build das imagens Docker concluído
- [ ] Containers iniciados com `docker compose up -d`
- [ ] Logs verificados (sem erros críticos)

### Verificações de Instalação:
- [ ] Backend responde: `curl http://192.168.80.132:5000/api/notifications/health`
- [ ] WhatsApp responde: `curl http://192.168.80.132:3000/health`
- [ ] Containers rodando: `docker compose ps` (ambos "Up")

---

## ⚙️ CONFIGURAÇÃO INICIAL

### Conta de Administrador:
- [ ] Acesso a `http://192.168.80.132:5000`
- [ ] Conta de admin criada
- [ ] Login bem-sucedido
- [ ] Dashboard acessível

### WhatsApp:
- [ ] Acesso a `http://192.168.80.132:3000`
- [ ] QR Code gerado
- [ ] QR Code escaneado no celular
- [ ] Status "CONNECTED" verificado
- [ ] Mensagem de teste enviada e recebida

### Email (SMTP):
- [ ] Credenciais SMTP configuradas no `.env`
- [ ] Teste de envio realizado
- [ ] Email de teste recebido
- [ ] Remetente aparece correto

---

## 🔔 NOTIFICAÇÕES

### Preferências do Usuário:
- [ ] Acesso a Settings/Configurações
- [ ] "Notificar via WhatsApp" habilitado
- [ ] "Notificar via Email" habilitado
- [ ] "Notificar no Dashboard" habilitado
- [ ] Saldo baixo configurado (ex: R$ 100)
- [ ] Variação investimentos configurada (ex: 3%)
- [ ] Horário "Não Perturbar" configurado (opcional)
- [ ] Dias de alerta de fatura: 3,1,0
- [ ] **OPT-IN WhatsApp marcado** ⚠️ OBRIGATÓRIO
- [ ] **OPT-IN Email marcado** ⚠️ OBRIGATÓRIO
- [ ] Preferências salvas

### Testes de Notificação:
- [ ] Teste de saldo baixo enviado
- [ ] Notificação recebida via WhatsApp
- [ ] Notificação recebida via Email
- [ ] Teste de fatura vencendo enviado
- [ ] Ambas notificações recebidas

---

## 📊 SCHEDULER

### Verificação do Scheduler:
- [ ] Health check: `curl http://192.168.80.132:5000/api/notifications/health`
- [ ] `scheduler_running: true`
- [ ] `jobs_count: 5`
- [ ] Próximas execuções listadas

### Jobs Configurados:
- [ ] check_due_invoices (09:00 diário)
- [ ] check_low_balance (06:00 diário)
- [ ] check_investment_updates (08:05 diário)
- [ ] check_monthly_spending (07:00 diário)
- [ ] send_periodic_reports (Dom 18:00)

### Teste Manual de Job:
- [ ] Job executado manualmente
- [ ] Notificação gerada (se aplicável)
- [ ] Log sem erros

---

## 💾 DADOS

### Contas e Cartões:
- [ ] Pelo menos 1 conta bancária cadastrada
- [ ] Pelo menos 1 cartão de crédito cadastrado
- [ ] Cartão com `due_day` configurado
- [ ] Transações de teste criadas

### Banco de Dados:
- [ ] Tabela `notifications` existe
- [ ] Tabela `user_notifications_settings` existe
- [ ] Tabela `notification_logs` existe
- [ ] Integridade verificada: `PRAGMA integrity_check`

---

## 🔐 SEGURANÇA

### Variáveis de Ambiente:
- [ ] SECRET_KEY aleatório e forte (32+ chars)
- [ ] WHATSAPP_AUTH_TOKEN único e seguro
- [ ] SMTP_PASSWORD protegido
- [ ] `.env` com permissões corretas (600)

### Firewall (se aplicável):
- [ ] Porta 5000 liberada (se acesso externo)
- [ ] Porta 3000 restrita (apenas local ou VPN)
- [ ] Portas desnecessárias bloqueadas

### HTTPS (se domínio disponível):
- [ ] Nginx Proxy Manager instalado
- [ ] Proxy Host criado
- [ ] Certificado SSL Let's Encrypt configurado
- [ ] Force SSL habilitado
- [ ] Acesso via `https://` funcionando

---

## 💾 BACKUP

### Backup Automático:
- [ ] Script de backup diário configurado no crontab
- [ ] Backup manual testado
- [ ] Restore de backup testado
- [ ] Local de backup definido e acessível
- [ ] Rotação de backups configurada (ex: manter 30 dias)

### Comandos Configurados:
```bash
# Backup diário (crontab)
0 2 * * * docker exec bws-finance-backend sqlite3 /app/bws_finance.db ".backup /app/data/backup_$(date +\%Y\%m\%d).db"

# Limpar backups antigos
0 3 * * * find /DATA/AppData/bws-finance/data -name "backup_*.db" -mtime +30 -delete
```

- [ ] Crontab configurado
- [ ] Backup executado pelo menos 1 vez
- [ ] Arquivo de backup criado

---

## 📝 LOGS E MONITORAMENTO

### Logs:
- [ ] Logs sendo escritos em `/app/logs/`
- [ ] `notifications.log` existe
- [ ] Logs acessíveis via `docker compose logs`
- [ ] Rotação de logs configurada (opcional)

### Monitoramento:
- [ ] Health check configurado e funcional
- [ ] Recursos do sistema monitorados (`docker stats`)
- [ ] Espaço em disco suficiente
- [ ] RAM não ultrapassando limite (< 1GB recomendado)

---

## 📚 DOCUMENTAÇÃO

### Acesso à Documentação:
- [ ] `DEPLOY_CASAOS.md` lido
- [ ] `SETUP_GUIDE_CASAOS.md` seguido
- [ ] `TROUBLESHOOTING_CASAOS.md` disponível para consulta
- [ ] `CASAOS_QUICK_START.md` consultado
- [ ] `DELIVERY_REPORT.md` revisado

---

## 🧪 TESTES FINAIS

### Funcionalidades Core:
- [ ] Criar transação via interface
- [ ] Criar transação via WhatsApp (IA)
- [ ] Visualizar dashboard com dados
- [ ] Gráficos carregando corretamente
- [ ] Filtros funcionando

### Notificações End-to-End:
- [ ] Cadastrar fatura vencendo em 3 dias
- [ ] Aguardar job executar (ou forçar manual)
- [ ] Receber notificação via WhatsApp
- [ ] Receber notificação via Email
- [ ] Notificação aparece no dashboard

### Performance:
- [ ] Tempo de resposta < 2s (páginas)
- [ ] API responde < 500ms
- [ ] Health check < 100ms
- [ ] Sem memory leaks (RAM estável)

---

## 🎯 VALIDAÇÃO FINAL

### Checklist de Produção:
- [ ] ✅ Sistema acessível remotamente (se aplicável)
- [ ] ✅ Notificações chegando em horário correto
- [ ] ✅ Scheduler executando jobs sem falhas
- [ ] ✅ Backup automático funcionando
- [ ] ✅ Logs sendo escritos corretamente
- [ ] ✅ Health check sempre "healthy"
- [ ] ✅ Sem erros críticos nos logs (últimas 24h)
- [ ] ✅ WhatsApp permanece conectado (> 24h)
- [ ] ✅ Email sendo enviado sem falhas
- [ ] ✅ Banco de dados íntegro

---

## 🚦 STATUS FINAL

Marque um:

- [ ] 🟢 **VERDE** - Todos os itens checados, sistema em produção
- [ ] 🟡 **AMARELO** - Maioria checada, alguns itens opcionais faltando
- [ ] 🔴 **VERMELHO** - Problemas críticos, consultar TROUBLESHOOTING

---

## 📞 PRÓXIMOS PASSOS

### Se VERDE (Tudo OK):
1. ✅ Sistema em produção
2. ✅ Monitorar logs diariamente (primeira semana)
3. ✅ Validar notificações automáticas
4. ✅ Ajustar preferências conforme necessário

### Se AMARELO (Quase Lá):
1. ⚠️ Revisar itens não checados
2. ⚠️ Configurar itens opcionais importantes
3. ⚠️ Testar novamente após ajustes

### Se VERMELHO (Problemas):
1. ❌ Consultar `TROUBLESHOOTING_CASAOS.md`
2. ❌ Verificar logs: `docker compose logs`
3. ❌ Pedir ajuda no GitHub Issues (com logs)

---

## 📌 INFORMAÇÕES DO SISTEMA

Preencha para referência:

```
Data de instalação: ___/___/_____
Versão do CasaOS: _________________
IP do servidor: _________________
Domínio (se houver): _________________
Email SMTP configurado: _________________
Telefone WhatsApp: _________________

Jobs configurados:
- check_due_invoices: [ ] Sim [ ] Não
- check_low_balance: [ ] Sim [ ] Não
- check_investment_updates: [ ] Sim [ ] Não
- check_monthly_spending: [ ] Sim [ ] Não
- send_periodic_reports: [ ] Sim [ ] Não

Backup configurado: [ ] Sim [ ] Não
Local do backup: _________________

HTTPS configurado: [ ] Sim [ ] Não
Certificado expira em: ___/___/_____

Observações:
_______________________________________
_______________________________________
_______________________________________
```

---

**🎉 Checklist completo! Sistema BWS Finance pronto para uso!** 🚀
