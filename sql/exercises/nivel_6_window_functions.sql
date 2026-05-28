-- nivel_6_window_functions.sql
-- Phase 6 practice — window functions on the practica schema
-- Run order: SET search_path first, then each exercise.

SET search_path TO practica;

-- Exercise 1 — empty OVER(): global average plays on every row

select * from artistas;

select * from canciones;

SELECT
	titulo,
	reproducciones,
	AVG(reproducciones) OVER () AS promedio_global
FROM canciones;

SELECT
	titulo,
	genero,
	reproducciones,
	AVG(reproducciones) OVER (PARTITION BY genero) AS promedio_global
FROM canciones;

SELECT 
	titulo,
	fecha_lanzamiento,
	reproducciones,
	SUM(reproducciones) OVER (ORDER BY fecha_lanzamiento) AS acumulado
FROM canciones; 

SELECT
	genero,
	titulo,
	reproducciones,
	ROW_NUMBER() OVER (PARTITION BY genero ORDER BY reproducciones DESC) AS posicion
FROM canciones;

WITH ranked AS (
    SELECT
        titulo,
        genero,
        reproducciones,
        ROW_NUMBER() OVER (PARTITION BY genero ORDER BY reproducciones DESC) AS rn
    FROM canciones
)
SELECT titulo, genero, reproducciones
FROM ranked
WHERE rn <= 3;



