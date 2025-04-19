import re
from datetime import datetime, timedelta

import orjson
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from src.utils.settings import settings


def init_browser() -> webdriver.Chrome:
    options = Options()
    if settings.headless:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    return webdriver.Chrome(options=options)


def extract_listing_id(url: str) -> str:
    match = re.search(r"-([a-zA-Z0-9]+)\.html", url)
    if match:
        return match.group(1)
    return None


def clean_price(price_str):
    if not isinstance(price_str, str):
        return None
    return int(re.sub(r"[^\d]", "", price_str))


def parse_posted_time(posted_str):
    now = datetime.now()
    if isinstance(posted_str, str):
        posted_str = posted_str.lower()
        if "min" in posted_str:
            minutes = int(re.search(r"(\d+)", posted_str).group(1))
            return now - timedelta(minutes=minutes)
        elif "hour" in posted_str:
            hours = int(re.search(r"(\d+)", posted_str).group(1))
            return now - timedelta(hours=hours)
        elif "day" in posted_str:
            days = int(re.search(r"(\d+)", posted_str).group(1))
            return now - timedelta(days=days)
        elif re.match(r"\d{2}/\d{2}", posted_str):
            day, month = map(int, posted_str.split("/"))
            year = now.year
            date = datetime(year, month, day)
            if date > now:
                date = date.replace(year=year - 1)
            return date
    return now


def safe_int(val):
    try:
        return int(val)
    except (TypeError, ValueError):
        return None


def parse_features(raw_features: dict) -> dict:
    parsed = {}
    for key, value in raw_features.items():
        value = value.replace("sqm", "")
        if isinstance(value, str) and value.isdigit():
            parsed[key] = int(value)
        else:
            parsed[key] = (
                safe_int(value)
                if isinstance(value, str) and re.fullmatch(r"\d+", value.strip())
                else value
            )
    return parsed


def save_json(output_file_path: str, data: dict) -> None:
    try:
        with open(output_file_path, "wb") as outfile:
            outfile.write(
                orjson.dumps(data, option=orjson.OPT_INDENT_2 | orjson.OPT_NON_STR_KEYS)
            )
    except IOError as e:
        raise RuntimeError(f"Error saving JSON to {output_file_path}: {e}")
