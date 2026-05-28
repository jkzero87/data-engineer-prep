-- nivel_8_performance.sql
-- Phase 8 practice — query performance: EXPLAIN ANALYZE and indexes
--
-- Requires the `eventos` table (500k rows) in schema `practica`.
-- If missing, recreate it by running the generator block from the
-- Level 8 session (or ask Claude for it).
--
-- Workflow per exercise:
--   1. Write the query
--   2. EXPLAIN ANALYZE it
--   3. Reason about whether an index helps (selectivity!)
--   4. CREATE INDEX if appropriate, re-run, compare
SET search_path TO practica;

SELECT COUNT(*) FROM practica.eventos;

SELECT * FROM eventos

SELECT * FROM eventos
WHERE usuario_id = 7777;

EXPLAIN ANALYZE
SELECT * FROM eventos
WHERE usuario_id = 7777;

SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'practica'
  AND tablename = 'eventos';

SELECT * FROM eventos
WHERE tipo = 'compra';

EXPLAIN ANALYZE
SELECT * FROM eventos
WHERE tipo = 'compra';

CREATE INDEX idx_eventos_tipo ON eventos (tipo);

EXPLAIN ANALYZE
SELECT * FROM eventos
WHERE tipo = 'compra';

SET enable_bitmapscan = off;
SET enable_indexscan = off;

RESET enable_bitmapscan;
RESET enable_indexscan;

DROP INDEX idx_eventos_tipo;

-- 8.2 conclusion: tested CREATE INDEX on tipo column.
-- Bitmap Index Scan: 377ms. Seq Scan: 390ms. Difference negligible.
-- At ~20% selectivity, index doesn't earn its write cost. Dropped.