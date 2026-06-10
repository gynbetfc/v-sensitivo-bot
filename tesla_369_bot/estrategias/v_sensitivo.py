# -*- coding: utf-8 -*-
# ESTRATÉGIA: V-Sensitivo Script
# Operação no INÍCIO da vela (entrada na virada do timeframe)

import time

INFO = {
    'nome': 'V-Sensitivo Script',
    'desc': 'Análise de momentum de velas com RSI, Estocástico, Médias Móveis, Bollinger e MACD. Entrada no início da vela.',
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
    return round(sum(get_close(x) for x in velas[-periodo:]) / periodo, 6)

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
    return round(100 - (100 / (1 + sum(ganhos[-periodo:]) / sum(perdas[-periodo:]))), 2)

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

def aguardar_inicio_vela_estrategia():
    """Aguarda o início da próxima vela para análise"""
    segundo_atual = time.localtime().tm_sec
    if segundo_atual <= 5:
        return True
    # Espera o próximo minuto
    while time.localtime().tm_sec > 1:
        time.sleep(0.1)
    return True

def rodar_analise(api, par, add_log):
    try:
        timeframe = INFO['timeframe']
        
        # ⭐ Aguarda o início da vela para fazer a análise
        add_log("📊 V-Sensitivo: Aguardando início da vela para análise...", "indicator")
        aguardar_inicio_vela_estrategia()
        
        add_log("📊 V-Sensitivo: Coletando dados do mercado...", "indicator")
        
        # Pega velas do timeframe atual
        velas = api.get_candles(par, timeframe, 50, time.time())
        
        if not velas or len(velas) < 30:
            add_log("⚠️ Dados insuficientes para análise", "warning")
            return None
        
        # ========== CÁLCULO DOS INDICADORES ==========
        
        # Médias Móveis
        mm5 = sma(velas, 5)
        mm10 = sma(velas, 10)
        mm20 = sma(velas, 20)
        mm50 = sma(velas, 50)
        
        # Preço atual
        pc = get_close(velas[-1])
        
        # RSI
        rs = rsi(velas, 14)
        
        # Estocástico
        st = estocastico(velas, 14)
        
        # Bollinger
        bs, bm, bi = bollinger(velas, 20, 2)
        
        add_log(f"   📊 RSI: {rs:.1f} | Estocástico: {st:.1f}", "indicator")
        if mm5 and mm20 and mm50:
            add_log(f"   📈 MM5: {mm5:.5f} | MM20: {mm20:.5f} | MM50: {mm50:.5f}", "indicator")
        add_log(f"   💵 Preço: {pc:.5f}", "indicator")
        
        # ========== LÓGICA DE SINAL ==========
        
        sc = 0  # Score CALL
        sp = 0  # Score PUT
        
        # 1. Médias Móveis (tendência de longo prazo)
        if mm5 and mm20 and mm50:
            if mm5 > mm20 and mm20 > mm50:
                sc += 25
                add_log("   ✅ Tendência de ALTA (MM5>MM20>MM50)", "indicator")
            elif mm5 < mm20 and mm20 < mm50:
                sp += 25
                add_log("   ⚠️ Tendência de BAIXA (MM5<MM20<MM50)", "indicator")
        
        # 2. Preço vs MM20
        if mm20:
            if pc > mm20:
                sc += 15
                add_log("   ✅ Preço acima da MM20", "indicator")
            else:
                sp += 15
                add_log("   ⚠️ Preço abaixo da MM20", "indicator")
        
        # 3. RSI
        if rs < 30:
            sc += 20
            add_log(f"   ✅ RSI sobrevendido ({rs:.0f} < 30)", "indicator")
        elif rs > 70:
            sp += 20
            add_log(f"   ⚠️ RSI sobrecomprado ({rs:.0f} > 70)", "indicator")
        elif rs < 50:
            sc += 5
        else:
            sp += 5
        
        # 4. Estocástico
        if st < 20:
            sc += 20
            add_log(f"   ✅ Estocástico sobrevendido ({st:.0f} < 20)", "indicator")
        elif st > 80:
            sp += 20
            add_log(f"   ⚠️ Estocástico sobrecomprado ({st:.0f} > 80)", "indicator")
        
        # 5. Bollinger (reversão)
        if bs and bi and pc:
            if pc <= bi * 1.005:
                sc += 20
                add_log("   ✅ Preço na banda INFERIOR", "indicator")
            elif pc >= bs * 0.995:
                sp += 20
                add_log("   ⚠️ Preço na banda SUPERIOR", "indicator")
        
        add_log(f"   🎯 SCORE: CALL={sc} | PUT={sp}", "indicator")
        
        # ⭐ Sinal apenas com diferença mínima
        if sc >= 40 and sc > sp + 20:
            add_log(f"🎯 SINAL DE CALL! ({sc}x{sp})", "win")
            return {'direcao': 'call', 'timeframe': INFO['timeframe']}
        
        elif sp >= 40 and sp > sc + 20:
            add_log(f"🎯 SINAL DE PUT! ({sp}x{sc})", "win")
            return {'direcao': 'put', 'timeframe': INFO['timeframe']}
        
        add_log(f"⏳ Sem sinal. CALL:{sc} PUT:{sp}", "info")
        return None
        
    except Exception as e:
        add_log(f"❌ Erro na análise: {e}", "error")
        import traceback
        traceback.print_exc()
        return None
