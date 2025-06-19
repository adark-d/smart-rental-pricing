# Smart Rental Pricing Pipeline Guide

## 🔄 Pipeline Overview

The Smart Rental Pricing pipeline consists of three main stages:

```
📡 SCRAPE → 🧽 CLEAN → 🚀 PUBLISH
    ↓         ↓         ↓
  Raw Data  Clean Data   API
```

### Pipeline Stages

1. **SCRAPE**: Collect raw listing data from sources (Tonaton)
2. **CLEAN**: Validate, normalize, and structure the data
3. **PUBLISH**: Upload cleaned data to the API database

## 🚀 Quick Start

### Run Complete Pipeline
```bash
# Process all listing types automatically
./pipeline.sh

# Or run individually
poetry run python run_pipeline.py --step full --source tonaton --listing_type rent
poetry run python run_pipeline.py --step full --source tonaton --listing_type sale
```

### Run Individual Steps
```bash
# Scrape data
poetry run python run_pipeline.py --step scrape --source tonaton --listing_type rent

# Clean scraped data
poetry run python run_pipeline.py --step clean --source tonaton --listing_type rent

# Publish to API
poetry run python run_pipeline.py --step publish --source tonaton --listing_type rent
```

## 📋 Command Reference

### Basic Usage
```bash
python run_pipeline.py --step <STEP> --source <SOURCE> --listing_type <TYPE>
```

### Required Arguments
- `--step`: Pipeline step to execute
  - `scrape` - Collect raw data from source
  - `clean` - Process and validate data  
  - `publish` - Upload to API
  - `full` - Run all steps sequentially
- `--source`: Data source (currently: `tonaton`, `jiji`)
- `--listing_type`: Property type (`rent` or `sale`)

### Optional Arguments
- `--debug` - Enable debug logging for troubleshooting
- `--concurrency <N>` - Concurrent requests for publishing (default: 20)
- `--batch-size <N>` - Batch size for publishing (default: 100)
- `--batch-delay <N>` - Delay between batches in seconds (default: 2.0)

### Examples

#### Production Pipeline Run
```bash
# Full pipeline with optimized settings
poetry run python run_pipeline.py \
  --step full \
  --source tonaton \
  --listing_type rent \
  --concurrency 30 \
  --batch-size 150
```

#### Debug Mode
```bash
# Run with detailed logging
poetry run python run_pipeline.py \
  --step scrape \
  --source tonaton \
  --listing_type rent \
  --debug
```

#### Custom Publishing Settings
```bash
# Gentle publishing (lower load on API)
poetry run python run_pipeline.py \
  --step publish \
  --source tonaton \
  --listing_type sale \
  --concurrency 10 \
  --batch-size 50 \
  --batch-delay 5.0
```

## 📁 File Structure

### Data Storage
```
data/
├── raw/              # Scraped data (unprocessed)
│   └── tonaton/
│       ├── rent/
│       └── sale/
├── cleaned/          # Processed data (validated)
│   └── tonaton/
│       ├── rent/
│       └── sale/
└── failed/           # Failed API uploads
    ├── rent_failed_listings.jsonl
    └── sale_failed_listings.jsonl
```

### Logs
```
logs/
├── scrape.log        # Scraping operations
├── clean.log         # Data cleaning
├── publish.log       # API publishing
└── full_pipeline.log # Complete pipeline runs
```

## ⚙️ Configuration

### Environment Settings
Configuration is managed via `configs/settings.yaml` using Dynaconf:

```yaml
# Development settings
env: "dev"
headless: true
API_URL: "http://localhost:8000"
API_TOKEN: "your-api-token-here"

paths:
  raw_data_dir: "data/raw"
  cleaned_data_dir: "data/cleaned"
  failed_data_dir: "data/failed"
  logs_dir: "logs"

# Scraper settings
sources:
  tonaton:
    scraper:
      base_url_rent: "https://tonaton.com/rent-apartments"
      base_url_sale: "https://tonaton.com/sale-apartments"
      wait_time: 2
      max_pages: 500
```

### API Authentication
Set your API token in settings:
```yaml
API_TOKEN: "your-jwt-token-from-api"
```

Or via environment variable:
```bash
export API_TOKEN="your-jwt-token"
```

## 🔍 Monitoring & Debugging

### Log Levels
- **INFO**: Normal operation progress
- **WARNING**: Non-critical issues (missing data, retries)
- **ERROR**: Step failures, connection issues
- **DEBUG**: Detailed execution information (use --debug flag)

### Common Issues

#### 1. Scraping Failures
```bash
# Check browser setup and network connectivity
poetry run python run_pipeline.py --step scrape --source tonaton --listing_type rent --debug
```

**Solutions:**
- Verify internet connection
- Check if Tonaton website is accessible
- Ensure Chrome/ChromeDriver is installed

#### 2. Data Cleaning Errors
```bash
# Review validation failures
tail -f logs/clean.log
```

**Solutions:**
- Check data format from scraper
- Review Pydantic model validation in `src/models/tonaton.py`
- Verify field mappings

#### 3. Publishing Failures
```bash
# Check API connectivity and authentication
poetry run python run_pipeline.py --step publish --source tonaton --listing_type rent --debug
```

**Solutions:**
- Verify API is running: `curl http://localhost:8000/api/v1/healthz`
- Check API token: `echo $API_TOKEN`
- Review failed listings: `cat data/failed/rent_failed_listings.jsonl`

### Performance Monitoring

#### Memory Usage
The scraper monitors memory usage automatically:
```
[Batch 1/5] Memory Usage: 245.67 MB
```

#### API Rate Limiting
Monitor rate limit headers in publishing logs:
```
[RATE LIMITED] Retrying after 60 seconds...
```

## 🚨 Error Recovery

### Failed Listings
Failed API uploads are saved to JSONL files for manual review:
```bash
# Review failed rent listings
cat data/failed/rent_failed_listings.jsonl | jq .

# Republish failed listings (manual process)
# 1. Fix data issues in the JSONL file
# 2. Convert back to JSON array
# 3. Place in cleaned data directory
# 4. Run publish step again
```

### Partial Pipeline Recovery
If pipeline fails at a specific step, resume from that point:
```bash
# If scraping completed but cleaning failed
poetry run python run_pipeline.py --step clean --source tonaton --listing_type rent
poetry run python run_pipeline.py --step publish --source tonaton --listing_type rent
```

## 📊 Performance Optimization

### Scraping Performance
- **Batch Processing**: Processes listings in batches to manage memory
- **Concurrent Extraction**: Multiple threads for data extraction
- **Resource Monitoring**: Automatic memory usage tracking

### Publishing Performance
- **Async HTTP**: Non-blocking HTTP requests
- **Batch Uploads**: Groups requests to reduce API load
- **Rate Limiting**: Respects API rate limits automatically

### Recommended Settings

#### Development
```bash
--concurrency 10 --batch-size 50 --batch-delay 3.0
```

#### Production
```bash
--concurrency 30 --batch-size 150 --batch-delay 1.0
```

#### Rate-Limited Environment
```bash
--concurrency 5 --batch-size 25 --batch-delay 10.0
```

## 🔄 Scheduling

### Cron Setup
Add to crontab for automated runs:
```bash
# Run pipeline daily at 2 AM
0 2 * * * cd /path/to/smart-rental-pricing && ./pipeline.sh >> logs/cron.log 2>&1

# Run twice daily
0 2,14 * * * cd /path/to/smart-rental-pricing && ./pipeline.sh
```

### Docker Scheduling
Use with Docker Compose for containerized scheduling:
```yaml
version: '3.8'
services:
  pipeline:
    build: .
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - API_TOKEN=${API_TOKEN}
    command: ["./pipeline.sh"]
```

## 🧪 Testing Pipeline

### Dry Run Mode
Test pipeline without actually publishing:
```bash
# Set API_URL to a test endpoint
export API_URL="http://httpbin.org/post"
poetry run python run_pipeline.py --step publish --source tonaton --listing_type rent
```

### Sample Data Testing
```bash
# Test with limited data
# Modify max_pages in settings.yaml to 1 for testing
poetry run python run_pipeline.py --step full --source tonaton --listing_type rent --debug
```

## 📈 Success Metrics

Monitor these indicators for healthy pipeline operation:

- **Scraping**: Successfully extracted listing count vs. expected
- **Cleaning**: Validation success rate (>90% typical)
- **Publishing**: API success rate (>95% target)
- **Timing**: Complete pipeline under 30 minutes for full run
- **Memory**: Peak usage under 1GB per batch

## 🆘 Support

### Logs Location
All logs are stored in `logs/` directory with rotation:
- **Retention**: 7 days
- **Size**: 1MB per file before rotation
- **Format**: `[YYYY-MM-DD HH:mm:ss] [LEVEL] message`

### Getting Help
1. **Check logs**: Start with `logs/<step>.log`
2. **Run with debug**: Add `--debug` flag for detailed output
3. **Verify settings**: Ensure `configs/settings.yaml` is correct
4. **Test components**: Run individual steps to isolate issues

---

**Quick Commands Summary:**
```bash
# Complete pipeline
./pipeline.sh

# Individual steps
python run_pipeline.py --step scrape --source tonaton --listing_type rent
python run_pipeline.py --step clean --source tonaton --listing_type rent  
python run_pipeline.py --step publish --source tonaton --listing_type rent

# Debug mode
python run_pipeline.py --step full --source tonaton --listing_type rent --debug
```