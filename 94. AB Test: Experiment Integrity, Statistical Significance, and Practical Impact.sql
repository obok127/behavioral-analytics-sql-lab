WITH params AS (
    SELECT
        TIMESTAMP('2026-08-20 00:00:00') AS analysis_end,
        0.50 AS expected_control_share,
        0.50 AS expected_treatment_share,
        0.002 AS min_practical_uplift
),

raw_assignment AS (
    SELECT
        ea.user_id,
        ea.variant,
        ea.assigned_at
    FROM experiment_assignments ea
    CROSS JOIN params p
    WHERE ea.experiment_name = 'new_order_ui'
      AND ea.assigned_at < p.analysis_end
),

assignment_audit AS (
    SELECT
        user_id,
        COUNT(*) AS assignment_rows,
        COUNT(DISTINCT variant) AS variant_count
    FROM raw_assignment
    GROUP BY user_id
),

ranked_assignment AS (
    SELECT
        ra.*,
        ROW_NUMBER() OVER (
            PARTITION BY ra.user_id
            ORDER BY ra.assigned_at, ra.variant
        ) AS rn
    FROM raw_assignment ra
),

first_assignment AS (
    SELECT
        r.user_id,
        r.variant,
        r.assigned_at,
        a.assignment_rows,
        a.variant_count
    FROM ranked_assignment r
    JOIN assignment_audit a
      ON r.user_id = a.user_id
    WHERE r.rn = 1
),

quality_summary AS (
    SELECT
        COUNT(*) AS total_assigned_users,

        SUM(
            CASE
                WHEN variant_count > 1 THEN 1
                ELSE 0
            END
        ) AS contaminated_users,

        SUM(
            CASE
                WHEN variant NOT IN ('control', 'treatment') THEN 1
                ELSE 0
            END
        ) AS unexpected_variant_users,

        SUM(
            CASE
                WHEN assigned_at + INTERVAL 7 DAY >
                     (SELECT analysis_end FROM params)
                THEN 1
                ELSE 0
            END
        ) AS immature_users

    FROM first_assignment
),

srm_counts AS (
    SELECT
        SUM(CASE WHEN variant = 'control' THEN 1 ELSE 0 END)
            AS control_n,

        SUM(CASE WHEN variant = 'treatment' THEN 1 ELSE 0 END)
            AS treatment_n

    FROM first_assignment
),

srm AS (
    SELECT
        s.control_n,
        s.treatment_n,

        POWER(
            s.control_n
            - (s.control_n + s.treatment_n)
              * p.expected_control_share,
            2
        )
        /
        NULLIF(
            (s.control_n + s.treatment_n)
            * p.expected_control_share,
            0
        )

        +

        POWER(
            s.treatment_n
            - (s.control_n + s.treatment_n)
              * p.expected_treatment_share,
            2
        )
        /
        NULLIF(
            (s.control_n + s.treatment_n)
            * p.expected_treatment_share,
            0
        ) AS srm_chi_square

    FROM srm_counts s
    CROSS JOIN params p
),

eligible_assignment AS (
    SELECT
        f.user_id,
        f.variant,
        f.assigned_at,
        f.variant_count
    FROM first_assignment f
    CROSS JOIN params p
    WHERE f.variant IN ('control', 'treatment')
      AND f.assigned_at + INTERVAL 7 DAY <= p.analysis_end
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

    FROM eligible_assignment a

    LEFT JOIN events e
      ON e.user_id = a.user_id
     AND e.event_name = 'order_submit'
     AND e.event_time >= a.assigned_at
     AND e.event_time < a.assigned_at + INTERVAL 7 DAY

    GROUP BY
        a.user_id,
        a.variant
),

variant_stats AS (
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
        MAX(
            CASE WHEN variant = 'control'
                 THEN users END
        ) AS control_n,

        MAX(
            CASE WHEN variant = 'control'
                 THEN conversions END
        ) AS control_conversions,

        MAX(
            CASE WHEN variant = 'control'
                 THEN conversion_rate END
        ) AS control_rate,

        MAX(
            CASE WHEN variant = 'treatment'
                 THEN users END
        ) AS treatment_n,

        MAX(
            CASE WHEN variant = 'treatment'
                 THEN conversions END
        ) AS treatment_conversions,

        MAX(
            CASE WHEN variant = 'treatment'
                 THEN conversion_rate END
        ) AS treatment_rate

    FROM variant_stats
),

effect_base AS (
    SELECT
        *,

        treatment_rate - control_rate
            AS absolute_uplift,

        (treatment_rate - control_rate)
        / NULLIF(control_rate, 0)
            AS relative_uplift,

        (
            control_conversions
            + treatment_conversions
        )
        /
        NULLIF(
            control_n + treatment_n,
            0
        ) AS pooled_rate

    FROM pivoted
),

standard_errors AS (
    SELECT
        *,

        SQRT(
            pooled_rate
            * (1 - pooled_rate)
            * (
                1.0 / control_n
                + 1.0 / treatment_n
            )
        ) AS se_h0,

        SQRT(
            control_rate
            * (1 - control_rate)
            / control_n

            +

            treatment_rate
            * (1 - treatment_rate)
            / treatment_n
        ) AS se_difference

    FROM effect_base
),

effect_result AS (
    SELECT
        *,

        absolute_uplift
        / NULLIF(se_h0, 0)
            AS z_stat,

        absolute_uplift
        - 1.96 * se_difference
            AS ci95_lower,

        absolute_uplift
        + 1.96 * se_difference
            AS ci95_upper

    FROM standard_errors
)

SELECT
    e.control_n,
    e.control_conversions,
    e.control_rate,

    e.treatment_n,
    e.treatment_conversions,
    e.treatment_rate,

    e.absolute_uplift,
    e.relative_uplift,

    e.se_h0,
    e.se_difference,
    e.z_stat,

    e.ci95_lower,
    e.ci95_upper,

    CASE
        WHEN ABS(e.z_stat) >= 1.96
        THEN 'significant'
        ELSE 'not significant'
    END AS statistical_significance,

    CASE
        WHEN e.absolute_uplift >= p.min_practical_uplift
        THEN 'practically meaningful'
        ELSE 'below practical threshold'
    END AS practical_significance,

    s.srm_chi_square,

    CASE
        WHEN s.srm_chi_square > 3.841
        THEN 'SRM detected'
        ELSE 'SRM not detected'
    END AS srm_status,

    q.contaminated_users,

    q.contaminated_users
        / NULLIF(q.total_assigned_users, 0)
        AS contamination_rate,

    q.immature_users,
    q.unexpected_variant_users

FROM effect_result e
CROSS JOIN srm s
CROSS JOIN quality_summary q
CROSS JOIN params p;
