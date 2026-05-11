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
curl -s https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/main.py | python &
sleep 5
echo "📱 Abrindo Chrome..."
termux-open-url http://localhost:5000 2>/dev/null || am start -a android.intent.action.VIEW -d http://localhost:5000 2>/dev/null
echo ""
echo "✅ BOT RODANDO!"
echo "📱 http://localhost:5000"
echo "🛑 Parar: pkill -f python"
while true; do sleep 60; done
