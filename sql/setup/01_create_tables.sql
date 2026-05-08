-- ============================================================
-- Setup inicial — crea tablas y carga datos de prueba
-- ============================================================
-- Ejecutar UNA SOLA VEZ sobre una base limpia.
-- Si necesitas reiniciar, usa primero 99_reset.sql.
-- ============================================================

-- Extensión para búsquedas sin acentos
CREATE EXTENSION IF NOT EXISTS unaccent;

-- Tabla clientes
CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    email TEXT UNIQUE,
    edad INTEGER,
    fecha_registro DATE DEFAULT CURRENT_DATE
);

-- Tabla productos
CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    categoria TEXT NOT NULL,
    precio NUMERIC(10,2) NOT NULL,
    stock INTEGER DEFAULT 0
);

-- Tabla ventas
CREATE TABLE ventas (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES clientes(id),
    producto_id INTEGER REFERENCES productos(id),
    cantidad INTEGER NOT NULL,
    fecha_venta DATE DEFAULT CURRENT_DATE
);

-- Datos: clientes (16)
INSERT INTO clientes (nombre, email, edad) VALUES
    ('Juan Perez', 'juan@example.com', 32),
    ('María García', 'maria@example.com', 28),
    ('Carlos López', 'carlos@example.com', 45),
    ('Ana Rodríguez', 'ana@example.com', 19),
    ('Pedro Martínez', 'pedro@example.com', 67),
    ('Laura Fernández', NULL, 34),
    ('Andrés Vargas', 'andres@example.com', 41),
    ('Sofía Ramírez', 'sofia@example.com', 22),
    ('Diego Torres', 'diego@example.com', 55),
    ('Valentina Cruz', 'valentina@example.com', 29),
    ('Roberto Silva', 'roberto@example.com', 38),
    ('Camila Herrera', 'camila@example.com', 26),
    ('Felipe Castro', 'felipe@example.com', 49),
    ('Isabella Mejía', 'isabella@example.com', 31),
    ('Mateo Jiménez', NULL, 23),
    ('Daniela Ortiz', 'daniela@example.com', 44);

-- Datos: productos (10)
INSERT INTO productos (nombre, categoria, precio, stock) VALUES
    ('Laptop HP', 'Electrónica', 2500000, 15),
    ('Mouse inalámbrico', 'Electrónica', 80000, 100),
    ('Teclado mecánico', 'Electrónica', 350000, 25),
    ('Monitor 27"', 'Electrónica', 1200000, 10),
    ('Silla ergonómica', 'Muebles', 800000, 8),
    ('Escritorio madera', 'Muebles', 600000, 5),
    ('Lámpara LED', 'Hogar', 120000, 50),
    ('Cafetera', 'Hogar', 450000, 12),
    ('Audífonos Bluetooth', 'Electrónica', 280000, 40),
    ('Cojín lumbar', 'Muebles', 90000, 30);

-- Datos: ventas (15)
INSERT INTO ventas (cliente_id, producto_id, cantidad, fecha_venta) VALUES
    (1, 1, 1, '2026-04-15'),
    (1, 2, 2, '2026-04-15'),
    (2, 7, 3, '2026-04-18'),
    (3, 1, 1, '2026-04-20'),
    (3, 4, 2, '2026-04-20'),
    (4, 8, 1, '2026-04-22'),
    (5, 5, 1, '2026-04-25'),
    (6, 2, 5, '2026-04-28'),
    (7, 3, 1, '2026-05-01'),
    (8, 9, 2, '2026-05-02'),
    (1, 7, 1, '2026-05-03'),
    (10, 6, 1, '2026-05-05'),
    (11, 1, 1, '2026-05-05'),
    (12, 10, 4, '2026-05-06'),
    (3, 3, 1, '2026-05-06');

-- Verificación
SELECT COUNT(*) AS total_clientes  FROM clientes;   -- esperado: 16
SELECT COUNT(*) AS total_productos FROM productos;  -- esperado: 10
SELECT COUNT(*) AS total_ventas    FROM ventas;     -- esperado: 15
