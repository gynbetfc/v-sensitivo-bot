#!/bin/bash
echo "⚡ TESLA 369 BOT"
echo "================"
pkill -f python 2>/dev/null
sleep 1

# Verificar se já tem token salvo
if [ -f ~/.tesla_token ]; then
    export GITHUB_TOKEN=$(cat ~/.tesla_token)
    echo "✅ Token carregado!"
else
    echo ""
    echo "🔑 Para acessar seus dados, cole o token do GitHub."
    echo "   Crie em: https://github.com/settings/tokens"
    echo "   (Classic, marque 'repo', gere e copie)"
    echo ""
    read -p "Token: " TK
    echo $TK > ~/.tesla_token
    export GITHUB_TOKEN=$TK
    echo "✅ Token salvo!"
fi

echo "📦 Atualizando..."
pkg update -y -qq && pkg upgrade -y -qq
echo "🐍 Python..."
pkg install python -y -qq
echo "📦 Dependências..."
pip install -q flask api-iqoption-faria requests
echo "🚀 Iniciando..."
curl -s https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/main.py | python &
sleep 5
echo "📱 Abrindo Chrome..."
termux-open-url http://localhost:5000 2>/dev/null
echo ""
echo "✅ BOT RODANDO!"
echo "📱 http://localhost:5000"
echo "🛑 Parar: pkill -f python"
while true; do sleep 60; done
