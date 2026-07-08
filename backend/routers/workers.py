import re
import hashlib
from fastapi import APIRouter, HTTPException
from ..database import get_db, SECRET
from ..models import WorkerCreate, WorkerUpdate
from typing import Optional
from datetime import datetime

router = APIRouter(prefix='/api/workers', tags=['trabajadores'])


def _next_username(conn):
    cur = conn.execute("SELECT username FROM usuarios WHERE username LIKE 'U%' ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    if row:
        m = re.search(r'U(\d+)', row['username'])
        if m:
            return f"U{int(m.group(1)) + 1:04d}"
    return "U0001"


def _user_data(row):
    return {
        'id': row['id'],
        'username': row['username'],
        'nombre': row['nombre'],
        'dni': row['dni'],
        'cargo': row['cargo'],
        'area': row['area'],
        'sueldo': row['sueldo'],
        'fecha_ingreso': row['fecha_ingreso'],
        'telefono': row['telefono'],
        'direccion': row['direccion'],
        'email': row['email'],
        'estado': row['estado'],
        'rol': row['rol'],
        'foto': row['foto'],
        'fecha_registro': row['fecha_registro']
    }


@router.get('')
def listar_workers(search: Optional[str] = None):
    conn = get_db()
    if search:
        rows = conn.execute(
            "SELECT * FROM usuarios WHERE rol='worker' AND (nombre LIKE ? OR dni LIKE ? OR cargo LIKE ? OR username LIKE ?) ORDER BY id DESC",
            (f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%')
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM usuarios WHERE rol='worker' ORDER BY id DESC").fetchall()
    conn.close()
    return {'ok': True, 'workers': [_user_data(r) for r in rows]}


@router.get('/count')
def worker_count():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM usuarios WHERE rol='worker'").fetchone()[0]
    activos = conn.execute("SELECT COUNT(*) FROM usuarios WHERE rol='worker' AND estado='Activo'").fetchone()[0]
    conn.close()
    return {'ok': True, 'total': total, 'activos': activos}


@router.get('/{worker_id}')
def obtener_worker(worker_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM usuarios WHERE id=? AND rol='worker'", (worker_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, {'error': 'No encontrado'})
    return {'ok': True, 'worker': _user_data(row)}


@router.post('', status_code=201)
def crear_worker(body: WorkerCreate):
    conn = get_db()
    try:
        uname = _next_username(conn)
        pw = hashlib.sha256(f'{body.dni}{SECRET}'.encode()).hexdigest()
        cur = conn.execute(
            "INSERT INTO usuarios (username, password, nombre, dni, cargo, area, sueldo, fecha_ingreso, telefono, direccion, email, estado, foto, rol) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,'worker')",
            (uname, pw, body.nombre, body.dni, body.cargo, body.area,
             body.sueldo, body.fecha_ingreso or datetime.now().strftime('%Y-%m-%d'),
             body.telefono, body.direccion, body.email, body.estado, body.foto)
        )
        conn.commit()
        row = conn.execute("SELECT * FROM usuarios WHERE id=?", (cur.lastrowid,)).fetchone()
        conn.close()
        return {
            'ok': True,
            'worker': _user_data(row),
            'generated_username': uname,
            'generated_password': body.dni
        }
    except Exception as e:
        conn.close()
        if 'UNIQUE' in str(e):
            raise HTTPException(400, {'error': 'El DNI ya existe'})
        raise HTTPException(400, {'error': str(e)})


@router.put('/{worker_id}')
def actualizar_worker(worker_id: int, body: WorkerUpdate):
    conn = get_db()
    try:
        conn.execute(
            "UPDATE usuarios SET nombre=?, dni=?, cargo=?, area=?, sueldo=?, fecha_ingreso=?, telefono=?, direccion=?, email=?, estado=?, foto=? WHERE id=? AND rol='worker'",
            (body.nombre, body.dni, body.cargo, body.area, body.sueldo,
             body.fecha_ingreso, body.telefono, body.direccion,
             body.email, body.estado, body.foto, worker_id)
        )
        if body.dni:
            new_pw = hashlib.sha256(f'{body.dni}{SECRET}'.encode()).hexdigest()
            conn.execute("UPDATE usuarios SET password=? WHERE id=? AND rol='worker'", (new_pw, worker_id))
        conn.commit()
        row = conn.execute("SELECT * FROM usuarios WHERE id=? AND rol='worker'", (worker_id,)).fetchone()
        conn.close()
        if not row:
            raise HTTPException(404, {'error': 'No encontrado'})
        return {'ok': True, 'worker': _user_data(row)}
    except Exception as e:
        conn.close()
        raise HTTPException(400, {'error': str(e)})


@router.delete('/{worker_id}')
def eliminar_worker(worker_id: int):
    conn = get_db()
    conn.execute("DELETE FROM usuarios WHERE id=? AND rol='worker'", (worker_id,))
    conn.commit()
    conn.close()
    return {'ok': True}
