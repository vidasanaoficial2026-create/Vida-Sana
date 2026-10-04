-- Fase 2
-- Crear tabla de favoritos
-- Ejecutada originalmente: 2026-10-04

CREATE TABLE IF NOT EXISTS public.favoritos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,
    fecha TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() - '05:00:00'::interval),

    CONSTRAINT favoritos_usuario_id_fkey 
        FOREIGN KEY (usuario_id) 
        REFERENCES public.usuarios(id) 
        ON DELETE CASCADE,

    CONSTRAINT favoritos_producto_id_fkey 
        FOREIGN KEY (producto_id) 
        REFERENCES public.productos(id) 
        ON DELETE CASCADE,

    CONSTRAINT uq_favorito_usuario_producto 
        UNIQUE (usuario_id, producto_id)
);

CREATE INDEX IF NOT EXISTS idx_favoritos_usuario 
    ON public.favoritos USING btree (usuario_id);

CREATE INDEX IF NOT EXISTS idx_favoritos_producto 
    ON public.favoritos USING btree (producto_id);
