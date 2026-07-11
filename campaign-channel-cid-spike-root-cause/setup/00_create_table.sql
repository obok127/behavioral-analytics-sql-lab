DROP TABLE IF EXISTS raw_events CASCADE;

CREATE TABLE raw_events (
    event_id                TEXT PRIMARY KEY,
    user_id                 TEXT,
    session_id              TEXT,
    event_timestamp         TIMESTAMP NOT NULL,
    event_date              DATE NOT NULL,

    page_name               TEXT,
    page_url                TEXT,
    referrer_url            TEXT,
    event_name              TEXT,

    marketing_channel       TEXT,
    raw_campaign_id         TEXT,
    processed_campaign_id   TEXT,
    campaign_source         TEXT,
    campaign_medium         TEXT,

    raw_payload             JSONB NOT NULL DEFAULT '{}'::jsonb,

    source_file_name        TEXT,
    load_batch_id           TEXT,
    ingested_at             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_raw_payload_is_object
        CHECK (jsonb_typeof(raw_payload) = 'object'),

    CONSTRAINT chk_event_date_matches_timestamp
        CHECK (event_date = event_timestamp::date)
);

CREATE INDEX idx_raw_events_event_date
    ON raw_events (event_date);

CREATE INDEX idx_raw_events_session_id_timestamp
    ON raw_events (session_id, event_timestamp);

CREATE INDEX idx_raw_events_event_name
    ON raw_events (event_name);

CREATE INDEX idx_raw_events_marketing_channel
    ON raw_events (marketing_channel);

CREATE INDEX idx_raw_events_processed_campaign_id
    ON raw_events (processed_campaign_id);

CREATE INDEX idx_raw_events_raw_campaign_id
    ON raw_events (raw_campaign_id);

CREATE INDEX idx_raw_events_campaign_source_medium
    ON raw_events (campaign_source, campaign_medium);

CREATE INDEX idx_raw_events_raw_payload_gin
    ON raw_events USING GIN (raw_payload);
