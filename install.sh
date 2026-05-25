#!/bin/bash
echo "⚡ TESLA 369 BOT - Instalação"
echo "=============================="
pkill -f "python.*bot.py" 2>/dev/null
sleep 1
echo "🧹 Limpando..."
rm -f bot.py bot.b64 main.py 2>/dev/null
echo "📦 Atualizando..."
pkg update -y -qq && pkg upgrade -y -qq
echo "🐍 Python..."
pkg install python -y -qq
echo "📦 Dependências..."
pip install flask requests api-iqoption-faria -q 2>/dev/null
echo "📥 Baixando bot..."
curl -4 -s "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/main.py?t=$(date +%s)" -o bot.py
echo "✅ Instalação concluída!"
echo "🚀 Digite: tesla"
grep -q "alias tesla=" ~/.bashrc 2>/dev/null || echo "alias tesla='bash <(curl -4 -s https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/tesla.sh)'" >> ~/.bashrc
source ~/.bashrc 2>/dev/null
