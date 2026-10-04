-- Fase 1
-- Agregar public_uuid para anonimización y QR público de trabajadores
-- Ejecutada originalmente: 2026-10-04

ALTER TABLE usuarios 
ADD COLUMN IF NOT EXISTS public_uuid VARCHAR(64) UNIQUE;
