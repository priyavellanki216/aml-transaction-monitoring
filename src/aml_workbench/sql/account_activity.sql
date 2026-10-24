WITH account_events AS (
    SELECT
        source_account_id AS account_id,
        'outgoing' AS direction,
        amount_minor
    FROM transactions
    UNION ALL
    SELECT
        destination_account_id AS account_id,
        'incoming' AS direction,
        amount_minor
    FROM transactions
)
SELECT
    a.account_id,
    COALESCE(SUM(CASE WHEN e.direction = 'outgoing' THEN 1 ELSE 0 END), 0)
        AS outgoing_count,
    COALESCE(SUM(CASE WHEN e.direction = 'incoming' THEN 1 ELSE 0 END), 0)
        AS incoming_count,
    COALESCE(SUM(CASE WHEN e.direction = 'outgoing' THEN e.amount_minor ELSE 0 END), 0)
        AS outgoing_amount_minor,
    COALESCE(SUM(CASE WHEN e.direction = 'incoming' THEN e.amount_minor ELSE 0 END), 0)
        AS incoming_amount_minor
FROM accounts AS a
LEFT JOIN account_events AS e ON e.account_id = a.account_id
GROUP BY a.account_id
ORDER BY a.account_id;
