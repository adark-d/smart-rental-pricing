import re
import time

from loguru import logger
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def extract_detail_from_page(
    driver, url: str, extracted_id: str, listing_type: str
) -> dict | None:
    try:
        driver.get(url)
        time.sleep(5)

        if "HTTP ERROR 429" in driver.page_source:
            logger.warning("Received 429 error. Sleeping before retry...")
            time.sleep(60)
            driver.refresh()

        wait = WebDriverWait(driver, 15)

        # Title
        try:
            title = wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            ).text.strip()
        except Exception:
            logger.warning(f"[MISSING] Title not found for: {url}")
            return None

        # Price
        price = None
        for selector in [".qa-advert-price-view-value", ".b-advert-price__value"]:
            try:
                price = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                ).text.strip()

                if price:
                    break
            except NoSuchElementException:
                continue
        if not price:
            logger.warning(f"[MISSING] Price not found for: {url}")

        # Location metadata
        try:
            location_raw = wait.until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        ".b-advert-info-statistics.b-advert-info-statistics--region, \
                        .qa-advert-location",
                    )
                )
            ).text.strip()
            parts = [part.strip() for part in location_raw.split(",")]
            region = parts[0] if len(parts) > 0 else ""
            area = parts[1] if len(parts) > 1 else ""
            posted_time = parts[-1] if len(parts) > 2 else ""
        except NoSuchElementException:
            logger.warning(f"[MISSING] Location metadata not found for: {url}")
            region, area, posted_time = "", "", ""

        # Icon features
        icon_features = {}
        try:
            wait.until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, "b-advert-icon-attribute")
                )
            )
            for block in driver.find_elements(By.CLASS_NAME, "b-advert-icon-attribute"):
                try:
                    text = block.find_element(By.TAG_NAME, "span").text.strip().lower()
                    if "bedroom" in text:
                        match = re.search(r"(\d+)", text)
                        if match:
                            icon_features["bedrooms"] = match.group(1)
                    elif "bathroom" in text:
                        match = re.search(r"(\d+)", text)
                        if match:
                            icon_features["bathrooms"] = match.group(1)
                    else:
                        icon_features["house_type"] = text.capitalize()
                except Exception as e:
                    logger.debug(f"[ICON SKIP] Could not parse icon block: {e}")
        except Exception as e:
            logger.warning(f"[ICON ERROR] Icon features not found: {e}")

        # Advert features
        features = {}
        try:
            wait.until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, "b-advert-attribute")
                )
            )
            attributes = driver.find_elements(By.CLASS_NAME, "b-advert-attribute")

            if attributes:
                for i, attr in enumerate(attributes):
                    try:
                        attributes = driver.find_elements(
                            By.CLASS_NAME, "b-advert-attribute"
                        )
                        key_elem = attributes[i].find_element(
                            By.CLASS_NAME, "b-advert-attribute__key"
                        )
                        value_elem = attributes[i].find_element(
                            By.CLASS_NAME, "b-advert-attribute__value"
                        )

                        # Use JS to extract raw text content
                        key_text = driver.execute_script(
                            "return arguments[0].textContent", key_elem
                        ).strip()
                        value_text = driver.execute_script(
                            "return arguments[0].textContent", value_elem
                        ).strip()

                        # Normalize key
                        key_clean = key_text.lower().replace(" ", "_")

                        features[key_clean] = value_text
                    except Exception as e:
                        logger.debug(f"[FEATURE SKIP] Label-value pair error: {e}")
        except Exception as e:
            logger.warning(f"[FEATURE ERROR] Structured features not found: {e}")

        # Amenities
        amenities = {
            elem.text.strip()
            for elem in driver.find_elements(
                By.CSS_SELECTOR, ".b-advert-attributes__tag, .b-advert-badge__content"
            )
            if elem.text.strip()
        }
        amenities_str = ", ".join(sorted(amenities)) if amenities else ""

        # Description
        try:
            raw_description = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".qa-description-text, .b-advert-description")
                )
            ).text.strip()
        except NoSuchElementException:
            logger.warning(f"[MISSING] Description not found for: {url}")
            raw_description = ""

        if raw_description:
            lines = raw_description.splitlines()
            cleaned_lines = list(
                dict.fromkeys(
                    line.strip("•- ").strip() for line in lines if line.strip()
                )
            )
            description = ". ".join(cleaned_lines)
            description = re.sub(r"\s{2,}", " ", description)
            if not description.endswith("."):
                description += "."
        else:
            description = ""

        return {
            "url": url,
            "listing_id": extracted_id,
            "listing_type": listing_type,
            "title": title,
            "price": price,
            "region": region,
            "area": area,
            **icon_features,
            "posted_date": posted_time,
            "amenities": amenities_str,
            "description": description,
            "features": features,
        }

    except Exception as final_e:
        logger.error(
            f"[FATAL] Failed to extract listing from {url} → {type(final_e).__name__}: {final_e}"
        )
        return None
