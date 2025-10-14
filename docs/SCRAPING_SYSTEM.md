# Future4200 Nightly Scraping System

This document describes the automated nightly scraping system that keeps the Future-Agent dataset up-to-date with the latest Future4200 forum discussions.

## Overview

The scraping system runs automatically every night at 2 AM UTC to:
1. Discover new threads on Future4200
2. Scrape thread content and metadata
3. Extract new questions from thread content
4. Merge new data with existing comprehensive dataset
5. Update DVC-tracked data files
6. Generate detailed reports

## Architecture

### Components

1. **GitHub Action Workflow** (`.github/workflows/nightly-scraping.yml`)
   - Triggers nightly at 2 AM UTC
   - Can be manually triggered with optional full scrape
   - Handles AWS credentials and DVC operations

2. **Nightly Scraper** (`scripts/nightly_scraper.py`)
   - Incremental scraping to avoid duplicates
   - Respectful rate limiting
   - Comprehensive error handling

3. **Data Merger** (`scripts/merge_scraping_data.py`)
   - Merges incremental data with existing dataset
   - Validates data integrity
   - Updates metadata and statistics

4. **Question Extractor** (`scripts/extract_questions.py`)
   - Extracts questions from new thread content
   - Categorizes questions by topic
   - Assesses question difficulty

5. **Report Generator** (`scripts/generate_scraping_report.py`)
   - Generates comprehensive scraping reports
   - Analyzes trends and metrics
   - Provides recommendations

### Data Flow

```
Future4200 Forum
       ↓
Nightly Scraper (discovers new threads)
       ↓
Content Scraping (extracts thread data)
       ↓
Data Merger (combines with existing data)
       ↓
Question Extractor (finds new questions)
       ↓
DVC Update (version control)
       ↓
Report Generation (metrics & analysis)
```

## Configuration

### Required Secrets

The GitHub Action requires these secrets to be configured:

- `AWS_ACCESS_KEY_ID`: AWS access key for S3 storage
- `AWS_SECRET_ACCESS_KEY`: AWS secret key for S3 storage
- `SLACK_WEBHOOK_URL`: (Optional) Slack webhook for notifications

### DVC Configuration

```bash
# Configure DVC remote
dvc remote add -d s3 s3://future-agent-dvc-data

# Pull existing data
dvc pull data/comprehensive_scraping_results.json
dvc pull data/extracted_questions.json
```

## Usage

### Manual Triggering

You can manually trigger the scraping workflow:

```bash
# Trigger with incremental scraping (default)
gh workflow run nightly-scraping.yml

# Trigger with full scrape
gh workflow run nightly-scraping.yml -f force_full_scrape=true
```

### Local Testing

Test the scraping scripts locally:

```bash
# Test nightly scraper
python scripts/nightly_scraper.py \
  --output data/test_scraping.json \
  --existing data/comprehensive_scraping_results.json \
  --last-run \
  --max-pages 2

# Test data merger
python scripts/merge_scraping_data.py \
  --existing data/comprehensive_scraping_results.json \
  --incremental data/test_scraping.json \
  --output data/merged_data.json \
  --validate

# Test question extraction
python scripts/extract_questions.py \
  --input data/merged_data.json \
  --output data/test_questions.json \
  --incremental \
  --existing-questions data/extracted_questions.json

# Generate report
python scripts/generate_scraping_report.py \
  --output data/test_report.json \
  --new-threads 5 \
  --incremental-file data/test_scraping.json
```

## Data Structure

### Comprehensive Scraping Results

```json
{
  "scraping_timestamp": "2025-10-13T02:00:00Z",
  "total_threads": 7061,
  "scraped_threads": 9963,
  "failed_threads": 17,
  "last_update": "2025-10-13T02:15:00Z",
  "update_summary": {
    "timestamp": "2025-10-13T02:15:00Z",
    "new_threads_added": 12,
    "successful_new_threads": 11,
    "failed_new_threads": 1,
    "total_threads_after_update": 7073,
    "processing_time": 45.2
  },
  "results": [...]
}
```

### Thread Data Structure

```json
{
  "success": true,
  "data": {
    "thread_id": "49374",
    "title": "Where can I find cbn isolate",
    "author": "LazyoldfarmwookieNC",
    "content": "Thread content...",
    "markdown": "Markdown version...",
    "post_count": 8,
    "view_count": 2000,
    "url": "https://future4200.com/t/where-can-i-find-cbn-isolate/49374",
    "linksOnPage": [...],
    "category": "extraction",
    "last_activity": "2025-10-13T02:00:00Z",
    "scraped_at": "2025-10-13T02:05:00Z"
  }
}
```

### Question Data Structure

```json
{
  "question": "How do I safely extract CBD from hemp?",
  "source": "content",
  "thread_url": "https://future4200.com/t/...",
  "author": "cannabis_expert",
  "context": "Thread context...",
  "category": "extraction",
  "difficulty": "intermediate",
  "thread_id": "49374",
  "extracted_at": "2025-10-13T02:10:00Z"
}
```

## Monitoring

### Success Metrics

- **New Threads Found**: Number of new threads discovered
- **Success Rate**: Percentage of successfully scraped threads
- **Processing Time**: Time taken to complete scraping
- **Data Quality**: Validation of scraped data integrity

### Alerts

The system sends notifications for:
- Scraping failures
- Low success rates
- Data validation errors
- Unusual activity patterns

### Reports

Daily reports include:
- Scraping summary
- Data metrics and trends
- Performance recommendations
- Next scheduled scrape time

## Troubleshooting

### Common Issues

1. **No New Threads Found**
   - Check if scraping patterns need updating
   - Verify forum structure hasn't changed
   - Review scraping logs for errors

2. **High Failure Rate**
   - Check network connectivity
   - Verify rate limiting isn't too aggressive
   - Review forum access permissions

3. **Data Validation Errors**
   - Check for changes in thread structure
   - Verify parsing logic is up-to-date
   - Review data format requirements

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python scripts/nightly_scraper.py --output debug_scraping.json
```

### Logs

Check GitHub Actions logs for detailed execution information:
- Go to Actions tab in GitHub repository
- Click on latest "Nightly Future4200 Thread Scraping" run
- Review step-by-step execution logs

## Maintenance

### Regular Tasks

1. **Weekly**: Review scraping reports and success rates
2. **Monthly**: Update scraping patterns based on forum changes
3. **Quarterly**: Review and optimize scraping performance
4. **As Needed**: Update dependencies and security patches

### Data Cleanup

The system automatically manages data versioning through DVC. Old data can be archived:

```bash
# Archive old data
dvc gc --cloud

# Check storage usage
dvc cache dir
```

## Security

### Rate Limiting

The scraper implements respectful rate limiting:
- 1 second delay between thread requests
- 0.5 second delay between page requests
- User-Agent identification as research bot

### Data Privacy

- Only public forum content is scraped
- No user authentication required
- No personal data collected beyond usernames
- All data stored securely in AWS S3

### Compliance

The scraping system is designed to:
- Respect robots.txt guidelines
- Follow ethical web scraping practices
- Comply with forum terms of service
- Maintain data privacy standards