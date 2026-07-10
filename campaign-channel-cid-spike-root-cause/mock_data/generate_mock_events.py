"""
generate_mock_events.py

Synthetic raw event generator for:
    campaign-channel-cid-spike-root-cause

Purpose:
    This script does NOT detect anomalies.
    It generates a realistic raw_events.csv so SQL queries can investigate:
      1. campaign/channel daily spike
      2. URL cid / hash cid / payload campaign / raw field extraction
      3. source-priority mistakes in metric-processing logic
      4. processed campaign values with no raw evidence
      5. internal navigation cid contamination
      6. deeplink campaign evidence being incorrectly overridden by URL cid
      7. campaign persistence behavior across a session
      8. root-cause contribution by scenario/page/platform/release

Target raw table contract:
    raw_events (
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
        ingested_at             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    )

Design principle:
    Python is the exam writer. SQL is the exam solver.
    The generator creates realistic raw evidence and intentional processing defects.
    SQL should first infer issues from observable fields, then use raw_payload.qa_truth
    only for final validation.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable, TypeVar
from urllib.parse import urlencode


OUTPUT_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_FILE = OUTPUT_DIR / "raw_events.csv"

DEFAULT_SEED = 42
DEFAULT_START_DATE = "2026-06-24"
DEFAULT_BASELINE_DAYS = 7
DEFAULT_SPIKE_DAYS = 4
DEFAULT_POST_DAYS = 3

BASE_URL = "https://example.com"
APP_IDENTIFIER = "DemoRetailApp"
SPIKE_CAMPAIGN_ID = "cmp_spike_999"

PAGE_SEQUENCE = [
    ("home", "/home"),
    ("landing", "/landing"),
    ("product_detail", "/product/product-alpha"),
    ("cart", "/cart"),
    ("checkout", "/checkout"),
    ("order_confirmation", "/order-confirmation"),
]

EVENT_BY_PAGE = {
    "home": ["page_view", "hero_banner_click", "nav_click"],
    "landing": ["page_view", "cta_click", "product_click"],
    "product_detail": ["page_view", "product_view", "add_to_cart"],
    "cart": ["page_view", "checkout_start", "remove_from_cart"],
    "checkout": ["page_view", "payment_start", "purchase"],
    "order_confirmation": ["page_view", "purchase"],
}

REFERRERS = {
    "direct": "",
    "organic_search": "https://search.example.com/search?q=product-alpha",
    "referral": "https://partner.example.com/deals",
    "paid_social": "https://social.example.com/ad/click",
    "paid_search": "https://ad.example.com/click",
    "email": "https://mail.example.com/campaign",
    "affiliate": "https://affiliate.example.com/promo",
}

USER_AGENTS = {
    "web": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) Safari/605.1.15",
    ],
    "mobile_web": [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) Mobile Safari/604.1",
        "Mozilla/5.0 (Linux; Android 14) Chrome/126.0 Mobile Safari/537.36",
    ],
    "app_webview": [
        f"Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/126.0 Mobile Safari/537.36 {APP_IDENTIFIER}/1.0.143",
        f"Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 {APP_IDENTIFIER}/1.0.143",
    ],
}


@dataclass(frozen=True)
class Campaign:
    campaign_id: str
    channel: str
    source: str
    medium: str
    name: str


@dataclass(frozen=True)
class Evidence:
    """Raw campaign evidence available on a single hit before processing."""

    url_cid: str | None = None
    hash_cid: str | None = None
    payload_campaign_id: str | None = None
    raw_field_campaign_id: str | None = None
    deeplink_cid: str | None = None
    utm_source: str | None = None
    utm_medium: str | None = None
    utm_campaign: str | None = None

    def primary_raw_campaign_id(self) -> str:
        """
        Column-level raw_campaign_id intentionally represents only a raw field.
        Other evidence types live inside page_url or raw_payload.campaign_candidates.
        """
        return self.raw_field_campaign_id or ""

    def has_any_campaign_evidence(self) -> bool:
        return any(
            [
                self.url_cid,
                self.hash_cid,
                self.payload_campaign_id,
                self.raw_field_campaign_id,
                self.deeplink_cid,
                self.utm_source,
                self.utm_medium,
                self.utm_campaign,
            ]
        )


@dataclass(frozen=True)
class ProcessedResult:
    campaign_id: str | None
    channel: str
    source: str
    medium: str
    reason: str


@dataclass(frozen=True)
class Scenario:
    scenario_type: str
    true_channel: str
    true_campaign_id: str | None
    evidence_mode: str
    anomaly_type: str | None
    root_cause_label: str
    preferred_platform: str | None = None


CAMPAIGNS = {
    "cmp_summer_001": Campaign("cmp_summer_001", "paid_search", "search_engine", "cpc", "summer_sale"),
    "cmp_brand_002": Campaign("cmp_brand_002", "paid_search", "search_engine", "cpc", "brand_search"),
    "cmp_social_003": Campaign("cmp_social_003", "paid_social", "social_network", "paid_social", "retargeting_social"),
    "cmp_email_004": Campaign("cmp_email_004", "email", "crm", "email", "july_newsletter"),
    "cmp_affiliate_005": Campaign("cmp_affiliate_005", "affiliate", "partner", "affiliate", "affiliate_deal"),
    "cmp_organic_006": Campaign("cmp_organic_006", "organic_search", "search_engine", "organic", "organic_search"),
    SPIKE_CAMPAIGN_ID: Campaign(SPIKE_CAMPAIGN_ID, "paid_search", "search_engine", "cpc", "spike_campaign"),
}

BASELINE_SCENARIOS = [
    (Scenario("normal_direct", "direct", None, "none", None, "normal_direct"), 22),
    (Scenario("normal_organic", "organic_search", "cmp_organic_006", "utm_only", None, "normal_organic"), 15),
    (Scenario("normal_referral", "referral", None, "none", None, "normal_referral"), 9),
    (Scenario("normal_paid_search_query_cid", "paid_search", "cmp_summer_001", "query_param", None, "normal_paid_search"), 13),
    (Scenario("normal_paid_search_payload", "paid_search", "cmp_brand_002", "payload", None, "normal_paid_search"), 8),
    (Scenario("normal_paid_social_deeplink", "paid_social", "cmp_social_003", "deeplink_payload", None, "normal_paid_social", "app_webview"), 9),
    (Scenario("normal_email_payload", "email", "cmp_email_004", "payload", None, "normal_email"), 9),
    (Scenario("normal_affiliate_hash", "affiliate", "cmp_affiliate_005", "hash_param", None, "normal_affiliate"), 6),
    (Scenario("missing_processed_campaign", "paid_search", "cmp_summer_001", "query_param", "missing_processed_campaign", "background_processing_defect"), 2),
    (Scenario("hash_param_ignored", "affiliate", "cmp_affiliate_005", "hash_param", "hash_param_ignored", "background_processing_defect"), 1),
]

SPIKE_SCENARIOS = [
    (Scenario("internal_cid_contamination_direct", "direct", None, "none", "internal_cid_contamination", "internal_url_cid_contamination"), 22),
    (Scenario("internal_cid_contamination_organic", "organic_search", "cmp_organic_006", "utm_only", "internal_cid_contamination", "internal_url_cid_contamination"), 16),
    (Scenario("internal_cid_contamination_social", "paid_social", "cmp_social_003", "deeplink_payload", "internal_cid_contamination", "internal_url_cid_contamination", "app_webview"), 13),
    (Scenario("deeplink_lost_to_url_cid", "paid_social", "cmp_social_003", "deeplink_payload", "deeplink_overwritten_by_url_cid", "source_priority_bug", "app_webview"), 14),
    (Scenario("processed_only_spike", "direct", None, "none", "processed_only_without_raw_evidence", "processed_only_without_raw_evidence"), 9),
    (Scenario("real_paid_search_spike", "paid_search", SPIKE_CAMPAIGN_ID, "query_param", None, "true_paid_search_growth"), 15),
    (Scenario("normal_paid_search_during_spike", "paid_search", "cmp_brand_002", "query_param", None, "normal_paid_search"), 5),
    (Scenario("normal_direct_during_spike", "direct", None, "none", None, "normal_direct"), 4),
    (Scenario("wrong_priority_output", "paid_search", "cmp_summer_001", "multi_conflict", "wrong_priority_output", "background_processing_defect"), 2),
]

POST_SCENARIOS = [
    (Scenario("internal_cid_contamination_direct", "direct", None, "none", "internal_cid_contamination", "internal_url_cid_contamination"), 7),
    (Scenario("deeplink_lost_to_url_cid", "paid_social", "cmp_social_003", "deeplink_payload", "deeplink_overwritten_by_url_cid", "source_priority_bug", "app_webview"), 4),
    (Scenario("processed_only_spike", "direct", None, "none", "processed_only_without_raw_evidence", "processed_only_without_raw_evidence"), 2),
    (Scenario("normal_direct", "direct", None, "none", None, "normal_direct"), 20),
    (Scenario("normal_organic", "organic_search", "cmp_organic_006", "utm_only", None, "normal_organic"), 15),
    (Scenario("normal_paid_search_query_cid", "paid_search", "cmp_summer_001", "query_param", None, "normal_paid_search"), 12),
    (Scenario("normal_paid_social_deeplink", "paid_social", "cmp_social_003", "deeplink_payload", None, "normal_paid_social", "app_webview"), 10),
    (Scenario("normal_email_payload", "email", "cmp_email_004", "payload", None, "normal_email"), 8),
    (Scenario("normal_affiliate_hash", "affiliate", "cmp_affiliate_005", "hash_param", None, "normal_affiliate"), 6),
]


class IdFactory:
    def __init__(self) -> None:
        self.event_index = 1

    def event_id(self) -> str:
        value = f"evt_{self.event_index:07d}"
        self.event_index += 1
        return value

    @staticmethod
    def user_id(user_index: int) -> str:
        return f"user_{user_index:05d}"

    @staticmethod
    def session_id(session_index: int) -> str:
        return f"sess_{session_index:06d}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate raw_events.csv for campaign spike SQL practice.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_FILE), help="Output CSV path.")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Random seed.")
    parser.add_argument("--start-date", default=DEFAULT_START_DATE, help="Baseline start date, YYYY-MM-DD.")
    parser.add_argument("--baseline-days", type=int, default=DEFAULT_BASELINE_DAYS)
    parser.add_argument("--spike-days", type=int, default=DEFAULT_SPIKE_DAYS)
    parser.add_argument("--post-days", type=int, default=DEFAULT_POST_DAYS)
    parser.add_argument("--baseline-sessions-per-day", type=int, default=45)
    parser.add_argument("--spike-sessions-per-day", type=int, default=90)
    parser.add_argument("--post-sessions-per-day", type=int, default=55)
    parser.add_argument("--load-batch-id", default=None, help="Optional batch id written to every row.")
    parser.add_argument("--source-file-name", default=None, help="Optional source file name written to every row.")
    parser.add_argument("--hide-qa-truth", action="store_true", help="Remove qa_truth from raw_payload for harder SQL practice.")
    return parser.parse_args()


def iso_ts(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def iso_date(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


T = TypeVar("T")


def weighted_choice(rng: random.Random, weighted_items: list[tuple[T, int | float]]) -> T:
    if not weighted_items:
        raise ValueError("weighted_items must not be empty")
    items = [item for item, _ in weighted_items]
    weights = [weight for _, weight in weighted_items]
    return rng.choices(items, weights=weights, k=1)[0]


def choose_platform(rng: random.Random, scenario: Scenario) -> str:
    if scenario.preferred_platform and rng.random() < 0.82:
        return scenario.preferred_platform

    return weighted_choice(rng, [("web", 45), ("mobile_web", 25), ("app_webview", 30)])


def choose_journey_length(rng: random.Random, true_channel: str) -> int:
    if true_channel in {"paid_search", "paid_social", "email"}:
        return weighted_choice(rng, [(2, 12), (3, 28), (4, 30), (5, 20), (6, 10)])
    return weighted_choice(rng, [(2, 18), (3, 27), (4, 27), (5, 18), (6, 10)])


def choose_event_name(rng: random.Random, page_name: str, event_number_on_page: int) -> str:
    events = EVENT_BY_PAGE[page_name]
    if event_number_on_page == 0:
        return "page_view"
    return rng.choice(events[1:] if len(events) > 1 else events)


def campaign_for(campaign_id: str | None) -> Campaign | None:
    if campaign_id is None:
        return None
    return CAMPAIGNS.get(campaign_id)


def build_landing_evidence(scenario: Scenario) -> Evidence:
    campaign = campaign_for(scenario.true_campaign_id)

    if scenario.evidence_mode == "none" or campaign is None:
        return Evidence()

    if scenario.evidence_mode == "query_param":
        return Evidence(url_cid=campaign.campaign_id, utm_source=campaign.source, utm_medium=campaign.medium, utm_campaign=campaign.name)

    if scenario.evidence_mode == "hash_param":
        return Evidence(hash_cid=campaign.campaign_id, utm_source=campaign.source, utm_medium=campaign.medium, utm_campaign=campaign.name)

    if scenario.evidence_mode == "payload":
        return Evidence(payload_campaign_id=campaign.campaign_id, utm_source=campaign.source, utm_medium=campaign.medium, utm_campaign=campaign.name)

    if scenario.evidence_mode == "raw_field":
        return Evidence(raw_field_campaign_id=campaign.campaign_id, utm_source=campaign.source, utm_medium=campaign.medium, utm_campaign=campaign.name)

    if scenario.evidence_mode == "deeplink_payload":
        return Evidence(deeplink_cid=f"deeplink_{campaign.campaign_id}", payload_campaign_id=campaign.campaign_id, utm_source=campaign.source, utm_medium=campaign.medium, utm_campaign=campaign.name)

    if scenario.evidence_mode == "utm_only":
        return Evidence(utm_source=campaign.source, utm_medium=campaign.medium, utm_campaign=campaign.name)

    if scenario.evidence_mode == "multi_conflict":
        return Evidence(
            url_cid="cmp_summer_001",
            payload_campaign_id="cmp_social_003",
            raw_field_campaign_id="cmp_brand_002",
            utm_source="search_engine",
            utm_medium="cpc",
            utm_campaign="summer_sale",
        )

    raise ValueError(f"Unsupported evidence_mode: {scenario.evidence_mode}")


def apply_hit_level_anomaly_evidence(
    *,
    base_evidence: Evidence,
    scenario: Scenario,
    page_name: str,
    event_name: str,
    step_index: int,
    rng: random.Random,
) -> Evidence:
    if scenario.anomaly_type == "internal_cid_contamination":
        internal_page = page_name in {"landing", "product_detail", "cart", "checkout"}
        eligible_event = event_name in {"page_view", "cta_click", "product_view", "add_to_cart", "checkout_start"}
        if step_index > 0 and internal_page and eligible_event and rng.random() < 0.76:
            return Evidence(
                url_cid=SPIKE_CAMPAIGN_ID,
                hash_cid=base_evidence.hash_cid,
                payload_campaign_id=base_evidence.payload_campaign_id,
                raw_field_campaign_id=base_evidence.raw_field_campaign_id,
                deeplink_cid=base_evidence.deeplink_cid,
                utm_source=base_evidence.utm_source,
                utm_medium=base_evidence.utm_medium,
                utm_campaign=base_evidence.utm_campaign,
            )

    if scenario.anomaly_type == "deeplink_overwritten_by_url_cid" and step_index == 0:
        return Evidence(
            url_cid=SPIKE_CAMPAIGN_ID,
            hash_cid=base_evidence.hash_cid,
            payload_campaign_id=base_evidence.payload_campaign_id,
            raw_field_campaign_id=base_evidence.raw_field_campaign_id,
            deeplink_cid=base_evidence.deeplink_cid,
            utm_source=base_evidence.utm_source,
            utm_medium=base_evidence.utm_medium,
            utm_campaign=base_evidence.utm_campaign,
        )

    return base_evidence


def build_url(page_path: str, evidence: Evidence) -> str:
    query_params: dict[str, str] = {}
    if evidence.url_cid:
        query_params["cid"] = evidence.url_cid
    if evidence.utm_source:
        query_params["utm_source"] = evidence.utm_source
    if evidence.utm_medium:
        query_params["utm_medium"] = evidence.utm_medium
    if evidence.utm_campaign:
        query_params["utm_campaign"] = evidence.utm_campaign

    url = f"{BASE_URL}{page_path}"
    if query_params:
        url = f"{url}?{urlencode(query_params)}"
    if evidence.hash_cid:
        url = f"{url}#cid={evidence.hash_cid}"
    return url


def campaign_id_from_deeplink(deeplink_cid: str | None) -> str | None:
    if not deeplink_cid:
        return None
    if deeplink_cid.startswith("deeplink_"):
        return deeplink_cid.replace("deeplink_", "", 1)
    return deeplink_cid


def infer_campaign_from_utm(evidence: Evidence) -> str | None:
    if not any([evidence.utm_source, evidence.utm_medium, evidence.utm_campaign]):
        return None

    for campaign in CAMPAIGNS.values():
        if (
            campaign.source == evidence.utm_source
            and campaign.medium == evidence.utm_medium
            and campaign.name == evidence.utm_campaign
        ):
            return campaign.campaign_id
    return None


def expected_processing(
    *,
    evidence: Evidence,
    previous_session_campaign_id: str | None,
    true_channel: str,
) -> ProcessedResult:
    candidates = [
        (campaign_id_from_deeplink(evidence.deeplink_cid), "deeplink_cid"),
        (evidence.url_cid, "url_cid"),
        (evidence.hash_cid, "hash_cid"),
        (evidence.payload_campaign_id, "payload_campaign_id"),
        (evidence.raw_field_campaign_id, "raw_campaign_id"),
        (infer_campaign_from_utm(evidence), "utm"),
        (previous_session_campaign_id, "session_persistence"),
    ]

    for candidate_id, reason in candidates:
        campaign = campaign_for(candidate_id)
        if campaign:
            return ProcessedResult(campaign.campaign_id, campaign.channel, campaign.source, campaign.medium, reason)

    source_medium = {
        "direct": ("", ""),
        "referral": ("partner", "referral"),
        "organic_search": ("search_engine", "organic"),
    }
    source, medium = source_medium.get(true_channel, ("", ""))
    return ProcessedResult(None, true_channel, source, medium, "fallback_true_channel")


def observed_processing(
    *,
    evidence: Evidence,
    expected: ProcessedResult,
    scenario: Scenario,
    step_index: int,
) -> ProcessedResult:
    if scenario.anomaly_type == "missing_processed_campaign" and step_index == 0:
        return ProcessedResult(None, "direct", "", "", "bug_missing_processed_campaign")

    if scenario.anomaly_type == "hash_param_ignored" and evidence.hash_cid:
        return ProcessedResult(None, "direct", "", "", "bug_hash_param_not_parsed")

    if scenario.anomaly_type == "wrong_priority_output" and step_index == 0:
        campaign = CAMPAIGNS["cmp_brand_002"]
        return ProcessedResult(campaign.campaign_id, campaign.channel, campaign.source, campaign.medium, "bug_wrong_priority_raw_field_wins")

    if scenario.anomaly_type == "processed_only_without_raw_evidence" and step_index == 0:
        campaign = CAMPAIGNS[SPIKE_CAMPAIGN_ID]
        return ProcessedResult(campaign.campaign_id, campaign.channel, campaign.source, campaign.medium, "bug_processed_value_without_raw_evidence")

    if scenario.anomaly_type in {"internal_cid_contamination", "deeplink_overwritten_by_url_cid"} and evidence.url_cid == SPIKE_CAMPAIGN_ID:
        campaign = CAMPAIGNS[SPIKE_CAMPAIGN_ID]
        return ProcessedResult(campaign.campaign_id, campaign.channel, campaign.source, campaign.medium, "bug_url_cid_overwrites_correct_source")

    return expected


def scenario_pool_for_period(period: str) -> list[tuple[Scenario, int]]:
    pools = {"baseline": BASELINE_SCENARIOS, "spike": SPIKE_SCENARIOS, "post": POST_SCENARIOS}
    if period not in pools:
        raise ValueError(f"Unsupported period: {period}")
    return pools[period]


def session_start_time(rng: random.Random, current_day: date) -> datetime:
    hour = weighted_choice(
        rng,
        [
            (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1),
            (6, 3), (7, 4), (8, 6), (9, 7), (10, 7), (11, 7),
            (12, 8), (13, 7), (14, 7), (15, 7), (16, 7), (17, 8),
            (18, 9), (19, 9), (20, 8), (21, 6), (22, 4), (23, 2),
        ],
    )
    return datetime(current_day.year, current_day.month, current_day.day, hour, rng.randint(0, 59), rng.randint(0, 59))


def events_per_page(rng: random.Random, page_name: str) -> int:
    if page_name in {"product_detail", "cart", "checkout"}:
        return weighted_choice(rng, [(1, 60), (2, 32), (3, 8)])
    return weighted_choice(rng, [(1, 75), (2, 22), (3, 3)])


def release_version_for(period: str) -> str:
    return {"baseline": "frontend-v2.4.0", "spike": "frontend-v2.5.0", "post": "frontend-v2.5.1"}[period]


def build_payload(
    *,
    event_id: str,
    user_id: str,
    session_id: str,
    event_timestamp: datetime,
    page_name: str,
    page_path: str,
    event_name: str,
    platform: str,
    user_agent: str,
    release_version: str,
    period: str,
    scenario: Scenario,
    evidence: Evidence,
    expected: ProcessedResult,
    observed: ProcessedResult,
    session_step_index: int,
    page_event_index: int,
    previous_page_name: str | None,
    include_qa_truth: bool,
) -> dict:
    payload = {
        "event_id": event_id,
        "user_id": user_id,
        "session_id": session_id,
        "event_timestamp": iso_ts(event_timestamp),
        "tracking_context": "synthetic_campaign_spike_lab",
        "release_version": release_version,
        "period": period,
        "platform": platform,
        "user_agent": user_agent,
        "page": {
            "page_name": page_name,
            "page_path": page_path,
            "previous_page_name": previous_page_name,
        },
        "event": {
            "event_name": event_name,
            "session_step_index": session_step_index,
            "page_event_index": page_event_index,
        },
        "campaign_candidates": {
            "url_cid": evidence.url_cid,
            "hash_cid": evidence.hash_cid,
            "payload_campaign_id": evidence.payload_campaign_id,
            "raw_field_campaign_id": evidence.raw_field_campaign_id,
            "deeplink_cid": evidence.deeplink_cid,
            "utm_source": evidence.utm_source,
            "utm_medium": evidence.utm_medium,
            "utm_campaign": evidence.utm_campaign,
            "has_any_campaign_evidence": evidence.has_any_campaign_evidence(),
        },
        "processing_output": {
            "expected_campaign_id": expected.campaign_id,
            "expected_marketing_channel": expected.channel,
            "expected_campaign_source": expected.source,
            "expected_campaign_medium": expected.medium,
            "expected_reason": expected.reason,
            "observed_campaign_id": observed.campaign_id,
            "observed_marketing_channel": observed.channel,
            "observed_campaign_source": observed.source,
            "observed_campaign_medium": observed.medium,
            "observed_reason": observed.reason,
        },
    }

    if include_qa_truth:
        payload["qa_truth"] = {
            "scenario_type": scenario.scenario_type,
            "true_acquisition_channel": scenario.true_channel,
            "true_campaign_id": scenario.true_campaign_id,
            "evidence_mode": scenario.evidence_mode,
            "anomaly_type": scenario.anomaly_type,
            "root_cause_label": scenario.root_cause_label,
            "is_intentional_anomaly": scenario.anomaly_type is not None,
            "is_campaign_id_mismatch": expected.campaign_id != observed.campaign_id,
            "is_channel_mismatch": expected.channel != observed.channel,
            "is_spike_campaign_observed": observed.campaign_id == SPIKE_CAMPAIGN_ID,
            "is_spike_period": period == "spike",
        }

    return payload


def generate_session_events(
    *,
    rng: random.Random,
    ids: IdFactory,
    session_index: int,
    current_day: date,
    period: str,
    source_file_name: str,
    load_batch_id: str,
    include_qa_truth: bool,
) -> list[dict]:
    scenario = weighted_choice(rng, scenario_pool_for_period(period))
    platform = choose_platform(rng, scenario)
    user_agent = rng.choice(USER_AGENTS[platform])
    release_version = release_version_for(period)

    user_id = ids.user_id(rng.randint(1, 680))
    session_id = ids.session_id(session_index)
    start_time = session_start_time(rng, current_day)
    journey = PAGE_SEQUENCE[: choose_journey_length(rng, scenario.true_channel)]

    landing_evidence = build_landing_evidence(scenario)
    previous_url = ""
    previous_page_name = None
    previous_session_campaign_id: str | None = None
    rows: list[dict] = []
    event_time = start_time
    session_step_index = 0

    for page_idx, (page_name, page_path) in enumerate(journey):
        for page_event_idx in range(events_per_page(rng, page_name)):
            event_name = choose_event_name(rng, page_name, page_event_idx)
            base_evidence = landing_evidence if page_idx == 0 and page_event_idx == 0 else Evidence()
            hit_evidence = apply_hit_level_anomaly_evidence(
                base_evidence=base_evidence,
                scenario=scenario,
                page_name=page_name,
                event_name=event_name,
                step_index=session_step_index,
                rng=rng,
            )

            expected = expected_processing(
                evidence=hit_evidence,
                previous_session_campaign_id=previous_session_campaign_id,
                true_channel=scenario.true_channel,
            )
            observed = observed_processing(evidence=hit_evidence, expected=expected, scenario=scenario, step_index=session_step_index)

            if expected.campaign_id is not None:
                previous_session_campaign_id = expected.campaign_id

            event_id = ids.event_id()
            page_url = build_url(page_path, hit_evidence)
            payload = build_payload(
                event_id=event_id,
                user_id=user_id,
                session_id=session_id,
                event_timestamp=event_time,
                page_name=page_name,
                page_path=page_path,
                event_name=event_name,
                platform=platform,
                user_agent=user_agent,
                release_version=release_version,
                period=period,
                scenario=scenario,
                evidence=hit_evidence,
                expected=expected,
                observed=observed,
                session_step_index=session_step_index,
                page_event_index=page_event_idx,
                previous_page_name=previous_page_name,
                include_qa_truth=include_qa_truth,
            )

            rows.append(
                {
                    "event_id": event_id,
                    "user_id": user_id,
                    "session_id": session_id,
                    "event_timestamp": iso_ts(event_time),
                    "event_date": iso_date(event_time),
                    "page_name": page_name,
                    "page_url": page_url,
                    "referrer_url": previous_url if previous_url else REFERRERS.get(scenario.true_channel, ""),
                    "event_name": event_name,
                    "marketing_channel": observed.channel,
                    "raw_campaign_id": hit_evidence.primary_raw_campaign_id(),
                    "processed_campaign_id": observed.campaign_id or "",
                    "campaign_source": observed.source,
                    "campaign_medium": observed.medium,
                    "raw_payload": json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
                    "source_file_name": source_file_name,
                    "load_batch_id": load_batch_id,
                }
            )

            session_step_index += 1
            event_time += timedelta(seconds=rng.randint(12, 210))

        previous_url = page_url
        previous_page_name = page_name

    return rows


def date_range(start_day: date, number_of_days: int) -> Iterable[date]:
    for day_offset in range(number_of_days):
        yield start_day + timedelta(days=day_offset)


def make_load_batch_id(args: argparse.Namespace) -> str:
    if args.load_batch_id:
        return args.load_batch_id
    return f"campaign_spike_{args.start_date.replace('-', '')}_seed{args.seed}"


def generate_rows(args: argparse.Namespace) -> list[dict]:
    rng = random.Random(args.seed)
    ids = IdFactory()
    rows: list[dict] = []
    session_index = 1

    baseline_start = datetime.strptime(args.start_date, "%Y-%m-%d").date()
    spike_start = baseline_start + timedelta(days=args.baseline_days)
    post_start = spike_start + timedelta(days=args.spike_days)

    periods = [
        ("baseline", baseline_start, args.baseline_days, args.baseline_sessions_per_day),
        ("spike", spike_start, args.spike_days, args.spike_sessions_per_day),
        ("post", post_start, args.post_days, args.post_sessions_per_day),
    ]

    output_path = Path(args.output)
    source_file_name = args.source_file_name or output_path.name
    load_batch_id = make_load_batch_id(args)
    include_qa_truth = not args.hide_qa_truth

    for period, start_day, number_of_days, sessions_per_day in periods:
        for current_day in date_range(start_day, number_of_days):
            daily_sessions = max(1, int(rng.gauss(sessions_per_day, sessions_per_day * 0.08)))
            for _ in range(daily_sessions):
                rows.extend(
                    generate_session_events(
                        rng=rng,
                        ids=ids,
                        session_index=session_index,
                        current_day=current_day,
                        period=period,
                        source_file_name=source_file_name,
                        load_batch_id=load_batch_id,
                        include_qa_truth=include_qa_truth,
                    )
                )
                session_index += 1

    rows.sort(key=lambda row: (row["event_timestamp"], row["session_id"], row["event_id"]))
    return rows


def validate_rows(rows: list[dict], *, require_qa_truth: bool) -> None:
    if not rows:
        raise ValueError("Generated dataset is empty")

    event_ids = [row["event_id"] for row in rows]
    if len(event_ids) != len(set(event_ids)):
        raise ValueError("event_id values are not unique")

    payloads = []

    for row in rows:
        event_dt = datetime.strptime(row["event_timestamp"], "%Y-%m-%d %H:%M:%S")
        if row["event_date"] != event_dt.date().isoformat():
            raise ValueError(f"event_date mismatch for event_id={row['event_id']}")
        payload = json.loads(row["raw_payload"])
        if not isinstance(payload, dict):
            raise ValueError(f"raw_payload is not a JSON object for event_id={row['event_id']}")
        if require_qa_truth and "qa_truth" not in payload:
            raise ValueError("qa_truth missing while require_qa_truth=True")
        payloads.append(payload)

    period_channel_counts: dict[tuple[str, str], int] = {}
    period_counts: dict[str, int] = {}
    root_causes: dict[str, int] = {}

    for row, payload in zip(rows, payloads):
        period = payload["period"]
        channel = row["marketing_channel"]
        period_channel_counts[(period, channel)] = period_channel_counts.get((period, channel), 0) + 1
        period_counts[period] = period_counts.get(period, 0) + 1
        if "qa_truth" in payload:
            root = payload["qa_truth"]["root_cause_label"]
            root_causes[root] = root_causes.get(root, 0) + 1

    baseline_paid_share = period_channel_counts.get(("baseline", "paid_search"), 0) / period_counts.get("baseline", 1)
    spike_paid_share = period_channel_counts.get(("spike", "paid_search"), 0) / period_counts.get("spike", 1)
    if spike_paid_share <= baseline_paid_share:
        raise ValueError("Expected paid_search share to increase during spike period")

    if require_qa_truth:
        required_root_causes = {
            "internal_url_cid_contamination",
            "source_priority_bug",
            "processed_only_without_raw_evidence",
            "true_paid_search_growth",
        }
        missing = sorted(required_root_causes - set(root_causes))
        if missing:
            raise ValueError(f"Required root-cause labels missing: {missing}")


def write_csv(rows: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "event_id",
        "user_id",
        "session_id",
        "event_timestamp",
        "event_date",
        "page_name",
        "page_url",
        "referrer_url",
        "event_name",
        "marketing_channel",
        "raw_campaign_id",
        "processed_campaign_id",
        "campaign_source",
        "campaign_medium",
        "raw_payload",
        "source_file_name",
        "load_batch_id",
    ]

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def print_summary(rows: list[dict], output_path: Path, *, include_qa_truth: bool) -> None:
    by_channel: dict[str, int] = {}
    by_period_channel: dict[tuple[str, str], int] = {}
    by_root_cause: dict[str, int] = {}
    mismatch_rows = 0
    spike_campaign_rows = 0

    for row in rows:
        payload = json.loads(row["raw_payload"])
        period = payload["period"]
        channel = row["marketing_channel"] or "NULL"

        by_channel[channel] = by_channel.get(channel, 0) + 1
        by_period_channel[(period, channel)] = by_period_channel.get((period, channel), 0) + 1

        if "qa_truth" in payload:
            root_cause = payload["qa_truth"]["root_cause_label"]
            by_root_cause[root_cause] = by_root_cause.get(root_cause, 0) + 1
            if payload["qa_truth"]["is_campaign_id_mismatch"] or payload["qa_truth"]["is_channel_mismatch"]:
                mismatch_rows += 1
            if payload["qa_truth"]["is_spike_campaign_observed"]:
                spike_campaign_rows += 1

    print(f"Generated rows: {len(rows):,}")
    print(f"Output file: {output_path}")
    print(f"Validation: passed")
    if include_qa_truth:
        print(f"Rows with expected vs observed mismatch: {mismatch_rows:,}")
        print(f"Rows where observed campaign is {SPIKE_CAMPAIGN_ID}: {spike_campaign_rows:,}")
    print()

    print("Marketing channel distribution:")
    for channel, count in sorted(by_channel.items(), key=lambda x: x[1], reverse=True):
        print(f"  {channel:15s} {count:6,d}  ({count / len(rows) * 100:5.1f}%)")
    print()

    print("Period x channel distribution:")
    for period in ["baseline", "spike", "post"]:
        period_total = sum(count for (p, _), count in by_period_channel.items() if p == period)
        print(f"  [{period}] total={period_total:,}")
        channels = sorted(
            [(channel, count) for (p, channel), count in by_period_channel.items() if p == period],
            key=lambda x: x[1],
            reverse=True,
        )
        for channel, count in channels:
            print(f"    {channel:15s} {count:6,d}  ({count / period_total * 100:5.1f}%)")
    print()

    if include_qa_truth:
        print("QA root-cause label distribution, for final validation only:")
        for root_cause, count in sorted(by_root_cause.items(), key=lambda x: x[1], reverse=True):
            print(f"  {root_cause:38s} {count:6,d}")


def main() -> None:
    args = parse_args()
    rows = generate_rows(args)
    validate_rows(rows, require_qa_truth=not args.hide_qa_truth)
    output_path = Path(args.output).resolve()
    write_csv(rows, output_path)
    print_summary(rows, output_path, include_qa_truth=not args.hide_qa_truth)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
