# -*- coding: utf-8 -*-
# TESLA 369 BOT - MÓDULO DE SKINS v2.0
# Todas as skins são carregadas dinamicamente deste arquivo
# As skins possuem efeitos visuais animados (partículas, ondas, brilhos)

SKINS_MODULE_VERSION = "2.0.0"

SKINS_LIST = [
    # ============= SKINS BÁSICAS =============
    {
        'id': 'skin_padrao', 
        'nome': '⚡ TESLA PADRÃO', 
        'desc': 'Tema escuro com raios dourados animados', 
        'preco_moedas': 0, 
        'categoria': 'basica',
        'cor_fundo': '#0a0a1a', 
        'cor_panel': '#1a1a3e', 
        'cor_destaque': '#ffd700', 
        'cor_texto': '#fff',
        'cor_botao': 'linear-gradient(135deg,#cc8800,#ffd700)', 
        'cor_tab_ativa': '#ffd700',
        'cor_header_bg': 'linear-gradient(135deg,#1a0000,#331100,#553300,#331100,#1a0000)', 
        'cor_header_borda': '#ffd700',
        'header_extra': '<div class="lightning"></div>',
        'css_extra': '.lightning{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:150px;height:150px;background:radial-gradient(circle at 30% 30%,rgba(255,215,0,0.3) 0%,rgba(255,165,0,0.15) 30%,transparent 100%);border-radius:50%;z-index:0;animation:glow 3s ease-in-out infinite;pointer-events:none}@keyframes glow{0%,100%{box-shadow:0 0 30px rgba(255,215,0,0.3)}50%{box-shadow:0 0 50px rgba(255,165,0,0.5)}}.lightning::after{content:"⚡";position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:50px;animation:float 2s ease-in-out infinite}@keyframes float{0%,100%{transform:translate(-50%,-50%) scale(1)}50%{transform:translate(-50%,-60%) scale(1.1)}}'
    },
    {
        'id': 'skin_dark', 
        'nome': '🌑 TESLA DARK', 
        'desc': 'Partículas roxas flutuantes na tela', 
        'preco_moedas': 6, 
        'categoria': 'basica',
        'cor_fundo': '#000000', 
        'cor_panel': '#0a0a0a', 
        'cor_destaque': '#9933ff', 
        'cor_texto': '#ccc',
        'cor_botao': 'linear-gradient(135deg,#4400aa,#9933ff)', 
        'cor_tab_ativa': '#9933ff',
        'cor_header_bg': 'linear-gradient(135deg,#000000,#110022,#220044,#110022,#000000)', 
        'cor_header_borda': '#9933ff',
        'header_extra': '<canvas id="darkCanvas" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none"></canvas>',
        'css_extra': 'body{background:#000000!important}.header{border-color:#9933ff!important;box-shadow:0 0 40px rgba(153,51,255,0.3)}'
    },
    {
        'id': 'skin_neon', 
        'nome': '💜 TESLA NEON', 
        'desc': 'Brilho neon roxo pulsante com glow', 
        'preco_moedas': 6, 
        'categoria': 'basica',
        'cor_fundo': '#0a0015', 
        'cor_panel': '#150025', 
        'cor_destaque': '#cc00ff', 
        'cor_texto': '#e0c0ff',
        'cor_botao': 'linear-gradient(135deg,#8800cc,#cc00ff)', 
        'cor_tab_ativa': '#cc00ff',
        'cor_header_bg': 'linear-gradient(135deg,#0a0015,#150030,#200050,#150030,#0a0015)', 
        'cor_header_borda': '#cc00ff',
        'header_extra': '<div class="neon-glow"></div>',
        'css_extra': '.neon-glow{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:200px;height:200px;background:radial-gradient(circle,rgba(204,0,255,0.2) 0%,transparent 70%);border-radius:50%;z-index:0;animation:neonPulse 2s ease-in-out infinite;pointer-events:none}@keyframes neonPulse{0%,100%{transform:translate(-50%,-50%) scale(1);opacity:0.5}50%{transform:translate(-50%,-50%) scale(1.3);opacity:0.8}}body{background:#0a0015!important}.header{border-color:#cc00ff!important;box-shadow:0 0 30px rgba(204,0,255,0.4)}'
    },
    {
        'id': 'skin_brasil', 
        'nome': '🇧🇷 BRASIL', 
        'desc': 'Tema verde e amarelo com confetes caindo', 
        'preco_moedas': 0, 
        'categoria': 'basica',
        'cor_fundo': '#001a0a', 
        'cor_panel': '#0a2a15', 
        'cor_destaque': '#ffd700', 
        'cor_texto': '#fff',
        'cor_botao': 'linear-gradient(135deg,#009933,#00cc44)', 
        'cor_tab_ativa': '#ffd700',
        'cor_header_bg': 'linear-gradient(135deg,#001a0a,#003315,#004d20,#003315,#001a0a)', 
        'cor_header_borda': '#ffd700',
        'header_extra': '<canvas id="confettiCanvas" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none"></canvas>',
        'css_extra': 'body{background:#001a0a!important}@keyframes confettiFall{0%{transform:translateY(-20px) rotate(0deg);opacity:1}100%{transform:translateY(100vh) rotate(360deg);opacity:0}}'
    },
    {
        'id': 'skin_princesa', 
        'nome': '👸 PRINCESA', 
        'desc': 'Tema rosa com brilhos e coroa flutuante', 
        'preco_moedas': 6, 
        'categoria': 'basica',
        'cor_fundo': '#1a0010', 
        'cor_panel': '#2a0a20', 
        'cor_destaque': '#ff69b4', 
        'cor_texto': '#ffe0f0',
        'cor_botao': 'linear-gradient(135deg,#cc3388,#ff69b4)', 
        'cor_tab_ativa': '#ff69b4',
        'cor_header_bg': 'linear-gradient(135deg,#1a0010,#2a0a20,#3a1530,#2a0a20,#1a0010)', 
        'cor_header_borda': '#ff69b4',
        'header_extra': '<div class="coroa-p">👑</div><canvas id="princesaSparkles" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none"></canvas>',
        'css_extra': '.coroa-p{position:absolute;top:10px;left:50%;transform:translateX(-50%);font-size:40px;animation:float 2s ease-in-out infinite;z-index:2}@keyframes float{0%,100%{transform:translateX(-50%) translateY(0)}50%{transform:translateX(-50%) translateY(-10px)}}.header h1{color:#ff69b4!important;text-shadow:0 0 30px #ff1493!important}'
    },

    # ============= SKINS PREMIUM =============
    {
        'id': 'skin_sakura', 
        'nome': '🌸 TESLA SAKURA', 
        'desc': 'Pétalas de cerejeira caindo na tela', 
        'preco_moedas': 9, 
        'categoria': 'premium',
        'cor_fundo': '#1a0a1a', 
        'cor_panel': '#2a0a2a', 
        'cor_destaque': '#ff69b4', 
        'cor_texto': '#ffe0f0',
        'cor_botao': 'linear-gradient(135deg,#cc3388,#ff69b4)', 
        'cor_tab_ativa': '#ff69b4',
        'cor_header_bg': 'linear-gradient(135deg,#1a0020,#330033,#4d004d,#330033,#1a0020)', 
        'cor_header_borda': '#ff69b4',
        'header_extra': '<canvas id="sakuraCanvas" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none"></canvas>',
        'css_extra': 'body{background:linear-gradient(180deg,#1a0a1a 0%,#0d001a 100%)!important}.header{border-color:#ff69b4!important;box-shadow:0 0 40px rgba(255,105,180,0.3)}'
    },
    {
        'id': 'skin_ocean', 
        'nome': '🌊 TESLA OCEAN', 
        'desc': 'Ondas do mar em movimento na base', 
        'preco_moedas': 9, 
        'categoria': 'premium',
        'cor_fundo': '#001020', 
        'cor_panel': '#0a1a2a', 
        'cor_destaque': '#00aacc', 
        'cor_texto': '#aaddff',
        'cor_botao': 'linear-gradient(135deg,#006688,#00aacc)', 
        'cor_tab_ativa': '#00aacc',
        'cor_header_bg': 'linear-gradient(135deg,#001020,#002040,#003060,#002040,#001020)', 
        'cor_header_borda': '#00aacc',
        'header_extra': '<canvas id="oceanCanvas" style="position:absolute;bottom:0;left:0;width:100%;height:100px;z-index:0"></canvas>',
        'css_extra': 'body{background:linear-gradient(180deg,#001020 0%,#000810 100%)!important}.header{border-color:#00aacc!important;box-shadow:0 0 30px rgba(0,170,204,0.3)}'
    },
    {
        'id': 'skin_sunset', 
        'nome': '🌅 TESLA SUNSET', 
        'desc': 'Céu em degradê animado com estrelas', 
        'preco_moedas': 9, 
        'categoria': 'premium',
        'cor_fundo': '#1a0010', 
        'cor_panel': '#2a0a1a', 
        'cor_destaque': '#ff6600', 
        'cor_texto': '#ffddaa',
        'cor_botao': 'linear-gradient(135deg,#cc4400,#ff8800)', 
        'cor_tab_ativa': '#ff6600',
        'cor_header_bg': 'linear-gradient(135deg,#1a0000,#331100,#552200,#331100,#1a0000)', 
        'cor_header_borda': '#ff6600',
        'header_extra': '<canvas id="sunsetCanvas" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none"></canvas>',
        'css_extra': 'body{background:linear-gradient(180deg,#1a0010 0%,#331100 50%,#1a0000 100%)!important}.header{border-color:#ff6600!important;box-shadow:0 0 40px rgba(255,102,0,0.3)}'
    },
    {
        'id': 'skin_fire', 
        'nome': '🔥 TESLA FIRE', 
        'desc': 'Chamas realistas animadas na base', 
        'preco_moedas': 9, 
        'categoria': 'premium',
        'cor_fundo': '#1a0000', 
        'cor_panel': '#2a0a0a', 
        'cor_destaque': '#ff4400', 
        'cor_texto': '#ffccaa',
        'cor_botao': 'linear-gradient(135deg,#cc2200,#ff6600)', 
        'cor_tab_ativa': '#ff4400',
        'cor_header_bg': 'linear-gradient(135deg,#1a0000,#330000,#551100,#330000,#1a0000)', 
        'cor_header_borda': '#ff4400',
        'header_extra': '<canvas id="fireCanvas" style="position:absolute;bottom:0;left:0;width:100%;height:80px;z-index:0"></canvas>',
        'css_extra': 'body{background:radial-gradient(ellipse at bottom,#1a0000 0%,#000000 100%)!important}.header{border-color:#ff4400!important;box-shadow:0 0 30px rgba(255,68,0,0.4)}'
    },
    {
        'id': 'skin_ice', 
        'nome': '❄️ TESLA ICE', 
        'desc': 'Neve caindo com cristais de gelo', 
        'preco_moedas': 9, 
        'categoria': 'premium',
        'cor_fundo': '#000a1a', 
        'cor_panel': '#0a102a', 
        'cor_destaque': '#3399ff', 
        'cor_texto': '#aaccff',
        'cor_botao': 'linear-gradient(135deg,#0044aa,#3399ff)', 
        'cor_tab_ativa': '#3399ff',
        'cor_header_bg': 'linear-gradient(135deg,#000a1a,#001133,#002255,#001133,#000a1a)', 
        'cor_header_borda': '#3399ff',
        'header_extra': '<canvas id="snowCanvas" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none"></canvas>',
        'css_extra': 'body{background:linear-gradient(180deg,#000a1a 0%,#001133 100%)!important}.header{border-color:#3399ff!important;box-shadow:0 0 40px rgba(51,153,255,0.3)}'
    },

    # ============= SKINS LENDÁRIAS =============
    {
        'id': 'skin_matrix', 
        'nome': '🧬 TESLA MATRIX', 
        'desc': 'Chuva de caracteres verdes estilo Matrix', 
        'preco_moedas': 12, 
        'categoria': 'lendaria',
        'cor_fundo': '#000000', 
        'cor_panel': '#0a0a0a', 
        'cor_destaque': '#00ff00', 
        'cor_texto': '#00cc00',
        'cor_botao': 'linear-gradient(135deg,#004400,#00ff00)', 
        'cor_tab_ativa': '#00ff00',
        'cor_header_bg': 'linear-gradient(135deg,#000000,#001100,#003300,#001100,#000000)', 
        'cor_header_borda': '#00ff00',
        'header_extra': '<canvas id="matrixCanvas" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none"></canvas>',
        'css_extra': 'body{background:#000000!important}.header{border-color:#00ff00!important;box-shadow:0 0 30px rgba(0,255,0,0.4)}.terminal{color:#00ff00!important;font-family:monospace!important}'
    },
    {
        'id': 'skin_thunder', 
        'nome': '⚡ TESLA THUNDER', 
        'desc': 'Raios elétricos aleatórios na tela', 
        'preco_moedas': 12, 
        'categoria': 'lendaria',
        'cor_fundo': '#000011', 
        'cor_panel': '#0a0a1a', 
        'cor_destaque': '#ffff00', 
        'cor_texto': '#ffffff',
        'cor_botao': 'linear-gradient(135deg,#aaaa00,#ffff00)', 
        'cor_tab_ativa': '#ffff00',
        'cor_header_bg': 'linear-gradient(135deg,#000011,#111122,#222244,#111122,#000011)', 
        'cor_header_borda': '#ffff00',
        'header_extra': '<canvas id="thunderCanvas" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none"></canvas>',
        'css_extra': 'body{background:#000011!important}.header{border-color:#ffff00!important;box-shadow:0 0 50px rgba(255,255,0,0.3)}'
    },
    {
        'id': 'skin_magos', 
        'nome': '🔮 MAGOS DA BOLA DE CRISTAL', 
        'desc': 'Magos flutuando com bola de cristal glow', 
        'preco_moedas': 12, 
        'categoria': 'lendaria',
        'cor_fundo': '#0a0a1a', 
        'cor_panel': '#1a1a3e', 
        'cor_destaque': '#cc66ff', 
        'cor_texto': '#e0d0ff',
        'cor_botao': 'linear-gradient(135deg,#6600cc,#9933ff)', 
        'cor_tab_ativa': '#9933ff',
        'cor_header_bg': 'linear-gradient(135deg,#0d001a,#1a0033,#2d0055,#1a0033,#0d001a)', 
        'cor_header_borda': '#9933ff',
        'header_extra': '<div class="crystal-ball"></div><div class="mago mago-esq">🧙‍♂️</div><div class="mago mago-dir">🧙‍♀️</div>',
        'css_extra': '.crystal-ball{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:130px;height:130px;background:radial-gradient(circle at 30% 30%,rgba(200,150,255,0.4) 0%,rgba(153,51,255,0.2) 30%,transparent 70%);border-radius:50%;z-index:0;animation:crystalGlow 4s ease-in-out infinite;pointer-events:none;border:2px solid rgba(153,51,255,0.3)}@keyframes crystalGlow{0%,100%{box-shadow:0 0 30px rgba(153,51,255,0.4),0 0 60px rgba(153,51,255,0.2)}50%{box-shadow:0 0 50px rgba(200,100,255,0.6),0 0 80px rgba(200,100,255,0.3)}}.crystal-ball::after{content:"🔮";position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:45px;animation:floatCrystal 3s ease-in-out infinite}@keyframes floatCrystal{0%,100%{transform:translate(-50%,-50%) scale(1)}50%{transform:translate(-50%,-60%) scale(1.1)}}.mago{position:absolute;top:50%;font-size:30px;z-index:1;animation:magoFloat 2s ease-in-out infinite;pointer-events:none}.mago-esq{left:15px}.mago-dir{right:15px;animation-delay:0.5s}@keyframes magoFloat{0%,100%{transform:translateY(-50%)}50%{transform:translateY(-60%)}}'
    },
    {
        'id': 'skin_cosmic',
        'nome': '🌌 TESLA COSMIC',
        'desc': 'Galáxia girando com estrelas cadentes',
        'preco_moedas': 12,
        'categoria': 'lendaria',
        'cor_fundo': '#050510',
        'cor_panel': '#0a0a2a',
        'cor_destaque': '#aa66ff',
        'cor_texto': '#e0d0ff',
        'cor_botao': 'linear-gradient(135deg,#6600cc,#aa66ff)',
        'cor_tab_ativa': '#aa66ff',
        'cor_header_bg': 'linear-gradient(135deg,#050510,#0a0a2a,#151545,#0a0a2a,#050510)',
        'cor_header_borda': '#aa66ff',
        'header_extra': '<canvas id="cosmicCanvas" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none"></canvas>',
        'css_extra': 'body{background:#050510!important}.header{border-color:#aa66ff!important;box-shadow:0 0 50px rgba(170,102,255,0.3)}.header h1{text-shadow:0 0 30px #aa66ff,0 0 60px #6600cc}'
    },

    # ============= 🆕 NOVA SKIN LENDÁRIA: AURORA BOREAL =============
    {
        'id': 'skin_aurora',
        'nome': '🌈 TESLA AURORA',
        'desc': 'Aurora boreal dançante no céu - Efeito especial!',
        'preco_moedas': 15,
        'categoria': 'lendaria',
        'cor_fundo': '#0a0a2a',
        'cor_panel': '#0f0f3a',
        'cor_destaque': '#00ffaa',
        'cor_texto': '#ccffea',
        'cor_botao': 'linear-gradient(135deg,#006644,#00ff88)',
        'cor_tab_ativa': '#00ffaa',
        'cor_header_bg': 'linear-gradient(135deg,#0a0a2a,#1a1a4a,#2a2a6a,#1a1a4a,#0a0a2a)',
        'cor_header_borda': '#00ffaa',
        'header_extra': '<canvas id="auroraCanvas" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none"></canvas><canvas id="auroraStarsCanvas" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none"></canvas>',
        'css_extra': 'body{background:linear-gradient(180deg,#0a0a2a 0%,#0f0f3a 50%,#0a0a2a 100%)!important}.header{border-color:#00ffaa!important;box-shadow:0 0 60px rgba(0,255,170,0.4),0 0 120px rgba(0,255,170,0.1)}@keyframes auroraWave{0%{opacity:0.3}50%{opacity:0.8}100%{opacity:0.3}}'
    },

    # ============= 🆕 NOVA SKIN PREMIUM: CAFÉ & NEGÓCIOS =============
    {
        'id': 'skin_coffee',
        'nome': '☕ TESLA COFFEE TRADER',
        'desc': 'Ambiente aconchegante com fumaça de café',
        'preco_moedas': 9,
        'categoria': 'premium',
        'cor_fundo': '#2a1a0a',
        'cor_panel': '#3a2a1a',
        'cor_destaque': '#d4a574',
        'cor_texto': '#f5e6d3',
        'cor_botao': 'linear-gradient(135deg,#8B5A2B,#d4a574)',
        'cor_tab_ativa': '#d4a574',
        'cor_header_bg': 'linear-gradient(135deg,#2a1a0a,#3a2a1a,#4a3a2a,#3a2a1a,#2a1a0a)',
        'cor_header_borda': '#d4a574',
        'header_extra': '<canvas id="coffeeCanvas" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none"></canvas><div class="steam-container"><div class="steam"></div><div class="steam2"></div></div>',
        'css_extra': '.steam-container{position:absolute;bottom:20px;left:0;width:100%;height:100px;overflow:hidden;z-index:1;pointer-events:none}.steam,.steam2{position:absolute;bottom:0;width:20px;height:100px;background:linear-gradient(180deg,rgba(210,180,140,0) 0%,rgba(210,180,140,0.4) 50%,rgba(210,180,140,0) 100%);border-radius:50%;animation:steamRise 4s ease-in-out infinite}.steam{left:20%;animation-delay:0s}.steam2{left:80%;animation-delay:2s}.steam::before,.steam2::before{content:"";position:absolute;width:40px;height:40px;background:radial-gradient(circle,rgba(210,180,140,0.3) 0%,transparent 70%);border-radius:50%;top:-20px;left:-10px}@keyframes steamRise{0%{transform:translateY(0) scale(1);opacity:0.4}100%{transform:translateY(-100px) scale(2);opacity:0}}body{background:linear-gradient(180deg,#2a1a0a 0%,#1a0a00 100%)!important}.header{border-color:#d4a574!important;box-shadow:0 0 40px rgba(212,165,116,0.3)}'
    },

    # ============= 🆕 NOVA SKIN BÁSICA: CYBERPUNK =============
    {
        'id': 'skin_cyberpunk',
        'nome': '🤖 TESLA CYBERPUNK',
        'desc': 'Tema futurista com scanlines e glitch',
        'preco_moedas': 6,
        'categoria': 'basica',
        'cor_fundo': '#0a0a0a',
        'cor_panel': '#1a1a2a',
        'cor_destaque': '#ff3366',
        'cor_texto': '#33ffcc',
        'cor_botao': 'linear-gradient(135deg,#ff3366,#ff6699)',
        'cor_tab_ativa': '#ff3366',
        'cor_header_bg': 'linear-gradient(135deg,#0a0a0a,#1a1a2a,#2a2a3a,#1a1a2a,#0a0a0a)',
        'cor_header_borda': '#ff3366',
        'header_extra': '<canvas id="cyberCanvas" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none"></canvas><div class="scanline"></div>',
        'css_extra': '.scanline{position:fixed;top:0;left:0;width:100%;height:5px;background:linear-gradient(180deg,rgba(255,51,102,0) 0%,rgba(255,51,102,0.5) 50%,rgba(255,51,102,0) 100%);animation:scanMove 8s linear infinite;pointer-events:none;z-index:100}@keyframes scanMove{0%{transform:translateY(0)}100%{transform:translateY(100vh)}}body{background:#0a0a0a!important;position:relative;overflow-x:hidden}.header{border-color:#ff3366!important;box-shadow:0 0 30px rgba(255,51,102,0.5),inset 0 0 30px rgba(255,51,102,0.1)}.header h1{font-family:monospace;letter-spacing:5px;text-shadow:0 0 20px #ff3366,0 0 40px #ff6699}'
    }
]


def get_skin_by_id(skin_id):
    """Retorna uma skin pelo ID"""
    for skin in SKINS_LIST:
        if skin['id'] == skin_id:
            return skin
    return SKINS_LIST[0]


def get_all_skins():
    """Retorna todas as skins"""
    return SKINS_LIST


def get_skins_by_category(categoria):
    """Retorna skins filtradas por categoria"""
    return [skin for skin in SKINS_LIST if skin.get('categoria') == categoria]


def get_skins_count_by_category():
    """Retorna a contagem de skins por categoria"""
    categorias = {}
    for skin in SKINS_LIST:
        cat = skin.get('categoria', 'basica')
        categorias[cat] = categorias.get(cat, 0) + 1
    return categorias
