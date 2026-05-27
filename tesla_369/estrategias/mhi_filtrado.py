ESTRATEGIA_MHI = {
    'nome': '📊 MHI-FILTRADO', 'desc': '5 velas + Média Móvel + filtro de cor dominante',
    'timeframe': 60, 'pares': ['EURUSD-OTC'], 'preco_moedas': 9, 'gratis': False
}

def sinal_mhi(API, par, timeframe_atual):
    from datetime import datetime
    import time
    agora = datetime.now()
    if not ((agora.minute >= 4.55 and agora.minute <= 5) or (agora.minute >= 9.55 and agora.minute <= 10)):
        return None, {}
    v = API.get_candles(par, timeframe_atual, 22, time.time())
    if len(v) < 22: return None, {}
    velas = []
    for vela in v[-5:]:
        if vela['open'] < vela['close']: velas.append('g')
        elif vela['open'] > vela['close']: velas.append('r')
        else: velas.append('d')
    cores = ''.join(velas)
    mm = sum(c['close'] for c in v[:-1]) / 21
    analise = {'preco': v[-1]['close'], 'rsi': None, 'mm5': None, 'mm10': None, 'mm20': round(mm,6), 'stoch': None, 'fase': 'MHI'}
    if v[-1]['close'] > mm and cores.count('r') > cores.count('g') and 'd' not in cores and velas[4] == 'r':
        return 'call', analise
    if v[-1]['close'] < mm and cores.count('r') < cores.count('g') and 'd' not in cores and velas[4] == 'g':
        return 'put', analise
    return None, analise
