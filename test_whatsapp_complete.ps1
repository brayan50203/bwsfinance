# Script de teste completo do WhatsApp
Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "   Teste Completo WhatsApp BWS Finance" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# 1. Health Check do WhatsApp Server
Write-Host "1️⃣  Testando WhatsApp Server..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri http://localhost:3000/health -Method GET
    Write-Host "   ✅ Status: $($health.status)" -ForegroundColor Green
    Write-Host "   ✅ WhatsApp Conectado: $($health.whatsapp_connected)" -ForegroundColor Green
    Write-Host "   ✅ Client Existe: $($health.client_exists)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Erro: $_" -ForegroundColor Red
    exit 1
}

# 2. Health Check do Flask
Write-Host "`n2️⃣  Testando Flask Server..." -ForegroundColor Yellow
try {
    $response = curl.exe http://localhost:5000/login -I 2>&1 | Select-String "HTTP/1.1 200"
    if ($response) {
        Write-Host "   ✅ Flask está respondendo (HTTP 200)" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Flask não retornou 200" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Erro: $_" -ForegroundColor Red
}

# 3. Teste do Webhook (simulando mensagem do WhatsApp)
Write-Host "`n3️⃣  Testando Webhook Flask..." -ForegroundColor Yellow
try {
    $headers = @{
        'Authorization' = 'Bearer bws_finance_token_55653'
        'Content-Type' = 'application/json'
    }
    
    $body = @{
        from = '5511974764971@c.us'
        type = 'text'
        text = 'teste do sistema'
        timestamp = [int][double]::Parse((Get-Date -UFormat %s))
    } | ConvertTo-Json
    
    $result = Invoke-RestMethod -Uri http://localhost:5000/api/whatsapp/webhook -Method POST -Headers $headers -Body $body
    
    Write-Host "   ✅ Webhook respondeu com sucesso!" -ForegroundColor Green
    Write-Host "   📨 Mensagem: $($result.message)" -ForegroundColor Cyan
    Write-Host "   🎯 Modo: $($result.mode)" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ Erro: $_" -ForegroundColor Red
}

# 4. Informações de rede
Write-Host "`n4️⃣  Informações de Rede:" -ForegroundColor Yellow
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "192.168.*"}).IPAddress
Write-Host "   🌐 IP Local: $ip" -ForegroundColor Cyan
Write-Host "   🔗 URL Externa Flask: http://$($ip):5000" -ForegroundColor Cyan
Write-Host "   🔗 URL Externa WhatsApp: http://$($ip):3000" -ForegroundColor Cyan

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "   ✅ Teste Completo Finalizado!" -ForegroundColor Green
Write-Host "============================================`n" -ForegroundColor Cyan

Write-Host "📱 Para testar o bot:" -ForegroundColor Yellow
Write-Host "   1. Envie uma mensagem WhatsApp para o número conectado" -ForegroundColor White
Write-Host "   2. Use um dos números autorizados: 5511974764971 ou 5511949967277" -ForegroundColor White
Write-Host "   3. Exemplos de mensagens:" -ForegroundColor White
Write-Host "      - 'quanto gastei esse mes?'" -ForegroundColor Gray
Write-Host "      - 'adicionar gasto 50 cafe'" -ForegroundColor Gray
Write-Host "      - 'meus investimentos'" -ForegroundColor Gray
