import sys

with open('server.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Add /producto routes right after /catalogo route
catalogo_route = """@app.route('/catalogo')
def catalogo():
    return render_template('catalogo.html', show_nav=True, is_admin=False)"""

producto_route = """@app.route('/catalogo')
def catalogo():
    return render_template('catalogo.html', show_nav=True, is_admin=False)

@app.route('/producto')
@app.route('/producto.html')
def producto_view():
    return render_template('producto.html', show_nav=True, is_admin=False)"""

code = code.replace(catalogo_route, producto_route)

# Add GET /api/productos/<id> route
api_productos_route = """@app.route('/api/productos/<int:pid>', methods=['GET'])
def get_producto(pid):
    conn = get_db()
    row = conn.execute("SELECT * FROM productos WHERE id=?", (pid,)).fetchone()
    conn.close()
    if row:
        return jsonify({'ok': True, 'producto': dict(row)})
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/productos/<int:pid>', methods=['PUT', 'DELETE'])"""

code = code.replace("@app.route('/api/productos/<int:pid>', methods=['PUT', 'DELETE'])", api_productos_route)

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("server.py updated successfully!")
