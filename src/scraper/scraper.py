import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import boto3
from botocore.exceptions import ClientError
from loguru import logger

from src.scraper.collector import get_listing_links
from src.scraper.parser import extract_detail_from_page
from src.utils.scraper_utils import extract_listing_id, init_browser
from src.utils.settings import settings


def scrape_single_listing(url: str, listing_type: str) -> dict | None:
    """
    Scrape details from a single property listing

    Args:
        driver: Initialized WebDriver
        url: URL of the listing
        listing_type: Type of listing ("rent" or "sale")

    Returns:
        dict: Scraped data for the listing or None if there was an error
    """

    driver = init_browser()
    try:
        extracted_id = extract_listing_id(url)
        if extracted_id:
            time.sleep(3)
            return extract_detail_from_page(driver, url, extracted_id, listing_type)
        else:
            logger.warning(f"[SKIPPING] Not apartment listing: {url}")
    except Exception as e:
        logger.warning(f"[SCRAPE FAIL] {url}: {e}")
    finally:
        driver.quit()
    return None


def scrape_listings(listing_type: str = "rent") -> list:
    """
    Scrape all listings of a specific type

    Args:
        listing_type: Type of listing to scrape ("rent" or "sale")

    Returns:
        list: List of scraped listing records, or empty list if failed
    """
    logger.info(f"Starting scraping for {listing_type} listings")

    # Initialize driver once and reuse
    driver = init_browser()

    try:
        # Get listing links
        links = get_listing_links(driver, listing_type)
        logger.info(f"Found {len(links)} links to scrape")

        # Scrape each listing
        records = []
        max_workers = min(4, os.cpu_count())

        # We need a separate browser instance for each thread
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(scrape_single_listing, url, listing_type)
                for url in links
            ]
            for i, future in enumerate(as_completed(futures), start=1):
                result = future.result()
                if result:
                    logger.success(f"[{i}/{len(links)}] Scraped {result['listing_id']}")
                    records.append(result)

        logger.success(f"Successfully scraped {len(records)} listings")
        return records

    except Exception as e:
        logger.error(f"Error during scraping process: {e}")
        return []
    finally:
        # Always close the initial driver
        driver.quit()


def ensure_s3_bucket_exists():
    """
    Ensure the S3 bucket exists, creating it if necessary
    """
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
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


def upload_to_s3(data, listing_type):
    """
    Upload scraped data to S3

    Args:
        data: Listing data to upload
        listing_type: Type of listing ("rent" or "sale")

    Returns:
        str: The S3 path where the data was uploaded, or None if failed
    """
    if not data:
        logger.error("No data to upload")
        return None

    try:
        # Ensure bucket exists
        ensure_s3_bucket_exists()

        # Create S3 client
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

        # Create filename with timestamp and organize by listing type
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        s3_key = f"raw/{listing_type}/{listing_type}_{timestamp}.json"

        # Upload data to S3
        s3_client.put_object(
            Bucket=settings.S3_BUCKET,
            Key=s3_key,
            Body=json.dumps(data),
            ContentType="application/json",
        )

        # Return the S3 path
        s3_path = f"s3://{settings.S3_BUCKET}/{s3_key}"
        logger.info(f"Successfully uploaded to {s3_path}")
        return s3_path

    except Exception as e:
        logger.error(f"Error uploading to S3: {e}")
        return None


def trigger_airflow_dag(s3_paths):
    """
    Trigger the Airflow DAG with the S3 paths

    Args:
        s3_paths: Dict mapping listing types to S3 paths

    Returns:
        bool: True if the DAG was triggered successfully, False otherwise
    """
    if not s3_paths:
        logger.error("No S3 paths provided to trigger Airflow DAG")
        return False

    try:
        import json
        import subprocess

        # Define the parameters
        dag_id = "real_estate_data_pipeline"

        # When running inside Docker, we should connect directly to the Airflow container
        # Use 'docker exec' to run the CLI command directly inside the Airflow container

        # Prepare the conf parameter with S3 paths
        conf_json = json.dumps({"s3_paths": s3_paths})

        # Construct the docker exec command to trigger the DAG
        command = [
            "docker",
            "exec",
            "airflow_webserver",
            "airflow",
            "dags",
            "trigger",
            "-c",
            conf_json,
            dag_id,
        ]

        logger.info(f"Triggering Airflow DAG '{dag_id}' using CLI inside container")
        logger.info(f"Command: {' '.join(command)}")
        logger.info(f"Config: {conf_json}")

        # Execute the command
        process = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # Check if the command was successful
        if process.returncode == 0:
            logger.success(f"Successfully triggered Airflow DAG with paths: {s3_paths}")
            logger.debug(f"Command output: {process.stdout}")
            return True
        else:
            logger.error(
                f"Failed to trigger Airflow DAG. Return code: {process.returncode}"
            )
            logger.error(f"Error message: {process.stderr}")

            # Check if the DAG exists
            check_command = [
                "docker",
                "exec",
                "airflow_webserver",
                "airflow",
                "dags",
                "list",
            ]
            logger.info("Checking available DAGs...")
            check_process = subprocess.run(
                check_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            if check_process.returncode == 0:
                logger.info(f"Available DAGs:\n{check_process.stdout}")

                # Check specifically for our DAG
                if dag_id in check_process.stdout:
                    logger.info(
                        f"The DAG '{dag_id}' exists, but could not be triggered"
                    )
                else:
                    logger.error(f"The DAG '{dag_id}' does not exist in Airflow")
            else:
                logger.error(f"Failed to list DAGs: {check_process.stderr}")

            return False

    except Exception as e:
        logger.error(f"Error triggering Airflow DAG: {e}")
        return False


def run_scraper(listing_type="rent"):
    """
    Main entry point for scraper functionality

    This function handles the complete flow:
    1. Scrape listings
    2. Upload to S3
    3. Trigger Airflow DAG (optional)

    Args:
        listing_type: Type of listing to scrape ("rent" or "sale")

    Returns:
        bool: True if the essential steps were successful, False otherwise
    """
    try:
        # Step 1: Scrape listings
        logger.info(f"=== Starting {listing_type} scraper pipeline ===")
        records = scrape_listings(listing_type)

        if not records:
            logger.error(f"No listings scraped for {listing_type}")
            return False

        # Step 2: Upload to S3
        s3_path = upload_to_s3(records, listing_type)
        if not s3_path:
            logger.error(f"Failed to upload {listing_type} data to S3")
            return False

        # Essential steps (scraping and S3 upload) completed successfully
        logger.success(
            f"Successfully scraped and uploaded {listing_type} data to S3: {s3_path}"
        )

        # Step 3: Trigger Airflow DAG (optional - we consider it a success even if this fails)
        try:
            success = trigger_airflow_dag({listing_type: s3_path})
            if not success:
                logger.warning(
                    "Failed to trigger Airflow DAG, but data was successfully scraped and uploaded"
                )
                logger.info(
                    f"You can manually trigger the DAG in Airflow with the S3 path: {s3_path}"
                )
                # We still return True because the essential steps succeeded
        except Exception as e:
            logger.warning(f"Error triggering Airflow DAG: {e}")
            logger.info(
                f"You can manually trigger the DAG in Airflow with the S3 path: {s3_path}"
            )
            # We still return True because the essential steps succeeded

        logger.info(f"Successfully completed {listing_type} scraper pipeline")
        return True

    except Exception as e:
        logger.error(f"Error in scraper pipeline: {e}")
        return False
