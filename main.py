# ◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈
# ☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿
# ⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗
#    🌀  O DINHEIRO VEM ATÉ MIM DE TODOS OS LADOS  🌀
#         DE FORMA ABUNDANTE, CONTÍNUA E PRÓSPERA
# ⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗
# ◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈
# ⚡ TESLA 369 BOT - COMPLETO v4.1.1.10 ⚡
# 8 ESTRATÉGIAS | LOJA DE SKINS | MERCADO PAGO | RENDER READY
# BD VIA GITHUB API - MOEDA CONSUMIDA AO CLICAR EM "COMEÇAR OPERAR"
# ◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈

from flask import Flask, render_template_string, jsonify, request
from iqoptionapi.stable_api import IQ_Option
from datetime import datetime
import threading, time, sys, os, json, warnings, requests, uuid, base64

warnings.filterwarnings("ignore")
app = Flask(__name__)

# ============= CONFIGURAÇÕES =============
MARTINGALE = 2
PAYOUT_PADRAO = 0.85
DRIVE_PATH = "vsens_users"
os.makedirs(DRIVE_PATH, exist_ok=True)

# ============= MERCADO PAGO =============
MERCADO_PAGO_ACCESS_TOKEN = "APP_USR-4548266140377032-050311-6589fc22b166e4cb2cfad0379b28dcdf-1059299796"
MODO_SIMULACAO = False

# ============= PLANOS =============
PLANOS = [
    {'id':1,'moedas':1,'preco':0.99,'nome':'🔰 INICIANTE','desc':'R$0,99/moeda','tag':'1 por 1'},
    {'id':2,'moedas':5,'preco':4.99,'nome':'⭐ BÁSICO','desc':'R$1,00/moeda'},
    {'id':3,'moedas':15,'preco':9.99,'nome':'💎 INTERMEDIÁRIO','desc':'R$0,67/moeda','desconto':'33% OFF'},
    {'id':4,'moedas':35,'preco':14.99,'nome':'🔥 PREMIUM','desc':'R$0,43/moeda','desconto':'57% OFF'},
    {'id':5,'moedas':60,'preco':19.99,'nome':'👑 ULTRA','desc':'R$0,33/moeda','desconto':'67% OFF'},
]

# ============= SKINS =============
SKINS = [
    {'id':'skin_padrao','nome':'⚡ TESLA PADRÃO','desc':'Tema escuro com raios dourados','preco_moedas':0,'cor_fundo':'#0a0a1a','cor_panel':'#1a1a3e','cor_destaque':'#ffd700','cor_texto':'#fff','cor_botao':'linear-gradient(135deg,#cc8800,#ffd700)','cor_tab_ativa':'#ffd700','cor_header_bg':'linear-gradient(135deg,#1a0000,#331100,#553300,#331100,#1a0000)','cor_header_borda':'#ffd700','header_extra':'<div class="lightning"></div>','css_extra':'.lightning{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:150px;height:150px;background:radial-gradient(circle at 30% 30%,rgba(255,215,0,0.3) 0%,rgba(255,165,0,0.15) 30%,transparent 100%);border-radius:50%;z-index:0;animation:glow 3s ease-in-out infinite;pointer-events:none}@keyframes glow{0%,100%{box-shadow:0 0 30px rgba(255,215,0,0.3)}50%{box-shadow:0 0 50px rgba(255,165,0,0.5)}}.lightning::after{content:"⚡";position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:50px;animation:float 2s ease-in-out infinite}@keyframes float{0%,100%{transform:translate(-50%,-50%) scale(1)}50%{transform:translate(-50%,-60%) scale(1.1)}}'},
    {'id':'skin_magos','nome':'🔮 MAGOS DA BOLA DE CRISTAL','desc':'Tema roxo místico','preco_moedas':1,'cor_fundo':'#0a0a1a','cor_panel':'#1a1a3e','cor_destaque':'#cc66ff','cor_texto':'#e0d0ff','cor_botao':'linear-gradient(135deg,#6600cc,#9933ff)','cor_tab_ativa':'#9933ff','cor_header_bg':'linear-gradient(135deg,#0d001a,#1a0033,#2d0055,#1a0033,#0d001a)','cor_header_borda':'#9933ff','header_extra':'<div class="crystal-ball"></div><div class="mago mago-esq">🧙‍♂️</div><div class="mago mago-dir">🧙‍♀️</div>','css_extra':'.crystal-ball{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:130px;height:130px;background:radial-gradient(circle at 30% 30%,rgba(200,150,255,0.4) 0%,rgba(153,51,255,0.2) 30%,transparent 70%);border-radius:50%;z-index:0;animation:crystalGlow 4s ease-in-out infinite;pointer-events:none;border:2px solid rgba(153,51,255,0.3)}@keyframes crystalGlow{0%,100%{box-shadow:0 0 30px rgba(153,51,255,0.4),0 0 60px rgba(153,51,255,0.2)}50%{box-shadow:0 0 50px rgba(200,100,255,0.6),0 0 80px rgba(200,100,255,0.3)}}.crystal-ball::after{content:"🔮";position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:45px;animation:floatCrystal 3s ease-in-out infinite}@keyframes floatCrystal{0%,100%{transform:translate(-50%,-50%) scale(1)}50%{transform:translate(-50%,-60%) scale(1.1)}}.mago{position:absolute;top:50%;font-size:30px;z-index:1;animation:magoFloat 2s ease-in-out infinite;pointer-events:none}.mago-esq{left:15px}.mago-dir{right:15px;animation-delay:0.5s}@keyframes magoFloat{0%,100%{transform:translateY(-50%)}50%{transform:translateY(-60%)}}'},
    {'id':'skin_brasil','nome':'🇧🇷 BRASIL','desc':'Tema verde e amarelo','preco_moedas':0,'cor_fundo':'#001a0a','cor_panel':'#0a2a15','cor_destaque':'#ffd700','cor_texto':'#fff','cor_botao':'linear-gradient(135deg,#009933,#00cc44)','cor_tab_ativa':'#ffd700','cor_header_bg':'linear-gradient(135deg,#001a0a,#003315,#004d20,#003315,#001a0a)','cor_header_borda':'#ffd700','header_extra':'<div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:60px;z-index:0;opacity:0.3;pointer-events:none">🇧🇷</div>','css_extra':''}
]

# ============= ESTRATÉGIAS (8 - SEM 9:30) =============
ESTRATEGIAS = {
    'v_sensitivo':{'nome':'🔮 v_SENSITIVO','desc':'RSI + MM + Bollinger + MACD + Estocástico + Fase da Vela','timeframe':60,'pares':['EURUSD-OTC','EURUSD']},
    'tesla_369':{'nome':'⚡ TESLA-369','desc':'6 velas: padrão g-g-g-r-r → CALL / r-r-r-g-g → PUT','timeframe':60,'pares':['EURUSD-OTC','EURUSD']},
    'mhi_filtrado':{'nome':'📊 MHI-FILTRADO','desc':'5 velas + Média Móvel + filtro de cor dominante','timeframe':60,'pares':['EURUSD-OTC','EURUSD']},
    'terceira_igual_primeira':{'nome':'3️⃣ 3ª = 1ª','desc':'Opera a cada 5min, seg 55+','timeframe':60,'pares':['EURUSD-OTC','EURUSD']},
    'quadrante_de_7':{'nome':'7️⃣ QUADRANTE DE 7','desc':'7 velas + MM, conta cores','timeframe':60,'pares':['EURUSD-OTC','EURUSD']},
    'fluxo_de_velas':{'nome':'🌊 FLUXO-DE-VELAS','desc':'5 velas mesma cor + MM','timeframe':60,'pares':['EURUSD-OTC','EURUSD']},
    'reversao':{'nome':'🔄 REVERSÃO','desc':'Padrão alternado g-r-g-r-g ou r-g-r-g-r','timeframe':60,'pares':['EURUSD-OTC','EURUSD']},
    'm5':{'nome':'⏰ M5','desc':'Quadrante de velas de 5min','timeframe':300,'pares':['EURUSD-OTC','EURUSD']}
}

# ============= BANCO DE DADOS VIA GITHUB API =============
def salvar_usuario(email, dados):
    """Salva no GitHub via API (funciona no Render!)"""
    try:
        token = os.environ.get("GITHUB_TOKEN", "")
        if token:
            fn = f"dados/{email.replace('@','_').replace('.','_')}.json"
            u = f"https://api.github.com/repos/gynbetfc/v-sensitivo-bot/contents/{fn}"
            h = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
            c = json.dumps(dados, indent=2)
            r = requests.get(u, headers=h)
            p = {"message": f"Update {email}", "content": base64.b64encode(c.encode()).decode(), "branch": "main"}
            if r.status_code == 200: p["sha"] = r.json()["sha"]
            requests.put(u, json=p, headers=h)
    except: pass
    os.makedirs(DRIVE_PATH, exist_ok=True)
    with open(f"{DRIVE_PATH}/{email.replace('@','_').replace('.','_')}.json", 'w') as f:
        json.dump(dados, f, indent=2)

def carregar_usuario(email):
    """Carrega do GitHub ou local"""
    try:
        token = os.environ.get("GITHUB_TOKEN", "")
        if token:
            fn = f"dados/{email.replace('@','_').replace('.','_')}.json"
            u = f"https://api.github.com/repos/gynbetfc/v-sensitivo-bot/contents/{fn}"
            h = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
            r = requests.get(u, headers=h)
            if r.status_code == 200: return json.loads(base64.b64decode(r.json()["content"]).decode())
    except: pass
    arq = f"{DRIVE_PATH}/{email.replace('@','_').replace('.','_')}.json"
    if os.path.exists(arq):
        with open(arq, 'r') as f: return json.load(f)
    return None

def criar_usuario(email):
    dados = {'email':email,'moedas':1,'moedas_ganhas_hoje':str(datetime.now())[:10],'total_ciclos':0,'total_wins':0,'total_losses':0,'total_gasto':0.0,'total_ganho':0.0,'lucro_total':0.0,'banca_atual':0.0,'data_cadastro':str(datetime.now())[:19],'historico_operacoes':[],'dias_ativos':{},'skin_atual':'skin_padrao','skins_compradas':['skin_padrao']}
    salvar_usuario(email, dados)
    return dados

# ============= VARIÁVEIS GLOBAIS =============
API, par = None, "EURUSD-OTC"
estrategia_atual = 'v_sensitivo'
timeframe_atual = 60
lucro, NumDeOperacoes = 0.0, 0
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
    logs_web.append({'time':t,'msg':msg,'tipo':tipo})
    if len(logs_web) > MAX_LOGS_WEB: logs_web = logs_web[-MAX_LOGS_WEB:]
    print(f"{t} - {msg}"); sys.stdout.flush()

def get_logs_html(limite=40):
    html = ''
    for log in logs_web[-limite:]:
        cor = {'win':'#00ff88','loss':'#ff4444','info':'#00ff88','sensitive':'#ff69b4','indicator':'#ffd700','error':'#ff4444'}.get(log['tipo'],'#00ff88')
        html += f'<span style="color:#666">{log["time"]}</span> <span style="color:{cor}">{log["msg"]}</span>\n'
    return html or '📡 Aguardando...'

# ============= INDICADORES =============
def sma(v,p):
    if len(v)<p: return None
    return round(sum(x['close'] for x in v[-p:])/p,6)

def bollinger(v,p=20,d=2):
    if len(v)<p: return None,None,None
    c=[x['close'] for x in v[-p:]]; m=sum(c)/p
    dp=(sum((x-m)**2 for x in c)/p)**0.5
    return round(m+d*dp,6),round(m,6),round(m-d*dp,6)

def rsi(v,p=9):
    if len(v)<p+1: return None
    g,l=[],[]
    for i in range(1,len(v)):
        d=v[i]['close']-v[i-1]['close']
        g.append(d if d>0 else 0); l.append(abs(d) if d<0 else 0)
    if sum(l)==0: return 100
    return round(100-(100/(1+sum(g)/sum(l))),2)

def macd(v,r=12,l=26):
    if len(v)<l: return None
    c=[x['close'] for x in v]; er=c[0]; el=c[0]
    for x in c[1:]:
        er=x*(2/(r+1))+er*(1-2/(r+1))
        el=x*(2/(l+1))+el*(1-2/(l+1))
    return round(er-el,8)

def estocastico(v,p=14):
    if len(v)<p: return None
    c=[x['close'] for x in v]
    h=[max(x['open'],x['close']) for x in v]
    l=[min(x['open'],x['close']) for x in v]
    hh,ll=max(h[-p:]),min(l[-p:])
    if hh==ll: return 50
    return round(((c[-1]-ll)/(hh-ll))*100,2)

# ============= SINAL v_SENSITIVO =============
def sinal_v_sensitivo():
    global ultimo_sinal, ultima_analise
    try:
        s=datetime.now().second
        fase="🌅NASCENDO" if s<20 else ("☀️VIVA" if s<45 else "🌇MORRENDO")
        v=API.get_candles(par,timeframe_atual,30,time.time())
        if len(v)<20: return None
        rs=rsi(v); m5=sma(v,5); m10=sma(v,10); m20=sma(v,20)
        bs,_,bi=bollinger(v); mc=macd(v); st=estocastico(v); pc=v[-1]['close']
        ultima_analise={'preco':pc,'rsi':rs,'mm5':m5,'mm10':m10,'mm20':m20,'stoch':st,'fase':fase}
        sc=sp=0
        if m5 and m20:
            if m5>m20: sc+=20
            else: sp+=20
        if m5 and m10:
            if m5>m10: sc+=15
            else: sp+=15
        if rs:
            if rs<30: sc+=25
            elif rs>70: sp+=25
            elif rs>50: sc+=10
            else: sp+=10
        if bs and bi and pc:
            if pc<=bi*1.01: sc+=20
            elif pc>=bs*0.99: sp+=20
        if mc:
            if mc>0: sc+=15
            else: sp+=15
        if st:
            if st<20: sc+=15
            elif st>80: sp+=15
        if fase=="🌇MORRENDO":
            cor='V' if v[-1]['open']<v[-1]['close'] else 'R'
            if cor=='V': sp+=10
            else: sc+=10
        dif=abs(sc-sp)
        if sc>sp and dif>=15:
            ultimo_sinal=f"🔮 CALL ({sc}x{sp})"
            return 'call'
        if sp>sc and dif>=15:
            ultimo_sinal=f"🔮 PUT ({sp}x{sc})"
            return 'put'
        ultimo_sinal="⏳..."
        return None
    except Exception as e:
        add_log(f"Erro: {e}",'error')
        return None

# ============= EXECUTAR CICLO =============
def calcular_entradas(b,p,g):
    bs=b*0.99; e0=bs/sum((1/p)**i for i in range(g+1))
    entradas=[e0]
    for i in range(1,g+1): entradas.append((sum(entradas)+e0)/p)
    ajuste=bs/sum(entradas); entradas=[round(e*ajuste,2) for e in entradas]
    soma=sum(entradas)
    if soma>b: entradas[-1]=round(entradas[-1]-(soma-b)-0.02,2)
    return [max(1,e) for e in entradas]

def executar_ciclo(direcao):
    global lucro, NumDeOperacoes, bot_rodando
    bi=API.get_balance()
    entradas=calcular_entradas(bi,0.85,MARTINGALE)
    for i in range(MARTINGALE+1):
        if not bot_rodando: break
        valor=entradas[i]
        saldo_antes=API.get_balance()
        if saldo_antes<valor:
            add_log("❌ Saldo insuficiente!",'error')
            break
        add_log(f"🎯 {'ENTRADA' if i==0 else f'GALE {i}'}: {direcao.upper()} ${valor:.2f}",'info')
        st,id_ordem=API.buy(valor,par,direcao,1)
        if not st or not id_ordem:
            try: st,id_ordem=API.buy_digital_spot(par,valor,direcao,1)
            except: pass
        if not st or not id_ordem:
            add_log("❌ Falha na ordem!",'error')
            break
        time.sleep(60)
        saldo_depois=API.get_balance()
        resultado=round(saldo_depois-saldo_antes,2)
        lucro+=resultado
        if resultado>0:
            add_log(f"🌟 WIN! +${resultado:.2f}",'win')
            NumDeOperacoes+=1
            break
        else:
            add_log(f"💀 LOSS! -${valor:.2f}",'loss')
    bot_rodando=False

def bot_loop():
    global bot_rodando, lucro, NumDeOperacoes
    add_log('🔮 Buscando sinal...','info')
    while bot_rodando:
        try:
            direcao=sinal_v_sensitivo()
            if direcao:
                executar_ciclo(direcao)
                break
            time.sleep(0.3)
        except Exception as e:
            add_log(f"Erro: {e}",'error')
            time.sleep(5)

# ============= MERCADO PAGO =============
def gerar_pix_mercadopago(email, plano):
    if MODO_SIMULACAO:
        pix_id=str(uuid.uuid4())[:8]
        pagamentos_pendentes[pix_id]={'email':email,'plano_id':plano['id'],'moedas':plano['moedas'],'valor':plano['preco'],'pago':False,'criado_em':str(datetime.now())[:19]}
        return {'sucesso':True,'simulacao':True,'pix_id':pix_id,'qr_code':f"[SIMULAÇÃO] PIX de R$ {plano['preco']:.2f}",'qr_code_base64':'','valor':plano['preco'],'moedas':plano['moedas']}
    try:
        url="https://api.mercadopago.com/v1/payments"
        headers={"Authorization":f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}","Content-Type":"application/json","X-Idempotency-Key":str(uuid.uuid4())}
        payment_data={"transaction_amount":float(plano['preco']),"description":f"TESLA369 - {plano['nome']} - {plano['moedas']} moedas","payment_method_id":"pix","payer":{"email":email,"first_name":"Cliente","last_name":"Tesla369"}}
        response=requests.post(url,json=payment_data,headers=headers)
        data=response.json()
        if response.status_code in [200,201]:
            pix_id=str(data['id'])
            qr_code=data['point_of_interaction']['transaction_data']['qr_code']
            qr_code_base64=data['point_of_interaction']['transaction_data']['qr_code_base64']
            pagamentos_pendentes[pix_id]={'email':email,'plano_id':plano['id'],'moedas':plano['moedas'],'valor':plano['preco'],'pago':False,'criado_em':str(datetime.now())[:19]}
            return {'sucesso':True,'simulacao':False,'pix_id':pix_id,'qr_code':qr_code,'qr_code_base64':qr_code_base64,'valor':plano['preco'],'moedas':plano['moedas']}
        return {'sucesso':False,'erro':data.get('message','Erro ao gerar PIX')}
    except Exception as e:
        return {'sucesso':False,'erro':str(e)}

def verificar_pagamento_mp(pix_id):
    if MODO_SIMULACAO: return pagamentos_pendentes.get(pix_id,{}).get('pago',False)
    try:
        url=f"https://api.mercadopago.com/v1/payments/{pix_id}"
        headers={"Authorization":f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}"}
        return requests.get(url,headers=headers).json().get('status')=='approved'
    except: return False

def verificador_automatico_pix():
    while True:
        time.sleep(10)
        try:
            pendentes={k:v for k,v in pagamentos_pendentes.items() if not v.get('pago',False)}
            for pix_id,dados in list(pendentes.items()):
                if verificar_pagamento_mp(pix_id):
                    pagamentos_pendentes[pix_id]['pago']=True
                    email=dados['email']; moedas=dados['moedas']
                    usuario=carregar_usuario(email) or criar_usuario(email)
                    usuario['moedas']=usuario.get('moedas',0)+moedas
                    salvar_usuario(email,usuario)
                    add_log(f"✅ PIX pago! +{moedas} moedas para {email}","win")
        except: pass

threading.Thread(target=verificador_automatico_pix,daemon=True).start()

# ============= HTML =============
HTML = r'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚡ TESLA 369 BOT</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:#0a0a1a;color:#fff;font-family:'Courier New',monospace;padding:10px}
        .container{max-width:800px;margin:0 auto}
        .header{background:linear-gradient(135deg,#1a0000,#331100,#553300,#331100,#1a0000);padding:20px;border-radius:20px;text-align:center;border:3px solid #ffd700;margin-bottom:15px}
        .header h1{color:#ffd700;font-size:22px}
        .tabs{display:flex;gap:5px;margin-bottom:10px}
        .tab{padding:10px 14px;background:#1a1a3e;border:1px solid #333;border-radius:10px 10px 0 0;cursor:pointer;color:#888;font-size:10px}
        .tab.active{background:#ffd700;color:#000;font-weight:bold}
        .panel{display:none;background:#1a1a3e;padding:15px;border-radius:0 10px 10px 10px;border:1px solid #333;margin-bottom:10px}
        .panel.active{display:block}
        .btn{padding:10px 14px;border:none;border-radius:8px;font-weight:bold;cursor:pointer;font-size:11px;font-family:'Courier New',monospace}
        .btn-start{background:linear-gradient(135deg,#cc8800,#ffd700);color:#000}
        .btn-stop{background:linear-gradient(135deg,#cc0000,#ff4444);color:#fff}
        .btn-info{background:linear-gradient(135deg,#0066cc,#3399ff);color:#fff}
        .dashboard{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px;margin-bottom:10px}
        .card{background:#1a1a3e;padding:10px;border-radius:10px;border:1px solid #333;text-align:center}
        .card .label{color:#888;font-size:9px}.card .value{color:#ffd700;font-size:14px;font-weight:bold;margin-top:4px}
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
        <h1>⚡ TESLA 369 BOT v4.1.1.10 ⚡</h1>
        <p>🔮 8 ESTRATÉGIAS | GALE 2 | STOP GAIN 1 WIN | RENDER</p>
    </div>
    <div style="color:#ffd700;text-align:center;margin:8px 0">🌀 O DINHEIRO VEM ATÉ MIM DE TODOS OS LADOS 🌀</div>
    
    <div class="tabs">
        <div class="tab active" id="tab-bot" onclick="mostrarPainel('bot')">🤖 BOT</div>
        <div class="tab" id="tab-moedas" onclick="mostrarPainel('moedas')">💸 MOEDAS</div>
        <div class="tab" id="tab-relatorio" onclick="mostrarPainel('relatorio')">📊 RELATÓRIO</div>
    </div>
    
    <div class="panel active" id="panel-bot">
        <h3 style="color:#ffd700;margin-bottom:8px">🔐 IQ OPTION</h3>
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px">
            <input type="email" id="email" placeholder="📧 Email IQ Option" style="flex:2">
            <input type="password" id="senha" placeholder="🔒 Senha" style="flex:1">
            <select id="tipo"><option value="PRACTICE">🧪 DEMO</option><option value="REAL">💰 REAL</option></select>
            <button class="btn btn-info" id="btnConectar" onclick="conectarIQ()">🔌 CONECTAR</button>
            <button class="btn btn-start" id="btnOperar" onclick="comecarOperar()" style="display:none">🚀 COMEÇAR OPERAR</button>
            <button class="btn btn-stop" id="btnParar" onclick="pararBot()" style="display:none">⏹️ PARAR</button>
        </div>
        <div class="dashboard">
            <div class="card"><div class="label">💰 BANCA</div><div class="value" id="banca">--</div></div>
            <div class="card"><div class="label">📈 LUCRO</div><div class="value" id="lucro">$0.00</div></div>
            <div class="card"><div class="label">🪙 MOEDAS</div><div class="value" id="moedas">0</div></div>
            <div class="card"><div class="label">🔮 SINAL</div><div class="value" id="sinal" style="font-size:11px">--</div></div>
        </div>
        <div class="terminal" id="terminal">📡 Aguardando...</div>
        <div style="display:flex;justify-content:space-between;padding:8px;background:#1a1a3e;border-radius:10px;margin-top:10px">
            <span><span class="status-dot inactive" id="statusDot"></span> <span id="statusTexto">⏸️ Desconectado</span></span>
            <span>⚡ v4.1.1.10</span>
        </div>
    </div>
    
    <div class="panel" id="panel-moedas">
        <h3 style="color:#ffd700">💳 COMPRAR MOEDAS</h3>
        <p style="color:#888;font-size:10px">🪙 1 moeda = 1 ciclo | +1 moeda grátis/dia</p>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:8px;margin-top:10px">
            ''' + ''.join([f'<div style="background:#111;padding:12px;border-radius:10px;text-align:center;border:2px solid #222"><div style="font-size:20px;color:#ffd700">🪙 {p["moedas"]}</div><div style="color:#00ff88;margin:5px 0">R$ {p["preco"]:.2f}</div><div style="color:#888;font-size:9px">{p["nome"]}</div></div>' for p in PLANOS]) + '''
        </div>
    </div>
    
    <div class="panel" id="panel-relatorio">
        <h3 style="color:#ffd700">📊 RELATÓRIO</h3>
        <input type="email" id="emailRelatorio" placeholder="Email" style="width:100%;margin:5px 0">
        <button class="btn btn-info" onclick="verRelatorio()">🔍 BUSCAR</button>
        <div id="relatorioContent" style="margin-top:10px"></div>
    </div>
</div>

<script>
var intervalo=null,botAtivo=false,conectadoIQ=false,emailLogado='';
function mostrarPainel(p){
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
            document.getElementById('statusTexto').textContent='🟢 Conectado';
            document.getElementById('statusDot').className='status-dot active';
            document.getElementById('moedas').textContent=d.moedas||0;
            if(intervalo)clearInterval(intervalo);
            intervalo=setInterval(atualizar,2000);
            atualizar();
        }else{alert('ERRO: '+d.erro);document.getElementById('btnConectar').disabled=false;document.getElementById('btnConectar').textContent='🔌 CONECTAR';}
    });
}
function comecarOperar(){
    if(!conectadoIQ){alert('Conecte primeiro!');return}
    fetch('/comecar_operar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({})})
    .then(r=>r.json()).then(d=>{
        if(d.ok){
            botAtivo=true;
            document.getElementById('btnOperar').style.display='none';
            document.getElementById('btnParar').style.display='inline-block';
            document.getElementById('statusTexto').textContent='🤖 Operando';
            document.getElementById('moedas').textContent=d.moedas;
        }else{alert('ERRO: '+d.erro);}
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
        document.getElementById('btnConectar').textContent='🔌 CONECTAR';
        document.getElementById('statusTexto').textContent='⏸️ Desconectado';
        document.getElementById('statusDot').className='status-dot inactive';
        if(intervalo)clearInterval(intervalo);
    });
}
function verRelatorio(){
    var email=document.getElementById('emailRelatorio').value.trim();
    if(!email){alert('Digite o email!');return}
    fetch('/relatorio?email='+email).then(r=>r.json()).then(d=>{
        if(d.erro){alert(d.erro);return}
        var h='<p>🪙 Moedas: <b>'+(d.moedas||0)+'</b></p>';
        h+='<p>📈 Lucro: <b>$'+(d.lucro_total||0).toFixed(2)+'</b></p>';
        h+='<p>✅ Wins: <b>'+(d.total_wins||0)+'</b></p>';
        h+='<p>❌ Losses: <b>'+(d.total_losses||0)+'</b></p>';
        h+='<p>🔄 Ciclos: <b>'+(d.total_ciclos||0)+'</b></p>';
        document.getElementById('relatorioContent').innerHTML=h;
    });
}
function atualizar(){
    fetch('/status').then(r=>r.json()).then(d=>{
        if(d.banca)document.getElementById('banca').textContent='$'+d.banca.toFixed(2);
        if(d.lucro!==undefined){var el=document.getElementById('lucro');el.textContent='$'+d.lucro.toFixed(2);el.style.color=d.lucro>=0?'#00ff88':'#ff4444';}
        if(d.moedas!==undefined)document.getElementById('moedas').textContent=d.moedas;
        if(d.sinal)document.getElementById('sinal').textContent=d.sinal;
        if(d.logs){document.getElementById('terminal').innerHTML=d.logs;document.getElementById('terminal').scrollTop=document.getElementById('terminal').scrollHeight;}
    });
}
</script>
</body>
</html>'''

def processar_html_com_skin():
    skin = next((s for s in SKINS if s['id'] == skin_atual_global), SKINS[0])
    return HTML

# ============= ROTAS =============
@app.route('/')
def index(): return render_template_string(processar_html_com_skin())

@app.route('/status')
def status():
    u = carregar_usuario(email_usuario_atual) if email_usuario_atual else {}
    return jsonify({'conectado':conectado_iq,'rodando':bot_rodando,'email':email_usuario_atual,'banca':API.get_balance() if API else 0,'lucro':lucro,'ops':NumDeOperacoes,'sinal':ultimo_sinal,'logs':get_logs_html(40),'moedas':u.get('moedas',0),'estrategia':estrategia_atual})

@app.route('/conectar', methods=['POST'])
def conectar():
    global API, email_usuario_atual, conectado_iq
    try:
        d = request.get_json()
        email = d.get('email','').strip(); senha = d.get('senha','').strip(); tipo = d.get('tipo','PRACTICE')
        if not email or not senha: return jsonify({'ok':False,'erro':'Email e senha obrigatórios'})
        email_usuario_atual = email
        usuario = carregar_usuario(email) or criar_usuario(email)
        hoje = str(datetime.now())[:10]
        if usuario.get('moedas_ganhas_hoje') != hoje:
            usuario['moedas'] = usuario.get('moedas',0) + 1
            usuario['moedas_ganhas_hoje'] = hoje
            salvar_usuario(email, usuario)
        API = IQ_Option(email, senha)
        status_conn, reason = API.connect()
        if not status_conn: return jsonify({'ok':False,'erro':str(reason)[:100]})
        API.change_balance(tipo)
        conectado_iq = True
        return jsonify({'ok':True,'moedas':usuario.get('moedas',0)})
    except Exception as e: return jsonify({'ok':False,'erro':str(e)[:100]})

@app.route('/comecar_operar', methods=['POST'])
def comecar_operar():
    global bot_rodando, bot_thread, lucro, NumDeOperacoes
    try:
        if not conectado_iq: return jsonify({'ok':False,'erro':'Conecte primeiro!'})
        usuario = carregar_usuario(email_usuario_atual)
        if not usuario or usuario.get('moedas',0) < 1: return jsonify({'ok':False,'erro':'Sem moedas!'})
        usuario['moedas'] -= 1; usuario['total_ciclos'] += 1
        salvar_usuario(email_usuario_atual, usuario)
        lucro = 0.0; NumDeOperacoes = 0
        if not bot_rodando:
            bot_rodando = True
            bot_thread = threading.Thread(target=bot_loop, daemon=True)
            bot_thread.start()
        return jsonify({'ok':True,'moedas':usuario['moedas']})
    except Exception as e: return jsonify({'ok':False,'erro':str(e)[:100]})

@app.route('/parar', methods=['POST'])
def parar():
    global bot_rodando, conectado_iq
    bot_rodando = False; conectado_iq = False
    return jsonify({'ok':True})

@app.route('/relatorio')
def relatorio():
    email = request.args.get('email','')
    if not email: return jsonify({'erro':'Email obrigatório'})
    u = carregar_usuario(email)
    return jsonify(u if u else {'erro':'Não encontrado'})

@app.route('/resetar', methods=['POST'])
def resetar():
    d = request.get_json()
    email = d.get('email','')
    if not email: return jsonify({'ok':False,'msg':'Email obrigatório'})
    usuario = criar_usuario(email)
    usuario['moedas_ganhas_hoje'] = str(datetime.now())[:10]
    usuario['moedas'] = 0
    salvar_usuario(email, usuario)
    return jsonify({'ok':True,'msg':'✅ Resetado!'})

if __name__ == '__main__':
    print("=" * 50)
    print("⚡ TESLA 369 BOT v4.1.1.10 ⚡")
    print("=" * 50)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
