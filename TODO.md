# AML Transaction Monitoring Workbench — Outcome ToDo

Status reflects delivered evidence only. Milestone 1 is complete after the recorded tests; later milestones remain queued pending approval.

## Milestone 1 — Reproducible synthetic data and SQL foundation — COMPLETE

- [x] Reproducible synthetic account and transaction data: generate account and transaction data deterministically from an explicit seed; include seeded positive and negative scenarios for tests; keep the scenario label as test ground truth only, never as a confirmed real-world AML finding.
- [x] SQL transaction analysis and time-window aggregations: define the SQLite account/transaction schema and SQL analysis queries, including explicit time-window boundaries and supporting transaction identifiers; use isolated temporary SQLite databases for automated tests.
- [x] Automated tests: use pytest with seeded positive and negative scenarios; report only tests actually run and their actual results. Evidence: 20 tests passed; see `docs/test-results.md`.
- [x] Foundation documentation: identify synthetic-data scope and limitations and explain that test labels do not represent confirmed suspicious activity.

## Milestone 2 — Configurable rules and explainable alerts — QUEUED; requires approval

- [ ] Configurable rules: implement rules for threshold-adjacent transfers, rapid movement of funds, and unusual transaction velocity; document each rule's definitions, configurable parameters, window boundaries, data limitations, false-positive sources, and scenarios it may miss.
- [ ] Explainable alerts: link every generated alert to supporting transaction identifiers and a rule explanation; clearly distinguish alerts from confirmed suspicious activity; do not treat synthetic scenario labels as confirmed real-world AML findings.

## Milestone 3 — NetworkX transaction-network analysis — QUEUED; requires approval

- [ ] Supported transaction-network patterns: use NetworkX for documented supported patterns, return the supporting account and transaction identifiers, and document parameters, data limitations, likely false positives, and missed scenarios; graph connectivity or a pattern match is not a confirmed suspicious-activity finding.

## Milestone 4 — Risk-prioritized investigation, history, and reporting — QUEUED; requires approval

- [ ] Investigation cases and analyst actions: create risk-prioritized investigation cases; support analyst notes, dispositions, escalation, and follow-up actions; keep an auditable case history; keep analyst disposition separate from an alert and from synthetic test ground truth.
- [ ] Evidence-linked reports and reporting datasets: create investigation reports linked to supporting evidence and transaction identifiers; provide Power BI-compatible reporting datasets and Excel-compatible exports; label alerts as leads rather than confirmed suspicious activity.

## Milestone 5 — Streamlit investigation interface and integrated delivery — QUEUED; requires approval

- [ ] Streamlit investigation interface: provide an analyst-facing interface for alerts, linked evidence, risk-prioritized cases, notes, dispositions, escalation, follow-up actions, auditable history, and evidence-linked reports/exports; visibly distinguish alerts from confirmed suspicious activity.
- [ ] Technology and analytical scope: use Python, Pandas, SQLite, SQL, pytest, and NetworkX; add Scikit-learn only if a specific, justified analytical requirement benefits from it.
- [ ] Documentation and test evidence: document rule definitions, parameters, data limitations, false positives, missed scenarios, and actual test results; automated tests must include seeded positive and negative scenarios; never fabricate successful tests, commits, pushes, or performance metrics.
