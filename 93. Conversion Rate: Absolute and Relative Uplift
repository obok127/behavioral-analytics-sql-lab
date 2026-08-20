WITH assignment AS (
    SELECT
        user_id,
        variant,
        assigned_at
    FROM (
        SELECT
            ea.*,
            ROW_NUMBER() OVER (
                PARTITION BY experiment_name, user_id
                ORDER BY assigned_at
            ) AS rn
        FROM experiment_assignments ea
        WHERE experiment_name = 'new_order_ui'
    ) x
    WHERE rn = 1
),

user_metric AS (
    SELECT
        a.user_id,
        a.variant,
        MAX(
            CASE
                WHEN e.event_id IS NOT NULL THEN 1
                ELSE 0
            END
        ) AS converted_7d
    FROM assignment a
    LEFT JOIN events e
        ON e.user_id = a.user_id
       AND e.event_name = 'order_submit'
       AND e.event_time >= a.assigned_at
       AND e.event_time < a.assigned_at + INTERVAL 7 DAY
    GROUP BY
        a.user_id,
        a.variant
),

rates AS (
    SELECT
        variant,
        COUNT(*) AS users,
        SUM(converted_7d) AS conversions,
        AVG(converted_7d) AS conversion_rate
    FROM user_metric
    GROUP BY variant
),

pivoted AS (
    SELECT
        MAX(CASE WHEN variant = 'control'
                 THEN conversion_rate END) AS control_rate,
        MAX(CASE WHEN variant = 'treatment'
                 THEN conversion_rate END) AS treatment_rate
    FROM rates
)

SELECT
    control_rate,
    treatment_rate,
    treatment_rate - control_rate AS absolute_uplift,
    (treatment_rate - control_rate)
        / NULLIF(control_rate, 0) AS relative_uplift
FROM pivoted;
