import re

import orjson
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from src.utils.settings import settings


def init_browser():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    if settings.headless:
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) \
                                AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
        )

    return webdriver.Chrome(options=chrome_options)


def extract_listing_id(url: str) -> str:
    match = re.search(r"-([a-zA-Z0-9]+)\.html", url)
    return match.group(1) if match else None


def save_json(output_file_path: str, data: dict) -> None:
    try:
        with open(output_file_path, "wb") as outfile:
            outfile.write(
                orjson.dumps(data, option=orjson.OPT_INDENT_2 | orjson.OPT_NON_STR_KEYS)
            )
    except IOError as e:
        raise RuntimeError(f"Error saving JSON to {output_file_path}: {e}")
