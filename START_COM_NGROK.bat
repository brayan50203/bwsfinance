@echo off
REM ======================================================
REM BWS Finance - Iniciar com ngrok (Acesso Online)
REM ======================================================
REM Permite acesso via internet usando ngrok tunnel
REM ======================================================

title BWS Finance - Ngrok Tunnel

echo ========================================
echo   BWS FINANCE - MODO ONLINE (NGROK)
echo ========================================
echo.

REM Verificar se ngrok está instalado
where ngrok >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERRO] ngrok nao encontrado!
    echo.
    echo Instale o ngrok:
    echo   1. Acesse: https://ngrok.com/download
    echo   2. Extraia o ngrok.exe
    echo   3. Adicione ao PATH ou coloque na pasta do projeto
    echo.
    pause
    exit /b 1
)

REM Matar processos anteriores
echo [1/3] Encerrando processos anteriores...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
taskkill /F /IM ngrok.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo [2/3] Iniciando Flask (Porta 5000)...
start "BWS Finance - Flask" cmd /k "cd /d %~dp0 && set PORT=5000 && python app.py"
timeout /t 4 /nobreak >nul

echo [3/3] Iniciando ngrok tunnel...
start "BWS Finance - Ngrok" cmd /k "ngrok http 5000"
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   SISTEMA INICIADO!
echo ========================================
echo.
echo ^>^> Local:
echo    http://localhost:5000
echo.
echo ^>^> Online (ngrok):
echo    Verifique a URL na janela do ngrok
echo    Exemplo: https://xxxx-xxxx-xxxx.ngrok-free.app
echo.
echo IMPORTANTE: Copie a URL do ngrok e atualize
echo            seu dominio para apontar para ela!
echo.
pause
