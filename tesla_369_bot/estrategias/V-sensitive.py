# -*- coding: utf-8 -*-
# ESTRATÉGIA: V-Sensitivo Script
# Análise de momentum de velas com RSI, Estocástico e Médias Móveis

import time
import math

INFO = {
    'nome': 'V-Sensitivo Script',
    'desc': 'Análise de momentum de velas com RSI, Estocástico e Médias Móveis.',
    'preco': 3,
    'timeframe': 60,
    'gratis': False
}

def calcular_rsi(velas, periodo=14):
    """Calcula RSI a partir das velas"""
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
    """Calcula Estocástico %K"""
    if len(velas) < periodo_k:
        return 50
    
    ultimas_velas = velas[-periodo_k:]
    
    maior_alta = max(v['high'] for v in ultimas_velas)
    menor_baixa = min(v['low'] for v in ultimas_velas)
    ultimo_fechamento = velas[-1]['close']
    
    if maior_alta == menor_baixa:
        return 50
    
    k = 100 * ((ultimo_fechamento - menor_baixa) / (maior_alta - menor_baixa))
    return k

def calcular_media_movel(velas, periodo):
    """Calcula média móvel simples"""
    if len(velas) < periodo:
        return velas[-1]['close'] if velas else 0
    
    ultimas_velas = velas[-periodo:]
    return sum(v['close'] for v in ultimas_velas) / periodo

def rodar_analise(api, par, add_log):
    """
    Função principal da estratégia.
    Retorna {'direcao': 'call' ou 'put', 'timeframe': 60}
    ou None se não houver sinal.
    """
    try:
        # ⭐ USA A VARIÁVEL GLOBAL INFO
        global INFO
        timeframe = INFO['timeframe']
        
        add_log("📊 V-Sensitivo: Coletando dados do mercado...", "indicator")
        
        # Pega as últimas 30 velas
        velas = api.get_candles(par, timeframe, 30, time.time())
        
        if not velas or len(velas) < 20:
            add_log("⚠️ V-Sensitivo: Dados insuficientes para análise", "warning")
            return None
        
        # ========== CÁLCULO DOS INDICADORES ==========
        
        rsi = calcular_rsi(velas, 14)
        add_log(f"   📊 RSI: {rsi:.1f}", "indicator")
        
        estocastico = calcular_estocastico(velas, 14)
        add_log(f"   📊 Estocástico: {estocastico:.1f}", "indicator")
        
        mm5 = calcular_media_movel(velas, 5)
        mm10 = calcular_media_movel(velas, 10)
        mm20 = calcular_media_movel(velas, 20)
        preco_atual = velas[-1]['close']
        
        add_log(f"   📈 MM5: {mm5:.5f} | MM10: {mm10:.5f} | MM20: {mm20:.5f}", "indicator")
        add_log(f"   💵 Preço: {preco_atual:.5f}", "indicator")
        
        # ========== LÓGICA DE SINAL ==========
        
        condicoes_call = 0
        condicoes_put = 0
        
        # 1. RSI
        if rsi < 40:
            condicoes_call += 1
            add_log("   ✅ RSI sobrevendido (<40)", "indicator")
        elif rsi > 60:
            condicoes_put += 1
            add_log("   ⚠️ RSI sobrecomprado (>60)", "indicator")
        
        # 2. Estocástico
        if estocastico < 20:
            condicoes_call += 1
            add_log("   ✅ Estocástico sobrevendido (<20)", "indicator")
        elif estocastico > 80:
            condicoes_put += 1
            add_log("   ⚠️ Estocástico sobrecomprado (>80)", "indicator")
        
        # 3. Médias Móveis
        if mm5 > mm10 and mm10 > mm20:
            condicoes_call += 1
            add_log("   ✅ Tendência de alta (MM5 > MM10 > MM20)", "indicator")
        elif mm5 < mm10 and mm10 < mm20:
            condicoes_put += 1
            add_log("   ⚠️ Tendência de baixa (MM5 < MM10 < MM20)", "indicator")
        
        # 4. Preço vs MM20
        if preco_atual > mm20:
            condicoes_call += 1
            add_log("   ✅ Preço acima da MM20", "indicator")
        elif preco_atual < mm20:
            condicoes_put += 1
            add_log("   ⚠️ Preço abaixo da MM20", "indicator")
        
        # ========== DECISÃO FINAL ==========
        
        if condicoes_call >= 3:
            add_log(f"🎯 V-Sensitivo: Sinal de CALL confirmado! ({condicoes_call}/4 condições)", "win")
            return {'direcao': 'call', 'timeframe': INFO['timeframe']}
        
        elif condicoes_put >= 3:
            add_log(f"🎯 V-Sensitivo: Sinal de PUT confirmado! ({condicoes_put}/4 condições)", "win")
            return {'direcao': 'put', 'timeframe': INFO['timeframe']}
        
        else:
            add_log(f"⏳ V-Sensitivo: Nenhum sinal forte. CALL:{condicoes_call} PUT:{condicoes_put}", "info")
            return None
        
    except Exception as e:
        add_log(f"❌ Erro na análise V-Sensitivo: {e}", "error")
        return None
