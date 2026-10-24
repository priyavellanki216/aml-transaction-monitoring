# Test Results

## Milestone 1 — 2026-10-24

- **Command:** `.venv/bin/python -m pytest` from the repository feature-branch checkout.
- **Environment:** Python 3.12.3, pytest 9.1.1, Pandas 3.1.0, SQLite 3.45.1.
- **Result:** 20 passed in 0.13 seconds.
- **Additional check:** `.venv/bin/python -m compileall -q src tests` completed successfully with no output.
- **Repository check:** `git diff --cached --check` completed successfully with no whitespace errors.

Coverage includes repeatable seeds, seed-dependent background rows, positive/negative test-label separation, valid account references, SQLite foreign keys and atomic inserts, UTC timestamp validation at loader and direct-SQL boundaries, required test ground truth for named scenarios, per-account SQL totals, rolling-window counts and amount totals, and the inclusive lower-boundary behavior.

No tests for configurable alert rules, NetworkX patterns, cases, reports/exports, or the Streamlit interface have been run; those features are deferred to later approval-gated milestones. These tests establish behavior only for the synthetic fixtures and do not establish real-world AML detection performance.
