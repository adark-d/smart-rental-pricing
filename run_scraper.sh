#!/bin/bash
#
# Smart Rental Pricing - Host Scraper
#
# This script runs the scraper on the host machine to:
# 1. Scrape listings from the web
# 2. Upload them to S3
# 3. Trigger the Airflow DAG
#
# Usage: ./run_scraper.sh [rent|sale|both]
#

# Change to the project directory
cd "$(dirname "$0")"

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Error: Poetry is not installed. Please install it first (https://python-poetry.org/docs/#installation)"
    exit 1
fi

# Ensure dependencies are installed
poetry install --no-interaction

# Set up logging
LOG_DIR="logs"
mkdir -p "$LOG_DIR"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="${LOG_DIR}/scraper_${TIMESTAMP}.log"

# Default to processing both listing types
LISTING_TYPE=${1:-both}

echo "[$(date)] Starting scraper for $LISTING_TYPE listings" | tee -a "$LOG_FILE"

if [ "$LISTING_TYPE" = "both" ]; then
    # Run the rent scraper
    echo "[$(date)] Processing rent listings..." | tee -a "$LOG_FILE"
    poetry run python run_pipeline.py --step scrape --listing_type rent 2>&1 | tee -a "$LOG_FILE"
    RENT_EXIT_CODE=${PIPESTATUS[0]}
    
    # Run the sale scraper
    echo "[$(date)] Processing sale listings..." | tee -a "$LOG_FILE"
    poetry run python run_pipeline.py --step scrape --listing_type sale 2>&1 | tee -a "$LOG_FILE"
    SALE_EXIT_CODE=${PIPESTATUS[0]}
    
    # Check results
    if [ $RENT_EXIT_CODE -eq 0 ] || [ $SALE_EXIT_CODE -eq 0 ]; then
        echo "[$(date)] Scraping completed successfully" | tee -a "$LOG_FILE"
        exit 0
    else
        echo "[$(date)] Scraping failed for both listing types" | tee -a "$LOG_FILE"
        exit 1
    fi
else
    # Run a single listing type
    echo "[$(date)] Processing $LISTING_TYPE listings..." | tee -a "$LOG_FILE"
    poetry run python run_pipeline.py --step scrape --listing_type "$LISTING_TYPE" 2>&1 | tee -a "$LOG_FILE"
    EXIT_CODE=${PIPESTATUS[0]}
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo "[$(date)] Scraping completed successfully" | tee -a "$LOG_FILE"
        exit 0
    else
        echo "[$(date)] Scraping failed" | tee -a "$LOG_FILE"
        exit 1
    fi
fi