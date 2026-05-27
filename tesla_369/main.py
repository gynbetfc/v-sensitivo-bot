# ⚡ TESLA 369 BOT v6.5.1 ⚡
from flask import Flask, render_template_string, jsonify, request
from iqoptionapi.stable_api import IQ_Option
from datetime import datetime
import threading, time, sys, os, json, warnings, requests, uuid, base64

warnings.filterwarnings("ignore")
app = Flask(__name__)

# Importa módulos organizados
from core.firebase import salvar_usuario, carregar_usuario, criar_usuario, FB_URL
from core.indicadores import sma, bollinger, rsi, macd, estocastico
from core.mercado_pago import gerar_pix_mercadopago, verificar_pagamento_mp, pagamentos_pendentes
from skins import SKINS
from estrategias import ESTRATEGIAS, ESTRATEGIA_TESLA_369

# ═══════════ CONFIGURAÇÕES ═══════════
MARTINGALE = 2
PAYOUT_PADRAO = 0.85
PERCENTUAL_BANCA = 15

PLANOS = [
    {'id':1,'moedas':1,'preco':0.99,'nome':'🔰 TESTE','desc':'R$0,99/VOLT','tag':'1 ciclo'},
    {'id':2,'moedas':6,'preco':6.69,'nome':'⭐ BÁSICO','desc':'R$1,11/VOLT','tag':'6 ciclos'},
    {'id':3,'moedas':15,'preco':9.99,'nome':'💎 INTERMEDIÁRIO','desc':'R$0,67/VOLT','desconto':'33% OFF','tag':'15 ciclos','bonus':'🎨 1 Skin Básica GRÁTIS'},
    {'id':4,'moedas':36,'preco':21.69,'nome':'🔥 PREMIUM','desc':'R$0,60/VOLT','desconto':'40% OFF','tag':'36 ciclos','bonus':'🎨 1 Skin Premium GRÁTIS'},
    {'id':5,'moedas':69,'preco':39.69,'nome':'👑 ULTRA','desc':'R$0,57/VOLT','desconto':'69% OFF','tag':'69 ciclos','bonus':'🎨 1 Skin Lendária GRÁTIS'},
]

# ═══════════ VARIÁVEIS GLOBAIS ═══════════
API, par = None, "EURUSD-OTC"
estrategia_atual = 'tesla_369'
timeframe_atual = 60
lucro, NumDeOperacoes = 0.0, 0
bot_rodando, bot_thread = False, None
conectado_iq = False
ultimo_sinal, ultima_analise = "Aguardando...", {}
logs_web, MAX_LOGS_WEB = [], 200
email_usuario_atual = ""
skin_atual_global = 'skin_padrao'

# ═══════════ FUNÇÕES AUXILIARES ═══════════
def add_log(msg, tipo='info'):
    global logs_web
    t = datetime.now().strftime('%H:%M:%S')
    logs_web.append({'time': t, 'msg': msg, 'tipo': tipo})
    if len(logs_web) > MAX_LOGS_WEB: logs_web = logs_web[-MAX_LOGS_WEB:]
    print(f"{t} - {msg}")

def get_logs_html(limite=40):
    html = ''
    for log in logs_web[-limite:]:
        cor = {'win': '#00ff88', 'loss': '#ff4444', 'info': '#00ff88', 'sensitive': '#ff69b4', 'indicator': '#ffd700', 'error': '#ff4444'}.get(log['tipo'], '#00ff88')
        html += f'<span style="color:#666">{log["time"]}</span> <span style="color:{cor}">{log["msg"]}</span>\n'
    return html or '📡 Aguardando...'

def Payout(p):
    try:
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
    for i in range(1, g+1): entradas.append((sum(entradas)+e0)/p)
    ajuste = bs / sum(entradas)
    entradas = [round(e*ajuste, 2) for e in entradas]
    soma = sum(entradas)
    if soma > b: entradas[-1] = round(entradas[-1] - (soma-b) - 0.02, 2)
    return [max(1, e) for e in entradas]

# ═══════════ ROTAS ═══════════
@app.route('/')
def index(): return "<h1>⚡ TESLA 369 v6.5.1</h1><p>Bot rodando! Estrutura modular.</p>"

@app.route('/status')
def status():
    return jsonify({
        'conectado': conectado_iq, 'rodando': bot_rodando,
        'banca': API.get_balance() if API else 0,
        'lucro': lucro, 'ops': NumDeOperacoes,
        'sinal': ultimo_sinal, 'analise': ultima_analise,
        'logs': get_logs_html(40), 'moedas': 0,
        'estrategia': estrategia_atual,
        'skins_status': [{'id': s['id'], 'nome': s['nome'], 'preco_moedas': s['preco_moedas'], 'categoria': s.get('categoria','basica'), 'comprado': True, 'ativo': s['id']==skin_atual_global} for s in SKINS]
    })

@app.route('/conectar', methods=['POST'])
def conectar():
    global API, email_usuario_atual, conectado_iq, skin_atual_global
    try:
        d = request.get_json()
        email, senha, tipo = d.get('email',''), d.get('senha',''), d.get('tipo','PRACTICE')
        if not email or not senha: return jsonify({'ok': False, 'erro': 'Email e senha obrigatórios'})
        email_usuario_atual = email
        API = IQ_Option(email, senha)
        status_conn, reason = API.connect()
        if not status_conn: return jsonify({'ok': False, 'erro': str(reason)[:100]})
        API.change_balance(tipo)
        conectado_iq = True
        usuario = carregar_usuario(email) or criar_usuario(email)
        hoje = str(datetime.now())[:10]
        if usuario.get('moedas_ganhas_hoje') != hoje:
            if tipo == "PRACTICE" and usuario.get('demo_iniciado') != True:
                usuario['moedas'] = 51; usuario['demo_iniciado'] = True
            else:
                usuario['moedas'] = usuario.get('moedas', 0) + 1
            usuario['moedas_ganhas_hoje'] = hoje
            salvar_usuario(email, usuario)
        skin_atual_global = usuario.get('skin_atual', 'skin_padrao')
        add_log(f'✅ Conectado! ${API.get_balance():.2f} | ⚡ {usuario.get("moedas", 0)} VOLTS', 'win')
        return jsonify({'ok': True, 'moedas': usuario.get('moedas', 0)})
    except Exception as e: return jsonify({'ok': False, 'erro': str(e)[:100]})

@app.route('/parar', methods=['POST'])
def parar():
    global bot_rodando, conectado_iq
    data = request.json or {}
    bot_rodando = False
    if data.get('desconectar'): conectado_iq = False
    return jsonify({'ok': True})

@app.route('/comprar_skin', methods=['POST'])
def comprar_skin():
    global skin_atual_global
    if not email_usuario_atual: return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    skin_id = request.json.get('skin_id','')
    skin = next((s for s in SKINS if s['id'] == skin_id), None)
    if not skin: return jsonify({'ok': False, 'erro': 'Skin não encontrada'})
    usuario = carregar_usuario(email_usuario_atual)
    if not usuario: return jsonify({'ok': False, 'erro': 'Usuário não encontrado'})
    if skin['preco_moedas'] == 0:
        usuario['skin_atual'] = skin_id
        if 'skins_compradas' not in usuario: usuario['skins_compradas'] = ['skin_padrao']
        if skin_id not in usuario['skins_compradas']: usuario['skins_compradas'].append(skin_id)
        salvar_usuario(email_usuario_atual, usuario)
        skin_atual_global = skin_id
        return jsonify({'ok': True, 'moedas': usuario.get('moedas',0), 'msg': 'Skin ativada!'})
    if skin_id in usuario.get('skins_compradas', []):
        usuario['skin_atual'] = skin_id
        salvar_usuario(email_usuario_atual, usuario)
        skin_atual_global = skin_id
        return jsonify({'ok': True, 'moedas': usuario['moedas'], 'msg': 'Skin já comprada! Ativada.'})
    if usuario.get('moedas',0) < skin['preco_moedas']:
        return jsonify({'ok': False, 'erro': f'VOLTS insuficientes! Precisa de {skin["preco_moedas"]} ⚡'})
    usuario['moedas'] -= skin['preco_moedas']
    if 'skins_compradas' not in usuario: usuario['skins_compradas'] = ['skin_padrao']
    usuario['skins_compradas'].append(skin_id)
    usuario['skin_atual'] = skin_id
    salvar_usuario(email_usuario_atual, usuario)
    skin_atual_global = skin_id
    return jsonify({'ok': True, 'moedas': usuario['moedas'], 'msg': f'Skin comprada!'})

@app.route('/criar_pix', methods=['POST'])
def criar_pix():
    d = request.get_json()
    plano = next((p for p in PLANOS if p['id'] == int(d.get('plano_id',1))), None)
    if not plano: return jsonify({'sucesso': False, 'erro': 'Plano não encontrado'})
    return jsonify(gerar_pix_mercadopago(d.get('email',''), plano))

@app.route('/verificar_pix', methods=['POST'])
def verificar_pix():
    pix_id = request.json.get('pix_id','')
    if verificar_pagamento_mp(pix_id):
        if pix_id in pagamentos_pendentes and not pagamentos_pendentes[pix_id]['pago']:
            pagamentos_pendentes[pix_id]['pago'] = True
            email = pagamentos_pendentes[pix_id]['email']
            moedas = pagamentos_pendentes[pix_id]['moedas']
            usuario = carregar_usuario(email) or criar_usuario(email)
            usuario['moedas'] = usuario.get('moedas',0) + moedas
            salvar_usuario(email, usuario)
            return jsonify({'pago': True, 'moedas': moedas, 'saldo': usuario['moedas']})
        return jsonify({'pago': True})
    return jsonify({'pago': False})

@app.route('/ranking')
def ranking():
    ranking_list = []
    try:
        r = requests.get(f'{FB_URL}/usuarios.json')
        usuarios = r.json() if r.status_code == 200 else {}
        if usuarios:
            for key, user_data in usuarios.items():
                if user_data:
                    ranking_list.append({
                        'email': user_data.get('email','N/A')[:20]+'...',
                        'lucro_total': round(user_data.get('lucro_total',0),2),
                        'total_wins': user_data.get('total_wins',0),
                        'total_losses': user_data.get('total_losses',0),
                        'total_ciclos': user_data.get('total_ciclos',0),
                        'taxa': round((user_data.get('total_wins',0)/max(user_data.get('total_ciclos',1),1))*100,1),
                        'banca_atual': round(user_data.get('banca_atual',0),2)
                    })
    except: pass
    ranking_list.sort(key=lambda x: x['lucro_total'], reverse=True)
    total_ops = sum(u['total_ciclos'] for u in ranking_list)
    total_wins = sum(u['total_wins'] for u in ranking_list)
    taxa_global = round((total_wins/max(total_ops,1))*100,1) if total_ops>0 else 0
    return jsonify({'ranking': ranking_list[:20], 'stats': {'total_usuarios': len(ranking_list), 'total_ops': total_ops, 'total_wins': total_wins, 'taxa_global': taxa_global}})

# ═══════════ INICIAR ═══════════
print("⚡ TESLA 369 v6.5.1 - Estrutura Modular")
print(f"📁 Skins: {len(SKINS)} | 📊 Estratégias: {len(ESTRATEGIAS)}")

if __name__ == '__main__':
    # Iniciar verificador PIX em background
    def verificador_pix():
        while True:
            time.sleep(10)
            try:
                pendentes = {k:v for k,v in pagamentos_pendentes.items() if not v.get('pago')}
                for pix_id, dados in list(pendentes.items()):
                    if verificar_pagamento_mp(pix_id):
                        pagamentos_pendentes[pix_id]['pago'] = True
                        usuario = carregar_usuario(dados['email']) or criar_usuario(dados['email'])
                        usuario['moedas'] = usuario.get('moedas',0) + dados['moedas']
                        salvar_usuario(dados['email'], usuario)
            except: pass
    
    threading.Thread(target=verificador_pix, daemon=True).start()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
