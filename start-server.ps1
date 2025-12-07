<#
    BWS Finance - Script de Inicialização (Windows PowerShell)
    Uso:
        .\start-server.ps1
    Objetivo:
        - Garantir que o banco existe
        - Criar view de saldos
        - Iniciar servidor de produção usando Waitress (estável)
    Observações:
        - Remove emojis para evitar problemas de encoding em consoles cp1252
        - Usa 127.0.0.1 por padrão; altere para 0.0.0.0 se quiser acesso externo
#>

Write-Host "Iniciando BWS Finance..." -ForegroundColor Cyan
Write-Host ""

$projectPath = "c:\App\nik0finance-base"
Set-Location $projectPath

if (-not (Test-Path "bws_finance.db")) {
    Write-Host "Banco de dados não encontrado. Criando..." -ForegroundColor Yellow
    python -c "from app import init_db, seed_default_data; init_db(); seed_default_data()"
}

Write-Host "Verificando estrutura do banco (views)..." -ForegroundColor Cyan
if (Test-Path "scripts\create_v_account_balances.py") {
    python scripts\create_v_account_balances.py
}

Write-Host ""
Write-Host "Aplicação pronta em http://localhost:5000" -ForegroundColor Green
Write-Host "Pressione CTRL+C para parar" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor DarkGray

# Iniciar via waitress para maior estabilidade
python -c "from scripts.run_server import run; run()"
