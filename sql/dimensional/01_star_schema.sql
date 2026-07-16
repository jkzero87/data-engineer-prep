-- ============================================================
-- Star schema for CoinGecko prices
-- Grain of fact_prices: one row per coin per price timestamp
-- Load order (MANDATORY): 1) dim_coins  2) dim_dates  3) fact_prices
--   Facts reference dimension keys — loading facts first yields 0 rows silently.
-- Source: flat table `coins` (id, name, current_price, price_updated_at)
-- ============================================================

-- Dimension: one row per coin (current version — SCD2 comes next session)
CREATE TABLE dim_coins (
    coin_key   SERIAL PRIMARY KEY,      -- surrogate key
    coin_id    TEXT NOT NULL UNIQUE,    -- natural key from CoinGecko
    symbol     TEXT,
    name       TEXT
);

-- Dimension: one row per calendar day, pre-populated
CREATE TABLE dim_dates (
    date_key    INT PRIMARY KEY,        -- 20260715
    full_date   DATE NOT NULL UNIQUE,
    year        INT NOT NULL,
    month       INT NOT NULL,
    month_name  TEXT NOT NULL,
    day_of_week TEXT NOT NULL,
    is_weekend  BOOLEAN NOT NULL
);

-- Fact: grain = one price snapshot per coin per day
CREATE TABLE fact_prices (
    coin_key    INT NOT NULL REFERENCES dim_coins(coin_key),
    date_key    INT NOT NULL REFERENCES dim_dates(date_key),
    price_usd   NUMERIC(20,8),
    market_cap  NUMERIC(24,2),
    volume_24h  NUMERIC(24,2),
    loaded_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (coin_key, date_key)    -- enforces the grain
);

INSERT INTO dim_dates
SELECT
    TO_CHAR(d, 'YYYYMMDD')::INT,
    d::DATE,
    EXTRACT(YEAR FROM d)::INT,
    EXTRACT(MONTH FROM d)::INT,
    TRIM(TO_CHAR(d, 'Month')),
    TRIM(TO_CHAR(d, 'Day')),
    EXTRACT(ISODOW FROM d) IN (6,7)
FROM generate_series('2026-01-01'::DATE, '2027-12-31'::DATE, '1 day') AS d;

SELECT COUNT(*) FROM dim_dates;                     -- expect 730 (2 years, no leap day in range)
SELECT * FROM dim_dates WHERE date_key = 20260715;  -- today: should say July, Wednesday, is_weekend = false

INSERT INTO dim_coins (coin_id, name)
SELECT DISTINCT id, name
FROM coins
ON CONFLICT (coin_id) DO NOTHING;

INSERT INTO fact_prices (coin_key, date_key, price_usd)
SELECT
    dc.coin_key,
    TO_CHAR(c.price_updated_at, 'YYYYMMDD')::INT,
    c.current_price
FROM coins c
JOIN dim_coins dc ON dc.coin_id = c.id
WHERE c.price_updated_at IS NOT NULL
ON CONFLICT (coin_key, date_key) DO UPDATE
    SET price_usd = EXCLUDED.price_usd;

SELECT c.name, d.day_of_week, f.price_usd
FROM fact_prices f
JOIN dim_coins c USING (coin_key)
JOIN dim_dates d USING (date_key);

SELECT COUNT(*) FROM coins;        -- source has data?
SELECT COUNT(*) FROM dim_coins;    -- step 1 worked?
SELECT COUNT(*) FROM fact_prices;  -- step 2 worked?

SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'coins';


