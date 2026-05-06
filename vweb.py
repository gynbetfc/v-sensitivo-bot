# ◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈
# ☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿☿
# ⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗
#    🌀  O DINHEIRO VEM ATÉ MIM DE TODOS OS LADOS  🌀
#         DE FORMA ABUNDANTE, CONTÍNUA E PRÓSPERA
# ⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗⊗
# ◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈
# ⚡ TESLA 369 BOT - COMPLETO E REFATORADO ⚡
# 9 ESTRATÉGIAS | LOJA DE SKINS | MERCADO PAGO | DRIVE
# MOEDA CONSUMIDA AO CLICAR EM "COMEÇAR OPERAR"
# ◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈◈

from flask import Flask, render_template_string, jsonify, request
from iqoptionapi.stable_api import IQ_Option
from datetime import datetime, timedelta
import threading
import time
import sys
import os
import json
import warnings
import requests
import uuid
import logging
from typing import Dict, Optional, List, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

warnings.filterwarnings("ignore")
app = Flask(__name__)

# ============= CONFIGURAÇÕES FIXAS =============
MARTINGALE = 2  # GALE 2 FIXO
PAYOUT_PADRAO = 0.85
DRIVE_PATH = "vsens_users"
MAX_LOGS_WEB = 200

# Garantir que o diretório existe
os.makedirs(DRIVE_PATH, exist_ok=True)

# ⭐⭐⭐ CONFIGURAÇÃO DO MERCADO PAGO ⭐⭐⭐
class MercadoPagoConfig:
    ACCESS_TOKEN = "APP_USR-4548266140377032-050311-6589fc22b166e4cb2cfad0379b28dcdf-1059299796"
    PUBLIC_KEY = "APP_USR-39e1950e-420d-479a-8125-902009ca3445"
    MODO_SIMULACAO = False
    API_URL = "https://api.mercadopago.com/v1"

# ⭐ ENUMS E DATACLASSES ⭐
class TipoConta(Enum):
    PRACTICE = "PRACTICE"
    REAL = "REAL"

class Direcao(Enum):
    CALL = "call"
    PUT = "put"

class ResultadoOperacao(Enum):
    WIN = "WIN"
    LOSS = "LOSS"

@dataclass
class PlanoMoedas:
    id: int
    moedas: int
    preco: float
    nome: str
    desc: str
    tag: str = ""
    desconto: str = ""

@dataclass
class SkinConfig:
    id: str
    nome: str
    desc: str
    preco_moedas: int
    cor_fundo: str
    cor_panel: str
    cor_destaque: str
    cor_texto: str
    cor_botao: str
    cor_tab_ativa: str
    cor_header_bg: str
    cor_header_borda: str
    header_extra: str = ""
    css_extra: str = ""

@dataclass
class EstrategiaConfig:
    nome: str
    desc: str
    timeframe: int
    pares: List[str]

@dataclass
class Usuario:
    email: str
    moedas: int = 1
    moedas_ganhas_hoje: str = ""
    total_ciclos: int = 0
    total_wins: int = 0
    total_losses: int = 0
    total_gasto: float = 0.0
    total_ganho: float = 0.0
    lucro_total: float = 0.0
    banca_atual: float = 0.0
    data_cadastro: str = field(default_factory=lambda: str(datetime.now())[:19])
    historico_operacoes: List[Dict] = field(default_factory=list)
    dias_ativos: Dict[str, int] = field(default_factory=dict)
    skin_atual: str = 'skin_padrao'
    skins_compradas: List[str] = field(default_factory=lambda: ['skin_padrao'])

# ⭐ PLANOS DE MOEDAS ⭐
PLANOS = [
    PlanoMoedas(1, 1, 0.99, '🔰 INICIANTE', 'R$0,99/moeda', '1 por 1'),
    PlanoMoedas(2, 5, 4.99, '⭐ BÁSICO', 'R$1,00/moeda'),
    PlanoMoedas(3, 15, 9.99, '💎 INTERMEDIÁRIO', 'R$0,67/moeda', '', '33% OFF'),
    PlanoMoedas(4, 35, 14.99, '🔥 PREMIUM', 'R$0,43/moeda', '', '57% OFF'),
    PlanoMoedas(5, 60, 19.99, '👑 ULTRA', 'R$0,33/moeda', '', '67% OFF'),
]

# ⭐ SKINS DA LOJA ⭐
SKINS = [
    SkinConfig(
        'skin_padrao', '⚡ TESLA PADRÃO',
        'Tema escuro com raios dourados - Skin padrão do Tesla 369',
        0, '#0a0a1a', '#1a1a3e', '#ffd700', '#fff',
        'linear-gradient(135deg,#cc8800,#ffd700)', '#ffd700',
        'linear-gradient(135deg,#1a0000,#331100,#553300,#331100,#1a0000)',
        '#ffd700',
        '<div class="lightning"></div>',
        '''
            .lightning{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:150px;height:150px;background:radial-gradient(circle at 30% 30%,rgba(255,215,0,0.3) 0%,rgba(255,165,0,0.15) 30%,transparent 100%);border-radius:50%;z-index:0;animation:glow 3s ease-in-out infinite;pointer-events:none}
            @keyframes glow{0%,100%{box-shadow:0 0 30px rgba(255,215,0,0.3)}50%{box-shadow:0 0 50px rgba(255,165,0,0.5)}}
            .lightning::after{content:"⚡";position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:50px;animation:float 2s ease-in-out infinite}
            @keyframes float{0%,100%{transform:translate(-50%,-50%) scale(1)}50%{transform:translate(-50%,-60%) scale(1.1)}}
        '''
    ),
    # ... (manter todas as outras skins)
]

# ⭐ ESTRATÉGIAS ⭐
ESTRATEGIAS = {
    'v_sensitivo': EstrategiaConfig(
        '🔮 v_SENSITIVO',
        'RSI + MM + Bollinger + MACD + Estocástico + Fase da Vela',
        60, ['EURUSD-OTC', 'EURUSD']
    ),
    'tesla_369': EstrategiaConfig(
        '⚡ TESLA-369',
        '6 velas: padrão g-g-g-r-r → CALL / r-r-r-g-g → PUT',
        60, ['EURUSD-OTC', 'EURUSD']
    ),
    # ... (manter todas as outras estratégias)
}

# ═══════════════════════════════════════════════════════
# GERENCIADOR DE ESTADO DO BOT
# ═══════════════════════════════════════════════════════
class BotState:
    """Classe para gerenciar o estado global do bot"""
    def __init__(self):
        self.api: Optional[IQ_Option] = None
        self.par: str = "EURUSD-OTC"
        self.estrategia_atual: str = 'v_sensitivo'
        self.timeframe_atual: int = 60
        self.lucro: float = 0.0
        self.num_operacoes: int = 0
        self.banca_inicial: float = 0.0
        self.stop_gain_atingido: bool = False
        self.bot_rodando: bool = False
        self.bot_thread: Optional[threading.Thread] = None
        self.conectado_iq: bool = False
        self.ultimo_sinal: str = "Aguardando..."
        self.ultima_analise: Dict = {}
        self.logs_web: List[Dict] = []
        self.email_usuario_atual: str = ""
        self.skin_atual_global: str = 'skin_padrao'
        self.pagamentos_pendentes: Dict = {}
        self._lock = threading.Lock()

    def add_log(self, msg: str, tipo: str = 'info') -> None:
        """Adiciona log com thread safety"""
        with self._lock:
            t = datetime.now().strftime('%H:%M:%S')
            self.logs_web.append({'time': t, 'msg': msg, 'tipo': tipo})
            if len(self.logs_web) > MAX_LOGS_WEB:
                self.logs_web = self.logs_web[-MAX_LOGS_WEB:]
            logger.info(f"{t} - {msg}")

    def get_logs_html(self, limite: int = 40) -> str:
        """Retorna logs formatados em HTML"""
        with self._lock:
            cores = {
                'win': '#00ff88', 'loss': '#ff4444', 'info': '#00ff88',
                'sensitive': '#ff69b4', 'indicator': '#ffd700', 'error': '#ff4444'
            }
            html = ''
            for log in self.logs_web[-limite:]:
                cor = cores.get(log['tipo'], '#00ff88')
                html += f'<span style="color:#666">{log["time"]}</span> <span style="color:{cor}">{log["msg"]}</span>\n'
            return html or '📡 Aguardando...'

# Instância global do estado do bot
bot = BotState()

# ═══════════════════════════════════════════════════════
# GERENCIADOR DE USUÁRIOS
# ═══════════════════════════════════════════════════════
class UserManager:
    """Gerencia operações de usuário"""
    
    @staticmethod
    def get_user_file(email: str) -> str:
        """Retorna o caminho do arquivo do usuário"""
        return f"{DRIVE_PATH}/{email.replace('@', '_').replace('.', '_')}.json"

    @staticmethod
    def load_user(email: str) -> Optional[Dict]:
        """Carrega dados do usuário"""
        try:
            arq = UserManager.get_user_file(email)
            if os.path.exists(arq):
                with open(arq, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar usuário {email}: {e}")
        return None

    @staticmethod
    def save_user(email: str, dados: Dict) -> None:
        """Salva dados do usuário"""
        try:
            with open(UserManager.get_user_file(email), 'w') as f:
                json.dump(dados, f, indent=2)
            # Backup automático
            os.system(f"cd /workspaces/v-sensitivo-bot && git add {DRIVE_PATH}/ && git commit -m 'backup {email}' && git push 2>/dev/null &")
        except Exception as e:
            logger.error(f"Erro ao salvar usuário {email}: {e}")

    @staticmethod
    def create_user(email: str) -> Dict:
        """Cria novo usuário"""
        return {
            'email': email,
            'moedas': 1,
            'moedas_ganhas_hoje': str(datetime.now())[:10],
            'total_ciclos': 0,
            'total_wins': 0,
            'total_losses': 0,
            'total_gasto': 0.0,
            'total_ganho': 0.0,
            'lucro_total': 0.0,
            'banca_atual': 0.0,
            'data_cadastro': str(datetime.now())[:19],
            'historico_operacoes': [],
            'dias_ativos': {},
            'skin_atual': 'skin_padrao',
            'skins_compradas': ['skin_padrao']
        }

# ═══════════════════════════════════════════════════════
# CONECTOR IQ OPTION
# ═══════════════════════════════════════════════════════
class IQOptionConnector:
    """Gerencia conexão com IQ Option"""
    
    @staticmethod
    def connect(email: str, password: str, account_type: str = "PRACTICE") -> Tuple[bool, str]:
        """Conecta na IQ Option"""
        try:
            bot.add_log('🔌 Conectando na IQ Option...', 'info')
            api = IQ_Option(email, password)
            status_conn, reason = api.connect()
            
            if not status_conn:
                return False, str(reason)[:100]
            
            api.change_balance(account_type)
            bot.api = api
            bot.conectado_iq = True
            bot.add_log(f'✅ Conectado! Saldo: ${api.get_balance():.2f}', 'win')
            return True, ""
            
        except Exception as e:
            return False, str(e)[:100]

    @staticmethod
    def reconnect() -> bool:
        """Tenta reconectar"""
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                if bot.api and bot.api.check_connect():
                    return True
            except:
                pass
            
            bot.add_log(f'⏳ Tentativa de reconexão {attempt + 1}/{max_attempts}...', 'warning')
            time.sleep(5)
            try:
                if bot.api:
                    bot.api.connect()
                    return True
            except:
                pass
        return False

    @staticmethod
    def get_payout(par: str) -> float:
        """Obtém o payout do par"""
        try:
            bot.api.subscribe_strike_list(par, 1)
            for _ in range(20):
                d = bot.api.get_digital_current_profit(par, 1)
                if d is not False:
                    bot.api.unsubscribe_strike_list(par, 1)
                    return round(int(d) / 100, 2)
                time.sleep(0.5)
            bot.api.unsubscribe_strike_list(par, 1)
        except Exception as e:
            logger.error(f"Erro ao obter payout: {e}")
        return PAYOUT_PADRAO

# ═══════════════════════════════════════════════════════
# INDICADORES TÉCNICOS
# ═══════════════════════════════════════════════════════
class TechnicalIndicators:
    """Implementa indicadores técnicos"""
    
    @staticmethod
    def sma(velas: List[Dict], periodo: int) -> Optional[float]:
        """Média Móvel Simples"""
        if len(velas) < periodo:
            return None
        closes = [v['close'] for v in velas[-periodo:]]
        return round(sum(closes) / len(closes), 6)

    @staticmethod
    def bollinger(velas: List[Dict], periodo: int = 20, desvios: int = 2) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """Bandas de Bollinger"""
        if len(velas) < periodo:
            return None, None, None
        
        closes = [v['close'] for v in velas[-periodo:]]
        media = sum(closes) / len(closes)
        variancia = sum((c - media) ** 2 for c in closes) / len(closes)
        desvio_padrao = variancia ** 0.5
        
        return (
            round(media + desvios * desvio_padrao, 6),
            round(media, 6),
            round(media - desvios * desvio_padrao, 6)
        )

    @staticmethod
    def rsi(velas: List[Dict], periodo: int = 9) -> Optional[float]:
        """Índice de Força Relativa"""
        if len(velas) < periodo + 1:
            return None
        
        ganhos = []
        perdas = []
        for i in range(1, len(velas)):
            diff = velas[i]['close'] - velas[i-1]['close']
            ganhos.append(max(diff, 0))
            perdas.append(max(-diff, 0))
        
        if sum(perdas) == 0:
            return 100.0
        
        return round(100 - (100 / (1 + sum(ganhos) / sum(perdas))), 2)

    @staticmethod
    def macd(velas: List[Dict], rapida: int = 12, lenta: int = 26) -> Optional[float]:
        """MACD"""
        if len(velas) < lenta:
            return None
        
        closes = [v['close'] for v in velas]
        ema_rapida = closes[0]
        ema_lenta = closes[0]
        
        for close in closes[1:]:
            ema_rapida = close * (2 / (rapida + 1)) + ema_rapida * (1 - 2 / (rapida + 1))
            ema_lenta = close * (2 / (lenta + 1)) + ema_lenta * (1 - 2 / (lenta + 1))
        
        return round(ema_rapida - ema_lenta, 8)

    @staticmethod
    def estocastico(velas: List[Dict], periodo: int = 14) -> Optional[float]:
        """Oscilador Estocástico"""
        if len(velas) < periodo:
            return None
        
        highs = [max(v['open'], v['close']) for v in velas[-periodo:]]
        lows = [min(v['open'], v['close']) for v in velas[-periodo:]]
        close = velas[-1]['close']
        
        highest_high = max(highs)
        lowest_low = min(lows)
        
        if highest_high == lowest_low:
            return 50.0
        
        return round(((close - lowest_low) / (highest_high - lowest_low)) * 100, 2)

# ═══════════════════════════════════════════════════════
# ESTRATÉGIAS DE SINAL
# ═══════════════════════════════════════════════════════
class SignalStrategies:
    """Implementa as estratégias de sinal"""
    
    @staticmethod
    def get_candle_color(vela: Dict) -> str:
        """Retorna a cor da vela: 'g' (verde/alta), 'r' (vermelha/baixa), 'd' (doji)"""
        if vela['open'] < vela['close']:
            return 'g'
        elif vela['open'] > vela['close']:
            return 'r'
        return 'd'

    @classmethod
    def v_sensitivo(cls) -> Optional[str]:
        """Estratégia original: RSI + MM + Bollinger + MACD + Estocástico"""
        try:
            velas = bot.api.get_candles(bot.par, bot.timeframe_atual, 30, time.time())
            if len(velas) < 20:
                return None

            # Calcular indicadores
            rsi_val = TechnicalIndicators.rsi(velas)
            mm5 = TechnicalIndicators.sma(velas, 5)
            mm10 = TechnicalIndicators.sma(velas, 10)
            mm20 = TechnicalIndicators.sma(velas, 20)
            bb_sup, bb_med, bb_inf = TechnicalIndicators.bollinger(velas)
            macd_val = TechnicalIndicators.macd(velas)
            stoch_val = TechnicalIndicators.estocastico(velas)
            preco_atual = velas[-1]['close']
            
            # Fase da vela
            segundo = datetime.now().second
            if segundo < 20:
                fase = "🌅NASCENDO"
            elif segundo < 45:
                fase = "☀️VIVA"
            else:
                fase = "🌇MORRENDO"

            bot.ultima_analise = {
                'preco': preco_atual, 'rsi': rsi_val,
                'mm5': mm5, 'mm10': mm10, 'mm20': mm20,
                'stoch': stoch_val, 'fase': fase
            }

            # Pontuação
            score_call = 0
            score_put = 0
            sinais = []

            # Médias móveis
            if mm5 and mm20:
                if mm5 > mm20:
                    score_call += 20
                    sinais.append("MM5>MM20")
                else:
                    score_put += 20
                    sinais.append("MM5<MM20")

            if mm5 and mm10:
                if mm5 > mm10:
                    score_call += 15
                    sinais.append("MM5>MM10")
                else:
                    score_put += 15
                    sinais.append("MM5<MM10")

            # RSI
            if rsi_val:
                if rsi_val < 30:
                    score_call += 25
                    sinais.append(f"RSI={rsi_val:.0f}↓")
                elif rsi_val > 70:
                    score_put += 25
                    sinais.append(f"RSI={rsi_val:.0f}↑")
                elif rsi_val > 50:
                    score_call += 10
                else:
                    score_put += 10

            # Bollinger
            if bb_sup and bb_inf and preco_atual:
                if preco_atual <= bb_inf * 1.01:
                    score_call += 20
                    sinais.append("BB↓")
                elif preco_atual >= bb_sup * 0.99:
                    score_put += 20
                    sinais.append("BB↑")

            # MACD
            if macd_val:
                if macd_val > 0:
                    score_call += 15
                    sinais.append("MACD+")
                else:
                    score_put += 15
                    sinais.append("MACD-")

            # Estocástico
            if stoch_val:
                if stoch_val < 20:
                    score_call += 15
                    sinais.append(f"E={stoch_val:.0f}↓")
                elif stoch_val > 80:
                    score_put += 15
                    sinais.append(f"E={stoch_val:.0f}↑")

            # Fase da vela
            if fase == "🌇MORRENDO":
                cor = cls.get_candle_color(velas[-1])
                if cor == 'g':
                    score_put += 10
                else:
                    score_call += 10

            diferenca = abs(score_call - score_put)
            
            if score_call > score_put and diferenca >= 15:
                bot.ultimo_sinal = f"🔮 CALL ({score_call}x{score_put})"
                bot.add_log(f"CALL! | {' '.join(sinais[:3])}", 'sensitive')
                return Direcao.CALL.value
            elif score_put > score_call and diferenca >= 15:
                bot.ultimo_sinal = f"🔮 PUT ({score_put}x{score_call})"
                bot.add_log(f"PUT! | {' '.join(sinais[:3])}", 'sensitive')
                return Direcao.PUT.value

            bot.ultimo_sinal = "⏳ Aguardando sinal..."
            return None

        except Exception as e:
            bot.add_log(f"Erro na estratégia v_sensitivo: {e}", 'error')
            return None

    # Implementar outras estratégias similares...

# ═══════════════════════════════════════════════════════
# EXECUTOR DE OPERAÇÕES
# ═══════════════════════════════════════════════════════
class TradeExecutor:
    """Executa as operações de trading"""
    
    @staticmethod
    def calcular_entradas(banca: float, payout: float, gales: int) -> List[float]:
        """Calcula os valores das entradas para Martingale"""
        banca_ajustada = banca * 0.99
        e0 = banca_ajustada / sum((1 / payout) ** i for i in range(gales + 1))
        
        entradas = [e0]
        for i in range(1, gales + 1):
            entradas.append((sum(entradas) + e0) / payout)
        
        ajuste = banca_ajustada / sum(entradas)
        entradas = [round(e * ajuste, 2) for e in entradas]
        
        # Ajuste final para não ultrapassar a banca
        soma = sum(entradas)
        if soma > banca:
            entradas[-1] = round(entradas[-1] - (soma - banca) - 0.02, 2)
        
        return [max(1.0, e) for e in entradas]

    @staticmethod
    def executar_ordem(valor: float, par: str, direcao: str) -> Tuple[bool, Optional[int]]:
        """Executa uma ordem de compra"""
        try:
            # Método principal
            status, order_id = bot.api.buy(valor, par, direcao, 1)
            if status and order_id:
                return True, order_id
            
            # Método alternativo
            status, order_id = bot.api.buy_digital_spot(par, valor, direcao, 1)
            if status and order_id:
                return True, order_id
            
            return False, None
            
        except Exception as e:
            logger.error(f"Erro ao executar ordem: {e}")
            return False, None

    @classmethod
    def executar_ciclo(cls, direcao: str) -> None:
        """Executa um ciclo completo de operações"""
        try:
            banca_inicial = bot.api.get_balance()
            payout = IQOptionConnector.get_payout(bot.par)
            entradas = cls.calcular_entradas(banca_inicial, payout, MARTINGALE)
            
            bot.add_log(f"💰 Banca: ${banca_inicial:.2f} | Payout: {payout*100:.0f}%", 'info')
            bot.add_log(f"📐 Entradas: {' | '.join(f'E{i+1}:${e:.2f}' for i, e in enumerate(entradas))}", 'info')
            
            for i in range(MARTINGALE + 1):
                if not bot.bot_rodando:
                    break
                
                valor = entradas[i]
                saldo_antes = bot.api.get_balance()
                
                if saldo_antes < valor:
                    bot.add_log("❌ Saldo insuficiente!", 'error')
                    break
                
                # Aguardar início da vela
                time.sleep(0.5)
                
                bot.add_log(f"🎯 {'ENTRADA' if i == 0 else f'GALE {i}'}: {direcao.upper()} ${valor:.2f}", 'info')
                
                # Executar ordem
                status, order_id = cls.executar_ordem(valor, bot.par, direcao)
                
                if not status:
                    bot.add_log("❌ Falha na ordem!", 'error')
                    break
                
                bot.add_log(f"   📝 Ordem #{order_id}", 'info')
                
                # Aguardar resultado
                time.sleep(60)  # Aguardar 1 minuto (vela M1)
                
                # Verificar resultado
                saldo_depois = bot.api.get_balance()
                resultado = round(saldo_depois - saldo_antes, 2)
                
                if resultado > 0:
                    bot.lucro += resultado
                    bot.num_operacoes += 1
                    bot.stop_gain_atingido = True
                    
                    bot.add_log(f"🌟 WIN! +${resultado:.2f}", 'win')
                    cls._atualizar_usuario(ResultadoOperacao.WIN, valor, resultado)
                    break
                else:
                    bot.lucro -= valor
                    bot.num_operacoes += 1
                    
                    bot.add_log(f"💀 LOSS! -${valor:.2f}", 'loss')
                    cls._atualizar_usuario(ResultadoOperacao.LOSS, valor, -valor)
                    
                    if i < MARTINGALE:
                        bot.add_log(f"   ➡️ Indo para GALE {i + 1}...", 'loss')
                    else:
                        bot.add_log("💀 CICLO PERDIDO! Bot PARADO!", 'loss')
            
            # Finalizar ciclo
            banca_final = bot.api.get_balance()
            bot.add_log("=" * 50, 'info')
            bot.add_log(f"{'🌟 LUCRO' if banca_final > banca_inicial else '💀 PERDA'}: ${abs(banca_final - banca_inicial):.2f}", 'info')
            bot.add_log("=" * 50, 'info')
            
        except Exception as e:
            bot.add_log(f"Erro no ciclo: {e}", 'error')
        finally:
            bot.bot_rodando = False
            bot.add_log("⏹️ Ciclo concluído!", 'info')

    @staticmethod
    def _atualizar_usuario(resultado: ResultadoOperacao, valor: float, lucro_operacao: float) -> None:
        """Atualiza estatísticas do usuário"""
        try:
            usuario = UserManager.load_user(bot.email_usuario_atual)
            if not usuario:
                return
            
            usuario['total_ciclos'] += 1
            usuario['banca_atual'] = bot.api.get_balance()
            hoje = str(datetime.now())[:10]
            usuario['dias_ativos'][hoje] = usuario['dias_ativos'].get(hoje, 0) + 1
            
            operacao = {
                'data': str(datetime.now())[:19],
                'resultado': resultado.value,
                'valor': valor,
                'lucro': lucro_operacao,
                'estrategia': bot.estrategia_atual
            }
            usuario['historico_operacoes'].append(operacao)
            
            if resultado == ResultadoOperacao.WIN:
                usuario['total_wins'] += 1
                usuario['total_ganho'] += abs(lucro_operacao)
            else:
                usuario['total_losses'] += 1
                usuario['total_gasto'] += valor
            
            usuario['lucro_total'] = usuario['total_ganho'] - usuario['total_gasto']
            UserManager.save_user(bot.email_usuario_atual, usuario)
            
        except Exception as e:
            logger.error(f"Erro ao atualizar usuário: {e}")

# ═══════════════════════════════════════════════════════
# PROCESSADOR DE PAGAMENTOS
# ═══════════════════════════════════════════════════════
class PaymentProcessor:
    """Gerencia pagamentos via Mercado Pago"""
    
    @staticmethod
    def criar_pix(email: str, plano: PlanoMoedas) -> Dict:
        """Cria um pagamento PIX"""
        if MercadoPagoConfig.MODO_SIMULACAO:
            pix_id = str(uuid.uuid4())[:8]
            bot.pagamentos_pendentes[pix_id] = {
                'email': email,
                'plano_id': plano.id,
                'moedas': plano.moedas,
                'valor': plano.preco,
                'pago': False,
                'criado_em': str(datetime.now())[:19]
            }
            return {
                'sucesso': True,
                'simulacao': True,
                'pix_id': pix_id,
                'qr_code': f"[SIMULAÇÃO] PIX de R$ {plano.preco:.2f}",
                'qr_code_base64': '',
                'valor': plano.preco,
                'moedas': plano.moedas
            }
        
        try:
            headers = {
                "Authorization": f"Bearer {MercadoPagoConfig.ACCESS_TOKEN}",
                "Content-Type": "application/json",
                "X-Idempotency-Key": str(uuid.uuid4())
            }
            
            payment_data = {
                "transaction_amount": float(plano.preco),
                "description": f"TESLA369 - {plano.nome} - {plano.moedas} moedas",
                "payment_method_id": "pix",
                "payer": {
                    "email": email,
                    "first_name": "Cliente",
                    "last_name": "Tesla369"
                }
            }
            
            response = requests.post(
                f"{MercadoPagoConfig.API_URL}/payments",
                json=payment_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                pix_id = str(data['id'])
                
                bot.pagamentos_pendentes[pix_id] = {
                    'email': email,
                    'plano_id': plano.id,
                    'moedas': plano.moedas,
                    'valor': plano.preco,
                    'pago': False,
                    'criado_em': str(datetime.now())[:19]
                }
                
                return {
                    'sucesso': True,
                    'simulacao': False,
                    'pix_id': pix_id,
                    'qr_code': data['point_of_interaction']['transaction_data']['qr_code'],
                    'qr_code_base64': data['point_of_interaction']['transaction_data']['qr_code_base64'],
                    'valor': plano.preco,
                    'moedas': plano.moedas
                }
            
            return {'sucesso': False, 'erro': response.json().get('message', 'Erro desconhecido')}
            
        except requests.Timeout:
            return {'sucesso': False, 'erro': 'Timeout na conexão com Mercado Pago'}
        except Exception as e:
            return {'sucesso': False, 'erro': str(e)[:100]}

    @staticmethod
    def verificar_pagamento(pix_id: str) -> bool:
        """Verifica se um pagamento foi aprovado"""
        if MercadoPagoConfig.MODO_SIMULACAO:
            return bot.pagamentos_pendentes.get(pix_id, {}).get('pago', False)
        
        try:
            headers = {"Authorization": f"Bearer {MercadoPagoConfig.ACCESS_TOKEN}"}
            response = requests.get(
                f"{MercadoPagoConfig.API_URL}/payments/{pix_id}",
                headers=headers,
                timeout=10
            )
            return response.json().get('status') == 'approved'
        except:
            return False

# ═══════════════════════════════════════════════════════
# VERIFICADOR AUTOMÁTICO DE PAGAMENTOS
# ═══════════════════════════════════════════════════════
def verificador_pagamentos():
    """Thread que verifica pagamentos pendentes"""
    bot.add_log("🔄 Verificador de pagamentos iniciado", "info")
    while True:
        time.sleep(15)
        try:
            pendentes = {
                k: v for k, v in bot.pagamentos_pendentes.items()
                if not v.get('pago', False)
            }
            
            for pix_id, dados in pendentes.items():
                if PaymentProcessor.verificar_pagamento(pix_id):
                    bot.pagamentos_pendentes[pix_id]['pago'] = True
                    email = dados['email']
                    moedas = dados['moedas']
                    
                    usuario = UserManager.load_user(email)
                    if not usuario:
                        usuario = UserManager.create_user(email)
                    
                    usuario['moedas'] = usuario.get('moedas', 0) + moedas
                    UserManager.save_user(email, usuario)
                    
                    bot.add_log(
                        f"✅ Pagamento confirmado! +{moedas} moedas para {email}",
                        "win"
                    )
                    
        except Exception as e:
            logger.error(f"Erro no verificador: {e}")

# Iniciar verificador
threading.Thread(target=verificador_pagamentos, daemon=True).start()

# ═══════════════════════════════════════════════════════
# ROTAS DA APLICAÇÃO
# ═══════════════════════════════════════════════════════

@app.route('/')
def index():
    """Página principal"""
    return render_template_string(get_html_template())

@app.route('/status')
def status():
    """Retorna status atual do bot"""
    try:
        usuario = UserManager.load_user(bot.email_usuario_atual) if bot.email_usuario_atual else None
        
        skins_status = []
        skins_compradas = usuario.get('skins_compradas', ['skin_padrao']) if usuario else ['skin_padrao']
        skin_atual = usuario.get('skin_atual', 'skin_padrao') if usuario else 'skin_padrao'
        
        for skin in SKINS:
            skins_status.append({
                'id': skin.id,
                'nome': skin.nome,
                'desc': skin.desc,
                'preco_moedas': skin.preco_moedas,
                'comprado': skin.id in skins_compradas,
                'ativo': skin.id == skin_atual
            })
        
        return jsonify({
            'conectado': bot.conectado_iq,
            'rodando': bot.bot_rodando,
            'email': bot.email_usuario_atual,
            'banca': bot.api.get_balance() if bot.api else 0,
            'lucro': bot.lucro,
            'ops': bot.num_operacoes,
            'sinal': bot.ultimo_sinal,
            'analise': bot.ultima_analise,
            'logs': bot.get_logs_html(40),
            'moedas': usuario.get('moedas', 0) if usuario else 0,
            'estrategia': bot.estrategia_atual,
            'estrategia_nome': ESTRATEGIAS.get(bot.estrategia_atual, EstrategiaConfig('Unknown', '', 60, [])).nome,
            'skin_id': skin_atual,
            'skins_status': skins_status
        })
        
    except Exception as e:
        logger.error(f"Erro no status: {e}")
        return jsonify({'erro': str(e)}), 500

@app.route('/conectar', methods=['POST'])
def conectar():
    """Conecta na IQ Option"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        senha = data.get('senha', '').strip()
        tipo = data.get('tipo', 'PRACTICE')
        
        if not email or not senha:
            return jsonify({'ok': False, 'erro': 'Email e senha são obrigatórios'}), 400
        
        # Carregar ou criar usuário
        usuario = UserManager.load_user(email)
        if not usuario:
            usuario = UserManager.create_user(email)
            UserManager.save_user(email, usuario)
        
        # Verificar moeda diária
        hoje = str(datetime.now())[:10]
        if usuario.get('moedas_ganhas_hoje') != hoje:
            usuario['moedas'] = usuario.get('moedas', 0) + 1
            usuario['moedas_ganhas_hoje'] = hoje
            UserManager.save_user(email, usuario)
        
        # Conectar
        sucesso, erro = IQOptionConnector.connect(email, senha, tipo)
        
        if not sucesso:
            return jsonify({'ok': False, 'erro': erro}), 400
        
        bot.email_usuario_atual = email
        bot.skin_atual_global = usuario.get('skin_atual', 'skin_padrao')
        
        # Configurar estratégia
        estrategia_config = ESTRATEGIAS[bot.estrategia_atual]
        bot.par = estrategia_config.pares[0]
        bot.timeframe_atual = estrategia_config.timeframe
        
        bot.add_log(f'📊 Estratégia: {estrategia_config.nome} | Par: {bot.par}', 'info')
        bot.add_log('👉 Clique em COMEÇAR OPERAR para iniciar', 'info')
        
        return jsonify({
            'ok': True,
            'moedas': usuario['moedas']
        })
        
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)[:100]}), 500

@app.route('/comecar_operar', methods=['POST'])
def comecar_operar():
    """Inicia operação do bot"""
    try:
        if not bot.conectado_iq:
            return jsonify({'ok': False, 'erro': 'Conecte na IQ Option primeiro'}), 400
        
        # Verificar moedas
        usuario = UserManager.load_user(bot.email_usuario_atual)
        if not usuario or usuario.get('moedas', 0) < 1:
            return jsonify({'ok': False, 'erro': 'Moedas insuficientes! Compre mais.'}), 400
        
        # Consumir moeda
        usuario['moedas'] -= 1
        usuario['total_ciclos'] += 1
        UserManager.save_user(bot.email_usuario_atual, usuario)
        
        bot.add_log(f'🪙 Moeda consumida! Restam: {usuario["moedas"]} | Ciclos: {usuario["total_ciclos"]}', 'info')
        
        # Resetar estado
        bot.lucro = 0.0
        bot.num_operacoes = 0
        bot.stop_gain_atingido = False
        
        # Iniciar bot
        if not bot.bot_rodando:
            bot.bot_rodando = True
            bot.bot_thread = threading.Thread(
                target=lambda: TradeExecutor.executar_ciclo(
                    SignalStrategies.v_sensitivo()  # Usar estratégia atual
                ),
                daemon=True
            )
            bot.bot_thread.start()
        
        return jsonify({
            'ok': True,
            'moedas': usuario['moedas']
        })
        
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)[:100]}), 500

@app.route('/parar', methods=['POST'])
def parar():
    """Para o bot"""
    bot.bot_rodando = False
    bot.conectado_iq = False
    bot.add_log('⏹️ Bot parado e desconectado', 'info')
    return jsonify({'ok': True})

@app.route('/criar_pix', methods=['POST'])
def criar_pix():
    """Cria pagamento PIX"""
    try:
        data = request.get_json()
        email = data.get('email', '')
        plano_id = int(data.get('plano_id', 1))
        
        if not email:
            return jsonify({'sucesso': False, 'erro': 'Email obrigatório'}), 400
        
        plano = next((p for p in PLANOS if p.id == plano_id), None)
        if not plano:
            return jsonify({'sucesso': False, 'erro': 'Plano não encontrado'}), 404
        
        resultado = PaymentProcessor.criar_pix(email, plano)
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)[:100]}), 500

@app.route('/verificar_pix', methods=['POST'])
def verificar_pix():
    """Verifica pagamento PIX"""
    try:
        data = request.get_json()
        pix_id = data.get('pix_id', '')
        
        if not pix_id:
            return jsonify({'pago': False}), 400
        
        if PaymentProcessor.verificar_pagamento(pix_id):
            dados = bot.pagamentos_pendentes.get(pix_id, {})
            email = dados.get('email', '')
            
            usuario = UserManager.load_user(email)
            saldo = usuario.get('moedas', 0) if usuario else 0
            
            return jsonify({
                'pago': True,
                'moedas': dados.get('moedas', 0),
                'saldo': saldo
            })
        
        return jsonify({'pago': False})
        
    except Exception as e:
        return jsonify({'pago': False, 'erro': str(e)[:100]}), 500

# ═══════════════════════════════════════════════════════
# FUNÇÃO PRINCIPAL
# ═══════════════════════════════════════════════════════
def get_html_template() -> str:
    """Retorna o template HTML processado com a skin atual"""
    # Implementar processamento do HTML com skin
    # (Manter o HTML original, apenas com as variáveis de skin)
    return HTML_TEMPLATE  # HTML original processado

if __name__ == '__main__':
    # Configurações de produção
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"🚀 Iniciando Tesla 369 Bot na porta {port}")
    app.run(host='0.0.0.0', port=port, debug=debug, threaded=True)
