import re
from pathlib import Path


def get_latest_scraped_file(directory: Path, listing_type: str) -> Path:
    """
    Get the latest scraped file from a directory based on timestamp in filename

    Args:
        directory: Directory to search
        listing_type: Type of listing ('rent' or 'sale')

    Returns:
        Path to the most recent file
    """
    directory.mkdir(parents=True, exist_ok=True)

    pattern = re.compile(rf"{listing_type}_(\d{{8}}_\d{{6}})\.json")

    files = [
        (f, pattern.search(f.name).group(1))
        for f in directory.glob(f"{listing_type}_*.json")
        if pattern.search(f.name)
    ]

    if not files:
        raise FileNotFoundError("No apartment listings file found in directory.")

    return sorted(files, key=lambda x: x[1], reverse=True)[0][0]
