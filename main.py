# ◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈
# ☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿
# ⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗
#    🌀  O DINHEIRO VEM ATÉ MIM DE TODOS OS LADOS  🌀
#         DE FORMA ABUNDANTE, CONTÍNUA E PRÓSPERA
# ⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗
# ◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈
# ⚡ TESLA 369 BOT - COMPLETO v4.1.1.10 ⚡
# 8 ESTRATÉGIAS | LOJA DE SKINS | MERCADO PAGO | RENDER READY
# BD VIA GITHUB API - MOEDA CONSUMIDA AO CLICAR EM "COMEÇAR OPERAR"
# ◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈

from flask import Flask, render_template_string, jsonify, request
from iqoptionapi.stable_api import IQ_Option
from datetime import datetime
import threading, time, sys, os, json, warnings, requests, uuid, base64

warnings.filterwarnings("ignore")
app = Flask(__name__)

# ============= CONFIGURAÇÕES FIXAS =============
MARTINGALE = 2
PAYOUT_PADRAO = 0.85
DRIVE_PATH = "vsens_users"
os.makedirs(DRIVE_PATH, exist_ok=True)

# ⭐⭐⭐ CONFIGURAÇÃO DO MERCADO PAGO ⭐⭐⭐
# Carregar configurações do Mercado Pago
try:
    config_url = f"https://api.github.com/repos/{USER}/{REPO}/contents/config.json"
    r_config = requests.get(config_url, headers={"Authorization": f"Bearer {os.environ.get('GITHUB_TOKEN', '')}", "Accept": "application/vnd.github.v3+json"})
    if r_config.status_code == 200:
        config_data = json.loads(base64.b64decode(r_config.json()["content"]).decode())
        MERCADO_PAGO_ACCESS_TOKEN = config_data.get("MERCADO_PAGO_ACCESS_TOKEN", "")
        MERCADO_PAGO_PUBLIC_KEY = config_data.get("MERCADO_PAGO_PUBLIC_KEY", "")
        MODO_SIMULACAO = config_data.get("MODO_SIMULACAO", False)
    else:
        MERCADO_PAGO_ACCESS_TOKEN = os.environ.get("MERCADO_PAGO_ACCESS_TOKEN", "")
        MERCADO_PAGO_PUBLIC_KEY = os.environ.get("MERCADO_PAGO_PUBLIC_KEY", "")
except:
    MERCADO_PAGO_ACCESS_TOKEN = os.environ.get("MERCADO_PAGO_ACCESS_TOKEN", "")
    MERCADO_PAGO_PUBLIC_KEY = os.environ.get("MERCADO_PAGO_PUBLIC_KEY", "")
MODO_SIMULACAO = False

# ⭐ PLANOS DE MOEDAS ⭐
PLANOS = [
    {'id':1,'moedas':1,'preco':0.99,'nome':'🔰 INICIANTE','desc':'R$0,99/moeda','tag':'1 por 1'},
    {'id':2,'moedas':5,'preco':4.99,'nome':'⭐ BÁSICO','desc':'R$1,00/moeda'},
    {'id':3,'moedas':15,'preco':9.99,'nome':'💎 INTERMEDIÁRIO','desc':'R$0,67/moeda','desconto':'33% OFF'},
    {'id':4,'moedas':35,'preco':14.99,'nome':'🔥 PREMIUM','desc':'R$0,43/moeda','desconto':'57% OFF'},
    {'id':5,'moedas':60,'preco':19.99,'nome':'👑 ULTRA','desc':'R$0,33/moeda','desconto':'67% OFF'},
]

# ⭐ SKINS DA LOJA ⭐
SKINS = [
    {
        'id': 'skin_padrao', 'nome': '⚡ TESLA PADRÃO', 'desc': 'Tema escuro com raios dourados', 'preco_moedas': 0,
        'cor_fundo': '#0a0a1a', 'cor_panel': '#1a1a3e', 'cor_destaque': '#ffd700', 'cor_texto': '#fff',
        'cor_botao': 'linear-gradient(135deg,#cc8800,#ffd700)', 'cor_tab_ativa': '#ffd700',
        'cor_header_bg': 'linear-gradient(135deg,#1a0000,#331100,#553300,#331100,#1a0000)', 'cor_header_borda': '#ffd700',
        'header_extra': '<div class="lightning"></div>',
        'css_extra': '.lightning{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:150px;height:150px;background:radial-gradient(circle at 30% 30%,rgba(255,215,0,0.3) 0%,rgba(255,165,0,0.15) 30%,transparent 100%);border-radius:50%;z-index:0;animation:glow 3s ease-in-out infinite;pointer-events:none}@keyframes glow{0%,100%{box-shadow:0 0 30px rgba(255,215,0,0.3)}50%{box-shadow:0 0 50px rgba(255,165,0,0.5)}}.lightning::after{content:"⚡";position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:50px;animation:float 2s ease-in-out infinite}@keyframes float{0%,100%{transform:translate(-50%,-50%) scale(1)}50%{transform:translate(-50%,-60%) scale(1.1)}}'
    },
    {
        'id': 'skin_magos', 'nome': '🔮 MAGOS DA BOLA DE CRISTAL', 'desc': 'Tema roxo místico', 'preco_moedas': 1,
        'cor_fundo': '#0a0a1a', 'cor_panel': '#1a1a3e', 'cor_destaque': '#cc66ff', 'cor_texto': '#e0d0ff',
        'cor_botao': 'linear-gradient(135deg,#6600cc,#9933ff)', 'cor_tab_ativa': '#9933ff',
        'cor_header_bg': 'linear-gradient(135deg,#0d001a,#1a0033,#2d0055,#1a0033,#0d001a)', 'cor_header_borda': '#9933ff',
        'header_extra': '<div class="crystal-ball"></div><div class="mago mago-esq">🧙‍♂️</div><div class="mago mago-dir">🧙‍♀️</div>',
        'css_extra': '.crystal-ball{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:130px;height:130px;background:radial-gradient(circle at 30% 30%,rgba(200,150,255,0.4) 0%,rgba(153,51,255,0.2) 30%,transparent 70%);border-radius:50%;z-index:0;animation:crystalGlow 4s ease-in-out infinite;pointer-events:none;border:2px solid rgba(153,51,255,0.3)}@keyframes crystalGlow{0%,100%{box-shadow:0 0 30px rgba(153,51,255,0.4),0 0 60px rgba(153,51,255,0.2)}50%{box-shadow:0 0 50px rgba(200,100,255,0.6),0 0 80px rgba(200,100,255,0.3)}}.crystal-ball::after{content:"🔮";position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:45px;animation:floatCrystal 3s ease-in-out infinite}@keyframes floatCrystal{0%,100%{transform:translate(-50%,-50%) scale(1)}50%{transform:translate(-50%,-60%) scale(1.1)}}.mago{position:absolute;top:50%;font-size:30px;z-index:1;animation:magoFloat 2s ease-in-out infinite;pointer-events:none}.mago-esq{left:15px}.mago-dir{right:15px;animation-delay:0.5s}@keyframes magoFloat{0%,100%{transform:translateY(-50%)}50%{transform:translateY(-60%)}}'
    },
    {
        'id': 'skin_brasil', 'nome': '🇧🇷 BRASIL', 'desc': 'Tema verde e amarelo', 'preco_moedas': 0,
        'cor_fundo': '#001a0a', 'cor_panel': '#0a2a15', 'cor_destaque': '#ffd700', 'cor_texto': '#fff',
        'cor_botao': 'linear-gradient(135deg,#009933,#00cc44)', 'cor_tab_ativa': '#ffd700',
        'cor_header_bg': 'linear-gradient(135deg,#001a0a,#003315,#004d20,#003315,#001a0a)', 'cor_header_borda': '#ffd700',
        'header_extra': '<div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:60px;z-index:0;opacity:0.3;pointer-events:none">🇧🇷</div>', 'css_extra': ''
    }
,
    {
        'id': 'skin_princesa', 'nome': '👸 PRINCESA', 'desc': 'Tema rosa com brilhos', 'preco_moedas': 2,
        'cor_fundo': '#1a0010', 'cor_panel': '#2a0a20', 'cor_destaque': '#ff69b4', 'cor_texto': '#ffe0f0',
        'cor_botao': 'linear-gradient(135deg,#cc3388,#ff69b4)', 'cor_tab_ativa': '#ff69b4',
        'cor_header_bg': 'linear-gradient(135deg,#1a0010,#2a0a20,#3a1530,#2a0a20,#1a0010)', 'cor_header_borda': '#ff69b4',
        'header_extra': '<div class="coroa-p">👑</div>',
        'css_extra': '.coroa-p{position:absolute;top:10px;left:50%;transform:translateX(-50%);font-size:40px;animation:float 2s ease-in-out infinite}@keyframes float{0%,100%{transform:translateX(-50%) translateY(0)}50%{transform:translateX(-50%) translateY(-10px)}}.header h1{color:#ff69b4!important;text-shadow:0 0 30px #ff1493!important}'
    }
]

# ⭐ ESTRATÉGIAS (8 - SEM 9:30) ⭐
ESTRATEGIAS = {
    'v_sensitivo': {'nome': '🔮 v_SENSITIVO', 'desc': 'RSI + MM + Bollinger + MACD + Estocástico + Fase da Vela', 'timeframe': 60, 'pares': ['EURUSD-OTC', 'EURUSD']},
    'tesla_369': {'nome': '⚡ TESLA-369', 'desc': '6 velas: padrão g-g-g-r-r → CALL / r-r-r-g-g → PUT', 'timeframe': 60, 'pares': ['EURUSD-OTC', 'EURUSD']},
    'mhi_filtrado': {'nome': '📊 MHI-FILTRADO', 'desc': '5 velas + Média Móvel + filtro de cor dominante', 'timeframe': 60, 'pares': ['EURUSD-OTC', 'EURUSD']},
    'terceira_igual_primeira': {'nome': '3️⃣ 3ª = 1ª', 'desc': 'Opera a cada 5min, seg 55+', 'timeframe': 60, 'pares': ['EURUSD-OTC', 'EURUSD']},
    'quadrante_de_7': {'nome': '7️⃣ QUADRANTE DE 7', 'desc': '7 velas + MM, conta cores', 'timeframe': 60, 'pares': ['EURUSD-OTC', 'EURUSD']},
    'fluxo_de_velas': {'nome': '🌊 FLUXO-DE-VELAS', 'desc': '5 velas mesma cor + MM', 'timeframe': 60, 'pares': ['EURUSD-OTC', 'EURUSD']},
    'reversao': {'nome': '🔄 REVERSÃO', 'desc': 'Padrão alternado g-r-g-r-g ou r-g-r-g-r', 'timeframe': 60, 'pares': ['EURUSD-OTC', 'EURUSD']},
    'm5': {'nome': '⏰ M5', 'desc': 'Quadrante de velas de 5min', 'timeframe': 300, 'pares': ['EURUSD-OTC', 'EURUSD']}
}

# ============= BANCO DE DADOS VIA GITHUB API =============
def salvar_usuario(email, dados):
    """Salva no GitHub via API + backup local"""
    try:
        token = os.environ.get("GITHUB_TOKEN", "")
        if token:
            fn = f"dados/{email.replace('@', '_').replace('.', '_')}.json"
            u = f"https://api.github.com/repos/gynbetfc/v-sensitivo-bot/contents/{fn}"
            h = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
            c = json.dumps(dados, indent=2)
            r = requests.get(u, headers=h)
            p = {"message": f"Update {email}", "content": base64.b64encode(c.encode()).decode(), "branch": "main"}
            if r.status_code == 200: p["sha"] = r.json()["sha"]
            requests.put(u, json=p, headers=h)
    except: pass
    os.makedirs(DRIVE_PATH, exist_ok=True)
    with open(f"{DRIVE_PATH}/{email.replace('@', '_').replace('.', '_')}.json", 'w') as f:
        json.dump(dados, f, indent=2)

def carregar_usuario(email):
    """Carrega do GitHub ou local"""
    try:
        token = os.environ.get("GITHUB_TOKEN", "")
        if token:
            fn = f"dados/{email.replace('@', '_').replace('.', '_')}.json"
            u = f"https://api.github.com/repos/gynbetfc/v-sensitivo-bot/contents/{fn}"
            h = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
            r = requests.get(u, headers=h)
            if r.status_code == 200: return json.loads(base64.b64decode(r.json()["content"]).decode())
    except: pass
    arq = f"{DRIVE_PATH}/{email.replace('@', '_').replace('.', '_')}.json"
    if os.path.exists(arq):
        with open(arq, 'r') as f: return json.load(f)
    return None

def criar_usuario(email):
    dados = {'email': email, 'moedas': 1, 'moedas_ganhas_hoje': str(datetime.now())[:10], 'total_ciclos': 0, 'total_wins': 0, 'total_losses': 0, 'total_gasto': 0.0, 'total_ganho': 0.0, 'lucro_total': 0.0, 'banca_atual': 0.0, 'data_cadastro': str(datetime.now())[:19], 'historico_operacoes': [], 'dias_ativos': {}, 'skin_atual': 'skin_padrao', 'skins_compradas': ['skin_padrao']}
    salvar_usuario(email, dados)
    return dados

# ============= VARIÁVEIS GLOBAIS =============
API, par = None, "EURUSD-OTC"
estrategia_atual = 'v_sensitivo'
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

def add_log(msg, tipo='info'):
    global logs_web
    t = datetime.now().strftime('%H:%M:%S')
    logs_web.append({'time': t, 'msg': msg, 'tipo': tipo})
    if len(logs_web) > MAX_LOGS_WEB: logs_web = logs_web[-MAX_LOGS_WEB:]
    print(f"{t} - {msg}"); sys.stdout.flush()

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
    'v_sensitivo': sinal_v_sensitivo, 'tesla_369': sinal_tesla_369,
    'mhi_filtrado': sinal_mhi_filtrado, 'terceira_igual_primeira': sinal_terceira_igual_primeira,
    'quadrante_de_7': sinal_quadrante_de_7, 'fluxo_de_velas': sinal_fluxo_de_velas,
    'reversao': sinal_reversao, 'm5': sinal_m5
}

# ═══════════════════════════════════════════════════════
# CÁLCULO DE ENTRADAS
# ═══════════════════════════════════════════════════════
def calcular_entradas(b, p, g):
    bs = b * 0.99; e0 = bs / sum((1/p)**i for i in range(g+1))
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
                u['historico_operacoes'].append({'data': str(datetime.now())[:19], 'resultado': 'WIN', 'valor': valor, 'lucro': lucro_liquido, 'estrategia': estrategia_atual})
                u['dias_ativos'][str(datetime.now())[:10]] = u['dias_ativos'].get(str(datetime.now())[:10], 0) + 1
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
                u['historico_operacoes'].append({'data': str(datetime.now())[:19], 'resultado': 'LOSS', 'valor': valor, 'lucro': -valor, 'estrategia': estrategia_atual})
                u['dias_ativos'][str(datetime.now())[:10]] = u['dias_ativos'].get(str(datetime.now())[:10], 0) + 1
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
    add_log("🔄 Verificador automático PIX iniciado!", "info")
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
                    add_log(f"✅ PIX {pix_id[:8]}... pago! +{moedas} moedas para {email}", "win")
        except: pass

threading.Thread(target=verificador_automatico_pix, daemon=True).start()

# ═══════════════════════════════════════════════════════
# HTML COMPLETO
# ═══════════════════════════════════════════════════════
HTML = r'''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚡ TESLA 369 BOT</title>
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
        .indicators{display:grid;grid-template-columns:repeat(auto-fit,minmax(80px,1fr));gap:6px;margin-bottom:10px}
        .ind-card{background:#111;padding:6px;border-radius:8px;border:1px solid #222;text-align:center;font-size:10px}
        .ind-card .ind-label{color:#666;font-size:9px}.ind-card .ind-value{color:{{COR_DESTAQUE}};font-size:11px}
        .terminal{background:#000;color:#00ff88;padding:12px;border-radius:10px;height:200px;overflow-y:auto;font-size:10px;line-height:1.4;white-space:pre-wrap;border:1px solid #333}
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
        .estrategia-card{background:#111;padding:12px;border-radius:10px;border:2px solid #222;cursor:pointer;transition:all 0.3s ease;text-align:center}
        .estrategia-card:hover{border-color:{{COR_DESTAQUE}}}
        .estrategia-card.ativa{border-color:#00ff88;box-shadow:0 0 15px rgba(0,255,136,0.3);background:#0a1a0a}
        .estrategia-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:8px}
        .badge-gratis{background:#00ff88;color:#000;font-size:9px;padding:2px 6px;border-radius:10px;display:inline-block}
        .badge-pago{background:#ffd700;color:#000;font-size:9px;padding:2px 6px;border-radius:10px;display:inline-block}
    
.sub-tabs{display:flex;gap:5px;margin-bottom:15px}
.sub-tab{padding:8px 16px;background:#111;border:1px solid #333;border-radius:8px 8px 0 0;cursor:pointer;color:#888;font-size:11px}
.sub-tab.active{background:linear-gradient(135deg,#cc8800,#ffd700);color:#000;font-weight:bold;border-color:#ffd700}
.sub-tab:hover{background:#1a1a2e;color:#fff}
.sub-panel{display:none}
.sub-panel.active{display:block}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        {{HEADER_EXTRA}}
        <h1>⚡ TESLA 369 BOT v4.1.1.10 ⚡</h1>
        <p>🔮 8 ESTRATÉGIAS | GALE 2 | STOP GAIN 1 WIN | LOJA DE SKINS</p>
        <p>⚡ O BOT QUE SENTE A VELA ⚡</p>
    </div>
    <div class="mantra">🌀 O DINHEIRO VEM ATÉ MIM DE TODOS OS LADOS 🌀</div>
    <div class="tabs">
        <div class="tab active" onclick="openTab('bot')">🤖 BOT</div>
        <div class="tab" onclick="openTab('estrategias')">📊 ESTRATÉGIAS</div>
        <div class="tab" onclick="openTab('loja')">🛍️ LOJA</div>
        <div class="tab" onclick="openTab('relatorio')">📊 RELATÓRIO</div>
    </div>
    
    <div class="panel active" id="panel-bot">
        <div class="config-section"><h3>🔐 IQ OPTION</h3><div class="config-row">
            <input type="email" id="email" placeholder="📧 Email IQ Option" style="flex:2">
            <input type="password" id="senha" placeholder="🔒 Senha" style="flex:1">
            <select id="tipo"><option value="PRACTICE">🧪</option><option value="REAL">💰</option></select>
            <button class="btn btn-info" id="btnConectar" onclick="conectarIQ()">🔌 CONECTAR</button>
            <button class="btn btn-start" id="btnOperar" onclick="comecarOperar()" style="display:none">🚀 COMEÇAR OPERAR</button>
            <button class="btn btn-stop" id="btnParar" onclick="pararBot()" style="display:none">⏹️ PARAR</button>
            <button class="btn btn-stop" id="btnDesconectar" onclick="desconectarIQ()" style="display:none">🔌 DESCONECTAR</button>
        </div></div>
        <div class="dashboard">
            <div class="card"><div class="label">💰 BANCA</div><div class="value" id="banca" style="color:#00ff88">--</div></div>
            <div class="card"><div class="label">📈 LUCRO</div><div class="value" id="lucro">$0.00</div></div>
            <div class="card"><div class="label">🎯 OPS</div><div class="value" id="ops">0</div></div>
            <div class="card"><div class="label">🪙 MOEDAS</div><div class="value" id="moedasSaldo">0</div></div>
            <div class="card"><div class="label">📊 ESTRATÉGIA</div><div class="value" id="estrategiaAtiva" style="font-size:10px">--</div></div>
            <div class="card"><div class="label">🔮 SINAL</div><div class="value" id="sinal" style="font-size:11px">--</div></div>
        </div>
        <div class="indicators">
            <div class="ind-card"><div class="ind-label">📊 RSI</div><div class="ind-value" id="rsi">--</div></div>
            <div class="ind-card"><div class="ind-label">📈 MM5</div><div class="ind-value" id="mm5">--</div></div>
            <div class="ind-card"><div class="ind-label">📈 MM10</div><div class="ind-value" id="mm10">--</div></div>
            <div class="ind-card"><div class="ind-label">📉 MM20</div><div class="ind-value" id="mm20">--</div></div>
            <div class="ind-card"><div class="ind-label">📊 ESTOC</div><div class="ind-value" id="stoch">--</div></div>
            <div class="ind-card"><div class="ind-label">🌅 FASE</div><div class="ind-value" id="fase">--</div></div>
            <div class="ind-card"><div class="ind-label">💵 PREÇO</div><div class="ind-value" id="preco">--</div></div>
        </div>
        <div class="terminal" id="terminal">📡 Aguardando...</div>
        <div class="barra-status">
            <span><span class="status-dot inactive" id="statusDot"></span> <span id="statusTexto">⏸️ Desconectado</span></span>
            <span>⚡ TESLA 369 v4.1.1.10</span>
            <span>GALE 2 | SG: 1 WIN</span>
        </div>
    </div>
    
    <div class="panel" id="panel-estrategias">
        <div class="config-section"><h3>📊 SELECIONAR ESTRATÉGIA (8 DISPONÍVEIS)</h3><p style="color:#888;font-size:10px">Escolha antes de clicar em COMEÇAR OPERAR</p></div>
        <div class="estrategia-grid" id="estrategiaGrid"></div>
    </div>
    
    <div class="panel" id="panel-loja">
        <div class="sub-tabs">
            <div class="sub-tab active" id="sub-tab-moedas" onclick="mostrarSubAba('moedas')">COMPRAR MOEDAS</div>
            <div class="sub-tab" id="sub-tab-skins" onclick="mostrarSubAba('skins')">LOJA DE SKINS</div>
        </div>
        <div class="sub-panel active" id="sub-panel-moedas">
            <div class="config-section"><h3>💳 COMPRAR MOEDAS COM PIX</h3><p style="color:#888;font-size:10px">📧 <input type="email" id="emailCompra" placeholder="Seu email" style="width:220px;padding:6px;background:#111;border:1px solid #333;color:#fff;border-radius:5px"></p><p style="color:#ffd700;font-size:10px;margin-top:5px">🪙 1 moeda = 1 ciclo | +1 moeda grátis/dia</p><p style="color:#888;font-size:9px;margin-top:3px">⭐ Selecione o plano e pague com PIX</p></div>
        <div class="planos-grid">''' + ''.join([f'<div class="plano-card" id="plano{p["id"]}" onclick="selecionarPlano({p["id"]})"><div style="color:#ffd700;font-size:11px">{p["nome"]}</div><div class="plano-moedas">🪙 {p["moedas"]}</div><div class="plano-preco">R$ {p["preco"]:.2f}</div><div class="plano-desc">{p.get("desc","")}</div>{f"<div><span class=\"plano-desconto\">{p['desconto']}</span></div>" if p.get("desconto") else ""}{f"<div class=\"plano-tag\">{p['tag']}</div>" if p.get("tag") else ""}<button class="btn btn-buy" style="display:none;margin-top:8px;padding:8px" id="btnPlano{p['id']}" onclick="event.stopPropagation();pagarComPix({p['id']})">💳 PAGAR COM PIX</button></div>' for p in PLANOS]) + r'''</div>
        </div>
        <div class="sub-panel" id="sub-panel-skins">
            <div class="config-section"><h3>SKINS DISPONIVEIS</h3><p style="color:#888;font-size:10px">Personalize a aparencia do seu bot! Skins compradas ficam salvas.</p></div>
            <div class="skins-grid" id="skinsGrid"></div>
        </div>
    </div>
    
    <div class="panel" id="panel-relatorio">
        <div class="config-section"><h3>📊 RELATÓRIO</h3><div class="config-row"><input type="email" id="emailRelatorio" placeholder="Email" style="flex:2"><button class="btn btn-info" onclick="verRelatorio()">🔍 BUSCAR</button><button class="btn btn-reset" onclick="resetarRelatorio()">🔄 RESETAR</button></div></div>
        <div id="relatorioContent"></div>
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

function mostrarSubAba(aba){
    document.querySelectorAll('.sub-tab').forEach(t=>t.classList.remove('active'));
    document.querySelectorAll('.sub-panel').forEach(p=>p.classList.remove('active'));
    document.getElementById('sub-tab-'+aba).classList.add('active');
    document.getElementById('sub-panel-'+aba).classList.add('active');
    if(aba==='skins') renderLoja();
}

var intervalo=null,botAtivo=false,conectadoIQ=false,emailLogado='',planoSelecionado=0,pixAtual=null;
var estrategiaSel='v_sensitivo';
var estrategias = ''' + json.dumps({k: {'nome': v['nome'], 'desc': v['desc']} for k, v in ESTRATEGIAS.items()}) + r''';

function openTab(tab){
    document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
    event.target.classList.add('active');
    document.getElementById('panel-'+tab).classList.add('active');
    if(tab=='relatorio'&&emailLogado){document.getElementById('emailRelatorio').value=emailLogado;verRelatorio()}
    if(tab=='loja'){renderLoja();mostrarSubAba('moedas');}
    if(tab=='estrategias')renderEstrategias();
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
            document.getElementById('btnOperar').style.display='inline-block';
            document.getElementById('btnDesconectar').style.display='inline-block';
            document.getElementById('statusTexto').textContent='🟢 Conectado';
            document.getElementById('statusDot').className='status-dot active';
            document.getElementById('moedasSaldo').textContent=d.moedas||0;
            if(intervalo)clearInterval(intervalo);
            intervalo=setInterval(atualizar,2000);
            atualizar();
        }else{
            alert('ERRO: '+d.erro);
            document.getElementById('btnConectar').disabled=false;
            document.getElementById('btnConectar').textContent='🔌 CONECTAR';
        }
    });
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
            document.getElementById('statusTexto').textContent='🤖 Operando';
            document.getElementById('moedasSaldo').textContent=d.moedas;
        }else{
            alert('ERRO: '+d.erro);
            document.getElementById('btnOperar').disabled=false;
            document.getElementById('btnOperar').textContent='🚀 COMEÇAR OPERAR';
        }
    });
}


function desconectarIQ(){
    if(botAtivo){
        alert('⚠️ Pare o bot primeiro antes de desconectar!');
        return;
    }
    if(confirm('Desconectar da IQ Option?')){
        fetch('/parar',{method:'POST'}).then(r=>r.json()).then(d=>{
            conectadoIQ=false;
            botAtivo=false;
            document.getElementById('btnConectar').style.display='inline-block';
            document.getElementById('btnOperar').style.display='none';
            document.getElementById('btnParar').style.display='none';
            document.getElementById('btnDesconectar').style.display='none';
            document.getElementById('statusTexto').textContent='⏸️ Desconectado';
            document.getElementById('statusDot').className='status-dot inactive';
            if(intervalo)clearInterval(intervalo);
        });
    }
}

function pararBot(){
    if(!confirm('Parar?'))return;
    fetch('/parar',{method:'POST'}).then(r=>r.json()).then(d=>{
        botAtivo=false;conectadoIQ=false;
        document.getElementById('btnConectar').style.display='inline-block';
        document.getElementById('btnOperar').style.display='none';
        document.getElementById('btnParar').style.display='none';
        document.getElementById('btnConectar').disabled=false;
        document.getElementById('btnConectar').textContent='🔌 CONECTAR';
        document.getElementById('btnOperar').disabled=false;
        document.getElementById('btnOperar').textContent='🚀 COMEÇAR OPERAR';
        document.getElementById('statusTexto').textContent='⏸️ Desconectado';
        document.getElementById('statusDot').className='status-dot inactive';
        if(intervalo)clearInterval(intervalo);
    });
}

function renderEstrategias(){
    var grid=document.getElementById('estrategiaGrid');
    var html='';
    for(var key in estrategias){
        var e=estrategias[key];
        var ativa=key==estrategiaSel?' ativa':'';
        html+='<div class="estrategia-card'+ativa+'" onclick="selecionarEstrategia(\''+key+'\')" id="est_'+key+'">';
        html+='<div style="font-size:14px;font-weight:bold">'+e.nome+'</div>';
        html+='<div style="font-size:9px;color:#888;margin-top:5px">'+e.desc+'</div>';
        html+='</div>';
    }
    grid.innerHTML=html;
    document.getElementById('estrategiaAtiva').textContent=estrategias[estrategiaSel].nome;
}

function selecionarEstrategia(key){
    estrategiaSel=key;
    document.getElementById('estrategiaAtiva').textContent=estrategias[key].nome;
    document.querySelectorAll('.estrategia-card').forEach(c=>c.classList.remove('ativa'));
    document.getElementById('est_'+key).classList.add('ativa');
    fetch('/selecionar_estrategia',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({estrategia:key})});
}

function renderLoja(){
    fetch('/status').then(r=>r.json()).then(d=>{
        var skinsStatus = d.skins_status || [];
        var grid=document.getElementById('skinsGrid');
        var html='';
        skinsStatus.forEach(function(skin){
            var ativa=skin.ativo?' ativo':'';
            var btnHtml='';
            if(skin.ativo){
                btnHtml='<button class="btn btn-info" style="width:100%;margin-top:8px;cursor:default">✅ EM USO</button>';
            }else if(skin.comprado){
                btnHtml='<button class="btn btn-skin" style="width:100%;margin-top:8px" onclick="ativarSkin(\''+skin.id+'\')">🎨 USAR SKIN</button>';
            }else{
                if(skin.preco_moedas==0){
                    btnHtml='<button class="btn btn-skin" style="width:100%;margin-top:8px" onclick="ativarSkin(\''+skin.id+'\')">🆓 ATIVAR GRÁTIS</button>';
                }else{
                    btnHtml='<button class="btn btn-buy" style="width:100%;margin-top:8px;padding:8px" onclick="comprarSkin(\''+skin.id+'\')">🛒 COMPRAR ('+skin.preco_moedas+' 🪙)</button>';
                }
            }
            html+='<div class="skin-card'+ativa+'">';
            html+='<div class="skin-nome">'+skin.nome+'</div>';
            html+='<div class="skin-desc">'+skin.desc+'</div>';
            html+='<div style="margin-top:5px">';
            if(skin.preco_moedas==0){html+='<span class="badge-gratis">GRÁTIS</span>';}
            else if(skin.comprado){html+='<span class="badge-gratis">✅ COMPRADO</span>';}
            else{html+='<span class="badge-pago">🪙 '+skin.preco_moedas+' moedas</span>';}
            html+='</div>';
            html+=btnHtml;
            html+='</div>';
        });
        grid.innerHTML=html;
    });
}

function comprarSkin(skinId){
    if(!emailLogado){alert('Conecte primeiro!');return}
    if(!confirm('Comprar esta skin?'))return;
    fetch('/comprar_skin',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({skin_id:skinId})})
    .then(r=>r.json()).then(d=>{
        if(d.ok){alert(d.msg||'Skin comprada!');document.getElementById('moedasSaldo').textContent=d.moedas;renderLoja();setTimeout(function(){location.reload();},500);}
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
            html+='<p style="color:#00ff88">🪙 '+d.moedas+' moedas</p>';
            if(d.qr_code_base64)html+='<div class="pix-qrcode"><img src="data:image/png;base64,'+d.qr_code_base64+'" alt="QR Code PIX"></div>';
            if(d.qr_code){html+='<p style="color:#888;font-size:10px;margin-top:8px">📋 Copie o código:</p><div class="pix-copiavel" onclick="copiarPix()">'+d.qr_code+'</div>';}
            html+='<button class="btn-confirmar" onclick="verificarPagamento(\''+d.pix_id+'\')">🔄 VERIFICAR PAGAMENTO</button>';
            document.getElementById('pixContent').innerHTML=html;
        }else{document.getElementById('pixContent').innerHTML='<p style="color:#ff4444">Erro: '+(d.erro||'Falha')+'</p>';}
    });
}

function copiarPix(){navigator.clipboard.writeText(pixAtual.qr_code).then(()=>alert('Código PIX copiado!'));}
function verificarPagamento(pixId){
    fetch('/verificar_pix',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({pix_id:pixId})})
    .then(r=>r.json()).then(d=>{
        if(d.pago){alert('PAGO! +'+d.moedas+' moedas!');document.getElementById('moedasSaldo').textContent=d.saldo;fecharModal();}
        else{alert('Ainda não confirmado.');}
    });
}
function fecharModal(){document.getElementById('modalPix').classList.remove('active');pixAtual=null;}

function verRelatorio(){
    var email=document.getElementById('emailRelatorio').value.trim();
    if(!email){alert('Digite o email!');return}
    fetch('/relatorio?email='+email).then(r=>r.json()).then(d=>{
        if(d.erro){alert(d.erro);return}
        var h='<div class="relatorio-grid">';
        h+='<div class="relatorio-card"><div class="rlabel">🪙 MOEDAS</div><div class="rvalue">'+(d.moedas||0)+'</div></div>';
        h+='<div class="relatorio-card"><div class="rlabel">📈 LUCRO TOTAL</div><div class="rvalue" style="color:'+(d.lucro_total>=0?'#00ff88':'#ff4444')+'">$'+(d.lucro_total||0).toFixed(2)+'</div></div>';
        h+='<div class="relatorio-card"><div class="rlabel">✅ WINS</div><div class="rvalue" style="color:#00ff88">'+(d.total_wins||0)+'</div></div>';
        h+='<div class="relatorio-card"><div class="rlabel">❌ LOSSES</div><div class="rvalue" style="color:#ff4444">'+(d.total_losses||0)+'</div></div>';
        h+='<div class="relatorio-card"><div class="rlabel">🔄 CICLOS</div><div class="rvalue">'+(d.total_ciclos||0)+'</div></div>';
        h+='<div class="relatorio-card"><div class="rlabel">💵 GASTO</div><div class="rvalue">$'+(d.total_gasto||0).toFixed(2)+'</div></div>';
        h+='<div class="relatorio-card"><div class="rlabel">💰 GANHO</div><div class="rvalue">$'+(d.total_ganho||0).toFixed(2)+'</div></div>';
        h+='<div class="relatorio-card"><div class="rlabel">📅 DIAS</div><div class="rvalue">'+Object.keys(d.dias_ativos||{}).length+'</div></div>';
        h+='<div class="relatorio-card"><div class="rlabel">🎯 TAXA</div><div class="rvalue">'+(d.total_ciclos>0?((d.total_wins/d.total_ciclos)*100).toFixed(1):0)+'%</div></div>';
        h+='<div class="relatorio-card"><div class="rlabel">💰 BANCA</div><div class="rvalue">$'+(d.banca_atual||0).toFixed(2)+'</div></div>';
        h+='<div class="relatorio-card"><div class="rlabel">📅 CADASTRO</div><div class="rvalue" style="font-size:10px">'+(d.data_cadastro||'--')+'</div></div>';
        h+='</div>';
        if(d.historico_operacoes&&d.historico_operacoes.length>0){
            h+='<h4 style="margin-top:10px">📋 ÚLTIMAS</h4><table class="historico-table"><tr><th>Data</th><th>Res.</th><th>Valor</th><th>Lucro</th><th>Est.</th></tr>';
            d.historico_operacoes.slice(-15).reverse().forEach(op=>{
                h+='<tr><td>'+op.data+'</td><td style="color:'+(op.resultado=='WIN'?'#00ff88':'#ff4444')+'">'+op.resultado+'</td><td>$'+op.valor.toFixed(2)+'</td><td style="color:'+(op.lucro>=0?'#00ff88':'#ff4444')+'">$'+op.lucro.toFixed(2)+'</td><td style="font-size:8px">'+(op.estrategia||'--')+'</td></tr>';
            });
            h+='</table>';
        }
        document.getElementById('relatorioContent').innerHTML=h;
    });
}

function resetarRelatorio(){
    var email=document.getElementById('emailRelatorio').value.trim();
    if(!email){alert('Digite o email!');return}
    if(!confirm('Resetar?'))return;
    fetch('/resetar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:email})})
    .then(r=>r.json()).then(d=>{alert(d.msg);if(d.ok)verRelatorio()});
}

function atualizar(){
    fetch('/status').then(r=>r.json()).then(d=>{
        if(!d.conectado&&conectadoIQ){
            conectadoIQ=false;botAtivo=false;
            document.getElementById('btnConectar').style.display='inline-block';
            document.getElementById('btnOperar').style.display='none';
            document.getElementById('btnParar').style.display='none';
            document.getElementById('btnDesconectar').style.display='none';
            document.getElementById('btnConectar').disabled=false;
            document.getElementById('btnConectar').textContent='🔌 CONECTAR';
            document.getElementById('btnOperar').disabled=false;
            document.getElementById('btnOperar').textContent='🚀 COMEÇAR OPERAR';
            document.getElementById('statusTexto').textContent='⏸️ Desconectado';
            document.getElementById('statusDot').className='status-dot inactive';
            if(intervalo)clearInterval(intervalo);
        }
        if(!d.rodando&&botAtivo){
            botAtivo=false;
            document.getElementById('btnOperar').style.display='inline-block';
            document.getElementById('btnDesconectar').style.display='inline-block';
            document.getElementById('btnParar').style.display='none';
            document.getElementById('btnOperar').disabled=false;
            document.getElementById('btnOperar').textContent='🚀 COMEÇAR OPERAR';
            document.getElementById('statusTexto').textContent='🟢 Conectado';
        }
        if(d.banca)document.getElementById('banca').textContent='$'+d.banca.toFixed(2);
        if(d.lucro!==undefined){var el=document.getElementById('lucro');el.textContent='$'+d.lucro.toFixed(2);el.style.color=d.lucro>=0?'#00ff88':'#ff4444';}
        if(d.ops!==undefined)document.getElementById('ops').textContent=d.ops;
        if(d.moedas!==undefined)document.getElementById('moedasSaldo').textContent=d.moedas;
        if(d.sinal)document.getElementById('sinal').textContent=d.sinal;
        if(d.estrategia_nome)document.getElementById('estrategiaAtiva').textContent=d.estrategia_nome;
        if(d.analise){
            document.getElementById('rsi').textContent=d.analise.rsi?d.analise.rsi.toFixed(1):'--';
            document.getElementById('mm5').textContent=d.analise.mm5?d.analise.mm5.toFixed(5):'--';
            document.getElementById('mm10').textContent=d.analise.mm10?d.analise.mm10.toFixed(5):'--';
            document.getElementById('mm20').textContent=d.analise.mm20?d.analise.mm20.toFixed(5):'--';
            document.getElementById('stoch').textContent=d.analise.stoch?d.analise.stoch.toFixed(1):'--';
            document.getElementById('fase').textContent=d.analise.fase||'--';
            document.getElementById('preco').textContent=d.analise.preco?d.analise.preco.toFixed(5):'--';
        }
        if(d.logs)document.getElementById('terminal').innerHTML=d.logs;
        document.getElementById('terminal').scrollTop=document.getElementById('terminal').scrollHeight;
    });
}

window.onload=function(){
    renderEstrategias();
    fetch('/status').then(r=>r.json()).then(d=>{
        if(d.estrategia){estrategiaSel=d.estrategia;renderEstrategias();}
        if(d.estrategia_nome)document.getElementById('estrategiaAtiva').textContent=d.estrategia_nome;
        if(d.conectado&&d.email){
            conectadoIQ=true;emailLogado=d.email;
            document.getElementById('email').value=d.email;
            document.getElementById('btnConectar').style.display='none';
            if(d.rodando){botAtivo=true;document.getElementById('btnOperar').style.display='none';document.getElementById('btnParar').style.display='inline-block';document.getElementById('statusTexto').textContent='🤖 Operando';}
            else{document.getElementById('btnOperar').style.display='inline-block';
            document.getElementById('btnDesconectar').style.display='inline-block';document.getElementById('statusTexto').textContent='🟢 Conectado';}
            document.getElementById('statusDot').className='status-dot active';
            if(intervalo)clearInterval(intervalo);
            intervalo=setInterval(atualizar,2000);atualizar();
        }
    });
}
</script>
</body>
</html>
'''

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
    global skin_atual_global, estrategia_atual
    if email_usuario_atual:
        u = carregar_usuario(email_usuario_atual)
        if u: skin_atual_global = u.get('skin_atual', 'skin_padrao')
    u = carregar_usuario(email_usuario_atual) if email_usuario_atual else {}
    skins_status = []
    skins_compradas = u.get('skins_compradas', ['skin_padrao']) if u else ['skin_padrao']
    skin_atual = u.get('skin_atual', 'skin_padrao') if u else 'skin_padrao'
    for skin in SKINS:
        skins_status.append({'id': skin['id'], 'nome': skin['nome'], 'desc': skin['desc'], 'preco_moedas': skin['preco_moedas'], 'comprado': skin['id'] in skins_compradas, 'ativo': skin['id'] == skin_atual})
    return jsonify({'conectado': conectado_iq, 'rodando': bot_rodando, 'email': email_usuario_atual, 'banca': API.get_balance() if API else 0, 'lucro': lucro, 'ops': NumDeOperacoes, 'sinal': ultimo_sinal, 'analise': ultima_analise, 'logs': get_logs_html(40), 'moedas': u.get('moedas', 0) if u else 0, 'estrategia': estrategia_atual, 'estrategia_nome': ESTRATEGIAS.get(estrategia_atual, {}).get('nome', '--'), 'skin_id': skin_atual, 'skins_status': skins_status})

@app.route('/conectar', methods=['POST'])
def conectar():
    global API, email_usuario_atual, conectado_iq, skin_atual_global, par, timeframe_atual
    try:
        d = request.get_json(); email = d.get('email', '').strip(); senha = d.get('senha', '').strip(); tipo = d.get('tipo', 'PRACTICE')
        if not email or not senha: return jsonify({'ok': False, 'erro': 'Email e senha obrigatórios'})
        email_usuario_atual = email
        usuario = carregar_usuario(email) or criar_usuario(email)
        hoje = str(datetime.now())[:10]
        if usuario.get('moedas_ganhas_hoje') != hoje:
            usuario['moedas'] = usuario.get('moedas', 0) + 1; usuario['moedas_ganhas_hoje'] = hoje
            salvar_usuario(email, usuario)
        skin_atual_global = usuario.get('skin_atual', 'skin_padrao')
        par = ESTRATEGIAS[estrategia_atual]['pares'][0]; timeframe_atual = ESTRATEGIAS[estrategia_atual]['timeframe']
        add_log('🔌 Conectando na IQ Option...', 'info')
        API = IQ_Option(email, senha); status_conn, reason = API.connect()
        if not status_conn: return jsonify({'ok': False, 'erro': str(reason)[:100]})
        API.change_balance(tipo); conectado_iq = True
        add_log(f'✅ Conectado! ${API.get_balance():.2f} | 🪙 {usuario.get("moedas", 0)} moedas', 'win')
        return jsonify({'ok': True, 'moedas': usuario.get('moedas', 0)})
    except Exception as e: return jsonify({'ok': False, 'erro': str(e)[:100]})

@app.route('/comecar_operar', methods=['POST'])
def comecar_operar():
    global bot_rodando, bot_thread, lucro, NumDeOperacoes
    try:
        if not conectado_iq: return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
        usuario = carregar_usuario(email_usuario_atual)
        if not usuario or usuario.get('moedas', 0) < 1: return jsonify({'ok': False, 'erro': 'Sem moedas!'})
        usuario['moedas'] -= 1; usuario['total_ciclos'] += 1; salvar_usuario(email_usuario_atual, usuario)
        lucro = 0.0; NumDeOperacoes = 0
        if not bot_rodando: bot_rodando = True; bot_thread = threading.Thread(target=bot_loop, daemon=True); bot_thread.start()
        return jsonify({'ok': True, 'moedas': usuario['moedas']})
    except Exception as e: return jsonify({'ok': False, 'erro': str(e)[:100]})

@app.route('/parar', methods=['POST'])
def parar():
    global bot_rodando, conectado_iq
    bot_rodando = False; conectado_iq = False; return jsonify({'ok': True})

@app.route('/selecionar_estrategia', methods=['POST'])
def selecionar_estrategia():
    global estrategia_atual, par, timeframe_atual
    d = request.get_json(); est_key = d.get('estrategia', 'v_sensitivo')
    if est_key in ESTRATEGIAS:
        estrategia_atual = est_key; par = ESTRATEGIAS[est_key]['pares'][0]; timeframe_atual = ESTRATEGIAS[est_key]['timeframe']
        return jsonify({'ok': True})
    return jsonify({'ok': False})

@app.route('/comprar_skin', methods=['POST'])
def comprar_skin():
    global skin_atual_global
    d = request.get_json(); skin_id = d.get('skin_id', '')
    if not email_usuario_atual: return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    skin = next((s for s in SKINS if s['id'] == skin_id), None)
    if not skin: return jsonify({'ok': False, 'erro': 'Skin não encontrada'})
    usuario = carregar_usuario(email_usuario_atual)
    if not usuario: return jsonify({'ok': False, 'erro': 'Usuário não encontrado'})
    if skin['preco_moedas'] == 0:
        if 'skins_compradas' not in usuario: usuario['skins_compradas'] = ['skin_padrao']
        if skin_id not in usuario['skins_compradas']: usuario['skins_compradas'].append(skin_id)
        usuario['skin_atual'] = skin_id; salvar_usuario(email_usuario_atual, usuario); skin_atual_global = skin_id
        return jsonify({'ok': True, 'moedas': usuario.get('moedas', 0), 'msg': 'Skin grátis ativada!'})
    if 'skins_compradas' not in usuario: usuario['skins_compradas'] = ['skin_padrao']
    if skin_id in usuario['skins_compradas']:
        usuario['skin_atual'] = skin_id; salvar_usuario(email_usuario_atual, usuario); skin_atual_global = skin_id
        return jsonify({'ok': True, 'moedas': usuario['moedas'], 'msg': 'Skin já comprada! Ativada.'})
    if usuario.get('moedas', 0) < skin['preco_moedas']: return jsonify({'ok': False, 'erro': f'Moedas insuficientes! Precisa de {skin["preco_moedas"]} 🪙'})
    usuario['moedas'] -= skin['preco_moedas']; usuario['skins_compradas'].append(skin_id); usuario['skin_atual'] = skin_id
    salvar_usuario(email_usuario_atual, usuario); skin_atual_global = skin_id
    return jsonify({'ok': True, 'moedas': usuario['moedas'], 'msg': f'Skin {skin["nome"]} comprada e ativada!'})

@app.route('/ativar_skin', methods=['POST'])
def ativar_skin():
    d = request.get_json(); skin_id = d.get('skin_id', '')
    if not email_usuario_atual: return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    skin = next((s for s in SKINS if s['id'] == skin_id), None)
    if not skin: return jsonify({'ok': False, 'erro': 'Skin não encontrada'})
    usuario = carregar_usuario(email_usuario_atual)
    if not usuario: return jsonify({'ok': False, 'erro': 'Usuário não encontrado'})
    if 'skins_compradas' not in usuario: usuario['skins_compradas'] = ['skin_padrao']
    if skin['preco_moedas'] > 0 and skin_id not in usuario['skins_compradas']: return jsonify({'ok': False, 'erro': 'Compre a skin primeiro!'})
    if skin_id not in usuario['skins_compradas']: usuario['skins_compradas'].append(skin_id)
    usuario['skin_atual'] = skin_id; salvar_usuario(email_usuario_atual, usuario)
    global skin_atual_global; skin_atual_global = skin_id
    return jsonify({'ok': True})

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

@app.route('/relatorio')
def relatorio():
    email = request.args.get('email', '')
    if not email: return jsonify({'erro': 'Email obrigatório'})
    u = carregar_usuario(email)
    return jsonify(u if u else {'erro': 'Não encontrado'})

@app.route('/resetar', methods=['POST'])
def resetar():
    d = request.get_json(); email = d.get('email', '')
    if not email: return jsonify({'ok': False, 'msg': 'Email obrigatório'})
    usuario = carregar_usuario(email)
    if not usuario: return jsonify({'ok': False, 'msg': 'Usuário não encontrado'})
    # Mantém moedas, skins e data de cadastro
    moedas = usuario.get('moedas', 0)
    skins_compradas = usuario.get('skins_compradas', ['skin_padrao'])
    skin_atual = usuario.get('skin_atual', 'skin_padrao')
    data_cadastro = usuario.get('data_cadastro', str(datetime.now())[:19])
    # Zera apenas estatísticas
    usuario['total_ciclos'] = 0
    usuario['total_wins'] = 0
    usuario['total_losses'] = 0
    usuario['total_gasto'] = 0.0
    usuario['total_ganho'] = 0.0
    usuario['lucro_total'] = 0.0
    usuario['historico_operacoes'] = []
    usuario['dias_ativos'] = {}
    usuario['banca_atual'] = 0.0
    # Mantém moedas e skins
    usuario['moedas'] = moedas
    usuario['skins_compradas'] = skins_compradas
    usuario['skin_atual'] = skin_atual
    usuario['data_cadastro'] = data_cadastro
    usuario['moedas_ganhas_hoje'] = str(datetime.now())[:10]
    salvar_usuario(email, usuario)
    return jsonify({'ok': True, 'msg': '✅ Estatísticas resetadas! Moedas e skins mantidas.'})

if __name__ == '__main__':
    print("=" * 50)
    print("⚡ TESLA 369 BOT v4.1.1.10 ⚡")
    print("=" * 50)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
