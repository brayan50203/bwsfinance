@echo off
chcp 65001 >nul
echo ========================================
echo  💬 WhatsApp BWS Finance - COMPLETO
echo ========================================
echo.

REM Verificar Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado!
    pause
    exit /b 1
)
echo ✅ Python encontrado
echo.

REM Verificar Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Node.js não encontrado!
    pause
    exit /b 1
)
echo ✅ Node.js encontrado
echo.

REM Verificar Tesseract
if exist "C:\Program Files\Tesseract-OCR\tesseract.exe" (
    echo ✅ Tesseract encontrado
) else (
    echo ⚠️  Tesseract não encontrado
    echo    Fotos de recibos não funcionarão
)
echo.

REM Verificar FFmpeg
where ffmpeg >nul 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  FFmpeg não encontrado
    echo    Áudio pode não funcionar
) else (
    echo ✅ FFmpeg encontrado
)
echo.

echo ========================================
echo  🚀 Iniciando Servidores...
echo ========================================
echo.

REM Iniciar Flask (porta 80)
echo [1/2] Iniciando Flask Server (porta 80)...
start "BWS Finance Flask" cmd /k "cd /d %~dp0 && set PORT=80 && python app.py"
echo     ✅ Flask iniciando em http://localhost:80
echo.

REM Aguardar Flask iniciar
echo ⏳ Aguardando Flask inicializar...
timeout /t 5 /nobreak >nul

REM Iniciar WhatsApp Server (porta 3000)
echo [2/2] Iniciando WhatsApp Server (porta 3000)...
start "WhatsApp Server" cmd /k "cd /d %~dp0\whatsapp_server && npm start"
echo     ✅ WhatsApp iniciando em http://localhost:3000
echo.

echo ========================================
echo  ✅ Servidores iniciados!
echo ========================================
echo.
echo  📊 Flask Backend:  http://localhost:80
echo  💬 WhatsApp Bot:   http://localhost:3000
echo.
echo ========================================
echo  📱 Funcionalidades:
echo ========================================
echo.
echo  ✅ Mensagens de TEXTO
echo     "Paguei R$ 50 no mercado"
echo.
echo  ✅ Mensagens de ÁUDIO
echo     Grave dizendo a transação
echo.
echo  ✅ Fotos de Recibos (OCR)
echo     Tire foto e envie
echo.
echo  ✅ Perguntas (Chat IA)
echo     "Quanto gastei esse mês?"
echo.
echo ========================================
echo  📱 Próximos Passos:
echo ========================================
echo.
echo  1. Abra: http://localhost:3000
echo  2. Escaneie QR Code com WhatsApp
echo  3. Aguarde: "✅ WhatsApp connected!"
echo  4. Envie: "Paguei R$ 50,00 no mercado"
echo.
echo ========================================
echo.

timeout /t 3

REM Abrir navegador
start http://localhost:3000

echo ✅ Tudo pronto! Escaneie o QR Code!
echo.
