-- ============================================================
-- Reset — vacía las tablas y reinicia secuencias
-- ============================================================
-- Ejecutar cuando los datos se ensucien o se dupliquen.
-- Después correr 01_create_tables.sql para repoblar.
-- ============================================================

-- Vaciar en orden (primero las tablas con foreign keys)
DELETE FROM ventas;
DELETE FROM productos;
DELETE FROM clientes;

-- Reiniciar contadores SERIAL
ALTER SEQUENCE clientes_id_seq  RESTART WITH 1;
ALTER SEQUENCE productos_id_seq RESTART WITH 1;
ALTER SEQUENCE ventas_id_seq    RESTART WITH 1;

-- Verificación
SELECT COUNT(*) FROM clientes;   -- esperado: 0
SELECT COUNT(*) FROM productos;  -- esperado: 0
SELECT COUNT(*) FROM ventas;     -- esperado: 0
