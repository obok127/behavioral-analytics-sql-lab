import csv
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = OUTPUT_DIR / "raw_events.csv"

START_DATE = datetime(2026, 6, 24, 9, 0, 0)
