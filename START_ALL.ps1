# BWS Finance - Inicialização Completa
# Execute este script para iniciar Flask + Bot WhatsApp

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "BWS Finance - Inicializacao Completa" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Configuração
$ProjectPath = "C:\App\nik0finance-base"
$WhatsAppPath = "$ProjectPath\whatsapp_server"
$FlaskPort = 5000
$WhatsAppPort = 3000

# Função para matar processos
function Kill-Processes {
    Write-Host "[1/5] Limpando processos antigos..." -ForegroundColor Yellow
    Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Get-Process -Name node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Write-Host "   OK - Processos limpos" -ForegroundColor Green
    Write-Host ""
}

# Função para verificar portas
function Test-Port {
    param($Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient("localhost", $Port)
        $connection.Close()
        return $true
    } catch {
        return $false
    }
}

# Função para iniciar Flask
function Start-Flask {
    Write-Host "[2/5] Iniciando Flask (Backend + API + IA)..." -ForegroundColor Yellow
    
    # Verificar se porta está em uso
    if (Test-Port $FlaskPort) {
        Write-Host "   AVISO: Porta $FlaskPort ja esta em uso" -ForegroundColor Red
        Write-Host "   Tentando matar processo..." -ForegroundColor Yellow
        Get-NetTCPConnection -LocalPort $FlaskPort -ErrorAction SilentlyContinue | 
            ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
        Start-Sleep -Seconds 2
    }
    
    # Iniciar Flask em nova janela
    $flaskCommand = "cd $ProjectPath; python app.py"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $flaskCommand -WindowStyle Normal
    
    Write-Host "   Aguardando Flask iniciar (10 segundos)..." -ForegroundColor Cyan
    Start-Sleep -Seconds 10
    
    if (Test-Port $FlaskPort) {
        Write-Host "   OK - Flask rodando em http://localhost:$FlaskPort" -ForegroundColor Green
    } else {
        Write-Host "   ERRO - Flask nao iniciou corretamente" -ForegroundColor Red
        Write-Host "   Verifique a janela do Flask para erros" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Função para verificar WPPConnect
function Test-WPPConnect {
    Write-Host "[3/5] Verificando WPPConnect..." -ForegroundColor Yellow
    
    $packageJson = Get-Content "$WhatsAppPath\package.json" -Raw | ConvertFrom-Json
    if ($packageJson.dependencies.'@wppconnect-team/wppconnect') {
        Write-Host "   OK - WPPConnect instalado" -ForegroundColor Green
        return $true
    } else {
        Write-Host "   AVISO - WPPConnect nao encontrado" -ForegroundColor Red
        Write-Host "   Instalando WPPConnect..." -ForegroundColor Yellow
        
        Set-Location $WhatsAppPath
        npm install @wppconnect-team/wppconnect --save
        
        Write-Host "   OK - WPPConnect instalado" -ForegroundColor Green
        return $true
    }
}

# Função para iniciar Bot WhatsApp
function Start-WhatsAppBot {
    Write-Host "[4/5] Iniciando Bot WhatsApp..." -ForegroundColor Yellow
    
    # Verificar se porta está em uso
    if (Test-Port $WhatsAppPort) {
        Write-Host "   AVISO: Porta $WhatsAppPort ja esta em uso" -ForegroundColor Red
        Get-NetTCPConnection -LocalPort $WhatsAppPort -ErrorAction SilentlyContinue | 
            ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
        Start-Sleep -Seconds 2
    }
    
    # Iniciar bot em nova janela
    $botCommand = "cd $WhatsAppPath; node index_v3.js"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $botCommand -WindowStyle Normal
    
    Write-Host "   Aguardando bot iniciar (15 segundos)..." -ForegroundColor Cyan
    Write-Host "   IMPORTANTE: Escaneie o QR code na janela do bot!" -ForegroundColor Yellow
    Start-Sleep -Seconds 15
    
    if (Test-Port $WhatsAppPort) {
        Write-Host "   OK - Bot rodando em http://localhost:$WhatsAppPort" -ForegroundColor Green
    } else {
        Write-Host "   ERRO - Bot nao iniciou corretamente" -ForegroundColor Red
        Write-Host "   Verifique a janela do bot para erros" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Função para exibir informações finais
function Show-Info {
    Write-Host "[5/5] Informacoes do Sistema" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "  SISTEMA INICIADO COM SUCESSO!" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "URLs Importantes:" -ForegroundColor White
    Write-Host "  Site Principal:     http://192.168.80.122:5000" -ForegroundColor Cyan
    Write-Host "  Cadastro WhatsApp:  http://192.168.80.122:5000/register-whatsapp" -ForegroundColor Cyan
    Write-Host "  Chat Web:           http://192.168.80.122:5000/whatsapp-chat" -ForegroundColor Cyan
    Write-Host "  Dashboard:          http://192.168.80.122:5000/dashboard" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Health Flask:       http://localhost:5000" -ForegroundColor Gray
    Write-Host "  Health Bot:         http://localhost:3000/health" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Bot WhatsApp:" -ForegroundColor White
    Write-Host "  Numero:             +5511947626417" -ForegroundColor Cyan
    Write-Host "  Status:             Verifique janela do bot" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Seu Usuario:" -ForegroundColor White
    Write-Host "  WhatsApp:           +5511974764971" -ForegroundColor Cyan
    Write-Host "  Email:              brayan@bws.com" -ForegroundColor Cyan
    Write-Host "  Senha:              123456" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Proximos Passos:" -ForegroundColor Yellow
    Write-Host "  1. Se ainda nao cadastrou, acesse /register-whatsapp" -ForegroundColor White
    Write-Host "  2. Escaneie o QR code do WhatsApp (janela do bot)" -ForegroundColor White
    Write-Host "  3. Envie mensagem de teste para +5511947626417" -ForegroundColor White
    Write-Host "  4. Se nao receber resposta, use: /whatsapp-chat" -ForegroundColor White
    Write-Host ""
    Write-Host "Pressione qualquer tecla para manter este resumo..." -ForegroundColor Gray
}

# Execução principal
try {
    Kill-Processes
    Start-Flask
    
    if (-not (Test-WPPConnect)) {
        Write-Host "ERRO: Falha ao instalar WPPConnect" -ForegroundColor Red
        exit 1
    }
    
    Start-WhatsAppBot
    Show-Info
    
    # Manter janela aberta
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    
} catch {
    Write-Host ""
    Write-Host "ERRO CRITICO:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Pressione qualquer tecla para sair..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}
