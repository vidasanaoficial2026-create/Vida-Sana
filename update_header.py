import os

files_to_update = ['templates/tienda.html', 'templates/catalogo.html']

old_btn = """      <button class="header-login" onclick="toggleLogin()" aria-label="Mi cuenta" id="loginBtn">
        <i class="fas fa-user"></i>
      </button>"""

new_btn = """      {% if session.get('nombre') %}
      <div style="display:flex; align-items:center; gap:10px;">
        <span style="color:var(--text); font-weight:600; font-size:14px;">Hola, {{ session.get('nombre').split(' ')[0] }}</span>
        <button class="header-login" onclick="logoutCustomer()" aria-label="Cerrar sesión" title="Cerrar sesión" style="color:#dc3545;">
          <i class="fas fa-sign-out-alt"></i>
        </button>
      </div>
      <script>
        async function logoutCustomer() {
          await fetch('/api/logout', {method: 'POST'});
          window.location.reload();
        }
      </script>
      {% else %}
      <button class="header-login" onclick="toggleLogin()" aria-label="Mi cuenta" id="loginBtn">
        <i class="fas fa-user"></i>
      </button>
      {% endif %}"""

for file in files_to_update:
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        content = content.replace(old_btn, new_btn)
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated header in {file}")
