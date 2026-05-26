
import requests
import base64
import subprocess
import sys
import os
import tempfile
import atexit

BOT_URL = "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/main.py"
bot_path = os.path.join(tempfile.gettempdir(), "_t369_bot.py")

def limpar():
    """Remove o arquivo temporário ao sair"""
    try:
        if os.path.exists(bot_path):
            os.remove(bot_path)
    except:
        pass

atexit.register(limpar)  # Garante limpeza mesmo se crashar

print("⚡ TESLA 369 - Carregando...")
try:
    r = requests.get(BOT_URL, timeout=30)
    codigo = r.text
    
    # Se estiver em Base64, decodifica
    if not codigo.strip().startswith('#') and not codigo.strip().startswith('from'):
        codigo = base64.b64decode(codigo).decode('utf-8')
        # Segunda camada?
        if not codigo.strip().startswith('#') and not codigo.strip().startswith('from'):
            codigo = base64.b64decode(codigo).decode('utf-8')
    
    with open(bot_path, 'w', encoding='utf-8') as f:
        f.write(codigo)
    
    print("✅ Bot iniciado! http://127.0.0.1:5000")
    subprocess.run([sys.executable, bot_path])
    
except Exception as e:
    print(f"Erro: {e}")
    input("Enter para sair...")
