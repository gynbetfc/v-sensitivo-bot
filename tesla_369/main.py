# ⚡ TESLA 369 BOT v6.5.1 ⚡
from flask import Flask, render_template_string, jsonify, request
from iqoptionapi.stable_api import IQ_Option
from datetime import datetime
import threading, time, sys, os, json, warnings, requests, uuid, base64

warnings.filterwarnings("ignore")
app = Flask(__name__)

# Importa módulos organizados
from core.firebase import salvar_usuario, carregar_usuario, criar_usuario, FB_URL
from core.indicadores import sma, bollinger, rsi, macd, estocastico
from core.mercado_pago import gerar_pix_mercadopago, verificar_pagamento_mp
from skins import SKINS
from estrategias import ESTRATEGIAS

# Configurações
MARTINGALE = 2
PAYOUT_PADRAO = 0.85
PERCENTUAL_BANCA = 15
PLANOS = [
    {'id':1,'moedas':1,'preco':0.99,'nome':'🔰 TESTE'},
    {'id':2,'moedas':6,'preco':6.69,'nome':'⭐ BÁSICO'},
    {'id':3,'moedas':15,'preco':9.99,'nome':'💎 INTERMEDIÁRIO','desconto':'33% OFF'},
    {'id':4,'moedas':36,'preco':21.69,'nome':'🔥 PREMIUM','desconto':'40% OFF'},
    {'id':5,'moedas':69,'preco':39.69,'nome':'👑 ULTRA','desconto':'69% OFF'},
]

print("✅ Tesla 369 v6.5.1 - Estrutura Modular")
print("📁 Skins carregadas:", len(SKINS))
print("📊 Estratégias carregadas:", len(ESTRATEGIAS))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
