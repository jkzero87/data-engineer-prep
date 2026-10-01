# data-engineer-prep

Mi camino hacia data engineering: Python, SQL, ETL y, en `llm/`, agentes de IA
locales. Cada carpeta es un paso de práctica; las más completas tienen su
propio README.

## Qué hay aquí

| Carpeta | Qué es |
|---|---|
| [`python/etl/`](python/etl/) | **Pipeline ETL de CoinGecko → PostgreSQL.** Extracción con `requests`, upsert idempotente que no pisa datos buenos con nulos, logging y tests con pytest que corren en GitHub Actions. Tiene README con arquitectura y decisiones de diseño |
| [`sql/dimensional/`](sql/dimensional/) | Modelo estrella sobre los precios de CoinGecko y conversión de `dim_coins` a SCD tipo 2 |
| [`sql/exercises/`](sql/exercises/) | Ejercicios por nivel, de `SELECT` básico a window functions, fechas y performance |
| [`sql/setup/`](sql/setup/) | Creación de tablas y reset del entorno de práctica |
| [`python/sessions/`](python/sessions/) | Scripts de las sesiones de práctica de Python (p. ej. `session4.py`: análisis de logs de un servidor web) |
| [`python/jira-analysis/`](python/jira-analysis/) | Notebook de exploración del dataset de issues de Apache JIRA con pandas |
| [`llm/`](llm/) | **suach**: asistente local de búsqueda con dos modelos (ejecutor y supervisor). [`llm/PROYECTO.md`](llm/PROYECTO.md) explica el experimento y el método; `llm/suach/PROJECT_TRUTH.md` es el registro de hechos verificados |
| [`cv/lane-detection/`](cv/lane-detection/) | Primer paso (Canny sobre un frame de video) de lo que luego fue el repo [lane-detection](https://github.com/jkzero87/lane-detection) |

El agente de archivos **chimi**, que nació junto a suach, vive en su propio
repositorio.

## Stack

- Python 3: `requests`, `psycopg2`, `pandas`, `pytest`
- PostgreSQL 16 (Docker), DBeaver
- GitHub Actions para los tests del ETL
- `llama.cpp` con modelos locales en una RTX 5060 Ti de 16 GB (para `llm/`)

## Correr los tests del ETL

```
pip install -r python/etl/requirements.txt pytest
pytest python/etl/test_load.py -v
```
