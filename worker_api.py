import os
with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_endpoints = '''
@app.route('/api/workers', methods=['POST'])
def create_worker():
    if not is_authenticated(): return jsonify({'error': 'No autorizado'}), 401
    data = request.json or {}
    nombre = data.get('nombre', '')
    dni = data.get('dni', '')
    cargo = data.get('cargo', '')
    area = data.get('area', '')
    fecha_ingreso = data.get('fecha_ingreso', '')
    telefono = data.get('telefono', '')
    direccion = data.get('direccion', '')
    email = data.get('email', '')
    estado = data.get('estado', 'Activo')
    foto = data.get('foto', '')
    
    import random
    import string
    username = nombre.split(' ')[0].lower() + str(random.randint(100,999)) if nombre else 'user' + str(random.randint(1000,9999))
    password = dni if dni else ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    pw_hash = hashlib.sha256(f'{password}{SECRET}'.encode()).hexdigest()
    
    conn = get_db()
    try:
        cur = conn.execute('''
            INSERT INTO usuarios (username, password, nombre, dni, cargo, area, fecha_ingreso, telefono, direccion, email, estado, foto, rol)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'worker') RETURNING id
        ''', (username, pw_hash, nombre, dni, cargo, area, fecha_ingreso, telefono, direccion, email, estado, foto))
        new_id = cur.fetchone()['id']
        conn.commit()
        worker = conn.execute("SELECT * FROM usuarios WHERE id = %s", (new_id,)).fetchone()
        return jsonify({'ok': True, 'generated_username': username, 'generated_password': password, 'worker': dict(worker)}), 201
    except Exception as e:
        conn.rollback()
        print('Error create worker:', e)
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()

@app.route('/api/workers/<int:worker_id>', methods=['GET'])
def get_worker_by_id(worker_id):
    conn = get_db()
    worker = conn.execute("SELECT * FROM usuarios WHERE id = %s AND rol='worker'", (worker_id,)).fetchone()
    conn.close()
    if worker:
        return jsonify({'ok': True, 'worker': _get_user_data(worker)})
    return jsonify({'error': 'Trabajador no encontrado'}), 404

@app.route('/api/workers/<int:worker_id>', methods=['PUT'])
def update_worker(worker_id):
    if not is_authenticated(): return jsonify({'error': 'No autorizado'}), 401
    data = request.json or {}
    conn = get_db()
    try:
        conn.execute('''
            UPDATE usuarios 
            SET nombre=%s, dni=%s, cargo=%s, area=%s, fecha_ingreso=%s, telefono=%s, direccion=%s, email=%s, estado=%s, foto=%s
            WHERE id=%s AND rol='worker'
        ''', (
            data.get('nombre',''), data.get('dni',''), data.get('cargo',''), data.get('area',''), 
            data.get('fecha_ingreso',''), data.get('telefono',''), data.get('direccion',''), 
            data.get('email',''), data.get('estado','Activo'), data.get('foto',''), worker_id
        ))
        conn.commit()
        return jsonify({'ok': True})
    except Exception as e:
        conn.rollback()
        print('Error update worker:', e)
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()
'''

if "'POST')" not in content.split("@app.route('/api/workers'")[0] and "@app.route('/api/workers/<int:worker_id>', methods=['PUT'])" not in content:
    content = content.replace("@app.route('/api/workers/count', methods=['GET'])", new_endpoints + "\n@app.route('/api/workers/count', methods=['GET'])")
    with open('server.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Worker endpoints added successfully')
else:
    print('Endpoints already present')

