# -*- coding: utf-8 -*-
# ESTRATÉGIA: V-Sensitivo Script
# Análise completa com RSI, MMs, Bollinger, MACD e Estocástico

import time

INFO = {
    'nome': 'V-Sensitivo Script',
    'desc': 'Análise de momentum de velas com RSI, Estocástico, Médias Móveis, Bollinger e MACD.',
    'preco': 0,
    'timeframe': 60,
    'gratis': True
}

def get_close(vela):
    if 'close' in vela:
        return vela['close']
    elif 'max' in vela:
        return vela['max']
    return 0

def get_high(vela):
    if 'high' in vela:
        return vela['high']
    elif 'max' in vela:
        return vela['max']
    return 0

def get_low(vela):
    if 'low' in vela:
        return vela['low']
    elif 'min' in vela:
        return vela['min']
    return 0

def sma(velas, periodo):
    if len(velas) < periodo:
        return None
    return round(sum(x['close'] for x in velas[-periodo:]) / periodo, 6)

def bollinger(velas, periodo=20, desvio=2):
    if len(velas) < periodo:
        return None, None, None
    closes = [get_close(x) for x in velas[-periodo:]]
    media = sum(closes) / periodo
    variancia = sum((x - media) ** 2 for x in closes) / periodo
    dp = variancia ** 0.5
    return round(media + desvio * dp, 6), round(media, 6), round(media - desvio * dp, 6)

def rsi(velas, periodo=14):
    if len(velas) < periodo + 1:
        return 50
    ganhos, perdas = [], []
    for i in range(1, len(velas)):
        diff = get_close(velas[i]) - get_close(velas[i-1])
        if diff > 0:
            ganhos.append(diff)
            perdas.append(0)
        else:
            ganhos.append(0)
            perdas.append(abs(diff))
    if sum(perdas) == 0:
        return 100
    return round(100 - (100 / (1 + sum(ganhos) / sum(perdas))), 2)

def macd(velas, rapido=12, lento=26):
    if len(velas) < lento:
        return None
    closes = [get_close(x) for x in velas]
    er = closes[0]
    el = closes[0]
    for x in closes[1:]:
        er = x * (2/(rapido+1)) + er * (1-2/(rapido+1))
        el = x * (2/(lento+1)) + el * (1-2/(lento+1))
    return round(er - el, 8)

def estocastico(velas, periodo=14):
    if len(velas) < periodo:
        return 50
    highs = [get_high(x) for x in velas[-periodo:]]
    lows = [get_low(x) for x in velas[-periodo:]]
    hh = max(highs)
    ll = min(lows)
    if hh == ll:
        return 50
    return round(((get_close(velas[-1]) - ll) / (hh - ll)) * 100, 2)

def get_fase_vela():
    segundo = time.localtime().tm_sec
    if segundo < 20:
        return "🌅 NASCENDO"
    elif segundo < 45:
        return "☀️ VIVA"
    return "🌇 MORRENDO"

def rodar_analise(api, par, add_log):
    try:
        timeframe = INFO['timeframe']
        
        add_log("📊 V-Sensitivo: Sentindo a vela...", "indicator")
        
        velas = api.get_candles(par, timeframe, 30, time.time())
        
        if not velas or len(velas) < 20:
            add_log("⚠️ Dados insuficientes", "warning")
            return None
        
        # ========== CÁLCULO DOS INDICADORES ==========
        
        fase = get_fase_vela()
        rs = rsi(velas, 14)
        m5 = sma(velas, 5)
        m10 = sma(velas, 10)
        m20 = sma(velas, 20)
        bs, bm, bi = bollinger(velas, 20, 2)
        mc = macd(velas, 12, 26)
        st = estocastico(velas, 14)
        pc = get_close(velas[-1])
        
        add_log(f"   🔮 Fase: {fase}", "indicator")
        if rs:
            add_log(f"   📊 RSI: {rs:.1f}", "indicator")
        if st:
            add_log(f"   📊 Estocástico: {st:.1f}", "indicator")
        if m5 and m10 and m20:
            add_log(f"   📈 MM5: {m5:.5f} | MM10: {m10:.5f} | MM20: {m20:.5f}", "indicator")
        if mc:
            add_log(f"   📉 MACD: {mc:.8f}", "indicator")
        add_log(f"   💵 Preço: {pc:.5f}", "indicator")
        
        # ========== LÓGICA DE SINAL ==========
        
        sc = 0
        sp = 0
        sinais = []
        
        # Médias Móveis
        if m5 and m20:
            if m5 > m20:
                sc += 20
                sinais.append("MM5>MM20")
            else:
                sp += 20
                sinais.append("MM5<MM20")
        
        if m5 and m10:
            if m5 > m10:
                sc += 15
                sinais.append("MM5>MM10")
            else:
                sp += 15
                sinais.append("MM5<MM10")
        
        # RSI
        if rs:
            if rs < 30:
                sc += 25
                sinais.append(f"RSI={rs:.0f}↓")
            elif rs > 70:
                sp += 25
                sinais.append(f"RSI={rs:.0f}↑")
            elif rs > 50:
                sc += 10
            else:
                sp += 10
        
        # Bollinger
        if bs and bi and pc:
            if pc <= bi * 1.01:
                sc += 20
                sinais.append("BB↓")
            elif pc >= bs * 0.99:
                sp += 20
                sinais.append("BB↑")
        
        # MACD
        if mc:
            if mc > 0:
                sc += 15
                sinais.append("MACD+")
            else:
                sp += 15
                sinais.append("MACD-")
        
        # Estocástico
        if st:
            if st < 20:
                sc += 15
                sinais.append(f"E={st:.0f}↓")
            elif st > 80:
                sp += 15
                sinais.append(f"E={st:.0f}↑")
        
        # Fase da vela
        if fase == "🌇 MORRENDO":
            cor = 'V' if velas[-1]['open'] < velas[-1]['close'] else 'R'
            if cor == 'V':
                sp += 10
            else:
                sc += 10
        
        add_log(f"   🎯 SCORE: CALL={sc} PUT={sp}", "indicator")
        if sinais:
            add_log(f"   📋 Sinais: {' '.join(sinais[:3])}", "indicator")
        
        dif = abs(sc - sp)
        
        if sc > sp and dif >= 15:
            add_log(f"🎯 SINAL DE CALL! ({sc}x{sp})", "win")
            return {'direcao': 'call', 'timeframe': INFO['timeframe']}
        
        elif sp > sc and dif >= 15:
            add_log(f"🎯 SINAL DE PUT! ({sp}x{sc})", "win")
            return {'direcao': 'put', 'timeframe': INFO['timeframe']}
        
        add_log(f"⏳ Aguardando... ({sc}x{sp})", "info")
        return None
        
    except Exception as e:
        add_log(f"❌ Erro na análise: {e}", "error")
        return None
