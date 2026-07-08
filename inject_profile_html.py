import os

files = ['templates/tienda.html', 'templates/catalogo.html']

profile_html = """
    <!-- PROFILE VIEW -->
    <div id="profileView" style="display: none;">
      <h2>Mi Perfil</h2>
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
        
        # Target the closing divs of the login overlay which are exactly these 3 lines:
        #       </div>
        #     </div>
        #   </div>
        target_str = "        <div style=\"text-align: center; margin-top: 15px;\">\n          <a class=\"login-forgot\" onclick=\"toggleAuthView('login')\">Volver a iniciar sesión</a>\n        </div>\n      </div>\n  \n    </div>\n  </div>"
        
        target_str2 = "        <div style=\"text-align: center; margin-top: 15px;\">\n          <a class=\"login-forgot\" onclick=\"toggleAuthView('login')\">Volver a iniciar sesin</a>\n        </div>\n      </div>\n  \n    </div>\n  </div>"
        
        replacement = f"        <div style=\"text-align: center; margin-top: 15px;\">\n          <a class=\"login-forgot\" onclick=\"toggleAuthView('login')\">Volver a iniciar sesión</a>\n        </div>\n      </div>\n  {profile_html}\n    </div>\n  </div>"
        
        replacement2 = f"        <div style=\"text-align: center; margin-top: 15px;\">\n          <a class=\"login-forgot\" onclick=\"toggleAuthView('login')\">Volver a iniciar sesin</a>\n        </div>\n      </div>\n  {profile_html}\n    </div>\n  </div>"
        
        if 'id="profileView"' not in content:
            if target_str in content:
                content = content.replace(target_str, replacement)
            elif target_str2 in content:
                content = content.replace(target_str2, replacement2)
                
            with open(file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Injected profileView HTML in {file}")
