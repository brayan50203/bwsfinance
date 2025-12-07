#!/usr/bin/env pwsh
# Script para iniciar BWS Finance no Windows
# Execução: .\RODAR.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   BWS Finance - Inicializador" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Função para verificar se Docker está rodando
function Test-DockerRunning {
    try {
        $null = docker ps 2>&1
        return $?
    }
    catch {
        return $false
    }
}

# Verificar se Docker Desktop está instalado
Write-Host "[1/5] Verificando Docker Desktop..." -ForegroundColor Yellow
$dockerPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
if (-not (Test-Path $dockerPath)) {
    Write-Host "❌ Docker Desktop não encontrado!" -ForegroundColor Red
    Write-Host "Instale em: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Verificar se Docker está rodando
Write-Host "[2/5] Verificando status do Docker..." -ForegroundColor Yellow
if (-not (Test-DockerRunning)) {
    Write-Host "⚠️  Docker não está rodando. Iniciando..." -ForegroundColor Yellow
    
    # Iniciar Docker Desktop
    Start-Process -FilePath $dockerPath -WindowStyle Hidden
    
    # Aguardar até 90 segundos
    $timeout = 90
    $elapsed = 0
    while (-not (Test-DockerRunning) -and ($elapsed -lt $timeout)) {
        Write-Host "   Aguardando Docker iniciar... ($elapsed/$timeout segundos)" -ForegroundColor Gray
        Start-Sleep -Seconds 5
        $elapsed += 5
    }
    
    if (-not (Test-DockerRunning)) {
        Write-Host "❌ Docker não iniciou após $timeout segundos" -ForegroundColor Red
        Write-Host "Por favor:" -ForegroundColor Yellow
        Write-Host "  1. Abra Docker Desktop manualmente" -ForegroundColor White
        Write-Host "  2. Aguarde aparecer 'Docker is running'" -ForegroundColor White
        Write-Host "  3. Execute este script novamente" -ForegroundColor White
        exit 1
    }
}

Write-Host "✅ Docker está rodando!" -ForegroundColor Green
Write-Host ""

# Parar containers antigos se existirem
Write-Host "[3/5] Parando containers antigos (se existirem)..." -ForegroundColor Yellow
docker-compose -f docker-compose.casaos.yml down 2>$null
Write-Host "✅ Containers antigos removidos" -ForegroundColor Green
Write-Host ""

# Criar arquivo .env se não existir
Write-Host "[4/5] Verificando configurações..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Arquivo .env não encontrado. Criando..." -ForegroundColor Yellow
    
    $envContent = @"
# Configuração BWS Finance
SECRET_KEY=seu-secret-key-super-secreto-aqui-$(Get-Random)
DATABASE_URL=sqlite:///instance/bws_finance.db

# WhatsApp
WHATSAPP_AUTH_TOKEN=token-seguro-para-api-whatsapp

# Email (Opcional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-app

# AI/ML (Opcional)
OPENAI_API_KEY=sua-chave-openai
GROQ_API_KEY=sua-chave-groq
"@
    
    Set-Content -Path ".env" -Value $envContent -Encoding UTF8
    Write-Host "✅ Arquivo .env criado! Edite se necessário." -ForegroundColor Green
} else {
    Write-Host "✅ Arquivo .env encontrado" -ForegroundColor Green
}
Write-Host ""

# Subir containers
Write-Host "[5/5] Iniciando containers..." -ForegroundColor Yellow
Write-Host "Isso pode levar alguns minutos (baixando imagens se necessário)..." -ForegroundColor Gray
Write-Host ""

docker-compose -f docker-compose.casaos.yml up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "   ✅ BWS Finance ESTÁ RODANDO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Dashboard: http://localhost:8080" -ForegroundColor Cyan
    Write-Host "📱 WhatsApp:  http://localhost:8080/whatsapp" -ForegroundColor Cyan
    Write-Host "🔌 API:       http://localhost:8080/api" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📋 Comandos úteis:" -ForegroundColor Yellow
    Write-Host "   Ver logs:     docker-compose -f docker-compose.casaos.yml logs -f" -ForegroundColor White
    Write-Host "   Ver status:   docker-compose -f docker-compose.casaos.yml ps" -ForegroundColor White
    Write-Host "   Parar tudo:   docker-compose -f docker-compose.casaos.yml down" -ForegroundColor White
    Write-Host "   Reiniciar:    docker-compose -f docker-compose.casaos.yml restart" -ForegroundColor White
    Write-Host ""
    Write-Host "📱 Para conectar WhatsApp:" -ForegroundColor Yellow
    Write-Host "   1. Acesse: http://localhost:8080/whatsapp" -ForegroundColor White
    Write-Host "   2. Escaneie o QR Code com WhatsApp" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Erro ao iniciar containers!" -ForegroundColor Red
    Write-Host "Verifique os logs acima para detalhes" -ForegroundColor Yellow
    exit 1
}
