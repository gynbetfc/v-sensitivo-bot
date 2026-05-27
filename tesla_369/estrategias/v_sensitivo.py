ESTRATEGIA_V_SENSITIVO = {
    'nome': '🔮 v_SENSITIVO', 'desc': 'RSI + MM + Bollinger + MACD + Estocástico + Fase da Vela',
    'timeframe': 60, 'pares': ['EURUSD-OTC'], 'preco_moedas': 9, 'gratis': False
}

def sinal_v_sensitivo(API, par, timeframe_atual):
    from datetime import datetime
    import time
    from core.indicadores import sma, bollinger, rsi, macd, estocastico
    
    s = datetime.now().second
    fase = "🌅NASCENDO" if s < 20 else ("☀️VIVA" if s < 45 else "🌇MORRENDO")
    v = API.get_candles(par, timeframe_atual, 30, time.time())
    if len(v) < 20: return None, {}
    
    rs = rsi(v); m5 = sma(v, 5); m10 = sma(v, 10); m20 = sma(v, 20)
    bs, _, bi = bollinger(v); mc = macd(v); st = estocastico(v); pc = v[-1]['close']
    
    analise = {'preco': pc, 'rsi': rs, 'mm5': m5, 'mm10': m10, 'mm20': m20, 'stoch': st, 'fase': fase}
    sc = sp = 0
    
    if m5 and m20:
        if m5 > m20: sc += 20
        else: sp += 20
    if m5 and m10:
        if m5 > m10: sc += 15
        else: sp += 15
    if rs:
        if rs < 30: sc += 25
        elif rs > 70: sp += 25
        elif rs > 50: sc += 10
        else: sp += 10
    if bs and bi and pc:
        if pc <= bi*1.01: sc += 20
        elif pc >= bs*0.99: sp += 20
    if mc:
        if mc > 0: sc += 15
        else: sp += 15
    if st:
        if st < 20: sc += 15
        elif st > 80: sp += 15
    
    if sc > sp and abs(sc-sp) >= 15: return 'call', analise
    if sp > sc and abs(sc-sp) >= 15: return 'put', analise
    return None, analise
