import time

from loguru import logger
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from src.utils.settings import settings


def get_listing_links(driver: WebDriver, pause_time: float = 2.0) -> list[str]:
    driver.get(settings.base_url)
    time.sleep(3)

    links = set()
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_attempts = 0
    max_scrolls = float("inf") if settings.scroll_count == -1 else settings.scroll_count

    while scroll_attempts < max_scrolls:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)

        cards = driver.find_elements(
            By.CSS_SELECTOR, "a[href*='/houses-apartments-for-rent/']"
        )
        for card in cards:
            href = card.get_attribute("href")
            if href:
                links.add(href)

        logger.debug(f"Scroll #{scroll_attempts + 1} → Total links: {len(links)}")

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            logger.info("Reached end of page. No more content to scroll.")
            break

        last_height = new_height
        scroll_attempts += 1

    if scroll_attempts >= max_scrolls:
        logger.warning(
            f"Reached max scroll limit ({max_scrolls}) — listings may be incomplete."
        )

    return list(links)
