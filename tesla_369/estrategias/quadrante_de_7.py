"""
Estratégia: Quadrante De 7
Extraída automaticamente do TESLA 369
"""

import time
from datetime import datetime

# Metadados da estratégia
ESTRATEGIA_INFO = {
    'nome': 'Quadrante De 7',
    'descricao': 'Estratégia extraída do TESLA 369',
    'timeframe': 60,
    'pares': ['EURUSD-OTC'],
    'preco_moedas': 0,
    'gratis': True
}

def sinal_quadrante_de_7():
    global ultimo_sinal, ultima_analise
    try:
        agora = datetime.now()
        if not ((agora.minute >= 1.55 and agora.minute <= 2) or (agora.minute >= 6.55 and agora.minute <= 7)):
            ultimo_sinal = f"⏳ Q7: {agora.minute}:{agora.second:02d}"; return None
        v = API.get_candles(par, timeframe_atual, 22, time.time())
        if len(v) < 22: return None
        velas = []
        for vela in v[-7:]:
            if vela['open'] < vela['close']: velas.append('g')
            elif vela['open'] > vela['close']: velas.append('r')
            else: velas.append('d')
        cores = ''.join(velas); preco_atual = v[-1]['close']; mm = sum(c['close'] for c in v[:-1]) / 21
        ultima_analise = {'preco': preco_atual, 'rsi': None, 'mm5': None, 'mm10': None, 'mm20': round(mm, 6), 'stoch': None, 'fase': 'QUADRANTE-7'}
        add_log(f"7️⃣ Q7 | Velas: {cores}", 'indicator')
        if preco_atual > mm and cores.count('g') < cores.count('r') and 'd' not in cores:
            ultimo_sinal = "7️⃣ CALL (Q7)"; add_log("Q7: CALL!", 'sensitive'); return 'call'
        if preco_atual < mm and cores.count('g') > cores.count('r') and 'd' not in cores:
            ultimo_sinal = "7️⃣ PUT (Q7)"; add_log("Q7: PUT!", 'sensitive'); return 'put'
        ultimo_sinal = "⏳..."; return None
    except Exception as e: add_log(f"Erro: {e}", 'error'); return None
