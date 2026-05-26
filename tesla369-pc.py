"""
⚡ TESLA 369 BOT - PC Version
Baixa a versão mais recente do GitHub e executa
Fecha = arquivo temporário é destruído
"""
import requests
import subprocess
import sys
import os
import tempfile
import time

print("""
╔══════════════════════════════════════════╗
║       ⚡ TESLA 369 BOT - PC ⚡          ║
║   Baixando versão mais recente...      ║
╚══════════════════════════════════════════╝
""")

# URL do bot no GitHub
BOT_URL = "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/main.py"

try:
    # Baixa o bot para arquivo temporário
    print("📥 Baixando bot...")
    response = requests.get(BOT_URL, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ Erro ao baixar: {response.status_code}")
        input("Pressione Enter para sair...")
        sys.exit(1)
    
    # Salva em arquivo temporário
    temp_dir = tempfile.gettempdir()
    bot_path = os.path.join(temp_dir, "tesla369_bot.py")
    
    with open(bot_path, 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    print(f"✅ Bot salvo em: {bot_path}")
    print("🚀 Iniciando Tesla 369...")
    print(f"🌐 Acesse: http://127.0.0.1:5000")
    print("=" * 50)
    
    # Executa o bot
    subprocess.run([sys.executable, bot_path])
    
except KeyboardInterrupt:
    print("
🛑 Bot interrompido pelo usuário.")
except Exception as e:
    print(f"❌ Erro: {e}")
    input("Pressione Enter para sair...")
finally:
    # Remove o arquivo temporário
    try:
        if os.path.exists(bot_path):
            os.remove(bot_path)
            print("🧹 Arquivo temporário removido.")
    except:
        pass
