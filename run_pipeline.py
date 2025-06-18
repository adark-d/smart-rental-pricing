import argparse
import sys
from pathlib import Path

from loguru import logger

from src.cleaner.cleaner import run_cleaner
from src.publisher.publisher import run_publisher
from src.scraper.scraper import run_scraper
from src.utils.settings import settings

VALID_STEPS = {
    "scrape": run_scraper,
    "clean": run_cleaner,
    "publish": run_publisher,
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
        choices=["scrape", "clean", "publish", "full"],
        required=True,
        help="Pipeline step to execute ('full' runs all steps).",
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
    parser.add_argument(
        "--concurrency",
        type=int,
        default=20,
        help="Number of concurrent requests for publishing (default: 20).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        dest="batch_size",
        help="Batch size for publishing (default: 100).",
    )
    parser.add_argument(
        "--batch-delay",
        type=float,
        default=2.0,
        dest="batch_delay",
        help="Delay between batches in seconds (default: 2.0).",
    )

    return parser.parse_args()


def prepare_step_parameters(args):
    base_params = {"source": args.source, "listing_type": args.listing_type}

    if args.step == "scrape":
        return base_params
    elif args.step == "clean":
        return base_params
    elif args.step == "publish":
        return {
            **base_params,
            "concurrency": getattr(args, "concurrency", 20),
            "batch_size": getattr(args, "batch_size", 100),
            "batch_delay": getattr(args, "batch_delay", 2.0),
        }
    return base_params


def run_full_pipeline(args):
    steps = ["scrape", "clean", "publish"]

    setup_logger("full_pipeline", debug=args.debug)
    logger.info(f"Starting full pipeline for {args.source} | {args.listing_type}")

    for step in steps:
        logger.info(f"Running step: {step}")

        step_args = argparse.Namespace(**vars(args))
        step_args.step = step

        result = run_single_step(step_args)
        if result != 0:
            logger.error(f"Full pipeline failed at step: {step}")
            return result

    logger.success(
        f"Full pipeline completed successfully for {args.source} | {args.listing_type}"
    )
    return 0


def run_single_step(args):
    step = args.step

    if step not in VALID_STEPS:
        logger.error(f"Invalid step: {step}. Valid steps: {list(VALID_STEPS.keys())}")
        return 1

    try:
        step_function = VALID_STEPS[step]
        step_params = prepare_step_parameters(args)

        logger.info(f"Executing {step} with parameters: {step_params}")
        result = step_function(**step_params)

        if result is False or result is None:
            logger.critical(f"Step '{step}' for '{args.listing_type}' failed.")
            return 1

        logger.success(
            f"Step '{step}' for '{args.listing_type}' completed successfully."
        )
        return 0

    except FileNotFoundError as e:
        logger.error(f"[File Missing] {e}")
        return 1
    except ImportError as e:
        logger.error(f"[Import Error] Missing dependency: {e}")
        return 1
    except Exception as e:
        logger.exception(f"Step '{step}' crashed with error: {e}")
        return 1


def main_pipeline(args):
    try:
        logger.info(f"Running in environment: {getattr(settings, 'env', 'dev')}")
        if hasattr(settings, "API_URL"):
            logger.info(f"API URL: {settings.API_URL}")
        if hasattr(settings, "paths"):
            logger.info(f"Data paths configured: {bool(settings.paths)}")
    except Exception as e:
        logger.warning(f"Could not validate environment settings: {e}")

    if args.step == "full":
        return run_full_pipeline(args)
    else:
        setup_logger(args.step, debug=args.debug)
        return run_single_step(args)


if __name__ == "__main__":
    args = parse_arguments()
    exit_code = main_pipeline(args)
    sys.exit(exit_code)
