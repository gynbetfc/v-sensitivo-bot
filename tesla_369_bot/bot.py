#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ⚡ TESLA 369 BOT v15.7.2 - LOGICA DEFINITIVA BLINDADA ⚡
# Firebase: SKINS e ESTRATÉGIAS carregadas da nuvem
# FIX: Estouro de cache de banca pós-60s e Martingale dinâmico adaptável

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

# ============= SKINS NO FIREBASE =============

def carregar_todas_skins_do_firebase():
    global cache_skins
    agora = time.time()
    if cache_skins["data"] and (agora - cache_skins["timestamp"]) < CACHE_TTL: return cache_skins["data"]
    try:
        r = requests.get(f'{FB_URL}/tesla_369/skins.json', timeout=5)
        if r.status_code == 200 and r.json():
            skins_list = []
            for skin_id, skin_data in r.json().items():
                skin_data['id'] = skin_id
                skins_list.append(skin_data)
            cache_skins["data"] = skins_list
            cache_skins["timestamp"] = agora
            return skins_list
    except: pass
    return []

def carregar_informacoes_estrategias():
    global cache_estrategias_info
    agora = time.time()
    if cache_estrategias_info["data"] and (agora - cache_estrategias_info["timestamp"]) < CACHE_TTL: return cache_estrategias_info["data"]
    try:
        r = requests.get(f'{FB_URL}/tesla_369/estrategias.json', timeout=5)
        if r.status_code == 200 and r.json():
            estrategias_info = {}
            for nome_est, dados in r.json().items():
                info = dados.get('info', {})
                estrategias_info[nome_est] = {
                    'nome': info.get('nome', nome_est.upper()), 'desc': info.get('desc', 'Sem descricao.'),
                    'preco_moedas': info.get('preco', 0), 'timeframe': info.get('timeframe', 60), 'gratis': info.get('preco', 0) == 0
                }
            cache_estrategias_info["data"] = estrategias_info
            cache_estrategias_info["timestamp"] = agora
            return estrategias_info
    except: pass
    return {}

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
    if cache_estrategia_carregada["nome"] == nome_estrategia and cache_estrategia_carregada["codigo"] is not None:
        return True
    estrategia_data = carregar_estrategia_do_firebase(nome_estrategia)
    if not estrategia_data: return False
    codigo = estrategia_data.get('codigo')
    try:
        escopo = {}
        exec(codigo, escopo)
        if 'rodar_analise' in escopo:
            estrategia_atual_executar = escopo['rodar_analise']
            cache_estrategia_carregada.update({"nome": nome_estrategia, "codigo": codigo, "timestamp": agora})
            estrategia_ja_injetada = True
            add_log(f"✅ Estrategia '{nome_estrategia}' injetada com sucesso!", "win")
            return True
    except: pass
    return False

def carregar_usuario(email):
    try:
        key = email.replace("@", "_").replace(".", "_").replace("#", "").replace("$", "").replace("[", "").replace("]", "").replace("/", "_")
        r = requests.get(f'{FB_URL}/tesla_369/usuarios/{key}.json', timeout=5)
        if r.status_code == 200 and r.json(): return r.json()
    except: pass
    return None

# ========== MOTOR DO BOT v15.7.2 CORRIGIDO ==========

def Payout(p):
    try:
        if not API: return PAYOUT_PADRAO
        API.subscribe_strike_list(p, 1)
        for _ in range(10):
            d = API.get_digital_current_profit(p, 1)
            if d != False:
                API.unsubscribe_strike_list(p, 1)
                return round(int(d) / 100, 2)
            time.sleep(0.5)
        API.unsubscribe_strike_list(p, 1)
        return PAYOUT_PADRAO
    except: return PAYOUT_PADRAO

def Martingale(valor, payout):
    lucro_esperado = valor * payout
    perca = float(valor)
    while True:
        if round(valor * payout, 2) > round(abs(perca) + lucro_esperado, 2): return round(valor, 2)
        valor += 0.01

def aguardar_inicio_vela():
    add_log("   ⏳ Aguardando inicio da vela...", 'info')
    while datetime.now().second > 4:
        if not bot_rodando: return False
        time.sleep(0.2)
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

def executar_ciclo(direcao):
    global lucro, NumDeOperacoes, STOP_GAIN_ATINGIDO, bot_rodando, volt_ja_consumido, timeframe_atual

    if not bot_rodando or not API: return

    try:
        if not consumir_volt():
            add_log("❌ Sem VOLTS!", 'error')
            bot_rodando = False
            return

        bi = API.get_balance()
        payout = Payout(par)
        
        # Determina o valor base inicial E1
        valor_atual = round((bi * PERCENTUAL_BANCA / 100) * 0.35, 2)
        if valor_atual < 1.0: valor_atual = 1.0
        
        add_log(f"💰 Banca Inicial: ${bi:.2f} | Payout: {payout*100:.0f}%", 'info')

        for i in range(MARTINGALE + 1):
            if not bot_rodando: break
            
            # Ajusta o valor se for Gale com base no payout real do instante
            if i > 0:
                payout = Payout(par)
                valor_atual = Martingale(valor_acumulado_losses, payout)

            if i == 0:
                if not aguardar_inicio_vela(): break

            saldo_antes = API.get_balance()
            if saldo_antes < valor_atual:
                add_log("❌ Saldo insuficiente!", 'error')
                break

            add_log(f"🎯 {'ENTRADA' if i == 0 else f'GALE {i} SEGUIDO'}: {direcao.upper()} ${valor_atual:.2f}", 'info')

            st, id_ordem = API.buy(valor_atual, par, direcao, 1)
            if not st or not id_ordem:
                try: st, id_ordem = API.buy_digital_spot(par, valor_atual, direcao.upper(), 1)
                except: pass

            if not st or not id_ordem:
                add_log("❌ Falha na ordem!", 'error')
                break

            add_log(f"   📝 Ordem #{id_ordem}", 'info')

            # 🔥 CONGELAMENTO REAL E BRUTO SEM TIMESTAMP DE CACHE 🔥
            add_log(f"   ⏳ Aguardando 60 segundos cravados de expiracao...", 'info')
            time.sleep(61)
            
            # FORCA A CORRETORA A ATUALIZAR O BALANCO REAL NA CONTA AGORA
            try: API.get_profile()
            except: pass
            
            saldo_depois = API.get_balance()
            lucro_liquido = round(saldo_depois - saldo_antes, 2)

            if lucro_liquido > 0:
                add_log(f"🌟 WIN! +${lucro_liquido:.2f}", 'win')
                lucro += lucro_liquido
                NumDeOperacoes += 1
                u = carregar_usuario(email_usuario_atual)
                if u:
                    u['total_wins'] = u.get('total_wins', 0) + 1
                    u['total_ganho'] = u.get('total_ganho', 0) + abs(lucro_liquido)
                    u['lucro_total'] = u['total_ganho'] - u.get('total_gasto', 0)
                    u['banca_atual'] = round(saldo_depois, 2)
                    u.setdefault('historico_operacoes', []).append({'data': str(datetime.now())[:19], 'resultado': 'WIN', 'valor': valor_atual, 'lucro': lucro_liquido, 'estrategia': estrategia_atual_global.upper()})
                    salvar_usuario(email_usuario_atual, u)
                STOP_GAIN_ATINGIDO = True
                add_log("🎯 STOP GAIN! Vitoria alcancada!", 'win')
                break
            else:
                add_log(f"💀 LOSS REAL! -${valor_atual:.2f}", 'loss')
                lucro -= valor_atual
                
                if i == 0: valor_acumulado_losses = valor_atual
                else: valor_acumulado_losses += valor_atual
                
                u = carregar_usuario(email_usuario_atual)
                if u:
                    u['total_losses'] = u.get('total_losses', 0) + 1
                    u['total_gasto'] = u.get('total_gasto', 0) + valor_atual
                    u['lucro_total'] = u['total_ganho'] - u['total_gasto']
                    u['banca_atual'] = round(saldo_depois, 2)
                    u.setdefault('historico_operacoes', []).append({'data': str(datetime.now())[:19], 'resultado': 'LOSS', 'valor': valor_atual, 'lucro': -valor_atual, 'estrategia': estrategia_atual_global.upper()})
                    salvar_usuario(email_usuario_atual, u)

                if i < MARTINGALE and bot_rodando:
                    add_log(f"   ➡️ Preparando virada automatica para o GALE {i + 1}...", 'loss')
                    time.sleep(0.5)
                else:
                    add_log("   💀 CICLO COMPLETO PERDIDO NA BANCA!", 'loss')

        if bot_rodando:
            bf = API.get_balance() if API else bi
            add_log("=" * 50, 'info')
            add_log(f"{'🌟 LUCRO' if bf > bi else '💀 PERDA'}: ${abs(bf - bi):.2f} | Banca: ${bf:.2f}", 'info')
            add_log("=" * 50, 'info')

    except Exception as e:
        add_log(f"Erro no motor: {e}", 'error')
    finally:
        bot_rodando = False
        add_log("⏹️ Ciclo finalizado!", 'info')

def bot_loop():
    global bot_rodando, BANCA_INICIAL_DO_BOT, lucro, NumDeOperacoes, STOP_GAIN_ATINGIDO, sinal_pendente, ultimo_sinal, timeframe_atual, volt_ja_consumido, estrategia_ja_injetada

    with bot_lock:
        if not bot_rodando or not API:
            bot_rodando = False
            return

        add_log(f"🔧 Carregando estrategia '{estrategia_atual_global}' do Firebase...", "info")
        if not carregar_e_injetar_estrategia(estrategia_atual_global):
            bot_rodando = False
            return

        BANCA_INICIAL_DO_BOT = API.get_balance()
        STOP_GAIN_ATINGIDO = False
        lucro, NumDeOperacoes = 0.0, 0
        volt_ja_consumido = False
        sinal_pendente = None
        ultimo_sinal = "Aguardando..."
        add_log(f"📌 {par} | 💰 ${BANCA_INICIAL_DO_BOT:.2f}")

        while bot_rodando and not STOP_GAIN_ATINGIDO:
            try:
                resultado = estrategia_atual_executar(API, par, add_log)
                if resultado and bot_rodando:
                    direcao = resultado.get('direcao', '').lower()
                    if direcao in ['call', 'put']:
                        ultimo_sinal = f"GATILHO: {direcao.upper()}"
                        executar_ciclo(direcao)
                        break
                time.sleep(0.3)
            except: time.sleep(5)

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
                    ultima_analise = {'rsi': round(rsi_val, 1), 'stoch': round(estoc_val, 1), 'fase': 'CONECTADO', 'preco': round(get_close(velas[-1]), 5)}
            except: pass
        time.sleep(2)

threading.Thread(target=analise_mercado_loop, daemon=True).start()

def sincronizar_html_local():
    try:
        os.makedirs("templates", exist_ok=True)
        response = requests.get("https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/tesla_369_bot/templates/index.html", timeout=10)
        if response.status_code == 200:
            with open("templates/index.html", "w", encoding="utf-8") as f: f.write(response.text)
            print("✅ HTML sincronizado!")
    except: pass

# ========== INJEÇÃO FLASK RESTO INTEGRAL ==========

@app.route('/')
def index():
    skins = carregar_todas_skins_do_firebase()
    skin = skins[0] if skins else {'cor_fundo': '#0a0a1a', 'cor_panel': '#1a1a3e', 'cor_destaque': '#ffd700', 'cor_texto': '#fff', 'cor_botao': 'linear-gradient(135deg,#cc8800,#ffd700)', 'cor_tab_ativa': '#ffd700', 'cor_header_bg': '#1a0000', 'cor_header_borda': '#ffd700', 'css_extra': '', 'header_extra': ''}
    return render_template('index.html', COR_FUNDO=skin.get('cor_fundo'), COR_PANEL=skin.get('cor_panel'), COR_DESTAQUE=skin.get('cor_destaque'), COR_TEXTO=skin.get('cor_texto'), COR_BOTAO=skin.get('cor_botao'), COR_TAB_ATIVA=skin.get('cor_tab_ativa'), COR_HEADER_BG=skin.get('cor_header_bg'), COR_HEADER_BORDA=skin.get('cor_header_borda'), CSS_EXTRA=skin.get('css_extra'), HEADER_EXTRA=skin.get('header_extra'), PLANOS_JSON='', BOT_VERSION=BOT_VERSION, BOT_NAME=BOT_NAME)

@app.route('/status')
def status():
    u = carregar_usuario(email_usuario_atual) if email_usuario_atual else {}
    estrategias_info = carregar_informacoes_estrategias()
    return jsonify({'conectado': conectado_iq, 'rodando': bot_rodando, 'email': email_usuario_atual, 'banca': API.get_balance() if API else 0, 'lucro': lucro, 'ops': NumDeOperacoes, 'sinal': ultimo_sinal, 'logs': get_logs_html(40), 'moedas': u.get('moedas', 0) if u else 0, 'skin_id': u.get('skin_atual','skin_padrao') if u else 'skin_padrao', 'estrategia': estrategia_atual_global, 'estrategia_nome': estrategias_info.get(estrategia_atual_global,{}).get('nome','Nenhuma'), 'analise': ultima_analise})

@app.route('/conectar', methods=['POST'])
def conectar():
    global API, email_usuario_atual, conectado_iq
    d = request.get_json()
    email, senha, tipo = d.get('email', '').strip(), d.get('senha', '').strip(), d.get('tipo', 'PRACTICE')
    email_usuario_atual = email
    API = IQ_Option(email, senha)
    status_conn, reason = API.connect()
    if not status_conn: return jsonify({'ok': False, 'erro': str(reason)})
    API.change_balance(tipo)
    conectado_iq = True
    add_log('🔌 Conectado!', 'info')
    return jsonify({'ok': True, 'refresh': True})

@app.route('/comecar_operar', methods=['POST'])
def comecar_operar():
    global bot_rodando, bot_thread
    if not conectado_iq: return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    with bot_lock:
        bot_rodando = True
        bot_thread = threading.Thread(target=bot_loop, daemon=True)
        bot_thread.start()
    return jsonify({'ok': True})

@app.route('/parar', methods=['POST'])
def parar():
    global bot_rodando; bot_rodando = False
    return jsonify({'ok': True})

if __name__ == '__main__':
    sincronizar_html_local()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
