#!/bin/bash
echo "⚡ TESLA 369 BOT"
echo "=============================="

# Mata bots anteriores
pkill -f "python.*bot.py" 2>/dev/null
sleep 1

# Verifica se o bot.py existe
if [ ! -f "bot.py" ]; then
    echo "❌ bot.py não encontrado!"
    echo "Execute: bash <(curl -4 -s https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/install.sh)"
    exit 1
fi

# Verifica firebase-key.json
if [ ! -f "firebase-key.json" ]; then
    echo "⚠️ firebase-key.json não encontrado. Baixando..."
    curl -4 -s -o firebase-key.json "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/firebase-key.json"
fi

# Inicia o bot
echo "🚀 Iniciando Tesla 369..."
python bot.py &

# Espera iniciar
sleep 3

# Abre o navegador
echo "✅ Bot rodando! http://127.0.0.1:5000"
termux-open-url http://127.0.0.1:5000 2>/dev/null || echo "📱 Abra manualmente: http://127.0.0.1:5000"
