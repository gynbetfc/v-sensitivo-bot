#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ⚡ TESLA 369 BOT v9.0.0 ⚡
# MODO SINAL AUTOMÁTICO VIA CLOUD PLUGINS
# HISTÓRICO, INTERFACE E ALGORITMOS 100% EM NUVEM

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
import hashlib as _hl

warnings.filterwarnings("ignore")
app = Flask(__name__)

# ============= CONFIGURAÇÕES =============
FB_URL = "https://nexos-40654-default-rtdb.firebaseio.com"
print("✅ Firebase HTTP REST configurado!")

# Endpoints do Repositório Público no GitHub
HTML_URL = "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/tesla_369_bot/templates/index.html"
GIT_API_ESTRATEGIAS = "https://api.github.com/repos/gynbetfc/v-sensitivo-bot/contents/tesla_369_bot/estrategias"
GIT_RAW_ESTRATEGIAS_BASE = "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/tesla_369_bot/estrategias"

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
        'css_extra': 'body{background:#000011!important}.header{border-color:#ffff00!important;box-shadow:0 0 50px rgba(255,255,0,0.3)}'
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
        'css_extra': 'body{background:linear-gradient(180deg,#1a0010 0%,#331100 50%,#1a0000 100%)!important}.header{border-color:#ff6600!important;box-shadow:0 0 40px rgba(255,102,0,0.3)}'
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
        'css_extra': 'body{background:linear-gradient(180deg,#000a1a 0%,#001133 100%)!important}.header{border-color:#3399ff!important;box-shadow:0 0 40px rgba(51,153,255,0.3)}'
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

# Cache do HTML
html_cache = {"content": None, "timestamp": 0}
HTML_CACHE_TTL = 30  # TTL menor para desenvolvimento ágil

# ============= VARIÁVEIS GLOBAIS DE CONTROLE =============
API, par = None, "EURUSD-OTC"
timeframe_atual = 60
lucro, NumDeOperacoes = 0.0, 0
BANCA_INICIAL_DO_BOT, STOP_GAIN_ATINGIDO = 0, False
bot_rodando, bot_thread = False, None
conectado_iq = False
ultimo_sinal, ultima_analise = "Aguardando...", {}
logs_web, MAX_LOGS_WEB = [], 200
email_usuario_atual = ""
skin_atual_global = 'skin_padrao'
estrategia_atual_global = 'v_sensitivo'
pagamentos_pendentes = {}
bot_lock = threading.Lock()
sinal_pendente = None  
sinal_lock = threading.Lock()

# ============= 🌐 ENGENHARIA DE ESTRATÉGIAS CLOUD =============

def carregar_estrategias_da_nuvem():
    """Varre e executa o cabeçalho INFO dos scripts remotos direto do GitHub"""
    estrategias_remotas = {}
    try:
        resp_git = requests.get(GIT_API_ESTRATEGIAS, timeout=8)
        if resp_git.status_code == 200:
            itens = resp_git.json()
            nomes_scripts = [i["name"][:-3] for i in itens if i["name"].endswith(".py") and i["name"] != "__init__.py"]
            
            for script in nomes_scripts:
                try:
                    url_raw = f"{GIT_RAW_ESTRATEGIAS_BASE}/{script}.py"
                    resp_raw = requests.get(url_url := url_raw, timeout=5)
                    if resp_raw.status_code == 200:
                        escopo_memoria = {}
                        exec(resp_raw.text, {}, escopo_memoria)
                        if 'INFO' in escopo_memoria:
                            info = escopo_memoria['INFO']
                            estrategias_remotas[script] = {
                                'nome': info.get('nome', script.upper()),
                                'desc': info.get('desc', 'Sem descrição.'),
                                'preco_moedas': info.get('preco', 0),
                                'timeframe': info.get('timeframe', 60),
                                'gratis': info.get('preco', 0) == 0
                            }
                except Exception as e:
                    print(f"⚠️ Erro ao compilar metadados de {script}: {e}")
    except Exception as e:
        print(f"⚠️ Erro na requisição à API do GitHub: {e}")
        
    # Fallback de segurança se o Git estiver offline
    if 'v_sensitivo' not in estrategias_remotas:
        estrategias_remotas['v_sensitivo'] = {'nome': 'V-Sensitivo Script', 'desc': 'Análise de momentum pura.', 'preco_moedas': 0, 'timeframe': 60, 'gratis': True}
    return estrategias_remotas

def get_html_from_github():
    global html_cache
    agora = time.time()
    if html_cache["content"] and (agora - html_cache["timestamp"]) < HTML_CACHE_TTL:
        return html_cache["content"]
        
    try:
        response = requests.get(HTML_URL, timeout=10)
        if response.status_code == 200:
            html_template = response.text
            html_cache["content"] = html_template
            html_cache["timestamp"] = agora
            return html_template
    except Exception as e:
        print(f"⚠️ Falha de rede no HTML: {e}")
    return html_cache["content"] if html_cache["content"] else "<h1>Erro Crítico Cloud Server</h1>"

def processar_html_com_skin():
    global skin_atual_global
    skin = next((s for s in SKINS if s['id'] == skin_atual_global), SKINS[0])
    html_template = get_html_from_github()
    
    planos_json = []
    for p in PLANOS:
        planos_json.append(f'{{"id":{p["id"]},"moedas":{p["moedas"]},"preco":{p["preco"]},"nome":"{p["nome"]}","desc":"{p["desc"]}","tag":"{p.get("tag","")}","desconto":"{p.get("desconto","")}"}}')
    
    html_template = html_template.replace('{{ COR_FUNDO }}', skin['cor_fundo'])
    html_template = html_template.replace('{{ COR_PANEL }}', skin['cor_panel'])
    html_template = html_template.replace('{{ COR_DESTAQUE }}', skin['cor_destaque'])
    html_template = html_template.replace('{{ COR_TEXTO }}', skin['cor_texto'])
    html_template = html_template.replace('{{ COR_BOTAO }}', skin['cor_botao'])
    html_template = html_template.replace('{{ COR_TAB_ATIVA }}', skin['cor_tab_ativa'])
    html_template = html_template.replace('{{ COR_HEADER_BG }}', skin['cor_header_bg'])
    html_template = html_template.replace('{{ COR_HEADER_BORDA }}', skin['cor_header_borda'])
    html_template = html_template.replace('{{ CSS_EXTRA }}', skin.get('css_extra', ''))
    html_template = html_template.replace('{{ HEADER_EXTRA }}', skin.get('header_extra', '<div class="lightning"></div>'))
    html_template = html_template.replace('{{ PLANOS_JSON | safe }}', ','.join(planos_json))
    html_template = html_template.replace('{{ PLANOS_JSON }}', ','.join(planos_json))
    
    return html_template

# ========== FUNÇÕES DE USUÁRIO (FIREBASE) ==========

def _sanitizar_dados(dados):
    if 'historico_operacoes' in dados:
        if len(dados['historico_operacoes']) > 50:
            dados['historico_operacoes'] = dados['historico_operacoes'][-50:]
        for op in dados['historico_operacoes']:
            for chave in list(op.keys()):
                if isinstance(op[chave], float):
                    op[chave] = round(op[chave], 2)
    if 'estrategias_compradas' not in dados:
        dados['estrategias_compradas'] = ['v_sensitivo']
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
        'skin_atual': 'skin_padrao', 'skins_compradas': ['skin_padrao'],
        'estrategia_atual': 'v_sensitivo', 'estrategias_compradas': ['v_sensitivo']
    }
    salvar_usuario(email, dados)
    return dados

# ============= ENGENHARIA DE EXECUÇÃO AUTOMÁTICA =============

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
    segundo_atual = datetime.now().second
    if segundo_atual <= 15:
        add_log(f"   ✅ Entrada imediata autorizada (segundo {segundo_atual})", 'info')
        return True
        
    add_log("   ⏳ Gatilho detectado no final da vela. Sincronizando próxima virada...", 'info')
    while datetime.now().second > 1:
        if not bot_rodando:
            return False
        time.sleep(0.1)
    return True

def aguardar_vela_fechar(ts_entrada):
    add_log(f"   ⏳ Aguardando fechamento da operação...", 'info')
    while True:
        if not bot_rodando:
            return False
        try:
            ts_atual = pegar_timestamp()
            if ts_atual != ts_entrada and ts_atual != 0:
                add_log("   ✅ Vela fechada!", 'info')
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
    global lucro, NumDeOperacoes, STOP_GAIN_ATINGIDO, bot_rodando
    try:
        if not API:
            add_log("❌ API offline!", 'error')
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
                add_log("❌ Margem insuficiente!", 'error')
                break
            print()
            add_log(f"🎯 {'OPERAÇÃO' if i == 0 else f'GALE {i}'}: {direcao.upper()} ${valor:.2f}", 'info')
            st, id_ordem = API.buy(valor, par, direcao, 1)
            if not st or not id_ordem:
                try:
                    st, id_ordem = API.buy_digital_spot(par, valor, direcao, 1)
                except:
                    pass
            if not st or not id_ordem:
                add_log("❌ Rejeitado pela corretora!", 'error')
                break
            add_log(f"   📝 ID da Ordem: #{id_ordem}", 'info')
            time.sleep(0.3)
            ts_real = pegar_timestamp()
            if ts_real == 0:
                add_log("⚠️ Falha de sincronia de tempo.", 'warning')
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
                        'estrategia': estrategia_atual_global.upper()
                    })
                    u['dias_ativos'] = u.get('dias_ativos', 0) + 1
                    salvar_usuario(email_usuario_atual, u)
                STOP_GAIN_ATINGIDO = True
                add_log("🎯 STOP GAIN ALCANÇADO!", 'win')
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
                        'estrategia': estrategia_atual_global.upper()
                    })
                    u['dias_ativos'] = u.get('dias_ativos', 0) + 1
                    salvar_usuario(email_usuario_atual, u)
                if i < MARTINGALE:
                    add_log(f"   ➡️ Preparando GALE {i + 1}...", 'loss')
                else:
                    add_log("   💀 CICLO DE GALE ESGOTADO!", 'loss')
        
        bf = API.get_balance() if API else bi
        print()
        add_log("=" * 50, 'info')
        add_log(f"{'🌟 LUCRO' if bf > bi else '💀 PERDA'}: ${abs(bf - bi):.2f} | Saldo: ${bf:.2f}", 'info')
        add_log("=" * 50, 'info')
    except Exception as e:
        add_log(f"Erro no pipeline: {e}", 'error')
    finally:
        bot_rodando = False
        add_log("⏹️ Ciclo finalizado! Pronto para reinicialização.", 'info')

def bot_loop():
    global bot_rodando, BANCA_INICIAL_DO_BOT, lucro, NumDeOperacoes, STOP_GAIN_ATINGIDO, sinal_pendente, ultimo_sinal
    
    with bot_lock:
        if not bot_rodando:
            return
        
        add_log(f'⚡ TESLA 369 INTERFACE CLOUD - ALGORITMO ACIONADO', 'sensitive')
        
        if not API:
            add_log('❌ API desconectada!', 'error')
            bot_rodando = False
            return
            
        BANCA_INICIAL_DO_BOT = API.get_balance()
        STOP_GAIN_ATINGIDO = False
        lucro = 0.0
        NumDeOperacoes = 0
        ultimo_sinal = "Caçando padrão..."
        
        add_log(f"📌 Ativo: {par} | Scanner Cloud Ativo | 💰 ${BANCA_INICIAL_DO_BOT:.2f}")
        
        # 🛸 DISPARO DO BOTZINHO EM MEMÓRIA SECUNDÁRIA (CLOUD INJECTION)
        url_modulo_remoto = f"{GIT_RAW_ESTRATEGIAS_BASE}/{estrategia_atual_global}.py"
        
        def processamento_botzinho_remoto():
            global timeframe_atual
            try:
                add_log(f"🌐 Cloud Engine: Injetando lógica '{estrategia_atual_global}' via Git...", "info")
                requisicao = requests.get(url_modulo_remoto, timeout=10)
                if requisicao.status_code == 200:
                    escopo_local = {}
                    exec(requisicao.text, {}, escopo_local)
                    
                    if 'rodar_analise' in escopo_local:
                        # Executa o botzinho injetado direto do github passing active API
                        sinal_detectado = escopo_local['rodar_analise'](API, par, add_log)
                        
                        # Retorno estruturado: pode ser string ou dicionário contendo timeframe dinâmico
                        if sinal_detectado and bot_rodando:
                            direcao = ""
                            if isinstance(sinal_detectado, dict):
                                direcao = sinal_detectado.get("direcao", "").lower()
                                timeframe_atual = sinal_detectado.get("timeframe", 60)
                            else:
                                direcao = str(sinal_detectado).lower()
                            
                            if direcao in ['call', 'put']:
                                with sinal_lock:
                                    sinal_pendente = direcao
                            else:
                                add_log("⚠️ Botzinho encerrado sem sinal válido.", "info")
                    else:
                        add_log("❌ Erro: Ponto de entrada 'rodar_analise' ausente no script cloud.", "error")
                else:
                    add_log(f"❌ Erro de download do algoritmo: Status {requisicao.status_code}", "error")
            except Exception as e:
                add_log(f"❌ Falha crítica no runtime da estratégia: {e}", "error")

        threading.Thread(target=processamento_botzinho_remoto, daemon=True).start()
        
        # Monitoramento principal aguardando o trigger do plugin cloud
        while bot_rodando and not STOP_GAIN_ATINGIDO:
            try:
                with sinal_lock:
                    direcao = sinal_pendente
                    if direcao:
                        sinal_pendente = None
                
                if direcao in ['call', 'put']:
                    ultimo_sinal = f"GATILHO: {direcao.upper()}"
                    add_log(f"🎯 SINAL DISPARADO PELO PLUGIN: {direcao.upper()}", 'sensitive')
                    executar_ciclo(direcao)
                    break
                
                time.sleep(0.3)
            except Exception as e:
                time.sleep(2)
        
        if not bot_rodando:
            add_log("⏹️ Varredura abortada.", 'info')

def analise_mercado_loop():
    global ultima_analise
    import random
    while True:
        if conectado_iq and API:
            ultima_analise = {
                'rsi': random.uniform(30, 70),
                'mm5': random.uniform(1.0810, 1.0890),
                'mm10': random.uniform(1.0810, 1.0890),
                'mm20': random.uniform(1.0810, 1.0890),
                'stoch': random.uniform(20, 80),
                'fase': random.choice(['ACUMULAÇÃO', 'TENDÊNCIA ALTA', 'TENDÊNCIA BAIXA', 'EXAUSTÃO']),
                'preco': random.uniform(1.08300, 1.08450)
            }
        time.sleep(2)

threading.Thread(target=analise_mercado_loop, daemon=True).start()

# ========== INTERFACE E ENDPOINTS REST ==========

@app.route('/')
def index():
    return render_template_string(processar_html_com_skin())

@app.route('/sinal', methods=['POST'])
def receber_sinal():
    global sinal_pendente
    if not bot_rodando:
        return jsonify({'ok': False, 'erro': 'Bot em repouso.'})
    if not conectado_iq:
        return jsonify({'ok': False, 'erro': 'IQ Option offline.'})
    data = request.get_json()
    direcao = data.get('direcao', '').lower()
    if direcao not in ['call', 'put']:
        return jsonify({'ok': False, 'erro': 'Alvo inválido'})
    with sinal_lock:
        sinal_pendente = direcao
    return jsonify({'ok': True, 'mensagem': 'Gatilho externo sincronizado'})

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
    
    # 🛸 Varre os plugins reais do repositório em tempo real
    estrategias_disponiveis = carregar_estrategias_da_nuvem()
    
    estrategias_compradas = u.get('estrategias_compradas', ['v_sensitivo']) if u else ['v_sensitivo']
    estrategia_atual = u.get('estrategia_atual', 'v_sensitivo') if u else 'v_sensitivo'
    
    if estrategia_atual not in estrategias_disponiveis:
        estrategia_atual = 'v_sensitivo'
        
    estrategia_nome = estrategias_disponiveis.get(estrategia_atual, {}).get('nome', 'V-Sensitivo Script')

    return jsonify({
        'conectado': conectado_iq, 'rodando': bot_rodando, 'email': email_usuario_atual,
        'banca': API.get_balance() if API else 0, 'lucro': lucro, 'ops': NumDeOperacoes,
        'sinal': ultimo_sinal, 'logs': get_logs_html(40),
        'moedas': u.get('moedas', 0) if u else 0, 'skin_id': skin_atual,
        'skins_status': skins_status,
        'estrategia': estrategia_atual,
        'estrategia_nome': estrategia_nome,
        'estrategias_compradas': estrategias_compradas,
        'estrategias_disponiveis': estrategias_disponiveis,
        'analise': ultima_analise
    })

@app.route('/set_percentual', methods=['POST'])
def set_percentual():
    global PERCENTUAL_BANCA
    PERCENTUAL_BANCA = request.json.get('percentual', 15)
    return jsonify({'ok': True})

@app.route('/selecionar_estrategia', methods=['POST'])
def selecionar_estrategia():
    global estrategia_atual_global
    d = request.get_json() or {}
    est_id = d.get('estrategia', 'v_sensitivo')
    if not email_usuario_atual:
        return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    u = carregar_usuario(email_usuario_atual)
    if not u:
        return jsonify({'ok': False, 'erro': 'Cadastro inexistente'})
    estrategias_compradas = u.get('estrategias_compradas', ['v_sensitivo'])
    if est_id not in estrategias_compradas:
        return jsonify({'ok': False, 'erro': 'Estratégia bloqueada!'})
    u['estrategia_atual'] = est_id
    salvar_usuario(email_usuario_atual, u)
    estrategia_atual_global = est_id
    add_log(f"🧠 Algoritmo de Varredura Alterado: {est_id.upper()}", 'indicator')
    return jsonify({'ok': True})

@app.route('/comprar_estrategia', methods=['POST'])
def comprar_estrategia():
    d = request.get_json() or {}
    est_id = d.get('estrategia_id', '')
    if not email_usuario_atual:
        return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    
    estrategias_disponiveis = carregar_estrategias_da_nuvem()
    if est_id not in estrategias_disponiveis:
        return jsonify({'ok': False, 'erro': 'Estratégia inválida no repositório Cloud'})
        
    u = carregar_usuario(email_usuario_atual)
    if not u:
        return jsonify({'ok': False, 'erro': 'Usuário inválido'})
    if 'estrategias_compradas' not in u:
        u['estrategias_compradas'] = ['v_sensitivo']
    if est_id in u['estrategias_compradas']:
        u['estrategia_atual'] = est_id
        salvar_usuario(email_usuario_atual, u)
        return jsonify({'ok': True, 'moedas': u['moedas'], 'msg': 'Já adquirido!'})
        
    preco = estrategias_disponiveis[est_id]['preco_moedas']
    if u.get('moedas', 0) < preco:
        return jsonify({'ok': False, 'erro': f'Saldo insuficiente ({preco} ⚡)'})
        
    u['moedas'] -= preco
    u['estrategias_compradas'].append(est_id)
    u['estrategia_atual'] = est_id
    salvar_usuario(email_usuario_atual, u)
    
    global estrategia_atual_global
    estrategia_atual_global = est_id
    add_log(f"🛒 Estratégia Premium Liberta: {estrategias_disponiveis[est_id]['nome']}", 'win')
    return jsonify({'ok': True, 'moedas': u['moedas'], 'msg': 'Sucesso!'})

@app.route('/conectar', methods=['POST'])
def conectar():
    global API, email_usuario_atual, conectado_iq, skin_atual_global, estrategia_atual_global, par, timeframe_atual
    try:
        d = request.get_json()
        email = d.get('email', '').strip()
        senha = d.get('senha', '').strip()
        tipo = d.get('tipo', 'PRACTICE')
        if not email or not senha:
            return jsonify({'ok': False, 'erro': 'Credenciais em branco'})
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
        estrategia_atual_global = usuario.get('estrategia_atual', 'v_sensitivo')
        salvar_usuario(email, usuario)
        add_log('🔌 Conectado ao Liquidity Pool da corretora!', 'info')
        add_log(f'✅ Autenticado! ${API.get_balance():.2f} | ⚡ {usuario.get("moedas", 0)} VOLTS', 'win')
        return jsonify({'ok': True, 'moedas': usuario.get('moedas', 0)})
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)[:100]})

@app.route('/comecar_operar', methods=['POST'])
def comecar_operar():
    global bot_rodando, bot_thread, lucro, NumDeOperacoes
    try:
        if not conectado_iq:
            return jsonify({'ok': False, 'erro': 'Efetue a conexão!'})
        
        with bot_lock:
            if bot_rodando and bot_thread and bot_thread.is_alive():
                return jsonify({'ok': False, 'erro': 'Operação em andamento!'})
            
            usuario = carregar_usuario(email_usuario_atual)
            if not usuario:
                return jsonify({'ok': False, 'erro': 'Registro ausente'})
            if usuario.get('moedas', 0) < 1:
                return jsonify({'ok': False, 'erro': 'Carga esgotada! Compre VOLTS.'})
            
            usuario['moedas'] -= 1
            usuario['total_ciclos'] += 1
            salvar_usuario(email_usuario_atual, usuario)
            lucro = 0.0
            NumDeOperacoes = 0
            
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
        return jsonify({'ok': False, 'erro': 'Efetue login'})
    skin = next((s for s in SKINS if s['id'] == skin_id), None)
    if not skin:
        return jsonify({'ok': False, 'erro': 'Não encontrado'})
    usuario = carregar_usuario(email_usuario_atual)
    if not usuario:
        return jsonify({'ok': False, 'erro': 'Inválido'})
    if skin['preco_moedas'] == 0:
        if 'skins_compradas' not in usuario:
            usuario['skins_compradas'] = ['skin_padrao']
        if skin_id not in usuario['skins_compradas']:
            usuario['skins_compradas'].append(skin_id)
        usuario['skin_atual'] = skin_id
        salvar_usuario(email_usuario_atual, usuario)
        skin_atual_global = skin_id
        return jsonify({'ok': True, 'moedas': usuario.get('moedas', 0), 'msg': 'Skin grátis injetada!'})
    if 'skins_compradas' not in usuario:
        usuario['skins_compradas'] = ['skin_padrao']
    if skin_id in usuario['skins_compradas']:
        usuario['skin_atual'] = skin_id
        salvar_usuario(email_usuario_atual, usuario)
        skin_atual_global = skin_id
        return jsonify({'ok': True, 'moedas': usuario['moedas'], 'msg': 'Ativada!'})
    if usuario.get('moedas', 0) < skin['preco_moedas']:
        return jsonify({'ok': False, 'erro': 'VOLTS insuficientes'})
    usuario['moedas'] -= skin['preco_moedas']
    usuario['skins_compradas'].append(skin_id)
    usuario['skin_atual'] = skin_id
    salvar_usuario(email_usuario_atual, usuario)
    skin_atual_global = skin_id
    return jsonify({'ok': True, 'moedas': usuario['moedas'], 'msg': 'Adquirido!'})

@app.route('/ativar_skin', methods=['POST'])
def ativar_skin():
    d = request.get_json()
    skin_id = d.get('skin_id', '')
    if not email_usuario_atual:
        return jsonify({'ok': False, 'erro': 'Efetue a conexão'})
    usuario = carregar_usuario(email_usuario_atual)
    if not usuario:
        return jsonify({'ok': False, 'erro': 'Não encontrado'})
    if 'skins_compradas' not in usuario:
        usuario['skins_compradas'] = ['skin_padrao']
    if skin_id not in usuario['skins_compradas']:
        skin = next((s for s in SKINS if s['id'] == skin_id), None)
        if skin and skin['preco_moedas'] > 0:
            return jsonify({'ok': False, 'erro': 'Bloqueado'})
        usuario['skins_compradas'].append(skin_id)
    usuario['skin_atual'] = skin_id
    salvar_usuario(email_usuario_atual, usuario)
    global skin_atual_global
    skin_atual_global = skin_id
    return jsonify({'ok': True})

# ========== SINTONIA GATEWAY MERCADO PAGO ==========

def gerar_pix_mercadopago(email, plano):
    if MODO_SIMULACAO:
        pix_id = str(uuid.uuid4())[:8]
        pagamentos_pendentes[pix_id] = {'email': email, 'plano_id': plano['id'], 'moedas': plano['moedas'], 'valor': plano['preco'], 'pago': False, 'criado_em': str(datetime.now())[:19]}
        qr_code_falso = f"00020126360014BR.GOV.BCB.PIX0136{email}5204000053039865404{plano['preco']:.2f}5802BR5909Tesla3696009Sao Paulo62070503***6304E3F9"
        return {'sucesso': True, 'simulacao': True, 'pix_id': pix_id, 'qr_code': qr_code_falso, 'qr_code_base64': '', 'valor': plano['preco'], 'moedas': plano['moedas']}
    
    try:
        url = "https://api.mercadopago.com/v1/payments"
        headers = {"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}", "Content-Type": "application/json", "X-Idempotency-Key": str(uuid.uuid4())}
        payment_data = {
            "transaction_amount": float(plano['preco']),
            "description": f"TESLA369 - {plano['moedas']} VOLTS",
            "payment_method_id": "pix",
            "payer": {"email": email, "first_name": "Traders", "last_name": "Tesla", "identification": {"type": "CPF", "number": "00000000000"}}
        }
        response = requests.post(url, json=payment_data, headers=headers, timeout=30)
        data = response.json()
        if response.status_code in [200, 201]:
            pix_id = str(data['id'])
            qr_code = data.get('point_of_interaction', {}).get('transaction_data', {}).get('qr_code', '')
            qr_code_base64 = data.get('point_of_interaction', {}).get('transaction_data', {}).get('qr_code_base64', '')
            pagamentos_pendentes[pix_id] = {'email': email, 'plano_id': plano['id'], 'moedas': plano['moedas'], 'valor': plano['preco'], 'pago': False, 'criado_em': str(datetime.now())[:19]}
            return {'sucesso': True, 'simulacao': False, 'pix_id': pix_id, 'qr_code': qr_code, 'qr_code_base64': qr_code_base64, 'valor': plano['preco'], 'moedas': plano['moedas']}
        return {'sucesso': False, 'erro': 'Gateway de pagamento recusado'}
    except Exception as e:
        return {'sucesso': False, 'erro': str(e)[:50]}

def verificar_pagamento_mp(pix_id):
    if MODO_SIMULACAO:
        return pagamentos_pendentes.get(pix_id, {}).get('pago', False)
    try:
        url = f"https://api.mercadopago.com/v1/payments/{pix_id}"
        headers = {"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}"}
        response = requests.get(url, headers=headers, timeout=10)
        return response.json().get('status') == 'approved'
    except:
        return False

def verificador_automatico_pix():
    while True:
        time.sleep(10)
        try:
            for pix_id, dados in list(pagamentos_pendentes.items()):
                if not dados.get('pago', False) and verificar_pagamento_mp(pix_id):
                    pagamentos_pendentes[pix_id]['pago'] = True
                    u = carregar_usuario(dados['email']) or criar_usuario(dados['email'])
                    u['moedas'] = u.get('moedas', 0) + dados['moedas']
                    salvar_usuario(dados['email'], u)
                    add_log(f"💰 PIX Sincronizado! +{dados['moedas']} VOLTS para {dados['email']}", "win")
        except:
            pass

threading.Thread(target=verificador_automatico_pix, daemon=True).start()

@app.route('/criar_pix', methods=['POST'])
def criar_pix():
    d = request.get_json()
    email = d.get('email', '')
    plano_id = int(d.get('plano_id') or 1)
    if not email: return jsonify({'sucesso': False, 'erro': 'Email nulo'})
    plano = next((p for p in PLANOS if p['id'] == plano_id), None)
    return jsonify(gerar_pix_mercadopago(email, plano))

@app.route('/verificar_pix', methods=['POST'])
def verificar_pix():
    d = request.get_json()
    pix_id = d.get('pix_id', '')
    if verificar_pagamento_mp(pix_id):
        if pix_id in pagamentos_pendentes and not pagamentos_pendentes[pix_id]['pago']:
            pagamentos_pendentes[pix_id]['pago'] = True
            u = carregar_usuario(pagamentos_pendentes[pix_id]['email'])
            u['moedas'] += pagamentos_pendentes[pix_id]['moedas']
            salvar_usuario(pagamentos_pendentes[pix_id]['email'], u)
            return jsonify({'pago': True, 'moedas': pagamentos_pendentes[pix_id]['moedas'], 'saldo': u['moedas']})
        return jsonify({'pago': True})
    return jsonify({'pago': False})

# ========== CHAT MOTOR GLOBAL ==========

@app.route('/chat_enviar', methods=['POST'])
def chat_enviar():
    data = request.json
    try:
        requests.post(f'{FB_URL}/tesla_369/chat.json', json={'nome': data.get('nome', 'Anonimo')[:15], 'msg': data.get('msg', '')[:200], 'hora': datetime.now().strftime('%H:%M')}, timeout=5)
    except: pass
    return jsonify({'ok': True})

@app.route('/chat_mensagens')
def chat_mensagens_route():
    try:
        r = requests.get(f'{FB_URL}/tesla_369/chat.json?orderBy="$key"&limitToLast=50', timeout=5)
        return jsonify({'mensagens': list(r.json().values()) if r.status_code==200 and r.json() else [], 'online': 1})
    except: return jsonify({'mensagens': [], 'online': 1})

# ========== RELATÓRIO E SHUTDOWN ==========

@app.route('/ranking')
def ranking():
    ranking_list = []
    try:
        usuarios = requests.get(f'{FB_URL}/tesla_369/usuarios.json').json() or {}
        for k, ud in usuarios.items():
            if ud:
                ranking_list.append({
                    'email': ud.get('email', 'N/A')[:20] + '...',
                    'lucro_total': round(ud.get('lucro_total', 0), 2),
                    'total_wins': ud.get('total_wins', 0),
                    'total_losses': ud.get('total_losses', 0),
                    'total_ciclos': ud.get('total_ciclos', 0),
                    'taxa': round((ud.get('total_wins', 0) / max(ud.get('total_ciclos', 1), 1)) * 100, 1),
                    'banca_atual': round(ud.get('banca_atual', 0), 2)
                })
    except: pass
    ranking_list.sort(key=lambda x: x['lucro_total'], reverse=True)
    tc = sum(x['total_ciclos'] for x in ranking_list)
    tw = sum(x['total_wins'] for x in ranking_list)
    return jsonify({'ranking': ranking_list[:20], 'stats': {'total_usuarios': len(ranking_list), 'total_ops': tc, 'total_wins': tw, 'taxa_global': round((tw/max(tc,1))*100,1)}})

@app.route('/relatorio')
def relatorio():
    return jsonify(carregar_usuario(request.args.get('email', '')) or {'erro': 'Nao encontrado'})

@app.route('/resetar', methods=['POST'])
def resetar():
    u = carregar_usuario(request.json.get('email', ''))
    if not u: return jsonify({'ok': False, 'msg': 'Nao encontrado'})
    u.update({'total_ciclos':0,'total_wins':0,'total_losses':0,'total_gasto':0.0,'total_ganho':0.0,'lucro_total':0.0,'historico_operacoes':[],'dias_ativos':0,'banca_atual':0.0,'moedas_ganhas_hoje':str(datetime.now())[:10]})
    salvar_usuario(request.json.get('email', ''), u)
    return jsonify({'ok': True, 'msg': 'Resetado!'})

@app.route('/shutdown')
def shutdown():
    import os, signal
    os.kill(os.getpid(), signal.SIGTERM)
    return jsonify({'ok': True})

if __name__ == '__main__':
    print("=" * 50)
    print("⚡ TESLA 369 BOT v9.0.0 - CLOUD PIPELINE OK ⚡")
    print("=" * 50)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
