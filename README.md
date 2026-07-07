# Daily SQL Practice for Measurement Reliability

![SQL](https://img.shields.io/badge/SQL-PostgreSQL%20%7C%20BigQuery%20%7C%20Snowflake-blue)
![Focus](https://img.shields.io/badge/Focus-Data%20Quality%20%26%20Root%20Cause%20Analysis-brightgreen)
![Status](https://img.shields.io/badge/Status-In%20Progress-yellow)

A portfolio-style SQL practice repository focused on **measurement reliability**, **behavioral event data quality**, and **root-cause analysis for analytics tracking issues**.

This repository is not a collection of basic SQL drills. Each scenario is designed as a realistic analytics engineering / product data investigation, where the goal is to diagnose why a metric changed, why tracking is inconsistent, or where a data pipeline failed.

---

## Why this repository exists

Modern product analytics depends on event data that is accurate, consistent, and interpretable. However, real-world tracking data is often noisy because of:

- inconsistent campaign parameters,
- deleted UI elements still firing events,
- bot or automation traffic,
- plaintext user identifier leakage,
- missing country or site-code mappings,
- user-agent based platform misclassification,
- delivery date drift across checkout journeys,
- raw payload fields not matching processed analytics dimensions.

This repository practices SQL as a diagnostic tool for answering one core question:

> **Can we trust this metric enough to make a business decision?**

---

## What this project demonstrates

This project is designed to show practical data skills beyond writing isolated queries.

| Area | What this repo demonstrates |
|---|---|
| SQL diagnostics | Window functions, CTEs, joins, aggregations, conditional logic, JSON extraction, ranking, and validation queries |
| Data quality | Missing values, unexpected overwrites, duplicate events, inconsistent identifiers, false positives, and coverage gaps |
| Product analytics | Session journeys, event sequencing, funnel context, platform segmentation, and campaign attribution checks |
| Root-cause analysis | Moving from symptom detection to source isolation and business impact measurement |
| Cross-platform SQL | Equivalent query patterns for PostgreSQL, BigQuery, and Snowflake |
| Portfolio communication | Each scenario is framed as a real analytics investigation, not just a coding exercise |

---

## Repository structure

```text
daily-sql-practice/
├── README.md
│
├── campaign-channel-cid-spike-root-cause/
├── deleted-button-still-firing-journey-trace/
├── bot-traffic-filtering-validation/
├── unencrypted-user-guid-collection/
├── missing-site-code-datastream-root-cause/
├── user-agent-origin-platform-validation/
└── delivery-date-drift-tracking/
```

Each scenario folder follows a consistent investigation pattern:

```text
scenario-name/
├── README.md
├── postgresql/
│   ├── 01_*.sql
│   ├── 02_*.sql
│   └── 10_*_summary.sql
├── bigquery/
│   ├── 01_*.sql
│   └── 10_*_summary.sql
└── snowflake/
    ├── 01_*.sql
    └── 10_*_summary.sql
```

The campaign-channel scenario also includes mock data generation and setup scripts:

```text
campaign-channel-cid-spike-root-cause/
├── schema.md
├── mock_data/
│   ├── generate_mock_events.py
│   ├── raw_events.csv
│   └── scenario_notes.md
└── setup/
    ├── 00_create_raw_events.sql
    ├── 01_load_mock_data_postgresql.sql
    ├── 02_create_staging_events.sql
    ├── 03_create_dimensions.sql
    ├── 04_create_fact_events.sql
    └── 05_validate_setup.sql
```

---

## Scenario catalog

### 1. Campaign Channel CID Spike Root Cause

Diagnoses a sudden spike in campaign-attributed traffic caused by inconsistent campaign ID extraction, source priority rules, or unexpected overwrites.

Key questions:

- Did campaign traffic actually increase, or did classification logic change?
- Which campaign ID source contributed most to the spike?
- Are URL parameters, raw payload fields, and processed campaign fields aligned?
- Did a processing rule overwrite the expected attribution value?

Representative queries:

- extract campaign IDs from URL and JSON payloads,
- compare campaign source priority,
- detect daily channel spikes,
- identify conflicting campaign sources within the same session,
- build a root-cause summary table.

---

### 2. Deleted Button Still Firing Journey Trace

Investigates cases where an event continues to fire even after the corresponding UI button was removed.

Key questions:

- Is the deleted button event still occurring after the removal date?
- Which pages, platforms, or app versions still send the event?
- Is the event coming from a hidden entry point, legacy code path, or reused tracking name?
- What user journey occurs immediately before and after the suspicious event?

Representative queries:

- detect post-removal event volume,
- trace previous and next events in a session,
- compare event sources by platform and app version,
- validate current UI inventory against observed events,
- classify likely source type.

---

### 3. Bot Traffic Filtering Validation

Validates whether bot filtering rules correctly remove automated traffic without damaging legitimate business metrics.

Key questions:

- Which user agents, sessions, or network clusters look suspicious?
- Are there high-frequency sessions or abnormal event velocities?
- Are filtering rules catching bot-like behavior?
- Are legitimate users being incorrectly filtered out?
- How much do business metrics change before and after filtering?

Representative queries:

- profile traffic by user agent,
- detect high-frequency sessions,
- compare bot-like vs. human-like journeys,
- measure metric impact before and after filtering,
- detect false positive filtering risk.

---

### 4. Unencrypted User GUID Collection

Audits whether user identifiers are being collected in plaintext instead of a hashed or encrypted format.

Key questions:

- Are plaintext user identifiers present in raw or processed fields?
- Which pages and events collect plaintext identifiers?
- Is the leakage specific to a platform, app version, or event type?
- Are hash formats consistent across events?
- What is the exposure rate of plaintext identifiers?

Representative queries:

- detect plaintext identifier patterns,
- compare raw vs. processed identifier fields,
- classify encryption status,
- trace first plaintext identifier occurrence,
- build an identifier security audit summary.

---

### 5. Missing Site Code Datastream Root Cause

Traces missing site-code values through raw payloads, preprocessing logic, country mappings, and datastream configuration.

Key questions:

- Which countries have missing site-code values?
- Is the site code missing in the raw payload or lost during processing?
- Are country-to-site-code mappings complete and valid?
- Are datastream IDs mapped to the expected countries?
- What downstream metrics are affected by missing site codes?

Representative queries:

- detect missing site codes by country,
- compare raw payload and processed fields,
- validate country mapping tables,
- detect mismatched datastream and country combinations,
- measure downstream metric impact.

---

### 6. User-Agent Origin Platform Validation

Validates whether raw platform values are correctly overwritten or classified based on user-agent logic.

Key questions:

- Does the raw platform value conflict with the user-agent string?
- Should a mobile web value be overwritten as app based on app-specific user-agent identifiers?
- Which pages or versions have platform overwrite failures?
- How does platform misclassification affect downstream metrics?

Representative queries:

- extract user-agent fields from raw payloads,
- detect raw platform and user-agent mismatches,
- validate user-agent based overwrite rules,
- compare raw vs. processed platform distributions,
- build an origin platform validation summary.

---

### 7. Delivery Date Drift Tracking

Checks whether estimated delivery date changes are captured consistently across product, cart, checkout, and confirmation journeys.

Key questions:

- Is the delivery date variable missing from payloads?
- Is delivery date captured on page load, CTA click, or both?
- Are delivery date formats consistent across pages?
- Can we detect delivery date drift within the same session?
- What is the metric impact of missing or inconsistent delivery date tracking?

Representative queries:

- check delivery date variable coverage by page and CTA,
- validate delivery date format consistency,
- detect EDD drift by session,
- simulate visit-level dimension persistence,
- build a delivery date drift quality summary.

---

## Common investigation workflow

Each scenario follows a 10-step diagnostic structure:

| Step | Purpose |
|---:|---|
| 01 | Extract the key field from raw payloads, URLs, or event attributes |
| 02 | Compare raw values against processed analytics fields |
| 03 | Detect abnormal volume, coverage gaps, or distribution changes |
| 04 | Compare before vs. after behavior or expected vs. observed outputs |
| 05 | Trace user/session journeys around the suspicious event |
| 06 | Segment by platform, country, page, version, or source |
| 07 | Validate business logic, mapping tables, or processing rules |
| 08 | Detect edge cases, overwrites, false positives, or leakage cases |
| 09 | Measure downstream business impact |
| 10 | Build a final root-cause or data-quality summary |

This structure is intentionally repetitive. The goal is to build the habit of moving from raw evidence to a defensible conclusion.

---

## How to use this repository

### Option 1: Read as a portfolio

Start with each scenario README to understand:

1. the business problem,
2. the data quality risk,
3. the SQL investigation path,
4. the final root-cause summary.

### Option 2: Practice SQL daily

Pick one scenario and run one query at a time.

Recommended order:

1. Read the scenario README.
2. Run query `01` to understand the raw data.
3. Run queries `02` to `04` to detect the symptom.
4. Run queries `05` to `08` to isolate the source.
5. Run query `09` to estimate impact.
6. Run query `10` to summarize the conclusion.

### Option 3: Compare SQL dialects

For each scenario, compare the same logic across:

- PostgreSQL,
- BigQuery,
- Snowflake.

This is useful for practicing how the same analytical logic changes across warehouse environments, especially for JSON extraction, date functions, window functions, and string handling.

---

## Example PostgreSQL setup

The campaign-channel scenario includes mock data and setup scripts.

```bash
cd campaign-channel-cid-spike-root-cause
```

Create raw tables and load mock data:

```sql
\i setup/00_create_raw_events.sql
\i setup/01_load_mock_data_postgresql.sql
```

Build staging, dimensions, and fact tables:

```sql
\i setup/02_create_staging_events.sql
\i setup/03_create_dimensions.sql
\i setup/04_create_fact_events.sql
\i setup/05_validate_setup.sql
```

Then run the diagnostic queries:

```sql
\i postgresql/01_extract_campaign_id_from_url_and_payload.sql
\i postgresql/02_check_campaign_id_source_priority.sql
\i postgresql/03_detect_campaign_channel_spike_by_day.sql
```

---

## Skills practiced

### SQL

- Common Table Expressions, or CTEs
- Window functions
- Date and time bucketing
- Conditional aggregation
- JSON and semi-structured data extraction
- Session-level journey analysis
- Before-and-after comparisons
- Ranking and contribution analysis
- Data quality summary tables

### Analytics engineering

- Raw-to-staging-to-fact modeling
- Dimension and fact separation
- Event taxonomy validation
- Processing rule validation
- Source priority logic
- Mapping table validation
- Cross-platform consistency checks

### Product data science

- Behavioral event reliability
- Campaign attribution sanity checks
- Funnel and journey diagnostics
- Metric impact analysis
- Bot filtering validation
- Privacy and identifier leakage audit

---

## Design principles

### 1. Start from the raw payload

Processed analytics fields can hide upstream problems. Each investigation starts by checking the raw event, URL parameter, user-agent, or payload field before trusting the final reporting dimension.

### 2. Compare expected vs. observed behavior

Most tracking issues are not visible from one row. They appear when observed data is compared against business logic, UI inventory, mapping tables, processing rules, or historical baselines.

### 3. Segment before concluding

A global metric spike is rarely global in cause. Each scenario segments by page, country, platform, app version, campaign source, datastream, or session path to isolate the failure point.

### 4. Measure business impact

The final goal is not just to find a bug. The goal is to estimate whether the issue changes decision-making, reporting, attribution, funnel analysis, or data governance risk.

### 5. End with a summary table

Every scenario ends with a query that produces a root-cause or data-quality summary. This makes the analysis easier to communicate to engineers, product managers, analytics teams, and stakeholders.

---

## Suggested progress tracker

| Scenario | PostgreSQL | BigQuery | Snowflake | Summary completed |
|---|---:|---:|---:|---:|
| Campaign Channel CID Spike Root Cause | ⬜ | ⬜ | ⬜ | ⬜ |
| Deleted Button Still Firing Journey Trace | ⬜ | ⬜ | ⬜ | ⬜ |
| Bot Traffic Filtering Validation | ⬜ | ⬜ | ⬜ | ⬜ |
| Unencrypted User GUID Collection | ⬜ | ⬜ | ⬜ | ⬜ |
| Missing Site Code Datastream Root Cause | ⬜ | ⬜ | ⬜ | ⬜ |
| User-Agent Origin Platform Validation | ⬜ | ⬜ | ⬜ | ⬜ |
| Delivery Date Drift Tracking | ⬜ | ⬜ | ⬜ | ⬜ |

---

## Portfolio positioning

This repository represents a practical analytics engineering and product data science skill set:

> I use SQL to investigate whether behavioral event data can be trusted for business decisions. My work focuses on validating raw payloads, processed analytics dimensions, attribution logic, platform classification, privacy-related identifier handling, and downstream metric impact.

The project is especially relevant for roles involving:

- Product Data Analyst,
- Product Data Scientist,
- Analytics Engineer,
- Data Quality Analyst,
- Experimentation Analyst,
- Digital Analytics Specialist,
- Measurement Reliability / Data Governance roles.

---

## Roadmap

Planned improvements:

- Add Docker-based local PostgreSQL environment.
- Add synthetic data generators for all scenarios.
- Add expected output tables for each query.
- Add dbt models for staging, dimensions, facts, and quality flags.
- Add automated SQL tests for data quality rules.
- Add dashboard mockups for issue monitoring.
- Add written case studies explaining the root-cause narrative for each scenario.

---

## Disclaimer

All data, scenarios, table names, and query examples in this repository are synthetic or generalized for learning and portfolio purposes. No confidential customer data or proprietary implementation details are included.
