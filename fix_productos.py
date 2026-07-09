import os

file = 'server.py'

old_func = """@app.route('/api/productos', methods=['GET'])
def get_productos():
    conn = get_db()
    rows = conn.execute("SELECT * FROM productos ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify({'ok': True, 'productos': [dict(r) for r in rows]})"""

new_func = """@app.route('/api/productos', methods=['GET'])
def get_productos():
    categoria = request.args.get('categoria', '').strip()
    q = request.args.get('q', '').strip()
    
    conn = get_db()
    
    query = "SELECT * FROM productos WHERE 1=1"
    params = []
    
    if categoria:
        # Hacer coincidencia que no distinga mayúsculas y minúsculas y soporte comodines si es necesario
        query += " AND categoria COLLATE NOCASE = ?"
        params.append(categoria)
        
    if q:
        query += " AND (nombre LIKE ? OR descripcion LIKE ?)"
        params.extend([f'%{q}%', f'%{q}%'])
        
    query += " ORDER BY id DESC"
    
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify({'ok': True, 'productos': [dict(r) for r in rows]})"""

with open(file, 'r', encoding='utf-8') as f:
    content = f.read()

if old_func in content:
    content = content.replace(old_func, new_func)
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully updated get_productos in server.py")
else:
    print("Could not find the exact get_productos block in server.py")
