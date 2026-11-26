# data-engineer-prep

**Summary (English).** My practice repository for data engineering, worked in sessions. Stack: Python 3, PostgreSQL 16 (Docker), psycopg2, pandas, pytest and GitHub Actions.

| Folder | Contents |
|---|---|
| `python/etl/` | CoinGecko → PostgreSQL extract-and-load pipeline with an idempotent, null-safe upsert (`ON CONFLICT (id) DO UPDATE`); 4 pytest tests run in CI (`.github/workflows/etl-tests.yml`). See its [README](python/etl/README.md). |
| `sql/setup/`, `sql/exercises/` | Table setup and SQL exercises by level, from basics to joins, window functions, dates and performance (levels 0–8). |
| `sql/dimensional/` | A star schema for the CoinGecko prices (`dim_coins`, `dim_dates`, `fact_prices`) and its conversion of `dim_coins` to SCD Type 2. |
| `python/sessions/` | Scripts from each practice session. |
| `python/jira-analysis/` | A pandas notebook exploring an Apache JIRA issues export. |
| `llm/` | Early local LLM agent experiments (`agent_v1.py`, the `suach` agent and its project notes in `PROYECTO.md` and `suach/PROJECT_TRUTH.md`). |
| `cv/lane-detection/` | A first Canny edge-detection step; the full project lives in [lane-detection](https://github.com/jkzero87/lane-detection). |

---

Mi camino hacia data engineering — Python, SQL, ETL, cloud.

## Estructura
.
├── python/
│   ├── sessions/   # Scripts de cada sesión de práctica
│   └── data/       # CSVs y outputs
├── sql/
│   ├── setup/      # CREATE TABLE, INSERT iniciales, extensiones
│   ├── exercises/  # Soluciones limpias por nivel
│   └── scratch/    # Sandbox local (ignorado por git)
└── README.md

## Stack actual

- Python 3
- PostgreSQL 16 (Docker)
- DBeaver
