from flask import render_template_string, request, jsonify

def register_admin_routes(app, carregar_usuario, salvar_usuario):
    
    @app.route('/admin_2026', methods=['GET', 'POST'])
    def admin_painel():
        if request.method == 'POST':
            if request.form.get('senha') == '!@#Anu,,..08':
                return render_template_string(ADMIN_HTML)
        
        if request.args.get('senha') != '!@#Anu,,..08':
            return LOGIN_HTML
        
        return render_template_string(ADMIN_HTML)
    
    @app.route('/admin_buscar')
    def admin_buscar():
        email = request.args.get('email','')
        u = carregar_usuario(email)
        if u: return jsonify(u)
        return jsonify({'erro':'Nao encontrado'})
    
    @app.route('/admin_salvar', methods=['POST'])
    def admin_salvar():
        d = request.json
        email = d.get('email','')
        u = carregar_usuario(email)
        if not u: return jsonify({'ok':False,'msg':'Usuario nao encontrado'})
        u['moedas'] = d.get('moedas', u.get('moedas',0))
        u['skin_atual'] = d.get('skin', u.get('skin_atual','skin_padrao'))
        u['estrategias_compradas'] = d.get('estrategias', u.get('estrategias_compradas',[]))
        salvar_usuario(email, u)
        return jsonify({'ok':True,'msg':'Salvo!'})
    
    @app.route('/admin_resetar', methods=['POST'])
    def admin_resetar():
        email = request.json.get('email','')
        u = carregar_usuario(email)
        if not u: return jsonify({'ok':False,'msg':'Usuario nao encontrado'})
        u['total_wins']=0; u['total_losses']=0; u['total_ciclos']=0
        u['total_gasto']=0; u['total_ganho']=0; u['lucro_total']=0
        u['historico_operacoes']=[]; u['dias_ativos']={}
        salvar_usuario(email, u)
        return jsonify({'ok':True,'msg':'Resetado!'})

LOGIN_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Admin</title>
<style>body{background:#0a0a1a;display:flex;justify-content:center;align-items:center;height:100vh;font-family:monospace}
.box{background:#1a1a3e;border:2px solid #ffd700;border-radius:15px;padding:30px;text-align:center}
h2{color:#ffd700}input{padding:12px;background:#111;border:1px solid #333;color:#fff;border-radius:8px;font-size:16px;text-align:center;margin:10px 0}
.btn{background:#ffd700;color:#000;padding:12px 30px;border:none;border-radius:8px;font-weight:bold;cursor:pointer;font-size:16px}</style></head>
<body><div class="box"><h2>🔐 Acesso Restrito</h2>
<form method="POST"><input type="password" name="senha" placeholder="Senha" autofocus><br>
<button class="btn" type="submit">Entrar</button></form></div></body></html>"""

ADMIN_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Painel Admin</title>
<style>body{background:#0a0a1a;color:#fff;font-family:monospace;padding:20px}
.container{max-width:800px;margin:0 auto}h1{color:#ffd700;text-align:center}
.card{background:#1a1a3e;border:2px solid #ffd700;border-radius:15px;padding:20px;margin:15px 0}
input,select,textarea{width:100%;padding:10px;margin:5px 0;background:#111;border:1px solid #333;color:#fff;border-radius:8px;font-family:monospace}
.btn{background:#ffd700;color:#000;padding:12px;border:none;border-radius:8px;font-weight:bold;cursor:pointer;width:100%;margin:5px 0;font-size:14px}
.btn-green{background:#00ff88}.btn-red{background:#ff4444;color:#fff}
.result{background:#000;padding:15px;border-radius:8px;margin:10px 0;white-space:pre-wrap;font-size:12px;max-height:300px;overflow-y:auto}</style></head>
<body><div class="container"><h1>🔐 Painel Admin</h1>
<div class="card"><h3 style="color:#ffd700">🔍 Buscar</h3>
<input type="email" id="emailBusca" placeholder="Email"><button class="btn" onclick="buscar()">🔍 Buscar</button>
<div class="result" id="resultado"></div></div>
<div class="card"><h3 style="color:#ffd700">✏️ Editar</h3>
<input type="email" id="emailEdit" placeholder="Email"><p>⚡ VOLTS: <input type="number" id="moedas"></p>
<p>🎨 Skin: <select id="skin"><option value="skin_padrao">Padrao</option><option value="skin_dark">Dark</option><option value="skin_neon">Neon</option><option value="skin_matrix">Matrix</option><option value="skin_sakura">Sakura</option><option value="skin_thunder">Thunder</option><option value="skin_ocean">Ocean</option><option value="skin_sunset">Sunset</option><option value="skin_magos">Magos</option><option value="skin_brasil">Brasil</option><option value="skin_fire">Fire</option><option value="skin_ice">Ice</option><option value="skin_princesa">Princesa</option></select></p>
<p>📊 Estratégias: <textarea id="estrategias" rows="2"></textarea></p>
<button class="btn btn-green" onclick="salvar()">💾 SALVAR</button>
<button class="btn btn-red" onclick="resetar()">🔄 RESETAR</button>
<div class="result" id="resultadoEdit"></div></div></div>
<script>
function buscar(){fetch('/admin_buscar?email='+document.getElementById('emailBusca').value).then(r=>r.json()).then(d=>{if(d.erro)document.getElementById('resultado').innerHTML='<p style=color:#ff4444>'+d.erro+'</p>';else{var h='<p style=color:#00ff88>✅ Encontrado!</p>';h+='<p>📧 '+d.email+'</p>';h+='<p>⚡ '+d.moedas+' VOLTS</p>';document.getElementById('resultado').innerHTML=h;document.getElementById('emailEdit').value=d.email;document.getElementById('moedas').value=d.moedas;document.getElementById('skin').value=d.skin_atual;document.getElementById('estrategias').value=d.estrategias_compradas.join(',')}})}
function salvar(){fetch('/admin_salvar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:document.getElementById('emailEdit').value,moedas:parseInt(document.getElementById('moedas').value),skin:document.getElementById('skin').value,estrategias:document.getElementById('estrategias').value.split(',').map(s=>s.trim())})}).then(r=>r.json()).then(d=>{document.getElementById('resultadoEdit').innerHTML='<p style=color:'+(d.ok?'#00ff88':'#ff4444')+'>'+d.msg+'</p>'})}
function resetar(){fetch('/admin_resetar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:document.getElementById('emailEdit').value})}).then(r=>r.json()).then(d=>{document.getElementById('resultadoEdit').innerHTML='<p style=color:'+(d.ok?'#00ff88':'#ff4444')+'>'+d.msg+'</p>'})}
</script></body></html>"""
