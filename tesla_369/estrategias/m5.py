ESTRATEGIA_M5 = {
    'nome': '⏰ M5', 'desc': 'Quadrante de velas de 5min',
    'timeframe': 300, 'pares': ['EURUSD-OTC'], 'preco_moedas': 6, 'gratis': False
}

def sinal_m5(API, par, timeframe_atual):
    from datetime import datetime
    import time
    agora = datetime.now()
    if agora.minute % 15 != 0: return None, {}
    time.sleep(2)
    v = API.get_candles(par, timeframe_atual, 7, time.time())
    if len(v) < 7: return None, {}
    velas = []
    for vela in v:
        if vela['open'] < vela['close']: velas.append('g')
        elif vela['open'] > vela['close']: velas.append('r')
        else: velas.append('d')
    analise = {'preco': v[-1]['close'], 'rsi': None, 'mm5': None, 'mm10': None, 'mm20': None, 'stoch': None, 'fase': 'M5'}
    if velas[0] == velas[1] == velas[2] and velas[3] == velas[4] == velas[5]:
        if velas[6] == 'g' and 'd' not in velas: return 'put', analise
        if velas[6] == 'r' and 'd' not in velas: return 'call', analise
    return None, analise
