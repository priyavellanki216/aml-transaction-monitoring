"""SQLite setup and loading helpers for synthetic data."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from importlib.resources import files
from pathlib import Path
from typing import Any

import pandas as pd

_ACCOUNT_REQUIRED = (
    "account_id",
    "customer_id",
    "account_type",
    "opened_at_utc",
    "country_code",
)
_TRANSACTION_REQUIRED = (
    "transaction_id",
    "source_account_id",
    "destination_account_id",
    "amount_minor",
    "currency",
    "timestamp_utc",
    "description",
    "scenario_id",
    "test_ground_truth",
)


def create_connection(database: str | Path = ":memory:") -> sqlite3.Connection:
    """Create a SQLite connection, enable foreign keys, and initialize tables.

    The default is an in-memory database. Tests should use this or a temporary
    path; the helper does not select any managed or shared production database.
    """
    connection = sqlite3.connect(str(database))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    initialize_schema(connection)
    return connection


def initialize_schema(connection: sqlite3.Connection) -> None:
    """Create the Milestone 1 schema if it does not already exist."""
    schema = files("aml_workbench").joinpath("sql/schema.sql").read_text(
        encoding="utf-8"
    )
    connection.executescript(schema)


def _require_columns(frame: pd.DataFrame, required: tuple[str, ...], name: str) -> None:
    missing = sorted(set(required).difference(frame.columns))
    if missing:
        raise ValueError(f"{name} is missing required columns: {', '.join(missing)}")


def _to_utc_iso(value: Any, field_name: str) -> str:
    if isinstance(value, pd.Timestamp):
        value = value.to_pydatetime()
    if isinstance(value, datetime):
        parsed = value
    else:
        text = str(value)
        if text.endswith("Z"):
            text = f"{text[:-1]}+00:00"
        try:
            parsed = datetime.fromisoformat(text)
        except ValueError as exc:
            raise ValueError(f"{field_name} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must include a timezone")
    if parsed.utcoffset() != timedelta(0):
        raise ValueError(f"{field_name} must be normalized to UTC")
    return parsed.astimezone(timezone.utc).isoformat(timespec="seconds")


def _nullable_text(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    return str(value)


def _positive_integer(value: Any, field_name: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be a positive integer")
    try:
        integer = int(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{field_name} must be a positive integer") from exc
    if integer <= 0 or integer != value:
        raise ValueError(f"{field_name} must be a positive integer")
    return integer


def load_synthetic_data(
    connection: sqlite3.Connection,
    accounts: pd.DataFrame,
    transactions: pd.DataFrame,
) -> None:
    """Insert synthetic account and transaction frames atomically.

    Foreign-key enforcement and the database constraints reject orphaned
    transactions, non-positive amounts, and invalid test-label combinations.
    Existing duplicate identifiers fail rather than silently replacing rows.
    """
    _require_columns(accounts, _ACCOUNT_REQUIRED, "accounts")
    _require_columns(transactions, _TRANSACTION_REQUIRED, "transactions")

    account_rows = [
        (
            str(row["account_id"]),
            str(row["customer_id"]),
            str(row["account_type"]),
            _to_utc_iso(row["opened_at_utc"], "opened_at_utc"),
            str(row["country_code"]),
        )
        for row in accounts.to_dict(orient="records")
    ]
    transaction_rows = []
    for row in transactions.to_dict(orient="records"):
        if row["source_account_id"] == row["destination_account_id"]:
            raise ValueError("source and destination accounts must be different")
        transaction_rows.append(
            (
                str(row["transaction_id"]),
                str(row["source_account_id"]),
                str(row["destination_account_id"]),
                _positive_integer(row["amount_minor"], "amount_minor"),
                str(row["currency"]).upper(),
                _to_utc_iso(row["timestamp_utc"], "timestamp_utc"),
                str(row["description"]),
                _nullable_text(row["scenario_id"]),
                _nullable_text(row["test_ground_truth"]),
            )
        )

    with connection:
        connection.executemany(
            """INSERT INTO accounts
               (account_id, customer_id, account_type, opened_at_utc, country_code)
               VALUES (?, ?, ?, ?, ?)""",
            account_rows,
        )
        connection.executemany(
            """INSERT INTO transactions
               (transaction_id, source_account_id, destination_account_id,
                amount_minor, currency, timestamp_utc, description, scenario_id,
                test_ground_truth)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            transaction_rows,
        )
