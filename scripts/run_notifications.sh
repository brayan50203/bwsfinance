#!/bin/bash
# Script para iniciar sistema de notificações
# BWS Finance - Auto Notifications

echo "🚀 Iniciando Sistema de Notificações BWS Finance..."
echo ""

# Verificar se .env existe
if [ ! -f .env ]; then
    echo "⚠️  Arquivo .env não encontrado!"
    echo "Copiando .env.example para .env..."
    cp .env.example .env
    echo "✅ Arquivo .env criado. EDITE-O antes de continuar!"
    echo ""
    exit 1
fi

# Verificar dependências Python
echo "📦 Verificando dependências..."
pip show apscheduler > /dev/null 2>&1 || {
    echo "⚠️  APScheduler não instalado. Instalando..."
    pip install apscheduler
}

pip show requests > /dev/null 2>&1 || {
    echo "⚠️  Requests não instalado. Instalando..."
    pip install requests
}

pip show jinja2 > /dev/null 2>&1 || {
    echo "⚠️  Jinja2 não instalado. Instalando..."
    pip install jinja2
}

echo "✅ Dependências OK"
echo ""

# Verificar banco de dados
if [ ! -f bws_finance.db ]; then
    echo "❌ Banco de dados não encontrado!"
    echo "Execute primeiro: python app.py"
    exit 1
fi

# Aplicar migração (se necessário)
echo "🔧 Verificando migração de notificações..."
python scripts/migrate_notifications_columns.py

echo ""
echo "✅ Sistema pronto para iniciar!"
echo ""
echo "Para iniciar o Flask (com scheduler de notificações):"
echo "  python app.py"
echo ""
echo "Para testar notificações:"
echo "  curl -X POST http://localhost:5000/api/notifications/run-job/check_due_invoices"
echo ""
echo "Health check:"
echo "  curl http://localhost:5000/api/notifications/health"
echo ""
echo "📖 Documentação completa: README_NOTIFICATIONS.md"
echo ""
