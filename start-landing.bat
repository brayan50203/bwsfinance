@echo off
title BWS Finance - Landing Page Server (Porta 80)
color 0B

echo.
echo ========================================
echo BWS Finance - Landing Page Server
echo ========================================
echo.

REM Verifica se está rodando como administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Executando como Administrador
    echo.
    goto :start
) else (
    echo [AVISO] Nao esta executando como Administrador!
    echo.
    echo A porta 80 requer privilegios de administrador.
    echo.
    echo Por favor, execute este arquivo como administrador:
    echo - Clique direito no arquivo
    echo - Selecione "Executar como administrador"
    echo.
    pause
    exit
)

:start
echo Iniciando servidor na porta 80...
echo.

REM Inicia o servidor Python
python landing_server.py

REM Se o servidor parar, aguarda
echo.
echo Servidor encerrado.
pause
