import os
import re

files = ['templates/tienda.html', 'templates/catalogo.html']

profile_view = """    <div id="profileView" style="display: none;">
      <h2>Mi Perfil</h2>
      <div style="display:flex; gap:10px; margin-bottom:20px; border-bottom:1px solid #eee; padding-bottom:10px;">
        <button onclick="showProfileTab('pedidos')" id="tabPedidos" style="flex:1; padding:10px; border:none; background:var(--primary); color:#fff; border-radius:5px; cursor:pointer;">Mis Pedidos</button>
        <button onclick="showProfileTab('favoritos')" id="tabFavoritos" style="flex:1; padding:10px; border:none; background:#f5f5f5; color:#333; border-radius:5px; cursor:pointer;">Mis Favoritos</button>
      </div>
      
      <div id="contentPedidos" style="max-height: 300px; overflow-y: auto;">
         <p style="text-align:center; color:#666; font-size:14px;">Cargando pedidos...</p>
      </div>
      
      <div id="contentFavoritos" style="display:none; max-height: 300px; overflow-y: auto;">
         <p style="text-align:center; color:#666; font-size:14px;">No tienes favoritos guardados.</p>
      </div>

      <button class="btn-login-submit" onclick="logoutCustomer()" style="background:#dc3545; margin-top:20px;">Cerrar Sesión</button>
    </div>
"""

profile_js = """function showProfileTab(tab) {
  document.getElementById('contentPedidos').style.display = tab === 'pedidos' ? 'block' : 'none';
  document.getElementById('contentFavoritos').style.display = tab === 'favoritos' ? 'block' : 'none';
  
  document.getElementById('tabPedidos').style.background = tab === 'pedidos' ? 'var(--primary)' : '#f5f5f5';
  document.getElementById('tabPedidos').style.color = tab === 'pedidos' ? '#fff' : '#333';
  
  document.getElementById('tabFavoritos').style.background = tab === 'favoritos' ? 'var(--primary)' : '#f5f5f5';
  document.getElementById('tabFavoritos').style.color = tab === 'favoritos' ? '#fff' : '#333';
}

async function loadPedidos() {
  try {
    const res = await fetch('/api/mis-pedidos');
    const data = await res.json();
    const container = document.getElementById('contentPedidos');
    if (data.pedidos && data.pedidos.length > 0) {
      container.innerHTML = data.pedidos.map(p => `
        <div style="border:1px solid #eee; padding:10px; border-radius:5px; margin-bottom:10px; text-align:left;">
          <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
            <strong style="color:var(--primary)">Pedido #${p.id}</strong>
            <span style="font-size:12px; padding:2px 6px; background:#f0f0f0; border-radius:10px;">${p.estado}</span>
          </div>
          <div style="font-size:14px; color:#555;">Total: S/ ${p.total.toFixed(2)}</div>
        </div>
      `).join('');
    } else {
      container.innerHTML = '<p style="text-align:center; color:#666; font-size:14px;">No tienes pedidos aún.</p>';
    }
  } catch (e) {
    document.getElementById('contentPedidos').innerHTML = '<p style="text-align:center; color:red; font-size:14px;">Error al cargar pedidos.</p>';
  }
}

function loadFavoritosProfile() {
  let favs = JSON.parse(localStorage.getItem('vid_sana_favoritos')) || [];
  const container = document.getElementById('contentFavoritos');
  if (favs.length > 0) {
    container.innerHTML = favs.map(f => `
      <div style="border:1px solid #eee; padding:10px; border-radius:5px; margin-bottom:10px; display:flex; align-items:center; gap:10px;">
        <img src="${f.image}" style="width:50px; height:50px; object-fit:cover; border-radius:5px;">
        <div style="text-align:left; flex:1;">
          <div style="font-weight:600; font-size:14px; color:var(--text)">${f.name}</div>
          <div style="font-size:13px; color:var(--primary)">S/ ${f.price.toFixed(2)}</div>
        </div>
      </div>
    `).join('');
  } else {
    container.innerHTML = '<p style="text-align:center; color:#666; font-size:14px;">No tienes favoritos guardados.</p>';
  }
}

function toggleAuthView(view) {
"""

for file in files:
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Inject profile HTML view inside loginOverlay
        if '<div id="profileView"' not in content:
            content = content.replace('    </div>\n  </div>\n</div>\n\n<!-- Auth Scripts -->', profile_view + '    </div>\n  </div>\n</div>\n\n<!-- Auth Scripts -->')
        
        # Update toggleAuthView logic
        if 'function loadPedidos()' not in content:
            content = content.replace('function toggleAuthView(view) {', profile_js)
            
            # Inside toggleAuthView
            content = content.replace(
                "document.getElementById('registerView').style.display = view === 'register' ? 'block' : 'none';",
                "document.getElementById('registerView').style.display = view === 'register' ? 'block' : 'none';\n  document.getElementById('profileView').style.display = view === 'profile' ? 'block' : 'none';\n  if(view === 'profile') { loadPedidos(); loadFavoritosProfile(); }"
            )
            
            # Update header button logic
            # Currently it is:
            # <button class="header-login" onclick="logoutCustomer()" aria-label="Cerrar sesión" title="Cerrar sesión" style="color:#dc3545;">
            # Change it so clicking the name opens profile.
            content = re.sub(
                r'<span style="color:var\(--text\); font-weight:600; font-size:14px;">Hola, (.*?)</span>',
                r'<span style="color:var(--text); font-weight:600; font-size:14px; cursor:pointer;" onclick="document.getElementById(\'loginOverlay\').style.display=\'flex\'; toggleAuthView(\'profile\');" title="Ver mi perfil">Hola, \1 <i class="fas fa-caret-down"></i></span>',
                content
            )

        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {file} for profile")

# Update Backend server.py
with open('server.py', 'r', encoding='utf-8') as f:
    server_content = f.read()

profile_backend = """
@app.route('/api/mis-pedidos', methods=['GET'])
def api_mis_pedidos():
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    conn = get_db()
    pedidos = conn.execute("SELECT * FROM pedidos WHERE usuario_id=? ORDER BY id DESC", (session['user_id'],)).fetchall()
    conn.close()
    
    pedidos_list = []
    for p in pedidos:
        pedidos_list.append({
            'id': p['id'],
            'total': p['total'],
            'estado': p['estado']
        })
    return jsonify({'pedidos': pedidos_list})

@app.route('/api/login'"""

if '/api/mis-pedidos' not in server_content:
    server_content = server_content.replace("@app.route('/api/login'", profile_backend)
    with open('server.py', 'w', encoding='utf-8') as f:
        f.write(server_content)
    print("Updated server.py for /api/mis-pedidos")
