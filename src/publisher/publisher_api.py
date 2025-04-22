import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
from loguru import logger

from src.utils.settings import FAILED_DIR, settings

API_URL = settings.api_url


def send_listing_to_api(data: dict) -> tuple[str, bool]:
    listing_id = data.get("listing_id")
    try:
        put_resp = requests.put(f"{API_URL}/listing/{listing_id}", json=data)
        if put_resp.status_code == 404:
            post_resp = requests.post(f"{API_URL}/listing", json=data)
            post_resp.raise_for_status()
            logger.info(f"[CREATE] {listing_id}")
        elif put_resp.ok:
            logger.info(f"[UPDATE] {listing_id}")
        else:
            return listing_id, False
        return listing_id, True
    except Exception:
        return listing_id, False


def write_failed_listing(listing: dict):
    listing_id = listing.get("listing_id") or str(time.time())
    listing_type = listing.get("listing_type")

    FAILED_DIR.mkdir(parents=True, exist_ok=True)
    with open(f"{FAILED_DIR}/{listing_type}_failed_{listing_id}.json", "w") as f:
        json.dump(listing, f, indent=2)


def run_publisher_api(file: str, threads: int, limit: int | None = None) -> bool:
    input_path = Path(file)
    if not input_path.exists():
        logger.error(f"File not found: {input_path}")
        return False

    with open(input_path) as f:
        listings = json.load(f)

    if limit:
        listings = listings[:limit]

    if not listings:
        logger.warning("No listings to publish.")
        return False

    logger.info(f"Publishing {len(listings)} listings with {threads} threads...")

    success_count = 0

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {
            executor.submit(send_listing_to_api, item): item for item in listings
        }
        for future in as_completed(futures):
            listing = futures[future]
            listing_id, success = future.result()
            if success:
                success_count += 1
            else:
                write_failed_listing(listing)

    logger.success(f"Published {success_count}/{len(listings)} listings")
    return True
