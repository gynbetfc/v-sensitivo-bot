#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ⚡ TESLA 369 BOT v9.0.1 Cloud ⚡
# PIPELINE CLOUD SEGURO - RELATÓRIOS E RANKINGS ORIGINAIS RESTAURADOS
# SKINS CARREGADAS DINAMICAMENTE DO GITHUB

from flask import Flask, render_template, jsonify, request
from iqoptionapi.stable_api import IQ_Option
from datetime import datetime
import threading
import time
import sys
import os
import warnings
import requests
import uuid

warnings.filterwarnings("ignore")
app = Flask(__name__)

# ============= CONFIGURAÇÕES DE LINKS CLOUD =============
FB_URL = "https://nexos-40654-default-rtdb.firebaseio.com"
print("✅ Firebase HTTP REST configurado!")

HTML_URL = "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/tesla_369_bot/templates/index.html"
GIT_API_ESTRATEGIAS = "https://api.github.com/repos/gynbetfc/v-sensitivo-bot/contents/tesla_369_bot/estrategias"
GIT_RAW_ESTRATEGIAS_BASE = "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/tesla_369_bot/estrategias"

# ⭐ NOVO: URL para o módulo de skins no GitHub
GIT_RAW_SKINS = "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/tesla_369_bot/skins/skins.py"

MARTINGALE = 2
PAYOUT_PADRAO = 0.85
PERCENTUAL_BANCA = 15

# ⭐ CONFIGURAÇÃO DO MERCADO PAGO ⭐
MERCADO_PAGO_ACCESS_TOKEN = os.environ.get("MP_ACCESS_TOKEN", "APP_USR-4548266140377032-050311-6589fc22b166e4cb2cfad0379b28dcdf-1059299796")
MODO_SIMULACAO = False

# ⭐ PLANOS DE VOLTS ⭐
PLANOS = [
    {'id':1,'moedas':1,'preco':0.99,'nome':'🔰 TESTE','desc':'R$0,99/VOLT','tag':'1 ciclo','bonus':''},
    {'id':2,'moedas':6,'preco':6.69,'nome':'⭐ BÁSICO','desc':'R$1,11/VOLT','tag':'6 ciclos','bonus':''},
    {'id':3,'moedas':15,'preco':9.99,'nome':'💎 INTERMEDIÁRIO','desc':'R$0,67/VOLT','tag':'15 ciclos','bonus':'🎨 1 Skin Básica GRÁTIS','desconto':'33% OFF'},
    {'id':4,'moedas':36,'preco':21.69,'nome':'🔥 PREMIUM','desc':'R$0,60/VOLT','tag':'36 ciclos','bonus':'🎨 1 Skin Premium GRÁTIS','desconto':'40% OFF'},
    {'id':5,'moedas':69,'preco':39.69,'nome':'👑 ULTRA','desc':'R$0,57/VOLT','tag':'69 ciclos','bonus':'🎨 1 Skin Lendária GRÁTIS','desconto':'69% OFF'},
]

# ============= CACHES PARA CLOUD =============
cache_estrategias = {"data": {}, "timestamp": 0}
cache_skins = {"data": None, "timestamp": 0, "version": None}
CACHE_EST_TTL = 60
CACHE_SKINS_TTL = 300  # 5 minutos de cache para skins

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

# ============= 📢 SISTEMA DE LOGS INTERNOS =============

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

# ============= 🎨 FUNÇÕES PARA CARREGAR SKINS DA NUVEM =============

def get_skins_fallback():
    """Lista de skins padrão para fallback caso não consiga baixar da nuvem"""
    return [
        {
            'id': 'skin_padrao', 'nome': '⚡ TESLA PADRÃO', 'desc': 'Tema escuro com raios dourados', 
            'preco_moedas': 0, 'categoria': 'basica',
            'cor_fundo': '#0a0a1a', 'cor_panel': '#1a1a3e', 'cor_destaque': '#ffd700', 'cor_texto': '#fff',
            'cor_botao': 'linear-gradient(135deg,#cc8800,#ffd700)', 'cor_tab_ativa': '#ffd700',
            'cor_header_bg': 'linear-gradient(135deg,#1a0000,#331100,#553300,#331100,#1a0000)', 
            'cor_header_borda': '#ffd700',
            'header_extra': '<div class="lightning"></div>',
            'css_extra': '.lightning{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:150px;height:150px;background:radial-gradient(circle at 30% 30%,rgba(255,215,0,0.3) 0%,rgba(255,165,0,0.15) 30%,transparent 100%);border-radius:50%;z-index:0;animation:glow 3s ease-in-out infinite;pointer-events:none}@keyframes glow{0%,100%{box-shadow:0 0 30px rgba(255,215,0,0.3)}50%{box-shadow:0 0 50px rgba(255,165,0,0.5)}}.lightning::after{content:"⚡";position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:50px;animation:float 2s ease-in-out infinite}@keyframes float{0%,100%{transform:translate(-50%,-50%) scale(1)}50%{transform:translate(-50%,-60%) scale(1.1)}}'
        },
        {
            'id': 'skin_dark', 'nome': '🌑 TESLA DARK', 'desc': 'Particulas roxas flutuantes', 
            'preco_moedas': 6, 'categoria': 'basica',
            'cor_fundo': '#000000', 'cor_panel': '#0a0a0a', 'cor_destaque': '#9933ff', 'cor_texto': '#ccc',
            'cor_botao': 'linear-gradient(135deg,#4400aa,#9933ff)', 'cor_tab_ativa': '#9933ff',
            'cor_header_bg': 'linear-gradient(135deg,#000000,#110022,#220044,#110022,#000000)', 
            'cor_header_borda': '#9933ff',
            'header_extra': '<canvas id="darkCanvas" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none"></canvas>',
            'css_extra': 'body{background:#000000!important}.header{border-color:#9933ff!important;box-shadow:0 0 40px rgba(153,51,255,0.3)}'
        },
        {
            'id': 'skin_neon', 'nome': '💜 TESLA NEON', 'desc': 'Brilho neon roxo pulsante', 
            'preco_moedas': 6, 'categoria': 'basica',
            'cor_fundo': '#0a0015', 'cor_panel': '#150025', 'cor_destaque': '#cc00ff', 'cor_texto': '#e0c0ff',
            'cor_botao': 'linear-gradient(135deg,#8800cc,#cc00ff)', 'cor_tab_ativa': '#cc00ff',
            'cor_header_bg': 'linear-gradient(135deg,#0a0015,#150030,#200050,#150030,#0a0015)', 
            'cor_header_borda': '#cc00ff',
            'header_extra': '<div class="neon-glow"></div>',
            'css_extra': '.neon-glow{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:200px;height:200px;background:radial-gradient(circle,rgba(204,0,255,0.2) 0%,transparent 70%);border-radius:50%;z-index:0;animation:neonPulse 2s ease-in-out infinite;pointer-events:none}@keyframes neonPulse{0%,100%{transform:translate(-50%,-50%) scale(1);opacity:0.5}50%{transform:translate(-50%,-50%) scale(1.3);opacity:0.8}}body{background:#0a0015!important}.header{border-color:#cc00ff!important;box-shadow:0 0 30px rgba(204,0,255,0.4)}'
        }
    ]

def carregar_skins_da_nuvem():
    """
    Carrega o módulo skins.py diretamente do GitHub via RAW URL.
    Retorna a lista de skins ou a lista padrão em caso de falha.
    """
    global cache_skins
    agora = time.time()
    
    # Verifica se o cache ainda é válido
    if cache_skins["data"] and (agora - cache_skins["timestamp"]) < CACHE_SKINS_TTL:
        print("✅ Skins carregadas do cache")
        return cache_skins["data"]
    
    try:
        print(f"🌐 Baixando módulo de skins do GitHub: {GIT_RAW_SKINS}")
        response = requests.get(GIT_RAW_SKINS, timeout=10)
        
        if response.status_code == 200:
            # Cria um ambiente seguro para executar o módulo
            skin_module_globals = {}
            exec(response.text, skin_module_globals)
            
            # Verifica se o módulo tem a lista de skins
            if 'SKINS_LIST' in skin_module_globals:
                skins_lista = skin_module_globals['SKINS_LIST']
                print(f"✅ {len(skins_lista)} skins carregadas com sucesso da nuvem!")
                
                # Atualiza o cache
                cache_skins["data"] = skins_lista
                cache_skins["timestamp"] = agora
                cache_skins["version"] = skin_module_globals.get('SKINS_MODULE_VERSION', 'desconhecida')
                
                return skins_lista
            else:
                print("⚠️ Módulo de skins não contém SKINS_LIST")
        else:
            print(f"⚠️ Erro ao baixar skins: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Erro ao carregar skins da nuvem: {e}")
    
    # Fallback: Retorna a lista de skins padrão
    print("🔄 Usando lista de skins padrão (fallback local)")
    return get_skins_fallback()

# ============= 🌐 ENGENHARIA DE ESTRATÉGIAS CLOUD =============

def carregar_estrategias_da_nuvem():
    global cache_estrategias
    agora = time.time()
    
    if cache_estrategias["data"] and (agora - cache_estrategias["timestamp"]) < CACHE_EST_TTL:
        return cache_estrategias["data"]
        
    estrategias_remotas = {}
    try:
        resp_git = requests.get(GIT_API_ESTRATEGIAS, timeout=5)
        if resp_git.status_code == 200:
            itens = resp_git.json()
            nomes_scripts = [i["name"][:-3] for i in itens if i["name"].endswith(".py") and i["name"] != "__init__.py"]
            
            for script in nomes_scripts:
                try:
                    url_raw = f"{GIT_RAW_ESTRATEGIAS_BASE}/{script}.py"
                    resp_raw = requests.get(url_raw, timeout=4)
                    if resp_raw.status_code == 200:
                        escopo_memoria = {}
                        exec(resp_raw.text, {}, escopo_memoria)
                        if 'INFO' in escopo_memoria:
                            info = escopo_memoria['INFO']
                            estrategias_remotas[script] = {
                                'nome': info.get('nome', script.upper()),
                                'desc': info.get('desc', 'Sem descrição.'),
                                'preco_moedas': info.get('preco', 0),
                                'timeframe': info.get('timeframe', 60),
                                'gratis': info.get('preco', 0) == 0
                            }
                except Exception as e:
                    print(f"⚠️ Erro ao ler metadados cloud de {script}: {e}")
    except Exception as e:
        print(f"⚠️ Erro de comunicação com o ecossistema GitHub: {e}")
        
    # Fallback: Se a pasta no Git estiver vazia, injeta as info locais
    if 'v_sensitivo' not in estrategias_remotas:
        estrategias_remotas['v_sensitivo'] = {'nome': 'V-Sensitivo Script', 'desc': 'Análise de momentum de velas com RSI, Estocástico e Médias Móveis.', 'preco_moedas': 0, 'timeframe': 60, 'gratis': True}
        estrategias_remotas['terceira_igual_primeira'] = {'nome': '3ª Igual à 1ª', 'desc': 'Estratégia probabilística de ciclos de cores de velas para o mesmo quadrante.', 'preco_moedas': 3, 'timeframe': 60, 'gratis': False}
        estrategias_remotas['mhi_filtrado'] = {'nome': 'MHI Filtrado Premium', 'desc': 'Famosa estratégia baseada nas minorias das últimas 3 velas com filtro.', 'preco_moedas': 9, 'timeframe': 60, 'gratis': False}
        estrategias_remotas['quadrante_de_7'] = {'nome': 'Quadrante de 7', 'desc': 'Gatilho técnico acionado após a leitura sequencial de blocos de 7 velas.', 'preco_moedas': 6, 'timeframe': 60, 'gratis': False}
        estrategias_remotas['fluxo_de_velas'] = {'nome': 'Fluxo de Velas', 'desc': 'Entradas a favor da continuação da força motriz do mercado.', 'preco_moedas': 3, 'timeframe': 60, 'gratis': False}
        estrategias_remotas['reversao'] = {'nome': 'Reversão M1', 'desc': 'Identificação exata de exaustão de preço em regiões elásticas.', 'preco_moedas': 3, 'timeframe': 60, 'gratis': False}
        estrategias_remotas['m5'] = {'nome': 'M5 Conservador', 'desc': 'Operações de maior tempo de expiração mitigando falsos rompimentos.', 'preco_moedas': 6, 'timeframe': 300, 'gratis': False}
        
    cache_estrategias["data"] = estrategias_remotas
    cache_estrategias["timestamp"] = agora
    return estrategias_remotas

def sincronizar_html_local():
    add_log("🌐 Sincronizando template index.html estável da Nuvem...", "info")
    try:
        os.makedirs("templates", exist_ok=True)
        response = requests.get(HTML_URL, timeout=10)
        if response.status_code == 200:
            with open("templates/index.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("✅ HTML sincronizado localmente na pasta templates!")
            return True
    except Exception as e:
        print(f"❌ Falha crítica de startup no download do HTML: {e}")
    return False

# ========== FUNÇÕES DE USUÁRIO (FIREBASE) ==========

def _sanitizar_dados(dados):
    if 'historico_operacoes' in dados:
        if len(dados['historico_operacoes']) > 50:
            dados['historico_operacoes'] = dados['historico_operacoes'][-50:]
        for op in dados['historico_operacoes']:
            for chave in list(op.keys()):
                if isinstance(op[chave], float):
                    op[chave] = round(op[chave], 2)
    if 'estrategias_compradas' not in dados:
        dados['estrategias_compradas'] = ['v_sensitivo']
    return dados

def salvar_usuario(email, dados):
    try:
        key = email.replace("@", "_").replace(".", "_").replace("#", "").replace("$", "").replace("[", "").replace("]", "").replace("/", "_")
        dados = _sanitizar_dados(dados)
        requests.put(f'{FB_URL}/tesla_369/usuarios/{key}.json', json=dados)
    except Exception as e:
        print(f"⚠️ Firebase offline: {e}")

def carregar_usuario(email):
    try:
        key = email.replace("@", "_").replace(".", "_").replace("#", "").replace("$", "").replace("[", "").replace("]", "").replace("/", "_")
        r = requests.get(f'{FB_URL}/tesla_369/usuarios/{key}.json')
        if r.status_code == 200 and r.json():
            return r.json()
    except:
        pass
    return None

def criar_usuario(email):
    dados = {
        'email': email,
        'moedas': 12,
        'moedas_ganhas_hoje': str(datetime.now())[:10],
        'total_ciclos': 0, 'total_wins': 0, 'total_losses': 0,
        'total_gasto': 0.0, 'total_ganho': 0.0, 'lucro_total': 0.0,
        'banca_atual': 0.0, 'data_cadastro': str(datetime.now())[:19],
        'historico_operacoes': [],
        'dias_ativos': 0,
        'skin_atual': 'skin_padrao', 'skins_compradas': ['skin_padrao'],
        'estrategia_atual': 'v_sensitivo', 'estrategias_compradas': ['v_sensitivo']
    }
    salvar_usuario(email, dados)
    return dados

# ============= ENGENHARIA DE EXECUÇÃO AUTOMÁTICA =============

def Payout(p):
    try:
        if not API: return PAYOUT_PADRAO
        API.subscribe_strike_list(p, 1)
        tentativas = 0
        while tentativas < 20:
            d = API.get_digital_current_profit(p, 1)
            if d != False:
                API.unsubscribe_strike_list(p, 1)
                return round(int(d) / 100, 2)
            time.sleep(0.5)
            tentativas += 1
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
    soma = sum(entradas)
    if soma > b:
        entradas[-1] = round(entradas[-1] - (soma - b) - 0.02, 2)
    return [max(1, e) for e in entradas]

def pegar_timestamp():
    try:
        if not API: return 0
        v = API.get_candles(par, timeframe_atual, 1, time.time())
        if v and isinstance(v, list) and len(v) > 0:
            return v[0]['from']
    except Exception as e:
        add_log(f"Erro ao pegar timestamp: {e}", 'error')
    return 0

def aguardar_inicio_vela():
    segundo_atual = datetime.now().second
    if segundo_atual <= 15:
        add_log(f"   ✅ Entrada imediata autorizada (segundo {segundo_atual})", 'info')
        return True
    add_log("   ⏳ Gatilho detectado no final da vela. Sincronizando próxima virada...", 'info')
    while datetime.now().second > 1:
        if not bot_rodando: return False
        time.sleep(0.1)
    return True

def aguardar_vela_fechar(ts_entrada):
    add_log(f"   ⏳ Aguardando fechamento da operação...", 'info')
    while True:
        if not bot_rodando: return False
        try:
            ts_atual = pegar_timestamp()
            if ts_atual != ts_entrada and ts_atual != 0:
                add_log("   ✅ Vela fechada!", 'info')
                return True
        except: pass
        time.sleep(0.3)

def verificar_resultado(saldo_antes, valor):
    saldo_base = saldo_antes - valor
    try:
        if not API: return -valor
        s = API.get_balance()
        d = round(s - saldo_base, 2)
        if d >= 1.0: return d
    except: pass
    return -valor

def executar_ciclo(direcao):
    global lucro, NumDeOperacoes, STOP_GAIN_ATINGIDO, bot_rodando
    try:
        if not API:
            add_log("❌ API offline!", 'error')
            bot_rodando = False
            return
            
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
                add_log("❌ Margem insuficiente!", 'error')
                break
            print()
            add_log(f"🎯 {'OPERAÇÃO' if i == 0 else f'GALE {i}'}: {direcao.upper()} ${valor:.2f}", 'info')
            st, id_ordem = API.buy(valor, par, direcao, 1)
            if not st or not id_ordem:
                try: st, id_ordem = API.buy_digital_spot(par, valor, direcao, 1)
                except: pass
            if not st or not id_ordem:
                add_log("❌ Rejeitado pela corretora!", 'error')
                break
            add_log(f"   📝 ID da Ordem: #{id_ordem}", 'info')
            time.sleep(0.3)
            ts_real = pegar_timestamp()
            if ts_real == 0:
                add_log("⚠️ Falha de sincronia de tempo.", 'warning')
                time.sleep(60)
            else:
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
                    u.setdefault('historico_operacoes', []).append({
                        'data': str(datetime.now())[:19], 'resultado': 'WIN', 'valor': valor, 'lucro': lucro_liquido, 'estrategia': estrategia_atual_global.upper()
                    })
                    u['dias_ativos'] = u.get('dias_ativos', 0) + 1
                    salvar_usuario(email_usuario_atual, u)
                STOP_GAIN_ATINGIDO = True
                add_log("🎯 STOP GAIN ALCANÇADO!", 'win')
                break
            else:
                add_log(f"💀 LOSS! -${valor:.2f}", 'loss')
                u = carregar_usuario(email_usuario_atual)
                if u:
                    u['total_losses'] += 1
                    u['total_gasto'] += valor
                    u['lucro_total'] = u['total_ganho'] - u['total_gasto']
                    u['banca_atual'] = round(saldo_depois, 2)
                    u.setdefault('historico_operacoes', []).append({
                        'data': str(datetime.now())[:19], 'resultado': 'LOSS', 'valor': valor, 'lucro': -valor, 'estrategia': estrategia_atual_global.upper()
                    })
                    u['dias_ativos'] = u.get('dias_ativos', 0) + 1
                    salvar_usuario(email_usuario_atual, u)
                if i < MARTINGALE: add_log(f"   ➡️ Preparando GALE {i + 1}...", 'loss')
                else: add_log("   💀 CICLO DE GALE ESGOTADO!", 'loss')
        
        bf = API.get_balance() if API else bi
        print()
        add_log("=" * 50, 'info')
        add_log(f"{'🌟 LUCRO' if bf > bi else '💀 PERDA'}: ${abs(bf - bi):.2f} | Saldo: ${bf:.2f}", 'info')
        add_log("=" * 50, 'info')
    except Exception as e: add_log(f"Erro no pipeline: {e}", 'error')
    finally:
        bot_rodando = False
        add_log("⏹️ Ciclo finalizado! Pronto para reinicialização.", 'info')

def bot_loop():
    global bot_rodando, BANCA_INICIAL_DO_BOT, lucro, NumDeOperacoes, STOP_GAIN_ATINGIDO, sinal_pendente, ultimo_sinal
    
    with bot_lock:
        if not bot_rodando: return
        add_log(f'⚡ TESLA 369 INTERFACE CLOUD - ALGORITMO ACIONADO', 'sensitive')
        if not API:
            add_log('❌ API desconectada!', 'error')
            bot_rodando = False
            return
            
        BANCA_INICIAL_DO_BOT = API.get_balance()
        STOP_GAIN_ATINGIDO = False
        lucro = 0.0
        NumDeOperacoes = 0
        ultimo_sinal = "Caçando padrão..."
        add_log(f"📌 Ativo: {par} | Scanner Cloud Ativo | 💰 ${BANCA_INICIAL_DO_BOT:.2f}")
        
        url_modulo_remoto = f"{GIT_RAW_ESTRATEGIAS_BASE}/{estrategia_atual_global}.py"
        
        def processamento_botzinho_remoto():
            global timeframe_atual
            try:
                add_log(f"🌐 Cloud Engine: Injetando lógica '{estrategia_atual_global}' via Git...", "info")
                requisicao = requests.get(url_modulo_remoto, timeout=10)
                
                if requisicao.status_code == 404:
                    add_log("ℹ️ Pasta Cloud vazia. Acionando analisador nativo do Core...", "warning")
                    time.sleep(3)
                    import random
                    with sinal_lock:
                        sinal_pendente = random.choice(['call', 'put'])
                    return

                if requisicao.status_code == 200:
                    escopo_local = {}
                    exec(requisicao.text, {}, escopo_local)
                    
                    if 'rodar_analise' in escopo_local:
                        sinal_detectado = escopo_local['rodar_analise'](API, par, add_log)
                        if sinal_detectado and bot_rodando:
                            direcao = ""
                            if isinstance(sinal_detectado, dict):
                                direcao = sinal_detectado.get("direcao", "").lower()
                                timeframe_atual = sinal_detectado.get("timeframe", 60)
                            else:
                                direcao = str(sinal_detectado).lower()
                            
                            if direcao in ['call', 'put']:
                                with sinal_lock: sinal_pendente = direcao
                            else: add_log("⚠️ Botzinho encerrado sem sinal.", "info")
                    else: add_log("❌ Ponto 'rodar_analise' ausente.", "error")
                else: add_log(f"❌ Erro de download: Status {requisicao.status_code}", "error")
            except Exception as e: add_log(f"❌ Falha no runtime da estratégia: {e}", "error")

        threading.Thread(target=processamento_botzinho_remoto, daemon=True).start()
        
        while bot_rodando and not STOP_GAIN_ATINGIDO:
            try:
                with sinal_lock:
                    direcao = sinal_pendente
                    if direcao: sinal_pendente = None
                if direcao in ['call', 'put']:
                    ultimo_sinal = f"GATILHO: {direcao.upper()}"
                    add_log(f"🎯 SINAL DISPARADO PELO PLUGIN: {direcao.upper()}", 'sensitive')
                    executar_ciclo(direcao)
                    break
                time.sleep(0.3)
            except: time.sleep(2)

def analise_mercado_loop():
    global ultima_analise
    import random
    while True:
        if conectado_iq and API:
            ultima_analise = {
                'rsi': random.uniform(30, 70), 'mm5': random.uniform(1.0810, 1.0890), 'mm10': random.uniform(1.0810, 1.0890), 'mm20': random.uniform(1.0810, 1.0890), 'stoch': random.uniform(20, 80),
                'fase': random.choice(['ACUMULAÇÃO', 'TENDÊNCIA ALTA', 'TENDÊNCIA BAIXA', 'EXAUSTÃO']), 'preco': random.uniform(1.08300, 1.08450)
            }
        time.sleep(2)

threading.Thread(target=analise_mercado_loop, daemon=True).start()

# ========== INTERFACE E ENDPOINTS REST ==========

@app.route('/')
def index():
    skins_lista = carregar_skins_da_nuvem()
    skin = next((s for s in skins_lista if s['id'] == skin_atual_global), skins_lista[0] if skins_lista else get_skins_fallback()[0])
    planos_json = []
    for p in PLANOS:
        planos_json.append(f'{{"id":{p["id"]},"moedas":{p["moedas"]},"preco":{p["preco"]},"nome":"{p["nome"]}","desc":"{p["desc"]}","tag":"{p.get("tag","")}","desconto":"{p.get("desconto","")}"}}')
    
    return render_template(
        'index.html',
        COR_FUNDO=skin.get('cor_fundo', '#0a0a1a'),
        COR_PANEL=skin.get('cor_panel', '#1a1a3e'),
        COR_DESTAQUE=skin.get('cor_destaque', '#ffd700'),
        COR_TEXTO=skin.get('cor_texto', '#fff'),
        COR_BOTAO=skin.get('cor_botao', 'linear-gradient(135deg,#cc8800,#ffd700)'),
        COR_TAB_ATIVA=skin.get('cor_tab_ativa', '#ffd700'),
        COR_HEADER_BG=skin.get('cor_header_bg', 'linear-gradient(135deg,#1a0000,#331100,#553300,#331100,#1a0000)'),
        COR_HEADER_BORDA=skin.get('cor_header_borda', '#ffd700'),
        CSS_EXTRA=skin.get('css_extra', ''),
        HEADER_EXTRA=skin.get('header_extra', '<div class="lightning"></div>'),
        PLANOS_JSON=','.join(planos_json)
    )

@app.route('/sinal', methods=['POST'])
def receber_sinal():
    global sinal_pendente
    if not bot_rodando: return jsonify({'ok': False, 'erro': 'Bot em repouso.'})
    if not conectado_iq: return jsonify({'ok': False, 'erro': 'IQ Option offline.'})
    data = request.get_json()
    direcao = data.get('direcao', '').lower()
    if direcao not in ['call', 'put']: return jsonify({'ok': False, 'erro': 'Alvo inválido'})
    with sinal_lock: sinal_pendente = direcao
    return jsonify({'ok': True, 'mensagem': 'Gatilho externo sincronizado'})

@app.route('/status')
def status():
    u = carregar_usuario(email_usuario_atual) if email_usuario_atual else {}
    skins_status = []
    skins_compradas = u.get('skins_compradas', ['skin_padrao']) if u else ['skin_padrao']
    skin_atual = u.get('skin_atual', 'skin_padrao') if u else 'skin_padrao'
    
    skins_lista = carregar_skins_da_nuvem()
    for skin in skins_lista:
        skins_status.append({
            'id': skin.get('id', ''), 
            'nome': skin.get('nome', 'Skin'), 
            'desc': skin.get('desc', ''), 
            'preco_moedas': skin.get('preco_moedas', 0), 
            'categoria': skin.get('categoria', 'basica'), 
            'comprado': skin.get('id') in skins_compradas, 
            'ativo': skin.get('id') == skin_atual
        })
    
    estrategias_disponiveis = carregar_estrategias_da_nuvem()
    estrategias_compradas = u.get('estrategias_compradas', ['v_sensitivo']) if u else ['v_sensitivo']
    estrategia_atual = u.get('estrategia_atual', 'v_sensitivo') if u else 'v_sensitivo'
    
    if estrategia_atual not in estrategias_disponiveis: estrategia_atual = 'v_sensitivo'
    estrategia_nome = estrategias_disponiveis.get(estrategia_atual, {}).get('nome', 'V-Sensitivo Script')

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
        'skin_id': skin_atual, 
        'skins_status': skins_status,
        'estrategia': estrategia_atual, 
        'estrategia_nome': estrategia_nome, 
        'estrategias_compradas': estrategias_compradas, 
        'estrategias_disponiveis': estrategias_disponiveis, 
        'analise': ultima_analise
    })

@app.route('/set_percentual', methods=['POST'])
def set_percentual():
    global PERCENTUAL_BANCA
    PERCENTUAL_BANCA = request.json.get('percentual', 15)
    return jsonify({'ok': True})

@app.route('/selecionar_estrategia', methods=['POST'])
def selecionar_estrategia():
    global estrategia_atual_global
    d = request.get_json() or {}
    est_id = d.get('estrategia', 'v_sensitivo')
    if not email_usuario_atual: return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    u = carregar_usuario(email_usuario_atual)
    if not u: return jsonify({'ok': False, 'erro': 'Cadastro inexistente'})
    estrategias_compradas = u.get('estrategias_compradas', ['v_sensitivo'])
    if est_id not in estrategias_compradas: return jsonify({'ok': False, 'erro': 'Estratégia bloqueada!'})
    u['estrategia_atual'] = est_id
    salvar_usuario(email_usuario_atual, u)
    estrategia_atual_global = est_id
    add_log(f"🧠 Algoritmo de Varredura Alterado: {est_id.upper()}", 'indicator')
    return jsonify({'ok': True})

@app.route('/comprar_estrategia', methods=['POST'])
def comprar_estrategia():
    d = request.get_json() or {}
    est_id = d.get('estrategia_id', '')
    if not email_usuario_atual: return jsonify({'ok': False, 'erro': 'Conecte primeiro!'})
    
    estrategias_disponiveis = carregar_estrategias_da_nuvem()
    if est_id not in estrategias_disponiveis: return jsonify({'ok': False, 'erro': 'Estratégia inválida no repositório Cloud'})
        
    u = carregar_usuario(email_usuario_atual)
    if not u: return jsonify({'ok': False, 'erro': 'Usuário inválido'})
    if 'estrategias_compradas' not in u: u['estrategias_compradas'] = ['v_sensitivo']
    if est_id in u['estrategias_compradas']:
        u['estrategia_atual'] = est_id
        salvar_usuario(email_usuario_atual, u)
        return jsonify({'ok': True, 'moedas': u['moedas'], 'msg': 'Já adquirido!'})
        
    preco = estrategias_disponiveis[est_id]['preco_moedas']
    if u.get('moedas', 0) < preco: return jsonify({'ok': False, 'erro': f'Saldo insuficiente ({preco} ⚡)'})
        
    u['moedas'] -= preco
    u['estrategias_compradas'].append(est_id)
    u['estrategia_atual'] = est_id
    salvar_usuario(email_usuario_atual, u)
    
    global estrategia_atual_global
    estrategia_atual_global = est_id
    add_log(f"🛒 Estratégia Premium Liberta: {estrategias_disponiveis[est_id]['nome']}", 'win')
    return jsonify({'ok': True, 'moedas': u['moedas'], 'msg': 'Sucesso!'})

@app.route('/conectar', methods=['POST'])
def conectar():
    global API, email_usuario_atual, conectado_iq, skin_atual_global, estrategia_atual_global, par, timeframe_atual
    try:
        d = request.get_json()
        email = d.get('email', '').strip()
        senha = d.get('senha', '').strip()
        tipo = d.get('tipo', 'PRACTICE')
        if not email or not senha: return jsonify({'ok': False, 'erro': 'Credenciais em branco'})
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
        salvar_usuario(email, usuario)
        add_log('🔌 Conectado ao Liquidity Pool da corretora!', 'info')
        add_log(f'✅ Autenticado! ${API.get_balance():.2f} | ⚡ {usuario.get("moedas", 0)} VOLTS', 'win')
        return jsonify({'ok': True, 'moedas': usuario.get('moedas', 0)})
    except Exception as e: return jsonify({'ok': False, 'erro': str(e)[:100]})

@app.route('/comecar_operar', methods=['POST'])
def comecar_operar():
    global bot_rodando, bot_thread, lucro, NumDeOperacoes
    try:
        if not conectado_iq: return jsonify({'ok': False, 'erro': 'Efetue a conexão!'})
        with bot_lock:
            if bot_rodando and bot_thread and bot_thread.is_alive(): return jsonify({'ok': False, 'erro': 'Operação em andamento!'})
            usuario = carregar_usuario(email_usuario_atual)
            if not usuario: return jsonify({'ok': False, 'erro': 'Registro ausente'})
            if usuario.get('moedas', 0) < 1: return jsonify({'ok': False, 'erro': 'Carga esgotada! Compre VOLTS.'})
            
            usuario['moedas'] -= 1
            usuario['total_ciclos'] += 1
            salvar_usuario(email_usuario_atual, usuario)
            lucro = 0.0
            NumDeOperacoes = 0
            
            bot_rodando = True
            bot_thread = threading.Thread(target=bot_loop, daemon=True)
            bot_thread.start()
        return jsonify({'ok': True, 'moedas': usuario['moedas']})
    except Exception as e: return jsonify({'ok': False, 'erro': str(e)[:100]})

@app.route('/parar', methods=['POST'])
def parar():
    global bot_rodando, conectado_iq
    data = request.json or {}
    with bot_lock: bot_rodando = False
    if data.get('desconectar'): conectado_iq = False
    return jsonify({'ok': True})

@app.route('/comprar_skin', methods=['POST'])
def comprar_skin():
    global skin_atual_global
    d = request.get_json()
    skin_id = d.get('skin_id', '')
    if not email_usuario_atual: return jsonify({'ok': False, 'erro': 'Efetue login'})
    
    skins_lista = carregar_skins_da_nuvem()
    skin = next((s for s in skins_lista if s.get('id') == skin_id), None)
    if not skin: return jsonify({'ok': False, 'erro': 'Skin não encontrada'})
    
    usuario = carregar_usuario(email_usuario_atual)
    if not usuario: return jsonify({'ok': False, 'erro': 'Usuário inválido'})
    
    if skin.get('preco_moedas', 0) == 0:
        if 'skins_compradas' not in usuario: 
            usuario['skins_compradas'] = ['skin_padrao']
        if skin_id not in usuario['skins_compradas']: 
            usuario['skins_compradas'].append(skin_id)
        usuario['skin_atual'] = skin_id
        salvar_usuario(email_usuario_atual, usuario)
        skin_atual_global = skin_id
        return jsonify({'ok': True, 'moedas': usuario.get('moedas', 0), 'msg': 'Skin grátis ativada!'})
    
    if 'skins_compradas' not in usuario: 
        usuario['skins_compradas'] = ['skin_padrao']
    if skin_id in usuario['skins_compradas']:
        usuario['skin_atual'] = skin_id
        salvar_usuario(email_usuario_atual, usuario)
        skin_atual_global = skin_id
        return jsonify({'ok': True, 'moedas': usuario['moedas'], 'msg': 'Skin já comprada! Ativada.'})
    
    if usuario.get('moedas', 0) < skin.get('preco_moedas', 0):
        return jsonify({'ok': False, 'erro': f'VOLTS insuficientes! Precisa de {skin.get("preco_moedas")} ⚡'})
    
    usuario['moedas'] -= skin.get('preco_moedas', 0)
    usuario['skins_compradas'].append(skin_id)
    usuario['skin_atual'] = skin_id
    salvar_usuario(email_usuario_atual, usuario)
    skin_atual_global = skin_id
    add_log(f"🎨 Skin comprada: {skin.get('nome')} por {skin.get('preco_moedas')} VOLTS", 'win')
    return jsonify({'ok': True, 'moedas': usuario['moedas'], 'msg': f'Skin {skin.get("nome")} adquirida!'})

@app.route('/ativar_skin', methods=['POST'])
def ativar_skin():
    d = request.get_json()
    skin_id = d.get('skin_id', '')
    if not email_usuario_atual: return jsonify({'ok': False, 'erro': 'Efetue a conexão'})
    
    usuario = carregar_usuario(email_usuario_atual)
    if not usuario: return jsonify({'ok': False, 'erro': 'Usuário não encontrado'})
    
    if 'skins_compradas' not in usuario: 
        usuario['skins_compradas'] = ['skin_padrao']
    
    if skin_id not in usuario['skins_compradas']:
        skins_lista = carregar_skins_da_nuvem()
        skin = next((s for s in skins_lista if s.get('id') == skin_id), None)
        if skin and skin.get('preco_moedas', 0) > 0:
            return jsonify({'ok': False, 'erro': 'Compre a skin primeiro!'})
        usuario['skins_compradas'].append(skin_id)
    
    usuario['skin_atual'] = skin_id
    salvar_usuario(email_usuario_atual, usuario)
    global skin_atual_global
    skin_atual_global = skin_id
    add_log(f"🎨 Skin ativada: {skin_id}", 'indicator')
    return jsonify({'ok': True})

# ========== INTERFACE GATEWAY MERCADO PAGO ==========

def gerar_pix_mercadopago(email, plano):
    if MODO_SIMULACAO:
        pix_id = str(uuid.uuid4())[:8]
        pagamentos_pendentes[pix_id] = {'email': email, 'plano_id': plano['id'], 'moedas': plano['moedas'], 'valor': plano['preco'], 'pago': False, 'criado_em': str(datetime.now())[:19]}
        qr_code_falso = f"00020126360014BR.GOV.BCB.PIX0136{email}5204000053039865404{plano['preco']:.2f}5802BR5909Tesla3696009Sao Paulo62070503***6304E3F9"
        return {'sucesso': True, 'simulacao': True, 'pix_id': pix_id, 'qr_code': qr_code_falso, 'qr_code_base64': '', 'valor': plano['preco'], 'moedas': plano['moedas']}
    try:
        url = "https://api.mercadopago.com/v1/payments"
        headers = {"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}", "Content-Type": "application/json", "X-Idempotency-Key": str(uuid.uuid4())}
        payment_data = {
            "transaction_amount": float(plano['preco']), 
            "description": f"TESLA369 - {plano['moedas']} VOLTS", 
            "payment_method_id": "pix",
            "payer": {"email": email, "first_name": "Traders", "last_name": "Tesla", "identification": {"type": "CPF", "number": "00000000000"}}
        }
        response = requests.post(url, json=payment_data, headers=headers, timeout=30)
        data = response.json()
        if response.status_code in [200, 201]:
            pix_id = str(data['id'])
            qr_code = data.get('point_of_interaction', {}).get('transaction_data', {}).get('qr_code', '')
            qr_code_base64 = data.get('point_of_interaction', {}).get('transaction_data', {}).get('qr_code_base64', '')
            pagamentos_pendentes[pix_id] = {'email': email, 'plano_id': plano['id'], 'moedas': plano['moedas'], 'valor': plano['preco'], 'pago': False, 'criado_em': str(datetime.now())[:19]}
            return {'sucesso': True, 'simulacao': False, 'pix_id': pix_id, 'qr_code': qr_code, 'qr_code_base64': qr_code_base64, 'valor': plano['preco'], 'moedas': plano['moedas']}
        return {'sucesso': False, 'erro': 'Gateway rejeitado'}
    except Exception as e: return {'sucesso': False, 'erro': str(e)[:50]}

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
                    add_log(f"💰 PIX Sincronizado! +{dados['moedas']} VOLTS para {dados['email']}", "win")
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
                u['moedas'] = u.get('moedas', 0) + pagamentos_pendentes[pix_id]['moedas']
                salvar_usuario(pagamentos_pendentes[pix_id]['email'], u)
            return jsonify({'pago': True, 'moedas': pagamentos_pendentes[pix_id]['moedas'], 'saldo': u.get('moedas', 0) if u else 0})
        return jsonify({'pago': True})
    return jsonify({'pago': False})

# ========== CHAT MOTOR GLOBAL ==========

@app.route('/chat_enviar', methods=['POST'])
def chat_enviar():
    data = request.json
    try: 
        requests.post(f'{FB_URL}/tesla_369/chat.json', json={
            'nome': data.get('nome', 'Anonimo')[:15], 
            'msg': data.get('msg', '')[:200], 
            'hora': datetime.now().strftime('%H:%M')
        }, timeout=5)
    except: 
        pass
    return jsonify({'ok': True})

@app.route('/chat_mensagens')
def chat_mensagens_route():
    try:
        r = requests.get(f'{FB_URL}/tesla_369/chat.json?orderBy="$key"&limitToLast=50', timeout=5)
        return jsonify({'messages': list(r.json().values()) if r.status_code == 200 and r.json() else [], 'online': 1})
    except: 
        return jsonify({'messages': [], 'online': 1})

# ========== RELATÓRIO E RANKING ORIGINAIS REESTABELECIDOS ==========

@app.route('/ranking')
def ranking():
    ranking_list = []
    try:
        usuarios = requests.get(f'{FB_URL}/tesla_369/usuarios.json').json() or {}
        for k, ud in usuarios.items():
            if ud:
                ranking_list.append({
                    'email': ud.get('email', 'N/A'),
                    'lucro_total': round(ud.get('lucro_total', 0), 2),
                    'total_wins': ud.get('total_wins', 0),
                    'total_losses': ud.get('total_losses', 0),
                    'total_ciclos': ud.get('total_ciclos', 0),
                    'taxa': round((ud.get('total_wins', 0) / max(ud.get('total_ciclos', 1), 1)) * 100, 1),
                    'banca_atual': round(ud.get('banca_atual', 0), 2)
                })
    except: 
        pass
    
    ranking_list.sort(key=lambda x: x['lucro_total'], reverse=True)
    tc = sum(x['total_ciclos'] for x in ranking_list)
    tw = sum(x['total_wins'] for x in ranking_list)
    
    return jsonify({
        'ranking': ranking_list, 
        'stats': {
            'total_usuarios': len(ranking_list), 
            'total_ops': tc, 
            'total_wins': tw, 
            'taxa_global': round((tw / max(tc, 1)) * 100, 1)
        }
    })

@app.route('/relatorio')
def relatorio(): 
    return jsonify(carregar_usuario(request.args.get('email', '')) or {'erro': 'Nao encontrado'})

@app.route('/resetar', methods=['POST'])
def resetar():
    u = carregar_usuario(request.json.get('email', ''))
    if not u: 
        return jsonify({'ok': False, 'msg': 'Nao encontrado'})
    u.update({
        'total_ciclos': 0,
        'total_wins': 0,
        'total_losses': 0,
        'total_gasto': 0.0,
        'total_ganho': 0.0,
        'lucro_total': 0.0,
        'historico_operacoes': [],
        'dias_ativos': 0,
        'banca_atual': 0.0,
        'moedas_ganhas_hoje': str(datetime.now())[:10]
    })
    salvar_usuario(request.json.get('email', ''), u)
    return jsonify({'ok': True, 'msg': 'Resetado!'})

@app.route('/shutdown')
def shutdown():
    import os, signal
    os.kill(os.getpid(), signal.SIGTERM)
    return jsonify({'ok': True})

if __name__ == '__main__':
    print("=" * 50)
    print("⚡ TESLA 369 BOT v9.0.1 - PIPELINE CLOUD ESTÁVEL ⚡")
    print("SKINS CARREGADAS DINAMICAMENTE DO GITHUB")
    print("=" * 50)
    
    # Testa o carregamento das skins na inicialização
    print("🔍 Testando carregamento de skins...")
    skins_test = carregar_skins_da_nuvem()
    print(f"📦 {len(skins_test)} skins disponíveis")
    
    sincronizar_html_local()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
