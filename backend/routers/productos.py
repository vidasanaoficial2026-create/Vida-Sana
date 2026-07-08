from fastapi import APIRouter, HTTPException
from ..database import get_db
from ..models import ProductoCreate, ProductoUpdate
from typing import Optional

router = APIRouter(prefix='/api/productos', tags=['productos'])


@router.get('')
def listar_productos(categoria: Optional[str] = None, q: Optional[str] = None):
    conn = get_db()
    sql = "SELECT * FROM productos WHERE 1=1"
    params = []
    if categoria:
        sql += " AND categoria=?"
        params.append(categoria)
    if q:
        sql += " AND (nombre LIKE ? OR descripcion LIKE ? OR categoria LIKE ?)"
        params.extend([f'%{q}%', f'%{q}%', f'%{q}%'])
    sql += " ORDER BY destacado DESC, id DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return {'ok': True, 'productos': [dict(r) for r in rows]}


@router.get('/{producto_id}')
def obtener_producto(producto_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM productos WHERE id=?", (producto_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, {'error': 'No encontrado'})
    return {'ok': True, 'producto': dict(row)}


@router.post('', status_code=201)
def crear_producto(body: ProductoCreate):
    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO productos (nombre, descripcion, precio, categoria, imagen, stock, destacado) VALUES (?,?,?,?,?,?,?)",
            (body.nombre, body.descripcion, body.precio, body.categoria, body.imagen, body.stock, body.destacado)
        )
        conn.commit()
        row = conn.execute("SELECT * FROM productos WHERE id=?", (cur.lastrowid,)).fetchone()
        conn.close()
        return {'ok': True, 'producto': dict(row)}
    except Exception as e:
        conn.close()
        raise HTTPException(400, {'error': str(e)})


@router.put('/{producto_id}')
def actualizar_producto(producto_id: int, body: ProductoUpdate):
    conn = get_db()
    try:
        conn.execute(
            "UPDATE productos SET nombre=?, descripcion=?, precio=?, categoria=?, imagen=?, stock=?, destacado=? WHERE id=?",
            (body.nombre, body.descripcion, body.precio, body.categoria, body.imagen, body.stock, body.destacado, producto_id)
        )
        conn.commit()
        row = conn.execute("SELECT * FROM productos WHERE id=?", (producto_id,)).fetchone()
        conn.close()
        if not row:
            raise HTTPException(404, {'error': 'No encontrado'})
        return {'ok': True, 'producto': dict(row)}
    except Exception as e:
        conn.close()
        raise HTTPException(400, {'error': str(e)})


@router.delete('/{producto_id}')
def eliminar_producto(producto_id: int):
    conn = get_db()
    conn.execute("DELETE FROM productos WHERE id=?", (producto_id,))
    conn.commit()
    conn.close()
    return {'ok': True}
