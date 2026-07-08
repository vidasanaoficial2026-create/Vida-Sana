import os
import hashlib
from datetime import datetime
import psycopg2
import psycopg2.extras
import uuid
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, make_response, send_from_directory
import json
import urllib.parse
from werkzeug.utils import secure_filename
import random
import smtplib
import time
from email.mime.text import MIMEText
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)

verification_codes = {}

@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    response.cache_control.no_cache = True
    response.cache_control.must_revalidate = True
    response.cache_control.max_age = 0
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

app.secret_key = 'natura-admin-secret-2026'

DB_PATH = os.path.join(os.path.dirname(__file__), 'natura.db')
SECRET = 'natura-admin-secret-2026'

class SQLiteEmulator:
    def __init__(self, conn):
        self.conn = conn
    def execute(self, query, params=()):
        cur = self.conn.cursor()
        query = query.replace('?', '%s')
        if "INSERT OR REPLACE INTO landing_config" in query:
            query = "INSERT INTO landing_config (clave, valor) VALUES (%s, %s) ON CONFLICT (clave) DO UPDATE SET valor = EXCLUDED.valor"
        cur.execute(query, params)
        return cur
    def executescript(self, script):
        pass
    def commit(self):
        self.conn.commit()
    def close(self):
        self.conn.close()

def get_db():
    conn = psycopg2.connect(os.getenv('DATABASE_URL'), cursor_factory=psycopg2.extras.DictCursor)
    return SQLiteEmulator(conn)

def init_db():
    conn = get_db()
    # (Same table structures as app.py)
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            nombre TEXT NOT NULL,
            dni TEXT,
            cargo TEXT DEFAULT '',
            area TEXT DEFAULT '',
            sueldo REAL DEFAULT 0,
            fecha_ingreso TEXT DEFAULT '',
            telefono TEXT DEFAULT '',
            direccion TEXT DEFAULT '',
            email TEXT DEFAULT '',
            estado TEXT DEFAULT 'Activo' CHECK(estado IN ('Activo','Inactivo')),
            rol TEXT NOT NULL DEFAULT 'worker' CHECK(rol IN ('admin','worker')),
            foto TEXT DEFAULT '',
            fecha_registro TEXT DEFAULT (datetime('now','-5 hours'))
        );
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT DEFAULT '',
            precio REAL NOT NULL,
            categoria TEXT DEFAULT '',
            imagen TEXT DEFAULT '',
            stock INTEGER DEFAULT 0,
            destacado INTEGER DEFAULT 0,
            fecha_registro TEXT DEFAULT (datetime('now','-5 hours'))
        );
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            total REAL NOT NULL,
            fecha TEXT DEFAULT (datetime('now','-5 hours')),
            FOREIGN KEY(producto_id) REFERENCES productos(id)
        );
    ''')
    cur = conn.execute("SELECT id FROM usuarios WHERE username='admin'")
    if not cur.fetchone():
        pw = hashlib.sha256(f'admin123{SECRET}'.encode()).hexdigest()
        conn.execute("INSERT INTO usuarios (username, password, nombre, rol) VALUES (?, ?, ?, 'admin')", ('admin', pw, 'Administrador'))
        conn.commit()
    conn.close()

init_db()

def is_authenticated():
    return 'user_id' in session

@app.route('/login', methods=['GET'])
def login_page():
    if is_authenticated():
        return redirect(url_for('index'))
    return render_template('login.html', show_nav=False)

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json or {}
    email = data.get('email')
    code = data.get('code')
    password = data.get('password')
    username = email
    nombre = data.get('nombre', 'Cliente')

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
            rows = conn.execute("""
                SELECT c.id, c.cantidad, p.id as producto_id, p.nombre, p.precio, p.imagen 
                FROM carrito c 
                JOIN productos p ON c.producto_id = p.id 
                WHERE c.usuario_id = %s
            """, (user_id,)).fetchall()
            return jsonify({'ok': True, 'carrito': [dict(r) for r in rows]})
        elif request.method == 'POST':
            data = request.json
            producto_id = data.get('producto_id')
            cantidad = data.get('cantidad', 1)
            conn.execute("""
                INSERT INTO carrito (usuario_id, producto_id, cantidad) 
                VALUES (%s, %s, %s) 
                ON CONFLICT (usuario_id, producto_id) 
                DO UPDATE SET cantidad = carrito.cantidad + EXCLUDED.cantidad
            """, (user_id, producto_id, cantidad))
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

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')
    conn = get_db()
    row = conn.execute("SELECT * FROM usuarios WHERE username=?", (username,)).fetchone()
    conn.close()
    if row:
        expected_pw = row['password']
        if password == expected_pw or hashlib.sha256(f'{password}{SECRET}'.encode()).hexdigest() == expected_pw:
            session['user_id'] = row['id']
            return jsonify({'ok': True}), 200
    return jsonify({'error': 'Credenciales inválidas'}), 401

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'ok': True}), 200

# Pages
@app.route('/')
def index():
    if not is_authenticated():
        return redirect(url_for('login_page'))
    return render_template('index.html', show_nav=True, is_admin=True)

@app.route('/admin_productos')
def admin_productos():
    if not is_authenticated():
        return redirect(url_for('login_page'))
    return render_template('admin_productos.html', show_nav=True, is_admin=True)

@app.route('/landing')
def landing():
    conn = get_db()
    rows = conn.execute("SELECT clave, valor FROM landing_config").fetchall()
    conn.close()
    config = {r['clave']: r['valor'] for r in rows}
    return render_template('landing.html', show_nav=True, is_admin=False, config=config)

@app.route('/dashboard')
def dashboard():
    if not is_authenticated():
        return redirect(url_for('login_page'))
    return render_template('dashboard.html', show_nav=True, is_admin=True)

@app.route('/admin_landing')
def admin_landing():
    if not is_authenticated():
        return redirect(url_for('login_page'))
    conn = get_db()
    rows = conn.execute("SELECT clave, valor FROM landing_config").fetchall()
    conn.close()
    config = {r['clave']: r['valor'] for r in rows}
    return render_template('admin_landing.html', show_nav=True, is_admin=True, config=config)

@app.route('/tienda')
def tienda():
    return render_template('tienda.html', show_nav=True, is_admin=False)

@app.route('/catalogo')
def catalogo():
    return render_template('catalogo.html', show_nav=True, is_admin=False)

@app.route('/worker')
def worker():
    return render_template('worker.html')

def _get_user_data(row):
    d = dict(row)
    del d['password']
    return d

@app.route('/api/productos', methods=['GET'])
def get_productos():
    conn = get_db()
    rows = conn.execute("SELECT * FROM productos ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify({'ok': True, 'productos': [dict(r) for r in rows]})

@app.route('/api/landing_config', methods=['POST'])
def save_landing_config():
    if not is_authenticated(): return jsonify({'error': 'No autorizado'}), 401
    data = request.json
    conn = get_db()
    try:
        for k, v in data.items():
            conn.execute("INSERT OR REPLACE INTO landing_config (clave, valor) VALUES (?, ?)", (k, v))
        conn.commit()
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()

@app.route('/api/ventas/stats', methods=['GET'])
def get_ventas_stats():
    if not is_authenticated(): return jsonify({'error': 'No autorizado'}), 401
    conn = get_db()
    ingresos = conn.execute("SELECT COALESCE(SUM(total), 0) FROM ventas").fetchone()[0]
    total_ventas = conn.execute("SELECT COUNT(*) FROM ventas").fetchone()[0]
    productos = conn.execute("SELECT COUNT(*) FROM productos").fetchone()[0]
    conn.close()
    return jsonify({'ok': True, 'ingresos': ingresos, 'total_ventas': total_ventas, 'productos': productos})

@app.route('/api/workers', methods=['GET'])
def get_workers():
    if not is_authenticated(): return jsonify({'error': 'No autorizado'}), 401
    conn = get_db()
    rows = conn.execute("SELECT * FROM usuarios WHERE rol='worker' ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify({'ok': True, 'workers': [_get_user_data(r) for r in rows]})

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

@app.route('/api/workers/count', methods=['GET'])
def get_workers_count():
    if not is_authenticated(): return jsonify({'error': 'No autorizado'}), 401
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM usuarios WHERE rol='worker'").fetchone()[0]
    activos = conn.execute("SELECT COUNT(*) FROM usuarios WHERE rol='worker' AND estado='Activo'").fetchone()[0]
    conn.close()
    return jsonify({'ok': True, 'total': total, 'activos': activos})

@app.route('/api/ventas', methods=['POST'])
def create_venta():
    if not is_authenticated(): return jsonify({'error': 'No autorizado'}), 401
    data = request.json
    conn = get_db()
    try:
        pid = data['producto_id']
        qty = int(data.get('cantidad', 1))
        row = conn.execute("SELECT precio, stock FROM productos WHERE id=?", (pid,)).fetchone()
        if not row: return jsonify({'error': 'Producto no encontrado'}), 404
        if row['stock'] < qty: return jsonify({'error': 'Stock insuficiente'}), 400
        total = row['precio'] * qty
        conn.execute("INSERT INTO ventas (producto_id, cantidad, total) VALUES (?,?,?)", (pid, qty, total))
        conn.execute("UPDATE productos SET stock = stock - ? WHERE id=?", (qty, pid))
        conn.commit()
        return jsonify({'ok': True, 'total': total, 'cantidad': qty}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()

@app.route('/api/send_code', methods=['POST'])
def send_code():
    data = request.json or {}
    email = data.get('email')
    if not email: return jsonify({'error': 'Email es requerido'}), 400
    
    code = str(random.randint(100000, 999999))
    verification_codes[email] = {'code': code, 'time': time.time()}
    
    api_key = os.environ.get('MAIL_API_KEY')
    sender_email = "vidasanaoficial2026@gmail.com"
    
    if api_key:
        try:
            url = "https://api.brevo.com/v3/smtp/email"
            headers = {
                "accept": "application/json",
                "api-key": api_key,
                "content-type": "application/json"
            }
            payload = {
                "sender": {"name": "Vida Sana", "email": sender_email},
                "to": [{"email": email}],
                "subject": "Código de Verificación - Vida Sana",
                "htmlContent": f"<p>Bienvenido a Vida Sana.</p><p>Tu código de verificación es: <b>{code}</b></p><p>Este código expirará en 5 minutos.</p><p>No compartas este código con nadie.</p>"
            }
            res = requests.post(url, json=payload, headers=headers)
            if res.ok:
                print(f"\n[BREVO API] Código enviado a {email}\n")
                return jsonify({'ok': True, 'method': 'api'})
            else:
                print("Error de Brevo API:", res.text)
                return jsonify({'error': 'Error de API al enviar el correo'}), 500
        except Exception as e:
            print("Error enviando correo por API:", e)
            return jsonify({'error': 'Error de conexión al enviar el correo'}), 500
    else:
        # Fallback si no hay API key
        print("\n" + "="*60)
        print(f" [SIMULADOR CORREO] Enviando a: {email}")
        print(f" Código de verificación: {code}")
        print("="*60 + "\n")
        return jsonify({'ok': True, 'method': 'simulated'})

@app.route('/api/check_code', methods=['POST'])
def check_code():
    data = request.json or {}
    email = data.get('email')
    code = data.get('code')
    
    stored = verification_codes.get(email)
    if not stored:
        return jsonify({'error': 'No existe código activo'}), 400
    
    if time.time() - stored['time'] > 300:
        return jsonify({'error': 'Expirado'}), 400
        
    if stored['code'] == str(code).strip():
        return jsonify({'ok': True})
        
    return jsonify({'error': 'Incorrecto'}), 400

@app.route('/api/verify_code', methods=['POST'])
def verify_code():
    data = request.json or {}
    email = data.get('email')
    code = data.get('code')
    
    stored = verification_codes.get(email)
    if not stored:
        return jsonify({'error': 'No se encontró un código para este correo'}), 400
        
    if time.time() - stored['time'] > 300: # 5 minutos
        return jsonify({'error': 'El código ha expirado. Por favor, solicita uno nuevo.'}), 400
        
    if stored['code'] == str(code).strip():
        # Lo eliminamos para que no se re-use
        del verification_codes[email]
        return jsonify({'ok': True})
        
    return jsonify({'error': 'Código incorrecto'}), 400

@app.route('/api/reset_password', methods=['POST'])
def reset_password():
    data = request.json or {}
    email = data.get('email')
    code = data.get('code')
    new_password = data.get('new_password')
    
    stored = verification_codes.get(email)
    if not stored:
        return jsonify({'error': 'No se encontró un código para este correo o ya fue usado'}), 400
        
    if time.time() - stored['time'] > 300:
        return jsonify({'error': 'El código ha expirado'}), 400
        
    if stored['code'] == str(code).strip():
        # Código correcto. Actualizamos en la base de datos
        conn = get_db()
        try:
            # Primero verificamos si el correo existe
            user = conn.execute("SELECT id FROM usuarios WHERE email = ?", (email,)).fetchone()
            if not user:
                return jsonify({'error': 'No existe una cuenta con este correo electrónico'}), 400
            
            conn.execute("UPDATE usuarios SET password = ? WHERE email = ?", (new_password, email))
            conn.commit()
            
            # Limpiamos el código
            del verification_codes[email]
            
            return jsonify({'ok': True})
        except Exception as e:
            print("Error actualizando contraseña:", e)
            return jsonify({'error': 'Error interno al actualizar la contraseña'}), 500
        finally:
            conn.close()
    
    return jsonify({'error': 'Código incorrecto'}), 400


@app.route('/api/productos', methods=['POST'])
def create_producto():
    if not is_authenticated(): return jsonify({'error': 'No autorizado'}), 401
    
    # Soporte para FormData (archivos) y JSON
    if request.content_type and 'multipart/form-data' in request.content_type:
        data = request.form
    else:
        data = request.json or {}
        
    imagen_path = data.get('imagen', '')
    
    if 'imagen_file' in request.files:
        file = request.files['imagen_file']
        if file.filename != '':
            ext = os.path.splitext(file.filename)[1]
            filename = f"prod_{uuid.uuid4().hex}{ext}"
            filepath = os.path.join('static', 'img', 'productos', filename)
            file.save(filepath)
            imagen_path = f"/{filepath.replace(chr(92), '/')}"
            
    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO productos (nombre, descripcion, precio, categoria, imagen, stock) VALUES (?,?,?,?,?,?) RETURNING id",
            (data.get('nombre'), data.get('descripcion', ''), float(data.get('precio', 0)), data.get('categoria', ''), imagen_path, int(data.get('stock', 0)))
        )
        pid = cur.fetchone()[0]
        conn.commit()
        row = conn.execute("SELECT * FROM productos WHERE id=?", (pid,)).fetchone()
        return jsonify({'ok': True, 'producto': dict(row)}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()

@app.route('/api/productos/<int:pid>', methods=['PUT', 'DELETE'])
def manage_producto(pid):
    if not is_authenticated(): return jsonify({'error': 'No autorizado'}), 401
    conn = get_db()
    try:
        if request.method == 'DELETE':
            conn.execute("DELETE FROM productos WHERE id=?", (pid,))
            conn.commit()
            return jsonify({'ok': True})
        elif request.method == 'PUT':
            if request.content_type and 'multipart/form-data' in request.content_type:
                data = request.form
            else:
                data = request.json or {}
                
            imagen_path = data.get('imagen')
            
            if 'imagen_file' in request.files:
                file = request.files['imagen_file']
                if file.filename != '':
                    ext = os.path.splitext(file.filename)[1]
                    filename = f"prod_{uuid.uuid4().hex}{ext}"
                    filepath = os.path.join('static', 'img', 'productos', filename)
                    file.save(filepath)
                    imagen_path = f"/{filepath.replace(chr(92), '/')}"
            
            # If imagen_path is missing, keep the old one
            if imagen_path is None:
                old_row = conn.execute("SELECT imagen FROM productos WHERE id=?", (pid,)).fetchone()
                imagen_path = old_row['imagen'] if old_row else ''
                
            conn.execute(
                "UPDATE productos SET nombre=?, descripcion=?, precio=?, categoria=?, imagen=?, stock=? WHERE id=?",
                (data.get('nombre'), data.get('descripcion', ''), float(data.get('precio', 0)), data.get('categoria', ''), imagen_path, int(data.get('stock', 0)), pid)
            )
            conn.commit()
            row = conn.execute("SELECT * FROM productos WHERE id=?", (pid,)).fetchone()
            if row: return jsonify({'ok': True, 'producto': dict(row)})
            else: return jsonify({'error': 'No encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(port=8000, debug=True)
