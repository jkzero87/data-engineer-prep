import requests
import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "coins.json"

BASE = "https://api.coingecko.com/api/v3"
params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 5 }

resp = requests.get(f"{BASE}/coins/markets", params=params)
resp.raise_for_status()
data = resp.json()

DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

with open(DATA_PATH, "w") as f:
    json.dump(data, f, indent=2)

print(f"Wrote {len(data)} coins to {DATA_PATH}")