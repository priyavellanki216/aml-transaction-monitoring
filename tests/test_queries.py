from __future__ import annotations

import pytest

from aml_workbench.database import create_connection, load_synthetic_data
from aml_workbench.queries import account_activity_summary, rolling_outgoing_activity
from aml_workbench.synthetic import generate_synthetic_data


def _scenario_database():
    accounts, transactions = generate_synthetic_data(
        seed=44, baseline_transaction_count=0
    )
    connection = create_connection(":memory:")
    load_synthetic_data(connection, accounts, transactions)
    return connection


def test_account_activity_summary_uses_sql_direction_and_minor_units():
    connection = _scenario_database()
    try:
        summary = account_activity_summary(connection).set_index("account_id")

        assert summary.loc["ACC-0001", "outgoing_count"] == 1
        assert summary.loc["ACC-0001", "outgoing_amount_minor"] == 999_500
        assert summary.loc["ACC-0002", "incoming_count"] == 1
        assert summary.loc["ACC-0002", "incoming_amount_minor"] == 999_500
        assert summary.loc["ACC-0006", "outgoing_count"] == 4
        assert summary.loc["ACC-0006", "outgoing_amount_minor"] == 100_000
    finally:
        connection.close()


def test_rolling_window_counts_include_exact_lower_boundary():
    connection = _scenario_database()
    try:
        rolling = rolling_outgoing_activity(
            connection, window_seconds=60, currency="usd"
        )
        velocity = rolling.loc[
            rolling["transaction_id"].str.startswith("TX-POS-VELOCITY-")
        ].sort_values("transaction_id")

        assert velocity["transaction_count_window"].tolist() == [1, 2, 2, 2]
        assert velocity["amount_minor_window"].tolist() == [25_000, 50_000, 50_000, 50_000]
        # The second event is exactly 60 seconds after the first and includes it.
        assert velocity.iloc[1]["transaction_count_window"] == 2
    finally:
        connection.close()


@pytest.mark.parametrize("window_seconds", [0, -1, 31_536_001])
def test_rolling_query_rejects_out_of_range_windows(window_seconds):
    connection = _scenario_database()
    try:
        with pytest.raises(ValueError):
            rolling_outgoing_activity(connection, window_seconds=window_seconds)
    finally:
        connection.close()


def test_rolling_query_rejects_boolean_or_non_integer_window():
    connection = _scenario_database()
    try:
        with pytest.raises(TypeError):
            rolling_outgoing_activity(connection, window_seconds=True)
    finally:
        connection.close()
