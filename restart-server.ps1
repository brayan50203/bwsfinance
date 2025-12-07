Write-Host "🔄 Reiniciando servidor..." -ForegroundColor Yellow

# Matar todos os processos Python
Write-Host "⏹️ Parando processos Python..." -ForegroundColor Red
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# Verificar se ainda tem algum processo na porta 5000
Write-Host "🔍 Verificando porta 5000..." -ForegroundColor Cyan
$port5000 = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue
if ($port5000) {
    Write-Host "⚠️ Ainda há processo na porta 5000, matando..." -ForegroundColor Yellow
    $processId = $port5000.OwningProcess
    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

# Limpar terminal
Clear-Host

# Iniciar servidor
Write-Host "🚀 Iniciando servidor Flask..." -ForegroundColor Green
Write-Host ""
python app.py
