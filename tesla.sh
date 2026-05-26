#!/bin/bash
echo "⚡ TESLA 369 BOT"
echo "=============================="

# 1. Mata bots anteriores
echo "🛑 Parando versão anterior..."
pkill -f "python.*bot.py" 2>/dev/null
pkill -f "python.*_t369" 2>/dev/null
sleep 2

# 2. Remove bot antigo
echo "🧹 Removendo versão antiga..."
rm -f bot.py 2>/dev/null

# 3. Baixa SEMPRE a versão NOVA
echo "📥 Baixando versão mais recente..."
curl -4 -s "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/main.py?t=$(date +%s)" -o bot.py

# 4. Inicia o bot
echo "🚀 Iniciando Tesla 369..."
python bot.py &
sleep 3

# 5. Abre o navegador
echo "✅ Bot rodando! http://127.0.0.1:5000"
termux-open-url http://127.0.0.1:5000 2>/dev/null || echo "📱 Abra: http://127.0.0.1:5000"
