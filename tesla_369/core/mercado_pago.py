import os, requests, uuid
from datetime import datetime

MERCADO_PAGO_ACCESS_TOKEN = os.environ.get("MP_ACCESS_TOKEN", "APP_USR-4548266140377032-050311-6589fc22b166e4cb2cfad0379b28dcdf-1059299796")
MERCADO_PAGO_PUBLIC_KEY = os.environ.get("MP_PUBLIC_KEY", "APP_USR-39e1950e-420d-479a-8125-902009ca3445")
MODO_SIMULACAO = False
pagamentos_pendentes = {}

def gerar_pix_mercadopago(email, plano):
    if MODO_SIMULACAO:
        pix_id = str(uuid.uuid4())[:8]
        pagamentos_pendentes[pix_id] = {'email': email, 'plano_id': plano['id'], 'moedas': plano.get('moedas',0), 'valor': plano.get('preco',0), 'pago': False}
        return {'sucesso': True, 'simulacao': True, 'pix_id': pix_id, 'qr_code': f"SIMULACAO PIX R$ {plano.get('preco',0):.2f}", 'qr_code_base64': '', 'valor': plano.get('preco',0), 'moedas': plano.get('moedas',0)}
    try:
        url = "https://api.mercadopago.com/v1/payments"
        headers = {"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}", "Content-Type": "application/json", "X-Idempotency-Key": str(uuid.uuid4())}
        payment_data = {"transaction_amount": float(plano.get('preco',0)), "description": f"TESLA369 - {plano.get('nome','')}", "payment_method_id": "pix", "payer": {"email": email}}
        response = requests.post(url, json=payment_data, headers=headers)
        data = response.json()
        if response.status_code in [200, 201]:
            pix_id = str(data['id'])
            qr = data['point_of_interaction']['transaction_data']
            pagamentos_pendentes[pix_id] = {'email': email, 'plano_id': plano['id'], 'moedas': plano.get('moedas',0), 'valor': plano.get('preco',0), 'pago': False}
            return {'sucesso': True, 'pix_id': pix_id, 'qr_code': qr['qr_code'], 'qr_code_base64': qr['qr_code_base64'], 'valor': plano.get('preco',0), 'moedas': plano.get('moedas',0)}
        return {'sucesso': False, 'erro': data.get('message', 'Erro')}
    except Exception as e: return {'sucesso': False, 'erro': str(e)}

def verificar_pagamento_mp(pix_id):
    if MODO_SIMULACAO: return pagamentos_pendentes.get(pix_id, {}).get('pago', False)
    try:
        url = f"https://api.mercadopago.com/v1/payments/{pix_id}"
        headers = {"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}"}
        return requests.get(url, headers=headers).json().get('status') == 'approved'
    except: return False
