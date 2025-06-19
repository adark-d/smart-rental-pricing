import re
from datetime import datetime
from pathlib import Path

import boto3
import orjson
from botocore.exceptions import ClientError
from loguru import logger

from src.utils.settings import settings


def load_json(file_path: str) -> dict:
    try:
        with open(file_path, "rb") as file:
            return orjson.loads(file.read())
    except (orjson.JSONDecodeError, FileNotFoundError) as e:
        raise RuntimeError(f"Error loading JSON from {file_path}: {e}")


def save_json(output_file_path: str, data: dict) -> None:
    try:
        with open(output_file_path, "wb") as outfile:
            outfile.write(
                orjson.dumps(data, option=orjson.OPT_INDENT_2 | orjson.OPT_NON_STR_KEYS)
            )
    except IOError as e:
        raise RuntimeError(f"Error saving JSON to {output_file_path}: {e}")


def ensure_s3_bucket_exists():
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    bucket_name = settings.AWS_S3_BUCKET
    region = settings.AWS_DEFAULT_REGION

    try:
        s3.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        error_code = int(e.response["Error"]["Code"])
        if error_code == 404:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": region},
            )
        else:
            raise


def upload_to_s3(
    data: list[dict],
    folder: str,
    source: str,
    listing_type: str,
    timestamp: str | None = None,
) -> str | None:
    if not data:
        logger.error("No data to upload")
        return None

    try:
        ensure_s3_bucket_exists()

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

        timestamp = timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")
        s3_key = (
            f"{folder}/{source}/{listing_type}/{source}_{listing_type}_{timestamp}.json"
        )

        json_bytes = orjson.dumps(
            data, option=orjson.OPT_INDENT_2 | orjson.OPT_NON_STR_KEYS
        )

        # Upload directly from memory
        s3_client.put_object(
            Bucket=settings.AWS_S3_BUCKET,
            Key=s3_key,
            Body=json_bytes,
            ContentType="application/json",
        )

        s3_path = f"s3://{settings.AWS_S3_BUCKET}/{s3_key}"
        return s3_path

    except Exception as e:
        logger.error(f"Error uploading to S3: {type(e).__name__} - {e}")
        return None


def download_from_s3(s3_path: str) -> list[dict] | None:
    try:
        if not s3_path.startswith("s3://"):
            logger.error(f"Invalid S3 path format: {s3_path}")
            return None

        bucket, _, key = s3_path[5:].partition("/")
        if not bucket or not key:
            logger.error(f"Malformed S3 path: {s3_path}")
            return None

        region = settings.AWS_DEFAULT_REGION
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=region,
        )

        response = s3_client.get_object(Bucket=bucket, Key=key)
        content = response["Body"].read()

        data = orjson.loads(content)

        return data

    except ClientError as e:
        logger.error(f"[S3 ERROR] {e}")
        return None
    except Exception as e:
        logger.error(f"[Unexpected Error] {e}")
        return None


def get_latest_local_file(local_path: Path, source: str, listing_type: str) -> Path:

    if not local_path.exists():
        raise FileNotFoundError(f"Directory not found: {local_path}")

    pattern = re.compile(rf"{source}_{listing_type}_(\d{{8}}_\d{{6}})\.json")

    files = [
        (f, pattern.search(f.name).group(1))
        for f in local_path.glob(f"{source}_{listing_type}_*.json")
        if pattern.search(f.name)
    ]

    if not files:
        raise FileNotFoundError("No apartment listings file found in directory.")

    return sorted(files, key=lambda x: x[1], reverse=True)[0][0]


def get_latest_s3_file(folder: str, source: str, listing_type: str) -> str | None:
    try:
        region = settings.AWS_DEFAULT_REGION
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=region,
        )

        bucket_name = settings.AWS_S3_BUCKET
        prefix = f"{folder}/{source}/{listing_type}/"

        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

        if "Contents" not in response:
            logger.warning(
                f"No files found in S3 bucket {bucket_name} with prefix {prefix}"
            )
            return None

        file_pattern = re.compile(rf"{source}_{listing_type}_(\d{{8}}_\d{{6}})\.json$")

        objects_with_timestamps = []
        for obj in response["Contents"]:
            key = obj["Key"]
            match = file_pattern.search(key)
            if match:
                timestamp_str = match.group(1)
                objects_with_timestamps.append((key, timestamp_str))

        if not objects_with_timestamps:
            logger.warning(
                f"No valid files found in S3 bucket {bucket_name} with prefix {prefix}"
            )
            return None

        latest_key = sorted(objects_with_timestamps, key=lambda x: x[1], reverse=True)[
            0
        ][0]
        s3_path = f"s3://{bucket_name}/{latest_key}"

        return s3_path

    except ClientError as e:
        logger.error(f"[S3 ERROR] {e}")
        return None
    except Exception as e:
        logger.error(f"Error getting latest S3 file for {listing_type}: {e}")
        return None


def extract_timestamp_from_filename(filename: str) -> str | None:
    match = re.search(r"\d{8}_\d{6}", filename)
    return match.group(0) if match else None


def load_from_s3(
    folder: str, source: str, listing_type: str
) -> tuple[list[dict] | None, str | None]:

    s3_path = get_latest_s3_file(folder, source, listing_type)

    if not s3_path:
        logger.error(f"No raw S3 file found for {source} | {listing_type}")
        return None, None

    timestamp = extract_timestamp_from_filename(s3_path)
    latest_listings = download_from_s3(s3_path)

    if not latest_listings:
        logger.error(f"No data found in S3 file for {source} | {listing_type}")
        return None, None

    logger.success(f"Downloaded data from {s3_path}")
    return latest_listings, timestamp


def load_from_local(
    folder: Path, source: str, listing_type: str
) -> tuple[list[dict] | None, str | None]:

    local_path = folder / source / listing_type
    local_file_path = get_latest_local_file(local_path, source, listing_type)

    if not local_file_path or not Path(local_file_path).exists():
        logger.error(f"No local raw file found for {source} | {listing_type}")
        return None, None

    latest_listings = load_json(local_file_path)
    timestamp = extract_timestamp_from_filename(local_file_path.name)
    return latest_listings, timestamp


def save_to_s3(
    data: list[dict], folder: str, source: str, listing_type: str, timestamp: str
) -> str:

    s3_path = upload_to_s3(
        data=data,
        folder=folder,
        source=source,
        listing_type=listing_type,
        timestamp=timestamp,
    )
    logger.success(f"Uploaded to {s3_path}")
    return s3_path


def save_to_local(
    data: list[dict], folder: Path, source: str, listing_type: str, timestamp: str
) -> str:

    file_dir = folder / source / listing_type
    file_dir.mkdir(parents=True, exist_ok=True)

    save_path = file_dir / f"{source}_{listing_type}_{timestamp}.json"
    save_json(save_path, data)

    logger.success(f"Saved cleaned data to {save_path}")
    return str(save_path)
