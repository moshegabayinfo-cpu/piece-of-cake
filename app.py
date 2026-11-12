"""Piece of Cake: דוגמה לימודית מקומית עם Flask ו-PostgreSQL.
GET מציג דפים; POST מאמת נתונים ושומר שינויים במסד poc.
"""
#hi git 

import argparse
from datetime import date
import logging
import os
from pathlib import Path
import secrets

from dotenv import load_dotenv
from flask import Flask, abort, redirect, render_template, request, session, url_for
import psycopg
from psycopg.rows import dict_row

from db_logging import LoggingCursor

# טוענים את ההגדרות מהקובץ שליד הסקריפט, ללא בקשת סיסמה במסוף.
load_dotenv(Path(__file__).with_name(".env"), override=False, interpolate=False)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config.update(MAX_CONTENT_LENGTH=16384, SESSION_COOKIE_SAMESITE="Lax")
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s"
)

STATUSES = {
    "new": "הזמנה חדשה",
    "preparing": "בהכנה",
    "ready": "מוכנה",
    "out_for_delivery": "יצאה למשלוח",
    "delivered": "נמסרה",
    "collected": "נאספה",
    "cancelled": "בוטלה",
}


def connect():
    # פרטי החיבור מגיעים מהסביבה. הסיסמה אינה כתובה בקוד.
    return psycopg.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "poc"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", ""),
        connect_timeout=5,
        row_factory=dict_row,
        cursor_factory=LoggingCursor,
    )


def database_diagnosis(error):
    # פרטי התקלה למסוף בלבד, ללא הדפסת הסיסמה.
    details = str(error)
    password = os.getenv("PGPASSWORD", "")
    if password:
        details = details.replace(password, "[hidden]")
    lower = details.lower()
    if "password authentication failed" in lower or error.sqlstate == "28P01":
        hint = "Incorrect PostgreSQL username/password. Use the database password, not the pgAdmin master password."
    elif "does not exist" in lower and "database" in lower:
        hint = (
            "Create database poc in pgAdmin on this same server, or correct PGDATABASE."
        )
    elif isinstance(error, psycopg.errors.UndefinedTable):
        hint = "Tables are missing. Run: python app.py --init-db"
    elif (
        "connection refused" in lower
        or "timeout" in lower
        or "could not translate host" in lower
    ):
        hint = "Check that the PostgreSQL service is running and PGHOST/PGPORT match pgAdmin."
    else:
        hint = "Compare host, port, database and username with your pgAdmin connection."
    return f"{type(error).__name__}: {details}\nAction: {hint}"


def check_tables(db):
    tables = db.execute(
        "SELECT to_regclass('products') AS products, to_regclass('orders') AS orders"
    ).fetchone()
    if not all(tables.values()):
        raise SystemExit(
            "Connected, but POC tables are missing. Run: python app.py --init-db"
        )
    print("POC tables are ready.")


def init_db():
    # עם סיום ה-with נעשה commit. אם יש שגיאה, נעשה rollback.
    with connect() as db:
        db.execute(Path(__file__).with_name("schema.sql").read_text(encoding="utf-8"))


def next_statuses(order):
    # זרימה שונה למשלוח ולאיסוף עצמי. אי אפשר לדלג ישר למסירה.
    route = ["new", "preparing", "ready"]
    route += (
        ["out_for_delivery", "delivered"]
        if order["fulfillment"] == "delivery"
        else ["collected"]
    )
    current = order["status"]
    if current not in route or current == route[-1]:
        return []
    return [route[route.index(current) + 1], "cancelled"]


@app.before_request
def protect_forms():
    # אסימון בטופס מבטיח שבקשת שינוי הגיעה מדף של האתר שלנו.
    session.setdefault("csrf", secrets.token_hex(24))
    if request.method == "POST":
        token = request.form.get("csrf", "")
        if not secrets.compare_digest(token, session["csrf"]):
            abort(400, "הטופס אינו בתוקף. רעננו את העמוד ונסו שוב.")


@app.get("/")
def catalog():
    with connect() as db:
        products = db.execute(
            "SELECT * FROM products WHERE active ORDER BY id"
        ).fetchall()
    return render_template("catalog.html", products=products)


@app.route("/order/<int:product_id>", methods=["GET", "POST"])
def order(product_id):
    with connect() as db:
        product = db.execute(
            "SELECT * FROM products WHERE id=%s AND active", (product_id,)
        ).fetchone()
        if not product:
            abort(404, "המוצר לא נמצא")
        error = None
        if request.method == "POST":
            try:
                # 1. קוראים ומאמתים את הטופס גם בשרת.
                name = request.form.get("customer_name", "").strip()
                phone = request.form.get("phone", "").strip()
                quantity = int(request.form.get("quantity", "0"))
                fulfillment = request.form.get("fulfillment", "")
                address = request.form.get("address", "").strip()
                notes = request.form.get("notes", "").strip()
                due_date = date.fromisoformat(request.form.get("due_date", ""))
                if not 1 <= len(name) <= 100 or not 1 <= len(phone) <= 30:
                    raise ValueError("יש להזין שם וטלפון באורך תקין")
                if not 1 <= quantity <= 20 or fulfillment not in ("delivery", "pickup"):
                    raise ValueError("בחרו כמות בין 1 ל-20 ואופן קבלה")
                if due_date <= date.today():
                    raise ValueError("אפשר להזמין למחר והלאה")
                if fulfillment == "delivery" and not address:
                    raise ValueError("למשלוח יש להזין כתובת מלאה")
                if len(address) > 300 or len(notes) > 500:
                    raise ValueError("הכתובת או ההערות ארוכות מדי")
            except ValueError as exc:
                error = str(exc)
            if error is None:
                # 2. המחיר נלקח מה-DB, ולא מטופס שעלול להשתנות בדפדפן.
                # שומרים מחיר בעת ההזמנה, כדי ששינוי עתידי בקטלוג לא ישנה אותה.
                result = db.execute(
                    """
                    INSERT INTO orders
                    (product_id, unit_price, customer_name, phone, quantity,
                     fulfillment, address, due_date, notes)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id
                    """,
                    (
                        product_id,
                        product["price"],
                        name,
                        phone,
                        quantity,
                        fulfillment,
                        address if fulfillment == "delivery" else "",
                        due_date,
                        notes,
                    ),
                ).fetchone()
                logging.info("Created order #%s", result["id"])
                # 3. הפניה ל-GET מונעת שליחה חוזרת כאשר מרעננים את דף האישור.
                return redirect(url_for("thanks", order_id=result["id"]), code=303)
    return render_template(
        "order.html",
        product=product,
        error=error,
        tomorrow=date.fromordinal(date.today().toordinal() + 1).isoformat(),
    ), (400 if error else 200)


@app.get("/thanks/<int:order_id>")
def thanks(order_id):
    with connect() as db:
        found = db.execute("SELECT id FROM orders WHERE id=%s", (order_id,)).fetchone()
    if not found:
        abort(404, "ההזמנה לא נמצאה")
    return render_template("thanks.html", order_id=order_id)


@app.get("/admin")
def admin():
    # JOIN מחבר הזמנות למוצרים. אין כאן עדיין מערכת התחברות למנהלים.
    with connect() as db:
        orders = db.execute("""
            SELECT o.*, p.name AS product_name, o.quantity * o.unit_price AS total
            FROM orders o JOIN products p ON p.id=o.product_id
            ORDER BY o.id DESC
        """).fetchall()
    return render_template(
        "admin.html", orders=orders, statuses=STATUSES, next_statuses=next_statuses
    )


@app.post("/admin/orders/<int:order_id>/status")
def change_status(order_id):
    with connect() as db:
        # נועלים את הרשומה עד לסיום העדכון כדי למנוע עדכונים מתנגשים.
        order = db.execute(
            "SELECT * FROM orders WHERE id=%s FOR UPDATE", (order_id,)
        ).fetchone()
        if not order:
            abort(404, "ההזמנה לא נמצאה")
        status = request.form.get("status", "")
        if status not in next_statuses(order):
            abort(400, "מעבר הסטטוס אינו אפשרי. רעננו את מסך הניהול.")
        # %s מעביר ערכים בנפרד מה-SQL ומונע SQL injection.
        db.execute("UPDATE orders SET status=%s WHERE id=%s", (status, order_id))
    logging.info("Order #%s -> %s", order_id, status)
    return redirect(url_for("admin"), code=303)


@app.errorhandler(psycopg.Error)
def database_error(error):
    logging.error("Database request failed: %s", database_diagnosis(error))
    return (
        render_template(
            "error.html",
            message="אין גישה תקינה למסד. הסיבה המדויקת והנחיות לבדיקה מופיעות במסוף שבו האתר רץ.",
        ),
        503,
    )


@app.errorhandler(400)
@app.errorhandler(404)
def request_error(error):
    return render_template("error.html", message=error.description), error.code


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--init-db", action="store_true", help="Create tables and demo products"
    )
    parser.add_argument(
        "--check-db", action="store_true", help="Check the PostgreSQL connection"
    )
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if not os.getenv("PGPASSWORD"):
        raise SystemExit(
            "Set PGPASSWORD in the .env file beside app.py, then restart. No password prompt is used."
        )
    print(
        "DB settings (no password):",
        {
            key: os.getenv(key, default)
            for key, default in [
                ("PGHOST", "localhost"),
                ("PGPORT", "5432"),
                ("PGDATABASE", "poc"),
                ("PGUSER", "postgres"),
            ]
        },
    )
    try:
        with connect() as db:
            result = db.execute(
                "SELECT current_database() AS name, version() AS version"
            ).fetchone()
        print(f"Connected to {result['name']}: {result['version']}")
        if args.init_db:
            init_db()
            print("Tables and demo products are ready.")
        else:
            with connect() as db:
                check_tables(db)
            if not args.check_db:
                app.run(host="127.0.0.1", port=args.port, debug=False)
    except psycopg.Error as error:
        raise SystemExit(database_diagnosis(error))
