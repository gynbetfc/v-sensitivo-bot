#!/bin/bash
echo "⚡ TESLA 369 BOT"
echo "================"
pkill -f python 2>/dev/null
sleep 1
echo "📦 Atualizando..."
pkg update -y -qq && pkg upgrade -y -qq
echo "🐍 Python..."
pkg install python -y -qq
echo "📦 Dependencias..."
pip install -q flask api-iqoption-faria requests
echo "🚀 Iniciando..."

# Baixar token
export GITHUB_TOKEN=$(curl -s https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/config.txt)

# Baixar e executar o bot
curl -s https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/main.py | python &

sleep 5
echo "📱 Abrindo Chrome..."
termux-open-url http://localhost:5000 2>/dev/null
echo ""
echo "✅ Pronto! http://localhost:5000"
echo "🛑 Parar: pkill -f python"
while true; do sleep 60; done
