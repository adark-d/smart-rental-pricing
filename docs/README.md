# Smart Rental Pricing and Recommendation System for Accra

## Project Overview

This project builds a data pipeline and API for real estate listings in Accra, with components for:
- Web scraping real estate listings (running outside containers)
- Cleaning and processing the data (running in Airflow)
- Publishing data via API and S3 (running in Airflow)
- Providing pricing recommendations

## Project Architecture

This project follows a decoupled architecture where:
1. Web scraping happens outside containers on the host machine
2. Data is saved to S3 for durability
3. Airflow orchestrates the processing pipeline
4. FastAPI serves the processed data

```
┌───────────────────┐       ┌───────────────────┐       ┌───────────────────┐
│                   │       │                   │       │                   │
│  External Scraper │ ─────►│        S3         │ ─────►│  Airflow Pipeline │
│ (Host Machine)    │       │   (Data Storage)  │       │  (In Container)   │
│                   │       │                   │       │                   │
└───────────────────┘       └───────────────────┘       └─────────┬─────────┘
                                                                  │
                                                                  ▼
┌───────────────────┐                                   ┌───────────────────┐
│                   │                                   │                   │
│     End Users     │ ◄─────────────────────────────── │     FastAPI       │
│                   │                                   │                   │
└───────────────────┘                                   └───────────────────┘
```

## Project Structure

- `app/` - FastAPI application
- `src/` - Core pipeline components
  - `scraper/` - Web scraping code
  - `cleaner/` - Data cleaning and processing
  - `publisher/` - Data publishing (API and S3)
  - `utils/` - Shared utilities
- `airflow/` - Airflow DAGs for task orchestration
- `data/` - Local data storage directories
- `configs/` - Configuration files
- `run_scraper.sh` - Shell script for running the scraper on the host machine

## Setup Instructions

### 1. Environment Configuration

Copy the example environment file and fill in your details:
```bash
cp .env.example .env
```

Required settings:
- Database credentials
- AWS credentials (for S3 access)
- Airflow API credentials

### 2. Start Docker Services

```bash
# Build and start all containers
make build
make up

# Run database migrations
make run-upgrade
```

Once the containers are running, access the Airflow UI at http://localhost:8080. The default credentials are:
- Username: `admin`
- Password: `admin`

Make sure to update configs/settings.yaml if you change the Airflow credentials.

### 3. Set Up Host Scraper

The scraper runs outside containers on your host machine. Make sure you have the following prerequisites:

1. **Chrome**: Required for web scraping (installed on your system)
2. **Poetry**: Required for dependency management
3. **Python 3.11+**: Required for running the scraper

Note: The scraper uses undetected-chromedriver to automatically handle browser automation without detection issues or version compatibility problems.

Setup steps:
```bash
# Install Poetry if you don't have it
curl -sSL https://install.python-poetry.org | python3 -

# Install Python dependencies using Poetry
poetry install

# Make the scraper script executable
chmod +x run_scraper.sh
```

### 4. Set Up Scheduled Scraping

Add a cron job to run the scraper weekly:

```bash
# Open crontab editor
crontab -e

# Add the following line (runs every Monday at 6 AM)
0 6 * * 1 /full/path/to/run_scraper.sh >> /full/path/to/logs/cron.log 2>&1
```

## Running the Pipeline

### Manual Execution of the Scraper

```bash
# Using the shell script directly
./run_scraper.sh                # Both rent and sale
./run_scraper.sh rent           # Just rent listings
./run_scraper.sh sale           # Just sale listings

# Using make commands
make run-scraper               # Both rent and sale
make run-scraper-rent          # Just rent listings
make run-scraper-sale          # Just sale listings
```

The scraper will:
1. Fetch real estate listings for both rent and sale properties
2. Save the data to S3
3. Attempt to trigger the Airflow pipeline automatically

If the Airflow triggering fails (e.g., due to authentication issues), you can:
1. Check the logs to find the S3 path where data was uploaded
2. Go to Airflow web UI (http://localhost:8080)
3. Trigger the DAG manually with the S3 paths as configuration:
   ```json
   {
     "s3_paths": {
       "rent": "s3://your-bucket/raw/rent/rent_20250425_123456.json",
       "sale": "s3://your-bucket/raw/sale/sale_20250425_123456.json"
     }
   }
   ```

### Airflow Pipeline Management

#### Monitoring Airflow

Monitor and manage Airflow operations:

```bash
# List available DAGs
make list-dags

# Ensure the pipeline DAG is unpaused
make unpause-dag
```

#### Manually Triggering the Pipeline

You can manually trigger the Airflow DAG without scraping when you already have data in S3:

```bash
# Trigger with rent data only
make trigger-dag-rent RENT_PATH="s3://your-bucket/raw/rent/rent_20250425_123456.json"

# Trigger with sale data only
make trigger-dag-sale SALE_PATH="s3://your-bucket/raw/sale/sale_20250425_123456.json"

# Trigger with both data types
make trigger-dag-both RENT_PATH="s3://your-bucket/raw/rent/rent_20250425_123456.json" SALE_PATH="s3://your-bucket/raw/sale/sale_20250425_123456.json"
```

Or use the run_pipeline.py script directly:

```bash
# Trigger with one or more paths
poetry run python run_pipeline.py --step trigger-dag --rent-path "s3://path/to/rent.json" --sale-path "s3://path/to/sale.json"
```

Access the Airflow UI at http://localhost:8080 (user: admin, pass: admin) to monitor the pipeline execution.

## Testing

### Test Airflow Setup

A test DAG is provided to verify Airflow functionality:

```bash
# Unpause the test DAG
make unpause-test-dag

# Trigger the test DAG
make test-dag
```

The test DAG performs the following checks:
- Basic Airflow functionality
- Database connectivity
- API connectivity 
- Pipeline script availability

### Manual Pipeline Testing

You can test individual pipeline components manually:

```bash
# Run the scraper
make run-scraper

# Test just the cleaning step with existing data
make run-cleaner

# Test API publishing with existing cleaned data
make run-publisher-api
```

## Accessing the API

- API documentation: http://localhost:8000/docs
- Health check: http://localhost:8000/api/v1/health/
- Listings endpoint: http://localhost:8000/api/v1/listings/

## Development Commands

```bash
# Install dependencies
make install

# Format code
make format

# Run linting
make lint

# Run pre-commit hooks
make precommit
```

## Architecture Benefits

This architecture offers several advantages:
1. **Separation of concerns**: Web scraping is isolated from the rest of the pipeline
2. **Reliability**: S3 provides durable storage between pipeline steps
3. **Scalability**: Each component can scale independently
4. **Maintainability**: Clear boundaries between components
5. **Robustness**: Browser dependencies are on the host machine, avoiding container issues