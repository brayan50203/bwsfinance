# Script PowerShell - Iniciar BWS Finance com Docker
# C:\App\nik0finance-base\start-docker.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  BWS Finance - Sistema Docker" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se Docker está rodando
Write-Host "Verificando Docker..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "✅ Docker está rodando" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker não está rodando!" -ForegroundColor Red
    Write-Host "Inicie o Docker Desktop e tente novamente." -ForegroundColor Yellow
    pause
    exit 1
}

# Ir para o diretório do projeto
Set-Location C:\App\nik0finance-base

# Menu
Write-Host ""
Write-Host "Escolha uma opção:" -ForegroundColor Cyan
Write-Host "1) Iniciar sistema (primeira vez - build + start)" -ForegroundColor White
Write-Host "2) Iniciar sistema (start rápido)" -ForegroundColor White
Write-Host "3) Parar sistema" -ForegroundColor White
Write-Host "4) Reiniciar sistema" -ForegroundColor White
Write-Host "5) Ver logs (todos)" -ForegroundColor White
Write-Host "6) Ver logs (Flask)" -ForegroundColor White
Write-Host "7) Ver logs (WhatsApp)" -ForegroundColor White
Write-Host "8) Ver status" -ForegroundColor White
Write-Host "9) Limpar tudo e reconstruir" -ForegroundColor White
Write-Host "0) Sair" -ForegroundColor White
Write-Host ""

$opcao = Read-Host "Digite o número"

switch ($opcao) {
    "1" {
        Write-Host ""
        Write-Host "Construindo imagens e iniciando..." -ForegroundColor Yellow
        docker-compose build
        docker-compose up -d
        Write-Host ""
        Write-Host "✅ Sistema iniciado!" -ForegroundColor Green
        Write-Host "🌐 Acesse: http://192.168.80.122" -ForegroundColor Cyan
        Write-Host "📊 Dashboard: http://192.168.80.122/dashboard" -ForegroundColor Cyan
        Write-Host "💬 WhatsApp: http://192.168.80.122/whatsapp/health" -ForegroundColor Cyan
    }
    
    "2" {
        Write-Host ""
        Write-Host "Iniciando sistema..." -ForegroundColor Yellow
        docker-compose up -d
        Write-Host ""
        Write-Host "✅ Sistema iniciado!" -ForegroundColor Green
        Write-Host "🌐 Acesse: http://192.168.80.122" -ForegroundColor Cyan
    }
    
    "3" {
        Write-Host ""
        Write-Host "Parando sistema..." -ForegroundColor Yellow
        docker-compose down
        Write-Host "✅ Sistema parado!" -ForegroundColor Green
    }
    
    "4" {
        Write-Host ""
        Write-Host "Reiniciando sistema..." -ForegroundColor Yellow
        docker-compose restart
        Write-Host "✅ Sistema reiniciado!" -ForegroundColor Green
    }
    
    "5" {
        Write-Host ""
        Write-Host "Logs (Ctrl+C para sair):" -ForegroundColor Yellow
        docker-compose logs -f
    }
    
    "6" {
        Write-Host ""
        Write-Host "Logs Flask (Ctrl+C para sair):" -ForegroundColor Yellow
        docker-compose logs -f bws-backend
    }
    
    "7" {
        Write-Host ""
        Write-Host "Logs WhatsApp (Ctrl+C para sair):" -ForegroundColor Yellow
        docker-compose logs -f whatsapp-server
    }
    
    "8" {
        Write-Host ""
        Write-Host "Status dos containers:" -ForegroundColor Yellow
        docker-compose ps
        Write-Host ""
        Write-Host "Uso de recursos:" -ForegroundColor Yellow
        docker stats --no-stream
    }
    
    "9" {
        Write-Host ""
        Write-Host "⚠️ ATENÇÃO: Isso vai remover tudo e reconstruir!" -ForegroundColor Red
        $confirma = Read-Host "Tem certeza? (s/n)"
        if ($confirma -eq "s" -or $confirma -eq "S") {
            Write-Host "Removendo containers e volumes..." -ForegroundColor Yellow
            docker-compose down -v
            Write-Host "Limpando sistema Docker..." -ForegroundColor Yellow
            docker system prune -f
            Write-Host "Reconstruindo imagens..." -ForegroundColor Yellow
            docker-compose build --no-cache
            Write-Host "Iniciando sistema..." -ForegroundColor Yellow
            docker-compose up -d
            Write-Host "✅ Sistema reconstruído e iniciado!" -ForegroundColor Green
        } else {
            Write-Host "Operação cancelada." -ForegroundColor Yellow
        }
    }
    
    "0" {
        Write-Host "Até logo!" -ForegroundColor Green
        exit 0
    }
    
    default {
        Write-Host "Opção inválida!" -ForegroundColor Red
    }
}

Write-Host ""
pause
