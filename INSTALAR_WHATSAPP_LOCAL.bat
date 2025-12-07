@echo off
chcp 65001 >nul
echo ========================================
echo  📦 Instalação WhatsApp LOCAL
echo ========================================
echo.

REM Verificar Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado!
    echo Instale Python 3.11+ de: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python encontrado
python --version
echo.

REM Verificar Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Node.js não encontrado!
    echo Instale Node.js de: https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Node.js encontrado
node --version
echo.

echo ========================================
echo  1/5 - Instalando dependências Python
echo ========================================
echo.

pip install --upgrade pip
pip install -r requirements-local.txt

if %errorlevel% neq 0 (
    echo ❌ Erro ao instalar dependências Python
    pause
    exit /b 1
)

echo.
echo ✅ Dependências Python instaladas
echo.

echo ========================================
echo  2/5 - Baixando modelo spaCy (NLP)
echo ========================================
echo.

python -m spacy download pt_core_news_sm

if %errorlevel% neq 0 (
    echo ⚠️  Erro ao baixar modelo spaCy
    echo Você pode tentar manualmente:
    echo   python -m spacy download pt_core_news_sm
)

echo.
echo ✅ Modelo spaCy instalado
echo.

echo ========================================
echo  3/5 - Instalando dependências Node.js
echo ========================================
echo.

cd whatsapp_server
npm install

if %errorlevel% neq 0 (
    echo ❌ Erro ao instalar dependências Node.js
    cd ..
    pause
    exit /b 1
)

cd ..
echo.
echo ✅ Dependências Node.js instaladas
echo.

echo ========================================
echo  4/5 - Verificando Tesseract OCR
echo ========================================
echo.

where tesseract >nul 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  Tesseract não encontrado!
    echo.
    echo Para processar FOTOS, instale Tesseract:
    echo.
    echo Opção 1 - Chocolatey:
    echo   choco install tesseract
    echo.
    echo Opção 2 - Download direto:
    echo   https://github.com/UB-Mannheim/tesseract/wiki
    echo   Instalar em: C:\Program Files\Tesseract-OCR
    echo.
) else (
    echo ✅ Tesseract encontrado
    tesseract --version | findstr "tesseract"
)

echo.

echo ========================================
echo  5/5 - Verificando FFmpeg
echo ========================================
echo.

where ffmpeg >nul 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  FFmpeg não encontrado!
    echo.
    echo Para processar ÁUDIOS, instale FFmpeg:
    echo.
    echo Opção 1 - Chocolatey:
    echo   choco install ffmpeg
    echo.
    echo Opção 2 - Download direto:
    echo   https://www.gyan.dev/ffmpeg/builds/
    echo   Extrair e adicionar ao PATH
    echo.
) else (
    echo ✅ FFmpeg encontrado
    ffmpeg -version | findstr "ffmpeg version"
)

echo.

echo ========================================
echo  ✅ Instalação Concluída!
echo ========================================
echo.
echo 📋 Resumo:
echo   ✅ Python instalado
echo   ✅ Node.js instalado
echo   ✅ Dependências Python instaladas
echo   ✅ Modelo spaCy (NLP) instalado
echo   ✅ Dependências Node.js instaladas

where tesseract >nul 2>nul
if %errorlevel% equ 0 (
    echo   ✅ Tesseract OCR instalado
) else (
    echo   ⚠️  Tesseract OCR pendente
)

where ffmpeg >nul 2>nul
if %errorlevel% equ 0 (
    echo   ✅ FFmpeg instalado
) else (
    echo   ⚠️  FFmpeg pendente
)

echo.
echo ========================================
echo  🚀 Próximos Passos:
echo ========================================
echo.
echo 1. Execute: START_WHATSAPP_LOCAL.bat
echo 2. Abra: http://localhost:3000
echo 3. Escaneie QR Code com WhatsApp
echo 4. Cadastre seu número:
echo    python -c "from app import get_db; db = get_db(); db.execute('UPDATE users SET phone=\"+5511999999999\" WHERE email=\"seu@email.com\"'); db.commit(); print('✅ OK!')"
echo 5. Envie: "Paguei R$ 50,00 no mercado"
echo.
echo ========================================
echo.
pause
