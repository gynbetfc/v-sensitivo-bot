# ◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈
# ☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿
# ⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗
#    🌀  O DINHEIRO VEM ATÉ MIM DE TODOS OS LADOS  🌀
#         DE FORMA ABUNDANTE, CONTÍNUA E PRÓSPERA
# ⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗
# ◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈
# VS.PY ORIGINAL + HTML NOVO + DRIVE + MOEDAS + MERCADO PAGO
# ◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈

from flask import Flask, render_template_string, jsonify, request
from iqoptionapi.stable_api import IQ_Option
from datetime import datetime
import threading, time, sys, os, json, warnings, requests, uuid

warnings.filterwarnings("ignore")
app = Flask(__name__)

# ============= CONFIGURAÇÕES (ORIGINAIS) =============
TIMEFRAME, MARTINGALE, PAYOUT_PADRAO = 60, 2, 0.85
TIMEOUT_ENTRE_CICLOS, STOP_GAIN_PERCENTUAL = 5, 100

# ============= GOOGLE DRIVE =============
DRIVE_PATH = "/content/drive/MyDrive/vsens_users"
os.makedirs(DRIVE_PATH, exist_ok=True)

# ⭐⭐⭐ CONFIGURAÇÃO DO MERCADO PAGO ⭐⭐⭐
MERCADO_PAGO_ACCESS_TOKEN = "APP_USR-4548266140377032-050311-6589fc22b166e4cb2cfad0379b28dcdf-1059299796"
MERCADO_PAGO_PUBLIC_KEY = "APP_USR-39e1950e-420d-479a-8125-902009ca3445"
MODO_SIMULACAO = False

# ⭐ PLANOS ⭐
PLANOS = [
    {'id':1,'moedas':10,'preco':0.10,'nome':'🧪 TESTES','desc':'1 centavo/moeda','tag':'Mercado Pago'},
    {'id':2,'moedas':30,'preco':30.00,'nome':'💎 BÁSICO','desc':'R$1,00/moeda'},
    {'id':3,'moedas':100,'preco':90.00,'nome':'🔥 PREMIUM','desc':'R$0,90/moeda','desconto':'10% OFF'},
    {'id':4,'moedas':300,'preco':240.00,'nome':'👑 ULTRA','desc':'R$0,80/moeda','desconto':'20% OFF'},
]

def arquivo_usuario(email):
    return f"{DRIVE_PATH}/{email.replace('@','_').replace('.','_')}.json"

def carregar_usuario(email):
    arq=arquivo_usuario(email)
    if os.path.exists(arq): return json.load(open(arq,'r'))
    return None

def salvar_usuario(email,dados):
    with open(arquivo_usuario(email),'w') as f: json.dump(dados,f,indent=2)

def criar_usuario(email):
    return {'email':email,'moedas':1,'moedas_ganhas_hoje':'','total_ciclos':0,'total_wins':0,'total_losses':0,'total_gasto':0.0,'total_ganho':0.0,'lucro_total':0.0,'banca_atual':0.0,'data_cadastro':str(datetime.now())[:19],'historico_operacoes':[],'dias_ativos':{}}

# ============= VARIÁVEIS GLOBAIS =============
API, par = None, "EURUSD-OTC"
lucro, NumDeOperacoes, ULTIMO_CICLO_TIMESTAMP = 0.0, 0, 0
BANCA_INICIAL_DO_BOT, STOP_GAIN_ATINGIDO = 0, False
bot_rodando, bot_thread = False, None
ultimo_sinal, ultima_analise = "Aguardando...", {}
logs_web, MAX_LOGS_WEB = [], 200
email_usuario_atual = ""

pagamentos_pendentes = {}

def add_log(msg, tipo='info'):
    global logs_web
    t=datetime.now().strftime('%H:%M:%S')
    logs_web.append({'time':t,'msg':msg,'tipo':tipo})
    if len(logs_web)>MAX_LOGS_WEB: logs_web=logs_web[-MAX_LOGS_WEB:]
    print(f"{t} - {msg}"); sys.stdout.flush()

def get_logs_html(limite=40):
    html=''
    for log in logs_web[-limite:]:
        cor={'win':'#00ff88','loss':'#ff4444','info':'#00ff88','sensitive':'#ff69b4','indicator':'#ffd700','error':'#ff4444'}.get(log['tipo'],'#00ff88')
        html+=f'<span style="color:#666">{log["time"]}</span> <span style="color:{cor}">{log["msg"]}</span>\n'
    return html or '📡 Aguardando...'

def conectar_api():
    while bot_rodando:
        try:
            if API.check_connect(): return True
        except: pass
        add_log('⏳ Reconectando...','warning'); time.sleep(5)
        try: API.connect()
        except: pass

def Payout(p):
    try: return float(API.get_all_profit()['binary'][p])/100
    except: return PAYOUT_PADRAO

# ═══════════════════════════════════════════════════════
# INDICADORES (ORIGINAIS - NÃO MEXER)
# ═══════════════════════════════════════════════════════
def sma(v,p):
    if len(v)<p: return None
    return round(sum(x['close'] for x in v[-p:])/p,6)

def bollinger(v,p=20,d=2):
    if len(v)<p: return None,None,None
    c=[x['close'] for x in v[-p:]]; m=sum(c)/p; dp=(sum((x-m)**2 for x in c)/p)**0.5
    return round(m+d*dp,6),round(m,6),round(m-d*dp,6)

def rsi(v,p=9):
    if len(v)<p+1: return None
    g,l=[],[]
    for i in range(1,len(v)):
        d=v[i]['close']-v[i-1]['close']; g.append(d if d>0 else 0); l.append(abs(d) if d<0 else 0)
    if sum(l)==0: return 100
    return round(100-(100/(1+sum(g)/sum(l))),2)

def macd(v,r=12,l=26):
    if len(v)<l: return None
    c=[x['close'] for x in v]; er=c[0]; el=c[0]
    for x in c[1:]: er=x*(2/(r+1))+er*(1-2/(r+1)); el=x*(2/(l+1))+el*(1-2/(l+1))
    return round(er-el,8)

def estocastico(v,p=14):
    if len(v)<p: return None
    c=[x['close'] for x in v]; h=[x.get('max',max(x['open'],x['close'])) for x in v]
    l=[x.get('min',min(x['open'],x['close'])) for x in v]; hh,ll=max(h[-p:]),min(l[-p:])
    if hh==ll: return 50
    return round(((c[-1]-ll)/(hh-ll))*100,2)

def sentir_a_vela():
    global ultimo_sinal,ultima_analise
    try:
        s=datetime.now().second
        fase="🌅NASCENDO" if s<20 else ("☀️VIVA" if s<45 else "🌇MORRENDO")
        v=API.get_candles(par,TIMEFRAME,30,time.time())
        if len(v)<20: return None
        rs=rsi(v); m5=sma(v,5); m10=sma(v,10); m20=sma(v,20)
        bs,_,bi=bollinger(v); mc=macd(v); st=estocastico(v); pc=v[-1]['close']
        ultima_analise={'preco':pc,'rsi':rs,'mm5':m5,'mm10':m10,'mm20':m20,'stoch':st,'fase':fase}
        sc=sp=0; sinais=[]
        if m5 and m20:
            if m5>m20: sc+=20; sinais.append("MM5>MM20")
            else: sp+=20; sinais.append("MM5<MM20")
        if m5 and m10:
            if m5>m10: sc+=15; sinais.append("MM5>MM10")
            else: sp+=15; sinais.append("MM5<MM10")
        if rs:
            if rs<30: sc+=25; sinais.append(f"RSI={rs:.0f}↓")
            elif rs>70: sp+=25; sinais.append(f"RSI={rs:.0f}↑")
            elif rs>50: sc+=10
            else: sp+=10
        if bs and bi and pc:
            if pc<=bi*1.01: sc+=20; sinais.append("BB↓")
            elif pc>=bs*0.99: sp+=20; sinais.append("BB↑")
        if mc:
            if mc>0: sc+=15; sinais.append("MACD+")
            else: sp+=15; sinais.append("MACD-")
        if st:
            if st<20: sc+=15; sinais.append(f"E={st:.0f}↓")
            elif st>80: sp+=15; sinais.append(f"E={st:.0f}↑")
        if fase=="🌇MORRENDO":
            cor='V' if v[-1]['open']<v[-1]['close'] else 'R'
            if cor=='V': sp+=10
            else: sc+=10
        add_log(f"🔮{fase} | C={sc} P={sp} | {' '.join(sinais[:3])}",'indicator')
        dif=abs(sc-sp)
        if sc>sp and dif>=15: ultimo_sinal=f"🔮 CALL ({sc}x{sp})"; add_log(f"CALL!",'sensitive'); return 'call'
        if sp>sc and dif>=15: ultimo_sinal=f"🔮 PUT ({sp}x{sc})"; add_log(f"PUT!",'sensitive'); return 'put'
        ultimo_sinal="⏳..."; return None
    except Exception as e: add_log(f"Erro: {e}",'error'); return None

def calcular_entradas(b,p,g):
    bs=b*0.99; e0=bs/sum((1/p)**i for i in range(g+1))
    entradas=[e0]
    for i in range(1,g+1): entradas.append((sum(entradas)+e0)/p)
    ajuste=bs/sum(entradas); entradas=[round(e*ajuste,2) for e in entradas]
    soma=sum(entradas)
    if soma>b: entradas[-1]=round(entradas[-1]-(soma-b)-0.02,2)
    return [max(1,e) for e in entradas]

def pegar_timestamp():
    v=API.get_candles(par,TIMEFRAME,1,time.time())
    return v[0]['from'] if v else 0

def aguardar_inicio_vela():
    add_log("   Aguardando início da vela...",'info')
    while datetime.now().second>5:
        if not bot_rodando: return False
        time.sleep(0.3)
    while True:
        if not bot_rodando: return False
        ts1=pegar_timestamp(); time.sleep(0.5); ts2=pegar_timestamp()
        if ts1==ts2: add_log("   Vela confirmada!",'info'); return True

def aguardar_vela_fechar(ts_entrada):
    add_log(f"   Aguardando vela fechar...",'info')
    while True:
        if not bot_rodando: return False
        try:
            if pegar_timestamp()!=ts_entrada: add_log("   Vela fechou!",'info'); return True
        except: pass
        time.sleep(0.3)

def verificar_resultado(saldo_antes,valor):
    saldo_base=saldo_antes-valor
    try:
        s=API.get_balance(); d=round(s-saldo_base,2)
        if d>=1.0: return d
    except: pass
    return -valor

def executar_ciclo(direcao):
    global lucro, NumDeOperacoes, ULTIMO_CICLO_TIMESTAMP, STOP_GAIN_ATINGIDO, bot_rodando
    
    if email_usuario_atual:
        u = carregar_usuario(email_usuario_atual)
        if not u or u.get('moedas', 0) < 1:
            add_log("🪙 Sem moedas! Bot PARADO.", 'error')
            bot_rodando = False
            return
        u['moedas'] -= 1
        u['total_ciclos'] += 1
        salvar_usuario(email_usuario_atual, u)
        add_log(f"🪙 Moeda consumida! Restam: {u['moedas']}", 'info')
    
    bi = API.get_balance()
    entradas = calcular_entradas(bi, Payout(par), MARTINGALE)
    add_log(f"💰 ${bi:.2f} | E1:${entradas[0]:.2f} E2:${entradas[1]:.2f} E3:${entradas[2]:.2f}", 'info')
    
    for i in range(MARTINGALE + 1):
        if not bot_rodando: break
        valor = entradas[i]
        
        if not aguardar_inicio_vela(): break
        
        saldo_antes = API.get_balance()
        if saldo_antes < valor:
            add_log("Saldo insuficiente!", 'error')
            break
        
        print()
        add_log(f"🎯 {'ENTRADA' if i == 0 else f'GALE {i}'}: {direcao.upper()} ${valor:.2f}", 'info')
        
        st, id_ordem = API.buy(valor, par, direcao, 1)
        
        if not st or not id_ordem:
            add_log("Falha na ordem!", 'error')
            break
        
        add_log(f"   Ordem #{id_ordem}", 'info')
        
        time.sleep(0.3)
        ts_real = pegar_timestamp()
        
        if not aguardar_vela_fechar(ts_real): break
        
        res = verificar_resultado(saldo_antes, valor)
        lucro += round(res, 2)
        
        saldo_depois = API.get_balance()
        lucro_liquido = round(saldo_depois - saldo_antes, 2)
        
        if res > 0:
            add_log(f"🌟 WIN! +${lucro_liquido:.2f}", 'win')
            NumDeOperacoes += 1
            u = carregar_usuario(email_usuario_atual)
            if u:
                u['total_wins'] += 1
                u['total_ganho'] += abs(lucro_liquido)
                u['lucro_total'] = u['total_ganho'] - u['total_gasto']
                u['banca_atual'] = round(saldo_depois, 2)
                u['historico_operacoes'].append({
                    'data': str(datetime.now())[:19],
                    'resultado': 'WIN',
                    'valor': valor,
                    'lucro': lucro_liquido
                })
                u['dias_ativos'][str(datetime.now())[:10]] = u['dias_ativos'].get(str(datetime.now())[:10], 0) + 1
                salvar_usuario(email_usuario_atual, u)
            break
        else:
            add_log(f"💀 LOSS! -${valor:.2f}", 'loss')
            u = carregar_usuario(email_usuario_atual)
            if u:
                u['total_losses'] += 1
                u['total_gasto'] += valor
                u['lucro_total'] = u['total_ganho'] - u['total_gasto']
                u['banca_atual'] = round(saldo_depois, 2)
                u['historico_operacoes'].append({
                    'data': str(datetime.now())[:19],
                    'resultado': 'LOSS',
                    'valor': valor,
                    'lucro': -valor
                })
                u['dias_ativos'][str(datetime.now())[:10]] = u['dias_ativos'].get(str(datetime.now())[:10], 0) + 1
                salvar_usuario(email_usuario_atual, u)
            if i < MARTINGALE:
                add_log(f"   GALE {i + 1}...", 'loss')
            else:
                add_log("   CICLO COMPLETO PERDIDO", 'loss')
    
    bf = API.get_balance()
    ULTIMO_CICLO_TIMESTAMP = time.time()
    print()
    add_log("=" * 50, 'info')
    add_log(f"{'LUCRO' if bf > bi else 'PERDA'}: ${abs(bf - bi):.2f} | Banca: ${bf:.2f}", 'info')
    add_log("=" * 50, 'info')
    
    if BANCA_INICIAL_DO_BOT > 0:
        lp = ((bf - BANCA_INICIAL_DO_BOT) / BANCA_INICIAL_DO_BOT) * 100
        if lp >= STOP_GAIN_PERCENTUAL:
            add_log(f"🎯 STOP GAIN! +{lp:.1f}%", 'win')
            STOP_GAIN_ATINGIDO = True

def bot_loop():
    global bot_rodando,BANCA_INICIAL_DO_BOT,lucro,NumDeOperacoes,ULTIMO_CICLO_TIMESTAMP,STOP_GAIN_ATINGIDO
    add_log('🧙‍♂️🔮 v_SENSITIVO - INICIANDO...','sensitive')
    BANCA_INICIAL_DO_BOT=API.get_balance(); ULTIMO_CICLO_TIMESTAMP=0; STOP_GAIN_ATINGIDO=False; lucro=0.0; NumDeOperacoes=0
    add_log(f"📌 {par} | 💰 ${BANCA_INICIAL_DO_BOT:.2f}")
    add_log('🧿 SIGILOS ATIVADOS 🧿','win')
    while bot_rodando:
        try:
            if STOP_GAIN_ATINGIDO: add_log('🎯 STOP GAIN!','win'); break
            if ULTIMO_CICLO_TIMESTAMP:
                if time.time()-ULTIMO_CICLO_TIMESTAMP<TIMEOUT_ENTRE_CICLOS: time.sleep(1); continue
                ULTIMO_CICLO_TIMESTAMP=0
            direcao=sentir_a_vela()
            if direcao: executar_ciclo(direcao)
            time.sleep(0.3)
        except Exception as e: add_log(f"Erro: {e}",'error'); time.sleep(5); conectar_api()

# ═══════════════════════════════════════════════════════
# FUNÇÕES DO MERCADO PAGO
# ═══════════════════════════════════════════════════════

def gerar_pix_mercadopago(email, plano):
    """Gera QR Code PIX via Mercado Pago"""
    if MODO_SIMULACAO:
        pix_id = str(uuid.uuid4())[:8]
        pagamentos_pendentes[pix_id] = {'email': email, 'plano_id': plano['id'], 'moedas': plano['moedas'], 'valor': plano['preco'], 'pago': False, 'criado_em': str(datetime.now())[:19]}
        return {'sucesso': True, 'simulacao': True, 'pix_id': pix_id, 'qr_code': f"[SIMULAÇÃO] PIX de R$ {plano['preco']:.2f} - ID: {pix_id}", 'qr_code_base64': '', 'valor': plano['preco'], 'moedas': plano['moedas']}
    try:
        url = "https://api.mercadopago.com/v1/payments"
        headers = {"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}", "Content-Type": "application/json", "X-Idempotency-Key": str(uuid.uuid4())}
        payment_data = {"transaction_amount": float(plano['preco']), "description": f"VSENSITIVO - {plano['nome']} - {plano['moedas']} moedas", "payment_method_id": "pix", "payer": {"email": email, "first_name": "Cliente", "last_name": "VSensitivo"}}
        response = requests.post(url, json=payment_data, headers=headers)
        data = response.json()
        if response.status_code in [200, 201]:
            pix_id = str(data['id'])
            qr_code = data['point_of_interaction']['transaction_data']['qr_code']
            qr_code_base64 = data['point_of_interaction']['transaction_data']['qr_code_base64']
            pagamentos_pendentes[pix_id] = {'email': email, 'plano_id': plano['id'], 'moedas': plano['moedas'], 'valor': plano['preco'], 'pago': False, 'criado_em': str(datetime.now())[:19]}
            return {'sucesso': True, 'simulacao': False, 'pix_id': pix_id, 'qr_code': qr_code, 'qr_code_base64': qr_code_base64, 'valor': plano['preco'], 'moedas': plano['moedas']}
        return {'sucesso': False, 'erro': data.get('message', 'Erro ao gerar PIX')}
    except Exception as e:
        return {'sucesso': False, 'erro': str(e)}

def verificar_pagamento_mp(pix_id):
    """Verifica pagamento PIX"""
    if MODO_SIMULACAO:
        return pagamentos_pendentes.get(pix_id, {}).get('pago', False)
    try:
        url = f"https://api.mercadopago.com/v1/payments/{pix_id}"
        headers = {"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}"}
        return requests.get(url, headers=headers).json().get('status') == 'approved'
    except:
        return False

# ═══════════════════════════════════════════════════════
# HTML COMPLETO
# ═══════════════════════════════════════════════════════
HTML = r'''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧙‍♂️🔮 v_SENSITIVO</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:#0a0a1a;color:#fff;font-family:'Courier New',monospace;padding:10px}
        .container{max-width:800px;margin:0 auto}
        .tabs{display:flex;gap:5px;margin-bottom:10px}
        .tab{padding:10px 15px;background:#1a1a3e;border:1px solid #333;border-radius:10px 10px 0 0;cursor:pointer;color:#888;font-size:12px}
        .tab.active{background:#9933ff;color:#fff}
        .panel{display:none;background:#1a1a3e;padding:15px;border-radius:0 10px 10px 10px;border:1px solid #333;margin-bottom:10px}
        .panel.active{display:block}
        .header{background:linear-gradient(135deg,#0d001a,#1a0033,#2d0055,#1a0033,#0d001a);padding:20px;border-radius:20px;text-align:center;border:3px solid #9933ff;position:relative;overflow:hidden;margin-bottom:15px}
        .crystal-ball{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:150px;height:150px;background:radial-gradient(circle at 30% 30%,rgba(200,150,255,0.3) 0%,rgba(153,51,255,0.15) 30%,transparent 100%);border-radius:50%;z-index:0;animation:crystalGlow 4s ease-in-out infinite;pointer-events:none}
        @keyframes crystalGlow{0%,100%{box-shadow:0 0 30px rgba(153,51,255,0.3)}50%{box-shadow:0 0 50px rgba(200,100,255,0.5)}}
        .crystal-ball::after{content:'🔮';position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:50px;animation:floatCrystal 3s ease-in-out infinite}
        @keyframes floatCrystal{0%,100%{transform:translate(-50%,-50%) scale(1)}50%{transform:translate(-50%,-60%) scale(1.08)}}
        .header h1{color:#cc66ff;font-size:20px;text-shadow:0 0 30px #9933ff;position:relative;z-index:3}
        .header p{color:#ffd700;font-size:10px;position:relative;z-index:3}
        .mantra{color:#ffd700;text-align:center;margin:8px 0;font-size:10px}
        .config-section{margin-bottom:12px}
        .config-section h3{color:#cc66ff;margin-bottom:8px;font-size:13px;border-bottom:1px solid #333;padding-bottom:5px}
        .config-row{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:8px}
        .config-row label{color:#888;font-size:11px}
        .config-row select,.config-row input{padding:8px;background:#111;border:1px solid #333;border-radius:8px;color:#fff;font-size:11px;font-family:'Courier New',monospace}
        .slider-group{display:flex;align-items:center;gap:6px}
        .slider-group input[type=range]{width:90px;accent-color:#9933ff}
        .slider-val{color:#ffd700;font-weight:bold;min-width:38px;text-align:center;font-size:13px}
        .btn{padding:10px 16px;border:none;border-radius:8px;font-weight:bold;cursor:pointer;font-size:12px;font-family:'Courier New',monospace}
        .btn-start{background:linear-gradient(135deg,#6600cc,#9933ff);color:#fff}
        .btn-stop{background:linear-gradient(135deg,#cc0000,#ff4444);color:#fff}
        .btn-buy{background:linear-gradient(135deg,#00aa44,#00cc55);color:#fff;width:100%;padding:12px;font-size:14px}
        .btn-info{background:linear-gradient(135deg,#0066cc,#3399ff);color:#fff;font-size:11px;padding:8px 14px}
        .btn-reset{background:linear-gradient(135deg,#cc0000,#ff6600);color:#fff;font-size:11px;padding:8px 14px}
        .dashboard{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px;margin-bottom:10px}
        .card{background:#1a1a3e;padding:10px;border-radius:10px;border:1px solid #333;text-align:center}
        .card .label{color:#888;font-size:9px}.card .value{color:#ffd700;font-size:15px;font-weight:bold;margin-top:4px}
        .indicators{display:grid;grid-template-columns:repeat(auto-fit,minmax(80px,1fr));gap:6px;margin-bottom:10px}
        .ind-card{background:#111;padding:6px;border-radius:8px;border:1px solid #222;text-align:center;font-size:10px}
        .ind-card .ind-label{color:#666;font-size:9px}.ind-card .ind-value{color:#ffd700;font-size:11px}
        .terminal{background:#000;color:#00ff88;padding:12px;border-radius:10px;height:200px;overflow-y:auto;font-size:10px;line-height:1.4;white-space:pre-wrap;border:1px solid #333}
        .barra-status{display:flex;justify-content:space-between;padding:8px;background:#1a1a3e;border-radius:10px;margin-top:10px;font-size:10px}
        .status-dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:4px}
        .status-dot.active{background:#00ff88;animation:pulse 1s infinite}.status-dot.inactive{background:#888}
        @keyframes pulse{0%,100%{opacity:1}50%{opacity:0.3}}
        .planos-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:8px}
        .plano-card{background:#111;padding:12px;border-radius:10px;border:2px solid #222;text-align:center;cursor:pointer;transition:all 0.3s ease}
        .plano-card:hover{border-color:#9933ff;background:#1a1a2e}
        .plano-card.selecionado{border-color:#ffd700;box-shadow:0 0 20px rgba(255,215,0,0.4);background:#1a1a2e}
        .plano-moedas{font-size:24px;color:#ffd700;font-weight:bold}
        .plano-preco{font-size:14px;color:#00ff88;margin:5px 0}
        .plano-desc{font-size:9px;color:#888;margin-top:4px}
        .plano-tag{background:#9933ff22;color:#cc66ff;font-size:9px;padding:2px 8px;border-radius:10px;display:inline-block;margin-top:4px}
        .plano-desconto{background:#ff4444;color:#fff;font-size:9px;padding:2px 6px;border-radius:10px;display:inline-block;margin-left:4px}
        .modal-overlay{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.85);z-index:1000;justify-content:center;align-items:center}
        .modal-overlay.active{display:flex}
        .modal-pagamento{background:#1a1a3e;border:2px solid #9933ff;border-radius:15px;padding:25px;max-width:400px;width:90%;text-align:center}
        .modal-pagamento h3{color:#ffd700;margin-bottom:15px}
        .pix-qrcode{background:#fff;padding:15px;border-radius:10px;display:inline-block;margin:10px 0}
        .pix-qrcode img{max-width:200px}
        .pix-copiavel{background:#000;color:#00ff88;padding:10px;border-radius:8px;font-size:9px;word-break:break-all;margin:10px 0;max-height:60px;overflow-y:auto;cursor:pointer}
        .btn-fechar{background:#444;color:#fff;padding:8px 20px;border-radius:8px;cursor:pointer;margin-top:10px;border:none;font-family:'Courier New',monospace}
        .btn-confirmar{background:#ffd700;color:#000;padding:8px 20px;border-radius:8px;cursor:pointer;margin-top:10px;font-weight:bold;border:none;font-family:'Courier New',monospace}
        .relatorio-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:6px}
        .relatorio-card{background:#111;padding:8px;border-radius:8px;border:1px solid #222;text-align:center}
        .relatorio-card .rlabel{color:#666;font-size:9px}.relatorio-card .rvalue{color:#ffd700;font-size:14px;font-weight:bold}
        .historico-table{width:100%;font-size:9px;border-collapse:collapse;margin-top:10px}
        .historico-table th{background:#9933ff;padding:4px}.historico-table td{padding:3px;border-bottom:1px solid #222;text-align:center}
    </style>
</head>
<body>
<div class="container">
    <div class="header"><div class="crystal-ball"></div><h1>🧙‍♂️🔮 v_SENSITIVO 🔮🧙‍♀️</h1><p>📊 RSI + MM + Bollinger + MACD + Estocástico</p><p>🔮 O BOT QUE SENTE NASCIMENTO, VIDA E MORTE DA VELA</p></div>
    <div class="mantra">🌀 O DINHEIRO VEM ATÉ MIM DE TODOS OS LADOS 🌀</div>
    <div class="tabs"><div class="tab active" onclick="openTab('bot')">🤖 BOT</div><div class="tab" onclick="openTab('moedas')">💸 COMPRAR MOEDAS</div><div class="tab" onclick="openTab('relatorio')">📊 RELATÓRIO</div></div>
    <div class="panel active" id="panel-bot">
        <div class="config-section"><h3>⚙️ CONFIGURAÇÕES</h3><div class="config-row">
            <label>🔄 Gales:<select id="galesSelect"><option value="0">1 entrada (sem gale)</option><option value="1">2 entradas (1 gale)</option><option value="2" selected>3 entradas (2 gales)</option><option value="3">4 entradas (3 gales)</option><option value="4">5 entradas (4 gales)</option></select></label>
            <div class="slider-group"><span style="color:#888;font-size:10px">🎯 Stop Gain:</span><input type="range" id="stopGainSlider" min="2" max="500" value="100" oninput="document.getElementById('stopGainVal').textContent=this.value+'%'"><span class="slider-val" id="stopGainVal">100%</span></div>
        </div></div>
        <div class="config-section"><h3>🔐 IQ OPTION</h3><div class="config-row"><input type="email" id="email" placeholder="📧 Email IQ Option" style="flex:2"><input type="password" id="senha" placeholder="🔒 Senha" style="flex:1"><select id="tipo"><option value="PRACTICE">🧪</option><option value="REAL">💰</option></select><button class="btn btn-start" id="btnConectar" onclick="iniciarBot()">🚀 ATIVAR</button><button class="btn btn-stop" id="btnParar" onclick="pararBot()" style="display:none">⏹️ PARAR</button></div></div>
        <div class="dashboard"><div class="card"><div class="label">💰 BANCA</div><div class="value green" id="banca">--</div></div><div class="card"><div class="label">📈 LUCRO</div><div class="value" id="lucro">$0.00</div></div><div class="card"><div class="label">🎯 OPS</div><div class="value purple" id="ops">0</div></div><div class="card"><div class="label">🪙 MOEDAS</div><div class="value" id="moedasSaldo" style="color:#ffd700">0</div></div><div class="card"><div class="label">🔮 SINAL</div><div class="value" id="sinal" style="font-size:11px;color:#ff69b4">--</div></div></div>
        <div class="indicators"><div class="ind-card"><div class="ind-label">📊 RSI</div><div class="ind-value" id="rsi">--</div></div><div class="ind-card"><div class="ind-label">📈 MM5</div><div class="ind-value" id="mm5">--</div></div><div class="ind-card"><div class="ind-label">📈 MM10</div><div class="ind-value" id="mm10">--</div></div><div class="ind-card"><div class="ind-label">📉 MM20</div><div class="ind-value" id="mm20">--</div></div><div class="ind-card"><div class="ind-label">📊 ESTOC</div><div class="ind-value" id="stoch">--</div></div><div class="ind-card"><div class="ind-label">🌅 FASE</div><div class="ind-value" id="fase">--</div></div><div class="ind-card"><div class="ind-label">💵 PREÇO</div><div class="ind-value" id="preco">--</div></div></div>
        <div class="terminal" id="terminal">📡 Aguardando...</div>
        <div class="barra-status"><span><span class="status-dot inactive" id="statusDot"></span> <span id="statusTexto">⏸️ Parado</span></span><span>⚡ M1 | v_SENSITIVO</span></div>
    </div>
    <div class="panel" id="panel-moedas">
        <div class="config-section"><h3>💳 COMPRAR MOEDAS</h3><p style="color:#888;font-size:10px">📧 <input type="email" id="emailCompra" placeholder="Seu email IQ Option" style="width:220px;padding:6px;background:#111;border:1px solid #333;color:#fff;border-radius:5px"></p><p style="color:#ffd700;font-size:10px;margin-top:5px">🪙 1 moeda = 1 ciclo | Ganhe 1 moeda grátis por dia!</p><p style="color:#888;font-size:9px;margin-top:3px">⭐ Clique no plano para selecionar e pagar com PIX</p></div>
        <div class="planos-grid">''' + ''.join([f'''<div class="plano-card" id="plano{p['id']}" onclick="selecionarPlano({p['id']})"><div style="color:#cc66ff;font-size:11px">{p['nome']}</div><div class="plano-moedas">🪙 {p['moedas']}</div><div class="plano-preco">R$ {p['preco']:.2f}</div><div class="plano-desc">{p.get('desc','')}</div>{f'<div><span class="plano-desconto">{p["desconto"]}</span></div>' if p.get('desconto') else ''}{f'<div class="plano-tag">{p["tag"]}</div>' if p.get('tag') else ''}<button class="btn btn-buy" style="display:none;margin-top:8px;padding:8px" id="btnPlano{p['id']}" onclick="event.stopPropagation();pagarComPix({p['id']})">💳 PAGAR COM PIX</button></div>''' for p in PLANOS]) + r'''</div>
    </div>
    <div class="panel" id="panel-relatorio">
        <div class="config-section"><h3>📊 RELATÓRIO COMPLETO</h3><div class="config-row"><input type="email" id="emailRelatorio" placeholder="Email IQ Option" style="flex:2"><button class="btn btn-info" onclick="verRelatorio()">🔍 BUSCAR</button><button class="btn btn-reset" onclick="resetarRelatorio()">🔄 RESETAR</button></div></div>
        <div id="relatorioContent"></div>
    </div>
</div>

<div class="modal-overlay" id="modalPix">
    <div class="modal-pagamento">
        <h3>💳 Pagamento PIX</h3>
        <div id="pixContent"><p style="color:#888">Carregando QR Code...</p></div>
        <button class="btn-fechar" onclick="fecharModal()">❌ Fechar</button>
    </div>
</div>

<script>
var intervalo=null,botAtivo=false,emailLogado='',planoSelecionado=0,pixAtual=null;
function openTab(tab){document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));event.target.classList.add('active');document.getElementById('panel-'+tab).classList.add('active');if(tab=='relatorio'&&emailLogado){document.getElementById('emailRelatorio').value=emailLogado;verRelatorio()}}
window.onload=function(){fetch('/status').then(r=>r.json()).then(d=>{if(d.rodando&&d.email){botAtivo=true;emailLogado=d.email;document.getElementById('email').value=d.email;document.getElementById('btnConectar').style.display='none';document.getElementById('btnParar').style.display='inline-block';document.getElementById('statusTexto').textContent='🤖 Ativo';document.getElementById('statusDot').className='status-dot active';if(intervalo)clearInterval(intervalo);intervalo=setInterval(atualizar,2000);atualizar()}})}
function iniciarBot(){var email=document.getElementById('email').value.trim();var senha=document.getElementById('senha').value.trim();var tipo=document.getElementById('tipo').value;var gales=parseInt(document.getElementById('galesSelect').value)||2;var stopGain=parseInt(document.getElementById('stopGainSlider').value)||100;if(!email||!senha){alert('Preencha email e senha!');return}emailLogado=email;document.getElementById('btnConectar').disabled=true;document.getElementById('btnConectar').textContent='...';fetch('/iniciar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:email,senha:senha,tipo:tipo,gales:gales,stop_gain:stopGain})}).then(r=>r.json()).then(d=>{if(d.ok){botAtivo=true;document.getElementById('btnConectar').style.display='none';document.getElementById('btnParar').style.display='inline-block';document.getElementById('statusTexto').textContent='🤖 Ativo';document.getElementById('statusDot').className='status-dot active';if(intervalo)clearInterval(intervalo);intervalo=setInterval(atualizar,2000)}else{alert('ERRO: '+d.erro);document.getElementById('btnConectar').disabled=false;document.getElementById('btnConectar').textContent='🚀 ATIVAR'}})}
function pararBot(){if(!confirm('Parar?'))return;fetch('/parar',{method:'POST'}).then(r=>r.json()).then(d=>{botAtivo=false;document.getElementById('btnConectar').style.display='inline-block';document.getElementById('btnParar').style.display='none';document.getElementById('btnConectar').disabled=false;document.getElementById('btnConectar').textContent='🚀 ATIVAR';document.getElementById('statusTexto').textContent='⏸️ Parado';document.getElementById('statusDot').className='status-dot inactive';if(intervalo)clearInterval(intervalo)})}
function selecionarPlano(id){
    document.querySelectorAll('.plano-card').forEach(c=>c.classList.remove('selecionado'));
    document.querySelectorAll('[id^="btnPlano"]').forEach(b=>b.style.display='none');
    var card=document.getElementById('plano'+id);
    card.classList.add('selecionado');
    document.getElementById('btnPlano'+id).style.display='block';
    planoSelecionado=id;
}
function pagarComPix(planoId){
    var email=document.getElementById('emailCompra').value.trim()||emailLogado;
    if(!email){alert('Digite seu email!');return}
    document.getElementById('modalPix').classList.add('active');
    document.getElementById('pixContent').innerHTML='<p style="color:#ffd700">Gerando QR Code PIX...</p>';
    fetch('/criar_pix',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:email,plano_id:planoId})})
    .then(r=>r.json())
    .then(d=>{
        if(d.sucesso){
            pixAtual=d;
            var html='<p style="font-size:18px;color:#ffd700">R$ '+d.valor.toFixed(2)+'</p>';
            html+='<p style="color:#00ff88">🪙 '+d.moedas+' moedas</p>';
            if(d.qr_code_base64){
                html+='<div class="pix-qrcode"><img src="data:image/png;base64,'+d.qr_code_base64+'" alt="QR Code PIX"></div>';
            }
            if(d.qr_code){
                html+='<p style="color:#888;font-size:10px;margin-top:8px">📋 Copie o código PIX:</p>';
                html+='<div class="pix-copiavel" onclick="copiarPix()">'+d.qr_code+'</div>';
                html+='<p style="color:#888;font-size:9px;margin-top:5px">Clique no código para copiar</p>';
            }
            html+='<p style="color:#888;font-size:10px;margin-top:10px">Apos pagar, clique em verificar</p>';
            html+='<button class="btn-confirmar" onclick="verificarPagamento(\''+d.pix_id+'\')">🔄 VERIFICAR PAGAMENTO</button>';
            document.getElementById('pixContent').innerHTML=html;
        }else{
            document.getElementById('pixContent').innerHTML='<p style="color:#ff4444">Erro: '+(d.erro||'Falha ao gerar PIX')+'</p>';
        }
    });
}
function copiarPix(){
    navigator.clipboard.writeText(pixAtual.qr_code).then(()=>alert('Codigo PIX copiado! Cole no seu banco para pagar.'));
}
function verificarPagamento(pixId){
    fetch('/verificar_pix',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({pix_id:pixId})})
    .then(r=>r.json())
    .then(d=>{
        if(d.pago){
            alert('PAGO! '+d.moedas+' moedas adicionadas!');
            document.getElementById('moedasSaldo').textContent=d.saldo;
            fecharModal();
            document.querySelectorAll('.plano-card').forEach(c=>c.classList.remove('selecionado'));
            document.querySelectorAll('[id^="btnPlano"]').forEach(b=>b.style.display='none');
        }else{
            alert('Pagamento ainda nao confirmado. Tente novamente em alguns segundos.');
        }
    });
}
function fecharModal(){
    document.getElementById('modalPix').classList.remove('active');
    pixAtual=null;
}
function verRelatorio(){var email=document.getElementById('emailRelatorio').value.trim();if(!email){alert('Digite o email!');return}fetch('/relatorio?email='+email).then(r=>r.json()).then(d=>{if(d.erro){alert(d.erro);return}var h='<div class="relatorio-grid">';h+='<div class="relatorio-card"><div class="rlabel">🪙 MOEDAS</div><div class="rvalue">'+(d.moedas||0)+'</div></div>';h+='<div class="relatorio-card"><div class="rlabel">📈 LUCRO TOTAL</div><div class="rvalue" style="color:'+(d.lucro_total>=0?'#00ff88':'#ff4444')+'">$'+(d.lucro_total||0).toFixed(2)+'</div></div>';h+='<div class="relatorio-card"><div class="rlabel">✅ WINS</div><div class="rvalue" style="color:#00ff88">'+(d.total_wins||0)+'</div></div>';h+='<div class="relatorio-card"><div class="rlabel">❌ LOSSES</div><div class="rvalue" style="color:#ff4444">'+(d.total_losses||0)+'</div></div>';h+='<div class="relatorio-card"><div class="rlabel">🔄 CICLOS</div><div class="rvalue">'+(d.total_ciclos||0)+'</div></div>';h+='<div class="relatorio-card"><div class="rlabel">💵 GASTO</div><div class="rvalue">$'+(d.total_gasto||0).toFixed(2)+'</div></div>';h+='<div class="relatorio-card"><div class="rlabel">💰 GANHO</div><div class="rvalue">$'+(d.total_ganho||0).toFixed(2)+'</div></div>';h+='<div class="relatorio-card"><div class="rlabel">📅 DIAS</div><div class="rvalue">'+Object.keys(d.dias_ativos||{}).length+'</div></div>';h+='<div class="relatorio-card"><div class="rlabel">🎯 TAXA</div><div class="rvalue">'+(d.total_ciclos>0?((d.total_wins/d.total_ciclos)*100).toFixed(1):0)+'%</div></div>';h+='<div class="relatorio-card"><div class="rlabel">💰 BANCA</div><div class="rvalue">$'+(d.banca_atual||0).toFixed(2)+'</div></div>';h+='<div class="relatorio-card"><div class="rlabel">📅 CADASTRO</div><div class="rvalue" style="font-size:10px">'+(d.data_cadastro||'--')+'</div></div>';h+='</div>';if(d.historico_operacoes&&d.historico_operacoes.length>0){h+='<h4 style="margin-top:10px;color:#cc66ff">📋 ÚLTIMAS</h4><table class="historico-table"><tr><th>Data</th><th>Resultado</th><th>Valor</th><th>Lucro</th></tr>';d.historico_operacoes.slice(-15).reverse().forEach(op=>{h+='<tr><td>'+op.data+'</td><td style="color:'+(op.resultado=='WIN'?'#00ff88':'#ff4444')+'">'+op.resultado+'</td><td>$'+op.valor.toFixed(2)+'</td><td style="color:'+(op.lucro>=0?'#00ff88':'#ff4444')+'">$'+op.lucro.toFixed(2)+'</td></tr>'});h+='</table>'}document.getElementById('relatorioContent').innerHTML=h})}
function resetarRelatorio(){var email=document.getElementById('emailRelatorio').value.trim();if(!email){alert('Digite o email!');return}if(!confirm('Resetar?'))return;fetch('/resetar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:email})}).then(r=>r.json()).then(d=>{alert(d.msg);if(d.ok)verRelatorio()})}
function atualizar(){fetch('/status').then(r=>r.json()).then(d=>{if(d.banca)document.getElementById('banca').textContent='$'+d.banca.toFixed(2);if(d.lucro!==undefined){var el=document.getElementById('lucro');el.textContent='$'+d.lucro.toFixed(2);el.style.color=d.lucro>=0?'#00ff88':'#ff4444'}if(d.ops!==undefined)document.getElementById('ops').textContent=d.ops;if(d.moedas!==undefined)document.getElementById('moedasSaldo').textContent=d.moedas;if(d.sinal)document.getElementById('sinal').textContent=d.sinal;if(d.analise){document.getElementById('rsi').textContent=d.analise.rsi?d.analise.rsi.toFixed(1):'--';document.getElementById('mm5').textContent=d.analise.mm5?d.analise.mm5.toFixed(5):'--';document.getElementById('mm10').textContent=d.analise.mm10?d.analise.mm10.toFixed(5):'--';document.getElementById('mm20').textContent=d.analise.mm20?d.analise.mm20.toFixed(5):'--';document.getElementById('stoch').textContent=d.analise.stoch?d.analise.stoch.toFixed(1):'--';document.getElementById('fase').textContent=d.analise.fase||'--';document.getElementById('preco').textContent=d.analise.preco?d.analise.preco.toFixed(5):'--'}if(d.logs)document.getElementById('terminal').innerHTML=d.logs;document.getElementById('terminal').scrollTop=document.getElementById('terminal').scrollHeight})}
</script>
</body>
</html>
'''

# ============= ROTAS =============
@app.route('/')
def index(): return render_template_string(HTML)

@app.route('/status')
def status():
    u=carregar_usuario(email_usuario_atual) if email_usuario_atual else {}
    return jsonify({'rodando':bot_rodando,'email':email_usuario_atual,'banca':API.get_balance() if API else 0,'lucro':lucro,'ops':NumDeOperacoes,'sinal':ultimo_sinal,'analise':ultima_analise,'logs':get_logs_html(40),'moedas':u.get('moedas',0)})

@app.route('/iniciar',methods=['POST'])
def iniciar():
    global API,bot_thread,bot_rodando,lucro,NumDeOperacoes,email_usuario_atual,MARTINGALE,STOP_GAIN_PERCENTUAL
    try:
        d=request.get_json()
        email=d.get('email','').strip(); senha=d.get('senha','').strip(); tipo=d.get('tipo','PRACTICE')
        gales=int(d.get('gales') or 2); stop_gain=int(d.get('stop_gain') or 100)
        gales=max(0,min(4,gales)); stop_gain=max(2,min(500,stop_gain))
        if not email or not senha: return jsonify({'ok':False,'erro':'Email e senha obrigatórios'})
        email_usuario_atual=email
        usuario=carregar_usuario(email)
        if not usuario: usuario=criar_usuario(email); salvar_usuario(email,usuario)
        hoje=str(datetime.now())[:10]
        if usuario.get('moedas_ganhas_hoje')!=hoje:
            usuario['moedas']=usuario.get('moedas',0)+1; usuario['moedas_ganhas_hoje']=hoje; salvar_usuario(email,usuario)
        usuario=carregar_usuario(email)
        MARTINGALE=gales; STOP_GAIN_PERCENTUAL=stop_gain
        add_log('🔌 Conectando...','info')
        API=IQ_Option(email,senha)
        status_conn,reason=API.connect()
        if not status_conn: return jsonify({'ok':False,'erro':str(reason)[:100]})
        API.change_balance(tipo)
        lucro=0.0; NumDeOperacoes=0
        add_log(f'✅ Conectado! ${API.get_balance():.2f} | 🪙 {usuario.get("moedas",0)} moedas','win')
        if not bot_rodando:
            bot_rodando=True; bot_thread=threading.Thread(target=bot_loop,daemon=True); bot_thread.start()
        return jsonify({'ok':True})
    except Exception as e: return jsonify({'ok':False,'erro':str(e)[:100]})

@app.route('/parar',methods=['POST'])
def parar():
    global bot_rodando
    bot_rodando=False; add_log('⏹️ Bot parado','info')
    return jsonify({'ok':True})

@app.route('/criar_pix', methods=['POST'])
def criar_pix():
    d = request.get_json()
    email = d.get('email', '')
    plano_id = int(d.get('plano_id') or 1)
    if not email: return jsonify({'sucesso': False, 'erro': 'Email obrigatório'})
    plano = next((p for p in PLANOS if p['id'] == plano_id), None)
    if not plano: return jsonify({'sucesso': False, 'erro': 'Plano não encontrado'})
    return jsonify(gerar_pix_mercadopago(email, plano))

@app.route('/verificar_pix', methods=['POST'])
def verificar_pix():
    d = request.get_json()
    pix_id = d.get('pix_id', '')
    if not pix_id: return jsonify({'pago': False})
    if verificar_pagamento_mp(pix_id):
        if pix_id in pagamentos_pendentes and not pagamentos_pendentes[pix_id]['pago']:
            pagamentos_pendentes[pix_id]['pago'] = True
            email = pagamentos_pendentes[pix_id]['email']
            moedas = pagamentos_pendentes[pix_id]['moedas']
            usuario = carregar_usuario(email) or criar_usuario(email)
            usuario['moedas'] = usuario.get('moedas', 0) + moedas
            salvar_usuario(email, usuario)
            return jsonify({'pago': True, 'moedas': moedas, 'saldo': usuario['moedas']})
        return jsonify({'pago': True})
    return jsonify({'pago': False})

@app.route('/comprar_moedas',methods=['POST'])
def comprar_moedas():
    d=request.get_json(); email=d.get('email',''); plano_id=int(d.get('plano_id') or 1)
    plano=next((p for p in PLANOS if p['id']==plano_id),PLANOS[0])
    if not email: return jsonify({'msg':'Email obrigatório','saldo':0})
    usuario=carregar_usuario(email) or criar_usuario(email)
    usuario['moedas']=usuario.get('moedas',0)+plano['moedas']
    salvar_usuario(email,usuario)
    return jsonify({'msg':f'✅ {plano["moedas"]} moedas!','saldo':usuario['moedas']})

@app.route('/relatorio')
def relatorio():
    email=request.args.get('email','')
    if not email: return jsonify({'erro':'Email obrigatório'})
    u=carregar_usuario(email)
    return jsonify(u if u else {'erro':'Não encontrado'})

@app.route('/resetar', methods=['POST'])
def resetar():
    d = request.get_json()
    email = d.get('email', '')
    if not email: return jsonify({'ok': False, 'msg': 'Email obrigatório'})
    usuario = criar_usuario(email)
    usuario['moedas_ganhas_hoje'] = str(datetime.now())[:10]
    usuario['moedas'] = 0
    salvar_usuario(email, usuario)
    return jsonify({'ok': True, 'msg': '✅ Resetado!'})

if __name__=='__main__':
    app.run(host='0.0.0.0',port=5000,debug=False,threaded=True)