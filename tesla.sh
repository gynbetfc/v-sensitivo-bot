#!/bin/bash
echo "⚡ TESLA 369 BOT - Instalação"
echo "=============================="
pkill -f python 2>/dev/null
sleep 1
echo "📦 Atualizando Termux..."
pkg update -y -qq && pkg upgrade -y -qq
echo "🐍 Instalando Python..."
pkg install python -y -qq
echo "📦 Instalando dependências..."
pip install flask requests api-iqoption-faria -q 2>/dev/null
echo "📥 Baixando o bot..."
curl -4 -s "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/main.py?t=$(date +%s)" -o bot.b64
python -c "import base64; open('bot.py','w').write(base64.b64decode(open('bot.b64').read()).decode())"
rm bot.b64
echo ""
echo "✅ INSTALAÇÃO CONCLUÍDA!"
echo ""
echo "⚡ Criando atalho..."
echo "alias tesla='bash <(curl -4 -s https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/install.sh)'" >> ~/.bashrc
source ~/.bashrc 2>/dev/null
echo ""
echo "=============================================="
echo "  🚀 Agora digite: tesla"
echo "  📱 O Chrome abrirá com o bot!"
echo "  🛑 Para parar: clique em DESCONECTAR"
echo "=============================================="
echo ""
