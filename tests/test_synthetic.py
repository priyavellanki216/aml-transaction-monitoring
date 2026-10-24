from __future__ import annotations

import pytest
from pandas.testing import assert_frame_equal

from aml_workbench.synthetic import generate_synthetic_data


def test_generation_is_reproducible_for_same_seed():
    first_accounts, first_transactions = generate_synthetic_data(seed=17)
    second_accounts, second_transactions = generate_synthetic_data(seed=17)

    assert_frame_equal(first_accounts, second_accounts)
    assert_frame_equal(first_transactions, second_transactions)


def test_seeded_positive_and_negative_scenarios_are_ground_truth_only():
    _, transactions = generate_synthetic_data(seed=8, baseline_transaction_count=0)
    labeled = transactions.loc[transactions["scenario_id"].notna()]

    assert set(labeled["test_ground_truth"]) == {"positive", "negative"}
    assert labeled.loc[
        labeled["scenario_id"].str.startswith("positive_"), "test_ground_truth"
    ].eq("positive").all()
    assert labeled.loc[
        labeled["scenario_id"].str.startswith("negative_"), "test_ground_truth"
    ].eq("negative").all()
    assert transactions.loc[
        transactions["scenario_id"].isna(), "test_ground_truth"
    ].isna().all()


def test_all_transactions_reference_generated_accounts():
    accounts, transactions = generate_synthetic_data(seed=21, baseline_transaction_count=10)
    known_accounts = set(accounts["account_id"])

    assert set(transactions["source_account_id"]).issubset(known_accounts)
    assert set(transactions["destination_account_id"]).issubset(known_accounts)
    assert transactions["transaction_id"].is_unique
    assert (transactions["amount_minor"] > 0).all()


def test_different_seeds_change_background_records_but_keep_named_scenarios():
    _, first = generate_synthetic_data(seed=1, baseline_transaction_count=8)
    _, second = generate_synthetic_data(seed=2, baseline_transaction_count=8)

    first_scenarios = first.loc[first["scenario_id"].notna()].reset_index(drop=True)
    second_scenarios = second.loc[second["scenario_id"].notna()].reset_index(drop=True)
    first_background = first.loc[first["scenario_id"].isna()].reset_index(drop=True)
    second_background = second.loc[second["scenario_id"].isna()].reset_index(drop=True)

    assert_frame_equal(first_scenarios, second_scenarios)
    assert not first_background.equals(second_background)


def test_generator_rejects_invalid_counts_and_seed_types():
    with pytest.raises(ValueError, match="cannot be negative"):
        generate_synthetic_data(baseline_transaction_count=-1)
    with pytest.raises(TypeError, match="seed must be an integer"):
        generate_synthetic_data(seed=True)
