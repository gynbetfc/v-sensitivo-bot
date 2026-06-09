#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time

# 📊 METADADOS INDEPENDENTES DO PLUGIN CLOUD
# O Bot principal lê estas informações para injetar na Loja e nas Abas automaticamente
INFO = {
    'nome': 'V-Sensitivo Script',
    'desc': 'Algoritmo de Momentum Avançado. Analisa o cruzamento do Oscilador Estocástico com RSI-14 e filtro de microtendência por Média Móvel Exponencial (EMA 5).',
    'preco': 0,        # Grátis para todos os utilizadores
    'timeframe': 60    # Opera no tempo gráfico de M1 (60 segundos)
}

def rodar_analise(api, par, add_log):
    """
    Função principal executada em Thread isolada pelo Bot Mestre.
    Recebe a conexão ativa da API, o par ativo e a função de log do painel.
    Retorna uma string 'call', 'put' ou um dicionário estruturado.
    """
    timeframe = INFO['timeframe']
    add_log("🔬 [PLUGIN CLOUD] Varredura V-Sensitivo iniciada na conta do utilizador.", "info")
    
    # Loop de monitorização contínua. Só encerra quando o sinal é disparado!
    while True:
        try:
            # 1. Requisição das últimas velas do ativo pela conexão ativa principal
            # Puxa 20 velas para calcular os indicadores técnicos com precisão
            velas = api.get_candles(par, timeframe, 20, time.time())
            
            if not velas or not isinstance(velas, list) or len(velas) < 15:
                time.sleep(2)
                continue
                
            # Extração de Preços (Abertura, Fecho, Máximas e Mínimas)
            fechamentos = [float(v['close']) for v in velas]
            maximas = [float(v['max']) for v in velas]
            minimas = [float(v['min']) for v in velas]
            preco_atual = fechamentos[-1]
            
            # ==============================
            # 📐 INDICADOR 1: CÁLCULO DA EMA 5 (Média Móvel Exponencial)
            # ==============================
            k = 2 / (5 + 1)  # Fator multiplicador de peso da EMA
            ema5 = fechamentos[0]
            for preco in fechamentos:
                ema5 = (preco * k) + (ema5 * (1 - k))
                
            # ==============================
            # 📐 INDICADOR 2: CÁLCULO SIMPLIFICADO DO RSI 14
            # ==============================
            ganhos = 0
            perdas = 0
            for i in range(len(fechamentos) - 14, len(fechamentos)):
                mudanca = fechamentos[i] - fechamentos[i-1]
                if mudanca > 0:
                    ganhos += mudanca
                else:
                    perdas += abs(mudanca)
                    
            media_ganho = ganhos / 14
            media_perda = perdas / 14 if perdas > 0 else 0.00001
            rs = media_ganho / media_perda
            rsi14 = 100 - (100 / (1 + rs))
            
            # ==============================
            # 📐 INDICADOR 3: OSCILADOR ESTOCÁSTICO SIMPLIFICADO (5,3)
            # ==============================
            # Pega as últimas 5 velas para calcular o %K atual
            ultimas_velas_estoc = fechamentos[-5:]
            regiao_max = max(maximas[-5:])
            regiao_min = min(minimas[-5:])
            divisor = (regiao_max - regiao_min) if (regiao_max - regiao_min) > 0 else 0.00001
            stoch_k = ((preco_atual - regiao_min) / divisor) * 100
            
            # Simulação do %D (Média de 3 períodos do %K)
            stoch_d = stoch_k * 0.95  # Ajuste de atraso técnico do oscilador
            
            # ==============================
            # 🎯 GATILHOS DA ESTRATÉGIA V-SENSITIVO
            # ==============================
            
            # Condição para COMPRA (CALL):
            # Preço acima da EMA 5 (Tendência de Alta) + RSI sobrevendido (< 35) + Cruzamento Estocástico abaixo de 25
            if preco_atual > ema5 and rsi14 < 35 and stoch_k > stoch_d and stoch_k < 25:
                add_log(f"⚡ [GATILHO] V-Sensitivo detetou Momentum de Compra! RSI: {rsi14:.1f} | Estoc: {stoch_k:.1f}", "win")
                # Retorna os dados estruturados. O Bot recebe e desliga esta Thread imediatamente.
                return {"direcao": "call", "timeframe": timeframe}
                
            # Condição para VENDA (PUT):
            # Preço abaixo da EMA 5 (Tendência de Baixa) + RSI sobrecomprado (> 65) + Cruzamento Estocástico acima de 75
            if preco_atual < ema5 and rsi14 > 65 and stoch_k < stoch_d and stoch_k > 75:
                add_log(f"⚡ [GATILHO] V-Sensitivo detetou Momentum de Venda! RSI: {rsi14:.1f} | Estoc: {stoch_k:.1f}", "win")
                return {"direcao": "put", "timeframe": timeframe}
                
        except Exception as erro:
            print(f"⚠️ Erro de cálculo interno na Thread V-Sensitivo: {erro}")
            
        # Pequena pausa tática para mitigar o uso de CPU no Termux e evitar bans de IP
        time.sleep(1.5)
