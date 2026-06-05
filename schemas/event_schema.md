```md
# Synthetic Event Schema

This project uses a synthetic event-level dataset designed to represent behavioral analytics data from a global ecommerce product.

The schema is intentionally generic and anonymized. It is designed for SQL practice around product analytics, measurement reliability, attribution validation, experimentation, and behavioral data quality.

## Table: synthetic_events

| Column | Type | Description |
|---|---|---|
| event_date | DATE | Date of the event |
| event_timestamp | TIMESTAMP | Timestamp when the event occurred |
| user_id | STRING | Anonymous user identifier |
| session_id | STRING | Anonymous session identifier |
| event_name | STRING | Name of the behavioral event |
| market | STRING | Anonymized market code |
| platform | STRING | Web, iOS, or Android |
| app_version | STRING | Application version |
| page_name | STRING | Name of the page or screen |
| page_url | STRING | URL or screen path |
| traffic_source | STRING | Classified marketing channel |
| media_source | STRING | Upstream attribution source |
| campaign_id | STRING | Campaign identifier |
| tracking_code | STRING | Tracking code from landing URL or deep link |
| product_id | STRING | Product identifier |
| product_category | STRING | Product category |
| order_id | STRING | Order identifier |
| revenue | FLOAT | Purchase revenue |
| experiment_id | STRING | Experiment identifier |
| variant | STRING | Experiment group, such as control or treatment |

## Event examples

| event_name | Description |
|---|---|
| page_view | User viewed a page or screen |
| product_view | User viewed a product detail page |
| add_to_cart | User added a product to cart |
| checkout_start | User started checkout |
| purchase | User completed purchase |
| login | User logged in |
| search | User performed a search |
| app_open | User opened the app |

## Measurement reliability questions

This schema supports SQL checks for questions such as:

1. Are required tracking fields missing?
2. Are events duplicated?
3. Are marketing channels classified correctly?
4. Are funnel steps recorded in the expected order?
5. Are conversion metrics distorted by missing or duplicate events?
6. Are anomalies concentrated in specific markets, platforms, app versions, or traffic sources?
7. Are experiment groups balanced before comparing outcomes?
