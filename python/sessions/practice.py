import requests

BASE = "https://api.coingecko.com/api/v3"
params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 5 }

resp = requests.get(f"{BASE}/coins/markets", params=params)
resp.raise_for_status()
data = resp.json()

for coin in data:
    print (coin["name"], coin["current_price"])