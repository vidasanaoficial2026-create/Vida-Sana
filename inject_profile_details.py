import os

# 1. Update server.py
with open('server.py', 'r', encoding='utf-8') as f:
    server_content = f.read()

# Fix api_login
if "session['nombre'] = row['nombre']" not in server_content.split("def api_login():")[1].split("def api_logout():")[0]:
    server_content = server_content.replace(
        "session['user_id'] = row['id']\n            return jsonify({'ok': True}), 200",
        "session['user_id'] = row['id']\n            session['nombre'] = row['nombre']\n            session['email'] = row['email']\n            session['rol'] = row['rol']\n            return jsonify({'ok': True}), 200"
    )

# Fix api_google_login to update nombre if it's 'Cliente' and add email to session
google_login_old = """    # Iniciar sesión
    session['user_id'] = row['id']
    session['rol'] = row['rol']
    session['nombre'] = row['nombre']"""

google_login_new = """    # Si el usuario ya existía pero su nombre es 'Cliente', actualizarlo con el de Google
    db_nombre = dict(row).get('nombre', 'Cliente')
    if db_nombre == 'Cliente' and nombre and nombre != 'Cliente':
        conn = get_db()
        conn.execute("UPDATE usuarios SET nombre=? WHERE email=?", (nombre, email))
        conn.commit()
        conn.close()
        db_nombre = nombre

    # Iniciar sesión
    session['user_id'] = row['id']
    session['rol'] = row['rol']
    session['nombre'] = db_nombre
    session['email'] = row['email']"""

if "db_nombre = dict(row).get('nombre', 'Cliente')" not in server_content:
    server_content = server_content.replace(google_login_old, google_login_new)

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(server_content)
print("server.py updated")

# 2. Update tienda.html and catalogo.html
files = ['templates/tienda.html', 'templates/catalogo.html']

profile_header_html = """      <h2>Mi Perfil</h2>
      {% if session.get('nombre') %}
      <div style="text-align:center; margin-bottom: 20px; padding: 15px; background: #f9f9f9; border-radius: 8px;">
        <div style="width: 50px; height: 50px; background: var(--primary); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: bold; margin: 0 auto 10px auto;">
          {{ session.get('nombre')[0].upper() }}
        </div>
        <h3 style="margin:0; font-size:18px; color: #333;">{{ session.get('nombre') }}</h3>
        <p style="color:#666; margin:5px 0 0 0; font-size:14px;">{{ session.get('email') }}</p>
      </div>
      {% endif %}"""

for file in files:
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        if "session.get('email')" not in html_content:
            html_content = html_content.replace("<h2>Mi Perfil</h2>", profile_header_html)
            with open(file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"{file} updated")
