@echo off
echo ========================================
echo  BWS Finance - Iniciar WhatsApp + IA
echo ========================================
echo.

REM Criar pasta temp se não existir
if not exist "temp" mkdir temp

REM Criar pasta logs se não existir
if not exist "logs" mkdir logs

echo [1/3] Verificando Node.js...
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Node.js nao encontrado!
    echo Instale em: https://nodejs.org
    pause
    exit /b 1
)
echo [OK] Node.js instalado

echo.
echo [2/3] Iniciando servidor WhatsApp (Node.js)...
cd whatsapp_server
start "WhatsApp Server" cmd /k "node index.js"
cd ..

echo [OK] Servidor WhatsApp iniciado (Terminal separado)
echo.
echo ========================================
echo  INSTRUCOES:
echo ========================================
echo.
echo 1. Escaneie o QR Code com WhatsApp
echo 2. Aguarde conectar
echo 3. Envie mensagem de teste: "Paguei R$ 50 no mercado"
echo.
echo ========================================
echo  Para testar manualmente:
echo ========================================
echo.
echo # Testar NLP:
echo python -c "from modules.nlp_classifier import NLPClassifier; nlp = NLPClassifier(); print(nlp.classify('Paguei R$ 50,00 no mercado hoje'))"
echo.
echo # Testar envio:
echo python -c "from services.whatsapp_sender import send_whatsapp_notification; send_whatsapp_notification('+5511999999999', 'Teste!')"
echo.
pause
