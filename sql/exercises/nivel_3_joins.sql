Crea un archivo sql/exercises/nivel_3_joins.sql (acuérdate del orden de carpetas que dejamos) y resuelve uno por uno. Mándame queries + screenshot de resultados.
Ejercicio 1. Trae cada venta con el ID de la venta, el nombre del cliente y la cantidad. Solo dos tablas (ventas + clientes).
Ejercicio 2. Trae cada venta con: ID de venta, nombre del cliente, nombre del producto y cantidad. Las tres tablas, ordenado por ID de venta.
Ejercicio 3. Trae todas las ventas con el nombre del producto y la categoría, ordenadas por categoría. Sin información del cliente.
Ejercicio 4. ¿Qué clientes han comprado alguna vez "Laptop HP"? Trae solo el nombre del cliente y la fecha de la venta. (Pista: filtras por p.nombre = 'Laptop HP').
Ejercicio 5 (importante — el LEFT JOIN). Trae todos los clientes y, si compraron algo, la fecha y el ID de la venta. Los clientes que NUNCA han comprado deben aparecer también, con NULL en las columnas de venta. Ordena por nombre del cliente. (Pista: LEFT JOIN ventas...).



SELECT 
	v.id AS venta_id,
	c.nombre AS nombre_cliente, 
	v.cantidad AS cantidad
FROM ventas AS v
INNER JOIN clientes as c 
	ON v.cliente_id = c.id;

SELECT 
	v.id AS venta_id,
	c.nombre AS nombre_cliente, 
	v.cantidad AS cantidad,
	p.nombre AS producto
FROM ventas AS v
INNER JOIN clientes AS c 
	ON v.cliente_id = c.id
INNER JOIN productos AS p 
	ON v.producto_id = p.id
ORDER BY venta_id ASC;

SELECT 
	v.id AS venta_id,
	p.nombre AS producto,
	p.categoria AS categoria_producto
FROM ventas AS v
INNER JOIN productos AS p 
	ON v.producto_id = p.id
ORDER BY categoria ASC;

SELECT 
  c.nombre       AS cliente,
  v.fecha_venta AS fecha
FROM ventas AS v
INNER JOIN clientes  AS c ON v.cliente_id  = c.id
INNER JOIN productos AS p ON v.producto_id = p.id
WHERE p.nombre = 'Laptop HP';

SELECT 
	c.nombre, 
	v.id AS venta_id, 
	v.fecha_venta
FROM clientes AS c
LEFT JOIN ventas AS v ON c.id = v.cliente_id
ORDER BY c.nombre;

SELECT * FROM clientes

SELECT * FROM ventas

SELECT * FROM productos