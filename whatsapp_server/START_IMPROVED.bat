@echo off
echo ============================================================
echo BWS Finance WhatsApp Bot v4.0 - IMPROVED
echo ============================================================
echo.
echo MELHORIAS:
echo - Auto-registro de usuarios
echo - Mensagem de instrucao se numero nao cadastrado
echo - Retry automatico em envios
echo - Heartbeat para manter conexao
echo - Reconexao automatica se desconectar
echo.
echo Pressione qualquer tecla para iniciar...
pause > nul

cd /d C:\App\nik0finance-base\whatsapp_server
node index_improved.js

echo.
echo ============================================================
echo Bot encerrado. Pressione qualquer tecla para fechar...
pause > nul
