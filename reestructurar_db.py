import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

db_url = os.getenv('DATABASE_URL')
conn = psycopg2.connect(db_url)
cur = conn.cursor()

try:
    # 1. Modificar tabla usuarios para permitir el rol 'cliente'
    cur.execute('ALTER TABLE usuarios DROP CONSTRAINT IF EXISTS usuarios_rol_check;')
    cur.execute("ALTER TABLE usuarios ADD CONSTRAINT usuarios_rol_check CHECK(rol IN ('admin','worker','cliente'));")

    # 2. Eliminar la tabla ventas (ya que estaba vacia y se va a reemplazar)
    cur.execute('DROP TABLE IF EXISTS ventas;')

    # 3. Crear tabla pedidos
    cur.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
            estado TEXT DEFAULT 'Pendiente' CHECK(estado IN ('Pendiente','Pagado','Enviado','Cancelado')),
            total REAL NOT NULL,
            fecha TIMESTAMP DEFAULT (NOW() - INTERVAL '5 hours')
        );
    ''')

    # 4. Crear tabla detalles_pedido
    cur.execute('''
        CREATE TABLE IF NOT EXISTS detalles_pedido (
            id SERIAL PRIMARY KEY,
            pedido_id INTEGER NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
            producto_id INTEGER NOT NULL REFERENCES productos(id),
            cantidad INTEGER NOT NULL,
            precio_unitario REAL NOT NULL
        );
    ''')

    # 5. Crear tabla carrito
    cur.execute('''
        CREATE TABLE IF NOT EXISTS carrito (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
            producto_id INTEGER NOT NULL REFERENCES productos(id) ON DELETE CASCADE,
            cantidad INTEGER NOT NULL,
            UNIQUE(usuario_id, producto_id)
        );
    ''')

    conn.commit()
    print('Base de datos reestructurada con exito!')
except Exception as e:
    conn.rollback()
    print(f'Error: {e}')
finally:
    conn.close()

