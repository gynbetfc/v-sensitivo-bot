# main.py - PDV INTELIGENTE v8.0.0 - COM VERIFICAÇÃO AUTOMÁTICA DE COLUNAS
"""
PDV INTELIGENTE - COMPLETO
- Compatível com Termux/Android/Linux
- Busca inteligente de produtos por código de barras
- APIs: OpenFoodFacts, BrasilAPI, Product Search
- VERIFICAÇÃO AUTOMÁTICA DE TODAS AS COLUNAS DO BANCO
"""
from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
import sqlite3
import json
import os
import hashlib
import secrets
import requests
import uuid
import socket
import threading
import logging
from datetime import datetime, timedelta
from contextlib import contextmanager
from functools import wraps
import sys
import re

# ===== CORREÇÃO: IMPORTAR time CORRETAMENTE =====
import time as _time

# ===== VERIFICAÇÃO DO SISTEMA OPERACIONAL =====
IS_WINDOWS = sys.platform == 'win32'
IS_LINUX = sys.platform.startswith('linux')
IS_TERMUX = 'com.termux' in os.environ.get('PREFIX', '')

# ===== IMPORTAÇÕES CONDICIONAIS =====
if IS_WINDOWS:
    try:
        import win32print
        import win32ui
        from PIL import Image, ImageDraw, ImageFont
        import qrcode
        from io import BytesIO
        IMPRESSAO_DISPONIVEL = True
        print("🖨️ Impressão Windows disponível")
    except ImportError:
        IMPRESSAO_DISPONIVEL = False
        print("⚠️ Módulos de impressão não encontrados. Impressão desabilitada.")
else:
    IMPRESSAO_DISPONIVEL = False
    print("🐧 Sistema Linux/Termux detectado. Impressão desabilitada.")

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False

CORS(app, origins=["*"], supports_credentials=True)

VERSION = "8.0.0"

# ===== CONFIGURAÇÕES DE LOG =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdv.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ===== CONFIGURAÇÕES =====
FB_URL = "https://nexos-40654-default-rtdb.firebaseio.com"
HTML_URL = "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/refs/heads/main/PDV/templates/index.html"
SESSOES_ATIVAS = {}
CACHE_CNPJ = {}
CACHE_PRODUTO_BARRAS = {}

# ===== MERCADO PAGO =====
MERCADO_PAGO_ACCESS_TOKEN = os.environ.get(
    "MP_ACCESS_TOKEN",
    "APP_USR-4548266140377032-050311-6589fc22b166e4cb2cfad0379b28dcdf-1059299796"
)

# ===== PLANOS =====
PLANOS = [
    {'id': 1, 'usuarios': 1, 'preco': 0.01, 'nome': '🔰 BÁSICO', 'dias': 7},
    {'id': 2, 'usuarios': 3, 'preco': 0.01, 'nome': '⭐ STANDARD', 'dias': 30},
    {'id': 3, 'usuarios': 5, 'preco': 0.01, 'nome': '💎 PREMIUM', 'dias': 90},
    {'id': 4, 'usuarios': 10, 'preco': 0.01, 'nome': '🔥 EMPRESARIAL', 'dias': 365},
    {'id': 5, 'usuarios': 2, 'preco': 0.01, 'nome': '🧪 TESTE 3 MIN', 'dias': 0.00208333},
]

pagamentos_pendentes = {}

# ===== RATE LIMITING =====
rate_limits = {}

def rate_limit(max_requests=10, window=60):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            key = request.remote_addr
            now = _time.time()
            
            if key not in rate_limits:
                rate_limits[key] = []
            
            rate_limits[key] = [t for t in rate_limits[key] if now - t < window]
            
            if len(rate_limits[key]) >= max_requests:
                return jsonify({
                    "success": False,
                    "error": "Muitas requisições. Tente novamente em alguns segundos."
                }), 429
            
            rate_limits[key].append(now)
            return f(*args, **kwargs)
        return wrapped
    return decorator

# ============================================================
# FUNÇÃO PARA VERIFICAR E ADICIONAR COLUNAS AUTOMATICAMENTE
# ============================================================

def verificar_e_adicionar_colunas(conn, tabela, colunas_necessarias):
    """
    Verifica se as colunas existem na tabela e adiciona se não existirem.
    
    Args:
        conn: Conexão SQLite
        tabela: Nome da tabela
        colunas_necessarias: Dict com {'nome_coluna': 'tipo_sql DEFAULT valor'}
    
    Returns:
        Lista de colunas adicionadas
    """
    colunas_adicionadas = []
    
    try:
        # Obter colunas existentes
        cursor = conn.execute(f"PRAGMA table_info({tabela})")
        colunas_existentes = [row[1] for row in cursor.fetchall()]
        
        # Verificar cada coluna necessária
        for coluna, tipo in colunas_necessarias.items():
            if coluna not in colunas_existentes:
                try:
                    conn.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {tipo}")
                    colunas_adicionadas.append(coluna)
                    logger.info(f"✅ Coluna '{coluna}' adicionada à tabela {tabela}")
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao adicionar coluna '{coluna}' em {tabela}: {e}")
        
        return colunas_adicionadas
    except Exception as e:
        logger.error(f"❌ Erro ao verificar colunas da tabela {tabela}: {e}")
        return colunas_adicionadas

# ============================================================
# DOWNLOAD AUTOMÁTICO DO HTML
# ============================================================

def baixar_html_github():
    try:
        logger.info("🔄 Baixando HTML do GitHub...")
        os.makedirs("templates", exist_ok=True)
        caminho_html = os.path.join("templates", "index.html")
        
        response = requests.get(HTML_URL, timeout=30)
        response.raise_for_status()
        
        with open(caminho_html, "w", encoding="utf-8") as f:
            f.write(response.text)
        
        logger.info(f"✅ HTML baixado com sucesso! ({len(response.text)} caracteres)")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao baixar HTML: {e}")
        return False

# ============================================================
# CONEXÃO SQLITE COM WAL
# ============================================================

@contextmanager
def get_db(db_path):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = None
    try:
        conn = sqlite3.connect(db_path, timeout=30, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        conn.execute("PRAGMA busy_timeout=30000")
        conn.execute("PRAGMA temp_store=MEMORY")
        yield conn
        conn.commit()
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            _time.sleep(0.5)
            try:
                conn = sqlite3.connect(db_path, timeout=30, check_same_thread=False)
                conn.row_factory = sqlite3.Row
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=NORMAL")
                conn.execute("PRAGMA busy_timeout=30000")
                yield conn
                conn.commit()
            except Exception as e2:
                raise e2
        else:
            raise e
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

# ============================================================
# FUNÇÕES FIREBASE
# ============================================================


def validar_cnpj_firebase(cnpj):
    """Verifica se um CNPJ já existe no Firebase"""
    try:
        url = f'{FB_URL}/pdv/usuarios.json'
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            usuarios = response.json()
            if usuarios:
                for key, dados in usuarios.items():
                    if dados.get('cnpj') == cnpj:
                        return True
        return False
    except:
        return False


def _fb_key(db_id):
    return db_id.replace(".", "_").replace("@", "_").replace("#", "").replace("$", "").replace("[", "").replace("]", "").replace("/", "_")

def salvar_usuario_firebase(db_id, dados):
    try:
        key = _fb_key(db_id)
        url = f'{FB_URL}/pdv/usuarios/{key}.json'
        response = requests.put(url, json=dados, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"⚠️ Erro Firebase: {e}")
        return False

def carregar_usuario_firebase(db_id):
    if not db_id:
        return None
    try:
        key = _fb_key(db_id)
        url = f'{FB_URL}/pdv/usuarios/{key}.json'
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        logger.error(f"⚠️ Erro Firebase: {e}")
        return None

def criar_usuario_firebase(db_id, nome, email, servidor_id, nome_loja="", cnpj="", cnpj_dados=None):
    dados = {
        'db_id': db_id,
        'nome': nome,
        'email': email,
        'servidor_id': servidor_id,
        'nome_loja': nome_loja,
        'cnpj': cnpj,
        'cnpj_dados': cnpj_dados or {},
        'data_cadastro': datetime.now().isoformat(),
        'plano': 1,
        'expira_em': (datetime.now() + timedelta(days=7)).isoformat(),
        'produtos': {},
        'clientes': {},
        'vendas': [],
        'caixa': {'status': 'fechado'},
        'config': {}
    }
    salvar_usuario_firebase(db_id, dados)
    return dados

# ============================================================
# GERAR ID DO SERVIDOR
# ============================================================

def obter_id_servidor():
    try:
        with get_db('data/config.db') as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS config (
                    chave TEXT PRIMARY KEY,
                    valor TEXT,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor = conn.execute("SELECT valor FROM config WHERE chave = 'servidor_id'")
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                hostname = socket.gethostname()
                servidor_id = f"SERV_{hostname[:6].upper()}_{str(uuid.uuid4())[:6]}"
                conn.execute("INSERT INTO config (chave, valor) VALUES (?, ?)",
                            ('servidor_id', servidor_id))
                return servidor_id
    except Exception as e:
        logger.error(f"⚠️ Erro ao gerar ID: {e}")
        return f"SERV_{str(uuid.uuid4())[:12]}"

SERVIDOR_ID = obter_id_servidor()

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def get_db_id():
    return session.get('db_id')

def get_usuario_id():
    return session.get('usuario_id')

def is_plano_ativo(db_id):
    if not db_id:
        return False
    dados = carregar_usuario_firebase(db_id)
    if not dados:
        return False
    expira = dados.get('expira_em')
    if not expira:
        return False
    try:
        expira_date = datetime.fromisoformat(expira)
        return expira_date >= datetime.now()
    except:
        return False

def get_dias_restantes(db_id):
    if not db_id:
        return 0
    dados = carregar_usuario_firebase(db_id)
    if not dados:
        return 0
    expira = dados.get('expira_em')
    if not expira:
        return 0
    try:
        expira_date = datetime.fromisoformat(expira)
        return max(0, (expira_date - datetime.now()).total_seconds() / 86400)
    except:
        return 0

def plano_bloqueado_response():
    return jsonify({
        "success": False,
        "error": "Seu plano expirou! Renove para continuar usando o PDV.",
        "plano_expirado": True
    }), 403

# ============================================================
# BUSCA INTELIGENTE DE PRODUTO POR CÓDIGO DE BARRAS
# ============================================================

def buscar_produto_por_codigo_barras(codigo_barras):
    """
    Busca informações de um produto pelo código de barras (GTIN/EAN)
    usando APIs oficiais que realmente funcionam
    """
    codigo_limpo = ''.join(filter(str.isdigit, codigo_barras))
    
    if len(codigo_limpo) < 8:
        return {"success": False, "error": "Código de barras inválido. Mínimo 8 dígitos."}
    
    # Verificar cache (7 dias)
    if codigo_limpo in CACHE_PRODUTO_BARRAS:
        cache_data = CACHE_PRODUTO_BARRAS[codigo_limpo]
        if _time.time() - cache_data['timestamp'] < 604800:
            logger.info(f"📦 Produto {codigo_limpo} retornado do cache")
            return {"success": True, "dados": cache_data['dados'], "fonte": "cache"}
    
    logger.info(f"🔍 Buscando produto {codigo_limpo}...")
    
    # ===== FONTE 1: OpenFoodFacts (GRATUITA E CONFIÁVEL) =====
    try:
        url = f"https://world.openfoodfacts.org/api/v0/product/{codigo_limpo}.json"
        response = requests.get(url, timeout=10, headers={
            "User-Agent": "PDV-Inteligente/8.0 - https://github.com/seu-repo"
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 1 and data.get('product'):
                produto = data['product']
                
                nome = produto.get('product_name', '') or produto.get('generic_name', '')
                if not nome:
                    nome = produto.get('product_name_pt', '') or produto.get('product_name_en', '')
                
                marca = produto.get('brands', '')
                if marca and ',' in marca:
                    marca = marca.split(',')[0].strip()
                
                categorias = produto.get('categories', '')
                if categorias:
                    categorias = categorias.split(',')[0].strip()
                
                dados_produto = {
                    "nome": nome or f"Produto {codigo_limpo}",
                    "marca": marca or "",
                    "categoria": categorias or "Geral",
                    "descricao": produto.get('ingredients_text', '') or produto.get('ingredients_text_pt', ''),
                    "imagem": produto.get('image_url', ''),
                    "gtin": codigo_limpo,
                    "fonte": "OpenFoodFacts"
                }
                
                CACHE_PRODUTO_BARRAS[codigo_limpo] = {
                    'dados': dados_produto,
                    'timestamp': _time.time()
                }
                
                logger.info(f"✅ Produto {codigo_limpo} encontrado via OpenFoodFacts")
                return {"success": True, "dados": dados_produto, "fonte": "OpenFoodFacts"}
    except Exception as e:
        logger.error(f"⚠️ Erro OpenFoodFacts: {e}")
    
    # ===== FONTE 2: BrasilAPI (PRODUTOS BRASILEIROS) =====
    try:
        url = f"https://brasilapi.com.br/api/gtin/v1/{codigo_limpo}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('gtin'):
                dados_produto = {
                    "nome": data.get('nome', '') or data.get('descricao', '') or f"Produto {codigo_limpo}",
                    "marca": data.get('marca', ''),
                    "categoria": data.get('categoria', '') or data.get('classe', '') or "Geral",
                    "gtin": data.get('gtin', codigo_limpo),
                    "fonte": "BrasilAPI"
                }
                
                CACHE_PRODUTO_BARRAS[codigo_limpo] = {
                    'dados': dados_produto,
                    'timestamp': _time.time()
                }
                
                logger.info(f"✅ Produto {codigo_limpo} encontrado via BrasilAPI")
                return {"success": True, "dados": dados_produto, "fonte": "BrasilAPI"}
    except Exception as e:
        logger.error(f"⚠️ Erro BrasilAPI: {e}")
    
    # ===== FONTE 3: Product Search (VIA SCRAPING - FALLBACK) =====
    try:
        ps_url = f"https://pt.product-search.net/?q={codigo_limpo}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml",
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"
        }
        
        response = requests.get(ps_url, timeout=15, headers=headers)
        
        if response.status_code == 200:
            html = response.text
            
            nome_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
            if nome_match:
                nome = nome_match.group(1).replace(' - Product Search', '').strip()
            else:
                nome_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE)
                nome = nome_match.group(1).strip() if nome_match else ""
            
            marca_match = re.search(r'(?:Brand|Marca)[^<]*<[^>]*>(.*?)<', html, re.IGNORECASE)
            marca = marca_match.group(1).strip() if marca_match else ""
            
            if nome:
                dados_produto = {
                    "nome": nome,
                    "marca": marca,
                    "categoria": "Geral",
                    "gtin": codigo_limpo,
                    "fonte": "Product Search"
                }
                
                CACHE_PRODUTO_BARRAS[codigo_limpo] = {
                    'dados': dados_produto,
                    'timestamp': _time.time()
                }
                
                logger.info(f"✅ Produto {codigo_limpo} encontrado via Product Search")
                return {"success": True, "dados": dados_produto, "fonte": "Product Search"}
    except Exception as e:
        logger.error(f"⚠️ Erro Product Search: {e}")
    
    # ===== FONTE 4: Fallback - Gerar nome a partir do código =====
    dados_produto = {
        "nome": f"Produto {codigo_limpo}",
        "marca": "",
        "categoria": "Geral",
        "gtin": codigo_limpo,
        "fonte": "Fallback (criado automaticamente)"
    }
    
    CACHE_PRODUTO_BARRAS[codigo_limpo] = {
        'dados': dados_produto,
        'timestamp': _time.time()
    }
    
    logger.info(f"⚠️ Produto {codigo_limpo} não encontrado - criando entrada padrão")
    return {"success": True, "dados": dados_produto, "fonte": "Fallback"}

# ============================================================
# IMPRESSÃO DE CUPOM (FORMATAÇÃO PROFISSIONAL)
# ============================================================

def imprimir_cupom(dados_impressao):
    if not IS_WINDOWS or not IMPRESSAO_DISPONIVEL:
        logger.info(f"🖨️ Impressão simulada: Venda #{dados_impressao.get('venda_id', '')}")
        return {"success": True, "message": "Impressão simulada (ambiente não Windows)"}
    
    try:
        # Dados do cupom
        nome_loja = dados_impressao.get('nome_loja', 'MINHA LOJA')
        cnpj = dados_impressao.get('cnpj', '')
        data_hora = dados_impressao.get('data_hora', datetime.now().strftime('%d/%m/%Y %H:%M'))
        venda_id = dados_impressao.get('venda_id', '')
        itens = dados_impressao.get('itens', [])
        subtotal = dados_impressao.get('subtotal', 0)
        desconto = dados_impressao.get('desconto', 0)
        total = dados_impressao.get('total', 0)
        metodo = dados_impressao.get('metodo', 'Dinheiro')
        cliente = dados_impressao.get('cliente', '')
        usuario = dados_impressao.get('usuario', '')

        # Formatar CNPJ
        if cnpj and len(cnpj) == 14:
            cnpj = f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}"

        # Construir texto do cupom (formatação profissional para 80mm)
        linhas = []
        largura = 48  # 80mm = 48 caracteres

        # Cabeçalho
        linhas.append('=' * largura)
        linhas.append(nome_loja.center(largura))
        if cnpj:
            linhas.append(f'CNPJ: {cnpj}'.center(largura))
        linhas.append('-' * largura)
        linhas.append('CUPOM FISCAL'.center(largura))
        linhas.append(f'Data: {data_hora}'.center(largura))
        if venda_id:
            linhas.append(f'Venda: #{venda_id}'.center(largura))
        linhas.append('=' * largura)
        linhas.append('')

        # Itens
        linhas.append('ITEM'.ljust(3) + 'DESCRIÇÃO'.ljust(25) + 'QTD'.rjust(4) + 'TOTAL'.rjust(16))
        linhas.append('-' * largura)

        for idx, item in enumerate(itens, 1):
            nome = item.get('nome', 'Item')[:22]
            qtd = item.get('quantidade', 1)
            total_item = item.get('total', 0)
            preco_unit = item.get('preco_unitario', 0)

            linhas.append(f"{str(idx).ljust(3)}{nome.ljust(25)}{str(qtd).rjust(4)}{f'R$ {total_item:.2f}'.rjust(16)}")
            if qtd > 1 and preco_unit:
                linhas.append(f"{' '*3}{'R$ ' + f'{preco_unit:.2f}'.rjust(6)} x {qtd}".ljust(largura - 10))

        linhas.append('-' * largura)

        # Totais
        linhas.append(f"{'SUBTOTAL:'.ljust(32)}R$ {subtotal:.2f}".rjust(largura))
        if desconto > 0:
            linhas.append(f"{'DESCONTO:'.ljust(32)}R$ {desconto:.2f}".rjust(largura))
        linhas.append(f"{'TOTAL:'.ljust(32)}R$ {total:.2f}".rjust(largura))
        linhas.append('-' * largura)

        # Forma de pagamento
        linhas.append(f"FORMA DE PAGAMENTO: {metodo}".center(largura))
        if cliente:
            linhas.append(f"CLIENTE: {cliente}".center(largura))
        if usuario:
            linhas.append(f"OPERADOR: {usuario}".center(largura))

        linhas.append('=' * largura)
        linhas.append('')
        linhas.append('VOLTE SEMPRE!'.center(largura))
        linhas.append('=' * largura)

        # Texto completo do cupom
        texto_cupom = '\n'.join(linhas) + '\n\n'

        # === IMPRESSÃO DIRETA (sem janela) ===
        # Usar a impressora padrão do Windows
        impressora_nome = win32print.GetDefaultPrinter()
        
        if not impressora_nome:
            return {"success": False, "error": "Nenhuma impressora padrão definida"}

        # Abrir impressora
        hprinter = win32print.OpenPrinter(impressora_nome)
        try:
            # Configurar para impressão térmica (RAW)
            dados_bytes = texto_cupom.encode('latin-1', 'replace')
            
            win32print.StartDocPrinter(hprinter, 1, ("Cupom Fiscal", None, "RAW"))
            win32print.StartPagePrinter(hprinter)
            win32print.WritePrinter(hprinter, dados_bytes)
            win32print.EndPagePrinter(hprinter)
            win32print.EndDocPrinter(hprinter)
        finally:
            win32print.ClosePrinter(hprinter)

        logger.info(f"✅ Cupom impresso: Venda #{venda_id} - R$ {total:.2f}")
        return {"success": True, "message": "Cupom impresso com sucesso!"}

    except Exception as e:
        logger.error(f"❌ Erro ao imprimir cupom: {e}")
        return {"success": False, "error": str(e)}

# ============================================================
# ROTAS
# ============================================================

@app.route('/api/imprimir/cupom', methods=['POST'])
def imprimir_cupom_route():
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401
        
        dados = request.json or {}
        
        with get_db('data/usuarios.db') as conn:
            cursor = conn.execute("SELECT nome_loja, cnpj FROM users WHERE db_id=? LIMIT 1", (db_id,))
            loja = cursor.fetchone()
            if loja:
                dados['nome_loja'] = loja[0]
                dados['cnpj'] = loja[1] or ''
        
        dados['usuario'] = session.get('nome', '')
        
        resultado = imprimir_cupom(dados)
        return jsonify(resultado)
        
    except Exception as e:
        logger.error(f"❌ Erro na rota de impressão: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/produto/buscar/<codigo_barras>', methods=['GET'])
def buscar_produto_barras_route(codigo_barras):
    try:
        resultado = buscar_produto_por_codigo_barras(codigo_barras)
        return jsonify(resultado)
    except Exception as e:
        logger.error(f"❌ Erro ao buscar produto por código: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"❌ Erro ao carregar template: {e}")
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>PDV Inteligente - Erro</title>
            <style>
                body { font-family: Arial, sans-serif; background: #0f0f1a; color: #fff; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; }
                .container { background: #16162e; border-radius: 12px; padding: 40px; max-width: 500px; text-align: center; border: 1px solid #2a2a4a; }
                h1 { color: #ef4444; }
                p { color: #a0a0c0; }
                button { background: #22c55e; color: #fff; border: none; padding: 12px 24px; border-radius: 8px; font-size: 16px; cursor: pointer; margin-top: 16px; }
                button:hover { background: #16a34a; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>❌ Erro ao carregar o PDV</h1>
                <p>O arquivo index.html não foi encontrado na pasta templates.</p>
                <p style="font-size: 13px; color: #6a6a8a;">Verifique sua conexão com a internet e tente novamente.</p>
                <button onclick="location.reload()">🔄 Tentar novamente</button>
            </div>
        </body>
        </html>
        """

# ============================================================
# INICIALIZAR BANCO DE DADOS (COM VERIFICAÇÃO DE TODAS AS COLUNAS)
# ============================================================

def init_db():
    os.makedirs("data", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    os.makedirs("Cupons", exist_ok=True)

    # ===== TABELA USERS (CORRIGIDA PARA TERMUX) =====
    with get_db('data/usuarios.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                nome TEXT,
                email TEXT UNIQUE,
                senha TEXT,
                cargo TEXT,
                db_id TEXT,
                servidor_id TEXT,
                nome_loja TEXT DEFAULT '',
                cnpj TEXT UNIQUE DEFAULT '',
                cnpj_dados TEXT DEFAULT '{}',
                session_id TEXT DEFAULT '',
                ultimo_acesso TIMESTAMP,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor = conn.execute("PRAGMA table_info(users)")
        colunas = [row[1] for row in cursor.fetchall()]
        
        # Adicionar ultimo_acesso SEM DEFAULT (evita erro)
        if 'ultimo_acesso' not in colunas:
            try:
                conn.execute("ALTER TABLE users ADD COLUMN ultimo_acesso TIMESTAMP")
                logger.info("✅ Coluna 'ultimo_acesso' adicionada")
                conn.execute("UPDATE users SET ultimo_acesso = CURRENT_TIMESTAMP WHERE ultimo_acesso IS NULL")
                logger.info("✅ Registros atualizados")
            except Exception as e:
                logger.warning(f"⚠️ Erro: {e}")
        
        # Adicionar outras colunas
        for coluna, tipo in [
            ('nome_loja', 'TEXT DEFAULT ""'),
            ('cnpj', 'TEXT DEFAULT ""'),
            ('cnpj_dados', 'TEXT DEFAULT "{}"'),
            ('session_id', 'TEXT DEFAULT ""'),
            ('criado_em', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        ]:
            if coluna not in colunas:
                try:
                    conn.execute(f"ALTER TABLE users ADD COLUMN {coluna} {tipo}")
                    logger.info(f"✅ Coluna '{coluna}' adicionada")
                except Exception as e:
                    logger.warning(f"⚠️ Erro em '{coluna}': {e}")

    # ===== TABELA PRODUTOS =====
    with get_db('data/produtos.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS produtos (
                codigo TEXT PRIMARY KEY,
                nome TEXT,
                preco REAL,
                estoque INTEGER DEFAULT 0,
                categoria TEXT DEFAULT "Geral",
                db_id TEXT
            )
        ''')
        cursor = conn.execute("PRAGMA table_info(produtos)")
        colunas = [row[1] for row in cursor.fetchall()]
        for coluna, tipo in [('estoque', 'INTEGER DEFAULT 0'), ('categoria', 'TEXT DEFAULT "Geral"'), ('db_id', 'TEXT')]:
            if coluna not in colunas:
                try:
                    conn.execute(f"ALTER TABLE produtos ADD COLUMN {coluna} {tipo}")
                    logger.info(f"✅ Coluna '{coluna}' adicionada em produtos")
                except: pass
        try:
            conn.execute("CREATE INDEX IF NOT EXISTS idx_produtos_nome ON produtos(nome)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_produtos_db_id ON produtos(db_id)")
        except: pass

    # ===== TABELA CLIENTES =====
    with get_db('data/clientes.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                telefone TEXT,
                email TEXT,
                divida REAL DEFAULT 0,
                db_id TEXT
            )
        ''')
        cursor = conn.execute("PRAGMA table_info(clientes)")
        colunas = [row[1] for row in cursor.fetchall()]
        for coluna, tipo in [('telefone', 'TEXT'), ('email', 'TEXT'), ('divida', 'REAL DEFAULT 0'), ('db_id', 'TEXT')]:
            if coluna not in colunas:
                try:
                    conn.execute(f"ALTER TABLE clientes ADD COLUMN {coluna} {tipo}")
                    logger.info(f"✅ Coluna '{coluna}' adicionada em clientes")
                except: pass
        try:
            conn.execute("CREATE INDEX IF NOT EXISTS idx_clientes_nome ON clientes(nome)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_clientes_db_id ON clientes(db_id)")
        except: pass

    # ===== TABELA VENDAS =====
    with get_db('data/vendas.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS vendas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_hora TEXT,
                subtotal REAL,
                desconto REAL,
                total REAL,
                metodo TEXT,
                itens TEXT,
                cliente TEXT,
                usuario_id TEXT,
                db_id TEXT
            )
        ''')
        cursor = conn.execute("PRAGMA table_info(vendas)")
        colunas = [row[1] for row in cursor.fetchall()]
        for coluna, tipo in [
            ('desconto', 'REAL DEFAULT 0'),
            ('metodo', 'TEXT DEFAULT "Dinheiro"'),
            ('itens', 'TEXT'),
            ('cliente', 'TEXT DEFAULT ""'),
            ('usuario_id', 'TEXT DEFAULT ""'),
            ('db_id', 'TEXT')
        ]:
            if coluna not in colunas:
                try:
                    conn.execute(f"ALTER TABLE vendas ADD COLUMN {coluna} {tipo}")
                    logger.info(f"✅ Coluna '{coluna}' adicionada em vendas")
                except: pass
        try:
            conn.execute("CREATE INDEX IF NOT EXISTS idx_vendas_db_id ON vendas(db_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_vendas_data ON vendas(data_hora)")
        except: pass

    # ===== TABELA CAIXA =====
    with get_db('data/caixa.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS caixa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id TEXT,
                valor_abertura REAL,
                data_abertura TEXT,
                data_fechamento TEXT,
                total REAL DEFAULT 0,
                status TEXT DEFAULT 'fechado',
                db_id TEXT
            )
        ''')
        cursor = conn.execute("PRAGMA table_info(caixa)")
        colunas = [row[1] for row in cursor.fetchall()]
        for coluna, tipo in [
            ('data_fechamento', 'TEXT'),
            ('total', 'REAL DEFAULT 0'),
            ('status', 'TEXT DEFAULT "fechado"'),
            ('db_id', 'TEXT')
        ]:
            if coluna not in colunas:
                try:
                    conn.execute(f"ALTER TABLE caixa ADD COLUMN {coluna} {tipo}")
                    logger.info(f"✅ Coluna '{coluna}' adicionada em caixa")
                except: pass
        try:
            conn.execute("CREATE INDEX IF NOT EXISTS idx_caixa_db_id ON caixa(db_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_caixa_status ON caixa(status)")
        except: pass

    # ===== TABELA PAGAMENTOS =====
    with get_db('data/pagamentos.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS pagamentos (
                id TEXT PRIMARY KEY,
                db_id TEXT,
                plano_id INTEGER,
                valor REAL,
                status TEXT DEFAULT 'pendente',
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                pago_em TIMESTAMP
            )
        ''')
        cursor = conn.execute("PRAGMA table_info(pagamentos)")
        colunas = [row[1] for row in cursor.fetchall()]
        for coluna, tipo in [
            ('plano_id', 'INTEGER'),
            ('valor', 'REAL'),
            ('status', 'TEXT DEFAULT "pendente"'),
            ('criado_em', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
            ('pago_em', 'TIMESTAMP')
        ]:
            if coluna not in colunas:
                try:
                    conn.execute(f"ALTER TABLE pagamentos ADD COLUMN {coluna} {tipo}")
                    logger.info(f"✅ Coluna '{coluna}' adicionada em pagamentos")
                except: pass
        try:
            conn.execute("CREATE INDEX IF NOT EXISTS idx_pagamentos_db_id ON pagamentos(db_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_pagamentos_status ON pagamentos(status)")
        except: pass

    # ===== TABELA CONFIG =====
    with get_db('data/config.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS config (
                chave TEXT PRIMARY KEY,
                valor TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor = conn.execute("PRAGMA table_info(config)")
        colunas = [row[1] for row in cursor.fetchall()]
        if 'criado_em' not in colunas:
            try:
                conn.execute("ALTER TABLE config ADD COLUMN criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                logger.info("✅ Coluna 'criado_em' adicionada em config")
            except: pass

    
        # Criar índice para CNPJ (otimiza buscas)
        try:
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_cnpj ON users(cnpj)")
            logger.info("✅ Índice idx_users_cnpj criado")
        except:
            pass

    logger.info("✅ Bancos de dados inicializados e todas as colunas verificadas")

# ============================================================
# ROTAS DE AUTENTICAÇÃO
# ============================================================



# ============================================================
# ROTA PARA VALIDAR CNPJ (VERIFICA SE JÁ EXISTE)
# ============================================================

@app.route('/api/validar/cnpj/<cnpj>', methods=['GET'])
def validar_cnpj_route(cnpj):
    try:
        cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
        if len(cnpj_limpo) != 14:
            return jsonify({"success": False, "error": "CNPJ inválido"})
        
        # Verificar no banco local
        with get_db('data/usuarios.db') as conn:
            cursor = conn.execute("SELECT email FROM users WHERE cnpj=?", (cnpj_limpo,))
            result = cursor.fetchone()
            if result:
                return jsonify({
                    "success": True,
                    "existe": True,
                    "email": result[0],
                    "fonte": "local"
                })
        
        # Verificar no Firebase
        if validar_cnpj_firebase(cnpj_limpo):
            return jsonify({
                "success": True,
                "existe": True,
                "fonte": "firebase"
            })
        
        return jsonify({"success": True, "existe": False})
    except Exception as e:
        logger.error(f"❌ Erro ao validar CNPJ: {e}")
        return jsonify({"success": False, "error": str(e)})


@app.route(\'/api/auth/register\', methods=['POST'])
@rate_limit(max_requests=5, window=300)
def register():
    try:
        data = request.json or {}
        nome = (data.get('nome') or '').strip()
        email = (data.get('email') or '').strip().lower()
        senha = data.get('senha') or ''
        nome_loja = (data.get('nome_loja') or 'Minha Loja').strip()
        cnpj = ''.join(filter(str.isdigit, data.get('cnpj') or ''))
        cnpj_dados = data.get('cnpj_dados') or {}
        db_id = (data.get('db_id') or '').strip()

        if not nome or not email or not senha:
            return jsonify({"success": False, "error": "Preencha todos os campos obrigatórios"})

        if len(senha) < 4:
            return jsonify({"success": False, "error": "A senha deve ter pelo menos 4 caracteres"})

        if not db_id:
            db_id = str(uuid.uuid4())[:8]

        usuario_firebase = carregar_usuario_firebase(db_id)
        if usuario_firebase and usuario_firebase.get('email') != email:
            return jsonify({"success": False, "error": "Este ID de loja pertence a outro usuário"})

        
        # ===== VERIFICAR SE CNPJ JÁ EXISTE =====
        if cnpj:
            # Verificar no banco local
            with get_db('data/usuarios.db') as conn:
                cursor = conn.execute("SELECT email FROM users WHERE cnpj=?", (cnpj,))
                result = cursor.fetchone()
                if result:
                    return jsonify({
                        "success": False, 
                        "error": f"Este CNPJ já está cadastrado no email: {result[0]}. Faça login com essa conta."
                    })
            
            # Verificar no Firebase
            if validar_cnpj_firebase(cnpj):
                return jsonify({
                    "success": False,
                    "error": "Este CNPJ já está cadastrado. Faça login com sua conta existente."
                })
        

        user_id = str(uuid.uuid4())[:8]
        with get_db('data/usuarios.db') as conn:
            cursor = conn.execute("SELECT id FROM users WHERE email=?", (email,))
            if cursor.fetchone():
                return jsonify({"success": False, "error": "Email já cadastrado"})

            conn.execute("""
                INSERT INTO users (id, nome, email, senha, cargo, db_id, servidor_id, nome_loja, cnpj, cnpj_dados)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, nome, email, hash_senha(senha), "Gerente", db_id, SERVIDOR_ID, nome_loja, cnpj, json.dumps(cnpj_dados)))

        usuario_firebase = carregar_usuario_firebase(db_id)
        if not usuario_firebase:
            criar_usuario_firebase(db_id, nome, email, SERVIDOR_ID, nome_loja, cnpj, cnpj_dados)
        else:
            usuario_firebase['nome'] = nome
            usuario_firebase['email'] = email
            usuario_firebase['servidor_id'] = SERVIDOR_ID
            usuario_firebase['nome_loja'] = nome_loja
            usuario_firebase['cnpj'] = cnpj
            usuario_firebase['cnpj_dados'] = cnpj_dados
            salvar_usuario_firebase(db_id, usuario_firebase)

        logger.info(f"✅ Novo usuário registrado: {email} (db_id: {db_id})")
        return jsonify({"success": True, "message": "Conta criada com sucesso!", "db_id": db_id})
    except Exception as e:
        logger.error(f"❌ Erro no registro: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/auth/login', methods=['POST'])
@rate_limit(max_requests=5, window=60)
def login():
    try:
        data = request.json or {}
        email = (data.get('email') or '').strip().lower()
        senha = data.get('senha') or ''
        db_id = (data.get('db_id') or '').strip()

        if not email or not senha:
            return jsonify({"success": False, "error": "Preencha email e senha"})

        with get_db('data/usuarios.db') as conn:
            if db_id:
                cursor = conn.execute("""
                    SELECT id, nome, cargo, db_id, servidor_id, nome_loja, cnpj, cnpj_dados, session_id
                    FROM users
                    WHERE email=? AND senha=? AND db_id=? AND servidor_id=?
                """, (email, hash_senha(senha), db_id, SERVIDOR_ID))
            else:
                cursor = conn.execute("""
                    SELECT id, nome, cargo, db_id, servidor_id, nome_loja, cnpj, cnpj_dados, session_id
                    FROM users
                    WHERE email=? AND senha=? AND servidor_id=?
                """, (email, hash_senha(senha), SERVIDOR_ID))
            user = cursor.fetchone()

        if user:
            user_db_id = user[3]
            
            session_id_atual = user[8] if len(user) > 8 else ''
            if session_id_atual:
                if session_id_atual in SESSOES_ATIVAS:
                    return jsonify({
                        "success": False,
                        "error": "Esta conta já está logada em outro dispositivo. Faça logout no outro dispositivo primeiro."
                    })
            
            nova_session_id = secrets.token_hex(32)
            session.permanent = True
            session['usuario_id'] = user[0]
            session['nome'] = user[1]
            session['cargo'] = user[2]
            session['db_id'] = user_db_id
            session['servidor_id'] = user[4]
            session['nome_loja'] = user[5] or 'Minha Loja'
            session['cnpj'] = user[6] or ''
            session['cnpj_dados'] = json.loads(user[7]) if user[7] else {}
            session['session_id'] = nova_session_id
            
            with get_db('data/usuarios.db') as conn:
                conn.execute("""
                    UPDATE users SET session_id=?, ultimo_acesso=?
                    WHERE id=?
                """, (nova_session_id, datetime.now().isoformat(), user[0]))
            
            SESSOES_ATIVAS[user_db_id] = nova_session_id
            
            logger.info(f"✅ Login bem-sucedido: {email} (db_id: {user_db_id})")
            
            return jsonify({
                "success": True,
                "nome": user[1],
                "cargo": user[2],
                "db_id": user_db_id,
                "servidor_id": user[4],
                "nome_loja": user[5] or 'Minha Loja',
                "cnpj": user[6] or '',
                "cnpj_dados": json.loads(user[7]) if user[7] else {},
                "plano_ativo": is_plano_ativo(user_db_id),
                "dias_restantes": get_dias_restantes(user_db_id)
            })

        return jsonify({"success": False, "error": "Email ou senha inválidos"})
    except Exception as e:
        logger.error(f"❌ Erro no login: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/auth/status')
def auth_status():
    if 'usuario_id' in session:
        db_id = session.get('db_id')
        return jsonify({
            "logged_in": True,
            "nome": session.get('nome'),
            "cargo": session.get('cargo'),
            "db_id": db_id,
            "servidor_id": session.get('servidor_id'),
            "nome_loja": session.get('nome_loja', 'Minha Loja'),
            "cnpj": session.get('cnpj', ''),
            "cnpj_dados": session.get('cnpj_dados', {}),
            "plano_ativo": is_plano_ativo(db_id),
            "dias_restantes": get_dias_restantes(db_id)
        })
    return jsonify({"logged_in": False})

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    try:
        db_id = session.get('db_id')
        if db_id and db_id in SESSOES_ATIVAS:
            del SESSOES_ATIVAS[db_id]
        
        usuario_id = session.get('usuario_id')
        if usuario_id:
            with get_db('data/usuarios.db') as conn:
                conn.execute("UPDATE users SET session_id='' WHERE id=?", (usuario_id,))
        
        session.clear()
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"❌ Erro no logout: {e}")
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# ROTAS DE PRODUTOS
# ============================================================

@app.route('/api/produtos')
def get_produtos():
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        if not is_plano_ativo(db_id):
            return plano_bloqueado_response()

        busca = request.args.get('busca', '').strip().lower()
        with get_db('data/produtos.db') as conn:
            if busca:
                termo = f'%{busca}%'
                cursor = conn.execute("""
                    SELECT codigo, nome, preco, estoque, categoria
                    FROM produtos
                    WHERE db_id=? AND (LOWER(nome) LIKE ? OR LOWER(codigo) LIKE ?)
                    ORDER BY nome
                """, (db_id, termo, termo))
            else:
                cursor = conn.execute("""
                    SELECT codigo, nome, preco, estoque, categoria
                    FROM produtos
                    WHERE db_id=?
                    ORDER BY nome
                """, (db_id,))
            produtos = [dict(row) for row in cursor.fetchall()]

        return jsonify({"success": True, "produtos": produtos})
    except Exception as e:
        logger.error(f"❌ Erro ao buscar produtos: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/produtos', methods=['POST'])
def save_produto():
    try:
        data = request.json or {}
        db_id = get_db_id()

        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        if not is_plano_ativo(db_id):
            return plano_bloqueado_response()

        if not data.get('codigo') or not data.get('nome'):
            return jsonify({"success": False, "error": "Código e nome são obrigatórios"})

        with get_db('data/produtos.db') as conn:
            conn.execute("""
                INSERT INTO produtos (codigo, nome, preco, estoque, categoria, db_id)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(codigo) DO UPDATE SET
                nome=excluded.nome, preco=excluded.preco, estoque=excluded.estoque,
                categoria=excluded.categoria
            """, (data['codigo'], data['nome'], data.get('preco', 0), data.get('estoque', 0), data.get('categoria', 'Geral'), db_id))

        return jsonify({"success": True, "message": "Produto salvo"})
    except Exception as e:
        logger.error(f"❌ Erro ao salvar produto: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/produtos/<codigo>', methods=['DELETE'])
def delete_produto(codigo):
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        if not is_plano_ativo(db_id):
            return plano_bloqueado_response()

        with get_db('data/produtos.db') as conn:
            conn.execute("DELETE FROM produtos WHERE codigo=? AND db_id=?", (codigo, db_id))
        return jsonify({"success": True, "message": "Produto excluído"})
    except Exception as e:
        logger.error(f"❌ Erro ao excluir produto: {e}")
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# ROTAS DE CLIENTES
# ============================================================

@app.route('/api/clientes')
def get_clientes():
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        if not is_plano_ativo(db_id):
            return plano_bloqueado_response()

        busca = request.args.get('busca', '').strip().lower()
        with get_db('data/clientes.db') as conn:
            if busca:
                termo = f'%{busca}%'
                cursor = conn.execute("""
                    SELECT id, nome, telefone, email, divida
                    FROM clientes
                    WHERE db_id=? AND LOWER(nome) LIKE ?
                    ORDER BY nome
                """, (db_id, termo))
            else:
                cursor = conn.execute("""
                    SELECT id, nome, telefone, email, divida
                    FROM clientes
                    WHERE db_id=?
                    ORDER BY nome
                """, (db_id,))
            clientes = [dict(row) for row in cursor.fetchall()]

        return jsonify({"success": True, "clientes": clientes})
    except Exception as e:
        logger.error(f"❌ Erro ao buscar clientes: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/clientes', methods=['POST'])
def save_cliente():
    try:
        data = request.json or {}
        db_id = get_db_id()

        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        if not is_plano_ativo(db_id):
            return plano_bloqueado_response()

        if not data.get('nome'):
            return jsonify({"success": False, "error": "Nome é obrigatório"})

        with get_db('data/clientes.db') as conn:
            if data.get('id'):
                conn.execute("""
                    UPDATE clientes SET nome=?, telefone=?, email=?, divida=?
                    WHERE id=? AND db_id=?
                """, (data['nome'], data.get('telefone', ''), data.get('email', ''), data.get('divida', 0), data['id'], db_id))
            else:
                conn.execute("""
                    INSERT INTO clientes (nome, telefone, email, divida, db_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (data['nome'], data.get('telefone', ''), data.get('email', ''), data.get('divida', 0), db_id))

        return jsonify({"success": True, "message": "Cliente salvo"})
    except Exception as e:
        logger.error(f"❌ Erro ao salvar cliente: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/clientes/<int:cliente_id>/pagar', methods=['POST'])
def pagar_cliente(cliente_id):
    try:
        data = request.json or {}
        db_id = get_db_id()
        valor = data.get('valor', 0)

        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        if not is_plano_ativo(db_id):
            return plano_bloqueado_response()

        with get_db('data/clientes.db') as conn:
            conn.execute("UPDATE clientes SET divida = MAX(0, divida - ?) WHERE id=? AND db_id=?",
                        (valor, cliente_id, db_id))

        return jsonify({"success": True, "message": "Pagamento registrado"})
    except Exception as e:
        logger.error(f"❌ Erro ao pagar cliente: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/clientes/<int:cliente_id>', methods=['DELETE'])
def delete_cliente(cliente_id):
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        if not is_plano_ativo(db_id):
            return plano_bloqueado_response()

        with get_db('data/clientes.db') as conn:
            conn.execute("DELETE FROM clientes WHERE id=? AND db_id=?", (cliente_id, db_id))
        return jsonify({"success": True, "message": "Cliente excluído"})
    except Exception as e:
        logger.error(f"❌ Erro ao excluir cliente: {e}")
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# ROTAS DE VENDAS
# ============================================================

@app.route('/api/vendas', methods=['POST'])
def registrar_venda():
    try:
        data = request.json or {}
        db_id = get_db_id()
        usuario_id = get_usuario_id()
        data_hora = datetime.now().isoformat()

        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        if not is_plano_ativo(db_id):
            return plano_bloqueado_response()

        itens = data.get('itens', [])
        if not itens:
            return jsonify({"success": False, "error": "Nenhum item na venda"})

        with get_db('data/produtos.db') as conn:
            conn.execute("BEGIN TRANSACTION")
            try:
                for item in itens:
                    codigo = item.get('codigo')
                    if codigo and codigo != 'AVULSO':
                        cursor = conn.execute(
                            "SELECT estoque, nome FROM produtos WHERE codigo=? AND db_id=?",
                            (codigo, db_id)
                        )
                        produto = cursor.fetchone()
                        if not produto:
                            conn.execute("ROLLBACK")
                            return jsonify({
                                "success": False,
                                "error": f"Produto '{item.get('nome', codigo)}' não encontrado"
                            })
                        qtd = item.get('quantidade', 1)
                        if produto[0] < qtd:
                            conn.execute("ROLLBACK")
                            return jsonify({
                                "success": False,
                                "error": f"Estoque insuficiente para '{produto[1]}': disponível {produto[0]}, necessário {qtd}"
                            })
                
                for item in itens:
                    codigo = item.get('codigo')
                    if codigo and codigo != 'AVULSO':
                        qtd = item.get('quantidade', 1)
                        conn.execute(
                            "UPDATE produtos SET estoque = estoque - ? WHERE codigo=? AND db_id=?",
                            (qtd, codigo, db_id)
                        )
                
                conn.execute("COMMIT")
            except Exception as e:
                conn.execute("ROLLBACK")
                raise e

        itens_salvar = []
        for item in itens:
            preco_unit = item.get('preco_unitario', item.get('preco', 0))
            qtd = item.get('quantidade', 1)
            itens_salvar.append({
                'codigo': item.get('codigo', 'AVULSO'),
                'nome': item.get('nome', 'Item'),
                'quantidade': qtd,
                'preco_unitario': preco_unit,
                'total': item.get('total', preco_unit * qtd)
            })

        venda_id = None
        with get_db('data/vendas.db') as conn:
            cursor = conn.execute("""
                INSERT INTO vendas (data_hora, subtotal, desconto, total, metodo, itens, cliente, usuario_id, db_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data_hora,
                data.get('subtotal', 0),
                data.get('desconto', 0),
                data.get('total', 0),
                data.get('metodo', 'Dinheiro'),
                json.dumps(itens_salvar, ensure_ascii=False),
                data.get('cliente', ''),
                usuario_id,
                db_id
            ))
            venda_id = cursor.lastrowid

        if data.get('metodo') == 'Fiado' and data.get('cliente'):
            try:
                with get_db('data/clientes.db') as conn:
                    cursor = conn.execute("SELECT id FROM clientes WHERE nome=? AND db_id=?",
                                         (data.get('cliente'), db_id))
                    cliente = cursor.fetchone()
                    if cliente:
                        conn.execute("UPDATE clientes SET divida = divida + ? WHERE id=? AND db_id=?",
                                    (data.get('total', 0), cliente[0], db_id))
                    else:
                        conn.execute("INSERT INTO clientes (nome, divida, db_id) VALUES (?, ?, ?)",
                                    (data.get('cliente'), data.get('total', 0), db_id))
            except Exception as e:
                logger.error(f"⚠️ Erro ao atualizar fiado: {e}")

        with get_db('data/usuarios.db') as conn:
            cursor = conn.execute("SELECT nome_loja, cnpj, cnpj_dados FROM users WHERE db_id=? LIMIT 1", (db_id,))
            loja = cursor.fetchone()

        dados_impressao = {
            'venda_id': venda_id,
            'data_hora': data_hora,
            'itens': itens_salvar,
            'subtotal': data.get('subtotal', 0),
            'desconto': data.get('desconto', 0),
            'total': data.get('total', 0),
            'metodo': data.get('metodo', 'Dinheiro'),
            'cliente': data.get('cliente', ''),
            'usuario': session.get('nome', ''),
            'nome_loja': loja[0] if loja else session.get('nome_loja', 'Minha Loja'),
            'cnpj': loja[1] if loja else session.get('cnpj', '')
        }

        if IS_WINDOWS and IMPRESSAO_DISPONIVEL:
            try:
                threading.Thread(target=imprimir_cupom, args=(dados_impressao,), daemon=True).start()
            except Exception as e:
                logger.error(f"⚠️ Erro ao iniciar impressão: {e}")
        else:
            logger.info(f"📄 Cupom gerado (impressão simulada): Venda #{venda_id}")

        return jsonify({
            "success": True,
            "id": venda_id,
            "data_hora": data_hora,
            "itens": itens_salvar,
            "dados_impressao": dados_impressao,
            "loja": {
                "nome_loja": loja[0] if loja else session.get('nome_loja', 'Minha Loja'),
                "cnpj": loja[1] if loja else session.get('cnpj', ''),
                "cnpj_dados": json.loads(loja[2]) if loja and loja[2] else session.get('cnpj_dados', {})
            }
        })
    except Exception as e:
        logger.error(f"❌ Erro na venda: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/vendas')
def get_vendas():
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        if not is_plano_ativo(db_id):
            return plano_bloqueado_response()

        limite = request.args.get('limite', 100, type=int)

        with get_db('data/vendas.db') as conn:
            cursor = conn.execute("""
                SELECT id, data_hora, subtotal, desconto, total, metodo, itens, cliente, usuario_id
                FROM vendas WHERE db_id=? ORDER BY id DESC LIMIT ?
            """, (db_id, limite))
            vendas = []
            for row in cursor.fetchall():
                try:
                    itens = json.loads(row[6]) if row[6] else []
                except:
                    itens = []
                vendas.append({
                    "id": row[0],
                    "data_hora": row[1],
                    "subtotal": row[2],
                    "desconto": row[3],
                    "total": row[4],
                    "metodo": row[5],
                    "itens": itens,
                    "cliente": row[7] or '',
                    "usuario_id": row[8] or ''
                })

        return jsonify({"success": True, "vendas": vendas})
    except Exception as e:
        logger.error(f"❌ Erro ao buscar vendas: {e}")
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# ROTAS DE CAIXA
# ============================================================

@app.route('/api/caixa/status')
def caixa_status():
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"aberto": False})

        with get_db('data/caixa.db') as conn:
            cursor = conn.execute("""
                SELECT id, usuario_id, valor_abertura, data_abertura, total
                FROM caixa WHERE db_id=? AND status='aberto'
                ORDER BY id DESC LIMIT 1
            """, (db_id,))
            result = cursor.fetchone()

        if result:
            return jsonify({
                "aberto": True,
                "id": result[0],
                "usuario_id": result[1],
                "valor_abertura": result[2],
                "data_abertura": result[3],
                "total": result[4] or 0
            })
        return jsonify({"aberto": False})
    except Exception as e:
        logger.error(f"❌ Erro ao verificar caixa: {e}")
        return jsonify({"aberto": False, "error": str(e)})

@app.route('/api/caixa/abrir', methods=['POST'])
def caixa_abrir():
    try:
        data = request.json or {}
        db_id = get_db_id()
        usuario_id = get_usuario_id()

        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        if not is_plano_ativo(db_id):
            return plano_bloqueado_response()

        with get_db('data/caixa.db') as conn:
            cursor = conn.execute("SELECT id FROM caixa WHERE db_id=? AND status='aberto'", (db_id,))
            if cursor.fetchone():
                return jsonify({"success": False, "error": "Caixa já está aberto"})

            conn.execute("""
                INSERT INTO caixa (usuario_id, valor_abertura, data_abertura, status, db_id)
                VALUES (?, ?, ?, 'aberto', ?)
            """, (usuario_id, data.get('valor', 0), datetime.now().isoformat(), db_id))

        return jsonify({"success": True, "message": "Caixa aberto"})
    except Exception as e:
        logger.error(f"❌ Erro ao abrir caixa: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/caixa/fechar', methods=['POST'])
def caixa_fechar():
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        if not is_plano_ativo(db_id):
            return plano_bloqueado_response()

        hoje = datetime.now().strftime('%Y-%m-%d')

        with get_db('data/vendas.db') as conn:
            cursor = conn.execute("SELECT SUM(total) FROM vendas WHERE db_id=? AND data_hora LIKE ?",
                                 (db_id, f'{hoje}%'))
            total = cursor.fetchone()[0] or 0

        with get_db('data/caixa.db') as conn:
            conn.execute("""
                UPDATE caixa SET status='fechado', data_fechamento=?, total=?
                WHERE db_id=? AND status='aberto'
            """, (datetime.now().isoformat(), total, db_id))

        return jsonify({"success": True, "total": total})
    except Exception as e:
        logger.error(f"❌ Erro ao fechar caixa: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/caixa/resumo')
def caixa_resumo():
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        data = request.args.get('data', datetime.now().strftime('%Y-%m-%d'))

        with get_db('data/vendas.db') as conn:
            cursor = conn.execute("""
                SELECT metodo, COUNT(*), SUM(total)
                FROM vendas WHERE db_id=? AND data_hora LIKE ?
                GROUP BY metodo
            """, (db_id, f'{data}%'))
            metodos = []
            for row in cursor.fetchall():
                metodos.append({
                    "metodo": row[0],
                    "quantidade": row[1],
                    "total": row[2] or 0
                })

            cursor = conn.execute("""
                SELECT SUM(total), COUNT(*)
                FROM vendas WHERE db_id=? AND data_hora LIKE ?
            """, (db_id, f'{data}%'))
            totals = cursor.fetchone()

        return jsonify({
            "success": True,
            "data": data,
            "total_geral": totals[0] or 0,
            "total_vendas": totals[1] or 0,
            "metodos": metodos
        })
    except Exception as e:
        logger.error(f"❌ Erro ao buscar resumo: {e}")
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# ROTAS DE ESTATÍSTICAS
# ============================================================

@app.route('/api/estatisticas')
def get_estatisticas():
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        if not is_plano_ativo(db_id):
            return plano_bloqueado_response()

        periodo = request.args.get('periodo', 'hoje')
        hoje = datetime.now()
        filtro = None
        filtro_data = None

        if periodo == "hoje":
            filtro = hoje.strftime('%Y-%m-%d') + '%'
        elif periodo == "semana":
            filtro_data = (hoje - timedelta(days=7)).strftime('%Y-%m-%d')
        elif periodo == "mes":
            filtro_data = (hoje - timedelta(days=30)).strftime('%Y-%m-%d')
        else:
            filtro = hoje.strftime('%Y-%m-%d') + '%'

        with get_db('data/vendas.db') as conn:
            if filtro:
                cursor = conn.execute("""
                    SELECT id, data_hora, subtotal, desconto, total, metodo, itens, cliente
                    FROM vendas WHERE db_id=? AND data_hora LIKE ? ORDER BY id DESC LIMIT 50
                """, (db_id, filtro))
            else:
                cursor = conn.execute("""
                    SELECT id, data_hora, subtotal, desconto, total, metodo, itens, cliente
                    FROM vendas WHERE db_id=? AND data_hora >= ? ORDER BY id DESC LIMIT 50
                """, (db_id, filtro_data))

            total_geral = 0
            total_vendas = 0
            total_itens = 0
            metodos = {"Dinheiro": 0, "PIX": 0, "Cartão": 0, "Fiado": 0}
            vendas = []

            for row in cursor.fetchall():
                total_geral += row[4] or 0
                total_vendas += 1
                if row[5] in metodos:
                    metodos[row[5]] += row[4] or 0

                try:
                    itens = json.loads(row[6]) if row[6] else []
                except:
                    itens = []
                total_itens += sum(i.get('quantidade', 1) for i in itens)

                nomes_produtos = ", ".join(
                    f"{i.get('quantidade', 1)}x {i.get('nome', 'Item')}" for i in itens
                ) if itens else "—"

                vendas.append({
                    "id": row[0],
                    "data_hora": row[1],
                    "subtotal": row[2],
                    "desconto": row[3],
                    "total": row[4],
                    "metodo": row[5],
                    "itens": itens,
                    "produtos_resumo": nomes_produtos,
                    "cliente": row[7] or ''
                })

        return jsonify({
            "success": True,
            "stats": {
                "total_geral": total_geral,
                "total_vendas": total_vendas,
                "media": total_geral / total_vendas if total_vendas > 0 else 0,
                "total_itens": total_itens,
                "metodos": metodos,
                "vendas": vendas
            }
        })
    except Exception as e:
        logger.error(f"❌ Erro ao buscar estatísticas: {e}")
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# ROTAS DE PLANOS E PIX
# ============================================================

@app.route('/api/planos')
def get_planos():
    return jsonify({"success": True, "planos": PLANOS})

@app.route('/api/plano/status')
def get_plano_status():
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        dados = carregar_usuario_firebase(db_id)
        if not dados:
            return jsonify({"success": False, "error": "Dados não encontrados"})

        plano_id = dados.get('plano', 1)
        plano = next((p for p in PLANOS if p['id'] == plano_id), None)
        expira = dados.get('expira_em')
        expira_date = datetime.fromisoformat(expira) if expira else None
        dias_restantes = (expira_date - datetime.now()).total_seconds() / 86400 if expira_date else 0

        return jsonify({
            "success": True,
            "plano": plano,
            "expira_em": expira,
            "dias_restantes": max(0, dias_restantes),
            "expirado": bool(expira_date and expira_date < datetime.now())
        })
    except Exception as e:
        logger.error(f"❌ Erro ao buscar status do plano: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/pix/criar', methods=['POST'])
def criar_pix():
    try:
        data = request.json or {}
        plano_id = data.get('plano_id')
        db_id = get_db_id()

        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        cnpj_dados_sessao = session.get('cnpj_dados', {}) or {}
        email = data.get('email') or cnpj_dados_sessao.get('email') or 'cliente@pdv.com'

        plano = next((p for p in PLANOS if p['id'] == plano_id), None)
        if not plano:
            return jsonify({"success": False, "error": "Plano inválido"})

        url = "https://api.mercadopago.com/v1/payments"
        headers = {
            "Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}",
            "Content-Type": "application/json",
            "X-Idempotency-Key": str(uuid.uuid4())
        }
        payment_data = {
            "transaction_amount": float(plano['preco']),
            "description": f"PDV Inteligente - {plano['nome']}",
            "payment_method_id": "pix",
            "payer": {
                "email": email,
                "first_name": "Cliente",
                "last_name": "PDV",
                "identification": {
                    "type": "CPF",
                    "number": "00000000000"
                }
            }
        }

        res = requests.post(url, json=payment_data, headers=headers, timeout=30)
        res_data = res.json()

        if res.status_code == 201 and res_data.get('id'):
            pix_id = str(res_data['id'])
            qr_code = res_data['point_of_interaction']['transaction_data']['qr_code']
            qr_code_base64 = res_data['point_of_interaction']['transaction_data']['qr_code_base64']

            if plano_id == 5:
                expira_em = (datetime.now() + timedelta(minutes=3)).isoformat()
            else:
                expira_em = (datetime.now() + timedelta(days=plano['dias'])).isoformat()

            pagamentos_pendentes[pix_id] = {
                'db_id': db_id,
                'plano_id': plano_id,
                'valor': plano['preco'],
                'pago': False,
                'criado_em': datetime.now().isoformat(),
                'expira_em': expira_em
            }

            return jsonify({
                "success": True,
                "pix_id": pix_id,
                "qr_code": qr_code,
                "qr_code_base64": qr_code_base64,
                "valor": plano['preco'],
                "plano": plano
            })

        return jsonify({"success": False, "error": res_data.get('message', 'Erro ao gerar PIX')})

    except Exception as e:
        logger.error(f"❌ Erro ao criar PIX: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/pix/verificar', methods=['POST'])
def verificar_pix():
    try:
        data = request.json or {}
        pix_id = data.get('pix_id')

        if pix_id not in pagamentos_pendentes:
            return jsonify({"success": False, "error": "Pagamento não encontrado"})

        if pagamentos_pendentes[pix_id]['pago']:
            return jsonify({"pago": True})

        url = f"https://api.mercadopago.com/v1/payments/{pix_id}"
        headers = {"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}"}
        res = requests.get(url, headers=headers, timeout=10)
        res_data = res.json()

        if res.status_code == 200 and res_data.get('status') == 'approved':
            _confirmar_pagamento_plano(pix_id)
            return jsonify({"pago": True})

        return jsonify({"pago": False, "status": res_data.get('status', 'pending')})

    except Exception as e:
        logger.error(f"❌ Erro ao verificar PIX: {e}")
        return jsonify({"success": False, "error": str(e)})

def _confirmar_pagamento_plano(pix_id):
    info = pagamentos_pendentes.get(pix_id)
    if not info or info.get('pago'):
        return
    info['pago'] = True
    db_id = info['db_id']
    plano_id = info['plano_id']
    plano = next((p for p in PLANOS if p['id'] == plano_id), None)

    if not plano:
        logger.error(f"❌ Plano {plano_id} não encontrado para {db_id}")
        return

    dados = carregar_usuario_firebase(db_id)
    if dados:
        dados['plano'] = plano_id
        if plano_id == 5:
            dados['expira_em'] = (datetime.now() + timedelta(minutes=3)).isoformat()
        else:
            dados['expira_em'] = (datetime.now() + timedelta(days=plano['dias'])).isoformat()
        
        if salvar_usuario_firebase(db_id, dados):
            logger.info(f"✅ Plano '{plano['nome']}' ativado para {db_id} via PIX {pix_id}")
        else:
            logger.error(f"❌ Erro ao salvar plano para {db_id}")
    else:
        logger.error(f"❌ Usuário {db_id} não encontrado no Firebase")

def _verificador_automatico_pix():
    while True:
        _time.sleep(15)
        try:
            for pix_id, dados in list(pagamentos_pendentes.items()):
                if dados.get('pago'):
                    continue
                try:
                    url = f"https://api.mercadopago.com/v1/payments/{pix_id}"
                    headers = {"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}"}
                    res = requests.get(url, headers=headers, timeout=10)
                    res_data = res.json()
                    if res.status_code == 200 and res_data.get('status') == 'approved':
                        _confirmar_pagamento_plano(pix_id)
                except Exception as e:
                    logger.error(f"⚠️ Erro verificando PIX {pix_id}: {e}")
        except Exception as e:
            logger.error(f"⚠️ Erro no verificador PIX: {e}")

# ============================================================
# ROTAS DE USUÁRIOS
# ============================================================

@app.route('/api/usuarios')
def get_usuarios():
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        if not is_plano_ativo(db_id):
            return plano_bloqueado_response()

        with get_db('data/usuarios.db') as conn:
            cursor = conn.execute("""
                SELECT id, nome, email, cargo, criado_em, ultimo_acesso, session_id 
                FROM users WHERE db_id=? ORDER BY criado_em ASC
            """, (db_id,))
            usuarios = []
            for row in cursor.fetchall():
                usuario = dict(row)
                usuario['online'] = bool(usuario['session_id'] and usuario['session_id'] in SESSOES_ATIVAS)
                usuarios.append(usuario)

        dados = carregar_usuario_firebase(db_id)
        plano_id = dados.get('plano', 1) if dados else 1
        plano = next((p for p in PLANOS if p['id'] == plano_id), PLANOS[0])

        return jsonify({
            "success": True,
            "usuarios": usuarios,
            "limite_usuarios": plano['usuarios'],
            "usuarios_atuais": len(usuarios)
        })
    except Exception as e:
        logger.error(f"❌ Erro ao buscar usuários: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/usuarios', methods=['POST'])
def criar_usuario():
    try:
        data = request.json or {}
        db_id = get_db_id()

        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        if not is_plano_ativo(db_id):
            return plano_bloqueado_response()

        nome = (data.get('nome') or '').strip()
        email = (data.get('email') or '').strip().lower()
        senha = data.get('senha') or ''

        if not nome or not email or not senha:
            return jsonify({"success": False, "error": "Preencha nome, email e senha"})

        dados = carregar_usuario_firebase(db_id)
        if not dados:
            return jsonify({"success": False, "error": "Dados do plano não encontrados"})

        plano_id = dados.get('plano', 1)
        plano = next((p for p in PLANOS if p['id'] == plano_id), None)
        if not plano:
            return jsonify({"success": False, "error": "Plano inválido"})

        max_usuarios = plano['usuarios']

        with get_db('data/usuarios.db') as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM users WHERE db_id=?", (db_id,))
            total = cursor.fetchone()[0]

            if total >= max_usuarios:
                return jsonify({
                    "success": False,
                    "error": f"Limite de {max_usuarios} usuário(s) do plano {plano['nome']} atingido.",
                    "limite": max_usuarios,
                    "atual": total
                })

            cursor = conn.execute("SELECT id FROM users WHERE email=?", (email,))
            if cursor.fetchone():
                return jsonify({"success": False, "error": "Este email já está cadastrado"})

            
        # ===== VERIFICAR SE CNPJ JÁ EXISTE =====
        if cnpj:
            # Verificar no banco local
            with get_db('data/usuarios.db') as conn:
                cursor = conn.execute("SELECT email FROM users WHERE cnpj=?", (cnpj,))
                result = cursor.fetchone()
                if result:
                    return jsonify({
                        "success": False, 
                        "error": f"Este CNPJ já está cadastrado no email: {result[0]}. Faça login com essa conta."
                    })
            
            # Verificar no Firebase
            if validar_cnpj_firebase(cnpj):
                return jsonify({
                    "success": False,
                    "error": "Este CNPJ já está cadastrado. Faça login com sua conta existente."
                })
        

        user_id = str(uuid.uuid4())[:8]
            conn.execute("""
                INSERT INTO users (id, nome, email, senha, cargo, db_id, servidor_id, nome_loja, cnpj)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                nome,
                email,
                hash_senha(senha),
                data.get('cargo', 'Funcionario'),
                db_id,
                SERVIDOR_ID,
                session.get('nome_loja', ''),
                session.get('cnpj', '')
            ))

        logger.info(f"✅ Novo usuário criado: {email} (db_id: {db_id})")
        
        return jsonify({
            "success": True,
            "message": "Usuário criado com sucesso!",
            "usuario": {
                "id": user_id,
                "nome": nome,
                "email": email,
                "cargo": data.get('cargo', 'Funcionario')
            }
        })
    except Exception as e:
        logger.error(f"❌ Erro ao criar usuário: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/usuarios/<user_id>', methods=['DELETE'])
def delete_usuario(user_id):
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        if not is_plano_ativo(db_id):
            return plano_bloqueado_response()

        if user_id == get_usuario_id():
            return jsonify({"success": False, "error": "Não é possível excluir seu próprio usuário"})

        with get_db('data/usuarios.db') as conn:
            cursor = conn.execute("SELECT id FROM users WHERE id=? AND db_id=?", (user_id, db_id))
            if not cursor.fetchone():
                return jsonify({"success": False, "error": "Usuário não encontrado"})
            
            conn.execute("DELETE FROM users WHERE id=? AND db_id=?", (user_id, db_id))
            
            for db_id_key, session_id in list(SESSOES_ATIVAS.items()):
                if session_id == user_id:
                    del SESSOES_ATIVAS[db_id_key]
                    break

        logger.info(f"✅ Usuário {user_id} excluído (db_id: {db_id})")
        return jsonify({"success": True, "message": "Usuário excluído"})
    except Exception as e:
        logger.error(f"❌ Erro ao excluir usuário: {e}")
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# ROTAS DE LOJA
# ============================================================

@app.route('/api/loja/nome', methods=['POST'])
def salvar_nome_loja():
    try:
        data = request.json or {}
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        nome = (data.get('nome') or '').strip()
        cnpj = ''.join(filter(str.isdigit, data.get('cnpj') or ''))
        cnpj_dados = data.get('cnpj_dados', {})

        if not nome:
            return jsonify({"success": False, "error": "Nome da loja é obrigatório"})

        with get_db('data/usuarios.db') as conn:
            conn.execute("UPDATE users SET nome_loja=?, cnpj=?, cnpj_dados=? WHERE db_id=?",
                        (nome, cnpj, json.dumps(cnpj_dados, ensure_ascii=False), db_id))

        session['nome_loja'] = nome
        session['cnpj'] = cnpj
        session['cnpj_dados'] = cnpj_dados

        dados = carregar_usuario_firebase(db_id)
        if dados:
            dados['nome_loja'] = nome
            dados['cnpj'] = cnpj
            dados['cnpj_dados'] = cnpj_dados
            salvar_usuario_firebase(db_id, dados)

        return jsonify({"success": True, "message": "Informações da loja salvas!"})
    except Exception as e:
        logger.error(f"❌ Erro ao salvar dados da loja: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/loja/info')
def get_loja_info():
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        with get_db('data/usuarios.db') as conn:
            cursor = conn.execute("SELECT nome_loja, cnpj, cnpj_dados FROM users WHERE db_id=? LIMIT 1", (db_id,))
            result = cursor.fetchone()

        return jsonify({
            "success": True,
            "nome_loja": result[0] if result else 'Minha Loja',
            "cnpj": result[1] if result else '',
            "cnpj_dados": json.loads(result[2]) if result and result[2] else {}
        })
    except Exception as e:
        logger.error(f"❌ Erro ao buscar dados da loja: {e}")
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# ROTA PARA BUSCAR CNPJ
# ============================================================

def _normalizar_cnpj_dados(data):
    end = data.get('endereco') or {}

    def pick(*keys, default=''):
        for k in keys:
            v = data.get(k)
            if v not in (None, ''):
                return v
            v = end.get(k)
            if v not in (None, ''):
                return v
        return default

    cnae_desc = data.get('cnae_fiscal_descricao') or data.get('cnaePrincipalDescricao')
    if not cnae_desc:
        ativ = data.get('atividade_principal')
        if isinstance(ativ, list) and ativ:
            cnae_desc = ativ[0].get('text', '')
    cnae_desc = cnae_desc or ''

    return {
        "razao_social": pick('razao_social', 'razaoSocial', 'nome'),
        "nome_fantasia": pick('nome_fantasia', 'nomeFantasia', 'fantasia', 'nome'),
        "logradouro": pick('logradouro'),
        "numero": pick('numero'),
        "complemento": pick('complemento'),
        "bairro": pick('bairro'),
        "municipio": pick('municipio'),
        "uf": pick('uf'),
        "cep": pick('cep'),
        "telefone": pick('ddd_telefone_1', 'telefone'),
        "email": pick('email'),
        "cnae_descricao": cnae_desc,
        "porte": pick('porte', 'porte_empresa', 'porteEmpresa'),
        "natureza_juridica": pick('natureza_juridica', 'naturezaJuridica'),
        "data_abertura": pick('data_inicio_atividade', 'dataInicioAtividades', 'abertura'),
        "situacao": pick('descricao_situacao_cadastral', 'situacaoCadastral', 'situacao_cadastral')
    }

@app.route('/api/cnpj/<cnpj>')
def buscar_cnpj(cnpj):
    try:
        cnpj_limpo = ''.join(filter(str.isdigit, cnpj))

        if len(cnpj_limpo) != 14:
            return jsonify({"success": False, "error": "CNPJ inválido. Deve ter 14 dígitos."})

        if cnpj_limpo in CACHE_CNPJ:
            cache_data = CACHE_CNPJ[cnpj_limpo]
            if _time.time() - cache_data['timestamp'] < 86400:
                logger.info(f"📦 CNPJ {cnpj_limpo} retornado do cache")
                return jsonify({"success": True, "dados": cache_data['dados'], "fonte": "cache"})

        apis = [
            f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}",
            f"https://api.opencnpj.org/{cnpj_limpo}",
            f"https://publica.cnpj.ws/cnpj/{cnpj_limpo}",
            f"https://www.receitaws.com.br/v1/cnpj/{cnpj_limpo}",
        ]

        ultimo_erro = "CNPJ não encontrado em nenhuma fonte disponível"

        for url in apis:
            try:
                response = requests.get(
                    url, timeout=12,
                    headers={"User-Agent": "PDV-Inteligente/8.0 (consulta CNPJ)"}
                )
                if response.status_code != 200:
                    ultimo_erro = f"Fonte respondeu status {response.status_code}"
                    continue

                raw = response.json()

                if 'estabelecimento' in raw:
                    est = raw.get('estabelecimento', {})
                    flat = {
                        "razao_social": raw.get('razao_social', ''),
                        "nome_fantasia": est.get('nome_fantasia', ''),
                        "logradouro": est.get('logradouro', ''),
                        "numero": est.get('numero', ''),
                        "complemento": est.get('complemento', ''),
                        "bairro": est.get('bairro', ''),
                        "municipio": (est.get('cidade') or {}).get('nome', ''),
                        "uf": (est.get('estado') or {}).get('sigla', ''),
                        "cep": est.get('cep', ''),
                        "ddd_telefone_1": f"{est.get('ddd1','')}{est.get('telefone1','')}",
                        "email": est.get('email', ''),
                        "cnae_fiscal_descricao": (est.get('atividade_principal') or {}).get('descricao', ''),
                        "porte": (raw.get('porte') or {}).get('descricao', ''),
                        "natureza_juridica": (raw.get('natureza_juridica') or {}).get('descricao', ''),
                        "data_inicio_atividade": est.get('data_inicio_atividade', ''),
                        "descricao_situacao_cadastral": est.get('situacao_cadastral', '')
                    }
                else:
                    flat = raw

                if not flat.get('razao_social') and not flat.get('razaoSocial') and not flat.get('nome'):
                    ultimo_erro = "Resposta sem razão social"
                    continue

                dados = _normalizar_cnpj_dados(flat)
                
                CACHE_CNPJ[cnpj_limpo] = {
                    'dados': dados,
                    'timestamp': _time.time()
                }
                
                return jsonify({"success": True, "dados": dados, "fonte": url.split('/')[2]})

            except requests.exceptions.Timeout:
                ultimo_erro = "Tempo de resposta excedido"
                continue
            except Exception as e:
                ultimo_erro = str(e)
                continue

        return jsonify({"success": False, "error": f"Não foi possível consultar o CNPJ. {ultimo_erro}"})

    except Exception as e:
        logger.error(f"❌ Erro ao buscar CNPJ: {e}")
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# ROTA DE SINCRONIZAÇÃO
# ============================================================

@app.route('/api/sincronizar', methods=['POST'])
def sincronizar():
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        if not is_plano_ativo(db_id):
            return plano_bloqueado_response()

        dados = carregar_usuario_firebase(db_id)
        if not dados:
            dados = {
                'db_id': db_id,
                'nome': session.get('nome', ''),
                'email': session.get('email', ''),
                'servidor_id': SERVIDOR_ID,
                'nome_loja': session.get('nome_loja', 'Minha Loja'),
                'cnpj': session.get('cnpj', ''),
                'cnpj_dados': session.get('cnpj_dados', {}),
                'data_cadastro': datetime.now().isoformat(),
                'plano': 1,
                'expira_em': (datetime.now() + timedelta(days=7)).isoformat(),
                'produtos': {},
                'clientes': {},
                'vendas': [],
                'caixa': {'status': 'fechado'},
                'config': {}
            }

        with get_db('data/produtos.db') as conn:
            cursor = conn.execute("SELECT codigo, nome, preco, estoque, categoria FROM produtos WHERE db_id=?", (db_id,))
            produtos = {}
            for row in cursor.fetchall():
                produtos[row[0]] = {"nome": row[1], "preco": row[2], "estoque": row[3], "categoria": row[4] or 'Geral'}
            dados['produtos'] = produtos

        with get_db('data/clientes.db') as conn:
            cursor = conn.execute("SELECT id, nome, telefone, email, divida FROM clientes WHERE db_id=?", (db_id,))
            clientes = {}
            for row in cursor.fetchall():
                clientes[str(row[0])] = {"nome": row[1], "telefone": row[2] or '', "email": row[3] or '', "divida": row[4] or 0}
            dados['clientes'] = clientes

        with get_db('data/vendas.db') as conn:
            cursor = conn.execute("""
                SELECT data_hora, subtotal, desconto, total, metodo, itens, cliente, usuario_id
                FROM vendas WHERE db_id=?
            """, (db_id,))
            vendas = []
            for row in cursor.fetchall():
                try:
                    itens = json.loads(row[5]) if row[5] else []
                except:
                    itens = []
                vendas.append({
                    "data_hora": row[0],
                    "subtotal": row[1],
                    "desconto": row[2],
                    "total": row[3],
                    "metodo": row[4],
                    "itens": itens,
                    "cliente": row[6] or '',
                    "usuario_id": row[7] or ''
                })
            dados['vendas'] = vendas

        with get_db('data/caixa.db') as conn:
            cursor = conn.execute("SELECT * FROM caixa WHERE db_id=? ORDER BY id DESC LIMIT 1", (db_id,))
            result = cursor.fetchone()
            if result:
                dados['caixa'] = {
                    "usuario_id": result[1],
                    "valor_abertura": result[2],
                    "data_abertura": result[3],
                    "data_fechamento": result[4],
                    "total": result[5] or 0,
                    "status": result[6]
                }
            else:
                dados['caixa'] = {'status': 'fechado'}

        if salvar_usuario_firebase(db_id, dados):
            return jsonify({"success": True, "message": "Dados sincronizados com Firebase!"})
        else:
            return jsonify({"success": False, "error": "Erro ao salvar no Firebase"})
    except Exception as e:
        logger.error(f"❌ Erro na sincronização: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/servidor/id')
def get_servidor_id():
    return jsonify({"success": True, "servidor_id": SERVIDOR_ID, "versao": VERSION})

# ============================================================
# HEALTH CHECK
# ============================================================

@app.route('/api/health')
def health_check():
    status = {
        "status": "online",
        "versao": VERSION,
        "servidor_id": SERVIDOR_ID,
        "timestamp": datetime.now().isoformat(),
        "db_status": "ok",
        "firebase_status": "ok",
        "sessoes_ativas": len(SESSOES_ATIVAS)
    }
    
    try:
        response = requests.get(f'{FB_URL}/pdv/usuarios.json?shallow=true', timeout=5)
        if response.status_code != 200:
            status["firebase_status"] = "warning"
    except:
        status["firebase_status"] = "error"
        status["status"] = "degraded"
    
    try:
        with get_db('data/usuarios.db') as conn:
            conn.execute("SELECT 1")
    except:
        status["db_status"] = "error"
        status["status"] = "degraded"
    
    return jsonify(status)

# ============================================================
# LIMPAR SESSÕES INATIVAS
# ============================================================

def limpar_sessoes_inativas():
    while True:
        _time.sleep(300)
        try:
            with get_db('data/usuarios.db') as conn:
                cursor = conn.execute("""
                    SELECT id, session_id FROM users 
                    WHERE session_id != '' AND ultimo_acesso < datetime('now', '-1 hour')
                """)
                inativos = cursor.fetchall()
                for user in inativos:
                    user_id, session_id = user
                    for db_id_key, sess_id in list(SESSOES_ATIVAS.items()):
                        if sess_id == session_id:
                            del SESSOES_ATIVAS[db_id_key]
                            break
                    conn.execute("UPDATE users SET session_id='' WHERE id=?", (user_id,))
                    logger.info(f"🧹 Sessão inativa removida: {user_id}")
        except Exception as e:
            logger.error(f"⚠️ Erro ao limpar sessões inativas: {e}")

# ============================================================
# VERIFICAR DEPENDÊNCIAS
# ============================================================

def verificar_dependencias():
    dependencias = {
        'flask': 'Flask',
        'requests': 'requests',
        'sqlite3': 'sqlite3',
    }
    
    if IS_WINDOWS:
        dependencias['win32print'] = 'pywin32'
        dependencias['PIL'] = 'Pillow'
        dependencias['qrcode'] = 'qrcode'
    
    problemas = []
    for modulo, nome in dependencias.items():
        try:
            __import__(modulo)
        except ImportError:
            problemas.append(nome)
    
    if problemas:
        logger.warning(f"⚠️ Dependências faltando: {', '.join(problemas)}")
        if IS_WINDOWS:
            logger.warning("Execute: pip install -r requirements.txt")
        else:
            logger.warning("Execute: pip install flask flask-cors requests")
        return False
    return True

# ============================================================
# INICIAR SERVIDOR
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print(f"🏪 PDV INTELIGENTE v{VERSION} - COM BUSCA INTELIGENTE DE CÓDIGO DE BARRAS")
    print("=" * 60)
    
    if not verificar_dependencias():
        if IS_WINDOWS:
            print("\n❌ Dependências faltando! Execute:")
            print("pip install flask flask-cors requests pywin32 Pillow qrcode")
        else:
            print("\n❌ Dependências faltando! Execute:")
            print("pip install flask flask-cors requests")
        sys.exit(1)
    
    print("📥 Verificando atualizações do HTML...")
    baixar_html_github()
    print("=" * 60)
    
    print("✅ WAL (Write-Ahead Logging) ativado")
    print("✅ Retry automático em caso de lock")
    print("✅ HTML servido localmente (templates/index.html)")
    print("✅ Download automático do HTML do GitHub")
    print("✅ Bloqueio total de funcionalidades com plano expirado")
    print("✅ Criação de usuários respeitando limite do plano")
    print("✅ Busca de CNPJ com múltiplas fontes (fallback automático)")
    print("✅ Cache de CNPJ por 24 horas")
    print("✅ Rate limiting para prevenir abusos")
    print("✅ Controle de sessão (apenas 1 dispositivo por conta)")
    if IS_WINDOWS and IMPRESSAO_DISPONIVEL:
        print("✅ Impressão direta (sem janela de seleção)")
        print("✅ Cupom fiscal 80mm formatado")
    else:
        print("✅ Impressão em modo de simulação (ambiente não Windows)")
    print("✅ Todos os planos a R$ 0,01 (teste de pagamento real)")
    print("✅ BUSCA INTELIGENTE DE PRODUTOS POR CÓDIGO DE BARRAS")
    print("   - OpenFoodFacts (gratuita e confiável)")
    print("   - BrasilAPI (produtos brasileiros)")
    print("   - Product Search (fallback)")
    print("   - Cache de 7 dias")
    print("✅ VERIFICAÇÃO AUTOMÁTICA DE COLUNAS EM TODAS AS TABELAS")
    print("=" * 60)

    init_db()

    # Iniciar threads
    threading.Thread(target=_verificador_automatico_pix, daemon=True).start()
    threading.Thread(target=limpar_sessoes_inativas, daemon=True).start()
    print("✅ Verificador automático de PIX iniciado")
    print("✅ Limpeza de sessões inativas iniciada")

    print(f"\n🆔 Servidor: {SERVIDOR_ID}")
    print("🌐 http://localhost:5000")
    print("\n📋 Para testar a busca de código de barras:")
    print("   1. Vá para a aba 'Estoque'")
    print("   2. Digite um código como '7894900027013'")
    print("   3. Clique em 'Buscar'")
    print("   4. O sistema buscará automaticamente em: OpenFoodFacts → BrasilAPI → Product Search\n")

    app.run(host='0.0.0.0', port=5000, debug=False)
