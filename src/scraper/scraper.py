import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from loguru import logger

from src.scraper.collector import get_listing_links
from src.scraper.parser import extract_detail_from_page
from src.utils.scraper_utils import extract_listing_id, init_browser, save_json
from src.utils.settings import RAW_DIR


def scrape_single_listing(url: str, listing_type: str) -> dict | None:
    driver = init_browser()
    try:
        extracted_id = extract_listing_id(url)
        if extracted_id:
            time.sleep(3)
            return extract_detail_from_page(driver, url, extracted_id, listing_type)
        else:
            logger.warning(f"[SKIPPING] Not apartment listing: {url}")
    except Exception as e:
        logger.warning(f"[SCRAPE FAIL] {url}: {e}")
    finally:
        driver.quit()
    return None


def run_scraper(listing_type: str = "rent") -> bool:
    driver = init_browser()

    try:
        links = get_listing_links(driver, listing_type)
        logger.info(f"Found {len(links)} links to scrape")
    except Exception:
        logger.exception("Failed to collect links")
        return False
    finally:
        driver.quit()

    records = []

    try:
        max_workers = min(8, os.cpu_count())
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(scrape_single_listing, url, listing_type)
                for url in links
            ]
            for i, future in enumerate(as_completed(futures), start=1):
                result = future.result()
                if result:
                    logger.success(
                        f"[OK] [{i}/{len(links)}] Scraped {result['listing_id']} | {result['url']}"
                    )
                    records.append(result)
    except Exception:
        logger.exception("Error during scraping process")
        return False

    if not records:
        logger.warning("No listings were scraped.")
        return False

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    save_json(f"{RAW_DIR}/{listing_type}_{timestamp}.json", records)
    logger.info(f"Saved {len(records)} listings to {listing_type}_{timestamp}.json")
    return True
