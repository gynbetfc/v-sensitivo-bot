"""
Skin: Padrao
Extraída automaticamente do TESLA 369
"""

SKIN_CONFIG = {
        'id': 'skin_padrao', 'nome': '⚡ TESLA PADRÃO', 'desc': 'Tema escuro com raios dourados', 'preco_moedas': 0, 'categoria': 'basica',
        'cor_fundo': '#0a0a1a', 'cor_panel': '#1a1a3e', 'cor_destaque': '#ffd700', 'cor_texto': '#fff',
        'cor_botao': 'linear-gradient(135deg,#cc8800,#ffd700)', 'cor_tab_ativa': '#ffd700',
        'cor_header_bg': 'linear-gradient(135deg,#1a0000,#331100,#553300,#331100,#1a0000)', 'cor_header_borda': '#ffd700',
        'header_extra': '<div class="lightning"></div>',
        'css_extra': '.lightning{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:150px;height:150px;background:radial-gradient(circle at 30% 30%,rgba(255,215,0,0.3) 0%,rgba(255,165,0,0.15) 30%,transparent 100%);border-radius:50%;z-index:0;animation:glow 3s ease-in-out infinite;pointer-events:none}@keyframes glow{0%,100%{box-shadow:0 0 30px rgba(255,215,0,0.3)}50%{box-shadow:0 0 50px rgba(255,165,0,0.5)}}.lightning::after{content:"⚡";position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:50px;animation:float 2s ease-in-out infinite}@keyframes float{0%,100%{transform:translate(-50%,-50%) scale(1)}50%{transform:translate(-50%,-60%) scale(1.1)}}'
    }
