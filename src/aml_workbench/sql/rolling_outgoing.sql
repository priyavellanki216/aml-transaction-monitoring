WITH normalized_events AS (
    SELECT
        transaction_id,
        source_account_id AS account_id,
        amount_minor,
        currency,
        timestamp_utc,
        CAST(strftime('%s', timestamp_utc) AS INTEGER) AS event_epoch
    FROM transactions
    WHERE currency = :currency
)
SELECT
    transaction_id,
    account_id,
    amount_minor,
    currency,
    timestamp_utc,
    COUNT(*) OVER (
        PARTITION BY account_id, currency
        ORDER BY event_epoch
        RANGE BETWEEN :window_seconds PRECEDING AND CURRENT ROW
    ) AS transaction_count_window,
    SUM(amount_minor) OVER (
        PARTITION BY account_id, currency
        ORDER BY event_epoch
        RANGE BETWEEN :window_seconds PRECEDING AND CURRENT ROW
    ) AS amount_minor_window
FROM normalized_events
ORDER BY account_id, event_epoch, transaction_id;
