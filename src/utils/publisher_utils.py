import re
from pathlib import Path


def get_latest_scraped_file(directory: Path, listing_type: str) -> Path:
    pattern = re.compile(rf"apartment_listings_{listing_type}_(\d{{8}}_\d{{6}})\.json")

    files = [
        (f, pattern.search(f.name).group(1))
        for f in directory.glob(f"apartment_listings_{listing_type}_*.json")
        if pattern.search(f.name)
    ]

    if not files:
        raise FileNotFoundError("No apartment listings file found in RAW_DIR.")

    return sorted(files, key=lambda x: x[1], reverse=True)[0][0]
