PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS accounts (
    account_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    account_type TEXT NOT NULL CHECK (account_type IN ('personal', 'business')),
    opened_at_utc TEXT NOT NULL CHECK (
        length(opened_at_utc) = 25
        AND strftime('%Y-%m-%dT%H:%M:%S+00:00', opened_at_utc) = opened_at_utc
    ),
    country_code TEXT NOT NULL CHECK (length(country_code) = 2)
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    source_account_id TEXT NOT NULL REFERENCES accounts(account_id),
    destination_account_id TEXT NOT NULL REFERENCES accounts(account_id),
    amount_minor INTEGER NOT NULL CHECK (amount_minor > 0),
    currency TEXT NOT NULL CHECK (length(currency) = 3),
    timestamp_utc TEXT NOT NULL CHECK (
        length(timestamp_utc) = 25
        AND strftime('%Y-%m-%dT%H:%M:%S+00:00', timestamp_utc) = timestamp_utc
    ),
    description TEXT NOT NULL,
    scenario_id TEXT,
    test_ground_truth TEXT,
    CHECK (source_account_id <> destination_account_id),
    CHECK (
        (scenario_id IS NULL AND test_ground_truth IS NULL)
        OR (
            scenario_id IS NOT NULL
            AND test_ground_truth IS NOT NULL
            AND test_ground_truth IN ('positive', 'negative')
        )
    )
);

CREATE INDEX IF NOT EXISTS idx_transactions_source_time
    ON transactions (source_account_id, timestamp_utc, transaction_id);

CREATE INDEX IF NOT EXISTS idx_transactions_destination_time
    ON transactions (destination_account_id, timestamp_utc, transaction_id);

CREATE INDEX IF NOT EXISTS idx_transactions_scenario
    ON transactions (scenario_id, test_ground_truth);
