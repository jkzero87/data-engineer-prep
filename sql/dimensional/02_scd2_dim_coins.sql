-- ============================================================
-- 02: Convert dim_coins to SCD Type 2
-- Adds validity columns, replaces UNIQUE(coin_id) with a
-- partial unique index (one current row per coin).
-- Includes an example rename transaction (edit values to re-run).
-- ============================================================

SELECT coin_id, name FROM dim_coins;

-----------------------------------------------------------

ALTER TABLE dim_coins
    ADD COLUMN valid_from  DATE NOT NULL DEFAULT '2026-01-01',
    ADD COLUMN valid_to    DATE NOT NULL DEFAULT '9999-12-31',
    ADD COLUMN is_current  BOOLEAN NOT NULL DEFAULT TRUE;

ALTER TABLE dim_coins DROP CONSTRAINT dim_coins_coin_id_key;
CREATE UNIQUE INDEX one_current_per_coin
    ON dim_coins (coin_id) WHERE is_current;

BEGIN;

-- Step 1: close the old version
UPDATE dim_coins
SET valid_to = CURRENT_DATE - 1,
    is_current = FALSE
WHERE coin_id = 'bitcoin'
  AND is_current;

-- Step 2: insert the new version
INSERT INTO dim_coins (coin_id, name, valid_from)
VALUES ('bitcoin', 'Bitcoin v2', CURRENT_DATE);
-- valid_to and is_current take their defaults: 9999-12-31, TRUE

COMMIT;

SELECT coin_key, coin_id, name, valid_from, valid_to, is_current
FROM dim_coins
WHERE coin_id = 'bitcoin';