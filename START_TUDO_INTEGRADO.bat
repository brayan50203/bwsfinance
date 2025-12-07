@echo off
REM ======================================================
REM BWS Finance - TUDO INTEGRADO NA PORTA 80
REM Execute como Administrador!
REM ======================================================
REM Sistema completo com Landing Page integrada
REM - Landing Page: http://localhost (visitantes)
REM - Login: http://localhost/login
REM - Dashboard: http://localhost/dashboard (logados)
REM - WhatsApp: http://localhost:3000
REM ======================================================

title BWS Finance - Porta 80 Integrado

color 0B
echo.
echo ================================================
echo      BWS FINANCE - INICIALIZANDO SISTEMA
echo ================================================
echo.
echo [INFO] Landing Page + Sistema na porta 80
echo [INFO] WhatsApp Bot na porta 3000
echo.

REM Matar processos anteriores
echo [1/3] Encerrando processos anteriores...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo [2/3] Iniciando Flask com Landing Page (Porta 80)...
start "BWS Finance - Sistema Principal" cmd /k "cd /d %~dp0 && set PORT=80 && color 0A && echo. && echo ===================================== && echo    FLASK + LANDING PAGE - PORTA 80 && echo ===================================== && echo. && python app.py"
timeout /t 4 /nobreak >nul

echo [3/3] Iniciando WhatsApp Bot (Porta 3000)...
start "BWS Finance - WhatsApp Bot" cmd /k "cd /d %~dp0\whatsapp_server && color 0E && echo. && echo ===================================== && echo    WHATSAPP BOT - PORTA 3000 && echo ===================================== && echo. && node index_v3.js"
timeout /t 2 /nobreak >nul

color 0A
echo.
echo ================================================
echo      SISTEMA INICIADO COM SUCESSO!
echo ================================================
echo.
echo ^>^> PAGINA INICIAL (Visitantes):
echo    http://localhost
echo.
echo ^>^> SISTEMA COMPLETO:
echo    Login: http://localhost/login
echo    Dashboard: http://localhost/dashboard
echo    Cadastro: http://localhost/register
echo.
echo ^>^> WHATSAPP BOT:
echo    API: http://localhost:3000
echo.
echo ^>^> DICA: A landing page aparece para visitantes
echo    e redireciona para o dashboard quando logado!
echo.
echo ================================================
echo    Mantenha esta janela aberta!
echo ================================================
echo.
pause
