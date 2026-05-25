#!/bin/bash
echo "⚡ TESLA 369 BOT"
echo "=============================="

# Mata bots anteriores
pkill -f "python.*bot.py" 2>/dev/null
sleep 1

# Verifica se bot.py existe
if [ ! -f "bot.py" ]; then
    echo "❌ bot.py não encontrado! Reinstale o bot."
    exit 1
fi

# Verifica firebase-key.json
if [ ! -f "firebase-key.json" ]; then
    echo "⚠️ Baixando firebase-key.json..."
    curl -4 -s -o firebase-key.json "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/firebase-key.json"
fi

# Inicia o bot
echo "🚀 Iniciando Tesla 369..."
python bot.py &
sleep 3

# Abre o navegador
echo "✅ Bot rodando! http://127.0.0.1:5000"
termux-open-url http://127.0.0.1:5000 2>/dev/null || echo "📱 Abra: http://127.0.0.1:5000"
