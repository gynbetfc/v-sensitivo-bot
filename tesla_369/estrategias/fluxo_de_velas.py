"""
Estratégia: Fluxo De Velas
Extraída automaticamente do TESLA 369
"""

import time
from datetime import datetime

ESTRATEGIA_INFO = {
    'nome': 'Fluxo De Velas',
    'descricao': 'Estratégia extraída do TESLA 369',
    'timeframe': 60,
    'pares': ['EURUSD-OTC'],
    'preco_moedas': 0,
    'gratis': True
}

def sinal_fluxo_de_velas():
    global ultimo_sinal, ultima_analise
    try:
        agora = datetime.now()
        if agora.second % 55 != 0: return None
        v = API.get_candles(par, timeframe_atual, 22, time.time())
        if len(v) < 22: return None
        velas = []
        for vela in v[-5:]:
            if vela['open'] < vela['close']: velas.append('g')
            elif vela['open'] > vela['close']: velas.append('r')
            else: velas.append('d')
        cores = ''.join(velas); preco_atual = v[-1]['close']; mm = sum(c['close'] for c in v[:-1]) / 21
        ultima_analise = {'preco': preco_atual, 'rsi': None, 'mm5': None, 'mm10': None, 'mm20': round(mm, 6), 'stoch': None, 'fase': 'FLUXO'}
        add_log(f"🌊 FLUXO | Velas: {cores}", 'indicator')
        if preco_atual > mm and cores == 'ggggg' and 'd' not in cores:
            ultimo_sinal = "🌊 CALL (FLUXO)"; add_log("FLUXO: CALL!", 'sensitive'); return 'call'
        if preco_atual < mm and cores == 'rrrrr' and 'd' not in cores:
            ultimo_sinal = "🌊 PUT (FLUXO)"; add_log("FLUXO: PUT!", 'sensitive'); return 'put'
        ultimo_sinal = "⏳..."; return None
    except Exception as e: add_log(f"Erro: {e}", 'error'); return None
