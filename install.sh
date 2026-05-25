#!/bin/bash
echo "⚡ TESLA 369 BOT - Instalação"
echo "=============================="
pkill -f python 2>/dev/null; sleep 1
echo "📦 Atualizando..."
pkg update -y -qq && pkg upgrade -y -qq
echo "🐍 Python..."
pkg install python -y -qq
echo "📦 Dependências..."
pip install firebase-admin flask requests api-iqoption-faria -q 2>/dev/null
echo "📥 Baixando bot..."
curl -4 -s "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/main.py

# Download firebase-key.json
echo "🔥 Configurando Firebase..."
curl -4 -s -o firebase-key.json https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/firebase-key.json
?t=$(date +%s)" -o bot.b64
python -c "import base64; open('bot.py','w').write(base64.b64decode(open('bot.b64').read()).decode())"
rm bot.b64
echo "alias tesla='bash <(curl -4 -s https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/tesla.sh)'" >> ~/.bashrc
source ~/.bashrc 2>/dev/null
echo "✅ Pronto! Agora digite: tesla"
