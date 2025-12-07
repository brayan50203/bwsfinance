@echo off
cd /d "%~dp0"
start /B pythonw.exe start_silent.py
echo Servidor iniciado em background (sem console)
echo Dashboard: http://127.0.0.1:5000/dashboard
echo Log: logs\server_*.log
echo.
echo Para parar: taskkill /F /IM pythonw.exe
pause
