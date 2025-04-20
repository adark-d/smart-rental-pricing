import argparse
import os
import sys

from loguru import logger

from src.publisher.publisher import run_publisher
from src.scraper.scraper import run_scraper
from src.utils.publisher_utils import get_latest_scraped_file
from src.utils.settings import LOG_DIR, RAW_DIR


def setup_logger(step: str, debug: bool = False):
    os.makedirs(LOG_DIR, exist_ok=True)
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


def parse_args():
    parser = argparse.ArgumentParser(description="Run scraper and/or publish listings")
    parser.add_argument(
        "--limit", type=int, default=None, help="Limit number of listings"
    )
    parser.add_argument(
        "--threads", type=int, default=os.cpu_count(), help="Number of threads to use"
    )
    parser.add_argument(
        "--step",
        choices=["scrape", "publish"],
        default="all",
        help="Which step(s) to run: scrape, or publish",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug-level logging",
    )
    parser.add_argument(
        "--listing_type",
        choices=["rent", "sale"],
        default="rent",
        help="Choose rent or sale listing type",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    if args.step == "scrape":
        setup_logger("scraper", debug=args.debug)
        try:
            logger.info(f"Starting scraper step for {args.listing_type}...")
            scrape_success = run_scraper(args.listing_type)
            if not scrape_success:
                logger.error("Scraper step failed. Pipeline halted.")
                return 1
        except Exception as e:
            logger.exception(f"Scraper crashed: {e}")
            return 1

    if args.step == "publish":
        setup_logger("publisher", debug=args.debug)
        try:
            try:
                DEFAULT_FILE = get_latest_scraped_file(RAW_DIR, args.listing_type)
            except FileNotFoundError:
                logger.error(
                    f"File not found for {args.listing_type} listings. Pipeline halted."
                )
                return 1

            logger.info(f"Starting publisher step for {args.listing_type}...")

            publish_success = run_publisher(DEFAULT_FILE, args.threads, args.limit)
            if not publish_success:
                logger.error("Publisher step failed. Pipeline halted.")
                return 1
        except Exception as e:
            logger.exception(f"Publisher crashed: {e}")
            return 1

    logger.success("Pipeline completed successfully.")
    return 0


if __name__ == "__main__":
    exit(main())
