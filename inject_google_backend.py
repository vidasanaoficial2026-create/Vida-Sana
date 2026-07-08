import os
import re

with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add the new route before the api_login route
google_route = """
import requests

@app.route('/api/google-login', methods=['POST'])
def api_google_login():
    data = request.json
    token = data.get('credential')
    if not token:
        return jsonify({'error': 'Falta el token de Google'}), 400
    
    # Validar el token con Google
    verify_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
    resp = requests.get(verify_url)
    
    if resp.status_code != 200:
        return jsonify({'error': 'Token de Google inválido'}), 401
        
    google_data = resp.json()
    email = google_data.get('email')
    nombre = google_data.get('name', 'Cliente')
    
    if not email:
        return jsonify({'error': 'No se pudo obtener el correo de Google'}), 400
        
    conn = get_db()
    # Buscar si el usuario existe
    row = conn.execute("SELECT * FROM usuarios WHERE email=?", (email,)).fetchone()
    
    if not row:
        # Registrar al nuevo usuario de Google
        import time
        username = email
        pw_hash = "GOOGLE_OAUTH_NO_PW" # No necesita contraseña porque usa Google
        conn.execute(
            "INSERT INTO usuarios (username, password, nombre, email, rol) VALUES (?, ?, ?, ?, 'cliente')",
            (username, pw_hash, nombre, email)
        )
        conn.commit()
        row = conn.execute("SELECT * FROM usuarios WHERE email=?", (email,)).fetchone()
        
    conn.close()
    
    # Iniciar sesión
    session['user_id'] = row['id']
    session['rol'] = row['rol']
    session['nombre'] = row['nombre']
    
    return jsonify({'ok': True, 'rol': row['rol'], 'nombre': row['nombre']})

@app.route('/api/login'"""

content = content.replace("@app.route('/api/login'", google_route)

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("server.py updated with google auth")
