from pathlib import Path
from dotenv import load_dotenv
import os

ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = ROOT / "data" / "raw"
INTERIM_DIR = ROOT / "data" / "interim"
PROCESSED_DIR = ROOT / "data" / "processed"

for folder in [RAW_DIR, INTERIM_DIR, PROCESSED_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

RAW_JSON_FILE = RAW_DIR / "data_scientist_naics5132_raw.json"
RAW_CSV_FILE = RAW_DIR / "data_scientist_naics5132_raw.csv"

ROLE_MATCHES_FILE = INTERIM_DIR / "data_scientist_role_matches.csv"

PROCESSED_FILE = PROCESSED_DIR / "data_scientist_software_publishers.csv"
SKILL_SUMMARY_FILE = PROCESSED_DIR / "skill_summary.csv"
DICTIONARY_FILE = PROCESSED_DIR / "data_dictionary.csv"

load_dotenv(ROOT / ".env", override=True)

API_KEY = os.getenv("EMPLOYABILITY_API_KEY", "").strip()
BASE_URL = os.getenv("EMPLOYABILITY_API_BASE_URL", "").strip().rstrip("/")
PATH_PREFIX = os.getenv("EMPLOYABILITY_API_PATH_PREFIX", "").strip().strip("/")

if not API_KEY:
    raise RuntimeError("EMPLOYABILITY_API_KEY is missing from .env.")

if not BASE_URL or not PATH_PREFIX:
    raise RuntimeError(
        "EMPLOYABILITY_API_BASE_URL or "
        "EMPLOYABILITY_API_PATH_PREFIX is missing from .env."
    )

API_URL = f"{BASE_URL}/{PATH_PREFIX}"

HEADERS = {
    "X-API-Key": API_KEY,
    "Accept": "application/json",
}