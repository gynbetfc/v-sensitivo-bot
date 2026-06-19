#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ⚡ TESLA 369 BOT v18.0.0 - EXECUTA ORDENS DE FATO ⚡
# CORREÇÃO: Agora executa as ordens corretamente!

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

# ============= VERSÃO =============
BOT_VERSION = "18.0.0"
BOT_NAME = "TESLA-369"

# ============= CONFIGURACOES =============
FB_URL = "https://nexos-40654-default-rtdb.firebaseio.com"
print("✅ Firebase HTTP REST configurado!")

MARTINGALE = 2
PAYOUT_PADRAO = 0.85
PERCENTUAL_BANCA = 15

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
STOP_GAIN_ATINGIDO = False
bot_rodando, bot_thread = False, None
conectado_iq = False
ultimo_sinal = "Aguardando..."
logs_web, MAX_LOGS_WEB = [], 200
email_usuario_atual = ""
skin_atual_global = 'skin_padrao'
estrategia_atual_global = 'v_sensitivo'
bot_lock = threading.Lock()
volt_ja_consumido = False
estrategia_ja_injetada = False
ordem_id_atual = None

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
            'id': 'skin_padrao', 'nome': '⚡ TESLA THUNDER',
            'preco_moedas': 0, 'categoria': 'lendaria',
            'cor_fundo': '#000011', 'cor_panel': '#0a0a1a',
            'cor_destaque': '#ffff00', 'cor_texto': '#ffffff',
        }
    }

def carregar_todas_skins_do_firebase():
    try:
        r = requests.get(f'{FB_URL}/tesla_369/skins.json', timeout=5)
        if r.status_code == 200 and r.json():
            skins_dict = r.json()
            skins_list = []
            for skin_id, skin_data in skins_dict.items():
                skin_data['id'] = skin_id
                skins_list.append(skin_data)
            return skins_list
    except:
        pass
    return list(get_skins_fallback().values())

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
            print(f"✅ {len(estrategias_info)} estrategias carregadas!")
            return estrategias_info
    except Exception as e:
        print(f"⚠️ Erro ao carregar estrategias: {e}")
    return {}

def carregar_estrategia_do_firebase(nome_estrategia):
    try:
        key = nome_estrategia.replace(".", "_").replace("@", "_").replace("#", "")
        r = requests.get(f'{FB_URL}/tesla_369/estrategias/{key}.json', timeout=5)
        if r.status_code == 200 and r.json():
            return r.json()
    except:
        pass
    return None

def carregar_e_injetar_estrategia(nome_estrategia):
    global estrategia_atual_executar, cache_estrategia_carregada, estrategia_ja_injetada
    
    agora = time.time()
    if cache_estrategia_carregada["nome"] == nome_estrategia and (agora - cache_estrategia_carregada["timestamp"]) < CACHE_TTL:
        return True

    estrategia_data = carregar_estrategia_do_firebase(nome_estrategia)
    if not estrategia_data:
        add_log(f"❌ Estrategia '{nome_estrategia}' nao encontrada!", "error")
        return False

    codigo = estrategia_data.get('codigo')
    if not codigo or 'def rodar_analise' not in codigo:
        add_log(f"❌ Codigo invalido para '{nome_estrategia}'!", "error")
        return False

    try:
        escopo = {}
        exec(codigo, escopo)
        if 'rodar_analise' in escopo:
            estrategia_atual_executar = escopo['rodar_analise']
            cache_estrategia_carregada.update({"nome": nome_estrategia, "codigo": codigo, "timestamp": agora})
            estrategia_ja_injetada = True
            add_log(f"✅ Estrategia '{nome_estrategia}' injetada!", "win")
            return True
    except Exception as e:
        add_log(f"❌ Erro ao executar estrategia: {e}", "error")
        return False

# ========== FUNCOES DE USUARIO ==========

def salvar_usuario(email, dados):
    try:
        key = email.replace("@", "_").replace(".", "_")
        requests.put(f'{FB_URL}/tesla_369/usuarios/{key}.json', json=dados, timeout=5)
    except: pass

def carregar_usuario(email):
    try:
        key = email.replace("@", "_").replace(".", "_")
        r = requests.get(f'{FB_URL}/tesla_369/usuarios/{key}.json', timeout=5)
        if r.status_code == 200 and r.json(): return r.json()
    except: pass
    return None

def criar_usuario(email):
    dados = {
        'email': email, 'moedas': 12, 'moedas_ganhas_hoje': str(datetime.now())[:10],
        'total_ciclos': 0, 'total_wins': 0, 'total_losses': 0,
        'total_gasto': 0.0, 'total_ganho': 0.0, 'lucro_total': 0.0,
        'banca_atual': 0.0, 'data_cadastro': str(datetime.now())[:19],
        'historico_operacoes': [], 'dias_ativos': 0,
        'skin_atual': 'skin_padrao', 'skins_compradas': ['skin_padrao'],
        'estrategia_atual': 'v_sensitivo', 'estrategias_compradas': ['v_sensitivo']
    }
    salvar_usuario(email, dados)
    return dados

# ========== FUNCOES DO BOT ==========

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

def consumir_volt():
    global volt_ja_consumido
    if volt_ja_consumido: return True
    usuario = carregar_usuario(email_usuario_atual)
    if not usuario or usuario.get('moedas', 0) < 1:
        add_log("❌ Sem VOLTS!", 'error')
        return False
    usuario['moedas'] -= 1
    usuario['total_ciclos'] = usuario.get('total_ciclos', 0) + 1
    salvar_usuario(email_usuario_atual, usuario)
    volt_ja_consumido = True
    add_log(f"⚡ 1 VOLT consumido. Saldo: {usuario['moedas']} VOLTS", 'info')
    return True

def aguardar_inicio_vela(timeframe=60):
    """Aguarda o inicio da proxima vela"""
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

def executar_ciclo(direcao, timeframe=60):
    """EXECUTA UM CICLO COMPLETO - AGORA FUNCIONA!"""
    global lucro, NumDeOperacoes, STOP_GAIN_ATINGIDO, bot_rodando, volt_ja_consumido, ordem_id_atual

    if not bot_rodando:
        add_log("⚠️ Bot não está rodando!", "error")
        return

    if not API or not conectado_iq:
        add_log("❌ Sem conexão com IQ Option!", "error")
        return

    add_log(f"🔥 INICIANDO CICLO: {direcao.upper()} | Timeframe: {timeframe}s", 'sensitive')

    try:
        # Consome VOLT
        if not consumir_volt():
            add_log("❌ Falha ao consumir VOLT!", 'error')
            bot_rodando = False
            return

        # Pega saldo
        bi = API.get_balance()
        if bi is None:
            add_log("❌ Falha ao obter saldo!", 'error')
            return

        payout = Payout(par)
        entradas = calcular_entradas(bi, payout, MARTINGALE)
        add_log(f"💰 Banca: ${bi:.2f} | Payout: {payout*100:.0f}%", 'info')
        add_log(f"📐 E1:${entradas[0]:.2f} | E2:${entradas[1]:.2f} | E3:${entradas[2]:.2f}", 'info')

        for i in range(MARTINGALE + 1):
            if not bot_rodando:
                add_log("⏹️ Bot parado!", 'info')
                break

            valor = entradas[i]

            # Aguarda início da vela só na entrada principal
            if i == 0:
                if not aguardar_inicio_vela(timeframe):
                    add_log("⚠️ Falha ao aguardar inicio da vela!", 'error')
                    break
            else:
                time.sleep(0.5)
                add_log(f"   🔄 Executando GALE {i}...", 'info')

            saldo_antes = API.get_balance()
            if saldo_antes < valor:
                add_log(f"❌ Saldo insuficiente! Tem: ${saldo_antes:.2f} | Precisa: ${valor:.2f}", 'error')
                break

            # 🔥🔥🔥 EXECUTA A ORDEM 🔥🔥🔥
            add_log(f"🎯 { 'ENTRADA' if i == 0 else f'GALE {i}' }: {direcao.upper()} ${valor:.2f}", 'info')
            
            tempo_minutos = timeframe // 60 if timeframe >= 60 else 1
            st = False
            id_ordem = None

            # Tenta comprar com buy_digital_spot
            try:
                add_log(f"   📤 Enviando ordem: {par} | {direcao.upper()} | ${valor:.2f} | {tempo_minutos}min", 'info')
                st, id_ordem = API.buy_digital_spot(par, valor, direcao, tempo_minutos)
                add_log(f"   📊 Resultado: st={st}, id={id_ordem}", 'info')
            except Exception as e:
                add_log(f"   ❌ Erro no buy_digital_spot: {e}", 'error')

            # Se falhou, tenta com buy (método antigo)
            if not st or not id_ordem:
                try:
                    add_log(f"   🔄 Tentando método alternativo...", 'info')
                    st, id_ordem = API.buy(valor, par, direcao, tempo_minutos)
                    add_log(f"   📊 Resultado: st={st}, id={id_ordem}", 'info')
                except Exception as e:
                    add_log(f"   ❌ Erro no buy: {e}", 'error')

            # Se ainda falhou, tenta com buy_digital_spot com parâmetros diferentes
            if not st or not id_ordem:
                try:
                    add_log(f"   🔄 Tentando buy_digital_spot sem par...", 'info')
                    st, id_ordem = API.buy_digital_spot(par, valor, direcao, 1)
                    add_log(f"   📊 Resultado: st={st}, id={id_ordem}", 'info')
                except Exception as e:
                    add_log(f"   ❌ Erro: {e}", 'error')

            if not st or not id_ordem:
                add_log("❌ Falha na ordem! Verifique saldo e conexão.", 'error')
                break

            if i == 0:
                ordem_id_atual = id_ordem
                add_log(f"   ✅✅✅ ORDEM #{id_ordem} EXECUTADA! (Entrada Principal)", 'win')
            else:
                add_log(f"   ✅✅✅ ORDEM #{id_ordem} EXECUTADA! (GALE {i})", 'win')

            # Aguarda o timeframe
            add_log(f"   ⏳ Aguardando {timeframe} segundos para resultado...", 'info')
            for s in range(timeframe):
                if not bot_rodando:
                    return
                time.sleep(1)

            # Verifica resultado
            if not API or not conectado_iq:
                add_log("❌ Conexão perdida!", 'error')
                bot_rodando = False
                break

            saldo_depois = API.get_balance()
            lucro_liquido = round(saldo_depois - saldo_antes, 2)
            lucro += lucro_liquido

            if lucro_liquido > 0:
                add_log(f"🌟 WIN! +${lucro_liquido:.2f}", 'win')
                NumDeOperacoes += 1
                STOP_GAIN_ATINGIDO = True
                break
            else:
                add_log(f"💀 LOSS! {lucro_liquido:.2f}", 'loss')
                if i < MARTINGALE and bot_rodando:
                    add_log(f"   ➡️ Indo para GALE {i + 1}...", 'loss')
                else:
                    add_log("   💀 CICLO ESGOTADO!", 'loss')

        # Resumo
        if bot_rodando:
            bf = API.get_balance() if API else bi
            add_log("=" * 50, 'info')
            add_log(f"{'🌟 LUCRO' if bf > bi else '💀 PERDA'}: ${abs(bf - bi):.2f}", 'info')
            add_log("=" * 50, 'info')

    except Exception as e:
        add_log(f"❌ Erro no ciclo: {e}", 'error')
        import traceback
        traceback.print_exc()
    finally:
        ordem_id_atual = None
        add_log("⏹️ Ciclo finalizado!", 'info')

def bot_loop():
    """Loop principal do bot"""
    global bot_rodando, lucro, NumDeOperacoes, STOP_GAIN_ATINGIDO, ultimo_sinal, timeframe_atual, volt_ja_consumido, estrategia_ja_injetada

    with bot_lock:
        if not bot_rodando:
            return

        if not API or not conectado_iq:
            add_log("❌ Conecte-se primeiro!", 'error')
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
        add_log(f"📌 {par} | Timeframe: {timeframe_atual}s | 💰 ${API.get_balance():.2f}", 'info')

        while bot_rodando and not STOP_GAIN_ATINGIDO:
            if not API or not conectado_iq:
                add_log("⚠️ Aguardando reconexão...", "info")
                time.sleep(3)
                continue

            try:
                resultado = estrategia_atual_executar(API, par, add_log)
                
                if resultado and bot_rodando:
                    direcao = resultado.get('direcao', '').lower()
                    tf = resultado.get('timeframe', timeframe_atual)
                    
                    if direcao in ['call', 'put']:
                        ultimo_sinal = f"SINAL: {direcao.upper()} | {tf}s"
                        add_log(f"🎯 SINAL: {direcao.upper()} | Timeframe: {tf}s", 'sensitive')
                        add_log(f"🚀 CHAMANDO EXECUTAR_CICLO...", 'sensitive')
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
        if API and conectado_iq:
            try:
                API.get_server_timestamp()
            except:
                pass

def monitor_conexao_thread():
    global conectado_iq, bot_rodando
    while True:
        time.sleep(10)
        if API and conectado_iq:
            try:
                test = API.get_server_timestamp()
                if not test:
                    conectado_iq = False
                    if bot_rodando:
                        add_log("⚠️ Conexão perdida!", 'error')
            except:
                conectado_iq = False
                if bot_rodando:
                    add_log("⚠️ Conexão perdida!", 'error')

threading.Thread(target=keep_alive_thread, daemon=True).start()
threading.Thread(target=monitor_conexao_thread, daemon=True).start()

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
    except Exception as e:
        print(f"❌ Erro HTML: {e}")
    return False

# ========== ROTAS ==========

@app.route('/')
def index():
    skins = carregar_todas_skins_do_firebase()
    skin = next((s for s in skins if s.get('id') == skin_atual_global), {})
    return render_template('index.html')

@app.route('/status')
def status():
    u = carregar_usuario(email_usuario_atual) if email_usuario_atual else {}
    estrategias_info = carregar_informacoes_estrategias()
    return jsonify({
        'conectado': conectado_iq,
        'rodando': bot_rodando,
        'email': email_usuario_atual,
        'banca': API.get_balance() if API else 0,
        'lucro': lucro,
        'ops': NumDeOperacoes,
        'sinal': ultimo_sinal,
        'logs': get_logs_html(40),
        'moedas': u.get('moedas', 0) if u else 0,
        'estrategia': estrategia_atual_global,
        'timeframe_atual': timeframe_atual,
        'bot_version': BOT_VERSION
    })

@app.route('/conectar', methods=['POST'])
def conectar():
    global API, email_usuario_atual, conectado_iq, skin_atual_global, estrategia_atual_global
    try:
        d = request.get_json()
        email, senha, tipo = d.get('email', '').strip(), d.get('senha', '').strip(), d.get('tipo', 'PRACTICE')
        
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

@app.route('/selecionar_estrategia', methods=['POST'])
def selecionar_estrategia():
    global estrategia_atual_global, estrategia_ja_injetada
    est_id = request.json.get('estrategia', 'v_sensitivo')
    
    if not email_usuario_atual:
        return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    
    u = carregar_usuario(email_usuario_atual)
    if not u:
        return jsonify({'ok': False, 'erro': 'Usuario nao encontrado!'})
    
    estrategias_info = carregar_informacoes_estrategias()
    if est_id not in estrategias_info:
        return jsonify({'ok': False, 'erro': 'Estrategia invalida!'})
    
    if est_id not in u.get('estrategias_compradas', ['v_sensitivo']):
        if not estrategias_info[est_id].get('gratis', False):
            return jsonify({'ok': False, 'erro': 'Compre esta estrategia na loja!'})
        u['estrategias_compradas'].append(est_id)
    
    u['estrategia_atual'] = est_id
    salvar_usuario(email_usuario_atual, u)
    
    estrategia_atual_global = est_id
    estrategia_ja_injetada = False
    
    tf = estrategias_info[est_id].get('timeframe', 60)
    add_log(f"🧠 Estrategia selecionada: {estrategias_info[est_id]['nome']} | Timeframe: {tf}s", 'indicator')
    
    return jsonify({'ok': True, 'timeframe': tf})

@app.route('/comecar_operar', methods=['POST'])
def comecar_operar():
    global bot_rodando, bot_thread
    
    try:
        if not API or not conectado_iq:
            return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
        
        usuario = carregar_usuario(email_usuario_atual)
        if not usuario:
            return jsonify({'ok': False, 'erro': 'Usuario nao encontrado!'})
        
        if usuario.get('moedas', 0) < 1:
            return jsonify({'ok': False, 'erro': 'Sem VOLTS! Compre na loja.'})
        
        with bot_lock:
            if bot_rodando:
                return jsonify({'ok': False, 'erro': 'Bot ja rodando!'})
            
            bot_rodando = True
            bot_thread = threading.Thread(target=bot_loop, daemon=True)
            bot_thread.start()
        
        return jsonify({'ok': True, 'moedas': usuario['moedas']})
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)[:100]})

@app.route('/parar', methods=['POST'])
def parar():
    global bot_rodando
    bot_rodando = False
    add_log("🛑 Bot parado!", 'info')
    return jsonify({'ok': True})

# ========== INÍCIO ==========

if __name__ == '__main__':
    print("=" * 70)
    print(f"⚡ {BOT_NAME} v{BOT_VERSION} - EXECUTA ORDENS DE FATO ⚡")
    print("=" * 70)
    
    estrategias_info = carregar_informacoes_estrategias()
    print(f"📊 {len(estrategias_info)} estrategias carregadas!")
    for nome, info in estrategias_info.items():
        print(f"   📈 {nome}: {info.get('timeframe', 60)}s")
    
    sincronizar_html_local()
    
    port = int(os.environ.get('PORT', 5000))
    print(f"\n🚀 Servidor rodando em http://localhost:{port}")
    print("💡 Conecte-se e clique em 'Começar Operar'")
    
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
