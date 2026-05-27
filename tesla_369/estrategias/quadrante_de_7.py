ESTRATEGIA_QUADRANTE = {
    'nome': '7️⃣ QUADRANTE DE 7', 'desc': '7 velas + MM, conta cores',
    'timeframe': 60, 'pares': ['EURUSD-OTC'], 'preco_moedas': 6, 'gratis': False
}

def sinal_quadrante(API, par, timeframe_atual):
    from datetime import datetime
    import time
    agora = datetime.now()
    if not ((agora.minute >= 1.55 and agora.minute <= 2) or (agora.minute >= 6.55 and agora.minute <= 7)):
        return None, {}
    v = API.get_candles(par, timeframe_atual, 22, time.time())
    if len(v) < 22: return None, {}
    velas = []
    for vela in v[-7:]:
        if vela['open'] < vela['close']: velas.append('g')
        elif vela['open'] > vela['close']: velas.append('r')
        else: velas.append('d')
    cores = ''.join(velas)
    mm = sum(c['close'] for c in v[:-1]) / 21
    analise = {'preco': v[-1]['close'], 'rsi': None, 'mm5': None, 'mm10': None, 'mm20': round(mm,6), 'stoch': None, 'fase': 'Q7'}
    if v[-1]['close'] > mm and cores.count('g') < cores.count('r') and 'd' not in cores:
        return 'call', analise
    if v[-1]['close'] < mm and cores.count('g') > cores.count('r') and 'd' not in cores:
        return 'put', analise
    return None, analise
