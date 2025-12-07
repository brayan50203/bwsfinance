# ======================================================
# BWS Finance - Iniciar na Porta 80
# ======================================================
# Execute como Administrador para usar a porta 80!
# ======================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  BWS FINANCE - Iniciando na Porta 80" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verifica se está rodando como Administrador
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️  ATENÇÃO: A porta 80 requer privilégios de Administrador!" -ForegroundColor Yellow
    Write-Host "   Clique com botão direito no arquivo e selecione 'Executar como Administrador'" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Pressione ENTER para sair"
    exit
}

# Define o diretório do projeto
$projectDir = $PSScriptRoot
Set-Location $projectDir

Write-Host "📁 Diretório: $projectDir" -ForegroundColor Green
Write-Host ""

# Define a porta 80 como variável de ambiente
$env:PORT = "80"
$env:FLASK_PORT = "80"

# Mata processos anteriores se existirem
Write-Host "🔄 Verificando processos anteriores..." -ForegroundColor Yellow
Get-Process -Name python,node -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*$projectDir*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  1/2 - Iniciando Flask (Porta 80)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Inicia o Flask na porta 80 em uma nova janela
$flaskJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$projectDir'; `$env:PORT='80'; python app.py" -PassThru -WindowStyle Normal
Write-Host "✅ Flask iniciado (PID: $($flaskJob.Id))" -ForegroundColor Green
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  2/2 - Iniciando WhatsApp Bot" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Inicia o WhatsApp em uma nova janela
$whatsappDir = Join-Path $projectDir "whatsapp_server"
$whatsappJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$whatsappDir'; node index_v3.js" -PassThru -WindowStyle Normal
Write-Host "✅ WhatsApp Bot iniciado (PID: $($whatsappJob.Id))" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ SISTEMA INICIADO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Acesse o sistema em:" -ForegroundColor Cyan
Write-Host "   http://localhost" -ForegroundColor White
Write-Host "   http://localhost/dashboard" -ForegroundColor White
Write-Host "   http://192.168.80.132" -ForegroundColor White
Write-Host ""
Write-Host "📱 WhatsApp Bot:" -ForegroundColor Cyan
Write-Host "   http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "💡 Dica: Mantenha esta janela aberta!" -ForegroundColor Yellow
Write-Host ""

# Aguarda o usuário
Write-Host "Pressione CTRL+C para parar os servidores..." -ForegroundColor Yellow
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
}
finally {
    Write-Host ""
    Write-Host "🛑 Encerrando servidores..." -ForegroundColor Red
    Stop-Process -Id $flaskJob.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $whatsappJob.Id -Force -ErrorAction SilentlyContinue
    Write-Host "✅ Servidores encerrados!" -ForegroundColor Green
}
