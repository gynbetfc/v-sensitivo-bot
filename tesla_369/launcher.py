#!/usr/bin/env python3
"""
⚡ TESLA 369 LAUNCHER v6.5.2
Lê o código DIRETO do GitHub em tempo real
NÃO salva nada no dispositivo
"""
import requests
import base64
import sys
import time
import webbrowser

GITHUB_REPO = "gynbetfc/v-sensitivo-bot"
GITHUB_BRANCH = "main"
BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/tesla_369"

print("⚡ TESLA 369 v6.5.2 - Carregando...")

# ═══════════ Baixa todos os módulos como texto ═══════════
modulos = {}

def baixar_modulo(nome, caminho):
    try:
        url = f"{BASE_URL}/{caminho}"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            modulos[nome] = r.text
            print(f"  ✅ {nome}")
            return True
        else:
            print(f"  ⚠️ {nome} (HTTP {r.status_code})")
            return False
    except Exception as e:
        print(f"  ❌ {nome}: {e}")
        return False

print("📥 Baixando módulos...")
baixar_modulo("firebase", "core/firebase.py")
baixar_modulo("indicadores", "core/indicadores.py")
baixar_modulo("mercado_pago", "core/mercado_pago.py")
baixar_modulo("skins_init", "skins/__init__.py")
baixar_modulo("skins_padrao", "skins/padrao.py")
baixar_modulo("skins_bobmarley", "skins/bobmarley.py")
baixar_modulo("estrategias_init", "estrategias/__init__.py")
baixar_modulo("estrategia_tesla369", "estrategias/tesla_369.py")
baixar_modulo("main", "main.py")

# ═══════════ Junta tudo em um único script ═══════════
codigo_completo = ""
for nome, conteudo in modulos.items():
    if nome != "main":
        codigo_completo += conteudo + "
"

# Adiciona o main.py (substitui os imports por nada, pois já juntamos tudo)
main_code = modulos.get("main", "")
main_code = main_code.replace("from core.firebase import", "# from core.firebase import")
main_code = main_code.replace("from core.indicadores import", "# from core.indicadores import")
main_code = main_code.replace("from core.mercado_pago import", "# from core.mercado_pago import")
main_code = main_code.replace("from skins import", "# from skins import")
main_code = main_code.replace("from estrategias import", "# from estrategias import")

codigo_completo += main_code

# ═══════════ Executa TUDO em memória ═══════════
print("🚀 Executando...")
namespace = {"__name__": "__main__"}
try:
    exec(codigo_completo, namespace)
except Exception as e:
    print(f"❌ Erro: {e}")
    # Mostra a linha do erro
    import traceback
    traceback.print_exc()
    input("Pressione Enter para sair...")
