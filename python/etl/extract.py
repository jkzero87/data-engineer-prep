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
import os
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from logging_setup import get_logger

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "coins.json"
BASE = "https://api.coingecko.com/api/v3"

logger = get_logger("extract")


def build_session() -> requests.Session:
    """A requests session that retries transient failures with backoff.

    Retries on connection errors and on 429/5xx responses (up to 3 times,
    with exponential backoff), so a momentary CoinGecko hiccup doesn't fail
    the whole run.
    """
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.mount("http://", HTTPAdapter(max_retries=retry))
    return session


def fetch_coins(session: requests.Session, per_page: int, vs_currency: str) -> list:
    """Fetch the top `per_page` coins by market cap, priced in `vs_currency`."""
    params = {"vs_currency": vs_currency, "order": "market_cap_desc", "per_page": per_page}
    resp = session.get(f"{BASE}/coins/markets", params=params)
    # Log the status and a response-body excerpt BEFORE raise_for_status(), which
    # would raise without exposing the body -- this keeps the failure debuggable.
    if resp.status_code != 200:
        logger.error("API returned status %d: %s", resp.status_code, resp.text[:200])
    resp.raise_for_status()
    return resp.json()


def main() -> None:
    per_page = int(os.getenv("COINGECKO_PER_PAGE", "5"))
    vs_currency = os.getenv("COINGECKO_VS_CURRENCY", "usd")

    session = build_session()
    data = fetch_coins(session, per_page, vs_currency)

    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

    logger.info("Wrote %d coins to %s", len(data), DATA_PATH)


if __name__ == "__main__":
    main()
