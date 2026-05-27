# ═══════════════════════════════════════════════════════
# ⚡ TESLA 369 BOT v7.0 - LEITURA DINÂMICA DO GITHUB ⚡
# Estratégias e Skins são carregadas em tempo real do GitHub
# ═══════════════════════════════════════════════════════

from flask import Flask, render_template_string, jsonify, request
from iqoptionapi.stable_api import IQ_Option
from datetime import datetime
import threading, time, sys, os, json, warnings, requests, uuid, base64

warnings.filterwarnings("ignore")
app = Flask(__name__)

# ═══════════ CONFIGURAÇÕES ═══════════
FB_URL = "https://nexos-40654-default-rtdb.firebaseio.com"
MARTINGALE = 2
PAYOUT_PADRAO = 0.85
PERCENTUAL_BANCA = 15
MERCADO_PAGO_ACCESS_TOKEN = os.environ.get("MP_ACCESS_TOKEN", "")
MODO_SIMULACAO = False

# ═══════════ GITHUB RAW URLS ═══════════
GITHUB_RAW = "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/tesla_369"
GITHUB_API = "https://api.github.com/repos/gynbetfc/v-sensitivo-bot/contents/tesla_369"

# Cache para evitar muitas requisições
_cache_estrategias = {}
_cache_skins = {}
_cache_tempo = {}
CACHE_DURACAO = 300  # 5 minutos

# ═══════════ CARREGADOR DINÂMICO DO GITHUB ═══════════
def carregar_do_github(caminho):
    """Carrega arquivo Python diretamente do GitHub"""
    url = f"{GITHUB_RAW}/{caminho}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.text
    except Exception as e:
        print(f"  ❌ Erro ao carregar {caminho}: {e}")
    return None

def listar_arquivos_github(pasta):
    """Lista arquivos .py de uma pasta no GitHub"""
    url = f"{GITHUB_API}/{pasta}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return [f['name'] for f in r.json() if f['name'].endswith('.py')]
    except:
        pass
    return []

def carregar_estrategia(nome_arquivo):
    """Carrega uma estratégia específica do GitHub"""
    global _cache_estrategias, _cache_tempo
    
    agora = time.time()
    
    # Verificar cache
    if nome_arquivo in _cache_estrategias:
        if agora - _cache_tempo.get(nome_arquivo, 0) < CACHE_DURACAO:
            return _cache_estrategias[nome_arquivo]
    
    codigo = carregar_do_github(f"estrategias/{nome_arquivo}")
    if codigo:
        # Executar código para extrair função e metadados
        namespace = {}
        try:
            exec(codigo, namespace)
            
            # Procurar função de sinal
            funcao_sinal = None
            for nome, obj in namespace.items():
                if nome.startswith('sinal_') and callable(obj):
                    funcao_sinal = obj
                    break
            
            info = namespace.get('ESTRATEGIA_INFO', {
                'nome': nome_arquivo.replace('.py', ''),
                'descricao': 'Carregada do GitHub',
                'preco_moedas': 0,
                'gratis': True
            })
            
            resultado = {
                'info': info,
                'funcao': funcao_sinal,
                'codigo': codigo
            }
            
            # Salvar no cache
            _cache_estrategias[nome_arquivo] = resultado
            _cache_tempo[nome_arquivo] = agora
            
            return resultado
            
        except Exception as e:
            print(f"  ❌ Erro ao executar {nome_arquivo}: {e}")
    
    return None

def carregar_skin(nome_arquivo):
    """Carrega uma skin específica do GitHub"""
    global _cache_skins, _cache_tempo
    
    agora = time.time()
    
    # Verificar cache
    if nome_arquivo in _cache_skins:
        if agora - _cache_tempo.get(nome_arquivo, 0) < CACHE_DURACAO:
            return _cache_skins[nome_arquivo]
    
    codigo = carregar_do_github(f"skins/{nome_arquivo}")
    if codigo:
        namespace = {}
        try:
            exec(codigo, namespace)
            skin_config = namespace.get('SKIN_CONFIG')
            
            if skin_config:
                _cache_skins[nome_arquivo] = skin_config
                _cache_tempo[nome_arquivo] = agora
                return skin_config
        except Exception as e:
            print(f"  ❌ Erro ao carregar skin {nome_arquivo}: {e}")
    
    return None

def carregar_todas_estrategias():
    """Carrega lista de todas as estratégias disponíveis no GitHub"""
    arquivos = listar_arquivos_github("estrategias")
    estrategias = {}
    
    for arquivo in arquivos:
        resultado = carregar_estrategia(arquivo)
        if resultado and resultado['info']:
            est_id = arquivo.replace('.py', '')
            estrategias[est_id] = resultado['info']
    
    return estrategias

def carregar_todas_skins():
    """Carrega lista de todas as skins disponíveis no GitHub"""
    arquivos = listar_arquivos_github("skins")
    skins = []
    
    for arquivo in arquivos:
        skin = carregar_skin(arquivo)
        if skin:
            skins.append(skin)
    
    return skins

# ═══════════ CARREGAR LISTAS NA INICIALIZAÇÃO ═══════════
print("📊 Conectando ao GitHub...")
print("="*50)

try:
    ESTRATEGIAS = carregar_todas_estrategias()
    print(f"✅ {len(ESTRATEGIAS)} estratégias encontradas no GitHub")
    
    SKINS = carregar_todas_skins()
    print(f"✅ {len(SKINS)} skins encontradas no GitHub")
    
except Exception as e:
    print(f"⚠️ Erro ao conectar ao GitHub: {e}")
    print("📦 Usando fallback local...")
    
    # Fallback básico se GitHub estiver offline
    def sinal_tesla_369():
        global ultimo_sinal, ultima_analise
        try:
            agora = datetime.now()
            if not ((agora.minute >= 1.55 and agora.minute <= 2) or (agora.minute >= 6.55 and agora.minute <= 7)):
                ultimo_sinal = f"⏳ Min: {agora.minute}:{agora.second:02d}"
                return None
            v = API.get_candles(par, timeframe_atual, 6, time.time())
            if len(v) < 6: return None
            velas = []
            for vela in v:
                if vela['open'] < vela['close']: velas.append('g')
                elif vela['open'] > vela['close']: velas.append('r')
                else: velas.append('d')
            cores = ''.join(velas)
            ultimo_sinal = f"⚡ 369: {cores}"
            if velas[0] == 'g' and velas[3] == 'g' and velas[4] == 'r' and velas[5] == 'r' and 'd' not in cores:
                return 'call'
            if velas[0] == 'r' and velas[3] == 'r' and velas[4] == 'g' and velas[5] == 'g' and 'd' not in cores:
                return 'put'
            return None
        except:
            return None
    
    ESTRATEGIAS = {
        'tesla_369': {'nome': '⚡ TESLA-369', 'desc': '6 velas padrão', 'preco_moedas': 0, 'gratis': True}
    }
    SKINS = []

# ═══════════ MAPA DE SINAIS (Carregado sob demanda) ═══════════
MAPA_SINAIS = {}

def obter_funcao_sinal(estrategia_id):
    """Obtém função de sinal do GitHub em tempo real"""
    if estrategia_id in MAPA_SINAIS:
        return MAPA_SINAIS[estrategia_id]
    
    # Carregar do GitHub
    resultado = carregar_estrategia(f"{estrategia_id}.py")
    if resultado and resultado['funcao']:
        MAPA_SINAIS[estrategia_id] = resultado['funcao']
        return resultado['funcao']
    
    return None

# ═══════════ VARIÁVEIS GLOBAIS ═══════════
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
bots_ativos = {}

# ═══════════ FUNÇÕES DO BOT ═══════════
def add_log(msg, tipo='info'):
    global logs_web
    t = datetime.now().strftime('%H:%M:%S')
    logs_web.append({'time': t, 'msg': msg, 'tipo': tipo})
    if len(logs_web) > MAX_LOGS_WEB:
        logs_web = logs_web[-MAX_LOGS_WEB:]
    print(f"{t} - {msg}")

# ═══════════ ROTA PARA LISTAR ESTRATÉGIAS DO GITHUB ═══════════
@app.route('/api/estrategias')
def api_estrategias():
    """Retorna lista de estratégias (recarrega do GitHub se necessário)"""
    global ESTRATEGIAS
    
    # Forçar recarregar do GitHub
    force = request.args.get('force', '0') == '1'
    if force:
        print("🔄 Forçando recarga do GitHub...")
        ESTRATEGIAS = carregar_todas_estrategias()
    
    return jsonify(ESTRATEGIAS)

@app.route('/api/skins')
def api_skins():
    """Retorna lista de skins (recarrega do GitHub se necessário)"""
    global SKINS
    
    force = request.args.get('force', '0') == '1'
    if force:
        print("🔄 Forçando recarga de skins...")
        SKINS = carregar_todas_skins()
    
    return jsonify(SKINS)

@app.route('/api/estrategia/<estrategia_id>')
def api_estrategia_codigo(estrategia_id):
    """Retorna código fonte de uma estratégia do GitHub"""
    codigo = carregar_do_github(f"estrategias/{estrategia_id}.py")
    if codigo:
        return jsonify({'codigo': codigo, 'id': estrategia_id})
    return jsonify({'erro': 'Estratégia não encontrada'}), 404

# ═══════════ INICIALIZAÇÃO ═══════════
print("\n⚡ TESLA 369 BOT v7.0")
print("🌐 Modo: Leitura dinâmica do GitHub")
print("="*50)
print(f"📊 {len(ESTRATEGIAS)} estratégias disponíveis")
print(f"🎨 {len(SKINS)} skins disponíveis")
print("💡 As estratégias são carregadas em tempo real do GitHub")
print("🚀 Iniciando servidor...")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
