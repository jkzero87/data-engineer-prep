-- nivel_7_fechas.sql
-- Phase 7 practice — date and time handling on the practica schema
-- DATE_TRUNC, INTERVAL arithmetic, EXTRACT
SET search_path TO practica;

-- Quick sanity check
SELECT * FROM canciones LIMIT 3;

SELECT
    DATE_TRUNC('month', fecha_lanzamiento) AS mes,
    COUNT(*) AS total_canciones,
    SUM(reproducciones) AS reproducciones_totales
FROM practica.canciones
GROUP BY DATE_TRUNC('month', fecha_lanzamiento)
ORDER BY mes;

SELECT titulo, CURRENT_DATE - fecha_lanzamiento AS dias_desde_lanzamiento
FROM practica.canciones;

SELECT *
FROM practica.canciones
WHERE fecha_lanzamiento >= CURRENT_DATE - INTERVAL '900 days';

WITH mensual AS (
    SELECT
        DATE_TRUNC('month', fecha_lanzamiento) AS mes,
        SUM(reproducciones) AS total
    FROM practica.canciones
    GROUP BY DATE_TRUNC('month', fecha_lanzamiento)
)
SELECT
    mes,
    total,
    LAG(total) OVER (ORDER BY mes) AS total_mes_anterior,
    total - LAG(total) OVER (ORDER BY mes) AS cambio
FROM mensual
ORDER BY mes;

SELECT
    titulo,
    fecha_lanzamiento,
    DATE_TRUNC('month', fecha_lanzamiento)::DATE AS inicio_mes
FROM canciones
ORDER BY fecha_lanzamiento;

SELECT
    DATE_TRUNC('month', fecha_lanzamiento) AS mes,
    COUNT(*) AS total_canciones,
    SUM(reproducciones) AS reproducciones_totales
FROM canciones
GROUP BY DATE_TRUNC('month', fecha_lanzamiento)
ORDER BY mes;

SELECT
    DATE_TRUNC('quarter', fecha_lanzamiento) AS trimestre,
    COUNT(*) AS total_canciones,
    SUM(reproducciones) AS reproducciones_totales
FROM canciones
GROUP BY DATE_TRUNC('quarter', fecha_lanzamiento)
ORDER BY trimestre;

Exercises
Write these in nivel_7_fechas.sql under a -- EJERCICIOS header. Work on practica.canciones. 
Do them in order — each builds on the last. Try each cold before running. 
If you stare at one and have no idea where to start, that's real information — tell me and 
we slow down on that piece.
7.1 — Days since release. For every song, show titulo, fecha_lanzamiento, 
and a column dias_desde_lanzamiento with how many days have passed since it was released.
 Order by that column so the oldest song is first.
7.2 — Releases per month. Show one row per release-month: the month bucket (mes), 
how many songs came out that month (total), and the total plays that month (reproducciones_mes).
 Chronological order.
7.3 — Plays by day of week. Which day of the week do releases happen on, 
and how do plays distribute across weekdays? Show dia_semana (0–6), count of songs, 
and total plays per weekday. Order by dia_semana.
7.4 — Recency filter. Show all songs released in roughly the last 18 months relative to today.
 (Hint: CURRENT_DATE - INTERVAL '...'. Your data is from 2025 and today is May 2026 — pick an
  interval that actually catches some rows, and notice how the choice of interval 
  changes what comes back. This is the exercise where you feel why the number matters.)
7.5 — Month-over-month (the hard one, combines Level 6 + 7). Build a CTE that gives total plays
 per month, then in the outer query show each month, its total, the previous month's total,
  and the difference. First row's "previous" will be NULL — that's correct,
   don't fight it (though you may wrap it in COALESCE(..., 0) if you want it tidy).
Start with 7.1, write it, run it, paste the result. We'll go one at a time
 — I'd rather catch a misunderstanding on 7.1 than have it compound through all five.