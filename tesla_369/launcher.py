#!/usr/bin/env python3
import requests
import base64
import sys
import time

print("⚡ TESLA 369 v6.5.2")
print("📥 Baixando codigo...")

url = "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/main.py"
r = requests.get(url, timeout=30)
codigo = r.text

# Decodifica se Base64
if not codigo.strip().startswith('#') and not codigo.strip().startswith('from'):
    codigo = base64.b64decode(codigo).decode('utf-8')
    if not codigo.strip().startswith('#') and not codigo.strip().startswith('from'):
        codigo = base64.b64decode(codigo).decode('utf-8')

print("🚀 Executando...")
exec(codigo, {"__name__": "__main__"})
