@echo off
echo ============================================================
echo BWS Finance WhatsApp Bot - VENOM
echo EXECUCAO MANUAL
echo ============================================================
echo.
echo INSTRUCOES:
echo 1. Uma janela do Chrome vai abrir
echo 2. Aguarde o QR code aparecer na tela do Chrome
echo 3. Escaneie com seu WhatsApp
echo.
echo Pressione qualquer tecla para iniciar...
pause > nul

cd /d C:\App\nik0finance-base\whatsapp_server
node test_venom.js

echo.
echo ============================================================
echo Bot encerrado. Pressione qualquer tecla para fechar...
pause > nul
