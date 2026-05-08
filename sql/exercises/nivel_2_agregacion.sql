Ejercicios — Nivel 2
8 ejercicios, de menor a mayor dificultad. Cada uno construye sobre el anterior. Crea un archivo sql/exercises/nivel_2_agregacion.sql con la cabecera de costumbre y agrega cada ejercicio dentro.
Ejercicio 1 — agregación simple, sin GROUP BY
¿Cuántos clientes tienes en total? Devuelve una sola fila con la columna total_clientes.
Ejercicio 2 — múltiples agregaciones a la vez
Con un solo SELECT, devuelve estas tres columnas: precio_minimo, precio_maximo, precio_promedio para todos los productos.
Ejercicio 3 — agregación con WHERE
¿Cuál es el precio promedio de los productos de la categoría 'Electrónica'? (Usa unaccent si quieres ser robusto a tildes, pero no es obligatorio en este ejercicio.)
Ejercicio 4 — primer GROUP BY
¿Cuántos productos hay en cada categoría? Devuelve categoria y total_productos. Ordena de mayor a menor cantidad.
Ejercicio 5 — GROUP BY + agregación numérica
Por cada categoría, muestra el precio_promedio y el precio_maximo. Ordena por precio promedio descendente.
Ejercicio 6 — GROUP BY sobre la tabla ventas
¿Cuántas unidades en total se han vendido por cada producto_id? Devuelve producto_id y total_unidades_vendidas. Ordena de mayor a menor.
Ejercicio 7 — HAVING
Muestra las categorías que tengan más de 2 productos. Devuelve categoria y total_productos.
Ejercicio 8 — combinación completa
De los productos con precio mayor a 100.000, agrupa por categoría y muestra:

categoria
total_productos (cuántos productos cumplen)
precio_promedio

Filtra para mostrar solo las categorías con más de 1 producto. Ordena por precio_promedio descendente.

SELECT COUNT (*) AS total_clientes  
FROM clientes;

SELECT MIN(precio) AS precio_minimo, 
MAX(precio) AS precio_maximo, 
AVG(precio) AS precio_promedio 
FROM productos;

SELECT categoria, AVG (precio) AS precio_promedio
FROM productos 
WHERE unaccent(categoria) ILIKE unaccent('electronica') 
GROUP BY categoria;


SELECT categoria,COUNT(*) AS total_productos 
FROM productos 
GROUP BY categoria 
ORDER BY total_productos DESC;

SELECT categoria,COUNT(categoria) AS total_productos, MAX(precio) AS precio_maximo, ROUND(AVG(precio), 0) AS precio_promedio
FROM productos 
GROUP BY categoria 
ORDER BY precio_promedio DESC;

SELECT producto_id, SUM(cantidad) AS total_unidades_vendidas
FROM ventas 
GROUP BY producto_id 
ORDER BY TOTAL_UNIDADES_VENDIDAS DESC;

SELECT categoria,COUNT(categoria) AS total_productos 
FROM productos 
GROUP BY categoria 
HAVING COUNT(categoria) > 2
ORDER BY total_productos DESC;

SELECT categoria,
	COUNT(*) AS total_productos,
	ROUND(AVG(precio), 0) AS precio_promedio
FROM productos 
WHERE precio > 100000
GROUP BY categoria 
HAVING COUNT(*) > 1 
ORDER BY precio_promedio DESC;