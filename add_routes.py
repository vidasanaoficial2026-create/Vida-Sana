import os
with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_routes = '''
@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json or {}
    email = data.get('email')
    code = data.get('code')
    password = data.get('password')
    username = email
    nombre = 'Cliente'

    stored = verification_codes.get(email)
    if not stored or time.time() - stored['time'] > 300 or stored['code'] != str(code).strip():
        return jsonify({'error': 'Código inválido o expirado'}), 400

    conn = get_db()
    try:
        user = conn.execute("SELECT id FROM usuarios WHERE email = %s", (email,)).fetchone()
        if user:
            return jsonify({'error': 'Ya existe una cuenta con este correo'}), 400
        pw_hash = hashlib.sha256(f'{password}{SECRET}'.encode()).hexdigest()
        conn.execute(
            "INSERT INTO usuarios (username, password, nombre, email, rol) VALUES (%s, %s, %s, %s, 'cliente')",
            (username, pw_hash, nombre, email)
        )
        conn.commit()
        del verification_codes[email]
        return jsonify({'ok': True})
    except Exception as e:
        print("Error registro:", e)
        return jsonify({'error': 'Error interno al registrar usuario'}), 500
    finally:
        conn.close()

@app.route('/api/carrito', methods=['GET', 'POST'])
def api_carrito():
    if not is_authenticated():
        return jsonify({'error': 'No autorizado'}), 401
    user_id = session['user_id']
    conn = get_db()
    try:
        if request.method == 'GET':
            rows = conn.execute('''
                SELECT c.id, c.cantidad, p.id as producto_id, p.nombre, p.precio, p.imagen 
                FROM carrito c 
                JOIN productos p ON c.producto_id = p.id 
                WHERE c.usuario_id = %s
            ''', (user_id,)).fetchall()
            return jsonify({'ok': True, 'carrito': [dict(r) for r in rows]})
        elif request.method == 'POST':
            data = request.json
            producto_id = data.get('producto_id')
            cantidad = data.get('cantidad', 1)
            conn.execute('''
                INSERT INTO carrito (usuario_id, producto_id, cantidad) 
                VALUES (%s, %s, %s) 
                ON CONFLICT (usuario_id, producto_id) 
                DO UPDATE SET cantidad = carrito.cantidad + EXCLUDED.cantidad
            ''', (user_id, producto_id, cantidad))
            conn.commit()
            return jsonify({'ok': True})
    except Exception as e:
        print("Error carrito:", e)
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/checkout', methods=['POST'])
def api_checkout():
    if not is_authenticated():
        return jsonify({'error': 'No autorizado'}), 401
    user_id = session['user_id']
    conn = get_db()
    try:
        items = conn.execute('SELECT c.producto_id, c.cantidad, p.precio FROM carrito c JOIN productos p ON c.producto_id = p.id WHERE c.usuario_id = %s', (user_id,)).fetchall()
        if not items:
            return jsonify({'error': 'El carrito está vacío'}), 400
        total = sum(i['cantidad'] * i['precio'] for i in items)
        cur = conn.execute('INSERT INTO pedidos (usuario_id, total, estado) VALUES (%s, %s, %s) RETURNING id', (user_id, total, 'Pendiente'))
        pedido_id = cur.fetchone()['id']
        for item in items:
            conn.execute('INSERT INTO detalles_pedido (pedido_id, producto_id, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)', 
                         (pedido_id, item['producto_id'], item['cantidad'], item['precio']))
            conn.execute('UPDATE productos SET stock = stock - %s WHERE id = %s', (item['cantidad'], item['producto_id']))
        conn.execute('DELETE FROM carrito WHERE usuario_id = %s', (user_id,))
        conn.commit()
        return jsonify({'ok': True, 'pedido_id': pedido_id})
    except Exception as e:
        conn.rollback()
        print("Error checkout:", e)
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()
'''

if '@app.route('/api/register'' not in content:
    content = content.replace("@app.route('/api/login', methods=['POST'])", new_routes + "\n@app.route('/api/login', methods=['POST'])")
    with open('server.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Routes added')
else:
    print('Routes already exist')

