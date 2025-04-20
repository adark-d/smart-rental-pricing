import argparse
import os
import sys

from loguru import logger

from src.publisher.publisher import run_publisher
from src.scraper.scraper import run_scraper
from src.utils.settings import LOG_DIR, RAW_DIR

DEFAULT_FILE = RAW_DIR / "apartment_listings.json"


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
        "--file", type=str, default=str(DEFAULT_FILE), help="Path to scraped JSON file"
    )
    parser.add_argument(
        "--limit", type=int, default=None, help="Limit number of listings"
    )
    parser.add_argument(
        "--threads", type=int, default=os.cpu_count(), help="Number of threads to use"
    )
    parser.add_argument(
        "--step",
        choices=["scrape", "publish", "all"],
        default="all",
        help="Which step(s) to run: scrape, publish, or all",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug-level logging",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.step in ["scrape", "all"]:
        setup_logger("scraper", debug=args.debug)
        try:
            logger.info("Starting scraper step...")
            scrape_success = run_scraper()
            if not scrape_success:
                logger.error("Scraper step failed. Pipeline halted.")
                return 1
        except Exception as e:
            logger.exception(f"Scraper crashed: {e}")
            return 1

    if args.step in ["publish", "all"]:
        setup_logger("publisher", debug=args.debug)
        try:
            logger.info("Starting publisher step...")
            publish_success = run_publisher(args.file, args.threads, args.limit)
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
