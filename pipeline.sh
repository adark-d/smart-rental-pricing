#!/bin/bash

# Cleanup files to make sure no stray data from prior runs
rm -rf data/ logs

# Run transformation steps
poetry run python run_pipeline.py --step scrape --source tonaton --listing_type rent
poetry run python run_pipeline.py --step scrape --source tonaton --listing_type sale
poetry run python run_pipeline.py --step clean --source tonaton --listing_type rent
poetry run python run_pipeline.py --step clean --source tonaton --listing_type sale