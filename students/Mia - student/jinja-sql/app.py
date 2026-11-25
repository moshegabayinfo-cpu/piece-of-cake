"""דוגמת לימוד: שאילתת PostgreSQL והצגתה ב־Flask ו־Jinja."""
import os
from pathlib import Path

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
from flask import Flask, render_template

load_dotenv(Path(__file__).with_name('.env'), override=True, interpolate=False)
app = Flask(__name__)


def read_products():
    """שולפת מוצרים פעילים ממסד התרגול; אינה כותבת למסד."""
    with psycopg.connect(
        host=os.getenv('PGHOST', 'localhost'),
        port=os.getenv('PGPORT', '5432'),
        dbname=os.getenv('PGDATABASE', 'poc-test'),
        user=os.getenv('PGUSER', 'postgres'),
        password=os.getenv('PGPASSWORD', ''),
        connect_timeout=5,
        row_factory=dict_row,
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT name,  description, price FROM products WHERE active ORDER BY id')
            return cursor.fetchall()


@app.get('/')
def catalog():
    try:
        products = read_products()
        return render_template('catalog.html', products=products, error=None, source='PostgreSQL')
    except psycopg.Error:
        return render_template('catalog.html', products=[], error='לא הצלחנו לקרוא ממסד התרגול. בדקו את החיבור ואת טבלת products.', source='PostgreSQL'), 503


@app.get('/example')
def example():
    # אותו HTML, נתוני הדגמה בפייתון. שימושי לפני שמחברים למסד.
    products = [{'name': 'עוגת שוקולד', 'price': 160}, {'name': 'עוגת גבינה', 'price': 159}]
    return render_template('catalog.html', products=products, error=None, source='נתוני דוגמה')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
