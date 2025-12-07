@echo off
title WhatsApp Server - BWS Finance
cd /d "%~dp0"
echo ========================================
echo WhatsApp Server - BWS Finance
echo ========================================
echo.
echo Servidor iniciando...
echo Pressione CTRL+C para parar
echo.

:loop
node index.js
echo.
echo [!] Servidor encerrado. Reiniciando em 3 segundos...
timeout /t 3 /nobreak > nul
goto loop
