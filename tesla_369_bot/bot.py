#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ⚡ TESLA 369 BOT v13.0.4 - MOTOR REESCRITO HARDCODED ⚡
# Ciclo de Gales autônomo e isolado (Módulo tes.py). As estratégias apenas enviam o gatilho inicial.

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

warnings.filterwarnings("ignore")
app = Flask(__name__)

# ============= CONFIGURAÇÕES =============
FB_URL = "https://nexos-40654-default-rtdb.firebaseio.com"
print("✅ Firebase HTTP REST configurado!")

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
cache_estrategias_info = {"data": {}, "timestamp": 0}
cache_estrategia_carregada = {"nome": None, "codigo": None, "timestamp": 0}
CACHE_TTL = 300

def estrategia_atual_executar(api, par, add_log):
    add_log("⚠️ Nenhuma estratégia carregada!", "error")
    return None

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
volt_ja_consumido = False
estrategia_ja_injetada = False

# ============= FUNÇÕES AUXILIARES DE LOGS E PARSE DE VELAS =============

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
    if 'max' in vela: return vela['max']
    return 0

def get_high(vela):
    if 'high' in vela: return vela['high']
    if 'max' in vela: return vela['max']
    return 0

def get_low(vela):
    if 'low' in vela: return vela['low']
    if 'min' in vela: return vela['min']
    return 0

# ============= INDICADORES PARA O DASHBOARD FRONTEND =============

def calcular_rsi(velas, periodo=14):
    if len(velas) < periodo + 1: return 50
    ganhos, perdas = [], []
    for i in range(1, len(velas)):
        diferenca = get_close(velas[i]) - get_close(velas[i-1])
        if diferenca >= 0:
            ganhos.append(diferenca); perdas.append(0)
        else:
            ganhos.append(0); perdas.append(abs(diferenca))
    ganhos, perdas = ganhos[-periodo:], perdas[-periodo:]
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

# ============= MANIPULAÇÃO DE MAPAS E ASSETS DO BANCO =============

def get_skins_fallback():
    return {
        'skin_padrao': {
            'id': 'skin_padrao', 'nome': '⚡ TESLA PADRÃO', 'desc': 'Tema escuro com raios dourados',
            'preco_moedas': 0, 'categoria': 'basica',
            'cor_fundo': '#0a0a1a', 'cor_panel': '#1a1a3e', 'cor_destaque': '#ffd700', 'cor_texto': '#fff',
            'cor_botao': 'linear-gradient(135deg,#cc8800,#ffd700)', 'cor_tab_ativa': '#ffd700',
            'cor_header_bg': 'linear-gradient(135deg,#1a0000,#331100,#553300,#331100,#1a0000)', 'cor_header_borda': '#ffd700',
            'header_extra': '<div class="lightning"></div>', 'css_extra': ''
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
        print(f"⚠️ Erro skin cloud {skin_id}: {e}")
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
            return skins_list
    except: pass
    
    fallback_skins = list(get_skins_fallback().values())
    cache_skins["data"] = fallback_skins
    cache_skins["timestamp"] = agora
    return fallback_skins

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
                    'desc': info.get('desc', 'Sem descrição.'),
                    'preco_moedas': info.get('preco', 0),
                    'timeframe': info.get('timeframe', 60),
                    'gratis': info.get('preco', 0) == 0
                }
            cache_estrategias_info["data"] = estrategias_info
            cache_estrategias_info["timestamp"] = agora
            return estrategias_info
    except: pass
    
    fallback = {'v_sensitivo': {'nome': 'V SENSITIVO', 'desc': 'Estratégia padrão', 'preco_moedas': 0, 'timeframe': 60, 'gratis': True}}
    cache_estrategias_info["data"] = fallback
    cache_estrategias_info["timestamp"] = agora
    return fallback

def carregar_estrategia_do_firebase(nome_estrategia):
    try:
        key = nome_estrategia.replace(".", "_").replace("@", "_").replace("#", "")
        r = requests.get(f'{FB_URL}/tesla_369/estrategias/{key}.json', timeout=5)
        if r.status_code == 200 and r.json(): return r.json()
    except: pass
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
            add_log(f"✅ Estratégia cloud '{nome_estrategia}' carregada!", "win")
            return True
    except Exception as e:
        print(f"❌ Erro compilação script dinâmico: {e}")
    return False

# ========== INTERFACE DATABASE USUÁRIOS ==========

def salvar_usuario(email, dados):
    try:
        key = email.replace("@", "_").replace(".", "_").replace("#", "").replace("$", "").replace("[", "").replace("]", "").replace("/", "_")
        requests.put(f'{FB_URL}/tesla_369/usuarios/{key}.json', json=dados, timeout=5)
    except: pass

def carregar_usuario(email):
    try:
        key = email.replace("@", "_").replace(".", "_").replace("#", "").replace("$", "").replace("[", "").replace("]", "").replace("/", "_")
        r = requests.get(f'{FB_URL}/tesla_369/usuarios/{key}.json', timeout=5)
        if r.status_code == 200: return r.json()
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

# ========== MOTOR DE OPERAÇÕES HARDCODED (TRANSTRANTE DIRETO DO TES.PY) ==========

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

def pegar_timestamp():
    try:
        if not API: return 0
        v = API.get_candles(par, timeframe_atual, 1, time.time())
        if v and isinstance(v, list) and len(v) > 0:
            return v[0]['from']
    except: pass
    return 0

def aguardar_inicio_vela():
    # Loop de espera rígido idêntico ao tes.py: segura o fluxo na virada da vela (segundo 0)
    while datetime.now().second > 1:
        if not bot_rodando: return False
        time.sleep(0.1)
    while True:
        if not bot_rodando: return False
        ts1 = pegar_timestamp()
        time.sleep(0.3)
        ts2 = pegar_timestamp()
        if ts1 == ts2 and ts1 != 0:
            return True

def aguardar_vela_fechar(ts_entrada):
    # Monitoramento síncrono bruto: só sai do loop se o timestamp do gráfico alterar
    while True:
        if not bot_rodando: return False
        try:
            ts_atual = pegar_timestamp()
            if ts_atual != ts_entrada and ts_atual > ts_entrada:
                return True
        except: pass
        time.sleep(0.4)

def verificar_resultado(saldo_antes, valor):
    saldo_base = saldo_antes - valor
    try:
        if not API: return -valor
        s = API.get_balance()
        d = round(s - saldo_base, 2)
        if d >= 1.0: return d
    except: pass
    return -valor

def consumir_volt():
    global volt_ja_consumido
    if volt_ja_consumido: return True
    usuario = carregar_usuario(email_usuario_atual)
    if not usuario: return False
    if usuario.get('moedas', 0) < 1: return False
    usuario['moedas'] -= 1
    usuario['total_ciclos'] = usuario.get('total_ciclos', 0) + 1
    salvar_usuario(email_usuario_atual, usuario)
    volt_ja_consumido = True
    add_log(f"⚡ 1 VOLT extraído. Saldo atual: {usuario['moedas']} VOLTS", 'info')
    return True

def executar_ciclo_completo_hardcoded(direcao_inicial):
    """
    MÉTODO EXCLUSIVO REESCRITO: Assume o controle completo das operações.
    Gerencia a Entrada Inicial e os Gales de forma isolada na mesma direção, exatamente como o tes.py.
    """
    global lucro, NumDeOperacoes, STOP_GAIN_ATINGIDO, bot_rodando, volt_ja_consumido
    if not bot_rodando or not API: return

    try:
        if not consumir_volt():
            add_log("❌ Módulo sem VOLTS!", 'error')
            bot_rodando = False
            return

        bi = API.get_balance()
        payout = Payout(par)
        entradas = calcular_entradas(bi, payout, MARTINGALE)
        
        add_log(f"💰 Operação Iniciada! Banca Inicial: ${bi:.2f} | Payout: {payout*100:.0f}%", 'info')
        add_log(f"📐 Grade Definida: E1:${entradas[0]:.2f} | E2:${entradas[1]:.2f} | E3:${entradas[2]:.2f}", 'info')

        gale_alcançado = 0
        vitoria = False
        ultimo_lucro_liquido = 0.0
        direcao = direcao_inicial  # Mantém a mesma direção fixa por todo o ciclo

        for i in range(MARTINGALE + 1):
            if not bot_rodando: break
            valor = entradas[i]
            gale_alcançado = i
            
            # Sincronização e trava de segundo inicial na vela (MOLDE TES.PY)
            if not aguardar_inicio_vela(): break
                
            saldo_antes = API.get_balance()
            if saldo_antes < valor:
                add_log(f"❌ Saldo insuficiente para realizar entrada no Gale {i}!", 'error')
                break

            # Dispara a ordem na corretora
            st, id_ordem = API.buy(valor, par, direcao, 1)
            if not st or not id_ordem:
                try: st, id_ordem = API.buy_digital_spot(par, valor, direcao, 1)
                except: pass
            
            if not st or not id_ordem:
                add_log(f"❌ Erro ao processar ordem no Gale {i}!", 'error')
                break

            # Coleta de timestamp pós-compra protegida contra delay
            time.sleep(0.5)
            ts_real = pegar_timestamp()
            
            # Trava a thread esperando os 60 segundos da vela fecharem de verdade
            if not aguardar_vela_fechar(ts_real): break
            
            # Checa o resultado calculando a variação do saldo líquido
            res = verificar_resultado(saldo_antes, valor)
            lucro += round(res, 2)
            saldo_depois = API.get_balance()
            ultimo_lucro_liquido = round(saldo_depois - saldo_antes, 2)

            if res > 0:
                vitoria = True
                NumDeOperacoes += 1
                u = carregar_usuario(email_usuario_atual)
                if u:
                    u['total_wins'] = u.get('total_wins', 0) + 1
                    u['total_ganho'] = u.get('total_ganho', 0) + abs(ultimo_lucro_liquido)
                    u['lucro_total'] = u['total_ganho'] - u.get('total_gasto', 0)
                    u['banca_atual'] = round(saldo_depois, 2)
                    u.setdefault('historico_operacoes', []).append({
                        'data': str(datetime.now())[:19], 'resultado': 'WIN', 'valor': valor, 'lucro': ultimo_lucro_liquido, 'estrategia': estrategia_atual_global.upper()
                    })
                    salvar_usuario(email_usuario_atual, u)
                STOP_GAIN_ATINGIDO = True
                break  # Sai do laço do ciclo imediatamente em caso de vitória (WIN)
            else:
                u = carregar_usuario(email_usuario_atual)
                if u:
                    u['total_losses'] = u.get('total_losses', 0) + 1
                    u['total_gasto'] = u.get('total_gasto', 0) + valor
                    u['lucro_total'] = u['total_ganho'] - u['total_gasto']
                    u['banca_atual'] = round(saldo_depois, 2)
                    u.setdefault('historico_operacoes', []).append({
                        'data': str(datetime.now())[:19], 'resultado': 'LOSS', 'valor': valor, 'lucro': -valor, 'estrategia': estrategia_atual_global.upper()
                    })
                    salvar_usuario(email_usuario_atual, u)
                # Se der Loss, ele continua no laço 'for' indo para o próximo Gale na mesma direção!

        # IMPRESSÃO EXCLUSIVA DO RELATÓRIO DO CICLO APÓS O FECHAMENTO TOTAL
        print()
        add_log("=" * 50, 'info')
        if vitoria:
            onde_ganhou = "de PRIMEIRA" if gale_alcançado == 0 else f"no GALE {gale_alcançado}"
            add_log(f"🌟 WIN ALCANÇADO {onde_ganhou}! Resultado: +${ultimo_lucro_liquido:.2f}", 'win')
            add_log("🎯 STOP GAIN ALCANÇADO - Ciclo finalizado.", 'win')
        else:
            add_log(f"💀 CICLO COMPLETO PERDIDO (STOP LOSS NO GALE {gale_alcançado})!", 'loss')
        
        bf = API.get_balance() if API else bi
        add_log(f"💰 Saldo Líquido do Ciclo: ${bf - bi:.2f} | Banca Final: ${bf:.2f}", 'info')
        add_log("=" * 50, 'info')
        print()
            
    except Exception as e:
        print(f"Erro controle de ciclos hardcoded: {e}")
    finally:
        bot_rodando = False
        add_log("⏹️ Robô em repouso pronto para nova ativação.", 'info')

# ========== LAÇO DE ESCUTA INFINITA DO GATILHO DA ESTRATÉGIA ==========

def bot_loop():
    global bot_rodando, BANCA_INICIAL_DO_BOT, lucro, NumDeOperacoes, STOP_GAIN_ATINGIDO, sinal_pendente, ultimo_sinal, timeframe_atual, volt_ja_consumido, estrategia_ja_injetada

    with bot_lock:
        if not bot_rodando or not API:
            bot_rodando = False
            return

        estrategias_info = carregar_informacoes_estrategias()
        if not estrategias_info or estrategia_atual_global not in estrategias_info:
            add_log("❌ Estratégia cloud inválida!", 'error')
            bot_rodando = False
            return

        estrategia_info = estrategias_info[estrategia_atual_global]
        timeframe_estrategia = estrategia_info.get('timeframe', 60)
        timeframe_atual = timeframe_estrategia
        add_log(f"📊 Algoritmo Selecionado: {estrategia_info.get('nome')}", 'indicator')
        add_log(f"⏱️ Base Gráfica: {timeframe_estrategia}s", 'info')

        if not estrategia_ja_injetada or cache_estrategia_carregada["nome"] != estrategia_atual_global:
            add_log(f"🔧 Baixando script dinâmico '{estrategia_atual_global}' do Cloud...", "info")
            if not carregar_e_injetar_estrategia(estrategia_atual_global):
                add_log(f"❌ Falha no download do algoritmo cloud.", 'error')
                bot_rodando = False
                return

        BANCA_INICIAL_DO_BOT = API.get_balance()
        STOP_GAIN_ATINGIDO = False
        lucro, NumDeOperacoes = 0.0, 0
        volt_ja_consumido = False
        ultimo_sinal = "Buscando gatilho..."
        add_log(f"📌 Par: {par} | Saldo em Conta: ${BANCA_INICIAL_DO_BOT:.2f}")

        def processar_estrategia():
            global timeframe_atual, sinal_pendente
            try:
                # O script injetado apenas monitora e cospe o sinal (Call/Put)
                resultado = estrategia_atual_executar(API, par, add_log)
                if resultado and bot_rodando:
                    direcao = resultado.get('direcao', '').lower()
                    novo_tf = resultado.get('timeframe', timeframe_estrategia)
                    if novo_tf != timeframe_atual: timeframe_atual = novo_tf
                    if direcao in ['call', 'put']:
                        with sinal_lock:
                            sinal_pendente = direcao
            except Exception as e:
                print(f"Erro execução thread sinal: {e}")

        # Inicia a thread em segundo plano para pescar o sinal
        threading.Thread(target=processar_estrategia, daemon=True).start()

        add_log("🧿 Monitoramento ativo. Aguardando sinal inicial da nuvem (Sem timeout)...", 'win')
        while bot_rodando and not STOP_GAIN_ATINGIDO:
            if not bot_rodando: break
            
            with sinal_lock:
                direcao = sinal_pendente
                if direcao:
                    sinal_pendente = None
            
            if direcao in ['call', 'put']:
                # Trava rígida: Só aceita o sinal se estiver nos segundos iniciais do nascimento da vela
                segundo_atual = datetime.now().second
                if segundo_atual <= 5:
                    ultimo_sinal = f"EXECUTANDO: {direcao.upper()}"
                    # CHAMA O CONTROLADOR COMPLETO HARDCODED: Ele consome o sinal e faz tudo sozinho!
                    executar_ciclo_completo_hardcoded(direcao)
                    break
                else:
                    add_log(f"⚠️ Sinal de {direcao.upper()} bloqueado por entrada tardia (Segundo {segundo_atual}). Buscando próximo...", 'indicator')
            
            time.sleep(0.5)

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
                        if mm5 > mm10 and mm10 > mm20: fase = "TENDÊNCIA ALTA"
                        elif mm5 < mm10 and mm10 < mm20: fase = "TENDÊNCIA BAIXA"
                        elif rsi_val < 40: fase = "ACUMULAÇÃO"
                        elif rsi_val > 60: fase = "EXAUSTÃO"
                        else: fase = "CONSOLIDAÇÃO"
                    else: fase = "ANALISANDO..."
                    
                    ultima_analise = {
                        'rsi': round(rsi_val, 1), 'mm5': round(mm5, 5) if mm5 else 0,
                        'mm10': round(mm10, 5) if mm10 else 0, 'mm20': round(mm20, 5) if mm20 else 0,
                        'stoch': round(estoc_val, 1), 'fase': fase, 'preco': round(preco_atual, 5) if preco_atual else 0
                    }
            except: pass
        time.sleep(2)

threading.Thread(target=analise_mercado_loop, daemon=True).start()

def sincronizar_html_local():
    try:
        os.makedirs("templates", exist_ok=True)
        HTML_URL = "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/tesla_369_bot/templates/index.html"
        response = requests.get(HTML_URL, timeout=10)
        if response.status_code == 200:
            with open("templates/index.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("✅ HTML sincronizado com o repositório principal!")
            return True
    except: return False

# ========== ENDPOINTS HTTP FLASK INTERFACE ==========

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
        HEADER_EXTRA=skin.get('header_extra', '<div class="lightning"></div>'), PLANOS_JSON=planos_json
    )

@app.route('/sinal', methods=['POST'])
def receber_sinal():
    global sinal_pendente
    if not bot_rodando or not conectado_iq: return jsonify({'ok': False, 'erro': 'Mecanismo inativo.'})
    direcao = request.get_json().get('direcao', '').lower()
    if direcao not in ['call', 'put']: return jsonify({'ok': False, 'erro': 'Gatilho inválido'})
    with sinal_lock: sinal_pendente = direcao
    return jsonify({'ok': True})

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

    return jsonify({
        'conectado': conectado_iq, 'rodando': bot_rodando, 'email': email_usuario_atual,
        'banca': API.get_balance() if API else 0, 'lucro': lucro, 'ops': NumDeOperacoes, 'sinal': ultimo_sinal,
        'logs': get_logs_html(40), 'moedas': u.get('moedas', 0) if u else 0, 'skin_id': skin_atual, 'skins_status': skins_status,
        'estrategia': estrategia_atual, 'estrategia_nome': estrategia_nome, 'estrategias_compradas': estrategias_compradas,
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
    if not email_usuario_atual: return jsonify({'ok': False, 'erro': 'Sessão ausente!'})
    u = carregar_usuario(email_usuario_atual)
    if not u: return jsonify({'ok': False, 'erro': 'Perfil não localizado'})
    estrategias_info = carregar_informacoes_estrategias()
    if est_id not in estrategias_info: return jsonify({'ok': False, 'erro': 'Identificador inválido'})
    
    compradas = u.get('estrategias_compradas', ['v_sensitivo'])
    if est_id not in compradas:
        if not estrategias_info[est_id].get('gratis', False): return jsonify({'ok': False, 'erro': f'Bloqueada!'})
        if 'estrategias_compradas' not in u: u['estrategias_compradas'] = ['v_sensitivo']
        u['estrategias_compradas'].append(est_id)
        
    u['estrategia_atual'] = est_id
    salvar_usuario(email_usuario_atual, u)
    estrategia_atual_global, estrategia_ja_injetada = est_id, False
    add_log(f"🧠 Estratégia alterada: {estrategias_info[est_id]['nome']}", 'indicator')
    return jsonify({'ok': True})

@app.route('/comprar_estrategia', methods=['POST'])
def comprar_estrategia():
    est_id = request.json.get('estrategia_id', '')
    if not email_usuario_atual: return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    estrategias_info = carregar_informacoes_estrategias()
    u = carregar_usuario(email_usuario_atual)
    if not u or est_id not in estrategias_info: return jsonify({'ok': False, 'erro': 'Parâmetros inválidos'})
    if 'estrategias_compradas' not in u: u['estrategias_compradas'] = ['v_sensitivo']
    if est_id in u['estrategias_compradas']:
        u['estrategia_atual'] = est_id
        salvar_usuario(email_usuario_atual, u)
        return jsonify({'ok': True, 'moedas': u['moedas'], 'msg': 'Já adquirida!'})
    preco = estrategias_info[est_id].get('preco_moedas', 0)
    if u.get('moedas', 0) < preco: return jsonify({'ok': False, 'erro': f'Precisa de {preco} ⚡'})
    u['moedas'] -= preco
    u['estrategias_compradas'].append(est_id)
    u['estrategia_atual'] = est_id
    salvar_usuario(email_usuario_atual, u)
    global estrategia_atual_global
    estrategia_atual_global = est_id
    add_log(f"🛒 Nova estratégia adquirida: {estrategias_info[est_id]['nome']}", 'win')
    return jsonify({'ok': True, 'moedas': u['moedas'], 'msg': 'Sucesso!'})

@app.route('/conectar', methods=['POST'])
def conectar():
    global API, email_usuario_atual, conectado_iq, skin_atual_global, estrategia_atual_global
    try:
        d = request.get_json()
        email, senha, tipo = d.get('email', '').strip(), d.get('senha', '').strip(), d.get('tipo', 'PRACTICE')
        if not email or not senha: return jsonify({'ok': False, 'erro': 'Credenciais vazias'})
        email_usuario_atual = email
        API = IQ_Option(email, senha)
        status_conn, reason = API.connect()
        if not status_conn: return jsonify({'ok': False, 'erro': str(reason)[:100]})
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
        add_log('🔌 Canal de dados síncronos estabelecido!', 'info')
        add_log(f'✅ Saldo: ${API.get_balance():.2f} | Módulo: {usuario.get("moedas", 0)} VOLTS', 'win')
        return jsonify({'ok': True, 'moedas': usuario.get('moedas', 0), 'refresh': True})
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)[:100]})

@app.route('/comecar_operar', methods=['POST'])
def comecar_operar():
    global bot_rodando, bot_thread, estrategia_ja_injetada
    try:
        if not conectado_iq: return jsonify({'ok': False, 'erro': 'Acesso à corretora offline!'})
        estrategias_info = carregar_informacoes_estrategias()
        if not estrategias_info or estrategia_atual_global not in estrategias_info:
            return jsonify({'ok': False, 'erro': '❌ Estratégia inválida no Cloud!'})
            
        usuario = carregar_usuario(email_usuario_atual)
        if not usuario: return jsonify({'ok': False, 'erro': 'Perfil não localizado!'})
        if usuario.get('moedas', 0) < 1: return jsonify({'ok': False, 'erro': 'Créditos insuficientes!'})

        with bot_lock:
            if bot_rodando and bot_thread and bot_thread.is_alive(): return jsonify({'ok': False, 'erro': 'Processo já ativo!'})
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
    add_log("🛑 Forçando interrupção imediata das rotinas...", 'info')
    bot_rodando = False
    volt_ja_consumido = False
    if data.get('desconectar'):
        conectado_iq = False
        add_log("🔌 Sessão encerrada", 'info')
    else:
        add_log("✅ Linha de execução limpa!", 'win')
    return jsonify({'ok': True, 'shutdown': data.get('desconectar', False)})

@app.route('/comprar_skin', methods=['POST'])
def comprar_skin():
    global skin_atual_global
    skin_id = request.get_json().get('skin_id', '')
    if not email_usuario_atual: return jsonify({'ok': False, 'erro': 'Sessão expirada'})
    skin = carregar_skin_do_firebase(skin_id) or next((s for s in carregar_todas_skins_do_firebase() if s.get('id') == skin_id), None)
    if not skin: return jsonify({'ok': False, 'erro': 'Tema inválido'})
    usuario = carregar_usuario(email_usuario_atual)
    
    compradas = usuario.get('skins_compradas', ['skin_padrao'])
    if skin.get('preco_moedas', 0) == 0:
        if skin_id not in compradas:
            if 'skins_compradas' not in usuario: usuario['skins_compradas'] = ['skin_padrao']
            usuario['skins_compradas'].append(skin_id)
        usuario['skin_atual'] = skin_id
        salvar_usuario(email_usuario_atual, usuario)
        skin_atual_global = skin_id
        return jsonify({'ok': True, 'moedas': usuario.get('moedas', 0), 'msg': 'Ativado!', 'refresh': True})
    
    if skin_id in compradas:
        usuario['skin_atual'] = skin_id
        salvar_usuario(email_usuario_atual, usuario)
        skin_atual_global = skin_id
        return jsonify({'ok': True, 'moedas': usuario['moedas'], 'msg': 'Modificado!', 'refresh': True})
        
    if usuario.get('moedas', 0) < skin.get('preco_moedas', 0): return jsonify({'ok': False, 'erro': 'Saldo insuficiente'})
    usuario['moedas'] -= skin['preco_moedas']
    usuario['skins_compradas'].append(skin_id)
    usuario['skin_atual'] = skin_id
    salvar_usuario(email_usuario_atual, usuario)
    skin_atual_global = skin_id
    return jsonify({'ok': True, 'moedas': usuario['moedas'], 'msg': 'Skin Adquirida!', 'refresh': True})

@app.route('/ativar_skin', methods=['POST'])
def activar_skin():
    skin_id = request.get_json().get('skin_id', '')
    if not email_usuario_atual: return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    usuario = carregar_usuario(email_usuario_atual)
    
    compradas = usuario.get('skins_compradas', ['skin_padrao'])
    if skin_id not in compradas:
        skin = carregar_skin_do_firebase(skin_id)
        if skin and skin.get('preco_moedas', 0) > 0: return jsonify({'ok': False, 'erro': 'Requer compra'})
        if 'skins_compradas' not in usuario: usuario['skins_compradas'] = ['skin_padrao']
        usuario['skins_compradas'].append(skin_id)
    usuario['skin_atual'] = skin_id
    salvar_usuario(email_usuario_atual, usuario)
    global skin_atual_global
    skin_atual_global = skin_id
    return jsonify({'ok': True, 'refresh': True})

# ========== INTERFACE GATEWAY MERCADO PAGO INTEGRADO ==========

def gerar_pix_mercadopago(email, plano):
    if MODO_SIMULACAO:
        pix_id = str(uuid.uuid4())[:8]
        pagamentos_pendentes[pix_id] = {'email': email, 'plano_id': plano['id'], 'moedas': plano['moedas'], 'valor': plano['preco'], 'pago': False, 'criado_em': str(datetime.now())[:19]}
        return {'sucesso': True, 'simulacao': True, 'pix_id': pix_id, 'qr_code': f"falso_{pix_id}", 'qr_code_base64': '', 'valor': plano['preco'], 'moedas': plano['moedas']}
    try:
        url = "https://api.mercadopago.com/v1/payments"
        headers = {"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}", "Content-Type": "application/json", "X-Idempotency-Key": str(uuid.uuid4())}
        payment_data = {
            "transaction_amount": float(plano['preco']), "description": f"TESLA369 - {plano['moedas']} VOLTS", "payment_method_id": "pix",
            "payer": {"email": email, "first_name": "Traders", "last_name": "Tesla", "identification": {"type": "CPF", "number": "00000000000"}}
        }
        response = requests.post(url, json=payment_data, headers=headers, timeout=30)
        data = response.json()
        if response.status_code in [200, 201]:
            pix_id = str(data['id'])
            pagamentos_pendentes[pix_id] = {'email': email, 'plano_id': plano['id'], 'moedas': plano['moedas'], 'valor': plano['preco'], 'pago': False, 'criado_em': str(datetime.now())[:19]}
            return {'sucesso': True, 'simulacao': False, 'pix_id': pix_id, 'qr_code': data['point_of_interaction']['transaction_data']['qr_code'], 'qr_code_base64': data['point_of_interaction']['transaction_data']['qr_code_base64'], 'valor': plano['preco'], 'moedas': plano['moedas']}
    except: pass
    return {'sucesso': False, 'erro': 'Gateway Indisponível'}

def verificar_pagamento_mp(pix_id):
    if MODO_SIMULACAO: return pagamentos_pendentes.get(pix_id, {}).get('pago', False)
    try:
        url = f"https://api.mercadopago.com/v1/payments/{pix_id}"
        headers = {"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}"}
        return requests.get(url, headers=headers, timeout=10).json().get('status') == 'approved'
    except: return False

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
                    add_log(f"💰 Transação MP Aprovada! +{dados['moedas']} VOLTS", "win")
        except: pass

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

# ========== CHAT E RANKING COMPATIBILIZADOS ==========

@app.route('/chat_enviar', methods=['POST'])
def chat_enviar():
    try:
        requests.post(f'{FB_URL}/tesla_369/chat.json', json={
            'nome': request.json.get('nome', 'Anonimo')[:15], 
            'msg': request.json.get('msg', '')[:200], 
            'hora': datetime.now().strftime('%H:%M')
        }, timeout=5)
    except: pass
    return jsonify({'ok': True})

@app.route('/chat_mensagens')
def chat_mensagens_route():
    try:
        r = requests.get(f'{FB_URL}/tesla_369/chat.json?orderBy="$key"&limitToLast=50', timeout=5)
        lista_msg = list(r.json().values()) if r.status_code == 200 and r.json() else []
        return jsonify({'messages': lista_msg, 'mensagens': lista_msg, 'online': 1})
    except: return jsonify({'messages': [], 'mensagens': [], 'online': 1})

@app.route('/ranking')
def ranking():
    ranking_list = []
    try:
        usuarios = requests.get(f'{FB_URL}/tesla_369/usuarios.json').json() or {}
        for k, ud in usuarios.items():
            if ud:
                ranking_list.append({
                    'email': ud.get('email', 'N/A'), 'lucro_total': round(ud.get('lucro_total', 0), 2),
                    'total_wins': ud.get('total_wins', 0), 'total_losses': ud.get('total_losses', 0), 'total_ciclos': ud.get('total_ciclos', 0),
                    'taxa': round((ud.get('total_wins', 0) / max(ud.get('total_ciclos', 1), 1)) * 100, 1), 'banca_atual': round(ud.get('banca_atual', 0), 2)
                })
    except: pass
    ranking_list.sort(key=lambda x: x['lucro_total'], reverse=True)
    tc, tw = sum(x['total_ciclos'] for x in ranking_list), sum(x['total_wins'] for x in ranking_list)
    return jsonify({'ranking': ranking_list, 'stats': {'total_usuarios': len(ranking_list), 'total_ops': tc, 'total_wins': tw, 'taxa_global': round((tw/max(tc,1))*100,1)}})

@app.route('/relatorio')
def relatorio():
    return jsonify(carregar_usuario(request.args.get('email', '')) or {'erro': 'Nao encontrado'})

@app.route('/resetar', methods=['POST'])
def resetar():
    u = carregar_usuario(request.json.get('email', ''))
    if not u: return jsonify({'ok': False, 'msg': 'Inexistente'})
    u.update({'total_ciclos':0,'total_wins':0,'total_losses':0,'total_gasto':0.0,'total_ganho':0.0,'lucro_total':0.0,'historico_operacoes':[],'dias_ativos':0,'banca_atual':0.0,'moedas_ganhas_hoje':str(datetime.now())[:10]})
    salvar_usuario(request.json.get('email', ''), u)
    return jsonify({'ok': True, 'msg': 'Zerado!'})

@app.route('/shutdown')
def shutdown():
    os.kill(os.getpid(), signal.SIGTERM)
    return jsonify({'ok': True})

if __name__ == '__main__':
    print("=" * 50)
    print("⚡ TESLA 369 BOT v13.0.4 - CICLO DE GALES ISOLADO DEFINITIVO ⚡")
    print("Lógica pura do tes.py restaurada: ordens e gales sob controle exclusivo do bot core.")
    print("=" * 50)

    carregar_todas_skins_do_firebase()
    carregar_informacoes_estrategias()
    sincronizar_html_local()

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
