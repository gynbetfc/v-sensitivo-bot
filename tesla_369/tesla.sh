#!/bin/bash
echo "⚡ TESLA 369 BOT"
echo "=============================="
pkill -f "python.*main.py" 2>/dev/null
sleep 2
echo "📥 Atualizando..."
cd ~/tesla_369
git pull origin main 2>/dev/null
echo "🚀 Iniciando..."
python main.py &
sleep 3
echo "✅ Bot rodando! http://127.0.0.1:5000"
termux-open-url http://127.0.0.1:5000 2>/dev/null || echo "📱 Abra: http://127.0.0.1:5000"
