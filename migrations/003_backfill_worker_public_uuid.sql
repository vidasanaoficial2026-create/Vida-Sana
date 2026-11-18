-- Backfill public_uuid for existing workers that do not have one yet
ALTER TABLE usuarios
ADD COLUMN IF NOT EXISTS public_uuid VARCHAR(64) UNIQUE;

UPDATE usuarios
SET public_uuid = gen_random_uuid()::text
WHERE rol = 'worker'
  AND (public_uuid IS NULL OR public_uuid = '');
