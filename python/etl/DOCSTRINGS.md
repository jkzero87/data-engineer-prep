# Suggested docstrings for `extract.py` and `load.py`

This file contains **suggestions only**. The `.py` source files are not
modified. Each block below shows the exact location it is meant for, followed
by a ready-to-paste docstring. Stylistic choices:

- Triple-double-quoted Google-style docstrings (lightweight, tool-friendly).
- Module docstrings explain *what* the script does and *what it depends on*,
  so a reviewer can understand the file without reading the body.
- Inline docstrings are added only where behavior is non-obvious (the upsert
  semantics, the staleness rule, the skip rule).

---

## `extract.py`

### Module-level docstring

Place at the very top of the file, immediately after the imports (or before
them, as the conventional module docstring).

```python
"""Extract top cryptocurrencies from the CoinGecko public API.

Calls the CoinGecko ``/coins/markets`` endpoint for the top coins ranked by
market cap (USD) and writes the raw JSON response to
``python/data/coins.json``. That file is the handoff contract consumed by
``load.py``.

The script is intended to be run as a standalone module:

    python extract.py

Dependencies:
    requests -- for the HTTP GET.

Notes:
    The request is executed once and raises on a non-2xx response via
    ``raise_for_status()``. Retry with exponential backoff is a planned
    improvement, not yet implemented.
"""
```

### Inline suggestions

After the `params = {...}` line:

```python
# Query parameters for /coins/markets: USD price, ranked by market cap,
# top `per_page` coins. Intentionally hardcoded for this project.
```

After the `resp.raise_for_status()` line:

```python
# Fail fast on HTTP errors (4xx/5xx). Retry/backoff is a planned addition.
```

After the `DATA_PATH.parent.mkdir(...)` line:

```python
# Ensure python/data/ exists before writing; harmless if it already does.
```

---

## `load.py`

### Module-level docstring

Place at the very top of the file.

```python
"""Load staged CoinGecko data into PostgreSQL with a null-safe upsert.

Reads the JSON produced by ``extract.py`` (``python/data/coins.json``) and
upserts each record into the ``coins`` table. The load is idempotent and
data-quality oriented:

    * Records missing the ``id`` field are logged at WARNING and skipped,
      since they have no stable key.
    * On conflict, incoming NULLs never overwrite existing values
      (``COALESCE(EXCLUDED.x, coins.x)``).
    * ``price_updated_at`` is advanced to ``NOW()`` only when a real
      (non-NULL) price arrives, so a lagging timestamp signals staleness.

Run-level counters (``loaded`` / ``skipped`` / ``stale``) are emitted in a
single summary INFO line and written both to stdout and to
``python/logs/pipeline.log``.

Intended to be run as a standalone module:

    python load.py

Dependencies:
    psycopg2       -- PostgreSQL driver.
    python-dotenv  -- loads DB_* credentials from the repo-root .env.

Environment:
    DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD -- read via os.getenv.
"""
```

### Docstring for the `UPSERT_SQL` constant

Place immediately above the `UPSERT_SQL = """..."""` assignment (replacing any
existing comment, if present).

```python
#: Idempotent upsert for the coins table. Three guarantees:
#:   1. Conflict target is the primary key ``id``.
#:   2. ``COALESCE(EXCLUDED.x, coins.x)`` keeps the existing value when the
#:      incoming value is NULL, so partial API data never clobbers good data.
#:   3. ``price_updated_at`` advances to NOW() only when a real price is
#:      provided; otherwise the previous timestamp is retained as a
#:      staleness signal.
```

### Inline suggestions

After the `logging.basicConfig(...)` block:

```python
# Dual handlers: FileHandler persists the audit trail to pipeline.log,
# StreamHandler mirrors it to stdout for interactive runs.
```

After the `load_dotenv(...)` line:

```python
# Load DB_* from the .env at the repository root (parents[1] of the etl dir).
```

Above the `for coin in coins:` loop:

```python
# Iterate once per record. Counters track data quality, not just throughput:
#   loaded  -- records sent to the DB (insert or update)
#   skipped -- records dropped (missing id)
#   stale   -- records with no price (price_updated_at will not advance)
```

After the `if coin_id is None:` branch:

```python
# A record without id has no stable key; it cannot be upserted, so we skip it
# rather than attempt an insert with a NULL primary key.
```

After the `if price is None:` branch:

```python
# Count stale prices for reporting. The row is still upserted; the CASE in
# UPSERT_SQL is what actually prevents price_updated_at from advancing.
```

After the `logger.info("Run complete: ...")` line:

```python
# Single summary line per run; grep "Run complete" in pipeline.log for history.
```

---

## How to apply (optional, manual)

These suggestions can be pasted in as-is. If adopted, consider also:

- Keeping the existing inline style (the files are currently sparsely
  commented, so adding all of the above may feel dense; a lighter touch would
  be the module docstrings plus the `UPSERT_SQL` docstring alone).
- Running `python -m pydoc etl.extract` / `etl.load` to confirm the module
  docstrings render cleanly.
