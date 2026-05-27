"""
Estratégia: M5
Extraída automaticamente do TESLA 369
"""

import time
from datetime import datetime

ESTRATEGIA_INFO = {
    'nome': 'M5',
    'descricao': 'Estratégia extraída do TESLA 369',
    'timeframe': 60,
    'pares': ['EURUSD-OTC'],
    'preco_moedas': 0,
    'gratis': True
}

def sinal_m5():
    global ultimo_sinal, ultima_analise
    try:
        agora = datetime.now()
        if agora.minute % 15 != 0: ultimo_sinal = f"⏳ M5: min {agora.minute} (15/30/45/0)"; return None
        time.sleep(2)
        v = API.get_candles(par, timeframe_atual, 7, time.time())
        if len(v) < 7: return None
        velas = []
        for vela in v:
            if vela['open'] < vela['close']: velas.append('g')
            elif vela['open'] > vela['close']: velas.append('r')
            else: velas.append('d')
        pc = v[-1]['close']
        ultima_analise = {'preco': pc, 'rsi': None, 'mm5': None, 'mm10': None, 'mm20': None, 'stoch': None, 'fase': 'M5'}
        add_log(f"⏰ M5 | Velas: {''.join(velas)}", 'indicator')
        if velas[0] == velas[1] and velas[1] == velas[2] and velas[3] == velas[4] and velas[4] == velas[5]:
            if velas[6] == 'g' and 'd' not in velas: ultimo_sinal = "⏰ PUT (M5)"; add_log("M5: PUT!", 'sensitive'); return 'put'
            if velas[6] == 'r' and 'd' not in velas: ultimo_sinal = "⏰ CALL (M5)"; add_log("M5: CALL!", 'sensitive'); return 'call'
        ultimo_sinal = "⏳ Sem sinal M5"; return None
    except Exception as e: add_log(f"Erro: {e}", 'error'); return None

MAPA_SINAIS = {
    'v_sensitivo': sinal_v_sensitivo,
    'tesla_369': sinal_tesla_369,
    'terceira_igual_primeira': sinal_terceira_igual_primeira,
    'mhi_filtrado': sinal_mhi_filtrado,
    'quadrante_de_7': sinal_quadrante_de_7,
    'fluxo_de_velas': sinal_fluxo_de_velas,
    'reversao': sinal_reversao,
    'm5': sinal_m5
}

@app.route('/set_percentual', methods=['POST'])
