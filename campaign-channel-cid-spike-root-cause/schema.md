# Schema - Campaign Channel CID Spike Root Cause

This scenario uses a synthetic event table to investigate a suddem marketing channel spike.

## Table: raw_events

| Column | Type | Description |
|---|---|---|
| event_id | TEXT | Synthetic event ID |
| user_id | TEXT | Synthetic user ID |
| session_id | TEXT | Synthetic session ID |
| event_timestamp | TIMESTAMP | Event timestamp |
| event_date | DATE | Event date |
| page_name | TEXT | Page where the event occurred |
| page_url | TEXT | Anonymized page URL |
| referrer_url | TEXT | Anonymized referrer URL |
| event_name | TEXT | Event name |
| marketing_channel | TEXT | Processed marketing channel |
| raw_campaign_id | TEXT | Raw campaign ID before processing |
| processed_campaign_id | TEXT | Final processed campaign ID |
| campaign_source | TEXT | Campaign source |
| campaign_medium | TEXT | Campaign medium |
| raw_payload | JSONB | Raw event payload |

## Security Note

All identifires, URLs, campaign values, and business logic are synthetic and anonymized.