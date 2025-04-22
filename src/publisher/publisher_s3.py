import gzip
import json
import random
import time
from datetime import datetime
from pathlib import Path

import boto3
from loguru import logger

from src.utils.publisher_utils import ensure_s3_bucket_exists
from src.utils.settings import COMPRESSED_DIR, settings


def upload_with_retry(local_path, bucket, s3_key, retries=3) -> bool:
    s3 = boto3.client("s3")
    for attempt in range(1, retries + 1):
        try:
            s3.upload_file(str(local_path), bucket, s3_key)
            return True
        except Exception as e:
            wait = 2**attempt + random.uniform(0, 1)
            logger.warning(
                f"[Retry {attempt}] Upload failed: {e}. Retrying in {wait:.1f}s..."
            )
            time.sleep(wait)
    return False


def run_publisher_s3(file: str, listing_type: str) -> str | None:
    input_path = Path(file)

    if not input_path.exists():
        logger.error(f"Cleaned file not found: {file}")
        return None

    with open(input_path) as f:
        data = json.load(f)

    if not isinstance(data, list):
        logger.error("Expected a list of listings in the file.")
        return None

    metadata = {
        "scraped_at": datetime.utcnow().isoformat(),
        "listing_type": listing_type,
        "listing_count": len(data),
        "scraper_version": "1.0.0",
        "cleaned": True,
        "source": "https://jiji.com.gh/",
    }

    wrapped = {
        "metadata": metadata,
        "data": data,
    }

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    COMPRESSED_DIR.mkdir(parents=True, exist_ok=True)
    local_path = COMPRESSED_DIR / f"{listing_type}_{timestamp}.json.gz"

    with gzip.open(local_path, "wt", encoding="utf-8") as f:
        json.dump(wrapped, f, indent=2)

    ensure_s3_bucket_exists()

    s3_key = f"listings/{listing_type}/{listing_type}_{timestamp}.json.gz"
    uploaded = upload_with_retry(local_path, settings.S3_BUCKET, s3_key)

    if not uploaded:
        logger.error("Failed to upload to S3 after retries.")
        return None

    # Tag the uploaded object
    try:
        s3 = boto3.client("s3")
        s3.put_object_tagging(
            Bucket=settings.S3_BUCKET,
            Key=s3_key,
            Tagging={
                "TagSet": [
                    {"Key": "listing_type", "Value": listing_type},
                    {"Key": "version", "Value": "1.0.0"},
                    {"Key": "source", "Value": "jiji"},
                ]
            },
        )
    except Exception as e:
        logger.warning(f"Failed to tag S3 object: {e}")

    s3_uri = f"s3://{settings.S3_BUCKET}/{s3_key}"
    logger.success(f"Uploaded to S3: {s3_uri}")
    return s3_uri
