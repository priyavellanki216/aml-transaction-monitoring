from __future__ import annotations

import sqlite3

import pytest

from aml_workbench.database import create_connection, load_synthetic_data


def test_loads_seeded_data_and_enables_foreign_keys(seeded_data):
    accounts, transactions = seeded_data
    connection = create_connection(":memory:")
    try:
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        load_synthetic_data(connection, accounts, transactions)

        assert connection.execute("SELECT COUNT(*) FROM accounts").fetchone()[0] == len(accounts)
        assert connection.execute("SELECT COUNT(*) FROM transactions").fetchone()[0] == len(transactions)
    finally:
        connection.close()


def test_orphan_transaction_is_rejected_and_insert_is_atomic(seeded_data):
    accounts, transactions = seeded_data
    invalid_transactions = transactions.copy()
    invalid_transactions.loc[0, "source_account_id"] = "ACC-NOT-FOUND"
    connection = create_connection(":memory:")
    try:
        with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY"):
            load_synthetic_data(connection, accounts, invalid_transactions)
        assert connection.execute("SELECT COUNT(*) FROM accounts").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM transactions").fetchone()[0] == 0
    finally:
        connection.close()


def test_load_rejects_naive_timestamps(seeded_data):
    accounts, transactions = seeded_data
    invalid_accounts = accounts.copy()
    invalid_accounts.loc[0, "opened_at_utc"] = "2025-01-01T00:00:00"
    connection = create_connection(":memory:")
    try:
        with pytest.raises(ValueError, match="must include a timezone"):
            load_synthetic_data(connection, invalid_accounts, transactions)
        assert connection.execute("SELECT COUNT(*) FROM accounts").fetchone()[0] == 0
    finally:
        connection.close()


def test_schema_rejects_scenario_without_test_ground_truth(seeded_data):
    accounts, transactions = seeded_data
    connection = create_connection(":memory:")
    try:
        load_synthetic_data(connection, accounts, transactions)
        with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint"):
            connection.execute(
                """INSERT INTO transactions
                   (transaction_id, source_account_id, destination_account_id,
                    amount_minor, currency, timestamp_utc, description, scenario_id,
                    test_ground_truth)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    "TX-INVALID-LABEL",
                    "ACC-0001",
                    "ACC-0002",
                    100,
                    "USD",
                    "2025-01-01T00:00:00+00:00",
                    "Synthetic invalid-label test row",
                    "invalid_missing_truth",
                    None,
                ),
            )
    finally:
        connection.close()


@pytest.mark.parametrize(
    "timestamp",
    [
        "2025-01-15T08:00:00",
        "not-a-timestamp",
        "2025-01-15T08:00:00.500000+00:00",
        "2025-01-15T13:00:00+05:00",
    ],
)
def test_schema_rejects_noncanonical_transaction_timestamps(seeded_data, timestamp):
    accounts, transactions = seeded_data
    connection = create_connection(":memory:")
    try:
        load_synthetic_data(connection, accounts, transactions)
        with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint"):
            connection.execute(
                """INSERT INTO transactions
                   (transaction_id, source_account_id, destination_account_id,
                    amount_minor, currency, timestamp_utc, description, scenario_id,
                    test_ground_truth)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    "TX-INVALID-TIME",
                    "ACC-0001",
                    "ACC-0002",
                    100,
                    "USD",
                    timestamp,
                    "Synthetic invalid-time test row",
                    None,
                    None,
                ),
            )
    finally:
        connection.close()


def test_schema_rejects_noncanonical_account_opened_at():
    connection = create_connection(":memory:")
    try:
        with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint"):
            connection.execute(
                """INSERT INTO accounts
                   (account_id, customer_id, account_type, opened_at_utc, country_code)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    "ACC-INVALID",
                    "CUS-INVALID",
                    "personal",
                    "2025-01-01T00:00:00",
                    "US",
                ),
            )
    finally:
        connection.close()
