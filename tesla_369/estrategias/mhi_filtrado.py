"""
Estratégia: Mhi Filtrado
Extraída automaticamente do TESLA 369
"""

import time
from datetime import datetime

# Metadados da estratégia
ESTRATEGIA_INFO = {
    'nome': 'Mhi Filtrado',
    'descricao': 'Estratégia extraída do TESLA 369',
    'timeframe': 60,
    'pares': ['EURUSD-OTC'],
    'preco_moedas': 0,
    'gratis': True
}

def sinal_mhi_filtrado():
    global ultimo_sinal, ultima_analise
    try:
        agora = datetime.now()
        if not ((agora.minute >= 4.55 and agora.minute <= 5) or (agora.minute >= 9.55 and agora.minute <= 10)):
            ultimo_sinal = f"⏳ MHI: {agora.minute}:{agora.second:02d}"; return None
        v = API.get_candles(par, timeframe_atual, 22, time.time())
        if len(v) < 22: return None
        velas = []
        for vela in v[-5:]:
            if vela['open'] < vela['close']: velas.append('g')
            elif vela['open'] > vela['close']: velas.append('r')
            else: velas.append('d')
        cores = ''.join(velas); preco_atual = v[-1]['close']; mm = sum(c['close'] for c in v[:-1]) / 21
        ultima_analise = {'preco': preco_atual, 'rsi': None, 'mm5': None, 'mm10': None, 'mm20': round(mm, 6), 'stoch': None, 'fase': 'MHI-FILTRADO'}
        add_log(f"📊 MHI | Velas: {cores} | MM: {mm:.5f}", 'indicator')
        if preco_atual > mm and cores.count('r') > cores.count('g') and 'd' not in cores and velas[4] == 'r':
            ultimo_sinal = "📊 CALL (MHI)"; add_log("MHI: CALL!", 'sensitive'); return 'call'
        if preco_atual < mm and cores.count('r') < cores.count('g') and 'd' not in cores and velas[4] == 'g':
            ultimo_sinal = "📊 PUT (MHI)"; add_log("MHI: PUT!", 'sensitive'); return 'put'
        ultimo_sinal = "⏳..."; return None
    except Exception as e: add_log(f"Erro: {e}", 'error'); return None
