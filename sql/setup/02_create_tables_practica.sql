-- ============================================================
-- Setup — schema 'practica' para Nivel 6 (window functions)
-- ============================================================
-- Re-ejecutable: DROP SCHEMA CASCADE limpia y reconstruye.
-- No toca el schema public (clientes/productos/ventas).
-- ============================================================

DROP SCHEMA IF EXISTS practica CASCADE;
CREATE SCHEMA practica;
SET search_path TO practica;

-- ------------------------------------------------------------
-- artistas (4 artistas, grupos desiguales en canciones: 4, 3, 2, 3)
-- ------------------------------------------------------------
CREATE TABLE artistas (
    id     INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    pais   TEXT
);

INSERT INTO artistas (id, nombre, pais) VALUES
    (1, 'Aurora Vibes',   'Colombia'),
    (2, 'Neon Pulse',     'Mexico'),
    (3, 'The Lo-Fi Cats', 'Colombia'),
    (4, 'Solar Beat',     'Argentina');

-- ------------------------------------------------------------
-- canciones (12 canciones)
--   reproducciones tiene EMPATES INTENCIONALES:
--     150000 aparece 3x (Amanecer, Circuito, Eco)
--      90000 aparece 2x (Ciudad Dormida, Tarde Gris)
--   fecha_lanzamiento: serie limpia Ene–May 2025
--   genero: Pop / Indie / Electronica (segunda dimensión PARTITION BY)
-- ------------------------------------------------------------
CREATE TABLE canciones (
    id                  INTEGER PRIMARY KEY,
    titulo              TEXT NOT NULL,
    artista_id          INTEGER REFERENCES artistas(id),
    genero              TEXT NOT NULL,
    duracion_segundos   INTEGER NOT NULL,
    reproducciones      INTEGER NOT NULL,
    fecha_lanzamiento   DATE NOT NULL
);

INSERT INTO canciones (id, titulo, artista_id, genero, duracion_segundos, reproducciones, fecha_lanzamiento) VALUES
    ( 1, 'Amanecer',       1, 'Pop',         210, 150000, '2025-01-10'),
    ( 2, 'Lluvia Neon',    1, 'Pop',         185, 220000, '2025-02-14'),
    ( 3, 'Ciudad Dormida', 1, 'Indie',       240,  90000, '2025-03-05'),
    ( 4, 'Eco',            1, 'Indie',       175, 150000, '2025-04-22'),
    ( 5, 'Pulso',          2, 'Electronica', 200, 300000, '2025-01-25'),
    ( 6, 'Circuito',       2, 'Electronica', 195, 150000, '2025-03-18'),
    ( 7, 'Senal',          2, 'Pop',         180,  75000, '2025-05-09'),
    ( 8, 'Tarde Gris',     3, 'Indie',       260,  90000, '2025-02-02'),
    ( 9, 'Cafe Frio',      3, 'Indie',       230,  45000, '2025-04-11'),
    (10, 'Orbita',         4, 'Electronica', 205, 280000, '2025-01-30'),
    (11, 'Gravedad',       4, 'Electronica', 215, 120000, '2025-03-27'),
    (12, 'Estrella Fugaz', 4, 'Pop',         190,  60000, '2025-05-20');

-- Verificación
SELECT COUNT(*) AS total_artistas  FROM practica.artistas;   -- esperado: 4
SELECT COUNT(*) AS total_canciones FROM practica.canciones;  -- esperado: 12