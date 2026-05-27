ESTRATEGIA_TESLA_369 = {
    'nome': '⚡ TESLA-369',
    'desc': '6 velas: padrão g-g-g-r-r → CALL / r-r-r-g-g → PUT',
    'timeframe': 60,
    'pares': ['EURUSD-OTC'],
    'preco_moedas': 0,
    'gratis': True,
    'fixa': True
}

def sinal_tesla_369(API, par, timeframe_atual):
    from datetime import datetime
    import time
    agora = datetime.now()
    if not ((agora.minute >= 1.55 and agora.minute <= 2) or (agora.minute >= 6.55 and agora.minute <= 7)):
        return None
    v = API.get_candles(par, timeframe_atual, 6, time.time())
    if len(v) < 6: return None
    velas = []
    for vela in v:
        if vela['open'] < vela['close']: velas.append('g')
        elif vela['open'] > vela['close']: velas.append('r')
        else: velas.append('d')
    cores = ''.join(velas)
    if velas[0] == 'g' and velas[3] == 'g' and velas[4] == 'r' and velas[5] == 'r' and 'd' not in cores:
        return 'call'
    if velas[0] == 'r' and velas[3] == 'r' and velas[4] == 'g' and velas[5] == 'g' and 'd' not in cores:
        return 'put'
    return None
