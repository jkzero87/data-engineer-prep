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