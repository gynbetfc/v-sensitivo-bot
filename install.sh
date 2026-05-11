#!/bin/bash
echo "⚡ TESLA 369 BOT"
pkill -f python 2>/dev/null; sleep 1
pkg update -y -qq && pkg upgrade -y -qq
pkg install python -y -qq
pip install -q flask api-iqoption-faria requests
curl -4 -s https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/main.py -o bot.py
python bot.py &
sleep 5
termux-open-url http://127.0.0.1:5000 2>/dev/null
echo "✅ http://127.0.0.1:5000"
while true; do sleep 60; done
