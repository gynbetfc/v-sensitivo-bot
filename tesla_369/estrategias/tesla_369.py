"""
Estratégia: Tesla 369
Extraída automaticamente do TESLA 369
"""

import time
from datetime import datetime

# Metadados da estratégia
ESTRATEGIA_INFO = {
    'nome': 'Tesla 369',
    'descricao': 'Estratégia extraída do TESLA 369',
    'timeframe': 60,
    'pares': ['EURUSD-OTC'],
    'preco_moedas': 0,
    'gratis': True
}

def sinal_tesla_369():
    global ultimo_sinal, ultima_analise
    try:
        agora = datetime.now()
        if not ((agora.minute >= 1.55 and agora.minute <= 2) or (agora.minute >= 6.55 and agora.minute <= 7)):
            ultimo_sinal = f"⏳ Min: {agora.minute}:{agora.second:02d}"; return None
        v = API.get_candles(par, timeframe_atual, 6, time.time())
        if len(v) < 6: return None
        velas = []
        for vela in v:
            if vela['open'] < vela['close']: velas.append('g')
            elif vela['open'] > vela['close']: velas.append('r')
            else: velas.append('d')
        cores = ''.join(velas); pc = v[-1]['close']
        ultima_analise = {'preco': pc, 'rsi': None, 'mm5': None, 'mm10': None, 'mm20': None, 'stoch': None, 'fase': 'TESLA-369'}
        add_log(f"⚡ TESLA-369 | Velas: {cores}", 'indicator'); ultimo_sinal = f"⚡ 369: {cores}"
        if velas[0] == 'g' and velas[3] == 'g' and velas[4] == 'r' and velas[5] == 'r' and 'd' not in cores:
            add_log("TESLA-369: CALL!", 'sensitive'); return 'call'
        if velas[0] == 'r' and velas[3] == 'r' and velas[4] == 'g' and velas[5] == 'g' and 'd' not in cores:
            add_log("TESLA-369: PUT!", 'sensitive'); return 'put'
        ultimo_sinal = "⏳..."; return None
    except Exception as e: add_log(f"Erro: {e}", 'error'); return None
