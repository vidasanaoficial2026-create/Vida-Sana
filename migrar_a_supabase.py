import sqlite3
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Conectar a Supabase
# Se asume que DATABASE_URL está en el .env con la contraseña correcta
db_url = os.getenv('DATABASE_URL')
if not db_url or '[YOUR-PASSWORD]' in db_url:
    print("ERROR: DATABASE_URL no está configurada correctamente en el .env.")
    exit(1)

try:
    pg_conn = psycopg2.connect(db_url)
    pg_cur = pg_conn.cursor()
    
    print("Conectado a Supabase correctamente.")

    # 1. Crear tablas en Supabase
    pg_cur.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
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
            fecha_registro TIMESTAMP DEFAULT (NOW() - INTERVAL '5 hours')
        );
        CREATE TABLE IF NOT EXISTS productos (
            id SERIAL PRIMARY KEY,
            nombre TEXT NOT NULL,
            descripcion TEXT DEFAULT '',
            precio REAL NOT NULL,
            categoria TEXT DEFAULT '',
            imagen TEXT DEFAULT '',
            stock INTEGER DEFAULT 0,
            destacado INTEGER DEFAULT 0,
            fecha_registro TIMESTAMP DEFAULT (NOW() - INTERVAL '5 hours')
        );
        CREATE TABLE IF NOT EXISTS ventas (
            id SERIAL PRIMARY KEY,
            producto_id INTEGER NOT NULL REFERENCES productos(id),
            cantidad INTEGER NOT NULL,
            total REAL NOT NULL,
            fecha TIMESTAMP DEFAULT (NOW() - INTERVAL '5 hours')
        );
        CREATE TABLE IF NOT EXISTS landing_config (
            clave TEXT PRIMARY KEY,
            valor TEXT NOT NULL
        );
    ''')
    pg_conn.commit()
    print("Tablas creadas en Supabase.")

    # 2. Conectar a SQLite
    sqlite_db_path = os.path.join(os.path.dirname(__file__), 'natura.db')
    if os.path.exists(sqlite_db_path):
        sqlite_conn = sqlite3.connect(sqlite_db_path)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cur = sqlite_conn.cursor()

        # Migrar usuarios
        usuarios = sqlite_cur.execute("SELECT * FROM usuarios").fetchall()
        for u in usuarios:
            pg_cur.execute(
                "INSERT INTO usuarios (id, username, password, nombre, dni, cargo, area, sueldo, fecha_ingreso, telefono, direccion, email, estado, rol, foto, fecha_registro) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
                (u['id'], u['username'], u['password'], u['nombre'], u['dni'], u['cargo'], u['area'], u['sueldo'], u['fecha_ingreso'], u['telefono'], u['direccion'], u['email'], u['estado'], u['rol'], u['foto'], u['fecha_registro'])
            )
        
        # Migrar productos
        productos = sqlite_cur.execute("SELECT * FROM productos").fetchall()
        for p in productos:
            pg_cur.execute(
                "INSERT INTO productos (id, nombre, descripcion, precio, categoria, imagen, stock, destacado, fecha_registro) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
                (p['id'], p['nombre'], p['descripcion'], p['precio'], p['categoria'], p['imagen'], p['stock'], p['destacado'], p['fecha_registro'])
            )

        # Migrar ventas
        ventas = sqlite_cur.execute("SELECT * FROM ventas").fetchall()
        for v in ventas:
            pg_cur.execute(
                "INSERT INTO ventas (id, producto_id, cantidad, total, fecha) "
                "VALUES (%s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
                (v['id'], v['producto_id'], v['cantidad'], v['total'], v['fecha'])
            )

        # Migrar landing_config
        try:
            config = sqlite_cur.execute("SELECT * FROM landing_config").fetchall()
            for c in config:
                pg_cur.execute(
                    "INSERT INTO landing_config (clave, valor) VALUES (%s, %s) ON CONFLICT (clave) DO UPDATE SET valor = EXCLUDED.valor",
                    (c['clave'], c['valor'])
                )
        except sqlite3.OperationalError:
            pass # Si no existe en sqlite, no pasa nada

        # Reset sequences para que los nuevos IDs funcionen bien
        pg_cur.execute("SELECT setval('usuarios_id_seq', (SELECT MAX(id) FROM usuarios));")
        pg_cur.execute("SELECT setval('productos_id_seq', (SELECT MAX(id) FROM productos));")
        pg_cur.execute("SELECT setval('ventas_id_seq', (SELECT MAX(id) FROM ventas));")
        
        pg_conn.commit()
        sqlite_conn.close()
        print(f"Migración completada: {len(usuarios)} usuarios, {len(productos)} productos, {len(ventas)} ventas.")
    else:
        print("No se encontró base de datos SQLite. Supabase ha sido inicializado en blanco.")

except Exception as e:
    print(f"Ocurrió un error en la migración: {e}")
finally:
    if 'pg_conn' in locals():
        pg_conn.close()
