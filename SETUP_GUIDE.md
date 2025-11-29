# Finance Analysis Pipeline - Quick Setup Guide

## Phase 1: Extraction + Snowflake Load (Current)

### Step 1: Snowflake Setup
**Run this in Snowflake Worksheet:**
```sql
-- Execute the entire file: sql/setup_snowflake.sql
-- This creates RAW, ANALYTICS, and METADATA schemas with tables
```

### Step 2: Install Dependencies (Local Testing)
**PowerShell commands:**
```powershell
# Navigate to project
cd C:\Users\jacob\Desktop\NU\ML_430\proj2

# Create virtual environment with uv
uv venv

# Activate venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
uv pip install -r requirements.txt
```

### Step 3: Test Components Locally (Optional)
**Run these to verify everything works:**
```powershell
# Make sure venv is activated
.\.venv\Scripts\Activate.ps1

# Test Yahoo Finance extractors
python src/extract/yahoo_prices.py
python src/extract/yahoo_company_info.py
python src/extract/yahoo_benchmark_series.py

# Test Snowflake connection
python src/load/snowflake_loader.py
```

**Expected output:**
- Extractors: Should print DataFrames with stock data
- Loader: Should print Snowflake connection details (version, user, role)

### Step 4: Start Airflow
**PowerShell:**
```powershell
# Start Astronomer Airflow
astro dev start
```

**Wait for all containers to start, then:**
- Open browser: http://localhost:8080/
- Login: `admin` / `admin`

### Step 5: Run the Pipeline
**In Airflow UI:**
1. Find DAG: `finance_pipeline_dag`
2. Toggle to enable the DAG
3. Click "Trigger DAG" (play button)
4. Watch tasks execute in Graph view

**Tasks will run in this order:**
```
start → [extract_yahoo_prices, extract_yahoo_company_info, extract_yahoo_benchmark_series] → verify_data_quality → end
```

### Step 6: Verify in Snowflake
**Run these queries:**
```sql
USE DATABASE MLDS430;
USE SCHEMA RAW;

-- Check row counts
SELECT COUNT(*) FROM RAW.STOCK_PRICES_DAILY;
SELECT COUNT(*) FROM RAW.COMPANY_INFO;
SELECT COUNT(*) FROM RAW.BENCHMARK_SERIES_DAILY;

-- View recent runs
SELECT * FROM METADATA.INGEST_RUNS ORDER BY run_timestamp DESC LIMIT 5;

-- Sample data
SELECT * FROM RAW.STOCK_PRICES_DAILY WHERE symbol = 'AAPL' ORDER BY date DESC LIMIT 10;
```

---

## Troubleshooting

### Issue: Import errors in Airflow
**Solution:**
```powershell
# Check DAG parsing
astro dev parse

# View scheduler logs
astro dev logs -f scheduler
```

### Issue: Snowflake connection fails
**Check:**
- `include/rsa_key.pem` exists and is readable
- `include/project_name/profiles.yml` has correct credentials
- Test connection locally: `python src/load/snowflake_loader.py`

### Issue: Yahoo Finance rate limits
**Solution:**
- Edit `config/tickers.yaml` to reduce ticker count
- Increase `time.sleep()` in extractors

---

## Next Phase Preview

After extraction + load is working, we'll add:
- **dbt transformations** (staging → marts)
- **Streamlit dashboard** (interactive visualizations)
- **Incremental loads** (watermark-based extraction)

---

## Quick Commands Reference

```powershell
# Airflow
astro dev start              # Start Airflow
astro dev stop               # Stop Airflow
astro dev restart            # Restart Airflow
astro dev logs               # View logs
astro dev parse              # Check DAG syntax

# Virtual Environment
uv venv                      # Create venv
.\.venv\Scripts\Activate.ps1 # Activate venv
uv pip install -r requirements.txt  # Install deps

# Testing
python src/extract/yahoo_prices.py          # Test price extraction
python src/load/snowflake_loader.py         # Test Snowflake connection
```
