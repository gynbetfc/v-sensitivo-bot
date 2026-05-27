"""
Estratégia: V Sensitivo
Extraída automaticamente do TESLA 369
"""

import time
from datetime import datetime

# Metadados da estratégia
ESTRATEGIA_INFO = {
    'nome': 'V Sensitivo',
    'descricao': 'Estratégia extraída do TESLA 369',
    'timeframe': 60,
    'pares': ['EURUSD-OTC'],
    'preco_moedas': 0,
    'gratis': True
}

def sinal_v_sensitivo():
    global ultimo_sinal, ultima_analise
    try:
        s = datetime.now().second
        fase = "🌅NASCENDO" if s < 20 else ("☀️VIVA" if s < 45 else "🌇MORRENDO")
        v = API.get_candles(par, timeframe_atual, 30, time.time())
        if len(v) < 20: return None
        rs = rsi(v); m5 = sma(v, 5); m10 = sma(v, 10); m20 = sma(v, 20)
        bs, _, bi = bollinger(v); mc = macd(v); st = estocastico(v); pc = v[-1]['close']
        ultima_analise = {'preco': pc, 'rsi': rs, 'mm5': m5, 'mm10': m10, 'mm20': m20, 'stoch': st, 'fase': fase}
        sc = sp = 0; sinais = []
        if m5 and m20:
            if m5 > m20: sc += 20; sinais.append("MM5>MM20")
            else: sp += 20; sinais.append("MM5<MM20")
        if m5 and m10:
            if m5 > m10: sc += 15; sinais.append("MM5>MM10")
            else: sp += 15; sinais.append("MM5<MM10")
        if rs:
            if rs < 30: sc += 25; sinais.append(f"RSI={rs:.0f}↓")
            elif rs > 70: sp += 25; sinais.append(f"RSI={rs:.0f}↑")
            elif rs > 50: sc += 10
            else: sp += 10
        if bs and bi and pc:
            if pc <= bi*1.01: sc += 20; sinais.append("BB↓")
            elif pc >= bs*0.99: sp += 20; sinais.append("BB↑")
        if mc:
            if mc > 0: sc += 15; sinais.append("MACD+")
            else: sp += 15; sinais.append("MACD-")
        if st:
            if st < 20: sc += 15; sinais.append(f"E={st:.0f}↓")
            elif st > 80: sp += 15; sinais.append(f"E={st:.0f}↑")
        if fase == "🌇MORRENDO":
            cor = 'V' if v[-1]['open'] < v[-1]['close'] else 'R'
            if cor == 'V': sp += 10
            else: sc += 10
        add_log(f"🔮{fase} | C={sc} P={sp} | {' '.join(sinais[:3])}", 'indicator')
        dif = abs(sc-sp)
        if sc > sp and dif >= 15:
            ultimo_sinal = f"🔮 CALL ({sc}x{sp})"; add_log(f"CALL!", 'sensitive'); return 'call'
        if sp > sc and dif >= 15:
            ultimo_sinal = f"🔮 PUT ({sp}x{sc})"; add_log(f"PUT!", 'sensitive'); return 'put'
        ultimo_sinal = "⏳..."; return None
    except Exception as e: add_log(f"Erro: {e}", 'error'); return None
