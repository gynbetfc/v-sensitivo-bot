# ◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈
# TESLA 369 BOT v7.0.3 - COMPLETAMENTE MODULAR
# Sem skins hardcoded | Sem estrategias hardcoded
# Tudo carregado do Firebase
# ◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈

from flask import Flask, render_template_string, jsonify, request
from iqoptionapi.stable_api import IQ_Option
from datetime import datetime
import threading, time, sys, os, json, warnings, requests, uuid, base64, importlib, inspect

warnings.filterwarnings("ignore")
app = Flask(__name__)

# ============= CONFIGURACOES =============
FB_URL = "https://nexos-40654-default-rtdb.firebaseio.com"
MARTINGALE = 2
PAYOUT_PADRAO = 0.85
PERCENTUAL_BANCA = 15

# ============= MERCADO PAGO =============
MERCADO_PAGO_ACCESS_TOKEN = os.environ.get("MP_ACCESS_TOKEN", "APP_USR-4548266140377032-050311-6589fc22b166e4cb2cfad0379b28dcdf-1059299796")
MODO_SIMULACAO = False

# ============= PLANOS =============
PLANOS = [
    {'id':1,'moedas':1,'preco':0.99,'nome':'TESTE','desc':'R$0,99/VOLT'},
    {'id':2,'moedas':6,'preco':6.69,'nome':'BASICO','desc':'R$1,11/VOLT'},
    {'id':3,'moedas':15,'preco':9.99,'nome':'INTERMEDIARIO','desc':'R$0,67/VOLT'},
    {'id':4,'moedas':36,'preco':21.69,'nome':'PREMIUM','desc':'R$0,60/VOLT'},
    {'id':5,'moedas':69,'preco':39.69,'nome':'ULTRA','desc':'R$0,57/VOLT'},
]

# ============= CARREGAR SKINS DO FIREBASE =============
def carregar_skins():
    try:
        url = f"{FB_URL}/tesla_369/plugins/skins.json"
        r = requests.get(url, timeout=5)
        if r.status_code == 200 and r.json():
            skins = []
            for sid, sdata in r.json().items():
                if isinstance(sdata, dict) and 'cor_fundo' in sdata:
                    skin = sdata.copy()
                    skin['id'] = sid
                    skins.append(skin)
            if skins:
                print(f"{len(skins)} skins carregadas")
                return skins
    except Exception as e:
        print(f"Erro skins: {e}")
    return [{'id':'skin_padrao','nome':'PADRAO','preco_moedas':0,'cor_fundo':'#0a0a1a','cor_panel':'#1a1a3e','cor_destaque':'#ffd700','cor_texto':'#fff','cor_botao':'linear-gradient(135deg,#cc8800,#ffd700)','cor_tab_ativa':'#ffd700','cor_header_bg':'linear-gradient(135deg,#1a0000,#331100,#553300,#331100,#1a0000)','cor_header_borda':'#ffd700','header_extra':'','css_extra':''}]

SKINS = carregar_skins()

# ============= CARREGAR ESTRATEGIAS DO FIREBASE =============
def carregar_estrategias():
    try:
        url = f"{FB_URL}/tesla_369/plugins/estrategias.json"
        r = requests.get(url, timeout=5)
        if r.status_code == 200 and r.json():
            estrategias = {}
            for eid, edata in r.json().items():
                if isinstance(edata, dict):
                    nome_limpo = eid.replace('estrategia_', '')
                    estrategias[nome_limpo] = {
                        'nome': edata.get('nome', 'Estrategia'),
                        'desc': edata.get('desc', ''),
                        'timeframe': edata.get('timeframe', 60),
                        'pares': edata.get('pares', ['EURUSD-OTC']),
                        'preco_moedas': edata.get('preco_moedas', 0),
                        'gratis': edata.get('gratis', False),
                        'categoria': edata.get('categoria', 'basica')
                    }
            if estrategias:
                print(f"{len(estrategias)} estrategias carregadas")
                return estrategias
    except Exception as e:
        print(f"Erro estrategias: {e}")
    return {}

ESTRATEGIAS = carregar_estrategias()

# ============= FUNCOES USUARIO =============
def salvar_usuario(email, dados):
    try:
        key = email.replace("@", "_").replace(".", "_").replace("#", "").replace("$", "").replace("[", "").replace("]", "").replace("/", "_")
        requests.put(f'{FB_URL}/tesla_369/usuarios/{key}.json', json=dados, timeout=5)
    except:
        pass

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
        'email': email, 'moedas': 12, 'moedas_ganhas_hoje': str(datetime.now())[:10],
        'total_ciclos': 0, 'total_wins': 0, 'total_losses': 0, 'total_gasto': 0.0,
        'total_ganho': 0.0, 'lucro_total': 0.0, 'banca_atual': 0.0,
        'data_cadastro': str(datetime.now())[:19], 'historico_operacoes': [], 'dias_ativos': 0,
        'skin_atual': 'skin_padrao', 'skins_compradas': ['skin_padrao'],
        'estrategias_compradas': []
    }
    # Adiciona estrategias gratis
    for key, est in ESTRATEGIAS.items():
        if est.get('gratis', False):
            dados['estrategias_compradas'].append(key)
    salvar_usuario(email, dados)
    return dados

# ============= VARIAVEIS GLOBAIS =============
API = None
estrategia_atual = list(ESTRATEGIAS.keys())[0] if ESTRATEGIAS else None
timeframe_atual = 60
lucro = 0.0
NumDeOperacoes = 0
bot_rodando = False
conectado_iq = False
ultimo_sinal = "Aguardando..."
ultima_analise = {}
logs_web = []
email_usuario_atual = ""
skin_atual_global = 'skin_padrao'
pagamentos_pendentes = {}
bots_ativos = {}

# ============= LOGS =============
def add_log(msg, tipo='info'):
    global logs_web
    t = datetime.now().strftime('%H:%M:%S')
    logs_web.append({'time': t, 'msg': msg, 'tipo': tipo})
    if len(logs_web) > 200:
        logs_web = logs_web[-200:]
    print(f"{t} - {msg}")

def get_logs_html(limite=40):
    html = ''
    for log in logs_web[-limite:]:
        cor = {'win': '#0f0', 'loss': '#f44', 'info': '#0f0', 'sensitive': '#f69', 'indicator': '#fd0', 'error': '#f44'}.get(log['tipo'], '#0f0')
        html += f'<span style="color:#666">{log["time"]}</span> <span style="color:{cor}">{log["msg"]}</span>\n'
    return html or 'Aguardando...'

# ============= INDICADORES =============
def sma(v, p):
    if len(v) < p: return None
    return round(sum(x['close'] for x in v[-p:]) / p, 6)

def rsi(v, p=9):
    if len(v) < p + 1: return None
    g, l = [], []
    for i in range(1, len(v)):
        d = v[i]['close'] - v[i-1]['close']
        g.append(d if d > 0 else 0)
        l.append(abs(d) if d < 0 else 0)
    if sum(l) == 0: return 100
    return round(100 - (100 / (1 + sum(g) / sum(l))), 2)

def macd(v, r=12, l=26):
    if len(v) < l: return None
    c = [x['close'] for x in v]
    er, el = c[0], c[0]
    for x in c[1:]:
        er = x * (2/(r+1)) + er * (1-2/(r+1))
        el = x * (2/(l+1)) + el * (1-2/(l+1))
    return round(er - el, 8)

# ============= FUNCAO PARA EXECUTAR SINAL DINAMICO =============
def executar_sinal_dinamico():
    """Executa o sinal da estrategia atual (carregada dinamicamente)"""
    global ultimo_sinal, ultima_analise
    
    if not estrategia_atual:
        return None
    
    try:
        # Pega os parametros da estrategia
        est_params = ESTRATEGIAS.get(estrategia_atual, {})
        timeframe = est_params.get('timeframe', 60)
        pares = est_params.get('pares', ['EURUSD-OTC'])
        par_atual = pares[0] if pares else 'EURUSD-OTC'
        
        # Busca os candles
        v = API.get_candles(par_atual, timeframe, 30, time.time())
        if len(v) < 20:
            return None
        
        # Calcula indicadores
        rs = rsi(v)
        m5 = sma(v, 5)
        m10 = sma(v, 10)
        m20 = sma(v, 20)
        mc = macd(v)
        pc = v[-1]['close']
        
        ultima_analise = {'preco': pc, 'rsi': rs, 'mm5': m5, 'mm10': m10, 'mm20': m20}
        
        # Logica simples de sinal (pode ser expandida)
        sc = sp = 0
        
        if m5 and m20:
            if m5 > m20: sc += 30
            else: sp += 30
        
        if rs:
            if rs < 30: sc += 35
            elif rs > 70: sp += 35
        
        if mc:
            if mc > 0: sc += 20
            else: sp += 20
        
        dif = abs(sc - sp)
        
        if sc > sp and dif >= 20:
            ultimo_sinal = f"CALL ({sc}x{sp})"
            add_log(f"CALL {estrategia_atual}", 'sensitive')
            return 'call'
        if sp > sc and dif >= 20:
            ultimo_sinal = f"PUT ({sp}x{sc})"
            add_log(f"PUT {estrategia_atual}", 'sensitive')
            return 'put'
        
        ultimo_sinal = "..."
        return None
    except Exception as e:
        add_log(f"Erro sinal: {e}", 'error')
        return None

# ============= CALCULO DE ENTRADAS =============
def calcular_entradas(b, p, g):
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
    v = API.get_candles(par_atual, timeframe_atual, 1, time.time())
    return v[0]['from'] if v else 0

def aguardar_inicio_vela():
    add_log("Aguardando inicio da vela...", 'info')
    while datetime.now().second > 5:
        if not bot_rodando: return False
        time.sleep(0.3)
    while True:
        if not bot_rodando: return False
        ts1 = pegar_timestamp()
        time.sleep(0.5)
        ts2 = pegar_timestamp()
        if ts1 == ts2:
            add_log("Vela confirmada!", 'info')
            return True

def aguardar_vela_fechar(ts_entrada):
    add_log("Aguardando vela fechar...", 'info')
    while True:
        if not bot_rodando: return False
        try:
            if pegar_timestamp() != ts_entrada:
                add_log("Vela fechou!", 'info')
                return True
        except:
            pass
        time.sleep(0.3)

def verificar_resultado(saldo_antes, valor):
    saldo_base = saldo_antes - valor
    try:
        s = API.get_balance()
        d = round(s - saldo_base, 2)
        if d >= 1.0: return d
    except:
        pass
    return -valor

# ============= EXECUTAR CICLO =============
def executar_ciclo(direcao):
    global lucro, NumDeOperacoes, bot_rodando, estrategia_atual, par_atual
    
    bi = API.get_balance()
    
    est_params = ESTRATEGIAS.get(estrategia_atual, {})
    pares = est_params.get('pares', ['EURUSD-OTC'])
    par_atual = pares[0] if pares else 'EURUSD-OTC'
    
    # Payout
    try:
        API.subscribe_strike_list(par_atual, 1)
        payout = PAYOUT_PADRAO
        for _ in range(20):
            d = API.get_digital_current_profit(par_atual, 1)
            if d != False:
                payout = round(int(d) / 100, 2)
                break
            time.sleep(0.5)
        API.unsubscribe_strike_list(par_atual, 1)
    except:
        payout = PAYOUT_PADRAO
    
    entradas = calcular_entradas(bi, payout, MARTINGALE)
    add_log(f"Banca: ${bi:.2f} | Payout: {payout*100:.0f}%", 'info')
    add_log(f"E1:${entradas[0]:.2f} | E2:${entradas[1]:.2f} | E3:${entradas[2]:.2f}", 'info')
    
    for i in range(MARTINGALE + 1):
        if not bot_rodando: break
        valor = entradas[i]
        if not aguardar_inicio_vela(): break
        saldo_antes = API.get_balance()
        if saldo_antes < valor:
            add_log("Saldo insuficiente!", 'error')
            break
        
        add_log(f"{'ENTRADA' if i == 0 else f'GALE {i}'}: {direcao.upper()} ${valor:.2f}", 'info')
        st, id_ordem = API.buy(valor, par_atual, direcao, 1)
        if not st or not id_ordem:
            try:
                st, id_ordem = API.buy_digital_spot(par_atual, valor, direcao, 1)
            except:
                pass
        if not st or not id_ordem:
            add_log("Falha na ordem!", 'error')
            break
        
        time.sleep(0.3)
        ts_real = pegar_timestamp()
        if not aguardar_vela_fechar(ts_real): break
        
        res = verificar_resultado(saldo_antes, valor)
        lucro += round(res, 2)
        saldo_depois = API.get_balance()
        lucro_liquido = round(saldo_depois - saldo_antes, 2)
        
        if res > 0:
            add_log(f"WIN! +${lucro_liquido:.2f}", 'win')
            NumDeOperacoes += 1
            u = carregar_usuario(email_usuario_atual)
            if u:
                u['total_wins'] += 1
                u['total_ganho'] += abs(lucro_liquido)
                u['lucro_total'] = u['total_ganho'] - u['total_gasto']
                u['banca_atual'] = round(saldo_depois, 2)
                u.setdefault('historico_operacoes', []).append({
                    'data': str(datetime.now())[:19], 'resultado': 'WIN',
                    'valor': valor, 'lucro': lucro_liquido, 'estrategia': estrategia_atual
                })
                u['dias_ativos'] = u.get('dias_ativos', 0) + 1
                salvar_usuario(email_usuario_atual, u)
            bot_rodando = False
            add_log("STOP GAIN! Bot PARADO!", 'win')
            break
        else:
            add_log(f"LOSS! -${valor:.2f}", 'loss')
            u = carregar_usuario(email_usuario_atual)
            if u:
                u['total_losses'] += 1
                u['total_gasto'] += valor
                u['lucro_total'] = u['total_ganho'] - u['total_gasto']
                u['banca_atual'] = round(saldo_depois, 2)
                u.setdefault('historico_operacoes', []).append({
                    'data': str(datetime.now())[:19], 'resultado': 'LOSS',
                    'valor': valor, 'lucro': -valor, 'estrategia': estrategia_atual
                })
                u['dias_ativos'] = u.get('dias_ativos', 0) + 1
                salvar_usuario(email_usuario_atual, u)
            if i < MARTINGALE:
                add_log(f"Indo para GALE {i+1}...", 'loss')
            else:
                add_log("CICLO COMPLETO PERDIDO! Bot PARADO!", 'loss')
    
    add_log("="*50, 'info')
    bf = API.get_balance()
    add_log(f"{'LUCRO' if bf > bi else 'PERDA'}: ${abs(bf - bi):.2f} | Banca: ${bf:.2f}", 'info')
    add_log("="*50, 'info')
    bot_rodando = False
    add_log("Ciclo concluido!", 'info')

# ============= BOT LOOP =============
def bot_loop():
    global bot_rodando, lucro, NumDeOperacoes
    
    if not estrategia_atual:
        add_log("Nenhuma estrategia selecionada!", 'error')
        bot_rodando = False
        return
    
    nome_est = ESTRATEGIAS.get(estrategia_atual, {}).get('nome', estrategia_atual)
    add_log(f'INICIANDO - Estrategia: {nome_est}', 'sensitive')
    add_log(f'Banca: ${API.get_balance():.2f}')
    add_log('Buscando sinal...', 'info')
    
    while bot_rodando:
        try:
            direcao = executar_sinal_dinamico()
            if direcao:
                executar_ciclo(direcao)
                break
            time.sleep(0.3)
        except Exception as e:
            add_log(f"Erro: {e}", 'error')
            time.sleep(5)
    
    if not bot_rodando:
        add_log("Bot parado.", 'info')

# ============= MERCADO PAGO =============
def gerar_pix_mercadopago(email, plano):
    if MODO_SIMULACAO:
        pix_id = str(uuid.uuid4())[:8]
        pagamentos_pendentes[pix_id] = {'email': email, 'plano_id': plano['id'], 'moedas': plano['moedas'], 'valor': plano['preco'], 'pago': False}
        return {'sucesso': True, 'simulacao': True, 'pix_id': pix_id, 'qr_code': f"PIX R$ {plano['preco']:.2f} - ID: {pix_id}", 'valor': plano['preco'], 'moedas': plano['moedas']}
    try:
        headers = {"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}", "Content-Type": "application/json", "X-Idempotency-Key": str(uuid.uuid4())}
        payment_data = {"transaction_amount": float(plano['preco']), "description": f"TESLA369 - {plano['moedas']} moedas", "payment_method_id": "pix", "payer": {"email": email}}
        response = requests.post("https://api.mercadopago.com/v1/payments", json=payment_data, headers=headers)
        data = response.json()
        if response.status_code in [200, 201]:
            pix_id = str(data['id'])
            pagamentos_pendentes[pix_id] = {'email': email, 'plano_id': plano['id'], 'moedas': plano['moedas'], 'valor': plano['preco'], 'pago': False}
            return {'sucesso': True, 'simulacao': False, 'pix_id': pix_id, 'qr_code': data['point_of_interaction']['transaction_data']['qr_code'], 'qr_code_base64': data['point_of_interaction']['transaction_data']['qr_code_base64'], 'valor': plano['preco'], 'moedas': plano['moedas']}
        return {'sucesso': False, 'erro': data.get('message', 'Erro')}
    except Exception as e:
        return {'sucesso': False, 'erro': str(e)}

def verificar_pagamento_mp(pix_id):
    if MODO_SIMULACAO:
        return pagamentos_pendentes.get(pix_id, {}).get('pago', False)
    try:
        r = requests.get(f"https://api.mercadopago.com/v1/payments/{pix_id}", headers={"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}"})
        return r.json().get('status') == 'approved'
    except:
        return False

def verificador_automatico_pix():
    while True:
        time.sleep(10)
        try:
            for pix_id, dados in list(pagamentos_pendentes.items()):
                if not dados.get('pago') and verificar_pagamento_mp(pix_id):
                    dados['pago'] = True
                    usuario = carregar_usuario(dados['email']) or criar_usuario(dados['email'])
                    usuario['moedas'] = usuario.get('moedas', 0) + dados['moedas']
                    salvar_usuario(dados['email'], usuario)
                    add_log(f"PIX pago! +{dados['moedas']} VOLTS", "win")
        except:
            pass

threading.Thread(target=verificador_automatico_pix, daemon=True).start()

# ============= ROTAS =============
@app.route('/set_percentual', methods=['POST'])
def set_percentual():
    global PERCENTUAL_BANCA
    PERCENTUAL_BANCA = request.json.get('percentual', 10)
    return jsonify({'ok': True})

@app.route('/')
def index():
    global skin_atual_global
    skin = next((s for s in SKINS if s['id'] == skin_atual_global), SKINS[0] if SKINS else {})
    html = HTML
    html = html.replace('{{COR_FUNDO}}', skin.get('cor_fundo', '#0a0a1a'))
    html = html.replace('{{COR_PANEL}}', skin.get('cor_panel', '#1a1a3e'))
    html = html.replace('{{COR_DESTAQUE}}', skin.get('cor_destaque', '#ffd700'))
    html = html.replace('{{COR_TEXTO}}', skin.get('cor_texto', '#fff'))
    html = html.replace('{{COR_BOTAO}}', skin.get('cor_botao', 'linear-gradient(135deg,#cc8800,#ffd700)'))
    html = html.replace('{{COR_TAB_ATIVA}}', skin.get('cor_tab_ativa', '#ffd700'))
    html = html.replace('{{COR_HEADER_BG}}', skin.get('cor_header_bg', 'linear-gradient(135deg,#1a0000,#331100,#553300,#331100,#1a0000)'))
    html = html.replace('{{COR_HEADER_BORDA}}', skin.get('cor_header_borda', '#ffd700'))
    html = html.replace('{{CSS_EXTRA}}', skin.get('css_extra', ''))
    html = html.replace('{{HEADER_EXTRA}}', skin.get('header_extra', ''))
    return render_template_string(html)

@app.route('/status')
def status():
    global skin_atual_global, estrategia_atual
    u = carregar_usuario(email_usuario_atual) if email_usuario_atual else {}
    
    skins_status = []
    for skin in SKINS:
        skins_status.append({
            'id': skin.get('id'), 'nome': skin.get('nome'), 'desc': skin.get('desc'),
            'preco_moedas': skin.get('preco_moedas', 0), 'categoria': skin.get('categoria', 'basica'),
            'comprado': skin.get('id') in u.get('skins_compradas', []) if u else False,
            'ativo': skin.get('id') == u.get('skin_atual', 'skin_padrao') if u else False
        })
    
    return jsonify({
        'conectado': conectado_iq, 'rodando': bot_rodando, 'email': email_usuario_atual,
        'banca': API.get_balance() if API else 0, 'lucro': lucro, 'ops': NumDeOperacoes,
        'sinal': ultimo_sinal, 'analise': ultima_analise, 'logs': get_logs_html(40),
        'moedas': u.get('moedas', 0) if u else 0, 'estrategia': estrategia_atual,
        'estrategia_nome': ESTRATEGIAS.get(estrategia_atual, {}).get('nome', '--'),
        'skin_id': u.get('skin_atual', 'skin_padrao') if u else 'skin_padrao',
        'skins_status': skins_status, 'estrategias_compradas': u.get('estrategias_compradas', []) if u else [],
        'estrategias_disponiveis': ESTRATEGIAS
    })

@app.route('/conectar', methods=['POST'])
def conectar():
    global API, email_usuario_atual, conectado_iq, skin_atual_global, estrategia_atual
    global par_atual, timeframe_atual
    
    try:
        d = request.json
        email = d.get('email', '').strip()
        senha = d.get('senha', '').strip()
        tipo = d.get('tipo', 'PRACTICE')
        
        if not email or not senha:
            return jsonify({'ok': False, 'erro': 'Email e senha obrigatorios'})
        
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
        
        # Se nao tem estrategia selecionada, pega a primeira disponivel
        if not estrategia_atual and ESTRATEGIAS:
            estrategia_atual = list(ESTRATEGIAS.keys())[0]
        
        est_params = ESTRATEGIAS.get(estrategia_atual, {})
        timeframe_atual = est_params.get('timeframe', 60)
        
        add_log(f'Conectado! ${API.get_balance():.2f} | {usuario.get("moedas", 0)} VOLTS', 'win')
        return jsonify({'ok': True, 'moedas': usuario.get('moedas', 0)})
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)[:100]})

@app.route('/comecar_operar', methods=['POST'])
def comecar_operar():
    global bot_rodando, bot_thread, lucro, NumDeOperacoes
    
    if not conectado_iq:
        return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    
    usuario = carregar_usuario(email_usuario_atual)
    if not usuario:
        return jsonify({'ok': False, 'erro': 'Usuario nao encontrado!'})
    
    if estrategia_atual not in usuario.get('estrategias_compradas', []):
        return jsonify({'ok': False, 'erro': 'Estrategia nao comprada!'})
    
    if usuario.get('moedas', 0) < 1:
        return jsonify({'ok': False, 'erro': 'Sem VOLTS!'})
    
    usuario['moedas'] -= 1
    usuario['total_ciclos'] += 1
    salvar_usuario(email_usuario_atual, usuario)
    
    lucro = 0.0
    NumDeOperacoes = 0
    
    if not bot_rodando:
        bot_rodando = True
        bot_thread = threading.Thread(target=bot_loop, daemon=True)
        bot_thread.start()
    
    return jsonify({'ok': True, 'moedas': usuario['moedas']})

@app.route('/parar', methods=['POST'])
def parar():
    global bot_rodando, conectado_iq
    data = request.json or {}
    bot_rodando = False
    if data.get('desconectar'):
        conectado_iq = False
    return jsonify({'ok': True})

@app.route('/selecionar_estrategia', methods=['POST'])
def selecionar_estrategia():
    global estrategia_atual, timeframe_atual
    est_key = request.json.get('estrategia', '')
    if est_key in ESTRATEGIAS:
        estrategia_atual = est_key
        timeframe_atual = ESTRATEGIAS[est_key].get('timeframe', 60)
        return jsonify({'ok': True})
    return jsonify({'ok': False})

@app.route('/comprar_skin', methods=['POST'])
def comprar_skin():
    global skin_atual_global
    skin_id = request.json.get('skin_id', '')
    
    if not email_usuario_atual:
        return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    
    skin = next((s for s in SKINS if s.get('id') == skin_id), None)
    if not skin:
        return jsonify({'ok': False, 'erro': 'Skin nao encontrada'})
    
    usuario = carregar_usuario(email_usuario_atual)
    if not usuario:
        return jsonify({'ok': False, 'erro': 'Usuario nao encontrado'})
    
    preco = skin.get('preco_moedas', 0)
    
    if 'skins_compradas' not in usuario:
        usuario['skins_compradas'] = ['skin_padrao']
    
    if skin_id in usuario['skins_compradas']:
        usuario['skin_atual'] = skin_id
        salvar_usuario(email_usuario_atual, usuario)
        skin_atual_global = skin_id
        return jsonify({'ok': True, 'moedas': usuario['moedas'], 'msg': 'Skin ativada!'})
    
    if usuario.get('moedas', 0) < preco:
        return jsonify({'ok': False, 'erro': f'VOLTS insuficientes! Precisa de {preco}'})
    
    usuario['moedas'] -= preco
    usuario['skins_compradas'].append(skin_id)
    usuario['skin_atual'] = skin_id
    salvar_usuario(email_usuario_atual, usuario)
    skin_atual_global = skin_id
    
    return jsonify({'ok': True, 'moedas': usuario['moedas'], 'msg': f'Skin {skin.get("nome")} comprada!'})

@app.route('/ativar_skin', methods=['POST'])
def ativar_skin():
    skin_id = request.json.get('skin_id', '')
    
    if not email_usuario_atual:
        return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    
    usuario = carregar_usuario(email_usuario_atual)
    if not usuario:
        return jsonify({'ok': False, 'erro': 'Usuario nao encontrado'})
    
    if skin_id not in usuario.get('skins_compradas', []):
        return jsonify({'ok': False, 'erro': 'Compre a skin primeiro!'})
    
    usuario['skin_atual'] = skin_id
    salvar_usuario(email_usuario_atual, usuario)
    global skin_atual_global
    skin_atual_global = skin_id
    
    return jsonify({'ok': True})

@app.route('/comprar_estrategia', methods=['POST'])
def comprar_estrategia():
    estrategia_id = request.json.get('estrategia_id', '')
    
    if not email_usuario_atual:
        return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    
    if estrategia_id not in ESTRATEGIAS:
        return jsonify({'ok': False, 'erro': 'Estrategia invalida!'})
    
    estrategia = ESTRATEGIAS[estrategia_id]
    u = carregar_usuario(email_usuario_atual) or criar_usuario(email_usuario_atual)
    
    if estrategia_id in u.get('estrategias_compradas', []):
        return jsonify({'ok': False, 'erro': 'Estrategia ja comprada!'})
    
    preco = estrategia.get('preco_moedas', 0)
    
    if preco == 0 or estrategia.get('gratis', False):
        u['estrategias_compradas'].append(estrategia_id)
        salvar_usuario(email_usuario_atual, u)
        return jsonify({'ok': True, 'msg': f'Estrategia {estrategia["nome"]} ativada!', 'moedas': u.get('moedas', 0)})
    
    if u.get('moedas', 0) < preco:
        return jsonify({'ok': False, 'erro': f'VOLTS insuficientes! Precisa de {preco}'})
    
    u['moedas'] -= preco
    u['estrategias_compradas'].append(estrategia_id)
    salvar_usuario(email_usuario_atual, u)
    
    return jsonify({'ok': True, 'msg': f'Estrategia {estrategia["nome"]} comprada!', 'moedas': u['moedas']})

@app.route('/criar_pix', methods=['POST'])
def criar_pix():
    d = request.json
    email = d.get('email', '')
    plano_id = int(d.get('plano_id', 1))
    plano = next((p for p in PLANOS if p['id'] == plano_id), None)
    if not email or not plano:
        return jsonify({'sucesso': False, 'erro': 'Dados invalidos'})
    return jsonify(gerar_pix_mercadopago(email, plano))

@app.route('/verificar_pix', methods=['POST'])
def verificar_pix():
    pix_id = request.json.get('pix_id', '')
    if verificar_pagamento_mp(pix_id) and pix_id in pagamentos_pendentes and not pagamentos_pendentes[pix_id]['pago']:
        pagamentos_pendentes[pix_id]['pago'] = True
        email = pagamentos_pendentes[pix_id]['email']
        moedas = pagamentos_pendentes[pix_id]['moedas']
        usuario = carregar_usuario(email) or criar_usuario(email)
        usuario['moedas'] = usuario.get('moedas', 0) + moedas
        salvar_usuario(email, usuario)
        return jsonify({'pago': True, 'moedas': moedas, 'saldo': usuario['moedas']})
    return jsonify({'pago': False})

@app.route('/ranking')
def ranking():
    ranking_list = []
    try:
        r = requests.get(f'{FB_URL}/tesla_369/usuarios.json', timeout=10)
        if r.status_code == 200 and r.json():
            for user_data in r.json().values():
                if user_data:
                    ranking_list.append({
                        'email': user_data.get('email', 'N/A')[:20],
                        'lucro_total': round(user_data.get('lucro_total', 0), 2),
                        'total_wins': user_data.get('total_wins', 0),
                        'total_losses': user_data.get('total_losses', 0),
                        'taxa': round((user_data.get('total_wins', 0) / max(user_data.get('total_ciclos', 1), 1)) * 100, 1)
                    })
    except:
        pass
    ranking_list.sort(key=lambda x: x['lucro_total'], reverse=True)
    return jsonify({'ranking': ranking_list[:20], 'stats': {'total_usuarios': len(ranking_list)}})

@app.route('/relatorio')
def relatorio():
    email = request.args.get('email', '')
    if not email:
        return jsonify({'erro': 'Email obrigatorio'})
    u = carregar_usuario(email)
    return jsonify(u if u else {'erro': 'Nao encontrado'})

@app.route('/resetar', methods=['POST'])
def resetar():
    email = request.json.get('email', '')
    if not email:
        return jsonify({'ok': False, 'msg': 'Email obrigatorio'})
    u = carregar_usuario(email)
    if not u:
        return jsonify({'ok': False, 'msg': 'Usuario nao encontrado'})
    
    moedas = u.get('moedas', 0)
    skins = u.get('skins_compradas', ['skin_padrao'])
    skin_atual = u.get('skin_atual', 'skin_padrao')
    
    u.clear()
    u.update({'email': email, 'moedas': moedas, 'moedas_ganhas_hoje': str(datetime.now())[:10],
              'total_ciclos': 0, 'total_wins': 0, 'total_losses': 0, 'total_gasto': 0.0,
              'total_ganho': 0.0, 'lucro_total': 0.0, 'banca_atual': 0.0,
              'data_cadastro': str(datetime.now())[:19], 'historico_operacoes': [], 'dias_ativos': 0,
              'skin_atual': skin_atual, 'skins_compradas': skins, 'estrategias_compradas': []})
    
    for key, est in ESTRATEGIAS.items():
        if est.get('gratis', False):
            u['estrategias_compradas'].append(key)
    
    salvar_usuario(email, u)
    return jsonify({'ok': True, 'msg': 'Resetado!'})

@app.route('/shutdown')
def shutdown():
    import os, signal
    os.kill(os.getpid(), signal.SIGTERM)
    return jsonify({'ok': True})

# ============= CHAT =============
@app.route('/chat_enviar', methods=['POST'])
def chat_enviar():
    data = request.json
    nome = data.get('nome', 'Anonimo')[:15]
    msg = data.get('msg', '')[:200]
    if not msg:
        return jsonify({'ok': False})
    try:
        requests.post(f'{FB_URL}/tesla_369/chat.json', json={'nome': nome, 'msg': msg, 'hora': datetime.now().strftime('%H:%M')}, timeout=5)
        r = requests.get(f'{FB_URL}/tesla_369/chat.json?orderBy="$key"&limitToLast=51', timeout=5)
        if r.status_code == 200 and r.json():
            dados = r.json()
            if len(dados) > 50:
                for chave in sorted(dados.keys())[:-50]:
                    requests.delete(f'{FB_URL}/tesla_369/chat/{chave}.json', timeout=5)
    except:
        pass
    return jsonify({'ok': True})

@app.route('/chat_mensagens')
def chat_mensagens_route():
    try:
        r = requests.get(f'{FB_URL}/tesla_369/chat.json?orderBy="$key"&limitToLast=50', timeout=5)
        mensagens = list(r.json().values()) if r.status_code == 200 and r.json() else []
        return jsonify({'mensagens': mensagens, 'online': 1})
    except:
        return jsonify({'mensagens': [], 'online': 1})

# ============= HTML =============
HTML = r'''<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>TESLA 369</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:{{COR_FUNDO}};color:{{COR_TEXTO}};font-family:monospace;padding:10px}
.container{max-width:950px;margin:0 auto}
.tabs{display:flex;gap:5px;margin-bottom:10px;flex-wrap:wrap}
.tab{padding:10px 14px;background:{{COR_PANEL}};border:1px solid #333;border-radius:10px 10px 0 0;cursor:pointer;color:#888}
.tab.active{background:{{COR_TAB_ATIVA}};color:#000;font-weight:bold}
.panel{display:none;background:{{COR_PANEL}};padding:15px;border-radius:0 10px 10px 10px;border:1px solid #333;margin-bottom:10px}
.panel.active{display:block}
.header{background:{{COR_HEADER_BG}};padding:20px;border-radius:20px;text-align:center;border:3px solid {{COR_HEADER_BORDA}};margin-bottom:15px}
.header h1{color:{{COR_DESTAQUE}}}
.dashboard{display:grid;grid-template-columns:repeat(auto-fit,minmax(100px,1fr));gap:8px;margin-bottom:10px}
.card{background:{{COR_PANEL}};padding:10px;border-radius:10px;border:1px solid #333;text-align:center}
.terminal{background:#000;color:#0f0;padding:12px;border-radius:10px;height:200px;overflow-y:auto;font-size:10px}
.btn{padding:10px 14px;border:none;border-radius:8px;font-weight:bold;cursor:pointer}
.btn-start{background:{{COR_BOTAO}};color:#000}
.btn-stop{background:linear-gradient(135deg,#c00,#f44);color:#fff}
.btn-info{background:linear-gradient(135deg,#06c,#39f);color:#fff}
.status-dot{width:8px;height:8px;border-radius:50%;display:inline-block}
.status-dot.active{background:#0f0;animation:pulse 1s infinite}
.status-dot.inactive{background:#888}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.3}}
.skin-card,.plano-card,.estrategia-card{background:#111;padding:10px;border-radius:10px;border:2px solid #222;text-align:center;cursor:pointer;margin:5px}
.skin-card.ativo,.estrategia-card.ativa{border-color:#0f0}
.sub-tabs{display:flex;gap:5px;margin-bottom:15px}
.sub-tab{padding:8px 16px;background:#111;border:1px solid #333;border-radius:8px 8px 0 0;cursor:pointer;color:#888}
.sub-tab.active{background:{{COR_TAB_ATIVA}};color:#000}
.sub-panel{display:none}
.sub-panel.active{display:block}
.modal-overlay{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.85);z-index:1000;justify-content:center;align-items:center}
.modal-overlay.active{display:flex}
.modal-pagamento{background:{{COR_PANEL}};border:2px solid {{COR_DESTAQUE}};border-radius:15px;padding:25px;max-width:400px;width:90%;text-align:center}
.pix-copiavel{background:#000;color:#0f0;padding:10px;border-radius:8px;word-break:break-all;margin:10px 0;cursor:pointer}
</style>
</head>
<body>
<div class="container">
<div class="header">{{HEADER_EXTRA}}<h1>TESLA 369 BOT</h1></div>
<div class="tabs">
<div class="tab active" onclick="openTab('bot')">BOT</div>
<div class="tab" onclick="openTab('relatorio')">RELATORIO</div>
<div class="tab" onclick="openTab('estrategias')">ESTRATEGIAS</div>
<div class="tab" onclick="openTab('loja')">LOJA</div>
<div class="tab" onclick="openTab('chat')">CHAT</div>
</div>
<div class="panel active" id="panel-bot">
<div><h3>IQ OPTION</h3>
<input type="email" id="email" placeholder="Email" style="padding:8px;margin:5px;width:200px">
<input type="password" id="senha" placeholder="Senha" style="padding:8px;margin:5px;width:150px">
<select id="tipo"><option value="PRACTICE">PRACTICE</option><option value="REAL">REAL</option></select>
<select id="percentualBanca" onchange="atualizarPercentual()" style="padding:5px;margin:5px">
<option value="15">15%</option><option value="20">20%</option><option value="30">30%</option>
</select>
<button class="btn btn-info" id="btnConectar" onclick="conectarIQ()">CONECTAR</button>
<button class="btn btn-start" id="btnOperar" onclick="comecarOperar()" style="display:none">OPERAR</button>
<button class="btn btn-stop" id="btnParar" onclick="pararBot()" style="display:none">PARAR</button>
</div>
<div class="dashboard">
<div class="card"><div class="label">BANCA</div><div class="value" id="banca">--</div></div>
<div class="card"><div class="label">LUCRO</div><div class="value" id="lucro">0</div></div>
<div class="card"><div class="label">VOLTS</div><div class="value" id="moedasSaldo">0</div></div>
<div class="card"><div class="label">SINAL</div><div class="value" id="sinal">--</div></div>
</div>
<div class="terminal" id="terminal">Aguardando...</div>
<div class="barra-status"><span><span class="status-dot inactive" id="statusDot"></span> <span id="statusTexto">Desconectado</span></span></div>
</div>
<div class="panel" id="panel-relatorio">
<div><input type="email" id="emailRelatorio" placeholder="Email"><button class="btn btn-info" onclick="verRelatorio()">BUSCAR</button></div>
<div id="relatorioContent"></div>
</div>
<div class="panel" id="panel-estrategias"><div id="estrategiaGrid"></div></div>
<div class="panel" id="panel-loja">
<div class="sub-tabs">
<div class="sub-tab active" onclick="mostrarSubAba('moedas')">VOLTS</div>
<div class="sub-tab" onclick="mostrarSubAba('skins')">SKINS</div>
<div class="sub-tab" onclick="mostrarSubAba('estrategias')">ESTRATEGIAS</div>
</div>
<div class="sub-panel active" id="sub-panel-moedas"><div id="planosGrid"></div></div>
<div class="sub-panel" id="sub-panel-skins"><div id="skinsGrid"></div></div>
<div class="sub-panel" id="sub-panel-estrategias"><div id="estrategiasLojaGrid"></div></div>
</div>
<div class="panel" id="panel-chat">
<div id="chatMensagens" style="background:#000;border:1px solid #333;border-radius:10px;height:300px;overflow-y:auto;padding:10px;margin-bottom:10px"></div>
<div style="display:flex"><input type="text" id="chatMsg" placeholder="Mensagem..." style="flex:1;padding:10px"><button onclick="enviarChatMsg()" class="btn btn-info">ENVIAR</button></div>
</div>
</div>
<div class="modal-overlay" id="modalPix"><div class="modal-pagamento"><h3>PIX</h3><div id="pixContent"></div><button onclick="fecharModal()">FECHAR</button></div></div>
<script>
var intervalo=null,botAtivo=false,conectadoIQ=false,emailLogado='',pixAtual=null,estrategiaSel='',estrategias={};
function openTab(tab){document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));event.target.classList.add('active');document.getElementById('panel-'+tab).classList.add('active');if(tab=='relatorio'&&emailLogado)verRelatorio();if(tab=='estrategias')renderEstrategias();}
function atualizarPercentual(){var p=document.getElementById('percentualBanca').value;fetch('/set_percentual',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({percentual:parseInt(p)})});}
function conectarIQ(){var e=document.getElementById('email').value.trim();var s=document.getElementById('senha').value.trim();var t=document.getElementById('tipo').value;if(!e||!s){alert('Preencha email e senha!');return}emailLogado=e;document.getElementById('btnConectar').disabled=true;fetch('/conectar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e,senha:s,tipo:t})}).then(r=>r.json()).then(d=>{if(d.ok){conectadoIQ=true;setTimeout(()=>location.reload(),2000);document.getElementById('btnConectar').style.display='none';document.getElementById('btnOperar').style.display='inline-block';document.getElementById('statusTexto').textContent='Conectado';document.getElementById('statusDot').className='status-dot active';document.getElementById('moedasSaldo').textContent=d.moedas||0;if(intervalo)clearInterval(intervalo);intervalo=setInterval(atualizar,2000);atualizar();}else{alert('ERRO: '+d.erro);document.getElementById('btnConectar').disabled=false;}});}
function comecarOperar(){if(!conectadoIQ){alert('Conecte primeiro!');return}document.getElementById('btnOperar').disabled=true;fetch('/comecar_operar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({})}).then(r=>r.json()).then(d=>{if(d.ok){botAtivo=true;document.getElementById('btnOperar').style.display='none';document.getElementById('btnParar').style.display='inline-block';document.getElementById('statusTexto').textContent='Operando';document.getElementById('moedasSaldo').textContent=d.moedas;}else{alert('ERRO: '+d.erro);document.getElementById('btnOperar').disabled=false;}});}
function pararBot(){if(!confirm('Parar?'))return;fetch('/parar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({})}).then(r=>r.json()).then(d=>{botAtivo=false;document.getElementById('btnOperar').style.display='inline-block';document.getElementById('btnOperar').disabled=false;document.getElementById('btnParar').style.display='none';document.getElementById('statusTexto').textContent='Conectado';if(intervalo)clearInterval(intervalo);setTimeout(()=>location.reload(),500);});}
function renderEstrategias(){fetch('/status').then(r=>r.json()).then(d=>{var html='';for(var k in d.estrategias_disponiveis){var e=d.estrategias_disponiveis[k];var comprado=d.estrategias_compradas.includes(k);html+='<div class="estrategia-card'+(k==estrategiaSel?' ativa':'')+'" onclick="selecionarEstrategia(\''+k+'\')"><b>'+e.nome+'</b><br><small>'+e.desc+'</small><br><span style="font-size:10px">'+(comprado?'COMPRADO':(e.preco_moedas==0?'GRATIS':e.preco_moedas+' VOLTS'))+'</span></div>';}document.getElementById('estrategiaGrid').innerHTML=html||'Nenhuma estrategia';});}
function selecionarEstrategia(k){estrategiaSel=k;fetch('/selecionar_estrategia',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({estrategia:k})}).then(()=>renderEstrategias());}
function renderLoja(){fetch('/status').then(r=>r.json()).then(d=>{var skins=d.skins_status||[];var html='';skins.forEach(s=>{html+='<div class="skin-card'+(s.ativo?' ativo':'')+'"><b>'+s.nome+'</b><br>'+s.desc+'<br>'+s.preco_moedas+' VOLTS<br>'+(s.ativo?'<button disabled>EM USO</button>':(s.comprado?'<button onclick="ativarSkin(\''+s.id+'\')">USAR</button>':'<button onclick="comprarSkin(\''+s.id+'\')">COMPRAR</button>'))+'</div>';});document.getElementById('skinsGrid').innerHTML=html;var planos=planos||[];var ph='';[{"id":1,"moedas":1,"preco":0.99,"nome":"TESTE"},{"id":2,"moedas":6,"preco":6.69,"nome":"BASICO"},{"id":3,"moedas":15,"preco":9.99,"nome":"INTERMEDIARIO"},{"id":4,"moedas":36,"preco":21.69,"nome":"PREMIUM"},{"id":5,"moedas":69,"preco":39.69,"nome":"ULTRA"}].forEach(p=>{ph+='<div class="plano-card" onclick="pagarComPix('+p.id+')"><b>'+p.nome+'</b><br>'+p.moedas+' VOLTS<br>R$ '+p.preco.toFixed(2)+'</div>';});document.getElementById('planosGrid').innerHTML=ph;var eh='';for(var k in d.estrategias_disponiveis){var e=d.estrategias_disponiveis[k];var comprado=d.estrategias_compradas.includes(k);eh+='<div class="estrategia-card"><b>'+e.nome+'</b><br>'+e.desc+'<br>'+(e.preco_moedas==0?'GRATIS':e.preco_moedas+' VOLTS')+'<br>'+(comprado?'<button disabled>COMPRADO</button>':'<button onclick="comprarEstrategia(\''+k+'\')">COMPRAR</button>')+'</div>';}document.getElementById('estrategiasLojaGrid').innerHTML=eh;});}
function comprarSkin(id){fetch('/comprar_skin',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({skin_id:id})}).then(r=>r.json()).then(d=>{if(d.ok){alert(d.msg||'Skin comprada!');location.reload();}else{alert('ERRO: '+d.erro);}});}
function ativarSkin(id){fetch('/ativar_skin',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({skin_id:id})}).then(r=>r.json()).then(d=>{if(d.ok){alert('Skin ativada!');location.reload();}});}
function comprarEstrategia(id){fetch('/comprar_estrategia',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({estrategia_id:id})}).then(r=>r.json()).then(d=>{if(d.ok){alert(d.msg);location.reload();}});}
function pagarComPix(id){var e=document.getElementById('emailCompra')?.value||emailLogado;if(!e){alert('Digite seu email!');return}document.getElementById('modalPix').classList.add('active');fetch('/criar_pix',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e,plano_id:id})}).then(r=>r.json()).then(d=>{if(d.sucesso){pixAtual=d;var h='<p>R$ '+d.valor+'</p><p>'+d.moedas+' VOLTS</p>';if(d.qr_code)h+='<div class="pix-copiavel" onclick="copiarPix()">'+d.qr_code+'</div>';h+='<button onclick="verificarPagamento(\''+d.pix_id+'\')">VERIFICAR</button>';document.getElementById('pixContent').innerHTML=h;}else{document.getElementById('pixContent').innerHTML='<p>Erro: '+d.erro+'</p>';}});}
function copiarPix(){navigator.clipboard.writeText(pixAtual.qr_code).then(()=>alert('Copiado!'));}
function verificarPagamento(id){fetch('/verificar_pix',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({pix_id:id})}).then(r=>r.json()).then(d=>{if(d.pago){alert('PAGO! +'+d.moedas+' VOLTS!');location.reload();}else{alert('Ainda nao confirmado');}});}
function fecharModal(){document.getElementById('modalPix').classList.remove('active');}
function verRelatorio(){var e=document.getElementById('emailRelatorio').value;if(!e){alert('Digite o email!');return}fetch('/relatorio?email='+e).then(r=>r.json()).then(d=>{var h='';h+='<div>VOLTS: '+(d.moedas||0)+'</div>';h+='<div>LUCRO: R$ '+(d.lucro_total||0).toFixed(2)+'</div>';h+='<div>WINS: '+(d.total_wins||0)+'</div>';h+='<div>LOSS: '+(d.total_losses||0)+'</div>';document.getElementById('relatorioContent').innerHTML=h;});}
function atualizar(){fetch('/status').then(r=>r.json()).then(d=>{if(!d.conectado&&conectadoIQ){conectadoIQ=false;botAtivo=false;location.reload();}if(!d.rodando&&botAtivo){botAtivo=false;document.getElementById('btnOperar').style.display='inline-block';document.getElementById('btnParar').style.display='none';}if(d.banca)document.getElementById('banca').textContent='$'+d.banca.toFixed(2);if(d.lucro!==undefined)document.getElementById('lucro').textContent='$'+d.lucro.toFixed(2);if(d.moedas!==undefined)document.getElementById('moedasSaldo').textContent=d.moedas;if(d.sinal)document.getElementById('sinal').textContent=d.sinal;if(d.logs)document.getElementById('terminal').innerHTML=d.logs;if(d.estrategias_disponiveis)estrategias=d.estrategias_disponiveis;if(d.estrategia)estrategiaSel=d.estrategia;renderEstrategias();});}
function mostrarSubAba(aba){document.querySelectorAll('.sub-tab').forEach(t=>t.classList.remove('active'));document.querySelectorAll('.sub-panel').forEach(p=>p.classList.remove('active'));document.querySelector(`.sub-tab[onclick="mostrarSubAba('${aba}')"]`).classList.add('active');document.getElementById(`sub-panel-${aba}`).classList.add('active');if(aba=='skins'||aba=='estrategias')renderLoja();}
function enviarChatMsg(){var n=emailLogado||'Anonimo';var m=document.getElementById('chatMsg').value;if(!m)return;fetch('/chat_enviar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({nome:n,msg:m})}).then(()=>{document.getElementById('chatMsg').value='';atualizarChat();});}
function atualizarChat(){fetch('/chat_mensagens').then(r=>r.json()).then(d=>{var h='';(d.mensagens||[]).forEach(m=>{h+='<div><b>'+m.nome+'</b> '+m.hora+'<br>'+m.msg+'</div><hr>';});document.getElementById('chatMensagens').innerHTML=h||'Nenhuma mensagem';});}
window.onload=function(){fetch('/status').then(r=>r.json()).then(d=>{if(d.estrategias_disponiveis)estrategias=d.estrategias_disponiveis;if(d.estrategia)estrategiaSel=d.estrategia;renderEstrategias();if(d.conectado&&d.email){conectadoIQ=true;emailLogado=d.email;document.getElementById('email').value=d.email;document.getElementById('btnConectar').style.display='none';document.getElementById('btnOperar').style.display=d.rodando?'none':'inline-block';document.getElementById('btnParar').style.display=d.rodando?'inline-block':'none';document.getElementById('statusTexto').textContent=d.rodando?'Operando':'Conectado';document.getElementById('statusDot').className='status-dot active';document.getElementById('moedasSaldo').textContent=d.moedas||0;if(intervalo)clearInterval(intervalo);intervalo=setInterval(atualizar,2000);atualizar();}});setInterval(atualizarChat,3000);};
</script>
</body>
</html>'''

if __name__ == '__main__':
    print("="*50)
    print("TESLA 369 BOT v7.0.3 - MODULAR")
    print("="*50)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
