# -*- coding: utf-8 -*-
# ESTRATÉGIA: V-Sensitivo Script (NOVA)
# Análise de momentum com RSI, Estocástico e Médias Móveis

import time

INFO = {
    'nome': 'V-Sensitivo Script',
    'desc': 'Análise de momentum de velas com RSI, Estocástico e Médias Móveis.',
    'preco': 0,
    'timeframe': 60,
    'gratis': True
}

def calcular_rsi(velas, periodo=14):
    if len(velas) < periodo + 1:
        return 50
    ganhos = []
    perdas = []
    for i in range(1, len(velas)):
        diferenca = velas[i]['close'] - velas[i-1]['close']
        if diferenca >= 0:
            ganhos.append(diferenca)
            perdas.append(0)
        else:
            ganhos.append(0)
            perdas.append(abs(diferenca))
    ganhos = ganhos[-periodo:]
    perdas = perdas[-periodo:]
    ganho_medio = sum(ganhos) / periodo if ganhos else 0
    perda_media = sum(perdas) / periodo if perdas else 0
    if perda_media == 0:
        return 100
    rs = ganho_medio / perda_media
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calcular_estocastico(velas, periodo_k=14):
    if len(velas) < periodo_k:
        return 50
    ultimas_velas = velas[-periodo_k:]
    maior_alta = max(v['high'] for v in ultimas_velas)
    menor_baixa = min(v['low'] for v in ultimas_velas)
    ultimo_fechamento = velas[-1]['close']
    if maior_alta == menor_baixa:
        return 50
    return 100 * ((ultimo_fechamento - menor_baixa) / (maior_alta - menor_baixa))

def calcular_media_movel(velas, periodo):
    if len(velas) < periodo:
        return velas[-1]['close'] if velas else 0
    return sum(v['close'] for v in velas[-periodo:]) / periodo

def rodar_analise(api, par, add_log):
    try:
        global INFO
        timeframe = INFO['timeframe']
        
        add_log("📊 V-Sensitivo: Coletando dados do mercado...", "indicator")
        
        velas = api.get_candles(par, timeframe, 30, time.time())
        
        if not velas or len(velas) < 20:
            add_log("⚠️ Dados insuficientes", "warning")
            return None
        
        rsi = calcular_rsi(velas, 14)
        estocastico = calcular_estocastico(velas, 14)
        mm5 = calcular_media_movel(velas, 5)
        mm10 = calcular_media_movel(velas, 10)
        mm20 = calcular_media_movel(velas, 20)
        preco_atual = velas[-1]['close']
        
        add_log(f"   📊 RSI: {rsi:.1f} | Estocástico: {estocastico:.1f}", "indicator")
        add_log(f"   📈 MM5: {mm5:.5f} | MM10: {mm10:.5f} | MM20: {mm20:.5f}", "indicator")
        
        condicoes_call = 0
        condicoes_put = 0
        
        if rsi < 40: condicoes_call += 1
        elif rsi > 60: condicoes_put += 1
        
        if estocastico < 20: condicoes_call += 1
        elif estocastico > 80: condicoes_put += 1
        
        if mm5 > mm10 and mm10 > mm20: condicoes_call += 1
        elif mm5 < mm10 and mm10 < mm20: condicoes_put += 1
        
        if preco_atual > mm20: condicoes_call += 1
        elif preco_atual < mm20: condicoes_put += 1
        
        if condicoes_call >= 3:
            add_log(f"🎯 SINAL DE CALL!", "win")
            return {'direcao': 'call', 'timeframe': INFO['timeframe']}
        elif condicoes_put >= 3:
            add_log(f"🎯 SINAL DE PUT!", "win")
            return {'direcao': 'put', 'timeframe': INFO['timeframe']}
        
        return None
    except Exception as e:
        add_log(f"❌ Erro: {e}", "error")
        return None
