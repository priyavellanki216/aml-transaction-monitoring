# AML Transaction Monitoring Workbench — Proposed Architecture

**Status:** user-approved Milestone 1 implemented and verified; later milestones remain approval-gated.

## Repository inspection and constraints

The requested public repository is `priyavellanki216/aml-transaction-monitoring`. Its only visible remote branch is `main`, currently at `419ecc31a33f9504e2407854961267fe6064d3b7`; the checkout contains only a short `README.md`. There are no repository-specific testing, branch, or commit instructions. The KYC project's workflow is not present in this repository or the current task context, so its exact conventions cannot yet be verified.

The initialized WebDev project is empty and uses its Manus-managed Git remote (`git_repository.provider = manus`). The WebDev GitHub canonical-switch workflow does not support adopting an existing GitHub repository. Proposed separation: use a normal checkout of the specified GitHub repository as the source of truth for feature-branch commits/pushes, and use the WebDev project only for the managed Preview runtime when an interface is ready. Do not overwrite the WebDev remote or treat a GitHub feature-branch push as a Manus checkpoint.

No change will be made to `main`. Proposed feature branch: `feature/aml-workbench`, based on the inspected `main`. Proposed commit style: Conventional Commit subjects such as `feat(aml): add reproducible synthetic data and SQL analysis`. After a verified push, verify that the remote feature-branch SHA exactly matches the tested local commit. These are proposed defaults, not claims about the KYC project.

## Architecture

Use a Python package with a deterministic synthetic-data boundary, a SQLite persistence/analysis layer, explicit monitoring and case-domain modules, and a Streamlit presentation layer. Keep test ground truth separate from operational alert state. A generated scenario label is only an oracle for automated tests; it must never appear as a claim that an account or transaction is actually suspicious.

Python is the application language. Pandas provides tabular generation and reporting; SQLite (Python standard library) stores and queries accounts, transactions, alerts, cases, and audit events; SQL owns transaction analysis and time-window aggregations; pytest provides automated tests; NetworkX evaluates explicitly supported transaction-network patterns; Streamlit presents the workbench; openpyxl may be added for `.xlsx` export. Scikit-learn is not currently justified: configured rules and graph patterns are intended to remain deterministic and explainable. Add it only if a later, specific requirement warrants a documented analytical benefit.

Proposed source layout:

```text
app.py                              # Streamlit entry point (later milestone)
src/aml_workbench/
  synthetic.py                      # seeded synthetic accounts, transactions, and test scenarios
  database.py                       # SQLite connection, schema initialization, safe test setup
  sql/
    schema.sql                      # account and transaction tables, constraints, indexes
    analysis.sql                    # reusable analysis and time-window queries
  rules/                            # threshold-adjacent, rapid-movement, velocity rules (later)
  network.py                        # supported NetworkX graph patterns (later)
  alerts.py                         # explainable alerts with evidence transaction IDs (later)
  cases.py                          # prioritized investigation cases and audit history (later)
  reporting.py                      # Power BI-compatible datasets and Excel/report exports (later)
tests/
  fixtures/                         # seeded positive and negative scenarios
  test_synthetic.py
  test_sql_analysis.py
docs/
  rule-definitions.md               # parameters, limitations, false positives, missed scenarios
  data-dictionary.md
  test-results.md                   # actual results only, updated after checks run
```

Synthetic records should be reproducible for a stated seed and generator version. SQLite tests use isolated temporary databases, never a managed/shared production database. SQL queries should return stable transaction identifiers and explicitly document each time boundary (inclusive/exclusive) and timezone assumption. The initial analysis layer will include account-level transaction summaries and rolling time-window measures suitable for later rule evaluation.

Alerts are leads that require review, not findings. Case disposition is a separate analyst decision and must not be inferred from a rule hit or a synthetic test label. Every alert/report should identify the supporting transaction IDs; analyst actions should be attributable and represented in a chronological audit history. The application is a decision-support workbench, not an automated filing or legal conclusion system.

## Milestones

Only Milestone 1 is proposed for the initial implementation. Each later milestone requires a separate approval after the current milestone's results are reported.

### Milestone 1 — reproducible data and SQL foundation

Implement deterministic synthetic account and transaction generation with seeded positive and negative test scenarios; an SQLite schema for accounts and transactions; SQL transaction analysis including time-window aggregations; pytest coverage for reproducibility, referential/data integrity, known seeded scenarios, and SQL window results; and concise README/data-dictionary documentation that labels scenario truth as test-only. No production/customer data is used. This milestone does not implement configurable alert rules, network detection, case workflows, exports, or the full investigation UI.

### Milestone 2 — configurable rules and explainable alerts

Add configurable rules for transfers adjacent to a configured reference threshold, rapid movement of funds, and unusual transaction velocity. Rule parameters and time windows must be explicit; alert explanations must cite supporting transaction IDs. Document parameter meanings, known false-positive sources, and scenarios that the rules can miss. Do not present alert generation as confirmation of suspicious activity.

### Milestone 3 — transaction-network analysis

Use NetworkX to analyze a documented, bounded set of supported patterns (initial candidates: short directed cycles, fan-in/fan-out concentration, and rapid pass-through paths). Return graph findings with the supporting account and transaction identifiers, explicit pattern/parameter names, and limitations. Do not label graph connectivity itself as suspicious activity.

### Milestone 4 — investigation cases and evidence reporting

Create risk-prioritized cases from alerts; support analyst notes, dispositions, escalation, and follow-up actions; preserve an auditable chronological case history; and generate evidence-linked investigation reports. Provide flat, typed Power BI-compatible reporting datasets and Excel-compatible workbook exports. Keep alert state, analyst disposition, and any synthetic test ground truth separate.

### Milestone 5 — Streamlit workbench and end-to-end integration

Deliver the Streamlit investigation interface for alert review, evidence drill-down, case prioritization, notes/dispositions/escalation/follow-up, case history, and report/dataset exports. Integrate the analysis modules and clearly show that alerts are not confirmed suspicious activity. Run automated seeded positive and negative scenarios across the integrated flow. Record actual test results and remaining limitations; do not claim unrun tests or performance figures.

## Proposed interface design

Three low-probability design directions considered:

- Swiss editorial risk console — 0.0136
- Forensic terminal ledger — 0.0612
- Quiet civic analytics — 0.0864

**Proposed selection: Swiss editorial risk console**, subject to review.

- **Design movement:** Swiss editorial information design applied to a restrained compliance operations console.
- **Core principles:** separate observations from conclusions; make evidence traceable; prioritize legibility over decorative density; make analyst actions and their history explicit.
- **Color philosophy:** deep ink and warm neutral surfaces support sustained review; one ownable muted teal signals the product identity; amber/red are reserved for configurable alert severity and never used as a verdict color.
- **Layout paradigm:** a persistent, narrow navigation rail with a broad, resizable evidence workspace; investigation lists lead into a transaction-and-history detail pane rather than a dashboard of equal-weight cards.
- **Signature elements:** rule-parameter chips, transaction-ID evidence rails, and a persistent neutral “alert ≠ confirmed finding” state label.
- **Interaction philosophy:** progressive disclosure from alert explanation to source transactions to case history; each analyst action records its rationale and timestamp.
- **Animation:** minimal, short transitions for pane changes only; no animated risk scores or attention-grabbing motion.
- **Typography system:** clear system sans-serif for interface text with tabular numerals and a restrained monospace face for identifiers, timestamps, and SQL-derived values.
- **Brand essence:** an evidence-first workbench for AML analysts that connects explainable monitoring leads to auditable investigation actions; precise, restrained, accountable.
- **Brand voice:** concise, non-accusatory and explicit about uncertainty. Examples: “Review the evidence; record the rationale.” “An alert is a lead—not a finding.”
- **Wordmark concept:** a compact ledger-column mark crossed by an evidence-link line, paired with a custom-spaced wordmark; no decorative hero artwork is needed for this internal tool.
- **Signature brand color:** muted teal, reserved for navigation and selected/linked evidence states.

## Build and delivery approach

Use Python 3.12-compatible dependency declarations and a lockable install path. Run the application from the repository checkout; run pytest against temporary SQLite databases. When the Streamlit interface milestone begins, register Python diagnostics, configure Preview to the actual Streamlit port (proposed 8501), add the required `/manus-routes.json` declaration, start the service on `0.0.0.0`, and verify the listener/route manifest. The WebDev project currently has Preview port 3000 and no language diagnostics registered; neither will be changed before plan approval.

For each approved milestone: implement only its scope, run the relevant automated tests, inspect `git diff` and status, then commit/push only the verified milestone to the approved feature branch. Never force-push or write to `main`. Report changed files, actual test output, open issues, commit SHA (if committed), and push verification (if pushed). If the KYC project's exact branch, commit, or test conventions are supplied, use them instead of the proposed defaults.
