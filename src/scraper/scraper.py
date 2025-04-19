import os
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from loguru import logger
from scraper.collector import get_listing_links
from scraper.parser import extract_detail_from_page
from utils.scraper_utils import extract_listing_id, init_browser, save_json

from src.utils.settings import RAW_DIR, use_thread


def scrape_single_listing(url: str) -> dict | None:
    driver = init_browser()
    try:
        extracted_id = extract_listing_id(url)
        if extracted_id:
            logger.info(f"[SCRAPING] {url}")
            time.sleep(random.uniform(2, 3))
            return extract_detail_from_page(driver, url, extracted_id)
    except Exception as e:
        logger.error(f"[THREAD ERROR] Failed to scrape {url}: {e}")
    finally:
        driver.quit()
    return None


def main() -> None:
    driver = init_browser()
    try:
        links = get_listing_links(driver)
        logger.info(f"Found {len(links)} links")
    finally:
        driver.quit()

    records = []

    if use_thread:

        max_workers = os.cpu_count()

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(scrape_single_listing, url) for url in links]

            for i, future in enumerate(as_completed(futures), start=1):
                result = future.result()
                if result:
                    logger.info(
                        f"[{i}/{len(links)}] Scraped listing: {result['listing_id']}"
                    )
                    records.append(result)
    else:
        for i, url in enumerate(links):
            logger.info(f"[{i+1}/{len(links)}] Scraping {url}")
            link_results = scrape_single_listing(url)

            if link_results:
                records.append(link_results)

    save_json(f"{RAW_DIR}/apartment_listings.json", records)
    logger.success(f"Saved {len(records)} listings")
