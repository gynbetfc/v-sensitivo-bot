#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ⚡ TESLA 369 BOT v9.0.1 Cloud ⚡
# ESTRATÉGIAS BAIXADAS UMA VEZ E INJETADAS NA FUNÇÃO LOCAL
# NÃO PRECISA BAIXAR A ESTRATÉGIA A CADA CICLO!

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
import sys

warnings.filterwarnings("ignore")
app = Flask(__name__)

# ============= CONFIGURAÇÕES DE LINKS CLOUD =============
FB_URL = "https://nexos-40654-default-rtdb.firebaseio.com"
print("✅ Firebase HTTP REST configurado!")

HTML_URL = "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/tesla_369_bot/templates/index.html"
GIT_RAW_SKINS = "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/tesla_369_bot/skins/skins.py"
GIT_RAW_ESTRATEGIAS_BASE = "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/tesla_369_bot/estrategias"
GIT_RAW_ESTRATEGIAS_LISTA = "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/tesla_369_bot/estrategias.py"

MARTINGALE = 2
PAYOUT_PADRAO = 0.85
PERCENTUAL_BANCA = 15

MERCADO_PAGO_ACCESS_TOKEN = os.environ.get("MP_ACCESS_TOKEN", "APP_USR-4548266140377032-050311-6589fc22b166e4cb2cfad0379b28dcdf-1059299796")
MODO_SIMULACAO = False

PLANOS = [
    {'id':1,'moedas':1,'preco':0.99,'nome':'🔰 TESTE','desc':'R$0,99/VOLT','tag':'1 ciclo','bonus':''},
    {'id':2,'moedas':6,'preco':6.69,'nome':'⭐ BÁSICO','desc':'R$1,11/VOLT','tag':'6 ciclos','bonus':''},
    {'id':3,'moedas':15,'preco':9.99,'nome':'💎 INTERMEDIÁRIO','desc':'R$0,67/VOLT','tag':'15 ciclos','bonus':'🎨 1 Skin Básica GRÁTIS','desconto':'33% OFF'},
    {'id':4,'moedas':36,'preco':21.69,'nome':'🔥 PREMIUM','desc':'R$0,60/VOLT','tag':'36 ciclos','bonus':'🎨 1 Skin Premium GRÁTIS','desconto':'40% OFF'},
    {'id':5,'moedas':69,'preco':39.69,'nome':'👑 ULTRA','desc':'R$0,57/VOLT','tag':'69 ciclos','bonus':'🎨 1 Skin Lendária GRÁTIS','desconto':'69% OFF'},
]

# ============= CACHES =============
cache_skins = {"data": None, "timestamp": 0}
cache_estrategias = {"data": {}, "timestamp": 0}
cache_estrategia_carregada = {"nome": None, "codigo": None, "timestamp": 0}
CACHE_TTL = 300

# ============= FUNÇÃO VAZIA QUE RECEBERÁ A ESTRATÉGIA =============
def estrategia_atual_executar(api, par, add_log):
    """FUNÇÃO VAZIA - SERÁ SOBRESCRITA PELA ESTRATÉGIA BAIXADA DO GITHUB"""
    add_log("⚠️ Nenhuma estratégia carregada!", "error")
    return None

# ============= VARIÁVEIS GLOBAIS =============
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
volt_ja_consumido = False
estrategia_ja_injetada = False

# ============= FUNÇÕES AUXILIARES =============

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

def get_close(vela):
    if 'close' in vela:
        return vela['close']
    elif 'max' in vela:
        return vela['max']
    return 0

def get_high(vela):
    if 'high' in vela:
        return vela['high']
    elif 'max' in vela:
        return vela['max']
    return 0

def get_low(vela):
    if 'low' in vela:
        return vela['low']
    elif 'min' in vela:
        return vela['min']
    return 0

def get_cor_vela(vela):
    close = get_close(vela)
    open_v = vela.get('open', 0)
    if close > open_v:
        return 'g'
    elif close < open_v:
        return 'r'
    return 'd'

def calcular_rsi(velas, periodo=14):
    if len(velas) < periodo + 1:
        return 50
    ganhos = []
    perdas = []
    for i in range(1, len(velas)):
        close_atual = get_close(velas[i])
        close_anterior = get_close(velas[i-1])
        diferenca = close_atual - close_anterior
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
    if perda_media == 0:
        return 100
    rs = ganho_medio / perda_media
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calcular_estocastico(velas, periodo_k=14):
    if len(velas) < periodo_k:
        return 50
    ultimas_velas = velas[-periodo_k:]
    maior_alta = max(get_high(v) for v in ultimas_velas)
    menor_baixa = min(get_low(v) for v in ultimas_velas)
    ultimo_fechamento = get_close(velas[-1])
    if maior_alta == menor_baixa:
        return 50
    k = 100 * ((ultimo_fechamento - menor_baixa) / (maior_alta - menor_baixa))
    return k

def calcular_media_movel(velas, periodo):
    if len(velas) < periodo:
        return get_close(velas[-1]) if velas else 0
    soma = 0
    for v in velas[-periodo:]:
        soma += get_close(v)
    return soma / periodo

# ============= CARREGAR SKINS =============

def get_skins_fallback():
    return [
        {
            'id': 'skin_padrao', 'nome': '⚡ TESLA PADRÃO', 'desc': 'Tema escuro com raios dourados',
            'preco_moedas': 0, 'categoria': 'basica',
            'cor_fundo': '#0a0a1a', 'cor_panel': '#1a1a3e', 'cor_destaque': '#ffd700', 'cor_texto': '#fff',
            'cor_botao': 'linear-gradient(135deg,#cc8800,#ffd700)', 'cor_tab_ativa': '#ffd700',
            'cor_header_bg': 'linear-gradient(135deg,#1a0000,#331100,#553300,#331100,#1a0000)',
            'cor_header_borda': '#ffd700',
            'header_extra': '<div class="lightning"></div>',
            'css_extra': '.lightning{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:150px;height:150px;background:radial-gradient(circle at 30% 30%,rgba(255,215,0,0.3) 0%,rgba(255,165,0,0.15) 30%,transparent 100%);border-radius:50%;z-index:0;animation:glow 3s ease-in-out infinite;pointer-events:none}@keyframes glow{0%,100%{box-shadow:0 0 30px rgba(255,215,0,0.3)}50%{box-shadow:0 0 50px rgba(255,165,0,0.5)}}.lightning::after{content:"⚡";position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:50px;animation:float 2s ease-in-out infinite}@keyframes float{0%,100%{transform:translate(-50%,-50%) scale(1)}50%{transform:translate(-50%,-60%) scale(1.1)}}'
        },
        {
            'id': 'skin_dark', 'nome': '🌑 TESLA DARK', 'desc': 'Particulas roxas flutuantes',
            'preco_moedas': 6, 'categoria': 'basica',
            'cor_fundo': '#000000', 'cor_panel': '#0a0a0a', 'cor_destaque': '#9933ff', 'cor_texto': '#ccc',
            'cor_botao': 'linear-gradient(135deg,#4400aa,#9933ff)', 'cor_tab_ativa': '#9933ff',
            'cor_header_bg': 'linear-gradient(135deg,#000000,#110022,#220044,#110022,#000000)',
            'cor_header_borda': '#9933ff',
            'header_extra': '<canvas id="darkCanvas" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none"></canvas>',
            'css_extra': 'body{background:#000000!important}.header{border-color:#9933ff!important;box-shadow:0 0 40px rgba(153,51,255,0.3)}'
        }
    ]

def carregar_skins_da_nuvem():
    global cache_skins
    agora = time.time()
    if cache_skins["data"] and (agora - cache_skins["timestamp"]) < CACHE_TTL:
        return cache_skins["data"]
    try:
        print(f"🌐 Baixando skins: {GIT_RAW_SKINS}")
        response = requests.get(GIT_RAW_SKINS, timeout=10)
        if response.status_code == 200:
            skin_module_globals = {}
            exec(response.text, skin_module_globals)
            if 'SKINS_LIST' in skin_module_globals:
                cache_skins["data"] = skin_module_globals['SKINS_LIST']
                cache_skins["timestamp"] = agora
                print(f"✅ {len(cache_skins['data'])} skins carregadas!")
                return cache_skins["data"]
    except Exception as e:
        print(f"⚠️ Erro skins: {e}")
    return get_skins_fallback()

# ============= CARREGAR LISTA DE ESTRATÉGIAS =============

def carregar_lista_estrategias():
    try:
        response = requests.get(GIT_RAW_ESTRATEGIAS_LISTA, timeout=10)
        if response.status_code == 200:
            escopo = {}
            exec(response.text, escopo)
            if 'ESTRATEGIAS_LISTA' in escopo:
                print(f"✅ Lista de estratégias carregada: {len(escopo['ESTRATEGIAS_LISTA'])}")
                return escopo['ESTRATEGIAS_LISTA']
    except Exception as e:
        print(f"⚠️ Erro ao carregar lista: {e}")
    return ['v_sensitivo']

def carregar_informacoes_estrategias():
    """Carrega apenas as informações (nome, preço, desc) sem o código"""
    global cache_estrategias
    agora = time.time()
    
    if cache_estrategias["data"] and (agora - cache_estrategias["timestamp"]) < CACHE_TTL:
        return cache_estrategias["data"]
    
    nomes_estrategias = carregar_lista_estrategias()
    estrategias_info = {}
    
    for nome_est in nomes_estrategias:
        try:
            url = f"{GIT_RAW_ESTRATEGIAS_BASE}/{nome_est}.py"
            print(f"📥 Lendo info da estratégia: {nome_est}")
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                escopo = {}
                exec(response.text, escopo)
                if 'INFO' in escopo:
                    info = escopo['INFO']
                    estrategias_info[nome_est] = {
                        'nome': info.get('nome', nome_est.upper()),
                        'desc': info.get('desc', 'Sem descrição.'),
                        'preco_moedas': info.get('preco', 0),
                        'timeframe': info.get('timeframe', 60),
                        'gratis': info.get('preco', 0) == 0
                    }
                    print(f"   ✅ {info.get('nome', nome_est)}")
                else:
                    print(f"   ⚠️ INFO não encontrado em {nome_est}")
            else:
                print(f"   ❌ HTTP {response.status_code} - {nome_est}")
        except Exception as e:
            print(f"   ❌ Erro ao ler {nome_est}: {e}")
    
    cache_estrategias["data"] = estrategias_info
    cache_estrategias["timestamp"] = agora
    print(f"✅ Total de {len(estrategias_info)} estratégias disponíveis!")
    return estrategias_info

def carregar_e_injetar_estrategia(nome_estrategia):
    """Baixa a estratégia do GitHub e injeta na função global"""
    global estrategia_atual_executar, cache_estrategia_carregada, estrategia_ja_injetada
    
    # Verifica cache
    agora = time.time()
    if cache_estrategia_carregada["nome"] == nome_estrategia and (agora - cache_estrategia_carregada["timestamp"]) < CACHE_TTL:
        add_log(f"📦 Estratégia '{nome_estrategia}' carregada do cache", "info")
        return True
    
    try:
        url = f"{GIT_RAW_ESTRATEGIAS_BASE}/{nome_estrategia}.py"
        add_log(f"🌐 Baixando estratégia '{nome_estrategia}' do GitHub...", "info")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            codigo = response.text
            
            # Verifica se tem a função rodar_analise
            if 'def rodar_analise' not in codigo:
                add_log(f"❌ Estratégia '{nome_estrategia}' não contém a função 'rodar_analise'", "error")
                return False
            
            # Cria um ambiente para executar o código
            escopo = {}
            exec(codigo, escopo)
            
            if 'rodar_analise' in escopo:
                # Injeta na função global
                estrategia_atual_executar = escopo['rodar_analise']
                cache_estrategia_carregada["nome"] = nome_estrategia
                cache_estrategia_carregada["codigo"] = codigo
                cache_estrategia_carregada["timestamp"] = agora
                estrategia_ja_injetada = True
                add_log(f"✅ Estratégia '{nome_estrategia}' injetada com sucesso!", "win")
                return True
            else:
                add_log(f"❌ Função 'rodar_analise' não encontrada em '{nome_estrategia}'", "error")
                return False
        else:
            add_log(f"❌ Estratégia '{nome_estrategia}' não encontrada (HTTP {response.status_code})", "error")
            return False
            
    except Exception as e:
        add_log(f"❌ Erro ao carregar estratégia: {e}", "error")
        return False

# ========== FUNÇÕES DE USUÁRIO ==========

def salvar_usuario(email, dados):
    try:
        key = email.replace("@", "_").replace(".", "_").replace("#", "").replace("$", "").replace("[", "").replace("]", "").replace("/", "_")
        requests.put(f'{FB_URL}/tesla_369/usuarios/{key}.json', json=dados, timeout=5)
    except Exception as e:
        print(f"⚠️ Firebase offline: {e}")

def carregar_usuario(email):
    try:
        key = email.replace("@", "_").replace(".", "_").replace("#", "").replace("$", "").replace("[", "").replace("]", "").replace("/", "_")
        r = requests.get(f'{FB_URL}/tesla_369/usuarios/{key}.json', timeout=5)
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

# ========== FUNÇÕES DO BOT ==========

def Payout(p):
    try:
        if not API: return PAYOUT_PADRAO
        API.subscribe_strike_list(p, 1)
        for _ in range(20):
            d = API.get_digital_current_profit(p, 1)
            if d != False:
                API.unsubscribe_strike_list(p, 1)
                return round(int(d) / 100, 2)
            time.sleep(0.5)
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
        if not API: return 0
        v = API.get_candles(par, timeframe_atual, 1, time.time())
        if v and isinstance(v, list) and len(v) > 0:
            return v[0]['from']
    except:
        pass
    return 0

def aguardar_inicio_vela():
    """Aguarda o início da próxima vela (entrada na virada)"""
    segundo_atual = datetime.now().second
    if segundo_atual <= 5:
        add_log(f"   ✅ Entrada imediata (segundo {segundo_atual})", 'info')
        return True
    add_log(f"   ⏳ Aguardando início da próxima vela... (segundo {segundo_atual})", 'info')
    # Espera até o próximo minuto
    while datetime.now().second > 1:
        if not bot_rodando:
            return False
        time.sleep(0.1)
    add_log(f"   ✅ Nova vela iniciada!", 'info')
    return True

def aguardar_vela_fechar(ts_entrada):
    """Aguarda o fechamento da vela atual"""
    add_log(f"   ⏳ Aguardando fechamento da vela (timeframe {timeframe_atual}s)...", 'info')
    while True:
        if not bot_rodando:
            return False
        try:
            ts_atual = pegar_timestamp()
            if ts_atual != ts_entrada and ts_atual != 0:
                add_log(f"   ✅ Vela fechada!", 'info')
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

def consumir_volt():
    global volt_ja_consumido
    if volt_ja_consumido:
        return True
    usuario = carregar_usuario(email_usuario_atual)
    if not usuario or usuario.get('moedas', 0) < 1:
        return False
    usuario['moedas'] -= 1
    usuario['total_ciclos'] = usuario.get('total_ciclos', 0) + 1
    salvar_usuario(email_usuario_atual, usuario)
    volt_ja_consumido = True
    add_log(f"⚡ 1 VOLT consumido. Saldo: {usuario['moedas']} VOLTS", 'info')
    return True

def executar_ciclo(direcao):
    global lucro, NumDeOperacoes, STOP_GAIN_ATINGIDO, bot_rodando, volt_ja_consumido, timeframe_atual
    try:
        if not API:
            bot_rodando = False
            return

        if not consumir_volt():
            add_log("❌ Sem VOLTS!", 'error')
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
            
            # ⭐ Aguarda o início da vela antes de cada entrada
            if not aguardar_inicio_vela():
                break
            
            saldo_antes = API.get_balance()
            if saldo_antes < valor:
                add_log("❌ Saldo insuficiente!", 'error')
                break

            add_log(f"🎯 {'OPERAÇÃO' if i == 0 else f'GALE {i}'}: {direcao.upper()} ${valor:.2f}", 'info')
            st, id_ordem = API.buy(valor, par, direcao, 1)
            if not st or not id_ordem:
                try:
                    st, id_ordem = API.buy_digital_spot(par, valor, direcao, 1)
                except:
                    pass
            if not st or not id_ordem:
                add_log("❌ Rejeitado!", 'error')
                break

            add_log(f"   📝 ID da Ordem: #{id_ordem}", 'info')
            
            # ⭐ Pega o timestamp da vela atual
            ts_real = pegar_timestamp()
            if ts_real == 0:
                add_log("⚠️ Falha de sincronia, aguardando 60s...", 'warning')
                time.sleep(60)
            else:
                # ⭐ Aguarda a vela fechar (tempo real)
                if not aguardar_vela_fechar(ts_real):
                    break
            
            # ⭐ Só agora verifica o resultado
            res = verificar_resultado(saldo_antes, valor)
            lucro += round(res, 2)
            saldo_depois = API.get_balance()
            lucro_liquido = round(saldo_depois - saldo_antes, 2)

            if res > 0:
                add_log(f"🌟 WIN! +${lucro_liquido:.2f}", 'win')
                NumDeOperacoes += 1
                u = carregar_usuario(email_usuario_atual)
                if u:
                    u['total_wins'] = u.get('total_wins', 0) + 1
                    u['total_ganho'] = u.get('total_ganho', 0) + abs(lucro_liquido)
                    u['lucro_total'] = u['total_ganho'] - u.get('total_gasto', 0)
                    u['banca_atual'] = round(saldo_depois, 2)
                    u.setdefault('historico_operacoes', []).append({
                        'data': str(datetime.now())[:19], 'resultado': 'WIN',
                        'valor': valor, 'lucro': lucro_liquido,
                        'estrategia': estrategia_atual_global.upper()
                    })
                    salvar_usuario(email_usuario_atual, u)
                STOP_GAIN_ATINGIDO = True
                add_log("🎯 STOP GAIN!", 'win')
                break
            else:
                add_log(f"💀 LOSS! -${valor:.2f}", 'loss')
                u = carregar_usuario(email_usuario_atual)
                if u:
                    u['total_losses'] = u.get('total_losses', 0) + 1
                    u['total_gasto'] = u.get('total_gasto', 0) + valor
                    u['lucro_total'] = u.get('total_ganho', 0) - u['total_gasto']
                    u['banca_atual'] = round(saldo_depois, 2)
                    u.setdefault('historico_operacoes', []).append({
                        'data': str(datetime.now())[:19], 'resultado': 'LOSS',
                        'valor': valor, 'lucro': -valor,
                        'estrategia': estrategia_atual_global.upper()
                    })
                    salvar_usuario(email_usuario_atual, u)
                if i < MARTINGALE:
                    add_log(f"   ➡️ Preparando GALE {i + 1}...", 'loss')
                else:
                    add_log("   💀 CICLO ESGOTADO!", 'loss')

        bf = API.get_balance() if API else bi
        add_log("=" * 50, 'info')
        add_log(f"{'🌟 LUCRO' if bf > bi else '💀 PERDA'}: ${abs(bf - bi):.2f} | Saldo: ${bf:.2f}", 'info')
        add_log("=" * 50, 'info')
    except Exception as e:
        add_log(f"Erro: {e}", 'error')
        import traceback
        traceback.print_exc()
    finally:
        bot_rodando = False
        add_log("⏹️ Ciclo finalizado!", 'info')

def bot_loop():
    global bot_rodando, BANCA_INICIAL_DO_BOT, lucro, NumDeOperacoes, STOP_GAIN_ATINGIDO, sinal_pendente, ultimo_sinal, timeframe_atual, volt_ja_consumido, estrategia_ja_injetada

    with bot_lock:
        if not bot_rodando:
            return

        if not API:
            add_log('❌ API desconectada!', 'error')
            bot_rodando = False
            return

        # Carrega informações das estratégias
        estrategias_info = carregar_informacoes_estrategias()

        if not estrategias_info:
            add_log("❌ NENHUMA ESTRATÉGIA DISPONÍVEL!", 'error')
            bot_rodando = False
            return

        if estrategia_atual_global not in estrategias_info:
            add_log(f"❌ Estratégia '{estrategia_atual_global}' não encontrada!", 'error')
            bot_rodando = False
            return

        estrategia_info = estrategias_info[estrategia_atual_global]
        timeframe_estrategia = estrategia_info.get('timeframe', 60)
        add_log(f"📊 Estratégia: {estrategia_info.get('nome')}", 'indicator')
        add_log(f"⏱️ Timeframe: {timeframe_estrategia}s", 'info')

        # ⭐ SE A ESTRATÉGIA NÃO ESTIVER INJETADA, BAIXA E INJETA
        if not estrategia_ja_injetada or cache_estrategia_carregada["nome"] != estrategia_atual_global:
            add_log(f"🔧 Carregando e injetando estratégia '{estrategia_atual_global}'...", "info")
            if not carregar_e_injetar_estrategia(estrategia_atual_global):
                add_log(f"❌ Falha ao carregar estratégia '{estrategia_atual_global}'", 'error')
                bot_rodando = False
                return
            add_log(f"✅ Estratégia '{estrategia_atual_global}' injetada com sucesso!", 'win')

        BANCA_INICIAL_DO_BOT = API.get_balance()
        STOP_GAIN_ATINGIDO = False
        lucro = 0.0
        NumDeOperacoes = 0
        volt_ja_consumido = False
        ultimo_sinal = "Aguardando..."
        add_log(f"📌 {par} | 💰 ${BANCA_INICIAL_DO_BOT:.2f}")

        # ⭐ THREAD QUE EXECUTA A ESTRATÉGIA INJETADA (roda uma vez e para)
        def processar_estrategia():
            global timeframe_atual, sinal_pendente
            try:
                add_log(f"🔍 Executando análise da estratégia...", "info")
                resultado = estrategia_atual_executar(API, par, add_log)
                if resultado and bot_rodando:
                    direcao = resultado.get('direcao', '').lower()
                    novo_tf = resultado.get('timeframe', timeframe_estrategia)
                    if novo_tf != timeframe_atual:
                        add_log(f"⏱️ Timeframe alterado para {novo_tf}s", 'indicator')
                        timeframe_atual = novo_tf
                    if direcao in ['call', 'put']:
                        with sinal_lock:
                            sinal_pendente = direcao
                        add_log(f"🎯 SINAL: {direcao.upper()}!", 'sensitive')
            except Exception as e:
                add_log(f"❌ Erro na execução: {e}", "error")
                import traceback
                traceback.print_exc()

        threading.Thread(target=processar_estrategia, daemon=True).start()

        # ⭐ Loop principal - espera o sinal (sem timeout)
        while bot_rodando and not STOP_GAIN_ATINGIDO:
            if not bot_rodando:
                break
            try:
                with sinal_lock:
                    direcao = sinal_pendente
                    if direcao:
                        sinal_pendente = None
                if direcao in ['call', 'put']:
                    ultimo_sinal = f"GATILHO: {direcao.upper()}"
                    add_log(f"🎯 EXECUTANDO: {direcao.upper()}", 'sensitive')
                    executar_ciclo(direcao)
                    break
                time.sleep(0.5)
            except:
                time.sleep(2)

        bot_rodando = False

def analise_mercado_loop():
    global ultima_analise
    while True:
        if conectado_iq and API:
            try:
                velas = API.get_candles(par, 60, 30, time.time())
                if velas and len(velas) >= 20:
                    rsi_val = calcular_rsi(velas, 14)
                    estoc_val = calcular_estocastico(velas, 14)
                    mm5 = calcular_media_movel(velas, 5)
                    mm10 = calcular_media_movel(velas, 10)
                    mm20 = calcular_media_movel(velas, 20)
                    preco_atual = get_close(velas[-1])
                    
                    if mm5 and mm10 and mm20:
                        if mm5 > mm10 and mm10 > mm20:
                            fase = "TENDÊNCIA ALTA"
                        elif mm5 < mm10 and mm10 < mm20:
                            fase = "TENDÊNCIA BAIXA"
                        elif rsi_val < 40:
                            fase = "ACUMULAÇÃO"
                        elif rsi_val > 60:
                            fase = "EXAUSTÃO"
                        else:
                            fase = "CONSOLIDAÇÃO"
                    else:
                        fase = "ANALISANDO..."
                    
                    ultima_analise = {
                        'rsi': round(rsi_val, 1),
                        'mm5': round(mm5, 5) if mm5 else 0,
                        'mm10': round(mm10, 5) if mm10 else 0,
                        'mm20': round(mm20, 5) if mm20 else 0,
                        'stoch': round(estoc_val, 1),
                        'fase': fase,
                        'preco': round(preco_atual, 5) if preco_atual else 0
                    }
                else:
                    ultima_analise = {
                        'rsi': 50, 'mm5': 1.08300, 'mm10': 1.08300, 'mm20': 1.08300,
                        'stoch': 50, 'fase': "AGUARDANDO DADOS", 'preco': 1.08300
                    }
            except Exception as e:
                pass
        time.sleep(2)

threading.Thread(target=analise_mercado_loop, daemon=True).start()

def sincronizar_html_local():
    try:
        os.makedirs("templates", exist_ok=True)
        response = requests.get(HTML_URL, timeout=10)
        if response.status_code == 200:
            with open("templates/index.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("✅ HTML sincronizado!")
            return True
    except Exception as e:
        print(f"❌ Erro HTML: {e}")
    return False

# ========== ROTAS FLASK ==========

@app.route('/')
def index():
    skins = carregar_skins_da_nuvem()
    skin = next((s for s in skins if s['id'] == skin_atual_global), skins[0] if skins else get_skins_fallback()[0])
    planos_json = ','.join([f'{{"id":{p["id"]},"moedas":{p["moedas"]},"preco":{p["preco"]},"nome":"{p["nome"]}","desc":"{p["desc"]}","tag":"{p.get("tag","")}","desconto":"{p.get("desconto","")}"}}' for p in PLANOS])
    return render_template('index.html',
        COR_FUNDO=skin.get('cor_fundo', '#0a0a1a'),
        COR_PANEL=skin.get('cor_panel', '#1a1a3e'),
        COR_DESTAQUE=skin.get('cor_destaque', '#ffd700'),
        COR_TEXTO=skin.get('cor_texto', '#fff'),
        COR_BOTAO=skin.get('cor_botao', 'linear-gradient(135deg,#cc8800,#ffd700)'),
        COR_TAB_ATIVA=skin.get('cor_tab_ativa', '#ffd700'),
        COR_HEADER_BG=skin.get('cor_header_bg', 'linear-gradient(135deg,#1a0000,#331100,#553300,#331100,#1a0000)'),
        COR_HEADER_BORDA=skin.get('cor_header_borda', '#ffd700'),
        CSS_EXTRA=skin.get('css_extra', ''),
        HEADER_EXTRA=skin.get('header_extra', '<div class="lightning"></div>'),
        PLANOS_JSON=planos_json
    )

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
    add_log(f"📡 Sinal externo: {direcao.upper()}", 'sensitive')
    return jsonify({'ok': True})

@app.route('/status')
def status():
    u = carregar_usuario(email_usuario_atual) if email_usuario_atual else {}
    skins = carregar_skins_da_nuvem()
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

    estrategia_nome = "Nenhuma"
    if estrategia_atual in estrategias_info:
        estrategia_nome = estrategias_info[estrategia_atual].get('nome', estrategia_atual)

    return jsonify({
        'conectado': conectado_iq, 'rodando': bot_rodando, 'email': email_usuario_atual,
        'banca': API.get_balance() if API else 0, 'lucro': lucro, 'ops': NumDeOperacoes,
        'sinal': ultimo_sinal, 'logs': get_logs_html(40),
        'moedas': u.get('moedas', 0) if u else 0, 'skin_id': skin_atual,
        'skins_status': skins_status, 'estrategia': estrategia_atual,
        'estrategia_nome': estrategia_nome,
        'estrategias_compradas': estrategias_compradas,
        'estrategias_disponiveis': {k: {'nome': v['nome'], 'desc': v['desc'], 'preco_moedas': v['preco_moedas'], 'gratis': v['gratis']} for k, v in estrategias_info.items()},
        'analise': ultima_analise
    })

@app.route('/set_percentual', methods=['POST'])
def set_percentual():
    global PERCENTUAL_BANCA
    PERCENTUAL_BANCA = request.json.get('percentual', 15)
    return jsonify({'ok': True})

@app.route('/selecionar_estrategia', methods=['POST'])
def selecionar_estrategia():
    global estrategia_atual_global, estrategia_ja_injetada
    est_id = request.json.get('estrategia', 'v_sensitivo')
    if not email_usuario_atual:
        return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    u = carregar_usuario(email_usuario_atual)
    if not u:
        return jsonify({'ok': False, 'erro': 'Usuário não encontrado'})
    estrategias_info = carregar_informacoes_estrategias()
    if est_id not in estrategias_info:
        return jsonify({'ok': False, 'erro': 'Estratégia inválida'})
    estrategias_compradas = u.get('estrategias_compradas', ['v_sensitivo'])
    if est_id not in estrategias_compradas:
        info = estrategias_info[est_id]
        if not info.get('gratis', False):
            return jsonify({'ok': False, 'erro': f'Estratégia bloqueada! Compre na loja.'})
        u['estrategias_compradas'].append(est_id)
    u['estrategia_atual'] = est_id
    salvar_usuario(email_usuario_atual, u)
    estrategia_atual_global = est_id
    estrategia_ja_injetada = False
    add_log(f"🧠 Estratégia: {estrategias_info[est_id]['nome']}", 'indicator')
    return jsonify({'ok': True})

@app.route('/comprar_estrategia', methods=['POST'])
def comprar_estrategia():
    est_id = request.json.get('estrategia_id', '')
    if not email_usuario_atual:
        return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    estrategias_info = carregar_informacoes_estrategias()
    if est_id not in estrategias_info:
        return jsonify({'ok': False, 'erro': 'Estratégia inválida'})
    u = carregar_usuario(email_usuario_atual)
    if not u:
        return jsonify({'ok': False, 'erro': 'Usuário inválido'})
    if 'estrategias_compradas' not in u:
        u['estrategias_compradas'] = ['v_sensitivo']
    if est_id in u['estrategias_compradas']:
        u['estrategia_atual'] = est_id
        salvar_usuario(email_usuario_atual, u)
        return jsonify({'ok': True, 'moedas': u['moedas'], 'msg': 'Já adquirida!'})
    info = estrategias_info[est_id]
    preco = info.get('preco_moedas', 0)
    if u.get('moedas', 0) < preco:
        return jsonify({'ok': False, 'erro': f'Precisa de {preco} ⚡'})
    u['moedas'] -= preco
    u['estrategias_compradas'].append(est_id)
    u['estrategia_atual'] = est_id
    salvar_usuario(email_usuario_atual, u)
    global estrategia_atual_global
    estrategia_atual_global = est_id
    add_log(f"🛒 Estratégia: {info['nome']}", 'win')
    return jsonify({'ok': True, 'moedas': u['moedas'], 'msg': 'Sucesso!'})

@app.route('/conectar', methods=['POST'])
def conectar():
    global API, email_usuario_atual, conectado_iq, skin_atual_global, estrategia_atual_global
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
        add_log('🔌 Conectado!', 'info')
        add_log(f'✅ ${API.get_balance():.2f} | ⚡ {usuario.get("moedas", 0)} VOLTS', 'win')
        return jsonify({'ok': True, 'moedas': usuario.get('moedas', 0), 'refresh': True})
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)[:100]})

@app.route('/comecar_operar', methods=['POST'])
def comecar_operar():
    global bot_rodando, bot_thread, estrategia_ja_injetada
    try:
        if not conectado_iq:
            return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})

        estrategias_info = carregar_informacoes_estrategias()
        if not estrategias_info:
            return jsonify({'ok': False, 'erro': '❌ NENHUMA ESTRATÉGIA! Adicione estratégias no GitHub.'})

        if estrategia_atual_global not in estrategias_info:
            return jsonify({'ok': False, 'erro': f'❌ Estratégia "{estrategia_atual_global}" não encontrada!'})

        usuario = carregar_usuario(email_usuario_atual)
        if not usuario:
            return jsonify({'ok': False, 'erro': 'Usuário não encontrado!'})
        if usuario.get('moedas', 0) < 1:
            return jsonify({'ok': False, 'erro': 'Sem VOLTS! Compre na loja.'})

        with bot_lock:
            if bot_rodando and bot_thread and bot_thread.is_alive():
                return jsonify({'ok': False, 'erro': 'Bot já rodando!'})
            
            estrategia_ja_injetada = False
            
            bot_rodando = True
            bot_thread = threading.Thread(target=bot_loop, daemon=True)
            bot_thread.start()
        return jsonify({'ok': True, 'moedas': usuario['moedas']})
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)[:100]})

@app.route('/parar', methods=['POST'])
def parar():
    global bot_rodando, conectado_iq, volt_ja_consumido
    data = request.json or {}

    add_log("🛑 Parando o bot...", 'info')

    with bot_lock:
        bot_rodando = False

    time.sleep(1)

    volt_ja_consumido = False

    if data.get('desconectar'):
        conectado_iq = False
        add_log("🔌 Desconectado da IQ Option", 'info')
    else:
        add_log("✅ Bot parado! Clique em COMEÇAR OPERAR para iniciar novamente.", 'win')

    return jsonify({'ok': True, 'shutdown': data.get('desconectar', False)})

@app.route('/comprar_skin', methods=['POST'])
def comprar_skin():
    global skin_atual_global
    d = request.get_json()
    skin_id = d.get('skin_id', '')
    if not email_usuario_atual:
        return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    skins = carregar_skins_da_nuvem()
    skin = next((s for s in skins if s['id'] == skin_id), None)
    if not skin:
        return jsonify({'ok': False, 'erro': 'Skin não encontrada'})
    usuario = carregar_usuario(email_usuario_atual)
    if not usuario:
        return jsonify({'ok': False, 'erro': 'Usuário inválido'})
    if skin['preco_moedas'] == 0:
        if 'skins_compradas' not in usuario:
            usuario['skins_compradas'] = ['skin_padrao']
        if skin_id not in usuario['skins_compradas']:
            usuario['skins_compradas'].append(skin_id)
        usuario['skin_atual'] = skin_id
        salvar_usuario(email_usuario_atual, usuario)
        skin_atual_global = skin_id
        return jsonify({'ok': True, 'moedas': usuario.get('moedas', 0), 'msg': 'Skin grátis ativada!', 'refresh': True})
    if 'skins_compradas' not in usuario:
        usuario['skins_compradas'] = ['skin_padrao']
    if skin_id in usuario['skins_compradas']:
        usuario['skin_atual'] = skin_id
        salvar_usuario(email_usuario_atual, usuario)
        skin_atual_global = skin_id
        return jsonify({'ok': True, 'moedas': usuario['moedas'], 'msg': 'Ativada!', 'refresh': True})
    if usuario.get('moedas', 0) < skin['preco_moedas']:
        return jsonify({'ok': False, 'erro': f'Precisa de {skin["preco_moedas"]} ⚡'})
    usuario['moedas'] -= skin['preco_moedas']
    usuario['skins_compradas'].append(skin_id)
    usuario['skin_atual'] = skin_id
    salvar_usuario(email_usuario_atual, usuario)
    skin_atual_global = skin_id
    return jsonify({'ok': True, 'moedas': usuario['moedas'], 'msg': 'Skin adquirida!', 'refresh': True})

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
        skins = carregar_skins_da_nuvem()
        skin = next((s for s in skins if s['id'] == skin_id), None)
        if skin and skin['preco_moedas'] > 0:
            return jsonify({'ok': False, 'erro': 'Compre primeiro!'})
        usuario['skins_compradas'].append(skin_id)
    usuario['skin_atual'] = skin_id
    salvar_usuario(email_usuario_atual, usuario)
    global skin_atual_global
    skin_atual_global = skin_id
    return jsonify({'ok': True, 'refresh': True})

# ========== PIX ==========

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
            "transaction_amount": float(plano['preco']), "description": f"TESLA369 - {plano['moedas']} VOLTS",
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
        return {'sucesso': False, 'erro': 'Gateway rejeitado'}
    except Exception as e:
        return {'sucesso': False, 'erro': str(e)[:50]}

def verificar_pagamento_mp(pix_id):
    if MODO_SIMULACAO:
        return pagamentos_pendentes.get(pix_id, {}).get('pago', False)
    try:
        url = f"https://api.mercadopago.com/v1/payments/{pix_id}"
        headers = {"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}"}
        return requests.get(url, headers=headers, timeout=10).json().get('status') == 'approved'
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
                    add_log(f"💰 PIX Confirmado! +{dados['moedas']} VOLTS", "win")
        except:
            pass

threading.Thread(target=verificador_automatico_pix, daemon=True).start()

@app.route('/criar_pix', methods=['POST'])
def criar_pix():
    d = request.get_json()
    plano = next((p for p in PLANOS if p['id'] == int(d.get('plano_id') or 1)), None)
    return jsonify(gerar_pix_mercadopago(d.get('email', ''), plano))

@app.route('/verificar_pix', methods=['POST'])
def verificar_pix():
    d = request.get_json()
    pix_id = d.get('pix_id', '')
    if verificar_pagamento_mp(pix_id):
        if pix_id in pagamentos_pendentes and not pagamentos_pendentes[pix_id]['pago']:
            pagamentos_pendentes[pix_id]['pago'] = True
            u = carregar_usuario(pagamentos_pendentes[pix_id]['email'])
            if u:
                u['moedas'] += pagamentos_pendentes[pix_id]['moedas']
                salvar_usuario(pagamentos_pendentes[pix_id]['email'], u)
            return jsonify({'pago': True, 'moedas': pagamentos_pendentes[pix_id]['moedas'], 'saldo': u.get('moedas', 0) if u else 0})
        return jsonify({'pago': True})
    return jsonify({'pago': False})

@app.route('/chat_enviar', methods=['POST'])
def chat_enviar():
    data = request.json
    try:
        requests.post(f'{FB_URL}/tesla_369/chat.json', json={
            'nome': data.get('nome', 'Anonimo')[:15], 'msg': data.get('msg', '')[:200],
            'hora': datetime.now().strftime('%H:%M')
        }, timeout=5)
    except:
        pass
    return jsonify({'ok': True})

@app.route('/chat_mensagens')
def chat_mensagens_route():
    try:
        r = requests.get(f'{FB_URL}/tesla_369/chat.json?orderBy="$key"&limitToLast=50', timeout=5)
        return jsonify({'messages': list(r.json().values()) if r.status_code == 200 and r.json() else [], 'online': 1})
    except:
        return jsonify({'messages': [], 'online': 1})

@app.route('/ranking')
def ranking():
    ranking_list = []
    try:
        usuarios = requests.get(f'{FB_URL}/tesla_369/usuarios.json').json() or {}
        for k, ud in usuarios.items():
            if ud:
                ranking_list.append({
                    'email': ud.get('email', 'N/A'),
                    'lucro_total': round(ud.get('lucro_total', 0), 2),
                    'total_wins': ud.get('total_wins', 0),
                    'total_losses': ud.get('total_losses', 0),
                    'total_ciclos': ud.get('total_ciclos', 0),
                    'taxa': round((ud.get('total_wins', 0) / max(ud.get('total_ciclos', 1), 1)) * 100, 1),
                    'banca_atual': round(ud.get('banca_atual', 0), 2)
                })
    except:
        pass
    ranking_list.sort(key=lambda x: x['lucro_total'], reverse=True)
    tc = sum(x['total_ciclos'] for x in ranking_list)
    tw = sum(x['total_wins'] for x in ranking_list)
    return jsonify({'ranking': ranking_list, 'stats': {'total_usuarios': len(ranking_list), 'total_ops': tc, 'total_wins': tw, 'taxa_global': round((tw/max(tc,1))*100,1)}})

@app.route('/relatorio')
def relatorio():
    return jsonify(carregar_usuario(request.args.get('email', '')) or {'erro': 'Nao encontrado'})

@app.route('/resetar', methods=['POST'])
def resetar():
    u = carregar_usuario(request.json.get('email', ''))
    if not u:
        return jsonify({'ok': False, 'msg': 'Nao encontrado'})
    u.update({'total_ciclos':0,'total_wins':0,'total_losses':0,'total_gasto':0.0,'total_ganho':0.0,'lucro_total':0.0,'historico_operacoes':[],'dias_ativos':0,'banca_atual':0.0,'moedas_ganhas_hoje':str(datetime.now())[:10]})
    salvar_usuario(request.json.get('email', ''), u)
    return jsonify({'ok': True, 'msg': 'Resetado!'})

@app.route('/shutdown')
def shutdown():
    os.kill(os.getpid(), signal.SIGTERM)
    return jsonify({'ok': True})

if __name__ == '__main__':
    print("=" * 50)
    print("⚡ TESLA 369 BOT v9.0.1 - PIPELINE CLOUD ESTÁVEL ⚡")
    print("SKINS CARREGADAS DO GITHUB")
    print("ESTRATÉGIAS BAIXADAS E INJETADAS UMA ÚNICA VEZ")
    print("COM TIMESTAMP E SINCRONISMO CORRETO")
    print("=" * 50)

    print("🔍 Testando carregamento de skins...")
    skins_test = carregar_skins_da_nuvem()
    print(f"📦 {len(skins_test)} skins disponíveis")

    print("🔍 Testando carregamento de estratégias...")
    estrategias_test = carregar_informacoes_estrategias()
    print(f"📊 {len(estrategias_test)} estratégias disponíveis")

    sincronizar_html_local()

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
