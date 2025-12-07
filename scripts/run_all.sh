#!/bin/bash
# Script para iniciar ambos os servidores (Flask + Node.js)

echo "🚀 Iniciando BWSFinance + WhatsApp Integration..."

# Verificar se está na pasta correta
if [ ! -f "app.py" ]; then
    echo "❌ Execute este script na pasta raiz do projeto"
    exit 1
fi

# Ativar ambiente virtual Python
if [ -d "venv" ]; then
    echo "📦 Ativando ambiente virtual Python..."
    source venv/bin/activate
else
    echo "⚠️ Ambiente virtual não encontrado. Criando..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements_whatsapp.txt
fi

# Função para cleanup ao sair
cleanup() {
    echo "\n🛑 Encerrando servidores..."
    kill $FLASK_PID $NODE_PID 2>/dev/null
    exit 0
}

trap cleanup INT TERM

# Iniciar Flask em background
echo "🐍 Iniciando Flask..."
python app.py > logs/flask.log 2>&1 &
FLASK_PID=$!
echo "   Flask PID: $FLASK_PID"

# Aguardar Flask iniciar
sleep 3

# Iniciar Node.js
echo "📱 Iniciando WhatsApp Server..."
cd whatsapp_server
node index.js > ../logs/node.log 2>&1 &
NODE_PID=$!
cd ..
echo "   Node PID: $NODE_PID"

echo ""
echo "✅ Servidores iniciados!"
echo "   Flask:    http://localhost:5000"
echo "   WhatsApp: http://localhost:3000"
echo ""
echo "📋 Logs:"
echo "   Flask:    tail -f logs/flask.log"
echo "   Node:     tail -f logs/node.log"
echo "   WhatsApp: tail -f logs/whatsapp.log"
echo ""
echo "⏸️  Pressione Ctrl+C para parar"

# Manter script rodando
wait
