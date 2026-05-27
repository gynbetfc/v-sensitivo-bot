# ⚡ TESLA 369 BOT v6.5.2 ⚡
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
from estrategias import ESTRATEGIAS

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
BANCA_INICIAL_DO_BOT, STOP_GAIN_ATINGIDO = 0, False
bot_rodando, bot_thread = False, None
conectado_iq = False
ultimo_sinal, ultima_analise = "Aguardando...", {}
logs_web, MAX_LOGS_WEB = [], 200
email_usuario_atual = ""
skin_atual_global = 'skin_padrao'
bots_ativos = {}

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


# ═══════════ FUNÇÕES DE TRADING ═══════════
def calcular_entradas(b, p, g):
    global PERCENTUAL_BANCA
    bs = (b * PERCENTUAL_BANCA / 100) * 0.99; e0 = bs / sum((1/p)**i for i in range(g+1))
    entradas = [e0]
    for i in range(1, g+1): entradas.append((sum(entradas)+e0)/p)
    ajuste = bs / sum(entradas); entradas = [round(e*ajuste, 2) for e in entradas]
    soma = sum(entradas)
    if soma > b: entradas[-1] = round(entradas[-1] - (soma-b) - 0.02, 2)
    return [max(1, e) for e in entradas]

def pegar_timestamp():

def pegar_timestamp():
    v = API.get_candles(par, timeframe_atual, 1, time.time())
    return v[0]['from'] if v else 0

def aguardar_inicio_vela():

def aguardar_inicio_vela():
    add_log("   ⏳ Aguardando início da vela...", 'info')
    while datetime.now().second > 5:
        if not bot_rodando: return False
        time.sleep(0.3)
    while True:
        if not bot_rodando: return False
        ts1 = pegar_timestamp(); time.sleep(0.5); ts2 = pegar_timestamp()
        if ts1 == ts2: add_log("   ✅ Vela confirmada!", 'info'); return True

def aguardar_vela_fechar(ts_entrada):

def aguardar_vela_fechar(ts_entrada):
    add_log(f"   ⏳ Aguardando vela fechar...", 'info')
    while True:
        if not bot_rodando: return False
        try:
            if pegar_timestamp() != ts_entrada: add_log("   ✅ Vela fechou!", 'info'); return True
        except: pass
        time.sleep(0.3)

def verificar_resultado(saldo_antes, valor):

def verificar_resultado(saldo_antes, valor):
    saldo_base = saldo_antes - valor
    try:
        s = API.get_balance(); d = round(s-saldo_base, 2)
        if d >= 1.0: return d
    except: pass
    return -valor

def executar_ciclo(direcao):

def executar_ciclo(direcao):
    global lucro, NumDeOperacoes, STOP_GAIN_ATINGIDO, bot_rodando
    bi = API.get_balance()
    payout = Payout(par)
    entradas = calcular_entradas(bi, payout, MARTINGALE)
    add_log(f"💰 Banca: ${bi:.2f} | Payout: {payout*100:.0f}%", 'info')
    add_log(f"📐 E1:${entradas[0]:.2f} | E2:${entradas[1]:.2f} | E3:${entradas[2]:.2f}", 'info')
    for i in range(MARTINGALE + 1):
        if not bot_rodando: break
        valor = entradas[i]
        if not aguardar_inicio_vela(): break
        saldo_antes = API.get_balance()
        if saldo_antes < valor:
            add_log("❌ Saldo insuficiente!", 'error')
            break
        print()
        add_log(f"🎯 {'ENTRADA' if i == 0 else f'GALE {i}'}: {direcao.upper()} ${valor:.2f}", 'info')
        st, id_ordem = API.buy(valor, par, direcao, 1)
        if not st or not id_ordem:
            try: st, id_ordem = API.buy_digital_spot(par, valor, direcao, 1)
            except: pass
        if not st or not id_ordem:
            add_log("❌ Falha na ordem!", 'error')
            break
        add_log(f"   📝 Ordem #{id_ordem}", 'info')
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
                u['total_wins'] += 1; u['total_ganho'] += abs(lucro_liquido)
                u['lucro_total'] = u['total_ganho'] - u['total_gasto']
                u['banca_atual'] = round(saldo_depois, 2)
                u.setdefault('historico_operacoes', []).append({'data': str(datetime.now())[:19], 'resultado': 'WIN', 'valor': valor, 'lucro': lucro_liquido, 'estrategia': estrategia_atual})
                u['dias_ativos'] = u.get('dias_ativos', 0) + 1
                salvar_usuario(email_usuario_atual, u)
            STOP_GAIN_ATINGIDO = True
            add_log("🎯 STOP GAIN! Vitória alcançada - Bot PARADO!", 'win')
            break
        else:
            add_log(f"💀 LOSS! -${valor:.2f}", 'loss')
            u = carregar_usuario(email_usuario_atual)
            if u:
                u['total_losses'] += 1; u['total_gasto'] += valor
                u['lucro_total'] = u['total_ganho'] - u['total_gasto']
                u['banca_atual'] = round(saldo_depois, 2)
                u.setdefault('historico_operacoes', []).append({'data': str(datetime.now())[:19], 'resultado': 'LOSS', 'valor': valor, 'lucro': -valor, 'estrategia': estrategia_atual})
                u['dias_ativos'] = u.get('dias_ativos', 0) + 1
                salvar_usuario(email_usuario_atual, u)
            if i < MARTINGALE: add_log(f"   ➡️ Indo para GALE {i + 1}...", 'loss')
            else: add_log("   💀 CICLO COMPLETO PERDIDO! Bot PARADO!", 'loss')
    bf = API.get_balance()
    print()
    add_log("=" * 50, 'info')
    add_log(f"{'🌟 LUCRO' if bf > bi else '💀 PERDA'}: ${abs(bf - bi):.2f} | Banca: ${bf:.2f}", 'info')
    add_log("=" * 50, 'info')
    bot_rodando = False
    add_log("⏹️ Ciclo concluído! Clique em CONECTAR e depois COMEÇAR OPERAR para novo ciclo.", 'info')

def bot_loop():

def bot_loop():
    global bot_rodando, BANCA_INICIAL_DO_BOT, lucro, NumDeOperacoes, STOP_GAIN_ATINGIDO
    nome_est = ESTRATEGIAS.get(estrategia_atual, ESTRATEGIAS['v_sensitivo'])['nome']
    add_log(f'⚡ TESLA 369 - INICIANDO...', 'sensitive')
    add_log(f'📊 Estratégia: {nome_est}', 'info')
    BANCA_INICIAL_DO_BOT = API.get_balance()
    STOP_GAIN_ATINGIDO = False; lucro = 0.0; NumDeOperacoes = 0
    add_log(f"📌 {par} | Timeframe: {timeframe_atual}s | 💰 ${BANCA_INICIAL_DO_BOT:.2f}")
    add_log('🧿 SIGILOS ATIVADOS 🧿', 'win')
    add_log('🔮 Buscando sinal...', 'info')
    funcao_sinal = MAPA_SINAIS.get(estrategia_atual, sinal_v_sensitivo)
    while bot_rodando and not STOP_GAIN_ATINGIDO:
        try:
            direcao = funcao_sinal()
            if direcao: executar_ciclo(direcao); break
            time.sleep(0.3)
        except Exception as e: add_log(f"Erro: {e}", 'error'); time.sleep(5); conectar_api()
    if not bot_rodando: add_log("⏹️ Bot parado.", 'info')

# ═══════════════════════════════════════════════════════



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

def pegar_timestamp():
    v = API.get_candles(par, timeframe_atual, 1, time.time())
    return v[0]['from'] if v else 0

def aguardar_inicio_vela():
    add_log("   Aguardando inicio da vela...", 'info')
    while datetime.now().second > 5:
        if not bot_rodando: return False
        time.sleep(0.3)
    while True:
        if not bot_rodando: return False
        ts1 = pegar_timestamp(); time.sleep(0.5); ts2 = pegar_timestamp()
        if ts1 == ts2: add_log("   Vela confirmada!", 'info'); return True

def aguardar_vela_fechar(ts_entrada):
    add_log("   Aguardando vela fechar...", 'info')
    while True:
        if not bot_rodando: return False
        try:
            if pegar_timestamp() != ts_entrada: add_log("   Vela fechou!", 'info'); return True
        except: pass
        time.sleep(0.3)

def verificar_resultado(saldo_antes, valor):
    saldo_base = saldo_antes - valor
    try:
        s = API.get_balance(); d = round(s-saldo_base, 2)
        if d >= 1.0: return d
    except: pass
    return -valor

def executar_ciclo(direcao):
    global lucro, NumDeOperacoes, STOP_GAIN_ATINGIDO, bot_rodando
    bi = API.get_balance()
    payout = Payout(par)
    entradas = calcular_entradas(bi, payout, MARTINGALE)
    add_log(f"Banca: ${bi:.2f} | Payout: {payout*100:.0f}%", 'info')
    for i in range(MARTINGALE + 1):
        if not bot_rodando: break
        valor = entradas[i]
        if not aguardar_inicio_vela(): break
        saldo_antes = API.get_balance()
        if saldo_antes < valor: add_log("Saldo insuficiente!", 'error'); break
        add_log(f"{'ENTRADA' if i == 0 else f'GALE {i}'}: {direcao.upper()} ${valor:.2f}", 'info')
        st, id_ordem = API.buy(valor, par, direcao, 1)
        if not st or not id_ordem:
            try: st, id_ordem = API.buy_digital_spot(par, valor, direcao, 1)
            except: pass
        if not st or not id_ordem: add_log("Falha na ordem!", 'error'); break
        time.sleep(0.3)
        ts_real = pegar_timestamp()
        if not aguardar_vela_fechar(ts_real): break
        res = verificar_resultado(saldo_antes, valor)
        lucro += round(res, 2)
        if res > 0:
            add_log(f"WIN! +${round(API.get_balance()-saldo_antes,2):.2f}", 'win')
            NumDeOperacoes += 1
            u = carregar_usuario(email_usuario_atual)
            if u:
                u['total_wins'] += 1; u['total_ganho'] += abs(res)
                u['lucro_total'] = u['total_ganho'] - u['total_gasto']
                u['banca_atual'] = round(API.get_balance(), 2)
                u.setdefault('historico_operacoes', []).append({'data': str(datetime.now())[:19], 'resultado': 'WIN', 'valor': valor, 'lucro': res, 'estrategia': estrategia_atual})
                u['dias_ativos'] = u.get('dias_ativos', 0) + 1
                salvar_usuario(email_usuario_atual, u)
            STOP_GAIN_ATINGIDO = True; add_log("STOP GAIN! Bot PARADO!", 'win'); break
        else:
            add_log(f"LOSS! -${valor:.2f}", 'loss')
            u = carregar_usuario(email_usuario_atual)
            if u:
                u['total_losses'] += 1; u['total_gasto'] += valor
                u['lucro_total'] = u['total_ganho'] - u['total_gasto']
                u.setdefault('historico_operacoes', []).append({'data': str(datetime.now())[:19], 'resultado': 'LOSS', 'valor': valor, 'lucro': -valor, 'estrategia': estrategia_atual})
                u['dias_ativos'] = u.get('dias_ativos', 0) + 1
                salvar_usuario(email_usuario_atual, u)
            if i < MARTINGALE: add_log(f"Indo para GALE {i+1}...", 'loss')
    bf = API.get_balance()
    add_log(f"{'LUCRO' if bf > bi else 'PERDA'}: ${abs(bf-bi):.2f} | Banca: ${bf:.2f}", 'info')
    bot_rodando = False

def bot_loop():
    global bot_rodando, BANCA_INICIAL_DO_BOT, lucro, NumDeOperacoes, STOP_GAIN_ATINGIDO
    BANCA_INICIAL_DO_BOT = API.get_balance()
    STOP_GAIN_ATINGIDO = False; lucro = 0.0; NumDeOperacoes = 0
    add_log(f"TESLA 369 - INICIANDO... {estrategia_atual}", 'sensitive')
    add_log(f"{par} | Timeframe: {timeframe_atual}s | Banca: ${BANCA_INICIAL_DO_BOT:.2f}")
    # Importa sinal da estratégia atual
    if estrategia_atual == 'tesla_369':
        from estrategias.tesla_369 import sinal_tesla_369 as funcao_sinal
    elif estrategia_atual == 'v_sensitivo':
        from estrategias.v_sensitivo import sinal_v_sensitivo as funcao_sinal
    else:
        from estrategias.tesla_369 import sinal_tesla_369 as funcao_sinal
    
    while bot_rodando and not STOP_GAIN_ATINGIDO:
        try:
            resultado = funcao_sinal(API, par, timeframe_atual)
            if isinstance(resultado, tuple):
                direcao, _ = resultado
            else:
                direcao = resultado
            if direcao: executar_ciclo(direcao); break
            time.sleep(0.3)
        except Exception as e: add_log(f"Erro: {e}", 'error'); time.sleep(5)

# ═══════════ HTML ═══════════
HTML = r'''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚡ TESLA 369 BOT v6.5.2</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:{{COR_FUNDO}};color:{{COR_TEXTO}};font-family:'Courier New',monospace;padding:10px}
        .container{max-width:950px;margin:0 auto}
        .tabs{display:flex;gap:5px;margin-bottom:10px;flex-wrap:wrap}
        .tab{padding:10px 14px;background:{{COR_PANEL}};border:1px solid #333;border-radius:10px 10px 0 0;cursor:pointer;color:#888;font-size:10px}
        .tab.active{background:{{COR_TAB_ATIVA}};color:#000;font-weight:bold}
        .panel{display:none;background:{{COR_PANEL}};padding:15px;border-radius:0 10px 10px 10px;border:1px solid #333;margin-bottom:10px}
        .panel.active{display:block}
        .header{background:{{COR_HEADER_BG}};padding:20px;border-radius:20px;text-align:center;border:3px solid {{COR_HEADER_BORDA}};position:relative;overflow:hidden;margin-bottom:15px}
        {{CSS_EXTRA}}
        .header h1{color:{{COR_DESTAQUE}};font-size:22px;text-shadow:0 0 30px {{COR_TAB_ATIVA}};position:relative;z-index:3}
        .header p{color:{{COR_DESTAQUE}};font-size:10px;position:relative;z-index:3;opacity:0.8}
        .mantra{color:{{COR_DESTAQUE}};text-align:center;margin:8px 0;font-size:10px}
        .config-section{margin-bottom:12px}
        .config-section h3{color:{{COR_DESTAQUE}};margin-bottom:8px;font-size:13px;border-bottom:1px solid #333;padding-bottom:5px}
        .config-row{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:8px}
        .config-row label{color:#888;font-size:11px}
        .config-row select,.config-row input{padding:8px;background:#111;border:1px solid #333;border-radius:8px;color:#fff;font-size:11px;font-family:'Courier New',monospace}
        .btn{padding:10px 14px;border:none;border-radius:8px;font-weight:bold;cursor:pointer;font-size:11px;font-family:'Courier New',monospace}
        .btn-start{background:{{COR_BOTAO}};color:#000;font-weight:bold}
        .btn-stop{background:linear-gradient(135deg,#cc0000,#ff4444);color:#fff}
        .btn-info{background:linear-gradient(135deg,#0066cc,#3399ff);color:#fff;font-size:11px;padding:8px 14px}
        .btn-buy{background:linear-gradient(135deg,#00aa44,#00cc55);color:#fff;width:100%;padding:12px;font-size:13px}
        .btn-reset{background:linear-gradient(135deg,#cc0000,#ff6600);color:#fff;font-size:11px;padding:8px 14px}
        .btn-skin{background:linear-gradient(135deg,#9933ff,#cc66ff);color:#fff;font-size:11px;padding:8px 12px}
        .dashboard{display:grid;grid-template-columns:repeat(auto-fit,minmax(105px,1fr));gap:8px;margin-bottom:10px}
        .card{background:{{COR_PANEL}};padding:10px;border-radius:10px;border:1px solid #333;text-align:center}
        .card .label{color:#888;font-size:9px}.card .value{color:{{COR_DESTAQUE}};font-size:14px;font-weight:bold;margin-top:4px}
        .indicators{display:grid;grid-template-columns:repeat(auto-fit,minmax(80px,1fr));gap:6px;margin-bottom:10px}
        .ind-card{background:#111;padding:6px;border-radius:8px;border:1px solid #222;text-align:center;font-size:10px}
        .ind-card .ind-label{color:#666;font-size:9px}.ind-card .ind-value{color:{{COR_DESTAQUE}};font-size:11px}
        .terminal{background:#000;color:#00ff88;padding:12px;border-radius:10px;height:200px;overflow-y:auto;font-size:10px;line-height:1.4;white-space:pre-wrap;border:1px solid #333;position:relative;overflow:hidden}.terminal span{position:relative;z-index:1}
        .barra-status{display:flex;justify-content:space-between;padding:8px;background:{{COR_PANEL}};border-radius:10px;margin-top:10px;font-size:10px;flex-wrap:wrap;gap:5px}
        .status-dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:4px}
        .status-dot.active{background:#00ff88;animation:pulse 1s infinite}.status-dot.inactive{background:#888}
        @keyframes pulse{0%,100%{opacity:1}50%{opacity:0.3}}
        .planos-grid,.skins-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}
        .plano-card,.skin-card{background:#111;padding:12px;border-radius:10px;border:2px solid #222;text-align:center;cursor:pointer;transition:all 0.3s ease}
        .plano-card:hover,.skin-card:hover{border-color:{{COR_DESTAQUE}};background:#1a1a2e}
        .plano-card.selecionado,.skin-card.selecionado{border-color:{{COR_DESTAQUE}};box-shadow:0 0 20px rgba(255,215,0,0.4)}
        .skin-card.ativo{border-color:#00ff88;box-shadow:0 0 15px rgba(0,255,136,0.3)}
        .plano-moedas,.skin-nome{font-size:20px;color:{{COR_DESTAQUE}};font-weight:bold}
        .plano-preco{font-size:14px;color:#00ff88;margin:5px 0}
        .plano-desc,.skin-desc{font-size:9px;color:#888;margin-top:4px}
        .plano-tag{background:{{COR_DESTAQUE}}22;color:{{COR_DESTAQUE}};font-size:9px;padding:2px 8px;border-radius:10px;display:inline-block;margin-top:4px}
        .plano-desconto{background:#ff4444;color:#fff;font-size:9px;padding:2px 6px;border-radius:10px;display:inline-block;margin-left:4px}
        .modal-overlay{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.85);z-index:1000;justify-content:center;align-items:center}
        .modal-overlay.active{display:flex}
        .modal-pagamento{background:{{COR_PANEL}};border:2px solid {{COR_DESTAQUE}};border-radius:15px;padding:25px;max-width:400px;width:90%;text-align:center}
        .modal-pagamento h3{color:{{COR_DESTAQUE}};margin-bottom:15px}
        .pix-qrcode{background:#fff;padding:15px;border-radius:10px;display:inline-block;margin:10px 0}
        .pix-qrcode img{max-width:200px}
        .pix-copiavel{background:#000;color:#00ff88;padding:10px;border-radius:8px;font-size:9px;word-break:break-all;margin:10px 0;max-height:60px;overflow-y:auto;cursor:pointer}
        .btn-fechar{background:#444;color:#fff;padding:8px 20px;border-radius:8px;cursor:pointer;margin-top:10px;border:none;font-family:'Courier New',monospace}
        .btn-confirmar{background:{{COR_DESTAQUE}};color:#000;padding:8px 20px;border-radius:8px;cursor:pointer;margin-top:10px;font-weight:bold;border:none;font-family:'Courier New',monospace}
        .relatorio-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:6px}
        .relatorio-card{background:#111;padding:8px;border-radius:8px;border:1px solid #222;text-align:center}
        .relatorio-card .rlabel{color:#666;font-size:9px}.relatorio-card .rvalue{color:{{COR_DESTAQUE}};font-size:14px;font-weight:bold}
        .historico-table{width:100%;font-size:9px;border-collapse:collapse;margin-top:10px}
        .historico-table th{background:{{COR_TAB_ATIVA}};color:#000;padding:4px}.historico-table td{padding:3px;border-bottom:1px solid #222;text-align:center}
        .estrategia-card{background:#111;padding:12px;border-radius:10px;border:2px solid #222;cursor:pointer;transition:all 0.3s ease;text-align:center}
        .estrategia-card:hover{border-color:{{COR_DESTAQUE}}}
        .estrategia-card.ativa{border-color:#00ff88;box-shadow:0 0 15px rgba(0,255,136,0.3);background:#0a1a0a}
        .estrategia-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:8px}
        .badge-gratis{background:#00ff88;color:#000;font-size:9px;padding:2px 6px;border-radius:10px;display:inline-block}
        .badge-pago{background:#ffd700;color:#000;font-size:9px;padding:2px 6px;border-radius:10px;display:inline-block}
    
.sub-tabs{display:flex;gap:5px;margin-bottom:15px}
.sub-tab{padding:8px 16px;background:#111;border:1px solid #333;border-radius:8px 8px 0 0;cursor:pointer;color:#888;font-size:11px}
.sub-tab.active{background:linear-gradient(135deg,#cc8800,#ffd700);color:#000;font-weight:bold;border-color:#ffd700}
.sub-tab:hover{background:#1a1a2e;color:#fff}
.sub-panel{display:none}
.sub-panel.active{display:block}

        /* 🎨 LOJA PREMIUM - NOVO DESIGN */
        .loja-container{padding:10px 0}
        .loja-titulo{text-align:center;color:{{COR_DESTAQUE}};font-size:16px;margin-bottom:15px;text-shadow:0 0 20px {{COR_TAB_ATIVA}};letter-spacing:2px}
        .planos-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:10px;padding:5px}
        .plano-card{background:linear-gradient(180deg,#1a1a2e 0%,#0d0d1a 100%);padding:15px 10px;border-radius:16px;border:1px solid #333;text-align:center;cursor:pointer;transition:all .3s cubic-bezier(.4,0,.2,1);position:relative;overflow:hidden;animation:fadeInUp .5s ease backwards}
        .plano-card:nth-child(1){animation-delay:.1s}
        .plano-card:nth-child(2){animation-delay:.2s}
        .plano-card:nth-child(3){animation-delay:.3s}
        .plano-card:nth-child(4){animation-delay:.4s}
        .plano-card:nth-child(5){animation-delay:.5s}
        .plano-card:hover{transform:translateY(-6px);border-color:{{COR_DESTAQUE}};box-shadow:0 12px 30px rgba(255,215,0,.2),0 0 60px rgba(255,215,0,.05)}
        .plano-card.selecionado{border-color:#ffd700!important;box-shadow:0 0 30px rgba(255,215,0,.5),inset 0 0 30px rgba(255,215,0,.05);background:linear-gradient(180deg,#2a2a1e 0%,#1a1a0d 100%)}
        .plano-card.selecionado::before{content:'';position:absolute;top:-50%;left:-50%;width:200%;height:200%;background:radial-gradient(circle,rgba(255,215,0,.1) 0%,transparent 70%);animation:rotate 4s linear infinite}
        .plano-icone{font-size:28px;margin-bottom:6px;filter:drop-shadow(0 0 8px {{COR_DESTAQUE}})}
        .plano-nome{color:{{COR_DESTAQUE}};font-weight:bold;font-size:12px;margin-bottom:4px;text-transform:uppercase;letter-spacing:1px}
        .plano-moedas{font-size:28px;font-weight:bold;background:linear-gradient(180deg,#ffd700,#ff8c00);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:5px 0}
        .plano-preco{font-size:16px;color:#00ff88;font-weight:bold}
        .plano-badge{position:absolute;top:10px;right:10px;background:linear-gradient(135deg,#ff4444,#ff6600);color:#fff;font-size:8px;padding:3px 8px;border-radius:12px;font-weight:bold;animation:pulse 2s infinite}
        .skin-card{background:linear-gradient(180deg,#1a102a 0%,#0d0a1a 100%);padding:15px 10px;border-radius:16px;border:1px solid #333;text-align:center;cursor:pointer;transition:all .3s ease;position:relative;overflow:hidden;animation:fadeInUp .4s ease backwards}
        .skin-card:hover{transform:translateY(-5px);border-color:#9933ff;box-shadow:0 10px 25px rgba(153,51,255,.2)}
        .skin-card.ativo{border-color:#00ff88!important;box-shadow:0 0 25px rgba(0,255,136,.3),inset 0 0 20px rgba(0,255,136,.03)}
        .skin-icone{font-size:30px;margin-bottom:5px}
        .skin-nome{color:#cc66ff;font-weight:bold;font-size:13px;margin-bottom:4px}
        .skin-desc{color:#888;font-size:9px;margin-bottom:8px;line-height:1.3}
        .btn-loja{padding:10px 16px;border:none;border-radius:10px;font-weight:bold;cursor:pointer;font-size:11px;width:100%;transition:all .2s ease;text-transform:uppercase;letter-spacing:1px}
        .btn-comprar-volts{background:linear-gradient(135deg,#ff8c00,#ffd700);color:#000;box-shadow:0 4px 15px rgba(255,215,0,.3)}
        .btn-comprar-volts:hover{transform:scale(1.03);box-shadow:0 6px 20px rgba(255,215,0,.5)}
        .btn-comprar-skin{background:linear-gradient(135deg,#6600cc,#9933ff);color:#fff;box-shadow:0 4px 15px rgba(153,51,255,.3)}
        .btn-comprar-skin:hover{transform:scale(1.03);box-shadow:0 6px 20px rgba(153,51,255,.5)}
        .btn-comprar-est{background:linear-gradient(135deg,#006644,#00aa55);color:#fff;box-shadow:0 4px 15px rgba(0,170,85,.3)}
        .btn-comprar-est:hover{transform:scale(1.03);box-shadow:0 6px 20px rgba(0,170,85,.5)}
        .btn-comprado{background:linear-gradient(135deg,#222,#333);color:#00ff88;border:1px solid #00ff88;cursor:default;box-shadow:0 0 10px rgba(0,255,136,.1)}
        .badge-preco{display:inline-block;padding:4px 10px;border-radius:10px;font-size:9px;font-weight:bold;margin:5px 0}
        .badge-gratis{background:#00ff8822;color:#00ff88;border:1px solid #00ff8844}
        .badge-pago{background:#ffd70022;color:#ffd700;border:1px solid #ffd70044}
        .badge-destaque{position:absolute;top:8px;left:8px;background:linear-gradient(135deg,#ffd700,#ff8c00);color:#000;font-size:7px;padding:3px 8px;border-radius:8px;font-weight:bold}
        @keyframes fadeInUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
        @keyframes rotate{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}
        @keyframes pulse{0%,100%{opacity:1}50%{opacity:.6}}
        @keyframes brilho{0%,100%{box-shadow:0 0 5px {{COR_DESTAQUE}}}50%{box-shadow:0 0 20px {{COR_DESTAQUE}},0 0 40px {{COR_TAB_ATIVA}}}}

    
        /* ═══════════════ LOJA PREMIUM V5 ═══════════════ */
        .planos-grid,.skins-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;padding:8px}
        
        .plano-card,.skin-card{background:linear-gradient(180deg,#111122 0%,#0a0a15 100%);padding:18px 14px;border-radius:18px;border:2px solid #1a1a2e;text-align:center;cursor:pointer;transition:all .35s cubic-bezier(.4,0,.2,1);position:relative;overflow:hidden}
        .plano-card::before,.skin-card::before{content:'';position:absolute;top:0;left:-100%;width:100%;height:100%;background:linear-gradient(90deg,transparent,rgba(255,215,0,.03),transparent);transition:left .6s ease}
        .plano-card:hover::before,.skin-card:hover::before{left:100%}
        .plano-card:hover,.skin-card:hover{transform:translateY(-8px);border-color:{{COR_DESTAQUE}};box-shadow:0 15px 35px rgba(0,0,0,.5),0 0 50px rgba(255,215,0,.08)}
        .plano-card.selecionado,.skin-card.selecionado{border-color:#ffd700!important;box-shadow:0 0 35px rgba(255,215,0,.4),inset 0 0 25px rgba(255,215,0,.03);background:linear-gradient(180deg,#1a1a0a 0%,#0d0d05 100%)}
        .skin-card.ativo{border-color:#00ff88!important;box-shadow:0 0 30px rgba(0,255,136,.35),inset 0 0 20px rgba(0,255,136,.03);background:linear-gradient(180deg,#0a1a0a 0%,#050d05 100%)}
        .plano-card.selecionado::after{content:'✨';position:absolute;top:8px;right:12px;font-size:14px;animation:float 1.5s ease-in-out infinite}
        @keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}
        
        .plano-icone,.skin-icone{font-size:35px;margin-bottom:8px;display:block;filter:drop-shadow(0 0 12px {{COR_DESTAQUE}})}
        .plano-nome,.skin-nome{color:{{COR_DESTAQUE}};font-weight:bold;font-size:13px;margin-bottom:4px;text-transform:uppercase;letter-spacing:1px}
        .plano-moedas{font-size:32px;font-weight:900;background:linear-gradient(180deg,#ffd700,#ff8c00);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:8px 0}
        .plano-preco{font-size:17px;color:#00ff88;font-weight:bold;margin:4px 0}
        .plano-desc,.skin-desc{color:#666;font-size:9px;margin:6px 0;line-height:1.4}
        .plano-tag{background:rgba(255,215,0,.1);color:{{COR_DESTAQUE}};font-size:8px;padding:3px 10px;border-radius:10px;display:inline-block;margin:4px 0}
        .plano-desconto{background:linear-gradient(135deg,#ff4444,#ff6600);color:#fff;font-size:8px;padding:3px 8px;border-radius:10px;display:inline-block;margin-left:4px;animation:pulse 2s infinite}
        
        .badge-gratis{background:rgba(0,255,136,.1);color:#00ff88;border:1px solid rgba(0,255,136,.3);padding:5px 12px;border-radius:12px;font-size:9px;font-weight:bold;display:inline-block}
        .badge-pago{background:rgba(255,215,0,.1);color:#ffd700;border:1px solid rgba(255,215,0,.3);padding:5px 12px;border-radius:12px;font-size:9px;font-weight:bold;display:inline-block}
        
        .btn-loja{padding:12px 18px;border:none;border-radius:12px;font-weight:bold;cursor:pointer;font-size:11px;width:100%;margin-top:10px;transition:all .25s ease;text-transform:uppercase;letter-spacing:1.5px;position:relative;overflow:hidden}
        .btn-loja::after{content:'';position:absolute;top:0;left:-100%;width:100%;height:100%;background:linear-gradient(90deg,transparent,rgba(255,255,255,.15),transparent);transition:left .5s ease}
        .btn-loja:hover::after{left:100%}
        .btn-comprar-volts{background:linear-gradient(135deg,#ff8c00,#ffd700);color:#000;box-shadow:0 5px 20px rgba(255,215,0,.25)}
        .btn-comprar-volts:hover{transform:translateY(-2px);box-shadow:0 8px 25px rgba(255,215,0,.45)}
        .btn-comprar-skin{background:linear-gradient(135deg,#6a0dad,#9933ff);color:#fff;box-shadow:0 5px 20px rgba(153,51,255,.25)}
        .btn-comprar-skin:hover{transform:translateY(-2px);box-shadow:0 8px 25px rgba(153,51,255,.45)}
        .btn-comprar-est{background:linear-gradient(135deg,#006644,#00aa55);color:#fff;box-shadow:0 5px 20px rgba(0,170,85,.25)}
        .btn-comprar-est:hover{transform:translateY(-2px);box-shadow:0 8px 25px rgba(0,170,85,.45)}
        .btn-comprado{background:linear-gradient(135deg,#1a1a2e,#0d0d1a);color:#00ff88;border:1px solid #00ff8844;cursor:default;box-shadow:0 0 12px rgba(0,255,136,.08)}
        .btn-usar{background:linear-gradient(135deg,#006699,#3399cc);color:#fff;box-shadow:0 5px 20px rgba(51,153,204,.25)}
        .btn-usar:hover{transform:translateY(-2px);box-shadow:0 8px 25px rgba(51,153,204,.45)}
        
        .sub-tabs{display:flex;gap:8px;margin-bottom:18px;flex-wrap:wrap}
        .sub-tab{padding:10px 18px;background:#111;border:2px solid #222;border-radius:12px 12px 0 0;cursor:pointer;color:#666;font-size:11px;font-weight:bold;transition:all .3s ease}
        .sub-tab:hover{background:#1a1a2e;color:#ccc;border-color:#333}
        .sub-tab.active{background:linear-gradient(135deg,#1a1a0a,#0d0d05);color:{{COR_DESTAQUE}};border-color:{{COR_DESTAQUE}};box-shadow:0 -3px 15px rgba(255,215,0,.1)}
        .sub-panel{display:none;animation:fadeIn .4s ease}
        .sub-panel.active{display:block}
        @keyframes fadeIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
        @keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}

    }
        

    </style>
</head>
<body>
<div class="container">
    <div class="header">
        {{HEADER_EXTRA}}
        <h1>⚡ TESLA 369 BOT ⚡</h1>
        
        
    </div>
    <div class="mantra">🌀 O DINHEIRO VEM ATÉ MIM DE TODOS OS LADOS 🌀</div>
    <div class="tabs">
        <div class="tab active" onclick="openTab('bot')">🤖 BOT</div>
        <div class="tab" onclick="openTab('relatorio')">📊 RELATÓRIO</div>
        <div class="tab" onclick="openTab('estrategias')">📊 ESTRATÉGIAS</div>
        <div class="tab" onclick="openTab('loja')">🛍️ LOJA</div>
        <div class="tab" onclick="openTab('chat')">💬 CHAT</div>
        <div class="tab" onclick="openTab('leia-me')">📖 TUTORIAL & LEIA-ME</div>
    </div>
    
    <div class="panel active" id="panel-bot">
        <div class="config-section"><h3>🔐 IQ OPTION</h3><div class="config-row">
            <input type="email" id="email" placeholder="📧 Email IQ Option" style="flex:2">
            <input type="password" id="senha" placeholder="🔒 Senha" style="flex:1">
            <select id="tipo"><option value="PRACTICE">🧪</option><option value="REAL">💰</option></select>
            <div style="margin-top:5px;display:flex;gap:8px;align-items:center">
            <label style="color:#888;font-size:9px">% Banca:</label>
            <select id="percentualBanca" onchange="atualizarPercentual()" style="padding:5px;background:#111;border:1px solid #333;border-radius:5px;color:#fff;font-size:10px;width:70px">
                <option value="15" selected>15%</option><option value="20">20%</option><option value="30">30%</option><option value="50">50%</option><option value="100">100%</option>
            </select>
            <span style="color:#ffd700;font-size:9px" id="valorEstimado">($0.00)</span>
            <span style="color:#ff4444;font-size:8px" id="avisoMinimo"></span>
        </div>
            <button class="btn btn-info" id="btnConectar" onclick="conectarIQ()">🔌 CONECTAR</button>
            <button class="btn btn-stop" id="btnDesconectar" onclick="desconectarIQ()" style="display:none">🔌 DESCONECTAR</button>
            <button class="btn btn-start" id="btnOperar" onclick="comecarOperar()" style="display:none">🚀 COMEÇAR OPERAR</button>
            <button class="btn btn-stop" id="btnParar" onclick="pararBot()" style="display:none">⏹️ PARAR</button>
        </div></div>
        <div class="dashboard">
            <div class="card"><div class="label">💰 BANCA</div><div class="value" id="banca" style="color:#00ff88">--</div></div>
            <div class="card"><div class="label">📈 LUCRO</div><div class="value" id="lucro">$0.00</div></div>
            <div class="card"><div class="label">🎯 OPS</div><div class="value" id="ops">0</div></div>
            <div class="card"><div class="label">⚡ VOLTS</div><div class="value" id="moedasSaldo">0</div></div>
            <div class="card"><div class="label">📊 ESTRATÉGIA</div><div class="value" id="estrategiaAtiva" style="font-size:10px">--</div></div>
            <div class="card"><div class="label">🔮 SINAL</div><div class="value" id="sinal" style="font-size:11px">--</div></div>
        </div>
        <div class="indicators">
            <div class="ind-card"><div class="ind-label">📊 RSI</div><div class="ind-value" id="rsi">--</div></div>
            <div class="ind-card"><div class="ind-label">📈 MM5</div><div class="ind-value" id="mm5">--</div></div>
            <div class="ind-card"><div class="ind-label">📈 MM10</div><div class="ind-value" id="mm10">--</div></div>
            <div class="ind-card"><div class="ind-label">📉 MM20</div><div class="ind-value" id="mm20">--</div></div>
            <div class="ind-card"><div class="ind-label">📊 ESTOC</div><div class="ind-value" id="stoch">--</div></div>
            <div class="ind-card"><div class="ind-label">🌅 FASE</div><div class="ind-value" id="fase">--</div></div>
            <div class="ind-card"><div class="ind-label">💵 PREÇO</div><div class="ind-value" id="preco">--</div></div>
        </div>
        <div class="terminal" id="terminal">📡 Aguardando...</div>
        <div class="barra-status">
            <span><span class="status-dot inactive" id="statusDot"></span> <span id="statusTexto">⏸️ Desconectado</span></span>
            <span>⚡ TESLA 369</span>
            <span>v6.5.2 | GALE 2 | SG: 1 WIN | 🔄 Bot roda em background</span>
        </div>
    </div>
    
    <div class="panel" id="panel-estrategias">
        <div class="config-section"><h3>📊 SELECIONAR ESTRATÉGIA</h3><p style="color:#888;font-size:10px">Escolha antes de clicar em COMEÇAR OPERAR</p></div>
        <div class="estrategia-grid" id="estrategiaGrid"></div>
    </div>
    
    <div class="panel" id="panel-loja">
        <div class="sub-tabs">
            <div class="sub-tab active" id="sub-tab-moedas" onclick="mostrarSubAba('moedas')">COMPRAR VOLTS</div>
            <div class="sub-tab" id="sub-tab-skins" onclick="mostrarSubAba('skins')">LOJA DE SKINS</div>
            <div class="sub-tab" id="sub-tab-estrategias" onclick="mostrarSubAba('estrategias')">LOJA DE ESTRATÉGIAS</div>
        </div>
        <div class="sub-panel active" id="sub-panel-moedas">
            <div class="config-section"><h3>💳 COMPRAR VOLTS COM PIX</h3><p style="color:#888;font-size:10px">📧 <input type="email" id="emailCompra" placeholder="Seu email" style="width:220px;padding:6px;background:#111;border:1px solid #333;color:#fff;border-radius:5px"></p><p style="color:#ffd700;font-size:10px;margin-top:5px">⚡ 1 VOLT = 1 ciclo | +1 VOLT grátis/dia</p><p style="color:#888;font-size:9px;margin-top:3px">⭐ Selecione o plano e pague com PIX</p></div>
        <div class="planos-grid">'''

def processar_html_com_skin():
    skin = next((s for s in SKINS if s['id'] == skin_atual_global), SKINS[0])
    html = HTML
    html = html.replace('{{COR_FUNDO}}', skin['cor_fundo'])
    html = html.replace('{{COR_PANEL}}', skin['cor_panel'])
    html = html.replace('{{COR_DESTAQUE}}', skin['cor_destaque'])
    html = html.replace('{{COR_TEXTO}}', skin['cor_texto'])
    html = html.replace('{{COR_BOTAO}}', skin['cor_botao'])
    html = html.replace('{{COR_TAB_ATIVA}}', skin['cor_tab_ativa'])
    html = html.replace('{{COR_HEADER_BG}}', skin['cor_header_bg'])
    html = html.replace('{{COR_HEADER_BORDA}}', skin['cor_header_borda'])
    html = html.replace('{{CSS_EXTRA}}', skin.get('css_extra', ''))
    html = html.replace('{{HEADER_EXTRA}}', skin.get('header_extra', '<div class="lightning"></div>'))
    return html

# ═══════════ ROTAS ═══════════
@app.route('/')
def index(): return render_template_string(processar_html_com_skin())

@app.route('/status')
def status():
    u = carregar_usuario(email_usuario_atual) if email_usuario_atual else {}
    skins_status = []
    skins_compradas = u.get('skins_compradas', ['skin_padrao']) if u else ['skin_padrao']
    skin_atual = u.get('skin_atual', 'skin_padrao') if u else 'skin_padrao'
    for skin in SKINS:
        skins_status.append({'id': skin['id'], 'nome': skin['nome'], 'desc': skin['desc'], 'preco_moedas': skin['preco_moedas'], 'categoria': skin.get('categoria','basica'), 'comprado': skin['id'] in skins_compradas, 'ativo': skin['id'] == skin_atual})
    estrategias_compradas = u.get('estrategias_compradas', ['tesla_369']) if u else ['tesla_369']
    estrategias_disponiveis = {k: {'nome': v['nome'], 'desc': v['desc'], 'preco_moedas': v.get('preco_moedas',0), 'gratis': v.get('gratis',False)} for k,v in ESTRATEGIAS.items()}
    return jsonify({'conectado': conectado_iq, 'rodando': bot_rodando, 'email': email_usuario_atual, 'banca': API.get_balance() if API else 0, 'lucro': lucro, 'ops': NumDeOperacoes, 'sinal': ultimo_sinal, 'analise': ultima_analise, 'logs': get_logs_html(40), 'moedas': u.get('moedas',0) if u else 0, 'estrategia': estrategia_atual, 'estrategia_nome': ESTRATEGIAS.get(estrategia_atual,{}).get('nome','--'), 'skin_id': skin_atual, 'skins_status': skins_status, 'estrategias_compradas': estrategias_compradas, 'estrategias_disponiveis': estrategias_disponiveis})

@app.route('/conectar', methods=['POST'])
def conectar():
    global API, email_usuario_atual, conectado_iq, skin_atual_global, par, timeframe_atual
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
        if 'estrategias_compradas' not in usuario: usuario['estrategias_compradas'] = []
        salvar_usuario(email, usuario)
        par = ESTRATEGIAS[estrategia_atual]['pares'][0]
        timeframe_atual = ESTRATEGIAS[estrategia_atual]['timeframe']
        add_log(f'✅ Conectado! ${API.get_balance():.2f} | ⚡ {usuario.get("moedas", 0)} VOLTS', 'win')
        return jsonify({'ok': True, 'moedas': usuario.get('moedas', 0)})
    except Exception as e: return jsonify({'ok': False, 'erro': str(e)[:100]})

@app.route('/comecar_operar', methods=['POST'])
def comecar_operar():
    global bot_rodando, bot_thread, lucro, NumDeOperacoes
    try:
        if not conectado_iq: return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
        usuario = carregar_usuario(email_usuario_atual)
        if not usuario: return jsonify({'ok': False, 'erro': 'Usuário não encontrado!'})
        if estrategia_atual not in usuario.get('estrategias_compradas', ['tesla_369']):
            preco = ESTRATEGIAS.get(estrategia_atual, {}).get('preco_moedas', 0)
            return jsonify({'ok': False, 'erro': f'Estratégia não comprada! Compre na loja por {preco} ⚡'})
        if usuario.get('moedas', 0) < 1: return jsonify({'ok': False, 'erro': 'Sem VOLTS!'})
        usuario['moedas'] -= 1; usuario['total_ciclos'] += 1
        salvar_usuario(email_usuario_atual, usuario)
        lucro = 0.0; NumDeOperacoes = 0
        if not bot_rodando:
            bot_rodando = True
            bot_thread = threading.Thread(target=bot_loop, daemon=True)
            bot_thread.start()
            bots_ativos[email_usuario_atual] = bot_thread
        return jsonify({'ok': True, 'moedas': usuario['moedas']})
    except Exception as e: return jsonify({'ok': False, 'erro': str(e)[:100]})

@app.route('/parar', methods=['POST'])
def parar():
    global bot_rodando, conectado_iq
    data = request.json or {}
    bot_rodando = False
    if data.get('desconectar'): conectado_iq = False
    return jsonify({'ok': True})

@app.route('/selecionar_estrategia', methods=['POST'])
def selecionar_estrategia():
    global estrategia_atual, par, timeframe_atual
    d = request.get_json()
    est_key = d.get('estrategia', 'tesla_369')
    if est_key in ESTRATEGIAS:
        estrategia_atual = est_key
        par = ESTRATEGIAS[est_key]['pares'][0]
        timeframe_atual = ESTRATEGIAS[est_key]['timeframe']
        return jsonify({'ok': True})
    return jsonify({'ok': False})

@app.route('/comprar_estrategia', methods=['POST'])
def comprar_estrategia():
    if not email_usuario_atual: return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    estrategia_id = request.json.get('estrategia_id','')
    if estrategia_id not in ESTRATEGIAS: return jsonify({'ok': False, 'erro': 'Estratégia inválida!'})
    est = ESTRATEGIAS[estrategia_id]
    u = carregar_usuario(email_usuario_atual) or criar_usuario(email_usuario_atual)
    if est.get('gratis', False):
        if 'estrategias_compradas' not in u: u['estrategias_compradas'] = []
        if estrategia_id not in u['estrategias_compradas']:
            u['estrategias_compradas'].append(estrategia_id)
            salvar_usuario(email_usuario_atual, u)
        return jsonify({'ok': True, 'msg': f'Estratégia {est["nome"]} ativada gratuitamente!', 'moedas': u.get('moedas',0)})
    if estrategia_id in u.get('estrategias_compradas', []): return jsonify({'ok': False, 'erro': 'Estratégia já comprada!'})
    preco = est.get('preco_moedas', 3)
    if u['moedas'] < preco: return jsonify({'ok': False, 'erro': f'VOLTS insuficientes! Precisa de {preco} ⚡'})
    u['moedas'] -= preco
    if 'estrategias_compradas' not in u: u['estrategias_compradas'] = ['tesla_369']
    u['estrategias_compradas'].append(estrategia_id)
    salvar_usuario(email_usuario_atual, u)
    return jsonify({'ok': True, 'msg': f'Estratégia {est["nome"]} comprada!', 'moedas': u['moedas']})

@app.route('/comprar_skin', methods=['POST'])
def comprar_skin():
    global skin_atual_global
    if not email_usuario_atual: return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    skin_id = request.json.get('skin_id','')
    skin = next((s for s in SKINS if s['id'] == skin_id), None)
    if not skin: return jsonify({'ok': False, 'erro': 'Skin não encontrada'})
    usuario = carregar_usuario(email_usuario_atual) or criar_usuario(email_usuario_atual)
    if skin['preco_moedas'] == 0:
        if 'skins_compradas' not in usuario: usuario['skins_compradas'] = ['skin_padrao']
        if skin_id not in usuario['skins_compradas']: usuario['skins_compradas'].append(skin_id)
        usuario['skin_atual'] = skin_id; salvar_usuario(email_usuario_atual, usuario); skin_atual_global = skin_id
        return jsonify({'ok': True, 'moedas': usuario.get('moedas',0), 'msg': 'Skin grátis ativada!'})
    if skin_id in usuario.get('skins_compradas', []):
        usuario['skin_atual'] = skin_id; salvar_usuario(email_usuario_atual, usuario); skin_atual_global = skin_id
        return jsonify({'ok': True, 'moedas': usuario['moedas'], 'msg': 'Skin já comprada! Ativada.'})
    if usuario.get('moedas',0) < skin['preco_moedas']: return jsonify({'ok': False, 'erro': f'VOLTS insuficientes! Precisa de {skin["preco_moedas"]} ⚡'})
    usuario['moedas'] -= skin['preco_moedas']
    if 'skins_compradas' not in usuario: usuario['skins_compradas'] = ['skin_padrao']
    usuario['skins_compradas'].append(skin_id); usuario['skin_atual'] = skin_id
    salvar_usuario(email_usuario_atual, usuario); skin_atual_global = skin_id
    return jsonify({'ok': True, 'moedas': usuario['moedas'], 'msg': f'Skin {skin["nome"]} comprada e ativada!'})

@app.route('/ativar_skin', methods=['POST'])
def ativar_skin():
    global skin_atual_global
    if not email_usuario_atual: return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    skin_id = request.json.get('skin_id','')
    usuario = carregar_usuario(email_usuario_atual)
    if not usuario: return jsonify({'ok': False, 'erro': 'Usuário não encontrado'})
    usuario['skin_atual'] = skin_id; salvar_usuario(email_usuario_atual, usuario); skin_atual_global = skin_id
    return jsonify({'ok': True})

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
            email = pagamentos_pendentes[pix_id]['email']; moedas = pagamentos_pendentes[pix_id]['moedas']
            usuario = carregar_usuario(email) or criar_usuario(email)
            usuario['moedas'] = usuario.get('moedas',0) + moedas; salvar_usuario(email, usuario)
            return jsonify({'pago': True, 'moedas': moedas, 'saldo': usuario['moedas']})
        return jsonify({'pago': True})
    return jsonify({'pago': False})

@app.route('/chat_enviar', methods=['POST'])
def chat_enviar():
    data = request.json
    nome, msg = data.get('nome','Anonimo')[:15], data.get('msg','')[:200]
    if not msg: return jsonify({'ok': False})
    try:
        requests.post(f'{FB_URL}/chat.json', json={'nome': nome, 'msg': msg, 'hora': datetime.now().strftime('%H:%M')})
        r_chat = requests.get(f'{FB_URL}/chat.json?orderBy="$key"&limitToLast=51')
        if r_chat.status_code == 200 and r_chat.json():
            dados = r_chat.json()
            if len(dados) > 50:
                for chave in sorted(dados.keys())[:-50]: requests.delete(f'{FB_URL}/chat/{chave}.json')
    except: pass
    return jsonify({'ok': True})

@app.route('/chat_mensagens')
def chat_mensagens():
    try:
        r = requests.get(f'{FB_URL}/chat.json?orderBy="$key"&limitToLast=50')
        mensagens = list(r.json().values()) if r.status_code == 200 and r.json() else []
        return jsonify({'mensagens': mensagens, 'online': 1})
    except: return jsonify({'mensagens': [], 'online': 1})

@app.route('/ranking')
def ranking():
    ranking_list = []
    try:
        r = requests.get(f'{FB_URL}/usuarios.json')
        usuarios = r.json() if r.status_code == 200 else {}
        if usuarios:
            for key, user_data in usuarios.items():
                if user_data:
                    ranking_list.append({'email': user_data.get('email','N/A')[:20]+'...', 'lucro_total': round(user_data.get('lucro_total',0),2), 'total_wins': user_data.get('total_wins',0), 'total_losses': user_data.get('total_losses',0), 'total_ciclos': user_data.get('total_ciclos',0), 'taxa': round((user_data.get('total_wins',0)/max(user_data.get('total_ciclos',1),1))*100,1), 'banca_atual': round(user_data.get('banca_atual',0),2)})
    except: pass
    ranking_list.sort(key=lambda x: x['lucro_total'], reverse=True)
    total_ops = sum(u['total_ciclos'] for u in ranking_list)
    total_wins = sum(u['total_wins'] for u in ranking_list)
    taxa_global = round((total_wins/max(total_ops,1))*100,1) if total_ops>0 else 0
    return jsonify({'ranking': ranking_list[:20], 'stats': {'total_usuarios': len(ranking_list), 'total_ops': total_ops, 'total_wins': total_wins, 'taxa_global': taxa_global}})

@app.route('/relatorio')
def relatorio():
    email = request.args.get('email','')
    if not email: return jsonify({'erro': 'Email obrigatório'})
    u = carregar_usuario(email)
    return jsonify(u if u else {'erro': 'Não encontrado'})

@app.route('/resetar', methods=['POST'])
def resetar():
    email = request.json.get('email','')
    usuario = carregar_usuario(email)
    if not usuario: return jsonify({'ok': False, 'msg': 'Usuário não encontrado'})
    moedas = usuario.get('moedas',0)
    usuario['total_wins'] = usuario['total_losses'] = usuario['total_ciclos'] = 0
    usuario['total_gasto'] = usuario['total_ganho'] = usuario['lucro_total'] = 0.0
    usuario['historico_operacoes'] = []; usuario['dias_ativos'] = 0
    usuario['moedas'] = moedas
    salvar_usuario(email, usuario)
    return jsonify({'ok': True, 'msg': '✅ Resetado!'})

@app.route('/set_percentual', methods=['POST'])
def set_percentual():
    global PERCENTUAL_BANCA
    PERCENTUAL_BANCA = request.json.get('percentual', 10)
    return jsonify({'ok': True})

# ═══════════ INICIAR ═══════════
print("⚡ TESLA 369 v6.5.2 - Estrutura Modular")
print(f"📁 Skins: {len(SKINS)} | 📊 Estratégias: {len(ESTRATEGIAS)}")

if __name__ == '__main__':
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
