from pydantic import BaseModel
from typing import Optional


class ProductoCreate(BaseModel):
    nombre: str
    descripcion: str = ''
    precio: float
    categoria: str = ''
    imagen: str = ''
    stock: int = 0
    destacado: int = 0


class ProductoUpdate(BaseModel):
    nombre: str
    descripcion: str = ''
    precio: float
    categoria: str = ''
    imagen: str = ''
    stock: int = 0
    destacado: int = 0


class WorkerCreate(BaseModel):
    nombre: str
    dni: str
    cargo: str = ''
    area: str = ''
    sueldo: float = 0
    fecha_ingreso: str = ''
    telefono: str = ''
    direccion: str = ''
    email: str = ''
    estado: str = 'Activo'
    foto: str = ''


class WorkerUpdate(BaseModel):
    nombre: str
    dni: str
    cargo: str = ''
    area: str = ''
    sueldo: float = 0
    fecha_ingreso: str = ''
    telefono: str = ''
    direccion: str = ''
    email: str = ''
    estado: str = 'Activo'
    foto: str = ''
