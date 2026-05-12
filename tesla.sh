#!/bin/bash
echo "⚡ TESLA 369 BOT"
rm -f bot.b64 2>/dev/null
pkill -f python 2>/dev/null
sleep 1
curl -4 -s "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/main.py?t=$(date +%s)" -o bot.b64
python -c "import base64; open('bot.py','w').write(base64.b64decode(open('bot.b64').read()).decode())"
rm bot.b64
python bot.py &
sleep 8
termux-open-url http://127.0.0.1:5000 2>/dev/null
echo "✅ Bot rodando! http://127.0.0.1:5000"
wait
rm -f bot.py
