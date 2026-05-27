#!/usr/bin/env python3
import requests
import base64
import sys
import os
import time

os.chdir(os.path.expanduser("~"))

print("⚡ TESLA 369 v6.5.2")
print("📥 Baixando modulos da nova estrutura...")

BASE = "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/tesla_369"

# Baixa todos os modulos
modulos = {}
arquivos = [
    "core/firebase.py",
    "core/indicadores.py", 
    "core/mercado_pago.py",
    "skins/__init__.py",
    "skins/padrao.py",
    "skins/dark.py",
    "skins/neon.py",
    "skins/bobmarley.py",
    "skins/brasil.py",
    "skins/fire.py",
    "skins/ice.py",
    "skins/sakura.py",
    "skins/sunset.py",
    "skins/ocean.py",
    "skins/matrix.py",
    "skins/thunder.py",
    "skins/magos.py",
    "skins/princesa.py",
    "estrategias/__init__.py",
    "estrategias/tesla_369.py",
    "estrategias/v_sensitivo.py",
    "estrategias/m5.py",
    "estrategias/terceira_igual_primeira.py",
    "estrategias/mhi_filtrado.py",
    "estrategias/quadrante_de_7.py",
    "estrategias/fluxo_de_velas.py",
    "estrategias/reversao.py",
    "main.py"
]

for arq in arquivos:
    try:
        r = requests.get(f"{BASE}/{arq}", timeout=10)
        if r.status_code == 200:
            modulos[arq] = r.text
            print(f"  ✅ {arq}")
        else:
            print(f"  ⚠️ {arq} (HTTP {r.status_code})")
    except Exception as e:
        print(f"  ❌ {arq}: {e}")

# Junta tudo em um unico script
codigo_completo = ""
for arq, conteudo in modulos.items():
    if arq != "main.py":
        codigo_completo += conteudo + "
"

# Adiciona o main.py (remove imports relativos)
main_code = modulos.get("main.py", "")
main_code = main_code.replace("from core.firebase import", "# from core.firebase")
main_code = main_code.replace("from core.indicadores import", "# from core.indicadores")
main_code = main_code.replace("from core.mercado_pago import", "# from core.mercado_pago")
main_code = main_code.replace("from skins import", "# from skins")
main_code = main_code.replace("from estrategias import", "# from estrategias")
codigo_completo += main_code

print("🚀 Executando...")
try:
    exec(codigo_completo, {"__name__": "__main__"})
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
    input("Enter para sair...")
