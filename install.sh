#!/bin/bash
echo "⚡ TESLA 369 BOT"
echo "================"
pkill -f python 2>/dev/null
sleep 1
echo "📦 Atualizando Termux..."
pkg update -y -qq && pkg upgrade -y -qq
echo "🐍 Instalando Python..."
pkg install python -y -qq
echo "📦 Instalando dependencias..."
pip install -q flask api-iqoption-faria requests
echo "🚀 Iniciando bot..."
curl -s https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/main.py | python
echo ""
echo "✅ BOT RODANDO!"
echo "📱 Acesse http://localhost:5000 no Chrome"
echo "🔒 Trave o Termux: notificacao > cadeado"
echo "🛑 Parar: pkill -f python"
while true; do sleep 60; done
