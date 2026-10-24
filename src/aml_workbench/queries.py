"""SQL-backed transaction analysis helpers loaded from packaged query files."""

from __future__ import annotations

import sqlite3
from functools import lru_cache
from importlib.resources import files

import pandas as pd


@lru_cache(maxsize=None)
def _query(name: str) -> str:
    return files("aml_workbench").joinpath(f"sql/{name}").read_text(
        encoding="utf-8"
    )


def account_activity_summary(connection: sqlite3.Connection) -> pd.DataFrame:
    """Return account-level incoming/outgoing counts and amount totals."""
    return pd.read_sql_query(_query("account_activity.sql"), connection)


def rolling_outgoing_activity(
    connection: sqlite3.Connection,
    window_seconds: int = 86_400,
    currency: str = "USD",
) -> pd.DataFrame:
    """Return per-transaction outgoing counts and totals in a trailing window.

    The SQL frame includes rows exactly ``window_seconds`` before the current
    transaction (inclusive lower boundary) and the current transaction itself.
    Events are partitioned by source account and currency, and timestamps are
    interpreted as UTC ISO-8601 values.
    """
    if isinstance(window_seconds, bool) or not isinstance(window_seconds, int):
        raise TypeError("window_seconds must be an integer")
    if window_seconds <= 0:
        raise ValueError("window_seconds must be greater than zero")
    if window_seconds > 31_536_000:
        raise ValueError("window_seconds cannot exceed 365 days")
    normalized_currency = currency.strip().upper()
    if len(normalized_currency) != 3 or not normalized_currency.isalpha():
        raise ValueError("currency must be a three-letter code")

    return pd.read_sql_query(
        _query("rolling_outgoing.sql"),
        connection,
        params={
            "currency": normalized_currency,
            "window_seconds": window_seconds,
        },
    )
