import time

from loguru import logger
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from src.utils.settings import settings


def get_listing_links(driver: WebDriver, listing_type: str) -> list[str]:
    base_url = (
        settings.base_url_rent if listing_type == "rent" else settings.base_url_sale
    )
    href_pattern = (
        "/houses-apartments-for-rent/"
        if listing_type == "rent"
        else "/houses-apartments-for-sale/"
    )

    driver.get(base_url)
    time.sleep(3)

    links = set()
    scroll_attempts = 0
    stagnant_attempts = 0
    last_link_count = 0
    max_scrolls = float("inf") if settings.scroll_count == -1 else settings.scroll_count

    while scroll_attempts < max_scrolls:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        cards = driver.find_elements(By.CSS_SELECTOR, f"a[href*='{href_pattern}']")
        for card in cards:
            href = card.get_attribute("href")
            if href:
                links.add(href)

        logger.info(f"Scroll #{scroll_attempts+1} → {len(links)} total links")

        if len(links) == last_link_count:
            stagnant_attempts += 1
        else:
            stagnant_attempts = 0

        if stagnant_attempts >= 3:
            logger.warning("No new links after 3 scrolls. Stopping.")
            break

        last_link_count = len(links)
        scroll_attempts += 1

    return list(links)
