import re
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from loguru import logger

from src.utils.settings import settings


def get_latest_scraped_file(directory: Path, listing_type: str) -> Path:

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


def ensure_s3_bucket_exists():
    s3 = boto3.client("s3")
    bucket_name = settings.S3_BUCKET
    region = settings.get("AWS_DEFAULT_REGION", "us-west-2")

    try:
        s3.head_bucket(Bucket=bucket_name)
        logger.info(f"Bucket '{bucket_name}' already exists.")
    except ClientError as e:
        error_code = int(e.response["Error"]["Code"])
        if error_code == 404:
            logger.info(f"Creating bucket: {bucket_name}")
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": region},
            )
        else:
            raise
