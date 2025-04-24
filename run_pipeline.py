import argparse
import os
import sys

from loguru import logger

from src.cleaner.cleaner import run_cleaner
from src.publisher.publisher_api import run_publisher_api
from src.scraper.scraper import run_scraper, trigger_airflow_dag
from src.utils.publisher_utils import get_latest_scraped_file
from src.utils.settings import CLEANED_DIR, LOG_DIR, RAW_DIR

# -------------------------
# Step mapping dictionary
# -------------------------
VALID_STEPS = {
    "scrape": run_scraper,
    "clean": run_cleaner,
    "publish_api": run_publisher_api,
    "trigger-dag": trigger_airflow_dag,
}


# -------------------------
# Setup logging
# -------------------------
def setup_logger(step: str, debug: bool = False):
    log_file = LOG_DIR / f"{step}.log"
    logger.remove()
    logger.add(
        log_file,
        rotation="1 MB",
        retention="7 days",
        level="DEBUG" if debug else "INFO",
        format="[{time:YYYY-MM-DD HH:mm:ss}] [{level}] {message}",
        enqueue=True,
    )
    logger.add(
        sys.stdout,
        level="DEBUG" if debug else "INFO",
        enqueue=True,
    )


# -------------------------
# Parse CLI arguments
# -------------------------
def parse_arguments():
    parser = argparse.ArgumentParser(description="Run real estate pipeline step.")

    parser.add_argument(
        "--step",
        choices=["scrape", "clean", "publish_api", "trigger-dag"],
        required=True,
        help="Pipeline step to execute.",
    )
    parser.add_argument(
        "--listing_type",
        choices=["rent", "sale"],
        default="rent",
        help="Specify listing type (rent or sale).",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=os.cpu_count(),
        help="Number of threads for publishing to API.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of listings to publish.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging.",
    )
    parser.add_argument(
        "--rent-path",
        help="S3 path to rent listings data (for trigger-dag step)",
    )
    parser.add_argument(
        "--sale-path",
        help="S3 path to sale listings data (for trigger-dag step)",
    )

    return parser.parse_args()


# -------------------------
# Prepare arguments for step
# -------------------------
def prepare_step_parameters(args):
    if args.step == "scrape":
        return {"listing_type": args.listing_type}

    elif args.step == "clean":
        raw_file = get_latest_scraped_file(RAW_DIR, args.listing_type)
        return {"file": raw_file, "listing_type": args.listing_type}

    elif args.step == "publish_api":
        cleaned_file = get_latest_scraped_file(CLEANED_DIR, args.listing_type)
        return {
            "file": cleaned_file,
            "threads": args.threads,
            "limit": args.limit,
        }

    elif args.step == "trigger-dag":
        # For triggering the Airflow DAG with S3 paths
        s3_paths = {}
        if args.rent_path:
            s3_paths["rent"] = args.rent_path
        if args.sale_path:
            s3_paths["sale"] = args.sale_path

        if not s3_paths:
            logger.error(
                "At least one S3 path (--rent-path or --sale-path) must be provided for \
                trigger-dag step"
            )
            sys.exit(1)

        # The trigger_airflow_dag function expects a parameter called 's3_paths'
        return {"s3_paths": s3_paths}

    return {}


# -------------------------
# Run pipeline entrypoint
# -------------------------
def main_pipeline(args):
    step = args.step

    if step not in VALID_STEPS:
        logger.error(f"Invalid step: {step}")
        return 1

    setup_logger(step, debug=args.debug)

    try:
        step_function = VALID_STEPS[step]
        step_params = prepare_step_parameters(args)

        logger.info(f"Starting '{step}' step for {args.listing_type}...")

        result = step_function(**step_params)

        if result is False:
            logger.critical(f"Step '{step}' failed.")
            return 1

        logger.success(f"Step '{step}' completed successfully.")
        return 0

    except FileNotFoundError as e:
        logger.error(f"[File Missing] {e}")
        return 1
    except Exception as e:
        logger.exception(f"Step '{step}' crashed with error: {e}")
        return 1


if __name__ == "__main__":
    args = parse_arguments()
    exit_code = main_pipeline(args)
    sys.exit(exit_code)
