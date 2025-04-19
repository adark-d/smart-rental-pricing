import os
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from loguru import logger

from src.scraper.collector import get_listing_links
from src.scraper.parser import extract_detail_from_page
from src.utils.scraper_utils import extract_listing_id, init_browser, save_json
from src.utils.settings import RAW_DIR


def scrape_single_listing(url: str) -> dict | None:
    driver = init_browser()
    try:
        extracted_id = extract_listing_id(url)
        if extracted_id:
            time.sleep(random.uniform(2, 3))
            return extract_detail_from_page(driver, url, extracted_id)
        else:
            logger.warning(f"[SKIPPING] Not apartment listing: {url}")
    except Exception as e:
        logger.warning(f"[SCRAPE FAIL] {url}: {e}")
    finally:
        driver.quit()
    return None


def run_scraper() -> bool:
    driver = init_browser()
    try:
        links = get_listing_links(driver)
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
            futures = [executor.submit(scrape_single_listing, url) for url in links]
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

    save_json(f"{RAW_DIR}/apartment_listings.json", records)
    logger.info(f"Saved {len(records)} listings to apartment_listings.json")
    return True
