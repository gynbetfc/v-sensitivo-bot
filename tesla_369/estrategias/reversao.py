"""
Estratégia: Reversao
Extraída automaticamente do TESLA 369
"""

import time
from datetime import datetime

# Metadados da estratégia
ESTRATEGIA_INFO = {
    'nome': 'Reversao',
    'descricao': 'Estratégia extraída do TESLA 369',
    'timeframe': 60,
    'pares': ['EURUSD-OTC'],
    'preco_moedas': 0,
    'gratis': True
}

def sinal_reversao():
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
        ultima_analise = {'preco': preco_atual, 'rsi': None, 'mm5': None, 'mm10': None, 'mm20': round(mm, 6), 'stoch': None, 'fase': 'REVERSÃO'}
        add_log(f"🔄 REV | Velas: {cores}", 'indicator')
        if preco_atual > mm and cores == 'grgrg':
            ultimo_sinal = "🔄 CALL (REV)"; add_log("REVERSÃO: CALL!", 'sensitive'); return 'call'
        if preco_atual < mm and cores == 'rgrgr':
            ultimo_sinal = "🔄 PUT (REV)"; add_log("REVERSÃO: PUT!", 'sensitive'); return 'put'
        ultimo_sinal = "⏳..."; return None
    except Exception as e: add_log(f"Erro: {e}", 'error'); return None
