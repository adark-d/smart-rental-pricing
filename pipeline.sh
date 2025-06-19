#!/bin/bash

# Smart Rental Pricing Pipeline Script
rm -rf data/ logs/

# poetry run python run_pipeline.py --step full --source tonaton --listing_type rent
# poetry run python run_pipeline.py --step full --source tonaton --listing_type sale

# Option 2: Run individual steps (uncomment if you prefer granular control)
poetry run python run_pipeline.py --step scrape --source tonaton --listing_type rent
poetry run python run_pipeline.py --step scrape --source tonaton --listing_type sale

poetry run python run_pipeline.py --step clean --source tonaton --listing_type rent
poetry run python run_pipeline.py --step clean --source tonaton --listing_type sale

# poetry run python run_pipeline.py --step publish --source tonaton --listing_type rent
# poetry run python run_pipeline.py --step publish --source tonaton --listing_type sale
