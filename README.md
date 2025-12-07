# 🚀 BWS Finance - Flask Backend

## Base: nik0finance + Funcionalidades Avançadas

### ✅ O que está PRONTO:

- ✅ Backend Flask estável e sem bugs
- ✅ SQLite database com schema completo
- ✅ Multi-tenant (suporte a múltiplas empresas)
- ✅ Autenticação (login/cadastro com hash seguro)
- ✅ **Dashboard** estilo nik0finance:
  - Renda Fixa / Renda Variável
  - Custo Fixo / Custo Variável
  - Saldo Mensal
  - Filtros por ano/mês
- ✅ **Múltiplas Contas Bancárias** (Corrente, Poupança, Investimento, Carteira)
- ✅ **Cartões de Crédito** (Nome, Limite, Fechamento, Vencimento)
- ✅ **Categorias Personalizadas** (com ícones e cores)
- ✅ **Transações** completas (CRUD)
- ✅ Templates HTML com Tailwind CSS
- ✅ Interface responsiva e moderna

### 📦 Estrutura do Banco de Dados:

```
✅ tenants - Empresas/Organizações
✅ users - Usuários com autenticação
✅ accounts - Contas bancárias
✅ categories - Categorias customizáveis
✅ cards - Cartões de crédito
✅ transactions - Transações financeiras
✅ recurring_transactions - Transações recorrentes
✅ installments - Parcelamentos
✅ investments - Investimentos
✅ goals - Metas financeiras
✅ notifications - Notificações
✅ integrations - Integrações bancárias
```

---

## 🏁 Como Iniciar

### 1. Instalar Dependências

```powershell
cd "c:\App\bwsfinnance v02 final - 2025-10-18_12-48\nik0finance-base"
pip install -r requirements.txt
```

### 2. Iniciar o Servidor

```powershell
python app.py
```

O servidor estará disponível em: **http://localhost:5000**

### 3. Primeiro Acesso

1. Acesse http://localhost:5000
2. Clique em "Cadastre-se"
3. Crie sua conta (nome, email, senha)
4. Faça login
5. Pronto! Você verá o dashboard vazio

---

## 📱 Funcionalidades Disponíveis

### Dashboard
- ✅ Cards com resumo financeiro
- ✅ Renda Fixa, Renda Variável
- ✅ Custo Fixo, Custo Variável
- ✅ Saldo Mensal
- ✅ Filtros por ano/mês
- ✅ Tabelas de rendas e custos
- ✅ Adicionar transação (modal)
- ✅ Excluir transação

### Contas Bancárias
- ✅ Listar todas as contas
- ✅ Adicionar nova conta
- ✅ Ver saldo atual de cada conta
- ✅ Tipos: Corrente, Poupança, Investimento, Carteira

### Cartões de Crédito
- ✅ Listar cartões
- ✅ Adicionar novo cartão
- ✅ Informações: Limite, Fechamento, Vencimento
- ✅ Vincular a uma conta

---

## 🎯 Próximas Funcionalidades (em desenvolvimento)

### Fase 2 - Transações Avançadas (2-3 dias)
- [ ] Transações recorrentes automáticas
- [ ] Parcelamentos (3x, 6x, 12x)
- [ ] Transferências entre contas
- [ ] Edição de transações
- [ ] Anexar comprovantes

### Fase 3 - Relatórios (2-3 dias)
- [ ] Relatório de Fluxo de Caixa
- [ ] DRE (Demonstração de Resultado)
- [ ] Gráficos (Chart.js)
- [ ] Exportar PDF
- [ ] Análise por categoria

### Fase 4 - Investimentos (2 dias)
- [ ] Cadastro de investimentos
- [ ] Cálculo de rentabilidade
- [ ] Integração com APIs de cotações

### Fase 5 - Notificações (1 dia)
- [ ] Alertas de vencimento
- [ ] Avisos de limite de cartão
- [ ] Notificações in-app

### Fase 6 - IA & Integrações (5-7 dias)
- [ ] Análise com OpenAI/Gemini
- [ ] Categorização automática
- [ ] Open Finance (Pluggy)
- [ ] Sincronização bancária

---

## 🔧 Configuração

### Arquivo `.env`
```
SECRET_KEY=change-me-in-production
DATABASE=bws_finance.db
FLASK_ENV=development
FLASK_DEBUG=True
```

### Banco de Dados
- **Tipo**: SQLite (fácil, local, sem instalação)
- **Arquivo**: `bws_finance.db` (criado automaticamente)
- **Migração para PostgreSQL**: Possível futuramente

---

## 🆚 Comparação: nik0finance vs BWS Finance Flask

| Funcionalidade | nik0finance Original | BWS Finance Flask |
|---|---|---|
| Login/Cadastro | ✅ | ✅ |
| Dashboard | ✅ Básico | ✅ Melhorado |
| Renda Fixa/Variável | ✅ | ✅ |
| Custo Fixo/Variável | ✅ | ✅ |
| Múltiplas Contas | ❌ | ✅ |
| Cartões de Crédito | ❌ | ✅ |
| Categorias Customizáveis | ❌ | ✅ |
| Parcelamentos | ❌ | ✅ (em breve) |
| Transações Recorrentes | ❌ | ✅ (em breve) |
| Investimentos | ❌ | ✅ (em breve) |
| Relatórios | ❌ | ✅ (em breve) |
| Multi-tenant | ❌ | ✅ |
| 2FA | ❌ | ✅ (em breve) |
| IA | ❌ | ✅ (em breve) |
| Integrações Bancárias | ❌ | ✅ (em breve) |

---

## 🐛 Por que Flask e não NestJS?

### Problemas do NestJS atual:
- ❌ Frontend Next.js não inicia (bug de port)
- ❌ Muitos erros de TypeScript
- ❌ Complexidade alta (Decorators, DI, Prisma)
- ❌ Tempo de desenvolvimento lento

### Vantagens do Flask:
- ✅ **Backend funciona 100%** (sem bugs)
- ✅ Python é mais simples e produtivo
- ✅ SQLite não precisa de servidor
- ✅ Templates funcionam (server-side rendering)
- ✅ Desenvolvimento RÁPIDO
- ✅ Menos complexidade

---

## 📞 Suporte

Criado por: BWS Finance Team
Base: nik0finance (https://github.com/Nik0lax/nik0finance)
Melhorado com: Multi-tenant, Contas, Cartões, e mais

---

## 📝 TODO List

- [ ] Implementar transações recorrentes
- [ ] Implementar parcelamentos
- [ ] Adicionar gráficos no dashboard
- [ ] Criar relatórios em PDF
- [ ] Adicionar 2FA
- [ ] Integrar com Open Finance
- [ ] Adicionar IA para análises
- [ ] Criar app mobile (React Native)
- [ ] Deploy em produção (Railway/Render)

---

**Status**: ✅ FUNCIONANDO e pronto para desenvolvimento!
**Versão**: 1.0.0
**Data**: Outubro 2025
