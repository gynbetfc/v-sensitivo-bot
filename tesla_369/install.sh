#!/bin/bash
echo "⚡ TESLA 369 BOT v6.5.2"
echo "===================================="
pkill -f "python.*launcher" 2>/dev/null
sleep 1
pkg update -y -qq && pkg upgrade -y -qq
pkg install python git -y -qq
pip install flask requests api-iqoption-faria -q 2>/dev/null
curl -4 -s "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/tesla_369/launcher.py" -o ~/tesla_launcher.py
echo "alias tesla='python ~/tesla_launcher.py'" >> ~/.bashrc
echo 'alias kill="pkill -f python.*launcher 2>/dev/null; echo Bots parados"' >> ~/.bashrc
source ~/.bashrc 2>/dev/null
echo ""
echo "✅✅✅ INSTALACAO CONCLUIDA! ✅✅✅"
echo "🚀 Digite: tesla"
