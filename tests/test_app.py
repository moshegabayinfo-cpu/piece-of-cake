"""בדיקות מול PostgreSQL אמיתי, ב-schema זמני ללא שינוי נתוני public."""
from datetime import date, timedelta
from getpass import getpass
import os
import sys
from pathlib import Path
from uuid import uuid4

import psycopg
from psycopg import sql
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app as site


@pytest.fixture(scope="session", autouse=True)
def password():
    if "PGPASSWORD" not in os.environ:
        os.environ["PGPASSWORD"] = getpass("PostgreSQL test password: ")


@pytest.fixture
def client(monkeypatch, password):
    original_connect = site.connect
    schema = "poc_test_" + uuid4().hex
    with original_connect() as db:
        db.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))

    def isolated_connect():
        db = original_connect()
        db.execute(sql.SQL("SET search_path TO {}").format(sql.Identifier(schema)))
        return db

    monkeypatch.setattr(site, "connect", isolated_connect)
    site.app.config.update(TESTING=True)
    try:
        site.init_db()
        yield site.app.test_client()
    finally:
        with original_connect() as db:
            db.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema)))


def form(client, **changes):
    client.get("/")
    with client.session_transaction() as session:
        token = session["csrf"]
    data = dict(csrf=token, customer_name="Test O'Reilly <script>", phone="0501234567",
                quantity="2", fulfillment="pickup", address="", notes="",
                due_date=(date.today() + timedelta(days=2)).isoformat())
    data.update(changes)
    return data


def product_id():
    with site.connect() as db:
        return db.execute("SELECT id FROM products ORDER BY id LIMIT 1").fetchone()["id"]


def submit(client, **changes):
    return client.post(f"/order/{product_id()}", data=form(client, **changes))


def saved_order():
    with site.connect() as db:
        return db.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 1").fetchone()


def advance(client, order_id, status):
    return client.post(f"/admin/orders/{order_id}/status", data=form(client, status=status))


def test_catalog_and_repeatable_setup(client):
    assert client.get("/").status_code == 200
    site.init_db()
    with site.connect() as db:
        assert db.execute("SELECT count(*) AS n FROM products").fetchone()["n"] == 3


def test_pickup_persistence_price_and_escaping(client):
    assert submit(client, unit_price="0.01").status_code == 303
    order = saved_order()
    assert order["unit_price"] == 140 and order["quantity"] == 2
    assert order["status"] == "new"
    html = client.get("/admin").get_data(as_text=True)
    assert "280.00" in html and "&lt;script&gt;" in html
    assert "O&#39;Reilly" in html
    # חיבור SQL נפרד ולקוח HTTP חדש קוראים את ההזמנה ששמורה בדיסק.
    assert site.app.test_client().get("/admin").status_code == 200
    for status in ("preparing", "ready", "collected"):
        assert advance(client, order["id"], status).status_code == 303
    assert saved_order()["status"] == "collected"
    assert advance(client, order["id"], "preparing").status_code == 400


def test_delivery_flow(client):
    assert submit(client, fulfillment="delivery", address="Test street 10", notes="Call first").status_code == 303
    order = saved_order()
    assert order["address"] == "Test street 10" and order["notes"] == "Call first"
    assert advance(client, order["id"], "delivered").status_code == 400
    for status in ("preparing", "ready", "out_for_delivery", "delivered"):
        assert advance(client, order["id"], status).status_code == 303
    assert saved_order()["status"] == "delivered"


@pytest.mark.parametrize("changes", [
    {"fulfillment": "delivery", "address": ""}, {"quantity": "0"},
    {"quantity": "21"}, {"quantity": "abc"}, {"customer_name": " "},
    {"due_date": "2020-01-01"}, {"fulfillment": "unknown"}, {"notes": "x" * 501},
])
def test_reject_invalid_orders(client, changes):
    assert submit(client, **changes).status_code == 400
    assert saved_order() is None


def test_csrf_and_missing_records(client):
    assert submit(client, csrf="bad-token").status_code == 400
    assert client.get("/order/999999").status_code == 404
    assert client.get("/thanks/999999").status_code == 404
    assert advance(client, 999999, "preparing").status_code == 404
    assert saved_order() is None


def test_cancellation_is_final_and_pickup_address_discarded(client):
    submit(client, address="Should not be saved")
    order = saved_order()
    assert order["address"] == ""
    assert advance(client, order["id"], "cancelled").status_code == 303
    assert advance(client, order["id"], "preparing").status_code == 400


def test_database_constraints(client):
    submit(client)
    order = saved_order()
    with pytest.raises(psycopg.errors.CheckViolation):
        with site.connect() as db:
            db.execute("UPDATE orders SET quantity=0 WHERE id=%s", (order["id"],))
    assert saved_order()["quantity"] == 2


def test_missing_tables_diagnosis(client):
    with site.connect() as db:
        db.execute("DROP TABLE orders")
    with site.connect() as db:
        with pytest.raises(SystemExit, match="tables are missing"):
            site.check_tables(db)
    response = client.get("/admin")
    assert response.status_code == 503


def test_diagnostics_hide_password(monkeypatch):
    monkeypatch.setenv("PGPASSWORD", "private-test-value")
    error = psycopg.OperationalError('password authentication failed private-test-value')
    details = site.database_diagnosis(error)
    assert "private-test-value" not in details
    assert "Incorrect PostgreSQL" in details
