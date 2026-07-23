#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ⚡ TESLA 369 BOT v16.0.0 - MULTICONTA + TIMEFRAME DINAMICO ⚡
#
# NOVIDADES v16:
#  🔧 MULTICONTA: cada aluno tem sua propria Sessao isolada (API, saldo, bot,
#     logs, estrategia). Antes era tudo variavel global: o 2o aluno que
#     conectasse SOBRESCREVIA a conexao do 1o e podia operar na conta errada.
#  🔧 TIMEFRAME DINAMICO: a estrategia manda o timeframe no retorno
#     ({'direcao':'put','timeframe':300}) e o bot RESPEITA - tanto na expiracao
#     da ordem quanto no alinhamento da vela. Antes o buy() era hardcoded em
#     1 minuto: o bot SO operava M1, mesmo com a estrategia pedindo M5.
#
# Herda do v15.0.4: reconexao robusta, gale instantaneo, espera ancorada no
# relogio, PIX via Cloudflare Worker.

from flask import Flask, render_template, jsonify, request, session
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

# ============================================================
# PONTE PYTHON -> ANDROID (notificacoes + vibracao)
# ============================================================
# No APK (Chaquopy), conseguimos chamar codigo Kotlin. No PC isso nao existe,
# entao a funcao vira no-op silencioso. Assim o MESMO bot.py roda nos dois.
_ANDROID_NOTIFIER = None
def _get_android_notifier():
    global _ANDROID_NOTIFIER
    if _ANDROID_NOTIFIER is not None:
        return _ANDROID_NOTIFIER
    try:
        from java import jclass
        _ANDROID_NOTIFIER = jclass("com.tesla369.bot.TeslaService")
    except Exception:
        _ANDROID_NOTIFIER = False  # nao estamos no Android
    return _ANDROID_NOTIFIER

def notificar_android(tipo, titulo, msg, vibracoes=0):
    """tipo: 'win'|'loss'|'gale'|'info'. vibracoes: quantas vibradas curtas.
    Silencioso e' seguro no PC (nao ha Android)."""
    notifier = _get_android_notifier()
    if not notifier:
        return
    try:
        notifier.notificarResultado(tipo, titulo, msg, int(vibracoes))
    except Exception:
        pass  # nunca deixa a notificacao quebrar a operacao


app = Flask(__name__)

# Necessario para o cookie de sessao assinado (e' ele que separa um aluno do
# outro sem precisar mexer no index.html - o browser manda o cookie sozinho).
app.secret_key = os.environ.get("TESLA_SECRET_KEY", "") or uuid.uuid4().hex
app.permanent_session_lifetime = 60 * 60 * 12  # 12h

# ============= VERSÃO DO BOT =============
BOT_VERSION = "16.0.0"
BOT_NAME = "TESLA-369"

# ============= CONFIGURACOES =============
FB_URL = "https://nexos-40654-default-rtdb.firebaseio.com"
print("✅ Firebase HTTP REST configurado!")

MARTINGALE_PADRAO = 2
PAYOUT_PADRAO = 0.85
PERCENTUAL_BANCA_PADRAO = 15
ENTRADA_MINIMA = 2  # a IQ Option recusa ordem abaixo disso (R$2 / $1 - usamos o piso mais alto)

# ============================================================
# BACKEND DE PAGAMENTOS (Cloudflare Worker) - MESMO PADRAO DO PDV
# ============================================================
# O token do Mercado Pago NAO fica aqui. Pedimos a cobranca a um worker
# Cloudflare DEDICADO ao TESLA 369 - so' ele conhece o token de producao e a
# tabela de precos dos planos de VOLTS.
BACKEND_PAGAMENTOS_URL = os.environ.get(
    "TESLA_BACKEND_URL",
    "https://tesla369.gyn-bet-fc.workers.dev"
)
MODO_SIMULACAO = os.environ.get("MODO_SIMULACAO", "false").lower() == "true"

PLANOS = [
    {'id':1,'moedas':1,'preco':0.99,'nome':'🔰 TESTE','desc':'R$0,99/VOLT','tag':'1 ciclo','bonus':''},
    {'id':2,'moedas':6,'preco':6.69,'nome':'⭐ BASICO','desc':'R$1,11/VOLT','tag':'6 ciclos','bonus':''},
    {'id':3,'moedas':15,'preco':9.99,'nome':'💎 INTERMEDIARIO','desc':'R$0,67/VOLT','tag':'15 ciclos','bonus':'🎨 1 Skin Basica GRATIS','desconto':'33% OFF'},
    {'id':4,'moedas':36,'preco':21.69,'nome':'🔥 PREMIUM','desc':'R$0,60/VOLT','tag':'36 ciclos','bonus':'🎨 1 Skin Premium GRATIS','desconto':'40% OFF'},
    {'id':5,'moedas':69,'preco':39.69,'nome':'👑 ULTRA','desc':'R$0,57/VOLT','tag':'69 ciclos','bonus':'🎨 1 Skin Lendaria GRATIS','desconto':'69% OFF'},
]

# ============= CACHES GLOBAIS (dados COMPARTILHADOS, iguais p/ todos) =============
# Isto aqui pode continuar global: sao dados publicos da nuvem (catalogo de
# skins/estrategias), nao estado de nenhum aluno especifico.
cache_skins = {"data": None, "timestamp": 0}
cache_estrategias_info = {"data": {}, "timestamp": 0}
cache_estrategias_compiladas = {}   # nome -> (funcao, timestamp)
cache_compilacao_lock = threading.Lock()
CACHE_TTL = 300

_payout_cache = {}  # par -> (valor, timestamp) - payout e' do MERCADO, nao do aluno
PAYOUT_CACHE_TTL = 300

pagamentos_pendentes = {}  # pix_id -> dados (por pagamento, nao por sessao)

MAX_ERROS_ANTES_RECONECTAR = 3
MAX_LOGS_WEB = 200


class BotParado(BaseException):
    """Sinal de que o aluno mandou PARAR e a estrategia deve abortar JA.

    🔧 Por que BaseException e nao Exception: quase toda estrategia do Firebase
    tem um `except Exception as e:` generico no meio do loop. Se isto herdasse
    de Exception, a propria estrategia engoliria o pedido de parada e continuaria
    rodando. Herdando de BaseException (igual KeyboardInterrupt/SystemExit), o
    `except Exception` delas nao pega e a parada realmente acontece.
    """
    pass

# ============================================================
# 🔧 SESSAO: TODO o estado que ANTES era global agora vive aqui.
# Uma instancia por aluno conectado. E' isto que permite N alunos
# simultaneos sem um atropelar o outro.
# ============================================================

class Sessao:
    def __init__(self, sid):
        self.sid = sid
        self.criada_em = time.time()
        self.ultimo_acesso = time.time()

        # --- conexao IQ Option (era: API, email_usuario_atual, senha_atual...) ---
        self.API = None
        self.email = ""
        self.senha = ""          # so' em memoria, p/ reconexao dura (troca de rede)
        self.tipo_conta = "PRACTICE"
        self.conectado = False
        self.par = "EURUSD-OTC"

        # --- estado do bot (era: bot_rodando, lucro, NumDeOperacoes...) ---
        self.bot_rodando = False
        self.bot_thread = None
        self.bot_lock = threading.Lock()
        self.timeframe_atual = 60
        self.lucro = 0.0
        self.num_operacoes = 0
        self.banca_inicial = 0.0
        self.stop_gain = False
        self.ultimo_sinal = "Aguardando..."
        self.ultima_analise = {}
        self.ordem_id_atual = None
        self.martingale = MARTINGALE_PADRAO
        self.percentual_banca = PERCENTUAL_BANCA_PADRAO

        # --- logs (era: logs_web global - todos viam o log de todos!) ---
        self.logs = []

        # --- VOLTS ---
        self.volt_ja_consumido = False
        self.volts_cache = None

        # --- skin / estrategia (era: skin_atual_global, estrategia_atual_global) ---
        self.skin_atual = 'skin_padrao'
        self.estrategia_atual = 'v_sensitivo'
        self.estrategia_executar = None
        self.estrategia_injetada = None   # nome da estrategia atualmente injetada

        # --- reconexao (era: ERROS_CONSECUTIVOS_API, RECONECTANDO...) ---
        self.erros_consecutivos = 0
        self.reconectando = False
        self.ultimo_ping = time.time()
        self.ultima_banca_conhecida = 0.0

    def add_log(self, msg, tipo='info'):
        t = datetime.now().strftime('%H:%M:%S')
        self.logs.append({'time': t, 'msg': msg, 'tipo': tipo})
        if len(self.logs) > MAX_LOGS_WEB:
            self.logs = self.logs[-MAX_LOGS_WEB:]
        # prefixo com o email ajuda a debugar o servidor com varios alunos online
        quem = self.email.split('@')[0] if self.email else self.sid[:6]
        print(f"{t} [{quem}] {msg}")

    def logs_html(self, limite=40):
        html = ''
        for log in self.logs[-limite:]:
            cor = {'win': '#00ff88', 'loss': '#ff4444', 'info': '#00ff88',
                   'sensitive': '#ff69b4', 'indicator': '#ffd700', 'error': '#ff4444'}.get(log['tipo'], '#00ff88')
            html += f'<span style="color:#666">{log["time"]}</span> <span style="color:{cor}">{log["msg"]}</span>\n'
        return html or '📡 Aguardando...'

    def log_para_estrategia(self):
        """Devolve o add_log que sera ENTREGUE a estrategia do Firebase.

        🔧 Isto e' o unico ponto de contato que temos com o codigo da estrategia
        (a assinatura e' fixa: rodar_analise(api, par, add_log)). Varias
        estrategias do Firebase tem `while True:` com sleeps longos e NUNCA
        checam se o bot foi parado - a tesla_369 dorme 177s por volta. Sem isto,
        o botao PARAR nao para nada: a thread fica viva pra sempre segurando o
        bot_lock, e a sessao daquele aluno trava de vez.
        Como toda estrategia loga entre um passo e outro, usamos o proprio
        add_log como ponto de interrupcao.
        """
        def _log(msg, tipo='info'):
            if not self.bot_rodando:
                raise BotParado()
            self.add_log(msg, tipo)
        return _log


# ============= REGISTRO DE SESSOES =============
sessoes = {}
sessoes_lock = threading.Lock()

def get_sessao():
    """Devolve a Sessao do browser que fez esta requisicao, criando se preciso.
    O 'sid' vive num cookie assinado do Flask - por isso o index.html NAO
    precisa mudar nada: o browser manda o cookie automaticamente."""
    sid = session.get('sid')
    if not sid:
        sid = uuid.uuid4().hex
        session['sid'] = sid
        session.permanent = True
    with sessoes_lock:
        s = sessoes.get(sid)
        if s is None:
            s = Sessao(sid)
            sessoes[sid] = s
        s.ultimo_acesso = time.time()
        return s

def sessoes_ativas():
    """Snapshot da lista de sessoes (p/ as threads de fundo iterarem com seguranca)."""
    with sessoes_lock:
        return list(sessoes.values())

def limpar_sessoes_thread():
    """Remove sessoes abandonadas - senao a memoria do servidor cresce pra sempre
    conforme alunos entram e saem."""
    while True:
        time.sleep(600)
        agora = time.time()
        with sessoes_lock:
            for sid in list(sessoes.keys()):
                s = sessoes[sid]
                inativa = (agora - s.ultimo_acesso) > 7200  # 2h sem nenhum request
                if inativa and not s.bot_rodando:
                    try:
                        if s.API:
                            s.API.close()  # fecha o websocket dela
                    except Exception:
                        pass
                    del sessoes[sid]
                    print(f"🧹 Sessao {sid[:6]} removida (inativa)")

# ============= FUNCOES AUXILIARES DE VELAS/INDICADORES =============

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
            ganhos.append(diferenca)
            perdas.append(0)
        else:
            ganhos.append(0)
            perdas.append(abs(diferenca))
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

# ============= SKINS NO FIREBASE (compartilhado) =============

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

# ============= ESTRATEGIAS NO FIREBASE (catalogo compartilhado) =============

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

def compilar_estrategia(nome_estrategia):
    """Compila (exec) o codigo da estrategia vindo do Firebase e devolve a funcao
    rodar_analise. Cacheado POR NOME - a funcao em si e' pura (recebe api, par e
    add_log como parametro), entao pode ser compartilhada entre sessoes que usam
    a mesma estrategia. O que NAO pode ser compartilhado e' qual estrategia cada
    aluno escolheu - isso vive na Sessao."""
    agora = time.time()
    with cache_compilacao_lock:
        em_cache = cache_estrategias_compiladas.get(nome_estrategia)
        if em_cache and (agora - em_cache[1]) < CACHE_TTL:
            return em_cache[0]

    estrategia_data = carregar_estrategia_do_firebase(nome_estrategia)
    if not estrategia_data:
        return None
    codigo = estrategia_data.get('codigo')
    if not codigo or 'def rodar_analise' not in codigo:
        return None
    try:
        escopo = {}
        exec(codigo, escopo)
        func = escopo.get('rodar_analise')
        if not func:
            return None
        with cache_compilacao_lock:
            cache_estrategias_compiladas[nome_estrategia] = (func, agora)
        return func
    except Exception as e:
        print(f"❌ Erro ao compilar estrategia {nome_estrategia}: {e}")
        return None

def carregar_e_injetar_estrategia(s, nome_estrategia):
    """Injeta a estrategia NA SESSAO do aluno (antes era uma global unica: se o
    aluno A trocasse de estrategia, o bot do aluno B passava a usar a dele)."""
    if s.estrategia_injetada == nome_estrategia and s.estrategia_executar:
        return True
    func = compilar_estrategia(nome_estrategia)
    if not func:
        s.add_log(f"❌ Erro ao carregar estrategia '{nome_estrategia}'", "error")
        return False
    s.estrategia_executar = func
    s.estrategia_injetada = nome_estrategia
    s.add_log(f"✅ Estrategia '{nome_estrategia}' carregada com sucesso!", "win")
    return True

# ========== FUNCOES DE USUARIO (FIREBASE) ==========

def _key_email(email):
    return email.replace("@", "_").replace(".", "_").replace("#", "").replace("$", "").replace("[", "").replace("]", "").replace("/", "_")

_usuario_cache = {}  # email -> (dados, timestamp)
USUARIO_CACHE_TTL = 3  # segundos

def salvar_usuario(email, dados):
    try:
        requests.put(f'{FB_URL}/tesla_369/usuarios/{_key_email(email)}.json', json=dados, timeout=5)
        _usuario_cache[email] = (dados, time.time())  # write-through: cache ja' sai atualizado
    except: pass

def carregar_usuario(email):
    """🔧 O /status e' consultado a cada 2s (poll do front-end) e SEMPRE fazia
    uma chamada de rede ao Firebase aqui dentro - sem cache nenhum. Numa rede
    lenta/instavel isso e' o principal motivo da tela demorar pra "assentar"
    depois de conectar (varias chamadas em sequencia, cada uma podendo levar
    ate 5s de timeout). Um cache curto (3s) tira a maioria dessas chamadas da
    rede sem deixar o saldo/estado desatualizado por muito tempo - e toda
    escrita (salvar_usuario) ja' atualiza o cache na hora, entao uma compra ou
    troca nunca fica "presa" mostrando dado velho."""
    agora = time.time()
    em_cache = _usuario_cache.get(email)
    if em_cache and (agora - em_cache[1]) < USUARIO_CACHE_TTL:
        return em_cache[0]
    try:
        r = requests.get(f'{FB_URL}/tesla_369/usuarios/{_key_email(email)}.json', timeout=5)
        if r.status_code == 200 and r.json():
            dados = r.json()
            _usuario_cache[email] = (dados, agora)
            return dados
    except: pass
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

def atualizar_estatisticas_async(s, resultado, valor, lucro_liquido, saldo_depois, estrategia, tipo='entrada'):
    """Atualiza estatisticas (Firebase) em thread separada. E' so historico -
    NUNCA deve bloquear a decisao de ir pro proximo GALE.

    tipo='entrada' -> uma entrada isolada (inclui cada gale). E' o detalhe fino
                      que aparece no historico/relatorio do aluno.
    tipo='ciclo'   -> o RESULTADO CONSOLIDADO da operacao inteira. Um ciclo
                      LOSS->LOSS->WIN e' UM ciclo vencedor, nao "2 loss + 1 win".
                      E' isto que o placar das estrategias conta.
    """
    email = s.email
    def worker():
        try:
            u = carregar_usuario(email)
            if not u:
                return
            # os contadores globais do usuario continuam contando ENTRADAS
            # (nao mexemos neles pra nao baguncar o relatorio existente)
            if tipo == 'ciclo':
                u.setdefault('historico_operacoes', []).append({
                    'data': str(datetime.now())[:19], 'resultado': resultado,
                    'valor': valor, 'lucro': lucro_liquido,
                    'estrategia': str(estrategia).upper(), 'tipo': 'ciclo'
                })
                salvar_usuario(email, u)
                return
            if resultado == 'WIN':
                u['total_wins'] = u.get('total_wins', 0) + 1
                u['total_ganho'] = u.get('total_ganho', 0) + abs(lucro_liquido)
            else:
                u['total_losses'] = u.get('total_losses', 0) + 1
                u['total_gasto'] = u.get('total_gasto', 0) + valor
            u['lucro_total'] = u.get('total_ganho', 0) - u.get('total_gasto', 0)
            u['banca_atual'] = round(saldo_depois, 2)
            u.setdefault('historico_operacoes', []).append({
                'data': str(datetime.now())[:19], 'resultado': resultado,
                'valor': valor, 'lucro': lucro_liquido,
                'estrategia': str(estrategia).upper(), 'tipo': 'entrada'
            })
            salvar_usuario(email, u)
        except Exception as e:
            s.add_log(f"⚠️ Falha ao salvar estatisticas (nao afeta a operacao): {e}", 'error')
    threading.Thread(target=worker, daemon=True).start()

# ========== FUNCOES DO BOT ==========

def Payout(s, p):
    """Payout e' propriedade do MERCADO (igual pra todos), entao o cache e' global.
    Cache evita travar ate 10s por ciclo esperando a IQ responder."""
    agora = time.time()
    em_cache = _payout_cache.get(p)
    if em_cache and (agora - em_cache[1]) < PAYOUT_CACHE_TTL:
        return em_cache[0]
    try:
        if not s.API: return PAYOUT_PADRAO
        s.API.subscribe_strike_list(p, 1)
        for _ in range(6):  # no maximo ~3s
            d = s.API.get_digital_current_profit(p, 1)
            if d != False:
                s.API.unsubscribe_strike_list(p, 1)
                valor = round(int(d) / 100, 2)
                _payout_cache[p] = (valor, agora)
                return valor
            time.sleep(0.5)
        s.API.unsubscribe_strike_list(p, 1)
        return PAYOUT_PADRAO
    except: return PAYOUT_PADRAO

def calcular_entradas(b, p, g, percentual):
    bs = (b * percentual / 100) * 0.99
    e0 = bs / sum((1/p)**i for i in range(g+1))
    entradas = [e0]
    for i in range(1, g+1):
        entradas.append((sum(entradas) + e0) / p)
    ajuste = bs / sum(entradas)
    entradas = [round(e * ajuste, 2) for e in entradas]
    if sum(entradas) > b:
        entradas[-1] = round(entradas[-1] - (sum(entradas) - b) - 0.02, 2)
    # 🔧 banca pequena + percentual baixo podiam dar uma entrada abaixo do minimo
    # que a corretora aceita (ex: 15% de banca baixa nao fecha 2$ na primeira
    # entrada). Sem isto o buy() falhava silenciosamente. Aqui o piso VENCE o
    # percentual escolhido: o robo so' opera se puder respeitar o minimo da IQ.
    return [max(ENTRADA_MINIMA, e) for e in entradas]

def normalizar_timeframe(tf):
    """Aceita segundos (60, 300) ou minutos (1, 5) e devolve SEGUNDOS.
    As estrategias no Firebase usam segundos ('timeframe': 60), mas se alguem
    escrever 1 ou 5 por engano o bot nao pode operar uma vela de 1 segundo."""
    try:
        tf = int(tf)
    except (TypeError, ValueError):
        return 60
    if tf <= 0:
        return 60
    if tf < 60:          # veio em minutos (1, 5, 15...)
        tf = tf * 60
    return tf

def expiracao_em_minutos(timeframe_seg):
    """A IQ Option recebe a expiracao em MINUTOS no buy()."""
    return max(1, int(normalizar_timeframe(timeframe_seg) // 60))

def aguardar_inicio_vela(s, timeframe_seg):
    """Aguarda o inicio da proxima vela DO TIMEFRAME CERTO.
    🔧 Antes: `while datetime.now().second > 5` - so' sabia alinhar em vela de 1
    minuto. Numa estrategia M5 isso entrava no meio da vela de 5 min.
    Agora usa o relogio epoch: velas de 60/300/900s sempre comecam quando
    (epoch % timeframe) == 0, entao isso alinha certo em qualquer timeframe."""
    tf = normalizar_timeframe(timeframe_seg)
    s.add_log(f"   ⏳ Aguardando inicio da vela (M{tf//60})...", 'info')
    while (time.time() % tf) > 5:
        if not s.bot_rodando: return False
        time.sleep(0.3)
    s.add_log("   ✅ Vela confirmada!", 'info')
    return True

def _persistir_consumo_volt(s):
    """Grava o consumo do VOLT no Firebase em segundo plano (fora do caminho critico)."""
    email = s.email
    try:
        u = carregar_usuario(email)
        if u:
            u['moedas'] = max(0, u.get('moedas', 0) - 1)
            u['total_ciclos'] = u.get('total_ciclos', 0) + 1
            salvar_usuario(email, u)
    except Exception as e:
        s.add_log(f"⚠️ Falha ao gravar consumo de VOLT (nao afeta a operacao): {e}", 'error')

def consumir_volt(s):
    """Valida com cache local (atualizado pelos polls do /status) e persiste em
    background - sem 2 chamadas Firebase bloqueantes antes de operar.
    Regra de negocio intacta: sem VOLT, nao opera."""
    if s.volt_ja_consumido: return True
    if s.volts_cache is None:
        usuario = carregar_usuario(s.email)
        if not usuario: return False
        s.volts_cache = usuario.get('moedas', 0)
    if s.volts_cache < 1:
        return False
    s.volts_cache -= 1
    s.volt_ja_consumido = True
    s.add_log(f"⚡ 1 VOLT consumido. Saldo: {s.volts_cache} VOLTS", 'info')
    threading.Thread(target=_persistir_consumo_volt, args=(s,), daemon=True).start()
    return True

# ========== 🔥 RECONEXÃO ROBUSTA (por sessao) ==========

def conectar_iq(s):
    """Tenta reconectar a sessao 's' com backoff exponencial + relogin duro."""
    if not s.email:
        s.add_log("❌ Sem credenciais para reconectar!", 'error')
        return False

    if s.reconectando:
        # Outra tentativa ja esta em andamento p/ ESTA sessao (ex: monitor de fundo
        # + checagem inline do ciclo). Espera o resultado dela em vez de reportar
        # falha na hora.
        espera = 0.0
        while s.reconectando and espera < 70:
            time.sleep(0.5)
            espera += 0.5
        try:
            return bool(s.API and s.API.check_connect())
        except Exception:
            return False

    s.reconectando = True
    tentativas = 0
    max_tentativas = 5
    try:
        while tentativas < max_tentativas:
            try:
                if s.API and s.API.check_connect():
                    s.conectado = True
                    s.erros_consecutivos = 0
                    s.reconectando = False
                    s.add_log("✅ Reconectado com sucesso!", 'win')
                    return True
            except:
                pass
            tentativas += 1
            tempo_espera = min(30, 2 ** tentativas)
            s.add_log(f"🔄 Tentativa {tentativas}/{max_tentativas} de reconexão em {tempo_espera}s...", 'info')
            time.sleep(tempo_espera)
            try:
                if s.API:
                    s.API.connect()
                    time.sleep(2)
                    if s.tipo_conta:
                        s.API.change_balance(s.tipo_conta)
            except:
                pass
    except Exception as e:
        s.add_log(f"❌ Erro durante reconexão: {e}", 'error')
    finally:
        s.reconectando = False

    # 🔧 RECONEXÃO DURA: as tentativas acima so chamam .connect() no MESMO objeto.
    # Quando o socket morre de vez (trocou WiFi<->4G), o objeto vira zumbi.
    # Ultimo recurso: LOGIN COMPLETO DO ZERO com objeto novo.
    if s.email and s.senha:
        s.reconectando = True
        try:
            s.add_log("🔄 Reconexão normal falhou. Tentando RECONEXÃO COMPLETA (novo login)...", 'error')
            nova_api = IQ_Option(s.email, s.senha)
            status_conn, motivo = nova_api.connect()
            if status_conn:
                if s.tipo_conta:
                    nova_api.change_balance(s.tipo_conta)
                s.API = nova_api
                s.conectado = True
                s.erros_consecutivos = 0
                s.add_log("✅ Reconexão completa (novo login) bem sucedida!", 'win')
                return True
            else:
                s.add_log(f"❌ Reconexão completa falhou: {str(motivo)[:80]}", 'error')
        except Exception as e:
            s.add_log(f"❌ Erro na reconexão completa: {str(e)[:80]}", 'error')
        finally:
            s.reconectando = False

    s.conectado = False
    s.add_log(f"❌ Falha na reconexão após {max_tentativas} tentativas!", 'error')
    return False

def verificar_saude_api(s):
    """Verifica saúde da conexao DESTA sessao com múltiplos endpoints."""
    if not s.API or not s.email:
        return False
    if s.reconectando:
        return False
    try:
        # 🔧 ORDEM IMPORTA: get_balance() e' rapido (~0.3s) e ja' confirma que a
        # conexao esta viva. get_profile() e' LENTO (~6s no celular) - era o 1o
        # da lista e travava toda checagem de saude, inclusive no caminho do gale.
        # Agora get_balance vem primeiro: se responde, retorna na hora e nunca
        # chega no get_profile. (get_profile fica por ultimo, so' como desempate.)
        # ⚠️ get_all_open_time() FOI REMOVIDO desta lista. Por dentro ele chama
        # get_instruments() (cfd/forex/crypto - que o bot nem usa), e esse metodo
        # tem um `while self.api.instruments == None:` SEM timeout que, no erro,
        # ainda chama self.connect() - refazendo o login no meio da operacao.
        # Era uma mina terrestre: bastava os 2 primeiros testes falharem pra
        # sessao travar pra sempre. get_balance + timestamp + profile ja' provam
        # que a conexao esta viva.
        testes = [
            lambda: s.API.get_balance(),
            lambda: s.API.get_server_timestamp(),
            lambda: s.API.get_profile()
        ]
        for teste in testes:
            try:
                resultado = teste()
                if resultado:
                    s.ultimo_ping = time.time()
                    s.erros_consecutivos = 0
                    if not s.conectado:
                        s.conectado = True
                        s.add_log("✅ Conexão restabelecida!", 'win')
                    return True
            except:
                continue

        s.erros_consecutivos += 1
        if s.erros_consecutivos % 5 == 0:
            s.add_log(f"⚠️ Falha na API ({s.erros_consecutivos}/{MAX_ERROS_ANTES_RECONECTAR})", 'error')
        if s.erros_consecutivos >= MAX_ERROS_ANTES_RECONECTAR:
            s.add_log(f"🔄 API instável! ({s.erros_consecutivos} erros). Iniciando reconexão...", 'error')
            s.conectado = False
            return conectar_iq(s)
        return False
    except Exception as e:
        s.erros_consecutivos += 1
        if s.erros_consecutivos >= MAX_ERROS_ANTES_RECONECTAR:
            s.add_log(f"❌ Erro crítico: {e}. Reconectando...", 'error')
            s.conectado = False
            return conectar_iq(s)
        return False

# ========== CICLO DE OPERACAO ==========

def calcular_expiracao_real(tf):
    """Quando esta operacao REALMENTE expira, em segundos a partir de agora.

    🔧 Por que nao e' so' 'tf segundos a partir da entrada':
    a opcao nao expira X segundos depois da compra - ela expira no FECHAMENTO da
    vela. A entrada principal e' alinhada no inicio da vela (entao sobra ~tf), mas
    os GALES entram no MEIO da vela, e ai sobra bem menos que tf.
    Alem disso, quando falta pouco tempo pro fim da vela, a corretora empurra a
    opcao pra vela seguinte.

    ⚠️ Austin: o limite de 30s abaixo e' o comportamento classico da IQ Option
    (se falta menos que isso, joga pra proxima vela), mas nao consegui confirmar
    contra a API real daqui. Vale conferir no log: se aparecer LOSS antes da hora
    em gale colado no fim da vela, mexemos nesse numero.
    """
    tf = normalizar_timeframe(tf)
    restante = tf - (time.time() % tf)
    if restante < 30:
        restante += tf   # corretora empurra pra proxima vela
    return restante

def executar_ciclo(s, direcao, timeframe_seg):
    """
    1. ENTRADA: alinha no inicio da vela DO TIMEFRAME e guarda o saldo.
    2. Espera ATIVA ate o fechamento da vela (reage na hora se o saldo mudar).
    3. Resultado por SALDO (o debito da entrada nunca conta como resultado).
    4. WIN -> para (STOP GAIN). LOSS -> GALE imediato, sem delay.
    """
    if not s.bot_rodando or not s.API: return

    tf = normalizar_timeframe(timeframe_seg)
    expiracao_min = expiracao_em_minutos(tf)
    s.timeframe_atual = tf

    try:
        if not consumir_volt(s):
            s.add_log("❌ Sem VOLTS!", 'error')
            s.bot_rodando = False
            return

        if not verificar_saude_api(s):
            s.add_log("❌ Conexão perdida! Tentando reconectar...", 'error')
            if conectar_iq(s):
                s.add_log("✅ Reconectado com sucesso!", 'win')
            else:
                s.add_log("❌ Falha na reconexão. Parando operação.", 'error')
                s.bot_rodando = False
                return

        bi = s.API.get_balance()
        payout = Payout(s, s.par)
        entradas = calcular_entradas(bi, payout, s.martingale, s.percentual_banca)
        s.add_log(f"💰 Banca: ${bi:.2f} | Payout: {payout*100:.0f}%", 'info')
        s.add_log("📐 " + " | ".join(f"E{i+1}:${e:.2f}" for i, e in enumerate(entradas)), 'info')

        for i in range(s.martingale + 1):
            if not s.bot_rodando: break

            # 🔧 GALE INSTANTANEO: verificar_saude_api() chama get_profile(), que
            # e' uma requisicao HTTP LENTA (~6s no celular). Na entrada principal
            # (i==0) vale a pena checar. No GALE (i>0) NAO: a conexao acabou de
            # ser usada na entrada anterior, esta viva. Pular isso tira os ~6s de
            # atraso do gale que o Austin cronometrou no celular.
            if i == 0 and not verificar_saude_api(s):
                s.add_log("⚠️ Conexão instável! Tentando reconectar...", 'error')
                if conectar_iq(s):
                    s.add_log("✅ Reconectado com sucesso!", 'win')
                else:
                    s.add_log("❌ Falha na reconexão. Parando operação.", 'error')
                    s.bot_rodando = False
                    break

            valor = entradas[i]

            # Alinha a vela SO na entrada principal; gale entra imediato
            if i == 0:
                if not aguardar_inicio_vela(s, tf):
                    s.add_log("⚠️ Falha ao aguardar inicio da vela para a entrada principal.", 'error')
                    break
            else:
                s.add_log(f"   🔄 GALE {i}: executando imediatamente...", 'info')

            saldo_antes = s.API.get_balance()
            if saldo_antes < valor:
                s.add_log("❌ Saldo insuficiente!", 'error')
                break

            s.add_log(f"🎯 {'ENTRADA' if i == 0 else f'GALE {i}'}: {direcao.upper()} ${valor:.2f} (M{tf//60})", 'info')

            # 🔧 EXPIRACAO DINAMICA: antes era `API.buy(valor, par, direcao, 1)` -
            # 1 minuto HARDCODED. O bot so' operava M1 mesmo quando a estrategia
            # pedia M5. Agora a expiracao vem do timeframe da estrategia.
            st, id_ordem = s.API.buy(valor, s.par, direcao, expiracao_min)
            if not st or not id_ordem:
                try:
                    st, id_ordem = s.API.buy_digital_spot(s.par, valor, direcao, expiracao_min)
                except:
                    pass

            if not st or not id_ordem:
                s.add_log("❌ Falha na ordem!", 'error')
                break

            if i == 0:
                s.ordem_id_atual = id_ordem
                s.add_log(f"   📝 Ordem #{id_ordem} (Entrada Principal)", 'info')
            else:
                s.add_log(f"   📝 Ordem #{id_ordem} (GALE {i})", 'info')

            # 🔧 saldo LOGO APOS o debito da entrada - e' esta a base de comparacao.
            # O debito da entrada NAO e' o resultado; so' uma mudanca a partir daqui
            # (credito de WIN) sinaliza que o resultado saiu.
            try:
                saldo_pos_entrada = s.API.get_balance()
            except Exception:
                saldo_pos_entrada = saldo_antes - valor

            segundos_ate_expirar = calcular_expiracao_real(tf)
            s.add_log(f"   ⏳ Aguardando fechamento da vela (~{int(segundos_ate_expirar)}s)...", 'info')
            vela_expira_em = time.time() + segundos_ate_expirar
            houve_queda = False
            reconectado_em = None
            saldo_mudou = False

            # loop ANCORADO NO RELOGIO: a latencia do get_balance() e' descontada
            # do sleep, senao a espera derrapa (60s viravam 85s no celular)
            while time.time() < vela_expira_em:
                if not s.bot_rodando:
                    return

                inicio_volta = time.time()

                if not s.conectado:
                    if not houve_queda:
                        houve_queda = True
                        s.add_log("   ⚠️ Conexão caiu durante a vela!", 'error')
                else:
                    if houve_queda and reconectado_em is None:
                        reconectado_em = time.time()
                        if reconectado_em <= vela_expira_em:
                            s.add_log("   ✅ Conexão voltou a tempo, dentro da vela!", 'win')
                        else:
                            s.add_log("   ⚠️ Conexão voltou, mas so depois da vela expirar!", 'error')
                    try:
                        if s.API.get_balance() != saldo_pos_entrada:
                            saldo_mudou = True
                            break
                    except Exception:
                        pass

                gasto = time.time() - inicio_volta
                restante = vela_expira_em - time.time()
                time.sleep(max(0, min(1.0 - gasto, restante)))

            # 🔧 So' verifica saude/reconecta se REALMENTE houve queda na vela.
            # Se a vela fechou normal (houve_queda=False), a conexao esta viva -
            # chamar verificar_saude_api aqui so' adicionava segundos ao gale.
            if not saldo_mudou and houve_queda and not verificar_saude_api(s):
                s.add_log("⚠️ Conexão perdida durante espera! Tentando reconectar...", 'error')
                if not houve_queda:
                    houve_queda = True
                if conectar_iq(s):
                    reconectado_em = time.time()
                    s.add_log("✅ Reconectado (apos a vela ja ter expirado)!", 'win')
                else:
                    s.add_log("❌ Falha na reconexão. Parando operação.", 'error')
                    s.bot_rodando = False
                    break

            # margem: a corretora pode demorar um pouquinho pra creditar um WIN.
            # 🔧 era 5s (a maior parte do "gale de 6s"). O credito real cai em
            # <1s; 1.5s cobre o atraso sem travar o gale apos um LOSS.
            if not saldo_mudou and s.bot_rodando:
                fim_margem = time.time() + 1.5
                while time.time() < fim_margem:
                    try:
                        if s.API.get_balance() != saldo_pos_entrada:
                            saldo_mudou = True
                            break
                    except Exception:
                        pass
                    time.sleep(min(0.5, max(0, fim_margem - time.time())))

            # queda que so' voltou DEPOIS da vela expirar -> aborta gale
            abortar_gale = False
            if houve_queda and (reconectado_em is None or reconectado_em > vela_expira_em):
                abortar_gale = True
                s.add_log("   🚫 Queda tardia detectada - GALE sera abortado se houver LOSS.", 'error')

            saldo_depois = s.API.get_balance()
            lucro_liquido = round(saldo_depois - saldo_antes, 2)
            s.lucro += lucro_liquido

            if lucro_liquido > 0:
                s.add_log(f"🌟 WIN! +${lucro_liquido:.2f}", 'win')
                s.num_operacoes += 1
                atualizar_estatisticas_async(s, 'WIN', valor, lucro_liquido, saldo_depois, s.estrategia_atual)
                s.stop_gain = True
                s.add_log("🎯 STOP GAIN! Vitoria alcancada!", 'win')
                # 🔔 notifica + vibra: i+1 vibradas (1a vela=1, gale1=2, gale2=3)
                _onde = "de primeira" if i == 0 else f"no GALE {i}"
                notificar_android('win', f'🌟 WIN {_onde}!', f'+${lucro_liquido:.2f} | Banca: ${saldo_depois:.2f}', i + 1)
                break
            else:
                s.add_log(f"💀 LOSS! {lucro_liquido:.2f}", 'loss')
                atualizar_estatisticas_async(s, 'LOSS', valor, lucro_liquido, saldo_depois, s.estrategia_atual)

                if i < s.martingale and s.bot_rodando and not abortar_gale:
                    s.add_log(f"   ➡️ Indo para GALE {i + 1}...", 'loss')
                    # 🔔 notifica que vai pro proximo gale (vibracao longa unica)
                    notificar_android('gale', f'🔄 GALE {i + 1}', f'LOSS na tentativa {i + 1}. Indo pro gale...', 0)
                elif abortar_gale:
                    s.add_log("   🚫 CICLO PERDIDO (GALE abortado): conexão caiu e só voltou depois da vela expirar.", 'loss')
                    break
                else:
                    s.add_log("   💀 CICLO PERDIDO! Todas as entradas perdidas.", 'loss')
                    # 🔔 LOSS final: 4 vibradas (distingue bem do WIN, que e' 1-3)
                    notificar_android('loss', '💀 LOSS - ciclo perdido', f'Todas as entradas perderam. Banca: ${saldo_depois:.2f}', 4)

        if s.bot_rodando:
            bf = s.API.get_balance() if s.API else bi
            s.add_log("=" * 50, 'info')
            s.add_log(f"{'🌟 LUCRO' if bf > bi else '💀 PERDA'}: ${abs(bf - bi):.2f} | Banca: ${bf:.2f}", 'info')
            s.add_log("=" * 50, 'info')
            # 📊 registra o CICLO consolidado (e' isso que o placar das estrategias
            # conta). Um ciclo LOSS->LOSS->WIN conta como UM ciclo vencedor.
            resultado_ciclo = 'WIN' if (bf - bi) > 0.005 else 'LOSS'
            atualizar_estatisticas_async(
                s, resultado_ciclo, round(sum(entradas[:i + 1]), 2),
                round(bf - bi, 2), bf, s.estrategia_atual, tipo='ciclo')

    except Exception as e:
        s.add_log(f"Erro: {e}", 'error')
        import traceback
        traceback.print_exc()
    finally:
        s.bot_rodando = False
        s.ordem_id_atual = None
        s.add_log("⏹️ Ciclo finalizado!", 'info')

def bot_loop(s):
    """Loop principal do bot DESTA sessao."""
    # 🔧 acquire NAO bloqueante: se uma execucao anterior ficou presa dentro de
    # uma estrategia com `while True` (varias do Firebase sao assim), o `with
    # s.bot_lock:` antigo faria esta thread esperar pra SEMPRE, em silencio, e
    # cada tentativa de reiniciar vazaria mais uma thread.
    if not s.bot_lock.acquire(blocking=False):
        s.add_log("⚠️ Ja existe uma execucao presa nesta sessao (estrategia travada). "
                  "Aguarde ela liberar ou reinicie o servidor.", 'error')
        s.bot_rodando = False
        return
    try:
        _bot_loop_interno(s)
    finally:
        s.bot_lock.release()


def _bot_loop_interno(s):
    if True:
        if not s.bot_rodando or not s.API:
            s.bot_rodando = False
            return

        if not verificar_saude_api(s):
            s.add_log("⚠️ Sem conexão! Tentando reconectar...", 'error')
            if conectar_iq(s):
                s.add_log("✅ Reconectado com sucesso!", 'win')
            else:
                s.add_log("❌ Falha na reconexão. Bot parado.", 'error')
                s.bot_rodando = False
                return

        estrategias_info = carregar_informacoes_estrategias()
        if not estrategias_info or s.estrategia_atual not in estrategias_info:
            s.add_log(f"❌ Estrategia '{s.estrategia_atual}' nao encontrada!", 'error')
            s.bot_rodando = False
            return

        estrategia_info = estrategias_info[s.estrategia_atual]
        # timeframe declarado no 'info' do Firebase = so' o PADRAO. Se a estrategia
        # mandar o timeframe no retorno da analise, aquele vence (ver abaixo).
        tf_padrao = normalizar_timeframe(estrategia_info.get('timeframe', 60))
        s.timeframe_atual = tf_padrao
        s.add_log(f"📊 Estrategia: {estrategia_info.get('nome')}", 'indicator')
        s.add_log(f"⏱️ Timeframe padrao: {tf_padrao}s (M{tf_padrao//60})", 'info')

        if not carregar_e_injetar_estrategia(s, s.estrategia_atual):
            s.bot_rodando = False
            return

        s.banca_inicial = s.API.get_balance()
        s.stop_gain = False
        s.lucro = 0.0
        s.num_operacoes = 0
        s.volt_ja_consumido = False
        s.ultimo_sinal = "Aguardando..."
        s.add_log(f"📌 {s.par} | 💰 ${s.banca_inicial:.2f}")

        # contador pra nao verificar saude a cada volta (isso travava o PARAR:
        # cada verificacao tem latencia e o loop ficava preso nela)
        _voltas = 0
        while s.bot_rodando and not s.stop_gain:
            # 🔧 PARAR INSTANTANEO: checa o flag ANTES de qualquer coisa cara.
            if not s.bot_rodando:
                break

            # 🔧 nao verifica saude a CADA volta - so' a cada ~10 voltas (~3s).
            # Antes, cada volta do loop chamava verificar_saude_api (lento no
            # celular), e o bot ficava preso nela quando voce clicava PARAR.
            _voltas += 1
            if _voltas == 1 or _voltas % 10 == 0:
                if not verificar_saude_api(s):
                    if not s.bot_rodando: break
                    s.add_log("⚠️ Conexão instável no loop! Tentando reconectar...", 'error')
                    if conectar_iq(s):
                        s.add_log("✅ Reconectado com sucesso!", 'win')
                    else:
                        s.add_log("❌ Falha na reconexão. Bot parado.", 'error')
                        s.bot_rodando = False
                        break
            if not s.bot_rodando: break

            try:
                # entrega o add_log interrompivel: e' o que permite o PARAR
                # realmente parar estrategias com `while True` e sleeps longos
                resultado = s.estrategia_executar(s.API, s.par, s.log_para_estrategia())
                if resultado and s.bot_rodando:
                    direcao = resultado.get('direcao', '').lower()
                    if direcao in ['call', 'put']:
                        # 🔧 A ESTRATEGIA MANDA O TIMEFRAME. Antes o bot lia so' o
                        # 'direcao' e jogava o resto fora - o timeframe do retorno
                        # era ignorado e a ordem saia sempre M1.
                        tf_sinal = normalizar_timeframe(resultado.get('timeframe', tf_padrao))
                        if tf_sinal != tf_padrao:
                            s.add_log(f"   ⏱️ Estrategia pediu M{tf_sinal//60} (info dizia M{tf_padrao//60}) - usando o do sinal", 'info')
                        s.ultimo_sinal = f"GATILHO: {direcao.upper()}"
                        s.add_log(f"🎯 SINAL: {direcao.upper()}!", 'sensitive')
                        s.add_log(f"🎯 EXECUTANDO CICLO: {direcao.upper()} (M{tf_sinal//60})", 'sensitive')
                        executar_ciclo(s, direcao, tf_sinal)
                        break
                time.sleep(0.3)
            except BotParado:
                s.add_log("🛑 Estrategia interrompida pelo PARAR.", 'info')
                break
            except Exception as e:
                s.add_log(f"Erro no loop: {e}", 'error')
                time.sleep(5)

        s.bot_rodando = False

# ========== THREADS DE MANUTENÇÃO (agora varrem TODAS as sessoes) ==========

def keep_alive_thread():
    while True:
        time.sleep(20)
        for s in sessoes_ativas():
            if s.conectado and s.API and s.email:
                try:
                    s.API.get_server_timestamp()
                except:
                    pass

def monitor_conexao_thread():
    while True:
        time.sleep(5)
        for s in sessoes_ativas():
            if s.email:
                try:
                    if not verificar_saude_api(s):
                        s.add_log("⚠️ Monitor detectou falha. Tentando reconectar...", 'error')
                        if conectar_iq(s):
                            s.add_log("✅ Reconexão pelo monitor bem-sucedida!", 'win')
                        else:
                            s.add_log("❌ Falha na reconexão pelo monitor.", 'error')
                except Exception:
                    pass

def analise_mercado_loop():
    """Analise do painel (RSI/MM/fase). Roda por sessao conectada."""
    while True:
        for s in sessoes_ativas():
            if s.conectado and s.API:
                try:
                    velas = s.API.get_candles(s.par, 60, 30, time.time())
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
                        s.ultima_analise = {
                            'rsi': round(rsi_val, 1), 'mm5': round(mm5, 5) if mm5 else 0,
                            'mm10': round(mm10, 5) if mm10 else 0, 'mm20': round(mm20, 5) if mm20 else 0,
                            'stoch': round(estoc_val, 1), 'fase': fase,
                            'preco': round(preco_atual, 5) if preco_atual else 0
                        }
                except Exception:
                    pass
        time.sleep(2)

threading.Thread(target=analise_mercado_loop, daemon=True).start()
threading.Thread(target=keep_alive_thread, daemon=True).start()
threading.Thread(target=monitor_conexao_thread, daemon=True).start()
threading.Thread(target=limpar_sessoes_thread, daemon=True).start()

def sincronizar_html_local():
    try:
        os.makedirs("templates", exist_ok=True)
        HTML_URL = "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/tesla_369_bot/templates/index.html"
        response = requests.get(HTML_URL, timeout=10)
        if response.status_code == 200:
            with open("templates/index.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("✅ HTML sincronizado!")
            return True
    except Exception as e: print(f"❌ Erro HTML: {e}")
    return False

# ========== ROTAS FLASK (todas isoladas por sessao) ==========

@app.route('/')
def index():
    s = get_sessao()
    skins = carregar_todas_skins_do_firebase()
    skin = next((k for k in skins if k.get('id') == s.skin_atual), skins[0] if skins else list(get_skins_fallback().values())[0])
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

@app.route('/status')
def status():
    s = get_sessao()
    u = carregar_usuario(s.email) if s.email else {}
    # aproveita este load (que ja acontece a cada poll) p/ manter o cache de VOLTS
    if u and not s.volt_ja_consumido:
        s.volts_cache = u.get('moedas', s.volts_cache)

    skins = carregar_todas_skins_do_firebase()
    skins_compradas = u.get('skins_compradas', ['skin_padrao']) if u else ['skin_padrao']
    skin_atual = u.get('skin_atual', 'skin_padrao') if u else 'skin_padrao'
    skins_status = [{
        'id': k.get('id'), 'nome': k.get('nome'), 'desc': k.get('desc'),
        'preco_moedas': k.get('preco_moedas'), 'categoria': k.get('categoria'),
        'comprado': k.get('id') in skins_compradas, 'ativo': k.get('id') == skin_atual
    } for k in skins]

    estrategias_info = carregar_informacoes_estrategias()
    estrategias_compradas = u.get('estrategias_compradas', ['v_sensitivo']) if u else ['v_sensitivo']
    estrategia_atual = u.get('estrategia_atual', 'v_sensitivo') if u else 'v_sensitivo'
    estrategia_nome = estrategias_info[estrategia_atual].get('nome', estrategia_atual) if estrategia_atual in estrategias_info else "Nenhuma"

    # get_balance() explode quando o socket morre - e o /status e' consultado a
    # cada poucos segundos, entao NAO pode estourar 500.
    banca_atual = s.ultima_banca_conhecida
    if s.API:
        try:
            banca_atual = s.API.get_balance()
            s.ultima_banca_conhecida = banca_atual
        except Exception:
            s.conectado = False

    return jsonify({
        'conectado': s.conectado, 'rodando': s.bot_rodando, 'email': s.email,
        'banca': banca_atual, 'lucro': s.lucro, 'ops': s.num_operacoes, 'sinal': s.ultimo_sinal,
        'logs': s.logs_html(40), 'moedas': u.get('moedas', 0) if u else 0,
        'skin_id': skin_atual, 'skins_status': skins_status,
        'estrategia': estrategia_atual, 'estrategia_nome': estrategia_nome,
        'estrategias_compradas': estrategias_compradas,
        'estrategias_disponiveis': {k: {'nome': v['nome'], 'desc': v['desc'], 'preco_moedas': v['preco_moedas'], 'gratis': v['gratis']} for k, v in estrategias_info.items()},
        'analise': s.ultima_analise, 'bot_version': BOT_VERSION,
        'par': s.par
    })

# cache dos pares: evita bater na corretora toda hora (e o dado muda pouco)
_pares_cache = {'dados': None, 'quando': 0}
PARES_TTL = 120

@app.route('/pares', methods=['GET'])
def listar_pares():
    """Lista os pares de opcao BINARIA (turbo/binary) abertos, separados em
    normais e OTC.

    ⚠️ NAO usamos get_all_open_time(): por dentro ele consulta cfd/forex/crypto
    via get_instruments(), que tem um `while ... == None:` SEM timeout e, no
    erro, chama self.connect() - refazendo o login. Era isso que travava o app
    em "Conectando..." quando a tela de pares carregava junto do login.

    Usamos get_all_init_v2(), que so' traz binary/turbo (o que o bot opera) e
    tem timeout proprio de 30s. Ainda assim rodamos com um teto de tempo.
    """
    s = get_sessao()
    if not s.conectado or not s.API:
        return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})

    agora = time.time()
    if _pares_cache['dados'] and (agora - _pares_cache['quando']) < PARES_TTL:
        cache = dict(_pares_cache['dados'])
        cache['atual'] = s.par
        return jsonify(cache)

    resultado = {}
    def _buscar():
        try:
            resultado['dados'] = s.API.get_all_init_v2()
        except Exception as e:
            resultado['erro'] = str(e)

    t = threading.Thread(target=_buscar, daemon=True)
    t.start()
    t.join(20)          # teto duro: nunca prende a interface
    if t.is_alive() or 'erro' in resultado or not resultado.get('dados'):
        return jsonify({'ok': False, 'erro': 'A corretora demorou a responder. Tente o botao de recarregar.'})

    dados = resultado['dados']
    normais, otc = [], []
    try:
        for categoria in ('turbo', 'binary'):
            bloco = (dados.get(categoria) or {}).get('actives') or {}
            for _id, ativo in bloco.items():
                nome = str(ativo.get('name', ''))
                if '.' in nome:
                    nome = nome.split('.')[1]
                if not nome:
                    continue
                # aberto = habilitado e nao suspenso (mesma regra da lib)
                aberto = bool(ativo.get('enabled')) and not bool(ativo.get('is_suspended'))
                if not aberto:
                    continue
                if nome.endswith('-OTC'):
                    if nome not in otc: otc.append(nome)
                else:
                    if nome not in normais: normais.append(nome)
    except Exception as e:
        return jsonify({'ok': False, 'erro': f'Formato inesperado: {str(e)[:60]}'})

    normais.sort(); otc.sort()
    resposta = {'ok': True, 'normais': normais, 'otc': otc, 'atual': s.par}
    _pares_cache['dados'] = {'ok': True, 'normais': normais, 'otc': otc}
    _pares_cache['quando'] = agora
    return jsonify(resposta)

@app.route('/set_par', methods=['POST'])
def set_par():
    """Define o par que o bot vai operar - VALIDANDO antes.

    Nem todo ativo que aparece como "aberto" devolve historico de velas por esta
    API (acoes/indices costumam falhar, pares de forex e OTC costumam funcionar).
    Antes o aluno so' descobria isso quando o bot ja' estava rodando e a
    estrategia reclamava "dados insuficientes". Agora testamos na hora da escolha
    e recusamos o par com uma mensagem clara, mantendo o anterior.
    """
    s = get_sessao()
    par = (request.json.get('par') or '').strip().upper()
    if not par:
        return jsonify({'ok': False, 'erro': 'Par vazio'})
    if not s.API or not s.conectado:
        return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})

    # testa se o ativo devolve velas (com teto de tempo pra nao travar a tela)
    teste = {}
    def _testar():
        try:
            teste['velas'] = s.API.get_candles(par, 60, 30, time.time())
        except Exception as e:
            teste['erro'] = str(e)

    t = threading.Thread(target=_testar, daemon=True)
    t.start()
    t.join(12)
    if t.is_alive():
        return jsonify({'ok': False, 'erro': f'{par}: a corretora nao respondeu a tempo.'})
    if 'erro' in teste:
        return jsonify({'ok': False, 'erro': f'{par}: {teste["erro"][:60]}'})

    velas = teste.get('velas') or []
    if len(velas) < 20:
        return jsonify({'ok': False,
                        'erro': f'{par} nao fornece historico suficiente ({len(velas)} velas). '
                                f'Escolha outro - pares de moeda e OTC costumam funcionar melhor.'})

    s.par = par
    s.add_log(f"📌 Par alterado para: {par} ({len(velas)} velas OK)", 'info')
    return jsonify({'ok': True, 'par': par, 'velas': len(velas)})

@app.route('/set_percentual', methods=['POST'])
def set_percentual():
    s = get_sessao()
    s.percentual_banca = request.json.get('percentual', 15)
    return jsonify({'ok': True})

@app.route('/selecionar_estrategia', methods=['POST'])
def selecionar_estrategia():
    s = get_sessao()
    est_id = request.json.get('estrategia', 'v_sensitivo')
    if not s.email: return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    u = carregar_usuario(s.email)
    if not u: return jsonify({'ok': False, 'erro': 'Usuario nao encontrado'})
    estrategias_info = carregar_informacoes_estrategias()
    if est_id not in estrategias_info: return jsonify({'ok': False, 'erro': 'Estrategia invalida'})

    estrategias_compradas = u.get('estrategias_compradas', ['v_sensitivo'])
    if est_id not in estrategias_compradas:
        if not estrategias_info[est_id].get('gratis', False):
            return jsonify({'ok': False, 'erro': 'Estrategia bloqueada! Compre na loja.'})
        u.setdefault('estrategias_compradas', ['v_sensitivo']).append(est_id)
    u['estrategia_atual'] = est_id
    salvar_usuario(s.email, u)
    s.estrategia_atual = est_id
    s.estrategia_injetada = None   # forca reinjecao na proxima operacao
    s.add_log(f"🧠 Estrategia: {estrategias_info[est_id]['nome']}", 'indicator')
    return jsonify({'ok': True})


@app.route('/comprar_estrategia', methods=['POST'])
def comprar_estrategia():
    s = get_sessao()
    est_id = request.json.get('estrategia_id', '')
    if not s.email: return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    estrategias_info = carregar_informacoes_estrategias()
    u = carregar_usuario(s.email)
    if not u or est_id not in estrategias_info: return jsonify({'ok': False, 'erro': 'Parametros invalidos'})

    if 'estrategias_compradas' not in u: u['estrategias_compradas'] = ['v_sensitivo']
    if est_id in u['estrategias_compradas']:
        u['estrategia_atual'] = est_id
        salvar_usuario(s.email, u)
        s.estrategia_atual = est_id
        s.estrategia_injetada = None
        return jsonify({'ok': True, 'moedas': u['moedas'], 'msg': 'Ja adquirida!'})

    preco = estrategias_info[est_id].get('preco_moedas', 0)
    if u.get('moedas', 0) < preco: return jsonify({'ok': False, 'erro': f'Precisa de {preco} ⚡'})
    u['moedas'] -= preco
    u['estrategias_compradas'].append(est_id)
    u['estrategia_atual'] = est_id
    salvar_usuario(s.email, u)
    s.volts_cache = u['moedas']
    s.estrategia_atual = est_id
    s.estrategia_injetada = None
    s.add_log(f"🛒 Estrategia: {estrategias_info[est_id]['nome']}", 'win')
    return jsonify({'ok': True, 'moedas': u['moedas'], 'msg': 'Sucesso!'})


def _conectar_com_timeout(api, timeout=25):
    """Roda api.connect() numa thread com TIMEOUT.

    A lib iqoption-faria tem um `while global_value.balance_id == None: pass`
    interno SEM timeout: se o balance_id nao chega (rede oscilando, websocket
    meio conectado), o connect() TRAVA pra sempre e o app fica em "Conectando..."
    eternamente. Aqui rodamos em thread separada; se estourar o tempo, desistimos
    e devolvemos um erro amigavel em vez de pendurar o app.

    Retorna (status, reason). status=False + reason explica se deu timeout.
    """
    resultado = {}
    def _run():
        try:
            resultado['ret'] = api.connect()
        except Exception as e:
            resultado['erro'] = e
    t = threading.Thread(target=_run, daemon=True)
    t.start()
    t.join(timeout)
    if t.is_alive():
        # ainda travado no connect() da lib apos o timeout
        try:
            api.close()
        except Exception:
            pass
        return False, "TIMEOUT: a corretora nao respondeu a tempo. Tente conectar de novo."
    if 'erro' in resultado:
        return False, str(resultado['erro'])[:100]
    return resultado.get('ret', (False, "Falha desconhecida ao conectar"))


@app.route('/conectar', methods=['POST'])
def conectar():
    s = get_sessao()
    try:
        d = request.get_json()
        email, senha, tipo = d.get('email', '').strip(), d.get('senha', '').strip(), d.get('tipo', 'PRACTICE')
        if not email or not senha: return jsonify({'ok': False, 'erro': 'Credenciais em branco'})

        # 🔧 Um mesmo email logado em 2 sessoes ao mesmo tempo brigaria pelos VOLTS
        # e pela mesma conta da corretora. Derruba a sessao antiga daquele email.
        for outra in sessoes_ativas():
            if outra is not s and outra.email == email:
                outra.add_log("⚠️ Esta conta foi conectada em outro lugar. Sessao encerrada aqui.", 'error')
                outra.bot_rodando = False
                outra.conectado = False
                try:
                    if outra.API: outra.API.close()
                except Exception:
                    pass
                outra.API = None

        s.email = email
        s.senha = senha
        s.tipo_conta = tipo

        # 🔧 2 tentativas: o connect() da lib as vezes trava esperando o
        # balance_id (bug interno sem timeout). Se a 1a der timeout, uma 2a
        # tentativa com objeto novo quase sempre resolve - por isso o app as
        # vezes "so' conectava na 2a vez" que voce tentava manualmente.
        status_conn, reason = False, "nao tentou"
        for tentativa in range(1, 3):
            s.API = IQ_Option(email, senha)
            status_conn, reason = _conectar_com_timeout(s.API, timeout=20)
            if status_conn:
                break
            # nao adianta repetir se a senha esta errada
            if reason and ('password' in str(reason).lower() or 'invalid' in str(reason).lower() or 'credential' in str(reason).lower()):
                break
            try:
                s.API.close()
            except Exception:
                pass
        if not status_conn: return jsonify({'ok': False, 'erro': str(reason)[:100]})
        s.API.change_balance(tipo)
        s.conectado = True

        usuario = carregar_usuario(email) or criar_usuario(email)
        hoje = str(datetime.now())[:10]
        if usuario.get('moedas_ganhas_hoje') != hoje:
            usuario['moedas'] = usuario.get('moedas', 0) + 1
            usuario['moedas_ganhas_hoje'] = hoje
            salvar_usuario(email, usuario)
        s.skin_atual = usuario.get('skin_atual', 'skin_padrao')
        s.estrategia_atual = usuario.get('estrategia_atual', 'v_sensitivo')
        s.volts_cache = usuario.get('moedas', 0)
        s.add_log('🔌 Conectado!', 'info')
        s.add_log(f'✅ ${s.API.get_balance():.2f} | ⚡ {usuario.get("moedas", 0)} VOLTS | Conta: {tipo}', 'win')
        return jsonify({'ok': True, 'moedas': usuario.get('moedas', 0), 'refresh': True})
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)[:100]})

@app.route('/comecar_operar', methods=['POST'])
def comecar_operar():
    s = get_sessao()
    try:
        if not s.conectado: return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
        estrategias_info = carregar_informacoes_estrategias()
        if not estrategias_info or s.estrategia_atual not in estrategias_info:
            return jsonify({'ok': False, 'erro': f'❌ Estrategia "{s.estrategia_atual}" invalida!'})

        usuario = carregar_usuario(s.email)
        if not usuario: return jsonify({'ok': False, 'erro': 'Usuario nao encontrado!'})
        if usuario.get('moedas', 0) < 1: return jsonify({'ok': False, 'erro': 'Sem VOLTS! Compre na loja.'})

        # 🔧 Se ha uma thread anterior AINDA finalizando (ex: acabou de ganhar e
        # esta no finally), NAO recusa nem cria uma segunda. Espera ela encerrar
        # de vez e entao inicia limpo. Antes, reiniciar logo apos um WIN caia num
        # limbo: o /comecar era recusado ("bot ja rodando"), mas a tela ja tinha
        # trocado pro botao PARAR - e ai o PARAR nao tinha o que parar.
        if s.bot_thread and s.bot_thread.is_alive():
            # se ja esta operando de verdade, nao reinicia
            if s.bot_rodando and not s.stop_gain:
                return jsonify({'ok': False, 'erro': 'Bot ja rodando!'})
            # senao, esta so' finalizando: sinaliza parada e espera encerrar
            s.bot_rodando = False
            s.bot_thread.join(timeout=8)

        # garante estado limpo antes de comecar
        s.stop_gain = False
        s.estrategia_injetada = None
        s.bot_rodando = True
        s.bot_thread = threading.Thread(target=bot_loop, args=(s,), daemon=True)
        s.bot_thread.start()
        return jsonify({'ok': True, 'moedas': usuario['moedas']})
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)[:100]})

@app.route('/parar', methods=['POST'])
def parar():
    s = get_sessao()
    data = request.json or {}
    s.add_log("🛑 Parando o bot...", 'info')
    s.bot_rodando = False
    s.volt_ja_consumido = False

    if data.get('desconectar'):
        s.conectado = False
        try:
            if s.API: s.API.close()
        except Exception:
            pass
        s.API = None
        s.senha = ""

        # 🔧 REGRA NOVA (pedido do Austin):
        #   - FECHAR o app  -> o bot CONTINUA (Foreground Service segura o server)
        #   - DESCONECTAR    -> mata TUDO (encerra o servico e fecha o app)
        # No APK, avisamos o Android pra parar o TeslaService e fechar o app.
        # No PC (sem Android), derruba o processo local mesmo.
        s.add_log("🔌 Desconectado. Encerrando o app...", 'info')
        try:
            notificar_android('encerrar', 'TESLA 369', 'Desconectado.', 0)
        except Exception:
            pass
        def shutdown_server():
            time.sleep(1.2)
            try:
                os.kill(os.getpid(), signal.SIGTERM)
            except Exception:
                pass
        threading.Thread(target=shutdown_server, daemon=True).start()
        return jsonify({'ok': True, 'shutdown': True})

        s.add_log("🔌 Desconectado com sucesso!", 'win')
        return jsonify({'ok': True, 'shutdown': False})

    s.add_log("✅ Bot parado!", 'win')
    return jsonify({'ok': True, 'shutdown': False})

@app.route('/comprar_skin', methods=['POST'])
def comprar_skin():
    s = get_sessao()
    skin_id = request.get_json().get('skin_id', '')
    if not s.email: return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    skin = carregar_skin_do_firebase(skin_id) or next((k for k in carregar_todas_skins_do_firebase() if k.get('id') == skin_id), None)
    if not skin: return jsonify({'ok': False, 'erro': 'Skin nao encontrada'})
    usuario = carregar_usuario(s.email)
    if not usuario: return jsonify({'ok': False, 'erro': 'Usuario invalido'})

    if skin.get('preco_moedas', 0) == 0:
        if skin_id not in usuario.setdefault('skins_compradas', ['skin_padrao']):
            usuario['skins_compradas'].append(skin_id)
        usuario['skin_atual'] = skin_id
        salvar_usuario(s.email, usuario)
        s.skin_atual = skin_id
        return jsonify({'ok': True, 'moedas': usuario.get('moedas', 0), 'msg': 'Skin gratis ativada!', 'refresh': True})

    if skin_id in usuario.setdefault('skins_compradas', ['skin_padrao']):
        usuario['skin_atual'] = skin_id
        salvar_usuario(s.email, usuario)
        s.skin_atual = skin_id
        return jsonify({'ok': True, 'moedas': usuario['moedas'], 'msg': 'Ativada!', 'refresh': True})

    if usuario.get('moedas', 0) < skin.get('preco_moedas', 0):
        return jsonify({'ok': False, 'erro': f'Precisa de {skin["preco_moedas"]} ⚡'})
    usuario['moedas'] -= skin['preco_moedas']
    usuario['skins_compradas'].append(skin_id)
    usuario['skin_atual'] = skin_id
    salvar_usuario(s.email, usuario)
    s.volts_cache = usuario['moedas']
    s.skin_atual = skin_id
    return jsonify({'ok': True, 'moedas': usuario['moedas'], 'msg': 'Skin adquirida!', 'refresh': True})

@app.route('/ativar_skin', methods=['POST'])
def ativar_skin():
    s = get_sessao()
    skin_id = request.get_json().get('skin_id', '')
    if not s.email: return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    usuario = carregar_usuario(s.email)
    if not usuario: return jsonify({'ok': False, 'erro': 'Usuario nao encontrado'})
    if skin_id not in usuario.setdefault('skins_compradas', ['skin_padrao']):
        skin = carregar_skin_do_firebase(skin_id)
        if skin and skin.get('preco_moedas', 0) > 0:
            return jsonify({'ok': False, 'erro': 'Compre primeiro!'})
        usuario['skins_compradas'].append(skin_id)
    usuario['skin_atual'] = skin_id
    salvar_usuario(s.email, usuario)
    s.skin_atual = skin_id
    return jsonify({'ok': True, 'refresh': True})

# ========== PIX (o worker Cloudflare fala com o Mercado Pago) ==========

def _sessao_http():
    """Sessao HTTP com User-Agent fixo, igual ao PDV."""
    h = requests.Session()
    h.headers.update({"User-Agent": "TESLA-369/16", "Connection": "close"})
    return h

def criar_pix_backend(email, plano_id):
    """Pede ao worker dedicado do TESLA 369 que crie a cobranca PIX.
    So' o worker conhece o token do Mercado Pago e a tabela de precos."""
    ultimo_erro = "erro desconhecido"
    for _ in range(2):
        try:
            with _sessao_http() as h:
                res = h.post(f"{BACKEND_PAGAMENTOS_URL}/criar",
                    json={"email": email, "plano_id": plano_id}, timeout=10)
            try:
                d = res.json()
            except Exception:
                ultimo_erro = f"resposta inesperada do servidor (HTTP {res.status_code})"
                time.sleep(1.0)
                continue
            if res.status_code == 200 and d.get('success'):
                return {"pix_id": d['pix_id'], "qr_code": d.get('qr_code', ''),
                        "qr_code_base64": d.get('qr_code_base64', '')}
            ultimo_erro = d.get('error') or f"HTTP {res.status_code}"
            return {"erro": ultimo_erro}
        except Exception as e:
            ultimo_erro = str(e)
            time.sleep(0.8)
    return {"erro": f"nao foi possivel falar com o servidor de pagamentos ({ultimo_erro})"}

def verificar_pagamento_backend(pix_id):
    if not pix_id:
        return False
    for _ in range(2):
        try:
            with _sessao_http() as h:
                res = h.get(f"{BACKEND_PAGAMENTOS_URL}/verificar", params={"id": pix_id}, timeout=8)
            if res.status_code == 200:
                return bool(res.json().get('pago'))
            return False
        except Exception:
            time.sleep(0.6)
    return False

def _creditar_volts(email, moedas):
    """Credita VOLTS no Firebase e sincroniza o cache de quem estiver online."""
    u = carregar_usuario(email) or criar_usuario(email)
    u['moedas'] = u.get('moedas', 0) + moedas
    salvar_usuario(email, u)
    for s in sessoes_ativas():
        if s.email == email:
            s.volts_cache = u['moedas']
            s.add_log(f"💰 PIX Confirmado! +{moedas} VOLTS", "win")
    return u

@app.route('/criar_pix', methods=['POST'])
def criar_pix():
    s = get_sessao()
    d = request.get_json()
    plano = next((p for p in PLANOS if p['id'] == int(d.get('plano_id') or 1)), None)
    if not plano:
        return jsonify({'sucesso': False, 'erro': 'Plano invalido'})
    email = (d.get('email') or s.email or '').strip()
    if not email:
        return jsonify({'sucesso': False, 'erro': 'Informe o email para receber os VOLTS'})

    if MODO_SIMULACAO:
        pix_id = str(uuid.uuid4())[:8]
        pagamentos_pendentes[pix_id] = {'email': email, 'plano_id': plano['id'], 'moedas': plano['moedas'], 'valor': plano['preco'], 'pago': False, 'criado_em': str(datetime.now())[:19]}
        return jsonify({'sucesso': True, 'simulacao': True, 'pix_id': pix_id,
            'qr_code': f"00020126360014BR.GOV.BCB.PIX0136{email}5204000053039865404{plano['preco']:.2f}5802BR5909Tesla3696009Sao Paulo62070503***6304E3F9",
            'qr_code_base64': '', 'valor': plano['preco'], 'moedas': plano['moedas']})

    resultado_pix = criar_pix_backend(email, plano['id'])
    if resultado_pix and resultado_pix.get('pix_id'):
        pix_id = resultado_pix['pix_id']
        pagamentos_pendentes[pix_id] = {'email': email, 'plano_id': plano['id'], 'moedas': plano['moedas'], 'valor': plano['preco'], 'pago': False, 'criado_em': str(datetime.now())[:19]}
        return jsonify({'sucesso': True, 'simulacao': False, 'pix_id': pix_id,
            'qr_code': resultado_pix['qr_code'], 'qr_code_base64': resultado_pix['qr_code_base64'],
            'valor': plano['preco'], 'moedas': plano['moedas']})
    motivo = (resultado_pix or {}).get('erro', 'Erro desconhecido')
    return jsonify({'sucesso': False, 'erro': f'Erro ao gerar PIX: {motivo}'})

@app.route('/verificar_pix', methods=['POST'])
def verificar_pix():
    pix_id = request.get_json().get('pix_id', '')
    dados = pagamentos_pendentes.get(pix_id)
    if not dados:
        return jsonify({'pago': False})
    if dados['pago']:
        return jsonify({'pago': True})
    if MODO_SIMULACAO:
        return jsonify({'pago': False})
    if verificar_pagamento_backend(pix_id):
        dados['pago'] = True
        u = _creditar_volts(dados['email'], dados['moedas'])
        return jsonify({'pago': True, 'moedas': dados['moedas'], 'saldo': u.get('moedas', 0)})
    return jsonify({'pago': False})

def verificador_automatico_pix():
    while True:
        time.sleep(10)
        try:
            for pix_id, dados in list(pagamentos_pendentes.items()):
                if dados.get('pago', False): continue
                if MODO_SIMULACAO: continue
                if verificar_pagamento_backend(pix_id):
                    dados['pago'] = True
                    _creditar_volts(dados['email'], dados['moedas'])
                    print(f"💰 PIX Confirmado! +{dados['moedas']} VOLTS para {dados['email']}")
        except: pass

threading.Thread(target=verificador_automatico_pix, daemon=True).start()

# ========== CHAT / RANKING / RELATORIO ==========

@app.route('/chat_enviar', methods=['POST'])
def chat_enviar():
    try:
        data = request.json
        requests.post(f'{FB_URL}/tesla_369/chat.json', json={
            'nome': data.get('nome', 'Anonimo')[:15], 'msg': data.get('msg', '')[:200],
            'hora': datetime.now().strftime('%H:%M')
        }, timeout=5)
    except: pass
    return jsonify({'ok': True})

@app.route('/chat_mensagens')
def chat_mensagens_route():
    try:
        r = requests.get(f'{FB_URL}/tesla_369/chat.json?orderBy="$key"&limitToLast=50', timeout=5)
        msgs = list(r.json().values()) if r.status_code == 200 and r.json() else []
        online = len([s for s in sessoes_ativas() if s.conectado])
        return jsonify({'messages': msgs, 'online': max(1, online)})
    except:
        return jsonify({'messages': [], 'online': 1})

@app.route('/ranking')
def ranking():
    ranking_list = []
    try:
        usuarios = requests.get(f'{FB_URL}/tesla_369/usuarios.json', timeout=8).json() or {}
        for k, ud in usuarios.items():
            if ud:
                ranking_list.append({
                    'email': ud.get('email', 'N/A'), 'lucro_total': round(ud.get('lucro_total', 0), 2),
                    'total_wins': ud.get('total_wins', 0), 'total_losses': ud.get('total_losses', 0),
                    'total_ciclos': ud.get('total_ciclos', 0),
                    'taxa': round((ud.get('total_wins', 0) / max(ud.get('total_ciclos', 1), 1)) * 100, 1),
                    'banca_atual': round(ud.get('banca_atual', 0), 2)
                })
    except: pass
    ranking_list.sort(key=lambda x: x['lucro_total'], reverse=True)
    tc = sum(x['total_ciclos'] for x in ranking_list)
    tw = sum(x['total_wins'] for x in ranking_list)
    return jsonify({'ranking': ranking_list, 'stats': {'total_usuarios': len(ranking_list), 'total_ops': tc, 'total_wins': tw, 'taxa_global': round((tw/max(tc,1))*100,1)}})

# cache: agregar o historico de TODOS os usuarios e' caro. Recalcula a cada 3 min.
_stats_est_cache = {'dados': None, 'quando': 0}
STATS_EST_TTL = 180

@app.route('/stats_estrategias')
def stats_estrategias():
    """Placar das estrategias somando TODOS os bots da comunidade.

    Devolve, por estrategia: wins/losses de HOJE e de TODO O PERIODO.
    A fonte e' o historico_operacoes de cada usuario, que ja' grava
    {'resultado': 'WIN'|'LOSS', 'estrategia': 'NOME', 'data': 'YYYY-MM-DD HH:MM:SS'}.
    """
    agora = time.time()
    if _stats_est_cache['dados'] and (agora - _stats_est_cache['quando']) < STATS_EST_TTL:
        return jsonify(_stats_est_cache['dados'])

    hoje = str(datetime.now())[:10]
    acc = {}   # nome -> contadores

    def _slot(nome):
        if nome not in acc:
            acc[nome] = {'wins': 0, 'losses': 0, 'wins_hoje': 0, 'losses_hoje': 0,
                         'lucro': 0.0, 'lucro_hoje': 0.0}
        return acc[nome]

    try:
        usuarios = requests.get(f'{FB_URL}/tesla_369/usuarios.json', timeout=10).json() or {}
        for _k, ud in usuarios.items():
            if not ud:
                continue
            for op in (ud.get('historico_operacoes') or []):
                # 🔧 conta SO' ciclos completos. Registros antigos (sem 'tipo') e
                # entradas isoladas ficam de fora: um ciclo LOSS->LOSS->WIN e' UMA
                # vitoria, e nao "2 derrotas + 1 vitoria" como seria por entrada.
                if op.get('tipo') != 'ciclo':
                    continue
                nome = str(op.get('estrategia') or '').strip().upper()
                if not nome:
                    continue
                d = _slot(nome)
                venceu = str(op.get('resultado', '')).upper() == 'WIN'
                lucro = float(op.get('lucro') or 0)
                if venceu:
                    d['wins'] += 1
                else:
                    d['losses'] += 1
                d['lucro'] += lucro
                if str(op.get('data', ''))[:10] == hoje:
                    if venceu:
                        d['wins_hoje'] += 1
                    else:
                        d['losses_hoje'] += 1
                    d['lucro_hoje'] += lucro
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)[:80], 'estrategias': {}})

    saida = {}
    for nome, d in acc.items():
        total = d['wins'] + d['losses']
        total_hoje = d['wins_hoje'] + d['losses_hoje']
        saida[nome] = {
            'wins': d['wins'], 'losses': d['losses'], 'total': total,
            'taxa': round((d['wins'] / total) * 100, 1) if total else 0.0,
            'wins_hoje': d['wins_hoje'], 'losses_hoje': d['losses_hoje'],
            'total_hoje': total_hoje,
            'taxa_hoje': round((d['wins_hoje'] / total_hoje) * 100, 1) if total_hoje else 0.0,
            'lucro': round(d['lucro'], 2), 'lucro_hoje': round(d['lucro_hoje'], 2),
        }

    resposta = {'ok': True, 'estrategias': saida, 'data': hoje,
                'amostra_total': sum(v['total'] for v in saida.values())}
    _stats_est_cache['dados'] = resposta
    _stats_est_cache['quando'] = agora
    return jsonify(resposta)

@app.route('/relatorio')
def relatorio():
    s = get_sessao()
    email = request.args.get('email', '') or s.email
    return jsonify(carregar_usuario(email) or {'erro': 'Nao encontrado'})

@app.route('/resetar', methods=['POST'])
def resetar():
    s = get_sessao()
    email = request.json.get('email', '') or s.email
    u = carregar_usuario(email)
    if not u: return jsonify({'ok': False, 'msg': 'Nao encontrado'})
    u.update({'total_ciclos':0,'total_wins':0,'total_losses':0,'total_gasto':0.0,'total_ganho':0.0,
              'lucro_total':0.0,'historico_operacoes':[],'dias_ativos':0,'banca_atual':0.0,
              'moedas_ganhas_hoje':str(datetime.now())[:10]})
    salvar_usuario(email, u)
    return jsonify({'ok': True, 'msg': 'Resetado!'})

@app.route('/sinal', methods=['POST'])
def receber_sinal():
    s = get_sessao()
    if not s.bot_rodando: return jsonify({'ok': False, 'erro': 'Bot em repouso.'})
    if not s.conectado: return jsonify({'ok': False, 'erro': 'IQ Option offline.'})
    direcao = request.get_json().get('direcao', '').lower()
    if direcao not in ['call', 'put']: return jsonify({'ok': False, 'erro': 'Alvo invalido'})
    s.add_log(f"📡 Sinal externo: {direcao.upper()}", 'sensitive')
    threading.Thread(target=executar_ciclo, args=(s, direcao, s.timeframe_atual), daemon=True).start()
    return jsonify({'ok': True})

@app.route('/sessoes')
def listar_sessoes():
    """Diagnostico: quem esta online agora (util pra debugar o servidor cloud)."""
    return jsonify({'total': len(sessoes_ativas()), 'sessoes': [{
        'sid': x.sid[:8], 'email': x.email, 'conectado': x.conectado,
        'rodando': x.bot_rodando, 'estrategia': x.estrategia_atual,
        'timeframe': x.timeframe_atual
    } for x in sessoes_ativas()]})

if __name__ == '__main__':
    print("=" * 70)
    print(f"⚡ {BOT_NAME} v{BOT_VERSION} - MULTICONTA + TIMEFRAME DINAMICO ⚡")
    print("✅ MULTICONTA: cada aluno tem sua sessao isolada (cookie)")
    print("✅ TIMEFRAME: a estrategia manda o timeframe (M1/M5/M15...)")
    print("✅ EXPIRACAO: buy() usa o timeframe real (antes era M1 hardcoded)")
    print("✅ VELA: alinhamento correto p/ qualquer timeframe")
    print("✅ RECONEXAO INTELIGENTE (backoff + relogin duro p/ WiFi<->4G)")
    print("=" * 70)

    print("\n🔍 Carregando skins do Firebase...")
    print(f"📦 {len(carregar_todas_skins_do_firebase())} skins disponiveis")
    print("\n🔍 Carregando estrategias do Firebase...")
    print(f"📊 {len(carregar_informacoes_estrategias())} estrategias disponiveis")

    sincronizar_html_local()

    port = int(os.environ.get('PORT', 5000))
    print(f"\n🚀 Servidor rodando em http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
