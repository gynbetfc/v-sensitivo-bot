
import requests
import base64
import subprocess
import sys
import os
import tempfile
import atexit

# URL exata que o install.sh usa
BOT_URL = "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/main.py"
bot_path = os.path.join(tempfile.gettempdir(), "_t369_bot.py")

def limpar():
    try:
        if os.path.exists(bot_path):
            os.remove(bot_path)
    except:
        pass

atexit.register(limpar)

print("""
╔══════════════════════════════════════════╗
║       ⚡ TESLA 369 BOT v6.5.0 ⚡       ║
╚══════════════════════════════════════════╝
""")

try:
    # Baixa igual o celular (curl no install.sh)
    print("📥 Baixando bot...")
    r = requests.get(BOT_URL, timeout=30)
    codigo = r.text
    
    # Se veio Base64, decodifica (igual o celular faz)
    if not codigo.strip().startswith('#') and not codigo.strip().startswith('from'):
        print("🔄 Decodificando...")
        codigo = base64.b64decode(codigo).decode('utf-8')
        # Dupla camada?
        if not codigo.strip().startswith('#') and not codigo.strip().startswith('from'):
            codigo = base64.b64decode(codigo).decode('utf-8')
    
    # Salva igual o install.sh salva
    with open(bot_path, 'w', encoding='utf-8') as f:
        f.write(codigo)
    
    print("✅ Bot pronto!")
    print("🌐 Abra: http://127.0.0.1:5000")
    print("=" * 50)
    
    # Roda igual o celular (python bot.py)
    subprocess.run([sys.executable, bot_path])
    
except Exception as e:
    print(f"❌ Erro: {e}")
    input("Pressione Enter para sair...")
