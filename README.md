# Measurement Reliability SQL Lab

This repository contains SQL case studies for product analytics, behavioral data quality, experimentation, attribution, and measurement reliability.

The goal is not only to calculate product metrics, but to validate whether those metrics are trustworthy enough for decision-making. Each query is designed around common failure modes in behavioral data pipelines, such as missing events, duplicate events, attribution mismatches, funnel breakage, sample ratio mismatch, and segment-level anomalies.

## Why this repository matters

Product metrics are often treated as ground truth. In practice, however, behavioral metrics are measured signals generated through event instrumentation, tracking specifications, attribution rules, SDK behavior, processing logic, and analytics pipelines.

This repository focuses on one core question:

> Did user behavior actually change, or did the measurement system fail?

## Topics covered

- Event grain and basic aggregation
- Conversion metrics
- Funnel analysis
- Duplicate event detection
- Missing tracking and data quality checks
- Attribution and marketing channel validation
- Session and user journey analysis
- Cohort and retention analysis
- Experimentation and A/B test SQL
- Anomaly monitoring and segment contribution analysis

## Repository structure

```text
measurement-reliability-sql/
├── README.md
├── data/
├── schemas/
│   └── event_schema.md
├── sql/
│   ├── 01_event_grain_basic_aggregation.sql
│   ├── 02_conversion_metrics.sql
│   ├── 03_funnel_analysis.sql
│   ├── 04_deduplication.sql
│   ├── 05_missing_tracking_data_quality.sql
│   ├── 06_attribution_marketing_channel.sql
│   ├── 07_session_user_journey.sql
│   ├── 08_cohort_retention.sql
│   ├── 09_experimentation_ab_test.sql
│   └── 10_anomaly_monitoring_segment_contribution.sql
├── notes/
│   ├── sql_patterns.md
│   ├── mistakes_and_fixes.md
│   └── interview_explanations.md
└── case_studies/
    └── natural_search_tracking_drop.md



## Data note

All schemas, tables, and examples in this repository are synthetic and anonymized. They are designed to represent common behavioral analytics patterns in global digital products without exposing any confidential company data.

## Core framing

A product metric is not the behavior itself. It is an observed measurement produced by a tracking and analytics system. Before using a metric for decision-making, we need to validate whether the metric is complete, consistent, correctly classified, and stable across platforms, markets, and user journeys.
