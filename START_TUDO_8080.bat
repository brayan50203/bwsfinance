@echo off
REM ======================================================
REM BWS Finance - Iniciar na Porta 8080 (Sem Admin)
REM ======================================================

title BWS Finance - Porta 8080

echo ========================================
echo   BWS FINANCE - Iniciando na Porta 8080
echo ========================================
echo.

REM Define a porta 8080 (não precisa de admin)
set PORT=8080
set FLASK_PORT=8080

echo [1/2] Iniciando Flask na porta 8080...
start "BWS Finance - Flask" cmd /k "cd /d %~dp0 && set PORT=8080 && python app.py"
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
echo   http://localhost:8080
echo   http://localhost:8080/dashboard
echo.
echo WhatsApp Bot:
echo   http://localhost:3000
echo.
echo Pressione qualquer tecla para fechar...
pause >nul
