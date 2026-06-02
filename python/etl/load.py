import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()  # reads .env into the environment
print("HOST:", os.getenv("DB_HOST"))   # debug

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
)