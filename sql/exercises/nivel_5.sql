Exercise 1 — Subquery returning a single value
Find all sales where the quantity (cantidad) is greater than the average quantity
 across all sales.
Return: id, cliente_id, producto_id, cantidad.
Hint: the subquery returns one number. Use it with >.

Exercise 2 — Subquery returning a list (with IN)
Find the names of all products that have been sold at least once.
Return: nombre.
Hint: which producto_ids appear in ventas? Filter productos against that list.

Exercise 3 — Subquery returning a list (with NOT IN)
Find the names of all clients who have NEVER made a purchase.
Return: nombre.
Heads up: remember the NULL gotcha I mentioned — if ventas.cliente_id has any NULLs, 
NOT IN will silently return zero rows. Filter the NULLs out inside the subquery.

Exercise 4 — Subquery in WHERE with MAX
Find the product (or products) with the highest price.
Return: nombre, precio.
Hint: the subquery returns one number — the max price. Compare precio against it.

Exercise 5 — Subquery in FROM (a mini-table)
Calculate the average number of sales per client 
(only counting clients who actually appear in ventas).
Return: a single number.
Hint: you cant write AVG(COUNT(*)) directly. Step 1: count sales per client in an inner query. 
Step 2: average that result in the outer query. Dont forget to alias the subquery in FROM.

SELECT id, cliente_id, producto_id, cantidad
FROM ventas
WHERE cantidad > (SELECT AVG(cantidad) FROM ventas);

SELECT nombre
FROM productos 
WHERE id IN (SELECT producto_id FROM ventas)

SELECT nombre
FROM clientes
WHERE id NOT IN (SELECT cliente_id FROM ventas WHERE cliente_id IS NOT NULL);

SELECT 
	nombre,
	precio 
FROM productos 
WHERE precio = (SELECT MAX(precio)FROM productos);

SELECT ROUND(AVG(total_ventas),2) AS avg_ventas_por_cliente
FROM (
    SELECT cliente_id, COUNT(*) AS total_ventas
    FROM ventas
    GROUP BY cliente_id
) AS per_cust;

Schema: clientes (id, nombre, ciudad) · productos (id, nombre, categoria, precio)
· ventas (id, cliente_id, producto_id, cantidad, fecha)
1. Clients who made at least one purchase. Return nombre. 
CTE: clientes_con_ventas with distinct cliente_id from ventas.
2. Products priced above the average product price. 
Return nombre, precio. CTE: precio_promedio with the single average.
3. Clients whose total SUM(cantidad) is greater than 3. 
Return cliente_id, total_cantidad. CTE: total_por_cliente does the GROUP BY + SUM; 
main query filters with plain WHERE.
4. Total revenue per category, sorted desc.
 Return categoria, revenue. CTE: ventas_con_precio joins ventas + productos; 
 main query does GROUP BY categoria and sums cantidad * precio.
5. Clients whose total spending is above the average total spending across all clients. 
Return cliente_id, total_gastado. CTE: gasto_por_cliente; 
main query reads it twice (once for the list, 
once inside (SELECT AVG(...) FROM gasto_por_cliente)).

WITH precio_promedio AS (
    SELECT AVG(precio) AS avg_precio
    FROM productos
)
SELECT p.nombre, p.precio
FROM productos p, precio_promedio pp
WHERE p.precio > pp.avg_precio
ORDER BY p.precio DESC;



WITH total_por_cliente AS (
    SELECT 
        cliente_id,
        SUM(cantidad) AS total_cantidad
    FROM ventas
    GROUP BY cliente_id
)
SELECT cliente_id, total_cantidad
FROM total_por_cliente
WHERE total_cantidad > 3
ORDER BY total_cantidad DESC;
	

WITH ventas_con_precio AS (
    SELECT 
        p.categoria,
        v.cantidad,
        p.precio
    FROM ventas v
    INNER JOIN productos p
        ON v.producto_id = p.id
)
SELECT 
    categoria,
    SUM(cantidad * precio) AS revenue
FROM ventas_con_precio
GROUP BY categoria
ORDER BY revenue DESC;


WITH gasto_por_cliente AS (
    SELECT 
        v.cliente_id,
        SUM(v.cantidad * p.precio) AS total_gastado
    FROM ventas v
    INNER JOIN productos p
        ON v.producto_id = p.id
    GROUP BY v.cliente_id
)
SELECT 
    cliente_id,
    total_gastado
FROM gasto_por_cliente
WHERE total_gastado > (SELECT AVG(total_gastado) FROM gasto_por_cliente)
ORDER BY total_gastado DESC;

Set 3 — Chained CTEs (corrected)
Schema:

clientes (id, nombre, email, edad, fecha_registro)
productos (id, nombre, categoria, precio, stock)
ventas (id, cliente_id, producto_id, cantidad, fecha_venta)


Exercise 1 — Two-step pipeline
For each age group (< 30, 30-50, > 50), find the total revenue (cantidad * precio).
Return: grupo_edad, revenue, sorted desc by revenue.
Pipeline:

CTE 1: ventas_enriquecidas — join ventas + productos + clientes so each sale 
row has price and client age next to it.
Main query: use a CASE WHEN on edad to bucket clients, 
then GROUP BY that bucket and SUM(cantidad * precio).

The CASE WHEN syntax:
sqlCASE
    WHEN edad < 30 THEN 'menor_30'
    WHEN edad BETWEEN 30 AND 50 THEN '30_a_50'
    ELSE 'mayor_50'
END AS grupo_edad

Exercise 2 — Aggregate, then aggregate again
Average revenue per category. (Compute total revenue per category,
 then take the average of those totals.)
Return: a single number, avg_revenue_per_category.
Pipeline:

CTE 1: revenue_por_categoria — GROUP BY categoria, 
SUM(cantidad * precio) joining with productos. One row per category.
Main query: SELECT AVG(revenue) FROM revenue_por_categoria.

Same as before — you cant do AVG(SUM(...)) in one flat query.

Exercise 3 — Filter after aggregating, then aggregate again
Average spending of clients who spent more than the overall average.
Return: a single number, avg_top_spenders.
Pipeline:

CTE 1: gasto_por_cliente — one row per client with total_gastado.
CTE 2: top_spenders — filter gasto_por_cliente keeping only clients
 above the overall average (subquery against gasto_por_cliente itself for the threshold).
Main query: SELECT AVG(total_gastado) FROM top_spenders.


Exercise 4 — Top per group classic
For each category, which client spent the most?
Return: categoria, cliente_nombre, total_gastado, sorted by category.
Pipeline:

CTE 1: gasto_cliente_categoria — (cliente_id, nombre, categoria, total) 
— one row per (client, category).
CTE 2: max_por_categoria — (categoria, max_total) — one row per category.
Main query: JOIN both on categoria AND total = max_total to recover the name.


Exercise 5 — Three-step pipeline (replacement for the "best product per city")
For each category, find the single best-selling product (by units sold).
Return: categoria, producto_nombre, unidades_vendidas, sorted by category.
Pipeline:

CTE 1: ventas_por_categoria_producto — (categoria, producto_id, nombre, total_unidades) 
— units sold per (category, product). Join ventas + productos, grouped by category and product.
CTE 2: max_por_categoria — (categoria, max_unidades).
Main query: JOIN both on categoria AND total_unidades = max_unidades to recover the product name.


Same order as before: 1 and 2 first, then 3, then 4 and 5. Save under
 -- Set 3: Chained CTEs in nivel_5_subqueries_ctes.sql.

 WITH ventas_enriquecidas AS (
	SELECT  
		c.edad,
		v.cantidad,
		p.precio
	FROM clientes AS c 
	INNER JOIN ventas AS v ON c.id = v.cliente_id 
	INNER JOIN productos AS p ON v.producto_id = p.id 
)
SELECT 
	CASE 
		WHEN edad < 30 then 'menor_30'
		WHEN edad BETWEEN 30 AND 50 THEN '30_a_50'
		ELSE 'mayor_50'
	END AS grupo_edad,
	SUM (cantidad * precio) AS revenue  
FROM ventas_enriquecidas 
GROUP BY grupo_edad 
ORDER BY revenue DESC;

WITH revenue_por_categoria AS (
	SELECT
		p.categoria,
		SUM (v.cantidad * p.precio) AS revenue
	FROM ventas AS v
	INNER JOIN productos p ON v.producto_id = p.id
GROUP BY p.categoria
)
SELECT ROUND(AVG (revenue),2) AS avg_renveue_per_category
FROM revenue_por_categoria;

WITH gasto_por_cliente AS (
	SELECT 
		v.cliente_id,
		SUM(v.cantidad * p.precio) AS total_gastado
	FROM ventas AS v
	INNER JOIN productos p ON v.producto_id = p.id
	GROUP BY v.cliente_id
),
top_spenders AS (
	SELECT *
	FROM gasto_por_cliente 
	WHERE total_gastado > (SELECT AVG(total_gastado) FROM gasto_por_cliente) 
)
SELECT AVG(total_gastado) AS top_average FROM top_spenders; 



WITH gasto_cliente_categoria AS (
	SELECT 
		v.cliente_id, 
		c.nombre, 
		p.categoria, 
		SUM(p.precio* v.cantidad) AS total
	FROM ventas AS v
	INNER JOIN clientes AS c ON v.cliente_id = c.id 
	INNER JOIN productos AS p ON v.producto_id = p.id
	GROUP BY c.nombre,p.categoria,v.cliente_id
),
max_por_categoria AS (
	SELECT 
		categoria,
		MAX(total) AS Max_spent
	FROM gasto_cliente_categoria 
	GROUP BY categoria 
)
SELECT 
	g.categoria,
    g.nombre AS cliente_nombre,
    g.total AS total_gastado
FROM gasto_cliente_categoria g
JOIN max_por_categoria m
	ON g.categoria = m.categoria
 AND g.total = m.Max_spent
ORDER BY g.categoria;


WITH ventas_por_categoria_producto AS (
	SELECT 
		p.categoria, 
		p.id AS producto_id, 
		p.nombre, 
		SUM(v.cantidad) AS total_unidades
	FROM ventas v
	INNER JOIN productos p ON v.producto_id = p.id
	GROUP BY p.nombre, p.id, p.categoria 
),
max_por_categoria AS (
	SELECT 
		categoria,
		MAX(total_unidades) AS best_sell
	FROM ventas_por_categoria_producto 
	GROUP BY categoria 
)
SELECT
    v.categoria,
    v.nombre AS producto_nombre,
    v.total_unidades AS unidades_vendidas
FROM ventas_por_categoria_producto v
JOIN max_por_categoria m
  ON v.categoria = m.categoria
 AND v.total_unidades = m.best_sell
ORDER BY v.categoria;
