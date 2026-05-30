# ◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈
# ☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿
# ⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗
#    🌀  O DINHEIRO VEM ATÉ MIM DE TODOS OS LADOS  🌀
#         DE FORMA ABUNDANTE, CONTÍNUA E PRÓSPERA
# ⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗
# ◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈
# ⚡ TESLA 369 BOT v7.0.0 ⚡
# TESLA-369 GRÁTIS | v_SENSITIVO 6⚡ | 3=1 3⚡ | LOJA ESTRATÉGIAS | SKINS | MERCADO PAGO
# BD VIA FIREBASE HTTP REST - MOEDA CONSUMIDA AO CLICAR EM "COMEÇAR OPERAR"
# ◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈

from flask import Flask, render_template_string, jsonify, request
from iqoptionapi.stable_api import IQ_Option
from datetime import datetime
import threading, time, sys, os, json, warnings, requests, uuid, base64

warnings.filterwarnings("ignore")
app = Flask(__name__)

import hashlib as _hl
import base64 as _b64

def _hash_email(email):
    return _hl.md5(email.encode()).hexdigest()[:12]

def _enc(s):
    return _b64.b64encode(s.encode()).decode()

def _dec(s):
    try:
        return _b64.b64decode(s).decode()
    except:
        return s

# ============= CONFIGURAÇÕES FIXAS =============

# ═══════════ FIREBASE HTTP REST ═══════════
FB_URL = "https://nexos-40654-default-rtdb.firebaseio.com"
print("✅ Firebase HTTP REST configurado!")
# ══════════════════════════════════════

MARTINGALE = 2
PAYOUT_PADRAO = 0.85
PERCENTUAL_BANCA = 15
DRIVE_PATH = "vsens_users"  # Não usado mais

# ⭐⭐⭐ CONFIGURAÇÃO DO MERCADO PAGO ⭐⭐⭐
# Carregar configurações do Mercado Pago
MERCADO_PAGO_ACCESS_TOKEN = os.environ.get("MP_ACCESS_TOKEN", "APP_USR-4548266140377032-050311-6589fc22b166e4cb2cfad0379b28dcdf-1059299796")
MERCADO_PAGO_PUBLIC_KEY = os.environ.get("MP_PUBLIC_KEY", "APP_USR-39e1950e-420d-479a-8125-902009ca3445")
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
        'id': 'skin_dark', 'nome': '🌑 TESLA DARK', 'desc': 'Particulas roxas flutuantes', 'preco_moedas': 6, 'categoria': 'basica', 'cor_fundo': '#000000', 'cor_panel': '#0a0a0a', 'cor_destaque': '#9933ff', 'cor_texto': '#ccc', 'cor_botao': 'linear-gradient(135deg,#4400aa,#9933ff)', 'cor_tab_ativa': '#9933ff', 'cor_header_bg': 'linear-gradient(135deg,#000000,#110022,#220044,#110022,#000000)', 'cor_header_borda': '#9933ff', 'header_extra': '<canvas id="darkCanvas" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none"></canvas>', 'css_extra': 'body{background:#000000!important}.header{border-color:#9933ff!important;box-shadow:0 0 40px rgba(153,51,255,0.3)}'
    },
    {
        'id': 'skin_neon', 'nome': '💜 TESLA NEON', 'desc': 'Brilho neon roxo pulsante', 'preco_moedas': 6, 'categoria': 'basica', 'cor_fundo': '#0a0015', 'cor_panel': '#150025', 'cor_destaque': '#cc00ff', 'cor_texto': '#e0c0ff', 'cor_botao': 'linear-gradient(135deg,#8800cc,#cc00ff)', 'cor_tab_ativa': '#cc00ff', 'cor_header_bg': 'linear-gradient(135deg,#0a0015,#150030,#200050,#150030,#0a0015)', 'cor_header_borda': '#cc00ff', 'header_extra': '<div class="neon-glow"></div>', 'css_extra': '.neon-glow{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:200px;height:200px;background:radial-gradient(circle,rgba(204,0,255,0.2) 0%,transparent 70%);border-radius:50%;z-index:0;animation:neonPulse 2s ease-in-out infinite;pointer-events:none}@keyframes neonPulse{0%,100%{transform:translate(-50%,-50%) scale(1);opacity:0.5}50%{transform:translate(-50%,-50%) scale(1.3);opacity:0.8}}body{background:#0a0015!important}.header{border-color:#cc00ff!important;box-shadow:0 0 30px rgba(204,0,255,0.4)}'
    },
    {
        'id': 'skin_matrix', 'nome': '🧬 TESLA MATRIX', 'desc': 'Chuva de caracteres verdes', 'preco_moedas': 12, 'categoria': 'lendaria', 'cor_fundo': '#000000', 'cor_panel': '#0a0a0a', 'cor_destaque': '#00ff00', 'cor_texto': '#00cc00', 'cor_botao': 'linear-gradient(135deg,#004400,#00ff00)', 'cor_tab_ativa': '#00ff00', 'cor_header_bg': 'linear-gradient(135deg,#000000,#001100,#003300,#001100,#000000)', 'cor_header_borda': '#00ff00', 'header_extra': '<canvas id="matrixCanvas" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none"></canvas>', 'css_extra': 'body{background:#000000!important}.header{border-color:#00ff00!important;box-shadow:0 0 30px rgba(0,255,0,0.4)}.terminal{color:#00ff00!important;font-family:monospace!important}'
    },
    {
        'id': 'skin_sakura', 'nome': '🌸 TESLA SAKURA', 'desc': 'Pétalas de cerejeira caindo', 'preco_moedas': 9, 'categoria': 'premium', 'cor_fundo': '#1a0a1a', 'cor_panel': '#2a0a2a', 'cor_destaque': '#ff69b4', 'cor_texto': '#ffe0f0', 'cor_botao': 'linear-gradient(135deg,#cc3388,#ff69b4)', 'cor_tab_ativa': '#ff69b4', 'cor_header_bg': 'linear-gradient(135deg,#1a0020,#330033,#4d004d,#330033,#1a0020)', 'cor_header_borda': '#ff69b4', 'header_extra': '<canvas id="sakuraCanvas" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none"></canvas>', 'css_extra': 'body{background:linear-gradient(180deg,#1a0a1a 0%,#0d001a 100%)!important}.header{border-color:#ff69b4!important;box-shadow:0 0 40px rgba(255,105,180,0.3)}'
    },
    {
        'id': 'skin_thunder', 'nome': '⚡ TESLA THUNDER', 'desc': 'Raios elétricos na tela', 'preco_moedas': 12, 'categoria': 'lendaria', 'cor_fundo': '#000011', 'cor_panel': '#0a0a1a', 'cor_destaque': '#ffff00', 'cor_texto': '#ffffff', 'cor_botao': 'linear-gradient(135deg,#aaaa00,#ffff00)', 'cor_tab_ativa': '#ffff00', 'cor_header_bg': 'linear-gradient(135deg,#000011,#111122,#222244,#111122,#000011)', 'cor_header_borda': '#ffff00', 'header_extra': '<canvas id="thunderCanvas" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none"></canvas>', 'css_extra': 'body{background:#000011!important}.header{border-color:#ffff00!important;box-shadow:0 0 50px rgba(255,255,0,0.3)}'
    },
    {
        'id': 'skin_ocean', 'nome': '🌊 TESLA OCEAN', 'desc': 'Ondas do mar em movimento', 'preco_moedas': 9, 'categoria': 'premium', 'cor_fundo': '#001020', 'cor_panel': '#0a1a2a', 'cor_destaque': '#00aacc', 'cor_texto': '#aaddff', 'cor_botao': 'linear-gradient(135deg,#006688,#00aacc)', 'cor_tab_ativa': '#00aacc', 'cor_header_bg': 'linear-gradient(135deg,#001020,#002040,#003060,#002040,#001020)', 'cor_header_borda': '#00aacc', 'header_extra': '<canvas id="oceanCanvas" style="position:absolute;bottom:0;left:0;width:100%;height:100px;z-index:0"></canvas>', 'css_extra': 'body{background:linear-gradient(180deg,#001020 0%,#000810 100%)!important}.header{border-color:#00aacc!important;box-shadow:0 0 30px rgba(0,170,204,0.3)}'
    },
    {
        'id': 'skin_sunset', 'nome': '🌅 TESLA SUNSET', 'desc': 'Ceu em degradê animado', 'preco_moedas': 9, 'categoria': 'premium', 'cor_fundo': '#1a0010', 'cor_panel': '#2a0a1a', 'cor_destaque': '#ff6600', 'cor_texto': '#ffddaa', 'cor_botao': 'linear-gradient(135deg,#cc4400,#ff8800)', 'cor_tab_ativa': '#ff6600', 'cor_header_bg': 'linear-gradient(135deg,#1a0000,#331100,#552200,#331100,#1a0000)', 'cor_header_borda': '#ff6600', 'header_extra': '<canvas id="sunsetCanvas" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none"></canvas>', 'css_extra': 'body{background:linear-gradient(180deg,#1a0010 0%,#331100 50%,#1a0000 100%)!important}.header{border-color:#ff6600!important;box-shadow:0 0 40px rgba(255,102,0,0.3)}'
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
        'id': 'skin_fire', 'nome': '🔥 TESLA FIRE', 'desc': 'Chamas realistas na base', 'preco_moedas': 9, 'categoria': 'premium', 'cor_fundo': '#1a0000', 'cor_panel': '#2a0a0a', 'cor_destaque': '#ff4400', 'cor_texto': '#ffccaa', 'cor_botao': 'linear-gradient(135deg,#cc2200,#ff6600)', 'cor_tab_ativa': '#ff4400', 'cor_header_bg': 'linear-gradient(135deg,#1a0000,#330000,#551100,#330000,#1a0000)', 'cor_header_borda': '#ff4400', 'header_extra': '<canvas id="fireCanvas" style="position:absolute;bottom:0;left:0;width:100%;height:80px;z-index:0"></canvas>', 'css_extra': 'body{background:radial-gradient(ellipse at bottom,#1a0000 0%,#000000 100%)!important}.header{border-color:#ff4400!important;box-shadow:0 0 30px rgba(255,68,0,0.4)}'
    },
    {
        'id': 'skin_ice', 'nome': '❄️ TESLA ICE', 'desc': 'Neve caindo com cristais', 'preco_moedas': 9, 'categoria': 'premium', 'cor_fundo': '#000a1a', 'cor_panel': '#0a102a', 'cor_destaque': '#3399ff', 'cor_texto': '#aaccff', 'cor_botao': 'linear-gradient(135deg,#0044aa,#3399ff)', 'cor_tab_ativa': '#3399ff', 'cor_header_bg': 'linear-gradient(135deg,#000a1a,#001133,#002255,#001133,#000a1a)', 'cor_header_borda': '#3399ff', 'header_extra': '<canvas id="snowCanvas" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none"></canvas>', 'css_extra': 'body{background:linear-gradient(180deg,#000a1a 0%,#001133 100%)!important}.header{border-color:#3399ff!important;box-shadow:0 0 40px rgba(51,153,255,0.3)}'
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

# ⭐ ESTRATÉGIAS (2 - COM PREÇOS) ⭐
ESTRATEGIAS = {
    'tesla_369': {
        'nome': '⚡ TESLA-369',
        'desc': '6 velas: padrão g-g-g-r-r → CALL / r-r-r-g-g → PUT',
        'timeframe': 60,
        'pares': ['EURUSD-OTC'],
        'preco_moedas': 0,
        'gratis': True,
        'fixa': True
    },
    'v_sensitivo': {
        'nome': '🔮 v_SENSITIVO',
        'desc': 'RSI + MM + Bollinger + MACD + Estocástico + Fase da Vela',
        'timeframe': 60,
        'pares': ['EURUSD-OTC'],
        'preco_moedas': 9,
        'gratis': False
    },
    'terceira_igual_primeira': {
        'nome': '3️⃣ 3ª = 1ª 🆓',
        'desc': 'Opera a cada 5min, seg 55+',
        'timeframe': 60,
        'pares': ['EURUSD-OTC'],
        'preco_moedas': 0,
        'gratis': True
    },
    'mhi_filtrado': {
        'nome': '📊 MHI-FILTRADO',
        'desc': '5 velas + Média Móvel + filtro de cor dominante',
        'timeframe': 60,
        'pares': ['EURUSD-OTC'],
        'preco_moedas': 9,
        'gratis': False
    },
    'quadrante_de_7': {
        'nome': '7️⃣ QUADRANTE DE 7',
        'desc': '7 velas + MM, conta cores',
        'timeframe': 60,
        'pares': ['EURUSD-OTC'],
        'preco_moedas': 6,
        'gratis': False
    },
    'fluxo_de_velas': {
        'nome': '🌊 FLUXO-DE-VELAS 🆓',
        'desc': '5 velas mesma cor + MM',
        'timeframe': 60,
        'pares': ['EURUSD-OTC'],
        'preco_moedas': 0,
        'gratis': True
    },
    'reversao': {
        'nome': '🔄 REVERSÃO',
        'desc': 'Padrão alternado g-r-g-r-g ou r-g-r-g-r',
        'timeframe': 60,
        'pares': ['EURUSD-OTC'],
        'preco_moedas': 3,
        'gratis': False
    },
    'm5': {
        'nome': '⏰ M5',
        'desc': 'Quadrante de velas de 5min',
        'timeframe': 300,
        'pares': ['EURUSD-OTC'],
        'preco_moedas': 6,
        'gratis': False
    }
}


def _sanitizar_dados(dados):
    """Limpa dados para Firebase"""
    if 'historico_operacoes' in dados:
        # Mantém apenas os últimos 50
        if len(dados['historico_operacoes']) > 50:
            dados['historico_operacoes'] = dados['historico_operacoes'][-50:]
        # Remove campos problemáticos
        for op in dados['historico_operacoes']:
            for chave in list(op.keys()):
                if isinstance(op[chave], float):
                    op[chave] = round(op[chave], 2)
    return dados

def salvar_usuario(email, dados):
    """Salva no Firebase (sem backup local)"""
    try:
        key = email.replace("@", "_").replace(".", "_").replace("#", "").replace("$", "").replace("[", "").replace("]", "").replace("/", "_")
        dados = _sanitizar_dados(dados)
        requests.put(f'{FB_URL}/tesla_369/usuarios/{key}.json', json=dados)
    except Exception as e:
        print(f"⚠️ Firebase offline: {e}")

def carregar_usuario(email):
    """Carrega do Firebase"""
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
        'moedas': 12,  # 12 moedas iniciais para TODOS
        'moedas_ganhas_hoje': str(datetime.now())[:10],
        'total_ciclos': 0, 'total_wins': 0, 'total_losses': 0,
        'total_gasto': 0.0, 'total_ganho': 0.0, 'lucro_total': 0.0,
        'banca_atual': 0.0, 'data_cadastro': str(datetime.now())[:19],
        'historico_operacoes': [],
        'dias_ativos': 0,
        'skin_atual': 'skin_padrao', 'skins_compradas': ['skin_padrao'],
        'estrategias_compradas': ['tesla_369']
    }
    salvar_usuario(email, dados)
    return dados

# ============= VARIÁVEIS GLOBAIS =============
API, par = None, "EURUSD-OTC"
estrategia_atual = 'tesla_369'
timeframe_atual = 60
lucro, NumDeOperacoes = 0.0, 0
BANCA_INICIAL_DO_BOT, STOP_GAIN_ATINGIDO = 0, False
bot_rodando, bot_thread = False, None
conectado_iq = False
ultimo_sinal, ultima_analise = "Aguardando...", {}
logs_web, MAX_LOGS_WEB = [], 200
email_usuario_atual = ""
skin_atual_global = 'skin_padrao'
pagamentos_pendentes = {}

# ============= SISTEMA MULTI-USUÁRIO =============
bots_ativos = {}  # {email: thread_do_bot}

def add_log(msg, tipo='info'):
    global logs_web
    t = datetime.now().strftime('%H:%M:%S')
    logs_web.append({'time': t, 'msg': msg, 'tipo': tipo})
    if len(logs_web) > MAX_LOGS_WEB: logs_web = logs_web[-MAX_LOGS_WEB:]
    print(f"{t} - {msg}")
    try: sys.stdout.flush()
    except: pass

def get_logs_html(limite=40):
    html = ''
    for log in logs_web[-limite:]:
        cor = {'win': '#00ff88', 'loss': '#ff4444', 'info': '#00ff88', 'sensitive': '#ff69b4', 'indicator': '#ffd700', 'error': '#ff4444'}.get(log['tipo'], '#00ff88')
        html += f'<span style="color:#666">{log["time"]}</span> <span style="color:{cor}">{log["msg"]}</span>\n'
    return html or '📡 Aguardando...'

def conectar_api():
    while bot_rodando:
        try:
            if API.check_connect(): return True
        except: pass
        add_log('⏳ Reconectando...', 'warning'); time.sleep(5)
        try: API.connect()
        except: pass

def Payout(p):
    try:
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
    except: return PAYOUT_PADRAO

# ═══════════════════════════════════════════════════════
# INDICADORES
# ═══════════════════════════════════════════════════════
def sma(v, p):
    if len(v) < p: return None
    return round(sum(x['close'] for x in v[-p:]) / p, 6)

def bollinger(v, p=20, d=2):
    if len(v) < p: return None, None, None
    c = [x['close'] for x in v[-p:]]; m = sum(c) / p
    dp = (sum((x-m)**2 for x in c) / p) ** 0.5
    return round(m+d*dp, 6), round(m, 6), round(m-d*dp, 6)

def rsi(v, p=9):
    if len(v) < p+1: return None
    g, l = [], []
    for i in range(1, len(v)):
        d = v[i]['close'] - v[i-1]['close']
        g.append(d if d > 0 else 0); l.append(abs(d) if d < 0 else 0)
    if sum(l) == 0: return 100
    return round(100 - (100 / (1 + sum(g) / sum(l))), 2)

def macd(v, r=12, l=26):
    if len(v) < l: return None
    c = [x['close'] for x in v]; er = c[0]; el = c[0]
    for x in c[1:]:
        er = x*(2/(r+1)) + er*(1-2/(r+1))
        el = x*(2/(l+1)) + el*(1-2/(l+1))
    return round(er-el, 8)

def estocastico(v, p=14):
    if len(v) < p: return None
    c = [x['close'] for x in v]
    h = [max(x['open'], x['close']) for x in v]
    l = [min(x['open'], x['close']) for x in v]
    hh, ll = max(h[-p:]), min(l[-p:])
    if hh == ll: return 50
    return round(((c[-1]-ll)/(hh-ll))*100, 2)

# ═══════════════════════════════════════════════════════
# SINAIS DAS ESTRATÉGIAS
# ═══════════════════════════════════════════════════════
def sinal_v_sensitivo():
    global ultimo_sinal, ultima_analise
    try:
        s = datetime.now().second
        fase = "🌅NASCENDO" if s < 20 else ("☀️VIVA" if s < 45 else "🌇MORRENDO")
        v = API.get_candles(par, timeframe_atual, 30, time.time())
        if len(v) < 20: return None
        rs = rsi(v); m5 = sma(v, 5); m10 = sma(v, 10); m20 = sma(v, 20)
        bs, _, bi = bollinger(v); mc = macd(v); st = estocastico(v); pc = v[-1]['close']
        ultima_analise = {'preco': pc, 'rsi': rs, 'mm5': m5, 'mm10': m10, 'mm20': m20, 'stoch': st, 'fase': fase}
        sc = sp = 0; sinais = []
        if m5 and m20:
            if m5 > m20: sc += 20; sinais.append("MM5>MM20")
            else: sp += 20; sinais.append("MM5<MM20")
        if m5 and m10:
            if m5 > m10: sc += 15; sinais.append("MM5>MM10")
            else: sp += 15; sinais.append("MM5<MM10")
        if rs:
            if rs < 30: sc += 25; sinais.append(f"RSI={rs:.0f}↓")
            elif rs > 70: sp += 25; sinais.append(f"RSI={rs:.0f}↑")
            elif rs > 50: sc += 10
            else: sp += 10
        if bs and bi and pc:
            if pc <= bi*1.01: sc += 20; sinais.append("BB↓")
            elif pc >= bs*0.99: sp += 20; sinais.append("BB↑")
        if mc:
            if mc > 0: sc += 15; sinais.append("MACD+")
            else: sp += 15; sinais.append("MACD-")
        if st:
            if st < 20: sc += 15; sinais.append(f"E={st:.0f}↓")
            elif st > 80: sp += 15; sinais.append(f"E={st:.0f}↑")
        if fase == "🌇MORRENDO":
            cor = 'V' if v[-1]['open'] < v[-1]['close'] else 'R'
            if cor == 'V': sp += 10
            else: sc += 10
        add_log(f"🔮{fase} | C={sc} P={sp} | {' '.join(sinais[:3])}", 'indicator')
        dif = abs(sc-sp)
        if sc > sp and dif >= 15:
            ultimo_sinal = f"🔮 CALL ({sc}x{sp})"; add_log(f"CALL!", 'sensitive'); return 'call'
        if sp > sc and dif >= 15:
            ultimo_sinal = f"🔮 PUT ({sp}x{sc})"; add_log(f"PUT!", 'sensitive'); return 'put'
        ultimo_sinal = "⏳..."; return None
    except Exception as e: add_log(f"Erro: {e}", 'error'); return None

def sinal_tesla_369():
    global ultimo_sinal, ultima_analise
    try:
        agora = datetime.now()
        if not ((agora.minute >= 1.55 and agora.minute <= 2) or (agora.minute >= 6.55 and agora.minute <= 7)):
            ultimo_sinal = f"⏳ Min: {agora.minute}:{agora.second:02d}"; return None
        v = API.get_candles(par, timeframe_atual, 6, time.time())
        if len(v) < 6: return None
        velas = []
        for vela in v:
            if vela['open'] < vela['close']: velas.append('g')
            elif vela['open'] > vela['close']: velas.append('r')
            else: velas.append('d')
        cores = ''.join(velas); pc = v[-1]['close']
        ultima_analise = {'preco': pc, 'rsi': None, 'mm5': None, 'mm10': None, 'mm20': None, 'stoch': None, 'fase': 'TESLA-369'}
        add_log(f"⚡ TESLA-369 | Velas: {cores}", 'indicator'); ultimo_sinal = f"⚡ 369: {cores}"
        if velas[0] == 'g' and velas[3] == 'g' and velas[4] == 'r' and velas[5] == 'r' and 'd' not in cores:
            add_log("TESLA-369: CALL!", 'sensitive'); return 'call'
        if velas[0] == 'r' and velas[3] == 'r' and velas[4] == 'g' and velas[5] == 'g' and 'd' not in cores:
            add_log("TESLA-369: PUT!", 'sensitive'); return 'put'
        ultimo_sinal = "⏳..."; return None
    except Exception as e: add_log(f"Erro: {e}", 'error'); return None

def sinal_mhi_filtrado():
    global ultimo_sinal, ultima_analise
    try:
        agora = datetime.now()
        if not ((agora.minute >= 4.55 and agora.minute <= 5) or (agora.minute >= 9.55 and agora.minute <= 10)):
            ultimo_sinal = f"⏳ MHI: {agora.minute}:{agora.second:02d}"; return None
        v = API.get_candles(par, timeframe_atual, 22, time.time())
        if len(v) < 22: return None
        velas = []
        for vela in v[-5:]:
            if vela['open'] < vela['close']: velas.append('g')
            elif vela['open'] > vela['close']: velas.append('r')
            else: velas.append('d')
        cores = ''.join(velas); preco_atual = v[-1]['close']; mm = sum(c['close'] for c in v[:-1]) / 21
        ultima_analise = {'preco': preco_atual, 'rsi': None, 'mm5': None, 'mm10': None, 'mm20': round(mm, 6), 'stoch': None, 'fase': 'MHI-FILTRADO'}
        add_log(f"📊 MHI | Velas: {cores} | MM: {mm:.5f}", 'indicator')
        if preco_atual > mm and cores.count('r') > cores.count('g') and 'd' not in cores and velas[4] == 'r':
            ultimo_sinal = "📊 CALL (MHI)"; add_log("MHI: CALL!", 'sensitive'); return 'call'
        if preco_atual < mm and cores.count('r') < cores.count('g') and 'd' not in cores and velas[4] == 'g':
            ultimo_sinal = "📊 PUT (MHI)"; add_log("MHI: PUT!", 'sensitive'); return 'put'
        ultimo_sinal = "⏳..."; return None
    except Exception as e: add_log(f"Erro: {e}", 'error'); return None

def sinal_terceira_igual_primeira():
    global ultimo_sinal, ultima_analise
    try:
        agora = datetime.now()
        if agora.minute % 5 != 0: ultimo_sinal = f"⏳ Min: {agora.minute} (5/10/15...)"; return None
        if agora.second < 55: ultimo_sinal = f"⏳ Seg: {agora.second}s (aguardando 55)"; return None
        time.sleep(2)
        v = API.get_candles(par, timeframe_atual, 22, time.time())
        if len(v) < 22: return None
        vela_atual = 'g' if v[-1]['open'] < v[-1]['close'] else ('r' if v[-1]['open'] > v[-1]['close'] else 'd')
        preco_atual = v[-1]['close']; mm = sum(c['close'] for c in v[:-1]) / 21
        ultima_analise = {'preco': preco_atual, 'rsi': None, 'mm5': None, 'mm10': None, 'mm20': round(mm, 6), 'stoch': None, 'fase': '3ª=1ª'}
        add_log(f"3️⃣ 3=1 | Vela: {vela_atual} | MM: {mm:.5f}", 'indicator')
        if preco_atual > mm and vela_atual == 'g': ultimo_sinal = "3️⃣ CALL (3=1)"; add_log("3ª=1ª: CALL!", 'sensitive'); return 'call'
        if preco_atual < mm and vela_atual == 'r': ultimo_sinal = "3️⃣ PUT (3=1)"; add_log("3ª=1ª: PUT!", 'sensitive'); return 'put'
        ultimo_sinal = "⏳..."; return None
    except Exception as e: add_log(f"Erro: {e}", 'error'); return None

def sinal_quadrante_de_7():
    global ultimo_sinal, ultima_analise
    try:
        agora = datetime.now()
        if not ((agora.minute >= 1.55 and agora.minute <= 2) or (agora.minute >= 6.55 and agora.minute <= 7)):
            ultimo_sinal = f"⏳ Q7: {agora.minute}:{agora.second:02d}"; return None
        v = API.get_candles(par, timeframe_atual, 22, time.time())
        if len(v) < 22: return None
        velas = []
        for vela in v[-7:]:
            if vela['open'] < vela['close']: velas.append('g')
            elif vela['open'] > vela['close']: velas.append('r')
            else: velas.append('d')
        cores = ''.join(velas); preco_atual = v[-1]['close']; mm = sum(c['close'] for c in v[:-1]) / 21
        ultima_analise = {'preco': preco_atual, 'rsi': None, 'mm5': None, 'mm10': None, 'mm20': round(mm, 6), 'stoch': None, 'fase': 'QUADRANTE-7'}
        add_log(f"7️⃣ Q7 | Velas: {cores}", 'indicator')
        if preco_atual > mm and cores.count('g') < cores.count('r') and 'd' not in cores:
            ultimo_sinal = "7️⃣ CALL (Q7)"; add_log("Q7: CALL!", 'sensitive'); return 'call'
        if preco_atual < mm and cores.count('g') > cores.count('r') and 'd' not in cores:
            ultimo_sinal = "7️⃣ PUT (Q7)"; add_log("Q7: PUT!", 'sensitive'); return 'put'
        ultimo_sinal = "⏳..."; return None
    except Exception as e: add_log(f"Erro: {e}", 'error'); return None

def sinal_fluxo_de_velas():
    global ultimo_sinal, ultima_analise
    try:
        agora = datetime.now()
        if agora.second % 55 != 0: return None
        v = API.get_candles(par, timeframe_atual, 22, time.time())
        if len(v) < 22: return None
        velas = []
        for vela in v[-5:]:
            if vela['open'] < vela['close']: velas.append('g')
            elif vela['open'] > vela['close']: velas.append('r')
            else: velas.append('d')
        cores = ''.join(velas); preco_atual = v[-1]['close']; mm = sum(c['close'] for c in v[:-1]) / 21
        ultima_analise = {'preco': preco_atual, 'rsi': None, 'mm5': None, 'mm10': None, 'mm20': round(mm, 6), 'stoch': None, 'fase': 'FLUXO'}
        add_log(f"🌊 FLUXO | Velas: {cores}", 'indicator')
        if preco_atual > mm and cores == 'ggggg' and 'd' not in cores:
            ultimo_sinal = "🌊 CALL (FLUXO)"; add_log("FLUXO: CALL!", 'sensitive'); return 'call'
        if preco_atual < mm and cores == 'rrrrr' and 'd' not in cores:
            ultimo_sinal = "🌊 PUT (FLUXO)"; add_log("FLUXO: PUT!", 'sensitive'); return 'put'
        ultimo_sinal = "⏳..."; return None
    except Exception as e: add_log(f"Erro: {e}", 'error'); return None

def sinal_reversao():
    global ultimo_sinal, ultima_analise
    try:
        agora = datetime.now()
        if agora.second % 55 != 0: return None
        v = API.get_candles(par, timeframe_atual, 22, time.time())
        if len(v) < 22: return None
        velas = []
        for vela in v[-5:]:
            if vela['open'] < vela['close']: velas.append('g')
            elif vela['open'] > vela['close']: velas.append('r')
            else: velas.append('d')
        cores = ''.join(velas); preco_atual = v[-1]['close']; mm = sum(c['close'] for c in v[:-1]) / 21
        ultima_analise = {'preco': preco_atual, 'rsi': None, 'mm5': None, 'mm10': None, 'mm20': round(mm, 6), 'stoch': None, 'fase': 'REVERSÃO'}
        add_log(f"🔄 REV | Velas: {cores}", 'indicator')
        if preco_atual > mm and cores == 'grgrg':
            ultimo_sinal = "🔄 CALL (REV)"; add_log("REVERSÃO: CALL!", 'sensitive'); return 'call'
        if preco_atual < mm and cores == 'rgrgr':
            ultimo_sinal = "🔄 PUT (REV)"; add_log("REVERSÃO: PUT!", 'sensitive'); return 'put'
        ultimo_sinal = "⏳..."; return None
    except Exception as e: add_log(f"Erro: {e}", 'error'); return None

def sinal_m5():
    global ultimo_sinal, ultima_analise
    try:
        agora = datetime.now()
        if agora.minute % 15 != 0: ultimo_sinal = f"⏳ M5: min {agora.minute} (15/30/45/0)"; return None
        time.sleep(2)
        v = API.get_candles(par, timeframe_atual, 7, time.time())
        if len(v) < 7: return None
        velas = []
        for vela in v:
            if vela['open'] < vela['close']: velas.append('g')
            elif vela['open'] > vela['close']: velas.append('r')
            else: velas.append('d')
        pc = v[-1]['close']
        ultima_analise = {'preco': pc, 'rsi': None, 'mm5': None, 'mm10': None, 'mm20': None, 'stoch': None, 'fase': 'M5'}
        add_log(f"⏰ M5 | Velas: {''.join(velas)}", 'indicator')
        if velas[0] == velas[1] and velas[1] == velas[2] and velas[3] == velas[4] and velas[4] == velas[5]:
            if velas[6] == 'g' and 'd' not in velas: ultimo_sinal = "⏰ PUT (M5)"; add_log("M5: PUT!", 'sensitive'); return 'put'
            if velas[6] == 'r' and 'd' not in velas: ultimo_sinal = "⏰ CALL (M5)"; add_log("M5: CALL!", 'sensitive'); return 'call'
        ultimo_sinal = "⏳ Sem sinal M5"; return None
    except Exception as e: add_log(f"Erro: {e}", 'error'); return None

MAPA_SINAIS = {
    'v_sensitivo': sinal_v_sensitivo,
    'tesla_369': sinal_tesla_369,
    'terceira_igual_primeira': sinal_terceira_igual_primeira,
    'mhi_filtrado': sinal_mhi_filtrado,
    'quadrante_de_7': sinal_quadrante_de_7,
    'fluxo_de_velas': sinal_fluxo_de_velas,
    'reversao': sinal_reversao,
    'm5': sinal_m5
}

@app.route('/set_percentual', methods=['POST'])
def set_percentual():
    global PERCENTUAL_BANCA
    data = request.json
    PERCENTUAL_BANCA = data.get('percentual', 10)
    return jsonify({'ok': True})

# ═══════════════════════════════════════════════════════
# CÁLCULO DE ENTRADAS
# ═══════════════════════════════════════════════════════
def calcular_entradas(b, p, g):
    global PERCENTUAL_BANCA
    bs = (b * PERCENTUAL_BANCA / 100) * 0.99; e0 = bs / sum((1/p)**i for i in range(g+1))
    entradas = [e0]
    for i in range(1, g+1): entradas.append((sum(entradas)+e0)/p)
    ajuste = bs / sum(entradas); entradas = [round(e*ajuste, 2) for e in entradas]
    soma = sum(entradas)
    if soma > b: entradas[-1] = round(entradas[-1] - (soma-b) - 0.02, 2)
    return [max(1, e) for e in entradas]

def pegar_timestamp():
    v = API.get_candles(par, timeframe_atual, 1, time.time())
    return v[0]['from'] if v else 0

def aguardar_inicio_vela():
    add_log("   ⏳ Aguardando início da vela...", 'info')
    while datetime.now().second > 5:
        if not bot_rodando: return False
        time.sleep(0.3)
    while True:
        if not bot_rodando: return False
        ts1 = pegar_timestamp(); time.sleep(0.5); ts2 = pegar_timestamp()
        if ts1 == ts2: add_log("   ✅ Vela confirmada!", 'info'); return True

def aguardar_vela_fechar(ts_entrada):
    add_log(f"   ⏳ Aguardando vela fechar...", 'info')
    while True:
        if not bot_rodando: return False
        try:
            if pegar_timestamp() != ts_entrada: add_log("   ✅ Vela fechou!", 'info'); return True
        except: pass
        time.sleep(0.3)

def verificar_resultado(saldo_antes, valor):
    saldo_base = saldo_antes - valor
    try:
        s = API.get_balance(); d = round(s-saldo_base, 2)
        if d >= 1.0: return d
    except: pass
    return -valor

def executar_ciclo(direcao):
    global lucro, NumDeOperacoes, STOP_GAIN_ATINGIDO, bot_rodando
    bi = API.get_balance()
    payout = Payout(par)
    entradas = calcular_entradas(bi, payout, MARTINGALE)
    add_log(f"💰 Banca: ${bi:.2f} | Payout: {payout*100:.0f}%", 'info')
    add_log(f"📐 E1:${entradas[0]:.2f} | E2:${entradas[1]:.2f} | E3:${entradas[2]:.2f}", 'info')
    for i in range(MARTINGALE + 1):
        if not bot_rodando: break
        valor = entradas[i]
        if not aguardar_inicio_vela(): break
        saldo_antes = API.get_balance()
        if saldo_antes < valor:
            add_log("❌ Saldo insuficiente!", 'error')
            break
        print()
        add_log(f"🎯 {'ENTRADA' if i == 0 else f'GALE {i}'}: {direcao.upper()} ${valor:.2f}", 'info')
        st, id_ordem = API.buy(valor, par, direcao, 1)
        if not st or not id_ordem:
            try: st, id_ordem = API.buy_digital_spot(par, valor, direcao, 1)
            except: pass
        if not st or not id_ordem:
            add_log("❌ Falha na ordem!", 'error')
            break
        add_log(f"   📝 Ordem #{id_ordem}", 'info')
        time.sleep(0.3)
        ts_real = pegar_timestamp()
        if not aguardar_vela_fechar(ts_real): break
        res = verificar_resultado(saldo_antes, valor)
        lucro += round(res, 2)
        saldo_depois = API.get_balance()
        lucro_liquido = round(saldo_depois - saldo_antes, 2)
        if res > 0:
            add_log(f"🌟 WIN! +${lucro_liquido:.2f}", 'win')
            NumDeOperacoes += 1
            u = carregar_usuario(email_usuario_atual)
            if u:
                u['total_wins'] += 1; u['total_ganho'] += abs(lucro_liquido)
                u['lucro_total'] = u['total_ganho'] - u['total_gasto']
                u['banca_atual'] = round(saldo_depois, 2)
                u.setdefault('historico_operacoes', []).append({'data': str(datetime.now())[:19], 'resultado': 'WIN', 'valor': valor, 'lucro': lucro_liquido, 'estrategia': estrategia_atual})
                u['dias_ativos'] = u.get('dias_ativos', 0) + 1
                salvar_usuario(email_usuario_atual, u)
            STOP_GAIN_ATINGIDO = True
            add_log("🎯 STOP GAIN! Vitória alcançada - Bot PARADO!", 'win')
            break
        else:
            add_log(f"💀 LOSS! -${valor:.2f}", 'loss')
            u = carregar_usuario(email_usuario_atual)
            if u:
                u['total_losses'] += 1; u['total_gasto'] += valor
                u['lucro_total'] = u['total_ganho'] - u['total_gasto']
                u['banca_atual'] = round(saldo_depois, 2)
                u.setdefault('historico_operacoes', []).append({'data': str(datetime.now())[:19], 'resultado': 'LOSS', 'valor': valor, 'lucro': -valor, 'estrategia': estrategia_atual})
                u['dias_ativos'] = u.get('dias_ativos', 0) + 1
                salvar_usuario(email_usuario_atual, u)
            if i < MARTINGALE: add_log(f"   ➡️ Indo para GALE {i + 1}...", 'loss')
            else: add_log("   💀 CICLO COMPLETO PERDIDO! Bot PARADO!", 'loss')
    bf = API.get_balance()
    print()
    add_log("=" * 50, 'info')
    add_log(f"{'🌟 LUCRO' if bf > bi else '💀 PERDA'}: ${abs(bf - bi):.2f} | Banca: ${bf:.2f}", 'info')
    add_log("=" * 50, 'info')
    bot_rodando = False
    add_log("⏹️ Ciclo concluído! Clique em CONECTAR e depois COMEÇAR OPERAR para novo ciclo.", 'info')

def bot_loop():
    global bot_rodando, BANCA_INICIAL_DO_BOT, lucro, NumDeOperacoes, STOP_GAIN_ATINGIDO
    nome_est = ESTRATEGIAS.get(estrategia_atual, ESTRATEGIAS['v_sensitivo'])['nome']
    add_log(f'⚡ TESLA 369 - INICIANDO...', 'sensitive')
    add_log(f'📊 Estratégia: {nome_est}', 'info')
    BANCA_INICIAL_DO_BOT = API.get_balance()
    STOP_GAIN_ATINGIDO = False; lucro = 0.0; NumDeOperacoes = 0
    add_log(f"📌 {par} | Timeframe: {timeframe_atual}s | 💰 ${BANCA_INICIAL_DO_BOT:.2f}")
    add_log('🧿 SIGILOS ATIVADOS 🧿', 'win')
    add_log('🔮 Buscando sinal...', 'info')
    funcao_sinal = MAPA_SINAIS.get(estrategia_atual, sinal_v_sensitivo)
    while bot_rodando and not STOP_GAIN_ATINGIDO:
        try:
            direcao = funcao_sinal()
            if direcao: executar_ciclo(direcao); break
            time.sleep(0.3)
        except Exception as e: add_log(f"Erro: {e}", 'error'); time.sleep(5); conectar_api()
    if not bot_rodando: add_log("⏹️ Bot parado.", 'info')

# ═══════════════════════════════════════════════════════
# FUNÇÕES DO MERCADO PAGO
# ═══════════════════════════════════════════════════════
def gerar_pix_mercadopago(email, plano):
    if MODO_SIMULACAO:
        pix_id = str(uuid.uuid4())[:8]
        pagamentos_pendentes[pix_id] = {'email': email, 'plano_id': plano['id'], 'moedas': plano['moedas'], 'valor': plano['preco'], 'pago': False, 'criado_em': str(datetime.now())[:19]}
        return {'sucesso': True, 'simulacao': True, 'pix_id': pix_id, 'qr_code': f"[SIMULAÇÃO] PIX de R$ {plano['preco']:.2f} - ID: {pix_id}", 'qr_code_base64': '', 'valor': plano['preco'], 'moedas': plano['moedas']}
    try:
        url = "https://api.mercadopago.com/v1/payments"
        headers = {"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}", "Content-Type": "application/json", "X-Idempotency-Key": str(uuid.uuid4())}
        payment_data = {"transaction_amount": float(plano['preco']), "description": f"TESLA369 - {plano['nome']} - {plano['moedas']} moedas", "payment_method_id": "pix", "payer": {"email": email, "first_name": "Cliente", "last_name": "Tesla369"}}
        response = requests.post(url, json=payment_data, headers=headers)
        data = response.json()
        if response.status_code in [200, 201]:
            pix_id = str(data['id']); qr_code = data['point_of_interaction']['transaction_data']['qr_code']; qr_code_base64 = data['point_of_interaction']['transaction_data']['qr_code_base64']
            pagamentos_pendentes[pix_id] = {'email': email, 'plano_id': plano['id'], 'moedas': plano['moedas'], 'valor': plano['preco'], 'pago': False, 'criado_em': str(datetime.now())[:19]}
            return {'sucesso': True, 'simulacao': False, 'pix_id': pix_id, 'qr_code': qr_code, 'qr_code_base64': qr_code_base64, 'valor': plano['preco'], 'moedas': plano['moedas']}
        return {'sucesso': False, 'erro': data.get('message', 'Erro ao gerar PIX')}
    except Exception as e: return {'sucesso': False, 'erro': str(e)}

def verificar_pagamento_mp(pix_id):
    if MODO_SIMULACAO: return pagamentos_pendentes.get(pix_id, {}).get('pago', False)
    try:
        url = f"https://api.mercadopago.com/v1/payments/{pix_id}"
        headers = {"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}"}
        return requests.get(url, headers=headers).json().get('status') == 'approved'
    except: return False

def verificador_automatico_pix():
    # Verificador PIX silencioso
    while True:
        time.sleep(10)
        try:
            pendentes = {k: v for k, v in pagamentos_pendentes.items() if not v.get('pago', False)}
            for pix_id, dados in list(pendentes.items()):
                if verificar_pagamento_mp(pix_id):
                    pagamentos_pendentes[pix_id]['pago'] = True
                    email = dados['email']; moedas = dados['moedas']
                    usuario = carregar_usuario(email) or criar_usuario(email)
                    usuario['moedas'] = usuario.get('moedas', 0) + moedas
                    salvar_usuario(email, usuario)
                    add_log(f"✅ PIX {pix_id[:8]}... pago! +{moedas} VOLTS para {email}", "win")
        except: pass

threading.Thread(target=verificador_automatico_pix, daemon=True).start()

# ═══════════════════════════════════════════════════════
# ROTA PARA COMPRAR ESTRATÉGIA
# ═══════════════════════════════════════════════════════
@app.route('/comprar_estrategia', methods=['POST'])
def comprar_estrategia():
    data = request.json
    estrategia_id = data.get('estrategia_id', '')
    
    if not email_usuario_atual:
        return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    
    if estrategia_id not in ESTRATEGIAS:
        return jsonify({'ok': False, 'erro': 'Estratégia inválida!'})
    
    estrategia = ESTRATEGIAS[estrategia_id]
    
    u = carregar_usuario(email_usuario_atual)
    if not u:
        u = criar_usuario(email_usuario_atual)
    
    if estrategia.get('gratis', False):
        if 'estrategias_compradas' not in u:
            u['estrategias_compradas'] = []
        if estrategia_id not in u['estrategias_compradas']:
            u['estrategias_compradas'].append(estrategia_id)
            salvar_usuario(email_usuario_atual, u)
        return jsonify({'ok': True, 'msg': f'Estratégia {estrategia["nome"]} ativada gratuitamente!', 'moedas': u.get('moedas', 0)})
    if not u:
        u = criar_usuario(email_usuario_atual)
    
    if estrategia_id in u.get('estrategias_compradas', []):
        return jsonify({'ok': False, 'erro': 'Estratégia já comprada!'})
    
    preco = estrategia.get('preco_moedas', 3)
    if u['moedas'] < preco:
        return jsonify({'ok': False, 'erro': f'VOLTS insuficientes! Precisa de {preco} ⚡'})
    
    u['moedas'] -= preco
    if 'estrategias_compradas' not in u:
        u['estrategias_compradas'] = ['tesla_369']
    u['estrategias_compradas'].append(estrategia_id)
    salvar_usuario(email_usuario_atual, u)
    
    return jsonify({'ok': True, 'msg': f'Estratégia {estrategia["nome"]} comprada!', 'moedas': u['moedas']})


# ═══════════════════════════════════════════════════════
# ROTAS DO CHAT
# ═══════════════════════════════════════════════════════
import hashlib as _hl2

@app.route('/chat_enviar', methods=['POST'])
def chat_enviar():
    data = request.json
    nome = data.get('nome', 'Anonimo')[:15]
    msg = data.get('msg', '')[:200]
    if not msg: return jsonify({'ok': False})
    try:
        # Envia mensagem
        requests.post(f'{FB_URL}/tesla_369/chat.json', json={'nome': nome, 'msg': msg, 'hora': datetime.now().strftime('%H:%M')})
        # Limpa chat antigo (mantém só 50)
        try:
            r_chat = requests.get(f'{FB_URL}/tesla_369/chat.json?orderBy="$key"&limitToLast=51')
            if r_chat.status_code == 200 and r_chat.json():
                dados = r_chat.json()
                if len(dados) > 50:
                    chaves = sorted(dados.keys())[:-50]
                    for chave in chaves:
                        requests.delete(f'{FB_URL}/tesla_369/chat/{chave}.json')
        except:
            pass
    except: pass
    return jsonify({'ok': True})

@app.route('/chat_mensagens')
def chat_mensagens_route():
    try:
        r = requests.get(f'{FB_URL}/tesla_369/chat.json?orderBy="$key"&limitToLast=50')
        mensagens = list(r.json().values()) if r.status_code == 200 and r.json() else []
        return jsonify({'mensagens': mensagens, 'online': 1})
    except:
        return jsonify({'mensagens': [], 'online': 1})

# ═══════════════════════════════════════════════════════
# HTML COMPLETO
# ═══════════════════════════════════════════════════════
HTML = r'''<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>⚡ TESLA 369 BOT v7.0.0</title><style>*{margin:0;padding:0;box-sizing:border-box}body{background:{{COR_FUNDO}};color:{{COR_TEXTO}};font-family:monospace;padding:10px}.container{max-width:950px;margin:0 auto}.tabs{display:flex;gap:5px;margin-bottom:10px;flex-wrap:wrap}.tab{padding:10px 14px;background:{{COR_PANEL}};border:1px solid #333;border-radius:10px 10px 0 0;cursor:pointer;color:#888;font-size:10px}.tab.active{background:{{COR_TAB_ATIVA}};color:#000;font-weight:bold}.panel{display:none;background:{{COR_PANEL}};padding:15px;border-radius:0 10px 10px 10px;border:1px solid #333;margin-bottom:10px}.panel.active{display:block}.header{background:{{COR_HEADER_BG}};padding:20px;border-radius:20px;text-align:center;border:3px solid {{COR_HEADER_BORDA}};position:relative;overflow:hidden;margin-bottom:15px}{{CSS_EXTRA}}.header h1{color:{{COR_DESTAQUE}};font-size:22px;text-shadow:0 0 30px {{COR_TAB_ATIVA}};position:relative;z-index:3}.mantra{color:{{COR_DESTAQUE}};text-align:center;margin:8px 0;font-size:10px}.config-section{margin-bottom:12px}.config-section h3{color:{{COR_DESTAQUE}};margin-bottom:8px;font-size:13px;border-bottom:1px solid #333;padding-bottom:5px}.config-row{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:8px}.config-row select,.config-row input{padding:8px;background:#111;border:1px solid #333;border-radius:8px;color:#fff;font-size:11px;font-family:monospace}.btn{padding:10px 14px;border:none;border-radius:8px;font-weight:bold;cursor:pointer;font-size:11px;font-family:monospace}.btn-start{background:{{COR_BOTAO}};color:#000}.btn-stop{background:linear-gradient(135deg,#c00,#f44);color:#fff}.btn-info{background:linear-gradient(135deg,#06c,#39f);color:#fff;font-size:11px;padding:8px 14px}.dashboard{display:grid;grid-template-columns:repeat(auto-fit,minmax(105px,1fr));gap:8px;margin-bottom:10px}.card{background:{{COR_PANEL}};padding:10px;border-radius:10px;border:1px solid #333;text-align:center}.card .label{color:#888;font-size:9px}.card .value{color:{{COR_DESTAQUE}};font-size:14px;font-weight:bold;margin-top:4px}.indicators{display:grid;grid-template-columns:repeat(auto-fit,minmax(80px,1fr));gap:6px;margin-bottom:10px}.ind-card{background:#111;padding:6px;border-radius:8px;border:1px solid #222;text-align:center;font-size:10px}.ind-card .ind-label{color:#666;font-size:9px}.ind-card .ind-value{color:{{COR_DESTAQUE}};font-size:11px}.terminal{background:#000;color:#0f8;padding:12px;border-radius:10px;height:200px;overflow-y:auto;font-size:10px;line-height:1.4;white-space:pre-wrap;border:1px solid #333;position:relative;overflow:hidden}.barra-status{display:flex;justify-content:space-between;padding:8px;background:{{COR_PANEL}};border-radius:10px;margin-top:10px;font-size:10px}.status-dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:4px}.status-dot.active{background:#0f8;animation:pulse 1s infinite}.status-dot.inactive{background:#888}@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.3}}.planos-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}.plano-card{background:#111;padding:12px;border-radius:10px;border:2px solid #222;text-align:center;cursor:pointer;transition:all 0.3s}.plano-card:hover{border-color:{{COR_DESTAQUE}};background:#1a1a2e}.plano-card.selecionado{border-color:#ffd700!important;box-shadow:0 0 20px rgba(255,215,0,0.4)}.plano-moedas{font-size:20px;color:{{COR_DESTAQUE}};font-weight:bold}.plano-preco{font-size:14px;color:#0f8;margin:5px 0}.plano-desc{font-size:9px;color:#888;margin-top:4px}.modal-overlay{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.85);z-index:1000;justify-content:center;align-items:center}.modal-overlay.active{display:flex}.modal-pagamento{background:{{COR_PANEL}};border:2px solid {{COR_DESTAQUE}};border-radius:15px;padding:25px;max-width:400px;width:90%;text-align:center}.btn-fechar{background:#444;color:#fff;padding:8px 20px;border-radius:8px;cursor:pointer;margin-top:10px;border:none;font-family:monospace}.btn-confirmar{background:{{COR_DESTAQUE}};color:#000;padding:8px 20px;border-radius:8px;cursor:pointer;margin-top:10px;font-weight:bold;border:none;font-family:monospace}.relatorio-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:6px}.relatorio-card{background:#111;padding:8px;border-radius:8px;border:1px solid #222;text-align:center}.relatorio-card .rlabel{color:#666;font-size:9px}.relatorio-card .rvalue{color:{{COR_DESTAQUE}};font-size:14px;font-weight:bold}.historico-table{width:100%;font-size:9px;border-collapse:collapse;margin-top:10px}.historico-table th{background:{{COR_TAB_ATIVA}};color:#000;padding:4px}.historico-table td{padding:3px;border-bottom:1px solid #222;text-align:center}.estrategia-card{background:#111;padding:12px;border-radius:10px;border:2px solid #222;cursor:pointer;transition:all 0.3s;text-align:center}.estrategia-card:hover{border-color:{{COR_DESTAQUE}}}.estrategia-card.ativa{border-color:#0f8;box-shadow:0 0 15px rgba(0,255,136,0.3);background:#0a1a0a}.estrategia-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:8px}.badge-gratis{background:#0f8;color:#000;font-size:9px;padding:2px 6px;border-radius:10px;display:inline-block}.badge-pago{background:#ffd700;color:#000;font-size:9px;padding:2px 6px;border-radius:10px;display:inline-block}</style></head><body><div class="container"><div class="header">{{HEADER_EXTRA}}<h1>⚡ TESLA 369 BOT ⚡</h1></div><div class="mantra">🌀 O DINHEIRO VEM ATÉ MIM DE TODOS OS LADOS 🌀</div><div class="tabs"><div class="tab active" onclick="openTab('bot')">🤖 BOT</div><div class="tab" onclick="openTab('relatorio')">📊 RELATÓRIO</div><div class="tab" onclick="openTab('estrategias')">📊 ESTRATÉGIAS</div><div class="tab" onclick="openTab('loja')">🛍️ LOJA</div><div class="tab" onclick="openTab('chat')">💬 CHAT</div><div class="tab" onclick="openTab('leia-me')">📖 TUTORIAL</div></div><div class="panel active" id="panel-bot"><div class="config-section"><h3>🔐 IQ OPTION</h3><div class="config-row"><input type="email" id="email" placeholder="📧 Email IQ Option" style="flex:2"><input type="password" id="senha" placeholder="🔒 Senha" style="flex:1"><select id="tipo"><option value="PRACTICE">🧪</option><option value="REAL">💰</option></select></div><div class="config-row"><label style="color:#888;font-size:9px">% Banca:</label><select id="percentualBanca" onchange="atualizarPercentual()" style="padding:5px;background:#111;border:1px solid #333;border-radius:5px;color:#fff;font-size:10px;width:70px"><option value="15" selected>15%</option><option value="20">20%</option><option value="30">30%</option><option value="50">50%</option><option value="100">100%</option></select><span style="color:#ffd700;font-size:9px" id="valorEstimado">($0.00)</span></div><button class="btn btn-info" id="btnConectar" onclick="conectarIQ()">🔌 CONECTAR</button><button class="btn btn-start" id="btnOperar" onclick="comecarOperar()" style="display:none">🚀 COMEÇAR OPERAR</button><button class="btn btn-stop" id="btnParar" onclick="pararBot()" style="display:none">⏹️ PARAR</button></div><div class="dashboard"><div class="card"><div class="label">💰 BANCA</div><div class="value" id="banca" style="color:#0f8">--</div></div><div class="card"><div class="label">📈 LUCRO</div><div class="value" id="lucro">$0.00</div></div><div class="card"><div class="label">🎯 OPS</div><div class="value" id="ops">0</div></div><div class="card"><div class="label">⚡ VOLTS</div><div class="value" id="moedasSaldo">0</div></div><div class="card"><div class="label">📊 ESTRATÉGIA</div><div class="value" id="estrategiaAtiva" style="font-size:10px">--</div></div><div class="card"><div class="label">🔮 SINAL</div><div class="value" id="sinal" style="font-size:11px">--</div></div></div><div class="indicators"><div class="ind-card"><div class="ind-label">📊 RSI</div><div class="ind-value" id="rsi">--</div></div><div class="ind-card"><div class="ind-label">📈 MM5</div><div class="ind-value" id="mm5">--</div></div><div class="ind-card"><div class="ind-label">📈 MM10</div><div class="ind-value" id="mm10">--</div></div><div class="ind-card"><div class="ind-label">📉 MM20</div><div class="ind-value" id="mm20">--</div></div><div class="ind-card"><div class="ind-label">📊 ESTOC</div><div class="ind-value" id="stoch">--</div></div><div class="ind-card"><div class="ind-label">🌅 FASE</div><div class="ind-value" id="fase">--</div></div><div class="ind-card"><div class="ind-label">💵 PREÇO</div><div class="ind-value" id="preco">--</div></div></div><div class="terminal" id="terminal">📡 Aguardando...</div><div class="barra-status"><span><span class="status-dot inactive" id="statusDot"></span> <span id="statusTexto">⏸️ Desconectado</span></span><span>⚡ TESLA 369 v7.0.0</span></div></div><div class="panel" id="panel-relatorio"><div class="config-section"><h3>📊 RELATÓRIO</h3><div class="config-row"><input type="email" id="emailRelatorio" placeholder="Email" style="flex:2"><button class="btn btn-info" onclick="verRelatorio()">🔍 BUSCAR</button><button class="btn btn-info" onclick="verRanking()" style="background:linear-gradient(135deg,#ff8c00,#ffd700);color:#000">🏆 RANKING</button></div></div><div id="relatorioContent"></div></div><div class="panel" id="panel-loja"><div class="sub-tabs"><div class="sub-tab active" onclick="mostrarSubAba('moedas')">COMPRAR VOLTS</div></div><div class="sub-panel active" id="sub-panel-moedas"><div class="config-section"><h3>💳 COMPRAR VOLTS COM PIX</h3><p style="color:#888;font-size:10px">📧 <input type="email" id="emailCompra" placeholder="Seu email" style="width:220px;padding:6px;background:#111;border:1px solid #333;color:#fff;border-radius:5px"></p></div><div class="planos-grid">''' + ''.join([f'<div class="plano-card" id="plano{p.get("id",0)}" onclick="selecionarPlano({p.get("id",0)})"><div style="color:#ffd700;font-size:11px">{p.get("nome","")}</div><div class="plano-moedas">⚡ {p.get("moedas",0)}</div><div class="plano-preco">R$ {p.get("preco",0):.2f}</div><div class="plano-desc">{p.get("desc","")}</div><button class="btn-loja btn-comprar-volts" style="display:none;margin-top:10px" id="btnPlano{p.get('id',0)}" onclick="event.stopPropagation();pagarComPix({p.get('id',0)})">💳 PAGAR COM PIX</button></div>' for p in PLANOS]) + r'''</div></div></div><div class="panel" id="panel-chat"><div class="config-section"><h3>💬 CHAT DOS TRADERS</h3><p style="color:#888;font-size:9px" id="chatInfo">Conecte na IQ Option para entrar</p></div><div id="chatMensagens" style="background:#000;border:1px solid #333;border-radius:10px;height:300px;overflow-y:auto;padding:10px;margin-bottom:10px;font-size:10px"><p style="color:#888;text-align:center">💬 Envie uma mensagem para começar</p></div><div style="display:flex;gap:8px"><input type="text" id="chatMsg" placeholder="Digite sua mensagem..." style="flex:1;padding:10px;background:#111;border:1px solid #333;border-radius:8px;color:#fff;font-size:11px;font-family:monospace" onkeypress="if(event.key==='Enter')enviarChatMsg()"><button onclick="enviarChatMsg()" class="btn btn-info" style="padding:10px 20px">ENVIAR</button></div><div style="text-align:center;margin-top:5px"><span style="color:#888;font-size:9px" id="chatOnline">0 online</span></div></div></div><script>var intervalo=null,botAtivo=false,conectadoIQ=false,emailLogado='',planoSelecionado=0;function openTab(tab){document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));event.target.classList.add('active');document.getElementById('panel-'+tab).classList.add('active')}function conectarIQ(){var email=document.getElementById('email').value.trim();var senha=document.getElementById('senha').value.trim();var tipo=document.getElementById('tipo').value;if(!email||!senha){alert('Preencha email e senha!');return}emailLogado=email;document.getElementById('btnConectar').disabled=true;fetch('/conectar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:email,senha:senha,tipo:tipo})}).then(r=>r.json()).then(d=>{if(d.ok){conectadoIQ=true;setTimeout(function(){location.reload()},2000);document.getElementById('btnConectar').style.display='none';document.getElementById('btnOperar').style.display='inline-block';document.getElementById('statusTexto').textContent='🟢 Conectado';document.getElementById('statusDot').className='status-dot active';document.getElementById('moedasSaldo').textContent=d.moedas||0;if(intervalo)clearInterval(intervalo);intervalo=setInterval(atualizar,2000);atualizar()}else{alert('ERRO: '+d.erro);document.getElementById('btnConectar').disabled=false}})}function comecarOperar(){if(!conectadoIQ){alert('Conecte primeiro!');return}fetch('/comecar_operar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({})}).then(r=>r.json()).then(d=>{if(d.ok){botAtivo=true;document.getElementById('btnOperar').style.display='none';document.getElementById('btnParar').style.display='inline-block';document.getElementById('statusTexto').textContent='🤖 Operando'}else{alert('ERRO: '+d.erro)}})}function pararBot(){fetch('/parar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({})}).then(r=>r.json()).then(d=>{botAtivo=false;document.getElementById('btnOperar').style.display='inline-block';document.getElementById('btnParar').style.display='none';document.getElementById('statusTexto').textContent='🟢 Conectado'})}function atualizar(){fetch('/status').then(r=>r.json()).then(d=>{if(d.banca)document.getElementById('banca').textContent='$'+d.banca.toFixed(2);if(d.lucro!==undefined){var el=document.getElementById('lucro');el.textContent='$'+d.lucro.toFixed(2);el.style.color=d.lucro>=0?'#0f8':'#f44'}if(d.ops!==undefined)document.getElementById('ops').textContent=d.ops;if(d.moedas!==undefined)document.getElementById('moedasSaldo').textContent=d.moedas;if(d.sinal)document.getElementById('sinal').textContent=d.sinal;if(d.logs)document.getElementById('terminal').innerHTML=d.logs})}function verRelatorio(){var email=document.getElementById('emailRelatorio').value.trim();if(!email){alert('Digite o email!');return}fetch('/relatorio?email='+email).then(r=>r.json()).then(d=>{if(d.erro){alert(d.erro);return}var h='<div class="relatorio-grid">';h+='<div class="relatorio-card"><div class="rlabel">⚡ VOLTS</div><div class="rvalue">'+(d.moedas||0)+'</div></div>';h+='<div class="relatorio-card"><div class="rlabel">📈 LUCRO TOTAL</div><div class="rvalue" style="color:'+(d.lucro_total>=0?'#0f8':'#f44')+'">$'+(d.lucro_total||0).toFixed(2)+'</div></div>';h+='<div class="relatorio-card"><div class="rlabel">✅ WINS</div><div class="rvalue" style="color:#0f8">'+(d.total_wins||0)+'</div></div>';h+='<div class="relatorio-card"><div class="rlabel">❌ LOSSES</div><div class="rvalue" style="color:#f44">'+(d.total_losses||0)+'</div></div>';document.getElementById('relatorioContent').innerHTML=h})}function verRanking(){document.getElementById('relatorioContent').innerHTML='<p style="color:#ffd700;text-align:center">🏆 Carregando ranking...</p>';fetch('/ranking').then(r=>r.json()).then(d=>{var h='<div style="background:#1a1a0a;border:2px solid #ffd700;border-radius:15px;padding:15px;margin-bottom:15px"><p style="color:#ffd700;font-size:14px;font-weight:bold;text-align:center">📊 ESTATÍSTICAS GLOBAIS</p><div class="relatorio-grid"><div class="relatorio-card"><div class="rlabel">👥 USUÁRIOS</div><div class="rvalue" style="color:#ffd700">'+d.stats.total_usuarios+'</div></div><div class="relatorio-card"><div class="rlabel">🔄 TOTAL OPS</div><div class="rvalue" style="color:#ffd700">'+d.stats.total_ops+'</div></div><div class="relatorio-card"><div class="rlabel">✅ WINS</div><div class="rvalue" style="color:#0f8">'+d.stats.total_wins+'</div></div><div class="relatorio-card"><div class="rlabel">🎯 TAXA GLOBAL</div><div class="rvalue" style="color:#ffd700">'+d.stats.taxa_global+'%</div></div></div></div>';h+='<table class="historico-table"><tr><th>#</th><th>EMAIL</th><th>LUCRO</th><th>WINS</th><th>LOSS</th><th>TAXA</th></tr>';d.ranking.forEach(function(u,i){var c=i===0?'#ffd700':(i===1?'#c0c0c0':(i===2?'#cd7f32':'#fff'));var m=i===0?'🥇':(i===1?'🥈':(i===2?'🥉':(i+1)));h+='<tr><td style="color:'+c+';font-weight:bold">'+m+'</td><td style="color:#ccc;font-size:8px">'+u.email+'</td><td style="color:'+(u.lucro_total>=0?'#0f8':'#f44')+'">$'+u.lucro_total.toFixed(2)+'</td><td style="color:#0f8">'+u.total_wins+'</td><td style="color:#f44">'+u.total_losses+'</td><td style="color:#ffd700">'+u.taxa+'%</td></tr>'});h+='</table>';document.getElementById('relatorioContent').innerHTML=h}).catch(function(){document.getElementById('relatorioContent').innerHTML='<p style="color:#f44;text-align:center">Erro ao carregar ranking</p>'})}function selecionarPlano(id){document.querySelectorAll('.plano-card').forEach(c=>c.classList.remove('selecionado'));document.getElementById('plano'+id).classList.add('selecionado');planoSelecionado=id;document.querySelectorAll('[id^="btnPlano"]').forEach(b=>b.style.display='none');document.getElementById('btnPlano'+id).style.display='block'}function pagarComPix(planoId){var email=document.getElementById('emailCompra').value.trim()||emailLogado;if(!email){alert('Digite seu email!');return}document.getElementById('modalPix').classList.add('active');document.getElementById('pixContent').innerHTML='<p style="color:#ffd700">Gerando QR Code PIX...</p>';fetch('/criar_pix',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:email,plano_id:planoId})}).then(r=>r.json()).then(d=>{if(d.sucesso){var html='<p style="font-size:18px;color:#ffd700">R$ '+d.valor.toFixed(2)+'</p>';html+='<p style="color:#0f8">⚡ '+d.moedas+' VOLTS</p>';if(d.qr_code_base64)html+='<div class="pix-qrcode"><img src="data:image/png;base64,'+d.qr_code_base64+'" alt="QR Code PIX"></div>';html+='<button class="btn-confirmar" onclick="verificarPagamento(\''+d.pix_id+'\')">🔄 VERIFICAR PAGAMENTO</button>';document.getElementById('pixContent').innerHTML=html}else{document.getElementById('pixContent').innerHTML='<p style="color:#f44">Erro: '+(d.erro||'Falha')+'</p>'}})}function verificarPagamento(pixId){fetch('/verificar_pix',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({pix_id:pixId})}).then(r=>r.json()).then(d=>{if(d.pago){alert('PAGO! +'+d.moedas+' VOLTS!');document.getElementById('moedasSaldo').textContent=d.saldo;fecharModal()}else{alert('Ainda não confirmado.')}})}function fecharModal(){document.getElementById('modalPix').classList.remove('active')}</script></body></html>'''

def processar_html_com_skin():
    skin_id = skin_atual_global
    skin = next((s for s in SKINS if s['id'] == skin_id), SKINS[0])
    html = HTML
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
    return html

# ============= ROTAS =============
@app.route('/')
def index(): return render_template_string(processar_html_com_skin())

@app.route('/status')
def status():
    global skin_atual_global
    if email_usuario_atual:
        u = carregar_usuario(email_usuario_atual)
        if u: skin_atual_global = u.get('skin_atual', 'skin_padrao')
    u = carregar_usuario(email_usuario_atual) if email_usuario_atual else {}
    return jsonify({
        'conectado': conectado_iq, 'rodando': bot_rodando, 'email': email_usuario_atual,
        'banca': API.get_balance() if API else 0, 'lucro': lucro, 'ops': NumDeOperacoes,
        'sinal': ultimo_sinal, 'analise': ultima_analise, 'logs': get_logs_html(40),
        'moedas': u.get('moedas', 0) if u else 0,
        'estrategia': estrategia_atual,
        'estrategia_nome': ESTRATEGIAS.get(estrategia_atual, {}).get('nome', '--'),
        'skin_id': u.get('skin_atual', 'skin_padrao') if u else 'skin_padrao'
    })

@app.route('/conectar', methods=['POST'])
def conectar():
    global API, email_usuario_atual, conectado_iq, skin_atual_global, par, timeframe_atual
    try:
        d = request.get_json(); email = d.get('email', '').strip(); senha = d.get('senha', '').strip(); tipo = d.get('tipo', 'PRACTICE')
        if not email or not senha: return jsonify({'ok': False, 'erro': 'Email e senha obrigatórios'})
        email_usuario_atual = email
        
        API = IQ_Option(email, senha)
        status_conn, reason = API.connect()
        if not status_conn: return jsonify({'ok': False, 'erro': str(reason)[:100]})
        API.change_balance(tipo)
        conectado_iq = True
        usuario = carregar_usuario(email) or criar_usuario(email)
        hoje = str(datetime.now())[:10]
        
        # +1 VOLT por dia (apenas 1x por dia)
        if usuario.get('moedas_ganhas_hoje') != hoje:
            usuario['moedas'] = usuario.get('moedas', 0) + 1
            usuario['moedas_ganhas_hoje'] = hoje
            salvar_usuario(email, usuario)
        skin_atual_global = usuario.get('skin_atual', 'skin_padrao')
        if 'estrategias_compradas' not in usuario:
            usuario['estrategias_compradas'] = []
        salvar_usuario(email, usuario)
        par = ESTRATEGIAS[estrategia_atual]['pares'][0]; timeframe_atual = ESTRATEGIAS[estrategia_atual]['timeframe']
        add_log('🔌 Conectando na IQ Option...', 'info')
        add_log(f'✅ Conectado! ${API.get_balance():.2f} | ⚡ {usuario.get("moedas", 0)} VOLTS', 'win')
        return jsonify({'ok': True, 'moedas': usuario.get('moedas', 0)})
    except Exception as e: return jsonify({'ok': False, 'erro': str(e)[:100]})

@app.route('/comecar_operar', methods=['POST'])
def comecar_operar():
    global bot_rodando, bot_thread, lucro, NumDeOperacoes
    try:
        if not conectado_iq: return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
        usuario = carregar_usuario(email_usuario_atual)
        if not usuario: return jsonify({'ok': False, 'erro': 'Usuário não encontrado!'})
        
        estrategias_compradas = usuario.get('estrategias_compradas', ['tesla_369'])
        if estrategia_atual not in estrategias_compradas:
            preco = ESTRATEGIAS.get(estrategia_atual, {}).get('preco_moedas', 0)
            return jsonify({'ok': False, 'erro': f'Estratégia não comprada! Compre na loja por {preco} ⚡'})
        
        if usuario.get('moedas', 0) < 1: return jsonify({'ok': False, 'erro': 'Sem VOLTS!'})
        usuario['moedas'] -= 1; usuario['total_ciclos'] += 1; salvar_usuario(email_usuario_atual, usuario)
        lucro = 0.0; NumDeOperacoes = 0
        
        email_atual = email_usuario_atual
        if not bot_rodando:
            bot_rodando = True
            bot_thread = threading.Thread(target=bot_loop, daemon=True)
            bot_thread.start()
            bots_ativos[email_atual] = bot_thread
        
        return jsonify({'ok': True, 'moedas': usuario['moedas']})
    except Exception as e: return jsonify({'ok': False, 'erro': str(e)[:100]})

@app.route('/parar', methods=['POST'])
def parar():
    global bot_rodando
    bot_rodando = False
    return jsonify({'ok': True})

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
    except: pass
    ranking_list.sort(key=lambda x: x['lucro_total'], reverse=True)
    total_ops = sum(u['total_ciclos'] for u in ranking_list)
    total_wins = sum(u['total_wins'] for u in ranking_list)
    taxa_global = round((total_wins / max(total_ops, 1)) * 100, 1) if total_ops > 0 else 0
    return jsonify({'ranking': ranking_list[:20], 'stats': {'total_usuarios': len(ranking_list), 'total_ops': total_ops, 'total_wins': total_wins, 'taxa_global': taxa_global}})

@app.route('/relatorio')
def relatorio():
    email = request.args.get('email', '')
    if not email: return jsonify({'erro': 'Email obrigatório'})
    u = carregar_usuario(email)
    return jsonify(u if u else {'erro': 'Não encontrado'})

@app.route('/criar_pix', methods=['POST'])
def criar_pix():
    d = request.get_json(); email = d.get('email', ''); plano_id = int(d.get('plano_id') or 1)
    if not email: return jsonify({'sucesso': False, 'erro': 'Email obrigatório'})
    plano = next((p for p in PLANOS if p['id'] == plano_id), None)
    if not plano: return jsonify({'sucesso': False, 'erro': 'Plano não encontrado'})
    return jsonify(gerar_pix_mercadopago(email, plano))

@app.route('/verificar_pix', methods=['POST'])
def verificar_pix():
    d = request.get_json(); pix_id = d.get('pix_id', '')
    if not pix_id: return jsonify({'pago': False})
    if verificar_pagamento_mp(pix_id):
        if pix_id in pagamentos_pendentes and not pagamentos_pendentes[pix_id]['pago']:
            pagamentos_pendentes[pix_id]['pago'] = True
            email = pagamentos_pendentes[pix_id]['email']; moedas = pagamentos_pendentes[pix_id]['moedas']
            usuario = carregar_usuario(email) or criar_usuario(email)
            usuario['moedas'] = usuario.get('moedas', 0) + moedas; salvar_usuario(email, usuario)
            return jsonify({'pago': True, 'moedas': moedas, 'saldo': usuario['moedas']})
        return jsonify({'pago': True})
    return jsonify({'pago': False})

if __name__ == '__main__':
    print("=" * 50)
    print("⚡ TESLA 369 BOT v7.0.0 ⚡")
    print("=" * 50)
    port = int(os.environ.get('PORT', 5000))
    import webbrowser as _wb
    try:
        _wb.open(f'http://localhost:{port}')
    except:
        pass
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
