ESTRATEGIA_REVERSAO = {
    'nome': '🔄 REVERSÃO', 'desc': 'Padrão alternado g-r-g-r-g ou r-g-r-g-r',
    'timeframe': 60, 'pares': ['EURUSD-OTC'], 'preco_moedas': 3, 'gratis': False
}

def sinal_reversao(API, par, timeframe_atual):
    from datetime import datetime
    import time
    if datetime.now().second % 55 != 0: return None, {}
    v = API.get_candles(par, timeframe_atual, 22, time.time())
    if len(v) < 22: return None, {}
    velas = []
    for vela in v[-5:]:
        if vela['open'] < vela['close']: velas.append('g')
        elif vela['open'] > vela['close']: velas.append('r')
        else: velas.append('d')
    cores = ''.join(velas)
    mm = sum(c['close'] for c in v[:-1]) / 21
    analise = {'preco': v[-1]['close'], 'rsi': None, 'mm5': None, 'mm10': None, 'mm20': round(mm,6), 'stoch': None, 'fase': 'REV'}
    if v[-1]['close'] > mm and cores == 'grgrg': return 'call', analise
    if v[-1]['close'] < mm and cores == 'rgrgr': return 'put', analise
    return None, analise
