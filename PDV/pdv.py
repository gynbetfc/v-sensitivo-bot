# pdv.py - SMART PDV v11.0.0 - VERSÃO COM PLANOS REVISADOS
"""
🏪 SMART PDV v11.0.0

🔹 NOVIDADES v10.3:
- 15 DIAS DE TESTE GRÁTIS (EMPRESARIAL COMPLETO) ✅
- NOVOS VALORES DE PLANOS (R$ 29,99 a R$ 129,99) ✅
- CORREÇÃO DA REIMPRESSÃO DE CUPONS ✅
- CAMPO CÓDIGO DE BARRAS RESTAURADO ✅
- FIADO BLOQUEADO PARA PLANOS SEM CLIENTES ✅
- SISTEMA DE CLIENTES CORRIGIDO ✅
"""

import sys
import os
import io
import json
import sqlite3
import hashlib
import secrets
import requests
import uuid
import socket
import unicodedata
import threading
import logging
import time as _time
from datetime import datetime, timedelta
from contextlib import contextmanager
from functools import wraps
from typing import Optional, Dict, List, Any, Union, Tuple, Callable
from dataclasses import dataclass, asdict
from flask import Flask, request, jsonify, render_template, session, make_response
from flask_cors import CORS
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import padding as rsa_padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key, pkcs12
from cryptography.x509.oid import NameOID
import hmac
import base64
import re

# ============================================================
# NFC-e - dependências pesadas e opcionais (lxml, signxml, nfelib,
# requests-pkcs12). Guardadas em try/except igual o win32print: quem gerou o
# .exe/apk antes dessas libs existirem não pode ficar com o app inteiro
# quebrado por causa de uma feature que talvez nem use ainda.
# ============================================================
FISCAL_NFCE_DISPONIVEL: bool = False
try:
    from lxml import etree as fiscal_etree
    from signxml import (XMLSigner as _XMLSignerBase, SignatureMethod as FiscalSigMethod,
        DigestAlgorithm as FiscalDigestAlg, CanonicalizationMethod as FiscalC14nMethod, methods as fiscal_signxml_methods)
    from requests_pkcs12 import Pkcs12Adapter
    from nfelib.nfe.client.v4_0.servers import servers as SEFAZ_SERVERS, Endpoint as SefazEndpoint

    class _NFCeXMLSigner(_XMLSignerBase):
        """A SEFAZ exige SHA-1/RSA-SHA1 pra assinar a NFC-e - é uma exigência
        do padrão nacional (não muda há mais de uma década), não uma escolha
        de segurança nossa. O signxml bloqueia SHA1 por padrão (com razão, em
        geral) mas aqui não tem alternativa: sem SHA1 a SEFAZ rejeita a nota."""
        def check_deprecated_methods(self):
            pass

    FISCAL_NFCE_DISPONIVEL = True
except Exception:
    pass

# ============================================================
# CORREÇÃO DE ENCODING PARA WINDOWS
# ============================================================
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

IS_WINDOWS: bool = sys.platform == 'win32'
IS_LINUX: bool = sys.platform.startswith('linux')
IS_TERMUX: bool = 'com.termux' in os.environ.get('PREFIX', '')

# ============================================================
# PASTA DE DADOS
# ============================================================
def get_app_data_dir() -> str:
    if IS_WINDOWS:
        base = os.environ.get('APPDATA', os.path.expanduser('~'))
        app_dir = os.path.join(base, 'SMART_PDV')
    else:
        app_dir = os.path.expanduser('~/.pdv')
    os.makedirs(app_dir, exist_ok=True)
    return app_dir

APP_DATA_DIR: str = get_app_data_dir()
DB_PATH: str = os.path.join(APP_DATA_DIR, 'pdv.db')
TEMPLATES_DIR: str = os.path.join(APP_DATA_DIR, 'templates')
CUPONS_DIR: str = os.path.join(APP_DATA_DIR, 'cupons')
LOG_PATH: str = os.path.join(APP_DATA_DIR, 'pdv.log')
# Certificado digital (NFC-e): pasta PRIVADA, nunca dentro de templates/static
# (não pode ser servida por rota nenhuma) e nunca sincronizada pro Firebase -
# é uma credencial que só faz sentido existir nesta instalação.
FISCAL_DIR: str = os.path.join(APP_DATA_DIR, 'fiscal')

os.makedirs(APP_DATA_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(CUPONS_DIR, exist_ok=True)
os.makedirs(FISCAL_DIR, exist_ok=True)

# ============================================================
# IMPRESSÃO - APENAS WINDOWS
# ============================================================
IMPRESSAO_DISPONIVEL: bool = False
if IS_WINDOWS:
    try:
        import win32print
        import win32ui
        IMPRESSAO_DISPONIVEL = True
        print("🖨️ Impressão Windows ESC/POS disponível")
    except ImportError as e:
        print(f"⚠️ Módulos de impressão não encontrados: {e}")
else:
    print("⚠️ Impressão ESC/POS disponível apenas no Windows")

# ============================================================
# FLASK APP
# ============================================================
app: Flask = Flask(__name__, template_folder=TEMPLATES_DIR)

def _obter_secret_key() -> str:
    """Carrega uma secret_key persistente do disco; gera e salva na primeira vez.
    Sem isso, a chave mudaria a cada restart e TODOS os logins cairiam (cookies invalidados)."""
    caminho_chave = os.path.join(APP_DATA_DIR, 'secret.key')
    try:
        if os.path.exists(caminho_chave):
            with open(caminho_chave, 'r', encoding='utf-8') as f:
                chave = f.read().strip()
                if chave:
                    return chave
        chave = secrets.token_hex(32)
        with open(caminho_chave, 'w', encoding='utf-8') as f:
            f.write(chave)
        return chave
    except Exception:
        # Se não der pra persistir, ao menos não quebra (mas sessões não sobrevivem a restart)
        return secrets.token_hex(32)

app.secret_key = _obter_secret_key()
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False

CORS(app, origins=["*"], supports_credentials=True)

@app.after_request
def _desabilitar_cache_api(response):
    """Evita que o navegador (WebView do Termux) sirva respostas de API em cache,
    como o /api/auth/status — o que faria o logout 'não pegar' após um refresh."""
    try:
        if request.path.startswith('/api/'):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
    except Exception:
        pass
    return response

VERSION: str = "11.0.0"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger: logging.Logger = logging.getLogger(__name__)

# ============================================================
# CONFIGURAÇÕES
# ============================================================
FB_URL: str = "https://droidguard-10597-default-rtdb.firebaseio.com"
HTML_URL: str = "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/refs/heads/main/PDV/templates/index.html"
# Imagem de fundo padrão para contas novas (tela de vendas)
BG_PADRAO_URL: str = "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/main/PDV/bg.png"
SESSOES_ATIVAS: Dict[str, str] = {}
# 🔧 token de sessão (assinado pelo Worker) que autoriza ESTE processo a ler/
# escrever os dados de cada db_id no Firebase, via proxy do Worker. Fica
# guardado aqui (não no Flask session) de propósito: várias funções de
# sincronização rodam em THREADS DE FUNDO, onde flask.session não existe -
# elas já recebem db_id como parâmetro, então indexar por db_id aqui também
# não exige mudar a assinatura de nenhuma delas.
FB_TOKENS_POR_DB_ID: Dict[str, str] = {}
# Porta usada só para um PDV avisar o outro que já existe um servidor rodando
PORTA_DESCOBERTA: int = 50505
# Controla quando cada conta sincronizou o token do plano pela última vez.
# Evita que toda operação (venda, exclusão) dispare uma chamada ao Firebase.
_ULTIMO_SYNC_TOKEN: Dict[str, float] = {}
CACHE_CNPJ: Dict[str, Dict] = {}
CACHE_PRODUTO_BARRAS: Dict[str, Dict] = {}

MERCADO_PAGO_ACCESS_TOKEN: str = ""  # vazio de propósito: o token vive só no backend

# ============================================================
# BACKEND DE PAGAMENTOS (Cloudflare Worker)
# ============================================================
# O token do Mercado Pago NÃO fica mais aqui. Este arquivo vai para a máquina de
# cada lojista, então qualquer segredo escrito aqui estaria exposto. Em vez disso,
# o PDV pede a cobrança ao nosso servidor, que é o único que conhece o token.
# Depois de publicar o worker, troque pela URL dele.
BACKEND_PAGAMENTOS_URL: str = os.environ.get(
    "PDV_BACKEND_URL",
    "https://smartpdv-pay.gyn-bet-fc.workers.dev"
)

# ============================================================
# CHAVES PARA TOKENS DE PLANO
# ============================================================
# 🔧 HISTÓRICO DE SEGURANÇA: até a v11, esta chave era SIMÉTRICA (a mesma
# usada pra assinar E verificar) e o próprio pdv.py assinava os tokens
# localmente. Como este arquivo é baixado em texto puro de um repositório
# PÚBLICO do GitHub, qualquer pessoa podia ler essa chave e assinar um token
# de plano "Empresarial" válido pra sempre - sem nunca pagar nada nem falar
# com o Mercado Pago. CHAVE_SECRETA_PLANO agora só existe pra continuar
# validando tokens ANTIGOS (v1) já emitidos antes desta correção - nenhum
# token novo é assinado com ela (ver PlanoSincronizado._criar_token).
#
# Tokens NOVOS (v2) usam assinatura RSA assimétrica: só o Worker (backend)
# tem a chave PRIVADA e consegue EMITIR um token. O pdv.py só tem a chave
# PÚBLICA abaixo, que serve só pra VERIFICAR - publicá-la não é um risco,
# é assim que assinatura assimétrica funciona por definição.
CHAVE_SECRETA_PLANO: str = "hs7sudjsjfirijf839djd"

CHAVE_PUBLICA_PLANO_PEM: str = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApSUNGT0VEP4Zkh/I2MD2
hdu8PUgrd0pI2wIMaNZXHB/C6i2KKTz+naXyTBA3CRIeJSjYIn4vbdlYHyDsAXkp
LkHuCBbCdxOd/dXmIsHh+fvF1FwLIrpxvdNBc2GADuJBvKjkbqtXC/dAQgOVipY/
+iE3INHopfRTw4KMddMipi28tHR37GlHuwHV3jj+ZIxMTId0tdP4u28bxUM1htcD
RhsQ46llCX1QBTP/jNPzKzYZBFMUEpkBDAHeDRHtrKXHujy8VaV24CI+cgyUEhFa
eAYEIsB7lcV+FUjyRnBSSn2nJS/uUWlziUYiLDRBuasGH6zfV4iIorZSKO3n+Vsq
JQIDAQAB
-----END PUBLIC KEY-----"""

# ============================================================
# PLANOS REVISADOS
# ============================================================
@dataclass
class Plano:
    id: int
    usuarios: int
    preco: float
    nome: str
    dias: int
    produtos: int
    permissoes: Dict
    is_teste: bool = False
    oculto: bool = False

PLANOS: List[Plano] = [
    Plano(1, 1, 49.99, '🔰 BÁSICO', 30, 1000, {
        'clientes': False,
        'dashboard': False,
        'busca_estoque': False,
        'margem': False,
        'fiado': False,
        'kit_combo': False,
    }),
    Plano(2, 3, 89.99, '⭐ STANDARD', 30, 5000, {
        'clientes': True,
        'dashboard': False,
        'busca_estoque': True,
        'margem': False,
        'fiado': True,
        'kit_combo': True,
    }),
    Plano(3, 10, 119.99, '💎 PREMIUM', 30, -1, {
        'clientes': True,
        'dashboard': True,
        'busca_estoque': True,
        'margem': True,
        'fiado': True,
        'kit_combo': True,
    }),
    Plano(4, 10, 149.99, '👑 EMPRESARIAL', 30, -1, {
        'clientes': True,
        'dashboard': True,
        'busca_estoque': True,
        'margem': True,
        'fiado': True,
        'kit_combo': True,
    }, oculto=True),
    # Plano de TESTE (15 dias, todas as permissões liberadas, limite de 300 produtos e 1 usuário)
    Plano(5, 1, 0.00, '🎁 TESTE', 15, 50, {
        'clientes': True,
        'dashboard': True,
        'busca_estoque': True,
        'margem': True,
        'fiado': True,
        'kit_combo': True,
    }, is_teste=True),
]

# ============================================================
# DURAÇÕES DOS PLANOS (com desconto progressivo)
# ============================================================
DURACOES_PLANO = [
    {"meses": 1,  "dias": 30,  "desconto": 0.00, "label": "Mensal"},
    {"meses": 3,  "dias": 90,  "desconto": 0.10, "label": "3 meses"},
    {"meses": 6,  "dias": 180, "desconto": 0.20, "label": "6 meses"},
    {"meses": 12, "dias": 365, "desconto": 0.30, "label": "1 ano"},
]

def calcular_preco_duracao(preco_mensal: float, meses: int):
    """Retorna (preco_total, dias, desconto, economia) para uma duração."""
    dur = next((d for d in DURACOES_PLANO if d["meses"] == meses), DURACOES_PLANO[0])
    preco_cheio = preco_mensal * meses
    preco_final = preco_cheio * (1 - dur["desconto"])
    economia = preco_cheio - preco_final
    return round(preco_final, 2), dur["dias"], dur["desconto"], round(economia, 2)

pagamentos_pendentes: Dict[str, Dict] = {}
rate_limits: Dict[str, List[float]] = {}

# ============================================================
def rate_limit(max_requests: int = 10, window: int = 60) -> Callable:
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapped(*args, **kwargs) -> Any:
            key: str = request.remote_addr
            now: float = _time.time()
            if key not in rate_limits:
                rate_limits[key] = []
            rate_limits[key] = [t for t in rate_limits[key] if now - t < window]
            if len(rate_limits[key]) >= max_requests:
                return jsonify({"success": False, "error": "Muitas requisições. Tente novamente."}), 429
            rate_limits[key].append(now)
            return f(*args, **kwargs)
        return wrapped
    return decorator

# ============================================================
# DECORATOR PARA VERIFICAR PLANO
# ============================================================

def verificar_plano(f: Callable) -> Callable:
    @wraps(f)
    def decorated(*args, **kwargs):
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401
        if not is_plano_ativo(db_id):
            dias_restantes = get_dias_restantes(db_id)
            return jsonify({
                "success": False,
                "error": "Plano expirado. Renove para continuar.",
                "plano_expirado": True,
                "dias_restantes": dias_restantes,
                "url_renovacao": "#/planos"
            }), 403
        
        return f(*args, **kwargs)
    return decorated

# ============================================================
# FUNÇÃO PARA VERIFICAR PERMISSÕES
# ============================================================

def verificar_permissao(permissao: str):
    """Decorator para verificar permissões específicas"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            db_id = get_db_id()
            if not db_id:
                return jsonify({"success": False, "error": "Não autenticado"}), 401
            
            permissoes = get_permissoes(db_id)
            if not permissoes.get(permissao, False):
                return jsonify({
                    "success": False,
                    "error": f"Seu plano não permite acesso a esta funcionalidade.",
                    "permissao_negada": True
                }), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator

# ============================================================
# BANCO DE DADOS
# ============================================================
def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=10000")
    conn.execute("PRAGMA busy_timeout=30000")
    conn.execute("PRAGMA temp_store=MEMORY")
    return conn

@contextmanager
def get_db_context():
    conn = None
    try:
        conn = get_db()
        yield conn
        conn.commit()
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            _time.sleep(0.5)
            try:
                conn2 = get_db()
                yield conn2
                conn2.commit()
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

def init_db() -> None:
    with get_db_context() as conn:
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
                cnpj TEXT DEFAULT '',
                cnpj_dados TEXT DEFAULT '{}',
                session_id TEXT DEFAULT '',
                ultimo_acesso TIMESTAMP,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                plano_cache INTEGER DEFAULT 1,
                expira_cache TEXT,
                ultima_verificacao TEXT,
                sincronizado_em TIMESTAMP
            )
        ''')
        for coluna, definicao in (
            ('inscricao_estadual', "TEXT DEFAULT ''"),
            ('regime_tributario', "TEXT DEFAULT '1'"),  # 1=Simples Nacional
        ):
            try:
                conn.execute(f"ALTER TABLE users ADD COLUMN {coluna} {definicao}")
                conn.commit()
            except Exception:
                pass

        conn.execute('''
            CREATE TABLE IF NOT EXISTS produtos (
                codigo TEXT PRIMARY KEY,
                nome TEXT,
                preco REAL,
                custo REAL DEFAULT 0,
                margem REAL DEFAULT 0,
                estoque INTEGER DEFAULT 0,
                categoria TEXT DEFAULT 'Geral',
                imagem_url TEXT DEFAULT '',
                db_id TEXT,
                ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sincronizado_em TIMESTAMP
            )
        ''')
        try:
            conn.execute("ALTER TABLE produtos ADD COLUMN imagem_url TEXT DEFAULT ''")
            conn.commit()
        except Exception:
            pass
        # Campos fiscais (NFC-e). Defaults pensados pro caso mais comum de
        # varejo pequeno no Simples Nacional (CSOSN 102 = tributado sem
        # crédito de ICMS, CFOP 5102 = venda dentro do estado, UN = unidade).
        # O NCM NÃO tem default seguro - cada produto precisa do código real
        # (8 dígitos), então fica em branco até o lojista preencher.
        for coluna, definicao in (
            ('ncm', "TEXT DEFAULT ''"),
            ('cfop', "TEXT DEFAULT '5102'"),
            ('csosn', "TEXT DEFAULT '102'"),
            ('unidade', "TEXT DEFAULT 'UN'"),
            ('origem', "TEXT DEFAULT '0'"),
        ):
            try:
                conn.execute(f"ALTER TABLE produtos ADD COLUMN {coluna} {definicao}")
                conn.commit()
            except Exception:
                pass

        conn.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                telefone TEXT,
                email TEXT,
                divida REAL DEFAULT 0,
                db_id TEXT,
                ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sincronizado_em TIMESTAMP
            )
        ''')

        conn.execute('''
            CREATE TABLE IF NOT EXISTS vendas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_hora TEXT,
                subtotal REAL,
                desconto REAL DEFAULT 0,
                total REAL,
                lucro_total REAL DEFAULT 0,
                metodo TEXT DEFAULT 'Dinheiro',
                itens TEXT,
                cliente TEXT DEFAULT '',
                usuario_id TEXT DEFAULT '',
                db_id TEXT,
                recebido REAL DEFAULT 0,
                troco REAL DEFAULT 0,
                sincronizado_em TIMESTAMP
            )
        ''')

        conn.execute('''
            CREATE TABLE IF NOT EXISTS caixa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id TEXT,
                valor_abertura REAL,
                data_abertura TEXT,
                data_fechamento TEXT,
                total REAL DEFAULT 0,
                status TEXT DEFAULT 'fechado',
                db_id TEXT,
                sincronizado_em TIMESTAMP
            )
        ''')

        conn.execute('''
            CREATE TABLE IF NOT EXISTS fiscal_nfce (
                venda_id INTEGER PRIMARY KEY,
                chave_acesso TEXT,
                protocolo TEXT,
                situacao TEXT,
                autorizada INTEGER DEFAULT 0,
                ambiente TEXT,
                xml_assinado TEXT,
                qrcode_url TEXT,
                erro TEXT,
                emitida_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                db_id TEXT,
                contingencia INTEGER DEFAULT 0,
                pendente_reenvio INTEGER DEFAULT 0,
                cancelada INTEGER DEFAULT 0,
                protocolo_cancelamento TEXT,
                justificativa_cancelamento TEXT,
                cancelada_em TIMESTAMP
            )
        ''')
        # Migração pra quem já tinha a tabela fiscal_nfce de antes desses campos existirem
        for coluna, definicao in (
            ('contingencia', "INTEGER DEFAULT 0"),
            ('pendente_reenvio', "INTEGER DEFAULT 0"),
            ('cancelada', "INTEGER DEFAULT 0"),
            ('protocolo_cancelamento', "TEXT"),
            ('justificativa_cancelamento', "TEXT"),
            ('cancelada_em', "TIMESTAMP"),
        ):
            try:
                conn.execute(f"ALTER TABLE fiscal_nfce ADD COLUMN {coluna} {definicao}")
                conn.commit()
            except Exception:
                pass

        conn.execute('''
            CREATE TABLE IF NOT EXISTS caixa_movimentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                caixa_id INTEGER,
                tipo TEXT,
                valor REAL,
                motivo TEXT,
                usuario_id TEXT,
                data_hora TEXT,
                db_id TEXT,
                sincronizado_em TIMESTAMP
            )
        ''')

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

        conn.execute('''
            CREATE TABLE IF NOT EXISTS config (
                chave TEXT PRIMARY KEY,
                valor TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.execute('''
            CREATE TABLE IF NOT EXISTS exclusoes (
                tipo TEXT,
                item_id TEXT,
                db_id TEXT,
                excluido_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (tipo, item_id, db_id)
            )
        ''')

        conn.execute('''
            CREATE TABLE IF NOT EXISTS kits (
                id TEXT PRIMARY KEY,
                nome TEXT,
                preco REAL DEFAULT 0,
                itens TEXT DEFAULT '[]',
                db_id TEXT,
                ativo INTEGER DEFAULT 1,
                ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sincronizado_em TIMESTAMP
            )
        ''')

        # MOVIMENTAÇÕES DE ESTOQUE (modelo de FATOS imutáveis).
        # Cada linha é um fato com ID único que NUNCA muda: um ajuste, uma entrada
        # ou uma saída (venda). O estoque de um produto = SOMA dos deltas dos seus
        # fatos. Como cada fato tem ID único, dois caixas vendendo ao mesmo tempo
        # SOMAM suas saídas (nunca se sobrescrevem) — o estoque fica sempre certo,
        # online, offline e em vários dispositivos. Sincroniza igual às vendas.
        # MOVIMENTAÇÕES DE FIADO (modelo de FATOS imutáveis).
        # A dívida de um cliente deixa de ser um número que se sobrescreve e passa
        # a ser a SOMA destes fatos: cada compra no fiado é um +valor, cada
        # pagamento é um -valor, todos com ID único. Assim, se um caixa registra
        # a compra e outro registra o pagamento ao mesmo tempo, os DOIS fatos
        # entram (ninguém sobrescreve ninguém) e a dívida fica sempre certa.
        #
        # A chave é o NOME do cliente (não o id): o id é AUTOINCREMENT local, ou
        # seja, dois dispositivos podem gerar o mesmo id para clientes diferentes.
        # As vendas já usam o nome pelo mesmo motivo.
        conn.execute('''
            CREATE TABLE IF NOT EXISTS fiado_mov (
                id TEXT PRIMARY KEY,
                cliente_nome TEXT,
                delta REAL,
                tipo TEXT,
                origem TEXT DEFAULT '',
                db_id TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.execute('''
            CREATE TABLE IF NOT EXISTS estoque_mov (
                id TEXT PRIMARY KEY,
                codigo TEXT,
                delta INTEGER,
                tipo TEXT,
                origem TEXT DEFAULT '',
                db_id TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Adicionar colunas faltantes
        for tabela, colunas in {
            'users': {'sincronizado_em': 'TIMESTAMP', 'bg_vendas_img': 'TEXT DEFAULT ""', 'bg_vendas_opacidade': 'INTEGER DEFAULT 50', 'escala_sistema': 'INTEGER DEFAULT 100', 'bg_vendas_img_ts': 'INTEGER DEFAULT 0', 'bg_vendas_opacidade_ts': 'INTEGER DEFAULT 0', 'escala_sistema_ts': 'INTEGER DEFAULT 0'},
            'produtos': {'custo': 'REAL DEFAULT 0', 'margem': 'REAL DEFAULT 0', 'ultima_atualizacao': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP', 'sincronizado_em': 'TIMESTAMP'},
            'clientes': {'ultima_atualizacao': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP', 'sincronizado_em': 'TIMESTAMP'},
            'vendas': {'lucro_total': 'REAL DEFAULT 0', 'recebido': 'REAL DEFAULT 0', 'troco': 'REAL DEFAULT 0', 'sincronizado_em': 'TIMESTAMP'},
            'caixa': {'sincronizado_em': 'TIMESTAMP'}
        }.items():
            cursor = conn.execute(f"PRAGMA table_info({tabela})")
            colunas_existentes = [row[1] for row in cursor.fetchall()]
            for coluna, tipo in colunas.items():
                if coluna not in colunas_existentes:
                    try:
                        conn.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {tipo}")
                    except:
                        pass

        conn.commit()
        logger.info("✅ Banco de dados inicializado")

# ============================================================
# AUXILIARES
# ============================================================
def hash_senha(senha: str) -> str:
    """Formato ANTIGO (SHA-256 puro). Mantido só para conseguir validar as senhas
    que já estão salvas. Contas novas usam gerar_hash_senha()."""
    return hashlib.sha256(senha.encode()).hexdigest()

# --- Senhas: PBKDF2 com sal ---------------------------------------------
# SHA-256 puro é rápido demais: quem obtiver o banco testa bilhões de senhas por
# segundo. PBKDF2 com sal deixa cada tentativa lenta e impede tabelas prontas
# (cada senha tem um sal diferente, então hashes iguais viram valores diferentes).
_PBKDF2_ITERACOES = 200_000

def gerar_hash_senha(senha: str) -> str:
    """Gera o hash novo. Formato: pbkdf2$<iteracoes>$<sal_hex>$<hash_hex>"""
    sal = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac('sha256', senha.encode(), sal, _PBKDF2_ITERACOES)
    return f"pbkdf2${_PBKDF2_ITERACOES}${sal.hex()}${dk.hex()}"

def senha_e_antiga(armazenado: str) -> bool:
    """True se o hash guardado ainda é do formato antigo (SHA-256)."""
    return bool(armazenado) and not str(armazenado).startswith('pbkdf2$')

def verificar_senha(senha: str, armazenado: str) -> bool:
    """Confere a senha contra o hash guardado, aceitando os formatos:
      - NOVO: pbkdf2$... (seguro, o padrão)
      - ANTIGO: SHA-256 puro (64 hex) — migrado no próximo login
      - TEXTO PURO: quando a senha foi digitada direto no Firebase sem hash
        (ex.: editada na mão no console). Aceitamos por conveniência e
        migramos para PBKDF2 assim que a pessoa loga.
    Assim ninguém fica travado, e senhas fracas em texto puro não permanecem."""
    if not armazenado:
        return False
    armazenado = str(armazenado)
    try:
        if armazenado.startswith('pbkdf2$'):
            _, iteracoes, sal_hex, hash_hex = armazenado.split('$', 3)
            dk = hashlib.pbkdf2_hmac('sha256', senha.encode(), bytes.fromhex(sal_hex), int(iteracoes))
            return secrets.compare_digest(dk.hex(), hash_hex)
        # SHA-256 puro tem exatamente 64 caracteres hexadecimais
        if len(armazenado) == 64 and all(ch in '0123456789abcdefABCDEF' for ch in armazenado):
            return secrets.compare_digest(hash_senha(senha), armazenado)
        # Caso contrário, tratamos como senha em TEXTO PURO (comparação direta).
        # É o caso de quem editou a senha manualmente no Firebase.
        return secrets.compare_digest(str(senha), armazenado)
    except Exception:
        return False


def senha_precisa_migrar(armazenado: str) -> bool:
    """True se o hash guardado NÃO está no formato seguro (PBKDF2).
    Cobre tanto SHA-256 antigo quanto senha em texto puro."""
    return bool(armazenado) and not str(armazenado).startswith('pbkdf2$')

def get_db_id() -> Optional[str]:
    db_id = session.get('db_id')
    if not db_id:
        return None
    # SESSÃO ÚNICA POR USUÁRIO: confere se este login ainda é o mais recente.
    # Quando a MESMA conta loga em outro lugar, gera um session_id novo e grava
    # no banco. Aqui, se o session_id do cookie não bate com o do banco, esta
    # sessão foi substituída (a conta abriu em outro caixa) → derruba esta.
    # Isso impede rodar vários caixas com uma conta só, furando o limite do plano.
    user_id = session.get('usuario_id')
    sess_id = session.get('session_id')
    if user_id and sess_id:
        try:
            with get_db_context() as conn:
                row = conn.execute("SELECT session_id FROM users WHERE id=? LIMIT 1", (user_id,)).fetchone()
            if row and row[0] and row[0] != sess_id:
                return None  # substituída por um login mais novo
        except Exception:
            pass
    return db_id


def _sessao_foi_substituida() -> bool:
    """True se a sessão atual foi derrubada por um login mais novo da mesma conta."""
    if not session.get('db_id'):
        return False
    user_id = session.get('usuario_id')
    sess_id = session.get('session_id')
    if not (user_id and sess_id):
        return False
    try:
        with get_db_context() as conn:
            row = conn.execute("SELECT session_id FROM users WHERE id=? LIMIT 1", (user_id,)).fetchone()
        return bool(row and row[0] and row[0] != sess_id)
    except Exception:
        return False

def get_usuario_id() -> Optional[str]:
    return session.get('usuario_id')

def get_timestamp() -> str:
    return datetime.now().isoformat()

# ============================================================
# FIREBASE — tudo passa pelo Worker (proxy autenticado), NUNCA mais direto.
# ============================================================
# 🔧 HISTÓRICO DE SEGURANÇA: até a v11, estas funções falavam com o Firebase
# DIRETO, em REST puro, sem nenhuma autenticação - e as regras do banco
# estavam completamente abertas (".read": true, ".write": true na raiz).
# Qualquer pessoa na internet lia/escrevia os dados de QUALQUER loja (hash de
# senha, CNPJ, vendas). Agora o pdv.py (código público) nunca mais toca o
# Firebase diretamente para dados de conta - ele fala com o Worker, que tem a
# credencial (Conta de Serviço) e decide o que cada pedido pode fazer, usando
# o token de sessão emitido no login (ver _login_via_backend).
def _fb_request(db_id: str, rota: str, corpo: Optional[Dict] = None) -> Optional[Dict]:
    """POST autenticado numa das rotas de dados do Worker (fb/get, fb/put,
    fb/patch), usando o token de sessão guardado pra este db_id. Devolve o
    corpo da resposta (dict) em caso de sucesso, ou None."""
    token = FB_TOKENS_POR_DB_ID.get(db_id)
    if not token:
        logger.warning(f"⚠️ Sem token de sessão pra {db_id} - não é possível falar com o Firebase agora (faça login de novo)")
        return None
    try:
        payload = {'session_token': token}
        if corpo:
            payload.update(corpo)
        with _sessao_http() as s:
            r = s.post(f"{BACKEND_PAGAMENTOS_URL}/{rota}", json=payload, timeout=15)
        if r.status_code == 200:
            return r.json()
        logger.warning(f"⚠️ Worker recusou {rota} para {db_id}: HTTP {r.status_code}")
        return None
    except Exception as e:
        logger.error(f"⚠️ Falha ao chamar o backend ({rota}) para {db_id}: {e}")
        return None

def salvar_usuario_firebase(db_id: str, dados: Dict) -> bool:
    r = _fb_request(db_id, 'fb/put', {'dados': dados})
    return bool(r and r.get('success'))

def salvar_campos_firebase(db_id: str, campos: Dict) -> bool:
    """Atualiza APENAS os campos informados no Firebase (PATCH), sem precisar
    carregar e reescrever todo o registro. Mais robusto para preferências
    como background, opacidade e escala."""
    r = _fb_request(db_id, 'fb/patch', {'campos': campos})
    return bool(r and r.get('success'))

# Valor mágico do Firebase: ao gravar, ele troca por um número com a HORA DO SERVIDOR
# (em milissegundos). Assim o timestamp não depende do relógio do dispositivo.
FIREBASE_TIMESTAMP = {".sv": "timestamp"}

def salvar_preferencia_firebase(db_id: str, campo: str, valor) -> bool:
    """Salva uma preferência (ex: bg_vendas_img) junto com um timestamp da hora
    do SERVIDOR Firebase. Grava dois campos: '<campo>' e '<campo>_ts'.
    Assim, na hora de sincronizar, o dispositivo com a versão mais NOVA vence,
    usando uma hora confiável (do servidor, não do aparelho)."""
    return salvar_campos_firebase(db_id, {campo: valor, f'{campo}_ts': FIREBASE_TIMESTAMP})

def em_segundo_plano(fn, *args, **kwargs) -> None:
    """Executa algo que depende da INTERNET sem fazer o usuário esperar.

    Princípio do PDV: o caixa é offline-first. Nenhuma ação do lojista (vender,
    cadastrar, salvar preferência) pode ficar parada esperando o Firebase. O que
    importa é gravar no banco LOCAL e responder na hora; subir para a nuvem é
    tarefa de fundo, e se falhar o próximo sync resolve."""
    def _rodar():
        try:
            fn(*args, **kwargs)
        except Exception as e:
            logger.warning(f"⚠️ Tarefa de fundo falhou (será refeita no próximo sync): {e}")
    threading.Thread(target=_rodar, daemon=True).start()


def ler_timestamp_online() -> Optional[int]:
    """Grava o timestamp do servidor Firebase num local temporário e lê de volta,
    para obter a hora do servidor em milissegundos. Usado para carimbar o valor
    LOCAL com uma hora confiável quando salvamos uma preferência."""
    try:
        url = f'{FB_URL}/pdv/_hora_servidor.json'
        r = requests.put(url, json=FIREBASE_TIMESTAMP, timeout=8)
        if r.status_code == 200:
            return r.json()  # o Firebase retorna o número já resolvido
    except Exception:
        pass
    return None

def carregar_usuario_firebase(db_id: str, timeout: int = 10) -> Optional[Dict]:
    if not db_id:
        return None
    r = _fb_request(db_id, 'fb/get')
    return r.get('dados') if r and r.get('success') else None

def firebase_online() -> bool:
    """Retorna True se o Firebase está acessível agora (temos internet).
    Usado no login para decidir: online = o Firebase manda (fonte da verdade);
    offline = permitimos login local como cortesia para não travar a loja.

    🔧 Continua batendo direto no Firebase (não passa pelo Worker) - este
    caminho (pdv/_hora_servidor) é intencionalmente público nas regras (só um
    timestamp, sem dado de ninguém), então não precisa de autenticação."""
    try:
        r = requests.get(f'{FB_URL}/pdv/_hora_servidor.json', timeout=5)
        return r.status_code == 200
    except Exception:
        return False

def _checar_existencia_backend(rota: str, campo: str, valor: str) -> bool:
    """Pergunta ao Worker se já existe uma conta com este email/CNPJ - SEM
    baixar o registro inteiro (nem o Worker devolve isso aqui, só um boolean).
    Usado no cadastro pra recusar duplicidade."""
    if not valor:
        return False
    try:
        with _sessao_http() as s:
            r = s.post(f"{BACKEND_PAGAMENTOS_URL}/{rota}", json={campo: valor}, timeout=10)
        if r.status_code == 200:
            return bool(r.json().get('existe'))
    except Exception as e:
        logger.warning(f"⚠️ Falha ao checar {campo} no backend: {e}")
    return False

def buscar_usuario_por_email_firebase(email: str) -> bool:
    """Só existência (pro cadastro recusar email duplicado) - a busca do
    registro completo pra LOGIN agora é feita pelo Worker (_login_via_backend),
    que é quem tem permissão de ver a senha com hash."""
    return _checar_existencia_backend('check_email', 'email', (email or '').strip().lower())

def validar_cnpj_firebase(cnpj: str) -> bool:
    return _checar_existencia_backend('check_cnpj', 'cnpj', cnpj)

def _login_via_backend(email: str, senha: str) -> Optional[Dict]:
    """Login em 2 idas ao Worker - por quê:

    🔧 Cloudflare Workers PROÍBE PBKDF2 com mais de 100.000 iterações (o
    pdv.py sempre usou 200.000 - _PBKDF2_ITERACOES). O Worker NUNCA consegue
    recalcular esse PBKDF2 sozinho, é uma trava da própria plataforma.

    Por isso quem faz a conta pesada (PBKDF2) continua sendo o PYTHON, que
    não tem esse limite - exatamente como sempre foi. 1ª ida (/login_salt):
    pergunta ao Worker o sal e o nº de iterações guardados pra este email
    (dado público, sem problema expor - já está hardcoded no pdv.py, que é
    público). 2ª ida (/login_verificar): manda o valor JÁ CALCULADO (nunca a
    senha em si) pro Worker comparar com o que está guardado - aí sim, se
    bater, ele emite o token de sessão."""
    try:
        with _sessao_http() as s:
            r1 = s.post(f"{BACKEND_PAGAMENTOS_URL}/login_salt", json={'email': email}, timeout=15)
        d1 = r1.json()
        if r1.status_code != 200 or not d1.get('success'):
            return None

        tipo = d1.get('tipo')
        if tipo == 'pbkdf2':
            salt = bytes.fromhex(d1['salt_hex'])
            iteracoes = int(d1['iteracoes'])
            valor = hashlib.pbkdf2_hmac('sha256', senha.encode(), salt, iteracoes).hex()
        elif tipo == 'sha256':
            valor = hash_senha(senha)  # mesmo hash SHA-256 puro do formato antigo
        else:
            valor = senha  # texto puro (conta editada manualmente no Firebase)

        with _sessao_http() as s:
            r2 = s.post(f"{BACKEND_PAGAMENTOS_URL}/login_verificar", json={'email': email, 'valor': valor}, timeout=15)
        d2 = r2.json()
        if r2.status_code == 200 and d2.get('success') and d2.get('session_token'):
            db_id = (d2.get('dados') or {}).get('db_id')
            if db_id:
                FB_TOKENS_POR_DB_ID[db_id] = d2['session_token']
            return d2.get('dados')
        return None
    except Exception as e:
        logger.error(f"⚠️ Falha ao fazer login no backend: {e}")
        return None

def _registrar_no_backend(db_id: str, dados: Dict) -> bool:
    """Cria a conta no Firebase (via Worker) e já guarda o token de sessão
    emitido, pra poder gravar o resto (ex: foto padrão) logo em seguida."""
    try:
        with _sessao_http() as s:
            r = s.post(f"{BACKEND_PAGAMENTOS_URL}/register", json={'db_id': db_id, 'dados': dados}, timeout=15)
        d = r.json()
        if r.status_code == 200 and d.get('success') and d.get('session_token'):
            FB_TOKENS_POR_DB_ID[db_id] = d['session_token']
            return True
        return False
    except Exception as e:
        logger.error(f"⚠️ Falha ao registrar conta no backend: {e}")
        return False

# ============================================================
# ID DO SERVIDOR
# ============================================================
def obter_id_servidor() -> str:
    try:
        with get_db_context() as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS config (chave TEXT PRIMARY KEY, valor TEXT, criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            cursor = conn.execute("SELECT valor FROM config WHERE chave='servidor_id'")
            result = cursor.fetchone()
            if result:
                return result[0]
            hostname = socket.gethostname()
            servidor_id = f"SERV_{hostname[:6].upper()}_{str(uuid.uuid4())[:6]}"
            conn.execute("INSERT INTO config (chave, valor) VALUES (?, ?)", ('servidor_id', servidor_id))
            conn.commit()
            return servidor_id
    except Exception as e:
        return f"SERV_{str(uuid.uuid4())[:12]}"

SERVIDOR_ID: str = obter_id_servidor()

# ============================================================
# SISTEMA DE PLANO SEGURO SINCRONIZADO
# ============================================================

class PlanoSincronizado:
    def __init__(self, db_id: str, chave_secreta: str):
        self.db_id = db_id
        self.chave_secreta = chave_secreta.encode()
        self.arquivo_token = os.path.join(APP_DATA_DIR, f'token_{db_id}.enc')
        self.arquivo_ultimo_timestamp = os.path.join(APP_DATA_DIR, f'ultimo_timestamp_{db_id}.json')
        
    def _derivar_chave(self) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.chave_secreta,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(self.db_id.encode()))
    
    def _criar_token(self, expira_em: str, plano_id: int) -> str:
        dados = {
            'db_id': self.db_id,
            'plano_id': plano_id,
            'expira_em': expira_em,
            'criado_em': datetime.now().isoformat(),
            'versao': '1.0',
            'token_id': str(uuid.uuid4())[:8]
        }
        dados_json = json.dumps(dados, sort_keys=True)
        assinatura = hmac.new(self.chave_secreta, dados_json.encode(), hashlib.sha256).hexdigest()
        token = {'dados': dados, 'assinatura': assinatura}
        fernet = Fernet(self._derivar_chave())
        token_criptografado = fernet.encrypt(json.dumps(token).encode())
        return base64.b64encode(token_criptografado).decode()
    
    def _verificar_token_v2(self, token_str: str) -> Optional[Dict]:
        """Verifica um token v2 (assinatura RSA - só o Worker consegue EMITIR,
        o pdv.py só consegue VERIFICAR, com a chave pública). Devolve None se
        não for um token v2 válido (nesse caso o chamador tenta o v1)."""
        try:
            pacote = json.loads(base64.b64decode(token_str.encode()).decode())
            if pacote.get('v') != 2:
                return None
            dados = {
                'db_id': pacote['db_id'], 'plano_id': pacote['plano_id'],
                'expira_em': pacote['expira_em'], 'criado_em': pacote['criado_em'],
                'token_id': pacote['token_id'],
            }
            # mensagem assinada é uma string simples (não JSON) de propósito:
            # evita qualquer divergência de formatação entre o Python (aqui) e
            # o JavaScript do Worker (que assina) - JSON "canônico" varia sutilmente
            # entre linguagens (espaços, ordem, escaping), string simples não.
            mensagem = f"{dados['db_id']}|{dados['plano_id']}|{dados['expira_em']}|{dados['token_id']}|{dados['criado_em']}|v2"
            assinatura = base64.b64decode(pacote['sig'])
            chave_publica = load_pem_public_key(CHAVE_PUBLICA_PLANO_PEM.encode())
            chave_publica.verify(
                assinatura, mensagem.encode(),
                rsa_padding.PSS(mgf=rsa_padding.MGF1(hashes.SHA256()), salt_length=32),
                hashes.SHA256(),
            )
            if dados['db_id'] != self.db_id:
                logger.warning(f"⚠️ Token v2 é de outra conta (esperado {self.db_id}, veio {dados['db_id']})")
                return None
            return dados
        except Exception:
            return None  # não é v2 (ou assinatura inválida) - tenta v1 no fallback

    def _verificar_token(self, token_criptografado: str) -> Optional[Dict]:
        # v2 primeiro (assinatura assimétrica - único formato que NOVOS tokens usam)
        dados_v2 = self._verificar_token_v2(token_criptografado)
        if dados_v2:
            return dados_v2
        # 🔧 fallback v1 (HMAC/Fernet simétrico): mantido SÓ pra não invalidar
        # tokens que já foram emitidos antes desta correção de segurança.
        # _criar_token (que gera v1) não é mais chamado pra tokens novos - ver
        # renovar_plano/_emitir_token_via_backend.
        try:
            fernet = Fernet(self._derivar_chave())
            token_bytes = base64.b64decode(token_criptografado.encode())
            token_json = fernet.decrypt(token_bytes).decode()
            token = json.loads(token_json)
            dados_json = json.dumps(token['dados'], sort_keys=True)
            assinatura_esperada = hmac.new(self.chave_secreta, dados_json.encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(assinatura_esperada, token['assinatura']):
                logger.warning(f"⚠️ Token adulterado para {self.db_id}")
                return None
            return token['dados']
        except Exception as e:
            logger.error(f"❌ Erro ao verificar token: {e}")
            return None

    def _emitir_token_via_backend(self, expira_em: str, plano_id: int, rota: str = "emitir_token", extra: Optional[Dict] = None) -> Optional[str]:
        """Único jeito SEGURO de obter um token novo: pede ao Worker (que tem a
        chave PRIVADA) pra assinar. Ver comentário em CHAVE_PUBLICA_PLANO_PEM."""
        try:
            corpo = {'db_id': self.db_id, 'plano_id': plano_id, 'expira_em': expira_em}
            if extra:
                corpo.update(extra)
            with _sessao_http() as s:
                r = s.post(f"{BACKEND_PAGAMENTOS_URL}/{rota}", json=corpo, timeout=10)
            if r.status_code == 200:
                d = r.json()
                if d.get('success') and d.get('token'):
                    return d['token']
            logger.warning(f"⚠️ Backend não emitiu token v2 ({rota}): HTTP {r.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ Falha ao pedir token v2 ao backend: {e}")
        return None
    
    def salvar_token_local(self, token_criptografado: str) -> bool:
        try:
            with open(self.arquivo_token, 'w') as f:
                f.write(token_criptografado)
            with open(self.arquivo_ultimo_timestamp, 'w') as f:
                json.dump({'ultimo_timestamp': datetime.now().isoformat(), 'ultima_verificacao': datetime.now().isoformat()}, f)
            logger.info(f"✅ Token salvo localmente para {self.db_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao salvar token local: {e}")
            return False
    
    def salvar_token_firebase(self, token_criptografado: str) -> bool:
        try:
            # PATCH: grava SÓ estes campos. Com o load-and-PUT anterior, se a
            # leitura do Firebase falhasse (oscilação de rede), o nó do usuário
            # era substituído só pelo token — apagando email, senha, produtos e
            # vendas. Era a causa dos "logins que sumiam".
            ok = salvar_campos_firebase(self.db_id, {
                'token_plano': token_criptografado,
                'token_atualizado_em': datetime.now().isoformat(),
            })
            if ok:
                logger.info(f"✅ Token salvo no Firebase para {self.db_id}")
            return ok
        except Exception as e:
            logger.error(f"❌ Erro ao salvar token no Firebase: {e}")
            return False
    
    def _agendar_sync_token_bg(self) -> None:
        """Dispara a sincronização do token do plano em SEGUNDO PLANO, no máximo
        uma vez a cada 5 minutos por conta. Assim nenhuma operação do caixa espera
        a rede, mas o plano continua sendo atualizado (renovação, corte de acesso)."""
        try:
            agora = _time.time()
            ultimo = _ULTIMO_SYNC_TOKEN.get(self.db_id, 0)
            if agora - ultimo < 300:  # 5 minutos
                return
            _ULTIMO_SYNC_TOKEN[self.db_id] = agora
            def _bg():
                try:
                    self.sincronizar_token()
                except Exception:
                    pass
            threading.Thread(target=_bg, daemon=True).start()
        except Exception:
            pass

    def sincronizar_token(self) -> Dict:
        resultado = {'success': True, 'token_atualizado': False, 'mensagem': ''}
        try:
            dados_fb = carregar_usuario_firebase(self.db_id, timeout=4)
            token_fb = dados_fb.get('token_plano') if dados_fb else None
            token_local = None
            if os.path.exists(self.arquivo_token):
                with open(self.arquivo_token, 'r') as f:
                    token_local = f.read().strip()
            if token_fb and token_local:
                dados_fb_token = self._verificar_token(token_fb)
                dados_local_token = self._verificar_token(token_local)
                if dados_fb_token and dados_local_token:
                    data_fb_obj = datetime.fromisoformat(dados_fb_token.get('criado_em', '2000-01-01'))
                    data_local_obj = datetime.fromisoformat(dados_local_token.get('criado_em', '2000-01-01'))
                    if data_fb_obj > data_local_obj:
                        self.salvar_token_local(token_fb)
                        resultado['token_atualizado'] = True
                        resultado['mensagem'] = 'Token atualizado do Firebase (mais novo)'
                    elif data_local_obj > data_fb_obj:
                        self.salvar_token_firebase(token_local)
                        resultado['mensagem'] = 'Token local enviado para Firebase (mais novo)'
            elif token_fb and not token_local:
                self.salvar_token_local(token_fb)
                resultado['token_atualizado'] = True
                resultado['mensagem'] = 'Token baixado do Firebase'
            elif token_local and not token_fb:
                self.salvar_token_firebase(token_local)
                resultado['mensagem'] = 'Token local enviado para Firebase'
            return resultado
        except Exception as e:
            logger.error(f"❌ Erro na sincronização do token: {e}")
            resultado['success'] = False
            resultado['mensagem'] = f'Erro: {str(e)}'
            return resultado
    
    def get_info_plano(self) -> Dict:
        try:
            # OFFLINE-FIRST: NÃO esperamos o Firebase aqui. Este método roda em
            # TODA operação (venda, exclusão, cadastro) por causa do @verificar_plano.
            # Se ele consultasse a rede, cada venda esperaria o Firebase e o caixa
            # travaria com internet ruim. O token local já é assinado e tem a data
            # de expiração, então basta lê-lo. A sincronização do token acontece
            # em SEGUNDO PLANO, no máximo a cada 5 minutos.
            self._agendar_sync_token_bg()
            if not os.path.exists(self.arquivo_token):
                return {'ativo': False, 'dias_restantes': 0, 'expirado': True, 'mensagem': 'Plano não encontrado'}
            with open(self.arquivo_token, 'r') as f:
                token_criptografado = f.read().strip()
            dados_token = self._verificar_token(token_criptografado)
            if not dados_token:
                return {'ativo': False, 'dias_restantes': 0, 'expirado': True, 'mensagem': 'Token inválido'}
            expira_em = dados_token.get('expira_em')
            if not expira_em:
                return {'ativo': False, 'dias_restantes': 0, 'expirado': True, 'mensagem': 'Sem data de expiração'}
            expira_date = datetime.fromisoformat(expira_em)
            if expira_date.tzinfo is not None:
                # 🔧 tokens novos (assinados pelo Worker, em JS) vêm com timezone
                # UTC ("...Z" -> new Date().toISOString()). O resto desta função
                # trabalha com datetime "naive" (hora local, sem fuso) - subtrair
                # aware de naive dá TypeError, que caía no except mais embaixo e
                # aparecia pro usuário como "plano expirado" na hora, mesmo
                # acabando de ganhar um token válido de 15 dias.
                expira_date = expira_date.astimezone().replace(tzinfo=None)
            agora = datetime.now()
            dias = (expira_date - agora).total_seconds() / 86400
            if os.path.exists(self.arquivo_ultimo_timestamp):
                with open(self.arquivo_ultimo_timestamp, 'r') as f:
                    ultimo_registro = json.load(f)
                    ultimo_timestamp = datetime.fromisoformat(ultimo_registro.get('ultimo_timestamp', ''))
                    if agora < ultimo_timestamp:
                        diferenca = (ultimo_timestamp - agora).total_seconds()
                        if diferenca > 60:
                            return {'ativo': False, 'dias_restantes': 0, 'expirado': True, 'mensagem': '⚠️ Data do sistema alterada'}
            if dias >= 0:
                with open(self.arquivo_ultimo_timestamp, 'w') as f:
                    json.dump({'ultimo_timestamp': agora.isoformat(), 'ultima_verificacao': agora.isoformat()}, f)
            return {
                'ativo': dias >= 0,
                'dias_restantes': max(0, dias),
                'expirado': dias < 0,
                'expira_em': expira_em,
                'plano_id': dados_token.get('plano_id', 1),
                'dias_para_expirar': dias,
                'mensagem': f"Plano {'ativo' if dias >= 0 else 'expirado'}"
            }
        except Exception as e:
            logger.error(f"❌ Erro ao obter info do plano: {e}")
            return {'ativo': False, 'dias_restantes': 0, 'expirado': True, 'mensagem': f'Erro: {str(e)}'}
    
    def renovar_plano(self, expira_em: str, plano_id: int, pix_id: Optional[str] = None) -> Dict:
        try:
            # 🔧 manda o pix_id (se tiver) pro Worker RE-CONFERIR o pagamento
            # direto com o Mercado Pago e derivar plano_id/expira_em sozinho a
            # partir do external_reference - NUNCA confiando no que o cliente
            # mandou. Sem isso, /emitir_token viraria só um novo jeito de
            # forjar plano (mudou de "assinar local" pra "chamar um endpoint
            # aberto"), sem resolver o problema de verdade.
            extra = {'pix_id': pix_id} if pix_id else None
            token = self._emitir_token_via_backend(expira_em, plano_id, rota='emitir_token', extra=extra)
            if not token:
                # 🔧 MODO INSEGURO (fallback): só cai aqui se o Worker estiver
                # fora do ar OU a rota /emitir_token ainda não tiver sido
                # publicada nele. Continua funcionando pro lojista não ficar
                # travado, mas ESTE token pode ser forjado por qualquer pessoa
                # com o código-fonte (é o problema original). Assim que o
                # Worker estiver no ar com /emitir_token, isto nunca mais roda.
                logger.error(f"⚠️ MODO INSEGURO: assinando token localmente para {self.db_id} (backend indisponível - publique /emitir_token no Worker)")
                token = self._criar_token(expira_em, plano_id)
            self.salvar_token_local(token)
            self.salvar_token_firebase(token)
            # PATCH: atualiza só o plano. Antes era load-and-PUT — se a rede
            # falhasse bem na hora do pagamento, o cliente pagava e PERDIA a
            # conta inteira (o nó era substituído só por estes 3 campos).
            salvar_campos_firebase(self.db_id, {
                'expira_em': expira_em,
                'plano': plano_id,
                'plano_atualizado_em': datetime.now().isoformat(),
            })
            logger.info(f"✅ Plano renovado para {self.db_id} até {expira_em}")
            return {'success': True, 'message': f'Plano renovado até {expira_em}', 'expira_em': expira_em}
        except Exception as e:
            logger.error(f"❌ Erro na renovação: {e}")
            return {'success': False, 'error': str(e)}

# ============================================================
# FUNÇÕES DE INTEGRAÇÃO DO PLANO
# ============================================================

def is_plano_ativo(db_id: str) -> bool:
    if not db_id:
        return False
    plano = PlanoSincronizado(db_id, CHAVE_SECRETA_PLANO)
    info = plano.get_info_plano()
    return info.get('ativo', False)

def get_dias_restantes(db_id: str) -> float:
    if not db_id:
        return 0
    try:
        plano = PlanoSincronizado(db_id, CHAVE_SECRETA_PLANO)
        info = plano.get_info_plano()
        return info.get('dias_restantes', 0)
    except:
        return 0

def get_info_plano_completa(db_id: str) -> Dict:
    if not db_id:
        return {'ativo': False, 'dias_restantes': 0, 'expirado': True}
    try:
        plano = PlanoSincronizado(db_id, CHAVE_SECRETA_PLANO)
        return plano.get_info_plano()
    except Exception as e:
        return {'ativo': False, 'dias_restantes': 0, 'expirado': True, 'erro': str(e)}

def get_plano_id_efetivo(db_id: str) -> int:
    """Resolve o plano_id usando o TOKEN LOCAL como fonte primária (funciona offline).
    Só consulta o Firebase como complemento se o token local não tiver a info."""
    # 1) Token local (offline-first)
    try:
        info = get_info_plano_completa(db_id)
        pid = info.get('plano_id')
        if pid:
            return int(pid)
    except Exception:
        pass
    # 2) Firebase (só se online e token não tinha)
    try:
        dados = carregar_usuario_firebase(db_id, timeout=3)
        if dados and dados.get('plano'):
            return int(dados.get('plano'))
    except Exception:
        pass
    # 3) Fallback seguro: plano básico
    return 1

def get_plano_efetivo(db_id: str) -> 'Plano':
    pid = get_plano_id_efetivo(db_id)
    return next((p for p in PLANOS if p.id == pid), PLANOS[0])

def precisa_aviso_renovacao(db_id: str) -> Tuple[bool, float]:
    if not db_id:
        return False, 0
    info = get_info_plano_completa(db_id)
    dias = info.get('dias_restantes', 0)
    if dias <= 3 and dias > 0:
        return True, dias
    return False, dias

def get_limite_produtos(db_id: str) -> int:
    try:
        plano = get_plano_efetivo(db_id)
        return plano.produtos if plano else 300
    except:
        return 300

def get_total_produtos(db_id: str) -> int:
    try:
        with get_db_context() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM produtos WHERE db_id=?", (db_id,))
            return cursor.fetchone()[0] or 0
    except:
        return 0

def get_usuarios_do_plano(db_id: str) -> List:
    try:
        with get_db_context() as conn:
            cursor = conn.execute("SELECT id FROM users WHERE db_id=?", (db_id,))
            return cursor.fetchall()
    except:
        return []

def pode_adicionar_produto(db_id: str, quantidade: int = 1) -> Tuple[bool, str]:
    limite = get_limite_produtos(db_id)
    atual = get_total_produtos(db_id)
    if limite == -1:
        return True, f"Ilimitado ({atual} atuais)"
    if atual + quantidade > limite:
        return False, f"Limite de {limite} produtos atingido! ({atual}/{limite})"
    return True, f"OK ({atual}/{limite})"

def get_permissoes(db_id: str) -> Dict:
    """Retorna as permissões do plano do usuário (offline-first via token local)"""
    _perm_padrao = {'clientes': False, 'dashboard': False, 'busca_estoque': False, 'margem': False, 'fiado': False, 'kit_combo': False}
    try:
        plano = get_plano_efetivo(db_id)
        return plano.permissoes if plano else _perm_padrao
    except:
        return _perm_padrao

# ============================================================
# FUNÇÃO DE SINCRONIZAÇÃO EM BACKGROUND
# ============================================================

def sincronizar_planos_periodicamente():
    while True:
        try:
            _time.sleep(3600)
            with get_db_context() as conn:
                usuarios = conn.execute("SELECT db_id FROM users").fetchall()
                for usuario in usuarios:
                    db_id = usuario[0]
                    if db_id:
                        try:
                            plano = PlanoSincronizado(db_id, CHAVE_SECRETA_PLANO)
                            resultado = plano.sincronizar_token()
                            if resultado.get('token_atualizado'):
                                logger.info(f"🔄 Token sincronizado em background para {db_id}")
                        except Exception as e:
                            logger.error(f"⚠️ Erro na sincronização background de {db_id}: {e}")
        except Exception as e:
            logger.error(f"❌ Erro no loop de sincronização: {e}")
            _time.sleep(300)

# ============================================================
# SINCRONIZAÇÃO INTELIGENTE
# ============================================================

def contar_dados_locais(db_id: str) -> Dict:
    try:
        with get_db_context() as conn:
            p = conn.execute("SELECT COUNT(*) FROM produtos WHERE db_id=?", (db_id,)).fetchone()[0]
            c = conn.execute("SELECT COUNT(*) FROM clientes WHERE db_id=?", (db_id,)).fetchone()[0]
            v = conn.execute("SELECT COUNT(*) FROM vendas WHERE db_id=?", (db_id,)).fetchone()[0]
            return {'produtos': p, 'clientes': c, 'vendas': v, 'total': p + c + v}
    except:
        return {'produtos': 0, 'clientes': 0, 'vendas': 0, 'total': 0}

def _normalizar_dados_firebase(dados_fb: Dict) -> Dict:
    if not dados_fb:
        return {'produtos': {}, 'clientes': {}, 'vendas': []}
    resultado = {}
    produtos = dados_fb.get('produtos')
    if produtos is None:
        resultado['produtos'] = {}
    elif isinstance(produtos, dict):
        resultado['produtos'] = produtos
    elif isinstance(produtos, list):
        novo_dict = {}
        for item in produtos:
            if isinstance(item, dict):
                codigo = item.get('codigo', str(uuid.uuid4())[:8])
                novo_dict[codigo] = item
        resultado['produtos'] = novo_dict
    else:
        resultado['produtos'] = {}
    clientes = dados_fb.get('clientes')
    if clientes is None:
        resultado['clientes'] = {}
    elif isinstance(clientes, dict):
        resultado['clientes'] = clientes
    elif isinstance(clientes, list):
        novo_dict = {}
        for item in clientes:
            if isinstance(item, dict):
                id_cli = item.get('id')
                if id_cli is None:
                    id_cli = str(uuid.uuid4())[:8]
                novo_dict[str(id_cli)] = item
        resultado['clientes'] = novo_dict
    else:
        resultado['clientes'] = {}
    vendas = dados_fb.get('vendas')
    if vendas is None:
        resultado['vendas'] = []
    elif isinstance(vendas, list):
        resultado['vendas'] = vendas
    elif isinstance(vendas, dict):
        resultado['vendas'] = list(vendas.values())
    else:
        resultado['vendas'] = []
    # Preserva os campos que o merge também usa (senão eram descartados aqui):
    resultado['kits'] = dados_fb.get('kits') or {}
    resultado['exclusoes'] = dados_fb.get('exclusoes') or {}
    resultado['estoque_mov'] = dados_fb.get('estoque_mov') or {}
    resultado['fiado_mov'] = dados_fb.get('fiado_mov') or {}
    # mantém também caixa/loja se existirem (não atrapalham o merge)
    for extra in ('caixa', 'nome_loja', 'cnpj', 'cnpj_dados'):
        if extra in dados_fb:
            resultado[extra] = dados_fb[extra]
    return resultado

def contar_dados_firebase(dados_fb: Dict) -> Dict:
    if not dados_fb:
        return {'produtos': 0, 'clientes': 0, 'vendas': 0, 'total': 0}
    normalizado = _normalizar_dados_firebase(dados_fb)
    p = len(normalizado.get('produtos') or {})
    c = len(normalizado.get('clientes') or {})
    v = len(normalizado.get('vendas') or [])
    return {'produtos': p, 'clientes': c, 'vendas': v, 'total': p + c + v}

def _garantir_conta_no_firebase(db_id: str) -> None:
    """Se a conta existe no banco LOCAL mas não no Firebase (ex.: foi criada
    offline, ou o envio inicial falhou), sobe ela agora — com email, senha e
    plano. Sem isso, a conta nunca chega ao Firebase e o login em OUTRO PC falha
    com 'conta não encontrada', mesmo a internet já tendo voltado."""
    try:
        if not firebase_online():
            return
        ja_no_fb = carregar_usuario_firebase(db_id)
        # Consideramos "presente" só se tiver email E senha (nó completo)
        if ja_no_fb and ja_no_fb.get('email') and ja_no_fb.get('senha'):
            return
        # Busca os dados da conta no banco local
        with get_db_context() as conn:
            row = conn.execute(
                "SELECT nome, email, senha, cargo, servidor_id, nome_loja, cnpj, cnpj_dados "
                "FROM users WHERE db_id=? LIMIT 1", (db_id,)).fetchone()
        if not row or not row[1] or not row[2]:
            return  # sem email/senha local não há o que subir
        try:
            cnpj_dados = json.loads(row[7]) if row[7] else {}
        except Exception:
            cnpj_dados = {}
        # Preserva o que já existir no Firebase (plano/token/expira) e completa o resto
        base = ja_no_fb if isinstance(ja_no_fb, dict) else {}
        base.update({
            'db_id': db_id, 'nome': row[0], 'email': row[1], 'senha': row[2],
            'cargo': row[3] or 'Gerente', 'servidor_id': row[4] or SERVIDOR_ID,
            'nome_loja': row[5] or 'Minha Loja', 'cnpj': row[6] or '', 'cnpj_dados': cnpj_dados,
        })
        if not base.get('token_plano') or not base.get('expira_em') or base.get('plano') is None:
            expira_em = base.get('expira_em') or (datetime.now() + timedelta(days=15)).isoformat()
            plano_id = base.get('plano', 5) if base.get('plano') is not None else 5
            try:
                pl = PlanoSincronizado(db_id, CHAVE_SECRETA_PLANO)
                token_reparo = pl._emitir_token_via_backend(expira_em, plano_id, rota='emitir_trial')
                base['token_plano'] = token_reparo or pl._criar_token(expira_em, plano_id)
                base['token_atualizado_em'] = get_timestamp()
            except Exception:
                pass
            base['expira_em'] = expira_em
            base['plano'] = plano_id
        salvar_usuario_firebase(db_id, base)
        logger.info(f"🔼 Conta que estava só local subiu para o Firebase: {db_id}")
    except Exception as e:
        logger.warning(f"⚠️ Não consegui garantir a conta no Firebase: {e}")


def sincronizar_dados(db_id: str) -> Dict:
    resultado = {'success': True, 'direcao': 'nenhuma', 'produtos_adicionados': 0, 'clientes_adicionados': 0, 'vendas_adicionadas': 0, 'erros': []}
    try:
        # ANTES de tudo: se a conta só existe local (criada offline), sobe ela.
        # Isso conserta o login em outro PC ("conta não encontrada").
        _garantir_conta_no_firebase(db_id)
        dados_firebase = None
        try:
            dados_firebase = carregar_usuario_firebase(db_id)
        except Exception as e:
            logger.error(f"⚠️ Erro ao carregar Firebase: {e}")
        dados_firebase = _normalizar_dados_firebase(dados_firebase)
        local_count = contar_dados_locais(db_id)
        firebase_count = contar_dados_firebase(dados_firebase)
        logger.info(f"📊 Local: {local_count['total']} | Firebase: {firebase_count['total']}")
        if not dados_firebase or firebase_count['total'] == 0:
            logger.info("🔼 Firebase vazio → subindo dados locais")
            enviou = enviar_para_firebase(db_id)
            resultado['direcao'] = 'local_para_firebase'
            resultado['success'] = enviou
            return resultado
        if local_count['total'] == 0:
            logger.info("🔽 Local vazio → baixando dados do Firebase")
            _baixar_firebase_para_local(db_id, dados_firebase, resultado)
            resultado['direcao'] = 'firebase_para_local'
            return resultado
        logger.info("🔄 Merge bidirecional")
        _merge_bidirecional_sem_duplicar(db_id, dados_firebase, resultado)
        resultado['direcao'] = 'merge'
        enviar_para_firebase(db_id)
        return resultado
    except Exception as e:
        logger.error(f"❌ Erro na sincronização: {e}")
        resultado['success'] = False
        resultado['erros'].append(str(e))
        return resultado

def _aplicar_tombstones_firebase(db_id: str, dados_firebase: Dict) -> None:
    """Aplica no banco local as exclusões (tombstones) registradas por QUALQUER dispositivo no Firebase.
    Isso impede que um cliente/kit/produto excluído em um aparelho volte a partir de outro."""
    exclusoes_fb = dados_firebase.get('exclusoes') or {}
    if not exclusoes_fb:
        return
    try:
        with get_db_context() as conn:
            for _, exc in exclusoes_fb.items():
                tipo = exc.get('tipo')
                item_id = str(exc.get('item_id', ''))
                excluido_em = exc.get('excluido_em', get_timestamp())
                if not tipo or not item_id:
                    continue
                # Registra o tombstone localmente (se ainda não existe)
                conn.execute("INSERT OR IGNORE INTO exclusoes (tipo, item_id, db_id, excluido_em) VALUES (?, ?, ?, ?)",
                    (tipo, item_id, db_id, excluido_em))
                # Remove o item do banco local, se ele existir
                if tipo == 'cliente':
                    if item_id.isdigit():
                        # Tombstone ANTIGO (por id). Não aplicamos: o id é local,
                        # apagaríamos outro cliente neste aparelho.
                        logger.info(f"ℹ️ Ignorando exclusão antiga por id ({item_id}) — hoje excluímos por nome")
                    else:
                        # Só apaga se o cliente local for ANTERIOR à exclusão.
                        # Se alguém recadastrou esse nome depois, ele fica.
                        row = conn.execute("SELECT ultima_atualizacao FROM clientes WHERE nome=? AND db_id=?",
                            (item_id, db_id)).fetchone()
                        if row and (row[0] or '') > excluido_em:
                            pass  # cliente recriado depois da exclusão: preservar
                        else:
                            conn.execute("DELETE FROM clientes WHERE nome=? AND db_id=?", (item_id, db_id))
                        # os fatos anteriores à exclusão nunca voltam
                        conn.execute("DELETE FROM fiado_mov WHERE cliente_nome=? AND db_id=? AND criado_em<=?",
                            (item_id, db_id, excluido_em))
                elif tipo == 'produto':
                    conn.execute("DELETE FROM produtos WHERE codigo=? AND db_id=?", (item_id, db_id))
                elif tipo == 'kit':
                    conn.execute("DELETE FROM kits WHERE id=? AND db_id=?", (item_id, db_id))
                elif tipo == 'venda':
                    conn.execute("DELETE FROM vendas WHERE id=? AND db_id=?", (item_id, db_id))
    except Exception as e:
        logger.error(f"⚠️ Erro ao aplicar tombstones do Firebase: {e}")

def _baixar_firebase_para_local(db_id: str, dados_firebase: Dict, resultado: Dict) -> None:
    _aplicar_tombstones_firebase(db_id, dados_firebase)
    with get_db_context() as conn:
        # Produtos EXCLUÍDOS (tombstones) — não trazer de volta do Firebase
        cur_exc_prod = conn.execute("SELECT item_id FROM exclusoes WHERE tipo='produto' AND db_id=?", (db_id,))
        produtos_excluidos_ids = {str(r[0]) for r in cur_exc_prod.fetchall()}
        for codigo, dados_prod in (dados_firebase.get('produtos') or {}).items():
            try:
                if str(codigo) in produtos_excluidos_ids:
                    continue  # apagado de propósito — não ressuscita
                conn.execute("""INSERT OR IGNORE INTO produtos (codigo, nome, preco, custo, margem, estoque, categoria, db_id, ultima_atualizacao)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (codigo, dados_prod.get('nome', ''), dados_prod.get('preco', 0),
                    dados_prod.get('custo', 0), dados_prod.get('margem', 0), dados_prod.get('estoque', 0),
                    dados_prod.get('categoria', 'Geral'), db_id, dados_prod.get('ultima_atualizacao', get_timestamp())))
                resultado['produtos_adicionados'] += 1
            except Exception as e:
                logger.error(f"⚠️ Erro ao inserir produto {codigo}: {e}")
        # Lista de clientes excluídos (tombstones) para NÃO ressuscitá-los no merge
        cur_exc_cli = conn.execute("SELECT item_id FROM exclusoes WHERE tipo='cliente' AND db_id=?", (db_id,))
        clientes_excluidos_ids = {str(r[0]) for r in cur_exc_cli.fetchall()}
        for _chave, dados_cli in (dados_firebase.get('clientes') or {}).items():
            try:
                nome_c = (dados_cli.get('nome') or '').strip()
                if not nome_c:
                    continue
                # Excluído? não traz de volta (identidade é o NOME, não o id local)
                if nome_c in clientes_excluidos_ids:
                    continue
                # Evita duplicar
                dup = conn.execute("SELECT id FROM clientes WHERE nome=? AND db_id=?", (nome_c, db_id)).fetchone()
                if dup:
                    continue
                conn.execute("""INSERT INTO clientes (nome, telefone, email, divida, db_id, ultima_atualizacao)
                    VALUES (?, ?, ?, ?, ?, ?)""", (nome_c, dados_cli.get('telefone', ''),
                    dados_cli.get('email', ''), 0, db_id, dados_cli.get('ultima_atualizacao', get_timestamp())))
                resultado['clientes_adicionados'] += 1
            except Exception as e:
                logger.error(f"⚠️ Erro ao inserir cliente {dados_cli.get('nome')}: {e}")
        cur_exc_v = conn.execute("SELECT item_id FROM exclusoes WHERE tipo='venda' AND db_id=?", (db_id,))
        vendas_excluidas = {r[0] for r in cur_exc_v.fetchall()}
        for venda_fb in (dados_firebase.get('vendas') or []):
            venda_id = venda_fb.get('id')
            if not venda_id:
                continue
            if str(venda_id) in vendas_excluidas:
                continue
            try:
                conn.execute("""INSERT OR IGNORE INTO vendas (id, data_hora, subtotal, desconto, total, lucro_total, metodo, itens, cliente, usuario_id, db_id, recebido, troco)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (venda_id, venda_fb.get('data_hora', get_timestamp()),
                    venda_fb.get('subtotal', 0), venda_fb.get('desconto', 0), venda_fb.get('total', 0),
                    venda_fb.get('lucro_total', 0), venda_fb.get('metodo', 'Dinheiro'),
                    json.dumps(venda_fb.get('itens', [])), venda_fb.get('cliente', ''),
                    venda_fb.get('usuario_id', ''), db_id, venda_fb.get('recebido', 0), venda_fb.get('troco', 0)))
                resultado['vendas_adicionadas'] += 1
            except Exception as e:
                logger.error(f"⚠️ Erro ao inserir venda {venda_id}: {e}")

        # FATOS (fiado e estoque): precisam vir junto, senão este dispositivo
        # ficaria só com o número final e a migração criaria um "saldo inicial"
        # que SOMARIA em cima dos fatos reais — dobrando a dívida/estoque.
        cur_exc_f = conn.execute("SELECT item_id, excluido_em FROM exclusoes WHERE tipo='cliente' AND db_id=?", (db_id,))
        cortes_cli = {str(r[0]): (r[1] or '') for r in cur_exc_f.fetchall()}
        for mov_id, m in (dados_firebase.get('fiado_mov') or {}).items():
            corte = cortes_cli.get(str(m.get('cliente_nome')))
            if corte and str(m.get('criado_em', '')) <= corte:
                continue  # cliente foi excluído: não traz a dívida antiga de volta
            try:
                conn.execute("""INSERT OR IGNORE INTO fiado_mov (id, cliente_nome, delta, tipo, origem, db_id, criado_em)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""", (str(mov_id), m.get('cliente_nome'), float(m.get('delta', 0)),
                    m.get('tipo', 'fiado'), m.get('origem', ''), db_id, m.get('criado_em', get_timestamp())))
            except Exception as e:
                logger.error(f"⚠️ Erro ao inserir mov fiado {mov_id}: {e}")
        for mov_id, m in (dados_firebase.get('estoque_mov') or {}).items():
            try:
                conn.execute("""INSERT OR IGNORE INTO estoque_mov (id, codigo, delta, tipo, origem, db_id, criado_em)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""", (str(mov_id), m.get('codigo'), int(m.get('delta', 0)),
                    m.get('tipo', 'saida'), m.get('origem', ''), db_id, m.get('criado_em', get_timestamp())))
            except Exception as e:
                logger.error(f"⚠️ Erro ao inserir mov estoque {mov_id}: {e}")
        # valores derivados: recalcula a partir dos fatos recém-baixados
        for (nome_c,) in conn.execute("SELECT DISTINCT cliente_nome FROM fiado_mov WHERE db_id=?", (db_id,)).fetchall():
            if nome_c:
                v = conn.execute("SELECT COALESCE(SUM(delta),0) FROM fiado_mov WHERE cliente_nome=? AND db_id=?",
                    (nome_c, db_id)).fetchone()[0]
                conn.execute("UPDATE clientes SET divida=? WHERE nome=? AND db_id=?",
                    (max(0.0, round(float(v), 2)), nome_c, db_id))
        # Garante que todo produto tenha fatos coerentes com sua coluna estoque.
        # Sem isso, um produto vindo de outro dispositivo (coluna preenchida, mas
        # sem fatos) ia para negativo na primeira venda.
        reconciliar_fatos_estoque(conn, db_id)
        for (cod,) in conn.execute("SELECT DISTINCT codigo FROM estoque_mov WHERE db_id=?", (db_id,)).fetchall():
            if cod:
                v = conn.execute("SELECT COALESCE(SUM(delta),0) FROM estoque_mov WHERE codigo=? AND db_id=?",
                    (cod, db_id)).fetchone()[0]
                conn.execute("UPDATE produtos SET estoque=? WHERE codigo=? AND db_id=?", (int(v), cod, db_id))
        conn.commit()

def _merge_bidirecional_sem_duplicar(db_id: str, dados_firebase: Dict, resultado: Dict) -> None:
    # Primeiro aplica as exclusões de todos os dispositivos (impede itens excluídos de voltarem)
    _aplicar_tombstones_firebase(db_id, dados_firebase)
    with get_db_context() as conn:
        cursor = conn.execute("SELECT codigo FROM produtos WHERE db_id=?", (db_id,))
        codigos_locais = {row[0] for row in cursor.fetchall()}
        # Lista de produtos EXCLUÍDOS (tombstones) para NÃO ressuscitá-los.
        # Sem isso, o produto apagado voltava do Firebase no merge (era o bug
        # do "apago um e o outro volta").
        cursor = conn.execute("SELECT item_id FROM exclusoes WHERE tipo='produto' AND db_id=?", (db_id,))
        codigos_excluidos = {row[0] for row in cursor.fetchall()}
        for codigo, dados_prod in (dados_firebase.get('produtos') or {}).items():
            if str(codigo) in codigos_excluidos:
                continue  # foi apagado de propósito — não traz de volta
            if codigo not in codigos_locais:
                try:
                    conn.execute("""INSERT INTO produtos (codigo, nome, preco, custo, margem, estoque, categoria, db_id, ultima_atualizacao)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (codigo, dados_prod.get('nome', ''), dados_prod.get('preco', 0),
                        dados_prod.get('custo', 0), dados_prod.get('margem', 0), dados_prod.get('estoque', 0),
                        dados_prod.get('categoria', 'Geral'), db_id, dados_prod.get('ultima_atualizacao', get_timestamp())))
                    resultado['produtos_adicionados'] += 1
                except Exception as e:
                    logger.error(f"⚠️ Erro no merge produto {codigo}: {e}")
            else:
                firebase_ts = dados_prod.get('ultima_atualizacao')
                if firebase_ts:
                    cursor2 = conn.execute("SELECT ultima_atualizacao FROM produtos WHERE codigo=? AND db_id=?", (codigo, db_id))
                    row = cursor2.fetchone()
                    local_ts = row[0] if row else None
                    if not local_ts or firebase_ts > local_ts:
                        try:
                            conn.execute("""UPDATE produtos SET nome=?, preco=?, custo=?, margem=?, estoque=?, categoria=?, ultima_atualizacao=?
                                WHERE codigo=? AND db_id=?""", (dados_prod.get('nome', ''), dados_prod.get('preco', 0),
                                dados_prod.get('custo', 0), dados_prod.get('margem', 0), dados_prod.get('estoque', 0),
                                dados_prod.get('categoria', 'Geral'), firebase_ts, codigo, db_id))
                        except Exception as e:
                            logger.error(f"⚠️ Erro ao atualizar produto {codigo}: {e}")
        # CLIENTES: casamos pelo NOME, nunca pelo id.
        # O id é INTEGER AUTOINCREMENT — LOCAL de cada aparelho. O "id 1" do PC
        # pode ser outra pessoa no celular. Casar por id fazia um cliente
        # sobrescrever o outro (o João virava Maria, e a dívida trocava de dono).
        # O nome já é a chave do negócio: vendas, fatos de fiado e exclusões
        # todos usam o nome, e o sistema impede nomes duplicados.
        cur_cn = conn.execute("SELECT item_id, excluido_em FROM exclusoes WHERE tipo='cliente' AND db_id=?", (db_id,))
        cortes_nome = {str(r[0]): (r[1] or '') for r in cur_cn.fetchall()}
        for _chave_fb, dados_cli in (dados_firebase.get('clientes') or {}).items():
            nome_cliente = (dados_cli.get('nome') or '').strip()
            if not nome_cliente:
                continue
            corte_c = cortes_nome.get(nome_cliente)
            if corte_c and str(dados_cli.get('ultima_atualizacao', '')) <= corte_c:
                continue  # cliente foi excluído; a versão do Firebase é antiga
            firebase_ts = dados_cli.get('ultima_atualizacao')
            local = conn.execute("SELECT id, ultima_atualizacao FROM clientes WHERE nome=? AND db_id=?",
                (nome_cliente, db_id)).fetchone()
            if local:
                local_ts = local[1]
                if firebase_ts and local_ts and firebase_ts <= local_ts:
                    continue  # o local é mais novo: mantém
                try:
                    # NÃO atualizamos 'divida': ela é DERIVADA dos fatos (fiado_mov).
                    conn.execute("""UPDATE clientes SET telefone=?, email=?, ultima_atualizacao=?
                        WHERE id=? AND db_id=?""", (dados_cli.get('telefone', ''),
                        dados_cli.get('email', ''), firebase_ts or get_timestamp(), local[0], db_id))
                except Exception as e:
                    logger.error(f"⚠️ Erro ao atualizar cliente {nome_cliente}: {e}")
            else:
                try:
                    # id local novo (autoincrement); a identidade é o nome
                    conn.execute("""INSERT INTO clientes (nome, telefone, email, divida, db_id, ultima_atualizacao)
                        VALUES (?, ?, ?, ?, ?, ?)""", (nome_cliente, dados_cli.get('telefone', ''),
                        dados_cli.get('email', ''), 0, db_id, dados_cli.get('ultima_atualizacao', get_timestamp())))
                    resultado['clientes_adicionados'] += 1
                except Exception as e:
                    logger.error(f"⚠️ Erro ao inserir cliente {nome_cliente}: {e}")
        cursor = conn.execute("SELECT id FROM vendas WHERE db_id=?", (db_id,))
        ids_vendas_locais = {row[0] for row in cursor.fetchall()}
        cur_exc_v2 = conn.execute("SELECT item_id FROM exclusoes WHERE tipo='venda' AND db_id=?", (db_id,))
        vendas_excluidas2 = {r[0] for r in cur_exc_v2.fetchall()}
        for venda_fb in (dados_firebase.get('vendas') or []):
            venda_id = venda_fb.get('id')
            if not venda_id or venda_id in ids_vendas_locais:
                continue
            if str(venda_id) in vendas_excluidas2:
                continue
            try:
                conn.execute("""INSERT INTO vendas (id, data_hora, subtotal, desconto, total, lucro_total, metodo, itens, cliente, usuario_id, db_id, recebido, troco)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (venda_id, venda_fb.get('data_hora', get_timestamp()),
                    venda_fb.get('subtotal', 0), venda_fb.get('desconto', 0), venda_fb.get('total', 0),
                    venda_fb.get('lucro_total', 0), venda_fb.get('metodo', 'Dinheiro'),
                    json.dumps(venda_fb.get('itens', [])), venda_fb.get('cliente', ''),
                    venda_fb.get('usuario_id', ''), db_id, venda_fb.get('recebido', 0), venda_fb.get('troco', 0)))
                resultado['vendas_adicionadas'] += 1
            except Exception as e:
                logger.error(f"⚠️ Erro no merge venda {venda_id}: {e}")

        # === KITS / COMBOS ===
        cursor = conn.execute("SELECT id FROM kits WHERE db_id=?", (db_id,))
        ids_kits_locais = {row[0] for row in cursor.fetchall()}
        cursor = conn.execute("SELECT item_id FROM exclusoes WHERE tipo='kit' AND db_id=?", (db_id,))
        ids_kits_excluidos = {row[0] for row in cursor.fetchall()}
        for kit_id, dados_kit in (dados_firebase.get('kits') or {}).items():
            if str(kit_id) in ids_kits_excluidos:
                continue
            itens_kit = dados_kit.get('itens', [])
            itens_json = json.dumps(itens_kit, ensure_ascii=False) if not isinstance(itens_kit, str) else itens_kit
            if kit_id in ids_kits_locais:
                firebase_ts = dados_kit.get('ultima_atualizacao')
                cursor2 = conn.execute("SELECT ultima_atualizacao, itens FROM kits WHERE id=? AND db_id=?", (kit_id, db_id))
                row = cursor2.fetchone()
                local_ts = row[0] if row else None
                local_itens = row[1] if row else '[]'
                # Não sobrescreve um kit local que TEM itens por uma versão do Firebase SEM itens
                fb_vazio = (not itens_kit) or (isinstance(itens_kit, list) and len(itens_kit) == 0)
                local_tem = local_itens and local_itens not in ('[]', '', None)
                if fb_vazio and local_tem:
                    continue
                if firebase_ts and local_ts and str(firebase_ts) <= str(local_ts):
                    continue
                try:
                    conn.execute("""UPDATE kits SET nome=?, preco=?, itens=?, ativo=?, ultima_atualizacao=?
                        WHERE id=? AND db_id=?""", (dados_kit.get('nome', ''), dados_kit.get('preco', 0),
                        itens_json, 1 if dados_kit.get('ativo', True) else 0, firebase_ts or get_timestamp(), kit_id, db_id))
                except Exception as e:
                    logger.error(f"⚠️ Erro ao atualizar kit {kit_id}: {e}")
            else:
                try:
                    conn.execute("""INSERT INTO kits (id, nome, preco, itens, db_id, ativo, ultima_atualizacao)
                        VALUES (?, ?, ?, ?, ?, ?, ?)""", (kit_id, dados_kit.get('nome', ''), dados_kit.get('preco', 0),
                        itens_json, db_id, 1 if dados_kit.get('ativo', True) else 0, dados_kit.get('ultima_atualizacao', get_timestamp())))
                except Exception as e:
                    logger.error(f"⚠️ Erro ao inserir kit {kit_id}: {e}")

        # MOVIMENTAÇÕES DE FIADO (fatos): insere as novas por ID único.
        movs_fiado = dados_firebase.get('fiado_mov') or {}
        clientes_afetados = set()
        # clientes excluídos: {nome: hora_da_exclusao}. Fatos criados ANTES dessa
        # hora não voltam (senão a dívida de um cliente apagado ressuscitaria).
        cur_exc = conn.execute("SELECT item_id, excluido_em FROM exclusoes WHERE tipo='cliente' AND db_id=?", (db_id,))
        cortes_cliente = {str(r[0]): (r[1] or '') for r in cur_exc.fetchall()}
        if movs_fiado:
            cursor = conn.execute("SELECT id FROM fiado_mov WHERE db_id=?", (db_id,))
            ids_f_locais = {row[0] for row in cursor.fetchall()}
            for mov_id, m in movs_fiado.items():
                if str(mov_id) in ids_f_locais:
                    continue
                corte = cortes_cliente.get(str(m.get('cliente_nome')))
                if corte and str(m.get('criado_em', '')) <= corte:
                    continue  # fato anterior à exclusão do cliente
                try:
                    conn.execute("""INSERT OR IGNORE INTO fiado_mov (id, cliente_nome, delta, tipo, origem, db_id, criado_em)
                        VALUES (?, ?, ?, ?, ?, ?, ?)""", (str(mov_id), m.get('cliente_nome'), float(m.get('delta', 0)),
                        m.get('tipo', 'fiado'), m.get('origem', ''), db_id, m.get('criado_em', get_timestamp())))
                    clientes_afetados.add(m.get('cliente_nome'))
                except Exception as e:
                    logger.error(f"⚠️ Erro ao inserir mov fiado {mov_id}: {e}")
        # a dívida é DERIVADA dos fatos: recalcula para todos os clientes com fatos
        for nome_c in conn.execute("SELECT DISTINCT cliente_nome FROM fiado_mov WHERE db_id=?", (db_id,)).fetchall():
            if nome_c[0]:
                v = conn.execute("SELECT COALESCE(SUM(delta),0) FROM fiado_mov WHERE cliente_nome=? AND db_id=?",
                    (nome_c[0], db_id)).fetchone()[0]
                conn.execute("UPDATE clientes SET divida=? WHERE nome=? AND db_id=?",
                    (max(0.0, round(float(v), 2)), nome_c[0], db_id))

        # MOVIMENTAÇÕES DE ESTOQUE (fatos): insere as novas por ID único (nunca
        # duplica, nunca sobrescreve). Depois recalcula o estoque dos produtos
        # afetados pela SOMA dos fatos — fica igual em todos os dispositivos.
        movs_fb = dados_firebase.get('estoque_mov') or {}
        codigos_afetados = set()
        if movs_fb:
            cursor = conn.execute("SELECT id FROM estoque_mov WHERE db_id=?", (db_id,))
            ids_locais = {row[0] for row in cursor.fetchall()}
            for mov_id, m in movs_fb.items():
                if str(mov_id) in ids_locais:
                    continue  # já temos esse fato
                try:
                    conn.execute("""INSERT OR IGNORE INTO estoque_mov (id, codigo, delta, tipo, origem, db_id, criado_em)
                        VALUES (?, ?, ?, ?, ?, ?, ?)""", (str(mov_id), m.get('codigo'), int(m.get('delta', 0)),
                        m.get('tipo', 'saida'), m.get('origem', ''), db_id, m.get('criado_em', get_timestamp())))
                    codigos_afetados.add(m.get('codigo'))
                except Exception as e:
                    logger.error(f"⚠️ Erro ao inserir mov estoque {mov_id}: {e}")
        # recalcula a coluna estoque dos produtos que receberam fatos novos
        for cod in codigos_afetados:
            if cod:
                valor = conn.execute("SELECT COALESCE(SUM(delta),0) FROM estoque_mov WHERE codigo=? AND db_id=?",
                    (str(cod), db_id)).fetchone()[0]
                conn.execute("UPDATE produtos SET estoque=? WHERE codigo=? AND db_id=?", (int(valor), str(cod), db_id))

        conn.commit()

def enviar_para_firebase(db_id: str) -> bool:
    try:
        dados_firebase = carregar_usuario_firebase(db_id)
        if dados_firebase is None:
            # Atenção: None é ambíguo — pode ser "a rede caiu" OU "o nó ainda não
            # existe" (conta recém-criada). Se for rede fora e mesmo assim
            # fizéssemos o PUT abaixo, o nó seria SUBSTITUÍDO só pelos dados
            # locais, apagando email, senha, plano e token. Então checamos.
            if not firebase_online():
                logger.warning("⚠️ Sem conexão; envio adiado (evita apagar a conta)")
                return False
            # Online, mas o nó não existe: seguro criar do zero.
            dados_firebase = {}
        with get_db_context() as conn:
            cursor = conn.execute("""SELECT codigo, nome, preco, custo, margem, estoque, categoria, ultima_atualizacao FROM produtos WHERE db_id=?""", (db_id,))
            produtos = {}
            for row in cursor.fetchall():
                produtos[row[0]] = {'nome': row[1], 'preco': row[2], 'custo': row[3] or 0, 'margem': row[4] or 0,
                    'estoque': row[5], 'categoria': row[6] or 'Geral', 'ultima_atualizacao': row[7] or get_timestamp()}
            dados_firebase['produtos'] = produtos
            cursor = conn.execute("""SELECT id, nome, telefone, email, divida, ultima_atualizacao FROM clientes WHERE db_id=?""", (db_id,))
            clientes = {}
            for row in cursor.fetchall():
                # chave estável derivada do NOME: o id é local e colidiria entre aparelhos
                clientes[chave_cliente(db_id, row[1])] = {'nome': row[1], 'telefone': row[2] or '', 'email': row[3] or '', 'divida': row[4] or 0, 'ultima_atualizacao': row[5] or get_timestamp()}
            dados_firebase['clientes'] = clientes
            cursor = conn.execute("""SELECT id, data_hora, subtotal, desconto, total, lucro_total, metodo, itens, cliente, usuario_id, recebido, troco
                FROM vendas WHERE db_id=?""", (db_id,))
            vendas = []
            for row in cursor.fetchall():
                vendas.append({'id': row[0], 'data_hora': row[1], 'subtotal': row[2], 'desconto': row[3], 'total': row[4],
                    'lucro_total': row[5] or 0, 'metodo': row[6], 'itens': json.loads(row[7]) if row[7] else [],
                    'cliente': row[8] or '', 'usuario_id': row[9] or '', 'recebido': row[10] or 0, 'troco': row[11] or 0})
            dados_firebase['vendas'] = vendas
            # Tombstones (exclusões) — compartilhados para nenhum dispositivo ressuscitar o que foi excluído
            cursor = conn.execute("SELECT tipo, item_id, excluido_em FROM exclusoes WHERE db_id=?", (db_id,))
            exclusoes = {}
            for row in cursor.fetchall():
                chave = f"{row[0]}_{row[1]}"  # ex: cliente_5, kit_abc, produto_789
                exclusoes[chave] = {'tipo': row[0], 'item_id': row[1], 'excluido_em': row[2] or get_timestamp()}
            dados_firebase['exclusoes'] = exclusoes
            cursor = conn.execute("""SELECT usuario_id, valor_abertura, data_abertura, data_fechamento, total, status
                FROM caixa WHERE db_id=? ORDER BY id DESC LIMIT 1""", (db_id,))
            result = cursor.fetchone()
            if result:
                dados_firebase['caixa'] = {'usuario_id': result[0], 'valor_abertura': result[1], 'data_abertura': result[2],
                    'data_fechamento': result[3], 'total': result[4] or 0, 'status': result[5]}
            cursor = conn.execute("SELECT nome_loja, cnpj, cnpj_dados, bg_vendas_img, bg_vendas_opacidade FROM users WHERE db_id=? LIMIT 1", (db_id,))
            loja = cursor.fetchone()
            if loja:
                dados_firebase['nome_loja'] = loja[0] or ''
                dados_firebase['cnpj'] = loja[1] or ''
                try:
                    dados_firebase['cnpj_dados'] = json.loads(loja[2]) if loja[2] else {}
                except:
                    dados_firebase['cnpj_dados'] = {}
                # NÃO subimos bg_vendas_img/opacidade/escala aqui. Essas preferências
                # têm seu próprio mecanismo com timestamp (salvar_preferencia_firebase),
                # senão um dispositivo sem foto apagaria a foto salva por outro.
            cursor = conn.execute("SELECT id, nome, preco, itens, ativo, ultima_atualizacao FROM kits WHERE db_id=?", (db_id,))
            kits = {}
            for row in cursor.fetchall():
                try:
                    itens_kit = json.loads(row[3]) if row[3] else []
                except:
                    itens_kit = []
                kits[str(row[0])] = {'nome': row[1], 'preco': row[2] or 0, 'itens': itens_kit,
                    'ativo': bool(row[4]), 'ultima_atualizacao': row[5] or get_timestamp()}
            dados_firebase['kits'] = kits
            # MOVIMENTAÇÕES DE ESTOQUE (fatos). Sobem como as vendas: cada uma com
            # ID único, só adiciona, nunca sobrescreve. Assim o estoque calculado
            # a partir delas fica igual em todos os dispositivos.
            cursor = conn.execute("SELECT id, cliente_nome, delta, tipo, origem, criado_em FROM fiado_mov WHERE db_id=?", (db_id,))
            fmovs = {}
            for row in cursor.fetchall():
                fmovs[str(row[0])] = {'cliente_nome': row[1], 'delta': row[2], 'tipo': row[3],
                    'origem': row[4] or '', 'criado_em': row[5] or get_timestamp()}
            dados_firebase['fiado_mov'] = fmovs

            cursor = conn.execute("SELECT id, codigo, delta, tipo, origem, criado_em FROM estoque_mov WHERE db_id=?", (db_id,))
            movs = {}
            for row in cursor.fetchall():
                movs[str(row[0])] = {'codigo': row[1], 'delta': row[2], 'tipo': row[3],
                    'origem': row[4] or '', 'criado_em': row[5] or get_timestamp()}
            dados_firebase['estoque_mov'] = movs
        # Preserva as preferências (foto, opacidade, escala) que já estão no Firebase,
        # junto com seus timestamps. Como o sync usa PUT (substitui tudo), sem isso
        # essas preferências seriam apagadas. Elas são gerenciadas à parte por timestamp.
        try:
            atual_fb = carregar_usuario_firebase(db_id, timeout=4)
            if atual_fb:
                for campo in ('bg_vendas_img', 'bg_vendas_img_ts',
                              'bg_vendas_opacidade', 'bg_vendas_opacidade_ts',
                              'escala_sistema', 'escala_sistema_ts'):
                    if campo in atual_fb:
                        dados_firebase[campo] = atual_fb[campo]
        except Exception:
            pass
        ok = salvar_usuario_firebase(db_id, dados_firebase)
        if ok:
            logger.info(f"✅ Dados enviados para Firebase: {db_id} ({len(vendas)} vendas, {len(produtos)} produtos)")
        else:
            logger.error(f"❌ Falha ao enviar para Firebase: {db_id}")
        return ok
    except Exception as e:
        logger.error(f"❌ Erro ao enviar para Firebase: {e}")
        return False

def sincronizar_automatico(db_id: str) -> None:
    if not db_id:
        return
    def _sync():
        try:
            _time.sleep(0.5)
            # A migração roda DEPOIS de sincronizar: assim os fatos que já existem
            # em outros dispositivos chegam primeiro, e ela não cria um "saldo
            # inicial" que somaria em cima deles (dívida dobrada).
            sincronizar_dados(db_id)
            migrar_dividas_para_fatos(db_id)
        except Exception as e:
            logger.error(f"⚠️ Erro sync automático: {e}")
    threading.Thread(target=_sync, daemon=True).start()

def criar_usuario_firebase(db_id: str, nome: str, email: str, senha_hash: str, servidor_id: str,
                          nome_loja: str = "", cnpj: str = "", cnpj_dados: Dict = None) -> Dict:
    if cnpj_dados is None:
        cnpj_dados = {}
    # 15 DIAS DE TESTE GRÁTIS (PLANO EMPRESARIAL)
    expira_em = (datetime.now() + timedelta(days=15)).isoformat()
    plano_id = 5  # Plano de TESTE (Empresarial completo)
    plano = PlanoSincronizado(db_id, CHAVE_SECRETA_PLANO)
    token = plano._emitir_token_via_backend(expira_em, plano_id, rota='emitir_trial')
    if not token:
        logger.error(f"⚠️ MODO INSEGURO: assinando token de teste localmente para {db_id} (backend indisponível - publique /emitir_trial no Worker)")
        token = plano._criar_token(expira_em, plano_id)
    dados = {
        'db_id': db_id, 'nome': nome, 'email': email, 'senha': senha_hash,
        'servidor_id': servidor_id, 'nome_loja': nome_loja, 'cnpj': cnpj,
        'cnpj_dados': cnpj_dados, 'data_cadastro': get_timestamp(),
        'plano': plano_id, 'expira_em': expira_em, 'token_plano': token,
        'token_atualizado_em': get_timestamp(), 'teste_usado': True, 'produtos': {}, 'clientes': {},
        'vendas': [], 'caixa': {'status': 'fechado'}, 'config': {}
    }
    # 🔧 usa /register (não salvar_usuario_firebase) porque esta conta é NOVA -
    # ainda não existe nenhum token de sessão pra ela. O Worker cria o registro
    # E já devolve um token de sessão, que fica guardado pra autorizar as
    # próximas escritas desta mesma conta (ex: foto padrão, logo abaixo).
    if not _registrar_no_backend(db_id, dados):
        logger.error(f"⚠️ Falha ao registrar {db_id} no backend - conta pode não ter sido criada no Firebase")
    plano.salvar_token_local(token)
    try:
        with get_db_context() as conn:
            conn.execute("INSERT OR REPLACE INTO config (chave, valor) VALUES ('teste_usado', '1')")
    except Exception as e:
        logger.error(f"⚠️ Erro ao marcar teste usado no registro: {e}")
    return dados

# ============================================================
# BUSCA PRODUTO POR CÓDIGO DE BARRAS
# ============================================================
def buscar_produto_por_codigo_barras(codigo_barras: str) -> Dict:
    codigo_limpo = ''.join(filter(str.isdigit, codigo_barras))
    if len(codigo_limpo) < 8:
        return {"success": False, "error": "Código de barras inválido. Mínimo 8 dígitos."}
    if codigo_limpo in CACHE_PRODUTO_BARRAS:
        cache_data = CACHE_PRODUTO_BARRAS[codigo_limpo]
        if _time.time() - cache_data['timestamp'] < 604800:
            return {"success": True, "dados": cache_data['dados'], "fonte": "cache"}
    try:
        url = f"https://www.dotcompany.com.br/api/catalogo/public/buscar?q={codigo_limpo}"
        response = requests.get(url, timeout=4, headers={"User-Agent": "SMART-PDV/10.0"})
        if response.status_code == 200:
            data = response.json()
            if data.get('sucesso') and data.get('produto'):
                produto = data['produto']
                dados_produto = {
                    "nome": produto.get('nome') or produto.get('descricao') or f"Produto {codigo_limpo}",
                    "marca": produto.get('marca', ''),
                    "categoria": produto.get('categoria') or produto.get('categoria_google_shopping') or "Geral",
                    "gtin": produto.get('gtin', codigo_limpo),
                    "imagem_url": produto.get('imagem_url', ''),
                    "ncm": produto.get('ncm', ''),
                    "fonte": "DotCompany"
                }
                CACHE_PRODUTO_BARRAS[codigo_limpo] = {'dados': dados_produto, 'timestamp': _time.time()}
                return {"success": True, "dados": dados_produto, "fonte": "DotCompany"}
    except:
        pass
    try:
        url = f"https://world.openfoodfacts.org/api/v0/product/{codigo_limpo}.json"
        response = requests.get(url, timeout=4, headers={"User-Agent": "SMART-PDV/10.0"})
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 1 and data.get('product'):
                produto = data['product']
                nome = (produto.get('product_name') or produto.get('product_name_pt') or
                        produto.get('product_name_en') or produto.get('generic_name') or '')
                marca = produto.get('brands', '').split(',')[0].strip() if produto.get('brands') else ''
                cat = produto.get('categories', '').split(',')[0].strip() if produto.get('categories') else 'Geral'
                imagem_url = produto.get('image_front_url') or produto.get('image_url') or ''
                dados_produto = {"nome": nome or f"Produto {codigo_limpo}", "marca": marca, "categoria": cat, "gtin": codigo_limpo, "imagem_url": imagem_url, "fonte": "OpenFoodFacts"}
                CACHE_PRODUTO_BARRAS[codigo_limpo] = {'dados': dados_produto, 'timestamp': _time.time()}
                return {"success": True, "dados": dados_produto, "fonte": "OpenFoodFacts"}
    except:
        pass
    try:
        url = f"https://brasilapi.com.br/api/gtin/v1/{codigo_limpo}"
        response = requests.get(url, timeout=4)
        if response.status_code == 200:
            data = response.json()
            if data.get('gtin'):
                dados_produto = {"nome": data.get('nome') or data.get('descricao') or f"Produto {codigo_limpo}",
                    "marca": data.get('marca', ''), "categoria": data.get('categoria') or data.get('classe') or "Geral",
                    "gtin": data.get('gtin', codigo_limpo), "imagem_url": "", "fonte": "BrasilAPI"}
                CACHE_PRODUTO_BARRAS[codigo_limpo] = {'dados': dados_produto, 'timestamp': _time.time()}
                return {"success": True, "dados": dados_produto, "fonte": "BrasilAPI"}
    except:
        pass
    dados_produto = {"nome": f"Produto {codigo_limpo}", "marca": "", "categoria": "Geral", "gtin": codigo_limpo, "imagem_url": "", "fonte": "Fallback"}
    CACHE_PRODUTO_BARRAS[codigo_limpo] = {'dados': dados_produto, 'timestamp': _time.time()}
    return {"success": True, "dados": dados_produto, "fonte": "Fallback"}

# ============================================================
# IMPRESSÃO ESC/POS - APENAS WINDOWS
# ============================================================
def formatar_cnpj(cnpj: str) -> str:
    if not cnpj or len(cnpj) != 14:
        return cnpj
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}"

def gerar_texto_cupom(dados: Dict) -> str:
    nome_loja = dados.get('nome_loja', 'MINHA LOJA')
    cnpj = dados.get('cnpj', '')
    cnpj_dados = dados.get('cnpj_dados', {})
    data_hora = dados.get('data_hora', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
    venda_id = dados.get('venda_id', '')
    itens = dados.get('itens', [])
    subtotal = dados.get('subtotal', 0)
    desconto = dados.get('desconto', 0)
    total = dados.get('total', 0)
    lucro_total = dados.get('lucro_total', 0)
    metodo = dados.get('metodo', 'Dinheiro')
    cliente = dados.get('cliente', '')
    usuario = dados.get('usuario', '')
    recebido = dados.get('recebido', 0)
    troco = dados.get('troco', 0)

    L = 48
    linhas = []
    linhas.append('=' * L)
    linhas.append(nome_loja.center(L))
    if cnpj:
        linhas.append(f'CNPJ: {formatar_cnpj(cnpj)}'.center(L))
    if cnpj_dados:
        if cnpj_dados.get('razao_social'):
            linhas.append(cnpj_dados['razao_social'][:46].center(L))
        if cnpj_dados.get('nome_fantasia'):
            linhas.append(f'FANTASIA: {cnpj_dados["nome_fantasia"][:37]}'.center(L))
        if cnpj_dados.get('data_abertura'):
            linhas.append(f'ABERTURA: {cnpj_dados["data_abertura"]}'.center(L))
        if cnpj_dados.get('porte'):
            linhas.append(f'PORTE: {cnpj_dados["porte"][:40]}'.center(L))
        if cnpj_dados.get('natureza_juridica'):
            linhas.append(f'NATUREZA: {cnpj_dados["natureza_juridica"][:37]}'.center(L))
        if cnpj_dados.get('cnae_descricao'):
            linhas.append(f'ATIVIDADE: {cnpj_dados["cnae_descricao"][:36]}'.center(L))
        if cnpj_dados.get('logradouro'):
            end = cnpj_dados.get('logradouro', '')
            if cnpj_dados.get('numero'):
                end += f", {cnpj_dados['numero']}"
            if cnpj_dados.get('bairro'):
                end += f" - {cnpj_dados['bairro']}"
            if cnpj_dados.get('municipio'):
                end += f", {cnpj_dados['municipio']}"
            if cnpj_dados.get('uf'):
                end += f"/{cnpj_dados['uf']}"
            linhas.append(end[:46].center(L))
        if cnpj_dados.get('telefone'):
            linhas.append(f'TEL: {cnpj_dados["telefone"]}'.center(L))
        if cnpj_dados.get('email'):
            linhas.append(f'EMAIL: {cnpj_dados["email"]}'.center(L))
    linhas.append('-' * L)
    linhas.append('CUPOM NÃO FISCAL'.center(L))
    linhas.append(f'Data: {data_hora}'.center(L))
    if venda_id:
        linhas.append(f'Venda: #{venda_id}'.center(L))
    linhas.append('=' * L)
    linhas.append('')
    linhas.append('ITEM'.ljust(3) + 'DESCRIÇÃO'.ljust(25) + 'QTD'.rjust(4) + 'TOTAL'.rjust(16))
    linhas.append('-' * L)

    for idx, item in enumerate(itens, 1):
        nome = item.get('nome', 'Item')[:22]
        qtd = item.get('quantidade', 1)
        total_item = item.get('total', 0)
        preco_unit = item.get('preco_unitario', 0)
        lucro_item = item.get('lucro', 0)
        linhas.append(f"{str(idx).ljust(3)}{nome.ljust(25)}{str(qtd).rjust(4)}{f'R$ {total_item:.2f}'.rjust(16)}")
        if qtd > 1 and preco_unit:
            linhas.append(f"   R$ {preco_unit:.2f} x {qtd}")
        # O lucro NÃO é impresso no cupom (informação interna)

    linhas.append('-' * L)
    linhas.append(f"{'SUBTOTAL:'.ljust(32)}R$ {subtotal:.2f}".rjust(L))
    if desconto > 0:
        linhas.append(f"{'DESCONTO:'.ljust(32)}R$ {desconto:.2f}".rjust(L))
    linhas.append(f"{'TOTAL:'.ljust(32)}R$ {total:.2f}".rjust(L))
    linhas.append('-' * L)
    linhas.append(f"PAGAMENTO: {metodo}".center(L))
    if recebido > 0:
        linhas.append(f"RECEBIDO: R$ {recebido:.2f}".center(L))
    if troco > 0:
        linhas.append(f"TROCO: R$ {troco:.2f}".center(L))
    if cliente:
        linhas.append(f"CLIENTE: {cliente}".center(L))
    if usuario:
        linhas.append(f"OPERADOR: {usuario}".center(L))
    linhas.append('=' * L)
    linhas.append('')
    linhas.append('VOLTE SEMPRE!'.center(L))
    linhas.append('=' * L)
    return '\n'.join(linhas) + '\n\n'

def _bytes_escpos_cupom(texto: str) -> bytes:
    """Monta os bytes ESC/POS (init + charset CP850 + corpo + corte). Usado tanto
    pela impressão via driver do Windows (win32print) quanto via rede (socket
    direto pra impressora Wi-Fi) - o protocolo ESC/POS é o mesmo nos dois casos,
    só muda o transporte."""
    ESC = chr(27)
    GS = chr(29)
    cmd_init = (ESC + '@').encode('latin-1', 'replace')
    # Seleciona a tabela de caracteres CP850 (código 2) — é a que a maioria
    # das impressoras térmicas usa para acentos do português. Sem isso,
    # "Ã", "Ç", "É" etc saem trocados (o famoso "N|O" no lugar de "NÃO").
    cmd_charset = (ESC + 't' + chr(2)).encode('latin-1', 'replace')
    cmd_cut = (GS + 'V' + chr(66) + chr(0)).encode('latin-1', 'replace')
    try:
        corpo = texto.encode('cp850')
    except Exception:
        sem_acento = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('ascii')
        corpo = sem_acento.encode('cp850', 'replace')
    return cmd_init + cmd_charset + corpo + b'\n\n\n' + cmd_cut


def _config_obter(chave: str, default: str = '') -> str:
    try:
        with get_db_context() as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS config (chave TEXT PRIMARY KEY, valor TEXT, criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            cursor = conn.execute("SELECT valor FROM config WHERE chave=?", (chave,))
            result = cursor.fetchone()
            return result[0] if result else default
    except Exception:
        return default


def _config_definir(chave: str, valor: str) -> None:
    with get_db_context() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS config (chave TEXT PRIMARY KEY, valor TEXT, criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        conn.execute("INSERT OR REPLACE INTO config (chave, valor) VALUES (?, ?)", (chave, valor))
        conn.commit()

# ============================================================
# NOTA FISCAL (NFC-e) - RECEBIMENTO DO CERTIFICADO DIGITAL
# ============================================================
# Esta seção só prepara o PDV pra RECEBER e guardar o certificado A1 (.pfx) e
# os dados necessários (CSC, série, UF, ambiente). A emissão de verdade (gerar
# o XML, assinar, transmitir pra SEFAZ) é a próxima etapa - só dá pra testar
# isso com um certificado e CSC reais, então fica pra quando você tiver os
# dois em mãos. Tudo aqui é local (nunca sincroniza pro Firebase): certificado
# e senhas são credenciais fiscais da empresa, não fazem sentido saltar de
# aparelho em aparelho como uma preferência normal.
CAMINHO_CERTIFICADO_PFX: str = os.path.join(FISCAL_DIR, 'certificado.pfx')

def _obter_chave_fiscal() -> bytes:
    """Chave simétrica local (só desta instalação), gerada uma vez, pra
    criptografar em repouso a senha do certificado e o token do CSC. Nunca é a
    mesma chave usada pra outra coisa (ex: assinatura de plano) - senha de
    certificado fiscal é sensível demais pra reaproveitar chave de outro uso."""
    caminho = os.path.join(APP_DATA_DIR, 'fiscal.key')
    try:
        if os.path.exists(caminho):
            with open(caminho, 'rb') as f:
                chave = f.read().strip()
                if chave:
                    return chave
        chave = Fernet.generate_key()
        with open(caminho, 'wb') as f:
            f.write(chave)
        return chave
    except Exception:
        return Fernet.generate_key()

def _fiscal_cifrar(texto: str) -> str:
    if not texto:
        return ''
    return Fernet(_obter_chave_fiscal()).encrypt(texto.encode()).decode()

def _fiscal_decifrar(texto_cifrado: str) -> str:
    if not texto_cifrado:
        return ''
    try:
        return Fernet(_obter_chave_fiscal()).decrypt(texto_cifrado.encode()).decode()
    except Exception:
        return ''

# ============================================================
# NFC-e - MOTOR DE EMISSÃO (modelo 65, layout 4.00)
# ============================================================
# IMPORTANTE: isto foi construído e testado isoladamente (chave de acesso,
# XML, assinatura, QR Code) com um certificado de teste autoassinado - mas a
# TRANSMISSÃO de verdade pra SEFAZ só pode ser confirmada com um certificado
# ICP-Brasil real, porque a SEFAZ exige o certificado na própria conexão
# HTTPS (mTLS), não só pra assinar. Teste em ambiente de Homologação antes de
# usar em Produção.
NFCE_URL_NS = "http://www.portalfiscal.inf.br/nfe"

UF_CODIGO_IBGE: Dict[str, int] = {
    "AC": 12, "AL": 27, "AP": 16, "AM": 13, "BA": 29, "CE": 23, "DF": 53, "ES": 32,
    "GO": 52, "MA": 21, "MT": 51, "MS": 50, "MG": 31, "PA": 15, "PB": 25, "PR": 41,
    "PE": 26, "PI": 22, "RJ": 33, "RN": 24, "RS": 43, "RO": 11, "RR": 14, "SC": 42,
    "SP": 35, "SE": 28, "TO": 17,
}

# Base do QR Code por UF (padrão NT2020.006). Só GO está preenchida de
# verdade (é o estado que vamos testar); as outras ficam como placeholder
# pra não fingir suporte que não foi validado ainda.
QRCODE_URL_BASE: Dict[str, Dict[str, str]] = {
    "GO": {
        "producao": "https://nfce.sefaz.go.gov.br/nfceweb/consultarNFce.jsp",
        "homologacao": "https://homolog.sefaz.go.gov.br/nfeweb/sites/nfce/danfeNFCe",
    },
}

MAPA_TPAG = {
    'DINHEIRO': '01', 'PIX': '17', 'CARTAO': '03', 'CARTÃO': '03',
    'DEBITO': '04', 'DÉBITO': '04', 'CREDITO': '03', 'CRÉDITO': '03',
    'FIADO': '99',  # "Outros" - fiado não é uma forma de pagamento fiscal formal
}

def _normalizar_texto_busca(t: str) -> str:
    t = unicodedata.normalize('NFKD', t or '').encode('ascii', 'ignore').decode('ascii')
    return t.strip().upper()

def _tpag_do_metodo(metodo: str) -> str:
    return MAPA_TPAG.get(_normalizar_texto_busca(metodo), '99')

def _obter_codigo_ibge_municipio(uf: str, nome_municipio: str) -> Optional[str]:
    """Busca (e guarda em cache local, indefinidamente - código IBGE de
    município não muda) o código de 7 dígitos do IBGE via API pública."""
    if not uf or not nome_municipio:
        return None
    chave_cache = f'fiscal_municipios_{uf}'
    municipios = {}
    cache_json = _config_obter(chave_cache)
    if cache_json:
        try:
            municipios = json.loads(cache_json)
        except Exception:
            municipios = {}
    nome_norm = _normalizar_texto_busca(nome_municipio)
    if nome_norm in municipios:
        return municipios[nome_norm]
    try:
        r = requests.get(f'https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios', timeout=10)
        r.raise_for_status()
        for m in r.json():
            municipios[_normalizar_texto_busca(m['nome'])] = str(m['id'])
        _config_definir(chave_cache, json.dumps(municipios))
    except Exception as e:
        logger.warning(f"⚠️ Não consegui buscar municípios do IBGE pra {uf}: {e}")
        return municipios.get(nome_norm)
    return municipios.get(nome_norm)

def _dv_mod11_chave(chave_43: str) -> str:
    pesos = [2, 3, 4, 5, 6, 7, 8, 9]
    soma = sum(int(c) * pesos[i % 8] for i, c in enumerate(reversed(chave_43)))
    resto = soma % 11
    return '0' if resto in (0, 1) else str(11 - resto)

def gerar_chave_acesso_nfce(uf: str, data_emissao: datetime, cnpj: str, serie, numero, codigo_numerico: int, tp_emis: str = '1') -> str:
    """Monta a chave de 44 dígitos: cUF(2) AAMM(4) CNPJ(14) mod(2)=65
    série(3) número(9) tpEmis(1) cNF(8) + DV(1) = 44.
    tpEmis=1 é emissão normal (online); tpEmis=9 é contingência offline
    (usado quando a SEFAZ está inacessível - ver EMISSAO_CONTINGENCIA)."""
    cuf = UF_CODIGO_IBGE.get(uf.upper())
    if not cuf:
        raise ValueError(f"UF desconhecida pra chave de acesso: {uf}")
    aamm = data_emissao.strftime('%y%m')
    cnpj_num = re.sub(r'\D', '', cnpj or '').zfill(14)
    chave_43 = f"{cuf:02d}{aamm}{cnpj_num}65{int(serie):03d}{int(numero):09d}{tp_emis}{int(codigo_numerico):08d}"
    return chave_43 + _dv_mod11_chave(chave_43)

def _fmt_dec(valor, casas=2) -> str:
    return f"{float(valor or 0):.{casas}f}"

def montar_xml_nfce(dados_loja: Dict, itens_venda: List[Dict], totais: Dict, config_fiscal: Dict, produtos_fiscais: Dict[str, Dict], contingencia: bool = False) -> Tuple[str, str]:
    """Constrói o XML da NFC-e (sem assinatura ainda). Retorna (chave_acesso, xml_string).
    Estrutura validada contra um XML real de NFe emitida (mesmo XSD da NFC-e,
    só muda o <mod> e alguns campos de <ide>) - não foi inventada do zero.
    contingencia=True gera com tpEmis=9 (contingência offline) - usado quando
    a SEFAZ está inacessível (ver EMISSAO_CONTINGENCIA)."""
    if not FISCAL_NFCE_DISPONIVEL:
        raise RuntimeError("Dependências de NFC-e (lxml/signxml/nfelib) não instaladas neste build")

    uf = config_fiscal['uf']
    ambiente = config_fiscal['ambiente']
    tp_amb = '1' if ambiente == 'producao' else '2'
    tp_emis = '9' if contingencia else '1'
    serie = config_fiscal.get('serie') or '1'
    numero = config_fiscal['proximo_numero']
    cnpj = re.sub(r'\D', '', dados_loja.get('cnpj', ''))
    agora = datetime.now()
    codigo_numerico = secrets.randbelow(99999999)
    chave = gerar_chave_acesso_nfce(uf, agora, cnpj, serie, numero, codigo_numerico, tp_emis)
    cnpj_dados = dados_loja.get('cnpj_dados') or {}
    cmun = _obter_codigo_ibge_municipio(uf, cnpj_dados.get('municipio', '')) or '0000000'

    NFE = f"{{{NFCE_URL_NS}}}"
    nsmap = {None: NFCE_URL_NS}
    NFe = fiscal_etree.Element(NFE + 'NFe', nsmap=nsmap)
    infNFe = fiscal_etree.SubElement(NFe, NFE + 'infNFe', versao='4.00', Id=f'NFe{chave}')

    ide = fiscal_etree.SubElement(infNFe, NFE + 'ide')
    fiscal_etree.SubElement(ide, NFE + 'cUF').text = str(UF_CODIGO_IBGE[uf])
    fiscal_etree.SubElement(ide, NFE + 'cNF').text = f"{codigo_numerico:08d}"
    fiscal_etree.SubElement(ide, NFE + 'natOp').text = 'Venda'
    fiscal_etree.SubElement(ide, NFE + 'mod').text = '65'
    fiscal_etree.SubElement(ide, NFE + 'serie').text = str(int(serie))
    fiscal_etree.SubElement(ide, NFE + 'nNF').text = str(int(numero))
    fiscal_etree.SubElement(ide, NFE + 'dhEmi').text = agora.astimezone().isoformat(timespec='seconds')
    fiscal_etree.SubElement(ide, NFE + 'tpNF').text = '1'
    fiscal_etree.SubElement(ide, NFE + 'idDest').text = '1'
    fiscal_etree.SubElement(ide, NFE + 'cMunFG').text = cmun
    fiscal_etree.SubElement(ide, NFE + 'tpImp').text = '4'
    fiscal_etree.SubElement(ide, NFE + 'tpEmis').text = tp_emis
    fiscal_etree.SubElement(ide, NFE + 'cDV').text = chave[-1]
    fiscal_etree.SubElement(ide, NFE + 'tpAmb').text = tp_amb
    fiscal_etree.SubElement(ide, NFE + 'finNFe').text = '1'
    fiscal_etree.SubElement(ide, NFE + 'indFinal').text = '1'
    fiscal_etree.SubElement(ide, NFE + 'indPres').text = '1'
    fiscal_etree.SubElement(ide, NFE + 'procEmi').text = '0'
    fiscal_etree.SubElement(ide, NFE + 'verProc').text = f'SmartPDV {VERSION}'
    if contingencia:
        # dhCont: quando entrou em contingência. xJust: motivo (mín. 15 chars
        # pelo schema - "SEFAZ indisponível" tem 19, então sempre passa).
        fiscal_etree.SubElement(ide, NFE + 'dhCont').text = agora.astimezone().isoformat(timespec='seconds')
        fiscal_etree.SubElement(ide, NFE + 'xJust').text = 'SEFAZ indisponível no momento da venda'

    emit = fiscal_etree.SubElement(infNFe, NFE + 'emit')
    fiscal_etree.SubElement(emit, NFE + 'CNPJ').text = cnpj
    fiscal_etree.SubElement(emit, NFE + 'xNome').text = (cnpj_dados.get('razao_social') or dados_loja.get('nome_loja') or 'MINHA LOJA')[:60]
    if cnpj_dados.get('nome_fantasia'):
        fiscal_etree.SubElement(emit, NFE + 'xFant').text = cnpj_dados['nome_fantasia'][:60]
    ender = fiscal_etree.SubElement(emit, NFE + 'enderEmit')
    fiscal_etree.SubElement(ender, NFE + 'xLgr').text = (cnpj_dados.get('logradouro') or 'NAO INFORMADO')[:60]
    fiscal_etree.SubElement(ender, NFE + 'nro').text = str(cnpj_dados.get('numero') or 'SN')[:60]
    if cnpj_dados.get('bairro'):
        fiscal_etree.SubElement(ender, NFE + 'xBairro').text = cnpj_dados['bairro'][:60]
    fiscal_etree.SubElement(ender, NFE + 'cMun').text = cmun
    fiscal_etree.SubElement(ender, NFE + 'xMun').text = (cnpj_dados.get('municipio') or 'NAO INFORMADO')[:60]
    fiscal_etree.SubElement(ender, NFE + 'UF').text = uf
    fiscal_etree.SubElement(ender, NFE + 'CEP').text = re.sub(r'\D', '', cnpj_dados.get('cep', '')) or '00000000'
    fiscal_etree.SubElement(ender, NFE + 'cPais').text = '1058'
    fiscal_etree.SubElement(ender, NFE + 'xPais').text = 'Brasil'
    if config_fiscal.get('inscricao_estadual'):
        fiscal_etree.SubElement(emit, NFE + 'IE').text = re.sub(r'\D', '', config_fiscal['inscricao_estadual'])
    fiscal_etree.SubElement(emit, NFE + 'CRT').text = config_fiscal.get('regime_tributario', '1')

    for idx, item in enumerate(itens_venda, 1):
        codigo = str(item.get('codigo') or 'AVULSO')
        fdados = produtos_fiscais.get(codigo, {})
        qtd = item.get('quantidade', 1) or 1
        preco_unit = item.get('preco_unitario') or (item.get('total', 0) / qtd if qtd else 0)

        det = fiscal_etree.SubElement(infNFe, NFE + 'det', nItem=str(idx))
        prod = fiscal_etree.SubElement(det, NFE + 'prod')
        fiscal_etree.SubElement(prod, NFE + 'cProd').text = codigo[:60]
        fiscal_etree.SubElement(prod, NFE + 'cEAN').text = 'SEM GTIN'
        fiscal_etree.SubElement(prod, NFE + 'xProd').text = str(item.get('nome', 'Item'))[:120]
        fiscal_etree.SubElement(prod, NFE + 'NCM').text = fdados.get('ncm') or '00000000'
        fiscal_etree.SubElement(prod, NFE + 'CFOP').text = fdados.get('cfop') or '5102'
        fiscal_etree.SubElement(prod, NFE + 'uCom').text = fdados.get('unidade') or 'UN'
        fiscal_etree.SubElement(prod, NFE + 'qCom').text = _fmt_dec(qtd, 4)
        fiscal_etree.SubElement(prod, NFE + 'vUnCom').text = _fmt_dec(preco_unit, 10)
        fiscal_etree.SubElement(prod, NFE + 'vProd').text = _fmt_dec(preco_unit * qtd)
        fiscal_etree.SubElement(prod, NFE + 'cEANTrib').text = 'SEM GTIN'
        fiscal_etree.SubElement(prod, NFE + 'uTrib').text = fdados.get('unidade') or 'UN'
        fiscal_etree.SubElement(prod, NFE + 'qTrib').text = _fmt_dec(qtd, 4)
        fiscal_etree.SubElement(prod, NFE + 'vUnTrib').text = _fmt_dec(preco_unit, 10)
        fiscal_etree.SubElement(prod, NFE + 'indTot').text = '1'

        imposto = fiscal_etree.SubElement(det, NFE + 'imposto')
        icms = fiscal_etree.SubElement(imposto, NFE + 'ICMS')
        # CSOSN 102 (padrão Simples Nacional sem crédito) é o mais comum pra
        # varejo simples. Regime normal (CRT=3) usaria <ICMS00> com CST, não
        # implementado ainda porque o regime confirmado é Simples Nacional.
        icmssn = fiscal_etree.SubElement(icms, NFE + 'ICMSSN102')
        fiscal_etree.SubElement(icmssn, NFE + 'orig').text = fdados.get('origem') or '0'
        fiscal_etree.SubElement(icmssn, NFE + 'CSOSN').text = fdados.get('csosn') or '102'
        pis = fiscal_etree.SubElement(imposto, NFE + 'PIS')
        pisnt = fiscal_etree.SubElement(pis, NFE + 'PISNT')
        fiscal_etree.SubElement(pisnt, NFE + 'CST').text = '07'
        cofins = fiscal_etree.SubElement(imposto, NFE + 'COFINS')
        cofinsnt = fiscal_etree.SubElement(cofins, NFE + 'COFINSNT')
        fiscal_etree.SubElement(cofinsnt, NFE + 'CST').text = '07'

    total = fiscal_etree.SubElement(infNFe, NFE + 'total')
    icmsTot = fiscal_etree.SubElement(total, NFE + 'ICMSTot')
    for campo, valor in (('vBC', 0), ('vICMS', 0), ('vICMSDeson', 0), ('vFCP', 0),
        ('vBCST', 0), ('vST', 0), ('vFCPST', 0), ('vFCPSTRet', 0),
        ('vProd', totais['subtotal']), ('vFrete', 0), ('vSeg', 0), ('vDesc', totais.get('desconto', 0)),
        ('vII', 0), ('vIPI', 0), ('vIPIDevol', 0), ('vPIS', 0), ('vCOFINS', 0),
        ('vOutro', 0), ('vNF', totais['total'])):
        fiscal_etree.SubElement(icmsTot, NFE + campo).text = _fmt_dec(valor)

    transp = fiscal_etree.SubElement(infNFe, NFE + 'transp')
    fiscal_etree.SubElement(transp, NFE + 'modFrete').text = '9'

    pag = fiscal_etree.SubElement(infNFe, NFE + 'pag')
    detPag = fiscal_etree.SubElement(pag, NFE + 'detPag')
    fiscal_etree.SubElement(detPag, NFE + 'tPag').text = _tpag_do_metodo(totais.get('metodo', ''))
    fiscal_etree.SubElement(detPag, NFE + 'vPag').text = _fmt_dec(totais['total'])
    if totais.get('troco'):
        fiscal_etree.SubElement(pag, NFE + 'vTroco').text = _fmt_dec(totais['troco'])

    infAdic = fiscal_etree.SubElement(infNFe, NFE + 'infAdic')
    fiscal_etree.SubElement(infAdic, NFE + 'infCpl').text = f'Venda #{totais.get("venda_id", "")} - Emitido por SmartPDV'

    xml_str = fiscal_etree.tostring(NFe, encoding='unicode')
    return chave, xml_str

def assinar_xml_nfce(xml_str: str, chave: str, pkcs12_bytes: bytes, pkcs12_senha: str) -> str:
    if not FISCAL_NFCE_DISPONIVEL:
        raise RuntimeError("Dependências de NFC-e não instaladas neste build")
    priv_key, cert, _outros = pkcs12.load_key_and_certificates(pkcs12_bytes, pkcs12_senha.encode())
    root = fiscal_etree.fromstring(xml_str.encode())
    signer = _NFCeXMLSigner(
        method=fiscal_signxml_methods.enveloped,
        signature_algorithm=FiscalSigMethod.RSA_SHA1,
        digest_algorithm=FiscalDigestAlg.SHA1,
        c14n_algorithm=FiscalC14nMethod.CANONICAL_XML_1_0,
    )
    signed_root = signer.sign(root, key=priv_key, cert=[cert], reference_uri=f"#NFe{chave}")
    return fiscal_etree.tostring(signed_root, encoding='unicode')

def montar_qrcode_nfce(chave: str, uf: str, ambiente: str, csc_id: str, csc_token: str) -> Optional[str]:
    """URL do QR Code impresso no DANFCE (padrão NT2020.006: hash SHA-1 de
    'chave' + 'CSC' em hex maiúsculo). ATENÇÃO: a fórmula exata e a URL base
    podem variar por estado - isto precisa ser conferido contra o Manual de
    Orientação do Contribuinte da SEFAZ-GO antes de confiar no QR impresso."""
    base = QRCODE_URL_BASE.get(uf.upper(), {}).get(ambiente)
    if not base or not csc_id or not csc_token:
        return None
    tp_amb = '1' if ambiente == 'producao' else '2'
    hash_input = f"{chave}{csc_token}"
    c_hash = hashlib.sha1(hash_input.encode()).hexdigest().upper()
    return f"{base}?p={chave}|2|{tp_amb}|{csc_id}|{c_hash}"

def gerar_texto_danfce(dados_loja: Dict, itens_venda: List[Dict], totais: Dict, chave: str, protocolo: str, qrcode_url: Optional[str], ambiente: str,
        pendente_contingencia: bool = False, cancelada: bool = False) -> str:
    """Texto pra impressão térmica do DANFCE (documento auxiliar da NFC-e).
    Reaproveita o layout do cupom normal e acrescenta os campos fiscais
    obrigatórios (chave de acesso, protocolo, aviso de homologação)."""
    cnpj_dados = dados_loja.get('cnpj_dados') or {}
    L = 48
    linhas = []
    linhas.append('=' * L)
    linhas.append((cnpj_dados.get('razao_social') or dados_loja.get('nome_loja', 'MINHA LOJA'))[:L].center(L))
    linhas.append(f"CNPJ: {formatar_cnpj(dados_loja.get('cnpj', ''))}".center(L))
    linhas.append('-' * L)
    linhas.append('DOCUMENTO AUXILIAR DA NOTA FISCAL'.center(L))
    linhas.append('DE CONSUMIDOR ELETRONICA'.center(L))
    if cancelada:
        linhas.append('=' * L)
        linhas.append('*** NFC-e CANCELADA ***'.center(L))
        linhas.append('=' * L)
    elif pendente_contingencia:
        linhas.append('=' * L)
        linhas.append('EMITIDA EM CONTINGENCIA'.center(L))
        linhas.append('PENDENTE DE TRANSMISSAO A SEFAZ'.center(L))
        linhas.append('=' * L)
    if ambiente != 'producao':
        linhas.append('=' * L)
        linhas.append('EMITIDO EM AMBIENTE DE HOMOLOGACAO'.center(L))
        linhas.append('SEM VALOR FISCAL'.center(L))
    linhas.append('=' * L)
    linhas.append('')
    for idx, item in enumerate(itens_venda, 1):
        qtd = item.get('quantidade', 1) or 1
        nome = str(item.get('nome', 'Item'))[:22]
        total_item = item.get('total', 0)
        linhas.append(f"{str(idx).ljust(3)}{nome.ljust(25)}{str(qtd).rjust(4)}{f'R$ {total_item:.2f}'.rjust(16)}")
    linhas.append('-' * L)
    linhas.append(f"{'TOTAL:'.ljust(32)}R$ {totais['total']:.2f}".rjust(L))
    linhas.append('=' * L)
    linhas.append('Consulte pela Chave de Acesso em:')
    linhas.append('www.nfce.fazenda.gov.br')
    linhas.append('')
    chave_espacada = ' '.join(chave[i:i+4] for i in range(0, len(chave), 4))
    linhas.append(chave_espacada.center(L))
    if protocolo:
        linhas.append(f'Protocolo: {protocolo}'.center(L))
    if qrcode_url:
        linhas.append('')
        linhas.append('[Escaneie o QR Code impresso]'.center(L))
    linhas.append('=' * L)
    return '\n'.join(linhas) + '\n\n'

def consultar_status_servico_sefaz(uf: str, ambiente: str, pkcs12_bytes: bytes, pkcs12_senha: str) -> Dict:
    """Chamada mais simples que existe pra testar se a conexão com a SEFAZ
    (URL certa + certificado aceito) está funcionando, sem emitir nada."""
    if not FISCAL_NFCE_DISPONIVEL:
        return {"success": False, "error": "Dependências de NFC-e não instaladas neste build"}
    try:
        cfg = SEFAZ_SERVERS.get(uf.upper())
        if not cfg:
            return {"success": False, "error": f"UF {uf} não tem endpoint configurado na biblioteca"}
        endpoints = cfg['dev_endpoints'] if ambiente != 'producao' else cfg['prod_endpoints']
        url = endpoints[SefazEndpoint.NFESTATUSSERVICO].replace('?wsdl', '')
        cuf = UF_CODIGO_IBGE[uf.upper()]
        tp_amb = '1' if ambiente == 'producao' else '2'
        corpo = (f'<consStatServ xmlns="{NFCE_URL_NS}" versao="4.00">'
                 f'<tpAmb>{tp_amb}</tpAmb><cUF>{cuf}</cUF><xServ>STATUS</xServ></consStatServ>')
        envelope = (
            '<soap12:Envelope xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">'
            '<soap12:Body><nfeDadosMsg xmlns="http://www.portalfiscal.inf.br/nfe/wsdl/NFeStatusServico4">'
            f'{corpo}</nfeDadosMsg></soap12:Body></soap12:Envelope>')
        sessao = requests.Session()
        sessao.mount(url, Pkcs12Adapter(pkcs12_data=pkcs12_bytes, pkcs12_password=pkcs12_senha))
        resp = sessao.post(url, data=envelope.encode('utf-8'),
            headers={'Content-Type': 'application/soap+xml; charset=utf-8'}, timeout=20)
        return {"success": resp.status_code == 200, "status_code": resp.status_code, "resposta": resp.text[:2000]}
    except Exception as e:
        return {"success": False, "error": str(e)}

def transmitir_nfce_sefaz(xml_assinado: str, chave: str, uf: str, ambiente: str, pkcs12_bytes: bytes, pkcs12_senha: str) -> Dict:
    """Envia a NFC-e assinada pra SEFAZ (autorização síncrona). Isto só pode
    ser testado de verdade com um certificado ICP-Brasil real - com um
    certificado de teste, a SEFAZ recusa a conexão TLS antes mesmo de olhar
    o XML (é assim que deve ser: só quem tem certificado emitido por uma AC
    credenciada consegue emitir nota de verdade)."""
    if not FISCAL_NFCE_DISPONIVEL:
        return {"success": False, "error": "Dependências de NFC-e não instaladas neste build"}
    try:
        cfg = SEFAZ_SERVERS.get(uf.upper())
        if not cfg:
            return {"success": False, "error": f"UF {uf} não tem endpoint configurado na biblioteca"}
        endpoints = cfg['dev_endpoints'] if ambiente != 'producao' else cfg['prod_endpoints']
        url = endpoints[SefazEndpoint.NFEAUTORIZACAO].replace('?wsdl', '')
        corpo = (f'<enviNFe xmlns="{NFCE_URL_NS}" versao="4.00">'
                 f'<idLote>1</idLote><indSinc>1</indSinc>{xml_assinado}</enviNFe>')
        envelope = (
            '<soap12:Envelope xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">'
            '<soap12:Body><nfeDadosMsg xmlns="http://www.portalfiscal.inf.br/nfe/wsdl/NFeAutorizacao4">'
            f'{corpo}</nfeDadosMsg></soap12:Body></soap12:Envelope>')
        sessao = requests.Session()
        sessao.mount(url, Pkcs12Adapter(pkcs12_data=pkcs12_bytes, pkcs12_password=pkcs12_senha))
        resp = sessao.post(url, data=envelope.encode('utf-8'),
            headers={'Content-Type': 'application/soap+xml; charset=utf-8'}, timeout=30)
        texto = resp.text
        protocolo = ''
        situacao = ''
        try:
            m_prot = re.search(r'<nProt>(.*?)</nProt>', texto)
            m_sit = re.search(r'<xMotivo>(.*?)</xMotivo>', texto)
            protocolo = m_prot.group(1) if m_prot else ''
            situacao = m_sit.group(1) if m_sit else ''
        except Exception:
            pass
        autorizada = '<cStat>100</cStat>' in texto  # 100 = Autorizado o uso da NF-e
        return {"success": autorizada, "status_code": resp.status_code, "protocolo": protocolo,
            "situacao": situacao, "resposta_bruta": texto[:4000], "chave": chave,
            "tipo_erro": None if autorizada else "rejeicao"}
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.SSLError) as e:
        # SEFAZ inacessível (rede caiu, timeout, certificado recusado na
        # camada TLS) - isto é diferente de uma REJEIÇÃO (onde a SEFAZ
        # respondeu e não gostou dos dados). Só neste caso entra
        # contingência - uma rejeição de verdade precisa ser corrigida, não
        # reemitida em contingência escondendo o erro real.
        return {"success": False, "error": str(e), "tipo_erro": "conectividade"}
    except Exception as e:
        return {"success": False, "error": str(e), "tipo_erro": "outro"}


def cancelar_nfce_sefaz(chave: str, protocolo: str, cnpj: str, uf: str, ambiente: str, justificativa: str, pkcs12_bytes: bytes, pkcs12_senha: str) -> Dict:
    """Envia o evento de Cancelamento (110111) pra SEFAZ. A NFC-e não é
    apagada nem alterada - fica marcada como cancelada por um evento
    separado, que é como o cancelamento funciona no padrão nacional."""
    if not FISCAL_NFCE_DISPONIVEL:
        return {"success": False, "error": "Dependências de NFC-e não instaladas neste build"}
    try:
        cfg = SEFAZ_SERVERS.get(uf.upper())
        if not cfg:
            return {"success": False, "error": f"UF {uf} não tem endpoint configurado na biblioteca"}
        endpoints = cfg['dev_endpoints'] if ambiente != 'producao' else cfg['prod_endpoints']
        url = endpoints[SefazEndpoint.RECEPCAOEVENTO].replace('?wsdl', '')
        cuf = UF_CODIGO_IBGE[uf.upper()]
        tp_amb = '1' if ambiente == 'producao' else '2'
        agora = datetime.now().astimezone().isoformat(timespec='seconds')
        cnpj_num = re.sub(r'\D', '', cnpj or '')
        id_evento = f"ID110111{chave}01"
        justificativa = (justificativa or '')[:255]
        if len(justificativa) < 15:
            justificativa = justificativa.ljust(15)

        NFE = f"{{{NFCE_URL_NS}}}"
        evento = fiscal_etree.Element(NFE + 'evento', nsmap={None: NFCE_URL_NS}, versao='1.00')
        infEvento = fiscal_etree.SubElement(evento, NFE + 'infEvento', Id=id_evento)
        fiscal_etree.SubElement(infEvento, NFE + 'cOrgao').text = str(cuf)
        fiscal_etree.SubElement(infEvento, NFE + 'tpAmb').text = tp_amb
        fiscal_etree.SubElement(infEvento, NFE + 'CNPJ').text = cnpj_num
        fiscal_etree.SubElement(infEvento, NFE + 'chNFe').text = chave
        fiscal_etree.SubElement(infEvento, NFE + 'dhEvento').text = agora
        fiscal_etree.SubElement(infEvento, NFE + 'tpEvento').text = '110111'
        fiscal_etree.SubElement(infEvento, NFE + 'nSeqEvento').text = '1'
        fiscal_etree.SubElement(infEvento, NFE + 'verEvento').text = '1.00'
        detEvento = fiscal_etree.SubElement(infEvento, NFE + 'detEvento', versao='1.00')
        fiscal_etree.SubElement(detEvento, NFE + 'descEvento').text = 'Cancelamento'
        fiscal_etree.SubElement(detEvento, NFE + 'nProt').text = protocolo
        fiscal_etree.SubElement(detEvento, NFE + 'xJust').text = justificativa

        xml_evento = fiscal_etree.tostring(evento, encoding='unicode')
        priv_key, cert, _outros = pkcs12.load_key_and_certificates(pkcs12_bytes, pkcs12_senha.encode())
        root = fiscal_etree.fromstring(xml_evento.encode())
        signer = _NFCeXMLSigner(method=fiscal_signxml_methods.enveloped, signature_algorithm=FiscalSigMethod.RSA_SHA1,
            digest_algorithm=FiscalDigestAlg.SHA1, c14n_algorithm=FiscalC14nMethod.CANONICAL_XML_1_0)
        signed_root = signer.sign(root, key=priv_key, cert=[cert], reference_uri=f"#{id_evento}")
        xml_assinado = fiscal_etree.tostring(signed_root, encoding='unicode')

        corpo = (f'<envEvento xmlns="{NFCE_URL_NS}" versao="1.00">'
                 f'<idLote>1</idLote>{xml_assinado}</envEvento>')
        envelope = (
            '<soap12:Envelope xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">'
            '<soap12:Body><nfeDadosMsg xmlns="http://www.portalfiscal.inf.br/nfe/wsdl/RecepcaoEvento4">'
            f'{corpo}</nfeDadosMsg></soap12:Body></soap12:Envelope>')
        sessao = requests.Session()
        sessao.mount(url, Pkcs12Adapter(pkcs12_data=pkcs12_bytes, pkcs12_password=pkcs12_senha))
        resp = sessao.post(url, data=envelope.encode('utf-8'),
            headers={'Content-Type': 'application/soap+xml; charset=utf-8'}, timeout=30)
        texto = resp.text
        m_prot = re.search(r'<nProt>(.*?)</nProt>', texto)
        m_sit = re.search(r'<xMotivo>(.*?)</xMotivo>', texto)
        cancelado = '<cStat>135</cStat>' in texto  # 135 = Evento registrado e vinculado a NF-e
        return {"success": cancelado, "protocolo_cancelamento": m_prot.group(1) if m_prot else '',
            "situacao": m_sit.group(1) if m_sit else '', "resposta_bruta": texto[:4000]}
    except Exception as e:
        return {"success": False, "error": str(e)}


def imprimir_cupom_rede(dados: Dict, ip: str, porta: int = 9100) -> Dict:
    """Envia o cupom direto por TCP pra uma impressora térmica de rede (Wi-Fi),
    sem precisar que ela esteja instalada como impressora do Windows. Funciona
    com qualquer impressora ESC/POS que escute na porta 9100 (padrão
    JetDirect/raw) - é assim que a maioria das impressoras térmicas Wi-Fi
    portáteis funciona, e o mesmo caminho serve pro app Android (só socket,
    sem depender de driver de SO nenhum)."""
    resultado = {}

    def _imprimir():
        try:
            texto = gerar_texto_cupom(dados)
            dados_bytes = _bytes_escpos_cupom(texto)
            with socket.create_connection((ip, porta), timeout=8) as sock:
                sock.sendall(dados_bytes)

            venda_id = dados.get('venda_id', '')
            if venda_id:
                arquivo = os.path.join(CUPONS_DIR, f'cupom_{venda_id}.txt')
                with open(arquivo, 'w', encoding='utf-8') as f:
                    f.write(texto)

            resultado['ok'] = True
            resultado['impressora'] = f'{ip}:{porta} (Wi-Fi)'
        except Exception as e:
            resultado['erro'] = str(e)

    t = threading.Thread(target=_imprimir, daemon=True)
    t.start()
    t.join(timeout=12)

    if t.is_alive():
        logger.error("❌ Impressão de rede travada - desistindo de esperar")
        return {"success": False, "error": "A impressora de rede não respondeu a tempo. Verifique o IP e se ela está ligada e na mesma rede Wi-Fi."}

    if resultado.get('ok'):
        logger.info(f"✅ Cupom impresso (rede): Venda #{dados.get('venda_id', '')} - R$ {dados.get('total', 0):.2f}")
        return {"success": True, "message": "Cupom impresso com sucesso!", "impressora": resultado['impressora']}

    erro = resultado.get('erro', 'Erro desconhecido ao imprimir')
    logger.error(f"❌ Erro ao imprimir cupom (rede): {erro}")
    return {"success": False, "error": f"Não consegui falar com a impressora de rede ({ip}): {erro}"}


def imprimir_cupom_escpos(dados: Dict) -> Dict:
    # Se tiver um IP de impressora de rede configurado (Config > Impressora),
    # usa ele em vez do driver do Windows - assim funciona também numa
    # impressora térmica Wi-Fi que não está instalada como impressora do SO.
    # Impressora Bluetooth: pareie ela normalmente no Windows (isso cria uma
    # impressora do sistema) e deixe o campo de IP em branco - o caminho por
    # win32print abaixo já manda pra qualquer impressora padrão do Windows,
    # seja ela USB, Bluetooth ou de rede instalada via driver.
    ip_rede = _config_obter('impressora_ip_rede')
    if ip_rede:
        return imprimir_cupom_rede(dados, ip_rede)

    if not IS_WINDOWS or not IMPRESSAO_DISPONIVEL:
        return {"success": False, "error": "Impressão indisponível. Se você está no Windows, os módulos de impressão (pywin32) não foram incluídos no aplicativo. Gere o executável novamente com o pywin32."}

    # 🔧 win32print pode travar de verdade (impressora sem papel, offline, ou
    # spooler do Windows preso) - situacao comum numa loja de verdade. Isso
    # ficava preso pra sempre dentro da requisicao HTTP e, como o servidor
    # roda sem threaded (ou rodava, ver app.run() no final do arquivo), NENHUMA
    # outra rota respondia ate alguem resolver a impressora manualmente. Agora
    # a impressao roda numa thread separada com um teto de 15s: se estourar,
    # devolvemos erro pro usuario em vez de travar o processo inteiro (a
    # thread presa fica sozinha em segundo plano, sem afetar mais nada).
    resultado = {}

    def _imprimir():
        try:
            import win32print
            texto = gerar_texto_cupom(dados)
            dados_bytes = _bytes_escpos_cupom(texto)

            impressora_nome = win32print.GetDefaultPrinter()
            if not impressora_nome:
                resultado['erro'] = "Nenhuma impressora padrão definida"
                return

            hprinter = win32print.OpenPrinter(impressora_nome)
            try:
                win32print.StartDocPrinter(hprinter, 1, ("Cupom Fiscal", None, "RAW"))
                win32print.StartPagePrinter(hprinter)
                win32print.WritePrinter(hprinter, dados_bytes)
                win32print.EndPagePrinter(hprinter)
                win32print.EndDocPrinter(hprinter)
            finally:
                win32print.ClosePrinter(hprinter)

            venda_id = dados.get('venda_id', '')
            if venda_id:
                arquivo = os.path.join(CUPONS_DIR, f'cupom_{venda_id}.txt')
                with open(arquivo, 'w', encoding='utf-8') as f:
                    f.write(texto)

            resultado['ok'] = True
            resultado['impressora'] = impressora_nome
        except Exception as e:
            resultado['erro'] = str(e)

    t = threading.Thread(target=_imprimir, daemon=True)
    t.start()
    t.join(timeout=15)

    if t.is_alive():
        logger.error("❌ Impressão travada (impressora sem papel/offline/spooler preso?) - desistindo de esperar")
        return {"success": False, "error": "A impressora não respondeu a tempo. Verifique se está ligada, com papel e online, e tente novamente."}

    if resultado.get('ok'):
        logger.info(f"✅ Cupom impresso: Venda #{dados.get('venda_id', '')} - R$ {dados.get('total', 0):.2f}")
        return {"success": True, "message": "Cupom impresso com sucesso!", "impressora": resultado['impressora']}

    erro = resultado.get('erro', 'Erro desconhecido ao imprimir')
    logger.error(f"❌ Erro ao imprimir cupom: {erro}")
    return {"success": False, "error": erro}

# ============================================================
# NORMALIZAÇÃO DE CNPJ
# ============================================================
def _normalizar_cnpj_dados(data: Dict) -> Dict:
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

# ============================================================
# DOWNLOAD HTML
# ============================================================
def baixar_html_github() -> bool:
    try:
        caminho_html = os.path.join(TEMPLATES_DIR, "index.html")
        logger.info("🔄 Baixando HTML do GitHub...")
        # cache-busting: evita que a rede/CDN devolva uma versão antiga em cache
        url = HTML_URL + ("&" if "?" in HTML_URL else "?") + "_=" + str(int(_time.time()))
        response = requests.get(url, timeout=8, headers={"Cache-Control": "no-cache"})
        response.raise_for_status()
        # grava num arquivo temporário e só troca se baixou 100% (evita HTML corrompido)
        tmp = caminho_html + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(response.text)
        os.replace(tmp, caminho_html)  # troca atômica
        logger.info(f"✅ HTML atualizado do GitHub ({len(response.text)} chars)")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao baixar HTML: {e}")
        return False

# ============================================================
# ROTAS FLASK
# ============================================================
@app.route('/')
def index():
    try:
        caminho_html = os.path.join(TEMPLATES_DIR, "index.html")
        # Se a interface não está no lugar (1ª execução, ou foi apagada),
        # tenta baixar na hora — o repositório é público.
        if not os.path.exists(caminho_html) or os.path.getsize(caminho_html) < 1000:
            baixar_html_github()
        resp = make_response(render_template('index.html'))
        # Impede o navegador de servir uma versão ANTIGA do HTML em cache
        # (causa comum de "o botão não faz nada" após atualizar o código).
        resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        resp.headers['Pragma'] = 'no-cache'
        resp.headers['Expires'] = '0'
        return resp
    except:
        return """<!DOCTYPE html><html><head><meta charset="UTF-8"><title>SMART PDV</title>
        <style>body{font-family:Arial;background:#0f0f1a;color:#fff;display:flex;justify-content:center;align-items:center;min-height:100vh;}
        .c{background:#16162e;border-radius:12px;padding:40px;text-align:center;}button{padding:12px 24px;background:#22c55e;color:#fff;border:0;border-radius:8px;cursor:pointer;}</style></head>
        <body><div class="c"><h1>🏪 SMART PDV</h1><p style="color:#a0a0c0;">Baixando interface...</p><button onclick="location.reload()">🔄 Recarregar</button></div></body></html>"""

@app.route('/api/versao')
def get_versao():
    return jsonify({"success": True, "versao": VERSION, "servidor_id": SERVIDOR_ID})

@app.route('/api/health')
def health_check():
    status = {"status": "online", "versao": VERSION, "servidor_id": SERVIDOR_ID, "timestamp": get_timestamp(),
        "db_status": "ok", "firebase_status": "ok", "sessoes_ativas": len(SESSOES_ATIVAS), "os": sys.platform}
    try:
        # 🔧 usa pdv/_hora_servidor (público nas regras) em vez de usuarios.json -
        # depois que as regras exigirem autenticação, um shallow de "usuarios"
        # sempre voltaria negado e este health-check ia reportar "warning" pra
        # sempre, mesmo com o Firebase 100% saudável.
        response = requests.get(f'{FB_URL}/pdv/_hora_servidor.json', timeout=5)
        if response.status_code != 200:
            status["firebase_status"] = "warning"
    except:
        status["firebase_status"] = "error"
        status["status"] = "degraded"
    try:
        with get_db_context() as conn:
            conn.execute("SELECT 1")
    except:
        status["db_status"] = "error"
        status["status"] = "degraded"
    return jsonify(status)

# ============================================================
# AUTH
# ============================================================
@app.route('/api/validar/cnpj/<cnpj>')
def validar_cnpj_route(cnpj: str):
    try:
        cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
        if len(cnpj_limpo) != 14:
            return jsonify({"success": False, "error": "CNPJ inválido"})
        with get_db_context() as conn:
            cursor = conn.execute("SELECT email FROM users WHERE cnpj=?", (cnpj_limpo,))
            result = cursor.fetchone()
            if result:
                return jsonify({"success": True, "existe": True, "email": result[0]})
        if validar_cnpj_firebase(cnpj_limpo):
            return jsonify({"success": True, "existe": True})
        return jsonify({"success": True, "existe": False})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/auth/register', methods=['POST'])
@rate_limit(max_requests=3, window=300)
def register():
    try:
        data = request.json or {}
        nome = (data.get('nome') or '').strip()
        email = (data.get('email') or '').strip().lower()
        senha = data.get('senha') or ''
        senha_hash = gerar_hash_senha(senha)  # formato novo (PBKDF2 + sal)
        cnpj = ''.join(filter(str.isdigit, data.get('cnpj') or ''))
        cnpj_dados = data.get('cnpj_dados') or {}
        nome_loja = cnpj_dados.get('razao_social') or cnpj_dados.get('nome_fantasia') or 'Minha Loja'

        if not nome or not email or not senha:
            return jsonify({"success": False, "error": "Preencha todos os campos"})
        if len(senha) < 4:
            return jsonify({"success": False, "error": "Senha deve ter pelo menos 4 caracteres"})
        # 🔧 SEGURANÇA: db_id nunca mais vem do cliente. Vinha um `data.get('db_id')`
        # aqui, mas o index.html atual NUNCA manda esse campo no registro (conferido
        # no front-end) - era uma porta sem uso legítimo, e permitia duas coisas
        # ruins: 1) o cliente escolher um db_id previsível/curto de propósito;
        # 2) potencialmente escolher o db_id de OUTRA conta já existente. Também
        # trocamos de uuid4()[:8] (32 bits, só 4 bilhões de combinações) pro UUID
        # completo (122 bits) - bem mais difícil de adivinhar/colidir.
        db_id = str(uuid.uuid4())

        with get_db_context() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM users WHERE servidor_id=? AND (cnpj='' OR cnpj IS NULL)", (SERVIDOR_ID,))
            contas_sem_cnpj = cursor.fetchone()[0]
            if contas_sem_cnpj >= 2 and not cnpj:
                return jsonify({"success": False, "error": "⚠️ Limite de 2 contas sem CNPJ neste dispositivo."}), 403

        with get_db_context() as conn:
            cursor = conn.execute("SELECT id FROM users WHERE email=?", (email,))
            if cursor.fetchone():
                return jsonify({"success": False, "error": "Email já cadastrado"})

        if buscar_usuario_por_email_firebase(email):
            return jsonify({"success": False, "error": "Este email já está cadastrado em outra conta."})

        if cnpj:
            with get_db_context() as conn:
                cursor = conn.execute("SELECT email FROM users WHERE cnpj=?", (cnpj,))
                result = cursor.fetchone()
                if result:
                    return jsonify({"success": False, "error": f"CNPJ já cadastrado no email: {result[0]}"})
            if validar_cnpj_firebase(cnpj):
                return jsonify({"success": False, "error": "CNPJ já cadastrado em outra conta."})

        user_id = str(uuid.uuid4())[:8]
        ts_bg = ler_timestamp_online() or int(_time.time() * 1000)
        with get_db_context() as conn:
            conn.execute("""INSERT INTO users (id, nome, email, senha, cargo, db_id, servidor_id, nome_loja, cnpj, cnpj_dados, bg_vendas_img, bg_vendas_img_ts, bg_vendas_opacidade, bg_vendas_opacidade_ts)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, nome, email, senha_hash, "Gerente", db_id, SERVIDOR_ID, nome_loja, cnpj, json.dumps(cnpj_dados), BG_PADRAO_URL, ts_bg, 0, ts_bg))

        # 1º) Cria a conta COMPLETA no Firebase (db_id, plano, expira_em, token).
        # Consideramos "já existe" só se houver um usuário COMPLETO (com email E
        # senha) — não confundir com um nó parcial (ex.: só a foto). Antes, salvar
        # a foto primeiro criava um nó parcial que enganava esta checagem e a conta
        # nascia sem db_id/plano/expira_em (plano não carregava, PIX não gerava).
        usuario_firebase = carregar_usuario_firebase(db_id)
        tem_usuario_completo = bool(usuario_firebase and usuario_firebase.get('email') and usuario_firebase.get('senha'))
        if not tem_usuario_completo:
            criar_usuario_firebase(db_id, nome, email, senha_hash, SERVIDOR_ID, nome_loja, cnpj, cnpj_dados)
        else:
            usuario_firebase.update({'nome': nome, 'email': email, 'senha': senha_hash, 'servidor_id': SERVIDOR_ID,
                'nome_loja': nome_loja, 'cnpj': cnpj, 'cnpj_dados': cnpj_dados, 'db_id': db_id})
            if not usuario_firebase.get('token_plano'):
                expira_em = usuario_firebase.get('expira_em', (datetime.now() + timedelta(days=15)).isoformat())
                plano_id = usuario_firebase.get('plano', 5)
                pl = PlanoSincronizado(db_id, CHAVE_SECRETA_PLANO)
                token_novo = pl._emitir_token_via_backend(expira_em, plano_id, rota='emitir_trial')
                usuario_firebase['token_plano'] = token_novo or pl._criar_token(expira_em, plano_id)
                usuario_firebase['token_atualizado_em'] = get_timestamp()
                usuario_firebase['plano'] = plano_id
                usuario_firebase['expira_em'] = expira_em
            salvar_usuario_firebase(db_id, usuario_firebase)

        # 2º) SÓ AGORA sobe a foto padrão (PATCH), depois da conta já existir.
        try:
            salvar_preferencia_firebase(db_id, 'bg_vendas_img', BG_PADRAO_URL)
            salvar_preferencia_firebase(db_id, 'bg_vendas_opacidade', 0)
        except Exception:
            pass

        return jsonify({"success": True, "message": "Conta criada! 15 dias de teste grátis!", "db_id": db_id})
    except Exception as e:
        logger.error(f"Erro no registro: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/auth/login', methods=['POST'])
@rate_limit(max_requests=5, window=60)
def login():
    try:
        data = request.json or {}
        email = (data.get('email') or '').strip().lower()
        senha = data.get('senha') or ''
        if not email or not senha:
            return jsonify({"success": False, "error": "Preencha email e senha"})

        def _fazer_login(user_db_id, user_id, nome, cargo, servidor_id_val, nome_loja_val, cnpj_val, cnpj_dados_val):
            nova_session_id = secrets.token_hex(32)
            session.permanent = True
            session['usuario_id'] = user_id
            session['nome'] = nome
            session['cargo'] = cargo
            session['db_id'] = user_db_id
            session['servidor_id'] = servidor_id_val
            session['nome_loja'] = nome_loja_val or 'Minha Loja'
            session['cnpj'] = cnpj_val or ''
            try:
                session['cnpj_dados'] = json.loads(cnpj_dados_val) if isinstance(cnpj_dados_val, str) else (cnpj_dados_val or {})
            except:
                session['cnpj_dados'] = {}
            session['session_id'] = nova_session_id

            with get_db_context() as conn:
                conn.execute("UPDATE users SET session_id=?, ultimo_acesso=? WHERE id=?", (nova_session_id, get_timestamp(), user_id))

            try:
                plano = PlanoSincronizado(user_db_id, CHAVE_SECRETA_PLANO)
                resultado = plano.sincronizar_token()
                if resultado.get('token_atualizado'):
                    logger.info(f"🔄 Token sincronizado durante login para {user_db_id}")
            except Exception as e:
                logger.warning(f"⚠️ Falha ao sincronizar token no login: {e}")

            try:
                dados_fb = carregar_usuario_firebase(user_db_id)
                if dados_fb:
                    if dados_fb.get('cnpj_dados'):
                        session['cnpj_dados'] = dados_fb.get('cnpj_dados', {})
            except:
                pass

            SESSOES_ATIVAS[user_id] = nova_session_id

            # Sincroniza com o Firebase em SEGUNDO PLANO — o login responde na hora,
            # sem esperar o merge completo (que travava a tela por vários segundos).
            threading.Thread(target=lambda: sincronizar_dados(user_db_id), daemon=True).start()

            plano_info = get_info_plano_completa(user_db_id)
            dias_restantes = plano_info.get('dias_restantes', 0)
            plano_ativo = plano_info.get('ativo', False)
            precisa_aviso, dias_para_aviso = precisa_aviso_renovacao(user_db_id)
            permissoes = get_permissoes(user_db_id)

            return jsonify({
                "success": True,
                "id": user_id,
                "nome": nome,
                "cargo": cargo,
                "db_id": user_db_id,
                "servidor_id": servidor_id_val,
                "nome_loja": nome_loja_val or 'Minha Loja',
                "cnpj": cnpj_val or '',
                "cnpj_dados": session.get('cnpj_dados', {}),
                "plano_ativo": plano_ativo,
                "dias_restantes": dias_restantes,
                "precisa_aviso": precisa_aviso,
                "dias_para_aviso": dias_para_aviso,
                "permissoes": permissoes,
                "url_renovacao": "#/planos" if not plano_ativo else None
            })

        # ============================================================
        # AUTENTICAÇÃO: o FIREBASE é a fonte da verdade.
        # - ONLINE: a conta PRECISA existir no Firebase. Se não existe lá,
        #   é inválida/desativada (você pode cortar acesso apagando de lá).
        # - OFFLINE: permitimos login com o banco local (cortesia), para a
        #   loja não parar quando a internet cai.
        # ============================================================
        online = firebase_online()

        if online:
            # 🔧 SEGURANÇA: a verificação de senha (comparar com o hash guardado
            # no Firebase) agora acontece DENTRO do Worker - ele é quem tem
            # permissão de ler esse hash. O pdv.py só recebe o registro
            # completo se a senha já bateu (e ganha um token de sessão pra
            # autorizar leituras/escritas seguintes desta conta).
            #
            # 🔧 Por design, não dá mais pra distinguir "conta não existe" de
            # "senha errada" (o Worker devolve o mesmo erro genérico pras
            # duas coisas, de propósito - não vazar se um email está
            # cadastrado é uma boa prática). Por isso também NÃO apagamos mais
            # a cópia local aqui: fazíamos isso antes assumindo que "não
            # existe no Firebase" só podia significar conta desativada, mas
            # agora esse mesmo caminho também é percorrido por um simples erro
            # de digitação na senha - apagar o acesso local por causa disso
            # seria pior que o problema que resolvia.
            usuario_firebase = _login_via_backend(email, senha)
            if not usuario_firebase:
                # 🔧 Não é necessariamente "conta não existe": um FUNCIONÁRIO
                # criado em Config > Usuários só existe no SQLite local desta
                # instalação (nunca teve registro próprio no Firebase pra ser
                # achado por lá) - sem este fallback, ele nunca conseguia logar,
                # mesmo tendo acabado de ser cadastrado com sucesso.
                with get_db_context() as conn:
                    cursor = conn.execute("""SELECT id, nome, cargo, db_id, servidor_id, nome_loja, cnpj, cnpj_dados, senha
                        FROM users WHERE email=?""", (email,))
                    user_local = cursor.fetchone()
                if user_local and verificar_senha(senha, user_local[8]):
                    return _fazer_login(user_local[3], user_local[0], user_local[1], user_local[2],
                        user_local[4], user_local[5], user_local[6], user_local[7])
                return jsonify({"success": False, "error": "Email ou senha inválidos"})

            firebase_db_id = usuario_firebase.get('db_id')

            if senha_e_antiga(usuario_firebase.get('senha')):
                # Senha correta, mas guardada no formato antigo (SHA-256 puro).
                # Migramos para PBKDF2 agora, sem o usuário perceber.
                try:
                    novo_hash = gerar_hash_senha(senha)
                    salvar_campos_firebase(firebase_db_id, {'senha': novo_hash})
                    usuario_firebase['senha'] = novo_hash
                    with get_db_context() as conn:
                        conn.execute("UPDATE users SET senha=? WHERE email=?", (novo_hash, email))
                    logger.info("🔐 Senha migrada para o formato seguro (PBKDF2)")
                except Exception as e:
                    logger.warning(f"⚠️ Não foi possível migrar a senha agora: {e}")

            # AUTO-CONSERTO de contas quebradas (criadas por versões antigas com bug):
            # se faltam campos essenciais (db_id, plano, expira_em ou token), a conta
            # não carrega o plano nem gera PIX. Aqui completamos e regravamos.
            precisa_reparar = False
            if not usuario_firebase.get('db_id'):
                usuario_firebase['db_id'] = firebase_db_id
                precisa_reparar = True
            if not usuario_firebase.get('token_plano') or not usuario_firebase.get('expira_em') or usuario_firebase.get('plano') is None:
                # tenta aproveitar o plano/validade que já existir; senão, teste de 15 dias
                expira_em = usuario_firebase.get('expira_em') or (datetime.now() + timedelta(days=15)).isoformat()
                plano_id = usuario_firebase.get('plano', 5) if usuario_firebase.get('plano') is not None else 5
                try:
                    pl = PlanoSincronizado(firebase_db_id, CHAVE_SECRETA_PLANO)
                    token_reparo = pl._emitir_token_via_backend(expira_em, plano_id, rota='emitir_trial')
                    usuario_firebase['token_plano'] = token_reparo or pl._criar_token(expira_em, plano_id)
                    usuario_firebase['token_atualizado_em'] = get_timestamp()
                except Exception:
                    pass
                usuario_firebase['expira_em'] = expira_em
                usuario_firebase['plano'] = plano_id
                precisa_reparar = True
            if precisa_reparar:
                try:
                    salvar_usuario_firebase(firebase_db_id, usuario_firebase)
                    logger.info(f"🛠️ Conta reparada no login: {firebase_db_id}")
                except Exception:
                    pass

            # Cria/atualiza a cópia local e faz login
            with get_db_context() as conn:
                cursor = conn.execute("SELECT id FROM users WHERE email=?", (email,))
                user_local = cursor.fetchone()
                if user_local:
                    user_id = user_local['id']
                    conn.execute("""UPDATE users SET nome=?, senha=?, cargo=?, db_id=?, servidor_id=?, nome_loja=?, cnpj=?, cnpj_dados=?
                        WHERE id=?""", (usuario_firebase.get('nome', ''), usuario_firebase.get('senha', ''),
                        usuario_firebase.get('cargo', 'Gerente'), firebase_db_id,
                        usuario_firebase.get('servidor_id', SERVIDOR_ID),
                        usuario_firebase.get('nome_loja', 'Minha Loja'),
                        usuario_firebase.get('cnpj', ''),
                        json.dumps(usuario_firebase.get('cnpj_dados', {})), user_id))
                else:
                    user_id = str(uuid.uuid4())[:8]
                    conn.execute("""INSERT INTO users (id, nome, email, senha, cargo, db_id, servidor_id, nome_loja, cnpj, cnpj_dados)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (user_id,
                        usuario_firebase.get('nome', ''), email, usuario_firebase.get('senha', ''),
                        usuario_firebase.get('cargo', 'Gerente'), firebase_db_id,
                        usuario_firebase.get('servidor_id', SERVIDOR_ID),
                        usuario_firebase.get('nome_loja', 'Minha Loja'),
                        usuario_firebase.get('cnpj', ''),
                        json.dumps(usuario_firebase.get('cnpj_dados', {}))))

            return _fazer_login(firebase_db_id, user_id, usuario_firebase.get('nome', ''),
                usuario_firebase.get('cargo', 'Gerente'), usuario_firebase.get('servidor_id', SERVIDOR_ID),
                usuario_firebase.get('nome_loja', 'Minha Loja'), usuario_firebase.get('cnpj', ''),
                usuario_firebase.get('cnpj_dados', {}))

        # OFFLINE: sem internet, autentica com o banco local (cortesia).
        # Buscamos pelo email e CONFERIMOS a senha: com sal, cada hash é único,
        # então não dá para comparar por igualdade dentro do SQL.
        with get_db_context() as conn:
            cursor = conn.execute("""SELECT id, nome, cargo, db_id, servidor_id, nome_loja, cnpj, cnpj_dados, senha
                FROM users WHERE email=?""", (email,))
            user = cursor.fetchone()
        if user and verificar_senha(senha, user[8]):
            return _fazer_login(user[3], user[0], user[1], user[2], user[4], user[5], user[6], user[7])

        return jsonify({"success": False, "error": "Sem internet e conta não encontrada neste dispositivo."})
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/auth/status')
def auth_status():
    # 🔧 é a rota de polling mais frequente do app inteiro (carga + a cada 20s
    # via setInterval no index.html, que engole erro com .catch(()=>{})) - sem
    # este try/except, qualquer exceção aqui vira 500 silencioso no front-end
    # e o polling de sessão para de funcionar sem ninguém perceber. Estava
    # inconsistente com o resto do arquivo, que é blindado assim em toda rota.
    try:
        if 'usuario_id' in session:
            # Se esta conta foi aberta em outro caixa/dispositivo, esta sessão foi
            # derrubada. Avisamos o frontend para voltar ao login com uma mensagem.
            if _sessao_foi_substituida():
                return jsonify({
                    "logged_in": False,
                    "sessao_substituida": True,
                    "error": "Sua conta foi acessada em outro dispositivo. Faça login novamente."
                })
            db_id = session.get('db_id')
            plano_info = get_info_plano_completa(db_id)
            dias_restantes = plano_info.get('dias_restantes', 0)
            plano_ativo = plano_info.get('ativo', False)
            precisa_aviso, dias_para_aviso = precisa_aviso_renovacao(db_id)
            permissoes = get_permissoes(db_id)
            return jsonify({
                "logged_in": True,
                "usuario_id": session.get('usuario_id'),
                "nome": session.get('nome'),
                "cargo": session.get('cargo'),
                "db_id": db_id,
                "servidor_id": session.get('servidor_id'),
                "nome_loja": session.get('nome_loja', 'Minha Loja'),
                "cnpj": session.get('cnpj', ''),
                "cnpj_dados": session.get('cnpj_dados', {}),
                "plano_ativo": plano_ativo,
                "dias_restantes": dias_restantes,
                "plano_expirado": not plano_ativo,
                "precisa_aviso": precisa_aviso,
                "dias_para_aviso": dias_para_aviso,
                "permissoes": permissoes
            })
        return jsonify({"logged_in": False})
    except Exception as e:
        logger.error(f"❌ Erro em /api/auth/status: {e}")
        return jsonify({"logged_in": False, "erro": str(e)[:100]})

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    try:
        db_id = session.get('db_id')
        if db_id and db_id in SESSOES_ATIVAS:
            del SESSOES_ATIVAS[db_id]
        usuario_id = session.get('usuario_id')
        if usuario_id:
            with get_db_context() as conn:
                conn.execute("UPDATE users SET session_id='' WHERE id=?", (usuario_id,))
        session.clear()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# PRODUTOS
# ============================================================
# ============================================================
# FIADO POR FATOS (movimentações imutáveis da dívida)
# ============================================================
def chave_cliente(db_id: str, nome: str) -> str:
    """Chave ESTÁVEL do cliente no Firebase, derivada do nome (não do id local).
    Dois aparelhos que conhecem o mesmo cliente geram a mesma chave, então nunca
    um sobrescreve o outro. O id do banco continua sendo só local."""
    return 'c_' + hashlib.sha256(f"{db_id}|{(nome or '').strip()}".encode()).hexdigest()[:16]

def registrar_mov_fiado(conn, db_id, cliente_nome, delta, tipo, origem=''):
    """Registra um FATO de fiado. delta positivo = comprou fiado (dívida sobe);
    negativo = pagou (dívida desce). A dívida é sempre a SOMA dos fatos."""
    mov_id = str(uuid.uuid4())
    conn.execute("""INSERT INTO fiado_mov (id, cliente_nome, delta, tipo, origem, db_id, criado_em)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (mov_id, str(cliente_nome), float(delta), tipo, origem, db_id, get_timestamp()))
    return mov_id

def calcular_divida(conn, db_id, cliente_nome):
    """Dívida atual = soma de todos os fatos daquele cliente (nunca negativa)."""
    row = conn.execute("SELECT COALESCE(SUM(delta),0) FROM fiado_mov WHERE cliente_nome=? AND db_id=?",
        (str(cliente_nome), db_id)).fetchone()
    return max(0.0, round(float(row[0]) if row else 0.0, 2))

def sincronizar_coluna_divida(conn, db_id, cliente_nome):
    """Atualiza a coluna 'divida' do cliente com a soma dos fatos (para exibição)."""
    valor = calcular_divida(conn, db_id, cliente_nome)
    conn.execute("UPDATE clientes SET divida=? WHERE nome=? AND db_id=?", (valor, str(cliente_nome), db_id))
    return valor

def migrar_dividas_para_fatos(db_id: str) -> None:
    """Converte as dívidas que já existem (o número atual) em um fato de
    'saldo_inicial'. Roda uma vez por cliente. O ID do fato é DETERMINÍSTICO
    (derivado do db_id + nome), então se dois dispositivos migrarem a mesma
    dívida, o fato é o mesmo e não duplica no merge."""
    if not db_id:
        return
    try:
        with get_db_context() as conn:
            clientes = conn.execute("SELECT nome, divida FROM clientes WHERE db_id=?", (db_id,)).fetchall()
            for row in clientes:
                nome, divida = row[0], float(row[1] or 0)
                if not nome:
                    continue
                # já tem fatos? então não migra
                tem = conn.execute("SELECT 1 FROM fiado_mov WHERE cliente_nome=? AND db_id=? LIMIT 1",
                    (nome, db_id)).fetchone()
                if tem:
                    continue
                if abs(divida) < 0.005:
                    continue
                mov_id = "saldo_" + hashlib.sha256(f"{db_id}|{nome}".encode()).hexdigest()[:20]
                conn.execute("""INSERT OR IGNORE INTO fiado_mov (id, cliente_nome, delta, tipo, origem, db_id, criado_em)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (mov_id, nome, divida, 'saldo_inicial', 'migração', db_id, get_timestamp()))
                logger.info(f"🔄 Dívida de {nome} (R$ {divida:.2f}) migrada para o modelo de fatos")
    except Exception as e:
        logger.error(f"⚠️ Erro ao migrar dívidas para fatos: {e}")

# ============================================================
# ESTOQUE POR FATOS (movimentações imutáveis)
# ============================================================
def registrar_mov_estoque(conn, db_id, codigo, delta, tipo, origem=''):
    """Registra um FATO de estoque (imutável, com ID único). delta positivo =
    entrada/ajuste pra cima; negativo = saída/venda. O estoque do produto é
    sempre a SOMA dos deltas. Como cada fato tem ID único, sincroniza igual às
    vendas — dois caixas somam suas saídas em vez de se sobrescreverem."""
    mov_id = str(uuid.uuid4())
    conn.execute("""INSERT INTO estoque_mov (id, codigo, delta, tipo, origem, db_id, criado_em)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (mov_id, str(codigo), int(delta), tipo, origem, db_id, get_timestamp()))
    return mov_id

def calcular_estoque(conn, db_id, codigo):
    """Estoque atual = soma de todos os fatos daquele produto."""
    row = conn.execute("SELECT COALESCE(SUM(delta),0) FROM estoque_mov WHERE codigo=? AND db_id=?",
        (str(codigo), db_id)).fetchone()
    return int(row[0]) if row else 0

def reconciliar_fatos_estoque(conn, db_id):
    """Corrige produtos cujo estoque em COLUNA não bate com a SOMA dos fatos.

    Isso acontece quando um produto chega de OUTRO dispositivo (ou de um backup
    antigo) pelo Firebase: ele vem com a coluna 'estoque' preenchida, mas sem os
    fatos correspondentes em estoque_mov. Como o estoque real é SUM(estoque_mov),
    a primeira venda levava o produto para negativo ('consome tudo e fica -1').

    Aqui, para cada produto SEM fatos, criamos um fato de ajuste igual à coluna —
    assim a soma passa a bater com o número que o usuário vê, e as próximas vendas
    descontam a partir do valor certo. Só age quando NÃO há fatos ainda, para não
    atropelar as vendas já registradas em estoque_mov.
    """
    try:
        produtos = conn.execute("SELECT codigo, estoque FROM produtos WHERE db_id=?", (db_id,)).fetchall()
        for codigo, estoque_coluna in produtos:
            estoque_coluna = int(estoque_coluna or 0)
            tem_fato = conn.execute("SELECT 1 FROM estoque_mov WHERE codigo=? AND db_id=? LIMIT 1",
                (str(codigo), db_id)).fetchone()
            if not tem_fato and estoque_coluna != 0:
                # produto sincronizado sem histórico de fatos: cria o fato inicial
                registrar_mov_estoque(conn, db_id, codigo, estoque_coluna, 'ajuste', 'reconciliação sync')
    except Exception as e:
        logger.error(f"⚠️ Erro ao reconciliar fatos de estoque: {e}")

def definir_estoque_absoluto(conn, db_id, codigo, novo_valor):
    """Quando o usuário digita um estoque TOTAL (ex: 'tenho 50'), criamos um fato
    de AJUSTE com a diferença entre o que ele quer e o que os fatos somam hoje.
    Assim o resultado bate com o número digitado, mas sem sobrescrever os fatos."""
    atual = calcular_estoque(conn, db_id, codigo)
    diferenca = int(novo_valor) - atual
    if diferenca != 0:
        registrar_mov_estoque(conn, db_id, codigo, diferenca, 'ajuste', 'ajuste manual')
    # espelha na coluna estoque (usada pela exibição rápida)
    conn.execute("UPDATE produtos SET estoque=? WHERE codigo=? AND db_id=?", (int(novo_valor), str(codigo), db_id))

def sincronizar_coluna_estoque(conn, db_id, codigo):
    """Atualiza a coluna 'estoque' do produto com a soma dos fatos (pra exibição)."""
    valor = calcular_estoque(conn, db_id, codigo)
    conn.execute("UPDATE produtos SET estoque=? WHERE codigo=? AND db_id=?", (valor, str(codigo), db_id))
    return valor

@app.route('/api/produtos')
@verificar_plano
def get_produtos():
    try:
        db_id = get_db_id()
        busca = request.args.get('busca', '').strip().lower()
        with get_db_context() as conn:
            if busca:
                termo = f'%{busca}%'
                cursor = conn.execute("""SELECT codigo, nome, preco, custo, margem, estoque, categoria, imagem_url, ncm, cfop, csosn, unidade, origem FROM produtos
                    WHERE db_id=? AND (LOWER(nome) LIKE ? OR LOWER(codigo) LIKE ?) ORDER BY nome""", (db_id, termo, termo))
            else:
                cursor = conn.execute("SELECT codigo, nome, preco, custo, margem, estoque, categoria, imagem_url, ncm, cfop, csosn, unidade, origem FROM produtos WHERE db_id=? ORDER BY nome", (db_id,))
            produtos = [dict(row) for row in cursor.fetchall()]
        return jsonify({"success": True, "produtos": produtos})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/produtos', methods=['POST'])
@verificar_plano
def save_produto():
    try:
        data = request.json or {}
        db_id = get_db_id()
        if not data.get('codigo') or not data.get('nome'):
            return jsonify({"success": False, "error": "Código e nome são obrigatórios"})
        
        preco = data.get('preco', 0)
        custo = data.get('custo', 0)
        margem = data.get('margem', 0)
        if preco > 0 and custo > 0 and margem == 0:
            margem = ((preco - custo) / preco) * 100
        
        with get_db_context() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM produtos WHERE codigo=? AND db_id=?", (data['codigo'], db_id))
            existe = cursor.fetchone()[0] > 0
        if not existe:
            pode, msg = pode_adicionar_produto(db_id, 1)
            if not pode:
                return jsonify({"success": False, "error": msg}), 403
        with get_db_context() as conn:
            estoque_desejado = int(data.get('estoque', 0) or 0)
            conn.execute("""INSERT INTO produtos (codigo, nome, preco, custo, margem, estoque, categoria, imagem_url, ncm, cfop, csosn, unidade, origem, db_id, ultima_atualizacao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(codigo) DO UPDATE SET
                nome=excluded.nome, preco=excluded.preco, custo=excluded.custo, margem=excluded.margem,
                categoria=excluded.categoria,
                imagem_url=CASE WHEN excluded.imagem_url!='' THEN excluded.imagem_url ELSE produtos.imagem_url END,
                ncm=excluded.ncm, cfop=excluded.cfop, csosn=excluded.csosn, unidade=excluded.unidade, origem=excluded.origem,
                ultima_atualizacao=excluded.ultima_atualizacao""",
                (data['codigo'], data['nome'], preco, custo, margem, estoque_desejado,
                data.get('categoria', 'Geral'), data.get('imagem_url', ''),
                (data.get('ncm') or '').strip(), (data.get('cfop') or '5102').strip(),
                (data.get('csosn') or '102').strip(), (data.get('unidade') or 'UN').strip(),
                str(data.get('origem') if data.get('origem') is not None else '0').strip(),
                db_id, get_timestamp()))
            # ESTOQUE POR FATOS: em vez de gravar o número direto (que dois caixas
            # sobrescreveriam), registramos um AJUSTE com a diferença. O estoque
            # final é sempre a soma dos fatos. Nota: no ON CONFLICT acima NÃO
            # atualizamos a coluna estoque — quem manda nela é a função abaixo.
            definir_estoque_absoluto(conn, db_id, data['codigo'], estoque_desejado)
            # Remove qualquer tombstone (exclusão) deste código: o produto existe de novo,
            # então o sync NÃO deve apagá-lo. (Corrige "salvou mas some da lista".)
            conn.execute("DELETE FROM exclusoes WHERE tipo='produto' AND item_id=? AND db_id=?", (data['codigo'], db_id))
        sincronizar_automatico(db_id)
        return jsonify({"success": True, "message": "Produto salvo"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/produtos/<codigo>', methods=['DELETE'])
@verificar_plano
def delete_produto(codigo: str):
    try:
        db_id = get_db_id()
        with get_db_context() as conn:
            conn.execute("DELETE FROM produtos WHERE codigo=? AND db_id=?", (codigo, db_id))
            # Registra o TOMBSTONE (marca de exclusão). Sem isso, o produto ainda
            # está no Firebase e a próxima sincronização o baixa de volta — era
            # esse o bug do "apago um e volta o outro". O tombstone avisa o sync
            # que este produto foi apagado de propósito, e ele não ressuscita.
            conn.execute("INSERT OR REPLACE INTO exclusoes (tipo, item_id, db_id, excluido_em) VALUES (?, ?, ?, ?)",
                ('produto', str(codigo), db_id, get_timestamp()))
        sincronizar_automatico(db_id)
        return jsonify({"success": True, "message": "Produto excluído"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# KITS / COMBOS - STANDARD PRA FRENTE
# ============================================================
@app.route('/api/kits')
@verificar_permissao('kit_combo')
@verificar_plano
def get_kits():
    try:
        db_id = get_db_id()
        # Lê os kits do banco LOCAL imediatamente (resposta rápida, igual ao estoque)
        with get_db_context() as conn:
            cursor = conn.execute("SELECT id, nome, preco, itens, ativo FROM kits WHERE db_id=? ORDER BY nome", (db_id,))
            kits = []
            for row in cursor.fetchall():
                try:
                    itens = json.loads(row[3]) if row[3] else []
                except:
                    itens = []
                kits.append({"id": row[0], "nome": row[1], "preco": row[2] or 0, "itens": itens, "ativo": bool(row[4])})
        # Sincroniza com o Firebase em segundo plano (não bloqueia a resposta)
        threading.Thread(target=_sync_kits_firebase_bg, args=(db_id,), daemon=True).start()
        return jsonify({"success": True, "kits": kits})
    except Exception as e:
        import traceback
        logger.error(f"❌ ERRO get_kits: {e}\n{traceback.format_exc()}")
        return jsonify({"success": False, "error": str(e)})

def _sync_kits_firebase_bg(db_id: str) -> None:
    """Sincroniza os kits do Firebase em segundo plano (não trava a tela)."""
    try:
        dados_fb = carregar_usuario_firebase(db_id, timeout=8)
        kits_fb = dados_fb.get('kits') if dados_fb else None
        # O Firebase pode devolver uma lista (quando as chaves são numéricas). Normaliza para dict.
        if isinstance(kits_fb, list):
            kits_fb = {str(i): v for i, v in enumerate(kits_fb) if v}
        if kits_fb and isinstance(kits_fb, dict):
            with get_db_context() as conn:
                cur_exc = conn.execute("SELECT item_id FROM exclusoes WHERE tipo='kit' AND db_id=?", (db_id,))
                excluidos = {r[0] for r in cur_exc.fetchall()}
                for kit_id, dk in kits_fb.items():
                    if not isinstance(dk, dict):
                        continue
                    if str(kit_id) in excluidos:
                        continue
                    itens_kit = dk.get('itens', [])
                    itens_json = json.dumps(itens_kit, ensure_ascii=False) if not isinstance(itens_kit, str) else itens_kit
                    fb_ts = dk.get('ultima_atualizacao') or get_timestamp()
                    cur = conn.execute("SELECT ultima_atualizacao, itens FROM kits WHERE id=? AND db_id=?", (kit_id, db_id))
                    row = cur.fetchone()
                    if row is None:
                        conn.execute("""INSERT INTO kits (id, nome, preco, itens, db_id, ativo, ultima_atualizacao)
                            VALUES (?, ?, ?, ?, ?, ?, ?)""",
                            (kit_id, dk.get('nome',''), dk.get('preco',0), itens_json, db_id,
                             1 if dk.get('ativo', True) else 0, fb_ts))
                    else:
                        local_ts = row[0]
                        local_itens = row[1]
                        fb_vazio = (not itens_kit) or (isinstance(itens_kit, list) and len(itens_kit) == 0)
                        local_tem = local_itens and local_itens not in ('[]', '', None)
                        if fb_vazio and local_tem:
                            continue
                        if not local_ts or fb_ts > local_ts:
                            conn.execute("""UPDATE kits SET nome=?, preco=?, itens=?, ativo=?, ultima_atualizacao=?
                                WHERE id=? AND db_id=?""",
                                (dk.get('nome',''), dk.get('preco',0), itens_json,
                                 1 if dk.get('ativo', True) else 0, fb_ts, kit_id, db_id))
    except Exception as e:
        logger.error(f"⚠️ Sync de kits em background falhou: {e}")

@app.route('/api/kits', methods=['POST'])
@verificar_permissao('kit_combo')
@verificar_plano
def save_kit():
    try:
        data = request.json or {}
        db_id = get_db_id()
        nome = (data.get('nome') or '').strip()
        itens = data.get('itens', [])
        preco = data.get('preco', 0)
        if not nome:
            return jsonify({"success": False, "error": "Nome do kit é obrigatório"})
        if not itens or len(itens) == 0:
            return jsonify({"success": False, "error": "Adicione pelo menos um item ao kit"})
        try:
            preco = float(preco)
        except:
            preco = 0
        if preco <= 0:
            return jsonify({"success": False, "error": "Defina um preço válido para o kit"})

        kit_id = data.get('id') or f"kit_{uuid.uuid4().hex[:10]}"
        itens_json = json.dumps(itens, ensure_ascii=False)
        with get_db_context() as conn:
            conn.execute("""INSERT INTO kits (id, nome, preco, itens, db_id, ativo, ultima_atualizacao)
                VALUES (?, ?, ?, ?, ?, 1, ?)
                ON CONFLICT(id) DO UPDATE SET
                nome=excluded.nome, preco=excluded.preco, itens=excluded.itens,
                ultima_atualizacao=excluded.ultima_atualizacao""",
                (kit_id, nome, preco, itens_json, db_id, get_timestamp()))
            # Garante que este kit NÃO esteja marcado como excluído (senão o sync o apagaria)
            conn.execute("DELETE FROM exclusoes WHERE tipo='kit' AND item_id=? AND db_id=?", (str(kit_id), db_id))
        sincronizar_automatico(db_id)
        return jsonify({"success": True, "message": "Kit salvo", "id": kit_id})
    except Exception as e:
        logger.error(f"❌ Erro ao salvar kit: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/kits/<kit_id>', methods=['DELETE'])
@verificar_permissao('kit_combo')
@verificar_plano
def delete_kit(kit_id: str):
    try:
        db_id = get_db_id()
        with get_db_context() as conn:
            cursor_del = conn.execute("DELETE FROM kits WHERE id=? AND db_id=?", (kit_id, db_id))
            linhas = cursor_del.rowcount
            conn.execute("INSERT OR REPLACE INTO exclusoes (tipo, item_id, db_id, excluido_em) VALUES (?, ?, ?, ?)",
                ('kit', str(kit_id), db_id, get_timestamp()))
        if linhas == 0:
            return jsonify({"success": False, "error": "Kit não encontrado"}), 404
        sincronizar_automatico(db_id)
        return jsonify({"success": True, "message": "Kit excluído"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# CLIENTES - COM PERMISSÃO
# ============================================================
@app.route('/api/clientes')
@verificar_permissao('clientes')
@verificar_plano
def get_clientes():
    try:
        db_id = get_db_id()
        busca = request.args.get('busca', '').strip().lower()
        with get_db_context() as conn:
            if busca:
                cursor = conn.execute("""SELECT id, nome, telefone, email, divida FROM clientes
                    WHERE db_id=? AND LOWER(nome) LIKE ? ORDER BY nome""", (db_id, f'%{busca}%'))
            else:
                cursor = conn.execute("SELECT id, nome, telefone, email, divida FROM clientes WHERE db_id=? ORDER BY nome", (db_id,))
            clientes = [dict(row) for row in cursor.fetchall()]
        return jsonify({"success": True, "clientes": clientes})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/clientes', methods=['POST'])
@verificar_permissao('clientes')
@verificar_plano
def save_cliente():
    try:
        data = request.json or {}
        db_id = get_db_id()
        nome = (data.get('nome') or '').strip()
        if not nome:
            return jsonify({"success": False, "error": "Nome é obrigatório"})
        with get_db_context() as conn:
            # O NOME é a identidade do cliente em todo o sistema (vendas, fatos de
            # fiado, exclusões e sincronização). Dois clientes com o mesmo nome
            # compartilhariam a mesma dívida — por isso não permitimos duplicar.
            if data.get('id'):
                dup = conn.execute("SELECT id FROM clientes WHERE LOWER(nome)=LOWER(?) AND db_id=? AND id<>?",
                    (nome, db_id, data['id'])).fetchone()
            else:
                dup = conn.execute("SELECT id FROM clientes WHERE LOWER(nome)=LOWER(?) AND db_id=?",
                    (nome, db_id)).fetchone()
            if dup:
                return jsonify({"success": False, "error": f"Já existe um cliente chamado '{nome}'"})
            if data.get('id'):
                # 'divida' NÃO vem do formulário: ela é a soma dos fatos (fiado_mov)
                conn.execute("""UPDATE clientes SET nome=?, telefone=?, email=?, ultima_atualizacao=?
                    WHERE id=? AND db_id=?""", (nome, data.get('telefone', ''), data.get('email', ''),
                    get_timestamp(), data['id'], db_id))
            else:
                conn.execute("""INSERT INTO clientes (nome, telefone, email, divida, db_id, ultima_atualizacao)
                    VALUES (?, ?, ?, ?, ?, ?)""", (nome, data.get('telefone', ''), data.get('email', ''),
                    0, db_id, get_timestamp()))
        sincronizar_automatico(db_id)
        return jsonify({"success": True, "message": "Cliente salvo"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/clientes/<int:cliente_id>/pagar', methods=['POST'])
@verificar_permissao('clientes')
@verificar_plano
def pagar_cliente(cliente_id: int):
    try:
        data = request.json or {}
        db_id = get_db_id()
        valor = data.get('valor', 0)
        if valor <= 0:
            return jsonify({"success": False, "error": "Valor deve ser maior que zero"})
        with get_db_context() as conn:
            cursor = conn.execute("SELECT id, nome, divida FROM clientes WHERE id=? AND db_id=?", (cliente_id, db_id))
            cliente = cursor.fetchone()
            if not cliente:
                return jsonify({"success": False, "error": "Cliente não encontrado"}), 404
            nome_cli = cliente['nome']
            # Não deixa pagar MAIS do que a dívida. Sem isso, o excesso viraria um
            # fato negativo "escondido" (a dívida é limitada a zero na exibição) e
            # as próximas compras no fiado sairiam de graça.
            divida_atual = calcular_divida(conn, db_id, nome_cli)
            if float(valor) > divida_atual + 0.005:
                return jsonify({"success": False,
                    "error": f"O valor é maior que a dívida (R$ {divida_atual:.2f})"})
            # FIADO POR FATOS: registra "pagou X" (delta negativo). Se outro caixa
            # registrar uma compra ao mesmo tempo, os DOIS fatos entram e a dívida
            # final fica correta — antes um sobrescrevia o outro.
            registrar_mov_fiado(conn, db_id, nome_cli, -float(valor), 'pagamento', f"pagamento {data.get('metodo','Dinheiro')}")
            sincronizar_coluna_divida(conn, db_id, nome_cli)
            conn.execute("UPDATE clientes SET ultima_atualizacao=? WHERE id=? AND db_id=?",
                (get_timestamp(), cliente_id, db_id))
            cursor = conn.execute("SELECT id, nome, divida FROM clientes WHERE id=? AND db_id=?", (cliente_id, db_id))
            cliente = cursor.fetchone()
            # Registra o pagamento do fiado como uma VENDA (aparece no dashboard, pois agora o dinheiro entrou)
            metodo_pg = data.get('metodo', 'Dinheiro')
            # Grava o item da quitação no MESMO formato das vendas normais
            # (preco_unitario + total). Antes só tinha 'preco', e o cupom quebrava
            # ao tentar ler i.total (undefined.toFixed).
            itens_quit = json.dumps([{
                "nome": f"Quitação de fiado - {cliente['nome']}",
                "codigo": "",
                "quantidade": 1,
                "preco_unitario": valor,
                "preco": valor,
                "total": valor,
                "lucro": 0
            }], ensure_ascii=False)
            usuario_atual = session.get('usuario_id', '')
            conn.execute("""INSERT INTO vendas (data_hora, subtotal, desconto, total, lucro_total, metodo, itens, cliente, usuario_id, db_id, recebido, troco)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (get_timestamp(), valor, 0, valor, 0, f"Fiado ({metodo_pg})", itens_quit,
                 cliente['nome'], usuario_atual, db_id, valor, 0))
        logger.info(f"✅ Dívida paga (registrada como venda) - cliente {cliente['nome']}: R$ {valor:.2f}")
        sincronizar_automatico(db_id)
        return jsonify({"success": True, "message": "Pagamento registrado",
            "cliente": {"id": cliente['id'], "nome": cliente['nome'], "divida": cliente['divida']}})
    except Exception as e:
        logger.error(f"❌ Erro ao registrar pagamento: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/clientes/<int:cliente_id>/relatorio')
@verificar_permissao('fiado')
@verificar_plano
def relatorio_cliente(cliente_id: int):
    """Monta o EXTRATO do cliente (como uma caderneta): as compras no fiado, os
    pagamentos feitos, e o saldo devedor atual. Assim o relatório é honesto e
    completo — não manda 'dívidas já pagas', pois mostra também o que foi pago."""
    try:
        db_id = get_db_id()
        with get_db_context() as conn:
            cur = conn.execute("SELECT nome, telefone, divida FROM clientes WHERE id=? AND db_id=?", (cliente_id, db_id))
            cli = cur.fetchone()
            if not cli:
                return jsonify({"success": False, "error": "Cliente não encontrado"})
            nome, telefone, divida = cli[0], (cli[1] or ''), (cli[2] or 0)
            # COMPRAS no fiado: metodo exatamente 'Fiado'
            cur = conn.execute("""SELECT data_hora, total, itens FROM vendas
                WHERE cliente=? AND metodo='Fiado' AND db_id=? ORDER BY data_hora""", (nome, db_id))
            vendas = cur.fetchall()
            # PAGAMENTOS: registrados como venda com metodo 'Fiado (forma)'
            cur = conn.execute("""SELECT data_hora, total FROM vendas
                WHERE cliente=? AND metodo LIKE 'Fiado (%' AND db_id=? ORDER BY data_hora""", (nome, db_id))
            pgs = cur.fetchall()
            cur2 = conn.execute("SELECT nome_loja FROM users WHERE db_id=? LIMIT 1", (db_id,))
            loja_row = cur2.fetchone()
            nome_loja = (loja_row[0] if loja_row else '') or 'Minha Loja'
        compras = []
        total_comprado = 0
        for v in vendas:
            try:
                itens = json.loads(v[2]) if v[2] else []
            except Exception:
                itens = []
            compras.append({"data": v[0], "total": v[1] or 0, "itens": itens})
            total_comprado += (v[1] or 0)
        pagamentos = []
        total_pago = 0
        for p in pgs:
            pagamentos.append({"data": p[0], "valor": p[1] or 0})
            total_pago += (p[1] or 0)
        return jsonify({"success": True, "nome_loja": nome_loja,
            "cliente": {"nome": nome, "telefone": telefone, "divida": divida},
            "compras": compras, "pagamentos": pagamentos,
            "total_comprado": total_comprado, "total_pago": total_pago})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/clientes/<int:cliente_id>', methods=['PUT'])
@verificar_permissao('clientes')
@verificar_plano
def editar_cliente(cliente_id: int):
    """Edita nome, telefone e email do cliente. Útil para adicionar o WhatsApp
    de um cliente que foi criado só com nome na hora da venda no fiado."""
    try:
        data = request.json or {}
        db_id = get_db_id()
        nome = (data.get('nome') or '').strip()
        telefone = (data.get('telefone') or '').strip()
        email = (data.get('email') or '').strip()
        if not nome:
            return jsonify({"success": False, "error": "O nome é obrigatório"})
        with get_db_context() as conn:
            # nome duplicado? (evita dois clientes com o mesmo nome, que bagunça o fiado)
            outro = conn.execute("SELECT id FROM clientes WHERE nome=? AND db_id=? AND id<>?", (nome, db_id, cliente_id)).fetchone()
            if outro:
                return jsonify({"success": False, "error": "Já existe outro cliente com esse nome"})
            # se o nome mudou, atualiza também as vendas ligadas a ele (o fiado usa o nome)
            atual = conn.execute("SELECT nome FROM clientes WHERE id=? AND db_id=?", (cliente_id, db_id)).fetchone()
            if not atual:
                return jsonify({"success": False, "error": "Cliente não encontrado"})
            nome_antigo = atual[0]
            conn.execute("UPDATE clientes SET nome=?, telefone=?, email=?, ultima_atualizacao=? WHERE id=? AND db_id=?",
                (nome, telefone, email, get_timestamp(), cliente_id, db_id))
            if nome_antigo and nome_antigo != nome:
                conn.execute("UPDATE vendas SET cliente=? WHERE cliente=? AND db_id=?", (nome, nome_antigo, db_id))
                # os fatos de fiado são chaveados pelo NOME: renomeia junto,
                # senão a dívida do cliente "sumiria" ao trocar o nome
                conn.execute("UPDATE fiado_mov SET cliente_nome=? WHERE cliente_nome=? AND db_id=?", (nome, nome_antigo, db_id))
        sincronizar_automatico(db_id)
        return jsonify({"success": True, "message": "Cliente atualizado"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/clientes/<int:cliente_id>', methods=['DELETE'])
@verificar_permissao('clientes')
@verificar_plano
def delete_cliente(cliente_id: int):
    try:
        db_id = get_db_id()
        with get_db_context() as conn:
            cursor = conn.execute("SELECT nome FROM clientes WHERE id=? AND db_id=?", (cliente_id, db_id))
            cliente = cursor.fetchone()
            nome_cliente = cliente['nome'] if cliente else f"ID {cliente_id}"
            cursor_del = conn.execute("DELETE FROM clientes WHERE id=? AND db_id=?", (cliente_id, db_id))
            linhas_afetadas = cursor_del.rowcount
            # Apaga os FATOS de fiado desse cliente. Sem isso, se um cliente com o
            # mesmo nome fosse cadastrado depois, a dívida antiga "ressuscitaria"
            # (a dívida é a soma dos fatos, e eles são chaveados pelo nome).
            if cliente:
                conn.execute("DELETE FROM fiado_mov WHERE cliente_nome=? AND db_id=?", (cliente['nome'], db_id))
            # TOMBSTONE POR NOME (não pelo id!): o id é AUTOINCREMENT local, então
            # o "id 1" do PC pode ser outra pessoa no celular. Apagar por id
            # excluiria o cliente ERRADO no outro aparelho.
            if cliente:
                conn.execute("INSERT OR REPLACE INTO exclusoes (tipo, item_id, db_id, excluido_em) VALUES (?, ?, ?, ?)",
                    ('cliente', cliente['nome'], db_id, get_timestamp()))
        if linhas_afetadas == 0:
            logger.warning(f"⚠️ Tentativa de excluir cliente {cliente_id} não encontrado (db_id={db_id})")
            return jsonify({"success": False, "error": "Cliente não encontrado"}), 404
        logger.info(f"✅ Cliente excluído: {nome_cliente}")
        sincronizar_automatico(db_id)
        return jsonify({"success": True, "message": f"Cliente {nome_cliente} excluído"})
    except Exception as e:
        logger.error(f"❌ Erro ao excluir cliente: {e}")
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# VENDAS - COM LUCRO TOTAL
# ============================================================
def _componentes_do_kit(conn, codigo_kit, db_id):
    """Retorna a lista de componentes (itens) de um kit a partir do código 'KIT:<id>'."""
    try:
        if not isinstance(codigo_kit, str) or not codigo_kit.startswith('KIT:'):
            return []
        kit_id = codigo_kit.split(':', 1)[1]
        cur = conn.execute("SELECT itens FROM kits WHERE id=? AND db_id=?", (kit_id, db_id))
        row = cur.fetchone()
        if not row or not row[0]:
            return []
        itens = json.loads(row[0]) if isinstance(row[0], str) else row[0]
        return itens if isinstance(itens, list) else []
    except Exception as e:
        logger.error(f"Erro ao ler componentes do kit: {e}")
        return []

@app.route('/api/vendas', methods=['POST'])
@verificar_plano
def registrar_venda():
    try:
        data = request.json or {}
        db_id = get_db_id()
        usuario_id = get_usuario_id()
        data_hora = get_timestamp()
        itens = data.get('itens', [])
        if not itens:
            return jsonify({"success": False, "error": "Nenhum item na venda"})

        # Um desconto maior que o subtotal geraria uma venda com total NEGATIVO,
        # que sujaria o faturamento e o caixa. Não permitimos.
        if float(data.get('total', 0) or 0) < 0:
            return jsonify({"success": False, "error": "O desconto não pode ser maior que o total da venda"})

        with get_db_context() as conn:
            conn.execute("BEGIN TRANSACTION")
            try:
                # Primeira passada: VALIDAR estoque (produtos normais e componentes de kits)
                for item in itens:
                    codigo = item.get('codigo')
                    is_kit = item.get('is_kit') or (isinstance(codigo, str) and codigo.startswith('KIT:'))
                    if is_kit:
                        # Mantém o custo do kit para o lucro
                        item['custo_unitario'] = item.get('custo_unitario', item.get('custo', 0)) or 0
                        # Verifica o estoque de CADA componente do kit
                        qtd_kit = item.get('quantidade', 1)
                        componentes = _componentes_do_kit(conn, codigo, db_id)
                        for comp in componentes:
                            comp_cod = comp.get('codigo')
                            comp_qtd = (comp.get('quantidade', 1) or 1) * qtd_kit
                            if not comp_cod or comp_cod == 'AVULSO':
                                continue
                            cur = conn.execute("SELECT estoque, nome FROM produtos WHERE codigo=? AND db_id=?", (comp_cod, db_id))
                            prod = cur.fetchone()
                            if prod and prod[0] < comp_qtd:
                                conn.execute("ROLLBACK")
                                return jsonify({"success": False, "error": f"Estoque insuficiente para '{prod[1]}' (usado no combo '{item.get('nome','')}'): disponível {prod[0]}, necessário {comp_qtd}"})
                        continue
                    if codigo and codigo != 'AVULSO':
                        cursor = conn.execute("SELECT estoque, nome, custo FROM produtos WHERE codigo=? AND db_id=?", (codigo, db_id))
                        produto = cursor.fetchone()
                        if not produto:
                            conn.execute("ROLLBACK")
                            return jsonify({"success": False, "error": f"Produto '{item.get('nome', codigo)}' não encontrado"})
                        qtd = item.get('quantidade', 1)
                        # O estoque de verdade é a SOMA dos fatos. Se a coluna e os
                        # fatos estiverem dessincronizados (ex: produto que veio de
                        # outro dispositivo sem histórico), acertamos AGORA criando o
                        # fato inicial — assim a baixa a seguir parte do número certo
                        # e nunca leva a negativo. Era esta a causa do "consome tudo
                        # e fica -1".
                        soma_fatos = calcular_estoque(conn, db_id, codigo)
                        tem_fato = conn.execute("SELECT 1 FROM estoque_mov WHERE codigo=? AND db_id=? LIMIT 1",
                            (str(codigo), db_id)).fetchone()
                        if not tem_fato and int(produto[0]) != 0:
                            registrar_mov_estoque(conn, db_id, codigo, int(produto[0]), 'ajuste', 'reconciliação venda')
                            soma_fatos = int(produto[0])
                        estoque_disponivel = max(int(produto[0]), soma_fatos) if not tem_fato else soma_fatos
                        if estoque_disponivel < qtd:
                            conn.execute("ROLLBACK")
                            return jsonify({"success": False, "error": f"Estoque insuficiente para '{produto[1]}': disponível {max(0, estoque_disponivel)}, necessário {qtd}"})
                        item['custo_unitario'] = produto[2] or 0
                # Segunda passada: BAIXAR estoque criando FATOS de saída (não
                # sobrescreve o número — registra "saiu N", que soma com as saídas
                # de outros caixas). A coluna estoque é atualizada pela soma.
                for item in itens:
                    codigo = item.get('codigo')
                    is_kit = item.get('is_kit') or (isinstance(codigo, str) and codigo.startswith('KIT:'))
                    if is_kit:
                        qtd_kit = item.get('quantidade', 1)
                        componentes = _componentes_do_kit(conn, codigo, db_id)
                        for comp in componentes:
                            comp_cod = comp.get('codigo')
                            comp_qtd = (comp.get('quantidade', 1) or 1) * qtd_kit
                            if not comp_cod or comp_cod == 'AVULSO':
                                continue
                            registrar_mov_estoque(conn, db_id, comp_cod, -comp_qtd, 'saida', 'venda')
                            sincronizar_coluna_estoque(conn, db_id, comp_cod)
                        continue
                    if codigo and codigo != 'AVULSO':
                        qtd = item.get('quantidade', 1)
                        registrar_mov_estoque(conn, db_id, codigo, -qtd, 'saida', 'venda')
                        sincronizar_coluna_estoque(conn, db_id, codigo)
                conn.execute("COMMIT")
            except Exception as e:
                conn.execute("ROLLBACK")
                raise e

        itens_salvar = []
        lucro_total = 0
        for item in itens:
            preco_unit = item.get('preco_unitario', item.get('preco', 0))
            qtd = item.get('quantidade', 1)
            custo_unit = item.get('custo_unitario', 0)
            total_item = preco_unit * qtd
            custo_total = custo_unit * qtd
            lucro_item = total_item - custo_total
            lucro_total += lucro_item
            
            itens_salvar.append({
                'codigo': item.get('codigo', 'AVULSO'),
                'nome': item.get('nome', 'Item'),
                'quantidade': qtd,
                'preco_unitario': preco_unit,
                'custo_unitario': custo_unit,
                'lucro': lucro_item,
                'total': total_item
            })

        venda_id = None
        with get_db_context() as conn:
            cursor = conn.execute("""INSERT INTO vendas (data_hora, subtotal, desconto, total, lucro_total, metodo, itens, cliente, usuario_id, db_id, recebido, troco)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (data_hora, data.get('subtotal', 0), data.get('desconto', 0),
                data.get('total', 0), lucro_total, data.get('metodo', 'Dinheiro'), json.dumps(itens_salvar, ensure_ascii=False),
                data.get('cliente', ''), usuario_id, db_id, data.get('recebido', 0), data.get('troco', 0)))
            venda_id = cursor.lastrowid

        if data.get('metodo') == 'Fiado' and data.get('cliente'):
            try:
                nome_cli = data.get('cliente')
                valor_fiado = float(data.get('total', 0) or 0)
                with get_db_context() as conn:
                    cursor = conn.execute("SELECT id FROM clientes WHERE nome=? AND db_id=?", (nome_cli, db_id))
                    cliente = cursor.fetchone()
                    if not cliente:
                        conn.execute("INSERT INTO clientes (nome, divida, db_id, ultima_atualizacao) VALUES (?, ?, ?, ?)",
                            (nome_cli, 0, db_id, get_timestamp()))
                    # FIADO POR FATOS: registra "comprou X" em vez de somar direto
                    # na coluna. Dois caixas somam seus fatos; nenhum sobrescreve.
                    registrar_mov_fiado(conn, db_id, nome_cli, valor_fiado, 'fiado', f'venda #{venda_id}')
                    sincronizar_coluna_divida(conn, db_id, nome_cli)
                    conn.execute("UPDATE clientes SET ultima_atualizacao=? WHERE nome=? AND db_id=?",
                        (get_timestamp(), nome_cli, db_id))
            except Exception as e:
                logger.error(f"⚠️ Erro ao registrar fiado: {e}")

        with get_db_context() as conn:
            cursor = conn.execute("SELECT nome_loja, cnpj, cnpj_dados FROM users WHERE db_id=? LIMIT 1", (db_id,))
            loja = cursor.fetchone()

        cnpj_dados = {}
        if loja and loja[2]:
            try:
                cnpj_dados = json.loads(loja[2])
            except:
                pass

        dados_impressao = {
            'venda_id': venda_id,
            'data_hora': data_hora,
            'itens': itens_salvar,
            'subtotal': data.get('subtotal', 0),
            'desconto': data.get('desconto', 0),
            'total': data.get('total', 0),
            'lucro_total': lucro_total,
            'metodo': data.get('metodo', 'Dinheiro'),
            'cliente': data.get('cliente', ''),
            'usuario': session.get('nome', ''),
            'nome_loja': loja[0] if loja else session.get('nome_loja', 'Minha Loja'),
            'cnpj': loja[1] if loja else session.get('cnpj', ''),
            'cnpj_dados': cnpj_dados,
            'recebido': data.get('recebido', 0),
            'troco': data.get('troco', 0)
        }

        sincronizar_automatico(db_id)

        return jsonify({
            "success": True,
            "id": venda_id,
            "data_hora": data_hora,
            "itens": itens_salvar,
            "lucro_total": lucro_total,
            "dados_impressao": dados_impressao,
            "loja": {
                "nome_loja": loja[0] if loja else session.get('nome_loja', 'Minha Loja'),
                "cnpj": loja[1] if loja else session.get('cnpj', ''),
                "cnpj_dados": cnpj_dados
            }
        })
    except Exception as e:
        logger.error(f"Erro ao registrar venda: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/vendas/<int:venda_id>', methods=['DELETE'])
@verificar_plano
def delete_venda(venda_id: int):
    try:
        db_id = get_db_id()
        with get_db_context() as conn:
            cur = conn.execute("DELETE FROM vendas WHERE id=? AND db_id=?", (venda_id, db_id))
            if cur.rowcount == 0:
                return jsonify({"success": False, "error": "Venda não encontrada"}), 404
            # Tombstone para não voltar em outro dispositivo
            conn.execute("INSERT OR REPLACE INTO exclusoes (tipo, item_id, db_id, excluido_em) VALUES (?, ?, ?, ?)",
                ('venda', str(venda_id), db_id, get_timestamp()))
        logger.info(f"🗑️ Venda {venda_id} excluída do histórico")
        sincronizar_automatico(db_id)
        return jsonify({"success": True, "message": "Venda excluída"})
    except Exception as e:
        logger.error(f"❌ Erro ao excluir venda: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/vendas')
@verificar_plano
def get_vendas():
    try:
        db_id = get_db_id()
        limite = request.args.get('limite', 200, type=int)
        with get_db_context() as conn:
            cursor = conn.execute("""SELECT id, data_hora, subtotal, desconto, total, lucro_total, metodo, itens, cliente, usuario_id, recebido, troco
                FROM vendas WHERE db_id=? ORDER BY id DESC LIMIT ?""", (db_id, limite))
            vendas = []
            for row in cursor.fetchall():
                try:
                    itens = json.loads(row[7]) if row[7] else []
                except:
                    itens = []
                vendas.append({"id": row[0], "data_hora": row[1], "subtotal": row[2], "desconto": row[3],
                    "total": row[4], "lucro_total": row[5] or 0, "metodo": row[6], "itens": itens,
                    "cliente": row[8] or '', "usuario_id": row[9] or '', "recebido": row[10] or 0, "troco": row[11] or 0})
        return jsonify({"success": True, "vendas": vendas})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/vendas/buscar')
@verificar_plano
def buscar_vendas():
    """Busca de vendas com filtros combináveis, para recuperar o cupom de uma
    venda antiga. Todos os filtros são opcionais e se somam (AND):
      - metodo: 'Dinheiro' | 'PIX' | 'Cartão' | 'Fiado' | '' (todos)
      - data_ini / data_fim: 'YYYY-MM-DD' (intervalo de dias, inclusive)
      - cliente: parte do nome (case-insensitive)
      - id: número exato da venda (#83 -> 83)
      - ordem: 'recente' (padrão) | 'antiga' | 'maior' (valor) | 'menor'
    """
    try:
        db_id = get_db_id()
        metodo = (request.args.get('metodo') or '').strip()
        data_ini = (request.args.get('data_ini') or '').strip()
        data_fim = (request.args.get('data_fim') or '').strip()
        cliente = (request.args.get('cliente') or '').strip()
        venda_id = request.args.get('id', type=int)
        ordem = (request.args.get('ordem') or 'recente').strip()
        limite = request.args.get('limite', 300, type=int)

        clausulas = ["db_id = ?"]
        params = [db_id]

        if venda_id:
            clausulas.append("id = ?")
            params.append(venda_id)
        if metodo:
            # 'Fiado' casa tanto a venda fiado quanto as quitações "Fiado (...)"
            if metodo == 'Fiado':
                clausulas.append("metodo LIKE 'Fiado%'")
            else:
                clausulas.append("metodo = ?")
                params.append(metodo)
        if data_ini:
            # data_hora é gravada em ISO ('2026-07-11T04:05:...'). Comparar com
            # 'YYYY-MM-DD' direto já funciona porque a data vem no comecinho do
            # texto e a ordenação alfabética coincide com a cronológica.
            clausulas.append("substr(data_hora,1,10) >= ?")
            params.append(data_ini)
        if data_fim:
            clausulas.append("substr(data_hora,1,10) <= ?")
            params.append(data_fim)
        if cliente:
            clausulas.append("LOWER(cliente) LIKE ?")
            params.append('%' + cliente.lower() + '%')

        ordem_sql = {
            'recente': 'id DESC',
            'antiga': 'id ASC',
            'maior': 'total DESC',
            'menor': 'total ASC',
        }.get(ordem, 'id DESC')

        sql = ("SELECT id, data_hora, subtotal, desconto, total, lucro_total, metodo, itens, cliente, usuario_id, recebido, troco "
               "FROM vendas WHERE " + " AND ".join(clausulas) +
               f" ORDER BY {ordem_sql} LIMIT ?")
        params.append(limite)

        with get_db_context() as conn:
            cursor = conn.execute(sql, params)
            vendas = []
            total_encontrado = 0.0
            for row in cursor.fetchall():
                try:
                    itens = json.loads(row[7]) if row[7] else []
                except Exception:
                    itens = []
                total_encontrado += row[4] or 0
                vendas.append({"id": row[0], "data_hora": row[1], "subtotal": row[2], "desconto": row[3],
                    "total": row[4], "lucro_total": row[5] or 0, "metodo": row[6], "itens": itens,
                    "cliente": row[8] or '', "usuario_id": row[9] or '', "recebido": row[10] or 0, "troco": row[11] or 0})
        return jsonify({"success": True, "vendas": vendas,
                        "quantidade": len(vendas), "total_encontrado": round(total_encontrado, 2)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
@app.route('/api/vendas/<int:venda_id>/cupom')
@verificar_plano
def get_cupom_venda(venda_id: int):
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401
        
        with get_db_context() as conn:
            cursor = conn.execute("""SELECT id, data_hora, subtotal, desconto, total, lucro_total, metodo, itens, cliente, usuario_id, recebido, troco
                FROM vendas WHERE id=? AND db_id=?""", (venda_id, db_id))
            row = cursor.fetchone()
            if not row:
                return jsonify({"success": False, "error": "Venda não encontrada"}), 404
            
            try:
                itens = json.loads(row[7]) if row[7] else []
            except Exception as e:
                logger.error(f"Erro ao parsear itens: {e}")
                itens = []
            
            # Busca dados da loja
            cursor2 = conn.execute("SELECT nome_loja, cnpj, cnpj_dados FROM users WHERE db_id=? LIMIT 1", (db_id,))
            loja = cursor2.fetchone()
            
            cnpj_dados = {}
            if loja and loja[2]:
                try:
                    cnpj_dados = json.loads(loja[2])
                except:
                    pass
            
            # Nome do operador de caixa que realizou a venda
            usuario_id_venda = row[9] or ''
            nome_operador = session.get('nome', '')
            if usuario_id_venda:
                cursor3 = conn.execute("SELECT nome FROM users WHERE id=?", (usuario_id_venda,))
                u = cursor3.fetchone()
                if u and u[0]:
                    nome_operador = u[0]
            
            dados = {
                'venda_id': row[0],
                'data_hora': row[1],
                'subtotal': row[2],
                'desconto': row[3],
                'total': row[4],
                'lucro_total': row[5] or 0,
                'metodo': row[6],
                'itens': itens,
                'cliente': row[8] or '',
                'usuario': nome_operador or '',
                'nome_loja': loja[0] if loja else session.get('nome_loja', 'Minha Loja'),
                'cnpj': loja[1] if loja else session.get('cnpj', ''),
                'cnpj_dados': cnpj_dados,
                'recebido': row[10] or 0,
                'troco': row[11] or 0
            }
            
            return jsonify({"success": True, "dados": dados})
    except Exception as e:
        logger.error(f"Erro ao buscar cupom: {e}")
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# CAIXA
# ============================================================
@app.route('/api/caixa/status')
def caixa_status():
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"aberto": False})
        with get_db_context() as conn:
            cursor = conn.execute("""SELECT id, usuario_id, valor_abertura, data_abertura, total
                FROM caixa WHERE db_id=? AND status='aberto' ORDER BY id DESC LIMIT 1""", (db_id,))
            result = cursor.fetchone()
            nome_usuario = None
            if result and result[1]:
                cur2 = conn.execute("SELECT nome FROM users WHERE id=?", (result[1],))
                row_u = cur2.fetchone()
                if row_u:
                    nome_usuario = row_u[0]
        if result:
            return jsonify({"aberto": True, "id": result[0], "usuario_id": result[1],
                "usuario_nome": nome_usuario or result[1],
                "valor_abertura": result[2], "data_abertura": result[3], "total": result[4] or 0})
        return jsonify({"aberto": False})
    except Exception as e:
        return jsonify({"aberto": False, "error": str(e)})

@app.route('/api/caixa/abrir', methods=['POST'])
@verificar_plano
def caixa_abrir():
    try:
        data = request.json or {}
        db_id = get_db_id()
        usuario_id = get_usuario_id()
        with get_db_context() as conn:
            cursor = conn.execute("SELECT id FROM caixa WHERE db_id=? AND status='aberto'", (db_id,))
            if cursor.fetchone():
                return jsonify({"success": False, "error": "Caixa já está aberto"})
            conn.execute("INSERT INTO caixa (usuario_id, valor_abertura, data_abertura, status, db_id) VALUES (?, ?, ?, 'aberto', ?)",
                (usuario_id, data.get('valor', 0), get_timestamp(), db_id))
        sincronizar_automatico(db_id)
        return jsonify({"success": True, "message": "Caixa aberto"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/caixa/fechar', methods=['POST'])
@verificar_plano
def caixa_fechar():
    try:
        db_id = get_db_id()
        hoje = datetime.now().strftime('%Y-%m-%d')
        with get_db_context() as conn:
            cursor = conn.execute("SELECT SUM(total) FROM vendas WHERE db_id=? AND data_hora LIKE ?", (db_id, f'{hoje}%'))
            total = cursor.fetchone()[0] or 0
            conn.execute("UPDATE caixa SET status='fechado', data_fechamento=?, total=? WHERE db_id=? AND status='aberto'",
                (get_timestamp(), total, db_id))
        sincronizar_automatico(db_id)
        return jsonify({"success": True, "total": total})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/caixa/resumo')
@verificar_plano
def caixa_resumo():
    try:
        db_id = get_db_id()
        data_param = request.args.get('data', datetime.now().strftime('%Y-%m-%d'))
        with get_db_context() as conn:
            cursor = conn.execute("""SELECT metodo, COUNT(*), SUM(total) FROM vendas
                WHERE db_id=? AND data_hora LIKE ? GROUP BY metodo""", (db_id, f'{data_param}%'))
            metodos = [{"metodo": row[0], "quantidade": row[1], "total": row[2] or 0} for row in cursor.fetchall()]
            cursor = conn.execute("SELECT SUM(total), COUNT(*) FROM vendas WHERE db_id=? AND data_hora LIKE ?",
                (db_id, f'{data_param}%'))
            totals = cursor.fetchone()

            caixa_aberto = conn.execute("SELECT id, valor_abertura FROM caixa WHERE db_id=? AND status='aberto' ORDER BY id DESC LIMIT 1", (db_id,)).fetchone()
            valor_abertura = caixa_aberto[1] if caixa_aberto else 0
            movimentos = []
            total_sangrias = 0
            total_suprimentos = 0
            if caixa_aberto:
                cursor = conn.execute("""SELECT id, tipo, valor, motivo, data_hora FROM caixa_movimentos
                    WHERE caixa_id=? AND db_id=? ORDER BY id DESC""", (caixa_aberto[0], db_id))
                for row in cursor.fetchall():
                    movimentos.append({"id": row[0], "tipo": row[1], "valor": row[2], "motivo": row[3] or '', "data_hora": row[4]})
                    if row[1] == 'sangria':
                        total_sangrias += row[2]
                    else:
                        total_suprimentos += row[2]

            total_dinheiro = sum(m['total'] for m in metodos if (m['metodo'] or '').lower() == 'dinheiro')
            esperado_em_caixa = valor_abertura + total_dinheiro - total_sangrias + total_suprimentos

        return jsonify({"success": True, "data": data_param, "total_geral": totals[0] or 0,
            "total_vendas": totals[1] or 0, "metodos": metodos, "movimentos": movimentos,
            "valor_abertura": valor_abertura, "total_sangrias": total_sangrias,
            "total_suprimentos": total_suprimentos, "esperado_em_caixa": esperado_em_caixa})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/caixa/movimento', methods=['POST'])
@verificar_plano
def caixa_movimento():
    try:
        db_id = get_db_id()
        usuario_id = get_usuario_id()
        data = request.json or {}
        tipo = data.get('tipo')
        if tipo not in ('sangria', 'suprimento'):
            return jsonify({"success": False, "error": "Tipo inválido (use 'sangria' ou 'suprimento')"})
        try:
            valor = float(data.get('valor', 0))
        except (TypeError, ValueError):
            valor = 0
        if valor <= 0:
            return jsonify({"success": False, "error": "Informe um valor maior que zero"})
        motivo = (data.get('motivo') or '').strip()[:200]

        with get_db_context() as conn:
            caixa_aberto = conn.execute("SELECT id FROM caixa WHERE db_id=? AND status='aberto' ORDER BY id DESC LIMIT 1", (db_id,)).fetchone()
            if not caixa_aberto:
                return jsonify({"success": False, "error": "Abra o caixa antes de registrar sangria/suprimento"})
            conn.execute("""INSERT INTO caixa_movimentos (caixa_id, tipo, valor, motivo, usuario_id, data_hora, db_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)""", (caixa_aberto[0], tipo, valor, motivo, usuario_id, get_timestamp(), db_id))
        sincronizar_automatico(db_id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# ESTATÍSTICAS - COM PERMISSÃO DASHBOARD
# ============================================================
@app.route('/api/estatisticas')
@verificar_permissao('dashboard')
@verificar_plano
def get_estatisticas():
    try:
        db_id = get_db_id()
        periodo = request.args.get('periodo', 'hoje')
        hoje = datetime.now()
        with get_db_context() as conn:
            if periodo == "hoje":
                filtro = hoje.strftime('%Y-%m-%d') + '%'
                cursor = conn.execute("""SELECT id, data_hora, subtotal, desconto, total, lucro_total, metodo, itens, cliente
                    FROM vendas WHERE db_id=? AND data_hora LIKE ? ORDER BY id DESC LIMIT 100""", (db_id, filtro))
            elif periodo == "semana":
                filtro_data = (hoje - timedelta(days=7)).strftime('%Y-%m-%d')
                cursor = conn.execute("""SELECT id, data_hora, subtotal, desconto, total, lucro_total, metodo, itens, cliente
                    FROM vendas WHERE db_id=? AND data_hora >= ? ORDER BY id DESC LIMIT 200""", (db_id, filtro_data))
            elif periodo == "mes":
                filtro_data = (hoje - timedelta(days=30)).strftime('%Y-%m-%d')
                cursor = conn.execute("""SELECT id, data_hora, subtotal, desconto, total, lucro_total, metodo, itens, cliente
                    FROM vendas WHERE db_id=? AND data_hora >= ? ORDER BY id DESC LIMIT 500""", (db_id, filtro_data))
            else:
                filtro = hoje.strftime('%Y-%m-%d') + '%'
                cursor = conn.execute("""SELECT id, data_hora, subtotal, desconto, total, lucro_total, metodo, itens, cliente
                    FROM vendas WHERE db_id=? AND data_hora LIKE ? ORDER BY id DESC LIMIT 100""", (db_id, filtro))
            
            total_geral = 0
            total_lucro = 0
            total_vendas = 0
            total_itens = 0
            metodos = {}
            vendas = []
            for row in cursor.fetchall():
                total_geral += row[4] or 0
                total_lucro += row[5] or 0
                total_vendas += 1
                metodo = row[6] or 'Dinheiro'
                metodos[metodo] = metodos.get(metodo, 0) + (row[4] or 0)
                try:
                    itens = json.loads(row[7]) if row[7] else []
                    # A venda pode vir de outro dispositivo com 'itens' em formatos
                    # inesperados (string dupla, lista de strings, etc). O dashboard
                    # só sabe trabalhar com lista de dicionários — então filtramos.
                    if isinstance(itens, str):
                        itens = json.loads(itens) if itens.strip().startswith('[') else []
                    if not isinstance(itens, list):
                        itens = []
                    itens = [i for i in itens if isinstance(i, dict)]
                except Exception:
                    itens = []
                total_itens += sum((i.get('quantidade', 1) or 1) for i in itens)
                vendas.append({"id": row[0], "data_hora": row[1], "subtotal": row[2], "desconto": row[3],
                    "total": row[4], "lucro_total": row[5] or 0, "metodo": metodo, "itens": itens, "cliente": row[8] or ''})

            if vendas:
                ids_vendas = [v['id'] for v in vendas]
                placeholders = ','.join('?' * len(ids_vendas))
                ids_com_nfce = {r[0] for r in conn.execute(
                    f"SELECT venda_id FROM fiscal_nfce WHERE db_id=? AND (autorizada=1 OR pendente_reenvio=1) AND venda_id IN ({placeholders})",
                    (db_id, *ids_vendas))}
                for v in vendas:
                    v['tem_nfce'] = v['id'] in ids_com_nfce

            # ---- Dados EXTRA do dashboard (só leitura, não altera nada) ----
            # 1) Ranking de produtos mais vendidos (a partir dos itens já lidos)
            ranking = {}
            for v in vendas:
                for it in v['itens']:
                    # Pula quitações de fiado: elas entram como "item" da venda para
                    # o faturamento, mas NÃO são produtos que saíram da prateleira,
                    # então não podem poluir o ranking. Identificamos pelo código
                    # vazio + nome de quitação.
                    nome_it = it.get('nome') or it.get('codigo') or 'Item'
                    if not (it.get('codigo') or '').strip() and str(nome_it).startswith('Quitação de fiado'):
                        continue
                    q = it.get('quantidade', 1) or 1
                    val = it.get('total')
                    if val is None:
                        val = (it.get('preco_unitario') or it.get('preco') or 0) * q
                    d = ranking.setdefault(nome_it, {'nome': nome_it, 'qtd': 0, 'total': 0.0, 'lucro': 0.0})
                    d['qtd'] += q
                    d['total'] += float(val or 0)
                    # lucro do item (se o frontend mandou); serve pro "mais lucrativo"
                    lucro_it = it.get('lucro')
                    if lucro_it is None:
                        cu = it.get('custo_unitario') or it.get('custo') or 0
                        pu = it.get('preco_unitario') or it.get('preco') or 0
                        lucro_it = (pu - cu) * q
                    d['lucro'] += float(lucro_it or 0)
            mais_vendidos = sorted(ranking.values(), key=lambda x: x['qtd'], reverse=True)[:5]
            # produto que mais deu LUCRO (diferente do que mais vendeu)
            mais_lucrativos = sorted(ranking.values(), key=lambda x: x['lucro'], reverse=True)[:5]

            # 2) Vendas por hora (para um gráfico simples de movimento)
            por_hora = {}
            for v in vendas:
                try:
                    h = int(str(v['data_hora'])[11:13])
                except Exception:
                    h = 0
                por_hora[h] = por_hora.get(h, 0) + (v['total'] or 0)
            vendas_por_hora = [{'hora': h, 'total': round(por_hora.get(h, 0), 2)} for h in range(24)]

            # 3) Fiado a receber e estoque baixo (independem do período)
            fiado_receber = conn.execute(
                "SELECT COALESCE(SUM(divida),0), COUNT(*) FROM clientes WHERE db_id=? AND divida > 0.005",
                (db_id,)).fetchone()
            top_devedores = [
                {'nome': r[0], 'divida': round(r[1], 2)}
                for r in conn.execute(
                    "SELECT nome, divida FROM clientes WHERE db_id=? AND divida > 0.005 ORDER BY divida DESC LIMIT 5",
                    (db_id,)).fetchall()]
            LIMITE_BAIXO = 5
            estoque_baixo = [
                {'codigo': r[0], 'nome': r[1], 'estoque': r[2]}
                for r in conn.execute(
                    "SELECT codigo, nome, estoque FROM produtos WHERE db_id=? AND estoque <= ? ORDER BY estoque ASC LIMIT 8",
                    (db_id, LIMITE_BAIXO)).fetchall()]

            # 4) Fiado vs À vista (do PERÍODO): separa o que já entrou no caixa do
            #    que saiu fiado. Cuidado com dois pontos que geravam erro:
            #    - "Fiado (Dinheiro/PIX/...)" é uma QUITAÇÃO: o dinheiro ENTROU,
            #      então conta como à vista, não como fiado.
            #    - Só "Fiado" puro é venda a prazo (ainda não entrou).
            def _e_quitacao(m):
                return m.startswith('Fiado (')
            def _e_fiado_puro(m):
                return m == 'Fiado'
            total_fiado_vendas = sum((v['total'] or 0) for v in vendas if _e_fiado_puro(v['metodo'] or ''))
            total_avista = sum((v['total'] or 0) for v in vendas if not _e_fiado_puro(v['metodo'] or ''))
            pct_fiado = (total_fiado_vendas / total_geral * 100) if total_geral > 0 else 0
            # "A receber" de verdade = dívida em aberto AGORA (não o histórico do mês).
            # É o mesmo número do card de fiado (fiado_receber[0]).
            fiado_a_receber_agora = round(fiado_receber[0], 2)

            # 5) Comparativo com o período anterior (mesmo tamanho de janela)
            if periodo == 'hoje':
                ini_ant = (hoje - timedelta(days=1)).strftime('%Y-%m-%d')
                fim_ant = ini_ant
                row_ant = conn.execute(
                    "SELECT COALESCE(SUM(total),0), COUNT(*) FROM vendas WHERE db_id=? AND data_hora LIKE ?",
                    (db_id, ini_ant + '%')).fetchone()
            elif periodo == 'semana':
                ini_ant = (hoje - timedelta(days=14)).strftime('%Y-%m-%d')
                fim_ant = (hoje - timedelta(days=7)).strftime('%Y-%m-%d')
                row_ant = conn.execute(
                    "SELECT COALESCE(SUM(total),0), COUNT(*) FROM vendas WHERE db_id=? AND data_hora >= ? AND data_hora < ?",
                    (db_id, ini_ant, fim_ant)).fetchone()
            elif periodo == 'mes':
                ini_ant = (hoje - timedelta(days=60)).strftime('%Y-%m-%d')
                fim_ant = (hoje - timedelta(days=30)).strftime('%Y-%m-%d')
                row_ant = conn.execute(
                    "SELECT COALESCE(SUM(total),0), COUNT(*) FROM vendas WHERE db_id=? AND data_hora >= ? AND data_hora < ?",
                    (db_id, ini_ant, fim_ant)).fetchone()
            else:
                row_ant = (0, 0)
            total_anterior = row_ant[0] or 0
            if total_anterior > 0:
                variacao_pct = (total_geral - total_anterior) / total_anterior * 100
            else:
                variacao_pct = None  # sem base de comparação

        return jsonify({"success": True, "stats": {
            "total_geral": total_geral,
            "total_lucro": total_lucro,
            "total_vendas": total_vendas,
            "media": total_geral / total_vendas if total_vendas > 0 else 0,
            "media_lucro": total_lucro / total_vendas if total_vendas > 0 else 0,
            "total_itens": total_itens,
            "metodos": metodos,
            "vendas": vendas,
            "mais_vendidos": mais_vendidos,
            "vendas_por_hora": vendas_por_hora,
            "fiado_total": round(fiado_receber[0], 2),
            "fiado_clientes": fiado_receber[1],
            "top_devedores": top_devedores,
            "estoque_baixo": estoque_baixo,
            "mais_lucrativos": mais_lucrativos,
            "total_fiado_vendas": round(total_fiado_vendas, 2),
            "total_avista": round(total_avista, 2),
            "pct_fiado": round(pct_fiado, 1),
            "fiado_a_receber_agora": fiado_a_receber_agora,
            "total_anterior": round(total_anterior, 2),
            "variacao_pct": (round(variacao_pct, 1) if variacao_pct is not None else None)
        }})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# PLANOS
# ============================================================
@app.route('/api/planos')
def get_planos():
    planos_out = []
    for p in PLANOS:
        # Planos ocultos (Empresarial) e o TESTE não aparecem na loja.
        # O teste já vem ativo por padrão ao criar a conta, então não precisa de card.
        if getattr(p, 'oculto', False) or p.is_teste:
            continue
        pd = asdict(p)
        if not p.is_teste and p.preco > 0:
            duracoes = []
            for dur in DURACOES_PLANO:
                preco_final, dias, desconto, economia = calcular_preco_duracao(p.preco, dur["meses"])
                duracoes.append({
                    "meses": dur["meses"],
                    "label": dur["label"],
                    "dias": dias,
                    "desconto_pct": int(dur["desconto"] * 100),
                    "preco_total": preco_final,
                    "preco_mensal_equivalente": round(preco_final / dur["meses"], 2),
                    "economia": economia,
                })
            pd["duracoes"] = duracoes
        planos_out.append(pd)
    return jsonify({"success": True, "planos": planos_out})

@app.route('/api/plano/status')
def get_plano_status():
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401
        # OFFLINE-FIRST: o token local é assinado e já traz plano_id e expira_em.
        # Antes consultávamos o Firebase aqui, e a tela dos Planos ficava presa
        # esperando a internet. Agora respondemos na hora; a atualização do token
        # (renovação, corte) acontece em segundo plano dentro de get_info_plano.
        info = get_info_plano_completa(db_id)

        plano_id = info.get('plano_id', 1)
        plano_obj = next((p for p in PLANOS if p.id == plano_id), PLANOS[0])
        expira = info.get('expira_em')

        dias_restantes = info.get('dias_restantes', 0)
        limite_produtos = plano_obj.produtos if plano_obj else 0
        total_produtos = get_total_produtos(db_id)
        produtos_restantes = -1 if limite_produtos == -1 else max(0, limite_produtos - total_produtos)
        usuarios_atuais = len(get_usuarios_do_plano(db_id))
        precisa_aviso, dias_para_aviso = precisa_aviso_renovacao(db_id)
        percentual = 0
        if limite_produtos != -1 and limite_produtos > 0:
            percentual = min(100, (total_produtos / limite_produtos) * 100)
        permissoes = get_permissoes(db_id)
        is_teste = plano_obj.is_teste if plano_obj else False
        ativo_final = info.get('ativo', False)
        return jsonify({
            "success": True,
            "plano": asdict(plano_obj) if plano_obj else None,
            "expira_em": expira,
            "dias_restantes": dias_restantes,
            "expirado": not info.get('ativo', False),
            "limite_produtos": limite_produtos,
            "produtos_atuais": total_produtos,
            "produtos_restantes": produtos_restantes,
            "percentual_produtos": percentual,
            "usuarios_limite": plano_obj.usuarios if plano_obj else 1,
            "usuarios_atuais": usuarios_atuais,
            "ativo": ativo_final,
            "precisa_aviso": precisa_aviso,
            "dias_para_aviso": dias_para_aviso,
            "permissoes": permissoes,
            "is_teste": is_teste,
            "offline": not _ULTIMO_SYNC_TOKEN.get(db_id),
            "mensagem": info.get('mensagem', ''),
            "url_renovacao": "#/planos"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# PIX
# ============================================================
@app.route('/api/pix/criar', methods=['POST'])
def criar_pix():
    try:
        data = request.json or {}
        plano_id = data.get('plano_id')
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401
        plano = next((p for p in PLANOS if p.id == plano_id), None)
        if not plano:
            return jsonify({"success": False, "error": "Plano inválido"})

        # Duração escolhida (em meses): 1, 3, 6 ou 12. Padrão: 1 mês.
        meses = int(data.get('duracao', data.get('meses', 1)) or 1)
        if meses not in (1, 3, 6, 12):
            meses = 1
        preco_final, dias_plano, desconto, economia = calcular_preco_duracao(plano.preco, meses)

        # Plano gratuito/teste: não existe cobrança real, ativa direto sem chamar o Mercado Pago
        if plano.is_teste or plano.preco <= 0:
            # TRAVA: o teste só pode ser ativado UMA vez por conta (evita renovação infinita)
            if plano.is_teste:
                ja_usou = False
                # 1) Verifica no banco local
                with get_db_context() as conn:
                    cur = conn.execute("SELECT valor FROM config WHERE chave='teste_usado'")
                    row = cur.fetchone()
                    if row and str(row[0]) == '1':
                        ja_usou = True
                # 2) Verifica no Firebase (fonte de verdade entre dispositivos)
                firebase_confirmou = False
                if not ja_usou:
                    dados_fb = carregar_usuario_firebase(db_id, timeout=5)
                    if dados_fb is not None:
                        firebase_confirmou = True
                        if dados_fb.get('teste_usado'):
                            ja_usou = True
                            # espelha no local para acelerar as próximas checagens
                            try:
                                with get_db_context() as conn:
                                    conn.execute("INSERT OR REPLACE INTO config (chave, valor) VALUES ('teste_usado', '1')")
                            except Exception:
                                pass
                # 3) FAIL-CLOSED: se o local não confirma E não conseguimos falar com o Firebase
                #    (ex: internet caiu), NÃO liberamos o teste — evita renovação infinita offline.
                if not ja_usou and not firebase_confirmou:
                    return jsonify({"success": False, "error": "Não foi possível validar o período de teste sem internet. Conecte-se à internet e tente novamente."}), 403
                if ja_usou:
                    return jsonify({"success": False, "error": "O período de teste já foi utilizado nesta conta. Escolha um plano pago para continuar."}), 403
            pix_id = f"gratis_{uuid.uuid4().hex}"
            pagamentos_pendentes[pix_id] = {'db_id': db_id, 'plano_id': plano_id, 'valor': 0, 'pago': False,
                'criado_em': get_timestamp(), 'expira_em': (datetime.now() + timedelta(days=plano.dias)).isoformat()}
            _confirmar_pagamento_plano(pix_id)
            # Marca o teste como usado (local + Firebase) para impedir renovação infinita
            if plano.is_teste:
                try:
                    with get_db_context() as conn:
                        conn.execute("INSERT OR REPLACE INTO config (chave, valor) VALUES ('teste_usado', '1')")
                    # PATCH (só este campo). Com PUT, se a leitura do Firebase
                    # falhasse, o nó do usuário seria substituído só por
                    # 'teste_usado' — apagando email, senha, produtos e vendas.
                    salvar_campos_firebase(db_id, {'teste_usado': True})
                except Exception as e:
                    logger.error(f"⚠️ Erro ao marcar teste usado: {e}")
            return jsonify({"success": True, "pix_id": pix_id, "gratis": True, "valor": 0, "plano": asdict(plano)})

        resultado_pix = criar_pix_backend(db_id, plano_id, meses)
        if resultado_pix and resultado_pix.get('pix_id'):
            pix_id = resultado_pix['pix_id']
            pagamentos_pendentes[pix_id] = {'db_id': db_id, 'plano_id': plano_id, 'valor': preco_final, 'pago': False,
                'meses': meses, 'dias': dias_plano,
                'criado_em': get_timestamp(), 'expira_em': (datetime.now() + timedelta(days=dias_plano)).isoformat()}
            return jsonify({"success": True, "pix_id": pix_id, "qr_code": resultado_pix['qr_code'],
                "qr_code_base64": resultado_pix['qr_code_base64'], "valor": preco_final, "meses": meses,
                "economia": economia, "plano": asdict(plano)})
        # Mostra o motivo real (vindo do backend/Mercado Pago) em vez de esconder
        motivo = (resultado_pix or {}).get('erro', 'Erro desconhecido')
        return jsonify({"success": False, "error": f"Erro ao gerar PIX: {motivo}"})
    except Exception as e:
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
        if verificar_pagamento_backend(pix_id):
            _confirmar_pagamento_plano(pix_id)
            return jsonify({"pago": True})
        return jsonify({"pago": False, "status": "pending"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def _sessao_http() -> requests.Session:
    """Sessão HTTP com retry automático. Conexões cortadas (erro 10054 no Windows,
    comum com antivírus/firewall inspecionando HTTPS) são muito frequentes: sem
    retry, o PIX falha 'aleatoriamente'."""
    s = requests.Session()
    s.headers.update({"User-Agent": "SMART-PDV/11", "Connection": "close"})
    return s

def criar_pix_backend(db_id: str, plano_id: int, meses: int = 1) -> Optional[Dict]:
    """Pede ao NOSSO backend que crie a cobrança PIX do plano.
    O backend é quem fala com o Mercado Pago (só ele tem o token). Enviamos o
    db_id junto: é assim que o pagamento fica amarrado à conta certa, mesmo com
    várias lojas comprando ao mesmo tempo (cada cobrança tem a sua referência).

    Tenta até 3 vezes: quedas de conexão pontuais não podem impedir a venda."""
    # Tempos CURTOS de propósito: esta chamada acontece enquanto o usuário espera
    # olhando a tela. Com timeout de 30s e 3 tentativas, um clique podia travar o
    # navegador por ~95s — e o navegador só permite 6 conexões simultâneas, então
    # alguns cliques congelavam o sistema inteiro. Melhor falhar rápido e avisar.
    ultimo_erro = "erro desconhecido"
    for tentativa in range(2):
        try:
            with _sessao_http() as s:
                res = s.post(f"{BACKEND_PAGAMENTOS_URL}/criar",
                    json={"db_id": db_id, "plano_id": plano_id, "meses": meses}, timeout=10)
            try:
                d = res.json()
            except Exception:
                ultimo_erro = f"resposta inesperada do servidor (HTTP {res.status_code})"
                logger.error(f"❌ {ultimo_erro}")
                _time.sleep(1.0)
                continue
            if res.status_code == 200 and d.get('success'):
                return {"pix_id": d['pix_id'], "qr_code": d.get('qr_code', ''),
                    "qr_code_base64": d.get('qr_code_base64', '')}
            # o servidor respondeu, mas recusou: não adianta tentar de novo
            ultimo_erro = d.get('error') or f"HTTP {res.status_code}"
            logger.error(f"❌ Backend recusou criar PIX: {ultimo_erro}")
            return {"erro": ultimo_erro}
        except Exception as e:
            ultimo_erro = str(e)
            logger.warning(f"⚠️ Falha de conexão ao criar PIX (tentativa {tentativa+1}/2): {e}")
            _time.sleep(0.8)
    return {"erro": f"não foi possível falar com o servidor de pagamentos ({ultimo_erro})"}

def verificar_pagamento_backend(pix_id: str) -> bool:
    """Pergunta ao nosso backend se aquele PIX já foi pago (com retry)."""
    if not pix_id or str(pix_id).startswith('gratis_'):
        return False
    # Também curto: o frontend chama isto de tempos em tempos enquanto o QR está
    # na tela. Se demorar, ele volta a perguntar na próxima rodada.
    for tentativa in range(2):
        try:
            with _sessao_http() as s:
                res = s.get(f"{BACKEND_PAGAMENTOS_URL}/verificar", params={"id": pix_id}, timeout=8)
            if res.status_code == 200:
                return bool(res.json().get('pago'))
            return False
        except Exception as e:
            logger.warning(f"⚠️ Falha ao verificar pagamento (tentativa {tentativa+1}/2): {e}")
            _time.sleep(0.6)
    return False

# Nomes antigos mantidos para não quebrar chamadas existentes
def verificar_pagamento_mercadopago(pix_id: str) -> bool:
    return verificar_pagamento_backend(pix_id)

def _confirmar_pagamento_plano(pix_id: str) -> None:
    info = pagamentos_pendentes.get(pix_id)
    if not info or info.get('pago'):
        return
    info['pago'] = True
    db_id = info['db_id']
    plano_id = info['plano_id']
    plano = next((p for p in PLANOS if p.id == plano_id), None)
    if not plano:
        return
    # Usa os dias da duração comprada (1, 3, 6 ou 12 meses); senão, padrão do plano
    dias = info.get('dias') or plano.dias
    expira_em = (datetime.now() + timedelta(days=dias)).isoformat()
    plano_obj = PlanoSincronizado(db_id, CHAVE_SECRETA_PLANO)
    resultado = plano_obj.renovar_plano(expira_em, plano_id, pix_id=pix_id)
    if resultado.get('success'):
        logger.info(f"✅ Pagamento confirmado e plano renovado para {db_id} até {expira_em}")
    else:
        logger.error(f"❌ Falha ao renovar plano para {db_id}: {resultado.get('error')}")

# ============================================================
# USUÁRIOS
# ============================================================
@app.route('/api/usuarios')
@verificar_plano
def get_usuarios():
    try:
        db_id = get_db_id()
        with get_db_context() as conn:
            cursor = conn.execute("""SELECT id, nome, email, cargo, criado_em, ultimo_acesso, session_id
                FROM users WHERE db_id=? ORDER BY criado_em ASC""", (db_id,))
            usuarios = []
            for row in cursor.fetchall():
                u = dict(row)
                u['online'] = bool(u['session_id'] and u['session_id'] in SESSOES_ATIVAS)
                usuarios.append(u)
        plano = get_plano_efetivo(db_id)
        return jsonify({"success": True, "usuarios": usuarios, "limite_usuarios": plano.usuarios,
            "usuarios_atuais": len(usuarios)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/usuarios', methods=['POST'])
@verificar_plano
def criar_usuario():
    try:
        data = request.json or {}
        db_id = get_db_id()
        nome = (data.get('nome') or '').strip()
        email = (data.get('email') or '').strip().lower()
        senha = data.get('senha') or ''
        if not nome or not email or not senha:
            return jsonify({"success": False, "error": "Preencha nome, email e senha"})
        plano = get_plano_efetivo(db_id)
        if not plano:
            return jsonify({"success": False, "error": "Plano inválido"})
        with get_db_context() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM users WHERE db_id=?", (db_id,))
            total = cursor.fetchone()[0]
            if total >= plano.usuarios:
                return jsonify({"success": False, "error": f"Limite de {plano.usuarios} usuário(s) atingido."})
            cursor = conn.execute("SELECT id FROM users WHERE email=?", (email,))
            if cursor.fetchone():
                return jsonify({"success": False, "error": "Email já cadastrado"})
            user_id = str(uuid.uuid4())[:8]
            conn.execute("""INSERT INTO users (id, nome, email, senha, cargo, db_id, servidor_id, nome_loja, cnpj)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (user_id, nome, email, gerar_hash_senha(senha),
                data.get('cargo', 'Funcionario'), db_id, SERVIDOR_ID, session.get('nome_loja', ''), session.get('cnpj', '')))
        return jsonify({"success": True, "message": "Usuário criado!",
            "usuario": {"id": user_id, "nome": nome, "email": email, "cargo": data.get('cargo', 'Funcionario')}})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/usuarios/<user_id>', methods=['DELETE'])
@verificar_plano
def delete_usuario(user_id: str):
    try:
        db_id = get_db_id()
        if user_id == get_usuario_id():
            return jsonify({"success": False, "error": "Não é possível excluir seu próprio usuário"})
        with get_db_context() as conn:
            cursor = conn.execute("SELECT id FROM users WHERE id=? AND db_id=?", (user_id, db_id))
            if not cursor.fetchone():
                return jsonify({"success": False, "error": "Usuário não encontrado"})
            conn.execute("DELETE FROM users WHERE id=? AND db_id=?", (user_id, db_id))
        return jsonify({"success": True, "message": "Usuário excluído"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# LOJA
# ============================================================
# 🔧 allowlist das ÚNICAS colunas que _sincronizar_preferencia_bg pode
# atualizar. O nome da coluna vem de um parâmetro (campo_ts) interpolado
# direto no SQL - hoje as duas chamadas existentes usam sempre literais fixos
# (nunca dado do usuário), mas sem essa trava seria um SQL injection pronto
# pra acontecer no dia em que alguém passasse algo vindo de request.json.
_COLUNAS_TS_PERMITIDAS = {'bg_vendas_img_ts', 'bg_vendas_opacidade_ts'}

def _sincronizar_preferencia_bg(db_id: str, campo: str, valor, campo_ts: str) -> None:
    """Sobe a preferência para o Firebase e corrige o carimbo de hora com a hora
    do SERVIDOR (para o "mais recente vence" funcionar mesmo se o relógio do PC
    estiver errado). Roda em segundo plano: o usuário já viu a mudança aplicada."""
    if campo_ts not in _COLUNAS_TS_PERMITIDAS:
        logger.error(f"❌ _sincronizar_preferencia_bg: coluna '{campo_ts}' não permitida - abortando")
        return
    ts = ler_timestamp_online()
    if ts:
        try:
            with get_db_context() as conn:
                conn.execute(f"UPDATE users SET {campo_ts}=? WHERE db_id=?", (ts, db_id))
        except Exception as e:
            logger.warning(f"⚠️ Não consegui carimbar a hora de {campo}: {e}")
    salvar_preferencia_firebase(db_id, campo, valor)


@app.route('/api/loja/nome', methods=['POST'])
@verificar_plano
def salvar_nome_loja():
    try:
        data = request.json or {}
        db_id = get_db_id()
        nome = (data.get('nome') or '').strip()
        cnpj = ''.join(filter(str.isdigit, data.get('cnpj') or ''))
        cnpj_dados = data.get('cnpj_dados', {})
        if not nome:
            return jsonify({"success": False, "error": "Nome da loja é obrigatório"})
        with get_db_context() as conn:
            conn.execute("UPDATE users SET nome_loja=?, cnpj=?, cnpj_dados=? WHERE db_id=?",
                (nome, cnpj, json.dumps(cnpj_dados, ensure_ascii=False), db_id))
        session['nome_loja'] = nome
        session['cnpj'] = cnpj
        session['cnpj_dados'] = cnpj_dados
        # OFFLINE-FIRST: o nome já está no banco local; subir para a nuvem é
        # tarefa de fundo. Usamos PATCH (não PUT) para não sobrescrever alterações
        # feitas em outro caixa entre a leitura e a gravação.
        em_segundo_plano(salvar_campos_firebase, db_id,
            {'nome_loja': nome, 'cnpj': cnpj, 'cnpj_dados': cnpj_dados})
        return jsonify({"success": True, "message": "Informações salvas!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/loja/info')
def get_loja_info():
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401
        with get_db_context() as conn:
            cursor = conn.execute("SELECT nome_loja, cnpj, cnpj_dados FROM users WHERE db_id=? LIMIT 1", (db_id,))
            result = cursor.fetchone()
        cnpj_dados = {}
        if result and result[2]:
            try:
                cnpj_dados = json.loads(result[2])
            except:
                pass
        return jsonify({
            "success": True,
            "nome_loja": result[0] if result else 'Minha Loja',
            "cnpj": result[1] if result else '',
            "cnpj_dados": cnpj_dados
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# PERSONALIZAÇÃO - Fundo da tela de vendas
# ============================================================
@app.route('/api/loja/background', methods=['POST'])
@verificar_plano
def salvar_background():
    try:
        data = request.json or {}
        db_id = get_db_id()
        img = data.get('img', '')  # URL ou data-URL (base64)
        opacidade = int(data.get('opacidade', 50))
        opacidade = max(0, min(100, opacidade))
        # OFFLINE-FIRST: aplica local e responde JÁ. Antes esperava TRÊS chamadas
        # de rede (hora do servidor + 2 gravações) — ~6s com internet ruim.
        ts_local = int(_time.time() * 1000)
        with get_db_context() as conn:
            conn.execute("UPDATE users SET bg_vendas_img=?, bg_vendas_opacidade=?, bg_vendas_img_ts=?, bg_vendas_opacidade_ts=? WHERE db_id=?",
                (img, opacidade, ts_local, ts_local, db_id))
        def _subir_fundo():
            _sincronizar_preferencia_bg(db_id, 'bg_vendas_img', img, 'bg_vendas_img_ts')
            _sincronizar_preferencia_bg(db_id, 'bg_vendas_opacidade', opacidade, 'bg_vendas_opacidade_ts')
        em_segundo_plano(_subir_fundo)
        return jsonify({"success": True, "message": "Fundo salvo!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def _atualizar_background_do_firebase(db_id: str) -> None:
    """Puxa a preferência de fundo do Firebase e guarda no banco local se ela for
    mais nova. Roda em SEGUNDO PLANO: quem abre a tela vê o valor local na hora,
    e o valor de outro aparelho aparece no próximo carregamento."""
    dados = carregar_usuario_firebase(db_id, timeout=6)
    if dados is None:
        return
    with get_db_context() as conn:
        row = conn.execute("SELECT bg_vendas_img, bg_vendas_opacidade, bg_vendas_img_ts, bg_vendas_opacidade_ts FROM users WHERE db_id=? LIMIT 1", (db_id,)).fetchone()
        img_local = (row[0] if row else '') or ''
        opac_local = (row[1] if row and row[1] is not None else 50)
        img_ts_local = (row[2] if row else 0) or 0
        opac_ts_local = (row[3] if row else 0) or 0

        img_fb = dados.get('bg_vendas_img', None)
        img_ts_fb = dados.get('bg_vendas_img_ts', 0) or 0
        opac_fb = dados.get('bg_vendas_opacidade', None)
        opac_ts_fb = dados.get('bg_vendas_opacidade_ts', 0) or 0

        img_final, img_ts_final = img_local, img_ts_local
        if img_fb:
            if (not img_local) or (img_ts_fb > img_ts_local):
                img_final, img_ts_final = img_fb, img_ts_fb
        elif img_fb == '' and img_ts_fb > img_ts_local:
            img_final, img_ts_final = '', img_ts_fb

        opac_final, opac_ts_final = opac_local, opac_ts_local
        if opac_fb is not None and (opac_ts_fb > opac_ts_local or (opac_ts_fb == 0 and img_final == img_fb)):
            opac_final, opac_ts_final = opac_fb, opac_ts_fb

        conn.execute("UPDATE users SET bg_vendas_img=?, bg_vendas_opacidade=?, bg_vendas_img_ts=?, bg_vendas_opacidade_ts=? WHERE db_id=?",
            (img_final, opac_final, img_ts_final, opac_ts_final, db_id))


@app.route('/api/loja/background')
def get_background():
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401
        # OFFLINE-FIRST: responde com o valor LOCAL na hora. Antes esperávamos o
        # Firebase aqui, e a tela de vendas demorava a abrir com internet ruim.
        # A checagem do que veio de outro aparelho roda em segundo plano.
        img_local, opac_local = '', 50
        with get_db_context() as conn:
            row = conn.execute("SELECT bg_vendas_img, bg_vendas_opacidade FROM users WHERE db_id=? LIMIT 1", (db_id,)).fetchone()
            if row:
                img_local = row[0] or ''
                opac_local = row[1] if row[1] is not None else 50
        em_segundo_plano(_atualizar_background_do_firebase, db_id)
        return jsonify({"success": True, "img": img_local, "opacidade": opac_local})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/loja/escala', methods=['POST'])
@verificar_plano
def salvar_escala():
    try:
        data = request.json or {}
        db_id = get_db_id()
        escala = int(data.get('escala', 100))
        escala = max(100, min(180, escala))
        # OFFLINE-FIRST: grava local com a hora do PC e responde JÁ. A hora do
        # servidor e o envio ao Firebase acontecem em segundo plano. Antes, salvar
        # o tamanho da letra esperava DUAS chamadas de rede (~4s com internet ruim).
        ts_local = int(_time.time() * 1000)
        with get_db_context() as conn:
            conn.execute("UPDATE users SET escala_sistema=?, escala_sistema_ts=? WHERE db_id=?", (escala, ts_local, db_id))
        em_segundo_plano(_sincronizar_preferencia_bg, db_id, 'escala_sistema', escala, 'escala_sistema_ts')
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def _atualizar_escala_do_firebase(db_id: str) -> None:
    """Puxa a escala do Firebase em segundo plano; o mais recente vence."""
    dados = carregar_usuario_firebase(db_id, timeout=6)
    if dados is None:
        return
    escala_fb = dados.get('escala_sistema', None)
    ts_fb = dados.get('escala_sistema_ts', 0) or 0
    if escala_fb is None:
        return
    with get_db_context() as conn:
        row = conn.execute("SELECT escala_sistema_ts FROM users WHERE db_id=? LIMIT 1", (db_id,)).fetchone()
        ts_local = (row[0] if row else 0) or 0
        if ts_fb > ts_local:
            conn.execute("UPDATE users SET escala_sistema=?, escala_sistema_ts=? WHERE db_id=?",
                (int(escala_fb), ts_fb, db_id))


@app.route('/api/loja/escala')
def get_escala():
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401
        # OFFLINE-FIRST: devolve o valor local imediatamente; a conferência com o
        # Firebase acontece em segundo plano (aparece no próximo carregamento).
        escala_local = 100
        with get_db_context() as conn:
            row = conn.execute("SELECT escala_sistema FROM users WHERE db_id=? LIMIT 1", (db_id,)).fetchone()
            if row and row[0]:
                escala_local = row[0]
        em_segundo_plano(_atualizar_escala_do_firebase, db_id)
        return jsonify({"success": True, "escala": int(escala_local)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/login/lembrar', methods=['POST'])
def salvar_login_lembrado():
    try:
        data = request.json or {}
        email = data.get('email', '')
        senha = data.get('senha', '')
        lembrar = data.get('lembrar', True)
        if not lembrar or not email:
            # limpar
            try:
                if os.path.exists(_ARQUIVO_LOGIN):
                    os.remove(_ARQUIVO_LOGIN)
            except Exception:
                pass
            return jsonify({"success": True})
        # Guarda APENAS o usuário (nunca a senha), por segurança.
        conteudo = json.dumps({"email": email, "senha": ""})
        try:
            with open(_ARQUIVO_LOGIN, 'w', encoding='utf-8') as f:
                f.write(base64.b64encode(conteudo.encode('utf-8')).decode('ascii'))
        except Exception:
            pass
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/login/lembrar')
def get_login_lembrado():
    try:
        if not os.path.exists(_ARQUIVO_LOGIN):
            return jsonify({"success": True, "email": "", "senha": ""})
        dados_raw = open(_ARQUIVO_LOGIN, 'rb').read()
        conteudo = None
        try:
            conteudo = base64.b64decode(dados_raw).decode('utf-8')
        except Exception:
            conteudo = None
        if not conteudo:
            return jsonify({"success": True, "email": "", "senha": ""})
        d = json.loads(conteudo)
        return jsonify({"success": True, "email": d.get("email", ""), "senha": d.get("senha", "")})
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "email": "", "senha": ""})

# ============================================================
# CNPJ
# ============================================================
@app.route('/api/cnpj/<cnpj>')
def buscar_cnpj(cnpj: str):
    try:
        cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
        if len(cnpj_limpo) != 14:
            return jsonify({"success": False, "error": "CNPJ inválido. Deve ter 14 dígitos."})
        if cnpj_limpo in CACHE_CNPJ:
            cache_data = CACHE_CNPJ[cnpj_limpo]
            if _time.time() - cache_data['timestamp'] < 86400:
                return jsonify({"success": True, "dados": cache_data['dados'], "fonte": "cache"})
        apis = [
            f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}",
            f"https://api.opencnpj.org/{cnpj_limpo}",
            f"https://publica.cnpj.ws/cnpj/{cnpj_limpo}",
            f"https://www.receitaws.com.br/v1/cnpj/{cnpj_limpo}",
        ]
        for url in apis:
            try:
                response = requests.get(url, timeout=12, headers={"User-Agent": "SMART-PDV/10.0"})
                if response.status_code != 200:
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
                    continue
                dados = _normalizar_cnpj_dados(flat)
                CACHE_CNPJ[cnpj_limpo] = {'dados': dados, 'timestamp': _time.time()}
                return jsonify({"success": True, "dados": dados, "fonte": url.split('/')[2]})
            except:
                continue
        return jsonify({"success": False, "error": "CNPJ não encontrado em nenhuma fonte disponível"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# IMPRESSÃO
# ============================================================
@app.route('/api/config/impressora', methods=['GET'])
def obter_config_impressora_route():
    try:
        if not get_db_id():
            return jsonify({"success": False, "error": "Não autenticado"}), 401
        return jsonify({"success": True, "ip_rede": _config_obter('impressora_ip_rede')})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/config/impressora', methods=['POST'])
def definir_config_impressora_route():
    try:
        if not get_db_id():
            return jsonify({"success": False, "error": "Não autenticado"}), 401
        ip_rede = (request.json or {}).get('ip_rede', '').strip()
        _config_definir('impressora_ip_rede', ip_rede)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# NOTA FISCAL (NFC-e) - ROTAS
# ============================================================
UFS_VALIDAS = {"AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG",
    "PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"}

@app.route('/api/config/fiscal', methods=['GET'])
def obter_config_fiscal_route():
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401
        tem_certificado = os.path.exists(CAMINHO_CERTIFICADO_PFX)
        with get_db_context() as conn:
            row = conn.execute("SELECT inscricao_estadual, regime_tributario FROM users WHERE db_id=? LIMIT 1", (db_id,)).fetchone()
        return jsonify({
            "success": True,
            "tem_certificado": tem_certificado,
            "validade_certificado": _config_obter('fiscal_validade_certificado'),
            "titular_certificado": _config_obter('fiscal_titular_certificado'),
            "uf": _config_obter('fiscal_uf'),
            "ambiente": _config_obter('fiscal_ambiente', 'homologacao'),
            "csc_id": _config_obter('fiscal_csc_id'),
            "tem_csc_token": bool(_config_obter('fiscal_csc_token_enc')),
            "serie": _config_obter('fiscal_serie', '1'),
            "proximo_numero": _config_obter('fiscal_proximo_numero', '1'),
            "inscricao_estadual": (row[0] if row else '') or '',
            "regime_tributario": (row[1] if row else '1') or '1',
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/config/fiscal', methods=['POST'])
def definir_config_fiscal_route():
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401
        data = request.json or {}
        uf = (data.get('uf') or '').strip().upper()
        if uf and uf not in UFS_VALIDAS:
            return jsonify({"success": False, "error": f"UF inválida: {uf}"})
        ambiente = (data.get('ambiente') or 'homologacao').strip().lower()
        if ambiente not in ('homologacao', 'producao'):
            return jsonify({"success": False, "error": "Ambiente deve ser 'homologacao' ou 'producao'"})
        regime = (data.get('regime_tributario') or '1').strip()
        if regime not in ('1', '2', '3'):
            return jsonify({"success": False, "error": "Regime tributário inválido"})
        if uf:
            _config_definir('fiscal_uf', uf)
        _config_definir('fiscal_ambiente', ambiente)
        if 'csc_id' in data:
            _config_definir('fiscal_csc_id', (data.get('csc_id') or '').strip())
        if data.get('csc_token'):
            _config_definir('fiscal_csc_token_enc', _fiscal_cifrar(data['csc_token'].strip()))
        if 'serie' in data:
            _config_definir('fiscal_serie', str(data.get('serie') or '1').strip())
        if 'proximo_numero' in data:
            _config_definir('fiscal_proximo_numero', str(data.get('proximo_numero') or '1').strip())
        with get_db_context() as conn:
            conn.execute("UPDATE users SET inscricao_estadual=?, regime_tributario=? WHERE db_id=?",
                ((data.get('inscricao_estadual') or '').strip(), regime, db_id))
            conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/config/fiscal/certificado', methods=['POST'])
def enviar_certificado_fiscal_route():
    try:
        if not get_db_id():
            return jsonify({"success": False, "error": "Não autenticado"}), 401
        arquivo = request.files.get('certificado')
        senha = request.form.get('senha', '')
        if not arquivo or not arquivo.filename:
            return jsonify({"success": False, "error": "Selecione o arquivo do certificado (.pfx ou .p12)"})
        conteudo = arquivo.read()
        if len(conteudo) > 10 * 1024 * 1024:
            return jsonify({"success": False, "error": "Arquivo grande demais pra ser um certificado válido"})

        # Valida o arquivo E a senha juntos, tentando abrir o PKCS12 de verdade -
        # assim o erro aparece na hora do envio, não só quando for tentar emitir.
        try:
            chave_privada, certificado, _outros = pkcs12.load_key_and_certificates(conteudo, senha.encode())
            if chave_privada is None or certificado is None:
                return jsonify({"success": False, "error": "O arquivo não contém uma chave privada e certificado válidos"})
        except Exception as e:
            return jsonify({"success": False, "error": f"Não consegui abrir o certificado — senha incorreta ou arquivo inválido ({e})"})

        validade = certificado.not_valid_after_utc.strftime('%d/%m/%Y') if hasattr(certificado, 'not_valid_after_utc') else certificado.not_valid_after.strftime('%d/%m/%Y')
        try:
            titular = certificado.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
        except Exception:
            titular = ''

        with open(CAMINHO_CERTIFICADO_PFX, 'wb') as f:
            f.write(conteudo)
        _config_definir('fiscal_senha_certificado_enc', _fiscal_cifrar(senha))
        _config_definir('fiscal_validade_certificado', validade)
        _config_definir('fiscal_titular_certificado', titular)

        logger.info(f"✅ Certificado fiscal recebido (válido até {validade})")
        return jsonify({"success": True, "validade": validade, "titular": titular})
    except Exception as e:
        logger.error(f"❌ Erro ao processar certificado fiscal: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/config/fiscal/certificado', methods=['DELETE'])
def remover_certificado_fiscal_route():
    try:
        if not get_db_id():
            return jsonify({"success": False, "error": "Não autenticado"}), 401
        if os.path.exists(CAMINHO_CERTIFICADO_PFX):
            os.remove(CAMINHO_CERTIFICADO_PFX)
        for chave in ('fiscal_senha_certificado_enc', 'fiscal_validade_certificado', 'fiscal_titular_certificado'):
            _config_definir(chave, '')
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def _carregar_config_fiscal_completa(db_id: str) -> Dict:
    with get_db_context() as conn:
        row = conn.execute("SELECT inscricao_estadual, regime_tributario FROM users WHERE db_id=? LIMIT 1", (db_id,)).fetchone()
    return {
        "uf": _config_obter('fiscal_uf'),
        "ambiente": _config_obter('fiscal_ambiente', 'homologacao'),
        "csc_id": _config_obter('fiscal_csc_id'),
        "csc_token": _fiscal_decifrar(_config_obter('fiscal_csc_token_enc')),
        "serie": _config_obter('fiscal_serie', '1'),
        "proximo_numero": _config_obter('fiscal_proximo_numero', '1'),
        "inscricao_estadual": (row[0] if row else '') or '',
        "regime_tributario": (row[1] if row else '1') or '1',
    }

def _erro_config_fiscal_incompleta(cfg: Dict) -> Optional[str]:
    if not os.path.exists(CAMINHO_CERTIFICADO_PFX):
        return "Nenhum certificado digital enviado ainda (Config > Nota Fiscal)"
    if not cfg['uf']:
        return "UF não configurada (Config > Nota Fiscal)"
    if not cfg['inscricao_estadual']:
        return "Inscrição Estadual não configurada (Config > Nota Fiscal)"
    if not cfg['csc_id'] or not cfg['csc_token']:
        return "CSC (ID e Token) não configurado (Config > Nota Fiscal) - obrigatório pro QR Code"
    return None

@app.route('/api/fiscal/status_servico')
def fiscal_status_servico_route():
    """Testa só a conexão com a SEFAZ (URL + certificado aceito), sem emitir
    nada. É o primeiro teste real que dá pra fazer quando o certificado
    chegar - se isto funcionar, a parte de rede/certificado está OK."""
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401
        if not FISCAL_NFCE_DISPONIVEL:
            return jsonify({"success": False, "error": "Dependências de NFC-e não instaladas neste build (lxml/signxml/nfelib/requests-pkcs12)"})
        cfg = _carregar_config_fiscal_completa(db_id)
        if not os.path.exists(CAMINHO_CERTIFICADO_PFX):
            return jsonify({"success": False, "error": "Nenhum certificado digital enviado ainda"})
        if not cfg['uf']:
            return jsonify({"success": False, "error": "UF não configurada"})
        senha = _fiscal_decifrar(_config_obter('fiscal_senha_certificado_enc'))
        with open(CAMINHO_CERTIFICADO_PFX, 'rb') as f:
            pfx_bytes = f.read()
        resultado = consultar_status_servico_sefaz(cfg['uf'], cfg['ambiente'], pfx_bytes, senha)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/fiscal/emitir/<int:venda_id>', methods=['POST'])
@verificar_plano
def fiscal_emitir_nfce_route(venda_id: int):
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401
        if not FISCAL_NFCE_DISPONIVEL:
            return jsonify({"success": False, "error": "Dependências de NFC-e não instaladas neste build (lxml/signxml/nfelib/requests-pkcs12)"})

        cfg = _carregar_config_fiscal_completa(db_id)
        erro_config = _erro_config_fiscal_incompleta(cfg)
        if erro_config:
            return jsonify({"success": False, "error": erro_config})

        with get_db_context() as conn:
            ja_emitida = conn.execute("SELECT chave_acesso, autorizada FROM fiscal_nfce WHERE venda_id=? AND db_id=?", (venda_id, db_id)).fetchone()
            if ja_emitida and ja_emitida[1]:
                return jsonify({"success": False, "error": f"Esta venda já tem uma NFC-e autorizada (chave {ja_emitida[0]})"})

            venda = conn.execute("""SELECT id, subtotal, desconto, total, metodo, itens, troco FROM vendas
                WHERE id=? AND db_id=?""", (venda_id, db_id)).fetchone()
            if not venda:
                return jsonify({"success": False, "error": "Venda não encontrada"}), 404
            try:
                itens = json.loads(venda[5]) if venda[5] else []
            except Exception:
                itens = []
            if not itens:
                return jsonify({"success": False, "error": "Venda sem itens"})

            loja = conn.execute("SELECT nome_loja, cnpj, cnpj_dados FROM users WHERE db_id=? LIMIT 1", (db_id,)).fetchone()
            if not loja or not loja[1]:
                return jsonify({"success": False, "error": "CNPJ da loja não configurado (Config > Loja)"})
            cnpj_dados = {}
            if loja[2]:
                try:
                    cnpj_dados = json.loads(loja[2])
                except Exception:
                    pass
            dados_loja = {"nome_loja": loja[0], "cnpj": loja[1], "cnpj_dados": cnpj_dados}

            codigos = {str(i.get('codigo')) for i in itens if i.get('codigo')}
            produtos_fiscais = {}
            if codigos:
                placeholders = ','.join('?' * len(codigos))
                for row in conn.execute(f"SELECT codigo, ncm, cfop, csosn, unidade, origem FROM produtos WHERE db_id=? AND codigo IN ({placeholders})",
                        (db_id, *codigos)):
                    produtos_fiscais[row[0]] = {"ncm": row[1], "cfop": row[2], "csosn": row[3], "unidade": row[4], "origem": row[5]}

        produtos_sem_ncm = [i.get('nome', i.get('codigo', '?')) for i in itens
            if not produtos_fiscais.get(str(i.get('codigo')), {}).get('ncm')]
        if produtos_sem_ncm:
            return jsonify({"success": False, "error":
                "Produto(s) sem NCM cadastrado (obrigatório pra NFC-e): " + ", ".join(produtos_sem_ncm[:5])})

        totais = {"subtotal": venda[1], "desconto": venda[2] or 0, "total": venda[3],
            "metodo": venda[4], "troco": venda[6] or 0, "venda_id": venda_id}

        senha = _fiscal_decifrar(_config_obter('fiscal_senha_certificado_enc'))
        with open(CAMINHO_CERTIFICADO_PFX, 'rb') as f:
            pfx_bytes = f.read()

        try:
            chave, xml_str = montar_xml_nfce(dados_loja, itens, totais, cfg, produtos_fiscais)
            xml_assinado = assinar_xml_nfce(xml_str, chave, pfx_bytes, senha)
        except Exception as e:
            logger.error(f"❌ Erro ao montar/assinar NFC-e: {e}")
            return jsonify({"success": False, "error": f"Erro ao montar ou assinar o XML: {e}"})

        resultado = transmitir_nfce_sefaz(xml_assinado, chave, cfg['uf'], cfg['ambiente'], pfx_bytes, senha)
        contingencia_usada = False

        if not resultado.get('success') and resultado.get('tipo_erro') == 'conectividade':
            # SEFAZ inacessível (não foi rejeição) - reemite em CONTINGÊNCIA
            # OFFLINE (tpEmis=9): a venda não pode parar esperando a SEFAZ
            # voltar. A chave muda (tpEmis faz parte dela), então monta e
            # assina de novo - fica pendente pra reenvio automático depois.
            logger.warning(f"⚠️ SEFAZ inacessível pra venda #{venda_id} - emitindo em contingência offline: {resultado.get('error')}")
            try:
                chave, xml_str = montar_xml_nfce(dados_loja, itens, totais, cfg, produtos_fiscais, contingencia=True)
                xml_assinado = assinar_xml_nfce(xml_str, chave, pfx_bytes, senha)
                contingencia_usada = True
                resultado = {"success": True, "protocolo": "", "situacao": "Emitida em contingência - pendente de transmissão"}
            except Exception as e:
                logger.error(f"❌ Erro ao montar NFC-e em contingência: {e}")
                return jsonify({"success": False, "error": f"SEFAZ inacessível e falha ao montar contingência: {e}"})

        qrcode_url = montar_qrcode_nfce(chave, cfg['uf'], cfg['ambiente'], cfg['csc_id'], cfg['csc_token'])

        with get_db_context() as conn:
            conn.execute("""INSERT INTO fiscal_nfce (venda_id, chave_acesso, protocolo, situacao, autorizada, ambiente, xml_assinado, qrcode_url, erro, db_id, contingencia, pendente_reenvio)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(venda_id) DO UPDATE SET
                chave_acesso=excluded.chave_acesso, protocolo=excluded.protocolo, situacao=excluded.situacao,
                autorizada=excluded.autorizada, ambiente=excluded.ambiente, xml_assinado=excluded.xml_assinado,
                qrcode_url=excluded.qrcode_url, erro=excluded.erro, contingencia=excluded.contingencia,
                pendente_reenvio=excluded.pendente_reenvio, emitida_em=CURRENT_TIMESTAMP""",
                (venda_id, chave, resultado.get('protocolo', ''), resultado.get('situacao', ''),
                1 if (resultado.get('success') and not contingencia_usada) else 0, cfg['ambiente'], xml_assinado, qrcode_url or '',
                '' if resultado.get('success') else resultado.get('error', resultado.get('situacao', 'Erro desconhecido')), db_id,
                1 if contingencia_usada else 0, 1 if contingencia_usada else 0))

        if resultado.get('success'):
            # avança o próximo número quando autoriza OU quando entra em
            # contingência (a numeração já foi "gasta" nos dois casos - se
            # rejeitar de verdade, aí sim pode reusar o mesmo número)
            _config_definir('fiscal_proximo_numero', str(int(cfg['proximo_numero']) + 1))
            if contingencia_usada:
                logger.info(f"⚠️ NFC-e emitida em CONTINGÊNCIA: venda #{venda_id}, chave {chave} (pendente de reenvio)")
            else:
                logger.info(f"✅ NFC-e autorizada: venda #{venda_id}, chave {chave}, protocolo {resultado.get('protocolo')}")
        else:
            logger.error(f"❌ NFC-e rejeitada/erro: venda #{venda_id} - {resultado}")

        return jsonify({
            "success": resultado.get('success', False),
            "chave": chave,
            "protocolo": resultado.get('protocolo', ''),
            "situacao": resultado.get('situacao', ''),
            "error": resultado.get('error', ''),
            "qrcode_url": qrcode_url,
            "contingencia": contingencia_usada,
        })
    except Exception as e:
        logger.error(f"❌ Erro ao emitir NFC-e: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/fiscal/reenviar/<int:venda_id>', methods=['POST'])
@verificar_plano
def fiscal_reenviar_nfce_route(venda_id: int):
    """Reenvio MANUAL de uma NFC-e pendente de contingência (sem esperar o
    reenvio automático de 5 em 5 minutos) - reenvia o mesmo XML já assinado."""
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401
        if not FISCAL_NFCE_DISPONIVEL:
            return jsonify({"success": False, "error": "Dependências de NFC-e não instaladas neste build"})
        with get_db_context() as conn:
            row = conn.execute("SELECT chave_acesso, xml_assinado, ambiente, pendente_reenvio FROM fiscal_nfce WHERE venda_id=? AND db_id=?", (venda_id, db_id)).fetchone()
        if not row:
            return jsonify({"success": False, "error": "Esta venda não tem NFC-e emitida"})
        if not row[3]:
            return jsonify({"success": False, "error": "Esta NFC-e não está pendente de reenvio"})
        cfg = _carregar_config_fiscal_completa(db_id)
        senha = _fiscal_decifrar(_config_obter('fiscal_senha_certificado_enc'))
        with open(CAMINHO_CERTIFICADO_PFX, 'rb') as f:
            pfx_bytes = f.read()
        resultado = transmitir_nfce_sefaz(row[1], row[0], cfg['uf'], row[2], pfx_bytes, senha)
        if resultado.get('success'):
            with get_db_context() as conn:
                conn.execute("""UPDATE fiscal_nfce SET autorizada=1, pendente_reenvio=0,
                    protocolo=?, situacao=?, erro='' WHERE venda_id=?""",
                    (resultado.get('protocolo', ''), resultado.get('situacao', ''), venda_id))
            return jsonify({"success": True, "protocolo": resultado.get('protocolo', '')})
        return jsonify({"success": False, "error": resultado.get('error', resultado.get('situacao', 'Ainda não foi possível transmitir'))})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/fiscal/cancelar/<int:venda_id>', methods=['POST'])
@verificar_plano
def fiscal_cancelar_nfce_route(venda_id: int):
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401
        if not FISCAL_NFCE_DISPONIVEL:
            return jsonify({"success": False, "error": "Dependências de NFC-e não instaladas neste build"})
        justificativa = ((request.json or {}).get('justificativa') or '').strip()
        if len(justificativa) < 15:
            return jsonify({"success": False, "error": "A justificativa precisa ter pelo menos 15 caracteres"})

        with get_db_context() as conn:
            nfce = conn.execute("SELECT chave_acesso, protocolo, autorizada, cancelada, emitida_em FROM fiscal_nfce WHERE venda_id=? AND db_id=?", (venda_id, db_id)).fetchone()
            loja = conn.execute("SELECT cnpj FROM users WHERE db_id=? LIMIT 1", (db_id,)).fetchone()
        if not nfce or not nfce[2]:
            return jsonify({"success": False, "error": "Esta venda não tem NFC-e autorizada pra cancelar"})
        if nfce[3]:
            return jsonify({"success": False, "error": "Esta NFC-e já está cancelada"})

        # Prazo nacional pra cancelamento simples (evento 110111) é de 24h
        # após a autorização - depois disso a SEFAZ rejeita o evento e o
        # processo de correção muda. Bloqueamos aqui pra dar um aviso claro
        # em vez de deixar a SEFAZ recusar sem explicação.
        try:
            emitida_em = datetime.fromisoformat(nfce[4])
            if (datetime.now() - emitida_em).total_seconds() > 24 * 3600:
                return jsonify({"success": False, "error": "Prazo de 24h pra cancelamento simples expirou. Fale com seu contador sobre os próximos passos."})
        except Exception:
            pass

        cfg = _carregar_config_fiscal_completa(db_id)
        senha = _fiscal_decifrar(_config_obter('fiscal_senha_certificado_enc'))
        with open(CAMINHO_CERTIFICADO_PFX, 'rb') as f:
            pfx_bytes = f.read()

        resultado = cancelar_nfce_sefaz(nfce[0], nfce[1], loja[0] if loja else '', cfg['uf'], cfg['ambiente'],
            justificativa, pfx_bytes, senha)

        if resultado.get('success'):
            with get_db_context() as conn:
                conn.execute("""UPDATE fiscal_nfce SET cancelada=1, protocolo_cancelamento=?,
                    justificativa_cancelamento=?, cancelada_em=CURRENT_TIMESTAMP WHERE venda_id=?""",
                    (resultado.get('protocolo_cancelamento', ''), justificativa, venda_id))
            logger.info(f"✅ NFC-e cancelada: venda #{venda_id}, chave {nfce[0]}")
        else:
            logger.error(f"❌ Falha ao cancelar NFC-e: venda #{venda_id} - {resultado}")

        return jsonify({
            "success": resultado.get('success', False),
            "protocolo_cancelamento": resultado.get('protocolo_cancelamento', ''),
            "error": resultado.get('error', resultado.get('situacao', '')),
        })
    except Exception as e:
        logger.error(f"❌ Erro ao cancelar NFC-e: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/fiscal/danfce/<int:venda_id>')
@verificar_plano
def fiscal_danfce_route(venda_id: int):
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401
        with get_db_context() as conn:
            nfce = conn.execute("""SELECT chave_acesso, protocolo, autorizada, qrcode_url, ambiente,
                contingencia, pendente_reenvio, cancelada, protocolo_cancelamento
                FROM fiscal_nfce WHERE venda_id=? AND db_id=?""", (venda_id, db_id)).fetchone()
            if not nfce or (not nfce[2] and not nfce[6]):
                return jsonify({"success": False, "error": "Esta venda não tem NFC-e emitida"})
            venda = conn.execute("SELECT total, itens FROM vendas WHERE id=? AND db_id=?", (venda_id, db_id)).fetchone()
            loja = conn.execute("SELECT nome_loja, cnpj, cnpj_dados FROM users WHERE db_id=? LIMIT 1", (db_id,)).fetchone()
        itens = json.loads(venda[1]) if venda and venda[1] else []
        cnpj_dados = json.loads(loja[2]) if loja and loja[2] else {}
        dados_loja = {"nome_loja": loja[0] if loja else '', "cnpj": loja[1] if loja else '', "cnpj_dados": cnpj_dados}
        texto = gerar_texto_danfce(dados_loja, itens, {"total": venda[0] if venda else 0}, nfce[0], nfce[1], nfce[3], nfce[4],
            pendente_contingencia=bool(nfce[6]), cancelada=bool(nfce[7]))
        return jsonify({"success": True, "texto": texto, "chave": nfce[0], "qrcode_url": nfce[3],
            "autorizada": bool(nfce[2]), "contingencia": bool(nfce[5]), "pendente_reenvio": bool(nfce[6]),
            "cancelada": bool(nfce[7]), "protocolo_cancelamento": nfce[8] or ''})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/fiscal/preview_demo/<int:venda_id>')
@verificar_plano
def fiscal_preview_demo_route(venda_id: int):
    """Gera uma PRÉVIA visual do cupom fiscal (chave de acesso + QR Code +
    DANFCE) sem falar com a SEFAZ e sem precisar de certificado configurado -
    serve só pra ver como vai ficar na tela. NUNCA fica marcada como
    autorizada, nunca consome numeração real, e o texto deixa isso bem claro
    em toda parte pra não ser confundida com uma nota fiscal de verdade."""
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401
        if not FISCAL_NFCE_DISPONIVEL:
            return jsonify({"success": False, "error": "Dependências de NFC-e não instaladas neste build"})

        with get_db_context() as conn:
            venda = conn.execute("SELECT total, itens FROM vendas WHERE id=? AND db_id=?", (venda_id, db_id)).fetchone()
            if not venda:
                return jsonify({"success": False, "error": "Venda não encontrada"}), 404
            loja = conn.execute("SELECT nome_loja, cnpj, cnpj_dados FROM users WHERE db_id=? LIMIT 1", (db_id,)).fetchone()
        itens = json.loads(venda[1]) if venda[1] else []
        cnpj_dados = json.loads(loja[2]) if loja and loja[2] else {}
        cnpj = (loja[1] if loja and loja[1] else '') or '00000000000000'
        nome_loja = (cnpj_dados.get('razao_social') if cnpj_dados else '') or (loja[0] if loja else 'MINHA LOJA')
        dados_loja = {"nome_loja": nome_loja, "cnpj": cnpj, "cnpj_dados": cnpj_dados}

        # UF real se já configurada; senão GO como padrão só pra prévia funcionar
        cfg = _carregar_config_fiscal_completa(db_id)
        uf = cfg.get('uf') or 'GO'
        agora = datetime.now()
        codigo_numerico = secrets.randbelow(99999999)
        chave = gerar_chave_acesso_nfce(uf, agora, cnpj, cfg.get('serie') or '1', cfg.get('proximo_numero') or '1', codigo_numerico)

        # QR Code de demonstração: usa CSC real se já tiver, senão um valor
        # fictício só pra montar a URL de exemplo (nunca é validado pela SEFAZ)
        csc_id = cfg.get('csc_id') or '000'
        csc_token = cfg.get('csc_token') or 'CSC-DE-DEMONSTRACAO-NAO-REAL'
        qrcode_url = montar_qrcode_nfce(chave, uf, cfg.get('ambiente') or 'homologacao', csc_id, csc_token)

        texto = gerar_texto_danfce(dados_loja, itens, {"total": venda[0]}, chave, 'PRÉVIA - SEM PROTOCOLO', qrcode_url, 'demo')
        texto = "⚠️ PRÉVIA DE DEMONSTRAÇÃO - NÃO É UMA NOTA FISCAL VÁLIDA ⚠️\n\n" + texto
        return jsonify({"success": True, "texto": texto, "chave": chave, "qrcode_url": qrcode_url, "demo": True})
    except Exception as e:
        logger.error(f"❌ Erro na prévia de demonstração: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/imprimir/cupom', methods=['POST'])
def imprimir_cupom_route():
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401
        dados = request.json or {}
        cnpj_dados_frontend = dados.get('cnpj_dados') or {}
        with get_db_context() as conn:
            cursor = conn.execute("SELECT nome_loja, cnpj, cnpj_dados FROM users WHERE db_id=? LIMIT 1", (db_id,))
            loja = cursor.fetchone()
            if loja:
                dados['nome_loja'] = loja[0] or 'MINHA LOJA'
                dados['cnpj'] = loja[1] or ''
                try:
                    cnpj_dados_db = json.loads(loja[2]) if loja[2] else {}
                except:
                    cnpj_dados_db = {}
                merged = {**cnpj_dados_frontend}
                for k, v in cnpj_dados_db.items():
                    if v not in (None, '', {}, []):
                        merged[k] = v
                dados['cnpj_dados'] = merged
        dados['usuario'] = session.get('nome', '')
        resultado = imprimir_cupom_escpos(dados)
        return jsonify(resultado)
    except Exception as e:
        logger.error(f"❌ Erro ao imprimir: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/imprimir/texto', methods=['POST'])
def imprimir_texto_route():
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401
        dados = request.json or {}
        with get_db_context() as conn:
            cursor = conn.execute("SELECT nome_loja, cnpj, cnpj_dados FROM users WHERE db_id=? LIMIT 1", (db_id,))
            loja = cursor.fetchone()
            if loja:
                dados['nome_loja'] = dados.get('nome_loja') or loja[0]
                dados['cnpj'] = dados.get('cnpj') or loja[1] or ''
                try:
                    cnpj_dados_db = json.loads(loja[2]) if loja[2] else {}
                except:
                    cnpj_dados_db = {}
                merged = {**cnpj_dados_db}
                merged.update(dados.get('cnpj_dados') or {})
                dados['cnpj_dados'] = merged
        texto = gerar_texto_cupom(dados)
        return jsonify({"success": True, "texto": texto})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# PRODUTO POR CÓDIGO DE BARRAS - COM PERMISSÃO DE BUSCA
# ============================================================
@app.route('/api/produto/buscar/<codigo_barras>')
@verificar_permissao('busca_estoque')
@verificar_plano
def buscar_produto_barras_route(codigo_barras: str):
    try:
        resultado = buscar_produto_por_codigo_barras(codigo_barras)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# SINCRONIZAÇÃO
# ============================================================
@app.route('/api/sincronizar', methods=['POST'])
@verificar_plano
def sincronizar_route():
    try:
        db_id = get_db_id()
        resultado = sincronizar_dados(db_id)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# SERVIDOR
# ============================================================
@app.route('/api/servidor/id')
def get_servidor_id_route():
    return jsonify({"success": True, "servidor_id": SERVIDOR_ID, "versao": VERSION})

@app.route('/api/baixar_html')
def baixar_html_manual():
    """Tentativa de emergência. O repositório é PRIVADO e o pdv.py não tem (nem
    deve ter) o token do GitHub — quem baixa a interface é o launcher. Se cair
    aqui, é porque o SMART_PDV.exe está desatualizado ou o pdv.py foi aberto
    direto pelo Python. Explicamos isso em vez de ficar 'baixando' pra sempre."""
    try:
        caminho = os.path.join(TEMPLATES_DIR, "index.html")
        if os.path.exists(caminho):
            return jsonify({"success": True, "message": "Interface já está no lugar!"})
        if baixar_html_github():
            return jsonify({"success": True, "message": "HTML baixado!"})
        return jsonify({"success": False, "error":
            "Não foi possível baixar a interface. O repositório é privado, então quem "
            "baixa o index.html é o SMART_PDV.exe. Abra o sistema por ele (e atualize "
            f"o .exe se for antigo). Alternativa: coloque o index.html em {TEMPLATES_DIR}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# THREADS BACKGROUND
# ============================================================

def _verificador_automatico_pix() -> None:
    while True:
        _time.sleep(15)
        try:
            for pix_id, dados in list(pagamentos_pendentes.items()):
                if dados.get('pago'):
                    continue
                try:
                    if verificar_pagamento_backend(pix_id):
                        _confirmar_pagamento_plano(pix_id)
                except:
                    pass
        except:
            pass

def _reenviar_nfce_pendentes_periodicamente() -> None:
    """A cada alguns minutos, tenta reenviar NFC-e emitidas em contingência
    (SEFAZ estava fora do ar na hora da venda). Reenvia o MESMO XML já
    assinado - nunca remonta, porque a chave impressa pro cliente não pode
    mudar depois de já ter saído no papel."""
    while True:
        _time.sleep(300)
        try:
            if not FISCAL_NFCE_DISPONIVEL:
                continue
            with get_db_context() as conn:
                pendentes = conn.execute(
                    "SELECT venda_id, chave_acesso, xml_assinado, ambiente, db_id FROM fiscal_nfce WHERE pendente_reenvio=1").fetchall()
            if not pendentes:
                continue
            logger.info(f"🔄 Tentando reenviar {len(pendentes)} NFC-e(s) pendente(s) de contingência...")
            for venda_id, chave, xml_assinado, ambiente, db_id in pendentes:
                try:
                    cfg = _carregar_config_fiscal_completa(db_id)
                    if not cfg.get('uf') or not os.path.exists(CAMINHO_CERTIFICADO_PFX):
                        continue
                    senha = _fiscal_decifrar(_config_obter('fiscal_senha_certificado_enc'))
                    with open(CAMINHO_CERTIFICADO_PFX, 'rb') as f:
                        pfx_bytes = f.read()
                    resultado = transmitir_nfce_sefaz(xml_assinado, chave, cfg['uf'], ambiente, pfx_bytes, senha)
                    if resultado.get('success'):
                        with get_db_context() as conn:
                            conn.execute("""UPDATE fiscal_nfce SET autorizada=1, pendente_reenvio=0,
                                protocolo=?, situacao=?, erro='' WHERE venda_id=?""",
                                (resultado.get('protocolo', ''), resultado.get('situacao', ''), venda_id))
                        logger.info(f"✅ NFC-e de contingência autorizada no reenvio: venda #{venda_id}, chave {chave}")
                    elif resultado.get('tipo_erro') == 'rejeicao':
                        # SEFAZ respondeu e rejeitou - reenviar nao vai resolver
                        # sozinho, isso precisa de intervenção humana (numeração
                        # duplicada, dados inválidos etc). Para de tentar.
                        with get_db_context() as conn:
                            conn.execute("UPDATE fiscal_nfce SET pendente_reenvio=0, erro=? WHERE venda_id=?",
                                (f"Rejeitada no reenvio: {resultado.get('situacao', resultado.get('error', ''))}", venda_id))
                        logger.error(f"❌ NFC-e de contingência REJEITADA no reenvio: venda #{venda_id} - {resultado}")
                    # se ainda for erro de conectividade, deixa pendente pra próxima rodada
                except Exception as e:
                    logger.warning(f"⚠️ Falha ao reenviar NFC-e da venda #{venda_id}: {e}")
        except Exception as e:
            logger.error(f"⚠️ Erro no reenvio periódico de NFC-e: {e}")

def _responder_descoberta_rede() -> None:
    """Fica ouvindo na rede local. Quando outro SMART PDV está sendo aberto, ele
    pergunta 'tem algum servidor aí?' e nós respondemos. Assim o novo consegue
    avisar o usuário de que já existe um PDV rodando (e evitar dois servidores).

    Só responde a essa pergunta específica; não expõe nenhum dado."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', PORTA_DESCOBERTA))
        logger.info(f"📡 Anunciando na rede (porta {PORTA_DESCOBERTA})")
        while True:
            try:
                dados, origem = s.recvfrom(512)
                if dados.strip() == b'SMART_PDV_DISCOVER':
                    nome_pc = socket.gethostname()
                    s.sendto(f'SMART_PDV|{nome_pc}'.encode('utf-8'), origem)
            except Exception:
                _time.sleep(0.2)
    except Exception as e:
        # Se a porta já está ocupada, é porque outro PDV desta máquina já responde.
        logger.info(f"📡 Descoberta de rede não iniciada: {e}")


def limpar_sessoes_inativas() -> None:
    while True:
        _time.sleep(300)
        try:
            with get_db_context() as conn:
                cursor = conn.execute("""SELECT id, session_id FROM users
                    WHERE session_id != '' AND ultimo_acesso < datetime('now', '-1 hour')""")
                for user in cursor.fetchall():
                    user_id, session_id = user
                    for db_id_key, sess_id in list(SESSOES_ATIVAS.items()):
                        if sess_id == session_id:
                            del SESSOES_ATIVAS[db_id_key]
                            break
                    conn.execute("UPDATE users SET session_id='' WHERE id=?", (user_id,))
        except:
            pass

def _sync_pendente_background() -> None:
    offline_detectado = False
    while True:
        _time.sleep(60)
        try:
            # 🔧 usa pdv/_hora_servidor (intencionalmente público nas regras) em
            # vez da raiz - só serve pra testar conectividade, não precisa
            # (nem deveria) tocar em nada que exija autenticação.
            requests.get(f'{FB_URL}/pdv/_hora_servidor.json', timeout=5)
            if offline_detectado:
                logger.info("🌐 Conexão restaurada! Sincronizando dados pendentes...")
                offline_detectado = False
                for db_id in list(SESSOES_ATIVAS.keys()):
                    try:
                        enviar_para_firebase(db_id)
                    except:
                        pass
        except:
            if not offline_detectado:
                logger.warning("📴 Sem conexão com Firebase - salvando localmente")
                offline_detectado = True

# ============================================================
# INICIAR SERVIDOR
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print(f"🏪 SMART PDV v{VERSION} - VERSÃO COMPLETA")
    print("=" * 60)
    print(f"📁 Dados: {APP_DATA_DIR}")
    print(f"📁 DB: {DB_PATH}")
    print("=" * 60)
    print("🔐 SISTEMA DE PLANO SEGURO:")
    print("  ✅ Token assinado digitalmente")
    print("  ✅ Funciona OFFLINE (sem brechas)")
    print("  ✅ Sincroniza entre dispositivos")
    print("  ✅ Detecta fraude de relógio")
    print("  ✅ SEM período de carência")
    print("  ✅ Renovação automática via Firebase")
    print("  ✅ Aviso com 3 dias de antecedência")
    print("  ✅ Mantém login mesmo com plano expirado")
    print("  ✅ Apenas a aba Planos fica acessível")
    print("=" * 60)
    print("📊 NOVOS PLANOS:")
    print("  🎁 TESTE: 15 dias grátis (Empresarial completo)")
    print("  🔰 BÁSICO: R$ 29,99/mês (1 usuário, 300 produtos)")
    print("  ⭐ STANDARD: R$ 59,99/mês (3 usuários, 1000 produtos)")
    print("  💎 PREMIUM: R$ 89,99/mês (5 usuários, 5000 produtos)")
    print("  👑 EMPRESARIAL: R$ 129,99/mês (10 usuários, Ilimitado)")
    print("=" * 60)
    print("📊 PERMISSÕES POR PLANO:")
    print("  🔰 BÁSICO: Vendas, Caixa, Estoque")
    print("  ⭐ STANDARD: + Clientes")
    print("  💎 PREMIUM: + Dashboard, Busca Estoque, Margem")
    print("  👑 EMPRESARIAL: Tudo liberado")
    print("=" * 60)
    print("📊 LUCRO LÍQUIDO:")
    print("  ✅ Custo e margem por produto")
    print("  ✅ Lucro por venda")
    print("  ✅ Lucro total no Dashboard")
    print("  ✅ CNPJ completo na nota fiscal")
    print("=" * 60)
    print("🔄 SINCRONIZAÇÃO INTELIGENTE:")
    print("  - Quem tem MAIS DADOS vence")
    print("  - Merge bidirecional automático")
    print("  - Sobe dados quando internet voltar")
    print("  - Firebase tem sempre prioridade final")
    print("=" * 60)
    if IS_WINDOWS and IMPRESSAO_DISPONIVEL:
        print("🖨️ Impressão ESC/POS ativa (impressora térmica)")
    else:
        print("🖨️ Impressão disponível apenas no Windows")
    print("=" * 60)
    print("⌨️ TECLAS:")
    print("  F1 → Mestre (foco/finalizar/confirmar)")
    print("  Enter no código de barras → Busca automática")
    print("  Clique nos botões do cupom → Funciona!")
    print("=" * 60)

    init_db()

    print("📥 Verificando HTML em segundo plano...")
    # A interface (index.html) fica num repositório PÚBLICO do GitHub, então o
    # próprio pdv.py consegue baixá-la — não depende mais do launcher.
    # Estratégia:
    #  - Se o index.html NÃO existe: baixa AGORA (bloqueante), senão a 1ª tela
    #    fica no "Baixando interface...". É rápido (~240KB).
    #  - Se JÁ existe: atualiza em segundo plano, para pegar a versão mais nova
    #    sem travar a abertura. Offline: mantém o que tem (não quebra sem net).
    caminho_html_local = os.path.join(TEMPLATES_DIR, "index.html")
    if not os.path.exists(caminho_html_local) or os.path.getsize(caminho_html_local) < 1000:
        logger.info("📥 index.html ausente — baixando do GitHub agora...")
        if not baixar_html_github():
            logger.error("❌ Não consegui baixar o index.html. Verifique a internet e recarregue a página.")
    else:
        threading.Thread(target=baixar_html_github, daemon=True).start()

    threading.Thread(target=_verificador_automatico_pix, daemon=True).start()
    threading.Thread(target=limpar_sessoes_inativas, daemon=True).start()
    threading.Thread(target=_sync_pendente_background, daemon=True).start()
    threading.Thread(target=sincronizar_planos_periodicamente, daemon=True).start()
    threading.Thread(target=_responder_descoberta_rede, daemon=True).start()
    threading.Thread(target=_reenviar_nfce_pendentes_periodicamente, daemon=True).start()
    print("🔄 Thread de sincronização de planos iniciada")

    print(f"\n🆔 Servidor: {SERVIDOR_ID}")
    print(f"📌 Versão: {VERSION}")
    print("🌐 http://localhost:5000")
    print("=" * 60)

    # 🔧 threaded=True: sem isto, o Werkzeug atende UM pedido por vez. Se
    # imprimir_cupom_escpos() travar numa impressora com problema, o servidor
    # inteiro parava (nem venda, nem login, nem abrir caixa) ate alguem
    # resolver a impressora manualmente. Com threaded=True, outras rotas
    # continuam respondendo mesmo se uma impressao estiver presa (a funcao de
    # impressao tambem ganhou timeout proprio - ver imprimir_cupom_escpos).
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
