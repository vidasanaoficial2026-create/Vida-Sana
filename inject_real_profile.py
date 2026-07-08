import os

files = ['templates/tienda.html', 'templates/catalogo.html']

profile_html = """
      <!-- PROFILE VIEW -->
      <div id="profileView" style="display: none;">
        <h2>Mi Perfil</h2>
        {% if session.get('nombre') %}
        <div style="text-align:center; margin-bottom: 20px; padding: 15px; background: #f9f9f9; border-radius: 8px;">
          <div style="width: 50px; height: 50px; background: var(--primary); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: bold; margin: 0 auto 10px auto;">
            {{ session.get('nombre')[0].upper() }}
          </div>
          <h3 style="margin:0; font-size:18px; color: #333;">{{ session.get('nombre') }}</h3>
          <p style="color:#666; margin:5px 0 0 0; font-size:14px;">{{ session.get('email') }}</p>
        </div>
        {% endif %}
        <div style="display:flex; gap:10px; margin-bottom:20px; border-bottom:1px solid #eee; padding-bottom:10px;">
          <button type="button" onclick="showProfileTab('pedidos')" id="tabPedidos" style="flex:1; padding:10px; border:none; background:var(--primary); color:#fff; border-radius:5px; cursor:pointer;">Mis Pedidos</button>
          <button type="button" onclick="showProfileTab('favoritos')" id="tabFavoritos" style="flex:1; padding:10px; border:none; background:#f5f5f5; color:#333; border-radius:5px; cursor:pointer;">Mis Favoritos</button>
        </div>
        
        <div id="contentPedidos" style="max-height: 300px; overflow-y: auto;">
           <p style="text-align:center; color:#666; font-size:14px;">Cargando pedidos...</p>
        </div>
        
        <div id="contentFavoritos" style="display:none; max-height: 300px; overflow-y: auto;">
           <p style="text-align:center; color:#666; font-size:14px;">No tienes favoritos guardados.</p>
        </div>

        <button type="button" class="btn-login-submit" onclick="logoutCustomer()" style="background:#dc3545; margin-top:20px;">Cerrar Sesión</button>
      </div>
"""

for file in files:
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # We will split at "<!-- CART MODAL -->" and insert profileView before the last two closing divs of loginOverlay
        if 'id="profileView"' not in content:
            if '<!-- CART MODAL -->' in content:
                parts = content.split('<!-- CART MODAL -->')
                # parts[0] ends with something like:
                #     </div>
                #   </div>
                #   
                
                # We can just replace the last </div>\n  </div> with our profile view
                # Let's find the position of the last "    </div>\n  </div>"
                pos = parts[0].rfind('    </div>\n  </div>')
                if pos != -1:
                    new_first_part = parts[0][:pos] + profile_html + parts[0][pos:]
                    content = new_first_part + '<!-- CART MODAL -->' + parts[1]
                    with open(file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Successfully injected into {file}")
                else:
                    print(f"Could not find closing divs in {file}")
            else:
                print(f"No CART MODAL in {file}")
