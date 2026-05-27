import requests, json
FB_URL = "https://nexos-40654-default-rtdb.firebaseio.com"

def _sanitizar_dados(dados):
    if 'historico_operacoes' in dados:
        if len(dados['historico_operacoes']) > 50:
            dados['historico_operacoes'] = dados['historico_operacoes'][-50:]
    return dados

def salvar_usuario(email, dados):
    try:
        key = email.replace("@", "_").replace(".", "_").replace("#", "").replace("$", "").replace("[", "").replace("]", "").replace("/", "_")
        dados = _sanitizar_dados(dados)
        requests.put(f'{FB_URL}/usuarios/{key}.json', json=dados)
    except Exception as e:
        print(f"⚠️ Firebase offline: {e}")

def carregar_usuario(email):
    try:
        key = email.replace("@", "_").replace(".", "_").replace("#", "").replace("$", "").replace("[", "").replace("]", "").replace("/", "_")
        r = requests.get(f'{FB_URL}/usuarios/{key}.json')
        if r.status_code == 200 and r.json():
            return r.json()
    except: pass
    return None

def criar_usuario(email):
    from datetime import datetime
    dados = {
        'email': email, 'moedas': 1,
        'moedas_ganhas_hoje': str(datetime.now())[:10],
        'total_ciclos': 0, 'total_wins': 0, 'total_losses': 0,
        'total_gasto': 0.0, 'total_ganho': 0.0, 'lucro_total': 0.0,
        'banca_atual': 0.0, 'data_cadastro': str(datetime.now())[:19],
        'historico_operacoes': [], 'dias_ativos': 0,
        'skin_atual': 'skin_padrao', 'skins_compradas': ['skin_padrao'],
        'estrategias_compradas': ['tesla_369']
    }
    salvar_usuario(email, dados)
    return dados
