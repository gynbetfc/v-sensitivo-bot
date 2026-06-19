#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ⚡ TESLA 369 BOT v17.0.0 - COMPLETO E FUNCIONAL ⚡
# Firebase: SKINS e ESTRATEGIAS carregadas da nuvem
# RECONEXÃO AUTOMÁTICA + TIME DINÂMICO + GALES
# 🔧 v17.0.0 - TUDO FUNCIONANDO

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

# ============= VERSÃO =============
BOT_VERSION = "17.0.0"
BOT_NAME = "TESLA-369"

# ============= CONFIGURACOES =============
FB_URL = "https://nexos-40654-default-rtdb.firebaseio.com"
print("✅ Firebase HTTP REST configurado!")

MARTINGALE = 2
PAYOUT_PADRAO = 0.85
PERCENTUAL_BANCA = 15

MERCADO_PAGO_ACCESS_TOKEN = os.environ.get("MP_ACCESS_TOKEN", "APP_USR-4548266140377032-050311-6589fc22b166e4cb2cfad0379b28dcdf-1059299796")
MODO_SIMULACAO = False

PLANOS = [
    {'id':1,'moedas':1,'preco':0.99,'nome':'🔰 TESTE','desc':'R$0,99/VOLT','tag':'1 ciclo','bonus':''},
    {'id':2,'moedas':6,'preco':6.69,'nome':'⭐ BASICO','desc':'R$1,11/VOLT','tag':'6 ciclos','bonus':''},
    {'id':3,'moedas':15,'preco':9.99,'nome':'💎 INTERMEDIARIO','desc':'R$0,67/VOLT','tag':'15 ciclos','bonus':'🎨 1 Skin Basica GRATIS','desconto':'33% OFF'},
    {'id':4,'moedas':36,'preco':21.69,'nome':'🔥 PREMIUM','desc':'R$0,60/VOLT','tag':'36 ciclos','bonus':'🎨 1 Skin Premium GRATIS','desconto':'40% OFF'},
    {'id':5,'moedas':69,'preco':39.69,'nome':'👑 ULTRA','desc':'R$0,57/VOLT','tag':'69 ciclos','bonus':'🎨 1 Skin Lendaria GRATIS','desconto':'69% OFF'},
]

# ============= CACHES =============
cache_skins = {"data": None, "timestamp": 0}
cache_estrategias_info = {"data": {}, "timestamp": 0}
cache_estrategia_carregada = {"nome": None, "codigo": None, "timestamp": 0}
CACHE_TTL = 300

# ============= FUNCAO VAZIA =============
def estrategia_atual_executar(api, par, add_log):
    add_log("⚠️ Nenhuma estrategia carregada!", "error")
    return None

# ============= VARIAVEIS GLOBAIS =============
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
ordem_id_atual = None
ultimo_keep_alive = time.time()
reconectando = False

# ============= GERENCIADOR DE RECONEXÃO =============
class ConnectionManager:
    def __init__(self):
        self.api = None
        self.email = None
        self.senha = None
        self.tipo_conta = "PRACTICE"
        self.conectado = False
        self.tentativas = 0
        self.max_tentativas = 5
        self.credenciais_validas = False
        self.lock = threading.Lock()
        self.ultimo_ping = time.time()
    
    def configurar(self, email, senha, tipo="PRACTICE"):
        self.email = email
        self.senha = senha
        self.tipo_conta = tipo
        self.credenciais_validas = bool(email and senha)
        self.tentativas = 0
        add_log(f"📝 Credenciais configuradas para {tipo}", "info")
    
    def conectar(self):
        if not self.credenciais_validas:
            return False
        
        with self.lock:
            if self.conectado and self.api:
                try:
                    self.api.get_server_timestamp()
                    return True
                except:
                    pass
            
            if self.tentativas >= self.max_tentativas:
                if time.time() - self.ultimo_ping > 60:
                    self.tentativas = 0
                else:
                    return False
            
            try:
                if self.api:
                    try:
                        self.api.desconectar()
                    except:
                        pass
                    self.api = None
                    time.sleep(0.5)
                
                add_log(f"🔄 Conectando em {self.tipo_conta}...", "info")
                self.api = IQ_Option(self.email, self.senha)
                status, msg = self.api.connect()
                
                if status:
                    self.api.change_balance(self.tipo_conta)
                    self.conectado = True
                    self.tentativas = 0
                    self.ultimo_ping = time.time()
                    add_log(f"✅ Conectado! Saldo: ${self.api.get_balance():.2f}", "win")
                    return True
                else:
                    self.conectado = False
                    self.tentativas += 1
                    add_log(f"⚠️ Falha {self.tentativas}/{self.max_tentativas}", "error")
                    time.sleep(2)
                    return False
                    
            except Exception as e:
                self.conectado = False
                self.tentativas += 1
                add_log(f"❌ Erro: {str(e)[:50]}", "error")
                return False
    
    def verificar(self):
        if not self.credenciais_validas:
            return False
        if not self.conectado or not self.api:
            return self.conectar()
        
        try:
            ping = self.api.get_server_timestamp()
            if ping:
                self.ultimo_ping = time.time()
                return True
            else:
                return self.conectar()
        except:
            return self.conectar()
    
    def get_api(self):
        if self.verificar():
            return self.api
        return None
    
    def get_saldo(self):
        api = self.get_api()
        if api:
            try:
                return api.get_balance()
            except:
                pass
        return None
    
    def get_tipo(self):
        return self.tipo_conta

conn_manager = ConnectionManager()

# ============= FUNCOES AUXILIARES =============

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

# ============= SKINS =============

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

# ============= ESTRATEGIAS =============

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

def carregar_e_injetar_estrategia(nome_estrategia):
    global estrategia_atual_executar, cache_estrategia_carregada, estrategia_ja_injetada
    agora = time.time()
    if cache_estrategia_carregada["nome"] == nome_estrategia and (agora - cache_estrategia_carregada["timestamp"]) < CACHE_TTL:
        return True

    estrategia_data = carregar_estrategia_do_firebase(nome_estrategia)
    if not estrategia_data: return False

    codigo = estrategia_data.get('codigo')
    if not codigo or 'def rodar_analise' not in codigo: return False

    try:
        escopo = {}
        exec(codigo, escopo)
        if 'rodar_analise' in escopo:
            estrategia_atual_executar = escopo['rodar_analise']
            cache_estrategia_carregada.update({"nome": nome_estrategia, "codigo": codigo, "timestamp": agora})
            estrategia_ja_injetada = True
            add_log(f"✅ Estrategia '{nome_estrategia}' injetada do Firebase!", "win")
            return True
        else: return False
    except Exception as e:
        add_log(f"❌ Erro ao executar estrategia: {e}", "error")
        return False

# ========== FUNCOES DE USUARIO ==========

def salvar_usuario(email, dados):
    try:
        key = email.replace("@", "_").replace(".", "_").replace("#", "").replace("$", "").replace("[", "").replace("]", "").replace("/", "_")
        requests.put(f'{FB_URL}/tesla_369/usuarios/{key}.json', json=dados, timeout=5)
    except: pass

def carregar_usuario(email):
    try:
        key = email.replace("@", "_").replace(".", "_").replace("#", "").replace("$", "").replace("[", "").replace("]", "").replace("/", "_")
        r = requests.get(f'{FB_URL}/tesla_369/usuarios/{key}.json', timeout=5)
        if r.status_code == 200 and r.json(): return r.json()
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

def salvar_tipo_conta(email, tipo):
    try:
        key = email.replace("@", "_").replace(".", "_")
        requests.patch(f'{FB_URL}/tesla_369/usuarios/{key}.json', 
                      json={'tipo_conta': tipo}, timeout=5)
    except:
        pass

# ========== FUNCOES DO BOT ==========

def Payout(p):
    try:
        api = conn_manager.get_api()
        if not api: return PAYOUT_PADRAO
        api.subscribe_strike_list(p, 1)
        for _ in range(20):
            d = api.get_digital_current_profit(p, 1)
            if d != False:
                api.unsubscribe_strike_list(p, 1)
                return round(int(d) / 100, 2)
            time.sleep(0.5)
        api.unsubscribe_strike_list(p, 1)
        return PAYOUT_PADRAO
    except: return PAYOUT_PADRAO

def calcular_entradas(b, p, g):
    global PERCENTUAL_BANCA
    bs = (b * PERCENTUAL_BANCA / 100) * 0.99
    e0 = bs / sum((1/p)**i for i in range(g+1))
    entradas = [e0]
    for i in range(1, g+1):
        entradas.append((sum(entradas) + e0) / p)
    ajuste = bs / sum(entradas)
    entradas = [round(e * ajuste, 2) for e in entradas]
    if sum(entradas) > b:
        entradas[-1] = round(entradas[-1] - (sum(entradas) - b) - 0.02, 2)
    return [max(1, e) for e in entradas]

def aguardar_inicio_vela(timeframe=60):
    add_log(f"   ⏳ Aguardando inicio da vela ({timeframe}s)...", 'info')
    
    agora = datetime.now()
    if timeframe >= 60:
        minutos_por_vela = timeframe // 60
        minutos_passados = agora.minute % minutos_por_vela
        segundos_restantes = (minutos_por_vela - minutos_passados) * 60 - agora.second
        if segundos_restantes < 0:
            segundos_restantes += minutos_por_vela * 60
    else:
        segundos_restantes = timeframe - (agora.second % timeframe)
        if segundos_restantes == timeframe:
            segundos_restantes = 0
    
    if segundos_restantes > 0:
        time.sleep(segundos_restantes + 0.5)
    
    add_log("   ✅ Vela confirmada!", 'info')
    return True

def consumir_volt():
    global volt_ja_consumido
    if volt_ja_consumido: return True
    usuario = carregar_usuario(email_usuario_atual)
    if not usuario or usuario.get('moedas', 0) < 1: return False
    usuario['moedas'] -= 1
    usuario['total_ciclos'] = usuario.get('total_ciclos', 0) + 1
    salvar_usuario(email_usuario_atual, usuario)
    volt_ja_consumido = True
    add_log(f"⚡ 1 VOLT consumido. Saldo: {usuario['moedas']} VOLTS", 'info')
    return True

def executar_ciclo(direcao, timeframe=60):
    global lucro, NumDeOperacoes, STOP_GAIN_ATINGIDO, bot_rodando, volt_ja_consumido, ordem_id_atual, timeframe_atual

    if not bot_rodando:
        add_log("⚠️ Bot não está rodando!", "error")
        return

    try:
        if not consumir_volt():
            add_log("❌ Sem VOLTS!", 'error')
            bot_rodando = False
            return

        api = conn_manager.get_api()
        if not api:
            add_log("❌ Sem conexão!", 'error')
            bot_rodando = False
            return

        bi = api.get_balance()
        if bi is None:
            add_log("❌ Falha ao obter saldo!", 'error')
            return

        payout = Payout(par)
        entradas = calcular_entradas(bi, payout, MARTINGALE)
        add_log(f"💰 Banca: ${bi:.2f} | Payout: {payout*100:.0f}%", 'info')
        add_log(f"📐 E1:${entradas[0]:.2f} | E2:${entradas[1]:.2f} | E3:${entradas[2]:.2f}", 'info')
        add_log(f"⏱️ Timeframe: {timeframe}s", 'info')

        for i in range(MARTINGALE + 1):
            if not bot_rodando:
                add_log("⏹️ Bot parado!", 'info')
                break

            valor = entradas[i]

            if i == 0:
                if not aguardar_inicio_vela(timeframe):
                    add_log("⚠️ Falha ao aguardar inicio da vela.", 'error')
                    break
            else:
                time.sleep(0.5)
                add_log(f"   🔄 Executando GALE {i}...", 'info')

            saldo_antes = api.get_balance()
            if saldo_antes is None or saldo_antes < valor:
                add_log("❌ Saldo insuficiente!", 'error')
                break

            add_log(f"🎯 {'ENTRADA' if i == 0 else f'GALE {i}'}: {direcao.upper()} ${valor:.2f} | Time: {timeframe}s", 'info')

            # 🔥 EXECUTA A ORDEM
            tempo_minutos = timeframe // 60 if timeframe >= 60 else 1
            st = False
            id_ordem = None

            try:
                add_log(f"   📤 Enviando ordem: {par} | {direcao} | ${valor} | {tempo_minutos}min", 'info')
                
                if timeframe >= 60:
                    st, id_ordem = api.buy_digital_spot(par, valor, direcao, tempo_minutos)
                else:
                    st, id_ordem = api.buy_digital_spot(par, valor, direcao, 1)
                
                if not st or not id_ordem:
                    add_log("   🔄 Tentando método alternativo...", 'info')
                    st, id_ordem = api.buy(valor, par, direcao, tempo_minutos)
                    
            except Exception as e:
                add_log(f"   ❌ Erro na compra: {e}", 'error')
                try:
                    st, id_ordem = api.buy(valor, par, direcao, 1)
                except:
                    pass

            if not st or not id_ordem:
                add_log("❌ Falha na ordem!", 'error')
                break

            if i == 0:
                ordem_id_atual = id_ordem
                add_log(f"   ✅ Ordem #{id_ordem} executada! (Entrada)", 'win')
            else:
                add_log(f"   ✅ Ordem #{id_ordem} executada! (GALE {i})", 'win')

            # 🔥 AGUARDA O TIMEFRAME
            add_log(f"   ⏳ Aguardando {timeframe} segundos...", 'info')
            for s in range(timeframe):
                if not bot_rodando:
                    return
                time.sleep(1)

            api = conn_manager.get_api()
            if not api:
                add_log("❌ Conexão perdida!", 'error')
                bot_rodando = False
                break

            saldo_depois = api.get_balance()
            if saldo_depois is None:
                add_log("❌ Falha ao obter saldo final!", 'error')
                break

            lucro_liquido = round(saldo_depois - saldo_antes, 2)
            lucro += lucro_liquido

            if lucro_liquido > 0:
                add_log(f"🌟 WIN! +${lucro_liquido:.2f}", 'win')
                NumDeOperacoes += 1
                STOP_GAIN_ATINGIDO = True
                add_log("🎯 STOP GAIN!", 'win')
                break
            else:
                add_log(f"💀 LOSS! {lucro_liquido:.2f}", 'loss')
                if i < MARTINGALE and bot_rodando:
                    add_log(f"   ➡️ Indo para GALE {i + 1}...", 'loss')
                else:
                    add_log("   💀 CICLO ESGOTADO!", 'loss')

        if bot_rodando:
            bf = conn_manager.get_saldo()
            if bf is not None:
                add_log("=" * 50, 'info')
                add_log(f"{'🌟 LUCRO' if bf > bi else '💀 PERDA'}: ${abs(bf - bi):.2f} | Banca: ${bf:.2f}", 'info')
                add_log("=" * 50, 'info')

    except Exception as e:
        add_log(f"❌ Erro: {e}", 'error')
        import traceback
        traceback.print_exc()
    finally:
        bot_rodando = False
        ordem_id_atual = None
        add_log("⏹️ Ciclo finalizado!", 'info')

def bot_loop():
    global bot_rodando, lucro, NumDeOperacoes, STOP_GAIN_ATINGIDO, ultimo_sinal, timeframe_atual, volt_ja_consumido, estrategia_ja_injetada

    with bot_lock:
        if not bot_rodando:
            return

        api = conn_manager.get_api()
        if not api:
            add_log("❌ Sem conexão!", 'error')
            bot_rodando = False
            return

        estrategias_info = carregar_informacoes_estrategias()
        if not estrategias_info or estrategia_atual_global not in estrategias_info:
            add_log(f"❌ Estrategia '{estrategia_atual_global}' nao encontrada!", 'error')
            bot_rodando = False
            return

        info = estrategias_info[estrategia_atual_global]
        timeframe_atual = info.get('timeframe', 60)
        add_log(f"📊 Estrategia: {info.get('nome')}", 'indicator')
        add_log(f"⏱️ Timeframe: {timeframe_atual}s", 'info')

        if not carregar_e_injetar_estrategia(estrategia_atual_global):
            add_log("❌ Falha ao carregar estratégia!", 'error')
            bot_rodando = False
            return

        STOP_GAIN_ATINGIDO = False
        lucro = 0.0
        NumDeOperacoes = 0
        volt_ja_consumido = False
        ultimo_sinal = "Aguardando..."
        add_log(f"📌 {par} | Timeframe: {timeframe_atual}s | 💰 ${api.get_balance():.2f}", 'info')

        while bot_rodando and not STOP_GAIN_ATINGIDO:
            api = conn_manager.get_api()
            if not api:
                add_log("⚠️ Aguardando reconexão...", "info")
                time.sleep(3)
                continue

            try:
                resultado = estrategia_atual_executar(api, par, add_log)
                
                if resultado and bot_rodando:
                    direcao = resultado.get('direcao', '').lower()
                    tf = resultado.get('timeframe', timeframe_atual)
                    
                    if direcao in ['call', 'put']:
                        ultimo_sinal = f"SINAL: {direcao.upper()} | {tf}s"
                        add_log(f"🎯 SINAL: {direcao.upper()} | Timeframe: {tf}s", 'sensitive')
                        executar_ciclo(direcao, tf)
                        break
                
                time.sleep(0.3)
                
            except Exception as e:
                add_log(f"Erro no loop: {e}", 'error')
                time.sleep(2)

        bot_rodando = False
        add_log("🛑 Bot finalizado!", 'info')

# ========== THREADS ==========

def keep_alive_thread():
    while True:
        time.sleep(20)
        api = conn_manager.get_api()
        if api:
            try:
                api.get_server_timestamp()
            except:
                pass

def monitor_thread():
    while True:
        time.sleep(10)
        if conn_manager.credenciais_validas:
            if not conn_manager.verificar():
                add_log("⚠️ Tentando reconectar...", "info")

def analise_thread():
    global ultima_analise
    while True:
        api = conn_manager.get_api()
        if api:
            try:
                velas = api.get_candles(par, 60, 30, time.time())
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

                    ultima_analise = {
                        'rsi': round(rsi_val, 1), 'mm5': round(mm5, 5) if mm5 else 0,
                        'mm10': round(mm10, 5) if mm10 else 0, 'mm20': round(mm20, 5) if mm20 else 0,
                        'stoch': round(estoc_val, 1), 'fase': fase, 'preco': round(preco_atual, 5) if preco_atual else 0
                    }
            except Exception as e:
                pass
        time.sleep(2)

threading.Thread(target=analise_thread, daemon=True).start()
threading.Thread(target=keep_alive_thread, daemon=True).start()
threading.Thread(target=monitor_thread, daemon=True).start()

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

# ========== ROTAS ==========

@app.route('/')
def index():
    skins = carregar_todas_skins_do_firebase()
    skin = next((s for s in skins if s.get('id') == skin_atual_global), skins[0] if skins else list(get_skins_fallback().values())[0])
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
    u = carregar_usuario(email_usuario_atual) if email_usuario_atual else {}
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

    saldo = conn_manager.get_saldo()

    return jsonify({
        'conectado': conn_manager.conectado, 
        'rodando': bot_rodando, 
        'email': email_usuario_atual,
        'banca': saldo if saldo is not None else 0, 
        'lucro': lucro, 
        'ops': NumDeOperacoes, 
        'sinal': ultimo_sinal,
        'logs': get_logs_html(40), 
        'moedas': u.get('moedas', 0) if u else 0, 
        'skin_id': skin_atual, 
        'skins_status': skins_status,
        'estrategia': estrategia_atual, 
        'estrategia_nome': estrategia_nome, 
        'estrategias_compradas': estrategias_compradas,
        'estrategias_disponiveis': {k: {'nome': v['nome'], 'desc': v['desc'], 'preco_moedas': v['preco_moedas'], 'gratis': v['gratis'], 'timeframe': v.get('timeframe', 60)} for k, v in estrategias_info.items()},
        'analise': ultima_analise, 
        'bot_version': BOT_VERSION,
        'tipo_conta': conn_manager.get_tipo(),
        'timeframe_atual': timeframe_atual
    })

@app.route('/conectar', methods=['POST'])
def conectar():
    global email_usuario_atual, skin_atual_global, estrategia_atual_global
    try:
        d = request.get_json()
        email, senha, tipo = d.get('email', '').strip(), d.get('senha', '').strip(), d.get('tipo', 'PRACTICE')
        
        if not email or not senha:
            return jsonify({'ok': False, 'erro': 'Credenciais em branco'})
        
        conn_manager.configurar(email, senha, tipo)
        
        if not conn_manager.conectar():
            return jsonify({'ok': False, 'erro': 'Falha na conexão com IQ Option'})
        
        email_usuario_atual = email
        usuario = carregar_usuario(email) or criar_usuario(email)
        
        salvar_tipo_conta(email, tipo)
        
        estrategia_atual_global = usuario.get('estrategia_atual', 'v_sensitivo')
        skin_atual_global = usuario.get('skin_atual', 'skin_padrao')
        
        saldo = conn_manager.get_saldo()
        
        add_log('🔌 Conectado!', 'info')
        add_log(f'✅ ${saldo:.2f} | ⚡ {usuario.get("moedas", 0)} VOLTS | Conta: {tipo}', 'win')
        
        return jsonify({
            'ok': True, 
            'moedas': usuario.get('moedas', 0),
            'tipo_conta': tipo,
            'saldo': saldo,
            'refresh': True
        })
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)[:100]})

@app.route('/selecionar_estrategia', methods=['POST'])
def selecionar_estrategia():
    global estrategia_atual_global, estrategia_ja_injetada
    est_id = request.json.get('estrategia', 'v_sensitivo')
    if not email_usuario_atual: return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    u = carregar_usuario(email_usuario_atual)
    if not u: return jsonify({'ok': False, 'erro': 'Usuario nao encontrado'})
    estrategias_info = carregar_informacoes_estrategias()
    if est_id not in estrategias_info: return jsonify({'ok': False, 'erro': 'Estrategia invalida'})

    estrategias_compradas = u.get('estrategias_compradas', ['v_sensitivo'])
    if est_id not in estrategias_compradas:
        if not estrategias_info[est_id].get('gratis', False): 
            return jsonify({'ok': False, 'erro': f'Estrategia bloqueada! Compre na loja.'})
        u['estrategias_compradas'].append(est_id)
    u['estrategia_atual'] = est_id
    salvar_usuario(email_usuario_atual, u)
    estrategia_atual_global = est_id
    estrategia_ja_injetada = False
    add_log(f"🧠 Estrategia: {estrategias_info[est_id]['nome']} | Timeframe: {estrategias_info[est_id].get('timeframe', 60)}s", 'indicator')
    return jsonify({'ok': True})

@app.route('/comecar_operar', methods=['POST'])
def comecar_operar():
    global bot_rodando, bot_thread, estrategia_ja_injetada
    try:
        if not conn_manager.conectado: 
            return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
        
        estrategias_info = carregar_informacoes_estrategias()
        if not estrategias_info or estrategia_atual_global not in estrategias_info:
            return jsonify({'ok': False, 'erro': f'❌ Estrategia "{estrategia_atual_global}" invalida!'})

        usuario = carregar_usuario(email_usuario_atual)
        if not usuario: return jsonify({'ok': False, 'erro': 'Usuario nao encontrado!'})
        if usuario.get('moedas', 0) < 1: return jsonify({'ok': False, 'erro': 'Sem VOLTS! Compre na loja.'})

        with bot_lock:
            if bot_rodando and bot_thread and bot_thread.is_alive(): 
                return jsonify({'ok': False, 'erro': 'Bot ja rodando!'})
            estrategia_ja_injetada = False
            bot_rodando = True
            bot_thread = threading.Thread(target=bot_loop, daemon=True)
            bot_thread.start()
            
        return jsonify({
            'ok': True, 
            'moedas': usuario['moedas'],
            'timeframe': timeframe_atual
        })
    except Exception as e: 
        return jsonify({'ok': False, 'erro': str(e)[:100]})

@app.route('/parar', methods=['POST'])
def parar():
    global bot_rodando, volt_ja_consumido
    data = request.json or {}
    add_log("🛑 Parando o bot...", 'info')
    bot_rodando = False
    volt_ja_consumido = False
    if data.get('desconectar'):
        conn_manager.conectado = False
        add_log("🔌 Desconectado e finalizando servidor...", 'info')
        def shutdown_server():
            time.sleep(1)
            os.kill(os.getpid(), signal.SIGTERM)
        threading.Thread(target=shutdown_server, daemon=True).start()
        return jsonify({'ok': True, 'shutdown': True})
    else:
        add_log("✅ Bot parado!", 'win')
        return jsonify({'ok': True, 'shutdown': False})

@app.route('/comprar_skin', methods=['POST'])
def comprar_skin():
    global skin_atual_global
    skin_id = request.get_json().get('skin_id', '')
    if not email_usuario_atual: return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    skin = carregar_skin_do_firebase(skin_id) or next((s for s in carregar_todas_skins_do_firebase() if s.get('id') == skin_id), None)
    if not skin: return jsonify({'ok': False, 'erro': 'Skin nao encontrada'})
    usuario = carregar_usuario(email_usuario_atual)
    if not usuario: return jsonify({'ok': False, 'erro': 'Usuario invalido'})

    if skin.get('preco_moedas', 0) == 0:
        if skin_id not in usuario.setdefault('skins_compradas', ['skin_padrao']): usuario['skins_compradas'].append(skin_id)
        usuario['skin_atual'] = skin_id
        salvar_usuario(email_usuario_atual, usuario)
        skin_atual_global = skin_id
        return jsonify({'ok': True, 'moedas': usuario.get('moedas', 0), 'msg': 'Skin gratis ativada!', 'refresh': True})

    if skin_id in usuario.setdefault('skins_compradas', ['skin_padrao']):
        usuario['skin_atual'] = skin_id
        salvar_usuario(email_usuario_atual, usuario)
        skin_atual_global = skin_id
        return jsonify({'ok': True, 'moedas': usuario['moedas'], 'msg': 'Ativada!', 'refresh': True})

    if usuario.get('moedas', 0) < skin.get('preco_moedas', 0): return jsonify({'ok': False, 'erro': f'Precisa de {skin["preco_moedas"]} ⚡'})
    usuario['moedas'] -= skin['preco_moedas']
    usuario['skins_compradas'].append(skin_id)
    usuario['skin_atual'] = skin_id
    salvar_usuario(email_usuario_atual, usuario)
    skin_atual_global = skin_id
    return jsonify({'ok': True, 'moedas': usuario['moedas'], 'msg': 'Skin adquirida!', 'refresh': True})

@app.route('/ativar_skin', methods=['POST'])
def ativar_skin():
    skin_id = request.get_json().get('skin_id', '')
    if not email_usuario_atual: return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    usuario = carregar_usuario(email_usuario_atual)
    if not usuario: return jsonify({'ok': False, 'erro': 'Usuario nao encontrado'})
    if skin_id not in usuario.setdefault('skins_compradas', ['skin_padrao']):
        skin = carregar_skin_do_firebase(skin_id)
        if skin and skin.get('preco_moedas', 0) > 0: return jsonify({'ok': False, 'erro': 'Compre primeiro!'})
        usuario['skins_compradas'].append(skin_id)
    usuario['skin_atual'] = skin_id
    salvar_usuario(email_usuario_atual, usuario)
    global skin_atual_global
    skin_atual_global = skin_id
    return jsonify({'ok': True, 'refresh': True})

# ========== PIX ==========

@app.route('/criar_pix', methods=['POST'])
def criar_pix():
    d = request.get_json()
    plano = next((p for p in PLANOS if p['id'] == int(d.get('plano_id') or 1)), None)
    if MODO_SIMULACAO:
        pix_id = str(uuid.uuid4())[:8]
        pagamentos_pendentes[pix_id] = {'email': d.get('email'), 'plano_id': plano['id'], 'moedas': plano['moedas'], 'valor': plano['preco'], 'pago': False, 'criado_em': str(datetime.now())[:19]}
        return jsonify({'sucesso': True, 'simulacao': True, 'pix_id': pix_id, 'qr_code': f"00020126360014BR.GOV.BCB.PIX0136{d.get('email')}5204000053039865404{plano['preco']:.2f}5802BR5909Tesla3696009Sao Paulo62070503***6304E3F9", 'qr_code_base64': '', 'valor': plano['preco'], 'moedas': plano['moedas']})
    try:
        url = "https://api.mercadopago.com/v1/payments"
        headers = {"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}", "Content-Type": "application/json", "X-Idempotency-Key": str(uuid.uuid4())}
        payment_data = {"transaction_amount": float(plano['preco']), "description": f"TESLA369 - {plano['moedas']} VOLTS", "payment_method_id": "pix", "payer": {"email": d.get('email'), "first_name": "Traders", "last_name": "Tesla", "identification": {"type": "CPF", "number": "00000000000"}}}
        res = requests.post(url, json=payment_data, headers=headers, timeout=30).json()
        if 'id' in res:
            pix_id = str(res['id'])
            pagamentos_pendentes[pix_id] = {'email': d.get('email'), 'plano_id': plano['id'], 'moedas': plano['moedas'], 'valor': plano['preco'], 'pago': False, 'criado_em': str(datetime.now())[:19]}
            return jsonify({'sucesso': True, 'simulacao': False, 'pix_id': pix_id, 'qr_code': res['point_of_interaction']['transaction_data']['qr_code'], 'qr_code_base64': res['point_of_interaction']['transaction_data']['qr_code_base64'], 'valor': plano['preco'], 'moedas': plano['moedas']})
        return jsonify({'sucesso': False, 'erro': res.get('message', 'Erro ao gerar PIX')})
    except Exception as e: return jsonify({'sucesso': False, 'erro': str(e)[:50]})

@app.route('/verificar_pix', methods=['POST'])
def verificar_pix():
    pix_id = request.get_json().get('pix_id', '')
    if MODO_SIMULACAO:
        pago = pagamentos_pendentes.get(pix_id, {}).get('pago', False)
        if pago and pix_id in pagamentos_pendentes and not pagamentos_pendentes[pix_id]['pago']:
            pagamentos_pendentes[pix_id]['pago'] = True
            u = carregar_usuario(pagamentos_pendentes[pix_id]['email'])
            if u: u['moedas'] += pagamentos_pendentes[pix_id]['moedas']; salvar_usuario(pagamentos_pendentes[pix_id]['email'], u)
            return jsonify({'pago': True, 'moedas': pagamentos_pendentes[pix_id]['moedas'], 'saldo': u.get('moedas', 0) if u else 0})
        return jsonify({'pago': pago})
    try:
        url = f"https://api.mercadopago.com/v1/payments/{pix_id}"
        headers = {"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}"}
        res = requests.get(url, headers=headers, timeout=10).json()
        if res.get('status') == 'approved':
            if pix_id in pagamentos_pendentes and not pagamentos_pendentes[pix_id]['pago']:
                pagamentos_pendentes[pix_id]['pago'] = True
                u = carregar_usuario(pagamentos_pendentes[pix_id]['email'])
                if u: u['moedas'] += pagamentos_pendentes[pix_id]['moedas']; salvar_usuario(pagamentos_pendentes[pix_id]['email'], u)
                return jsonify({'pago': True, 'moedas': pagamentos_pendentes[pix_id]['moedas'], 'saldo': u.get('moedas', 0) if u else 0})
            return jsonify({'pago': True})
        return jsonify({'pago': False})
    except: return jsonify({'pago': False})

def verificador_automatico_pix():
    while True:
        time.sleep(10)
        try:
            for pix_id, dados in list(pagamentos_pendentes.items()):
                if dados.get('pago', False): continue
                if MODO_SIMULACAO:
                    pago = dados.get('pago', False)
                else:
                    try:
                        res = requests.get(f"https://api.mercadopago.com/v1/payments/{pix_id}", headers={"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}"}, timeout=10).json()
                        pago = res.get('status') == 'approved'
                    except: continue
                if pago:
                    pagamentos_pendentes[pix_id]['pago'] = True
                    u = carregar_usuario(dados['email']) or criar_usuario(dados['email'])
                    u['moedas'] = u.get('moedas', 0) + dados['moedas']
                    salvar_usuario(dados['email'], u)
                    add_log(f"💰 PIX Confirmado! +{dados['moedas']} VOLTS para {dados['email']}", "win")
        except: pass

threading.Thread(target=verificador_automatico_pix, daemon=True).start()

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
        return jsonify({'messages': list(r.json().values()) if r.status_code == 200 and r.json() else [], 'online': 1})
    except: return jsonify({'messages': [], 'online': 1})

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
    except: pass
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
    if not u: return jsonify({'ok': False, 'msg': 'Nao encontrado'})
    u.update({'total_ciclos':0,'total_wins':0,'total_losses':0,'total_gasto':0.0,'total_ganho':0.0,'lucro_total':0.0,'historico_operacoes':[],'dias_ativos':0,'banca_atual':0.0,'moedas_ganhas_hoje':str(datetime.now())[:10]})
    salvar_usuario(request.json.get('email', ''), u)
    return jsonify({'ok': True, 'msg': 'Resetado!'})

@app.route('/shutdown')
def shutdown():
    os.kill(os.getpid(), signal.SIGTERM)
    return jsonify({'ok': True})

# ========== INÍCIO ==========

if __name__ == '__main__':
    print("=" * 70)
    print(f"⚡ {BOT_NAME} v{BOT_VERSION} - COMPLETO E FUNCIONAL ⚡")
    print("✅ Firebase: SKINS e ESTRATEGIAS carregadas da nuvem")
    print("✅ RECONEXÃO: Mantém o tipo de conta (PRACTICE/REAL)")
    print("✅ TIME DINÂMICO: Estratégias definem o timeframe")
    print("✅ ENTRADA: guarda ID da ordem (referencia)")
    print("✅ RESULTADO: espera minuto virar + mudança de saldo")
    print("✅ GALES: nova ordem, novo saldo, nova verificacao")
    print("=" * 70)

    print("\n🔍 Carregando skins do Firebase...")
    skins_test = carregar_todas_skins_do_firebase()
    print(f"📦 {len(skins_test)} skins disponiveis")

    print("\n🔍 Carregando estrategias do Firebase...")
    estrategias_test = carregar_informacoes_estrategias()
    print(f"📊 {len(estrategias_test)} estrategias disponiveis")
    for nome, info in estrategias_test.items():
        print(f"   📈 {nome}: {info.get('timeframe', 60)}s")

    sincronizar_html_local()

    port = int(os.environ.get('PORT', 5000))
    print(f"\n🚀 Servidor rodando em http://localhost:{port}")
    print("💡 Conecte-se com suas credenciais da IQ Option para começar!")

    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
