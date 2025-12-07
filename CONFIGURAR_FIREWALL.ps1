# ======================================================
# BWS Finance - Configurar Firewall (Porta 80)
# Execute como Administrador!
# ======================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CONFIGURANDO FIREWALL - PORTA 80" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verifica se está rodando como Administrador
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "❌ ERRO: Este script precisa ser executado como Administrador!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Clique com botão direito e selecione 'Executar como Administrador'" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Pressione ENTER para sair"
    exit
}

Write-Host "✅ Executando como Administrador" -ForegroundColor Green
Write-Host ""

# Remover regras antigas se existirem
Write-Host "🔄 Removendo regras antigas..." -ForegroundColor Yellow
Remove-NetFirewallRule -DisplayName "BWS Finance - HTTP (80)" -ErrorAction SilentlyContinue
Remove-NetFirewallRule -DisplayName "BWS Finance - HTTP Alt (5000)" -ErrorAction SilentlyContinue
Remove-NetFirewallRule -DisplayName "BWS Finance - WhatsApp (3000)" -ErrorAction SilentlyContinue

Write-Host "✅ Regras antigas removidas" -ForegroundColor Green
Write-Host ""

# Adicionar regras para porta 80
Write-Host "🔧 Criando regra para porta 80..." -ForegroundColor Yellow
New-NetFirewallRule -DisplayName "BWS Finance - HTTP (80)" `
    -Direction Inbound `
    -Action Allow `
    -Protocol TCP `
    -LocalPort 80 `
    -Profile Any `
    -Enabled True `
    -Description "Permite acesso ao BWS Finance na porta 80" | Out-Null

Write-Host "✅ Porta 80 liberada no firewall" -ForegroundColor Green
Write-Host ""

# Adicionar regras para porta 5000 (alternativa)
Write-Host "🔧 Criando regra para porta 5000..." -ForegroundColor Yellow
New-NetFirewallRule -DisplayName "BWS Finance - HTTP Alt (5000)" `
    -Direction Inbound `
    -Action Allow `
    -Protocol TCP `
    -LocalPort 5000 `
    -Profile Any `
    -Enabled True `
    -Description "Permite acesso ao BWS Finance na porta 5000" | Out-Null

Write-Host "✅ Porta 5000 liberada no firewall" -ForegroundColor Green
Write-Host ""

# Adicionar regras para porta 3000 (WhatsApp)
Write-Host "🔧 Criando regra para porta 3000..." -ForegroundColor Yellow
New-NetFirewallRule -DisplayName "BWS Finance - WhatsApp (3000)" `
    -Direction Inbound `
    -Action Allow `
    -Protocol TCP `
    -LocalPort 3000 `
    -Profile Any `
    -Enabled True `
    -Description "Permite acesso ao WhatsApp Bot na porta 3000" | Out-Null

Write-Host "✅ Porta 3000 liberada no firewall" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "  FIREWALL CONFIGURADO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "📋 Próximos passos:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Configure Port Forwarding no seu roteador:" -ForegroundColor White
Write-Host "   - Porta externa: 80 → IP interno: 192.168.80.132:80" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Verifique seu IP público:" -ForegroundColor White
Write-Host "   - Acesse: https://www.whatismyip.com/" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Configure o domínio bwsfinance.bytecare.online:" -ForegroundColor White
Write-Host "   - Registro A apontando para seu IP público" -ForegroundColor Yellow
Write-Host ""
Write-Host "4. Inicie o servidor:" -ForegroundColor White
Write-Host "   - Execute: START_TUDO_INTEGRADO.bat (como Admin)" -ForegroundColor Yellow
Write-Host ""

# Mostrar IP público
Write-Host "🌐 Detectando IP público..." -ForegroundColor Cyan
try {
    $publicIP = (Invoke-WebRequest -Uri "https://api.ipify.org" -UseBasicParsing).Content
    Write-Host "   Seu IP público: $publicIP" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️ Não foi possível detectar automaticamente" -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Pressione ENTER para continuar"
