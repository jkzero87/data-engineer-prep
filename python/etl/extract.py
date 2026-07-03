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
if resp.status_code != 200:
    logger.error("API returned status %d: %s", resp.status_code, resp.text[:200])
resp.raise_for_status()
data = resp.json()

DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

with open(DATA_PATH, "w") as f:
    json.dump(data, f, indent=2)

logger.info("Wrote %d coins to %s", len(data), DATA_PATH)