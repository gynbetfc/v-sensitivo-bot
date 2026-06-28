# pdv.py - SMART PDV v9.0.5 - VERSÃO COMPLETA COM SINCRONIZAÇÃO AUTOMÁTICA
"""
🏪 SMART PDV v9.0.5 - SISTEMA INTELIGENTE DE PONTO DE VENDA

🔹 CORREÇÕES:
- Sincronização de VENDAS do Firebase para o banco local ✅
- Dashboard carrega todas as vendas ✅
- Login funciona sem dados locais ✅
- Sincronização automática após cada venda ✅
- Indicador de sincronização simplificado ✅
- Troco exibido no modal de pagamento ✅
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
import threading
import logging
import shutil
import time as _time
from datetime import datetime, timedelta
from contextlib import contextmanager
from functools import wraps
from typing import Optional, Dict, List, Any, Union, Tuple, Callable
from dataclasses import dataclass, asdict
from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS

# ============================================================
# CORREÇÃO DE ENCODING PARA WINDOWS
# ============================================================
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

# ============================================================
# VERIFICAÇÃO DO SISTEMA OPERACIONAL
# ============================================================
IS_WINDOWS: bool = sys.platform == 'win32'
IS_LINUX: bool = sys.platform.startswith('linux')
IS_TERMUX: bool = 'com.termux' in os.environ.get('PREFIX', '')

# ============================================================
# DETERMINAR PASTA DE DADOS
# ============================================================
def get_app_data_dir() -> str:
    """Retorna o diretório de dados do aplicativo"""
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

os.makedirs(APP_DATA_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(CUPONS_DIR, exist_ok=True)

# ============================================================
# IMPORTAÇÕES CONDICIONAIS PARA IMPRESSÃO
# ============================================================
IMPRESSAO_DISPONIVEL: bool = False
if IS_WINDOWS:
    try:
        import win32print
        import win32ui
        from PIL import Image, ImageDraw, ImageFont
        import qrcode
        from io import BytesIO
        IMPRESSAO_DISPONIVEL = True
        print("🖨️ Impressão Windows disponível")
    except ImportError as e:
        print(f"⚠️ Módulos de impressão não encontrados: {e}")
        print("   Impressão desabilitada.")
else:
    print("🐧 Sistema Linux/Termux detectado. Impressão desabilitada.")

# ============================================================
# CONFIGURAÇÃO DO APP
# ============================================================
app: Flask = Flask(__name__, template_folder=TEMPLATES_DIR)
app.secret_key = secrets.token_hex(32)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False

CORS(app, origins=["*"], supports_credentials=True)

# ============================================================
# VERSÃO
# ============================================================
VERSION: str = "9.0.5"

# ============================================================
# CONFIGURAÇÕES DE LOG
# ============================================================
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
FB_URL: str = "https://nexos-40654-default-rtdb.firebaseio.com"
HTML_URL: str = "https://raw.githubusercontent.com/gynbetfc/v-sensitivo-bot/refs/heads/main/PDV/templates/index.html"
SESSOES_ATIVAS: Dict[str, str] = {}
CACHE_CNPJ: Dict[str, Dict] = {}
CACHE_PRODUTO_BARRAS: Dict[str, Dict] = {}

# ============================================================
# MERCADO PAGO
# ============================================================
MERCADO_PAGO_ACCESS_TOKEN: str = os.environ.get(
    "MP_ACCESS_TOKEN",
    "APP_USR-4548266140377032-050311-6589fc22b166e4cb2cfad0379b28dcdf-1059299796"
)

# ============================================================
# PLANOS
# ============================================================
@dataclass
class Plano:
    id: int
    usuarios: int
    preco: float
    nome: str
    dias: int
    produtos: int

PLANOS: List[Plano] = [
    Plano(1, 1, 79.99, '🔰 BÁSICO', 30, 300),
    Plano(2, 3, 119.99, '⭐ STANDARD', 30, 1000),
    Plano(3, 5, 129.99, '💎 PREMIUM', 30, 5000),
    Plano(4, 10, 139.99, '👑 EMPRESARIAL', 30, -1),
]

pagamentos_pendentes: Dict[str, Dict] = {}

# ============================================================
# RATE LIMITING
# ============================================================
rate_limits: Dict[str, List[float]] = {}

def rate_limit(max_requests: int = 10, window: int = 60) -> Callable:
    """Decorator para limitar requisições"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapped(*args, **kwargs) -> Any:
            key: str = request.remote_addr
            now: float = _time.time()
            
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
# TYPE HINTS
# ============================================================

@dataclass
class Usuario:
    id: str
    nome: str
    email: str
    senha: str
    cargo: str
    db_id: str
    servidor_id: str
    nome_loja: str = ''
    cnpj: str = ''
    cnpj_dados: Dict = None
    session_id: str = ''
    ultimo_acesso: Optional[str] = None
    criado_em: Optional[str] = None
    plano_cache: int = 1
    expira_cache: Optional[str] = None
    ultima_verificacao: Optional[str] = None
    
    def __post_init__(self):
        if self.cnpj_dados is None:
            self.cnpj_dados = {}

@dataclass
class Produto:
    codigo: str
    nome: str
    preco: float
    estoque: int = 0
    categoria: str = 'Geral'
    db_id: str = ''
    ultima_atualizacao: Optional[str] = None

@dataclass
class Cliente:
    id: int
    nome: str
    telefone: str = ''
    email: str = ''
    divida: float = 0
    db_id: str = ''
    ultima_atualizacao: Optional[str] = None

@dataclass
class Venda:
    id: int
    data_hora: str
    subtotal: float
    desconto: float
    total: float
    metodo: str
    itens: List[Dict]
    cliente: str = ''
    usuario_id: str = ''
    db_id: str = ''
    recebido: float = 0
    troco: float = 0

# ============================================================
# FUNÇÕES DE BANCO DE DADOS UNIFICADO
# ============================================================

def get_db() -> sqlite3.Connection:
    """Retorna conexão com o banco de dados unificado"""
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=10000")
    conn.execute("PRAGMA busy_timeout=30000")
    conn.execute("PRAGMA temp_store=MEMORY")
    return conn

@contextmanager
def get_db_context() -> sqlite3.Connection:
    """Context manager para conexão com banco de dados"""
    conn = None
    try:
        conn = get_db()
        yield conn
        conn.commit()
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            _time.sleep(0.5)
            try:
                conn = get_db()
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
# INICIALIZAR BANCO DE DADOS
# ============================================================

def init_db() -> None:
    """Inicializa o banco de dados unificado com todas as tabelas"""
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
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS produtos (
                codigo TEXT PRIMARY KEY,
                nome TEXT,
                preco REAL,
                estoque INTEGER DEFAULT 0,
                categoria TEXT DEFAULT 'Geral',
                db_id TEXT,
                ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sincronizado_em TIMESTAMP
            )
        ''')
        
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
        
        # Adicionar colunas faltantes
        colunas_necessarias: Dict[str, Dict[str, str]] = {
            'users': {'sincronizado_em': 'TIMESTAMP'},
            'produtos': {'ultima_atualizacao': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP', 'sincronizado_em': 'TIMESTAMP'},
            'clientes': {'ultima_atualizacao': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP', 'sincronizado_em': 'TIMESTAMP'},
            'vendas': {'recebido': 'REAL DEFAULT 0', 'troco': 'REAL DEFAULT 0', 'sincronizado_em': 'TIMESTAMP'},
            'caixa': {'sincronizado_em': 'TIMESTAMP'}
        }
        
        for tabela, colunas in colunas_necessarias.items():
            cursor = conn.execute(f"PRAGMA table_info({tabela})")
            colunas_existentes = [row[1] for row in cursor.fetchall()]
            
            for coluna, tipo in colunas.items():
                if coluna not in colunas_existentes:
                    try:
                        conn.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {tipo}")
                        logger.info(f"✅ Coluna '{coluna}' adicionada à tabela {tabela}")
                    except Exception as e:
                        logger.warning(f"⚠️ Erro ao adicionar coluna '{coluna}' em {tabela}: {e}")
        
        conn.commit()
        logger.info("✅ Banco de dados unificado inicializado")

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()

def get_db_id() -> Optional[str]:
    return session.get('db_id')

def get_usuario_id() -> Optional[str]:
    return session.get('usuario_id')

def get_timestamp() -> str:
    return datetime.now().isoformat()

def _fb_key(db_id: str) -> str:
    return db_id.replace(".", "_").replace("@", "_").replace("#", "").replace("$", "").replace("[", "").replace("]", "").replace("/", "_")

# ============================================================
# FUNÇÕES FIREBASE
# ============================================================

def validar_cnpj_firebase(cnpj: str) -> bool:
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

def salvar_usuario_firebase(db_id: str, dados: Dict) -> bool:
    try:
        key = _fb_key(db_id)
        url = f'{FB_URL}/pdv/usuarios/{key}.json'
        response = requests.put(url, json=dados, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"⚠️ Erro Firebase: {e}")
        return False

def carregar_usuario_firebase(db_id: str) -> Optional[Dict]:
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

def carregar_todos_usuarios_firebase() -> Dict:
    try:
        url = f'{FB_URL}/pdv/usuarios.json'
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json() or {}
        return {}
    except:
        return {}

def buscar_usuario_por_email_firebase(email: str) -> Optional[Dict]:
    try:
        url = f'{FB_URL}/pdv/usuarios.json'
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            usuarios = response.json()
            if usuarios:
                for key, dados in usuarios.items():
                    if dados.get('email') == email:
                        return dados
        return None
    except:
        return None

# ============================================================
# CACHE LOCAL DO PLANO
# ============================================================

def salvar_plano_cache(db_id: str, plano_id: int, expira_em: str) -> None:
    try:
        with get_db_context() as conn:
            conn.execute("""
                UPDATE users SET 
                    plano_cache = ?,
                    expira_cache = ?,
                    ultima_verificacao = ?
                WHERE db_id = ?
            """, (plano_id, expira_em, get_timestamp(), db_id))
            conn.commit()
            logger.info(f"✅ Plano cache salvo: {db_id}")
    except Exception as e:
        logger.error(f"⚠️ Erro ao salvar cache do plano: {e}")

def carregar_plano_cache(db_id: str) -> Optional[Dict]:
    try:
        with get_db_context() as conn:
            cursor = conn.execute("""
                SELECT plano_cache, expira_cache, ultima_verificacao 
                FROM users WHERE db_id = ?
            """, (db_id,))
            result = cursor.fetchone()
            if result:
                return {
                    'plano_id': result[0],
                    'expira_em': result[1],
                    'ultima_verificacao': result[2]
                }
            return None
    except Exception as e:
        logger.error(f"⚠️ Erro ao carregar cache do plano: {e}")
        return None

# ============================================================
# GERAR ID DO SERVIDOR
# ============================================================

def obter_id_servidor() -> str:
    try:
        with get_db_context() as conn:
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
                conn.commit()
                return servidor_id
    except Exception as e:
        logger.error(f"⚠️ Erro ao gerar ID: {e}")
        return f"SERV_{str(uuid.uuid4())[:12]}"

SERVIDOR_ID: str = obter_id_servidor()

# ============================================================
# FUNÇÕES DE SINCRONIZAÇÃO (CORRIGIDAS)
# ============================================================

def sincronizar_dados(db_id: str) -> Dict:
    """
    Sincroniza dados do Firebase para o banco local.
    ⭐ CORREÇÃO: Agora sincroniza VENDAS corretamente!
    """
    resultado = {
        'success': True,
        'produtos_adicionados': 0,
        'produtos_atualizados': 0,
        'clientes_adicionados': 0,
        'clientes_atualizados': 0,
        'vendas_adicionadas': 0,
        'erros': []
    }
    
    try:
        dados_firebase = carregar_usuario_firebase(db_id)
        if not dados_firebase:
            resultado['success'] = False
            resultado['erros'].append('Usuário não encontrado no Firebase')
            return resultado
        
        with get_db_context() as conn:
            # === SINCRONIZAR PRODUTOS ===
            produtos_firebase = dados_firebase.get('produtos', {})
            
            cursor = conn.execute("""
                SELECT codigo, nome, preco, estoque, categoria, ultima_atualizacao 
                FROM produtos WHERE db_id = ?
            """, (db_id,))
            produtos_locais = {row[0]: dict(row) for row in cursor.fetchall()}
            
            for codigo, dados_prod in produtos_firebase.items():
                if codigo in produtos_locais:
                    local_ts = produtos_locais[codigo].get('ultima_atualizacao')
                    firebase_ts = dados_prod.get('ultima_atualizacao')
                    
                    if firebase_ts and (not local_ts or firebase_ts > local_ts):
                        conn.execute("""
                            UPDATE produtos SET 
                                nome = ?, preco = ?, estoque = ?, categoria = ?,
                                ultima_atualizacao = ?, sincronizado_em = ?
                            WHERE codigo = ? AND db_id = ?
                        """, (
                            dados_prod.get('nome', ''),
                            dados_prod.get('preco', 0),
                            dados_prod.get('estoque', 0),
                            dados_prod.get('categoria', 'Geral'),
                            firebase_ts,
                            get_timestamp(),
                            codigo,
                            db_id
                        ))
                        resultado['produtos_atualizados'] += 1
                else:
                    conn.execute("""
                        INSERT INTO produtos (codigo, nome, preco, estoque, categoria, db_id, ultima_atualizacao, sincronizado_em)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        codigo,
                        dados_prod.get('nome', ''),
                        dados_prod.get('preco', 0),
                        dados_prod.get('estoque', 0),
                        dados_prod.get('categoria', 'Geral'),
                        db_id,
                        dados_prod.get('ultima_atualizacao', get_timestamp()),
                        get_timestamp()
                    ))
                    resultado['produtos_adicionados'] += 1
            
            # === SINCRONIZAR CLIENTES ===
            clientes_firebase = dados_firebase.get('clientes', {})
            
            cursor = conn.execute("""
                SELECT id, nome, telefone, email, divida, ultima_atualizacao 
                FROM clientes WHERE db_id = ?
            """, (db_id,))
            clientes_locais = {str(row[0]): dict(row) for row in cursor.fetchall()}
            
            for id_cliente, dados_cli in clientes_firebase.items():
                if id_cliente in clientes_locais:
                    local_ts = clientes_locais[id_cliente].get('ultima_atualizacao')
                    firebase_ts = dados_cli.get('ultima_atualizacao')
                    
                    if firebase_ts and (not local_ts or firebase_ts > local_ts):
                        conn.execute("""
                            UPDATE clientes SET 
                                nome = ?, telefone = ?, email = ?, divida = ?,
                                ultima_atualizacao = ?, sincronizado_em = ?
                            WHERE id = ? AND db_id = ?
                        """, (
                            dados_cli.get('nome', ''),
                            dados_cli.get('telefone', ''),
                            dados_cli.get('email', ''),
                            dados_cli.get('divida', 0),
                            firebase_ts,
                            get_timestamp(),
                            id_cliente,
                            db_id
                        ))
                        resultado['clientes_atualizados'] += 1
                else:
                    conn.execute("""
                        INSERT INTO clientes (id, nome, telefone, email, divida, db_id, ultima_atualizacao, sincronizado_em)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        int(id_cliente),
                        dados_cli.get('nome', ''),
                        dados_cli.get('telefone', ''),
                        dados_cli.get('email', ''),
                        dados_cli.get('divida', 0),
                        db_id,
                        dados_cli.get('ultima_atualizacao', get_timestamp()),
                        get_timestamp()
                    ))
                    resultado['clientes_adicionados'] += 1
            
            # ⭐⭐⭐ SINCRONIZAR VENDAS - CORRIGIDO ⭐⭐⭐
            vendas_firebase = dados_firebase.get('vendas', [])
            
            # Buscar IDs das vendas locais
            cursor = conn.execute("""
                SELECT id FROM vendas WHERE db_id = ?
            """, (db_id,))
            vendas_locais_ids = {row[0] for row in cursor.fetchall()}
            
            for venda_fb in vendas_firebase:
                venda_id = venda_fb.get('id')
                if not venda_id:
                    continue
                
                # Se a venda já existe localmente, pular
                if venda_id in vendas_locais_ids:
                    continue
                
                # Inserir venda do Firebase
                conn.execute("""
                    INSERT INTO vendas (
                        id, data_hora, subtotal, desconto, total, metodo, 
                        itens, cliente, usuario_id, db_id, recebido, troco, sincronizado_em
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    venda_id,
                    venda_fb.get('data_hora', get_timestamp()),
                    venda_fb.get('subtotal', 0),
                    venda_fb.get('desconto', 0),
                    venda_fb.get('total', 0),
                    venda_fb.get('metodo', 'Dinheiro'),
                    json.dumps(venda_fb.get('itens', [])),
                    venda_fb.get('cliente', ''),
                    venda_fb.get('usuario_id', ''),
                    db_id,
                    venda_fb.get('recebido', 0),
                    venda_fb.get('troco', 0),
                    get_timestamp()
                ))
                resultado['vendas_adicionadas'] += 1
                vendas_locais_ids.add(venda_id)
            
            conn.commit()
        
        # Enviar dados locais para Firebase (backup)
        enviar_para_firebase(db_id)
        
        logger.info(f"✅ Sincronização concluída: {resultado['vendas_adicionadas']} vendas adicionadas")
        return resultado
        
    except Exception as e:
        logger.error(f"❌ Erro na sincronização: {e}")
        resultado['success'] = False
        resultado['erros'].append(str(e))
        return resultado

def enviar_para_firebase(db_id: str) -> bool:
    """Envia dados locais para o Firebase e marca como sincronizados"""
    try:
        dados_firebase = carregar_usuario_firebase(db_id) or {}
        
        with get_db_context() as conn:
            # === PRODUTOS ===
            cursor = conn.execute("""
                SELECT codigo, nome, preco, estoque, categoria, ultima_atualizacao 
                FROM produtos WHERE db_id = ?
            """, (db_id,))
            produtos = {}
            for row in cursor.fetchall():
                produtos[row[0]] = {
                    'nome': row[1],
                    'preco': row[2],
                    'estoque': row[3],
                    'categoria': row[4] or 'Geral',
                    'ultima_atualizacao': row[5] or get_timestamp()
                }
            dados_firebase['produtos'] = produtos
            
            # === CLIENTES ===
            cursor = conn.execute("""
                SELECT id, nome, telefone, email, divida, ultima_atualizacao 
                FROM clientes WHERE db_id = ?
            """, (db_id,))
            clientes = {}
            for row in cursor.fetchall():
                clientes[str(row[0])] = {
                    'nome': row[1],
                    'telefone': row[2] or '',
                    'email': row[3] or '',
                    'divida': row[4] or 0,
                    'ultima_atualizacao': row[5] or get_timestamp()
                }
            dados_firebase['clientes'] = clientes
            
            # === VENDAS ===
            cursor = conn.execute("""
                SELECT id, data_hora, subtotal, desconto, total, metodo, itens, cliente, usuario_id, recebido, troco
                FROM vendas WHERE db_id = ?
            """, (db_id,))
            vendas = []
            for row in cursor.fetchall():
                vendas.append({
                    'id': row[0],
                    'data_hora': row[1],
                    'subtotal': row[2],
                    'desconto': row[3],
                    'total': row[4],
                    'metodo': row[5],
                    'itens': json.loads(row[6]) if row[6] else [],
                    'cliente': row[7] or '',
                    'usuario_id': row[8] or '',
                    'recebido': row[9] or 0,
                    'troco': row[10] or 0
                })
            dados_firebase['vendas'] = vendas
            
            # === CAIXA ===
            cursor = conn.execute("""
                SELECT id, usuario_id, valor_abertura, data_abertura, data_fechamento, total, status
                FROM caixa WHERE db_id = ? ORDER BY id DESC LIMIT 1
            """, (db_id,))
            result = cursor.fetchone()
            if result:
                dados_firebase['caixa'] = {
                    'usuario_id': result[1],
                    'valor_abertura': result[2],
                    'data_abertura': result[3],
                    'data_fechamento': result[4],
                    'total': result[5] or 0,
                    'status': result[6]
                }
            
            # === INFORMAÇÕES DA LOJA ===
            cursor = conn.execute("""
                SELECT nome_loja, cnpj, cnpj_dados FROM users WHERE db_id = ? LIMIT 1
            """, (db_id,))
            loja = cursor.fetchone()
            if loja:
                dados_firebase['nome_loja'] = loja[0] or ''
                dados_firebase['cnpj'] = loja[1] or ''
                try:
                    dados_firebase['cnpj_dados'] = json.loads(loja[2]) if loja[2] else {}
                except:
                    dados_firebase['cnpj_dados'] = {}
        
        if salvar_usuario_firebase(db_id, dados_firebase):
            logger.info(f"✅ Dados enviados para Firebase: {db_id}")
            return True
        else:
            logger.error(f"❌ Falha ao enviar dados para Firebase: {db_id}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao enviar para Firebase: {e}")
        return False

def sincronizar_automatico(db_id: str) -> None:
    """Sincroniza dados automaticamente em background"""
    if not db_id:
        return
    
    def _sincronizar():
        try:
            _time.sleep(0.5)
            resultado = sincronizar_dados(db_id)
            if resultado.get('success'):
                logger.info("✅ Sincronização automática concluída")
        except Exception as e:
            logger.error(f"⚠️ Erro na sincronização automática: {e}")
    
    thread = threading.Thread(target=_sincronizar, daemon=True)
    thread.start()

def criar_usuario_firebase(db_id: str, nome: str, email: str, senha_hash: str, servidor_id: str, 
                          nome_loja: str = "", cnpj: str = "", cnpj_dados: Dict = None) -> Dict:
    if cnpj_dados is None:
        cnpj_dados = {}
    
    dados = {
        'db_id': db_id,
        'nome': nome,
        'email': email,
        'senha': senha_hash,
        'servidor_id': servidor_id,
        'nome_loja': nome_loja,
        'cnpj': cnpj,
        'cnpj_dados': cnpj_dados,
        'data_cadastro': get_timestamp(),
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
# FUNÇÕES DE PLANO
# ============================================================

def is_plano_ativo(db_id: str) -> bool:
    if not db_id:
        return False
    
    GRACE_PERIOD_DIAS: int = 3
    
    cache = carregar_plano_cache(db_id)
    if cache and cache.get('expira_em'):
        try:
            expira_date = datetime.fromisoformat(cache['expira_em'])
            dias_restantes = (expira_date - datetime.now()).total_seconds() / 86400
            if dias_restantes >= -GRACE_PERIOD_DIAS:
                return True
        except:
            pass
    
    try:
        dados = carregar_usuario_firebase(db_id)
        if dados:
            expira = dados.get('expira_em')
            plano_id = dados.get('plano', 1)
            if expira:
                salvar_plano_cache(db_id, plano_id, expira)
                expira_date = datetime.fromisoformat(expira)
                dias_restantes = (expira_date - datetime.now()).total_seconds() / 86400
                if dias_restantes >= -GRACE_PERIOD_DIAS:
                    return True
    except:
        pass
    
    return True

def get_dias_restantes(db_id: str) -> float:
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

def get_limite_produtos(db_id: str) -> int:
    if not db_id:
        return 0
    
    dados = carregar_usuario_firebase(db_id)
    if not dados:
        return 0
    
    plano_id = dados.get('plano', 1)
    plano = next((p for p in PLANOS if p.id == plano_id), None)
    if not plano:
        return 0
    
    return plano.produtos

def get_total_produtos(db_id: str) -> int:
    if not db_id:
        return 0
    
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
    if not db_id:
        return False, "Usuário não autenticado"
    
    limite = get_limite_produtos(db_id)
    atual = get_total_produtos(db_id)
    
    if limite == -1:
        return True, f"Produtos ilimitados ({atual} atuais)"
    
    if atual + quantidade > limite:
        return False, f"Limite de {limite} produtos atingido! ({atual}/{limite})"
    
    restam = limite - atual
    return True, f"Pode adicionar! ({atual}/{limite} - restam {restam})"

# ============================================================
# BUSCA INTELIGENTE DE PRODUTO POR CÓDIGO DE BARRAS
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
        url = f"https://world.openfoodfacts.org/api/v0/product/{codigo_limpo}.json"
        response = requests.get(url, timeout=10, headers={"User-Agent": "SMART-PDV/9.0"})
        
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
                
                return {"success": True, "dados": dados_produto, "fonte": "OpenFoodFacts"}
    except:
        pass
    
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
                
                return {"success": True, "dados": dados_produto, "fonte": "BrasilAPI"}
    except:
        pass
    
    dados_produto = {
        "nome": f"Produto {codigo_limpo}",
        "marca": "",
        "categoria": "Geral",
        "gtin": codigo_limpo,
        "fonte": "Fallback"
    }
    
    CACHE_PRODUTO_BARRAS[codigo_limpo] = {
        'dados': dados_produto,
        'timestamp': _time.time()
    }
    
    return {"success": True, "dados": dados_produto, "fonte": "Fallback"}

# ============================================================
# IMPRESSÃO PROFISSIONAL DE CUPOM
# ============================================================

def formatar_cnpj(cnpj: str) -> str:
    if not cnpj or len(cnpj) != 14:
        return cnpj
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}"

def gerar_texto_cupom(dados_impressao: Dict) -> str:
    nome_loja = dados_impressao.get('nome_loja', 'MINHA LOJA')
    cnpj = dados_impressao.get('cnpj', '')
    cnpj_dados = dados_impressao.get('cnpj_dados', {})
    data_hora = dados_impressao.get('data_hora', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
    venda_id = dados_impressao.get('venda_id', '')
    itens = dados_impressao.get('itens', [])
    subtotal = dados_impressao.get('subtotal', 0)
    desconto = dados_impressao.get('desconto', 0)
    total = dados_impressao.get('total', 0)
    metodo = dados_impressao.get('metodo', 'Dinheiro')
    cliente = dados_impressao.get('cliente', '')
    usuario = dados_impressao.get('usuario', '')
    recebido = dados_impressao.get('recebido', 0)
    troco = dados_impressao.get('troco', 0)

    linhas = []
    largura = 48

    linhas.append('=' * largura)
    linhas.append(nome_loja.center(largura))
    
    if cnpj:
        linhas.append(f'CNPJ: {formatar_cnpj(cnpj)}'.center(largura))
    
    if cnpj_dados:
        if cnpj_dados.get('razao_social'):
            linhas.append(f'{cnpj_dados["razao_social"][:42]}'.center(largura))
        if cnpj_dados.get('nome_fantasia'):
            linhas.append(f'FANTASIA: {cnpj_dados["nome_fantasia"][:38]}'.center(largura))
        if cnpj_dados.get('data_abertura'):
            linhas.append(f'ABERTURA: {cnpj_dados["data_abertura"]}'.center(largura))
        if cnpj_dados.get('porte'):
            linhas.append(f'PORTE: {cnpj_dados["porte"][:40]}'.center(largura))
        if cnpj_dados.get('natureza_juridica'):
            linhas.append(f'NATUREZA: {cnpj_dados["natureza_juridica"][:38]}'.center(largura))
        if cnpj_dados.get('cnae_descricao'):
            linhas.append(f'ATIVIDADE: {cnpj_dados["cnae_descricao"][:38]}'.center(largura))
    
    linhas.append('-' * largura)
    linhas.append('CUPOM FISCAL'.center(largura))
    linhas.append(f'Data: {data_hora}'.center(largura))
    if venda_id:
        linhas.append(f'Venda: #{venda_id}'.center(largura))
    linhas.append('=' * largura)
    linhas.append('')

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

    linhas.append(f"{'SUBTOTAL:'.ljust(32)}R$ {subtotal:.2f}".rjust(largura))
    if desconto > 0:
        linhas.append(f"{'DESCONTO:'.ljust(32)}R$ {desconto:.2f}".rjust(largura))
    linhas.append(f"{'TOTAL:'.ljust(32)}R$ {total:.2f}".rjust(largura))
    linhas.append('-' * largura)

    linhas.append(f"FORMA DE PAGAMENTO: {metodo}".center(largura))
    if recebido > 0:
        linhas.append(f"RECEBIDO: R$ {recebido:.2f}".center(largura))
    if troco > 0:
        linhas.append(f"TROCO: R$ {troco:.2f}".center(largura))
    if cliente:
        linhas.append(f"CLIENTE: {cliente}".center(largura))
    if usuario:
        linhas.append(f"OPERADOR: {usuario}".center(largura))

    linhas.append('=' * largura)
    if cnpj and cnpj_dados:
        if cnpj_dados.get('logradouro'):
            end = cnpj_dados.get('logradouro', '')
            if cnpj_dados.get('numero'):
                end += f', {cnpj_dados["numero"]}'
            if cnpj_dados.get('bairro'):
                end += f' - {cnpj_dados["bairro"]}'
            if cnpj_dados.get('municipio'):
                end += f', {cnpj_dados["municipio"]}'
            if cnpj_dados.get('uf'):
                end += f' - {cnpj_dados["uf"]}'
            linhas.append(end.center(largura))
        if cnpj_dados.get('telefone'):
            linhas.append(f'TEL: {cnpj_dados["telefone"]}'.center(largura))
        if cnpj_dados.get('email'):
            linhas.append(f'EMAIL: {cnpj_dados["email"]}'.center(largura))
    
    linhas.append('')
    linhas.append('VOLTE SEMPRE!'.center(largura))
    linhas.append('=' * largura)

    return '\n'.join(linhas) + '\n\n'

def imprimir_cupom(dados_impressao: Dict) -> Dict:
    if not IS_WINDOWS or not IMPRESSAO_DISPONIVEL:
        texto = gerar_texto_cupom(dados_impressao)
        logger.info(f"🖨️ Cupom gerado (simulação):\n{texto}")
        
        try:
            venda_id = dados_impressao.get('venda_id', '')
            if venda_id:
                arquivo = os.path.join(CUPONS_DIR, f'cupom_{venda_id}.txt')
                with open(arquivo, 'w', encoding='utf-8') as f:
                    f.write(texto)
        except:
            pass
        
        return {"success": True, "simulacao": True, "message": "Cupom gerado (simulação)"}
    
    try:
        import win32print
        
        LARGURA = 48
        
        ESC = chr(27)
        GS = chr(29)
        
        cmd_iniciar = ESC + '@'
        cmd_cortar = GS + 'V' + chr(66) + chr(0)
        cmd_centralizar = ESC + 'a' + chr(1)
        cmd_esquerda = ESC + 'a' + chr(0)
        cmd_negrito_on = ESC + 'E' + chr(1)
        cmd_negrito_off = ESC + 'E' + chr(0)
        
        texto = gerar_texto_cupom(dados_impressao)
        
        impressora_nome = win32print.GetDefaultPrinter()
        if not impressora_nome:
            return {"success": False, "error": "Nenhuma impressora padrão definida"}
        
        hprinter = win32print.OpenPrinter(impressora_nome)
        
        try:
            dados_bytes = bytearray()
            
            dados_bytes.extend(cmd_iniciar.encode('latin-1', 'replace'))
            dados_bytes.extend(cmd_centralizar.encode('latin-1', 'replace'))
            dados_bytes.extend(cmd_negrito_on.encode('latin-1', 'replace'))
            
            nome_loja = dados_impressao.get('nome_loja', 'MINHA LOJA')
            dados_bytes.extend((nome_loja.center(LARGURA) + '\n').encode('latin-1', 'replace'))
            dados_bytes.extend(cmd_negrito_off.encode('latin-1', 'replace'))
            
            cnpj = dados_impressao.get('cnpj', '')
            if cnpj:
                dados_bytes.extend((f'CNPJ: {formatar_cnpj(cnpj)}' + '\n').encode('latin-1', 'replace'))
            
            cnpj_dados = dados_impressao.get('cnpj_dados', {})
            if cnpj_dados:
                if cnpj_dados.get('razao_social'):
                    dados_bytes.extend((cnpj_dados['razao_social'][:42].center(LARGURA) + '\n').encode('latin-1', 'replace'))
                if cnpj_dados.get('nome_fantasia'):
                    dados_bytes.extend((f'FANTASIA: {cnpj_dados["nome_fantasia"][:38]}'.center(LARGURA) + '\n').encode('latin-1', 'replace'))
                if cnpj_dados.get('data_abertura'):
                    dados_bytes.extend((f'ABERTURA: {cnpj_dados["data_abertura"]}'.center(LARGURA) + '\n').encode('latin-1', 'replace'))
                if cnpj_dados.get('porte'):
                    dados_bytes.extend((f'PORTE: {cnpj_dados["porte"][:40]}'.center(LARGURA) + '\n').encode('latin-1', 'replace'))
                if cnpj_dados.get('natureza_juridica'):
                    dados_bytes.extend((f'NATUREZA: {cnpj_dados["natureza_juridica"][:38]}'.center(LARGURA) + '\n').encode('latin-1', 'replace'))
            
            dados_bytes.extend(('=' * LARGURA + '\n').encode('latin-1', 'replace'))
            dados_bytes.extend(cmd_centralizar.encode('latin-1', 'replace'))
            dados_bytes.extend(('CUPOM FISCAL\n').encode('latin-1', 'replace'))
            
            data_hora = dados_impressao.get('data_hora', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
            dados_bytes.extend((data_hora + '\n').encode('latin-1', 'replace'))
            
            venda_id = dados_impressao.get('venda_id', '')
            if venda_id:
                dados_bytes.extend(('Venda #' + str(venda_id) + '\n').encode('latin-1', 'replace'))
            
            dados_bytes.extend(('=' * LARGURA + '\n').encode('latin-1', 'replace'))
            
            dados_bytes.extend(cmd_esquerda.encode('latin-1', 'replace'))
            dados_bytes.extend(cmd_negrito_on.encode('latin-1', 'replace'))
            header = 'ITEM'.ljust(3) + 'DESCRIÇÃO'.ljust(25) + 'QTD'.rjust(4) + 'TOTAL'.rjust(16)
            dados_bytes.extend((header + '\n').encode('latin-1', 'replace'))
            dados_bytes.extend(cmd_negrito_off.encode('latin-1', 'replace'))
            dados_bytes.extend(('-' * LARGURA + '\n').encode('latin-1', 'replace'))
            
            itens = dados_impressao.get('itens', [])
            for idx, item in enumerate(itens, 1):
                nome = item.get('nome', 'Item')[:22]
                qtd = item.get('quantidade', 1)
                total_item = item.get('total', 0)
                preco_unit = item.get('preco_unitario', 0)
                
                linha = f"{str(idx).ljust(3)}{nome.ljust(25)}{str(qtd).rjust(4)}{f'R$ {total_item:.2f}'.rjust(16)}"
                dados_bytes.extend((linha + '\n').encode('latin-1', 'replace'))
                
                if qtd > 1 and preco_unit:
                    linha_unit = f"{' '*3}{'R$ ' + f'{preco_unit:.2f}'.rjust(6)} x {qtd}".ljust(LARGURA - 10)
                    dados_bytes.extend((linha_unit + '\n').encode('latin-1', 'replace'))
            
            dados_bytes.extend(('-' * LARGURA + '\n').encode('latin-1', 'replace'))
            
            subtotal = dados_impressao.get('subtotal', 0)
            desconto = dados_impressao.get('desconto', 0)
            total = dados_impressao.get('total', 0)
            
            dados_bytes.extend(cmd_negrito_on.encode('latin-1', 'replace'))
            dados_bytes.extend((f"{'SUBTOTAL:'.ljust(32)}R$ {subtotal:.2f}".rjust(LARGURA) + '\n').encode('latin-1', 'replace'))
            if desconto > 0:
                dados_bytes.extend((f"{'DESCONTO:'.ljust(32)}R$ {desconto:.2f}".rjust(LARGURA) + '\n').encode('latin-1', 'replace'))
            dados_bytes.extend((f"{'TOTAL:'.ljust(32)}R$ {total:.2f}".rjust(LARGURA) + '\n').encode('latin-1', 'replace'))
            dados_bytes.extend(cmd_negrito_off.encode('latin-1', 'replace'))
            dados_bytes.extend(('-' * LARGURA + '\n').encode('latin-1', 'replace'))
            
            dados_bytes.extend(cmd_centralizar.encode('latin-1', 'replace'))
            metodo = dados_impressao.get('metodo', 'Dinheiro')
            dados_bytes.extend((f"FORMA DE PAGAMENTO: {metodo}".center(LARGURA) + '\n').encode('latin-1', 'replace'))
            
            recebido = dados_impressao.get('recebido', 0)
            troco = dados_impressao.get('troco', 0)
            if recebido > 0:
                dados_bytes.extend((f"RECEBIDO: R$ {recebido:.2f}".center(LARGURA) + '\n').encode('latin-1', 'replace'))
            if troco > 0:
                dados_bytes.extend((f"TROCO: R$ {troco:.2f}".center(LARGURA) + '\n').encode('latin-1', 'replace'))
            
            cliente = dados_impressao.get('cliente', '')
            if cliente:
                dados_bytes.extend((f"CLIENTE: {cliente}".center(LARGURA) + '\n').encode('latin-1', 'replace'))
            
            usuario = dados_impressao.get('usuario', '')
            if usuario:
                dados_bytes.extend((f"OPERADOR: {usuario}".center(LARGURA) + '\n').encode('latin-1', 'replace'))
            
            dados_bytes.extend(('=' * LARGURA + '\n').encode('latin-1', 'replace'))
            
            if cnpj and cnpj_dados:
                if cnpj_dados.get('logradouro'):
                    end = cnpj_dados.get('logradouro', '')
                    if cnpj_dados.get('numero'):
                        end += f', {cnpj_dados["numero"]}'
                    if cnpj_dados.get('bairro'):
                        end += f' - {cnpj_dados["bairro"]}'
                    if cnpj_dados.get('municipio'):
                        end += f', {cnpj_dados["municipio"]}'
                    if cnpj_dados.get('uf'):
                        end += f' - {cnpj_dados["uf"]}'
                    dados_bytes.extend((end.center(LARGURA) + '\n').encode('latin-1', 'replace'))
                if cnpj_dados.get('telefone'):
                    dados_bytes.extend((f'TEL: {cnpj_dados["telefone"]}'.center(LARGURA) + '\n').encode('latin-1', 'replace'))
                if cnpj_dados.get('email'):
                    dados_bytes.extend((f'EMAIL: {cnpj_dados["email"]}'.center(LARGURA) + '\n').encode('latin-1', 'replace'))
            
            dados_bytes.extend(('\n').encode('latin-1', 'replace'))
            dados_bytes.extend(('VOLTE SEMPRE!'.center(LARGURA) + '\n').encode('latin-1', 'replace'))
            dados_bytes.extend(('=' * LARGURA + '\n').encode('latin-1', 'replace'))
            
            dados_bytes.extend(('\n' * 3).encode('latin-1', 'replace'))
            dados_bytes.extend(cmd_cortar.encode('latin-1', 'replace'))
            
            win32print.StartDocPrinter(hprinter, 1, ("Cupom Fiscal", None, "RAW"))
            win32print.StartPagePrinter(hprinter)
            win32print.WritePrinter(hprinter, bytes(dados_bytes))
            win32print.EndPagePrinter(hprinter)
            win32print.EndDocPrinter(hprinter)
            
        finally:
            win32print.ClosePrinter(hprinter)
        
        logger.info(f"✅ Cupom impresso: Venda #{dados_impressao.get('venda_id', '')} - R$ {dados_impressao.get('total', 0):.2f}")
        return {"success": True, "message": "Cupom impresso com sucesso!"}
        
    except Exception as e:
        logger.error(f"❌ Erro ao imprimir cupom: {e}")
        return {"success": False, "error": str(e)}

# ============================================================
# DOWNLOAD AUTOMÁTICO DO HTML
# ============================================================

def baixar_html_github() -> bool:
    try:
        logger.info("🔄 Baixando HTML do GitHub...")
        caminho_html = os.path.join(TEMPLATES_DIR, "index.html")
        
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
# ROTAS DO FLASK
# ============================================================

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"><title>SMART PDV</title>
        <style>body{{font-family:Arial;background:#0f0f1a;color:#fff;display:flex;justify-content:center;align-items:center;min-height:100vh;padding:20px;}}
        .container{{background:#16162e;border-radius:12px;padding:40px;max-width:500px;text-align:center;}}
        h1{{font-size:24px;}}button{{padding:12px 24px;background:#22c55e;color:#fff;border:0;border-radius:8px;cursor:pointer;font-size:16px;}}
        button:hover{{background:#16a34a;}}</style></head>
        <body><div class="container"><h1>🏪 SMART PDV</h1>
        <p style="color:#a0a0c0;">Baixando interface...</p>
        <button onclick="location.reload()">🔄 Recarregar</button>
        </div></body></html>
        """

@app.route('/api/versao')
def get_versao():
    return jsonify({"success": True, "versao": VERSION, "servidor_id": SERVIDOR_ID})

@app.route('/api/health')
def health_check():
    status = {
        "status": "online",
        "versao": VERSION,
        "servidor_id": SERVIDOR_ID,
        "timestamp": get_timestamp(),
        "db_status": "ok",
        "firebase_status": "ok",
        "sessoes_ativas": len(SESSOES_ATIVAS),
        "os": sys.platform,
        "data_dir": APP_DATA_DIR
    }
    
    try:
        response = requests.get(f'{FB_URL}/pdv/usuarios.json?shallow=true', timeout=5)
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
# ROTAS DE AUTENTICAÇÃO
# ============================================================

@app.route('/api/validar/cnpj/<cnpj>', methods=['GET'])
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
        senha_hash = hash_senha(senha)
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

        # PROTEÇÃO: LIMITE DE CONTAS SEM CNPJ
        with get_db_context() as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) FROM users 
                WHERE servidor_id = ? AND (cnpj = '' OR cnpj IS NULL)
            """, (SERVIDOR_ID,))
            contas_sem_cnpj = cursor.fetchone()[0]
            
            if contas_sem_cnpj >= 2 and not cnpj:
                return jsonify({
                    "success": False,
                    "error": "⚠️ Limite de 2 contas sem CNPJ neste dispositivo. Informe um CNPJ válido."
                }), 403
            
            cursor = conn.execute("""
                SELECT db_id, expira_cache FROM users 
                WHERE servidor_id = ? ORDER BY criado_em DESC LIMIT 1
            """, (SERVIDOR_ID,))
            ultimo = cursor.fetchone()
            
            if ultimo and not cnpj:
                expira = ultimo[1]
                if expira:
                    try:
                        expira_date = datetime.fromisoformat(expira)
                        if expira_date < datetime.now():
                            return jsonify({
                                "success": False,
                                "error": "⚠️ Seu plano expirou neste dispositivo. Informe um CNPJ válido."
                            }), 403
                    except:
                        pass

        # VALIDAR CNPJ
        if cnpj:
            try:
                res = requests.get(f'{request.host_url}api/cnpj/{cnpj}', timeout=10)
                if res.status_code == 200:
                    dados_cnpj = res.json()
                    if not dados_cnpj.get('success'):
                        return jsonify({
                            "success": False,
                            "error": "CNPJ inválido ou não encontrado."
                        }), 400
            except:
                pass
            
            with get_db_context() as conn:
                cursor = conn.execute("SELECT email FROM users WHERE cnpj=?", (cnpj,))
                result = cursor.fetchone()
                if result:
                    return jsonify({
                        "success": False, 
                        "error": f"Este CNPJ já está cadastrado no email: {result[0]}"
                    })
            
            if validar_cnpj_firebase(cnpj):
                return jsonify({
                    "success": False, 
                    "error": "Este CNPJ já está cadastrado em outra conta."
                })

        # EMAIL DUPLICADO
        with get_db_context() as conn:
            cursor = conn.execute("SELECT id FROM users WHERE email=?", (email,))
            if cursor.fetchone():
                return jsonify({"success": False, "error": "Email já cadastrado"})

        usuarios_firebase = carregar_todos_usuarios_firebase()
        if usuarios_firebase:
            for key, dados in usuarios_firebase.items():
                if dados.get('email') == email:
                    return jsonify({
                        "success": False,
                        "error": "Este email já está cadastrado em outra conta."
                    })

        usuario_firebase = carregar_usuario_firebase(db_id)
        if usuario_firebase and usuario_firebase.get('email') != email:
            return jsonify({"success": False, "error": "Este ID de loja pertence a outro usuário"})

        # Criar usuário local
        user_id = str(uuid.uuid4())[:8]
        with get_db_context() as conn:
            conn.execute("""
                INSERT INTO users (id, nome, email, senha, cargo, db_id, servidor_id, nome_loja, cnpj, cnpj_dados)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, nome, email, senha_hash, "Gerente", db_id, SERVIDOR_ID, nome_loja, cnpj, json.dumps(cnpj_dados)))

        # Criar no Firebase
        usuario_firebase = carregar_usuario_firebase(db_id)
        if not usuario_firebase:
            criar_usuario_firebase(db_id, nome, email, senha_hash, SERVIDOR_ID, nome_loja, cnpj, cnpj_dados)
        else:
            usuario_firebase['nome'] = nome
            usuario_firebase['email'] = email
            usuario_firebase['senha'] = senha_hash
            usuario_firebase['servidor_id'] = SERVIDOR_ID
            usuario_firebase['nome_loja'] = nome_loja
            usuario_firebase['cnpj'] = cnpj
            usuario_firebase['cnpj_dados'] = cnpj_dados
            salvar_usuario_firebase(db_id, usuario_firebase)

        return jsonify({"success": True, "message": "Conta criada com sucesso!", "db_id": db_id})
        
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
        db_id = (data.get('db_id') or '').strip()

        if not email or not senha:
            return jsonify({"success": False, "error": "Preencha email e senha"})

        senha_hash = hash_senha(senha)

        # PRIMEIRO: VERIFICAR NO FIREBASE
        usuario_firebase = buscar_usuario_por_email_firebase(email)
        
        if usuario_firebase:
            firebase_db_id = usuario_firebase.get('db_id')
            firebase_senha = usuario_firebase.get('senha')
            
            # Verificar se a senha está correta
            if not firebase_senha or senha_hash != firebase_senha:
                with get_db_context() as conn:
                    cursor = conn.execute("SELECT senha FROM users WHERE email=?", (email,))
                    local = cursor.fetchone()
                    if local and local[0] == senha_hash:
                        usuario_firebase['senha'] = senha_hash
                        salvar_usuario_firebase(firebase_db_id, usuario_firebase)
                    else:
                        return jsonify({"success": False, "error": "Email ou senha inválidos"})
            
            # CRIAR/ATUALIZAR USUÁRIO LOCAL
            with get_db_context() as conn:
                cursor = conn.execute("SELECT * FROM users WHERE email=?", (email,))
                user_local = cursor.fetchone()
                
                if user_local:
                    user_id = user_local['id']
                    conn.execute("""
                        UPDATE users SET 
                            nome = ?, 
                            senha = ?, 
                            cargo = ?, 
                            db_id = ?, 
                            servidor_id = ?, 
                            nome_loja = ?, 
                            cnpj = ?, 
                            cnpj_dados = ?,
                            session_id = ''
                        WHERE id = ?
                    """, (
                        usuario_firebase.get('nome', ''),
                        senha_hash,
                        usuario_firebase.get('cargo', 'Gerente'),
                        firebase_db_id,
                        usuario_firebase.get('servidor_id', SERVIDOR_ID),
                        usuario_firebase.get('nome_loja', 'Minha Loja'),
                        usuario_firebase.get('cnpj', ''),
                        json.dumps(usuario_firebase.get('cnpj_dados', {})),
                        user_id
                    ))
                else:
                    user_id = str(uuid.uuid4())[:8]
                    conn.execute("""
                        INSERT INTO users (id, nome, email, senha, cargo, db_id, servidor_id, nome_loja, cnpj, cnpj_dados)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        user_id,
                        usuario_firebase.get('nome', ''),
                        email,
                        senha_hash,
                        usuario_firebase.get('cargo', 'Gerente'),
                        firebase_db_id,
                        usuario_firebase.get('servidor_id', SERVIDOR_ID),
                        usuario_firebase.get('nome_loja', 'Minha Loja'),
                        usuario_firebase.get('cnpj', ''),
                        json.dumps(usuario_firebase.get('cnpj_dados', {}))
                    ))
            
            # ⭐⭐⭐ SINCRONIZAR DADOS DO FIREBASE (INCLUINDO VENDAS) ⭐⭐⭐
            sincronizar_dados(firebase_db_id)
            
            # BUSCAR USUÁRIO PARA LOGIN
            with get_db_context() as conn:
                cursor = conn.execute("""
                    SELECT id, nome, cargo, db_id, servidor_id, nome_loja, cnpj, cnpj_dados, session_id
                    FROM users WHERE email=? AND senha=?
                """, (email, senha_hash))
                user = cursor.fetchone()
            
            if user:
                user_db_id = user[3]
                
                session_id_atual = user[8] if len(user) > 8 else ''
                if session_id_atual and session_id_atual in SESSOES_ATIVAS:
                    return jsonify({
                        "success": False,
                        "error": "Esta conta já está logada em outro dispositivo."
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
                try:
                    session['cnpj_dados'] = json.loads(user[7]) if user[7] else {}
                except:
                    session['cnpj_dados'] = {}
                session['session_id'] = nova_session_id
                
                with get_db_context() as conn:
                    conn.execute("UPDATE users SET session_id=?, ultimo_acesso=? WHERE id=?",
                                (nova_session_id, get_timestamp(), user[0]))
                
                try:
                    dados_firebase = carregar_usuario_firebase(user_db_id)
                    if dados_firebase:
                        plano_id = dados_firebase.get('plano', 1)
                        expira_em = dados_firebase.get('expira_em')
                        if expira_em:
                            salvar_plano_cache(user_db_id, plano_id, expira_em)
                        if dados_firebase.get('cnpj_dados'):
                            session['cnpj_dados'] = dados_firebase.get('cnpj_dados', {})
                except:
                    pass

                SESSOES_ATIVAS[user_db_id] = nova_session_id
                
                # Sincronização automática após login
                sincronizar_automatico(user_db_id)
                
                return jsonify({
                    "success": True,
                    "id": user[0],
                    "nome": user[1],
                    "cargo": user[2],
                    "db_id": user_db_id,
                    "servidor_id": user[4],
                    "nome_loja": user[5] or 'Minha Loja',
                    "cnpj": user[6] or '',
                    "cnpj_dados": session.get('cnpj_dados', {}),
                    "plano_ativo": is_plano_ativo(user_db_id),
                    "dias_restantes": get_dias_restantes(user_db_id)
                })

        # SE NÃO ENCONTROU NO FIREBASE, VERIFICAR NO BANCO LOCAL
        with get_db_context() as conn:
            cursor = conn.execute("""
                SELECT id, nome, cargo, db_id, servidor_id, nome_loja, cnpj, cnpj_dados, session_id
                FROM users
                WHERE email=? AND senha=?
            """, (email, senha_hash))
            user = cursor.fetchone()

        if user:
            user_db_id = user[3]
            
            session_id_atual = user[8] if len(user) > 8 else ''
            if session_id_atual and session_id_atual in SESSOES_ATIVAS:
                return jsonify({
                    "success": False,
                    "error": "Esta conta já está logada em outro dispositivo."
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
            try:
                session['cnpj_dados'] = json.loads(user[7]) if user[7] else {}
            except:
                session['cnpj_dados'] = {}
            session['session_id'] = nova_session_id
            
            with get_db_context() as conn:
                conn.execute("UPDATE users SET session_id=?, ultimo_acesso=? WHERE id=?",
                            (nova_session_id, get_timestamp(), user[0]))
            
            try:
                dados_firebase = carregar_usuario_firebase(user_db_id)
                if dados_firebase:
                    plano_id = dados_firebase.get('plano', 1)
                    expira_em = dados_firebase.get('expira_em')
                    if expira_em:
                        salvar_plano_cache(user_db_id, plano_id, expira_em)
                    if dados_firebase.get('cnpj_dados'):
                        session['cnpj_dados'] = dados_firebase.get('cnpj_dados', {})
            except:
                pass

            SESSOES_ATIVAS[user_db_id] = nova_session_id
            
            sincronizar_dados(user_db_id)
            sincronizar_automatico(user_db_id)
            
            return jsonify({
                "success": True,
                "id": user[0],
                "nome": user[1],
                "cargo": user[2],
                "db_id": user_db_id,
                "servidor_id": user[4],
                "nome_loja": user[5] or 'Minha Loja',
                "cnpj": user[6] or '',
                "cnpj_dados": session.get('cnpj_dados', {}),
                "plano_ativo": is_plano_ativo(user_db_id),
                "dias_restantes": get_dias_restantes(user_db_id)
            })

        return jsonify({"success": False, "error": "Email ou senha inválidos"})
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/auth/status')
def auth_status():
    if 'usuario_id' in session:
        db_id = session.get('db_id')
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
            with get_db_context() as conn:
                conn.execute("UPDATE users SET session_id='' WHERE id=?", (usuario_id,))
        
        session.clear()
        return jsonify({"success": True})
    except Exception as e:
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
            return jsonify({
                "success": False,
                "error": "Seu plano expirou! Renove para continuar.",
                "plano_expirado": True
            }), 403

        busca = request.args.get('busca', '').strip().lower()
        with get_db_context() as conn:
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
        logger.error(f"Erro ao listar produtos: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/produtos', methods=['POST'])
def save_produto():
    try:
        data = request.json or {}
        db_id = get_db_id()

        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        if not is_plano_ativo(db_id):
            return jsonify({
                "success": False,
                "error": "Seu plano expirou! Renove para continuar.",
                "plano_expirado": True
            }), 403

        if not data.get('codigo') or not data.get('nome'):
            return jsonify({"success": False, "error": "Código e nome são obrigatórios"})

        with get_db_context() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM produtos WHERE codigo=? AND db_id=?", (data['codigo'], db_id))
            existe = cursor.fetchone()[0] > 0
        
        if not existe:
            pode, mensagem = pode_adicionar_produto(db_id, 1)
            if not pode:
                return jsonify({"success": False, "error": mensagem}), 403

        with get_db_context() as conn:
            conn.execute("""
                INSERT INTO produtos (codigo, nome, preco, estoque, categoria, db_id, ultima_atualizacao)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(codigo) DO UPDATE SET
                nome=excluded.nome, preco=excluded.preco, estoque=excluded.estoque,
                categoria=excluded.categoria, ultima_atualizacao=excluded.ultima_atualizacao
            """, (
                data['codigo'],
                data['nome'],
                data.get('preco', 0),
                data.get('estoque', 0),
                data.get('categoria', 'Geral'),
                db_id,
                get_timestamp()
            ))

        sincronizar_automatico(db_id)

        return jsonify({"success": True, "message": "Produto salvo"})
    except Exception as e:
        logger.error(f"Erro ao salvar produto: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/produtos/<codigo>', methods=['DELETE'])
def delete_produto(codigo: str):
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        if not is_plano_ativo(db_id):
            return jsonify({
                "success": False,
                "error": "Seu plano expirou! Renove para continuar.",
                "plano_expirado": True
            }), 403

        with get_db_context() as conn:
            conn.execute("DELETE FROM produtos WHERE codigo=? AND db_id=?", (codigo, db_id))

        sincronizar_automatico(db_id)

        return jsonify({"success": True, "message": "Produto excluído"})
    except Exception as e:
        logger.error(f"Erro ao excluir produto: {e}")
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
            return jsonify({
                "success": False,
                "error": "Seu plano expirou! Renove para continuar.",
                "plano_expirado": True
            }), 403

        busca = request.args.get('busca', '').strip().lower()
        with get_db_context() as conn:
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
        logger.error(f"Erro ao listar clientes: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/clientes', methods=['POST'])
def save_cliente():
    try:
        data = request.json or {}
        db_id = get_db_id()

        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        if not is_plano_ativo(db_id):
            return jsonify({
                "success": False,
                "error": "Seu plano expirou! Renove para continuar.",
                "plano_expirado": True
            }), 403

        if not data.get('nome'):
            return jsonify({"success": False, "error": "Nome é obrigatório"})

        with get_db_context() as conn:
            if data.get('id'):
                conn.execute("""
                    UPDATE clientes SET nome=?, telefone=?, email=?, divida=?, ultima_atualizacao=?
                    WHERE id=? AND db_id=?
                """, (
                    data['nome'],
                    data.get('telefone', ''),
                    data.get('email', ''),
                    data.get('divida', 0),
                    get_timestamp(),
                    data['id'],
                    db_id
                ))
            else:
                conn.execute("""
                    INSERT INTO clientes (nome, telefone, email, divida, db_id, ultima_atualizacao)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    data['nome'],
                    data.get('telefone', ''),
                    data.get('email', ''),
                    data.get('divida', 0),
                    db_id,
                    get_timestamp()
                ))

        sincronizar_automatico(db_id)

        return jsonify({"success": True, "message": "Cliente salvo"})
    except Exception as e:
        logger.error(f"Erro ao salvar cliente: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/clientes/<int:cliente_id>/pagar', methods=['POST'])
def pagar_cliente(cliente_id: int):
    try:
        data = request.json or {}
        db_id = get_db_id()
        valor = data.get('valor', 0)

        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        if not is_plano_ativo(db_id):
            return jsonify({
                "success": False,
                "error": "Seu plano expirou! Renove para continuar.",
                "plano_expirado": True
            }), 403

        with get_db_context() as conn:
            conn.execute("UPDATE clientes SET divida = MAX(0, divida - ?), ultima_atualizacao=? WHERE id=? AND db_id=?",
                        (valor, get_timestamp(), cliente_id, db_id))

        sincronizar_automatico(db_id)

        return jsonify({"success": True, "message": "Pagamento registrado"})
    except Exception as e:
        logger.error(f"Erro ao registrar pagamento: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/clientes/<int:cliente_id>', methods=['DELETE'])
def delete_cliente(cliente_id: int):
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        if not is_plano_ativo(db_id):
            return jsonify({
                "success": False,
                "error": "Seu plano expirou! Renove para continuar.",
                "plano_expirado": True
            }), 403

        with get_db_context() as conn:
            conn.execute("DELETE FROM clientes WHERE id=? AND db_id=?", (cliente_id, db_id))

        sincronizar_automatico(db_id)

        return jsonify({"success": True, "message": "Cliente excluído"})
    except Exception as e:
        logger.error(f"Erro ao excluir cliente: {e}")
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
        data_hora = get_timestamp()

        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        if not is_plano_ativo(db_id):
            return jsonify({
                "success": False,
                "error": "Seu plano expirou! Renove para continuar.",
                "plano_expirado": True
            }), 403

        itens = data.get('itens', [])
        if not itens:
            return jsonify({"success": False, "error": "Nenhum item na venda"})

        with get_db_context() as conn:
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
                            "UPDATE produtos SET estoque = estoque - ?, ultima_atualizacao=? WHERE codigo=? AND db_id=?",
                            (qtd, get_timestamp(), codigo, db_id)
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
        with get_db_context() as conn:
            cursor = conn.execute("""
                INSERT INTO vendas (data_hora, subtotal, desconto, total, metodo, itens, cliente, usuario_id, db_id, recebido, troco)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data_hora,
                data.get('subtotal', 0),
                data.get('desconto', 0),
                data.get('total', 0),
                data.get('metodo', 'Dinheiro'),
                json.dumps(itens_salvar, ensure_ascii=False),
                data.get('cliente', ''),
                usuario_id,
                db_id,
                data.get('recebido', 0),
                data.get('troco', 0)
            ))
            venda_id = cursor.lastrowid

        if data.get('metodo') == 'Fiado' and data.get('cliente'):
            try:
                with get_db_context() as conn:
                    cursor = conn.execute("SELECT id FROM clientes WHERE nome=? AND db_id=?",
                                         (data.get('cliente'), db_id))
                    cliente = cursor.fetchone()
                    if cliente:
                        conn.execute("UPDATE clientes SET divida = divida + ?, ultima_atualizacao=? WHERE id=? AND db_id=?",
                                    (data.get('total', 0), get_timestamp(), cliente[0], db_id))
                    else:
                        conn.execute("INSERT INTO clientes (nome, divida, db_id, ultima_atualizacao) VALUES (?, ?, ?, ?)",
                                    (data.get('cliente'), data.get('total', 0), db_id, get_timestamp()))
            except:
                pass

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
            'metodo': data.get('metodo', 'Dinheiro'),
            'cliente': data.get('cliente', ''),
            'usuario': session.get('nome', ''),
            'nome_loja': loja[0] if loja else session.get('nome_loja', 'Minha Loja'),
            'cnpj': loja[1] if loja else session.get('cnpj', ''),
            'cnpj_dados': cnpj_dados,
            'recebido': data.get('recebido', 0),
            'troco': data.get('troco', 0)
        }

        # ⭐⭐⭐ SINCRONIZAÇÃO AUTOMÁTICA APÓS VENDA ⭐⭐⭐
        sincronizar_automatico(db_id)

        return jsonify({
            "success": True,
            "id": venda_id,
            "data_hora": data_hora,
            "itens": itens_salvar,
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

@app.route('/api/vendas')
def get_vendas():
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        if not is_plano_ativo(db_id):
            return jsonify({
                "success": False,
                "error": "Seu plano expirou! Renove para continuar.",
                "plano_expirado": True
            }), 403

        limite = request.args.get('limite', 100, type=int)

        with get_db_context() as conn:
            cursor = conn.execute("""
                SELECT id, data_hora, subtotal, desconto, total, metodo, itens, cliente, usuario_id, recebido, troco, sincronizado_em
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
                    "usuario_id": row[8] or '',
                    "recebido": row[9] or 0,
                    "troco": row[10] or 0,
                    "sincronizado_em": row[11] if len(row) > 11 else None
                })

        return jsonify({"success": True, "vendas": vendas})
    except Exception as e:
        logger.error(f"Erro ao listar vendas: {e}")
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

        with get_db_context() as conn:
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
        logger.error(f"Erro ao verificar caixa: {e}")
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
            return jsonify({
                "success": False,
                "error": "Seu plano expirou! Renove para continuar.",
                "plano_expirado": True
            }), 403

        with get_db_context() as conn:
            cursor = conn.execute("SELECT id FROM caixa WHERE db_id=? AND status='aberto'", (db_id,))
            if cursor.fetchone():
                return jsonify({"success": False, "error": "Caixa já está aberto"})

            conn.execute("""
                INSERT INTO caixa (usuario_id, valor_abertura, data_abertura, status, db_id)
                VALUES (?, ?, ?, 'aberto', ?)
            """, (usuario_id, data.get('valor', 0), get_timestamp(), db_id))

        sincronizar_automatico(db_id)

        return jsonify({"success": True, "message": "Caixa aberto"})
    except Exception as e:
        logger.error(f"Erro ao abrir caixa: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/caixa/fechar', methods=['POST'])
def caixa_fechar():
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        if not is_plano_ativo(db_id):
            return jsonify({
                "success": False,
                "error": "Seu plano expirou! Renove para continuar.",
                "plano_expirado": True
            }), 403

        hoje = datetime.now().strftime('%Y-%m-%d')

        with get_db_context() as conn:
            cursor = conn.execute("SELECT SUM(total) FROM vendas WHERE db_id=? AND data_hora LIKE ?",
                                 (db_id, f'{hoje}%'))
            total = cursor.fetchone()[0] or 0

            conn.execute("""
                UPDATE caixa SET status='fechado', data_fechamento=?, total=?
                WHERE db_id=? AND status='aberto'
            """, (get_timestamp(), total, db_id))

        sincronizar_automatico(db_id)

        return jsonify({"success": True, "total": total})
    except Exception as e:
        logger.error(f"Erro ao fechar caixa: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/caixa/resumo')
def caixa_resumo():
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        data = request.args.get('data', datetime.now().strftime('%Y-%m-%d'))

        with get_db_context() as conn:
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
        logger.error(f"Erro no resumo do caixa: {e}")
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
            return jsonify({
                "success": False,
                "error": "Seu plano expirou! Renove para continuar.",
                "plano_expirado": True
            }), 403

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

        with get_db_context() as conn:
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
            metodos = {}
            vendas = []

            for row in cursor.fetchall():
                total_geral += row[4] or 0
                total_vendas += 1
                metodo = row[5] or 'Dinheiro'
                metodos[metodo] = metodos.get(metodo, 0) + (row[4] or 0)

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
                    "metodo": metodo,
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
        logger.error(f"Erro nas estatísticas: {e}")
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# ROTAS DE PLANOS
# ============================================================

@app.route('/api/planos')
def get_planos():
    return jsonify({
        "success": True,
        "planos": [asdict(p) for p in PLANOS]
    })

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
        plano = next((p for p in PLANOS if p.id == plano_id), None)
        expira = dados.get('expira_em')
        expira_date = datetime.fromisoformat(expira) if expira else None
        dias_restantes = (expira_date - datetime.now()).total_seconds() / 86400 if expira_date else 0
        
        limite_produtos = plano.produtos if plano else 0
        total_produtos = get_total_produtos(db_id)
        produtos_restantes = -1 if limite_produtos == -1 else max(0, limite_produtos - total_produtos)
        
        usuarios_atuais = len(get_usuarios_do_plano(db_id))

        return jsonify({
            "success": True,
            "plano": asdict(plano) if plano else None,
            "expira_em": expira,
            "dias_restantes": max(0, dias_restantes),
            "expirado": bool(expira_date and expira_date < datetime.now()),
            "limite_produtos": limite_produtos,
            "produtos_atuais": total_produtos,
            "produtos_restantes": produtos_restantes,
            "usuarios_limite": plano.usuarios if plano else 1,
            "usuarios_atuais": usuarios_atuais
        })
    except Exception as e:
        logger.error(f"Erro ao buscar status do plano: {e}")
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# ROTAS DE PIX
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

        if not MERCADO_PAGO_ACCESS_TOKEN:
            return jsonify({"success": False, "error": "Token do Mercado Pago não configurado"})

        url = "https://api.mercadopago.com/v1/payments"
        headers = {
            "Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}",
            "Content-Type": "application/json",
            "X-Idempotency-Key": str(uuid.uuid4())
        }
        payment_data = {
            "transaction_amount": float(plano.preco),
            "description": f"SMART PDV - {plano.nome}",
            "payment_method_id": "pix",
            "payer": {
                "email": "cliente@pdv.com",
                "first_name": "Cliente",
                "last_name": "PDV",
                "identification": {"type": "CPF", "number": "00000000000"}
            }
        }

        res = requests.post(url, json=payment_data, headers=headers, timeout=30)
        res_data = res.json()

        if res.status_code == 201 and res_data.get('id'):
            pix_id = str(res_data['id'])
            qr_code = res_data['point_of_interaction']['transaction_data']['qr_code']
            qr_code_base64 = res_data['point_of_interaction']['transaction_data']['qr_code_base64']

            pagamentos_pendentes[pix_id] = {
                'db_id': db_id,
                'plano_id': plano_id,
                'valor': plano.preco,
                'pago': False,
                'criado_em': get_timestamp(),
                'expira_em': (datetime.now() + timedelta(days=plano.dias)).isoformat()
            }

            return jsonify({
                "success": True,
                "pix_id": pix_id,
                "qr_code": qr_code,
                "qr_code_base64": qr_code_base64,
                "valor": plano.preco,
                "plano": asdict(plano)
            })

        return jsonify({"success": False, "error": res_data.get('message', 'Erro ao gerar PIX')})
    except Exception as e:
        logger.error(f"Erro ao criar PIX: {e}")
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

        if not MERCADO_PAGO_ACCESS_TOKEN:
            return jsonify({"success": False, "error": "Token do Mercado Pago não configurado"})

        url = f"https://api.mercadopago.com/v1/payments/{pix_id}"
        headers = {"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}"}
        res = requests.get(url, headers=headers, timeout=10)
        res_data = res.json()

        if res.status_code == 200 and res_data.get('status') == 'approved':
            _confirmar_pagamento_plano(pix_id)
            return jsonify({"pago": True})

        return jsonify({"pago": False, "status": res_data.get('status', 'pending')})
    except Exception as e:
        logger.error(f"Erro ao verificar PIX: {e}")
        return jsonify({"success": False, "error": str(e)})

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

    dados = carregar_usuario_firebase(db_id)
    if dados:
        dados['plano'] = plano_id
        dados['expira_em'] = (datetime.now() + timedelta(days=plano.dias)).isoformat()
        salvar_usuario_firebase(db_id, dados)
        salvar_plano_cache(db_id, plano_id, dados['expira_em'])

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
            return jsonify({
                "success": False,
                "error": "Seu plano expirou! Renove para continuar.",
                "plano_expirado": True
            }), 403

        with get_db_context() as conn:
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
        plano = next((p for p in PLANOS if p.id == plano_id), PLANOS[0])

        return jsonify({
            "success": True,
            "usuarios": usuarios,
            "limite_usuarios": plano.usuarios,
            "usuarios_atuais": len(usuarios)
        })
    except Exception as e:
        logger.error(f"Erro ao listar usuários: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/usuarios', methods=['POST'])
def criar_usuario():
    try:
        data = request.json or {}
        db_id = get_db_id()

        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        if not is_plano_ativo(db_id):
            return jsonify({
                "success": False,
                "error": "Seu plano expirou! Renove para continuar.",
                "plano_expirado": True
            }), 403

        nome = (data.get('nome') or '').strip()
        email = (data.get('email') or '').strip().lower()
        senha = data.get('senha') or ''

        if not nome or not email or not senha:
            return jsonify({"success": False, "error": "Preencha nome, email e senha"})

        dados = carregar_usuario_firebase(db_id)
        if not dados:
            return jsonify({"success": False, "error": "Dados do plano não encontrados"})

        plano_id = dados.get('plano', 1)
        plano = next((p for p in PLANOS if p.id == plano_id), None)
        if not plano:
            return jsonify({"success": False, "error": "Plano inválido"})

        max_usuarios = plano.usuarios

        with get_db_context() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM users WHERE db_id=?", (db_id,))
            total = cursor.fetchone()[0]

            if total >= max_usuarios:
                return jsonify({
                    "success": False,
                    "error": f"Limite de {max_usuarios} usuário(s) do plano {plano.nome} atingido."
                })

            cursor = conn.execute("SELECT id FROM users WHERE email=?", (email,))
            if cursor.fetchone():
                return jsonify({"success": False, "error": "Este email já está cadastrado"})

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
        logger.error(f"Erro ao criar usuário: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/usuarios/<user_id>', methods=['DELETE'])
def delete_usuario(user_id: str):
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        if not is_plano_ativo(db_id):
            return jsonify({
                "success": False,
                "error": "Seu plano expirou! Renove para continuar.",
                "plano_expirado": True
            }), 403

        if user_id == get_usuario_id():
            return jsonify({"success": False, "error": "Não é possível excluir seu próprio usuário"})

        with get_db_context() as conn:
            cursor = conn.execute("SELECT id FROM users WHERE id=? AND db_id=?", (user_id, db_id))
            if not cursor.fetchone():
                return jsonify({"success": False, "error": "Usuário não encontrado"})
            
            conn.execute("DELETE FROM users WHERE id=? AND db_id=?", (user_id, db_id))

        return jsonify({"success": True, "message": "Usuário excluído"})
    except Exception as e:
        logger.error(f"Erro ao excluir usuário: {e}")
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

        with get_db_context() as conn:
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
        logger.error(f"Erro ao salvar nome da loja: {e}")
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

        return jsonify({
            "success": True,
            "nome_loja": result[0] if result else 'Minha Loja',
            "cnpj": result[1] if result else '',
            "cnpj_dados": json.loads(result[2]) if result and result[2] else {}
        })
    except Exception as e:
        logger.error(f"Erro ao buscar informações da loja: {e}")
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# ROTAS DE CNPJ
# ============================================================

def _normalizar_cnpj_dados(data: Dict) -> Dict:
    end = data.get('endereco') or {}

    def pick(*keys: str, default: str = '') -> str:
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

        ultimo_erro = "CNPJ não encontrado em nenhuma fonte disponível"

        for url in apis:
            try:
                response = requests.get(url, timeout=12, headers={"User-Agent": "SMART-PDV/9.0"})
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

            except:
                continue

        return jsonify({"success": False, "error": f"Não foi possível consultar o CNPJ. {ultimo_erro}"})
    except Exception as e:
        logger.error(f"Erro ao buscar CNPJ: {e}")
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# ROTAS DE IMPRESSÃO
# ============================================================

@app.route('/api/imprimir/cupom', methods=['POST'])
def imprimir_cupom_route():
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401
        
        dados = request.json or {}

        # cnpj_dados enviado pelo frontend (state.cnpj_dados já populado no browser)
        cnpj_dados_frontend = dados.get('cnpj_dados') or {}

        with get_db_context() as conn:
            cursor = conn.execute("SELECT nome_loja, cnpj, cnpj_dados FROM users WHERE db_id=? LIMIT 1", (db_id,))
            loja = cursor.fetchone()
            if loja:
                dados['nome_loja'] = loja[0]
                dados['cnpj'] = loja[1] or ''
                try:
                    cnpj_dados_db = json.loads(loja[2]) if loja[2] else {}
                except:
                    cnpj_dados_db = {}
                # Mescla: frontend como base, banco completa campos não-vazios
                merged = {**cnpj_dados_frontend}
                for k, v in cnpj_dados_db.items():
                    if v not in (None, '', {}, []):
                        merged[k] = v
                dados['cnpj_dados'] = merged

        dados['usuario'] = session.get('nome', '')
        
        resultado = imprimir_cupom(dados)
        return jsonify(resultado)
        
    except Exception as e:
        logger.error(f"❌ Erro na rota de impressão: {e}")
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# ROTAS DE PRODUTO POR CÓDIGO DE BARRAS
# ============================================================

@app.route('/api/produto/buscar/<codigo_barras>', methods=['GET'])
def buscar_produto_barras_route(codigo_barras: str):
    try:
        resultado = buscar_produto_por_codigo_barras(codigo_barras)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# ROTAS DE SINCRONIZAÇÃO
# ============================================================

@app.route('/api/sincronizar', methods=['POST'])
def sincronizar_route():
    try:
        db_id = get_db_id()
        if not db_id:
            return jsonify({"success": False, "error": "Não autenticado"}), 401

        if not is_plano_ativo(db_id):
            return jsonify({
                "success": False,
                "error": "Seu plano expirou! Renove para continuar.",
                "plano_expirado": True
            }), 403

        resultado = sincronizar_dados(db_id)
        return jsonify(resultado)
    except Exception as e:
        logger.error(f"Erro na sincronização: {e}")
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# ROTAS DE SERVIDOR
# ============================================================

@app.route('/api/servidor/id')
def get_servidor_id_route():
    return jsonify({"success": True, "servidor_id": SERVIDOR_ID, "versao": VERSION})

@app.route('/api/baixar_html', methods=['GET'])
def baixar_html_manual():
    try:
        if baixar_html_github():
            return jsonify({"success": True, "message": "HTML baixado com sucesso!"})
        return jsonify({"success": False, "error": "Falha ao baixar HTML"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/reiniciar', methods=['POST'])
def reiniciar_servidor():
    try:
        logger.info("🔄 Reiniciando servidor...")
        import subprocess
        import sys
        subprocess.Popen([sys.executable, sys.argv[0]])
        return jsonify({"success": True, "message": "Servidor reiniciando..."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ============================================================
# THREADS EM BACKGROUND
# ============================================================

def _verificador_automatico_pix() -> None:
    while True:
        _time.sleep(15)
        try:
            if not MERCADO_PAGO_ACCESS_TOKEN:
                continue
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
                except:
                    pass
        except:
            pass

def limpar_sessoes_inativas() -> None:
    while True:
        _time.sleep(300)
        try:
            with get_db_context() as conn:
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
        except:
            pass

# ============================================================
# VERIFICAR DEPENDÊNCIAS
# ============================================================

def verificar_dependencias() -> bool:
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
        return False
    return True

# ============================================================
# INICIAR SERVIDOR
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print(f"🏪 SMART PDV v{VERSION} - VERSÃO COMPLETA UNIFICADA")
    print("=" * 60)
    
    if not verificar_dependencias():
        if IS_WINDOWS:
            print("\n❌ Dependências faltando! Execute:")
            print("pip install flask flask-cors requests pywin32 Pillow qrcode")
        else:
            print("\n❌ Dependências faltando! Execute:")
            print("pip install flask flask-cors requests")
        sys.exit(1)
    
    print(f"📁 Pasta de dados: {APP_DATA_DIR}")
    print(f"📁 Banco de dados: {DB_PATH}")
    print("=" * 60)
    
    print("📥 Verificando atualizações do HTML...")
    baixar_html_github()
    print("=" * 60)
    
    if IS_WINDOWS and IMPRESSAO_DISPONIVEL:
        print("🖨️ Impressão profissional com ESC/POS")
        print("   - Corte automático de papel")
        print("   - Formatação 80mm")
        print("   - Negrito e centralização")
        print("   - Dados da empresa no cupom")
    else:
        print("🖨️ Modo de simulação de impressão")
    
    print("=" * 60)
    print("⌨️ TECLA MESTRE:")
    print("  F1 → Tudo! (foco, busca, finalizar, confirmar)")
    print("  F2 a F12 → TOTALMENTE BLOQUEADAS")
    print("  ↑/↓ → Navegar entre opções (modais)")
    print("  ENTER → Confirmar (modais)")
    print("  ESC → Fechar modais")
    print("=" * 60)
    print("🔄 LOGIN COM FIREBASE:")
    print("  - Busca usuário no Firebase primeiro")
    print("  - SENHA SALVA NO FIREBASE ✅")
    print("  - Sincroniza dados automaticamente")
    print("  - Funciona de qualquer lugar")
    print("=" * 60)
    print("🔄 SINCRONIZAÇÃO DE VENDAS:")
    print("  - Vendas do Firebase são baixadas para o banco local")
    print("  - Dashboard mostra todas as vendas")
    print("=" * 60)
    print("🔄 SINCRONIZAÇÃO AUTOMÁTICA:")
    print("  - A cada mudança no banco de dados")
    print("  - Vendas sincronizadas em background")
    print("  - Status no header (Online/Offline)")
    print("=" * 60)
    print("🛡️ PROTEÇÃO CONTRA MÚLTIPLAS CONTAS:")
    print("  - Limite de 2 contas sem CNPJ por dispositivo")
    print("  - Bloqueio após plano expirar (sem CNPJ)")
    print("  - Validação de CNPJ via API")
    print("  - Email e CNPJ únicos no sistema")
    print("=" * 60)

    init_db()

    threading.Thread(target=_verificador_automatico_pix, daemon=True).start()
    threading.Thread(target=limpar_sessoes_inativas, daemon=True).start()

    print(f"\n🆔 Servidor: {SERVIDOR_ID}")
    print(f"📌 Versão: {VERSION}")
    print("🌐 http://localhost:5000")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
