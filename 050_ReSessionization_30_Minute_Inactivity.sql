-- Re-sessionize user events using a 30-minute inactivity threshold.
-- Do not rely on the existing session_id.
-- A new session starts when:
--   1) the event is the user's first event, or
--   2) more than 30 minutes have passed since the previous event.
-- Assign session numbers starting from 1 for each user.

WITH with_prev AS (
    SELECT
        e.*,

        -- Get the previous event timestamp for each user.
        -- event_id is used as a tie-breaker when multiple events
        -- have the same event_time.
        LAG(event_time) OVER (
            PARTITION BY user_id
            ORDER BY event_time, event_id
        ) AS prev_event_time

    FROM events e
),

flags AS (
    SELECT
        *,

        -- Mark the start of a new session.
        -- The first event always starts a session.
        -- A gap greater than 30 minutes also starts a new session.
        CASE
            WHEN prev_event_time IS NULL
              OR event_time > prev_event_time + INTERVAL 30 MINUTE
            THEN 1
            ELSE 0
        END AS new_session_flag

    FROM with_prev
)

SELECT
    event_id,
    user_id,
    event_time,

    -- Cumulatively sum the session-start flags within each user.
    -- This assigns session numbers starting from 1.
    SUM(new_session_flag) OVER (
        PARTITION BY user_id
        ORDER BY event_time, event_id
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS derived_session_number

FROM flags;
