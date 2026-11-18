import os
import hashlib
from datetime import datetime
from functools import wraps
import psycopg2
import psycopg2.extras
import uuid
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, make_response, send_from_directory
import json
import urllib.parse
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
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

# Configuration and secrets (loaded safely from environment)
app.secret_key = os.getenv('SECRET_KEY', 'natura-admin-secret-2026')
SECRET = os.getenv('SECRET_KEY', 'natura-admin-secret-2026')
DB_PATH = os.path.join(os.path.dirname(__file__), 'natura.db')

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
    def rollback(self):
        self.conn.rollback()
    def close(self):
        self.conn.close()

def get_db():
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("[DATABASE CRITICAL] DATABASE_URL no configurada en las variables de entorno.")
        raise RuntimeError("DATABASE_URL no configurada.")
    try:
        conn = psycopg2.connect(
            db_url,
            cursor_factory=psycopg2.extras.DictCursor,
            connect_timeout=8
        )
        return SQLiteEmulator(conn)
    except psycopg2.OperationalError as e:
        print(f"[DATABASE ERROR] Error conectando a PostgreSQL/Supabase: {e}")
        raise

@app.errorhandler(psycopg2.OperationalError)
def handle_db_error(e):
    print(f"[ERROR 503] Servicio de base de datos no disponible: {e}")
    error_msg = 'El servicio de base de datos está temporalmente no disponible. Por favor intente nuevamente en unos instantes.'
    if request.path.startswith('/api/') or request.is_json:
        return jsonify({
            'error': 'Servicio de base de datos temporalmente no disponible. Intente nuevamente en unos instantes.',
            'status': 503
        }), 503
    if request.path.startswith('/worker/public/'):
        return render_template(
            'worker_public.html',
            worker=None,
            error=error_msg,
            error_title='Servicio No Disponible',
            error_hint='Intenta escanear el código nuevamente en unos minutos'
        ), 503
    return render_template(
        'login.html',
        error=error_msg,
        show_nav=False
    ), 503

def init_db():
    try:
        conn = get_db()
        cur = conn.execute("SELECT id FROM usuarios WHERE username='admin'")
        if not cur.fetchone():
            pw = generate_password_hash('admin123')
            conn.execute("INSERT INTO usuarios (username, password, nombre, rol) VALUES (%s, %s, %s, 'admin')", ('admin', pw, 'Administrador'))
            conn.commit()
        col = conn.execute(
            "SELECT 1 FROM information_schema.columns WHERE table_name = 'usuarios' AND column_name = 'public_uuid'"
        ).fetchone()
        if not col:
            conn.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS public_uuid VARCHAR(64) UNIQUE")
            conn.commit()
        missing_uuids = conn.execute(
            "SELECT id FROM usuarios WHERE rol = 'worker' AND (public_uuid IS NULL OR public_uuid = '')"
        ).fetchall()
        if missing_uuids:
            for row in missing_uuids:
                conn.execute(
                    "UPDATE usuarios SET public_uuid = %s WHERE id = %s AND (public_uuid IS NULL OR public_uuid = '')",
                    (str(uuid.uuid4()), row['id'])
                )
            conn.commit()
        conn.close()
    except Exception as e:
        print(f"[INIT_DB WARNING] No se pudo inicializar la base de datos: {e}")

init_db()

def is_authenticated():
    return 'user_id' in session

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            if request.path.startswith('/api/') or request.is_json:
                return jsonify({'error': 'No autorizado: sesión requerida'}), 401
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not is_authenticated():
                if request.path.startswith('/api/') or request.is_json:
                    return jsonify({'error': 'No autorizado: sesión requerida'}), 401
                return redirect(url_for('login_page'))
            user_role = session.get('rol', '')
            if user_role not in allowed_roles:
                if request.path.startswith('/api/') or request.is_json:
                    return jsonify({'error': 'Acceso denegado: permisos insuficientes'}), 403
                return render_template('login.html', error='Acceso denegado: permisos insuficientes', show_nav=False), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def verify_and_migrate_password(conn, user_id, password_input, stored_hash):
    """
    Verifica la contraseña y migra progresivamente hashes antiguos o texto plano
    hacia Werkzeug PBKDF2/scrypt tras un login exitoso.
    """
    if not stored_hash or not password_input:
        return False

    is_valid = False
    needs_rehash = False

    # 1. Verificación moderna de Werkzeug
    if stored_hash.startswith(('pbkdf2:', 'scrypt:', 'argon2:')):
        is_valid = check_password_hash(stored_hash, password_input)
    else:
        # 2. Compatibilidad con hash antiguo SHA-256 + salt
        legacy_hash = hashlib.sha256(f'{password_input}{SECRET}'.encode()).hexdigest()
        if stored_hash == legacy_hash:
            is_valid = True
            needs_rehash = True
        # 3. Compatibilidad temporal con texto plano antiguo
        elif stored_hash == password_input:
            is_valid = True
            needs_rehash = True

    # 4. Migración inmediata y automática tras credenciales válidas
    if is_valid and needs_rehash:
        new_hash = generate_password_hash(password_input)
        try:
            conn.execute("UPDATE usuarios SET password = %s WHERE id = %s", (new_hash, user_id))
            conn.commit()
            print(f"[AUTH] Contraseña migrada exitosamente a Werkzeug para el usuario ID {user_id}.")
        except Exception as e:
            print(f"[AUTH ERROR] Error al migrar contraseña del usuario ID {user_id}: {e}")

    return is_valid

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
        pw_hash = generate_password_hash(password)
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
@login_required
def api_carrito():
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
@login_required
def api_checkout():
    user_id = session['user_id']
    conn = get_db()
    try:
        # 1. Obtener items del carrito para el usuario ordenados por producto_id para prevenir deadlocks
        cart_items = conn.execute('''
            SELECT producto_id, cantidad 
            FROM carrito 
            WHERE usuario_id = %s 
            ORDER BY producto_id ASC
        ''', (user_id,)).fetchall()
        
        if not cart_items:
            return jsonify({'error': 'El carrito está vacío'}), 400
            
        # 2. Bloqueo pesimista y verificación de stock fila por fila (SELECT ... FOR UPDATE)
        verified_items = []
        total = 0.0
        
        for item in cart_items:
            p_id = item['producto_id']
            solicitado = item['cantidad']
            
            # Bloquea la fila del producto en PostgreSQL para prevenir overselling concurrente
            prod = conn.execute('''
                SELECT id, nombre, precio, stock 
                FROM productos 
                WHERE id = %s 
                FOR UPDATE
            ''', (p_id,)).fetchone()
            
            if not prod:
                conn.rollback()
                return jsonify({'error': f"El producto ID {p_id} ya no está disponible"}), 404
                
            if prod['stock'] < solicitado:
                conn.rollback()
                return jsonify({
                    'error': f"Stock insuficiente para el producto '{prod['nombre']}'",
                    'producto_id': prod['id'],
                    'stock_disponible': prod['stock'],
                    'cantidad_solicitada': solicitado
                }), 409
                
            precio_unitario = float(prod['precio'])
            subtotal = precio_unitario * solicitado
            total += subtotal
            
            verified_items.append({
                'producto_id': prod['id'],
                'nombre': prod['nombre'],
                'cantidad': solicitado,
                'precio_unitario': precio_unitario
            })
            
        # 3. Insertar pedido con total calculado estrictamente en el backend
        cur = conn.execute(
            'INSERT INTO pedidos (usuario_id, total, estado) VALUES (%s, %s, %s) RETURNING id',
            (user_id, total, 'Pendiente')
        )
        pedido_id = cur.fetchone()['id']
        
        # 4. Insertar detalles con precio unitario congelado y descontar stock
        for v in verified_items:
            conn.execute(
                'INSERT INTO detalles_pedido (pedido_id, producto_id, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)', 
                (pedido_id, v['producto_id'], v['cantidad'], v['precio_unitario'])
            )
            conn.execute(
                'UPDATE productos SET stock = stock - %s WHERE id = %s',
                (v['cantidad'], v['producto_id'])
            )
            
        # 5. Vaciar carrito del usuario
        conn.execute('DELETE FROM carrito WHERE usuario_id = %s', (user_id,))
        
        # 6. Commit de toda la operación en una sola transacción
        conn.commit()
        return jsonify({'ok': True, 'pedido_id': pedido_id})
    except Exception as e:
        conn.rollback()
        print("[ERROR CHECKOUT]", e)
        return jsonify({'error': 'Error interno al procesar el pedido'}), 500
    finally:
        conn.close()

# API FAVORITOS (Persistencia oficial en Base de Datos)
@app.route('/api/favoritos', methods=['GET'])
@login_required
def get_favoritos():
    user_id = session['user_id']
    conn = get_db()
    try:
        rows = conn.execute("""
            SELECT f.id as favorito_id, f.producto_id, f.fecha,
                   p.nombre, p.precio, p.imagen, p.categoria, p.stock
            FROM favoritos f
            JOIN productos p ON f.producto_id = p.id
            WHERE f.usuario_id = %s
            ORDER BY f.id DESC
        """, (user_id,)).fetchall()
        return jsonify({'ok': True, 'favoritos': [dict(r) for r in rows]})
    except Exception as e:
        print("[ERROR FAVORITOS GET]", e)
        return jsonify({'error': 'Error al consultar favoritos'}), 500
    finally:
        conn.close()

@app.route('/api/favoritos', methods=['POST'])
@login_required
def add_favorito():
    user_id = session['user_id']
    data = request.json or {}
    producto_id = data.get('producto_id')
    if not producto_id:
        return jsonify({'error': 'producto_id es requerido'}), 400
    try:
        producto_id = int(producto_id)
    except (ValueError, TypeError):
        return jsonify({'error': 'producto_id debe ser un número entero'}), 400

    conn = get_db()
    try:
        prod = conn.execute("SELECT id FROM productos WHERE id = %s", (producto_id,)).fetchone()
        if not prod:
            return jsonify({'error': 'Producto no encontrado'}), 404

        exists = conn.execute(
            "SELECT id FROM favoritos WHERE usuario_id = %s AND producto_id = %s",
            (user_id, producto_id)
        ).fetchone()
        if exists:
            return jsonify({'ok': True, 'mensaje': 'El producto ya está en favoritos', 'favorito_id': exists['id']}), 200

        conn.execute(
            "INSERT INTO favoritos (usuario_id, producto_id) VALUES (%s, %s)",
            (user_id, producto_id)
        )
        conn.commit()
        return jsonify({'ok': True, 'mensaje': 'Producto añadido a favoritos'}), 201
    except Exception as e:
        conn.rollback()
        print("[ERROR FAVORITOS POST]", e)
        return jsonify({'error': 'Error al guardar favorito'}), 500
    finally:
        conn.close()

@app.route('/api/favoritos/<int:producto_id>', methods=['DELETE'])
@login_required
def delete_favorito(producto_id):
    user_id = session['user_id']
    conn = get_db()
    try:
        conn.execute(
            "DELETE FROM favoritos WHERE usuario_id = %s AND producto_id = %s",
            (user_id, producto_id)
        )
        conn.commit()
        return jsonify({'ok': True, 'mensaje': 'Producto eliminado de favoritos'})
    except Exception as e:
        conn.rollback()
        print("[ERROR FAVORITOS DELETE]", e)
        return jsonify({'error': 'Error al eliminar favorito'}), 500
    finally:
        conn.close()


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
    
    # Si el usuario ya existía pero su nombre es 'Cliente', actualizarlo con el de Google
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
    session['email'] = row['email']
    
    return jsonify({'ok': True, 'rol': row['rol'], 'nombre': row['nombre']})


@app.route('/api/mis-pedidos', methods=['GET'])
@login_required
def api_mis_pedidos():
    conn = get_db()
    pedidos = conn.execute("SELECT * FROM pedidos WHERE usuario_id = %s ORDER BY id DESC", (session['user_id'],)).fetchall()
    conn.close()
    
    pedidos_list = []
    for p in pedidos:
        pedidos_list.append({
            'id': p['id'],
            'total': p['total'],
            'estado': p['estado']
        })
    return jsonify({'pedidos': pedidos_list})

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')
    if not username or not password:
        return jsonify({'error': 'Usuario y contraseña requeridos'}), 400

    conn = get_db()
    row = conn.execute("SELECT * FROM usuarios WHERE username = %s OR email = %s", (username, username)).fetchone()
    if row:
        if verify_and_migrate_password(conn, row['id'], password, row['password']):
            session['user_id'] = row['id']
            session['nombre'] = row['nombre']
            session['email'] = row['email']
            session['rol'] = row['rol']
            conn.close()
            return jsonify({'ok': True, 'rol': row['rol'], 'nombre': row['nombre']}), 200
    conn.close()
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
    user_rol = session.get('rol', '')
    if user_rol == 'cliente':
        return redirect(url_for('tienda'))
    elif user_rol == 'worker':
        return redirect(url_for('worker'))
    elif user_rol == 'admin':
        return render_template('index.html', show_nav=True, is_admin=True)
    return redirect(url_for('login_page'))

@app.route('/admin_productos')
@role_required('admin')
def admin_productos():
    return render_template('admin_productos.html', show_nav=True, is_admin=True)

@app.route('/landing')
def landing():
    conn = get_db()
    rows = conn.execute("SELECT clave, valor FROM landing_config").fetchall()
    conn.close()
    config = {r['clave']: r['valor'] for r in rows}
    return render_template('landing.html', show_nav=True, is_admin=False, config=config)

@app.route('/dashboard')
@role_required('admin')
def dashboard():
    return render_template('dashboard.html', show_nav=True, is_admin=True)

@app.route('/admin_landing')
@role_required('admin')
def admin_landing():
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

@app.route('/producto')
@app.route('/producto.html')
def producto_view():
    return render_template('producto.html', show_nav=True, is_admin=False)

@app.route('/worker')
@role_required('admin', 'worker')
def worker():
    return render_template('worker.html')

@app.route('/worker/public/<string:uuid_val>', methods=['GET'])
def worker_public_profile(uuid_val):
    conn = get_db()
    try:
        worker_row = conn.execute(
            "SELECT nombre, cargo, area, estado, foto FROM usuarios WHERE public_uuid = %s AND rol = 'worker'",
            (uuid_val,)
        ).fetchone()
    finally:
        conn.close()

    wants_json = request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json'
    if not worker_row:
        error_msg = 'Trabajador no encontrado o credencial inválida'
        if wants_json:
            return jsonify({'ok': False, 'error': error_msg}), 404
        return render_template('worker_public.html', worker=None, error=error_msg), 404

    if wants_json:
        return jsonify({'ok': True, 'worker': dict(worker_row)})
    return render_template('worker_public.html', worker=dict(worker_row), error=None)

def _get_user_data(row):
    d = dict(row)
    del d['password']
    return d

def _ensure_worker_public_uuid(conn, row):
    """Ensure every worker record has a persisted public_uuid before exposing it."""
    d = _get_user_data(row)
    if d.get('rol') == 'worker' and not d.get('public_uuid'):
        new_uuid = str(uuid.uuid4())
        updated = conn.execute(
            "UPDATE usuarios SET public_uuid = %s WHERE id = %s AND (public_uuid IS NULL OR public_uuid = '') RETURNING public_uuid",
            (new_uuid, d['id'])
        ).fetchone()
        if updated:
            d['public_uuid'] = updated['public_uuid']
        else:
            refetched = conn.execute("SELECT public_uuid FROM usuarios WHERE id = %s", (d['id'],)).fetchone()
            if refetched:
                d['public_uuid'] = refetched['public_uuid']
        conn.commit()
    return d

@app.route('/api/productos', methods=['GET'])
def get_productos():
    categoria = request.args.get('categoria', '').strip()
    q = request.args.get('q', '').strip()
    
    conn = get_db()
    
    query = "SELECT * FROM productos WHERE 1=1"
    params = []
    
    if categoria:
        # Hacer coincidencia que no distinga mayúsculas y minúsculas y soporte comodines si es necesario
        query += " AND categoria = ?"
        params.append(categoria)
        
    if q:
        query += " AND (nombre ILIKE ? OR descripcion ILIKE ?)"
        params.extend([f'%{q}%', f'%{q}%'])
        
    query += " ORDER BY id DESC"
    
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify({'ok': True, 'productos': [dict(r) for r in rows]})

@app.route('/api/landing_config', methods=['POST'])
@role_required('admin')
def save_landing_config():
    data = request.json or {}
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
@role_required('admin')
def get_ventas_stats():
    conn = get_db()
    try:
        row_pedidos = conn.execute("""
            SELECT COALESCE(SUM(total), 0) as ingresos_pedidos, COUNT(*) as count_pedidos
            FROM pedidos
            WHERE estado != 'Cancelado'
        """).fetchone()
        
        row_ventas = conn.execute("""
            SELECT COALESCE(SUM(total), 0) as ingresos_ventas, COUNT(*) as count_ventas
            FROM ventas
        """).fetchone()
        
        ingresos = float(row_pedidos['ingresos_pedidos']) + float(row_ventas['ingresos_ventas'])
        total_ventas = int(row_pedidos['count_pedidos']) + int(row_ventas['count_ventas'])
        productos = conn.execute("SELECT COUNT(*) FROM productos").fetchone()[0]
        return jsonify({
            'ok': True,
            'ingresos': ingresos,
            'total_ventas': total_ventas,
            'productos': productos,
            'pedidos_count': int(row_pedidos['count_pedidos']),
            'ventas_historicas_count': int(row_ventas['count_ventas'])
        })
    finally:
        conn.close()

@app.route('/api/workers', methods=['GET'])
@role_required('admin')
def get_workers():
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM usuarios WHERE rol='worker' ORDER BY id DESC").fetchall()
        return jsonify({'ok': True, 'workers': [_ensure_worker_public_uuid(conn, r) for r in rows]})
    finally:
        conn.close()

@app.route('/api/workers', methods=['POST'])
@role_required('admin')
def create_worker():
    data = request.json or {}
    nombre = data.get('nombre', '').strip()
    dni = data.get('dni', '').strip()
    cargo = data.get('cargo', '').strip()
    area = data.get('area', '').strip()
    fecha_ingreso = data.get('fecha_ingreso', '')
    telefono = data.get('telefono', '').strip()
    direccion = data.get('direccion', '').strip()
    email = data.get('email', '').strip()
    estado = data.get('estado', 'Activo')
    foto = data.get('foto', '')
    
    import random
    import string
    username = nombre.split(' ')[0].lower() + str(random.randint(100,999)) if nombre else 'user' + str(random.randint(1000,9999))
    password = dni if dni else ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    pw_hash = generate_password_hash(password)
    public_uuid = str(uuid.uuid4())
    
    conn = get_db()
    try:
        cur = conn.execute('''
            INSERT INTO usuarios (username, password, nombre, dni, cargo, area, fecha_ingreso, telefono, direccion, email, estado, foto, rol, public_uuid)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'worker', %s) RETURNING id
        ''', (username, pw_hash, nombre, dni, cargo, area, fecha_ingreso, telefono, direccion, email, estado, foto, public_uuid))
        new_id = cur.fetchone()['id']
        conn.commit()
        worker = conn.execute("SELECT * FROM usuarios WHERE id = %s", (new_id,)).fetchone()
        return jsonify({
            'ok': True,
            'generated_username': username,
            'generated_password': password,
            'worker': _get_user_data(worker)
        }), 201
    except Exception as e:
        conn.rollback()
        print('Error create worker:', e)
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()

@app.route('/api/worker/me', methods=['GET'])
@role_required('admin', 'worker')
def get_my_worker_profile():
    user_id = session.get('user_id')
    conn = get_db()
    try:
        row = conn.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,)).fetchone()
        if not row:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        return jsonify({'ok': True, 'worker': _ensure_worker_public_uuid(conn, row)})
    finally:
        conn.close()

@app.route('/api/workers/<int:worker_id>', methods=['GET'])
@role_required('admin', 'worker')
def get_worker_by_id(worker_id):
    if session.get('rol') == 'worker' and session.get('user_id') != worker_id:
        return jsonify({'error': 'Acceso denegado: permisos insuficientes'}), 403
    conn = get_db()
    try:
        worker = conn.execute("SELECT * FROM usuarios WHERE id = %s AND rol='worker'", (worker_id,)).fetchone()
        if worker:
            return jsonify({'ok': True, 'worker': _ensure_worker_public_uuid(conn, worker)})
        return jsonify({'error': 'Trabajador no encontrado'}), 404
    finally:
        conn.close()

@app.route('/api/workers/<int:worker_id>', methods=['PUT'])
@role_required('admin')
def update_worker(worker_id):
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
@role_required('admin')
def get_workers_count():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM usuarios WHERE rol='worker'").fetchone()[0]
    activos = conn.execute("SELECT COUNT(*) FROM usuarios WHERE rol='worker' AND estado='Activo'").fetchone()[0]
    conn.close()
    return jsonify({'ok': True, 'total': total, 'activos': activos})

@app.route('/api/ventas', methods=['POST'])
@login_required
def create_venta():
    data = request.json or {}
    conn = get_db()
    try:
        pid = data['producto_id']
        qty = int(data.get('cantidad', 1))
        row = conn.execute("SELECT precio, stock FROM productos WHERE id = %s", (pid,)).fetchone()
        if not row: return jsonify({'error': 'Producto no encontrado'}), 404
        if row['stock'] < qty: return jsonify({'error': 'Stock insuficiente'}), 400
        total = row['precio'] * qty
        conn.execute("INSERT INTO ventas (producto_id, cantidad, total) VALUES (%s, %s, %s)", (pid, qty, total))
        conn.execute("UPDATE productos SET stock = stock - %s WHERE id = %s", (qty, pid))
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
            user = conn.execute("SELECT id FROM usuarios WHERE email = %s", (email,)).fetchone()
            if not user:
                return jsonify({'error': 'No existe una cuenta con este correo electrónico'}), 400
            
            pw_hash = generate_password_hash(new_password)
            conn.execute("UPDATE usuarios SET password = %s WHERE email = %s", (pw_hash, email))
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
@role_required('admin')
def create_producto():
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

@app.route('/api/productos/<int:pid>', methods=['GET'])
def get_producto(pid):
    conn = get_db()
    row = conn.execute("SELECT * FROM productos WHERE id=?", (pid,)).fetchone()
    conn.close()
    if row:
        return jsonify({'ok': True, 'producto': dict(row)})
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/productos/<int:pid>', methods=['PUT', 'DELETE'])
@role_required('admin')
def manage_producto(pid):
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
