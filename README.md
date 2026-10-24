# AML Transaction Monitoring & Suspicious Activity Investigation Workbench

A Python workbench for reproducible synthetic transaction monitoring, explainable alerts, and auditable analyst investigations. It is being built incrementally; only the Milestone 1 synthetic-data and SQLite/SQL foundation is implemented at this stage.

## Synthetic-data notice

All records produced by the included generator are synthetic. Seeded positive and negative scenario labels are automated-test ground truth only. They are not real-world findings, do not establish suspicious activity, and must not be used to make decisions about real people or accounts. The threshold-adjacent fixture is five dollars below an arbitrary $10,000 test reference, not a legal or regulatory reporting threshold.

## Milestone 1 capabilities

The current foundation provides deterministic Pandas account and transaction generation, an SQLite schema with referential and value constraints, per-account incoming/outgoing totals, and SQL window-function aggregation for outgoing transaction count and amount. The rolling window is inclusive at its lower boundary, partitions by source account and currency, and uses UTC ISO-8601 timestamps. Automated tests cover deterministic output, scenario-label separation, data integrity, SQL totals, and window boundaries.

Configurable monitoring rules, NetworkX patterns, explainable alert records, case management, reporting exports, and the Streamlit investigation interface are planned for later milestones and are not claimed as complete here.

## Setup and tests

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
python -m pytest
```

Use the generator and isolated in-memory database:

```python
from aml_workbench import create_connection, generate_synthetic_data, load_synthetic_data
from aml_workbench.queries import account_activity_summary, rolling_outgoing_activity

accounts, transactions = generate_synthetic_data(seed=20261024)
connection = create_connection(":memory:")
load_synthetic_data(connection, accounts, transactions)
summary = account_activity_summary(connection)
rolling = rolling_outgoing_activity(connection, window_seconds=3600)
```

See [`docs/data-dictionary.md`](docs/data-dictionary.md) for fields and limitations, and [`plan.md`](plan.md) for the approved architecture and gated milestones. Actual test results are recorded in [`docs/test-results.md`](docs/test-results.md) only after the tests have run.
