#!/usr/bin/env python3
import requests
import base64
import sys
import time
import webbrowser

BASE_URL = "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/tesla_369"
modulos = {}

def baixar(nome, caminho):
    try:
        r = requests.get(BASE_URL + "/" + caminho, timeout=10)
        if r.status_code == 200:
            modulos[nome] = r.text
            print("  OK " + nome)
        else:
            print("  ERRO " + nome + " HTTP " + str(r.status_code))
    except Exception as e:
        print("  FALHA " + nome + ": " + str(e))

print("⚡ TESLA 369 v6.5.2")
print("📥 Baixando modulos...")

baixar("fb", "core/firebase.py")
baixar("ind", "core/indicadores.py")
baixar("mp", "core/mercado_pago.py")
baixar("skins_init", "skins/__init__.py")
baixar("skins_padrao", "skins/padrao.py")
baixar("skins_bob", "skins/bobmarley.py")
baixar("skins_dark", "skins/dark.py")
baixar("skins_neon", "skins/neon.py")
baixar("skins_br", "skins/brasil.py")
baixar("skins_fire", "skins/fire.py")
baixar("skins_ice", "skins/ice.py")
baixar("skins_sakura", "skins/sakura.py")
baixar("skins_sunset", "skins/sunset.py")
baixar("skins_ocean", "skins/ocean.py")
baixar("skins_matrix", "skins/matrix.py")
baixar("skins_thunder", "skins/thunder.py")
baixar("skins_magos", "skins/magos.py")
baixar("skins_princesa", "skins/princesa.py")
baixar("est_init", "estrategias/__init__.py")
baixar("est_tesla", "estrategias/tesla_369.py")
baixar("est_v", "estrategias/v_sensitivo.py")
baixar("est_m5", "estrategias/m5.py")
baixar("main", "main.py")

# Junta tudo
tudo = ""
for k, v in modulos.items():
    if k != "main":
        tudo = tudo + v + "
"

main_code = modulos.get("main", "print('ERRO: main.py nao encontrado')")
main_code = main_code.replace("from core.firebase import", "#")
main_code = main_code.replace("from core.indicadores import", "#")
main_code = main_code.replace("from core.mercado_pago import", "#")
main_code = main_code.replace("from skins import", "#")
main_code = main_code.replace("from estrategias import", "#")
tudo = tudo + main_code

print("🚀 Executando...")
try:
    exec(tudo, {"__name__": "__main__"})
except Exception as e:
    print("❌ Erro: " + str(e))
    import traceback
    traceback.print_exc()
    input("Enter para sair...")
