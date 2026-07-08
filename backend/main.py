import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import init_db
from .routers import productos, workers

app = FastAPI(title='4M Nature API', version='2.0.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(productos.router)
app.include_router(workers.router)

frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist')
if os.path.isdir(frontend_dir):
    app.mount('/', StaticFiles(directory=frontend_dir, html=True), name='frontend')


@app.on_event('startup')
def startup():
    init_db()
