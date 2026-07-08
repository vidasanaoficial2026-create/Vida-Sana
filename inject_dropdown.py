import os
import re

files = ['templates/tienda.html', 'templates/catalogo.html']

dropdown_html = """
        {% if session.get('nombre') %}
        <div class="profile-dropdown-wrap" style="position: relative; display:flex; align-items:center; cursor:pointer; padding: 10px 0;">
          <span style="color:var(--text); font-weight:600; font-size:14px; display:flex; align-items:center; gap:5px; padding: 5px 10px; border-radius: 20px; transition: background 0.3s;" onmouseover="this.style.background='#f0f0f0'" onmouseout="this.style.background='transparent'">
            Hola, {{ session.get('nombre').split(' ')[0] }} <i class="fas fa-caret-down"></i>
          </span>
          <div id="myProfileDropdown" class="profile-dropdown" style="display:none; position:absolute; top:45px; right:0; background:#fff; box-shadow:0 10px 25px rgba(0,0,0,0.15); border-radius:12px; width:250px; z-index:1000; overflow:hidden; border: 1px solid #eee;">
            <div style="background:var(--primary); color:white; padding:20px; text-align:center;">
               <div style="width:50px; height:50px; background:white; color:var(--primary); border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:22px; font-weight:bold; margin:0 auto 10px auto; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                  {{ session.get('nombre')[0].upper() }}
               </div>
               <div style="font-weight:bold; font-size:16px;">{{ session.get('nombre') }}</div>
               <div style="font-size:12px; opacity:0.9; margin-top:2px; word-break:break-all;">{{ session.get('email') }}</div>
            </div>
            <div style="padding:10px 0;">
               <a onclick="openProfileModal('pedidos')" style="display:flex; align-items:center; gap:10px; padding:12px 20px; color:#333; text-decoration:none; font-size:14px; cursor:pointer; transition: background 0.2s;" onmouseover="this.style.background='#f9f9f9'" onmouseout="this.style.background='transparent'">
                  <i class="fas fa-box" style="color:var(--primary); width:20px; text-align:center;"></i> Mis Pedidos
               </a>
               <a onclick="openProfileModal('favoritos')" style="display:flex; align-items:center; gap:10px; padding:12px 20px; color:#333; text-decoration:none; font-size:14px; cursor:pointer; transition: background 0.2s;" onmouseover="this.style.background='#f9f9f9'" onmouseout="this.style.background='transparent'">
                  <i class="fas fa-heart" style="color:var(--primary); width:20px; text-align:center;"></i> Mis Favoritos
               </a>
               <div style="border-top:1px solid #eee; margin:5px 0;"></div>
               <a onclick="logoutCustomer()" style="display:flex; align-items:center; gap:10px; padding:12px 20px; color:#dc3545; text-decoration:none; font-size:14px; cursor:pointer; transition: background 0.2s;" onmouseover="this.style.background='#fff5f5'" onmouseout="this.style.background='transparent'">
                  <i class="fas fa-sign-out-alt" style="width:20px; text-align:center;"></i> Cerrar Sesión
               </a>
            </div>
          </div>
        </div>
        <script>
          function openProfileModal(tab) {
             document.getElementById('myProfileDropdown').style.display = 'none';
             document.getElementById('loginOverlay').style.display='flex';
             toggleAuthView('profile');
             showProfileTab(tab);
          }
          document.addEventListener('click', function(e) {
             const wrap = document.querySelector('.profile-dropdown-wrap');
             const dropdown = document.getElementById('myProfileDropdown');
             if (wrap && dropdown) {
                 if (wrap.contains(e.target)) {
                     dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
                 } else {
                     dropdown.style.display = 'none';
                 }
             }
          });
          async function logoutCustomer() {
            await fetch('/api/logout', {method: 'POST'});
            window.location.reload();
          }
        </script>
"""

for file in files:
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # We need to replace the old header block with the new one
        # The block starts at "{% if session.get('nombre') %}" and ends right before "{% else %}"
        # We will use regex to find this exact block of HTML
        
        pattern = re.compile(r"\{% if session\.get\('nombre'\) %\}.*?<div style=\"display:flex; align-items:center; gap:10px;\">.*?Hola, \{\{ session\.get\('nombre'\)\.split\(' '\)\[0\] \}\} <i class=\"fas fa-caret-down\"></i></span>.*?<script>.*?async function logoutCustomer.*?window\.location\.reload\(\);\s*\}\s*</script>", re.DOTALL)
        
        match = pattern.search(content)
        if match:
            new_content = content[:match.start()] + dropdown_html.strip('\n') + content[match.end():]
            with open(file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Replaced header in {file}")
        else:
            print(f"Could not find matching header in {file}")
