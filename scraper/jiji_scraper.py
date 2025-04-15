import csv
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

URL = "https://jiji.com.gh/houses-apartments-for-rent"


def start_browser():
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    return driver


def scrape_listings(driver):
    driver.get(URL)
    time.sleep(3)

    listings = []

    for _ in range(3):
        cards = driver.find_elements(By.CLASS_NAME, "b-list-advert__item-wrapper")

        for card in cards:
            try:
                title = card.find_element(By.TAG_NAME, "h4").text.strip()
                price = card.find_element(
                    By.CLASS_NAME, "b-list-advert__item-price"
                ).text.strip()
                location = card.find_element(
                    By.CLASS_NAME, "b-advert__region"
                ).text.strip()
                listings.append((title, price, location))
            except Exception:
                continue

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

    return listings


def save_to_csv(data, filename="jiji_listings.csv"):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Price", "Location"])
        writer.writerows(data)


if __name__ == "__main__":
    driver = start_browser()
    try:
        listings = scrape_listings(driver)
        save_to_csv(listings)
        print(f"Scraped {len(listings)} listings")
    finally:
        driver.quit()
