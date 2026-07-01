#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ⚡ TESLA 369 BOT v16.0.0 - MULTI-SESSAO + RECONEXAO ROBUSTA ⚡
# Firebase: SKINS e ESTRATEGIAS carregadas da nuvem
# ENTRADA: guarda ID da ordem (referencia)
# RESULTADO: comparacao de saldo APOS 60 segundos
# GALES: executados imediatamente (sem aguardar inicio de vela)
# 🔧 v16.0.0 - CADA USUARIO TEM SUA PROPRIA SESSAO (API, bot, logs, conexao)
#              N dispositivos na mesma rede podem operar ao mesmo tempo sem
#              um atrapalhar o outro. So muda ONDE o estado mora — a logica
#              de trading, martingale, VOLTS e stop gain e a MESMA de antes.

from flask import Flask, render_template, jsonify, request
from iqoptionapi.stable_api import IQ_Option
from datetime import datetime
import threading
import time
import os
import warnings
import requests
import uuid
import signal
import random

warnings.filterwarnings("ignore")
app = Flask(__name__)

# ============= VERSÃO DO BOT =============
BOT_VERSION = "16.0.0"
BOT_NAME = "TESLA-369"

# ============= CONFIGURACOES =============
FB_URL = "https://nexos-40654-default-rtdb.firebaseio.com"
print("✅ Firebase HTTP REST configurado!")

MARTINGALE = 2
PAYOUT_PADRAO = 0.85
PERCENTUAL_BANCA_PADRAO = 15  # valor inicial pra sessoes novas; cada usuario pode ajustar o seu depois

MERCADO_PAGO_ACCESS_TOKEN = os.environ.get("MP_ACCESS_TOKEN", "")
if not MERCADO_PAGO_ACCESS_TOKEN:
    print("⚠️ MP_ACCESS_TOKEN nao definido nas variaveis de ambiente!")
MODO_SIMULACAO = False

PLANOS = [
    {'id':1,'moedas':1,'preco':0.99,'nome':'🔰 TESTE','desc':'R$0,99/VOLT','tag':'1 ciclo','bonus':''},
    {'id':2,'moedas':6,'preco':6.69,'nome':'⭐ BASICO','desc':'R$1,11/VOLT','tag':'6 ciclos','bonus':''},
    {'id':3,'moedas':15,'preco':9.99,'nome':'💎 INTERMEDIARIO','desc':'R$0,67/VOLT','tag':'15 ciclos','bonus':'🎨 1 Skin Basica GRATIS','desconto':'33% OFF'},
    {'id':4,'moedas':36,'preco':21.69,'nome':'🔥 PREMIUM','desc':'R$0,60/VOLT','tag':'36 ciclos','bonus':'🎨 1 Skin Premium GRATIS','desconto':'40% OFF'},
    {'id':5,'moedas':69,'preco':39.69,'nome':'👑 ULTRA','desc':'R$0,57/VOLT','tag':'69 ciclos','bonus':'🎨 1 Skin Lendaria GRATIS','desconto':'69% OFF'},
]

# ============= CACHES GLOBAIS (compartilhados entre usuarios, dados nao mudam por pessoa) =============
cache_skins = {"data": None, "timestamp": 0}
cache_estrategias_info = {"data": {}, "timestamp": 0}
CACHE_TTL = 300

# Cache de FUNCOES de estrategia ja "exec"-utadas, compartilhado entre sessoes.
# Isso evita re-executar exec() do mesmo codigo pra cada usuario que usa a
# mesma estrategia — o codigo e o mesmo, so quem chama a funcao muda.
estrategias_funcoes_cache = {}   # nome_estrategia -> {'funcao': fn, 'timestamp': t}
estrategias_funcoes_lock = threading.Lock()

pagamentos_pendentes = {}
pagamentos_lock = threading.Lock()

MAX_LOGS_WEB = 200
MAX_ERROS_ANTES_RECONECTAR = 10
SESSAO_TIMEOUT_SEGUNDOS = 3600 * 6   # sessoes inativas ha 6h sao limpas da memoria

# ============================================================================
# ============= SESSAO POR USUARIO (o coração do isolamento) ===============
# ============================================================================
# Cada dispositivo/usuario que faz /conectar ganha um objeto Sessao só dele.
# Nada aqui é global — dois usuários rodando ao mesmo tempo têm APIs, bots,
# logs e conexões completamente separados dentro do MESMO processo Flask.

class Sessao:
    def __init__(self, email):
        self.email = email
        self.API = None
        self.par = "EURUSD-OTC"
        self.timeframe_atual = 60
        self.lucro = 0.0
        self.NumDeOperacoes = 0
        self.BANCA_INICIAL_DO_BOT = 0
        self.STOP_GAIN_ATINGIDO = False
        self.bot_rodando = False
        self.bot_thread = None
        self.conectado_iq = False
        self.ultimo_sinal = "Aguardando..."
        self.ultima_analise = {}
        self.logs_web = []
        self.skin_atual = 'skin_padrao'
        self.estrategia_atual = 'v_sensitivo'
        self.sinal_pendente = None
        self.sinal_lock = threading.Lock()
        self.volt_ja_consumido = False
        self.ordem_id_atual = None
        self.tipo_conta_atual = "PRACTICE"
        self.percentual_banca = PERCENTUAL_BANCA_PADRAO  # por sessao — o ajuste de um usuario nao afeta o de outro
        self.senha = None  # guardada em memoria só pra permitir reconexão do zero (ver nota de segurança no final)

        # ===== CONFIG DE OPERACAO (escolhas do USUARIO, nao da estrategia) =====
        # usar_config_padrao=True => usa o que a estrategia sugere (gales/timeframe).
        # False => usa os overrides abaixo.
        self.usar_config_padrao = True
        self.gales_override = 2              # usado só quando usar_config_padrao=False
        self.auto_par = True                 # True => bot escolhe o melhor par OTC; False => usa self.par
        self.modo_entrada = 'calculo'        # 'calculo' (recomendado) ou 'fixa'
        self.mao_fixa_valor = 2.0            # valor em $ quando modo_entrada='fixa'
        self.melhor_par_info = {}            # ultimo resultado do auto-par (pra mostrar na tela)

        self.bot_lock = threading.Lock()          # protege iniciar/parar bot desta sessao
        self.conexao_lock = threading.Lock()       # protege conectar_iq/verificar_saude desta sessao

        self.erros_consecutivos_api = 0
        self.ultimo_ping_sucesso = time.time()
        self.reconectando = False
        self.reconexao_evento = threading.Event()   # permite threads esperarem sem "chutar" reconexao alheia
        self.reconexao_evento.set()  # começa "livre" (ninguém reconectando)

        self.criado_em = time.time()
        self.ultimo_acesso = time.time()


sessoes = {}
sessoes_global_lock = threading.Lock()


def get_sessao(email):
    """Retorna a sessao do usuario, criando se ainda nao existir.
    E' isso que garante que o dispositivo A nunca ve/mexe no estado do B."""
    email = (email or "").strip().lower()
    if not email:
        return None
    with sessoes_global_lock:
        if email not in sessoes:
            sessoes[email] = Sessao(email)
        sessoes[email].ultimo_acesso = time.time()
        return sessoes[email]


def limpar_sessoes_inativas():
    """Roda em background: libera memoria de sessoes esquecidas (sem fechar
    bots que ainda estejam rodando de verdade)."""
    while True:
        time.sleep(600)
        agora = time.time()
        with sessoes_global_lock:
            para_remover = [
                email for email, s in sessoes.items()
                if not s.bot_rodando and (agora - s.ultimo_acesso) > SESSAO_TIMEOUT_SEGUNDOS
            ]
            for email in para_remover:
                del sessoes[email]
        if para_remover:
            print(f"🧹 {len(para_remover)} sessao(oes) inativa(s) removida(s) da memoria")


# ============= FUNCOES AUXILIARES (agora recebem a sessao) =============

def add_log(sessao, msg, tipo='info'):
    t = datetime.now().strftime('%H:%M:%S')
    sessao.logs_web.append({'time': t, 'msg': msg, 'tipo': tipo})
    if len(sessao.logs_web) > MAX_LOGS_WEB:
        sessao.logs_web = sessao.logs_web[-MAX_LOGS_WEB:]
    print(f"[{sessao.email}] {t} - {msg}")

def get_logs_html(sessao, limite=40):
    html = ''
    for log in sessao.logs_web[-limite:]:
        cor = {'win': '#00ff88', 'loss': '#ff4444', 'info': '#00ff88', 'sensitive': '#ff69b4', 'indicator': '#ffd700', 'error': '#ff4444'}.get(log['tipo'], '#00ff88')
        html += f'<span style="color:#666">{log["time"]}</span> <span style="color:{cor}">{log["msg"]}</span>\n'
    return html or '📡 Aguardando...'

def get_close(vela):
    if 'close' in vela: return vela['close']
    elif 'max' in vela: return vela['max']
    return 0

def get_high(vela):
    if 'high' in vela: return vela['high']
    elif 'max' in vela: return vela['max']
    return 0

def get_low(vela):
    if 'low' in vela: return vela['low']
    elif 'min' in vela: return vela['min']
    return 0

def calcular_rsi(velas, periodo=14):
    if len(velas) < periodo + 1: return 50
    ganhos, perdas = [], []
    for i in range(1, len(velas)):
        diferenca = get_close(velas[i]) - get_close(velas[i-1])
        if diferenca >= 0:
            ganhos.append(diferenca); perdas.append(0)
        else:
            ganhos.append(0); perdas.append(abs(diferenca))
    ganhos = ganhos[-periodo:]
    perdas = perdas[-periodo:]
    ganho_medio = sum(ganhos) / periodo if ganhos else 0
    perda_media = sum(perdas) / periodo if perdas else 0
    if perda_media == 0: return 100
    rs = ganho_medio / perda_media
    return 100 - (100 / (1 + rs))

def calcular_estocastico(velas, periodo_k=14):
    if len(velas) < periodo_k: return 50
    ultimas_velas = velas[-periodo_k:]
    maior_alta = max(get_high(v) for v in ultimas_velas)
    menor_baixa = min(get_low(v) for v in ultimas_velas)
    ultimo_fechamento = get_close(velas[-1])
    if maior_alta == menor_baixa: return 50
    return 100 * ((ultimo_fechamento - menor_baixa) / (maior_alta - menor_baixa))

def calcular_media_movel(velas, periodo):
    if len(velas) < periodo: return get_close(velas[-1]) if velas else 0
    return sum(get_close(v) for v in velas[-periodo:]) / periodo

# ============= SKINS NO FIREBASE (dados compartilhados, sem mudanca) =============

def get_skins_fallback():
    return {
        'skin_padrao': {
            'id': 'skin_padrao', 'nome': '⚡ TESLA THUNDER', 'desc': 'Raios eletricos na tela - Skin Padrao',
            'preco_moedas': 0, 'categoria': 'lendaria',
            'cor_fundo': '#000011', 'cor_panel': '#0a0a1a', 'cor_destaque': '#ffff00', 'cor_texto': '#ffffff',
            'cor_botao': 'linear-gradient(135deg,#aaaa00,#ffff00)', 'cor_tab_ativa': '#ffff00',
            'cor_header_bg': 'linear-gradient(135deg,#000011,#111122,#222244,#111122,#000011)', 'cor_header_borda': '#ffff00',
            'header_extra': '<canvas id="thunderCanvas" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:1;pointer-events:none"></canvas>',
            'css_extra': 'body{background:#000011!important}.header{border-color:#ffff00!important;box-shadow:0 0 50px rgba(255,255,0,0.3)}'
        }
    }

def carregar_skin_do_firebase(skin_id):
    try:
        key = skin_id.replace(".", "_").replace("@", "_").replace("#", "")
        r = requests.get(f'{FB_URL}/tesla_369/skins/{key}.json', timeout=5)
        if r.status_code == 200 and r.json():
            skin_data = r.json()
            skin_data['id'] = skin_id
            return skin_data
    except Exception as e:
        print(f"⚠️ Erro ao carregar skin {skin_id}: {e}")
    return None

def carregar_todas_skins_do_firebase():
    global cache_skins
    agora = time.time()
    if cache_skins["data"] and (agora - cache_skins["timestamp"]) < CACHE_TTL:
        return cache_skins["data"]
    try:
        r = requests.get(f'{FB_URL}/tesla_369/skins.json', timeout=5)
        if r.status_code == 200 and r.json():
            skins_dict = r.json()
            skins_list = []
            for skin_id, skin_data in skins_dict.items():
                skin_data['id'] = skin_id
                skins_list.append(skin_data)
            cache_skins["data"] = skins_list
            cache_skins["timestamp"] = agora
            print(f"✅ {len(skins_list)} skins carregadas do Firebase!")
            return skins_list
    except Exception as e:
        print(f"⚠️ Erro ao carregar skins: {e}")

    fallback_skins = list(get_skins_fallback().values())
    cache_skins["data"] = fallback_skins
    cache_skins["timestamp"] = agora
    return fallback_skins

# ============= ESTRATEGIAS NO FIREBASE =============

def carregar_informacoes_estrategias():
    global cache_estrategias_info
    agora = time.time()
    if cache_estrategias_info["data"] and (agora - cache_estrategias_info["timestamp"]) < CACHE_TTL:
        return cache_estrategias_info["data"]
    try:
        r = requests.get(f'{FB_URL}/tesla_369/estrategias.json', timeout=5)
        if r.status_code == 200 and r.json():
            estrategias_dict = r.json()
            estrategias_info = {}
            for nome_est, dados in estrategias_dict.items():
                info = dados.get('info', {})
                estrategias_info[nome_est] = {
                    'nome': info.get('nome', nome_est.upper()),
                    'desc': info.get('desc', 'Sem descricao.'),
                    'preco_moedas': info.get('preco', 0),
                    'timeframe': info.get('timeframe', 60),
                    'gratis': info.get('preco', 0) == 0
                }
            cache_estrategias_info["data"] = estrategias_info
            cache_estrategias_info["timestamp"] = agora
            print(f"✅ {len(estrategias_info)} estrategias carregadas do Firebase!")
            return estrategias_info
    except Exception as e:
        print(f"⚠️ Erro ao carregar estrategias: {e}")
    return {}

def carregar_estrategia_do_firebase(nome_estrategia):
    try:
        key = nome_estrategia.replace(".", "_").replace("@", "_").replace("#", "")
        r = requests.get(f'{FB_URL}/tesla_369/estrategias/{key}.json', timeout=5)
        if r.status_code == 200 and r.json():
            dados = r.json()
            return {'codigo': dados.get('codigo', ''), 'info': dados.get('info', {})}
    except Exception as e:
        print(f"⚠️ Erro ao carregar estrategia {nome_estrategia}: {e}")
    return None

def obter_funcao_estrategia(nome_estrategia):
    """Cache COMPARTILHADO de funcoes ja carregadas. Duas sessoes usando a
    mesma estrategia reaproveitam o mesmo exec() em vez de repetir o trabalho."""
    agora = time.time()
    with estrategias_funcoes_lock:
        cached = estrategias_funcoes_cache.get(nome_estrategia)
        if cached and (agora - cached['timestamp']) < CACHE_TTL:
            return cached['funcao']

    estrategia_data = carregar_estrategia_do_firebase(nome_estrategia)
    if not estrategia_data:
        return None
    codigo = estrategia_data.get('codigo')
    if not codigo or 'def rodar_analise' not in codigo:
        return None
    try:
        escopo = {}
        exec(codigo, escopo)
        fn = escopo.get('rodar_analise')
        if fn:
            with estrategias_funcoes_lock:
                estrategias_funcoes_cache[nome_estrategia] = {'funcao': fn, 'timestamp': agora}
            return fn
    except Exception as e:
        print(f"❌ Erro ao executar estrategia '{nome_estrategia}': {e}")
    return None

# ========== FUNCOES DE USUARIO (FIREBASE) — dados persistidos, sem mudanca ==========

def salvar_usuario(email, dados):
    try:
        key = email.replace("@", "_").replace(".", "_").replace("#", "").replace("$", "").replace("[", "").replace("]", "").replace("/", "_")
        requests.put(f'{FB_URL}/tesla_369/usuarios/{key}.json', json=dados, timeout=5)
    except Exception as e:
        print(f"⚠️ Erro ao salvar usuario {email}: {e}")

def carregar_usuario(email):
    try:
        key = email.replace("@", "_").replace(".", "_").replace("#", "").replace("$", "").replace("[", "").replace("]", "").replace("/", "_")
        r = requests.get(f'{FB_URL}/tesla_369/usuarios/{key}.json', timeout=5)
        if r.status_code == 200 and r.json(): return r.json()
    except Exception as e:
        print(f"⚠️ Erro ao carregar usuario {email}: {e}")
    return None

def criar_usuario(email):
    dados = {
        'email': email, 'moedas': 12, 'moedas_ganhas_hoje': str(datetime.now())[:10],
        'total_ciclos': 0, 'total_wins': 0, 'total_losses': 0, 'total_gasto': 0.0, 'total_ganho': 0.0,
        'lucro_total': 0.0, 'banca_atual': 0.0, 'data_cadastro': str(datetime.now())[:19],
        'historico_operacoes': [], 'dias_ativos': 0, 'skin_atual': 'skin_padrao',
        'skins_compradas': ['skin_padrao'], 'estrategia_atual': 'v_sensitivo', 'estrategias_compradas': ['v_sensitivo']
    }
    salvar_usuario(email, dados)
    return dados

# ========== FUNCOES DO BOT (recebem `sessao` — nada de estado global aqui) ==========

def Payout(sessao, p):
    try:
        if not sessao.API: return PAYOUT_PADRAO
        sessao.API.subscribe_strike_list(p, 1)
        try:
            # espera no maximo ~3s por par (6 x 0.5s) em vez de 10s — o scan
            # inteiro fica leve e nao segura o socket por muito tempo
            for _ in range(6):
                d = sessao.API.get_digital_current_profit(p, 1)
                if d != False:
                    return round(int(d) / 100, 2)
                time.sleep(0.5)
            return PAYOUT_PADRAO
        finally:
            # unsubscribe SEMPRE, mesmo se der erro/timeout — senao ficam
            # varias subscriptions penduradas afogando a conexao
            try: sessao.API.unsubscribe_strike_list(p, 1)
            except Exception: pass
    except: return PAYOUT_PADRAO

def calcular_entradas(b, p, g, percentual_banca):
    bs = (b * percentual_banca / 100) * 0.99
    e0 = bs / sum((1/p)**i for i in range(g+1))
    entradas = [e0]
    for i in range(1, g+1):
        entradas.append((sum(entradas) + e0) / p)
    ajuste = bs / sum(entradas)
    entradas = [round(e * ajuste, 2) for e in entradas]
    if sum(entradas) > b:
        entradas[-1] = round(entradas[-1] - (sum(entradas) - b) - 0.02, 2)
    return [max(1, e) for e in entradas]

# ===================== PARES OTC + AUTO-PAR =====================
# Cache curto de pares OTC abertos (compartilhado — nao muda por usuario).
cache_pares_otc = {"data": [], "timestamp": 0}
CACHE_PARES_TTL = 60

# Pares de CAMBIO OTC que a lib iqoptionapi reconhece de forma confiavel.
# A conta lista ~179 ativos OTC (acoes, cripto, indices...), mas boa parte
# retorna "Asset X not found on consts" e/ou trava o Payout, afogando o
# websocket ate a corretora derrubar a conexao. Entao o auto-par so testa
# esta lista curta de forex OTC — que e o foco do bot e o que a lib suporta.
PARES_OTC_CONFIAVEIS = [
    "EURUSD-OTC", "GBPUSD-OTC", "USDJPY-OTC", "AUDUSD-OTC", "USDCHF-OTC",
    "EURGBP-OTC", "EURJPY-OTC", "NZDUSD-OTC", "AUDCAD-OTC", "EURUSD-OTC"
]
MAX_PARES_AUTO = 8   # teto rigido: nunca testa mais que isso, pra nao afogar o socket

def listar_pares_otc(sessao):
    """Lista pares OTC ABERTOS agora, MAS filtrando pela whitelist de forex
    que a lib reconhece. Sem isso o auto-par tentava 179 ativos e derrubava
    a conexao."""
    global cache_pares_otc
    agora = time.time()
    if cache_pares_otc["data"] and (agora - cache_pares_otc["timestamp"]) < CACHE_PARES_TTL:
        return cache_pares_otc["data"]
    abertos_set = set()
    try:
        abertos = sessao.API.get_all_open_time()
        for tipo in ('turbo', 'binary'):
            if tipo in abertos:
                for par, info in abertos[tipo].items():
                    if par.endswith('-OTC') and info.get('open'):
                        abertos_set.add(par)
    except Exception as e:
        print(f"⚠️ Erro ao listar pares OTC: {e}")

    # so mantem os da whitelist que estao REALMENTE abertos agora (preserva ordem, sem duplicar)
    pares = []
    for p in PARES_OTC_CONFIAVEIS:
        if p in pares:
            continue
        if not abertos_set or p in abertos_set:
            pares.append(p)
    if not pares:
        pares = ["EURUSD-OTC"]  # fallback minimo
    cache_pares_otc["data"] = pares
    cache_pares_otc["timestamp"] = agora
    return pares

def escolher_melhor_par(sessao, funcao_estrategia, pares_candidatos=None):
    """Escolhe o par OTC com melhor PAYOUT atual (fato concreto), usando a
    atividade da estrategia so como leve desempate. Testa NO MAXIMO
    MAX_PARES_AUTO pares, com uma pausa entre cada um pra nao sobrecarregar
    o websocket da IQ (foi isso que derrubava a conexao antes)."""
    pares = pares_candidatos or listar_pares_otc(sessao)
    pares = pares[:MAX_PARES_AUTO]  # teto rigido
    ranking = []
    add_log(sessao, f"🔎 Testando {len(pares)} pares OTC (payout)...", 'indicator')
    for par in pares:
        if not sessao.bot_rodando:
            break
        try:
            payout = Payout(sessao, par)
            if payout <= 0:
                continue
            deu_sinal = False
            try:
                res = funcao_estrategia(sessao.API, par, lambda m, t='info': None)
                deu_sinal = bool(res and res.get('direcao', '').lower() in ('call', 'put'))
            except Exception:
                deu_sinal = False
            score = payout + (0.02 if deu_sinal else 0)
            ranking.append({'par': par, 'payout': payout, 'sinal_agora': deu_sinal, 'score': score})
        except Exception:
            continue
        time.sleep(0.5)  # respiro entre pares — evita afogar o socket

    if not ranking:
        # nao conseguiu testar nenhum (conexao ruim?) — nao troca o par, segue com o atual
        add_log(sessao, "⚠️ Auto-par não obteve payouts; mantendo par atual.", 'error')
        return None
    ranking.sort(key=lambda x: x['score'], reverse=True)
    melhor = ranking[0]
    sessao.melhor_par_info = {
        'par': melhor['par'],
        'payout': round(melhor['payout'] * 100, 1),
        'testados': len(ranking)
    }
    add_log(sessao, f"🏆 Melhor par: {melhor['par']} (payout {round(melhor['payout']*100,1)}%)", 'win')
    return melhor['par']


def aguardar_inicio_vela(sessao):
    add_log(sessao, "   ⏳ Aguardando inicio da vela...", 'info')
    while datetime.now().second > 5:
        if not sessao.bot_rodando: return False
        time.sleep(0.3)
    add_log(sessao, "   ✅ Vela confirmada!", 'info')
    return True

def consumir_volt(sessao):
    if sessao.volt_ja_consumido: return True
    usuario = carregar_usuario(sessao.email)
    if not usuario or usuario.get('moedas', 0) < 1: return False
    usuario['moedas'] -= 1
    usuario['total_ciclos'] = usuario.get('total_ciclos', 0) + 1
    salvar_usuario(sessao.email, usuario)
    sessao.volt_ja_consumido = True
    add_log(sessao, f"⚡ 1 VOLT consumido. Saldo: {usuario['moedas']} VOLTS", 'info')
    return True

# ========== 🔥 RECONEXÃO ROBUSTA POR SESSÃO ==========

def _login_do_zero(sessao):
    """Ultimo recurso: recria o objeto IQ_Option inteiro. Necessario porque,
    apos uma troca real de rede/IP, o websocket interno as vezes fica 'zumbi'
    e check_connect()/connect() na MESMA instancia nao percebem."""
    if not sessao.senha:
        return False
    try:
        nova_api = IQ_Option(sessao.email, sessao.senha)
        ok, motivo = nova_api.connect()
        if ok:
            nova_api.change_balance(sessao.tipo_conta_atual)
            sessao.API = nova_api
            return True
        add_log(sessao, f"❌ Falha ao recriar sessao: {motivo}", 'error')
    except Exception as e:
        add_log(sessao, f"❌ Erro ao recriar sessao: {e}", 'error')
    return False

def conectar_iq(sessao):
    """Tenta reconectar com backoff exponencial + fallback pra recriar a sessao.
    Usa reconexao_evento pra que OUTRAS threads da MESMA sessao esperem o
    resultado em vez de assumir falha na hora (isso e o que causava o bot
    'desistir' errado quando o monitor ja estava reconectando)."""
    if not sessao.email:
        return False

    # Ja tem uma reconexao rolando PARA ESTA SESSAO? Espera o resultado
    # em vez de competir ou desistir.
    if not sessao.conexao_lock.acquire(blocking=False):
        sessao.reconexao_evento.wait(timeout=40)
        return sessao.conectado_iq

    sessao.reconexao_evento.clear()
    try:
        tentativas = 0
        max_tentativas = 5
        while tentativas < max_tentativas:
            try:
                if sessao.API and sessao.API.check_connect():
                    sessao.conectado_iq = True
                    sessao.erros_consecutivos_api = 0
                    add_log(sessao, "✅ Reconectado com sucesso!", 'win')
                    return True
            except Exception:
                pass

            tentativas += 1
            tempo_espera = min(30, 2 ** tentativas)
            add_log(sessao, f"🔄 Tentativa {tentativas}/{max_tentativas} de reconexão em {tempo_espera}s...", 'info')
            time.sleep(tempo_espera)

            try:
                if sessao.API:
                    sessao.API.connect()
                    time.sleep(2)
                    if sessao.tipo_conta_atual:
                        sessao.API.change_balance(sessao.tipo_conta_atual)
            except Exception as e:
                add_log(sessao, f"   (tentativa falhou: {str(e)[:60]})", 'info')

        # Esgotou as tentativas normais: plano B, recriar a sessao do zero
        add_log(sessao, "🔧 Tentando recriar a sessão do zero (rede pode ter mudado)...", 'info')
        if _login_do_zero(sessao):
            sessao.conectado_iq = True
            sessao.erros_consecutivos_api = 0
            add_log(sessao, "✅ Sessão recriada e reconectada!", 'win')
            return True

    except Exception as e:
        add_log(sessao, f"❌ Erro durante reconexão: {e}", 'error')
    finally:
        sessao.reconexao_evento.set()
        sessao.conexao_lock.release()

    sessao.conectado_iq = False
    add_log(sessao, f"❌ Falha na reconexão!", 'error')
    return False

def verificar_saude_api(sessao):
    if not sessao.API or not sessao.email:
        return False
    if sessao.conexao_lock.locked():
        return sessao.conectado_iq

    try:
        testes = [
            lambda: sessao.API.get_profile(),
            lambda: sessao.API.get_balance(),
            lambda: sessao.API.get_server_timestamp(),
            lambda: sessao.API.get_all_open_time()
        ]
        for teste in testes:
            try:
                resultado = teste()
                if resultado:
                    sessao.ultimo_ping_sucesso = time.time()
                    sessao.erros_consecutivos_api = 0
                    if not sessao.conectado_iq:
                        sessao.conectado_iq = True
                        add_log(sessao, "✅ Conexão restabelecida!", 'win')
                    return True
            except Exception:
                continue

        sessao.erros_consecutivos_api += 1
        if sessao.erros_consecutivos_api % 5 == 0:
            add_log(sessao, f"⚠️ Falha na API ({sessao.erros_consecutivos_api}/{MAX_ERROS_ANTES_RECONECTAR})", 'error')

        if sessao.erros_consecutivos_api >= MAX_ERROS_ANTES_RECONECTAR:
            add_log(sessao, f"🔄 API instável! Iniciando reconexão...", 'error')
            sessao.conectado_iq = False
            return conectar_iq(sessao)
        return False

    except Exception as e:
        sessao.erros_consecutivos_api += 1
        if sessao.erros_consecutivos_api >= MAX_ERROS_ANTES_RECONECTAR:
            add_log(sessao, f"❌ Erro crítico: {e}. Reconectando...", 'error')
            sessao.conectado_iq = False
            return conectar_iq(sessao)
        return False

# ========== FUNCOES DO BOT (LOGICA DEFINITIVA — inalterada, so usa sessao) ==========

def _timestamp_servidor(sessao):
    """Relogio do servidor da IQ (nao do celular). Fallback pro relogio local."""
    try:
        ts = sessao.API.get_server_timestamp()
        if ts:
            return float(ts)
    except Exception:
        pass
    return time.time()

def aguardar_expiracao_vela(sessao, timeframe):
    """Espera ATE a vela expirar de verdade, ancorado no relogio do servidor.
    Isso mata o 'delay crescente': antes a gente contava 60s a partir do buy,
    entao cada ~2s de processamento do buy empurrava tudo pra frente e ia
    acumulando. Agora a espera termina no fechamento REAL da vela + margem,
    independente de quanto o buy demorou."""
    agora = _timestamp_servidor(sessao)
    # proximo multiplo de 'timeframe' (fechamento da vela em que entramos)
    expiracao = (int(agora // timeframe) + 1) * timeframe
    margem = 2  # segundos apos a expiracao pra garantir que o payout caiu na conta
    ciclos = 0
    while _timestamp_servidor(sessao) < expiracao + margem:
        if not sessao.bot_rodando:
            return False
        ciclos += 1
        if ciclos % 15 == 0:
            verificar_saude_api(sessao)  # checagem leve, nao interrompe a espera
        time.sleep(0.5)
    return True

def executar_ciclo(sessao, plano):
    """
    LOGICA DEFINITIVA (mesma essencia de sempre), agora dirigida por 'plano':
      plano = {
        'direcao': 'call'|'put',      # da estrategia
        'timeframe': 60,              # resolvido (estrategia ou override do usuario)
        'gales': 2,                   # resolvido (estrategia ou override do usuario)
        'entradas': [e0, e1, ...],    # ja calculado (calculo OU mao fixa)
      }
    1. ENTRADA: aguarda inicio da vela, guarda saldo antes.
    2. Aguarda a vela EXPIRAR (ancorado no relogio, sem delay crescente).
    3. Verifica resultado por SALDO.
    4. WIN => STOP GAIN. LOSS => proximo GALE (imediato). Repete ate acabar os gales.
    """
    if not sessao.bot_rodando or not sessao.API:
        return

    direcao = plano['direcao']
    timeframe = plano['timeframe']
    gales = plano['gales']
    entradas = plano['entradas']

    try:
        if not consumir_volt(sessao):
            add_log(sessao, "❌ Sem VOLTS!", 'error')
            sessao.bot_rodando = False
            return

        if not verificar_saude_api(sessao):
            add_log(sessao, "❌ Conexão perdida! Tentando reconectar...", 'error')
            if not conectar_iq(sessao):
                add_log(sessao, "❌ Falha na reconexão. Parando operação.", 'error')
                sessao.bot_rodando = False
                return

        bi = sessao.API.get_balance()
        add_log(sessao, f"💰 Banca: ${bi:.2f} | ⏱️ {timeframe}s | 🔁 {gales} gale(s)", 'info')
        entradas_str = " | ".join(f"E{idx+1}:${e:.2f}" for idx, e in enumerate(entradas))
        add_log(sessao, f"📐 {entradas_str}", 'info')

        for i in range(gales + 1):
            if not sessao.bot_rodando: break

            if not verificar_saude_api(sessao):
                add_log(sessao, "⚠️ Conexão instável! Tentando reconectar...", 'error')
                if not conectar_iq(sessao):
                    add_log(sessao, "❌ Falha na reconexão. Parando operação.", 'error')
                    sessao.bot_rodando = False
                    break

            valor = entradas[i]

            if i == 0:
                if not aguardar_inicio_vela(sessao):
                    add_log(sessao, "⚠️ Falha ao aguardar inicio da vela para a entrada principal.", 'error')
                    break
            else:
                time.sleep(0.5)
                add_log(sessao, f"   🔄 Executando GALE {i} imediatamente...", 'info')

            saldo_antes = sessao.API.get_balance()
            if saldo_antes < valor:
                add_log(sessao, "❌ Saldo insuficiente!", 'error')
                break

            add_log(sessao, f"🎯 {'ENTRADA' if i == 0 else f'GALE {i}'}: {direcao.upper()} ${valor:.2f}", 'info')

            # duracao em minutos pra API.buy (binaria/turbo). timeframe vem em segundos.
            duracao_min = max(1, int(round(timeframe / 60)))
            st, id_ordem = sessao.API.buy(valor, sessao.par, direcao, duracao_min)
            if not st or not id_ordem:
                try:
                    st, id_ordem = sessao.API.buy_digital_spot(sessao.par, valor, direcao, duracao_min)
                except Exception:
                    pass

            if not st or not id_ordem:
                add_log(sessao, "❌ Falha na ordem!", 'error')
                break

            if i == 0:
                sessao.ordem_id_atual = id_ordem
                add_log(sessao, f"   📝 Ordem #{id_ordem} (Entrada Principal)", 'info')
            else:
                add_log(sessao, f"   📝 Ordem #{id_ordem} (GALE {i})", 'info')

            add_log(sessao, f"   ⏳ Aguardando expiração da vela ({timeframe}s)...", 'info')
            if not aguardar_expiracao_vela(sessao, timeframe):
                return  # bot foi parado no meio da espera

            if not verificar_saude_api(sessao):
                add_log(sessao, "⚠️ Conexão perdida durante espera! Tentando reconectar...", 'error')
                if not conectar_iq(sessao):
                    add_log(sessao, "❌ Falha na reconexão. Parando operação.", 'error')
                    sessao.bot_rodando = False
                    break

            saldo_depois = sessao.API.get_balance()
            lucro_liquido = round(saldo_depois - saldo_antes, 2)
            sessao.lucro += lucro_liquido

            if lucro_liquido > 0:
                add_log(sessao, f"🌟 WIN! +${lucro_liquido:.2f}", 'win')
                sessao.NumDeOperacoes += 1
                u = carregar_usuario(sessao.email)
                if u:
                    u['total_wins'] = u.get('total_wins', 0) + 1
                    u['total_ganho'] = u.get('total_ganho', 0) + abs(lucro_liquido)
                    u['lucro_total'] = u['total_ganho'] - u.get('total_gasto', 0)
                    u['banca_atual'] = round(saldo_depois, 2)
                    u.setdefault('historico_operacoes', []).append({
                        'data': str(datetime.now())[:19], 'resultado': 'WIN',
                        'valor': valor, 'lucro': lucro_liquido,
                        'estrategia': sessao.estrategia_atual.upper()
                    })
                    salvar_usuario(sessao.email, u)
                sessao.STOP_GAIN_ATINGIDO = True
                add_log(sessao, "🎯 STOP GAIN! Vitoria alcancada!", 'win')
                break
            else:
                add_log(sessao, f"💀 LOSS! {lucro_liquido:.2f}", 'loss')
                u = carregar_usuario(sessao.email)
                if u:
                    u['total_losses'] = u.get('total_losses', 0) + 1
                    u['total_gasto'] = u.get('total_gasto', 0) + valor
                    u['lucro_total'] = u['total_ganho'] - u['total_gasto']
                    u['banca_atual'] = round(saldo_depois, 2)
                    u.setdefault('historico_operacoes', []).append({
                        'data': str(datetime.now())[:19], 'resultado': 'LOSS',
                        'valor': valor, 'lucro': lucro_liquido,
                        'estrategia': sessao.estrategia_atual.upper()
                    })
                    salvar_usuario(sessao.email, u)

                if i < gales and sessao.bot_rodando:
                    add_log(sessao, f"   ➡️ Indo para GALE {i + 1}...", 'loss')
                else:
                    add_log(sessao, "   💀 CICLO ESGOTADO! Todas as entradas perdidas.", 'loss')

        if sessao.bot_rodando:
            bf = sessao.API.get_balance() if sessao.API else bi
            add_log(sessao, "=" * 50, 'info')
            add_log(sessao, f"{'🌟 LUCRO' if bf > bi else '💀 PERDA'}: ${abs(bf - bi):.2f} | Banca: ${bf:.2f}", 'info')
            add_log(sessao, "=" * 50, 'info')

    except Exception as e:
        add_log(sessao, f"Erro: {e}", 'error')
        import traceback
        traceback.print_exc()
    finally:
        sessao.bot_rodando = False
        sessao.ordem_id_atual = None
        add_log(sessao, "⏹️ Ciclo finalizado!", 'info')

def _resolver_plano(sessao, resultado_estrategia, estrategia_info):
    """Junta o que a ESTRATEGIA decidiu com o que o USUARIO configurou.
    Regra: se sessao.usar_config_padrao=True, usa as sugestoes da estrategia;
    senao, usa os overrides do usuario. Direcao SEMPRE vem da estrategia."""
    direcao = resultado_estrategia.get('direcao', '').lower()

    # timeframe e gales: estrategia sugere, usuario pode sobrescrever
    tf_estrategia = resultado_estrategia.get('timeframe', estrategia_info.get('timeframe', 60))
    gales_estrategia = resultado_estrategia.get('gales', estrategia_info.get('gales', 2))

    if sessao.usar_config_padrao:
        timeframe = int(tf_estrategia)
        gales = int(gales_estrategia)
    else:
        timeframe = int(tf_estrategia)          # timeframe segue a estrategia (o par OTC depende dele)
        gales = int(sessao.gales_override)

    gales = max(0, min(gales, 5))  # teto de seguranca: nunca mais que 5 gales

    # entradas: calculo do sistema OU mao fixa
    if sessao.modo_entrada == 'fixa':
        # mao fixa: mesmo valor em todas as entradas do ciclo (usuario assume o risco)
        entradas = [round(float(sessao.mao_fixa_valor), 2)] * (gales + 1)
    else:
        banca = sessao.API.get_balance()
        payout = Payout(sessao, sessao.par)
        entradas = calcular_entradas(banca, payout, gales, sessao.percentual_banca)

    return {'direcao': direcao, 'timeframe': timeframe, 'gales': gales, 'entradas': entradas}

def bot_loop(sessao):
    """Loop principal do bot — uma instancia POR SESSAO."""
    with sessao.bot_lock:
        if not sessao.bot_rodando or not sessao.API:
            sessao.bot_rodando = False
            return

        if not verificar_saude_api(sessao):
            add_log(sessao, "⚠️ Sem conexão! Tentando reconectar...", 'error')
            if not conectar_iq(sessao):
                add_log(sessao, "❌ Falha na reconexão. Bot parado.", 'error')
                sessao.bot_rodando = False
                return

        estrategias_info = carregar_informacoes_estrategias()
        if not estrategias_info or sessao.estrategia_atual not in estrategias_info:
            add_log(sessao, f"❌ Estrategia '{sessao.estrategia_atual}' nao encontrada!", 'error')
            sessao.bot_rodando = False
            return

        estrategia_info = estrategias_info[sessao.estrategia_atual]
        sessao.timeframe_atual = estrategia_info.get('timeframe', 60)
        add_log(sessao, f"📊 Estrategia: {estrategia_info.get('nome')}", 'indicator')

        funcao_estrategia = obter_funcao_estrategia(sessao.estrategia_atual)
        if not funcao_estrategia:
            add_log(sessao, f"❌ Nao foi possivel carregar a estrategia '{sessao.estrategia_atual}'!", 'error')
            sessao.bot_rodando = False
            return

        # ===== AUTO-PAR: escolhe o melhor par OTC antes de comecar =====
        if sessao.auto_par:
            melhor = escolher_melhor_par(sessao, funcao_estrategia)
            if melhor:
                sessao.par = melhor
            else:
                add_log(sessao, "⚠️ Auto-par não encontrou par; usando o atual.", 'error')
        add_log(sessao, f"📌 Par: {sessao.par}", 'info')

        # log da config resolvida (transparencia pro usuario)
        if sessao.usar_config_padrao:
            add_log(sessao, "⚙️ Config: PADRÃO da estratégia", 'info')
        else:
            add_log(sessao, f"⚙️ Config: PERSONALIZADA ({sessao.gales_override} gales)", 'info')
        add_log(sessao, f"💵 Entrada: {'MÃO FIXA $' + format(sessao.mao_fixa_valor, '.2f') if sessao.modo_entrada == 'fixa' else 'CÁLCULO do sistema'}", 'info')

        sessao.BANCA_INICIAL_DO_BOT = sessao.API.get_balance()
        sessao.STOP_GAIN_ATINGIDO = False
        sessao.lucro = 0.0
        sessao.NumDeOperacoes = 0
        sessao.volt_ja_consumido = False
        sessao.sinal_pendente = None
        sessao.ultimo_sinal = "Aguardando..."
        add_log(sessao, f"💰 ${sessao.BANCA_INICIAL_DO_BOT:.2f}")

        while sessao.bot_rodando and not sessao.STOP_GAIN_ATINGIDO:
            if not verificar_saude_api(sessao):
                add_log(sessao, "⚠️ Conexão instável no loop! Tentando reconectar...", 'error')
                if not conectar_iq(sessao):
                    add_log(sessao, "❌ Falha na reconexão. Bot parado.", 'error')
                    sessao.bot_rodando = False
                    break

            try:
                resultado = funcao_estrategia(sessao.API, sessao.par, lambda msg, tipo='info': add_log(sessao, msg, tipo))
                if resultado and sessao.bot_rodando:
                    direcao = resultado.get('direcao', '').lower()
                    if direcao in ['call', 'put']:
                        sessao.ultimo_sinal = f"GATILHO: {direcao.upper()}"
                        add_log(sessao, f"🎯 SINAL: {direcao.upper()}!", 'sensitive')
                        plano = _resolver_plano(sessao, resultado, estrategia_info)
                        add_log(sessao, f"🎯 EXECUTANDO CICLO: {direcao.upper()}", 'sensitive')
                        executar_ciclo(sessao, plano)
                        break
                time.sleep(0.3)
            except Exception as e:
                add_log(sessao, f"Erro no loop: {e}", 'error')
                time.sleep(5)

        sessao.bot_rodando = False

# ========== THREADS DE MANUTENÇÃO (agora iteram por TODAS as sessoes ativas) ==========

def _sessoes_snapshot():
    with sessoes_global_lock:
        return list(sessoes.values())

def keep_alive_thread():
    while True:
        time.sleep(20)
        for sessao in _sessoes_snapshot():
            if sessao.conectado_iq and sessao.API and sessao.email:
                try:
                    sessao.API.get_server_timestamp()
                except Exception:
                    pass

def monitor_conexao_thread():
    while True:
        time.sleep(10)
        for sessao in _sessoes_snapshot():
            # so vale a pena monitorar quem esta com bot ligado ou conectado
            if sessao.email and (sessao.bot_rodando or sessao.conectado_iq):
                if not verificar_saude_api(sessao):
                    add_log(sessao, "⚠️ Monitor detectou falha. Tentando reconectar...", 'error')
                    if conectar_iq(sessao):
                        add_log(sessao, "✅ Reconexão pelo monitor bem-sucedida!", 'win')
                    else:
                        add_log(sessao, "❌ Falha na reconexão pelo monitor.", 'error')

def analise_mercado_loop():
    while True:
        for sessao in _sessoes_snapshot():
            if sessao.conectado_iq and sessao.API:
                try:
                    velas = sessao.API.get_candles(sessao.par, 60, 30, time.time())
                    if velas and len(velas) >= 20:
                        rsi_val = calcular_rsi(velas, 14)
                        estoc_val = calcular_estocastico(velas, 14)
                        mm5 = calcular_media_movel(velas, 5)
                        mm10 = calcular_media_movel(velas, 10)
                        mm20 = calcular_media_movel(velas, 20)
                        preco_atual = get_close(velas[-1])

                        if mm5 and mm10 and mm20:
                            if mm5 > mm10 and mm10 > mm20: fase = "TENDENCIA ALTA"
                            elif mm5 < mm10 and mm10 < mm20: fase = "TENDENCIA BAIXA"
                            elif rsi_val < 40: fase = "ACUMULACAO"
                            elif rsi_val > 60: fase = "EXAUSTAO"
                            else: fase = "CONSOLIDACAO"
                        else: fase = "ANALISANDO..."

                        sessao.ultima_analise = {
                            'rsi': round(rsi_val, 1), 'mm5': round(mm5, 5) if mm5 else 0,
                            'mm10': round(mm10, 5) if mm10 else 0, 'mm20': round(mm20, 5) if mm20 else 0,
                            'stoch': round(estoc_val, 1), 'fase': fase, 'preco': round(preco_atual, 5) if preco_atual else 0
                        }
                except Exception:
                    pass
        time.sleep(2)

# 🔧 INICIAR THREADS DE MANUTENÇÃO (uma so de cada, cobrindo todas as sessoes)
threading.Thread(target=analise_mercado_loop, daemon=True).start()
threading.Thread(target=keep_alive_thread, daemon=True).start()
threading.Thread(target=monitor_conexao_thread, daemon=True).start()
threading.Thread(target=limpar_sessoes_inativas, daemon=True).start()

def sincronizar_html_local():
    try:
        os.makedirs("templates", exist_ok=True)
        HTML_URL = "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/tesla_369_bot/templates/index.html"
        response = requests.get(HTML_URL, timeout=10)
        if response.status_code == 200:
            conteudo = response.text
            # PROTECAO: so sobrescreve se o que baixou for HTML DE VERDADE.
            # Ja aconteceu do arquivo no GitHub estar com codigo Python colado
            # por engano — sem essa checagem, o bot se auto-sabotava toda vez
            # que iniciava, baixando Python por cima do HTML bom.
            inicio = conteudo.lstrip()[:200].lower()
            parece_html = inicio.startswith('<!doctype') or inicio.startswith('<html') or '<head' in inicio
            parece_python = inicio.startswith('#!/usr/bin/env python') or 'from flask import' in inicio or inicio.startswith('# -*-')
            if parece_python or not parece_html:
                print("⚠️ HTML remoto parece inválido (não é HTML). Mantendo o arquivo local.")
                # se nem existe um local, ai nao tem o que manter — avisa alto
                if not os.path.exists("templates/index.html"):
                    print("❌ ATENÇÃO: não há index.html local válido! Corrija o arquivo no GitHub.")
                return False
            with open("templates/index.html", "w", encoding="utf-8") as f:
                f.write(conteudo)
            print("✅ HTML sincronizado!")
            return True
    except Exception as e: print(f"❌ Erro HTML: {e}")
    return False

# ========== ROTAS FLASK ==========
# IMPORTANTE: toda rota agora recebe 'email' (do JSON, form ou query string)
# e usa get_sessao(email) para pegar o estado certo. O FRONTEND precisa
# mandar esse email em toda chamada — veja a nota no final da explicação.

def _email_da_requisicao():
    """Tenta achar o email em JSON, form ou querystring, nessa ordem."""
    if request.is_json:
        d = request.get_json(silent=True) or {}
        if d.get('email'):
            return d.get('email')
    if request.form.get('email'):
        return request.form.get('email')
    return request.args.get('email', '')

@app.route('/')
def index():
    skins = carregar_todas_skins_do_firebase()
    # A skin certa do usuario vem do e-mail, nao de um parametro solto na URL.
    # Sem isso, todo reload da pagina (compra de skin, PIX pago, conectar)
    # cai de volta na skin padrao, mesmo que o usuario tenha ativado outra.
    email = _email_da_requisicao()
    skin_id = 'skin_padrao'
    if email:
        usuario = carregar_usuario(email.strip().lower())
        if usuario:
            skin_id = usuario.get('skin_atual', 'skin_padrao')
    skin = next((s for s in skins if s.get('id') == skin_id), skins[0] if skins else list(get_skins_fallback().values())[0])
    planos_json = ','.join([f'{{"id":{p["id"]},"moedas":{p["moedas"]},"preco":{p["preco"]},"nome":"{p["nome"]}","desc":"{p["desc"]}","tag":"{p.get("tag","")}","desconto":"{p.get("desconto","")}"}}' for p in PLANOS])
    return render_template('index.html',
        COR_FUNDO=skin.get('cor_fundo', '#0a0a1a'), COR_PANEL=skin.get('cor_panel', '#1a1a3e'),
        COR_DESTAQUE=skin.get('cor_destaque', '#ffd700'), COR_TEXTO=skin.get('cor_texto', '#fff'),
        COR_BOTAO=skin.get('cor_botao', 'linear-gradient(135deg,#cc8800,#ffd700)'), COR_TAB_ATIVA=skin.get('cor_tab_ativa', '#ffd700'),
        COR_HEADER_BG=skin.get('cor_header_bg', 'linear-gradient(135deg,#1a0000,#331100,#553300,#331100,#1a0000)'),
        COR_HEADER_BORDA=skin.get('cor_header_borda', '#ffd700'), CSS_EXTRA=skin.get('css_extra', ''),
        HEADER_EXTRA=skin.get('header_extra', '<div class="lightning"></div>'), PLANOS_JSON=planos_json,
        BOT_VERSION=BOT_VERSION
    )

@app.route('/sinal', methods=['POST'])
def receber_sinal():
    sessao = get_sessao(_email_da_requisicao())
    if not sessao: return jsonify({'ok': False, 'erro': 'Email ausente'})
    if not sessao.bot_rodando: return jsonify({'ok': False, 'erro': 'Bot em repouso.'})
    if not sessao.conectado_iq: return jsonify({'ok': False, 'erro': 'IQ Option offline.'})
    direcao = request.get_json().get('direcao', '').lower()
    if direcao not in ['call', 'put']: return jsonify({'ok': False, 'erro': 'Alvo invalido'})
    with sessao.sinal_lock: sessao.sinal_pendente = direcao
    add_log(sessao, f"📡 Sinal externo: {direcao.upper()}", 'sensitive')
    return jsonify({'ok': True})

@app.route('/status')
def status():
    sessao = get_sessao(_email_da_requisicao())
    if not sessao:
        return jsonify({'erro': 'email ausente — envie ?email=... na querystring'})

    u = carregar_usuario(sessao.email) if sessao.email else {}
    skins = carregar_todas_skins_do_firebase()
    skins_status = []
    skins_compradas = u.get('skins_compradas', ['skin_padrao']) if u else ['skin_padrao']
    skin_atual = u.get('skin_atual', 'skin_padrao') if u else 'skin_padrao'
    for skin in skins:
        skins_status.append({
            'id': skin.get('id'), 'nome': skin.get('nome'), 'desc': skin.get('desc'),
            'preco_moedas': skin.get('preco_moedas'), 'categoria': skin.get('categoria'),
            'comprado': skin.get('id') in skins_compradas, 'ativo': skin.get('id') == skin_atual
        })

    estrategias_info = carregar_informacoes_estrategias()
    estrategias_compradas = u.get('estrategias_compradas', ['v_sensitivo']) if u else ['v_sensitivo']
    estrategia_atual = u.get('estrategia_atual', 'v_sensitivo') if u else 'v_sensitivo'
    estrategia_nome = estrategias_info[estrategia_atual].get('nome', estrategia_atual) if estrategia_atual in estrategias_info else "Nenhuma"

    return jsonify({
        'conectado': sessao.conectado_iq, 'rodando': sessao.bot_rodando, 'email': sessao.email,
        'banca': sessao.API.get_balance() if sessao.API else 0, 'lucro': sessao.lucro,
        'ops': sessao.NumDeOperacoes, 'sinal': sessao.ultimo_sinal,
        'logs': get_logs_html(sessao, 40), 'moedas': u.get('moedas', 0) if u else 0,
        'skin_id': skin_atual, 'skins_status': skins_status,
        'estrategia': estrategia_atual, 'estrategia_nome': estrategia_nome, 'estrategias_compradas': estrategias_compradas,
        'estrategias_disponiveis': {k: {'nome': v['nome'], 'desc': v['desc'], 'preco_moedas': v['preco_moedas'], 'gratis': v['gratis']} for k, v in estrategias_info.items()},
        'analise': sessao.ultima_analise, 'bot_version': BOT_VERSION,
        'par': sessao.par, 'melhor_par_info': sessao.melhor_par_info,
        'config': {
            'usar_config_padrao': sessao.usar_config_padrao,
            'gales_override': sessao.gales_override,
            'auto_par': sessao.auto_par,
            'modo_entrada': sessao.modo_entrada,
            'mao_fixa_valor': sessao.mao_fixa_valor,
            'percentual_banca': sessao.percentual_banca
        }
    })

@app.route('/pares_otc')
def pares_otc():
    sessao = get_sessao(_email_da_requisicao())
    if not sessao or not sessao.API or not sessao.conectado_iq:
        return jsonify({'pares': [], 'erro': 'Conecte primeiro'})
    return jsonify({'pares': listar_pares_otc(sessao)})

@app.route('/set_config', methods=['POST'])
def set_config():
    """Salva as escolhas do usuario (padrao vs personalizado, auto-par,
    mao fixa vs calculo, gales). Tudo por sessao — nao afeta outros usuarios."""
    d = request.json or {}
    sessao = get_sessao(d.get('email'))
    if not sessao: return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    if 'usar_config_padrao' in d: sessao.usar_config_padrao = bool(d['usar_config_padrao'])
    if 'auto_par' in d: sessao.auto_par = bool(d['auto_par'])
    if 'par' in d and d['par']: sessao.par = d['par']
    if 'modo_entrada' in d and d['modo_entrada'] in ('calculo', 'fixa'): sessao.modo_entrada = d['modo_entrada']
    if 'mao_fixa_valor' in d:
        try: sessao.mao_fixa_valor = max(1.0, float(d['mao_fixa_valor']))
        except (TypeError, ValueError): pass
    if 'gales_override' in d:
        try: sessao.gales_override = max(0, min(5, int(d['gales_override'])))
        except (TypeError, ValueError): pass
    return jsonify({'ok': True, 'config': {
        'usar_config_padrao': sessao.usar_config_padrao, 'auto_par': sessao.auto_par,
        'par': sessao.par, 'modo_entrada': sessao.modo_entrada,
        'mao_fixa_valor': sessao.mao_fixa_valor, 'gales_override': sessao.gales_override
    }})

@app.route('/set_percentual', methods=['POST'])
def set_percentual():
    d = request.json or {}
    sessao = get_sessao(d.get('email'))
    if not sessao: return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    sessao.percentual_banca = d.get('percentual', PERCENTUAL_BANCA_PADRAO)
    return jsonify({'ok': True})

@app.route('/selecionar_estrategia', methods=['POST'])
def selecionar_estrategia():
    d = request.json or {}
    sessao = get_sessao(d.get('email'))
    if not sessao: return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    est_id = d.get('estrategia', 'v_sensitivo')
    u = carregar_usuario(sessao.email)
    if not u: return jsonify({'ok': False, 'erro': 'Usuario nao encontrado'})
    estrategias_info = carregar_informacoes_estrategias()
    if est_id not in estrategias_info: return jsonify({'ok': False, 'erro': 'Estrategia invalida'})

    estrategias_compradas = u.get('estrategias_compradas', ['v_sensitivo'])
    if est_id not in estrategias_compradas:
        if not estrategias_info[est_id].get('gratis', False): return jsonify({'ok': False, 'erro': f'Estrategia bloqueada! Compre na loja.'})
        u['estrategias_compradas'].append(est_id)
    u['estrategia_atual'] = est_id
    salvar_usuario(sessao.email, u)
    sessao.estrategia_atual = est_id
    add_log(sessao, f"🧠 Estrategia: {estrategias_info[est_id]['nome']}", 'indicator')
    return jsonify({'ok': True})

@app.route('/comprar_estrategia', methods=['POST'])
def comprar_estrategia():
    d = request.json or {}
    sessao = get_sessao(d.get('email'))
    if not sessao: return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    est_id = d.get('estrategia_id', '')
    estrategias_info = carregar_informacoes_estrategias()
    u = carregar_usuario(sessao.email)
    if not u or est_id not in estrategias_info: return jsonify({'ok': False, 'erro': 'Parametros invalidos'})

    if 'estrategias_compradas' not in u: u['estrategias_compradas'] = ['v_sensitivo']
    if est_id in u['estrategias_compradas']:
        u['estrategia_atual'] = est_id
        salvar_usuario(sessao.email, u)
        sessao.estrategia_atual = est_id
        return jsonify({'ok': True, 'moedas': u['moedas'], 'msg': 'Ja adquirida!'})

    preco = estrategias_info[est_id].get('preco_moedas', 0)
    if u.get('moedas', 0) < preco: return jsonify({'ok': False, 'erro': f'Precisa de {preco} ⚡'})
    u['moedas'] -= preco
    u['estrategias_compradas'].append(est_id)
    u['estrategia_atual'] = est_id
    salvar_usuario(sessao.email, u)
    sessao.estrategia_atual = est_id
    add_log(sessao, f"🛒 Estrategia: {estrategias_info[est_id]['nome']}", 'win')
    return jsonify({'ok': True, 'moedas': u['moedas'], 'msg': 'Sucesso!'})

@app.route('/conectar', methods=['POST'])
def conectar():
    try:
        d = request.get_json()
        email, senha, tipo = d.get('email', '').strip(), d.get('senha', '').strip(), d.get('tipo', 'PRACTICE')
        if not email or not senha: return jsonify({'ok': False, 'erro': 'Credenciais em branco'})

        sessao = get_sessao(email)
        sessao.senha = senha  # guardada em memoria (RAM), so pra permitir reconexao apos queda de rede
        sessao.tipo_conta_atual = tipo
        sessao.API = IQ_Option(email, senha)
        status_conn, reason = sessao.API.connect()
        if not status_conn: return jsonify({'ok': False, 'erro': str(reason)[:100]})
        sessao.API.change_balance(tipo)
        sessao.conectado_iq = True
        usuario = carregar_usuario(email) or criar_usuario(email)
        hoje = str(datetime.now())[:10]
        if usuario.get('moedas_ganhas_hoje') != hoje:
            usuario['moedas'] = usuario.get('moedas', 0) + 1
            usuario['moedas_ganhas_hoje'] = hoje
            salvar_usuario(email, usuario)
        sessao.skin_atual = usuario.get('skin_atual', 'skin_padrao')
        sessao.estrategia_atual = usuario.get('estrategia_atual', 'v_sensitivo')
        add_log(sessao, '🔌 Conectado!', 'info')
        add_log(sessao, f'✅ ${sessao.API.get_balance():.2f} | ⚡ {usuario.get("moedas", 0)} VOLTS | Conta: {tipo}', 'win')
        return jsonify({'ok': True, 'moedas': usuario.get('moedas', 0), 'refresh': True})
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)[:100]})

@app.route('/comecar_operar', methods=['POST'])
def comecar_operar():
    try:
        d = request.json or {}
        sessao = get_sessao(d.get('email'))
        if not sessao or not sessao.conectado_iq: return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})

        estrategias_info = carregar_informacoes_estrategias()
        if not estrategias_info or sessao.estrategia_atual not in estrategias_info:
            return jsonify({'ok': False, 'erro': f'❌ Estrategia "{sessao.estrategia_atual}" invalida!'})

        usuario = carregar_usuario(sessao.email)
        if not usuario: return jsonify({'ok': False, 'erro': 'Usuario nao encontrado!'})
        if usuario.get('moedas', 0) < 1: return jsonify({'ok': False, 'erro': 'Sem VOLTS! Compre na loja.'})

        with sessao.bot_lock:
            if sessao.bot_rodando and sessao.bot_thread and sessao.bot_thread.is_alive():
                return jsonify({'ok': False, 'erro': 'Bot ja rodando!'})
            sessao.bot_rodando = True
            sessao.bot_thread = threading.Thread(target=bot_loop, args=(sessao,), daemon=True)
            sessao.bot_thread.start()
        return jsonify({'ok': True, 'moedas': usuario['moedas']})
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)[:100]})

@app.route('/parar', methods=['POST'])
def parar():
    data = request.json or {}
    sessao = get_sessao(data.get('email'))
    if not sessao: return jsonify({'ok': False, 'erro': 'Email ausente'})
    add_log(sessao, "🛑 Parando o bot...", 'info')
    sessao.bot_rodando = False
    sessao.volt_ja_consumido = False
    if data.get('desconectar'):
        sessao.conectado_iq = False
        add_log(sessao, "🔌 Desconectado.", 'info')
        # OBS: shutdown do processo inteiro foi removido daqui de proposito —
        # com varias pessoas usando o mesmo servidor, um usuario desconectando
        # nao pode derrubar o servidor de todo mundo. Se quiser um botao de
        # "desligar o servidor" separado, precisa de autenticacao de admin.
        return jsonify({'ok': True, 'shutdown': False})
    add_log(sessao, "✅ Bot parado!", 'win')
    return jsonify({'ok': True, 'shutdown': False})

@app.route('/comprar_skin', methods=['POST'])
def comprar_skin():
    d = request.get_json()
    sessao = get_sessao(d.get('email'))
    if not sessao: return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    skin_id = d.get('skin_id', '')
    skin = carregar_skin_do_firebase(skin_id) or next((s for s in carregar_todas_skins_do_firebase() if s.get('id') == skin_id), None)
    if not skin: return jsonify({'ok': False, 'erro': 'Skin nao encontrada'})
    usuario = carregar_usuario(sessao.email)
    if not usuario: return jsonify({'ok': False, 'erro': 'Usuario invalido'})

    if skin.get('preco_moedas', 0) == 0:
        if skin_id not in usuario.setdefault('skins_compradas', ['skin_padrao']): usuario['skins_compradas'].append(skin_id)
        usuario['skin_atual'] = skin_id
        salvar_usuario(sessao.email, usuario)
        sessao.skin_atual = skin_id
        return jsonify({'ok': True, 'moedas': usuario.get('moedas', 0), 'msg': 'Skin gratis ativada!', 'refresh': True})

    if skin_id in usuario.setdefault('skins_compradas', ['skin_padrao']):
        usuario['skin_atual'] = skin_id
        salvar_usuario(sessao.email, usuario)
        sessao.skin_atual = skin_id
        return jsonify({'ok': True, 'moedas': usuario['moedas'], 'msg': 'Ativada!', 'refresh': True})

    if usuario.get('moedas', 0) < skin.get('preco_moedas', 0): return jsonify({'ok': False, 'erro': f'Precisa de {skin["preco_moedas"]} ⚡'})
    usuario['moedas'] -= skin['preco_moedas']
    usuario['skins_compradas'].append(skin_id)
    usuario['skin_atual'] = skin_id
    salvar_usuario(sessao.email, usuario)
    sessao.skin_atual = skin_id
    return jsonify({'ok': True, 'moedas': usuario['moedas'], 'msg': 'Skin adquirida!', 'refresh': True})

@app.route('/ativar_skin', methods=['POST'])
def ativar_skin():
    d = request.get_json()
    sessao = get_sessao(d.get('email'))
    if not sessao: return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    skin_id = d.get('skin_id', '')
    usuario = carregar_usuario(sessao.email)
    if not usuario: return jsonify({'ok': False, 'erro': 'Usuario nao encontrado'})
    if skin_id not in usuario.setdefault('skins_compradas', ['skin_padrao']):
        skin = carregar_skin_do_firebase(skin_id)
        if skin and skin.get('preco_moedas', 0) > 0: return jsonify({'ok': False, 'erro': 'Compre primeiro!'})
        usuario['skins_compradas'].append(skin_id)
    usuario['skin_atual'] = skin_id
    salvar_usuario(sessao.email, usuario)
    sessao.skin_atual = skin_id
    return jsonify({'ok': True, 'refresh': True})

# ========== PIX (compartilhado entre usuarios por natureza — nao muda) ==========

@app.route('/criar_pix', methods=['POST'])
def criar_pix():
    d = request.get_json()
    plano = next((p for p in PLANOS if p['id'] == int(d.get('plano_id') or 1)), None)
    if MODO_SIMULACAO:
        pix_id = str(uuid.uuid4())[:8]
        with pagamentos_lock:
            pagamentos_pendentes[pix_id] = {'email': d.get('email'), 'plano_id': plano['id'], 'moedas': plano['moedas'], 'valor': plano['preco'], 'pago': False, 'criado_em': time.time()}
        return jsonify({'sucesso': True, 'simulacao': True, 'pix_id': pix_id, 'qr_code': f"00020126360014BR.GOV.BCB.PIX0136{d.get('email')}5204000053039865404{plano['preco']:.2f}5802BR5909Tesla3696009Sao Paulo62070503***6304E3F9", 'qr_code_base64': '', 'valor': plano['preco'], 'moedas': plano['moedas']})
    try:
        url = "https://api.mercadopago.com/v1/payments"
        headers = {"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}", "Content-Type": "application/json", "X-Idempotency-Key": str(uuid.uuid4())}
        payment_data = {"transaction_amount": float(plano['preco']), "description": f"TESLA369 - {plano['moedas']} VOLTS", "payment_method_id": "pix", "payer": {"email": d.get('email'), "first_name": "Traders", "last_name": "Tesla", "identification": {"type": "CPF", "number": "00000000000"}}}
        res = requests.post(url, json=payment_data, headers=headers, timeout=30).json()
        if 'id' in res:
            pix_id = str(res['id'])
            with pagamentos_lock:
                pagamentos_pendentes[pix_id] = {'email': d.get('email'), 'plano_id': plano['id'], 'moedas': plano['moedas'], 'valor': plano['preco'], 'pago': False, 'criado_em': time.time()}
            return jsonify({'sucesso': True, 'simulacao': False, 'pix_id': pix_id, 'qr_code': res['point_of_interaction']['transaction_data']['qr_code'], 'qr_code_base64': res['point_of_interaction']['transaction_data']['qr_code_base64'], 'valor': plano['preco'], 'moedas': plano['moedas']})
        return jsonify({'sucesso': False, 'erro': res.get('message', 'Erro ao gerar PIX')})
    except Exception as e: return jsonify({'sucesso': False, 'erro': str(e)[:50]})

@app.route('/verificar_pix', methods=['POST'])
def verificar_pix():
    pix_id = request.get_json().get('pix_id', '')
    if MODO_SIMULACAO:
        with pagamentos_lock:
            info = pagamentos_pendentes.get(pix_id, {})
            pago = info.get('pago', False)
        if pago and pix_id in pagamentos_pendentes:
            with pagamentos_lock:
                if not pagamentos_pendentes[pix_id]['pago']:
                    pagamentos_pendentes[pix_id]['pago'] = True
                    info = pagamentos_pendentes[pix_id]
                else:
                    info = None
            if info:
                u = carregar_usuario(info['email'])
                if u: u['moedas'] += info['moedas']; salvar_usuario(info['email'], u)
                return jsonify({'pago': True, 'moedas': info['moedas'], 'saldo': u.get('moedas', 0) if u else 0})
        return jsonify({'pago': pago})
    try:
        url = f"https://api.mercadopago.com/v1/payments/{pix_id}"
        headers = {"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}"}
        res = requests.get(url, headers=headers, timeout=10).json()
        if res.get('status') == 'approved':
            with pagamentos_lock:
                jah_processado = pix_id not in pagamentos_pendentes or pagamentos_pendentes[pix_id]['pago']
                if not jah_processado:
                    pagamentos_pendentes[pix_id]['pago'] = True
                    info = pagamentos_pendentes[pix_id]
                else:
                    info = None
            if info:
                u = carregar_usuario(info['email'])
                if u: u['moedas'] += info['moedas']; salvar_usuario(info['email'], u)
                return jsonify({'pago': True, 'moedas': info['moedas'], 'saldo': u.get('moedas', 0) if u else 0})
            return jsonify({'pago': True})
        return jsonify({'pago': False})
    except Exception:
        return jsonify({'pago': False})

def verificador_automatico_pix():
    while True:
        time.sleep(10)
        try:
            with pagamentos_lock:
                itens = list(pagamentos_pendentes.items())
            for pix_id, dados in itens:
                if dados.get('pago', False):
                    continue
                # limpeza: PIX gerado ha mais de 30min e nunca pago, descarta
                if time.time() - dados.get('criado_em', time.time()) > 1800:
                    with pagamentos_lock:
                        pagamentos_pendentes.pop(pix_id, None)
                    continue
                if MODO_SIMULACAO:
                    pago = dados.get('pago', False)
                else:
                    try:
                        res = requests.get(f"https://api.mercadopago.com/v1/payments/{pix_id}", headers={"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}"}, timeout=10).json()
                        pago = res.get('status') == 'approved'
                    except Exception:
                        continue
                if pago:
                    with pagamentos_lock:
                        if pagamentos_pendentes.get(pix_id, {}).get('pago'):
                            continue
                        pagamentos_pendentes[pix_id]['pago'] = True
                    u = carregar_usuario(dados['email']) or criar_usuario(dados['email'])
                    u['moedas'] = u.get('moedas', 0) + dados['moedas']
                    salvar_usuario(dados['email'], u)
                    print(f"💰 PIX Confirmado! +{dados['moedas']} VOLTS para {dados['email']}")
        except Exception:
            pass

threading.Thread(target=verificador_automatico_pix, daemon=True).start()

@app.route('/chat_enviar', methods=['POST'])
def chat_enviar():
    try:
        data = request.json
        requests.post(f'{FB_URL}/tesla_369/chat.json', json={
            'nome': data.get('nome', 'Anonimo')[:15], 'msg': data.get('msg', '')[:200],
            'hora': datetime.now().strftime('%H:%M')
        }, timeout=5)
    except Exception: pass
    return jsonify({'ok': True})

@app.route('/chat_mensagens')
def chat_mensagens_route():
    try:
        r = requests.get(f'{FB_URL}/tesla_369/chat.json?orderBy="$key"&limitToLast=50', timeout=5)
        return jsonify({'messages': list(r.json().values()) if r.status_code == 200 and r.json() else [], 'online': len(_sessoes_snapshot())})
    except Exception:
        return jsonify({'messages': [], 'online': 0})

@app.route('/ranking')
def ranking():
    ranking_list = []
    try:
        usuarios = requests.get(f'{FB_URL}/tesla_369/usuarios.json').json() or {}
        for k, ud in usuarios.items():
            if ud:
                ranking_list.append({
                    'email': ud.get('email', 'N/A'), 'lucro_total': round(ud.get('lucro_total', 0), 2),
                    'total_wins': ud.get('total_wins', 0), 'total_losses': ud.get('total_losses', 0),
                    'total_ciclos': ud.get('total_ciclos', 0),
                    'taxa': round((ud.get('total_wins', 0) / max(ud.get('total_ciclos', 1), 1)) * 100, 1),
                    'banca_atual': round(ud.get('banca_atual', 0), 2)
                })
    except Exception: pass
    ranking_list.sort(key=lambda x: x['lucro_total'], reverse=True)
    tc = sum(x['total_ciclos'] for x in ranking_list)
    tw = sum(x['total_wins'] for x in ranking_list)
    return jsonify({'ranking': ranking_list, 'stats': {'total_usuarios': len(ranking_list), 'total_ops': tc, 'total_wins': tw, 'taxa_global': round((tw/max(tc,1))*100,1)}})

@app.route('/relatorio')
def relatorio():
    return jsonify(carregar_usuario(request.args.get('email', '')) or {'erro': 'Nao encontrado'})

@app.route('/resetar', methods=['POST'])
def resetar():
    email = request.json.get('email', '')
    u = carregar_usuario(email)
    if not u: return jsonify({'ok': False, 'msg': 'Nao encontrado'})
    u.update({'total_ciclos':0,'total_wins':0,'total_losses':0,'total_gasto':0.0,'total_ganho':0.0,'lucro_total':0.0,'historico_operacoes':[],'dias_ativos':0,'banca_atual':0.0,'moedas_ganhas_hoje':str(datetime.now())[:10]})
    salvar_usuario(email, u)
    return jsonify({'ok': True, 'msg': 'Resetado!'})

@app.route('/shutdown')
def shutdown():
    os.kill(os.getpid(), signal.SIGTERM)
    return jsonify({'ok': True})

if __name__ == '__main__':
    print("=" * 70)
    print(f"⚡ {BOT_NAME} v{BOT_VERSION} - MULTI-SESSAO + RECONEXÃO ROBUSTA ⚡")
    print("✅ Cada dispositivo/usuario tem sua propria sessao isolada")
    print("✅ Firebase: SKINS e ESTRATEGIAS carregadas da nuvem")
    print("=" * 70)

    print("\n🔍 Carregando skins do Firebase...")
    skins_test = carregar_todas_skins_do_firebase()
    print(f"📦 {len(skins_test)} skins disponiveis")

    print("\n🔍 Carregando estrategias do Firebase...")
    estrategias_test = carregar_informacoes_estrategias()
    print(f"📊 {len(estrategias_test)} estrategias disponiveis")

    sincronizar_html_local()

    port = int(os.environ.get('PORT', 5000))
    print(f"\n🚀 Servidor rodando em http://0.0.0.0:{port}")
    print("   Qualquer dispositivo na mesma rede pode acessar via IP local, ex:")
    print("   http://192.168.x.x:5000")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
