-- ============================================================
-- Nivel 0 — Filtros básicos: WHERE, ORDER BY, LIMIT
-- ============================================================
-- Fecha: 2026-05-08
-- Tablas: clientes, productos, ventas
-- ============================================================

-- ------------------------------------------------------------
-- Ejercicio 1: clientes con edad mayor a 35, ordenados de mayor a menor.
-- ------------------------------------------------------------
SELECT nombre, edad
FROM clientes
WHERE edad > 35
ORDER BY edad DESC;

-- ------------------------------------------------------------
-- Ejercicio 2: top 5 productos más caros.
-- ------------------------------------------------------------
SELECT nombre, precio
FROM productos
ORDER BY precio DESC
LIMIT 5;

-- ------------------------------------------------------------
-- Ejercicio 3: ventas con cantidad exactamente 2,
-- ordenadas de la fecha más reciente a la más antigua.
-- ------------------------------------------------------------
SELECT cantidad, fecha_venta
FROM ventas
WHERE cantidad = 2
ORDER BY fecha_venta DESC;
