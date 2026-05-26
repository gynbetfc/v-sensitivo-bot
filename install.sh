#!/bin/bash
echo "⚡ TESLA 369 BOT - Instalação"
echo "=============================="

# 1. MATA todos os bots rodando
echo "🛑 Parando bots anteriores..."
pkill -f "python.*bot.py" 2>/dev/null
pkill -f "python.*_t369" 2>/dev/null
sleep 2

# 2. LIMPA arquivos antigos
echo "🧹 Limpando versão anterior..."
rm -f bot.py bot.b64 main.py 2>/dev/null

# 3. Atualiza pacotes
echo "📦 Atualizando..."
pkg update -y -qq && pkg upgrade -y -qq
echo "🐍 Python..."
pkg install python -y -qq

# 4. Instala dependências
echo "📦 Dependências..."
pip install flask requests api-iqoption-faria -q 2>/dev/null

# 5. Baixa SEMPRE a versão NOVA do GitHub
echo "📥 Baixando versão mais recente..."
curl -4 -s "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/main.py?t=$(date +%s)" -o bot.py

# 6. Cria aliases
grep -q "alias tesla=" ~/.bashrc 2>/dev/null || echo "alias tesla='bash <(curl -4 -s https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/tesla.sh)'" >> ~/.bashrc
grep -q "alias kill=" ~/.bashrc 2>/dev/null || echo "alias kill='pkill -f "python.*bot.py" 2>/dev/null; pkill -f "python.*_t369" 2>/dev/null; echo "✅ Todos os bots foram parados"'" >> ~/.bashrc
source ~/.bashrc 2>/dev/null

echo ""
echo "✅✅✅ INSTALAÇÃO CONCLUÍDA! ✅✅✅"
echo "=================================="
echo "🚀 Para iniciar: tesla"
echo "🛑 Para parar tudo: kill"
echo "=================================="
