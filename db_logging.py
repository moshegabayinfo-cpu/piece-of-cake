"""לוגים לשאילתות ולתוצאות, ללא שינוי אופן הקריאה למסד בקוד האתר."""

import logging
import os
from time import perf_counter

import psycopg

logger = logging.getLogger("poc.sql")


def safe_text(value):
    """מסתירים את סיסמת החיבור אם היא מופיעה בטקסט כלשהו."""
    text = str(value)
    password = os.getenv("PGPASSWORD", "")
    if password:
        text = text.replace(password, "[hidden]")
    return text


class LoggingCursor(psycopg.Cursor):
    """כל execute מדפיס שאילתה; fetchone/fetchall מדפיסים את הנתונים שנקראו."""

    def execute(self, query, params=None, **kwargs):
        query_text = (
            query.as_string(self.connection) if hasattr(query, "as_string") else query
        )
        if isinstance(query_text, bytes):
            query_text = query_text.decode("utf-8", errors="replace")
        logger.info("SQL QUERY: %s", safe_text(query_text))
        started = perf_counter()
        try:
            result = super().execute(query, params, **kwargs)
        except psycopg.Error as error:
            logger.error(
                "SQL ERROR [%s]: %s",
                error.sqlstate or type(error).__name__,
                safe_text(error),
            )
            raise
        logger.info(
            "SQL OK: status=%s rows=%s duration_ms=%.2f",
            self.statusmessage,
            self.rowcount,
            (perf_counter() - started) * 1000,
        )
        # לא קוראים כאן fetchall: פעולה כזאת הייתה צורכת את התוצאות לפני האתר.
        return result

    def fetchone(self):
        try:
            row = super().fetchone()
        except psycopg.Error as error:
            logger.error("SQL FETCH ERROR: %s", safe_text(error))
            raise
        logger.info("SQL RESULT (one): %s", safe_text(repr(row)))
        return row

    def fetchall(self):
        try:
            rows = super().fetchall()
        except psycopg.Error as error:
            logger.error("SQL FETCH ERROR: %s", safe_text(error))
            raise
        logger.info("SQL RESULT (all, count=%s): %s", len(rows), safe_text(repr(rows)))
        return rows
