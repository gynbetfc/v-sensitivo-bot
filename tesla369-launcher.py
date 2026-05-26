
import requests
import base64
import subprocess
import sys
import os
import tempfile
import atexit
import time
import webbrowser

BOT_URL = "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/main.py"
bot_path = os.path.join(tempfile.gettempdir(), "_t369_bot.py")

def limpar():
    try:
        if os.path.exists(bot_path):
            os.remove(bot_path)
    except:
        pass

# 1. Remove versão antiga
print("🧹 Removendo versão antiga...")
limpar()

# 2. Mata processos antigos
try:
    if sys.platform == 'win32':
        os.system('taskkill /f /im python.exe 2>nul')
    else:
        os.system('pkill -f "_t369_bot.py" 2>/dev/null')
    time.sleep(1)
except:
    pass

atexit.register(limpar)

print("⚡ TESLA 369 BOT - PC")
print("=" * 40)

try:
    # 3. Baixa versão NOVA
    print("📥 Baixando versão mais recente...")
    headers = {'Cache-Control': 'no-cache'}
    r = requests.get(BOT_URL, headers=headers, timeout=30)
    codigo = r.text
    
    # Decodifica se Base64
    if not codigo.strip().startswith('#') and not codigo.strip().startswith('from'):
        codigo = base64.b64decode(codigo).decode('utf-8')
        if not codigo.strip().startswith('#') and not codigo.strip().startswith('from'):
            codigo = base64.b64decode(codigo).decode('utf-8')
    
    # 4. Salva novo arquivo
    with open(bot_path, 'w', encoding='utf-8') as f:
        f.write(codigo)
    
    print("✅ Bot atualizado!")
    
    # 5. Inicia o bot em background
    print("🚀 Iniciando servidor...")
    if sys.platform == 'win32':
        subprocess.Popen([sys.executable, bot_path], creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        subprocess.Popen([sys.executable, bot_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # 6. Espera 3 segundos
    time.sleep(3)
    
    # 7. Abre navegador
    print("🌐 Abrindo navegador...")
    webbrowser.open("http://127.0.0.1:5000")
    
    # 8. Launcher se auto-fecha
    print("✅ Bot rodando! Esta janela vai fechar.")
    time.sleep(1)
    
except Exception as e:
    print(f"❌ Erro: {e}")
    input("Pressione Enter para sair...")
