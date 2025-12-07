@echo off
chcp 65001 >nul
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║   BWS Finance - Inicio Completo COM FFmpeg                ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Adicionar FFmpeg ao PATH
echo [1/3] Configurando FFmpeg...
set "PATH=%PATH%;C:\ProgramData\chocolatey\lib\ffmpeg\tools\ffmpeg\bin"

REM Testar FFmpeg
where ffmpeg >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  FFmpeg não encontrado no PATH
    echo    Você pode precisar instalar: winget install ffmpeg
) else (
    echo ✅ FFmpeg configurado
)

echo.
echo [2/3] Iniciando Flask na porta 80...
start "Flask Server" cmd /k "python app.py"
timeout /t 3 /nobreak >nul

echo.
echo [3/3] Iniciando WhatsApp Server na porta 3000...
cd whatsapp_server
start "WhatsApp Server" cmd /k "node index_v3.js"
cd ..

echo.
echo ════════════════════════════════════════════════════════════
echo ✅ Sistema iniciado com sucesso!
echo.
echo 📊 Flask:     http://localhost:80
echo 📱 WhatsApp:  http://localhost:3000
echo 🎤 Áudio:     ✅ Suporte Whisper Ativo
echo ════════════════════════════════════════════════════════════
echo.
pause
