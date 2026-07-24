WITH weekly_sales AS (
    SELECT
        retailer_id,
        store_id,
        DATE_TRUNC('week', sales_date) AS week_start,
        SUM(sales_amount) AS current_week_sales
    FROM daily_sales
    GROUP BY
        retailer_id,
        store_id,
        DATE_TRUNC('week', sales_date)
),

sales_with_previous_week AS (
    SELECT
        retailer_id,
        store_id,
        week_start,
        current_week_sales,
        LAG(current_week_sales) OVER (
            PARTITION BY retailer_id, store_id
            ORDER BY week_start
        ) AS previous_week_sales
    FROM weekly_sales
)

SELECT
    retailer_id,
    store_id,
    week_start,
    current_week_sales,
    previous_week_sales,
    current_week_sales - previous_week_sales AS sales_change,
    ROUND(
        100.0 * (current_week_sales - previous_week_sales)
        / NULLIF(previous_week_sales, 0),
        2
    ) AS wow_growth_pct
FROM sales_with_previous_week
ORDER BY
    retailer_id,
    store_id,
    week_start;
