"""Extract top cryptocurrencies from the CoinGecko API into a staged JSON file.

Calls the CoinGecko `/coins/markets` endpoint (top coins by market cap, priced
in USD) and writes the raw JSON list to python/data/coins.json. That file is
the handoff consumed by load.py, which upserts it into the Postgres coins
table. This script does not touch the database.

Inputs:
    CoinGecko public API (no key required for this endpoint).
Outputs:
    python/data/coins.json -- the API response list, pretty-printed.
Pipeline position:
    extract.py  ->  python/data/coins.json  ->  load.py  ->  Postgres coins
"""

import json
import logging
from pathlib import Path

import requests

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "coins.json"

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "pipeline.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("extract")

BASE = "https://api.coingecko.com/api/v3"
params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 5 }

resp = requests.get(f"{BASE}/coins/markets", params=params)
# Log the status and a response-body excerpt BEFORE raise_for_status(), which
# would raise without exposing the body -- this keeps the failure debuggable.
if resp.status_code != 200:
    logger.error("API returned status %d: %s", resp.status_code, resp.text[:200])
resp.raise_for_status()
data = resp.json()

DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

with open(DATA_PATH, "w") as f:
    json.dump(data, f, indent=2)

logger.info("Wrote %d coins to %s", len(data), DATA_PATH)