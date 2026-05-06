# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                    🧙‍♂️🔮 v-SENSITIVE BOT - COMPLETO 🔮🧙‍♀️                    ║
# ║  ⚡ SCRIPT ÚNICO | BANCO DE DADOS | FÁCIL EDITAR | NOVAS ESTRATÉGIAS      ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# ==============================================================================
# 📦 IMPORTS
# ==============================================================================
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
import base64
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, field

warnings.filterwarnings("ignore")
app = Flask(__name__)

# ==============================================================================
# 🗄️ SEÇÃO 1: BANCO DE DADOS (GITHUB)
# ==============================================================================
# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  CONFIGURE AQUI SEU TOKEN E REPOSITÓRIO DO GITHUB                      ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class DatabaseConfig:
    """Configurações do Banco de Dados"""
    # 🔧 CONFIGURADO COM SUAS CREDENCIAIS
    GITHUB_TOKEN = "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"  # ✅ Seu token
    GITHUB_USER = "gynbetfc"                                     # ✅ Seu usuário
    GITHUB_REPO = "v-sensitivo-bot"                              # ✅ Seu repositório
    GITHUB_BRANCH = "main"
    DATA_PATH = "data/users"             # Pasta onde salva os usuários
    
    # Fallback local se GitHub não funcionar
    LOCAL_DATA_PATH = "local_database"
    
    # Criar pasta local se não existir
    os.makedirs(LOCAL_DATA_PATH, exist_ok=True)

class UserDatabase:
    """
    🗄️ BANCO DE DADOS DOS USUÁRIOS
    Salva automaticamente no GitHub + Backup Local
    """
    
    def __init__(self):
        self.token = DatabaseConfig.GITHUB_TOKEN
        self.user = DatabaseConfig.GITHUB_USER
        self.repo = DatabaseConfig.GITHUB_REPO
        self.branch = DatabaseConfig.GITHUB_BRANCH
        self.data_path = DatabaseConfig.DATA_PATH
        self.local_path = DatabaseConfig.LOCAL_DATA_PATH
        
        # Headers para API do GitHub
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Cache local (evita muitas chamadas à API)
        self.cache = {}
        self.cache_time = {}
        self.cache_duration = 30  # segundos
        
        # Verificar conexão
        self.github_online = self._check_github()
        if self.github_online:
            print("✅ Banco de Dados: GitHub conectado!")
        else:
            print("⚠️ Banco de Dados: Usando modo local (GitHub offline)")
    
    def _check_github(self) -> bool:
        """Verifica se GitHub está acessível"""
        try:
            url = f"https://api.github.com/repos/{self.user}/{self.repo}"
            r = requests.get(url, headers=self.headers, timeout=5)
            return r.status_code == 200
        except:
            return False
    
    def _get_user_filename(self, email: str) -> str:
        """Converte email em nome de arquivo seguro"""
        return email.replace('@', '_at_').replace('.', '_dot_') + '.json'
    
    def _get_github_file(self, filename: str) -> Optional[Dict]:
        """Lê arquivo do GitHub"""
        # Verificar cache
        if filename in self.cache:
            cache_age = (datetime.now() - self.cache_time[filename]).seconds
            if cache_age < self.cache_duration:
                return self.cache[filename]
        
        url = f"https://api.github.com/repos/{self.user}/{self.repo}/contents/{self.data_path}/{filename}"
        
        try:
            r = requests.get(url, headers=self.headers, timeout=10)
            if r.status_code == 200:
                data = r.json()
                content = base64.b64decode(data['content']).decode('utf-8')
                result = {
                    'content': content,
                    'sha': data['sha']
                }
                
                # Atualizar cache
                self.cache[filename] = result
                self.cache_time[filename] = datetime.now()
                
                return result
        except Exception as e:
            print(f"❌ Erro ao ler do GitHub: {e}")
        
        return None
    
    def _save_github_file(self, filename: str, content: str, message: str) -> bool:
        """Salva arquivo no GitHub"""
        # Verificar se arquivo já existe
        existing = self._get_github_file(filename)
        
        url = f"https://api.github.com/repos/{self.user}/{self.repo}/contents/{self.data_path}/{filename}"
        
        data = {
            "message": message,
            "content": base64.b64encode(content.encode('utf-8')).decode('utf-8'),
            "branch": self.branch
        }
        
        if existing and 'sha' in existing:
            data['sha'] = existing['sha']
        
        try:
            r = requests.put(url, json=data, headers=self.headers, timeout=10)
            
            if r.status_code in [200, 201]:
                # Atualizar cache
                response_data = r.json()
                self.cache[filename] = {
                    'content': content,
                    'sha': response_data.get('sha', '')
                }
                self.cache_time[filename] = datetime.now()
                return True
            else:
                print(f"❌ GitHub: {r.status_code} - {r.json().get('message', 'Erro')}")
        except Exception as e:
            print(f"❌ Erro ao salvar no GitHub: {e}")
        
        return False
    
    def _save_local(self, filename: str, content: str):
        """Backup local"""
        filepath = os.path.join(self.local_path, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _load_local(self, filename: str) -> Optional[Dict]:
        """Carrega do backup local"""
        filepath = os.path.join(self.local_path, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                return {'content': content, 'sha': None}
        return None
    
    # ============= OPERAÇÕES DE USUÁRIO =============
    
    def save_user(self, email: str, user_data: Dict) -> bool:
        """Salva usuário no GitHub + Local"""
        filename = self._get_user_filename(email)
        content = json.dumps(user_data, indent=2, ensure_ascii=False)
        message = f"💾 Update: {email}"
        
        # Sempre salvar local
        self._save_local(filename, content)
        
        # Tentar GitHub
        if self.github_online:
            success = self._save_github_file(filename, content, message)
            if not success:
                print(f"⚠️ Salvo apenas localmente: {email}")
            return success
        
        return True  # Pelo menos local salvou
    
    def load_user(self, email: str) -> Optional[Dict]:
        """Carrega usuário (GitHub → Local)"""
        filename = self._get_user_filename(email)
        user_data = None
        
        # Tentar GitHub primeiro
        if self.github_online:
            github_data = self._get_github_file(filename)
            if github_data:
                try:
                    user_data = json.loads(github_data['content'])
                    user_data['_github_sha'] = github_data['sha']
                    
                    # Sincronizar com local
                    self._save_local(filename, github_data['content'])
                    
                    return user_data
                except json.JSONDecodeError:
                    print(f"❌ Erro ao decodificar JSON de {email}")
        
        # Fallback para local
        local_data = self._load_local(filename)
        if local_data:
            try:
                user_data = json.loads(local_data['content'])
                return user_data
            except json.JSONDecodeError:
                pass
        
        return None
    
    def create_user(self, email: str) -> Dict:
        """Cria novo usuário com 1 moeda grátis"""
        user_data = {
            'email': email,
            'moedas': 1,  # 1 moeda grátis
            'moedas_ganhas_hoje': str(datetime.now())[:10],
            'total_ciclos': 0,
            'total_wins': 0,
            'total_losses': 0,
            'total_gasto': 0.0,
            'total_ganho': 0.0,
            'lucro_total': 0.0,
            'banca_atual': 0.0,
            'data_cadastro': str(datetime.now())[:19],
            'ultimo_login': str(datetime.now())[:19],
            'historico_operacoes': [],
            'dias_ativos': {},
            'estrategia_preferida': 'v_sensitive',  # ← NOVO: estratégia favorita
            'configuracoes': {  # ← NOVO: configurações pessoais
                'martingale': 2,
                'stop_gain': 1,
                'timeframe': 60
            }
        }
        
        self.save_user(email, user_data)
        print(f"✅ Novo usuário criado: {email}")
        return user_data
    
    def daily_coin(self, email: str) -> bool:
        """Concede moeda diária grátis"""
        user = self.load_user(email)
        if not user:
            return False
        
        hoje = str(datetime.now())[:10]
        if user.get('moedas_ganhas_hoje') != hoje:
            user['moedas'] = user.get('moedas', 0) + 1
            user['moedas_ganhas_hoje'] = hoje
            self.save_user(email, user)
            print(f"🎁 Moeda diária: {email}")
            return True
        
        return False
    
    def consume_coin(self, email: str) -> Tuple[bool, int]:
        """Consome 1 moeda para operar"""
        user = self.load_user(email)
        if not user:
            return False, 0
        
        if user.get('moedas', 0) < 1:
            return False, 0
        
        user['moedas'] -= 1
        user['total_ciclos'] = user.get('total_ciclos', 0) + 1
        self.save_user(email, user)
        
        return True, user['moedas']
    
    def add_coins(self, email: str, amount: int) -> int:
        """Adiciona moedas (compra)"""
        user = self.load_user(email)
        if not user:
            user = self.create_user(email)
        
        user['moedas'] = user.get('moedas', 0) + amount
        self.save_user(email, user)
        
        return user['moedas']
    
    def add_operation(self, email: str, operation: Dict):
        """Registra uma operação no histórico"""
        user = self.load_user(email)
        if not user:
            return
        
        # Atualizar estatísticas
        if operation['resultado'] == 'WIN':
            user['total_wins'] = user.get('total_wins', 0) + 1
            user['total_ganho'] = user.get('total_ganho', 0.0) + operation['lucro']
        else:
            user['total_losses'] = user.get('total_losses', 0) + 1
            user['total_gasto'] = user.get('total_gasto', 0.0) + operation['valor']
        
        user['lucro_total'] = user['total_ganho'] - user['total_gasto']
        
        # Adicionar ao histórico
        if 'historico_operacoes' not in user:
            user['historico_operacoes'] = []
        
        user['historico_operacoes'].append(operation)
        
        # Manter últimas 100 operações
        if len(user['historico_operacoes']) > 100:
            user['historico_operacoes'] = user['historico_operacoes'][-100:]
        
        # Registrar dia ativo
        hoje = str(datetime.now())[:10]
        if 'dias_ativos' not in user:
            user['dias_ativos'] = {}
        user['dias_ativos'][hoje] = user['dias_ativos'].get(hoje, 0) + 1
        
        self.save_user(email, user)
    
    def reset_user(self, email: str) -> Dict:
        """Reseta estatísticas do usuário"""
        user = self.create_user(email)
        user['moedas'] = 0
        self.save_user(email, user)
        return user

# Inicializar banco de dados
db = UserDatabase()

# ==============================================================================
# ⚙️ SEÇÃO 2: CONFIGURAÇÕES DO BOT
# ==============================================================================
# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  CONFIGURE AQUI AS CONFIGURAÇÕES PADRÃO DO BOT                         ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class BotConfig:
    """Configurações do Bot - Fáceis de editar"""
    
    # ═══════════ IQ OPTION ═══════════
    PAR_PADRAO = "EURUSD-OTC"
    TIMEFRAME_PADRAO = 60
    TIPO_CONTA_PADRAO = "PRACTICE"  # "PRACTICE" ou "REAL"
    
    # ═══════════ MARTINGALE ═══════════
    MARTINGALE_PADRAO = 2  # Número de gales (1 = sem gale)
    MARTINGALE_MAXIMO = 5  # Limite máximo de gales
    
    # ═══════════ STOP GAIN ═══════════
    STOP_GAIN_PERCENTUAL = 1.0  # % de lucro para parar
    STOP_LOSS_PERCENTUAL = 5.0  # % de perda para parar
    
    # ═══════════ PAYOUT ═══════════
    PAYOUT_PADRAO = 0.85  # Usado quando não consegue pegar payout real
    
    # ═══════════ TIMERS ═══════════
    TIMEOUT_ENTRE_CICLOS = 5  # Segundos entre ciclos
    TIMEOUT_ORDEM = 30  # Timeout para executar ordem
    
    # ═══════════ MERCADO PAGO ═══════════
    MERCADO_PAGO_TOKEN = os.environ.get(
        "MERCADO_PAGO_TOKEN",
        "APP_USR-4548266140377032-050311-6589fc22b166e4cb2cfad0379b28dcdf-1059299796"
    )
    MODO_SIMULACAO_PIX = False
    
    # ═══════════ PLANOS DE MOEDAS ═══════════
    PLANOS = [
        {'id': 1, 'moedas': 1, 'preco': 0.99, 'nome': '🔰 INICIANTE', 'desc': 'R$0,99/moeda', 'tag': '1 por 1'},
        {'id': 2, 'moedas': 5, 'preco': 4.99, 'nome': '⭐ BÁSICO', 'desc': 'R$1,00/moeda'},
        {'id': 3, 'moedas': 15, 'preco': 9.99, 'nome': '💎 INTERMEDIÁRIO', 'desc': 'R$0,67/moeda', 'desconto': '33% OFF'},
        {'id': 4, 'moedas': 35, 'preco': 14.99, 'nome': '🔥 PREMIUM', 'desc': 'R$0,43/moeda', 'desconto': '57% OFF'},
        {'id': 5, 'moedas': 60, 'preco': 19.99, 'nome': '👑 ULTRA', 'desc': 'R$0,33/moeda', 'desconto': '67% OFF'},
    ]

# ==============================================================================
# 📊 SEÇÃO 3: INDICADORES TÉCNICOS
# ==============================================================================

class Indicators:
    """
    📊 INDICADORES TÉCNICOS
    Todos os cálculos de análise técnica
    """
    
    @staticmethod
    def sma(candles: List[Dict], period: int) -> Optional[float]:
        """Média Móvel Simples"""
        if len(candles) < period:
            return None
        closes = [c['close'] for c in candles[-period:]]
        return round(sum(closes) / len(closes), 6)
    
    @staticmethod
    def ema(candles: List[Dict], period: int) -> Optional[float]:
        """Média Móvel Exponencial"""
        if len(candles) < period:
            return None
        
        closes = [c['close'] for c in candles]
        multiplier = 2 / (period + 1)
        ema = closes[0]
        
        for close in closes[1:]:
            ema = (close - ema) * multiplier + ema
        
        return round(ema, 6)
    
    @staticmethod
    def rsi(candles: List[Dict], period: int = 9) -> Optional[float]:
        """Índice de Força Relativa"""
        if len(candles) < period + 1:
            return None
        
        gains = []
        losses = []
        
        for i in range(1, len(candles)):
            diff = candles[i]['close'] - candles[i-1]['close']
            gains.append(max(diff, 0))
            losses.append(max(-diff, 0))
        
        # Usar apenas os últimos 'period' valores
        avg_gain = sum(gains[-period:]) / period if gains else 0
        avg_loss = sum(losses[-period:]) / period if losses else 0
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        return round(100 - (100 / (1 + rs)), 2)
    
    @staticmethod
    def bollinger_bands(candles: List[Dict], period: int = 20, std_dev: int = 2) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """Bandas de Bollinger - Retorna (superior, media, inferior)"""
        if len(candles) < period:
            return None, None, None
        
        closes = [c['close'] for c in candles[-period:]]
        mean = sum(closes) / len(closes)
        
        # Desvio padrão
        variance = sum((c - mean) ** 2 for c in closes) / len(closes)
        std = variance ** 0.5
        
        upper = round(mean + std_dev * std, 6)
        middle = round(mean, 6)
        lower = round(mean - std_dev * std, 6)
        
        return upper, middle, lower
    
    @staticmethod
    def macd(candles: List[Dict], fast: int = 12, slow: int = 26, signal: int = 9) -> Optional[float]:
        """MACD - Retorna o valor do MACD"""
        if len(candles) < slow:
            return None
        
        closes = [c['close'] for c in candles]
        
        # EMA rápida
        ema_fast = closes[0]
        for close in closes[1:]:
            ema_fast = (close - ema_fast) * (2 / (fast + 1)) + ema_fast
        
        # EMA lenta
        ema_slow = closes[0]
        for close in closes[1:]:
            ema_slow = (close - ema_slow) * (2 / (slow + 1)) + ema_slow
        
        return round(ema_fast - ema_slow, 8)
    
    @staticmethod
    def stochastic(candles: List[Dict], period: int = 14, smooth_k: int = 3) -> Optional[float]:
        """Oscilador Estocástico"""
        if len(candles) < period:
            return None
        
        highs = [max(c['open'], c['close']) for c in candles[-period:]]
        lows = [min(c['open'], c['close']) for c in candles[-period:]]
        close = candles[-1]['close']
        
        highest_high = max(highs)
        lowest_low = min(lows)
        
        if highest_high == lowest_low:
            return 50.0
        
        return round(((close - lowest_low) / (highest_high - lowest_low)) * 100, 2)
    
    @staticmethod
    def atr(candles: List[Dict], period: int = 14) -> Optional[float]:
        """Average True Range - Volatilidade"""
        if len(candles) < period + 1:
            return None
        
        tr_values = []
        for i in range(1, len(candles)):
            high = max(candles[i]['open'], candles[i]['close'])
            low = min(candles[i]['open'], candles[i]['close'])
            prev_close = candles[i-1]['close']
            
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            tr_values.append(tr)
        
        return round(sum(tr_values[-period:]) / period, 6)
    
    @staticmethod
    def get_candle_color(candle: Dict) -> str:
        """Retorna a cor da vela: 'g' (verde), 'r' (vermelha), 'd' (doji)"""
        if candle['open'] < candle['close']:
            return 'g'
        elif candle['open'] > candle['close']:
            return 'r'
        return 'd'
    
    @staticmethod
    def get_candle_phase(second: int) -> str:
        """Retorna a fase da vela baseado no segundo atual"""
        if second < 20:
            return "🌅 NASCENDO"
        elif second < 45:
            return "☀️ VIVA"
        else:
            return "🌇 MORRENDO"

# ==============================================================================
# 🎯 SEÇÃO 4: ESTRATÉGIAS DE SINAL
# ==============================================================================
# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  ADICIONE NOVAS ESTRATÉGIAS AQUI!                                      ║
# ║  Cada estratégia é uma função que retorna 'call', 'put' ou None        ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class SignalStrategies:
    """
    🎯 ESTRATÉGIAS DE SINAL
    Coleção de todas as estratégias do bot
    """
    
    def __init__(self, api, par: str, timeframe: int):
        self.api = api
        self.par = par
        self.timeframe = timeframe
        self.indicators = Indicators()
        
        # Dicionário de estratégias disponíveis
        self.strategies = {
            'v_sensitive': {
                'name': '🔮 v_SENSITIVE',
                'function': self.v_sensitive,
                'description': 'RSI + MM + Bollinger + MACD + Estocástico + Fase da Vela',
                'timeframe': 60
            },
            'tesla_369': {
                'name': '⚡ TESLA 369',
                'function': self.tesla_369,
                'description': 'Padrão de 6 velas: ggg-rr → CALL / rrr-gg → PUT',
                'timeframe': 60
            },
            'mhi_filtered': {
                'name': '📊 MHI FILTRADO',
                'function': self.mhi_filtered,
                'description': '5 velas + MM + filtro de cor dominante',
                'timeframe': 60
            },
            # 🆕 ADICIONE NOVAS ESTRATÉGIAS AQUI:
            # 'minha_estrategia': {
            #     'name': '🌟 MINHA ESTRATÉGIA',
            #     'function': self.minha_estrategia,
            #     'description': 'Descrição da minha estratégia',
            #     'timeframe': 60
            # },
        }
    
    def get_signal(self, strategy_name: str = 'v_sensitive') -> Optional[str]:
        """Executa a estratégia selecionada"""
        if strategy_name in self.strategies:
            return self.strategies[strategy_name]['function']()
        return self.v_sensitive()  # Fallback
    
    def get_available_strategies(self) -> Dict:
        """Retorna lista de estratégias disponíveis"""
        return {
            key: {
                'name': val['name'],
                'description': val['description'],
                'timeframe': val['timeframe']
            }
            for key, val in self.strategies.items()
        }
    
    # ═══════════════════════════════════════════════
    # ESTRATÉGIA 1: v_SENSITIVE (ORIGINAL)
    # ═══════════════════════════════════════════════
    def v_sensitive(self) -> Optional[str]:
        """Estratégia original: Análise multi-indicador com pontuação ponderada"""
        try:
            # Carregar velas
            candles = self.api.get_candles(self.par, self.timeframe, 30, time.time())
            if len(candles) < 20:
                return None
            
            # Calcular indicadores
            rsi_value = self.indicators.rsi(candles, 9)
            mm5 = self.indicators.sma(candles, 5)
            mm10 = self.indicators.sma(candles, 10)
            mm20 = self.indicators.sma(candles, 20)
            bb_upper, bb_middle, bb_lower = self.indicators.bollinger_bands(candles)
            macd_value = self.indicators.macd(candles)
            stoch_value = self.indicators.stochastic(candles)
            
            current_price = candles[-1]['close']
            current_second = datetime.now().second
            phase = self.indicators.get_candle_phase(current_second)
            
            # Salvar para dashboard
            global ultima_analise
            ultima_analise = {
                'preco': current_price,
                'rsi': rsi_value,
                'mm5': mm5,
                'mm10': mm10,
                'mm20': mm20,
                'stoch': stoch_value,
                'fase': phase
            }
            
            # Sistema de pontuação
            score_call = 0
            score_put = 0
            signals = []
            
            # MM5 vs MM20
            if mm5 and mm20:
                if mm5 > mm20:
                    score_call += 20
                    signals.append("✅ MM5>MM20")
                else:
                    score_put += 20
                    signals.append("❌ MM5<MM20")
            
            # MM5 vs MM10
            if mm5 and mm10:
                if mm5 > mm10:
                    score_call += 15
                    signals.append("✅ MM5>MM10")
                else:
                    score_put += 15
                    signals.append("❌ MM5<MM10")
            
            # RSI
            if rsi_value:
                if rsi_value < 30:
                    score_call += 25
                    signals.append(f"📈 RSI={rsi_value:.0f} (sobrevendido)")
                elif rsi_value > 70:
                    score_put += 25
                    signals.append(f"📉 RSI={rsi_value:.0f} (sobrecomprado)")
                elif rsi_value > 50:
                    score_call += 10
                else:
                    score_put += 10
            
            # Bollinger
            if bb_upper and bb_lower and current_price:
                if current_price <= bb_lower * 1.01:
                    score_call += 20
                    signals.append("📊 Preço na banda inferior")
                elif current_price >= bb_upper * 0.99:
                    score_put += 20
                    signals.append("📊 Preço na banda superior")
            
            # MACD
            if macd_value:
                if macd_value > 0:
                    score_call += 15
                    signals.append("📈 MACD positivo")
                else:
                    score_put += 15
                    signals.append("📉 MACD negativo")
            
            # Estocástico
            if stoch_value:
                if stoch_value < 20:
                    score_call += 15
                    signals.append(f"📊 Estocástico={stoch_value:.0f} (baixo)")
                elif stoch_value > 80:
                    score_put += 15
                    signals.append(f"📊 Estocástico={stoch_value:.0f} (alto)")
            
            # Fase da vela
            if phase == "🌇 MORRENDO":
                candle_color = self.indicators.get_candle_color(candles[-1])
                if candle_color == 'g':
                    score_put += 10
                    signals.append("🌇 Vela verde morrendo")
                else:
                    score_call += 10
                    signals.append("🌇 Vela vermelha morrendo")
            
            # Decisão final
            difference = abs(score_call - score_put)
            
            add_log(f"🔮 {phase} | CALL:{score_call} PUT:{score_put} | {' | '.join(signals[:3])}", 'indicator')
            
            if score_call > score_put and difference >= 15:
                global ultimo_sinal
                ultimo_sinal = f"🔮 CALL ({score_call}×{score_put})"
                add_log(f"✅ CALL! ({score_call}×{score_put})", 'sensitive')
                return 'call'
            
            elif score_put > score_call and difference >= 15:
                ultimo_sinal = f"🔮 PUT ({score_put}×{score_call})"
                add_log(f"❌ PUT! ({score_put}×{score_call})", 'sensitive')
                return 'put'
            
            ultimo_sinal = "⏳ Aguardando..."
            return None
            
        except Exception as e:
            add_log(f"❌ Erro v_sensitive: {e}", 'error')
            return None
    
    # ═══════════════════════════════════════════════
    # ESTRATÉGIA 2: TESLA 369
    # ═══════════════════════════════════════════════
    def tesla_369(self) -> Optional[str]:
        """Estratégia Tesla 369: Padrão de velas específico"""
        try:
            candles = self.api.get_candles(self.par, self.timeframe, 6, time.time())
            if len(candles) < 6:
                return None
            
            # Cores das velas
            colors = ''.join(self.indicators.get_candle_color(c) for c in candles)
            
            add_log(f"⚡ 369 | Velas: {colors}", 'indicator')
            
            # Padrões
            # CALL: g,g,g,r,r (3 verdes + 2 vermelhas)
            if colors == 'gggrrr' or (colors[0]=='g' and colors[1]=='g' and colors[2]=='g' 
                                       and colors[3]=='r' and colors[4]=='r' and colors[5]=='r'):
                add_log("⚡ 369: CALL!", 'sensitive')
                return 'call'
            
            # PUT: r,r,r,g,g (3 vermelhas + 2 verdes)
            if colors == 'rrrggg' or (colors[0]=='r' and colors[1]=='r' and colors[2]=='r'
                                       and colors[3]=='g' and colors[4]=='g' and colors[5]=='g'):
                add_log("⚡ 369: PUT!", 'sensitive')
                return 'put'
            
            return None
            
        except Exception as e:
            add_log(f"❌ Erro tesla_369: {e}", 'error')
            return None
    
    # ═══════════════════════════════════════════════
    # ESTRATÉGIA 3: MHI FILTRADO
    # ═══════════════════════════════════════════════
    def mhi_filtered(self) -> Optional[str]:
        """Estratégia MHI com filtro de média móvel"""
        try:
            candles = self.api.get_candles(self.par, self.timeframe, 22, time.time())
            if len(candles) < 22:
                return None
            
            # Últimas 5 velas
            recent_candles = candles[-5:]
            colors = ''.join(self.indicators.get_candle_color(c) for c in recent_candles)
            
            # Média móvel das 21 velas anteriores
            mm = sum(c['close'] for c in candles[-22:-1]) / 21
            current_price = candles[-1]['close']
            
            add_log(f"📊 MHI | Velas: {colors} | MM: {mm:.5f}", 'indicator')
            
            # Condições
            count_green = colors.count('g')
            count_red = colors.count('r')
            
            if current_price > mm and count_red > count_green and 'd' not in colors:
                add_log("📊 MHI: CALL!", 'sensitive')
                return 'call'
            
            if current_price < mm and count_green > count_red and 'd' not in colors:
                add_log("📊 MHI: PUT!", 'sensitive')
                return 'put'
            
            return None
            
        except Exception as e:
            add_log(f"❌ Erro mhi_filtered: {e}", 'error')
            return None
    
    # 🆕 ADICIONE NOVAS ESTRATÉGIAS AQUI:
    # def minha_estrategia(self) -> Optional[str]:
    #     """Minha estratégia personalizada"""
    #     # Sua lógica aqui
    #     return None

# ==============================================================================
# 💰 SEÇÃO 5: EXECUTOR DE TRADES
# ==============================================================================

class TradeExecutor:
    """
    💰 EXECUTOR DE TRADES
    Gerencia entradas, Martingale e execução de ordens
    """
    
    def __init__(self, api, par: str):
        self.api = api
        self.par = par
    
    def calculate_entries(self, balance: float, payout: float, gales: int) -> List[float]:
        """Calcula valores das entradas para Martingale"""
        adjusted_balance = balance * 0.99
        e0 = adjusted_balance / sum((1 / payout) ** i for i in range(gales + 1))
        
        entries = [e0]
        for i in range(1, gales + 1):
            entries.append((sum(entries) + e0) / payout)
        
        # Ajuste final
        factor = adjusted_balance / sum(entries)
        entries = [round(e * factor, 2) for e in entries]
        
        # Garantir que não ultrapasse a banca
        total = sum(entries)
        if total > balance:
            entries[-1] = round(entries[-1] - (total - balance) - 0.02, 2)
        
        return [max(1.0, e) for e in entries]
    
    def execute_order(self, amount: float, direction: str) -> Tuple[bool, Optional[int]]:
        """Executa uma ordem de compra"""
        try:
            # Método 1: buy()
            status, order_id = self.api.buy(amount, self.par, direction, 1)
            if status and order_id:
                return True, order_id
            
            # Método 2: buy_digital_spot()
            time.sleep(0.5)
            status, order_id = self.api.buy_digital_spot(self.par, amount, direction, 1)
            if status and order_id:
                return True, order_id
            
            return False, None
            
        except Exception as e:
            add_log(f"❌ Erro na ordem: {e}", 'error')
            return False, None
    
    def get_payout(self) -> float:
        """Obtém payout real do par"""
        try:
            # Método 1: get_all_profit
            profits = self.api.get_all_profit()
            if profits and 'binary' in profits and self.par in profits['binary']:
                return float(profits['binary'][self.par]) / 100
            
            # Método 2: get_digital_current_profit
            self.api.subscribe_strike_list(self.par, 1)
            time.sleep(0.5)
            profit = self.api.get_digital_current_profit(self.par, 1)
            self.api.unsubscribe_strike_list(self.par, 1)
            
            if profit and profit != False:
                return round(int(profit) / 100, 2)
            
        except:
            pass
        
        return BotConfig.PAYOUT_PADRAO
    
    def wait_candle_start(self) -> bool:
        """Aguarda início de uma nova vela"""
        add_log("⏳ Aguardando início da vela...", 'info')
        
        while datetime.now().second > 5:
            if not bot_rodando:
                return False
            time.sleep(0.3)
        
        while True:
            if not bot_rodando:
                return False
            
            candles = self.api.get_candles(self.par, BotConfig.TIMEFRAME_PADRAO, 1, time.time())
            if candles:
                timestamp1 = candles[0]['from']
                time.sleep(0.5)
                
                candles = self.api.get_candles(self.par, BotConfig.TIMEFRAME_PADRAO, 1, time.time())
                if candles and candles[0]['from'] == timestamp1:
                    add_log("✅ Vela confirmada!", 'info')
                    return True
            
            time.sleep(0.3)
    
    def wait_candle_close(self, entry_timestamp: int) -> bool:
        """Aguarda vela fechar"""
        add_log("⏳ Aguardando resultado...", 'info')
        
        while True:
            if not bot_rodando:
                return False
            
            try:
                candles = self.api.get_candles(self.par, BotConfig.TIMEFRAME_PADRAO, 1, time.time())
                if candles and candles[0]['from'] != entry_timestamp:
                    add_log("✅ Vela fechou!", 'info')
                    return True
            except:
                pass
            
            time.sleep(0.3)
    
    def execute_cycle(self, direction: str, gales: int) -> None:
        """Executa um ciclo completo de operações"""
        global lucro, NumDeOperacoes, bot_rodando
        
        # Consumir moeda
        if email_usuario_atual:
            success, remaining = db.consume_coin(email_usuario_atual)
            if not success:
                add_log("❌ Moedas insuficientes!", 'error')
                bot_rodando = False
                return
            add_log(f"🪙 Moeda consumida! Restam: {remaining}", 'info')
        
        # Preparar ciclo
        initial_balance = self.api.get_balance()
        payout = self.get_payout()
        entries = self.calculate_entries(initial_balance, payout, gales)
        
        add_log(f"💰 Banca: ${initial_balance:.2f} | Payout: {payout:.0%}", 'info')
        add_log(f"📐 E1:${entries[0]:.2f} | E2:${entries[1]:.2f} | E3:${entries[2]:.2f}", 'info')
        
        # Executar entradas
        for i in range(gales + 1):
            if not bot_rodando:
                break
            
            amount = entries[i]
            
            # Aguardar vela
            if not self.wait_candle_start():
                break
            
            # Verificar saldo
            balance_before = self.api.get_balance()
            if balance_before < amount:
                add_log("❌ Saldo insuficiente!", 'error')
                break
            
            # Executar ordem
            print()
            entry_type = "ENTRADA" if i == 0 else f"GALE {i}"
            add_log(f"🎯 {entry_type}: {direction.upper()} ${amount:.2f}", 'info')
            
            success, order_id = self.execute_order(amount, direction)
            
            if not success:
                add_log("❌ Falha na ordem!", 'error')
                break
            
            add_log(f"📝 Ordem #{order_id}", 'info')
            
            # Aguardar resultado
            time.sleep(0.3)
            candles = self.api.get_candles(self.par, BotConfig.TIMEFRAME_PADRAO, 1, time.time())
            entry_timestamp = candles[0]['from'] if candles else 0
            
            if not self.wait_candle_close(entry_timestamp):
                break
            
            # Verificar resultado
            balance_after = self.api.get_balance()
            result = round(balance_after - balance_before, 2)
            lucro += result
            
            if result > 0:
                # WIN!
                add_log(f"🌟 WIN! +${result:.2f}", 'win')
                NumDeOperacoes += 1
                
                # Registrar no banco
                if email_usuario_atual:
                    db.add_operation(email_usuario_atual, {
                        'data': str(datetime.now())[:19],
                        'resultado': 'WIN',
                        'valor': amount,
                        'lucro': result,
                        'estrategia': estrategia_atual
                    })
                
                break  # Stop gain
            
            else:
                # LOSS
                add_log(f"💀 LOSS! -${amount:.2f}", 'loss')
                
                # Registrar no banco
                if email_usuario_atual:
                    db.add_operation(email_usuario_atual, {
                        'data': str(datetime.now())[:19],
                        'resultado': 'LOSS',
                        'valor': amount,
                        'lucro': -amount,
                        'estrategia': estrategia_atual
                    })
                
                if i < gales:
                    add_log(f"➡️ Indo para GALE {i+1}...", 'loss')
                else:
                    add_log("💀 Ciclo completo perdido!", 'loss')
        
        # Resumo final
        final_balance = self.api.get_balance()
        print()
        add_log("=" * 50, 'info')
        profit = final_balance - initial_balance
        emoji = "🌟" if profit >= 0 else "💀"
        add_log(f"{emoji} {'LUCRO' if profit >= 0 else 'PERDA'}: ${abs(profit):.2f} | Banca: ${final_balance:.2f}", 'info')
        add_log("=" * 50, 'info')

# ==============================================================================
# 🚀 SEÇÃO 6: BOT PRINCIPAL
# ==============================================================================

class VSensitiveBot:
    """
    🚀 BOT PRINCIPAL
    Controla todo o fluxo do bot
    """
    
    def __init__(self):
        self.api = None
        self.par = BotConfig.PAR_PADRAO
        self.timeframe = BotConfig.TIMEFRAME_PADRAO
        self.martingale = BotConfig.MARTINGALE_PADRAO
        self.stop_gain = BotConfig.STOP_GAIN_PERCENTUAL
        self.is_running = False
        self.current_strategy = 'v_sensitive'
        
        self.signals = None
        self.executor = None
        
    def connect(self, email: str, password: str, account_type: str = "PRACTICE") -> Tuple[bool, str]:
        """Conecta na IQ Option"""
        try:
            add_log("🔌 Conectando na IQ Option...", 'info')
            
            self.api = IQ_Option(email, password)
            status, reason = self.api.connect()
            
            if not status:
                return False, str(reason)[:100]
            
            self.api.change_balance(account_type)
            
            # Inicializar componentes
            self.signals = SignalStrategies(self.api, self.par, self.timeframe)
            self.executor = TradeExecutor(self.api, self.par)
            
            balance = self.api.get_balance()
            add_log(f"✅ Conectado! Saldo: ${balance:.2f}", 'win')
            
            return True, ""
            
        except Exception as e:
            return False, str(e)[:100]
    
    def start(self):
        """Inicia o bot"""
        if not self.api:
            add_log("❌ Não conectado!", 'error')
            return
        
        self.is_running = True
        
        global bot_rodando
        bot_rodando = True
        
        add_log("🚀 Bot iniciado!", 'win')
        add_log(f"📊 Estratégia: {self.signals.strategies[self.current_strategy]['name']}", 'info')
        add_log(f"💱 Par: {self.par} | ⏱️ Timeframe: {self.timeframe}s", 'info')
        
        # Loop principal
        while self.is_running and bot_rodando:
            try:
                # Obter sinal
                direction = self.signals.get_signal(self.current_strategy)
                
                if direction:
                    self.executor.execute_cycle(direction, self.martingale)
                
                time.sleep(0.3)
                
            except Exception as e:
                add_log(f"❌ Erro no loop: {e}", 'error')
                time.sleep(5)
                
                # Tentar reconectar
                try:
                    if self.api:
                        self.api.connect()
                except:
                    pass
        
        add_log("⏹️ Bot parado!", 'info')
    
    def stop(self):
        """Para o bot"""
        self.is_running = False
        global bot_rodando
        bot_rodando = False
    
    def change_strategy(self, strategy_name: str):
        """Muda a estratégia atual"""
        if strategy_name in self.signals.strategies:
            self.current_strategy = strategy_name
            strategy_config = self.signals.strategies[strategy_name]
            self.timeframe = strategy_config['timeframe']
            add_log(f"📊 Estratégia alterada: {strategy_config['name']}", 'info')
            return True
        return False
    
    def get_status(self) -> Dict:
        """Retorna status atual do bot"""
        if not self.api:
            return {'conectado': False}
        
        try:
            balance = self.api.get_balance()
        except:
            balance = 0
        
        return {
            'conectado': True,
            'rodando': self.is_running,
            'banca': balance,
            'par': self.par,
            'timeframe': self.timeframe,
            'estrategia': self.current_strategy,
            'estrategia_nome': self.signals.strategies.get(self.current_strategy, {}).get('name', 'Unknown')
        }

# ==============================================================================
# 💳 SEÇÃO 7: MERCADO PAGO
# ==============================================================================

class MercadoPago:
    """
    💳 INTEGRAÇÃO MERCADO PAGO
    Gera e verifica pagamentos PIX
    """
    
    def __init__(self):
        self.token = BotConfig.MERCADO_PAGO_TOKEN
        self.simulation = BotConfig.MODO_SIMULACAO_PIX
        self.pending_payments = {}
        self.base_url = "https://api.mercadopago.com/v1"
    
    def create_pix(self, email: str, plan: Dict) -> Dict:
        """Cria um pagamento PIX"""
        if self.simulation:
            pix_id = str(uuid.uuid4())[:8]
            self.pending_payments[pix_id] = {
                'email': email,
                'moedas': plan['moedas'],
                'valor': plan['preco'],
                'pago': False,
                'criado_em': str(datetime.now())[:19]
            }
            return {
                'sucesso': True,
                'simulacao': True,
                'pix_id': pix_id,
                'qr_code': f"[SIMULAÇÃO] PIX R${plan['preco']:.2f}",
                'valor': plan['preco'],
                'moedas': plan['moedas']
            }
        
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "X-Idempotency-Key": str(uuid.uuid4())
            }
            
            payment_data = {
                "transaction_amount": float(plan['preco']),
                "description": f"V-SENSITIVE - {plan['nome']} - {plan['moedas']} moedas",
                "payment_method_id": "pix",
                "payer": {
                    "email": email,
                    "first_name": "Cliente",
                    "last_name": "VSensitive"
                }
            }
            
            response = requests.post(
                f"{self.base_url}/payments",
                json=payment_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                pix_id = str(data['id'])
                
                self.pending_payments[pix_id] = {
                    'email': email,
                    'moedas': plan['moedas'],
                    'valor': plan['preco'],
                    'pago': False,
                    'criado_em': str(datetime.now())[:19]
                }
                
                return {
                    'sucesso': True,
                    'pix_id': pix_id,
                    'qr_code': data['point_of_interaction']['transaction_data']['qr_code'],
                    'qr_code_base64': data['point_of_interaction']['transaction_data']['qr_code_base64'],
                    'valor': plan['preco'],
                    'moedas': plan['moedas']
                }
            
            return {'sucesso': False, 'erro': response.json().get('message', 'Erro desconhecido')}
            
        except Exception as e:
            return {'sucesso': False, 'erro': str(e)[:100]}
    
    def check_payment(self, pix_id: str) -> Dict:
        """Verifica se pagamento foi aprovado"""
        if self.simulation:
            if pix_id in self.pending_payments:
                self.pending_payments[pix_id]['pago'] = True
                dados = self.pending_payments[pix_id]
                
                # Adicionar moedas
                new_balance = db.add_coins(dados['email'], dados['moedas'])
                
                return {
                    'pago': True,
                    'moedas': dados['moedas'],
                    'saldo': new_balance
                }
            return {'pago': False}
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.base_url}/payments/{pix_id}",
                headers=headers,
                timeout=10
            )
            
            if response.json().get('status') == 'approved':
                if pix_id in self.pending_payments and not self.pending_payments[pix_id]['pago']:
                    self.pending_payments[pix_id]['pago'] = True
                    dados = self.pending_payments[pix_id]
                    
                    # Adicionar moedas
                    new_balance = db.add_coins(dados['email'], dados['moedas'])
                    
                    return {
                        'pago': True,
                        'moedas': dados['moedas'],
                        'saldo': new_balance
                    }
                
                return {'pago': True}
            
            return {'pago': False}
            
        except:
            return {'pago': False}

# Inicializar Mercado Pago
mp = MercadoPago()

# ==============================================================================
# 📝 SEÇÃO 8: SISTEMA DE LOGS
# ==============================================================================

MAX_LOGS = 200
logs_web = []
ultimo_sinal = "Aguardando..."
ultima_analise = {}

def add_log(msg: str, tipo: str = 'info'):
    """Adiciona log ao sistema"""
    global logs_web
    
    timestamp = datetime.now().strftime('%H:%M:%S')
    logs_web.append({
        'time': timestamp,
        'msg': msg,
        'tipo': tipo
    })
    
    # Limitar tamanho
    if len(logs_web) > MAX_LOGS:
        logs_web = logs_web[-MAX_LOGS:]
    
    # Print no console
    print(f"{timestamp} - {msg}")
    sys.stdout.flush()

def get_logs_html(limit: int = 40) -> str:
    """Retorna logs formatados em HTML"""
    colors = {
        'win': '#00ff88',
        'loss': '#ff4444',
        'info': '#00ff88',
        'sensitive': '#ff69b4',
        'indicator': '#ffd700',
        'error': '#ff4444',
        'warning': '#ffaa00'
    }
    
    html = ''
    for log in logs_web[-limit:]:
        color = colors.get(log['tipo'], '#00ff88')
        html += f'<span style="color:#666">{log["time"]}</span> '
        html += f'<span style="color:{color}">{log["msg"]}</span>\n'
    
    return html or '📡 Aguardando...'

# ==============================================================================
# 🌐 SEÇÃO 9: VARIÁVEIS GLOBAIS
# ==============================================================================

# Bot
bot = VSensitiveBot()
bot_rodando = False
bot_thread = None

# Status
lucro = 0.0
NumDeOperacoes = 0
email_usuario_atual = ""
estrategia_atual = 'v_sensitive'

# ==============================================================================
# 🎨 SEÇÃO 10: HTML TEMPLATE
# ==============================================================================

def get_html_template() -> str:
    """Retorna o HTML completo do bot"""
    
    # Gerar HTML dos planos
    planos_html = ''
    for plano in BotConfig.PLANOS:
        desconto_html = f'<div><span class="plano-desconto">{plano["desconto"]}</span></div>' if 'desconto' in plano else ''
        tag_html = f'<div class="plano-tag">{plano["tag"]}</div>' if 'tag' in plano else ''
        
        planos_html += f'''
        <div class="plano-card" id="plano{plano['id']}" onclick="selecionarPlano({plano['id']})">
            <div style="color:#cc66ff;font-size:11px">{plano['nome']}</div>
            <div class="plano-moedas">🪙 {plano['moedas']}</div>
            <div class="plano-preco">R$ {plano['preco']:.2f}</div>
            <div class="plano-desc">{plano['desc']}</div>
            {desconto_html}
            {tag_html}
            <button class="btn btn-buy" style="display:none;margin-top:8px;padding:8px" 
                    id="btnPlano{plano['id']}" 
                    onclick="event.stopPropagation();pagarComPix({plano['id']})">
                💳 PAGAR COM PIX
            </button>
        </div>'''
    
    # HTML completo
    html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧙‍♂️🔮 v_SENSITIVE</title>
    <style>
        *{{margin:0;padding:0;box-sizing:border-box}}
        body{{background:#0a0a1a;color:#fff;font-family:'Courier New',monospace;padding:10px}}
        .container{{max-width:900px;margin:0 auto}}
        
        /* TABS */
        .tabs{{display:flex;gap:5px;margin-bottom:10px;flex-wrap:wrap}}
        .tab{{padding:10px 15px;background:#1a1a3e;border:1px solid #333;border-radius:10px 10px 0 0;cursor:pointer;color:#888;font-size:12px}}
        .tab.active{{background:#9933ff;color:#fff;font-weight:bold}}
        
        /* PAINÉIS */
        .panel{{display:none;background:#1a1a3e;padding:15px;border-radius:0 10px 10px 10px;border:1px solid #333;margin-bottom:10px}}
        .panel.active{{display:block}}
        
        /* HEADER */
        .header{{background:linear-gradient(135deg,#0d001a,#1a0033,#2d0055,#1a0033,#0d001a);padding:20px;border-radius:20px;text-align:center;border:3px solid #9933ff;position:relative;overflow:hidden;margin-bottom:15px}}
        .crystal-ball{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:150px;height:150px;background:radial-gradient(circle at 30% 30%,rgba(200,150,255,0.3) 0%,rgba(153,51,255,0.15) 30%,transparent 100%);border-radius:50%;z-index:0;animation:crystalGlow 4s ease-in-out infinite;pointer-events:none}}
        @keyframes crystalGlow{{0%,100%{{box-shadow:0 0 30px rgba(153,51,255,0.3)}}50%{{box-shadow:0 0 50px rgba(200,100,255,0.5)}}}}
        .crystal-ball::after{{content:'🔮';position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:50px;animation:floatCrystal 3s ease-in-out infinite}}
        @keyframes floatCrystal{{0%,100%{{transform:translate(-50%,-50%) scale(1)}}50%{{transform:translate(-50%,-60%) scale(1.08)}}}}
        .header h1{{color:#cc66ff;font-size:20px;text-shadow:0 0 30px #9933ff;position:relative;z-index:3}}
        .header p{{color:#ffd700;font-size:10px;position:relative;z-index:3}}
        
        /* MANTRA */
        .mantra{{color:#ffd700;text-align:center;margin:8px 0;font-size:10px}}
        
        /* BOTÕES */
        .btn{{padding:10px 16px;border:none;border-radius:8px;font-weight:bold;cursor:pointer;font-size:12px;font-family:'Courier New',monospace}}
        .btn-start{{background:linear-gradient(135deg,#6600cc,#9933ff);color:#fff}}
        .btn-stop{{background:linear-gradient(135deg,#cc0000,#ff4444);color:#fff}}
        .btn-buy{{background:linear-gradient(135deg,#00aa44,#00cc55);color:#fff;width:100%;padding:12px;font-size:14px}}
        .btn-info{{background:linear-gradient(135deg,#0066cc,#3399ff);color:#fff;font-size:11px;padding:8px 14px}}
        .btn-reset{{background:linear-gradient(135deg,#cc0000,#ff6600);color:#fff;font-size:11px;padding:8px 14px}}
        
        /* DASHBOARD */
        .dashboard{{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px;margin-bottom:10px}}
        .card{{background:#1a1a3e;padding:10px;border-radius:10px;border:1px solid #333;text-align:center}}
        .card .label{{color:#888;font-size:9px}}
        .card .value{{color:#ffd700;font-size:15px;font-weight:bold;margin-top:4px}}
        
        /* INDICADORES */
        .indicators{{display:grid;grid-template-columns:repeat(auto-fit,minmax(90px,1fr));gap:6px;margin-bottom:10px}}
        .ind-card{{background:#111;padding:6px;border-radius:8px;border:1px solid #222;text-align:center;font-size:10px}}
        .ind-card .ind-label{{color:#666;font-size:9px}}
        .ind-card .ind-value{{color:#ffd700;font-size:11px}}
        
        /* TERMINAL */
        .terminal{{background:#000;color:#00ff88;padding:12px;border-radius:10px;height:200px;overflow-y:auto;font-size:10px;line-height:1.4;white-space:pre-wrap;border:1px solid #333}}
        
        /* STATUS BAR */
        .barra-status{{display:flex;justify-content:space-between;padding:8px;background:#1a1a3e;border-radius:10px;margin-top:10px;font-size:10px}}
        .status-dot{{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:4px}}
        .status-dot.active{{background:#00ff88;animation:pulse 1s infinite}}
        .status-dot.inactive{{background:#888}}
        @keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:0.3}}}}
        
        /* PLANOS */
        .planos-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}}
        .plano-card{{background:#111;padding:12px;border-radius:10px;border:2px solid #222;text-align:center;cursor:pointer;transition:all 0.3s ease}}
        .plano-card:hover{{border-color:#9933ff;background:#1a1a2e}}
        .plano-card.selecionado{{border-color:#ffd700;box-shadow:0 0 20px rgba(255,215,0,0.4);background:#1a1a2e}}
        .plano-moedas{{font-size:24px;color:#ffd700;font-weight:bold}}
        .plano-preco{{font-size:14px;color:#00ff88;margin:5px 0}}
        .plano-desc{{font-size:9px;color:#888;margin-top:4px}}
        .plano-tag{{background:#9933ff22;color:#cc66ff;font-size:9px;padding:2px 8px;border-radius:10px;display:inline-block;margin-top:4px}}
        .plano-desconto{{background:#ff4444;color:#fff;font-size:9px;padding:2px 6px;border-radius:10px;display:inline-block;margin-left:4px}}
        
        /* MODAL */
        .modal-overlay{{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.85);z-index:1000;justify-content:center;align-items:center}}
        .modal-overlay.active{{display:flex}}
        .modal-pagamento{{background:#1a1a3e;border:2px solid #9933ff;border-radius:15px;padding:25px;max-width:400px;width:90%;text-align:center}}
        .modal-pagamento h3{{color:#ffd700;margin-bottom:15px}}
        .pix-qrcode{{background:#fff;padding:15px;border-radius:10px;display:inline-block;margin:10px 0}}
        .pix-qrcode img{{max-width:200px}}
        .pix-copiavel{{background:#000;color:#00ff88;padding:10px;border-radius:8px;font-size:9px;word-break:break-all;margin:10px 0;max-height:60px;overflow-y:auto;cursor:pointer}}
        
        /* RELATÓRIO */
        .relatorio-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:6px}}
        .relatorio-card{{background:#111;padding:8px;border-radius:8px;border:1px solid #222;text-align:center}}
        .relatorio-card .rlabel{{color:#666;font-size:9px}}
        .relatorio-card .rvalue{{color:#ffd700;font-size:14px;font-weight:bold}}
        .historico-table{{width:100%;font-size:9px;border-collapse:collapse;margin-top:10px}}
        .historico-table th{{background:#9933ff;padding:4px}}
        .historico-table td{{padding:3px;border-bottom:1px solid #222;text-align:center}}
        
        /* ESTRATÉGIAS */
        .estrategia-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:8px}}
        .estrategia-card{{background:#111;padding:12px;border-radius:10px;border:2px solid #222;cursor:pointer;transition:all 0.3s ease}}
        .estrategia-card:hover{{border-color:#9933ff}}
        .estrategia-card.ativa{{border-color:#00ff88;box-shadow:0 0 15px rgba(0,255,136,0.3);background:#0a1a0a}}
    </style>
</head>
<body>
<div class="container">
    <!-- HEADER -->
    <div class="header">
        <div class="crystal-ball"></div>
        <h1>🧙‍♂️🔮 v_SENSITIVE 🔮🧙‍♀️</h1>
        <p>📊 RSI + MM + Bollinger + MACD + Estocástico</p>
        <p>🔮 O BOT QUE SENTE NASCIMENTO, VIDA E MORTE DA VELA</p>
    </div>
    
    <div class="mantra">🌀 O DINHEIRO VEM ATÉ MIM DE TODOS OS LADOS 🌀</div>
    
    <!-- TABS -->
    <div class="tabs">
        <div class="tab active" onclick="openTab('bot')">🤖 BOT</div>
        <div class="tab" onclick="openTab('estrategias')">📊 ESTRATÉGIAS</div>
        <div class="tab" onclick="openTab('moedas')">💸 COMPRAR MOEDAS</div>
        <div class="tab" onclick="openTab('relatorio')">📊 RELATÓRIO</div>
    </div>
    
    <!-- PAINEL BOT -->
    <div class="panel active" id="panel-bot">
        <div class="config-section">
            <h3 style="color:#cc66ff;margin-bottom:8px">🔐 IQ OPTION</h3>
            <div class="config-row" style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px">
                <input type="email" id="email" placeholder="📧 Email IQ Option" style="flex:2;padding:8px;background:#111;border:1px solid #333;border-radius:8px;color:#fff;font-family:'Courier New'">
                <input type="password" id="senha" placeholder="🔒 Senha" style="flex:1;padding:8px;background:#111;border:1px solid #333;border-radius:8px;color:#fff;font-family:'Courier New'">
                <select id="tipo" style="padding:8px;background:#111;border:1px solid #333;border-radius:8px;color:#fff;font-family:'Courier New'">
                    <option value="PRACTICE">🧪 DEMO</option>
                    <option value="REAL">💰 REAL</option>
                </select>
                <button class="btn btn-start" id="btnConectar" onclick="iniciarBot()">🚀 ATIVAR</button>
                <button class="btn btn-stop" id="btnParar" onclick="pararBot()" style="display:none">⏹️ PARAR</button>
            </div>
        </div>
        
        <!-- DASHBOARD -->
        <div class="dashboard">
            <div class="card"><div class="label">💰 BANCA</div><div class="value" id="banca" style="color:#00ff88">--</div></div>
            <div class="card"><div class="label">📈 LUCRO</div><div class="value" id="lucro">$0.00</div></div>
            <div class="card"><div class="label">🎯 OPS</div><div class="value" id="ops">0</div></div>
            <div class="card"><div class="label">🪙 MOEDAS</div><div class="value" id="moedasSaldo" style="color:#ffd700">0</div></div>
            <div class="card"><div class="label">📊 ESTRATÉGIA</div><div class="value" id="estrategiaNome" style="font-size:10px">--</div></div>
            <div class="card"><div class="label">🔮 SINAL</div><div class="value" id="sinal" style="font-size:11px;color:#ff69b4">--</div></div>
        </div>
        
        <!-- INDICADORES -->
        <div class="indicators">
            <div class="ind-card"><div class="ind-label">📊 RSI</div><div class="ind-value" id="rsi">--</div></div>
            <div class="ind-card"><div class="ind-label">📈 MM5</div><div class="ind-value" id="mm5">--</div></div>
            <div class="ind-card"><div class="ind-label">📈 MM10</div><div class="ind-value" id="mm10">--</div></div>
            <div class="ind-card"><div class="ind-label">📉 MM20</div><div class="ind-value" id="mm20">--</div></div>
            <div class="ind-card"><div class="ind-label">📊 ESTOC</div><div class="ind-value" id="stoch">--</div></div>
            <div class="ind-card"><div class="ind-label">🌅 FASE</div><div class="ind-value" id="fase">--</div></div>
            <div class="ind-card"><div class="ind-label">💵 PREÇO</div><div class="ind-value" id="preco">--</div></div>
        </div>
        
        <!-- TERMINAL -->
        <div class="terminal" id="terminal">📡 Aguardando...</div>
        
        <!-- STATUS BAR -->
        <div class="barra-status">
            <span><span class="status-dot inactive" id="statusDot"></span> <span id="statusTexto">⏸️ Parado</span></span>
            <span>⚡ v_SENSITIVE</span>
            <span id="modoTexto">🧪 DEMO</span>
        </div>
    </div>
    
    <!-- PAINEL ESTRATÉGIAS -->
    <div class="panel" id="panel-estrategias">
        <h3 style="color:#cc66ff;margin-bottom:10px">📊 SELECIONAR ESTRATÉGIA</h3>
        <div class="estrategia-grid" id="estrategiaGrid">
            <!-- Preenchido dinamicamente -->
        </div>
    </div>
    
    <!-- PAINEL MOEDAS -->
    <div class="panel" id="panel-moedas">
        <h3 style="color:#cc66ff;margin-bottom:10px">💳 COMPRAR MOEDAS COM PIX</h3>
        <p style="color:#888;font-size:10px">
            📧 <input type="email" id="emailCompra" placeholder="Seu email" 
                      style="width:220px;padding:6px;background:#111;border:1px solid #333;color:#fff;border-radius:5px">
        </p>
        <p style="color:#ffd700;font-size:10px;margin-top:5px">🪙 1 moeda = 1 ciclo | +1 moeda grátis/dia</p>
        <p style="color:#888;font-size:9px;margin-top:3px">⭐ Selecione o plano e pague com PIX</p>
        
        <div class="planos-grid">
            {planos_html}
        </div>
    </div>
    
    <!-- PAINEL RELATÓRIO -->
    <div class="panel" id="panel-relatorio">
        <h3 style="color:#cc66ff;margin-bottom:10px">📊 RELATÓRIO COMPLETO</h3>
        <div style="display:flex;gap:8px;margin-bottom:10px">
            <input type="email" id="emailRelatorio" placeholder="Email" style="flex:2;padding:8px;background:#111;border:1px solid #333;border-radius:8px;color:#fff">
            <button class="btn btn-info" onclick="verRelatorio()">🔍 BUSCAR</button>
            <button class="btn btn-reset" onclick="resetarRelatorio()">🔄 RESETAR</button>
        </div>
        <div id="relatorioContent"></div>
    </div>
</div>

<!-- MODAL PIX -->
<div class="modal-overlay" id="modalPix">
    <div class="modal-pagamento">
        <h3>💳 Pagamento PIX</h3>
        <div id="pixContent"><p>Carregando QR Code...</p></div>
        <button class="btn" style="background:#444;color:#fff;margin-top:10px" onclick="fecharModal()">❌ Fechar</button>
    </div>
</div>

<script>
var intervalo=null,botAtivo=false,emailLogado='',planoSelecionado=0,pixAtual=null;

// ═══════════ TABS ═══════════
function openTab(tab){{
    document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
    event.target.classList.add('active');
    document.getElementById('panel-'+tab).classList.add('active');
    if(tab=='relatorio'&&emailLogado){{document.getElementById('emailRelatorio').value=emailLogado;verRelatorio()}}
    if(tab=='estrategias')carregarEstrategias();
}}

// ═══════════ ESTRATÉGIAS ═══════════
function carregarEstrategias(){{
    fetch('/estrategias').then(r=>r.json()).then(d=>{{
        var grid=document.getElementById('estrategiaGrid');
        var html='';
        for(var key in d.estrategias){{
            var e=d.estrategias[key];
            var ativa=key==d.ativa?' ativa':'';
            html+='<div class="estrategia-card'+ativa+'" onclick="mudarEstrategia(\''+key+'\')">';
            html+='<div style="font-size:14px;font-weight:bold">'+e.name+'</div>';
            html+='<div style="font-size:9px;color:#888;margin-top:5px">'+e.description+'</div>';
            html+='<div style="font-size:9px;color:#666;margin-top:3px">⏱️ Timeframe: '+e.timeframe+'s</div>';
            html+='</div>';
        }}
        grid.innerHTML=html;
    }});
}}

function mudarEstrategia(key){{
    fetch('/mudar_estrategia',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{estrategia:key}})}})
    .then(r=>r.json()).then(d=>{{
        if(d.ok)carregarEstrategias();
    }});
}}

// ═══════════ BOT ═══════════
function iniciarBot(){{
    var email=document.getElementById('email').value.trim();
    var senha=document.getElementById('senha').value.trim();
    var tipo=document.getElementById('tipo').value;
    if(!email||!senha){{alert('Preencha email e senha!');return}}
    emailLogado=email;
    document.getElementById('btnConectar').disabled=true;
    document.getElementById('btnConectar').textContent='...';
    document.getElementById('modoTexto').textContent=tipo=='REAL'?'💰 REAL':'🧪 DEMO';
    fetch('/iniciar',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{email:email,senha:senha,tipo:tipo}})}})
    .then(r=>r.json()).then(d=>{{
        if(d.ok){{
            botAtivo=true;
            document.getElementById('btnConectar').style.display='none';
            document.getElementById('btnParar').style.display='inline-block';
            document.getElementById('statusTexto').textContent='🤖 Ativo';
            document.getElementById('statusDot').className='status-dot active';
            document.getElementById('moedasSaldo').textContent=d.moedas||0;
            if(intervalo)clearInterval(intervalo);
            intervalo=setInterval(atualizar,2000);
            atualizar();
        }}else{{
            alert('ERRO: '+d.erro);
            document.getElementById('btnConectar').disabled=false;
            document.getElementById('btnConectar').textContent='🚀 ATIVAR';
        }}
    }});
}}

function pararBot(){{
    if(!confirm('Parar bot?'))return;
    fetch('/parar',{{method:'POST'}}).then(r=>r.json()).then(d=>{{
        botAtivo=false;
        document.getElementById('btnConectar').style.display='inline-block';
        document.getElementById('btnParar').style.display='none';
        document.getElementById('btnConectar').disabled=false;
        document.getElementById('btnConectar').textContent='🚀 ATIVAR';
        document.getElementById('statusTexto').textContent='⏸️ Parado';
        document.getElementById('statusDot').className='status-dot inactive';
        if(intervalo)clearInterval(intervalo);
    }});
}}

// ═══════════ PLANOS/PIX ═══════════
function selecionarPlano(id){{
    document.querySelectorAll('.plano-card').forEach(c=>c.classList.remove('selecionado'));
    document.querySelectorAll('[id^="btnPlano"]').forEach(b=>b.style.display='none');
    document.getElementById('plano'+id).classList.add('selecionado');
    document.getElementById('btnPlano'+id).style.display='block';
    planoSelecionado=id;
}}

function pagarComPix(planoId){{
    var email=document.getElementById('emailCompra').value.trim()||emailLogado;
    if(!email){{alert('Digite seu email!');return}}
    document.getElementById('modalPix').classList.add('active');
    document.getElementById('pixContent').innerHTML='<p>Gerando QR Code PIX...</p>';
    fetch('/criar_pix',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{email:email,plano_id:planoId}})}})
    .then(r=>r.json()).then(d=>{{
        if(d.sucesso){{
            pixAtual=d;
            var html='<p style="font-size:18px;color:#ffd700">R$ '+d.valor.toFixed(2)+'</p>';
            html+='<p style="color:#00ff88">🪙 '+d.moedas+' moedas</p>';
            if(d.qr_code_base64)html+='<div class="pix-qrcode"><img src="data:image/png;base64,'+d.qr_code_base64+'" alt="QR Code"></div>';
            if(d.qr_code)html+='<div class="pix-copiavel" onclick="copiarPix()">'+d.qr_code+'</div>';
            html+='<button class="btn btn-buy" onclick="verificarPagamento(\''+d.pix_id+'\')">🔄 VERIFICAR PAGAMENTO</button>';
            document.getElementById('pixContent').innerHTML=html;
        }}else{{alert('Erro: '+(d.erro||'Falha'));}}
    }});
}}

function copiarPix(){{navigator.clipboard.writeText(pixAtual.qr_code);alert('Código PIX copiado!')}}

function verificarPagamento(pixId){{
    fetch('/verificar_pix',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{pix_id:pixId}})}})
    .then(r=>r.json()).then(d=>{{
        if(d.pago){{alert('✅ PAGO! +'+d.moedas+' moedas');document.getElementById('moedasSaldo').textContent=d.saldo;fecharModal()}}
        else{{alert('Ainda não confirmado. Tente novamente.')}}
    }});
}}

function fecharModal(){{document.getElementById('modalPix').classList.remove('active');pixAtual=null}}

// ═══════════ RELATÓRIO ═══════════
function verRelatorio(){{
    var email=document.getElementById('emailRelatorio').value.trim();
    if(!email){{alert('Digite o email!');return}}
    fetch('/relatorio?email='+email).then(r=>r.json()).then(d=>{{
        if(d.erro){{alert(d.erro);return}}
        var h='<div class="relatorio-grid">';
        h+='<div class="relatorio-card"><div class="rlabel">🪙 MOEDAS</div><div class="rvalue">'+(d.moedas||0)+'</div></div>';
        h+='<div class="relatorio-card"><div class="rlabel">📈 LUCRO TOTAL</div><div class="rvalue" style="color:'+(d.lucro_total>=0?'#00ff88':'#ff4444')+'">$'+(d.lucro_total||0).toFixed(2)+'</div></div>';
        h+='<div class="relatorio-card"><div class="rlabel">✅ WINS</div><div class="rvalue">'+(d.total_wins||0)+'</div></div>';
        h+='<div class="relatorio-card"><div class="rlabel">❌ LOSSES</div><div class="rvalue">'+(d.total_losses||0)+'</div></div>';
        h+='<div class="relatorio-card"><div class="rlabel">🔄 CICLOS</div><div class="rvalue">'+(d.total_ciclos||0)+'</div></div>';
        h+='</div>';
        if(d.historico_operacoes&&d.historico_operacoes.length>0){{
            h+='<h4 style="margin-top:10px">📋 ÚLTIMAS OPERAÇÕES</h4><table class="historico-table"><tr><th>Data</th><th>Res.</th><th>Valor</th><th>Lucro</th></tr>';
            d.historico_operacoes.slice(-15).reverse().forEach(op=>{{
                h+='<tr><td>'+op.data+'</td><td style="color:'+(op.resultado=='WIN'?'#00ff88':'#ff4444')+'">'+op.resultado+'</td><td>$'+op.valor.toFixed(2)+'</td><td style="color:'+(op.lucro>=0?'#00ff88':'#ff4444')+'">$'+op.lucro.toFixed(2)+'</td></tr>';
            }});
            h+='</table>';
        }}
        document.getElementById('relatorioContent').innerHTML=h;
    }});
}}

function resetarRelatorio(){{
    var email=document.getElementById('emailRelatorio').value.trim();
    if(!email||!confirm('Resetar estatísticas de '+email+'?'))return;
    fetch('/resetar',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{email:email}})}})
    .then(r=>r.json()).then(d=>{{alert(d.msg);if(d.ok)verRelatorio()}});
}}

// ═══════════ ATUALIZAÇÃO ═══════════
function atualizar(){{
    fetch('/status').then(r=>r.json()).then(d=>{{
        if(d.banca)document.getElementById('banca').textContent='$'+d.banca.toFixed(2);
        if(d.lucro!==undefined){{var el=document.getElementById('lucro');el.textContent='$'+d.lucro.toFixed(2);el.style.color=d.lucro>=0?'#00ff88':'#ff4444'}}
        if(d.ops!==undefined)document.getElementById('ops').textContent=d.ops;
        if(d.moedas!==undefined)document.getElementById('moedasSaldo').textContent=d.moedas;
        if(d.sinal)document.getElementById('sinal').textContent=d.sinal;
        if(d.estrategia_nome)document.getElementById('estrategiaNome').textContent=d.estrategia_nome;
        if(d.analise){{
            document.getElementById('rsi').textContent=d.analise.rsi?d.analise.rsi.toFixed(1):'--';
            document.getElementById('mm5').textContent=d.analise.mm5?d.analise.mm5.toFixed(5):'--';
            document.getElementById('mm10').textContent=d.analise.mm10?d.analise.mm10.toFixed(5):'--';
            document.getElementById('mm20').textContent=d.analise.mm20?d.analise.mm20.toFixed(5):'--';
            document.getElementById('stoch').textContent=d.analise.stoch?d.analise.stoch.toFixed(1):'--';
            document.getElementById('fase').textContent=d.analise.fase||'--';
            document.getElementById('preco').textContent=d.analise.preco?d.analise.preco.toFixed(5):'--';
        }}
        if(d.logs)document.getElementById('terminal').innerHTML=d.logs;
        document.getElementById('terminal').scrollTop=document.getElementById('terminal').scrollHeight;
    }});
}}

// Iniciar
window.onload=function(){{
    carregarEstrategias();
    fetch('/status').then(r=>r.json()).then(d=>{{
        if(d.rodando&&d.email){{
            botAtivo=true;emailLogado=d.email;
            document.getElementById('email').value=d.email;
            document.getElementById('btnConectar').style.display='none';
            document.getElementById('btnParar').style.display='inline-block';
            document.getElementById('statusTexto').textContent='🤖 Ativo';
            document.getElementById('statusDot').className='status-dot active';
            if(intervalo)clearInterval(intervalo);
            intervalo=setInterval(atualizar,2000);
            atualizar();
        }}
    }});
}}
</script>
</body>
</html>'''
    
    return html

# ==============================================================================
# 🌐 SEÇÃO 11: ROTAS FLASK
# ==============================================================================

@app.route('/')
def index():
    """Página principal"""
    return render_template_string(get_html_template())

@app.route('/status')
def status():
    """Retorna status do bot"""
    try:
        user_data = db.load_user(email_usuario_atual) if email_usuario_atual else {}
        
        return jsonify({
            'rodando': bot_rodando,
            'email': email_usuario_atual,
            'banca': bot.api.get_balance() if bot.api else 0,
            'lucro': lucro,
            'ops': NumDeOperacoes,
            'sinal': ultimo_sinal,
            'analise': ultima_analise,
            'logs': get_logs_html(40),
            'moedas': user_data.get('moedas', 0),
            'estrategia': estrategia_atual,
            'estrategia_nome': bot.signals.strategies.get(estrategia_atual, {}).get('name', '--') if bot.signals else '--'
        })
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/estrategias')
def listar_estrategias():
    """Lista estratégias disponíveis"""
    if bot.signals:
        return jsonify({
            'estrategias': bot.signals.get_available_strategies(),
            'ativa': estrategia_atual
        })
    return jsonify({'estrategias': {}, 'ativa': 'v_sensitive'})

@app.route('/mudar_estrategia', methods=['POST'])
def mudar_estrategia():
    """Muda a estratégia atual"""
    data = request.get_json()
    strategy = data.get('estrategia', 'v_sensitive')
    
    if bot.change_strategy(strategy):
        global estrategia_atual
        estrategia_atual = strategy
        return jsonify({'ok': True})
    
    return jsonify({'ok': False}), 400

@app.route('/iniciar', methods=['POST'])
def iniciar():
    """Inicia o bot"""
    global bot_thread, bot_rodando, email_usuario_atual, lucro, NumDeOperacoes
    
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        senha = data.get('senha', '').strip()
        tipo = data.get('tipo', 'PRACTICE')
        
        if not email or not senha:
            return jsonify({'ok': False, 'erro': 'Email e senha obrigatórios'}), 400
        
        email_usuario_atual = email
        
        # Carregar/criar usuário no banco
        user = db.load_user(email)
        if not user:
            user = db.create_user(email)
        
        # Verificar moeda diária
        db.daily_coin(email)
        user = db.load_user(email)
        
        # Conectar IQ Option
        success, error = bot.connect(email, senha, tipo)
        if not success:
            return jsonify({'ok': False, 'erro': error}), 400
        
        # Resetar stats
        lucro = 0.0
        NumDeOperacoes = 0
        
        add_log(f'✅ Conectado! Moedas: {user.get("moedas", 0)}', 'win')
        
        # Iniciar thread do bot
        if not bot_rodando:
            bot_rodando = True
            bot_thread = threading.Thread(target=bot.start, daemon=True)
            bot_thread.start()
        
        return jsonify({
            'ok': True,
            'moedas': user.get('moedas', 0)
        })
        
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)[:100]}), 500

@app.route('/parar', methods=['POST'])
def parar():
    """Para o bot"""
    bot.stop()
    add_log('⏹️ Bot parado', 'info')
    return jsonify({'ok': True})

@app.route('/criar_pix', methods=['POST'])
def criar_pix():
    """Cria pagamento PIX"""
    data = request.get_json()
    email = data.get('email', '')
    plano_id = int(data.get('plano_id', 1))
    
    if not email:
        return jsonify({'sucesso': False, 'erro': 'Email obrigatório'}), 400
    
    plano = next((p for p in BotConfig.PLANOS if p['id'] == plano_id), None)
    if not plano:
        return jsonify({'sucesso': False, 'erro': 'Plano não encontrado'}), 404
    
    result = mp.create_pix(email, plano)
    return jsonify(result)

@app.route('/verificar_pix', methods=['POST'])
def verificar_pix():
    """Verifica pagamento PIX"""
    data = request.get_json()
    pix_id = data.get('pix_id', '')
    
    if not pix_id:
        return jsonify({'pago': False}), 400
    
    result = mp.check_payment(pix_id)
    return jsonify(result)

@app.route('/relatorio')
def relatorio():
    """Relatório do usuário"""
    email = request.args.get('email', '')
    if not email:
        return jsonify({'erro': 'Email obrigatório'}), 400
    
    user = db.load_user(email)
    if not user:
        return jsonify({'erro': 'Usuário não encontrado'}), 404
    
    return jsonify(user)

@app.route('/resetar', methods=['POST'])
def resetar():
    """Reseta estatísticas"""
    data = request.get_json()
    email = data.get('email', '')
    
    if not email:
        return jsonify({'ok': False, 'msg': 'Email obrigatório'}), 400
    
    db.reset_user(email)
    return jsonify({'ok': True, 'msg': '✅ Resetado com sucesso!'})

# ==============================================================================
# 🚀 SEÇÃO 12: INICIALIZAÇÃO
# ==============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("🧙‍♂️🔮 v_SENSITIVE BOT - INICIANDO 🔮🧙‍♀️")
    print("=" * 60)
    
    # Verificar banco de dados
    if db.github_online:
        print("✅ Banco de dados: GitHub Online")
    else:
        print("⚠️ Banco de dados: Modo Local")
    
    # Iniciar servidor
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
