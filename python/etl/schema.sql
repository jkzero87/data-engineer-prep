-- ============================================================
-- coins table -- target of the CoinGecko ETL load step
-- ============================================================
-- Reproduces the table that load.py writes to.
--
-- Column types are inferred from how load.py uses each field:
--   id                 TEXT         -- natural key from the API; used as
--                                      the ON CONFLICT (id) target, so it
--                                      MUST be a PRIMARY KEY (or at least
--                                      carry a UNIQUE constraint) for the
--                                      upsert in load.py to be valid.
--   name               TEXT         -- coin display name; may be NULL,
--                                      preserved via COALESCE on update.
--   current_price      NUMERIC      -- price in the target currency (USD);
--                                      nullable on a partial API response.
--   price_updated_at   TIMESTAMPTZ  -- advanced to NOW() only when a real
--                                      price arrives (see load.py CASE),
--                                      so a lagging value signals staleness.
--
-- Idempotent: safe to run on a fresh or existing database.
-- ============================================================

CREATE TABLE IF NOT EXISTS coins (
    id                TEXT        PRIMARY KEY,
    name              TEXT,
    current_price     NUMERIC,
    price_updated_at  TIMESTAMPTZ
);

-- ============================================================
-- Optional supporting DDL (not strictly required by load.py,
-- but recommended for operating the table)
-- ============================================================

-- Index to make staleness queries cheap: find rows whose price timestamp
-- lags behind the newest update.
CREATE INDEX IF NOT EXISTS idx_coins_price_updated_at
    ON coins (price_updated_at);

-- Self-documenting schema comments, surfaced by \d+ in psql and most GUIs.
COMMENT ON TABLE  coins IS
    'Top cryptocurrencies from CoinGecko, upserted by python/etl/load.py. Rows are never deleted; a NULL incoming value is preserved with COALESCE.';
COMMENT ON COLUMN coins.id IS
    'Natural key from the CoinGecko API (e.g. "bitcoin"). Target of ON CONFLICT (id).';
COMMENT ON COLUMN coins.current_price IS
    'Latest price in USD. NULL on a partial API response; never overwrites a good value on update.';
COMMENT ON COLUMN coins.price_updated_at IS
    'Last time a non-NULL price was received. Advanced only when current_price IS NOT NULL, so a stale value indicates the API stopped returning a price for this coin.';
