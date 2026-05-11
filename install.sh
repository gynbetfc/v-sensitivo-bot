#!/bin/bash
echo "⚡ TESLA 369 BOT"
echo "================"
pkill -f python 2>/dev/null
sleep 1
echo "📦 Atualizando..."
pkg update -y -qq && pkg upgrade -y -qq
echo "🐍 Python..."
pkg install python -y -qq
echo "📦 Dependências..."
pip install -q flask api-iqoption-faria requests
echo "📥 Baixando bot..."
curl -4 -s https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/main.py -o bot.py
echo "🚀 Iniciando..."
python bot.py &
sleep 5
echo "📱 Abrindo Chrome..."
termux-open-url http://127.0.0.1:5000 2>/dev/null
echo ""
echo "✅ BOT RODANDO!"
echo "📱 http://127.0.0.1:5000"
echo "🛑 Parar: pkill -f python"
while true; do sleep 60; done
