import csv
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = OUTPUT_DIR / "raw_events.csv"

START_DATE = datetime(2026, 6, 24, 9, 0, 0)
SPIKE_DATE - datetime(2026, 7, 1, 9, 0, 0)

PAGES = ["home", "landing", "product_detail", "cart", "checkout", "order_confirmation"]
EVENTS = ["page_view", "product_view", "add_to_cart", "checkout_start", "purchage"]
NORMAL_CHANNELS = ["organic_search", "direct", "paid_social", "owned channel"]
SPIKE_CHANNEL = "paid_search"

CAMPAIGNS = [
    "cmp_summer_001",
    "cmp_brand_002",
    "cmp_retargeting_003",
    "cmp_affiliate_004",
    "cmp_spike_999",
]
