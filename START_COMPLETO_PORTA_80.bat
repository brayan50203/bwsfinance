@echo off
REM ======================================================
REM BWS Finance - SISTEMA COMPLETO na Porta 80
REM Execute como Administrador!
REM ======================================================
REM Landing Page: http://localhost
REM Sistema: http://localhost/app
REM WhatsApp: http://localhost:3000
REM ======================================================

title BWS Finance - Sistema Completo Porta 80

echo ========================================
echo   BWS FINANCE - SISTEMA COMPLETO
echo ========================================
echo.
echo [INFO] Landing Page: Porta 80
echo [INFO] Sistema Flask: Porta 5000
echo [INFO] WhatsApp Bot: Porta 3000
echo.

REM Matar processos anteriores
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo [1/3] Iniciando Landing Page (Porta 80)...
start "BWS Finance - Landing Page" cmd /k "cd /d %~dp0 && python landing_server.py"
timeout /t 3 /nobreak >nul

echo [2/3] Iniciando Flask (Porta 5000)...
start "BWS Finance - Flask" cmd /k "cd /d %~dp0 && set PORT=5000 && python app.py"
timeout /t 3 /nobreak >nul

echo [3/3] Iniciando WhatsApp Bot (Porta 3000)...
start "BWS Finance - WhatsApp" cmd /k "cd /d %~dp0\whatsapp_server && node index_v3.js"
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo   SISTEMA INICIADO COM SUCESSO!
echo ========================================
echo.
echo Pagina Inicial (Landing):
echo   http://localhost
echo.
echo Sistema Completo (Dashboard):
echo   http://localhost:5000
echo   http://localhost:5000/dashboard
echo.
echo WhatsApp Bot:
echo   http://localhost:3000
echo.
echo Pressione qualquer tecla para fechar...
pause >nul
