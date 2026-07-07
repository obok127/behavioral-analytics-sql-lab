
WITH extracted AS (
    SELECT
        event_id,
        user_id,
        session_id,
        event_timestamp,
        page_name,
        page_url,
        referrer_url,
        marketing_channel,
        raw_campaign_id,
        processed_campaign_id

        -- Extract campaign_id from query string: ?cid=xxx or &cid=xxx
        NULLIF(
            substring(page_url FROM '[?&]cid=([^&#]+)'),
            ''
        ) AS cid_from_query,

        -- Extract campaign_id from hash fragment: #cid=xxx or &cid=xxx
        NuLLIF(
            substring(page_url FROM '[#&]cid=([^&#]+)'),
            ''
        ) AS cid_from_hash,

        -- Extract campaign_id from JSON payload
        NULLIF(raw_payload ->> 'campaign_id', '') AS cid_from_payload,

        NULLIF(raw_payload ->> 'utm_campaign', '') AS utm_campaign_from_payload,
        NULLIF(raw_payload ->> 'utm_source', '') AS utm_source_from_payload,
        NULLIF(raw_payload ->> 'utm_medium','') AS utm_source_from_payload
    
    FROM raw_events
)

SELECT
    event_id,
    user_id,
    session_id,
    event_timestamp,
    page_name,
    marketing_channel,
    cid_from_query,
    cid_from_hash,
    cid_from_payload,
    utm_campaign_from_payload,
    utm_source_from_payload,
    utm_medium_from_payload,
    raw_campaign_id,
    processed_campaign_id,

    CASE
        WHEN cid_from_query IS NOT NULL THEN 'query_param'
        WHEN cid_from_hash IS NOT NULL THEN 'hash_param'
        WHEN cid_from_payload IS NOT NULL THEN 'payload'
        WHEN raw_campaign_id IS NOT NULL THEN 'raw_campaign_field'
        WHEN processed_campaign_id IS NOT NULL THEN 'processed_campaign_field'
        ELSE 'no_campaign_id_found'
    END AS first_detected_campaign_source

FROM extracted
ORDER BY event_timestamp;
