# Finance Analysis Pipeline

A production-ready data pipeline for extracting financial data from Yahoo Finance, loading to Snowflake, transforming with dbt, and visualizing with Streamlit.

## Architecture

See `assets/architecture.md` for detailed architecture documentation.

**Data Flow:**
```
Yahoo Finance (yfinance) → Airflow DAG → Snowflake (RAW) → dbt (ANALYTICS) → Streamlit
```

**Key Components:**
- **Extraction:** Yahoo Finance API (keyless) - stock prices, company info, benchmarks
- **Orchestration:** Apache Airflow (Astronomer)
- **Storage:** Snowflake (RAW, ANALYTICS, METADATA schemas)
- **Transformation:** dbt (future phase)
- **Visualization:** Streamlit (future phase)

## Project Structure

```
project-root/
├── dags/                          # Airflow DAGs
│   ├── finance_pipeline_dag.py   # Main ETL pipeline
│   └── exampledag.py
├── src/                           # Pipeline source code
│   ├── extract/                   # Yahoo Finance extractors
│   │   ├── yahoo_prices.py
│   │   ├── yahoo_company_info.py
│   │   └── yahoo_benchmark_series.py
│   ├── load/                      # Snowflake loaders
│   │   └── snowflake_loader.py
│   └── common/                    # Utilities
│       ├── profiles_reader.py
│       ├── logging.py
│       └── state_store.py
├── config/                        # Configuration files
│   └── tickers.yaml              # Stock ticker universe
├── sql/                          # SQL scripts
│   └── setup_snowflake.sql       # Snowflake DDL
├── include/                      # Airflow includes
│   ├── rsa_key.pem              # Snowflake private key
│   └── project_name/
│       └── profiles.yml          # dbt/Snowflake credentials
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Astro Runtime image
└── airflow_settings.yaml         # Local Airflow config
```

## Setup Instructions

### Prerequisites
- [Astronomer CLI](https://www.astronomer.io/docs/astro/cli/install-cli) installed
- [uv](https://github.com/astral-sh/uv) package manager installed
- Snowflake account with credentials configured
- Docker Desktop running

### 1. Snowflake Setup

**Run the setup SQL:**
```sql
-- Execute sql/setup_snowflake.sql in Snowflake
-- This creates RAW, ANALYTICS, and METADATA schemas with required tables
```

**Required credentials:**
- Ensure `include/rsa_key.pem` contains your Snowflake private key
- Verify `include/project_name/profiles.yml` has correct Snowflake settings

### 2. Python Environment (Local Development)

**Create virtual environment with uv:**
```powershell
# Create venv
uv venv

# Activate venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
uv pip install -r requirements.txt
```

### 3. Test Extraction (Local - Optional)

**Test Yahoo Finance extraction:**
```powershell
# Activate venv first
.\.venv\Scripts\Activate.ps1

# Test extractors
python src/extract/yahoo_prices.py
python src/extract/yahoo_company_info.py
python src/extract/yahoo_benchmark_series.py

# Test Snowflake connection
python src/load/snowflake_loader.py
```

### 4. Start Airflow with Astronomer

**Start Airflow locally:**
```powershell
astro dev start
```

This starts 5 Docker containers:
- **Postgres:** Airflow metadata database
- **Scheduler:** Task monitoring and triggering
- **DAG Processor:** DAG parsing
- **API Server:** Airflow UI and API
- **Triggerer:** Deferred task handling

**Access Airflow UI:** http://localhost:8080/  
**Default credentials:** admin / admin

### 5. Run the Finance Pipeline

1. **Navigate to Airflow UI:** http://localhost:8080/
2. **Find DAG:** `finance_pipeline_dag`
3. **Enable the DAG** (toggle switch)
4. **Trigger manually** or wait for schedule (2 AM weekdays)

**DAG Tasks:**
```
start
  ├─> extract_yahoo_prices ─┐
  ├─> extract_yahoo_company_info ─┤
  └─> extract_yahoo_benchmark_series ─┘
           ↓
      verify_data_quality
           ↓
         end
```

### 6. Verify Data in Snowflake

**Check loaded data:**
```sql
-- Row counts
SELECT 'prices' as dataset, COUNT(*) FROM RAW.STOCK_PRICES_DAILY
UNION ALL
SELECT 'company', COUNT(*) FROM RAW.COMPANY_INFO
UNION ALL
SELECT 'benchmarks', COUNT(*) FROM RAW.BENCHMARK_SERIES_DAILY;

-- Recent ingestion runs
SELECT * FROM METADATA.INGEST_RUNS ORDER BY run_timestamp DESC LIMIT 10;

-- Sample price data
SELECT * FROM RAW.STOCK_PRICES_DAILY 
WHERE symbol = 'AAPL' 
ORDER BY date DESC 
LIMIT 10;
```

## Configuration

### Ticker Universe

Edit `config/tickers.yaml` to modify the stock universe:
```yaml
stocks:
  - AAPL
  - MSFT
  # ... add more tickers

benchmarks:
  - ^GSPC  # S&P 500
  - ^VIX   # Volatility Index
  # ... add more benchmarks
```

### Snowflake Credentials

Located in `include/project_name/profiles.yml`:
- **Do NOT commit secrets to git**
- Private key: `include/rsa_key.pem`
- Profile name: `finance_analysis_pipeline`

## Troubleshooting

**DAG import errors:**
```powershell
# Check DAG syntax
astro dev parse
```

**Snowflake connection issues:**
- Verify `include/rsa_key.pem` permissions
- Test connection: `python src/load/snowflake_loader.py`
- Check Snowflake role/warehouse permissions

**Yahoo Finance rate limits:**
- Reduce ticker count in `config/tickers.yaml`
- Increase retry delays in DAG `default_args`

## Next Steps (Future Phases)

1. **dbt Transformations:** Build staging and mart models in `dbt_finance/`
2. **Streamlit Dashboard:** Create interactive visualizations
3. **CI/CD:** Add testing and deployment automation
4. **Incremental Loads:** Implement watermark-based incremental extraction

## Deploy Your Project Locally (Astro CLI)

Stop Airflow: `astro dev stop`  
Restart Airflow: `astro dev restart`  
View logs: `astro dev logs`

## Resources

- **Architecture:** `assets/architecture.md`
- **Astronomer Docs:** https://www.astronomer.io/docs/astro/
- **dbt Docs:** https://docs.getdbt.com/
- **Yahoo Finance (yfinance):** https://github.com/ranaroussi/yfinance

## License

This project is for educational purposes (MLDS 430).
