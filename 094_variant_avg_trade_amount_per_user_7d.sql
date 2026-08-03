-- 094. Average Trade Amount per Assigned User by Experiment Variant
-- Calculate each user's total trade amount during the 7 days
-- following their first assignment to the new_order_ui experiment.
-- Then calculate the average trade amount per assigned user for each variant.
-- Users with no trades are included with a trade amount of 0.

WITH assignment AS (
    SELECT
        user_id,
        variant,
        assigned_at
    FROM (
        SELECT
            ea.*,

            -- Assign a sequence number to each experiment assignment per user
            ROW_NUMBER() OVER (
                PARTITION BY experiment_name, user_id
                ORDER BY assigned_at, variant
            ) AS rn

        FROM experiment_assignments ea

        -- Include only assignments for the new_order_ui experiment
        WHERE experiment_name = 'new_order_ui'
    ) x

    -- Retain only each user's first experiment assignment
    WHERE rn = 1
),

user_metric AS (
    SELECT
        a.user_id,
        a.variant,

        -- Calculate the user's total executed trade amount
        -- during the 7-day window following assignment
        COALESCE(
            SUM(t.quantity * t.execution_price),
            0
        ) AS trade_amount_7d

    FROM assignment a

    -- Retain assigned users even if they did not execute any trades
    LEFT JOIN trades t
      ON t.user_id = a.user_id

     -- Include trades executed on or after the assignment time
     AND t.executed_at >= a.assigned_at

     -- Include trades executed before 7 days have passed
     AND t.executed_at < a.assigned_at + INTERVAL 7 DAY

    -- Create one row per assigned user
    GROUP BY
        a.user_id,
        a.variant
)

SELECT
    variant,

    -- Number of users assigned to each experiment variant
    COUNT(*) AS assigned_users,

    -- Average 7-day trade amount per assigned user,
    -- including users with no trades as 0
    AVG(trade_amount_7d) AS avg_trade_amount_7d

FROM user_metric

-- Return one row per experiment variant
GROUP BY variant;
