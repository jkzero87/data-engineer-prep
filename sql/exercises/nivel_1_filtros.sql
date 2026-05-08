-- ============================================================
-- Nivel 1 — Operadores de filtrado: BETWEEN, IN, LIKE, IS NULL
-- ============================================================
-- Tablas: clientes, productos, ventas
-- Fecha: 2026-05-08
-- ============================================================

Ejercicio 1
Lista nombre y edad de los clientes con edad entre 30 y 45 (inclusive). Ordena por edad ascendente.
Ejercicio 2
Lista nombre y categoría de los productos cuya categoría sea 'Electrónica' o 'Hogar'. Usa IN.
Ejercicio 3
Lista nombre de todos los clientes cuyo nombre empiece por la letra 'C' (mayúscula o minúscula — usa ILIKE).
Ejercicio 4
Lista nombre y precio de los productos cuyo nombre contenga la palabra 'Laptop' en cualquier parte.
Ejercicio 5
Lista todas las ventas hechas entre el 15 de abril y el 30 de abril de 2026 (inclusive), ordenadas por fecha ascendente. Muestra id, cliente_id, producto_id, cantidad, fecha_venta.

SELECT nombre, edad FROM clientes 
WHERE edad BETWEEN 30 AND 45 
ORDER BY edad ASC; 

SELECT nombre, categoria FROM productos 
WHERE unaccent(categoria) IN (unaccent('Electronica'), unaccent('Hogar'));


SELECT nombre FROM clientes
WHERE nombre ILIKE 'C%';

SELECT nombre, precio FROM productos 
WHERE nombre ILIKE '%laptop%';

SELECT * FROM ventas  
WHERE fecha_venta BETWEEN '2026-04-15' AND '2026-04-30'
ORDER BY fecha_venta ASC; 