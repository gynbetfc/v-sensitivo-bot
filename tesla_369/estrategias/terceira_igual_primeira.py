ESTRATEGIA_TERCEIRA = {
    'nome': '3️⃣ 3ª = 1ª 🆓', 'desc': 'Opera a cada 5min, seg 55+',
    'timeframe': 60, 'pares': ['EURUSD-OTC'], 'preco_moedas': 0, 'gratis': True
}

def sinal_terceira(API, par, timeframe_atual):
    from datetime import datetime
    import time
    agora = datetime.now()
    if agora.minute % 5 != 0 or agora.second < 55: return None, {}
    time.sleep(2)
    v = API.get_candles(par, timeframe_atual, 22, time.time())
    if len(v) < 22: return None, {}
    vela_atual = 'g' if v[-1]['open'] < v[-1]['close'] else ('r' if v[-1]['open'] > v[-1]['close'] else 'd')
    mm = sum(c['close'] for c in v[:-1]) / 21
    analise = {'preco': v[-1]['close'], 'rsi': None, 'mm5': None, 'mm10': None, 'mm20': round(mm,6), 'stoch': None, 'fase': '3ª=1ª'}
    if v[-1]['close'] > mm and vela_atual == 'g': return 'call', analise
    if v[-1]['close'] < mm and vela_atual == 'r': return 'put', analise
    return None, analise
