# News Data Pipeline Project

A complete streaming + batch data pipeline using NewsAPI, Apache Kafka, Apache Airflow, and SQLite, all containerized with Docker Compose.

## Team Members
- Igenbek Zhaina
- Tolebek Nazym
- Spandiyar Kuanysh

---

## Table of Contents
- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Technologies Used](#technologies-used)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Project Structure](#project-structure)
- [DAGs Description](#dags-description)
- [Database Schema](#database-schema)
- [Usage Guide](#usage-guide)
- [Monitoring & Troubleshooting](#monitoring--troubleshooting)
- [API Information](#api-information)

---

## Project Overview

This project demonstrates a production-ready data engineering pipeline that:
1. **Continuously ingests** real-time news data from NewsAPI
2. **Streams** raw data through Apache Kafka
3. **Cleans and processes** data using Pandas
4. **Stores** structured data in SQLite
5. **Computes** daily analytics and summaries
6. **Orchestrates** all workflows through Apache Airflow

### Data Flow
```
NewsAPI → DAG 1 (Producer) → Kafka → DAG 2 (Cleaner) → SQLite (events) → DAG 3 (Analytics) → SQLite (daily_summary)
```

---

## Architecture

### System Components

1. **Apache Kafka**: Message broker for streaming raw news data
2. **Apache Zookeeper**: Coordination service for Kafka
3. **Apache Airflow**: Workflow orchestration and scheduling
4. **PostgreSQL**: Airflow metadata database
5. **SQLite**: Application data storage
6. **NewsAPI**: External data source: https://newsapi.org

### Three-Stage Pipeline

#### Stage 1: Data Ingestion (DAG 1)
- **Schedule**: `@hourly` (runs for 55 minutes each hour)
- **Function**: Fetches news articles from NewsAPI every 2 minutes
- **Output**: Raw JSON messages to Kafka topic `raw_events`

#### Stage 2: Data Cleaning (DAG 2)
- **Schedule**: `@hourly`
- **Function**: Consumes Kafka messages, cleans data using Pandas
- **Output**: Cleaned records in SQLite `events` table

#### Stage 3: Analytics (DAG 3)
- **Schedule**: `@daily`
- **Function**: Computes aggregated metrics from cleaned data
- **Output**: Summary statistics in SQLite `daily_summary` table

---

## Technologies Used

| Technology | Version | Purpose |
|------------|---------|---------|
| Apache Airflow | 2.7.0 | Workflow orchestration |
| Apache Kafka | 7.4.0 | Message streaming |
| Apache Zookeeper | 7.4.0 | Kafka coordination |
| PostgreSQL | 13 | Airflow metadata |
| SQLite | 3 | Data storage |
| Python | 3.10 | Programming language |
| Pandas | 2.0.3 | Data processing |
| kafka-python | 2.0.2 | Kafka client |
| Docker | Latest | Containerization |
| Docker Compose | Latest | Multi-container orchestration |

---

## Prerequisites

Before starting, ensure you have:

1. **Docker Desktop** installed and running
   - Download from: https://www.docker.com/products/docker-desktop

2. **NewsAPI Key**
   - Sign up at: https://newsapi.org
   - Free tier provides 100 requests/day

3. **Minimum System Requirements**
   - 8GB RAM
   - 10GB free disk space
   - Stable internet connection

---

## Installation & Setup

### Step 1: Clone the Repository

```bash
git clone <your-repository-url>
cd news-pipeline
```

### Step 2: Verify Project Structure

```bash
news-pipeline/
├── airflow/
│   └── dags/
│       ├── job1_ingestion_dag.py
│       ├── job2_clean_store_dag.py
│       └── job3_daily_summary_dag.py
├── data/             # SQLite database will be created here
├── report/           # Project report goes here
├── src/
│   ├── db_utils.py
│   ├── job1_producer.py
│   ├── job2_cleaner.py
│   └── job3_analytics.py
├── docker-compose.yml
├── requirements.txt
└── README.md
```

### Step 3: Configure NewsAPI Key

1. Open `docker-compose.yml`
2. Find the line: `NEWS_API_KEY: 'YOUR_API_KEY_HERE'`
3. Replace `YOUR_API_KEY_HERE` with your actual API key
4. **Important**: This appears in **TWO** places (airflow-webserver and airflow-scheduler)

```yaml
# Example:
NEWS_API_KEY: 'abc123def456ghi789'  # Replace with your key
```

### Step 4: Start the Pipeline

```bash
# Start all services
docker-compose up -d

# Wait 30-60 seconds for services to initialize
```

### Step 5: Verify Services are Running

```bash
# Check container status
docker-compose ps

# All services should show "Up" status:
# - zookeeper
# - kafka
# - postgres
# - airflow-init (will exit after completion)
# - airflow-webserver
# - airflow-scheduler
```

### Step 6: Access Airflow UI

1. Open browser: http://localhost:8080
2. Login credentials:
   - **Username**: `admin`
   - **Password**: `admin`

### Step 7: Enable DAGs

In the Airflow UI:
1. You should see 3 DAGs listed
2. Toggle each DAG to **ON** (click the toggle switch)
3. DAGs will start running automatically according to their schedules

**DAGs to enable:**
- `job1_continuous_ingestion` (@hourly)
- `job2_hourly_cleaning` (@hourly)
- `job3_daily_analytics` (@daily)

### Step 8: Verify Data Collection

After 10-15 minutes, check if database was created:

```bash
# Check if database file exists
ls -la data/

# Should see: app.db
```

---

## Project Structure

### Directory Layout

```
news-pipeline/
│
├── docker-compose.yml          # Docker orchestration configuration
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── airflow/
│   └── dags/
│       ├── job1_ingestion_dag.py       # DAG 1: Continuous data ingestion
│       ├── job2_clean_store_dag.py     # DAG 2: Hourly data cleaning
│       └── job3_daily_summary_dag.py   # DAG 3: Daily analytics
│
├── src/
│   ├── db_utils.py            # Database connection and initialization
│   ├── job1_producer.py       # Kafka producer (NewsAPI → Kafka)
│   ├── job2_cleaner.py        # Data cleaning logic (Kafka → SQLite)
│   └── job3_analytics.py      # Analytics computation (SQLite → SQLite)
│
├── data/
│   └── app.db                 # SQLite database (created automatically)
│
└── report/
    └── report.pdf             # Project report (to be created)
```

### File Descriptions

#### `docker-compose.yml`
Defines all services (Kafka, Zookeeper, Airflow, PostgreSQL) and their configurations.

#### `requirements.txt`
Python packages required by the pipeline:
- apache-airflow==2.7.0
- kafka-python==2.0.2
- pandas==2.0.3
- requests==2.31.0

#### `src/db_utils.py`
- Database connection management
- Table initialization (events, daily_summary)
- Shared utility functions

#### `src/job1_producer.py`
- Connects to NewsAPI
- Fetches news articles every 2 minutes
- Sends raw JSON to Kafka topic

#### `src/job2_cleaner.py`
- Consumes messages from Kafka
- Cleans data using Pandas operations
- Stores cleaned data in SQLite

#### `src/job3_analytics.py`
- Reads cleaned data from SQLite
- Computes statistical aggregations
- Stores summary in separate table

---

## DAGs Description

### DAG 1: Continuous Ingestion

**Name**: `job1_continuous_ingestion`

**Schedule**: `@hourly` (every hour, runs for 55 minutes)

**Purpose**: Continuously fetch news from NewsAPI and send to Kafka

**Tasks**:
1. `fetch_and_produce_to_kafka`: Main producer task

**Workflow**:
1. Connect to Kafka broker
2. Every 2 minutes:
   - Fetch 20 articles from NewsAPI
   - Send each article as JSON to Kafka topic `raw_events`
3. Run for 55 minutes, then stop

**Key Features**:
- Retry logic for Kafka connection (15 attempts)
- Error handling for API failures
- Logs number of articles sent

---

### DAG 2: Hourly Cleaning

**Name**: `job2_hourly_cleaning`

**Schedule**: `@hourly`

**Purpose**: Clean and store data from Kafka to SQLite

**Tasks**:
1. `clean_and_store_data`: Main cleaning task

**Workflow**:
1. Connect to Kafka consumer
2. Read all available messages
3. Clean data using Pandas:
   - Extract source name from nested object
   - Remove rows with missing title/URL
   - Fill missing values (author, description, content)
   - Convert timestamps to datetime
   - Remove duplicate URLs
   - Categorize articles (Technology/Business/General)
   - Normalize text (strip whitespace, remove extra spaces)
4. Store cleaned records in SQLite `events` table

**Data Cleaning Rules**:
- **Missing Values**: Fill author with "Unknown", description/content with empty string
- **Duplicates**: Remove based on URL (keep first occurrence)
- **Text Normalization**: Strip whitespace, replace multiple spaces with single space
- **Type Conversion**: Convert publishedAt string to datetime
- **Validation**: Drop records with invalid timestamps or missing critical fields

---

### DAG 3: Daily Analytics

**Name**: `job3_daily_analytics`

**Schedule**: `@daily` (runs at midnight)

**Purpose**: Compute daily summary statistics

**Tasks**:
1. `compute_daily_summary`: Main analytics task

**Workflow**:
1. Read yesterday's data from `events` table
2. Compute using Pandas aggregations:
   - Total article count
   - Unique sources count
   - Average title/description lengths
   - Top source and its article count
   - Articles with author/content statistics
3. Store results in `daily_summary` table

**Metrics Computed**:
- `total_articles`: Total number of articles ingested
- `unique_sources`: Number of distinct news sources
- `avg_title_length`: Mean character count of titles
- `avg_description_length`: Mean character count of descriptions
- `top_source`: Most frequent news source
- `top_source_count`: Number of articles from top source
- `articles_with_author`: Count of articles with known author
- `articles_with_content`: Count of articles with content field

---

## Database Schema

### Table 1: `events` (Cleaned Data)

Stores cleaned news articles.

```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT,
    author TEXT,
    title TEXT,
    description TEXT,
    url TEXT UNIQUE,
    published_at TIMESTAMP,
    content TEXT,
    category TEXT,
    ingestion_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Columns**:
- `id`: Auto-incrementing primary key
- `source_name`: News source (e.g., "CNN", "BBC News")
- `author`: Article author (default: "Unknown")
- `title`: Article headline
- `description`: Article summary/description
- `url`: Unique article URL (used for deduplication)
- `published_at`: Original publication timestamp
- `content`: Article content snippet
- `category`: Assigned category (Technology/Business/General)
- `ingestion_time`: Timestamp when record was inserted

**Constraints**:
- `url` is UNIQUE (prevents duplicate articles)
- `id` is PRIMARY KEY

---

### Table 2: `daily_summary` (Analytics)

Stores daily aggregated statistics.

```sql
CREATE TABLE daily_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    summary_date DATE UNIQUE,
    total_articles INTEGER,
    unique_sources INTEGER,
    avg_title_length REAL,
    avg_description_length REAL,
    top_source TEXT,
    top_source_count INTEGER,
    articles_with_author INTEGER,
    articles_with_content INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Columns**:
- `id`: Auto-incrementing primary key
- `summary_date`: Date of analysis (UNIQUE)
- `total_articles`: Total articles processed that day
- `unique_sources`: Count of distinct news sources
- `avg_title_length`: Average title length in characters
- `avg_description_length`: Average description length
- `top_source`: Most frequent news source
- `top_source_count`: Article count from top source
- `articles_with_author`: Count with known author
- `articles_with_content`: Count with non-empty content
- `created_at`: When summary was created

**Constraints**:
- `summary_date` is UNIQUE (one summary per day)
- `id` is PRIMARY KEY

---

## Usage Guide

### Starting the Pipeline

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Stopping the Pipeline

```bash
# Stop all services (keeps data)
docker-compose down

# Stop and remove all data
docker-compose down -v
```

### Manually Triggering DAGs

1. Go to Airflow UI: http://localhost:8080
2. Click on a DAG name
3. Click the "Play" button (▶) on the right
4. Confirm the trigger

### Viewing DAG Logs

**Method 1: In Airflow UI**
1. Click on DAG name
2. Click on the colored square (task instance)
3. Click "Log" button

**Method 2: In Terminal**
```bash
# View scheduler logs
docker-compose logs -f airflow-scheduler

# View webserver logs
docker-compose logs -f airflow-webserver
```

### Querying the Database

```bash
# Access SQLite CLI
docker-compose exec airflow-webserver sqlite3 /opt/airflow/data/app.db

# Example queries:
sqlite> SELECT COUNT(*) FROM events;
sqlite> SELECT * FROM daily_summary ORDER BY summary_date DESC LIMIT 5;
sqlite> SELECT source_name, COUNT(*) as count FROM events GROUP BY source_name ORDER BY count DESC LIMIT 10;
sqlite> .quit
```

### Checking Kafka Messages

```bash
# List Kafka topics
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092

# View messages in topic (latest 10)
docker-compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic raw_events \
  --from-beginning \
  --max-messages 10
```

### Accessing Database File

The SQLite database file is located at:
- **Inside container**: `/opt/airflow/data/app.db`
- **On your machine**: `data/app.db`

You can open it with any SQLite browser like:
- DB Browser for SQLite: https://sqlitebrowser.org
- SQLite Viewer (VS Code extension)

---

## Monitoring & Troubleshooting

### Health Checks

#### Check All Services Status
```bash
docker-compose ps
```

All services should show "Up" status.

#### Check Kafka is Ready
```bash
docker-compose logs kafka | grep "started"
```

Should see: "Kafka Server started"

#### Check Database Exists
```bash
ls -la data/
```

Should see `app.db` file.

#### Check Airflow DAGs
```bash
# List all DAGs
docker-compose exec airflow-scheduler airflow dags list

# Should show:
# job1_continuous_ingestion
# job2_hourly_cleaning
# job3_daily_analytics
```

---

### Common Issues & Solutions

#### Issue 1: DAGs Not Appearing in Airflow UI

**Symptoms**: No DAGs visible in Airflow UI

**Solutions**:
```bash
# Check if DAG files exist
ls -la airflow/dags/

# Check for Python syntax errors
docker-compose exec airflow-scheduler python -m py_compile /opt/airflow/dags/job1_ingestion_dag.py

# Restart scheduler
docker-compose restart airflow-scheduler

# Wait 30 seconds and refresh UI
```

---

#### Issue 2: DAG Failing - Kafka Connection Error

**Symptoms**: DAG shows red/failed status, logs show "Kafka connection failed"

**Solutions**:
```bash
# Wait longer - Kafka takes 30-60 seconds to start
sleep 60

# Check Kafka is running
docker-compose logs kafka

# Restart Kafka
docker-compose restart kafka zookeeper

# Wait and retry DAG
```

---

#### Issue 3: No Data in Database

**Symptoms**: `app.db` exists but tables are empty

**Solutions**:
```bash
# Check if API key is set correctly
docker-compose exec airflow-webserver printenv | grep NEWS_API_KEY

# Should show your actual key, not 'YOUR_API_KEY_HERE'

# If wrong, edit docker-compose.yml and restart:
docker-compose down
docker-compose up -d

# Manually trigger DAG 1, wait 5 minutes, then trigger DAG 2
```

---

#### Issue 4: NewsAPI Rate Limit Error

**Symptoms**: Logs show "API Error: Rate limit exceeded"

**Solutions**:
- NewsAPI free tier: 100 requests/day
- Each DAG 1 run makes ~30 requests/hour
- Solution: Wait 24 hours for rate limit reset
- Or upgrade to NewsAPI paid plan

---

#### Issue 5: Database File Not Created

**Symptoms**: `data/` folder is empty

**Solutions**:
```bash
# Manually initialize database
docker-compose exec airflow-webserver python /opt/airflow/src/db_utils.py

# Check if created
docker-compose exec airflow-webserver ls -la /opt/airflow/data/

# Check permissions
docker-compose exec airflow-webserver ls -la /opt/airflow/
```

---

#### Issue 6: DAG 3 Shows No Data

**Symptoms**: DAG 3 runs but reports "No data for [date]"

**Cause**: DAG 3 analyzes YESTERDAY's data, so you need at least 24 hours of data collection

**Solutions**:
- Wait until next day after DAG 1 and DAG 2 have run
- Or modify `job3_analytics.py` to analyze today's data:
  ```python
  # Change this line:
  yesterday = (datetime.now() - timedelta(days=1)).date()
  # To this:
  yesterday = datetime.now().date()
  ```

---

### Viewing Logs

#### Specific Service Logs
```bash
# Airflow scheduler (shows DAG execution)
docker-compose logs -f airflow-scheduler

# Airflow webserver (shows UI access)
docker-compose logs -f airflow-webserver

# Kafka (shows message streaming)
docker-compose logs -f kafka

# All services
docker-compose logs -f
```

#### DAG-Specific Logs
In Airflow UI:
1. Click on DAG name
2. Click on task instance (colored square)
3. Click "Log" button

---

### Performance Monitoring

#### Check Kafka Message Count
```bash
docker-compose exec kafka kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic raw_events
```

#### Check Database Size
```bash
docker-compose exec airflow-webserver du -h /opt/airflow/data/app.db
```

#### Check Record Counts
```bash
docker-compose exec airflow-webserver sqlite3 /opt/airflow/data/app.db \
  "SELECT 'events' as table_name, COUNT(*) as count FROM events 
   UNION ALL 
   SELECT 'daily_summary', COUNT(*) FROM daily_summary;"
```

---

## API Information

### NewsAPI Details

**Official Website**: https://newsapi.org

**Documentation**: https://newsapi.org/docs

**Endpoint Used**: `GET https://newsapi.org/v2/top-headlines`

**Parameters**:
- `apiKey`: Your authentication key
- `country`: Country code (we use "us" for United States)
- `pageSize`: Number of articles per request (we use 20)

**Rate Limits**:
- Free tier: 100 requests per day
- Developer tier: 1000 requests per day
- Business tier: Unlimited

**Response Format** (JSON):
```json
{
  "status": "ok",
  "totalResults": 38,
  "articles": [
    {
      "source": {
        "id": "cnn",
        "name": "CNN"
      },
      "author": "John Doe",
      "title": "Article headline here",
      "description": "Article description here",
      "url": "https://example.com/article",
      "publishedAt": "2025-12-16T10:30:00Z",
      "content": "Article content snippet here..."
    }
  ]
}
```

### Why NewsAPI?

**Justification for project requirements**:

1. ✅ **Returns NEW data frequently**: News articles are published continuously, providing fresh data every hour
2. ✅ **Stable and documented**: Professional API with comprehensive documentation
3. ✅ **Returns structured data**: Clean JSON format
4. ✅ **Not used in SIS-1**: This is a new API for the course
5. ✅ **Meaningful, real values**: Actual news articles from verified sources

---

## Project Evaluation Checklist

### Requirements Met

- ✅ **Job 1 (API → Kafka)**: Continuous ingestion implemented
- ✅ **Job 2 (Kafka → SQLite)**: Hourly cleaning with Pandas
- ✅ **Job 3 (SQLite analytics)**: Daily summary computation
- ✅ **Kafka**: Used kafka-python library
- ✅ **Data Cleaning**: All operations use Pandas (no vanilla Python loops)
- ✅ **Analytics**: Computed using Pandas aggregations
- ✅ **SQLite**: Two tables (events, daily_summary)
- ✅ **Airflow**: Three DAGs with proper schedules
- ✅ **Docker**: Fully containerized with docker-compose
- ✅ **Documentation**: Complete README and report template

### Grading Breakdown (10 points)

1. **Job 1 (3.0 points)**: API → Kafka continuous ingestion
2. **Job 2 (3.0 points)**: Kafka → Cleaning → SQLite
3. **Job 3 (3.0 points)**: Daily analytics computation
4. **Report & Repository (1.0 point)**: Documentation quality

---

## Team Collaboration

### Git Workflow

```bash
# Clone repository
git clone <repo-url>
cd news-pipeline

# Create feature branch
git checkout -b feature/your-feature

# Make changes and commit
git add .
git commit -m "Description of changes"

# Push to GitHub
git push origin feature/your-feature

# Create Pull Request on GitHub
```

### Division of Work (Example)

- **Student 1**: DAG 1 (Ingestion), Kafka setup, Docker configuration
- **Student 2**: DAG 2 (Cleaning), Database schema, Data validation
- **Student 3**: DAG 3 (Analytics), Documentation, Report writing

---

## Additional Resources

### Learning Materials

- **Apache Airflow**: https://airflow.apache.org/docs/
- **Apache Kafka**: https://kafka.apache.org/documentation/
- **Pandas**: https://pandas.pydata.org/docs/
- **Docker Compose**: https://docs.docker.com/compose/

### Useful Tools

- **DB Browser for SQLite**: https://sqlitebrowser.org
- **Postman** (for testing NewsAPI): https://www.postman.com
- **VS Code** with Python extension

---

## License

This project is for educational purposes as part of the SIS-2 course.

---

## Contact

For questions or issues:
- Create an issue on GitHub
- Contact team members via email
- Reach out to course instructor

---

**Last Updated**: December 2025

**Version**: 1.0.0