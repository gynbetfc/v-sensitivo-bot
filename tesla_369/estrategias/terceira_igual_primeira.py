"""
Estratégia: Terceira Igual Primeira
Extraída automaticamente do TESLA 369
"""

import time
from datetime import datetime

ESTRATEGIA_INFO = {
    'nome': 'Terceira Igual Primeira',
    'descricao': 'Estratégia extraída do TESLA 369',
    'timeframe': 60,
    'pares': ['EURUSD-OTC'],
    'preco_moedas': 0,
    'gratis': True
}

def sinal_terceira_igual_primeira():
    global ultimo_sinal, ultima_analise
    try:
        agora = datetime.now()
        if agora.minute % 5 != 0: ultimo_sinal = f"⏳ Min: {agora.minute} (5/10/15...)"; return None
        if agora.second < 55: ultimo_sinal = f"⏳ Seg: {agora.second}s (aguardando 55)"; return None
        time.sleep(2)
        v = API.get_candles(par, timeframe_atual, 22, time.time())
        if len(v) < 22: return None
        vela_atual = 'g' if v[-1]['open'] < v[-1]['close'] else ('r' if v[-1]['open'] > v[-1]['close'] else 'd')
        preco_atual = v[-1]['close']; mm = sum(c['close'] for c in v[:-1]) / 21
        ultima_analise = {'preco': preco_atual, 'rsi': None, 'mm5': None, 'mm10': None, 'mm20': round(mm, 6), 'stoch': None, 'fase': '3ª=1ª'}
        add_log(f"3️⃣ 3=1 | Vela: {vela_atual} | MM: {mm:.5f}", 'indicator')
        if preco_atual > mm and vela_atual == 'g': ultimo_sinal = "3️⃣ CALL (3=1)"; add_log("3ª=1ª: CALL!", 'sensitive'); return 'call'
        if preco_atual < mm and vela_atual == 'r': ultimo_sinal = "3️⃣ PUT (3=1)"; add_log("3ª=1ª: PUT!", 'sensitive'); return 'put'
        ultimo_sinal = "⏳..."; return None
    except Exception as e: add_log(f"Erro: {e}", 'error'); return None
