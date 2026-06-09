# -*- coding: utf-8 -*-
# TESLA 369 BOT - MÓDULO DE SKINS
# Todas as skins são carregadas dinamicamente deste arquivo

SKINS_MODULE_VERSION = "1.0.0"

SKINS_LIST = [
    {
        'id': 'skin_padrao', 
        'nome': '⚡ TESLA PADRÃO', 
        'desc': 'Tema escuro com raios dourados', 
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
        'desc': 'Particulas roxas flutuantes', 
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
        'desc': 'Brilho neon roxo pulsante', 
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
        'id': 'skin_matrix', 
        'nome': '🧬 TESLA MATRIX', 
        'desc': 'Chuva de caracteres verdes', 
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
        'id': 'skin_sakura', 
        'nome': '🌸 TESLA SAKURA', 
        'desc': 'Pétalas de cerejeira caindo', 
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
        'id': 'skin_thunder', 
        'nome': '⚡ TESLA THUNDER', 
        'desc': 'Raios elétricos na tela', 
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
        'id': 'skin_ocean', 
        'nome': '🌊 TESLA OCEAN', 
        'desc': 'Ondas do mar em movimento', 
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
        'desc': 'Ceu em degradê animado', 
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
        'id': 'skin_magos', 
        'nome': '🔮 MAGOS DA BOLA DE CRISTAL', 
        'desc': 'Tema roxo místico', 
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
        'id': 'skin_brasil', 
        'nome': '🇧🇷 BRASIL', 
        'desc': 'Tema verde e amarelo', 
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
        'header_extra': '<div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:60px;z-index:0;opacity:0.3;pointer-events:none">🇧🇷</div>', 
        'css_extra': ''
    },
    {
        'id': 'skin_fire', 
        'nome': '🔥 TESLA FIRE', 
        'desc': 'Chamas realistas na base', 
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
        'desc': 'Neve caindo com cristais', 
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
    {
        'id': 'skin_princesa', 
        'nome': '👸 PRINCESA', 
        'desc': 'Tema rosa com brilhos', 
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
        'header_extra': '<div class="coroa-p">👑</div>',
        'css_extra': '.coroa-p{position:absolute;top:10px;left:50%;transform:translateX(-50%);font-size:40px;animation:float 2s ease-in-out infinite}@keyframes float{0%,100%{transform:translateX(-50%) translateY(0)}50%{transform:translateX(-50%) translateY(-10px)}}.header h1{color:#ff69b4!important;text-shadow:0 0 30px #ff1493!important}'
    }
]

# Função auxiliar para obter skin por ID
def get_skin_by_id(skin_id):
    for skin in SKINS_LIST:
        if skin['id'] == skin_id:
            return skin
    return SKINS_LIST[0]  # Retorna a skin padrão se não encontrar

# Função para obter todas as skins
def get_all_skins():
    return SKINS_LIST

# Função para obter skins por categoria
def get_skins_by_category(categoria):
    return [skin for skin in SKINS_LIST if skin.get('categoria') == categoria]
