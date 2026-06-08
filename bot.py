#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ⚡ TESLA 369 BOT v9.0.0 - MODO SINAL EXTERNO ⚡
# Recebe sinais via POST /sinal

from flask import Flask, render_template_string, jsonify, request
from iqoptionapi.stable_api import IQ_Option
from datetime import datetime
import threading
import time
import sys
import os
import warnings
import requests
import uuid

warnings.filterwarnings("ignore")
app = Flask(__name__)

# ============= CONFIGURAÇÕES FIXAS =============
FB_URL = "https://nexos-40654-default-rtdb.firebaseio.com"
print("✅ Firebase HTTP REST configurado!")

MARTINGALE = 2
PAYOUT_PADRAO = 0.85
PERCENTUAL_BANCA = 15

# ⭐ CONFIGURAÇÃO DO MERCADO PAGO ⭐
MERCADO_PAGO_ACCESS_TOKEN = os.environ.get("MP_ACCESS_TOKEN", "APP_USR-4548266140377032-050311-6589fc22b166e4cb2cfad0379b28dcdf-1059299796")
MODO_SIMULACAO = False

# ⭐ PLANOS DE VOLTS ⭐
PLANOS = [
    {'id':1,'moedas':1,'preco':0.99,'nome':'🔰 TESTE','desc':'R$0,99/VOLT','tag':'1 ciclo','bonus':''},
    {'id':2,'moedas':6,'preco':6.69,'nome':'⭐ BÁSICO','desc':'R$1,11/VOLT','tag':'6 ciclos','bonus':''},
    {'id':3,'moedas':15,'preco':9.99,'nome':'💎 INTERMEDIÁRIO','desc':'R$0,67/VOLT','tag':'15 ciclos','bonus':'🎨 1 Skin Básica GRÁTIS','desconto':'33% OFF'},
    {'id':4,'moedas':36,'preco':21.69,'nome':'🔥 PREMIUM','desc':'R$0,60/VOLT','tag':'36 ciclos','bonus':'🎨 1 Skin Premium GRÁTIS','desconto':'40% OFF'},
    {'id':5,'moedas':69,'preco':39.69,'nome':'👑 ULTRA','desc':'R$0,57/VOLT','tag':'69 ciclos','bonus':'🎨 1 Skin Lendária GRÁTIS','desconto':'69% OFF'},
]

# ⭐ SKINS DA LOJA ⭐
SKINS = [
    {
        'id': 'skin_padrao', 'nome': '⚡ TESLA PADRÃO', 'desc': 'Tema escuro com raios dourados', 'preco_moedas': 0, 'categoria': 'basica',
        'cor_fundo': '#0a0a1a', 'cor_panel': '#1a1a3e', 'cor_destaque': '#ffd700', 'cor_texto': '#fff',
        'cor_botao': 'linear-gradient(135deg,#cc8800,#ffd700)', 'cor_tab_ativa': '#ffd700',
        'cor_header_bg': 'linear-gradient(135deg,#1a0000,#331100,#553300,#331100,#1a0000)', 'cor_header_borda': '#ffd700',
        'header_extra': '<div class="lightning"></div>',
        'css_extra': '.lightning{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:150px;height:150px;background:radial-gradient(circle at 30% 30%,rgba(255,215,0,0.3) 0%,rgba(255,165,0,0.15) 30%,transparent 100%);border-radius:50%;z-index:0;animation:glow 3s ease-in-out infinite;pointer-events:none}@keyframes glow{0%,100%{box-shadow:0 0 30px rgba(255,215,0,0.3)}50%{box-shadow:0 0 50px rgba(255,165,0,0.5)}}.lightning::after{content:"⚡";position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:50px;animation:float 2s ease-in-out infinite}@keyframes float{0%,100%{transform:translate(-50%,-50%) scale(1)}50%{transform:translate(-50%,-60%) scale(1.1)}}'
    },
    {
        'id': 'skin_dark', 'nome': '🌑 TESLA DARK', 'desc': 'Particulas roxas flutuantes', 'preco_moedas': 6, 'categoria': 'basica',
        'cor_fundo': '#000000', 'cor_panel': '#0a0a0a', 'cor_destaque': '#9933ff', 'cor_texto': '#ccc',
        'cor_botao': 'linear-gradient(135deg,#4400aa,#9933ff)', 'cor_tab_ativa': '#9933ff',
        'cor_header_bg': 'linear-gradient(135deg,#000000,#110022,#220044,#110022,#000000)', 'cor_header_borda': '#9933ff',
        'header_extra': '<canvas id="darkCanvas" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none"></canvas>',
        'css_extra': 'body{background:#000000!important}.header{border-color:#9933ff!important;box-shadow:0 0 40px rgba(153,51,255,0.3)}'
    },
    {
        'id': 'skin_neon', 'nome': '💜 TESLA NEON', 'desc': 'Brilho neon roxo pulsante', 'preco_moedas': 6, 'categoria': 'basica',
        'cor_fundo': '#0a0015', 'cor_panel': '#150025', 'cor_destaque': '#cc00ff', 'cor_texto': '#e0c0ff',
        'cor_botao': 'linear-gradient(135deg,#8800cc,#cc00ff)', 'cor_tab_ativa': '#cc00ff',
        'cor_header_bg': 'linear-gradient(135deg,#0a0015,#150030,#200050,#150030,#0a0015)', 'cor_header_borda': '#cc00ff',
        'header_extra': '<div class="neon-glow"></div>',
        'css_extra': '.neon-glow{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:200px;height:200px;background:radial-gradient(circle,rgba(204,0,255,0.2) 0%,transparent 70%);border-radius:50%;z-index:0;animation:neonPulse 2s ease-in-out infinite;pointer-events:none}@keyframes neonPulse{0%,100%{transform:translate(-50%,-50%) scale(1);opacity:0.5}50%{transform:translate(-50%,-50%) scale(1.3);opacity:0.8}}body{background:#0a0015!important}.header{border-color:#cc00ff!important;box-shadow:0 0 30px rgba(204,0,255,0.4)}'
    },
    {
        'id': 'skin_matrix', 'nome': '🧬 TESLA MATRIX', 'desc': 'Chuva de caracteres verdes', 'preco_moedas': 12, 'categoria': 'lendaria',
        'cor_fundo': '#000000', 'cor_panel': '#0a0a0a', 'cor_destaque': '#00ff00', 'cor_texto': '#00cc00',
        'cor_botao': 'linear-gradient(135deg,#004400,#00ff00)', 'cor_tab_ativa': '#00ff00',
        'cor_header_bg': 'linear-gradient(135deg,#000000,#001100,#003300,#001100,#000000)', 'cor_header_borda': '#00ff00',
        'header_extra': '<canvas id="matrixCanvas" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none"></canvas>',
        'css_extra': 'body{background:#000000!important}.header{border-color:#00ff00!important;box-shadow:0 0 30px rgba(0,255,0,0.4)}.terminal{color:#00ff00!important;font-family:monospace!important}'
    },
    {
        'id': 'skin_sakura', 'nome': '🌸 TESLA SAKURA', 'desc': 'Pétalas de cerejeira caindo', 'preco_moedas': 9, 'categoria': 'premium',
        'cor_fundo': '#1a0a1a', 'cor_panel': '#2a0a2a', 'cor_destaque': '#ff69b4', 'cor_texto': '#ffe0f0',
        'cor_botao': 'linear-gradient(135deg,#cc3388,#ff69b4)', 'cor_tab_ativa': '#ff69b4',
        'cor_header_bg': 'linear-gradient(135deg,#1a0020,#330033,#4d004d,#330033,#1a0020)', 'cor_header_borda': '#ff69b4',
        'header_extra': '<canvas id="sakuraCanvas" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none"></canvas>',
        'css_extra': 'body{background:linear-gradient(180deg,#1a0a1a 0%,#0d001a 100%)!important}.header{border-color:#ff69b4!important;box-shadow:0 0 40px rgba(255,105,180,0.3)}'
    },
    {
        'id': 'skin_thunder', 'nome': '⚡ TESLA THUNDER', 'desc': 'Raios elétricos na tela', 'preco_moedas': 12, 'categoria': 'lendaria',
        'cor_fundo': '#000011', 'cor_panel': '#0a0a1a', 'cor_destaque': '#ffff00', 'cor_texto': '#ffffff',
        'cor_botao': 'linear-gradient(135deg,#aaaa00,#ffff00)', 'cor_tab_ativa': '#ffff00',
        'cor_header_bg': 'linear-gradient(135deg,#000011,#111122,#222244,#111122,#000011)', 'cor_header_borda': '#ffff00',
        'header_extra': '<canvas id="thunderCanvas" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none"></canvas>',
        'css_extra': 'body{background:#000011!important}.header{border-color:#ffff00!important;box-shadow:0 0 30px rgba(255,255,0,0.3)}'
    },
    {
        'id': 'skin_ocean', 'nome': '🌊 TESLA OCEAN', 'desc': 'Ondas do mar em movimento', 'preco_moedas': 9, 'categoria': 'premium',
        'cor_fundo': '#001020', 'cor_panel': '#0a1a2a', 'cor_destaque': '#00aacc', 'cor_texto': '#aaddff',
        'cor_botao': 'linear-gradient(135deg,#006688,#00aacc)', 'cor_tab_ativa': '#00aacc',
        'cor_header_bg': 'linear-gradient(135deg,#001020,#002040,#003060,#002040,#001020)', 'cor_header_borda': '#00aacc',
        'header_extra': '<canvas id="oceanCanvas" style="position:absolute;bottom:0;left:0;width:100%;height:100px;z-index:0"></canvas>',
        'css_extra': 'body{background:linear-gradient(180deg,#001020 0%,#000810 100%)!important}.header{border-color:#00aacc!important;box-shadow:0 0 30px rgba(0,170,204,0.3)}'
    },
    {
        'id': 'skin_sunset', 'nome': '🌅 TESLA SUNSET', 'desc': 'Ceu em degradê animado', 'preco_moedas': 9, 'categoria': 'premium',
        'cor_fundo': '#1a0010', 'cor_panel': '#2a0a1a', 'cor_destaque': '#ff6600', 'cor_texto': '#ffddaa',
        'cor_botao': 'linear-gradient(135deg,#cc4400,#ff8800)', 'cor_tab_ativa': '#ff6600',
        'cor_header_bg': 'linear-gradient(135deg,#1a0000,#331100,#552200,#331100,#1a0000)', 'cor_header_borda': '#ff6600',
        'header_extra': '<canvas id="sunsetCanvas" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none"></canvas>',
        'css_extra': 'body{background:linear-gradient(180deg,#1a0010 0%,#331100 50%,#1a0000 100%)!important}.header{border-color:#ff6600!important;box-shadow:0 0 30px rgba(255,102,0,0.3)}'
    },
    {
        'id': 'skin_magos', 'nome': '🔮 MAGOS DA BOLA DE CRISTAL', 'desc': 'Tema roxo místico', 'preco_moedas': 12, 'categoria': 'lendaria',
        'cor_fundo': '#0a0a1a', 'cor_panel': '#1a1a3e', 'cor_destaque': '#cc66ff', 'cor_texto': '#e0d0ff',
        'cor_botao': 'linear-gradient(135deg,#6600cc,#9933ff)', 'cor_tab_ativa': '#9933ff',
        'cor_header_bg': 'linear-gradient(135deg,#0d001a,#1a0033,#2d0055,#1a0033,#0d001a)', 'cor_header_borda': '#9933ff',
        'header_extra': '<div class="crystal-ball"></div><div class="mago mago-esq">🧙‍♂️</div><div class="mago mago-dir">🧙‍♀️</div>',
        'css_extra': '.crystal-ball{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:130px;height:130px;background:radial-gradient(circle at 30% 30%,rgba(200,150,255,0.4) 0%,rgba(153,51,255,0.2) 30%,transparent 70%);border-radius:50%;z-index:0;animation:crystalGlow 4s ease-in-out infinite;pointer-events:none;border:2px solid rgba(153,51,255,0.3)}@keyframes crystalGlow{0%,100%{box-shadow:0 0 30px rgba(153,51,255,0.4),0 0 60px rgba(153,51,255,0.2)}50%{box-shadow:0 0 50px rgba(200,100,255,0.6),0 0 80px rgba(200,100,255,0.3)}}.crystal-ball::after{content:"🔮";position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:45px;animation:floatCrystal 3s ease-in-out infinite}@keyframes floatCrystal{0%,100%{transform:translate(-50%,-50%) scale(1)}50%{transform:translate(-50%,-60%) scale(1.1)}}.mago{position:absolute;top:50%;font-size:30px;z-index:1;animation:magoFloat 2s ease-in-out infinite;pointer-events:none}.mago-esq{left:15px}.mago-dir{right:15px;animation-delay:0.5s}@keyframes magoFloat{0%,100%{transform:translateY(-50%)}50%{transform:translateY(-60%)}}'
    },
    {
        'id': 'skin_brasil', 'nome': '🇧🇷 BRASIL', 'desc': 'Tema verde e amarelo', 'preco_moedas': 0, 'categoria': 'basica',
        'cor_fundo': '#001a0a', 'cor_panel': '#0a2a15', 'cor_destaque': '#ffd700', 'cor_texto': '#fff',
        'cor_botao': 'linear-gradient(135deg,#009933,#00cc44)', 'cor_tab_ativa': '#ffd700',
        'cor_header_bg': 'linear-gradient(135deg,#001a0a,#003315,#004d20,#003315,#001a0a)', 'cor_header_borda': '#ffd700',
        'header_extra': '<div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:60px;z-index:0;opacity:0.3;pointer-events:none">🇧🇷</div>', 'css_extra': ''
    },
    {
        'id': 'skin_fire', 'nome': '🔥 TESLA FIRE', 'desc': 'Chamas realistas na base', 'preco_moedas': 9, 'categoria': 'premium',
        'cor_fundo': '#1a0000', 'cor_panel': '#2a0a0a', 'cor_destaque': '#ff4400', 'cor_texto': '#ffccaa',
        'cor_botao': 'linear-gradient(135deg,#cc2200,#ff6600)', 'cor_tab_ativa': '#ff4400',
        'cor_header_bg': 'linear-gradient(135deg,#1a0000,#330000,#551100,#330000,#1a0000)', 'cor_header_borda': '#ff4400',
        'header_extra': '<canvas id="fireCanvas" style="position:absolute;bottom:0;left:0;width:100%;height:80px;z-index:0"></canvas>',
        'css_extra': 'body{background:radial-gradient(ellipse at bottom,#1a0000 0%,#000000 100%)!important}.header{border-color:#ff4400!important;box-shadow:0 0 30px rgba(255,68,0,0.4)}'
    },
    {
        'id': 'skin_ice', 'nome': '❄️ TESLA ICE', 'desc': 'Neve caindo com cristais', 'preco_moedas': 9, 'categoria': 'premium',
        'cor_fundo': '#000a1a', 'cor_panel': '#0a102a', 'cor_destaque': '#3399ff', 'cor_texto': '#aaccff',
        'cor_botao': 'linear-gradient(135deg,#0044aa,#3399ff)', 'cor_tab_ativa': '#3399ff',
        'cor_header_bg': 'linear-gradient(135deg,#000a1a,#001133,#002255,#001133,#000a1a)', 'cor_header_borda': '#3399ff',
        'header_extra': '<canvas id="snowCanvas" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none"></canvas>',
        'css_extra': 'body{background:linear-gradient(180deg,#000a1a 0%,#001133 100%)!important}.header{border-color:#3399ff!important;box-shadow:0 0 30px rgba(51,153,255,0.3)}'
    },
    {
        'id': 'skin_princesa', 'nome': '👸 PRINCESA', 'desc': 'Tema rosa com brilhos', 'preco_moedas': 6, 'categoria': 'basica',
        'cor_fundo': '#1a0010', 'cor_panel': '#2a0a20', 'cor_destaque': '#ff69b4', 'cor_texto': '#ffe0f0',
        'cor_botao': 'linear-gradient(135deg,#cc3388,#ff69b4)', 'cor_tab_ativa': '#ff69b4',
        'cor_header_bg': 'linear-gradient(135deg,#1a0010,#2a0a20,#3a1530,#2a0a20,#1a0010)', 'cor_header_borda': '#ff69b4',
        'header_extra': '<div class="coroa-p">👑</div>',
        'css_extra': '.coroa-p{position:absolute;top:10px;left:50%;transform:translateX(-50%);font-size:40px;animation:float 2s ease-in-out infinite}@keyframes float{0%,100%{transform:translateX(-50%) translateY(0)}50%{transform:translateX(-50%) translateY(-10px)}}.header h1{color:#ff69b4!important;text-shadow:0 0 30px #ff1493!important}'
    },
]

def _sanitizar_dados(dados):
    if 'historico_operacoes' in dados:
        if len(dados['historico_operacoes']) > 50:
            dados['historico_operacoes'] = dados['historico_operacoes'][-50:]
        for op in dados['historico_operacoes']:
            for chave in list(op.keys()):
                if isinstance(op[chave], float):
                    op[chave] = round(op[chave], 2)
    return dados

def salvar_usuario(email, dados):
    try:
        key = email.replace("@", "_").replace(".", "_").replace("#", "").replace("$", "").replace("[", "").replace("]", "").replace("/", "_")
        dados = _sanitizar_dados(dados)
        requests.put(f'{FB_URL}/tesla_369/usuarios/{key}.json', json=dados)
    except Exception as e:
        print(f"⚠️ Firebase offline: {e}")

def carregar_usuario(email):
    try:
        key = email.replace("@", "_").replace(".", "_").replace("#", "").replace("$", "").replace("[", "").replace("]", "").replace("/", "_")
        r = requests.get(f'{FB_URL}/tesla_369/usuarios/{key}.json')
        if r.status_code == 200 and r.json():
            return r.json()
    except:
        pass
    return None

def criar_usuario(email):
    dados = {
        'email': email,
        'moedas': 12,
        'moedas_ganhas_hoje': str(datetime.now())[:10],
        'total_ciclos': 0, 'total_wins': 0, 'total_losses': 0,
        'total_gasto': 0.0, 'total_ganho': 0.0, 'lucro_total': 0.0,
        'banca_atual': 0.0, 'data_cadastro': str(datetime.now())[:19],
        'historico_operacoes': [],
        'dias_ativos': 0,
        'skin_atual': 'skin_padrao', 'skins_compradas': ['skin_padrao']
    }
    salvar_usuario(email, dados)
    return dados

# ============= VARIÁVEIS GLOBAIS =============
API, par = None, "EURUSD-OTC"
timeframe_atual = 60
lucro, NumDeOperacoes = 0.0, 0
BANCA_INICIAL_DO_BOT, STOP_GAIN_ATINGIDO = 0, False
bot_rodando, bot_thread = False, None
conectado_iq = False
ultimo_sinal = "Aguardando sinal externo..."
logs_web, MAX_LOGS_WEB = [], 200
email_usuario_atual = ""
skin_atual_global = 'skin_padrao'
pagamentos_pendentes = {}
bot_lock = threading.Lock()
sinal_pendente = None
sinal_lock = threading.Lock()

def add_log(msg, tipo='info'):
    global logs_web
    t = datetime.now().strftime('%H:%M:%S')
    logs_web.append({'time': t, 'msg': msg, 'tipo': tipo})
    if len(logs_web) > MAX_LOGS_WEB:
        logs_web = logs_web[-MAX_LOGS_WEB:]
    print(f"{t} - {msg}")

def get_logs_html(limite=40):
    html = ''
    for log in logs_web[-limite:]:
        cor = {'win': '#00ff88', 'loss': '#ff4444', 'info': '#00ff88', 'sensitive': '#ff69b4', 'indicator': '#ffd700', 'error': '#ff4444'}.get(log['tipo'], '#00ff88')
        html += f'<span style="color:#666">{log["time"]}</span> <span style="color:{cor}">{log["msg"]}</span>\n'
    return html or '📡 Aguardando...'

def Payout(p):
    try:
        if not API:
            return PAYOUT_PADRAO
        API.subscribe_strike_list(p, 1)
        tentativas = 0
        while tentativas < 20:
            d = API.get_digital_current_profit(p, 1)
            if d != False:
                API.unsubscribe_strike_list(p, 1)
                return round(int(d) / 100, 2)
            time.sleep(0.5)
            tentativas += 1
        API.unsubscribe_strike_list(p, 1)
        return PAYOUT_PADRAO
    except:
        return PAYOUT_PADRAO

def calcular_entradas(b, p, g):
    global PERCENTUAL_BANCA
    bs = (b * PERCENTUAL_BANCA / 100) * 0.99
    e0 = bs / sum((1/p)**i for i in range(g+1))
    entradas = [e0]
    for i in range(1, g+1):
        entradas.append((sum(entradas) + e0) / p)
    ajuste = bs / sum(entradas)
    entradas = [round(e * ajuste, 2) for e in entradas]
    soma = sum(entradas)
    if soma > b:
        entradas[-1] = round(entradas[-1] - (soma - b) - 0.02, 2)
    return [max(1, e) for e in entradas]

def pegar_timestamp():
    try:
        if not API:
            return 0
        v = API.get_candles(par, timeframe_atual, 1, time.time())
        if v and isinstance(v, list) and len(v) > 0:
            return v[0]['from']
    except Exception as e:
        add_log(f"Erro ao pegar timestamp: {e}", 'error')
    return 0

def aguardar_inicio_vela():
    add_log("   ⏳ Aguardando início da vela...", 'info')
    while datetime.now().second > 5:
        if not bot_rodando:
            return False
        time.sleep(0.3)
    while True:
        if not bot_rodando:
            return False
        ts1 = pegar_timestamp()
        time.sleep(0.5)
        ts2 = pegar_timestamp()
        if ts1 == ts2 and ts1 != 0:
            add_log("   ✅ Vela confirmada!", 'info')
            return True
        if ts1 == 0 or ts2 == 0:
            time.sleep(0.3)
            continue

def aguardar_vela_fechar(ts_entrada):
    add_log(f"   ⏳ Aguardando vela fechar...", 'info')
    while True:
        if not bot_rodando:
            return False
        try:
            ts_atual = pegar_timestamp()
            if ts_atual != ts_entrada and ts_atual != 0:
                add_log("   ✅ Vela fechou!", 'info')
                return True
        except:
            pass
        time.sleep(0.3)

def verificar_resultado(saldo_antes, valor):
    saldo_base = saldo_antes - valor
    try:
        if not API:
            return -valor
        s = API.get_balance()
        d = round(s - saldo_base, 2)
        if d >= 1.0:
            return d
    except:
        pass
    return -valor

def executar_ciclo(direcao):
    global lucro, NumDeOperacoes, STOP_GAIN_ATINGIDO, bot_rodando, ultimo_sinal
    try:
        if not API:
            add_log("❌ API desconectada!", 'error')
            bot_rodando = False
            return
            
        bi = API.get_balance()
        payout = Payout(par)
        entradas = calcular_entradas(bi, payout, MARTINGALE)
        add_log(f"💰 Banca: ${bi:.2f} | Payout: {payout*100:.0f}%", 'info')
        add_log(f"📐 E1:${entradas[0]:.2f} | E2:${entradas[1]:.2f} | E3:${entradas[2]:.2f}", 'info')
        
        for i in range(MARTINGALE + 1):
            if not bot_rodando:
                break
            valor = entradas[i]
            if not aguardar_inicio_vela():
                break
            saldo_antes = API.get_balance()
            if saldo_antes < valor:
                add_log("❌ Saldo insuficiente!", 'error')
                break
            print()
            add_log(f"🎯 {'ENTRADA' if i == 0 else f'GALE {i}'}: {direcao.upper()} ${valor:.2f}", 'info')
            st, id_ordem = API.buy(valor, par, direcao, 1)
            if not st or not id_ordem:
                try:
                    st, id_ordem = API.buy_digital_spot(par, valor, direcao, 1)
                except:
                    pass
            if not st or not id_ordem:
                add_log("❌ Falha na ordem!", 'error')
                break
            add_log(f"   📝 Ordem #{id_ordem}", 'info')
            time.sleep(0.3)
            ts_real = pegar_timestamp()
            if ts_real == 0:
                add_log("⚠️ Não foi possível obter timestamp da vela", 'warning')
                time.sleep(60)
            else:
                if not aguardar_vela_fechar(ts_real):
                    break
            res = verificar_resultado(saldo_antes, valor)
            lucro += round(res, 2)
            saldo_depois = API.get_balance()
            lucro_liquido = round(saldo_depois - saldo_antes, 2)
            
            if res > 0:
                add_log(f"🌟 WIN! +${lucro_liquido:.2f}", 'win')
                NumDeOperacoes += 1
                u = carregar_usuario(email_usuario_atual)
                if u:
                    u['total_wins'] += 1
                    u['total_ganho'] += abs(lucro_liquido)
                    u['lucro_total'] = u['total_ganho'] - u['total_gasto']
                    u['banca_atual'] = round(saldo_depois, 2)
                    u.setdefault('historico_operacoes', []).append({
                        'data': str(datetime.now())[:19],
                        'resultado': 'WIN',
                        'valor': valor,
                        'lucro': lucro_liquido,
                        'estrategia': 'SINAL_EXTERNO'
                    })
                    u['dias_ativos'] = u.get('dias_ativos', 0) + 1
                    salvar_usuario(email_usuario_atual, u)
                STOP_GAIN_ATINGIDO = True
                add_log("🎯 STOP GAIN! Vitória alcançada - Bot PARADO!", 'win')
                ultimo_sinal = "✅ WIN! Bot parado"
                break
            else:
                add_log(f"💀 LOSS! -${valor:.2f}", 'loss')
                u = carregar_usuario(email_usuario_atual)
                if u:
                    u['total_losses'] += 1
                    u['total_gasto'] += valor
                    u['lucro_total'] = u['total_ganho'] - u['total_gasto']
                    u['banca_atual'] = round(saldo_depois, 2)
                    u.setdefault('historico_operacoes', []).append({
                        'data': str(datetime.now())[:19],
                        'resultado': 'LOSS',
                        'valor': valor,
                        'lucro': -valor,
                        'estrategia': 'SINAL_EXTERNO'
                    })
                    u['dias_ativos'] = u.get('dias_ativos', 0) + 1
                    salvar_usuario(email_usuario_atual, u)
                if i < MARTINGALE:
                    add_log(f"   ➡️ Indo para GALE {i + 1}...", 'loss')
                else:
                    add_log("   💀 CICLO COMPLETO PERDIDO! Bot PARADO!", 'loss')
                    ultimo_sinal = "❌ LOSS total! Bot parado"
        
        bf = API.get_balance() if API else bi
        print()
        add_log("=" * 50, 'info')
        add_log(f"{'🌟 LUCRO' if bf > bi else '💀 PERDA'}: ${abs(bf - bi):.2f} | Banca: ${bf:.2f}", 'info')
        add_log("=" * 50, 'info')
    except Exception as e:
        add_log(f"Erro na execução do ciclo: {e}", 'error')
    finally:
        bot_rodando = False
        add_log("⏹️ Ciclo concluído! Clique em CONECTAR e depois COMEÇAR OPERAR para novo ciclo.", 'info')

def bot_loop():
    global bot_rodando, BANCA_INICIAL_DO_BOT, lucro, NumDeOperacoes, STOP_GAIN_ATINGIDO, sinal_pendente, ultimo_sinal    
    with bot_lock:
        if not bot_rodando:
            return
        
        add_log(f'⚡ TESLA 369 v9.0.0 - MODO SINAL EXTERNO', 'sensitive')
        add_log(f'📡 Aguardando sinal via POST /sinal', 'info')
        
        if not API:
            add_log('❌ API não conectada!', 'error')
            bot_rodando = False
            return
            
        BANCA_INICIAL_DO_BOT = API.get_balance()
        STOP_GAIN_ATINGIDO = False
        lucro = 0.0
        NumDeOperacoes = 0
        ultimo_sinal = "📡 Aguardando sinal externo..."
        add_log(f"📌 {par} | Timeframe: {timeframe_atual}s | 💰 ${BANCA_INICIAL_DO_BOT:.2f}")
        add_log('🧿 SIGILOS ATIVADOS - AGUARDANDO SINAL EXTERNO 🧿', 'win')
        
        while bot_rodando and not STOP_GAIN_ATINGIDO:
            try:
                with sinal_lock:
                    direcao = sinal_pendente
                    if direcao:
                        sinal_pendente = None
                
                if direcao in ['call', 'put']:
                    ultimo_sinal = f"📡 SINAL: {direcao.upper()}"
                    add_log(f"📡 SINAL EXTERNO RECEBIDO: {direcao.upper()}", 'sensitive')
                    executar_ciclo(direcao)
                    break
                
                time.sleep(0.3)
            except Exception as e:
                add_log(f"Erro no loop: {e}", 'error')
                time.sleep(5)
                if API:
                    try:
                        API.connect()
                    except:
                        pass
        
        if not bot_rodando:
            add_log("⏹️ Bot parado.", 'info')
            ultimo_sinal = "⏹️ Bot parado"

# ========== ROTA PARA RECEBER SINAL EXTERNO ==========
@app.route('/sinal', methods=['POST'])
def receber_sinal():
    global sinal_pendente
    
    if not bot_rodando:
        return jsonify({'ok': False, 'erro': 'Bot não está rodando. Execute /comecar_operar primeiro.'})
    
    if not conectado_iq:
        return jsonify({'ok': False, 'erro': 'API da IQ Option não conectada.'})
    
    data = request.get_json()
    direcao = data.get('direcao', '').lower()
    
    if direcao not in ['call', 'put']:
        return jsonify({'ok': False, 'erro': 'Direção inválida. Use "call" ou "put"'})
    
    with sinal_lock:
        sinal_pendente = direcao
    
    add_log(f"📡 Sinal externo enfileirado: {direcao.upper()}", 'sensitive')
    return jsonify({'ok': True, 'mensagem': f'Sinal {direcao} recebido e enfileirado'})

# ========== FUNÇÕES DO MERCADO PAGO (PIX) ==========

def gerar_pix_mercadopago(email, plano):
    if MODO_SIMULACAO:
        pix_id = str(uuid.uuid4())[:8]
        pagamentos_pendentes[pix_id] = {
            'email': email,
            'plano_id': plano['id'],
            'moedas': plano['moedas'],
            'valor': plano['preco'],
            'pago': False,
            'criado_em': str(datetime.now())[:19]
        }
        add_log(f"🔰 [SIMULAÇÃO] PIX gerado para {email}: R$ {plano['preco']:.2f} - {plano['moedas']} VOLTS", "info")
        qr_code_falso = f"00020126360014BR.GOV.BCB.PIX0136{email}5204000053039865404{plano['preco']:.2f}5802BR5909Tesla3696009Sao Paulo62070503***6304E3F9"
        return {
            'sucesso': True,
            'simulacao': True,
            'pix_id': pix_id,
            'qr_code': qr_code_falso,
            'qr_code_base64': '',
            'valor': plano['preco'],
            'moedas': plano['moedas']
        }
    
    try:
        url = "https://api.mercadopago.com/v1/payments"
        headers = {
            "Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}",
            "Content-Type": "application/json",
            "X-Idempotency-Key": str(uuid.uuid4())
        }
        
        payment_data = {
            "transaction_amount": float(plano['preco']),
            "description": f"TESLA369 - {plano['nome']} - {plano['moedas']} VOLTS",
            "payment_method_id": "pix",
            "payer": {
                "email": email,
                "first_name": "Cliente",
                "last_name": "Tesla369",
                "identification": {"type": "CPF", "number": "00000000000"}
            }
        }
        
        add_log(f"💳 Gerando PIX para {email} - Valor: R$ {plano['preco']:.2f}", "info")
        response = requests.post(url, json=payment_data, headers=headers, timeout=30)
        data = response.json()
        
        if response.status_code in [200, 201]:
            pix_id = str(data['id'])
            qr_code = data.get('point_of_interaction', {}).get('transaction_data', {}).get('qr_code', '')
            qr_code_base64 = data.get('point_of_interaction', {}).get('transaction_data', {}).get('qr_code_base64', '')
            
            pagamentos_pendentes[pix_id] = {
                'email': email,
                'plano_id': plano['id'],
                'moedas': plano['moedas'],
                'valor': plano['preco'],
                'pago': False,
                'criado_em': str(datetime.now())[:19]
            }
            
            add_log(f"✅ PIX gerado com sucesso! ID: {pix_id[:8]}... Aguardando pagamento.", "win")
            
            return {
                'sucesso': True,
                'simulacao': False,
                'pix_id': pix_id,
                'qr_code': qr_code,
                'qr_code_base64': qr_code_base64,
                'valor': plano['preco'],
                'moedas': plano['moedas']
            }
        
        erro_msg = data.get('message', 'Erro desconhecido ao gerar PIX')
        add_log(f"❌ Erro do Mercado Pago: {erro_msg}", "error")
        return {'sucesso': False, 'erro': erro_msg}
        
    except Exception as erro:
        add_log(f"❌ Erro ao gerar PIX: {str(erro)[:100]}", "error")
        return {'sucesso': False, 'erro': str(erro)[:100]}

def verificar_pagamento_mp(pix_id):
    if MODO_SIMULACAO:
        pago = pagamentos_pendentes.get(pix_id, {}).get('pago', False)
        if pago:
            add_log(f"💰 [SIMULAÇÃO] Pagamento PIX {pix_id[:8]} confirmado!", "win")
        return pago
    
    try:
        url = f"https://api.mercadopago.com/v1/payments/{pix_id}"
        headers = {"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}"}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        pago = data.get('status') == 'approved'
        if pago:
            add_log(f"💰 Pagamento PIX {pix_id[:8]} confirmado via API!", "win")
        return pago
    except Exception as erro:
        add_log(f"⚠️ Erro ao verificar pagamento {pix_id[:8]}: {str(erro)[:50]}", "warning")
        return False

def verificador_automatico_pix():
    add_log("🔍 Verificador automático de pagamentos PIX iniciado!", "info")
    while True:
        time.sleep(10)
        try:
            pagamentos_pendentes_nao_pagos = {
                pid: dados for pid, dados in pagamentos_pendentes.items() 
                if not dados.get('pago', False)
            }
            for pix_id, dados in list(pagamentos_pendentes_nao_pagos.items()):
                if verificar_pagamento_mp(pix_id):
                    pagamentos_pendentes[pix_id]['pago'] = True
                    email_cliente = dados['email']
                    quantidade_moedas = dados['moedas']
                    usuario = carregar_usuario(email_cliente)
                    if not usuario:
                        usuario = criar_usuario(email_cliente)
                    usuario['moedas'] = usuario.get('moedas', 0) + quantidade_moedas
                    salvar_usuario(email_cliente, usuario)
                    add_log(f"✅ PAGAMENTO CONFIRMADO! +{quantidade_moedas} VOLTS para {email_cliente}", "win")
        except Exception as erro:
            pass

threading.Thread(target=verificador_automatico_pix, daemon=True).start()

# ========== ROTAS DO CHAT ==========

@app.route('/chat_enviar', methods=['POST'])
def chat_enviar():
    data = request.json
    nome = data.get('nome', 'Anonimo')[:15]
    msg = data.get('msg', '')[:200]
    if not msg:
        return jsonify({'ok': False})
    try:
        requests.post(f'{FB_URL}/tesla_369/chat.json', json={
            'nome': nome, 'msg': msg, 'hora': datetime.now().strftime('%H:%M')
        }, timeout=5)
    except Exception:
        pass
    return jsonify({'ok': True})

@app.route('/chat_mensagens')
def chat_mensagens_route():
    try:
        url = f'{FB_URL}/tesla_369/chat.json?orderBy="$key"&limitToLast=50'
        response = requests.get(url, timeout=5)
        if response.status_code == 200 and response.json():
            mensagens = list(response.json().values())
        else:
            mensagens = []
        return jsonify({'mensagens': mensagens, 'online': 1})
    except Exception:
        return jsonify({'mensagens': [], 'online': 1})

# ========== ROTAS PRINCIPAIS ==========

@app.route('/')
def index():
    return render_template_string(processar_html_com_skin())

def processar_html_com_skin():
    global skin_atual_global
    skin = next((s for s in SKINS if s['id'] == skin_atual_global), SKINS[0])
    
    # Converte PLANOS para string JSON no HTML
    planos_json = []
    for p in PLANOS:
        planos_json.append(f'{{"id":{p["id"]},"moedas":{p["moedas"]},"preco":{p["preco"]},"nome":"{p["nome"]}","desc":"{p["desc"]}","tag":"{p.get("tag","")}","desconto":"{p.get("desconto","")}"}}')
    
    html = HTML_TEMPLATE
    html = html.replace('{{COR_FUNDO}}', skin['cor_fundo'])
    html = html.replace('{{COR_PANEL}}', skin['cor_panel'])
    html = html.replace('{{COR_DESTAQUE}}', skin['cor_destaque'])
    html = html.replace('{{COR_TEXTO}}', skin['cor_texto'])
    html = html.replace('{{COR_BOTAO}}', skin['cor_botao'])
    html = html.replace('{{COR_TAB_ATIVA}}', skin['cor_tab_ativa'])
    html = html.replace('{{COR_HEADER_BG}}', skin['cor_header_bg'])
    html = html.replace('{{COR_HEADER_BORDA}}', skin['cor_header_borda'])
    html = html.replace('{{CSS_EXTRA}}', skin.get('css_extra', ''))
    html = html.replace('{{HEADER_EXTRA}}', skin.get('header_extra', '<div class="lightning"></div>'))
    html = html.replace('/* PLANOS_JSON */', ','.join(planos_json))
    
    return html

@app.route('/status')
def status():
    u = carregar_usuario(email_usuario_atual) if email_usuario_atual else {}
    skins_status = []
    skins_compradas = u.get('skins_compradas', ['skin_padrao']) if u else ['skin_padrao']
    skin_atual = u.get('skin_atual', 'skin_padrao') if u else 'skin_padrao'
    for skin in SKINS:
        skins_status.append({
            'id': skin['id'], 'nome': skin['nome'], 'desc': skin['desc'],
            'preco_moedas': skin['preco_moedas'], 'categoria': skin.get('categoria', 'basica'),
            'comprado': skin['id'] in skins_compradas, 'ativo': skin['id'] == skin_atual
        })
    return jsonify({
        'conectado': conectado_iq, 'rodando': bot_rodando, 'email': email_usuario_atual,
        'banca': API.get_balance() if API else 0, 'lucro': lucro, 'ops': NumDeOperacoes,
        'sinal': ultimo_sinal, 'logs': get_logs_html(40),
        'moedas': u.get('moedas', 0) if u else 0, 'skin_id': skin_atual,
        'skins_status': skins_status
    })

@app.route('/set_percentual', methods=['POST'])
def set_percentual():
    global PERCENTUAL_BANCA
    PERCENTUAL_BANCA = request.json.get('percentual', 15)
    return jsonify({'ok': True})

@app.route('/conectar', methods=['POST'])
def conectar():
    global API, email_usuario_atual, conectado_iq, skin_atual_global, par, timeframe_atual
    try:
        d = request.get_json()
        email = d.get('email', '').strip()
        senha = d.get('senha', '').strip()
        tipo = d.get('tipo', 'PRACTICE')
        if not email or not senha:
            return jsonify({'ok': False, 'erro': 'Email e senha obrigatórios'})
        email_usuario_atual = email
        
        API = IQ_Option(email, senha)
        status_conn, reason = API.connect()
        if not status_conn:
            return jsonify({'ok': False, 'erro': str(reason)[:100]})
        API.change_balance(tipo)
        conectado_iq = True
        usuario = carregar_usuario(email) or criar_usuario(email)
        hoje = str(datetime.now())[:10]
        
        if usuario.get('moedas_ganhas_hoje') != hoje:
            usuario['moedas'] = usuario.get('moedas', 0) + 1
            usuario['moedas_ganhas_hoje'] = hoje
            salvar_usuario(email, usuario)
        skin_atual_global = usuario.get('skin_atual', 'skin_padrao')
        salvar_usuario(email, usuario)
        add_log('🔌 Conectado na IQ Option!', 'info')
        add_log(f'✅ Conectado! ${API.get_balance():.2f} | ⚡ {usuario.get("moedas", 0)} VOLTS', 'win')
        return jsonify({'ok': True, 'moedas': usuario.get('moedas', 0)})
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)[:100]})

@app.route('/comecar_operar', methods=['POST'])
def comecar_operar():
    global bot_rodando, bot_thread, lucro, NumDeOperacoes, ultimo_sinal, sinal_pendente
    try:
        if not conectado_iq:
            return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
        
        with bot_lock:
            if bot_rodando and bot_thread and bot_thread.is_alive():
                return jsonify({'ok': False, 'erro': 'Bot já está rodando!'})
            
            usuario = carregar_usuario(email_usuario_atual)
            if not usuario:
                return jsonify({'ok': False, 'erro': 'Usuário não encontrado!'})
            
            if usuario.get('moedas', 0) < 1:
                return jsonify({'ok': False, 'erro': 'Sem VOLTS! Compre mais na loja.'})
            
            usuario['moedas'] -= 1
            usuario['total_ciclos'] += 1
            salvar_usuario(email_usuario_atual, usuario)
            lucro = 0.0
            NumDeOperacoes = 0
            ultimo_sinal = "📡 Aguardando sinal externo..."
            
            with sinal_lock:
                sinal_pendente = None
            
            bot_rodando = True
            bot_thread = threading.Thread(target=bot_loop, daemon=True)
            bot_thread.start()
        
        return jsonify({'ok': True, 'moedas': usuario['moedas']})
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)[:100]})

@app.route('/parar', methods=['POST'])
def parar():
    global bot_rodando, conectado_iq
    data = request.json or {}
    with bot_lock:
        bot_rodando = False
    if data.get('desconectar'):
        conectado_iq = False
    return jsonify({'ok': True})

@app.route('/comprar_skin', methods=['POST'])
def comprar_skin():
    global skin_atual_global
    d = request.get_json()
    skin_id = d.get('skin_id', '')
    if not email_usuario_atual:
        return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    skin = next((s for s in SKINS if s['id'] == skin_id), None)
    if not skin:
        return jsonify({'ok': False, 'erro': 'Skin não encontrada'})
    usuario = carregar_usuario(email_usuario_atual)
    if not usuario:
        return jsonify({'ok': False, 'erro': 'Usuário não encontrado'})
    if skin['preco_moedas'] == 0:
        if 'skins_compradas' not in usuario:
            usuario['skins_compradas'] = ['skin_padrao']
        if skin_id not in usuario['skins_compradas']:
            usuario['skins_compradas'].append(skin_id)
        usuario['skin_atual'] = skin_id
        salvar_usuario(email_usuario_atual, usuario)
        skin_atual_global = skin_id
        return jsonify({'ok': True, 'moedas': usuario.get('moedas', 0), 'msg': 'Skin grátis ativada!'})
    if 'skins_compradas' not in usuario:
        usuario['skins_compradas'] = ['skin_padrao']
    if skin_id in usuario['skins_compradas']:
        usuario['skin_atual'] = skin_id
        salvar_usuario(email_usuario_atual, usuario)
        skin_atual_global = skin_id
        return jsonify({'ok': True, 'moedas': usuario['moedas'], 'msg': 'Skin já comprada! Ativada.'})
    if usuario.get('moedas', 0) < skin['preco_moedas']:
        return jsonify({'ok': False, 'erro': f'VOLTS insuficientes! Precisa de {skin["preco_moedas"]} ⚡'})
    usuario['moedas'] -= skin['preco_moedas']
    usuario['skins_compradas'].append(skin_id)
    usuario['skin_atual'] = skin_id
    salvar_usuario(email_usuario_atual, usuario)
    skin_atual_global = skin_id
    return jsonify({'ok': True, 'moedas': usuario['moedas'], 'msg': f'Skin {skin["nome"]} comprada e ativada!'})

@app.route('/ativar_skin', methods=['POST'])
def ativar_skin():
    d = request.get_json()
    skin_id = d.get('skin_id', '')
    if not email_usuario_atual:
        return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    usuario = carregar_usuario(email_usuario_atual)
    if not usuario:
        return jsonify({'ok': False, 'erro': 'Usuário não encontrado'})
    if 'skins_compradas' not in usuario:
        usuario['skins_compradas'] = ['skin_padrao']
    if skin_id not in usuario['skins_compradas']:
        skin = next((s for s in SKINS if s['id'] == skin_id), None)
        if skin and skin['preco_moedas'] > 0:
            return jsonify({'ok': False, 'erro': 'Compre a skin primeiro!'})
        usuario['skins_compradas'].append(skin_id)
    usuario['skin_atual'] = skin_id
    salvar_usuario(email_usuario_atual, usuario)
    global skin_atual_global
    skin_atual_global = skin_id
    return jsonify({'ok': True})

@app.route('/criar_pix', methods=['POST'])
def criar_pix():
    d = request.get_json()
    email = d.get('email', '')
    plano_id = int(d.get('plano_id') or 1)
    if not email:
        return jsonify({'sucesso': False, 'erro': 'Email obrigatório'})
    plano = next((p for p in PLANOS if p['id'] == plano_id), None)
    if not plano:
        return jsonify({'sucesso': False, 'erro': 'Plano não encontrado'})
    return jsonify(gerar_pix_mercadopago(email, plano))

@app.route('/verificar_pix', methods=['POST'])
def verificar_pix():
    d = request.get_json()
    pix_id = d.get('pix_id', '')
    if not pix_id:
        return jsonify({'pago': False})
    if verificar_pagamento_mp(pix_id):
        if pix_id in pagamentos_pendentes and not pagamentos_pendentes[pix_id]['pago']:
            pagamentos_pendentes[pix_id]['pago'] = True
            email = pagamentos_pendentes[pix_id]['email']
            moedas = pagamentos_pendentes[pix_id]['moedas']
            usuario = carregar_usuario(email) or criar_usuario(email)
            usuario['moedas'] = usuario.get('moedas', 0) + moedas
            salvar_usuario(email, usuario)
            return jsonify({'pago': True, 'moedas': moedas, 'saldo': usuario['moedas']})
        return jsonify({'pago': True})
    return jsonify({'pago': False})

@app.route('/ranking')
def ranking():
    ranking_list = []
    try:
        r = requests.get(f'{FB_URL}/tesla_369/usuarios.json')
        usuarios = r.json() if r.status_code == 200 else {}
        if usuarios:
            for key, user_data in usuarios.items():
                if user_data:
                    ranking_list.append({
                        'email': user_data.get('email', 'N/A')[:20] + '...',
                        'lucro_total': round(user_data.get('lucro_total', 0), 2),
                        'total_wins': user_data.get('total_wins', 0),
                        'total_losses': user_data.get('total_losses', 0),
                        'total_ciclos': user_data.get('total_ciclos', 0),
                        'taxa': round((user_data.get('total_wins', 0) / max(user_data.get('total_ciclos', 1), 1)) * 100, 1),
                        'banca_atual': round(user_data.get('banca_atual', 0), 2)
                    })
    except:
        pass
    ranking_list.sort(key=lambda x: x['lucro_total'], reverse=True)
    total_ops = sum(u['total_ciclos'] for u in ranking_list)
    total_wins = sum(u['total_wins'] for u in ranking_list)
    taxa_global = round((total_wins / max(total_ops, 1)) * 100, 1) if total_ops > 0 else 0
    return jsonify({
        'ranking': ranking_list[:20],
        'stats': {
            'total_usuarios': len(ranking_list),
            'total_ops': total_ops,
            'total_wins': total_wins,
            'taxa_global': taxa_global
        }
    })

@app.route('/relatorio')
def relatorio():
    email = request.args.get('email', '')
    if not email:
        return jsonify({'erro': 'Email obrigatório'})
    u = carregar_usuario(email)
    return jsonify(u if u else {'erro': 'Não encontrado'})

@app.route('/resetar', methods=['POST'])
def resetar():
    d = request.get_json()
    email = d.get('email', '')
    if not email:
        return jsonify({'ok': False, 'msg': 'Email obrigatório'})
    usuario = carregar_usuario(email)
    if not usuario:
        return jsonify({'ok': False, 'msg': 'Usuário não encontrado'})
    moedas = usuario.get('moedas', 0)
    skins_compradas = usuario.get('skins_compradas', ['skin_padrao'])
    skin_atual = usuario.get('skin_atual', 'skin_padrao')
    data_cadastro = usuario.get('data_cadastro', str(datetime.now())[:19])
    usuario['total_ciclos'] = 0
    usuario['total_wins'] = 0
    usuario['total_losses'] = 0
    usuario['total_gasto'] = 0.0
    usuario['total_ganho'] = 0.0
    usuario['lucro_total'] = 0.0
    usuario['historico_operacoes'] = []
    usuario['dias_ativos'] = 0
    usuario['banca_atual'] = 0.0
    usuario['moedas'] = moedas
    usuario['skins_compradas'] = skins_compradas
    usuario['skin_atual'] = skin_atual
    usuario['data_cadastro'] = data_cadastro
    usuario['moedas_ganhas_hoje'] = str(datetime.now())[:10]
    salvar_usuario(email, usuario)
    return jsonify({'ok': True, 'msg': '✅ Estatísticas resetadas!'})

# Admin
LOGIN_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Admin</title><style>body{background:#0a0a1a;display:flex;justify-content:center;align-items:center;height:100vh;font-family:monospace}.box{background:#1a1a3e;border:2px solid #ffd700;border-radius:15px;padding:25px;text-align:center}input{padding:14px;background:#111;border:1px solid #333;color:#fff;border-radius:10px;margin:10px 0}.btn{background:#ffd700;color:#000;padding:14px;border:none;border-radius:10px;cursor:pointer}</style></head><body><div class='box'><h2>🔐 Admin</h2><form method='POST'><input type='password' name='senha' placeholder='Senha'><br><button class='btn' type='submit'>Entrar</button></form></div></body></html>"""
ADMIN_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Admin</title><style>body{background:#0a0a1a;color:#fff;font-family:monospace;padding:10px}.container{max-width:500px;margin:0 auto}h1{color:#ffd700}.card{background:#1a1a3e;border:1px solid #ffd700;border-radius:12px;padding:15px;margin:10px 0}input,select{width:100%;padding:12px;margin:8px 0;background:#111;border:1px solid #333;color:#fff;border-radius:8px}.btn{background:#ffd700;color:#000;padding:14px;border:none;border-radius:10px;cursor:pointer;width:100%;margin:5px 0}</style></head><body><div class='container'><h1>🔐 Admin</h1><div class='card'><h3>🔍 Buscar</h3><input type='email' id='emailBusca' placeholder='Email'><button class='btn' onclick='buscar()'>Buscar</button><div id='resultado' style='margin-top:10px;background:#000;padding:10px;border-radius:8px'></div></div><div class='card'><h3>✏️ Editar</h3><input type='email' id='emailEdit' placeholder='Email'><p>⚡ VOLTS: <input type='number' id='moedas'></p><p>🎨 Skin: <select id='skin'><option value='skin_padrao'>Padrao</option><option value='skin_dark'>Dark</option><option value='skin_neon'>Neon</option><option value='skin_matrix'>Matrix</option><option value='skin_sakura'>Sakura</option><option value='skin_thunder'>Thunder</option><option value='skin_ocean'>Ocean</option><option value='skin_sunset'>Sunset</option><option value='skin_magos'>Magos</option><option value='skin_brasil'>Brasil</option><option value='skin_fire'>Fire</option><option value='skin_ice'>Ice</option><option value='skin_princesa'>Princesa</option></select></p><button class='btn' onclick='salvar()'>💾 SALVAR</button><button class='btn' onclick='resetar()' style='background:#ff4444;color:#fff'>🔄 RESETAR</button><div id='resultadoEdit' style='margin-top:10px;background:#000;padding:10px;border-radius:8px'></div></div></div><script>function buscar(){fetch('/api/admin/buscar?email='+document.getElementById('emailBusca').value).then(r=>r.json()).then(d=>{if(d.erro)document.getElementById('resultado').innerHTML='<p style=color:#ff4444>'+d.erro+'</p>';else{document.getElementById('resultado').innerHTML='<p>✅ '+d.email+'<br>⚡ '+d.moedas+' VOLTS<br>💰 $'+d.lucro_total.toFixed(2)+'</p>';document.getElementById('emailEdit').value=d.email;document.getElementById('moedas').value=d.moedas;document.getElementById('skin').value=d.skin_atual;}})}function salvar(){fetch('/api/admin/salvar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:document.getElementById('emailEdit').value,moedas:parseInt(document.getElementById('moedas').value),skin:document.getElementById('skin').value})}).then(r=>r.json()).then(d=>{document.getElementById('resultadoEdit').innerHTML='<p style=color:#00ff88>'+d.msg+'</p>';});}function resetar(){fetch('/api/admin/resetar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:document.getElementById('emailEdit').value})}).then(r=>r.json()).then(d=>{document.getElementById('resultadoEdit').innerHTML='<p style=color:#00ff88>'+d.msg+'</p>';});}</script></body></html>"""

@app.route('/admin369', methods=['GET','POST'])
def admin_painel():
    if request.method == 'POST':
        if request.form.get('senha') == '85133856':
            return ADMIN_HTML
        return '<center><h2 style="color:red">Senha incorreta!</h2></center>'
    if request.args.get('s') != '85133856':
        return LOGIN_HTML
    return ADMIN_HTML

@app.route('/api/admin/buscar')
def admin_buscar():
    email = request.args.get('email', '')
    u = carregar_usuario(email)
    if u:
        return jsonify(u)
    return jsonify({'erro': 'Nao encontrado'})

@app.route('/api/admin/salvar', methods=['POST'])
def admin_salvar():
    d = request.json
    email = d.get('email', '')
    u = carregar_usuario(email)
    if not u:
        return jsonify({'ok': False, 'msg': 'Nao encontrado'})
    if 'moedas' in d:
        u['moedas'] = int(d['moedas'])
    if 'skin' in d:
        u['skin_atual'] = d['skin']
    salvar_usuario(email, u)
    return jsonify({'ok': True, 'msg': 'Salvo!'})

@app.route('/api/admin/resetar', methods=['POST'])
def admin_resetar():
    email = request.json.get('email', '')
    u = carregar_usuario(email)
    if not u:
        return jsonify({'ok': False, 'msg': 'Nao encontrado'})
    u['total_wins'] = 0
    u['total_losses'] = 0
    u['total_ciclos'] = 0
    u['total_gasto'] = 0
    u['total_ganho'] = 0
    u['lucro_total'] = 0
    salvar_usuario(email, u)
    return jsonify({'ok': True, 'msg': 'Resetado!'})

# ========== HTML TEMPLATE COMPLETO ==========
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚡ TESLA 369 BOT v9.0</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:{{COR_FUNDO}};color:{{COR_TEXTO}};font-family:'Courier New',monospace;padding:10px}
        .container{max-width:950px;margin:0 auto}
        .tabs{display:flex;gap:5px;margin-bottom:10px;flex-wrap:wrap}
        .tab{padding:10px 14px;background:{{COR_PANEL}};border:1px solid #333;border-radius:10px 10px 0 0;cursor:pointer;color:#888;font-size:10px}
        .tab.active{background:{{COR_TAB_ATIVA}};color:#000;font-weight:bold}
        .panel{display:none;background:{{COR_PANEL}};padding:15px;border-radius:0 10px 10px 10px;border:1px solid #333;margin-bottom:10px}
        .panel.active{display:block}
        .header{background:{{COR_HEADER_BG}};padding:20px;border-radius:20px;text-align:center;border:3px solid {{COR_HEADER_BORDA}};position:relative;overflow:hidden;margin-bottom:15px}
        {{CSS_EXTRA}}
        .header h1{color:{{COR_DESTAQUE}};font-size:22px;text-shadow:0 0 30px {{COR_TAB_ATIVA}};position:relative;z-index:3}
        .header p{color:{{COR_DESTAQUE}};font-size:10px;position:relative;z-index:3;opacity:0.8}
        .mantra{color:{{COR_DESTAQUE}};text-align:center;margin:8px 0;font-size:10px}
        .config-section{margin-bottom:12px}
        .config-section h3{color:{{COR_DESTAQUE}};margin-bottom:8px;font-size:13px;border-bottom:1px solid #333;padding-bottom:5px}
        .config-row{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:8px}
        .config-row label{color:#888;font-size:11px}
        .config-row select,.config-row input{padding:8px;background:#111;border:1px solid #333;border-radius:8px;color:#fff;font-size:11px;font-family:'Courier New',monospace}
        .btn{padding:10px 14px;border:none;border-radius:8px;font-weight:bold;cursor:pointer;font-size:11px;font-family:'Courier New',monospace}
        .btn-start{background:{{COR_BOTAO}};color:#000;font-weight:bold}
        .btn-stop{background:linear-gradient(135deg,#cc0000,#ff4444);color:#fff}
        .btn-info{background:linear-gradient(135deg,#0066cc,#3399ff);color:#fff;font-size:11px;padding:8px 14px}
        .btn-buy{background:linear-gradient(135deg,#00aa44,#00cc55);color:#fff;width:100%;padding:12px;font-size:13px}
        .btn-reset{background:linear-gradient(135deg,#cc0000,#ff6600);color:#fff;font-size:11px;padding:8px 14px}
        .btn-skin{background:linear-gradient(135deg,#9933ff,#cc66ff);color:#fff;font-size:11px;padding:8px 12px}
        .dashboard{display:grid;grid-template-columns:repeat(auto-fit,minmax(105px,1fr));gap:8px;margin-bottom:10px}
        .card{background:{{COR_PANEL}};padding:10px;border-radius:10px;border:1px solid #333;text-align:center}
        .card .label{color:#888;font-size:9px}.card .value{color:{{COR_DESTAQUE}};font-size:14px;font-weight:bold;margin-top:4px}
        .terminal{background:#000;color:#00ff88;padding:12px;border-radius:10px;height:200px;overflow-y:auto;font-size:10px;line-height:1.4;white-space:pre-wrap;border:1px solid #333;position:relative;overflow:hidden}.terminal span{position:relative;z-index:1}
        .barra-status{display:flex;justify-content:space-between;padding:8px;background:{{COR_PANEL}};border-radius:10px;margin-top:10px;font-size:10px;flex-wrap:wrap;gap:5px}
        .status-dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:4px}
        .status-dot.active{background:#00ff88;animation:pulse 1s infinite}.status-dot.inactive{background:#888}
        @keyframes pulse{0%,100%{opacity:1}50%{opacity:0.3}}
        .planos-grid,.skins-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}
        .plano-card,.skin-card{background:#111;padding:12px;border-radius:10px;border:2px solid #222;text-align:center;cursor:pointer;transition:all 0.3s ease}
        .plano-card:hover,.skin-card:hover{border-color:{{COR_DESTAQUE}};background:#1a1a2e}
        .plano-card.selecionado,.skin-card.selecionado{border-color:{{COR_DESTAQUE}};box-shadow:0 0 20px rgba(255,215,0,0.4)}
        .skin-card.ativo{border-color:#00ff88;box-shadow:0 0 15px rgba(0,255,136,0.3)}
        .plano-moedas,.skin-nome{font-size:20px;color:{{COR_DESTAQUE}};font-weight:bold}
        .plano-preco{font-size:14px;color:#00ff88;margin:5px 0}
        .plano-desc,.skin-desc{font-size:9px;color:#888;margin-top:4px}
        .plano-tag{background:{{COR_DESTAQUE}}22;color:{{COR_DESTAQUE}};font-size:9px;padding:2px 8px;border-radius:10px;display:inline-block;margin-top:4px}
        .plano-desconto{background:#ff4444;color:#fff;font-size:9px;padding:2px 6px;border-radius:10px;display:inline-block;margin-left:4px}
        .modal-overlay{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.85);z-index:1000;justify-content:center;align-items:center}
        .modal-overlay.active{display:flex}
        .modal-pagamento{background:{{COR_PANEL}};border:2px solid {{COR_DESTAQUE}};border-radius:15px;padding:25px;max-width:400px;width:90%;text-align:center}
        .modal-pagamento h3{color:{{COR_DESTAQUE}};margin-bottom:15px}
        .pix-qrcode{background:#fff;padding:15px;border-radius:10px;display:inline-block;margin:10px 0}
        .pix-qrcode img{max-width:200px}
        .pix-copiavel{background:#000;color:#00ff88;padding:10px;border-radius:8px;font-size:9px;word-break:break-all;margin:10px 0;max-height:60px;overflow-y:auto;cursor:pointer}
        .btn-fechar{background:#444;color:#fff;padding:8px 20px;border-radius:8px;cursor:pointer;margin-top:10px;border:none;font-family:'Courier New',monospace}
        .btn-confirmar{background:{{COR_DESTAQUE}};color:#000;padding:8px 20px;border-radius:8px;cursor:pointer;margin-top:10px;font-weight:bold;border:none;font-family:'Courier New',monospace}
        .relatorio-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:6px}
        .relatorio-card{background:#111;padding:8px;border-radius:8px;border:1px solid #222;text-align:center}
        .relatorio-card .rlabel{color:#666;font-size:9px}.relatorio-card .rvalue{color:{{COR_DESTAQUE}};font-size:14px;font-weight:bold}
        .historico-table{width:100%;font-size:9px;border-collapse:collapse;margin-top:10px}
        .historico-table th{background:{{COR_TAB_ATIVA}};color:#000;padding:4px}.historico-table td{padding:3px;border-bottom:1px solid #222;text-align:center}
        .sub-tabs{display:flex;gap:5px;margin-bottom:15px}.sub-tab{padding:8px 16px;background:#111;border:1px solid #333;border-radius:8px 8px 0 0;cursor:pointer;color:#888;font-size:11px}.sub-tab.active{background:linear-gradient(135deg,#cc8800,#ffd700);color:#000;font-weight:bold;border-color:#ffd700}.sub-tab:hover{background:#1a1a2e;color:#fff}.sub-panel{display:none}.sub-panel.active{display:block}
        /* LOJA PREMIUM */
        .loja-container{padding:10px 0}
        .loja-titulo{text-align:center;color:{{COR_DESTAQUE}};font-size:16px;margin-bottom:15px;text-shadow:0 0 20px {{COR_TAB_ATIVA}};letter-spacing:2px}
        .planos-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:10px;padding:5px}
        .plano-card{background:linear-gradient(180deg,#1a1a2e 0%,#0d0d1a 100%);padding:15px 10px;border-radius:16px;border:1px solid #333;text-align:center;cursor:pointer;transition:all .3s cubic-bezier(.4,0,.2,1);position:relative;overflow:hidden;animation:fadeInUp .5s ease backwards}
        .plano-card:hover{transform:translateY(-6px);border-color:{{COR_DESTAQUE}};box-shadow:0 12px 30px rgba(255,215,0,.2),0 0 60px rgba(255,215,0,.05)}
        .plano-card.selecionado{border-color:#ffd700!important;box-shadow:0 0 30px rgba(255,215,0,.5),inset 0 0 30px rgba(255,215,0,.05);background:linear-gradient(180deg,#2a2a1e 0%,#1a1a0d 100%)}
        .plano-card.selecionado::before{content:'';position:absolute;top:-50%;left:-50%;width:200%;height:200%;background:radial-gradient(circle,rgba(255,215,0,.1) 0%,transparent 70%);animation:rotate 4s linear infinite}
        .plano-icone{font-size:28px;margin-bottom:6px;filter:drop-shadow(0 0 8px {{COR_DESTAQUE}})}
        .plano-nome{color:{{COR_DESTAQUE}};font-weight:bold;font-size:12px;margin-bottom:4px;text-transform:uppercase;letter-spacing:1px}
        .plano-moedas{font-size:28px;font-weight:bold;background:linear-gradient(180deg,#ffd700,#ff8c00);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:5px 0}
        .plano-preco{font-size:16px;color:#00ff88;font-weight:bold}
        .plano-badge{position:absolute;top:10px;right:10px;background:linear-gradient(135deg,#ff4444,#ff6600);color:#fff;font-size:8px;padding:3px 8px;border-radius:12px;font-weight:bold;animation:pulse 2s infinite}
        .skin-card{background:linear-gradient(180deg,#1a102a 0%,#0d0a1a 100%);padding:15px 10px;border-radius:16px;border:1px solid #333;text-align:center;cursor:pointer;transition:all .3s ease;position:relative;overflow:hidden;animation:fadeInUp .4s ease backwards}
        .skin-card:hover{transform:translateY(-5px);border-color:#9933ff;box-shadow:0 10px 25px rgba(153,51,255,.2)}
        .skin-card.ativo{border-color:#00ff88!important;box-shadow:0 0 25px rgba(0,255,136,.3),inset 0 0 20px rgba(0,255,136,.03)}
        .skin-icone{font-size:30px;margin-bottom:5px}
        .skin-nome{color:#cc66ff;font-weight:bold;font-size:13px;margin-bottom:4px}
        .skin-desc{color:#888;font-size:9px;margin-bottom:8px;line-height:1.3}
        .btn-loja{padding:10px 16px;border:none;border-radius:10px;font-weight:bold;cursor:pointer;font-size:11px;width:100%;transition:all .2s ease;text-transform:uppercase;letter-spacing:1px}
        .btn-comprar-volts{background:linear-gradient(135deg,#ff8c00,#ffd700);color:#000;box-shadow:0 4px 15px rgba(255,215,0,.3)}
        .btn-comprar-volts:hover{transform:scale(1.03);box-shadow:0 6px 20px rgba(255,215,0,.5)}
        .btn-comprar-skin{background:linear-gradient(135deg,#6600cc,#9933ff);color:#fff;box-shadow:0 4px 15px rgba(153,51,255,.3)}
        .btn-comprar-skin:hover{transform:scale(1.03);box-shadow:0 6px 20px rgba(153,51,255,.5)}
        .btn-comprado{background:linear-gradient(135deg,#222,#333);color:#00ff88;border:1px solid #00ff88;cursor:default;box-shadow:0 0 10px rgba(0,255,136,.1)}
        .badge-preco{display:inline-block;padding:4px 10px;border-radius:10px;font-size:9px;font-weight:bold;margin:5px 0}
        .badge-gratis{background:#00ff8822;color:#00ff88;border:1px solid #00ff8844}
        .badge-pago{background:#ffd70022;color:#ffd700;border:1px solid #ffd70044}
        .badge-destaque{position:absolute;top:8px;left:8px;background:linear-gradient(135deg,#ffd700,#ff8c00);color:#000;font-size:7px;padding:3px 8px;border-radius:8px;font-weight:bold}
        @keyframes fadeInUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
        @keyframes rotate{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}
        @keyframes pulse{0%,100%{opacity:1}50%{opacity:.6}}
        .sub-tabs{display:flex;gap:8px;margin-bottom:18px;flex-wrap:wrap}
        .sub-tab{padding:10px 18px;background:#111;border:2px solid #222;border-radius:12px 12px 0 0;cursor:pointer;color:#666;font-size:11px;font-weight:bold;transition:all .3s ease}
        .sub-tab:hover{background:#1a1a2e;color:#ccc;border-color:#333}
        .sub-tab.active{background:linear-gradient(135deg,#1a1a0a,#0d0d05);color:{{COR_DESTAQUE}};border-color:{{COR_DESTAQUE}};box-shadow:0 -3px 15px rgba(255,215,0,.1)}
        .sub-panel{display:none;animation:fadeIn .4s ease}
        .sub-panel.active{display:block}
        @keyframes fadeIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        {{HEADER_EXTRA}}
        <h1>⚡ TESLA 369 BOT ⚡</h1>
        <p>MODO SINAL EXTERNO - Envie POST /sinal</p>
    </div>
    <div class="mantra">🌀 O DINHEIRO VEM ATÉ MIM DE TODOS OS LADOS 🌀</div>
    <div class="tabs">
        <div class="tab active" onclick="openTab('bot')">🤖 BOT</div>
        <div class="tab" onclick="openTab('relatorio')">📊 RELATÓRIO</div>
        <div class="tab" onclick="openTab('loja')">🛍️ LOJA</div>
        <div class="tab" onclick="openTab('chat')">💬 CHAT</div>
        <div class="tab" onclick="openTab('leia-me')">📖 TUTORIAL</div>
        <div class="tab" onclick="openTab('contato')">📞 CONTATO</div>
    </div>
    
    <!-- PAINEL BOT -->
    <div class="panel active" id="panel-bot">
        <div class="config-section"><h3>🔐 IQ OPTION</h3><div class="config-row">
            <input type="email" id="email" placeholder="📧 Email IQ Option" style="flex:2">
            <input type="password" id="senha" placeholder="🔒 Senha" style="flex:1">
            <select id="tipo"><option value="PRACTICE">🧪 PRACTICE</option><option value="REAL">💰 REAL</option></select>
            <div style="margin-top:5px;display:flex;gap:8px;align-items:center">
                <label style="color:#888;font-size:9px">% Banca:</label>
                <select id="percentualBanca" onchange="atualizarPercentual()" style="padding:5px;background:#111;border:1px solid #333;border-radius:5px;color:#fff;font-size:10px;width:70px">
                    <option value="15" selected>15%</option><option value="20">20%</option><option value="30">30%</option><option value="50">50%</option>
                </select>
                <span style="color:#ffd700;font-size:9px" id="valorEstimado">($0.00)</span>
            </div>
            <button class="btn btn-info" id="btnConectar" onclick="conectarIQ()">🔌 CONECTAR</button>
            <button class="btn btn-stop" id="btnDesconectar" onclick="desconectarIQ()" style="display:none">🔌 DESCONECTAR</button>
            <button class="btn btn-start" id="btnOperar" onclick="comecarOperar()" style="display:none">🚀 COMEÇAR OPERAR</button>
            <button class="btn btn-stop" id="btnParar" onclick="pararBot()" style="display:none">⏹️ PARAR</button>
        </div></div>
        <div class="dashboard">
            <div class="card"><div class="label">💰 BANCA</div><div class="value" id="banca" style="color:#00ff88">--</div></div>
            <div class="card"><div class="label">📈 LUCRO</div><div class="value" id="lucro">$0.00</div></div>
            <div class="card"><div class="label">🎯 OPS</div><div class="value" id="ops">0</div></div>
            <div class="card"><div class="label">⚡ VOLTS</div><div class="value" id="moedasSaldo">0</div></div>
            <div class="card"><div class="label">📡 SINAL</div><div class="value" id="sinal" style="font-size:10px">--</div></div>
        </div>
        <div class="terminal" id="terminal">📡 Aguardando...</div>
        <div class="barra-status">
            <span><span class="status-dot inactive" id="statusDot"></span> <span id="statusTexto">⏸️ Desconectado</span></span>
            <span>⚡ TESLA 369 v9.0</span>
            <span>📡 SINAL EXTERNO | GALE 2 | WIN = STOP</span>
        </div>
    </div>
    
    <!-- PAINEL RELATÓRIO -->
    <div class="panel" id="panel-relatorio">
        <div class="config-section"><h3>📊 RELATÓRIO</h3><div class="config-row">
            <input type="email" id="emailRelatorio" placeholder="Email" style="flex:2">
            <button class="btn btn-info" onclick="verRelatorio()">🔍 BUSCAR</button>
            <button class="btn btn-info" onclick="verRanking()" style="background:linear-gradient(135deg,#ff8c00,#ffd700);color:#000">🏆 RANKING</button>
        </div></div>
        <div id="relatorioContent"></div>
    </div>
    
    <!-- PAINEL LOJA -->
    <div class="panel" id="panel-loja">
        <div class="sub-tabs">
            <div class="sub-tab active" onclick="mostrarSubAba('moedas')">💳 COMPRAR VOLTS</div>
            <div class="sub-tab" onclick="mostrarSubAba('skins')">🎨 LOJA DE SKINS</div>
        </div>
        <div class="sub-panel active" id="sub-panel-moedas">
            <div class="config-section"><h3>💳 COMPRAR VOLTS COM PIX</h3>
            <p style="color:#888;font-size:10px">📧 <input type="email" id="emailCompra" placeholder="Seu email" style="width:220px;padding:6px;background:#111;border:1px solid #333;color:#fff;border-radius:5px"></p>
            <p style="color:#ffd700;font-size:10px">⚡ 1 VOLT = 1 ciclo | +1 VOLT grátis/dia</p></div>
            <div class="planos-grid" id="planosGrid"></div>
        </div>
        <div class="sub-panel" id="sub-panel-skins">
            <div class="config-section"><h3>🎨 LOJA DE SKINS</h3></div>
            <div class="sub-tabs" style="margin-bottom:10px">
                <div class="sub-tab active" onclick="mostrarCategoriaSkin('basica')">⚡ BÁSICAS</div>
                <div class="sub-tab" onclick="mostrarCategoriaSkin('premium')">🔮 PREMIUM</div>
                <div class="sub-tab" onclick="mostrarCategoriaSkin('lendaria')">💎 LENDÁRIAS</div>
            </div>
            <div class="sub-panel active" id="sub-panel-skin-basica">
                <div class="skins-grid" id="skinsGridBasicas"></div>
            </div>
            <div class="sub-panel" id="sub-panel-skin-premium">
                <div class="skins-grid" id="skinsGridPremium"></div>
            </div>
            <div class="sub-panel" id="sub-panel-skin-lendaria">
                <div class="skins-grid" id="skinsGridLendarias"></div>
            </div>
        </div>
    </div>
    
    <!-- PAINEL CHAT -->
    <div class="panel" id="panel-chat">
        <div class="config-section"><h3>💬 CHAT DOS TRADERS</h3>
        <p style="color:#888;font-size:9px" id="chatInfo">Conecte na IQ Option para entrar</p></div>
        <div id="chatMensagens" style="background:#000;border:1px solid #333;border-radius:10px;height:300px;overflow-y:auto;padding:10px;margin-bottom:10px;font-size:10px"></div>
        <div style="display:flex;gap:8px">
            <input type="text" id="chatMsg" placeholder="Digite sua mensagem..." style="flex:1;padding:10px;background:#111;border:1px solid #333;border-radius:8px;color:#fff">
            <button onclick="enviarChatMsg()" class="btn btn-info">ENVIAR</button>
        </div>
        <div style="text-align:center;margin-top:5px">
            <span style="color:#888;font-size:9px" id="chatOnline">0 online</span>
        </div>
    </div>
    
    <!-- PAINEL TUTORIAL -->
    <div class="panel" id="panel-leia-me">
        <div class="config-section"><h3>📖 TUTORIAL - MODO SINAL EXTERNO</h3></div>
        <div style="background:#0a0a1a;border:1px solid #00ff88;border-radius:15px;padding:20px;margin:10px 0">
            <p style="color:#ffd700;font-weight:bold">🔰 COMO USAR</p>
            <p style="color:#ccc;font-size:11px">1. Conecte na IQ Option<br>2. Clique em COMEÇAR OPERAR<br>3. Envie sinais via POST para /sinal</p>
            <p style="color:#ffd700;font-weight:bold;margin-top:10px">📡 EXEMPLO DE SINAL</p>
            <p style="color:#00ff88;font-size:10px">curl -X POST http://localhost:5000/sinal -H "Content-Type: application/json" -d '{"direcao":"call"}'</p>
            <p style="color:#00ff88;font-size:10px;margin-top:5px">curl -X POST http://localhost:5000/sinal -H "Content-Type: application/json" -d '{"direcao":"put"}'</p>
        </div>
        <div style="background:#1a0000;border:2px solid #ff4444;border-radius:15px;padding:20px;margin:10px 0">
            <p style="color:#ff4444;font-weight:bold">⚠️ AVISO IMPORTANTE</p>
            <p style="color:#ff8888;font-size:11px">Opções binárias envolvem risco de perda total do capital. Use com responsabilidade.</p>
        </div>
    </div>
    
    <!-- PAINEL CONTATO -->
    <div class="panel" id="panel-contato">
        <div class="config-section"><h3>📞 CONTATO</h3></div>
        <div style="background:linear-gradient(135deg,#1a1a2e,#0d0d1a);border:2px solid #ffd700;border-radius:15px;padding:20px;text-align:center">
            <p style="color:#ffd700;font-weight:bold">💬 FALE COM O DESENVOLVEDOR</p>
            <p style="color:#ccc">📧 gyn.bet.fc@gmail.com</p>
            <a href="https://wa.me/5562981728653" target="_blank"><button style="background:#25D366;color:#fff;border:none;padding:10px 20px;border-radius:10px;margin-top:10px;cursor:pointer">💬 WhatsApp</button></a>
        </div>
    </div>
</div>

<div class="modal-overlay" id="modalPix">
    <div class="modal-pagamento">
        <h3>💳 Pagamento PIX</h3>
        <div id="pixContent"><p style="color:#888">Carregando QR Code...</p></div>
        <button class="btn-fechar" onclick="fecharModal()">❌ Fechar</button>
    </div>
</div>

<script>
// PLANOS carregados do backend
var PLANOS = [/* PLANOS_JSON */];

var intervalo=null,botAtivo=false,conectadoIQ=false,emailLogado='',planoSelecionado=0,pixAtual=null;

function openTab(tab){
    document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
    event.target.classList.add('active');
    document.getElementById('panel-'+tab).classList.add('active');
    if(tab=='relatorio'&&emailLogado){document.getElementById('emailRelatorio').value=emailLogado;verRelatorio()}
    if(tab=='loja'){mostrarSubAba('moedas');}
}

function mostrarSubAba(aba){
    document.querySelectorAll('.sub-tab').forEach(t=>t.classList.remove('active'));
    document.querySelectorAll('.sub-panel').forEach(p=>p.classList.remove('active'));
    event.target.classList.add('active');
    document.getElementById('sub-panel-'+aba).classList.add('active');
    if(aba==='skins'){mostrarCategoriaSkin('basica'); renderSkins();}
    if(aba==='moedas'){renderPlanos();}
}

function mostrarCategoriaSkin(categoria){
    document.querySelectorAll('#panel-loja .sub-tabs .sub-tab').forEach(t=>t.classList.remove('active'));
    document.querySelectorAll('#panel-loja .sub-panel[id^="sub-panel-skin-"]').forEach(p=>p.classList.remove('active'));
    document.getElementById('sub-panel-skin-'+categoria).classList.add('active');
    renderSkinsPorCategoria(categoria);
}

function renderPlanos(){
    var grid = document.getElementById('planosGrid');
    if(!grid) return;
    var html = '';
    PLANOS.forEach(function(p){
        html += '<div class="plano-card" id="plano'+p.id+'" onclick="selecionarPlano('+p.id+')">';
        html += '<div class="plano-nome">'+p.nome+'</div>';
        html += '<div class="plano-moedas">⚡ '+p.moedas+'</div>';
        html += '<div class="plano-preco">R$ '+p.preco.toFixed(2)+'</div>';
        html += '<div class="plano-desc">'+p.desc+'</div>';
        if(p.desconto) html += '<div><span class="plano-desconto">'+p.desconto+'</span></div>';
        if(p.tag) html += '<div class="plano-tag">'+p.tag+'</div>';
        html += '<button class="btn-loja btn-comprar-volts" style="display:none;margin-top:10px" id="btnPlano'+p.id+'" onclick="event.stopPropagation();pagarComPix('+p.id+')">💳 PAGAR COM PIX</button>';
        html += '</div>';
    });
    grid.innerHTML = html;
}

function renderSkins(){
    renderSkinsPorCategoria('basica');
}

function renderSkinsPorCategoria(categoria){
    fetch('/status').then(r=>r.json()).then(d=>{
        var skinsStatus = d.skins_status || [];
        var gridId = categoria === 'basica' ? 'skinsGridBasicas' : (categoria === 'premium' ? 'skinsGridPremium' : 'skinsGridLendarias');
        var grid = document.getElementById(gridId);
        if(!grid) return;
        var html = '';
        var skinsFiltradas = skinsStatus.filter(function(s){ return s.categoria === categoria; });
        skinsFiltradas.forEach(function(skin){
            var ativa = skin.ativo ? ' ativo' : '';
            var btnHtml = '';
            if(skin.ativo){
                btnHtml = '<button class="btn-loja btn-comprado" style="width:100%;cursor:default">✅ EM USO</button>';
            } else if(skin.comprado){
                btnHtml = '<button class="btn-loja btn-comprar-skin" style="width:100%" onclick="ativarSkin(\\''+skin.id+'\\')">🎨 USAR</button>';
            } else {
                if(skin.preco_moedas == 0){
                    btnHtml = '<button class="btn-loja btn-comprar-skin" style="width:100%" onclick="ativarSkin(\\''+skin.id+'\\')">🆓 ATIVAR</button>';
                } else {
                    btnHtml = '<button class="btn-loja btn-comprar-skin" style="width:100%" onclick="comprarSkin(\\''+skin.id+'\\')">🛒 COMPRAR ('+skin.preco_moedas+' ⚡)</button>';
                }
            }
            html += '<div class="skin-card'+ativa+'">';
            html += '<div class="skin-nome">'+skin.nome+'</div>';
            html += '<div class="skin-desc">'+skin.desc+'</div>';
            html += btnHtml;
            html += '</div>';
        });
        grid.innerHTML = html || '<p style="color:#888;text-align:center">Nenhuma skin</p>';
    });
}

function comprarSkin(skinId){
    if(!emailLogado){alert('Conecte primeiro!');return}
    if(!confirm('Comprar esta skin?'))return;
    fetch('/comprar_skin',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({skin_id:skinId})})
    .then(r=>r.json()).then(d=>{
        if(d.ok){alert(d.msg||'Skin comprada!');document.getElementById('moedasSaldo').textContent=d.moedas;renderSkins();setTimeout(function(){location.reload();},500);}
        else{alert('ERRO: '+d.erro);}
    });
}

function ativarSkin(skinId){
    fetch('/ativar_skin',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({skin_id:skinId})})
    .then(r=>r.json()).then(d=>{
        if(d.ok){alert('Skin ativada!');location.reload();}
        else{alert('ERRO: '+d.erro);}
    });
}

function selecionarPlano(id){
    document.querySelectorAll('.plano-card').forEach(c=>c.classList.remove('selecionado'));
    document.querySelectorAll('[id^="btnPlano"]').forEach(b=>b.style.display='none');
    document.getElementById('plano'+id).classList.add('selecionado');
    document.getElementById('btnPlano'+id).style.display='block';
    planoSelecionado=id;
}

function pagarComPix(planoId){
    var email=document.getElementById('emailCompra').value.trim()||emailLogado;
    if(!email){alert('Digite seu email!');return}
    document.getElementById('modalPix').classList.add('active');
    document.getElementById('pixContent').innerHTML='<p style="color:#ffd700">Gerando QR Code PIX...</p>';
    fetch('/criar_pix',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:email,plano_id:planoId})})
    .then(r=>r.json()).then(d=>{
        if(d.sucesso){
            pixAtual=d;
            var html='<p style="font-size:18px;color:#ffd700">R$ '+d.valor.toFixed(2)+'</p>';
            html+='<p style="color:#00ff88">⚡ '+d.moedas+' VOLTS</p>';
            if(d.qr_code_base64)html+='<div class="pix-qrcode"><img src="data:image/png;base64,'+d.qr_code_base64+'" alt="QR Code PIX"></div>';
            if(d.qr_code){html+='<p style="color:#888;font-size:10px;margin-top:8px">📋 Copie o código:</p><div class="pix-copiavel" onclick="copiarPix()">'+d.qr_code+'</div>';}
            html+='<button class="btn-confirmar" onclick="verificarPagamento(\\''+d.pix_id+'\\')">🔄 VERIFICAR PAGAMENTO</button>';
            document.getElementById('pixContent').innerHTML=html;
        }else{document.getElementById('pixContent').innerHTML='<p style="color:#ff4444">Erro: '+(d.erro||'Falha')+'</p>';}
    });
}

function copiarPix(){navigator.clipboard.writeText(pixAtual.qr_code).then(()=>alert('Código PIX copiado!'));}
function verificarPagamento(pixId){
    fetch('/verificar_pix',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({pix_id:pixId})})
    .then(r=>r.json()).then(d=>{if(d.pago){alert('PAGO! +'+d.moedas+' VOLTS!');document.getElementById('moedasSaldo').textContent=d.saldo;fecharModal();}else{alert('Ainda não confirmado.');}});
}
function fecharModal(){document.getElementById('modalPix').classList.remove('active');pixAtual=null;}

function atualizarPercentual(){
    var perc = document.getElementById('percentualBanca').value;
    fetch('/set_percentual',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({percentual:parseInt(perc)})});
    var banca = parseFloat(document.getElementById('banca').textContent.replace('$','')) || 0;
    var valor = (banca * perc / 100).toFixed(2);
    document.getElementById('valorEstimado').textContent = '($' + valor + ')';
}

function conectarIQ(){
    var email=document.getElementById('email').value.trim();
    var senha=document.getElementById('senha').value.trim();
    var tipo=document.getElementById('tipo').value;
    if(!email||!senha){alert('Preencha email e senha!');return}
    emailLogado=email;
    document.getElementById('btnConectar').disabled=true;
    document.getElementById('btnConectar').textContent='Conectando...';
    fetch('/conectar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:email,senha:senha,tipo:tipo})})
    .then(r=>r.json()).then(d=>{
        if(d.ok){
            conectadoIQ=true;
            document.getElementById('btnConectar').style.display='none';
            document.getElementById('btnDesconectar').style.display='inline-block';
            document.getElementById('btnOperar').style.display='inline-block';
            document.getElementById('btnParar').style.display='none';
            document.getElementById('statusTexto').textContent='🟢 Conectado';
            document.getElementById('statusDot').className='status-dot active';
            document.getElementById('moedasSaldo').textContent=d.moedas||0;
            if(intervalo)clearInterval(intervalo);
            intervalo=setInterval(atualizar,2000);
            atualizar();
            iniciarChat();
        }else{
            alert('ERRO: '+d.erro);
            document.getElementById('btnConectar').disabled=false;
            document.getElementById('btnConectar').textContent='🔌 CONECTAR';
        }
    });
}

function desconectarIQ(){
    if(botAtivo){alert('⚠️ Pare o bot primeiro!');return;}
    if(confirm('Desconectar da IQ Option?')){
        fetch('/parar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({desconectar:true})});
        setTimeout(function(){location.reload()},2000);
    }
}

function comecarOperar(){
    if(!conectadoIQ){alert('Conecte primeiro!');return}
    document.getElementById('btnOperar').disabled=true;
    document.getElementById('btnOperar').textContent='...';
    fetch('/comecar_operar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({})})
    .then(r=>r.json()).then(d=>{
        if(d.ok){
            botAtivo=true;
            document.getElementById('btnOperar').style.display='none';
            document.getElementById('btnParar').style.display='inline-block';
            document.getElementById('statusTexto').textContent='🤖 Aguardando Sinal';
            document.getElementById('moedasSaldo').textContent=d.moedas;
        }else{
            alert('ERRO: '+d.erro);
            document.getElementById('btnOperar').disabled=false;
            document.getElementById('btnOperar').textContent='🚀 COMEÇAR OPERAR';
        }
    });
}

function pararBot(){
    if(!confirm('Parar o bot?'))return;
    fetch('/parar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({})})
    .then(()=>{location.reload()});
}

function verRelatorio(){
    var email=document.getElementById('emailRelatorio').value.trim();
    if(!email){alert('Digite o email!');return}
    fetch('/relatorio?email='+email).then(r=>r.json()).then(d=>{
        if(d.erro){alert(d.erro);return}
        var h='<div class="relatorio-grid">';
        h+='<div class="relatorio-card"><div class="rlabel">⚡ VOLTS</div><div class="rvalue">'+(d.moedas||0)+'</div></div>';
        h+='<div class="relatorio-card"><div class="rlabel">📈 LUCRO TOTAL</div><div class="rvalue">$'+(d.lucro_total||0).toFixed(2)+'</div></div>';
        h+='<div class="relatorio-card"><div class="rlabel">✅ WINS</div><div class="rvalue">'+(d.total_wins||0)+'</div></div>';
        h+='<div class="relatorio-card"><div class="rlabel">❌ LOSSES</div><div class="rvalue">'+(d.total_losses||0)+'</div></div>';
        h+='<div class="relatorio-card"><div class="rlabel">🔄 CICLOS</div><div class="rvalue">'+(d.total_ciclos||0)+'</div></div>';
        h+='</div>';
        if(d.historico_operacoes&&d.historico_operacoes.length>0){
            h+='<table class="historico-table"><tr><th>Data</th><th>Resultado</th><th>Valor</th><th>Lucro</th></tr>';
            d.historico_operacoes.slice(-10).reverse().forEach(op=>{
                h+='<tr><td>'+op.data+'</td><td style="color:'+(op.resultado=='WIN'?'#00ff88':'#ff4444')+'">'+op.resultado+'</td><td>$'+op.valor.toFixed(2)+'</td><td>$'+op.lucro.toFixed(2)+'</td></tr>';
            });
            h+='</table>';
        }
        document.getElementById('relatorioContent').innerHTML=h;
    });
}

function verRanking(){
    fetch('/ranking').then(r=>r.json()).then(d=>{
        var h='<div class="relatorio-grid"><div class="relatorio-card"><div class="rlabel">👥 USUÁRIOS</div><div class="rvalue">'+d.stats.total_usuarios+'</div></div>';
        h+='<div class="relatorio-card"><div class="rlabel">🎯 TAXA GLOBAL</div><div class="rvalue">'+d.stats.taxa_global+'%</div></div></div>';
        h+='<table class="historico-table"><tr><th>#</th><th>EMAIL</th><th>LUCRO</th><th>WINS</th><th>TAXA</th></tr>';
        d.ranking.forEach((u,i)=>{
            h+='<tr><td>'+(i+1)+'</td><td>'+u.email+'</td><td style="color:'+(u.lucro_total>=0?'#00ff88':'#ff4444')+'">$'+u.lucro_total.toFixed(2)+'</td><td>'+u.total_wins+'</td><td>'+u.taxa+'%</td></tr>';
        });
        h+='</table>';
        document.getElementById('relatorioContent').innerHTML=h;
    });
}

function atualizar(){
    fetch('/status').then(r=>r.json()).then(d=>{
        if(d.banca)document.getElementById('banca').textContent='$'+d.banca.toFixed(2);
        if(d.lucro!==undefined){var el=document.getElementById('lucro');el.textContent='$'+d.lucro.toFixed(2);el.style.color=d.lucro>=0?'#00ff88':'#ff4444';}
        if(d.ops!==undefined)document.getElementById('ops').textContent=d.ops;
        if(d.moedas!==undefined)document.getElementById('moedasSaldo').textContent=d.moedas;
        if(d.sinal)document.getElementById('sinal').textContent=d.sinal;
        if(d.logs)document.getElementById('terminal').innerHTML=d.logs;
        document.getElementById('terminal').scrollTop=document.getElementById('terminal').scrollHeight;
    });
}

// Chat
var chatIntervalo = null;
function iniciarChat(){
    var nome = emailLogado || '';
    if(!nome) return;
    document.getElementById('chatInfo').textContent = '✅ Chat ativo: ' + nome;
    document.getElementById('chatInfo').style.color = '#00ff88';
    if(chatIntervalo) clearInterval(chatIntervalo);
    chatIntervalo = setInterval(atualizarChat, 3000);
    atualizarChat();
}

function enviarChatMsg(){
    var nome = emailLogado || 'Anonimo';
    var msg = document.getElementById('chatMsg').value.trim();
    if(!msg) return;
    fetch('/chat_enviar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({nome:nome,msg:msg})})
    .then(()=>{document.getElementById('chatMsg').value='';atualizarChat();});
}

function atualizarChat(){
    fetch('/chat_mensagens').then(r=>r.json()).then(d=>{
        var html='';
        (d.mensagens||[]).forEach(m=>{
            html+='<div><span style="color:#ffd700">'+m.nome+'</span> <span style="color:#555">'+m.hora+'</span><br><span style="color:#ccc">'+m.msg+'</span></div><hr style="border-color:#222">';
        });
        document.getElementById('chatMensagens').innerHTML=html||'<p style="color:#888">Nenhuma mensagem</p>';
        document.getElementById('chatMensagens').scrollTop=document.getElementById('chatMensagens').scrollHeight;
        document.getElementById('chatOnline').textContent = '🟢 ' + (d.online || 1) + ' online';
    });
}

window.onload=function(){
    renderPlanos();
    fetch('/status').then(r=>r.json()).then(d=>{
        if(d.conectado&&d.email){
            conectadoIQ=true;emailLogado=d.email;
            document.getElementById('email').value=d.email;
            document.getElementById('btnConectar').style.display='none';
            document.getElementById('btnDesconectar').style.display='inline-block';
            if(d.rodando){botAtivo=true;document.getElementById('btnOperar').style.display='none';document.getElementById('btnParar').style.display='inline-block';document.getElementById('statusTexto').textContent='🤖 Aguardando Sinal';}
            else{document.getElementById('btnOperar').style.display='inline-block';}
            document.getElementById('statusDot').className='status-dot active';
            document.getElementById('statusTexto').textContent='🟢 Conectado';
            intervalo=setInterval(atualizar,2000);
            atualizar();
            iniciarChat();
        }
    });
    setInterval(atualizarChat,3000);
};

// Efeitos visuais das skins
function initSkinEffects() {
    var matrixCanvas = document.getElementById('matrixCanvas');
    if(matrixCanvas){
        var mctx = matrixCanvas.getContext('2d');
        matrixCanvas.width = matrixCanvas.parentElement.offsetWidth;
        matrixCanvas.height = matrixCanvas.parentElement.offsetHeight;
        var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*()';
        var fontSize = 14;
        var columns = Math.floor(matrixCanvas.width / fontSize);
        var drops = [];
        for(var i=0;i<columns;i++) drops[i]=Math.random()*-100;
        function drawMatrix(){
            mctx.fillStyle='rgba(0,0,0,0.05)';
            mctx.fillRect(0,0,matrixCanvas.width,matrixCanvas.height);
            mctx.fillStyle='#00ff00';
            mctx.font=fontSize+'px monospace';
            for(var i=0;i<drops.length;i++){
                var text=chars[Math.floor(Math.random()*chars.length)];
                mctx.fillText(text,i*fontSize,drops[i]*fontSize);
                if(drops[i]*fontSize>matrixCanvas.height && Math.random()>0.975) drops[i]=0;
                drops[i]++;
            }
            requestAnimationFrame(drawMatrix);
        }
        drawMatrix();
    }
    var sakuraCanvas = document.getElementById('sakuraCanvas');
    if(sakuraCanvas){
        var skctx = sakuraCanvas.getContext('2d');
        sakuraCanvas.width = sakuraCanvas.parentElement.offsetWidth;
        sakuraCanvas.height = sakuraCanvas.parentElement.offsetHeight;
        var petals = [];
        for(var i=0;i<20;i++) petals.push({x:Math.random()*sakuraCanvas.width,y:Math.random()*sakuraCanvas.height,r:Math.random()*4+2,speed:Math.random()*0.5+0.3,wind:(Math.random()-0.5)*0.4,rotation:Math.random()*Math.PI*2,rotSpeed:(Math.random()-0.5)*0.02});
        function drawSakura(){
            skctx.clearRect(0,0,sakuraCanvas.width,sakuraCanvas.height);
            petals.forEach(function(p){
                skctx.save();
                skctx.translate(p.x,p.y);
                skctx.rotate(p.rotation);
                skctx.fillStyle='rgba(255,105,180,0.6)';
                skctx.beginPath();
                skctx.ellipse(0,0,p.r,p.r*0.6,0,0,Math.PI*2);
                skctx.fill();
                skctx.restore();
                p.y+=p.speed;
                p.x+=p.wind;
                p.rotation+=p.rotSpeed;
                if(p.y>sakuraCanvas.height+10){p.y=-10;p.x=Math.random()*sakuraCanvas.width;}
            });
            requestAnimationFrame(drawSakura);
        }
        drawSakura();
    }
    var thunderCanvas = document.getElementById('thunderCanvas');
    if(thunderCanvas){
        var tctx = thunderCanvas.getContext('2d');
        thunderCanvas.width = thunderCanvas.parentElement.offsetWidth;
        thunderCanvas.height = thunderCanvas.parentElement.offsetHeight;
        function drawThunder(){
            tctx.clearRect(0,0,thunderCanvas.width,thunderCanvas.height);
            if(Math.random()<0.02){
                tctx.strokeStyle='rgba(255,255,100,0.8)';
                tctx.lineWidth=2;
                tctx.beginPath();
                var x=Math.random()*thunderCanvas.width;
                tctx.moveTo(x,0);
                for(var y=0;y<thunderCanvas.height;y+=20){
                    x+=(Math.random()-0.5)*60;
                    tctx.lineTo(x,y);
                }
                tctx.stroke();
                tctx.strokeStyle='rgba(255,255,255,0.5)';
                tctx.lineWidth=1;
                tctx.stroke();
            }
            requestAnimationFrame(drawThunder);
        }
        drawThunder();
    }
    var oceanCanvas = document.getElementById('oceanCanvas');
    if(oceanCanvas){
        var octx = oceanCanvas.getContext('2d');
        oceanCanvas.width = oceanCanvas.parentElement.offsetWidth;
        oceanCanvas.height = 100;
        var offset=0;
        function drawOcean(){
            octx.clearRect(0,0,oceanCanvas.width,oceanCanvas.height);
            octx.beginPath();
            octx.moveTo(0,oceanCanvas.height);
            for(var x=0;x<oceanCanvas.width;x+=5){
                var y = oceanCanvas.height/2 + Math.sin(x*0.02+offset)*15 + Math.sin(x*0.05+offset*1.3)*10;
                octx.lineTo(x,y);
            }
            octx.lineTo(oceanCanvas.width,oceanCanvas.height);
            octx.closePath();
            octx.fillStyle='rgba(0,170,204,0.3)';
            octx.fill();
            offset+=0.03;
            requestAnimationFrame(drawOcean);
        }
        drawOcean();
    }
    var sunsetCanvas = document.getElementById('sunsetCanvas');
    if(sunsetCanvas){
        var sctx2 = sunsetCanvas.getContext('2d');
        sunsetCanvas.width = sunsetCanvas.parentElement.offsetWidth;
        sunsetCanvas.height = sunsetCanvas.parentElement.offsetHeight;
        var stars=[];
        for(var i=0;i<30;i++) stars.push({x:Math.random()*sunsetCanvas.width,y:Math.random()*sunsetCanvas.height*0.5,r:Math.random()*2+0.5,twinkle:Math.random()*Math.PI*2,speed:Math.random()*0.02+0.01});
        function drawSunset(){
            sctx2.clearRect(0,0,sunsetCanvas.width,sunsetCanvas.height);
            stars.forEach(function(s){
                s.twinkle+=s.speed;
                var alpha=0.3+Math.sin(s.twinkle)*0.5;
                sctx2.fillStyle='rgba(255,200,100,'+alpha+')';
                sctx2.beginPath();
                sctx2.arc(s.x,s.y,s.r,0,Math.PI*2);
                sctx2.fill();
            });
            requestAnimationFrame(drawSunset);
        }
        drawSunset();
    }
    var darkCanvas = document.getElementById('darkCanvas');
    if(darkCanvas){
        var dctx = darkCanvas.getContext('2d');
        darkCanvas.width = darkCanvas.parentElement.offsetWidth;
        darkCanvas.height = darkCanvas.parentElement.offsetHeight;
        var particles=[];
        for(var i=0;i<25;i++) particles.push({x:Math.random()*darkCanvas.width,y:Math.random()*darkCanvas.height,r:Math.random()*3+1,vx:(Math.random()-0.5)*0.3,vy:-Math.random()*0.5-0.1,alpha:Math.random()*0.5+0.2});
        function drawDark(){
            dctx.clearRect(0,0,darkCanvas.width,darkCanvas.height);
            particles.forEach(function(p){
                dctx.beginPath();
                dctx.arc(p.x,p.y,p.r,0,Math.PI*2);
                dctx.fillStyle='rgba(153,51,255,'+p.alpha+')';
                dctx.fill();
                p.x+=p.vx;
                p.y+=p.vy;
                if(p.y<-10){p.y=darkCanvas.height+10;p.x=Math.random()*darkCanvas.width;}
                if(p.x<-10)p.x=darkCanvas.width+10;
                if(p.x>darkCanvas.width+10)p.x=-10;
            });
            requestAnimationFrame(drawDark);
        }
        drawDark();
    }
    var fireCanvas = document.getElementById('fireCanvas');
    if(fireCanvas){
        var fctx = fireCanvas.getContext('2d');
        fireCanvas.width = fireCanvas.parentElement.offsetWidth;
        fireCanvas.height = 80;
        var fireParticles=[];
        for(var i=0;i<50;i++) fireParticles.push({x:Math.random()*fireCanvas.width,y:fireCanvas.height-Math.random()*30,vx:(Math.random()-0.5)*0.8,vy:-Math.random()*2.5-1,life:Math.random()*40+20,maxLife:60,size:Math.random()*5+2});
        function drawFire(){
            fctx.clearRect(0,0,fireCanvas.width,fireCanvas.height);
            fireParticles.forEach(function(p,i){
                var progress=p.life/p.maxLife;
                var gradient=fctx.createRadialGradient(p.x,p.y,0,p.x,p.y,p.size*progress);
                gradient.addColorStop(0,'rgba(255,255,100,'+progress+')');
                gradient.addColorStop(0.4,'rgba(255,150,0,'+progress*0.8+')');
                gradient.addColorStop(1,'rgba(255,0,0,0)');
                fctx.beginPath();
                fctx.arc(p.x,p.y,p.size*progress,0,Math.PI*2);
                fctx.fillStyle=gradient;
                fctx.fill();
                p.x+=p.vx;
                p.y+=p.vy;
                p.life--;
                if(p.life<=0){
                    fireParticles[i]={x:Math.random()*fireCanvas.width,y:fireCanvas.height-Math.random()*10,vx:(Math.random()-0.5)*0.8,vy:-Math.random()*2.5-1,life:Math.random()*40+20,maxLife:60,size:Math.random()*5+2};
                }
            });
            requestAnimationFrame(drawFire);
        }
        drawFire();
    }
    var snowCanvas = document.getElementById('snowCanvas');
    if(snowCanvas){
        var sctx = snowCanvas.getContext('2d');
        snowCanvas.width = snowCanvas.parentElement.offsetWidth;
        snowCanvas.height = snowCanvas.parentElement.offsetHeight;
        var snowflakes=[];
        for(var i=0;i<40;i++) snowflakes.push({x:Math.random()*snowCanvas.width,y:Math.random()*snowCanvas.height,r:Math.random()*3+1,speed:Math.random()*0.8+0.2,wind:(Math.random()-0.5)*0.3,opacity:Math.random()*0.6+0.4});
        function drawSnow(){
            sctx.clearRect(0,0,snowCanvas.width,snowCanvas.height);
            snowflakes.forEach(function(f){
                sctx.beginPath();
                sctx.arc(f.x,f.y,f.r,0,Math.PI*2);
                sctx.fillStyle='rgba(255,255,255,'+f.opacity+')';
                sctx.fill();
                f.y+=f.speed;
                f.x+=f.wind;
                if(f.y>snowCanvas.height+10){f.y=-10;f.x=Math.random()*snowCanvas.width;}
                if(f.x>snowCanvas.width+10)f.x=-10;
                if(f.x<-10)f.x=snowCanvas.width+10;
            });
            requestAnimationFrame(drawSnow);
        }
        drawSnow();
    }
}
window.addEventListener('load',function(){setTimeout(initSkinEffects,300);});
</script>
</body>
</html>
"""

if __name__ == '__main__':
    print("=" * 50)
    print("⚡ TESLA 369 BOT v9.0.0 - MODO SINAL EXTERNO ⚡")
    print("Envie sinais via POST para /sinal")
    print('Exemplo: curl -X POST http://localhost:5000/sinal -H "Content-Type: application/json" -d \'{"direcao":"call"}\'')
    print("=" * 50)
    port = int(os.environ.get('PORT', 5000))
    try:
        import webbrowser
        webbrowser.open(f'http://localhost:{port}')
    except:
        pass
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
