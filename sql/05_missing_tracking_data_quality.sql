-- ============================================================
-- 05. Missing Tracking & Data Quality
-- ============================================================
-- Purpose:
--   Validate whether observed product metrics are affected by
--   missing tracking fields, unspecified channels, or broken
--   event instrumentation.
--
-- Core question:
--   Did user behavior change, or did the measurement system fail?
--
-- Table:
--   synthetic_events
-- ============================================================


-- ============================================================
-- Problem 041: Calculate tracking_code null rate
-- Grain:
--   Overall event-level aggregation
-- Why it matters:
--   A missing tracking_code may indicate that attribution or campaign
--   classification cannot be trusted.
-- ============================================================

SELECT
    COUNT(*) AS total_events,
    SUM(CASE WHEN tracking_code IS NULL THEN 1 ELSE 0 END) AS missing_tracking_code_events,
    1.0 * SUM(CASE WHEN tracking_code IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_tracking_code_rate
FROM synthetic_events;


-- ============================================================
-- Problem 042: Calculate campaign_id null rate
-- Grain:
--   Overall event-level aggregation
-- Why it matters:
--   Missing campaign_id values may break campaign-level performance
--   reporting and attribution analysis.
-- ============================================================

SELECT
    COUNT(*) AS total_events,
    SUM(CASE WHEN campaign_id IS NULL THEN 1 ELSE 0 END) AS missing_campaign_id_events,
    1.0 * SUM(CASE WHEN campaign_id IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_campaign_id_rate
FROM synthetic_events;


-- ============================================================
-- Problem 043: Calculate unspecified traffic_source rate
-- Grain:
--   Overall event-level aggregation
-- Why it matters:
--   A spike in unspecified traffic_source may suggest classification
--   failure rather than a real shift in user acquisition.
-- ============================================================

SELECT
    COUNT(*) AS total_events,
    SUM(CASE WHEN traffic_source IS NULL OR traffic_source = 'unspecified' THEN 1 ELSE 0 END) AS unspecified_traffic_source_events,
    1.0 * SUM(CASE WHEN traffic_source IS NULL OR traffic_source = 'unspecified' THEN 1 ELSE 0 END) / COUNT(*) AS unspecified_traffic_source_rate
FROM synthetic_events;


-- ============================================================
-- Problem 044: Calculate media_source null rate
-- Grain:
--   Overall event-level aggregation
-- Why it matters:
--   Missing upstream attribution source values can create mismatches
--   between attribution platforms and analytics platforms.
-- ============================================================

SELECT
    COUNT(*) AS total_events,
    SUM(CASE WHEN media_source IS NULL THEN 1 ELSE 0 END) AS missing_media_source_events,
    1.0 * SUM(CASE WHEN media_source IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_media_source_rate
FROM synthetic_events;


-- ============================================================
-- Problem 045: Calculate product_id null rate
-- Grain:
--   Overall product-related event aggregation
-- Why it matters:
--   Product-level analysis becomes unreliable when product_id is missing
--   from product-related events.
-- ============================================================

SELECT
    COUNT(*) AS product_related_events,
    SUM(CASE WHEN product_id IS NULL THEN 1 ELSE 0 END) AS missing_product_id_events,
    1.0 * SUM(CASE WHEN product_id IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_product_id_rate
FROM synthetic_events
WHERE event_name IN ('product_view', 'add_to_cart', 'checkout_start', 'purchase');


-- ============================================================
-- Problem 046: Find purchase events with missing order_id
-- Grain:
--   Purchase event level
-- Why it matters:
--   Purchase events without order_id cannot be reliably deduplicated
--   or reconciled with order systems.
-- ============================================================

SELECT
    event_date,
    event_timestamp,
    user_id,
    session_id,
    platform,
    market,
    order_id,
    revenue
FROM synthetic_events
WHERE event_name = 'purchase'
  AND order_id IS NULL;


-- ============================================================
-- Problem 047: Find events with user_id but missing session_id
-- Grain:
--   Event level
-- Why it matters:
--   Missing session_id can break session-level funnel analysis and
--   user journey reconstruction.
-- ============================================================

SELECT
    event_date,
    event_timestamp,
    user_id,
    session_id,
    event_name,
    platform,
    market
FROM synthetic_events
WHERE user_id IS NOT NULL
  AND session_id IS NULL;


-- ============================================================
-- Problem 048: Find events with page_name but missing page_url
-- Grain:
--   Page event level
-- Why it matters:
--   Missing page_url makes it harder to validate whether page-level
--   tracking matches the intended page taxonomy.
-- ============================================================

SELECT
    event_date,
    event_timestamp,
    user_id,
    session_id,
    event_name,
    page_name,
    page_url,
    platform,
    market
FROM synthetic_events
WHERE page_name IS NOT NULL
  AND page_url IS NULL;


-- ============================================================
-- Problem 049: Calculate missing tracking rate by market
-- Grain:
--   market-level event aggregation
-- Why it matters:
--   Concentration in a specific market may indicate regional
--   implementation drift or market-specific tracking failure.
-- ============================================================

SELECT
    market,
    COUNT(*) AS total_events,
    SUM(CASE WHEN tracking_code IS NULL THEN 1 ELSE 0 END) AS missing_tracking_code_events,
    1.0 * SUM(CASE WHEN tracking_code IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_tracking_code_rate
FROM synthetic_events
GROUP BY market
ORDER BY missing_tracking_code_rate DESC;


-- ============================================================
-- Problem 050: Calculate missing tracking rate by platform
-- Grain:
--   platform-level event aggregation
-- Why it matters:
--   Platform concentration helps distinguish product behavior changes
--   from web, iOS, or Android instrumentation issues.
-- ============================================================

SELECT
    platform,
    COUNT(*) AS total_events,
    SUM(CASE WHEN tracking_code IS NULL THEN 1 ELSE 0 END) AS missing_tracking_code_events,
    1.0 * SUM(CASE WHEN tracking_code IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_tracking_code_rate
FROM synthetic_events
GROUP BY platform
ORDER BY missing_tracking_code_rate DESC;
