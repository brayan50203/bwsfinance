# Script para iniciar sistema de notificações
# BWS Finance - Auto Notifications (Windows PowerShell)

Write-Host "🚀 Iniciando Sistema de Notificações BWS Finance..." -ForegroundColor Cyan
Write-Host ""

# Verificar se .env existe
if (-not (Test-Path .env)) {
    Write-Host "⚠️  Arquivo .env não encontrado!" -ForegroundColor Yellow
    Write-Host "Copiando .env.example para .env..."
    Copy-Item .env.example .env
    Write-Host "✅ Arquivo .env criado. EDITE-O antes de continuar!" -ForegroundColor Green
    Write-Host ""
    exit 1
}

# Verificar dependências Python
Write-Host "📦 Verificando dependências..."

$packages = @('apscheduler', 'requests', 'jinja2')

foreach ($package in $packages) {
    $installed = pip show $package 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  $package não instalado. Instalando..." -ForegroundColor Yellow
        pip install $package
    }
}

Write-Host "✅ Dependências OK" -ForegroundColor Green
Write-Host ""

# Verificar banco de dados
if (-not (Test-Path bws_finance.db)) {
    Write-Host "❌ Banco de dados não encontrado!" -ForegroundColor Red
    Write-Host "Execute primeiro: python app.py"
    exit 1
}

# Aplicar migração (se necessário)
Write-Host "🔧 Verificando migração de notificações..."
python scripts/migrate_notifications_columns.py

Write-Host ""
Write-Host "✅ Sistema pronto para iniciar!" -ForegroundColor Green
Write-Host ""
Write-Host "Para iniciar o Flask (com scheduler de notificações):"
Write-Host "  python app.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para testar notificações:"
Write-Host '  curl -X POST http://localhost:5000/api/notifications/run-job/check_due_invoices' -ForegroundColor Cyan
Write-Host ""
Write-Host "Health check:"
Write-Host "  curl http://localhost:5000/api/notifications/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "📖 Documentação completa: README_NOTIFICATIONS.md" -ForegroundColor Magenta
Write-Host ""
