import os
import psycopg2
from dotenv import load_dotenv
from pathlib import Path
import json

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "coins.json"

with open(DATA_PATH) as f:
    coins = json.load(f)

load_dotenv()  # reads .env into the environment
print("HOST:", os.getenv("DB_HOST"))   # debug

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
)


cur = conn.cursor()

for coin in coins:
    cur.execute(
        """
        INSERT INTO coins (id, name, current_price)
        VALUES (%s, %s, %s)
        ON CONFLICT (id) DO UPDATE
            SET name = EXCLUDED.name,
                current_price = EXCLUDED.current_price;
        """,
        (coin["id"], coin["name"], coin["current_price"])
    )

conn.commit()
cur.close()
conn.close()

print(f"Loaded {len(coins)} coins")