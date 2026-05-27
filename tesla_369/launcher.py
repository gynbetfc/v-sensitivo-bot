#!/usr/bin/env python3
import requests
import base64
import sys
import os
import time

os.chdir(os.path.expanduser("~"))

print("⚡ TESLA 369 v6.5.2")
print("📥 Baixando...")

url = "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/tesla_369/main.py"
r = requests.get(url, timeout=30)
codigo = r.text

if not codigo.strip().startswith('#') and not codigo.strip().startswith('from'):
    codigo = base64.b64decode(codigo).decode('utf-8')
    if not codigo.strip().startswith('#') and not codigo.strip().startswith('from'):
        codigo = base64.b64decode(codigo).decode('utf-8')

print("🚀 Executando...")
exec(codigo, {"__name__": "__main__"})
