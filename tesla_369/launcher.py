#!/usr/bin/env python3
import requests, base64, sys, os, time
os.chdir(os.path.expanduser("~"))
print("⚡ TESLA 369 v6.5.2")
BASE = "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/tesla_369"
# Baixa módulos
for nome, arq in [("skins", "modulos/skins.py"), ("estrategias", "modulos/estrategias.py")]:
    r = requests.get(f"{BASE}/{arq}", timeout=10)
    if r.status_code == 200: exec(r.text, globals())
# Baixa main.py
r = requests.get(f"{BASE}/main.py", timeout=10)
main_code = r.text
if not main_code.strip().startswith('#') and not main_code.strip().startswith('from'):
    main_code = base64.b64decode(main_code).decode('utf-8')
print("🚀 Executando...")
exec(main_code, {"__name__": "__main__"})
