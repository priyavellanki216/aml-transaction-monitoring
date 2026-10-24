"""Deterministic synthetic account and transaction data for tests and demos.

The ``test_ground_truth`` field labels seeded scenarios for automated test oracles.
It is not a real-world AML finding or a claim about suspicious activity.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from typing import Any

import pandas as pd

ACCOUNT_COLUMNS = (
    "account_id",
    "customer_id",
    "account_type",
    "opened_at_utc",
    "country_code",
)
TRANSACTION_COLUMNS = (
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


def _iso_utc(value: datetime) -> str:
    """Return a stable ISO-8601 UTC timestamp with second precision."""
    return value.astimezone(timezone.utc).isoformat(timespec="seconds")


def _transaction(
    transaction_id: str,
    source_account_id: str,
    destination_account_id: str,
    amount_minor: int,
    timestamp: datetime,
    description: str,
    scenario_id: str | None = None,
    test_ground_truth: str | None = None,
) -> dict[str, Any]:
    return {
        "transaction_id": transaction_id,
        "source_account_id": source_account_id,
        "destination_account_id": destination_account_id,
        "amount_minor": amount_minor,
        "currency": "USD",
        "timestamp_utc": _iso_utc(timestamp),
        "description": description,
        "scenario_id": scenario_id,
        "test_ground_truth": test_ground_truth,
    }


def generate_synthetic_data(
    seed: int = 20261024,
    baseline_transaction_count: int = 24,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return reproducible account and transaction DataFrames.

    Positive and negative labels are attached only to explicitly seeded test
    scenarios. Background synthetic transfers have no scenario label. The
    threshold-adjacent fixture is five dollars below an arbitrary $10,000 test
    reference; it is not a regulatory threshold or an AML conclusion.

    Args:
        seed: Integer seed controlling account metadata and background transfers.
        baseline_transaction_count: Number of unlabeled background transfers.

    Returns:
        ``(accounts, transactions)`` with stable columns and row ordering.
    """
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise TypeError("seed must be an integer")
    if isinstance(baseline_transaction_count, bool) or not isinstance(
        baseline_transaction_count, int
    ):
        raise TypeError("baseline_transaction_count must be an integer")
    if baseline_transaction_count < 0:
        raise ValueError("baseline_transaction_count cannot be negative")

    rng = random.Random(seed)
    account_ids = [f"ACC-{number:04d}" for number in range(1, 13)]
    opened_anchor = datetime(2020, 1, 1, tzinfo=timezone.utc)
    account_rows = []
    for number, account_id in enumerate(account_ids, start=1):
        opened_at = opened_anchor + timedelta(days=rng.randint(0, 1800))
        account_rows.append(
            {
                "account_id": account_id,
                "customer_id": f"CUS-{number:04d}",
                "account_type": rng.choice(("personal", "business")),
                "opened_at_utc": _iso_utc(opened_at),
                "country_code": rng.choice(("US", "CA", "GB", "IN")),
            }
        )

    scenario_rows: list[dict[str, Any]] = []

    # This is an arbitrary synthetic fixture for later configurable rule tests.
    # It is not derived from a reporting obligation or legal/regulatory limit.
    scenario_rows.append(
        _transaction(
            "TX-POS-THRESHOLD-001",
            "ACC-0001",
            "ACC-0002",
            999_500,
            datetime(2025, 1, 15, 8, 0, tzinfo=timezone.utc),
            "Synthetic test transfer near a configurable reference amount",
            "positive_threshold_adjacent",
            "positive",
        )
    )

    rapid_start = datetime(2025, 1, 15, 9, 0, tzinfo=timezone.utc)
    scenario_rows.extend(
        [
            _transaction(
                "TX-POS-RAPID-001",
                "ACC-0003",
                "ACC-0004",
                800_000,
                rapid_start,
                "Synthetic test inflow to an intermediary account",
                "positive_rapid_movement",
                "positive",
            ),
            _transaction(
                "TX-POS-RAPID-002",
                "ACC-0004",
                "ACC-0005",
                760_000,
                rapid_start + timedelta(minutes=17),
                "Synthetic test outflow from the intermediary account",
                "positive_rapid_movement",
                "positive",
            ),
        ]
    )

    velocity_start = datetime(2025, 1, 15, 10, 0, tzinfo=timezone.utc)
    for number, seconds_after_start in enumerate((0, 60, 120, 180), start=1):
        scenario_rows.append(
            _transaction(
                f"TX-POS-VELOCITY-{number:03d}",
                "ACC-0006",
                f"ACC-{number + 6:04d}",
                25_000,
                velocity_start + timedelta(seconds=seconds_after_start),
                "Synthetic test transfer in a high-velocity sequence",
                "positive_high_velocity",
                "positive",
            )
        )

    # A simple recurring-payment fixture provides a seeded negative scenario.
    for number, month in enumerate((1, 2, 3), start=1):
        scenario_rows.append(
            _transaction(
                f"TX-NEG-ROUTINE-{number:03d}",
                "ACC-0012",
                "ACC-0011",
                450_000,
                datetime(2025, month, 1, 8, 0, tzinfo=timezone.utc),
                "Synthetic test recurring monthly payment",
                "negative_routine_monthly",
                "negative",
            )
        )

    # Background rows precede the named scenarios in time so they do not
    # contaminate the seeded three-minute velocity window.
    baseline_start = datetime(2024, 10, 1, tzinfo=timezone.utc)
    baseline_seconds = 90 * 24 * 60 * 60
    for number in range(1, baseline_transaction_count + 1):
        source, destination = rng.sample(account_ids, 2)
        timestamp = baseline_start + timedelta(seconds=rng.randrange(baseline_seconds))
        scenario_rows.append(
            _transaction(
                f"TX-BASE-{number:05d}",
                source,
                destination,
                rng.randint(5_000, 2_500_000),
                timestamp,
                "Synthetic background transfer",
            )
        )

    accounts = pd.DataFrame(account_rows, columns=ACCOUNT_COLUMNS)
    transactions = pd.DataFrame(scenario_rows, columns=TRANSACTION_COLUMNS)
    transactions = transactions.sort_values(
        ["timestamp_utc", "transaction_id"], kind="stable"
    ).reset_index(drop=True)
    return accounts, transactions
