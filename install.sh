#!/bin/bash
echo "⚡ TESLA 369 BOT - Instalação"
echo "=============================="

# 1. MATA o bot anterior
echo "🛑 Parando bot anterior..."
pkill -f "python.*bot.py" 2>/dev/null
pkill -f "python.*main.py" 2>/dev/null
sleep 2

# 2. LIMPA arquivos antigos (backup dos dados locais)
echo "🧹 Limpando instalação anterior..."
rm -f bot.py bot.b64 main.py 2>/dev/null
# Mantém vsens_users/ como backup local

# 3. Atualiza pacotes
echo "📦 Atualizando..."
pkg update -y -qq && pkg upgrade -y -qq
echo "🐍 Python..."
pkg install python -y -qq

# 4. Instala dependências
echo "📦 Dependências..."
pip install firebase-admin flask requests api-iqoption-faria -q 2>/dev/null

# 5. Baixa o bot (Base64 → decodifica)
echo "📥 Baixando bot..."
curl -4 -s "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/main.py?t=$(date +%s)" -o bot.b64
python -c "import base64; open('bot.py','w').write(base64.b64decode(open('bot.b64').read()).decode())"
rm bot.b64

# 6. Baixa firebase-key.json
echo "🔥 Configurando Firebase..."
curl -4 -s -o firebase-key.json "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/firebase-key.json"

# 7. Cria alias
echo "alias tesla='bash <(curl -4 -s https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/tesla.sh)'" >> ~/.bashrc
source ~/.bashrc 2>/dev/null

echo "✅ Pronto! Agora digite: tesla"
