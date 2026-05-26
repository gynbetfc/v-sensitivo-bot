
import requests
import base64
import subprocess
import sys
import os
import tempfile
import atexit
import signal
import time

BOT_URL = "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/main.py"
bot_path = os.path.join(tempfile.gettempdir(), "_t369_bot.py")

def limpar():
    """Remove e mata processos antigos"""
    try:
        # Mata qualquer processo Python rodando bot.py
        if sys.platform == 'win32':
            os.system('taskkill /f /im python.exe 2>nul')
        else:
            os.system('pkill -f "_t369_bot.py" 2>/dev/null')
        time.sleep(1)
        # Remove arquivo antigo
        if os.path.exists(bot_path):
            os.remove(bot_path)
    except:
        pass

# Limpa ANTES de baixar (remove versão antiga)
limpar()

atexit.register(limpar)

print("""
╔══════════════════════════════════════════╗
║       ⚡ TESLA 369 BOT v6.5.0 ⚡       ║
╚══════════════════════════════════════════╝
""")

try:
    # Força baixar sem cache
    headers = {'Cache-Control': 'no-cache', 'Pragma': 'no-cache'}
    r = requests.get(BOT_URL, headers=headers, timeout=30)
    codigo = r.text
    
    # Decodifica se Base64
    if not codigo.strip().startswith('#') and not codigo.strip().startswith('from'):
        codigo = base64.b64decode(codigo).decode('utf-8')
        if not codigo.strip().startswith('#') and not codigo.strip().startswith('from'):
            codigo = base64.b64decode(codigo).decode('utf-8')
    
    # Remove arquivo antigo e salva novo
    if os.path.exists(bot_path):
        os.remove(bot_path)
    
    with open(bot_path, 'w', encoding='utf-8') as f:
        f.write(codigo)
    
    print("✅ Bot atualizado!")
    print("🌐 Abra: http://127.0.0.1:5000")
    print("=" * 50)
    
    # Executa
    subprocess.run([sys.executable, bot_path])
    
except Exception as e:
    print(f"❌ Erro: {e}")
    input("Pressione Enter para sair...")
