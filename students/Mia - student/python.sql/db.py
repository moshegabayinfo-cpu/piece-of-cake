import os , psycopg 
from decimal import Decimal, InvalidOperation
from dotenv import load_dotenv

def connect_db():
    load_dotenv(interpolate=False)
    return psycopg.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", 5432),
        dbname=os.getenv("PGDATABASE", "poc"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", "369153")
    )
