#!/usr/bin/env python3
"""
⚡ TESLA 369 LAUNCHER v6.5.2 v6.5.2
Lê o código DIRETO do GitHub em tempo real
NÃO salva nada no dispositivo
"""
import requests
import base64
import sys
import os
import tempfile
import atexit
import time
import webbrowser

GITHUB_REPO = "gynbetfc/v-sensitivo-bot"
GITHUB_BRANCH = "main"
BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/tesla_369"

print("⚡ TESLA 369 - Carregando módulos...")

# ═══════════ FUNÇÃO MÁGICA: baixa e executa em memória ═══════════
def executar_modulo(nome, url):
    """Baixa o código e executa em memória, sem salvar no disco"""
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            print(f"⚠️ Módulo {nome} não encontrado")
            return None
        
        codigo = r.text
        # Se estiver em Base64, decodifica
        if not codigo.strip().startswith('#') and not codigo.strip().startswith('from') and not codigo.strip().startswith('import'):
            try:
                codigo = base64.b64decode(codigo).decode('utf-8')
            except:
                pass
        
        # Executa o código em memória
        namespace = {}
        exec(codigo, namespace)
        return namespace
    except Exception as e:
        print(f"❌ Erro ao carregar {nome}: {e}")
        return None

print("📥 Baixando core...")
core_firebase = executar_modulo("firebase", f"{BASE_URL}/core/firebase.py")
core_indicadores = executar_modulo("indicadores", f"{BASE_URL}/core/indicadores.py")
core_mp = executar_modulo("mercado_pago", f"{BASE_URL}/core/mercado_pago.py")

print("📥 Baixando skins...")
skins_ns = executar_modulo("skins_init", f"{BASE_URL}/skins/__init__.py")

print("📥 Baixando estratégias...")
estrategias_ns = executar_modulo("estrategias_init", f"{BASE_URL}/estrategias/__init__.py")

print("📥 Baixando main.py...")
main_ns = executar_modulo("main", f"{BASE_URL}/main.py")

if main_ns:
    print("✅ Todos os módulos carregados!")
    print("🚀 Iniciando Tesla 369...")
    
    # Inicia o servidor Flask
    if 'app' in main_ns:
        # Abre o navegador
        time.sleep(2)
        webbrowser.open("http://127.0.0.1:5000")
        
        # Roda o app
        main_ns['app'].run(host='0.0.0.0', port=5000, debug=False, threaded=True)
else:
    print("❌ Falha ao carregar o bot!")
    print("Verifique sua conexão com a internet.")
    input("Pressione Enter para sair...")
