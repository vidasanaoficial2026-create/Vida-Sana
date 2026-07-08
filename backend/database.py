import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'natura.db')
SECRET = 'natura-admin-secret-2026'


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_db()
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
    ''')
    try:
        conn.execute("ALTER TABLE usuarios ADD COLUMN foto TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    cur = conn.execute("SELECT id FROM usuarios WHERE username='admin'")
    if not cur.fetchone():
        pw = hashlib.sha256(f'admin123{SECRET}'.encode()).hexdigest()
        conn.execute(
            "INSERT INTO usuarios (username, password, nombre, rol) VALUES (?, ?, ?, 'admin')",
            ('admin', pw, 'Administrador')
        )
    conn.executescript('''
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
    ''')
    cur = conn.execute("SELECT COUNT(*) FROM productos")
    if cur.fetchone()[0] == 0:
        sample = [
            ('STEM CELL', 'Cápsulas naturales para fortalecer el sistema inmunológico', 18, 'Capsulas',
             'https://naturasanaperu.com/wp-content/uploads/2023/06/1.png', 50, 1),
            ('T-OSITO', 'Bebida reconfortante 700ml a base de hierbas naturales', 21, 'Bebidas',
             'https://naturasanaperu.com/wp-content/uploads/2023/06/3-2.png', 30, 1),
            ('COLAGENO H.', 'Colágeno hidrolizado bebida 500ml para piel y articulaciones', 18, 'Bebidas',
             'https://naturasanaperu.com/wp-content/uploads/2023/06/6-2.png', 40, 1),
            ('PROPOLEO', 'Propóleo bebida 1.2L, refuerzo natural para defensas', 25, 'Bebidas',
             'https://naturasanaperu.com/wp-content/uploads/2023/06/2-2.png', 25, 1),
            ('WOMEN PROT', 'Proteína vegetal x 500gr para mujer', 28, 'Harinas',
             'https://naturasanaperu.com/wp-content/uploads/2023/06/4-2.png', 20, 1),
            ('PRO MAX', 'Bebida energética 500ml con proteínas y vitaminas', 18, 'Bebidas',
             'https://naturasanaperu.com/wp-content/uploads/2023/06/5-2.png', 35, 0),
            ('ALOE VERA', 'Jugo de Aloe Vera 1L, depurativo natural', 22, 'Bebidas', '', 30, 0),
            ('MACA NEGRA', 'Cápsulas de Maca Negra x 60, energía natural', 15, 'Capsulas', '', 45, 0),
            ('QUINUA ORGÁNICA', 'Harina de Quinua Orgánica x 1kg', 12, 'Harinas', '', 50, 0),
            ('TÉ VERDE', 'Té Verde en hojas x 100g, antioxidante natural', 10, 'Harinas', '', 60, 0),
        ]
        conn.executemany(
            "INSERT INTO productos (nombre, descripcion, precio, categoria, imagen, stock, destacado) VALUES (?,?,?,?,?,?,?)",
            sample
        )
    conn.commit()
    conn.close()
