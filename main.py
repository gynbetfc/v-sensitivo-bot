
# TESLA 369 BOT - COMPLETO
from flask import Flask, render_template_string, jsonify, request
from iqoptionapi.stable_api import IQ_Option
from datetime import datetime
import threading, time, sys, os, json, warnings, requests, uuid

warnings.filterwarnings("ignore")
app = Flask(__name__)

MARTINGALE = 2
PAYOUT_PADRAO = 0.85
DB_PATH = "vsens_users"
os.makedirs(DB_PATH, exist_ok=True)

MERCADO_PAGO_ACCESS_TOKEN = "APP_USR-4548266140377032-050311-6589fc22b166e4cb2cfad0379b28dcdf-1059299796"
MERCADO_PAGO_PUBLIC_KEY = "APP_USR-39e1950e-420d-479a-8125-902009ca3445"
MODO_SIMULACAO = False

PLANOS = [
    {'id':1,'moedas':1,'preco':0.99,'nome':'INICIANTE','desc':'R$0,99/moeda','tag':'1 por 1'},
    {'id':2,'moedas':5,'preco':4.99,'nome':'BASICO','desc':'R$1,00/moeda'},
    {'id':3,'moedas':15,'preco':9.99,'nome':'INTERMEDIARIO','desc':'R$0,67/moeda','desconto':'33% OFF'},
    {'id':4,'moedas':35,'preco':14.99,'nome':'PREMIUM','desc':'R$0,43/moeda','desconto':'57% OFF'},
    {'id':5,'moedas':60,'preco':19.99,'nome':'ULTRA','desc':'R$0,33/moeda','desconto':'67% OFF'},
]

SKINS = [
    {
        'id': 'skin_padrao',
        'nome': 'TESLA PADRAO',
        'desc': 'Tema escuro com raios dourados',
        'preco_moedas': 0,
        'cor_fundo': '#0a0a1a',
        'cor_panel': '#1a1a3e',
        'cor_destaque': '#ffd700',
        'cor_texto': '#fff',
        'cor_botao': 'linear-gradient(135deg,#cc8800,#ffd700)',
        'cor_tab_ativa': '#ffd700',
        'cor_header_bg': 'linear-gradient(135deg,#1a0000,#331100,#553300,#331100,#1a0000)',
        'cor_header_borda': '#ffd700',
        'header_extra': '<div class="lightning"></div>',
        'css_extra': '.lightning{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:150px;height:150px;background:radial-gradient(circle at 30% 30%,rgba(255,215,0,0.3) 0%,rgba(255,165,0,0.15) 30%,transparent 100%);border-radius:50%;z-index:0;animation:glow 3s ease-in-out infinite;pointer-events:none}@keyframes glow{0%,100%{box-shadow:0 0 30px rgba(255,215,0,0.3)}50%{box-shadow:0 0 50px rgba(255,165,0,0.5)}}.lightning::after{content:"⚡";position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:50px;animation:float 2s ease-in-out infinite}@keyframes float{0%,100%{transform:translate(-50%,-50%) scale(1)}50%{transform:translate(-50%,-60%) scale(1.1)}}'
    },
    {
        'id': 'skin_magos',
        'nome': 'MAGOS DA BOLA DE CRISTAL',
        'desc': 'Tema roxo mistico',
        'preco_moedas': 1,
        'cor_fundo': '#0a0a1a',
        'cor_panel': '#1a1a3e',
        'cor_destaque': '#cc66ff',
        'cor_texto': '#e0d0ff',
        'cor_botao': 'linear-gradient(135deg,#6600cc,#9933ff)',
        'cor_tab_ativa': '#9933ff',
        'cor_header_bg': 'linear-gradient(135deg,#0d001a,#1a0033,#2d0055,#1a0033,#0d001a)',
        'cor_header_borda': '#9933ff',
        'header_extra': '<div class="crystal-ball"></div><div class="mago mago-esq">🧙‍♂️</div><div class="mago mago-dir">🧙‍♀️</div>',
        'css_extra': '.crystal-ball{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:130px;height:130px;background:radial-gradient(circle at 30% 30%,rgba(200,150,255,0.4) 0%,rgba(153,51,255,0.2) 30%,transparent 70%);border-radius:50%;z-index:0;animation:crystalGlow 4s ease-in-out infinite;pointer-events:none;border:2px solid rgba(153,51,255,0.3)}@keyframes crystalGlow{0%,100%{box-shadow:0 0 30px rgba(153,51,255,0.4),0 0 60px rgba(153,51,255,0.2)}50%{box-shadow:0 0 50px rgba(200,100,255,0.6),0 0 80px rgba(200,100,255,0.3)}}.crystal-ball::after{content:"🔮";position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:45px;animation:floatCrystal 3s ease-in-out infinite}@keyframes floatCrystal{0%,100%{transform:translate(-50%,-50%) scale(1)}50%{transform:translate(-50%,-60%) scale(1.1)}}.mago{position:absolute;top:50%;font-size:30px;z-index:1;animation:magoFloat 2s ease-in-out infinite;pointer-events:none}.mago-esq{left:15px}.mago-dir{right:15px;animation-delay:0.5s}@keyframes magoFloat{0%,100%{transform:translateY(-50%)}50%{transform:translateY(-60%)}}'
    },
    {
        'id': 'skin_brasil',
        'nome': 'BRASIL',
        'desc': 'Tema verde e amarelo',
        'preco_moedas': 0,
        'cor_fundo': '#001a0a',
        'cor_panel': '#0a2a15',
        'cor_destaque': '#ffd700',
        'cor_texto': '#fff',
        'cor_botao': 'linear-gradient(135deg,#009933,#00cc44)',
        'cor_tab_ativa': '#ffd700',
        'cor_header_bg': 'linear-gradient(135deg,#001a0a,#003315,#004d20,#003315,#001a0a)',
        'cor_header_borda': '#ffd700',
        'header_extra': '<div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:60px;z-index:0;opacity:0.3;pointer-events:none">🇧🇷</div>',
        'css_extra': ''
    }
]

ESTRATEGIAS = {
    'v_sensitivo': {'nome': 'v_SENSITIVE', 'desc': 'RSI + MM + Bollinger + MACD + Estocastico + Fase da Vela', 'timeframe': 60, 'pares': ['EURUSD-OTC', 'EURUSD']},
    'tesla_369': {'nome': 'TESLA-369', 'desc': '6 velas: padrao g-g-g-r-r -> CALL / r-r-r-g-g -> PUT', 'timeframe': 60, 'pares': ['EURUSD-OTC', 'EURUSD']},
    'mhi_filtrado': {'nome': 'MHI-FILTRADO', 'desc': '5 velas + Media Movel + filtro de cor dominante', 'timeframe': 60, 'pares': ['EURUSD-OTC', 'EURUSD']},
}

def arquivo_usuario(email):
    return f"{DB_PATH}/{email.replace('@','_').replace('.','_')}.json"

def carregar_usuario(email):
    arq = arquivo_usuario(email)
    if os.path.exists(arq): return json.load(open(arq,'r'))
    return None

def salvar_usuario(email, dados):
    with open(arquivo_usuario(email),'w') as f: json.dump(dados, f, indent=2)

def criar_usuario(email):
    return {
        'email': email, 'moedas': 1, 'moedas_ganhas_hoje': '',
        'total_ciclos': 0, 'total_wins': 0, 'total_losses': 0,
        'total_gasto': 0.0, 'total_ganho': 0.0, 'lucro_total': 0.0, 'banca_atual': 0.0,
        'data_cadastro': str(datetime.now())[:19], 'historico_operacoes': [], 'dias_ativos': {},
        'skin_atual': 'skin_padrao', 'skins_compradas': ['skin_padrao']
    }

API, par = None, "EURUSD-OTC"
estrategia_atual = 'v_sensitivo'
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

def add_log(msg, tipo='info'):
    global logs_web
    t = datetime.now().strftime('%H:%M:%S')
    logs_web.append({'time': t, 'msg': msg, 'tipo': tipo})
    if len(logs_web) > MAX_LOGS_WEB: logs_web = logs_web[-MAX_LOGS_WEB:]
    print(f"{t} - {msg}"); sys.stdout.flush()

def get_logs_html(limite=40):
    html = ''
    for log in logs_web[-limite:]:
        cor = {'win': '#00ff88', 'loss': '#ff4444', 'info': '#00ff88', 'sensitive': '#ff69b4', 'indicator': '#ffd700', 'error': '#ff4444'}.get(log['tipo'], '#00ff88')
        html += f'<span style="color:#666">{log["time"]}</span> <span style="color:{cor}">{log["msg"]}</span>\n'
    return html or 'Aguardando...'

def sma(v, p):
    if len(v) < p: return None
    return round(sum(x['close'] for x in v[-p:]) / p, 6)

def bollinger(v, p=20, d=2):
    if len(v) < p: return None, None, None
    c = [x['close'] for x in v[-p:]]
    m = sum(c) / p
    dp = (sum((x-m)**2 for x in c) / p) ** 0.5
    return round(m+d*dp, 6), round(m, 6), round(m-d*dp, 6)

def rsi(v, p=9):
    if len(v) < p+1: return None
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

def estocastico(v, p=14):
    if len(v) < p: return None
    c = [x['close'] for x in v]
    h = [max(x['open'], x['close']) for x in v]
    l = [min(x['open'], x['close']) for x in v]
    hh, ll = max(h[-p:]), min(l[-p:])
    if hh == ll: return 50
    return round(((c[-1] - ll) / (hh - ll)) * 100, 2)

def sentir_a_vela():
    global ultimo_sinal, ultima_analise
    try:
        s = datetime.now().second
        fase = "NASCENDO" if s < 20 else ("VIVA" if s < 45 else "MORRENDO")
        v = API.get_candles(par, timeframe_atual, 30, time.time())
        if len(v) < 20: return None
        rs = rsi(v); m5 = sma(v, 5); m10 = sma(v, 10); m20 = sma(v, 20)
        bs, _, bi = bollinger(v); mc = macd(v); st = estocastico(v); pc = v[-1]['close']
        ultima_analise = {'preco': pc, 'rsi': rs, 'mm5': m5, 'mm10': m10, 'mm20': m20, 'stoch': st, 'fase': fase}
        sc = sp = 0
        if m5 and m20:
            if m5 > m20: sc += 20
            else: sp += 20
        if m5 and m10:
            if m5 > m10: sc += 15
            else: sp += 15
        if rs:
            if rs < 30: sc += 25
            elif rs > 70: sp += 25
            elif rs > 50: sc += 10
            else: sp += 10
        if bs and bi and pc:
            if pc <= bi * 1.01: sc += 20
            elif pc >= bs * 0.99: sp += 20
        if mc:
            if mc > 0: sc += 15
            else: sp += 15
        if st:
            if st < 20: sc += 15
            elif st > 80: sp += 15
        if fase == "MORRENDO":
            cor = 'V' if v[-1]['open'] < v[-1]['close'] else 'R'
            if cor == 'V': sp += 10
            else: sc += 10
        dif = abs(sc - sp)
        if sc > sp and dif >= 15:
            ultimo_sinal = f"CALL ({sc}x{sp})"
            add_log("CALL!", 'sensitive')
            return 'call'
        if sp > sc and dif >= 15:
            ultimo_sinal = f"PUT ({sp}x{sc})"
            add_log("PUT!", 'sensitive')
            return 'put'
        ultimo_sinal = "..."
        return None
    except Exception as e:
        add_log(f"Erro: {e}", 'error')
        return None

def calcular_entradas(b, p, g):
    bs = b * 0.99
    e0 = bs / sum((1/p)**i for i in range(g+1))
    entradas = [e0]
    for i in range(1, g+1): entradas.append((sum(entradas) + e0) / p)
    ajuste = bs / sum(entradas)
    entradas = [round(e * ajuste, 2) for e in entradas]
    soma = sum(entradas)
    if soma > b: entradas[-1] = round(entradas[-1] - (soma - b) - 0.02, 2)
    return [max(1, e) for e in entradas]

def executar_ciclo(direcao):
    global lucro, NumDeOperacoes, STOP_GAIN_ATINGIDO, bot_rodando
    bi = API.get_balance()
    entradas = calcular_entradas(bi, 0.85, MARTINGALE)
    for i in range(MARTINGALE + 1):
        if not bot_rodando: break
        valor = entradas[i]
        saldo_antes = API.get_balance()
        if saldo_antes < valor:
            add_log("Saldo insuficiente!", 'error')
            break
        add_log(f"ENTRADA {i+1}: {direcao.upper()} ${valor:.2f}", 'info')
        st, id_ordem = API.buy(valor, par, direcao, 1)
        if not st or not id_ordem:
            try: st, id_ordem = API.buy_digital_spot(par, valor, direcao, 1)
            except: pass
        if not st or not id_ordem:
            add_log("Falha na ordem!", 'error')
            break
        time.sleep(60)
        saldo_depois = API.get_balance()
        resultado = round(saldo_depois - saldo_antes, 2)
        lucro += resultado
        if resultado > 0:
            add_log(f"WIN! +${resultado:.2f}", 'win')
            NumDeOperacoes += 1
            STOP_GAIN_ATINGIDO = True
            break
        else:
            add_log(f"LOSS! -${valor:.2f}", 'loss')
    bot_rodando = False

def bot_loop():
    global bot_rodando, BANCA_INICIAL_DO_BOT, lucro, NumDeOperacoes, STOP_GAIN_ATINGIDO
    BANCA_INICIAL_DO_BOT = API.get_balance()
    STOP_GAIN_ATINGIDO = False
    lucro = 0.0
    NumDeOperacoes = 0
    add_log('Buscando sinal...', 'info')
    while bot_rodando and not STOP_GAIN_ATINGIDO:
        try:
            direcao = sentir_a_vela()
            if direcao:
                executar_ciclo(direcao)
                break
            time.sleep(0.3)
        except Exception as e:
            add_log(f"Erro: {e}", 'error')
            time.sleep(5)

# HTML SIMPLIFICADO
HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TESLA 369 BOT</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:COR_FUNDO;color:COR_TEXTO;font-family:'Courier New',monospace;padding:10px}
        .container{max-width:800px;margin:0 auto}
        .tabs{display:flex;gap:5px;margin-bottom:10px}
        .tab{padding:10px 14px;background:COR_PANEL;border:1px solid #333;border-radius:10px 10px 0 0;cursor:pointer;color:#888;font-size:11px}
        .tab.active{background:COR_TAB_ATIVA;color:#000;font-weight:bold}
        .panel{display:none;background:COR_PANEL;padding:15px;border-radius:0 10px 10px 10px;border:1px solid #333;margin-bottom:10px}
        .panel.active{display:block}
        .header{background:COR_HEADER_BG;padding:20px;border-radius:20px;text-align:center;border:3px solid COR_HEADER_BORDA;position:relative;overflow:hidden;margin-bottom:15px}
        CSS_EXTRA
        .header h1{color:COR_DESTAQUE;font-size:22px;text-shadow:0 0 30px COR_TAB_ATIVA;position:relative;z-index:3}
        .header p{color:COR_DESTAQUE;font-size:10px;position:relative;z-index:3}
        .btn{padding:10px 14px;border:none;border-radius:8px;font-weight:bold;cursor:pointer;font-size:11px;font-family:'Courier New',monospace}
        .btn-start{background:COR_BOTAO;color:#000}
        .btn-stop{background:linear-gradient(135deg,#cc0000,#ff4444);color:#fff}
        .btn-info{background:linear-gradient(135deg,#0066cc,#3399ff);color:#fff}
        .dashboard{display:grid;grid-template-columns:repeat(auto-fit,minmax(105px,1fr));gap:8px;margin-bottom:10px}
        .card{background:COR_PANEL;padding:10px;border-radius:10px;border:1px solid #333;text-align:center}
        .card .label{color:#888;font-size:9px}.card .value{color:COR_DESTAQUE;font-size:14px;font-weight:bold;margin-top:4px}
        .terminal{background:#000;color:#00ff88;padding:12px;border-radius:10px;height:200px;overflow-y:auto;font-size:10px;line-height:1.4;white-space:pre-wrap;border:1px solid #333}
        .status-dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:4px}
        .status-dot.active{background:#00ff88;animation:pulse 1s infinite}.status-dot.inactive{background:#888}
        @keyframes pulse{0%,100%{opacity:1}50%{opacity:0.3}}
        input,select{padding:8px;background:#111;border:1px solid #333;border-radius:8px;color:#fff;font-size:11px;font-family:'Courier New',monospace;margin:3px}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        HEADER_EXTRA
        <h1>TESLA 369 BOT</h1>
        <p>9 ESTRATEGIAS | GALE 2 | STOP GAIN 1 WIN | LOJA DE SKINS</p>
    </div>
    <div style="color:COR_DESTAQUE;text-align:center;margin:8px 0;font-size:10px">O DINHEIRO VEM ATE MIM DE TODOS OS LADOS</div>
    
    <div class="tabs">
        <div class="tab active" id="tab-bot" onclick="mostrarPainel('bot')">BOT</div>
        <div class="tab" id="tab-moedas" onclick="mostrarPainel('moedas')">MOEDAS</div>
        <div class="tab" id="tab-relatorio" onclick="mostrarPainel('relatorio')">RELATORIO</div>
    </div>
    
    <div class="panel active" id="panel-bot">
        <h3 style="color:COR_DESTAQUE;margin-bottom:8px">IQ OPTION</h3>
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px">
            <input type="email" id="email" placeholder="Email IQ Option" style="flex:2">
            <input type="password" id="senha" placeholder="Senha" style="flex:1">
            <select id="tipo"><option value="PRACTICE">DEMO</option><option value="REAL">REAL</option></select>
            <button class="btn btn-info" id="btnConectar" onclick="conectarIQ()">CONECTAR</button>
            <button class="btn btn-start" id="btnOperar" onclick="comecarOperar()" style="display:none">COMEÇAR OPERAR</button>
            <button class="btn btn-stop" id="btnParar" onclick="pararBot()" style="display:none">PARAR</button>
        </div>
        <div class="dashboard">
            <div class="card"><div class="label">BANCA</div><div class="value" id="banca">--</div></div>
            <div class="card"><div class="label">LUCRO</div><div class="value" id="lucro">$0.00</div></div>
            <div class="card"><div class="label">OPS</div><div class="value" id="ops">0</div></div>
            <div class="card"><div class="label">MOEDAS</div><div class="value" id="moedasSaldo">0</div></div>
            <div class="card"><div class="label">SINAL</div><div class="value" id="sinal" style="font-size:11px">--</div></div>
        </div>
        <div class="terminal" id="terminal">Aguardando...</div>
        <div style="display:flex;justify-content:space-between;padding:8px;background:COR_PANEL;border-radius:10px;margin-top:10px">
            <span><span class="status-dot inactive" id="statusDot"></span> <span id="statusTexto">Desconectado</span></span>
            <span>TESLA 369</span>
        </div>
    </div>
    
    <div class="panel" id="panel-moedas">
        <h3 style="color:COR_DESTAQUE">COMPRAR MOEDAS</h3>
        <p style="color:#888;font-size:10px">1 moeda = 1 ciclo | +1 moeda gratis/dia</p>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:8px;margin-top:10px">
""" + "".join([f'<div style="background:#111;padding:12px;border-radius:10px;text-align:center;border:2px solid #222"><div style="font-size:20px;color:COR_DESTAQUE">{p["moedas"]} moedas</div><div style="color:#00ff88;margin:5px 0">R$ {p["preco"]:.2f}</div><div style="color:#888;font-size:9px">{p["nome"]}</div></div>' for p in PLANOS]) + """
        </div>
    </div>
    
    <div class="panel" id="panel-relatorio">
        <h3 style="color:COR_DESTAQUE">RELATORIO</h3>
        <div style="display:flex;gap:8px;margin-bottom:10px">
            <input type="email" id="emailRelatorio" placeholder="Email" style="flex:2">
            <button class="btn btn-info" onclick="verRelatorio()">BUSCAR</button>
        </div>
        <div id="relatorioContent"></div>
    </div>
</div>

<script>
var intervalo=null,botAtivo=false,conectadoIQ=false,emailLogado='';

function mostrarPainel(p) {
    document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
    document.getElementById('tab-'+p).classList.add('active');
    document.getElementById('panel-'+p).classList.add('active');
}

function conectarIQ(){
    var email=document.getElementById('email').value.trim();
    var senha=document.getElementById('senha').value.trim();
    var tipo=document.getElementById('tipo').value;
    if(!email||!senha){alert('Preencha email e senha!');return}
    emailLogado=email;
    document.getElementById('btnConectar').disabled=true;
    document.getElementById('btnConectar').textContent='...';
    fetch('/conectar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:email,senha:senha,tipo:tipo})})
    .then(r=>r.json()).then(d=>{
        if(d.ok){
            conectadoIQ=true;
            document.getElementById('btnConectar').style.display='none';
            document.getElementById('btnOperar').style.display='inline-block';
            document.getElementById('statusTexto').textContent='Conectado';
            document.getElementById('statusDot').className='status-dot active';
            document.getElementById('moedasSaldo').textContent=d.moedas||0;
            if(intervalo)clearInterval(intervalo);
            intervalo=setInterval(atualizar,2000);
            atualizar();
        }else{alert('ERRO: '+d.erro);document.getElementById('btnConectar').disabled=false;document.getElementById('btnConectar').textContent='CONECTAR';}
    });
}

function comecarOperar(){
    if(!conectadoIQ){alert('Conecte primeiro!');return}
    document.getElementById('btnOperar').disabled=true;
    document.getElementById('btnOperar').textContent='...';
    fetch('/comecar_operar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({})})
    .then(r=>r.json()).then(d=>{
        if(d.ok){
            botAtivo=true;
            document.getElementById('btnOperar').style.display='none';
            document.getElementById('btnParar').style.display='inline-block';
            document.getElementById('statusTexto').textContent='Operando';
            document.getElementById('moedasSaldo').textContent=d.moedas;
        }else{alert('ERRO: '+d.erro);document.getElementById('btnOperar').disabled=false;document.getElementById('btnOperar').textContent='COMEÇAR OPERAR';}
    });
}

function pararBot(){
    if(!confirm('Parar?'))return;
    fetch('/parar',{method:'POST'}).then(r=>r.json()).then(d=>{
        botAtivo=false;conectadoIQ=false;
        document.getElementById('btnConectar').style.display='inline-block';
        document.getElementById('btnOperar').style.display='none';
        document.getElementById('btnParar').style.display='none';
        document.getElementById('btnConectar').disabled=false;
        document.getElementById('btnConectar').textContent='CONECTAR';
        document.getElementById('statusTexto').textContent='Desconectado';
        document.getElementById('statusDot').className='status-dot inactive';
        if(intervalo)clearInterval(intervalo);
    });
}

function verRelatorio(){
    var email=document.getElementById('emailRelatorio').value.trim();
    if(!email){alert('Digite o email!');return}
    fetch('/relatorio?email='+email).then(r=>r.json()).then(d=>{
        if(d.erro){alert(d.erro);return}
        var h='<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:6px">';
        h+='<div style="background:#111;padding:8px;border-radius:8px;text-align:center"><div style="color:#666;font-size:9px">MOEDAS</div><div style="color:#ffd700;font-size:14px">'+(d.moedas||0)+'</div></div>';
        h+='<div style="background:#111;padding:8px;border-radius:8px;text-align:center"><div style="color:#666;font-size:9px">LUCRO</div><div style="color:'+(d.lucro_total>=0?'#00ff88':'#ff4444')+';font-size:14px">$'+(d.lucro_total||0).toFixed(2)+'</div></div>';
        h+='<div style="background:#111;padding:8px;border-radius:8px;text-align:center"><div style="color:#666;font-size:9px">WINS</div><div style="color:#00ff88;font-size:14px">'+(d.total_wins||0)+'</div></div>';
        h+='<div style="background:#111;padding:8px;border-radius:8px;text-align:center"><div style="color:#666;font-size:9px">LOSSES</div><div style="color:#ff4444;font-size:14px">'+(d.total_losses||0)+'</div></div>';
        h+='<div style="background:#111;padding:8px;border-radius:8px;text-align:center"><div style="color:#666;font-size:9px">CICLOS</div><div style="color:#ffd700;font-size:14px">'+(d.total_ciclos||0)+'</div></div>';
        h+='</div>';
        document.getElementById('relatorioContent').innerHTML=h;
    });
}

function atualizar(){
    fetch('/status').then(r=>r.json()).then(d=>{
        if(!d.conectado&&conectadoIQ){
            conectadoIQ=false;botAtivo=false;
            document.getElementById('btnConectar').style.display='inline-block';
            document.getElementById('btnOperar').style.display='none';
            document.getElementById('btnParar').style.display='none';
            document.getElementById('btnConectar').disabled=false;
            document.getElementById('btnConectar').textContent='CONECTAR';
            document.getElementById('statusTexto').textContent='Desconectado';
            document.getElementById('statusDot').className='status-dot inactive';
            if(intervalo)clearInterval(intervalo);
        }
        if(d.banca)document.getElementById('banca').textContent='$'+d.banca.toFixed(2);
        if(d.lucro!==undefined){var el=document.getElementById('lucro');el.textContent='$'+d.lucro.toFixed(2);el.style.color=d.lucro>=0?'#00ff88':'#ff4444';}
        if(d.ops!==undefined)document.getElementById('ops').textContent=d.ops;
        if(d.moedas!==undefined)document.getElementById('moedasSaldo').textContent=d.moedas;
        if(d.sinal)document.getElementById('sinal').textContent=d.sinal;
        if(d.logs){document.getElementById('terminal').innerHTML=d.logs;document.getElementById('terminal').scrollTop=document.getElementById('terminal').scrollHeight;}
    });
}

window.onload=function(){
    fetch('/status').then(r=>r.json()).then(d=>{
        if(d.conectado&&d.email){
            conectadoIQ=true;emailLogado=d.email;
            document.getElementById('email').value=d.email;
            document.getElementById('btnConectar').style.display='none';
            if(d.rodando){botAtivo=true;document.getElementById('btnOperar').style.display='none';document.getElementById('btnParar').style.display='inline-block';document.getElementById('statusTexto').textContent='Operando';}
            else{document.getElementById('btnOperar').style.display='inline-block';document.getElementById('statusTexto').textContent='Conectado';}
            document.getElementById('statusDot').className='status-dot active';
            if(intervalo)clearInterval(intervalo);
            intervalo=setInterval(atualizar,2000);atualizar();
        }
    });
}
</script>
</body>
</html>"""

def processar_html_com_skin():
    skin = next((s for s in SKINS if s['id'] == skin_atual_global), SKINS[0])
    html = HTML
    for key in ['COR_FUNDO','COR_PANEL','COR_DESTAQUE','COR_TEXTO','COR_BOTAO','COR_TAB_ATIVA','COR_HEADER_BG','COR_HEADER_BORDA','CSS_EXTRA','HEADER_EXTRA']:
        html = html.replace(key, skin.get(key.lower(), ''))
    return html

@app.route('/')
def index():
    return render_template_string(processar_html_com_skin())

@app.route('/status')
def status():
    u = carregar_usuario(email_usuario_atual) if email_usuario_atual else {}
    return jsonify({
        'conectado': conectado_iq,
        'rodando': bot_rodando,
        'email': email_usuario_atual,
        'banca': API.get_balance() if API else 0,
        'lucro': lucro,
        'ops': NumDeOperacoes,
        'sinal': ultimo_sinal,
        'analise': ultima_analise,
        'logs': get_logs_html(40),
        'moedas': u.get('moedas', 0) if u else 0,
        'estrategia': estrategia_atual,
        'estrategia_nome': ESTRATEGIAS.get(estrategia_atual, {}).get('nome', '--')
    })

@app.route('/conectar', methods=['POST'])
def conectar():
    global API, email_usuario_atual, conectado_iq
    try:
        d = request.get_json()
        email = d.get('email', '').strip()
        senha = d.get('senha', '').strip()
        tipo = d.get('tipo', 'PRACTICE')
        if not email or not senha:
            return jsonify({'ok': False, 'erro': 'Email e senha obrigatorios'})
        email_usuario_atual = email
        usuario = carregar_usuario(email)
        if not usuario:
            usuario = criar_usuario(email)
            salvar_usuario(email, usuario)
        hoje = str(datetime.now())[:10]
        if usuario.get('moedas_ganhas_hoje') != hoje:
            usuario['moedas'] = usuario.get('moedas', 0) + 1
            usuario['moedas_ganhas_hoje'] = hoje
            salvar_usuario(email, usuario)
        API = IQ_Option(email, senha)
        status_conn, reason = API.connect()
        if not status_conn:
            return jsonify({'ok': False, 'erro': str(reason)[:100]})
        API.change_balance(tipo)
        conectado_iq = True
        return jsonify({'ok': True, 'moedas': usuario.get('moedas', 0)})
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)[:100]})

@app.route('/comecar_operar', methods=['POST'])
def comecar_operar():
    global bot_rodando, bot_thread, lucro, NumDeOperacoes
    try:
        if not conectado_iq:
            return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
        usuario = carregar_usuario(email_usuario_atual)
        if not usuario or usuario.get('moedas', 0) < 1:
            return jsonify({'ok': False, 'erro': 'Sem moedas!'})
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
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)[:100]})

@app.route('/parar', methods=['POST'])
def parar():
    global bot_rodando, conectado_iq
    bot_rodando = False
    conectado_iq = False
    return jsonify({'ok': True})

@app.route('/relatorio')
def relatorio():
    email = request.args.get('email', '')
    if not email: return jsonify({'erro': 'Email obrigatorio'})
    u = carregar_usuario(email)
    return jsonify(u if u else {'erro': 'Nao encontrado'})

@app.route('/resetar', methods=['POST'])
def resetar():
    d = request.get_json()
    email = d.get('email', '')
    if not email: return jsonify({'ok': False, 'msg': 'Email obrigatorio'})
    usuario = criar_usuario(email)
    usuario['moedas_ganhas_hoje'] = str(datetime.now())[:10]
    usuario['moedas'] = 0
    salvar_usuario(email, usuario)
    return jsonify({'ok': True, 'msg': 'Resetado!'})

if __name__ == '__main__':
    print("=" * 50)
    print("TESLA 369 BOT - INICIANDO")
    print("=" * 50)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
