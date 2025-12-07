@echo off
REM ======================================================
REM BWS Finance - Iniciar na Porta 80
REM Execute como Administrador!
REM ======================================================

title BWS Finance - Porta 80

echo ========================================
echo   BWS FINANCE - Iniciando na Porta 80
echo ========================================
echo.

REM Define a porta 80
set PORT=80
set FLASK_PORT=80

echo [1/2] Iniciando Flask na porta 80...
start "BWS Finance - Flask" cmd /k "cd /d %~dp0 && set PORT=80 && python app.py"
timeout /t 3 /nobreak >nul

echo [2/2] Iniciando WhatsApp Bot...
start "BWS Finance - WhatsApp" cmd /k "cd /d %~dp0\whatsapp_server && node index_v3.js"
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo   SISTEMA INICIADO!
echo ========================================
echo.
echo Acesse em:
echo   http://localhost
echo   http://localhost/dashboard
echo.
echo WhatsApp Bot:
echo   http://localhost:3000
echo.
echo Pressione qualquer tecla para fechar...
pause >nul
