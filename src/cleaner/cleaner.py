import json
from datetime import datetime
from pathlib import Path

from loguru import logger

from src.utils.cleaner_utils import clean_listing
from src.utils.scraper_utils import save_json
from src.utils.settings import CLEANED_DIR


def run_cleaner(file: str, listing_type: str) -> bool:
    raw_path = Path(file)
    if not raw_path.exists():
        logger.error(f"Raw file not found: {raw_path}")
        return False

    with open(raw_path, "r") as f:
        raw_data = json.load(f)

    if not isinstance(raw_data, list):
        logger.error("Expected a list of listings in the raw file.")
        return False

    logger.info(f"Cleaning {len(raw_data)} listings...")

    cleaned = []
    for i, record in enumerate(raw_data):
        try:
            cleaned_record = clean_listing(record)
            cleaned.append(cleaned_record)
        except Exception as e:
            logger.warning(f"[SKIPPED] Listing {i} due to error: {e}")

    if not cleaned:
        logger.warning("No valid listings after cleaning.")
        return False

    CLEANED_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    save_json(f"{CLEANED_DIR}/{listing_type}_{timestamp}.json", cleaned)
    logger.success(f"Saved cleaned listings to {listing_type}_{timestamp}.json")
    return True
