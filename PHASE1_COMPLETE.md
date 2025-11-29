# Finance Analysis Pipeline - Phase 1 Complete ✓

## What Has Been Built

### ✅ Project Structure
```
✓ src/extract/         - Yahoo Finance data extractors (prices, company info, benchmarks)
✓ src/load/            - Snowflake loader with metadata tracking
✓ src/common/          - Utilities (profiles reader, logging, state management)
✓ config/              - Ticker configuration (20 stocks + 5 benchmarks)
✓ sql/                 - Snowflake DDL scripts (RAW, ANALYTICS, METADATA schemas)
✓ dags/                - Airflow DAG for orchestration
✓ include/             - Credentials (profiles.yml configured, rsa_key.pem present)
```

### ✅ Components Implemented

**1. Yahoo Finance Extractors** (`src/extract/`)
- `yahoo_prices.py` - OHLCV data for 20 stocks
- `yahoo_company_info.py` - Company fundamentals (sector, market cap, ratios)
- `yahoo_benchmark_series.py` - Benchmarks (^GSPC, ^VIX, ^TNX, XLK, XLF)
- Features: Batch downloads, error handling, retries, progress logging

**2. Snowflake Loader** (`src/load/snowflake_loader.py`)
- Reads credentials from `profiles.yml` (single source of truth)
- Bulk loading with `write_pandas`
- Metadata tracking in `METADATA.INGEST_RUNS`
- Watermark management for incremental loads
- Private key authentication (no passphrase)

**3. Common Utilities** (`src/common/`)
- `profiles_reader.py` - Parse dbt profiles.yml, extract Snowflake credentials
- `logging.py` - Consistent logging across all modules
- `state_store.py` - Run ID generation and metadata creation

**4. Airflow DAG** (`dags/finance_pipeline_dag.py`)
- Task graph: `start → [3 extractors in parallel] → verify → end`
- Schedule: 2 AM on weekdays
- Features: XCom passing, data quality checks, error handling
- Verification: Row counts, freshness checks, duplicate detection

**5. Snowflake Schema** (`sql/setup_snowflake.sql`)
- **RAW schema:** Landing tables for all 3 datasets
- **METADATA schema:** Run logs and watermarks
- **ANALYTICS schema:** Placeholder for dbt (Phase 2)

**6. Configuration** (`config/tickers.yaml`)
- 20 stocks: AAPL, MSFT, GOOGL, AMZN, TSLA, META, NVDA, JPM, BAC, WFC, JNJ, PFE, UNH, XOM, CVX, WMT, HD, DIS, NFLX, PYPL
- 5 benchmarks: ^GSPC, ^VIX, ^TNX, XLK, XLF

**7. Documentation**
- `README.md` - Complete setup and usage guide
- `SETUP_GUIDE.md` - Step-by-step quick start
- `test_local.py` - Local testing script
- `.gitignore` - Secrets protection

---

## What You Need to Do Now

### 🔴 STEP 1: Run Snowflake Setup SQL
**Execute this in Snowflake Worksheet:**
```powershell
# File to run: sql/setup_snowflake.sql
# This creates RAW, ANALYTICS, and METADATA schemas with all required tables
```

**Expected result:** Schemas and tables created successfully.

---

### 🔴 STEP 2: Create Virtual Environment with uv
**Run these commands in PowerShell:**
```powershell
# Navigate to project
cd C:\Users\jacob\Desktop\NU\ML_430\proj2

# Create venv
uv venv

# Activate venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
uv pip install -r requirements.txt
```

**Expected result:** Virtual environment created with all packages installed.

---

### 🔴 STEP 3: Test Components Locally (Optional but Recommended)
**Run test script:**
```powershell
# Make sure venv is activated
.\.venv\Scripts\Activate.ps1

# Run comprehensive test
python test_local.py
```

**Expected result:** All tests pass (profiles, Snowflake connection, extractors, full pipeline).

---

### 🔴 STEP 4: Start Airflow
**Run in PowerShell:**
```powershell
astro dev start
```

**Expected result:**
- 5 Docker containers start successfully
- Browser opens to http://localhost:8080/
- Login with `admin` / `admin`

---

### 🔴 STEP 5: Run the Finance Pipeline DAG
**In Airflow UI:**
1. Navigate to DAGs page
2. Find `finance_pipeline_dag`
3. Toggle switch to enable
4. Click "Trigger DAG" (play button)
5. Watch execution in Graph or Grid view

**Expected result:** All tasks turn green (success).

---

### 🔴 STEP 6: Verify Data in Snowflake
**Run these queries:**
```sql
USE DATABASE MLDS430;

-- Check row counts
SELECT COUNT(*) as price_records FROM RAW.STOCK_PRICES_DAILY;
SELECT COUNT(*) as company_records FROM RAW.COMPANY_INFO;
SELECT COUNT(*) as benchmark_records FROM RAW.BENCHMARK_SERIES_DAILY;

-- View recent runs
SELECT * FROM METADATA.INGEST_RUNS ORDER BY run_timestamp DESC LIMIT 5;

-- Sample data
SELECT * FROM RAW.STOCK_PRICES_DAILY 
WHERE symbol = 'AAPL' 
ORDER BY date DESC 
LIMIT 10;
```

**Expected result:**
- Hundreds/thousands of price records
- 20 company records
- Dozens of benchmark records
- Recent successful runs in metadata

---

## Technical Details

### Dependencies (requirements.txt)
```
yfinance>=0.2.32                      # Yahoo Finance API
pandas>=2.0.0                         # Data manipulation
snowflake-connector-python[pandas]    # Snowflake connectivity
cryptography>=41.0.0                  # Private key handling
PyYAML>=6.0.1                        # Config parsing
```

### Credentials Setup (Already Configured)
- **Location:** `include/project_name/profiles.yml`
- **Private key:** `include/rsa_key.pem` (no passphrase)
- **Profile name:** `finance_analysis_pipeline`
- **Database:** MLDS430
- **Schema:** COBRA (default), plus RAW, ANALYTICS, METADATA

### DAG Schedule
- **Frequency:** `0 2 * * 1-5` (2 AM, Monday-Friday)
- **Catchup:** Disabled
- **Retries:** 2 with 5-minute delay

---

## Troubleshooting

### ❌ DAG Import Errors
```powershell
astro dev parse  # Check syntax
astro dev logs -f scheduler  # View logs
```

### ❌ Snowflake Connection Fails
- Verify `include/rsa_key.pem` exists and is readable
- Check `include/project_name/profiles.yml` credentials
- Test: `python src/load/snowflake_loader.py`

### ❌ Yahoo Finance Rate Limits
- Reduce tickers in `config/tickers.yaml`
- Increase `time.sleep()` in extractors

### ❌ "Module not found" Errors
- Make sure venv is activated before running Python scripts
- Re-install: `uv pip install -r requirements.txt`

---

## What's Next (Phase 2)

After this phase is working, we'll add:

### 1. dbt Transformations
- Staging models (deduplication, type casting)
- Mart models (joins, aggregations, metrics)
- Tests (uniqueness, nulls, relationships)

### 2. Streamlit Dashboard
- Stock screener with filters
- Benchmark overlays
- Interactive charts

### 3. Enhanced Pipeline
- Incremental loads (watermark-based)
- Airflow sensors for real-time updates
- CI/CD with testing

---

## File Checklist

### Created Files ✓
- [x] `src/extract/yahoo_prices.py`
- [x] `src/extract/yahoo_company_info.py`
- [x] `src/extract/yahoo_benchmark_series.py`
- [x] `src/load/snowflake_loader.py`
- [x] `src/common/profiles_reader.py`
- [x] `src/common/logging.py`
- [x] `src/common/state_store.py`
- [x] `dags/finance_pipeline_dag.py`
- [x] `config/tickers.yaml`
- [x] `sql/setup_snowflake.sql`
- [x] `test_local.py`
- [x] `SETUP_GUIDE.md`
- [x] `README.md` (updated)
- [x] `requirements.txt` (updated)
- [x] `.gitignore` (updated)

### Modified Files ✓
- [x] `include/project_name/profiles.yml` (renamed profile key to `finance_analysis_pipeline`)

### Existing Files (Preserved) ✓
- [x] `include/rsa_key.pem` (Snowflake private key)
- [x] `Dockerfile`
- [x] `packages.txt`
- [x] `airflow_settings.yaml`

---

## Success Criteria ✅

Phase 1 is **complete** when:
- ✅ Snowflake schemas and tables exist
- ✅ Python dependencies installed via uv
- ✅ Airflow DAG runs successfully
- ✅ Data appears in Snowflake RAW tables
- ✅ Metadata tracking works (INGEST_RUNS, WATERMARKS)
- ✅ Data quality checks pass

---

## Questions or Issues?

**Common questions:**
- **"Can I change the ticker list?"** Yes, edit `config/tickers.yaml`
- **"How do I stop Airflow?"** Run `astro dev stop`
- **"Can I run extractors without Airflow?"** Yes, run Python files directly
- **"Where are the logs?"** Airflow UI → DAG → Task → Logs

**Ready to proceed?** Start with Step 1 (Snowflake setup) and let me know if you hit any issues!
