# Script para iniciar o frontend do BWS Finance
Write-Host "🚀 Iniciando BWS Finance Frontend..." -ForegroundColor Cyan
Write-Host ""

# Navegar para pasta frontend
Set-Location -Path "frontend"

# Verificar se node_modules existe
if (-Not (Test-Path "node_modules")) {
    Write-Host "📦 Instalando dependências (primeira vez)..." -ForegroundColor Yellow
    npm install
    Write-Host ""
}

Write-Host "✅ Dependências prontas!" -ForegroundColor Green
Write-Host "🌐 Iniciando servidor Vite..." -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 Frontend estará disponível em: http://localhost:5173" -ForegroundColor Green
Write-Host "📊 Acesse a dashboard em: http://localhost:5173/dashboard" -ForegroundColor Green
Write-Host ""

# Iniciar servidor de desenvolvimento
npm run dev
