"""Shared, isolated fixtures for the synthetic-data test suite."""

from __future__ import annotations

import sqlite3

import pytest

from aml_workbench.database import create_connection, load_synthetic_data
from aml_workbench.synthetic import generate_synthetic_data


@pytest.fixture
def seeded_data():
    return generate_synthetic_data(seed=20261024, baseline_transaction_count=12)


@pytest.fixture
def populated_connection(seeded_data):
    accounts, transactions = seeded_data
    connection = create_connection(":memory:")
    load_synthetic_data(connection, accounts, transactions)
    try:
        yield connection
    finally:
        connection.close()
