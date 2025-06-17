import argparse
import sys
from pathlib import Path

from loguru import logger

from src.cleaner.cleaner import run_cleaner
from src.scraper.scraper import run_scraper
from src.utils.settings import settings

VALID_STEPS = {
    "scrape": run_scraper,
    "clean": run_cleaner,
}


def setup_logger(step: str, debug: bool = False):
    log_dir = Path(settings.paths.logs_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"{step}.log"

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


def parse_arguments():
    parser = argparse.ArgumentParser(description="Run real estate pipeline step.")

    parser.add_argument(
        "--step",
        choices=["scrape", "clean"],
        required=True,
        help="Pipeline step to execute.",
    )
    parser.add_argument(
        "--source",
        choices=["tonaton", "jiji"],
        required=True,
        help="Pipeline source to execute.",
    )
    parser.add_argument(
        "--listing_type",
        choices=["rent", "sale"],
        default="rent",
        help="Specify listing type (rent or sale).",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging.",
    )
    return parser.parse_args()


def prepare_step_parameters(args):
    if args.step == "scrape":
        return {"source": args.source, "listing_type": args.listing_type}

    elif args.step == "clean":
        return {"source": args.source, "listing_type": args.listing_type}

    return {}


def main_pipeline(args):
    step = args.step

    if step not in VALID_STEPS:
        logger.error(f"Invalid step: {step}")
        return 1

    setup_logger(step, debug=args.debug)

    try:
        step_function = VALID_STEPS[step]
        step_params = prepare_step_parameters(args)

        result = step_function(**step_params)

        if result is False:
            logger.critical(f"Step '{step}' for '{args.listing_type}' failed.")
            return 1

        logger.success(
            f"Step '{step}' for '{args.listing_type}' completed successfully."
        )
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
