import re
from datetime import datetime, timedelta


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


def clean_listing(record: dict) -> dict:
    return {
        **record,
        "price": clean_price(record.get("price")),
        "posted_date": parse_posted_time(record.get("posted_date")),
        "bedrooms": safe_int(record.get("bedrooms")),
        "bathrooms": safe_int(record.get("bathrooms")),
        "features": parse_features(record.get("features", {})),
    }
