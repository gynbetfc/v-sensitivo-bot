# ═══════════════════════════════════════════════════════
# ⚡ TESLA 369 BOT v7.0.0 - SISTEMA DE PLUGINS ⚡
# Estratégias e Skins carregadas dinamicamente
# ═══════════════════════════════════════════════════════

from flask import Flask, render_template_string, jsonify, request
from iqoptionapi.stable_api import IQ_Option
from datetime import datetime
import threading, time, sys, os, json, warnings, requests, uuid, base64, importlib, glob

warnings.filterwarnings("ignore")
app = Flask(__name__)

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
    }
,
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
        requests.put(f'{FB_URL}/usuarios/{key}.json', json=dados)
    except Exception as e:
        print(f"⚠️ Firebase offline: {e}")

def carregar_usuario(email):
    """Carrega do Firebase"""
    try:
        key = email.replace("@", "_").replace(".", "_").replace("#", "").replace("$", "").replace("[", "").replace("]", "").replace("/", "_")
        r = requests.get(f'{FB_URL}/usuarios/{key}.json')
        if r.status_code == 200 and r.json():
            return r.json()
    except:
        pass
    return None

def criar_usuario(email):
    dados = {
        'email': email,
        'moedas': 1,
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

# ═══════════ CARREGADOR DE PLUGINS ═══════════
def carregar_estrategias():
    """Carrega todas as estratégias da pasta estrategias/"""
    estrategias = {}
    mapa_sinais = {}
    
    for arquivo in glob.glob("estrategias/*.py"):
        if "__init__" in arquivo:
            continue
        
        nome_modulo = arquivo.replace("/", ".").replace("\\", ".")[:-3]
        
        try:
            modulo = importlib.import_module(nome_modulo)
            
            funcao_sinal = None
            for nome in dir(modulo):
                if nome.startswith('sinal_'):
                    funcao_sinal = getattr(modulo, nome)
                    break
            
            info = getattr(modulo, 'ESTRATEGIA_INFO', {
                'nome': nome_modulo.split('.')[-1],
                'descricao': 'Estratégia carregada dinamicamente',
                'timeframe': 60,
                'preco_moedas': 0,
                'gratis': True
            })
            
            estrategia_id = nome_modulo.split('.')[-1]
            estrategias[estrategia_id] = info
            
            if funcao_sinal:
                mapa_sinais[estrategia_id] = funcao_sinal
                print(f"  ✅ Estratégia: {info.get('nome', estrategia_id)}")
            
        except Exception as e:
            print(f"  ❌ Erro {arquivo}: {e}")
    
    return estrategias, mapa_sinais

def carregar_skins():
    """Carrega todas as skins da pasta skins/"""
    skins = []
    
    for arquivo in glob.glob("skins/*.py"):
        if "__init__" in arquivo:
            continue
        
        nome_modulo = arquivo.replace("/", ".").replace("\\", ".")[:-3]
        
        try:
            modulo = importlib.import_module(nome_modulo)
            skin_config = getattr(modulo, 'SKIN_CONFIG', None)
            
            if skin_config:
                skins.append(skin_config)
                print(f"  🎨 Skin: {skin_config.get('id', 'desconhecida')}")
            
        except Exception as e:
            print(f"  ❌ Erro {arquivo}: {e}")
    
    return skins

# Carregar plugins
print("\n📊 Carregando estratégias...")
ESTRATEGIAS, MAPA_SINAIS = carregar_estrategias()

print("\n🎨 Carregando skins...")
SKINS = carregar_skins()

print(f"\n✅ {len(ESTRATEGIAS)} estratégias | {len(SKINS)} skins carregadas")

# ═══════════ VARIÁVEIS GLOBAIS ═══════════
API, par = None, "EURUSD-OTC"
estrategia_atual = list(ESTRATEGIAS.keys())[0] if ESTRATEGIAS else 'tesla_369'
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
bots_ativos = {}

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

def salvar_usuario(email, dados):
    """Salva no Firebase (sem backup local)"""
    try:
        key = email.replace("@", "_").replace(".", "_").replace("#", "").replace("$", "").replace("[", "").replace("]", "").replace("/", "_")
        dados = _sanitizar_dados(dados)
        requests.put(f'{FB_URL}/usuarios/{key}.json', json=dados)
    except Exception as e:
        print(f"⚠️ Firebase offline: {e}")

def carregar_usuario(email):
    """Carrega do Firebase"""
    try:
        key = email.replace("@", "_").replace(".", "_").replace("#", "").replace("$", "").replace("[", "").replace("]", "").replace("/", "_")
        r = requests.get(f'{FB_URL}/usuarios/{key}.json')
        if r.status_code == 200 and r.json():
            return r.json()
    except:
        pass
    return None

def criar_usuario(email):
    dados = {
        'email': email,
        'moedas': 1,
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

# ═══════════ INICIALIZAÇÃO ═══════════
if __name__ == "__main__":
    print("⚡ TESLA 369 BOT v7.0.0")
    print("="*50)
    app.run(host='0.0.0.0', port=5000, debug=False)
