"""Load staged CoinGecko JSON into Postgres with a null-safe upsert.

Reads python/data/coins.json (produced by extract.py) and upserts each record
into the coins table. The load is idempotent and protects stored values from
partial API data:

    * Records with no `id` are logged WARNING and skipped (no stable key).
    * On conflict, a NULL incoming field never overwrites a stored value.
    * price_updated_at advances to NOW() only when a real price arrives, so a
      lagging timestamp flags a coin whose price the API stopped returning.

Inputs:
    python/data/coins.json -- list of coin objects from extract.py.
Outputs:
    The Postgres coins table (inserted/updated rows).
Pipeline position:
    extract.py  ->  python/data/coins.json  ->  load.py  ->  Postgres coins
"""

import os
import json
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

from logging_setup import get_logger

BASE_DIR = Path(__file__).resolve().parent            # .../python/etl
DATA_PATH = BASE_DIR.parent / "data" / "coins.json"   # same result as your line 7

logger = get_logger("load")

UPSERT_SQL = """
    INSERT INTO coins (id, name, current_price, price_updated_at)
    VALUES (%s, %s, %s,
            CASE WHEN %s::numeric IS NOT NULL THEN NOW() ELSE NULL END)
    ON CONFLICT (id) DO UPDATE SET
        -- COALESCE keeps the existing stored value when the incoming
        -- (EXCLUDED) value is NULL, so a partial API response never
        -- overwrites previously loaded good data.
        name = COALESCE(EXCLUDED.name, coins.name),
        current_price = COALESCE(EXCLUDED.current_price, coins.current_price),
        -- Staleness signal: price_updated_at only moves forward to NOW() when
        -- a real (non-NULL) price arrives. When the price is NULL the
        -- previous timestamp is retained, so a lagging value shows the coin
        -- is no longer being priced by the API.
        price_updated_at = CASE
            WHEN EXCLUDED.current_price IS NOT NULL THEN NOW()
            ELSE coins.price_updated_at
        END;
"""


def upsert_params(coin: dict):
    """Extract (id, name, price) from a coin record, or None if it has no id.

    A record with no id has no stable key, so it cannot be upserted against
    an existing row -- callers should skip it rather than insert a NULL
    primary key.
    """
    coin_id = coin.get("id")
    if coin_id is None:
        return None
    return coin_id, coin.get("name"), coin.get("current_price")


def load_coins(path: Path) -> list:
    with open(path) as f:
        return json.load(f)


def connect():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


def run(coins: list, conn) -> dict:
    loaded = skipped = stale = 0
    cur = conn.cursor()
    try:
        for coin in coins:
            params = upsert_params(coin)
            if params is None:
                logger.warning("Skipping record with missing id: %s", coin)
                skipped += 1
                continue

            coin_id, name, price = params
            if price is None:
                stale += 1
                logger.warning("No price for %s - keeping existing value", coin_id)

            # 4 placeholders in UPSERT_SQL, filled positionally: id, name, price, and
            # price again for the CASE WHEN %s::numeric IS NOT NULL timestamp clause.
            cur.execute(UPSERT_SQL, (coin_id, name, price, price))
            loaded += 1

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()

    return {"loaded": loaded, "skipped": skipped, "stale": stale}


def main() -> None:
    load_dotenv(BASE_DIR.parents[1] / ".env")
    coins = load_coins(DATA_PATH)

    conn = connect()
    try:
        counts = run(coins, conn)
    finally:
        conn.close()

    logger.info(
        "Run complete: loaded=%d skipped=%d stale=%d",
        counts["loaded"], counts["skipped"], counts["stale"],
    )


if __name__ == "__main__":
    main()
