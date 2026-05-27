#!/bin/bash
echo "⚡ TESLA 369 BOT - Instalação"
echo "=============================="
pkill -f "python.*bot.py" 2>/dev/null
pkill -f "python.*main.py" 2>/dev/null
sleep 2
echo "🧹 Limpando..."
rm -rf bot.py tesla_369 temp_repo 2>/dev/null
echo "📦 Atualizando..."
pkg update -y -qq && pkg upgrade -y -qq
echo "🐍 Python..."
pkg install python git -y -qq
echo "📦 Dependências..."
pip install flask requests api-iqoption-faria -q 2>/dev/null
echo "📥 Baixando Tesla 369..."
git clone https://github.com/gynbetfc/v-sensitivo-bot.git temp_repo
cp -r temp_repo/tesla_369 .
rm -rf temp_repo
echo "alias tesla='cd ~/tesla_369 && python main.py'" >> ~/.bashrc
echo "alias kill='pkill -f "python.*main.py" 2>/dev/null; echo "✅ Bots parados"'" >> ~/.bashrc
source ~/.bashrc 2>/dev/null
echo ""
echo "✅✅✅ INSTALAÇÃO CONCLUÍDA! ✅✅✅"
echo "🚀 Digite: tesla"
echo "🛑 Parar: kill"
