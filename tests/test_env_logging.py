"""בדיקות טעינת הגדרות ולוגי SQL בפרויקט הפעיל."""
import sys
from pathlib import Path
import psycopg
import pytest
from test_app import client, password, site


def test_sql_logs_results_errors_and_redacts_password(client, caplog):
    import logging
    import os

    caplog.set_level(logging.INFO, logger="poc.sql")
    password = os.environ["PGPASSWORD"]
    with site.connect() as db:
        row = db.execute("SELECT %s AS example", (password,)).fetchone()
        assert row["example"] == password
        assert db.execute("SELECT 1 AS n WHERE FALSE").fetchall() == []
    assert "SQL QUERY" in caplog.text
    assert "SQL OK" in caplog.text
    assert "SQL RESULT (one)" in caplog.text
    assert "count=0" in caplog.text
    assert "[hidden]" in caplog.text
    assert password not in caplog.text
    with pytest.raises(psycopg.errors.DivisionByZero):
        with site.connect() as db:
            db.execute("SELECT 1 / 0")
    assert "SQL ERROR [22012]" in caplog.text


def test_dotenv_startup_without_password_prompt(client, tmp_path):
    import os
    import shutil
    import subprocess

    with site.connect() as db:
        schema = db.execute("SELECT current_schema() AS name").fetchone()["name"]
    project = Path(site.__file__).parent
    for filename in ("app.py", "db_logging.py"):
        shutil.copy2(project / filename, tmp_path / filename)
    values = {
        key: os.environ.get(key, default)
        for key, default in [
            ("PGHOST", "localhost"),
            ("PGPORT", "5432"),
            ("PGDATABASE", "poc"),
            ("PGUSER", "postgres"),
        ]
    }
    values["PGPASSWORD"] = os.environ["PGPASSWORD"]
    (tmp_path / ".env").write_text(
        "\n".join(f"{k}='{v}'" for k, v in values.items()), encoding="utf-8"
    )
    env = {k: v for k, v in os.environ.items() if k not in values}
    env["PGOPTIONS"] = f"-c search_path={schema}"
    result = subprocess.run(
        [sys.executable, str(tmp_path / "app.py"), "--check-db"],
        cwd=tmp_path.parent,
        env=env,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Connected to" in result.stdout
    assert "PostgreSQL password:" not in result.stdout + result.stderr
    assert values["PGPASSWORD"] not in result.stdout + result.stderr
