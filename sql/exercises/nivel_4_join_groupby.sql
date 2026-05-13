Ejercicio 1. ¿Cuál fue el monto promedio facturado por venta en cada categoría de producto? 
Trae categoría y el promedio. Ordena descendente.

Recuerda: facturado por venta = cantidad × precio. 
Promedio sobre eso = AVG(v.cantidad * p.precio). Puedes redondear con ROUND(..., 2).

Ejercicio 2. ¿Cuántos productos distintos ha comprado cada cliente? 
Incluye a los que han comprado 0. Ordena descendente.

Pista: te puede servir COUNT(DISTINCT v.producto_id). 
DISTINCT adentro de COUNT cuenta sin repetir.

Ejercicio 3. ¿Cuál es la fecha de la última compra de cada cliente que sí compró? 
Trae nombre y fecha.

Las funciones de agregación funcionan con fechas: MAX(v.fecha_venta) te da la fecha más reciente. 
Acá sí INNER JOIN porque solo quieres los que compraron.

Ejercicio 4. ¿Qué categorías han comprado los clientes mayores de 40 años? 
Trae categoría y unidades totales vendidas a ese grupo etario. Ordena descendente.

Necesitas las 3 tablas. El filtro c.edad > 40 va en WHERE, antes del GROUP BY.

Ejercicio 5 (el más difícil). 
¿Cuál es el cliente que más ha facturado en la categoría 'Electrónica'? 
Trae nombre y total facturado. Solo el top 1.

Combo completo: 3 tablas, WHERE p.categoria = 'Electrónica', 
GROUP BY cliente, ORDER BY facturado DESC, LIMIT 1.

SELECT 
	p.categoria,
	ROUND(AVG(v.cantidad * p.precio),2) AS promedio_venta
FROM productos AS p 
INNER JOIN ventas AS v ON P.id = v.producto_id 
GROUP BY categoria

SELECT 
	c.nombre,
	COUNT(DISTINCT v.producto_id) AS Products_purchased
FROM clientes AS c
LEFT JOIN ventas AS v ON v.cliente_id = c.id 
GROUP BY nombre 
ORDER BY Products_purchased DESC; 

SELECT 
	c.nombre,
	MAX(v.fecha_venta) AS ultima_compra
FROM clientes AS c 
INNER JOIN ventas AS v ON v.cliente_id = c.id 
GROUP BY nombre
ORDER BY ultima_compra DESC;

SELECT 
	p.categoria,
	SUM(v.cantidad) AS Comprados
FROM productos AS p
INNER JOIN ventas AS v ON p.id = v.producto_id
INNER JOIN clientes  AS c ON v.cliente_id = c.id
WHERE c.edad > 40 
GROUP BY p.categoria
ORDER BY Comprados DESC;

SELECT 
	c.nombre,
	SUM(v.cantidad * p.precio) AS mejor_cliente
FROM clientes AS c
INNER JOIN ventas AS v ON c.id = v.cliente_id
INNER JOIN productos AS p ON v.producto_id = p.id
WHERE unaccent(p.categoria) ILIKE 'electronica'
GROUP BY c.nombre 
ORDER BY mejor_cliente DESC LIMIT 1;