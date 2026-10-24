# Milestone 1 Data Dictionary

The included generator creates fictional accounts and transfers only. It does not ingest customer, bank, or public-record data. Stable IDs and fixed scenario timestamps make the seeded fixtures reproducible; the seed affects account metadata and background transfers.

## Accounts

| Field | Meaning |
|---|---|
| `account_id` | Stable synthetic account identifier, such as `ACC-0001`. |
| `customer_id` | Synthetic customer key; no real identity information is included. |
| `account_type` | Synthetic category: `personal` or `business`. |
| `opened_at_utc` | ISO-8601 timestamp with an explicit UTC offset. |
| `country_code` | Synthetic two-letter country code; it is not evidence of a real customer's location. |

## Transactions

| Field | Meaning |
|---|---|
| `transaction_id` | Stable synthetic transaction identifier. |
| `source_account_id` | Account from which the transfer is modeled as sent. |
| `destination_account_id` | Account to which the transfer is modeled as sent. |
| `amount_minor` | Positive integer amount in the smallest currency unit; for USD this is cents. SQL sums this integer field to avoid floating-point money arithmetic. |
| `currency` | Three-letter currency code; current fixtures use USD. |
| `timestamp_utc` | ISO-8601 event time normalized to UTC with second precision. |
| `description` | Synthetic, non-evidentiary fixture description. |
| `scenario_id` | Named test scenario for seeded fixtures; null for unlabeled background transfers. |
| `test_ground_truth` | `positive` or `negative` only for named test scenarios; null for background transfers. This is an automated-test oracle, not a confirmed real-world AML finding. |

## SQL time-window semantics

Rolling outgoing metrics group by source account and currency. The SQLite window includes events from exactly `window_seconds` before the current event through the current event, inclusive at both ends. The input timestamps use the exact second-precision format `YYYY-MM-DDTHH:MM:SS+00:00`; the loader normalizes UTC timestamps and the schema rejects naive, malformed, fractional-second, or non-UTC-offset values. SQL converts the validated text to epoch seconds. The public helper accepts integer windows from 1 second through 365 days.

The threshold-adjacent positive fixture is $9,995, five dollars below an arbitrary $10,000 test reference used solely to seed later rule tests. No jurisdictional thresholds, customer risk profiles, behavior baselines, or real payment rails are represented.

## Limitations

Synthetic scenarios are intentionally small and do not model all transaction products, currencies, settlement states, customer relationships, jurisdiction-specific reporting obligations, or adversarial behavior. A seeded positive scenario is not proof of suspicious activity; a negative scenario is not proof that comparable real-world activity is benign. No false-positive, missed-detection, or operational-performance rate is implied by this data.
