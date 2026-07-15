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