@echo off
chcp 65001 >nul
echo ========================================
echo  💬 WhatsApp BWS Finance - LOCAL
echo  (Sem OCR - Apenas Texto e Áudio)
echo ========================================
echo.

REM Verificar Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado!
    pause
    exit /b 1
)
echo ✅ Python encontrado:
python --version
echo.

REM Verificar Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Node.js não encontrado!
    pause
    exit /b 1
)
echo ✅ Node.js encontrado:
node --version
echo.

REM Verificar FFmpeg (opcional)
where ffmpeg >nul 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  FFmpeg não encontrado (áudio pode não funcionar)
    echo    Para instalar: winget install FFmpeg
) else (
    echo ✅ FFmpeg encontrado:
    ffmpeg -version | findstr "ffmpeg version"
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
echo  📱 Funcionalidades Disponíveis:
echo ========================================
echo.
echo  ✅ Mensagens de TEXTO
echo     "Paguei R$ 50 no mercado"
echo.
echo  ✅ Mensagens de ÁUDIO (se FFmpeg instalado)
echo     Grave dizendo a transação
echo.
echo  ✅ Perguntas via Chat IA
echo     "Quanto gastei esse mês?"
echo.
echo  ⚠️  Fotos de recibos DESABILITADAS
echo     (Tesseract não instalado)
echo     Para habilitar: winget install Tesseract
echo.
echo ========================================
echo  📱 Próximos Passos:
echo ========================================
echo.
echo  1. Aguarde 10 segundos
echo  2. Abra: http://localhost:3000
echo  3. Escaneie o QR Code com WhatsApp
echo  4. Aguarde "✅ WhatsApp connected!"
echo  5. Envie mensagem de teste:
echo     "Paguei R$ 50,00 no mercado"
echo.
echo ========================================
echo.

timeout /t 5

REM Abrir navegador automaticamente
echo 🌐 Abrindo navegador...
start http://localhost:3000

echo.
echo ✅ Tudo pronto! Escaneie o QR Code!
echo.
echo 💡 DICA: Para habilitar processamento de FOTOS:
echo    winget install Tesseract
echo.
pause
