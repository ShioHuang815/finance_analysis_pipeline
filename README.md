# Finance Analysis Pipeline

A production-ready end-to-end data pipeline for financial market analysis. Extracts daily stock market data from Yahoo Finance, loads to Snowflake data warehouse, transforms with dbt, orchestrates with Apache Airflow, and visualizes through an interactive Streamlit dashboard.

## 🏗️ Architecture

**Data Flow:**
```
Yahoo Finance API → Airflow Orchestration → Snowflake (COBRA) → dbt Transformations → Streamlit Dashboard
```

**Technology Stack:**
- **Data Source:** Yahoo Finance (yfinance - keyless API)
- **Orchestration:** Apache Airflow (Astronomer CLI)
- **Data Warehouse:** Snowflake (MLDS430 database, COBRA schema)
- **Transformation:** dbt-core + dbt-snowflake
- **Visualization:** Streamlit + Plotly
- **Package Management:** UV (ultra-fast Python package installer)

## 📁 Project Structure

```
finance_analysis_pipeline/
├── dags/
│   └── finance_pipeline_dag.py        # Main Airflow DAG
├── src/
│   ├── extract/                       # Data extractors
│   │   ├── yahoo_prices.py           # OHLCV stock prices
│   │   ├── yahoo_company_info.py     # Company fundamentals
│   │   └── yahoo_benchmark_series.py # Market benchmarks (S&P 500, VIX, etc.)
│   ├── load/
│   │   └── snowflake_loader.py       # Snowflake bulk loader with metadata tracking
│   └── common/                        # Shared utilities
│       ├── profiles_reader.py        # Snowflake credentials reader
│       ├── logging.py                # Centralized logging
│       └── state_store.py            # Run ID generation
├── dbt_finance/                       # dbt project
│   ├── models/
│   │   ├── staging/                  # Cleaned & deduplicated models
│   │   │   ├── stg_stock_prices.sql
│   │   │   ├── stg_company_info.sql
│   │   │   └── stg_benchmark_series.sql
│   │   └── marts/                    # Analytics-ready datasets
│   │       ├── dim_stocks.sql        # Stock dimension table
│   │       └── fact_daily_metrics.sql # Daily metrics fact table
│   ├── dbt_project.yml
│   └── packages.yml
├── streamlit_app/
│   └── app.py                         # Interactive dashboard (3 pages)
├── scripts/
│   └── run_extraction.py              # Standalone extraction script
├── config/
│   └── tickers.yaml                   # Stock universe (20 stocks + 5 benchmarks)
├── sql/
│   └── setup_snowflake.sql            # Snowflake DDL for tables
├── include/
│   ├── rsa_key.pem                    # Snowflake private key (RSA 2048)
│   └── finance_analysis_pipeline/
│       └── profiles.yml               # dbt profiles (dev + local targets)
├── requirements.txt                    # Python dependencies
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Docker Desktop (for Airflow)
- Astronomer CLI (`brew install astro` or [installation guide](https://docs.astronomer.io/astro/cli/install-cli))
- Snowflake account with TRAINING_ROLE permissions
- UV package manager (`pip install uv`)

### 1. Setup Virtual Environment
```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

### 2. Configure Snowflake Credentials

Ensure `include/rsa_key.pem` contains your Snowflake private key (no passphrase).

### 3. Initialize Snowflake Tables

Run the DDL script in Snowflake:
```sql
-- Execute contents of sql/setup_snowflake.sql
-- Creates: STOCK_PRICES_DAILY, COMPANY_INFO, BENCHMARK_SERIES_DAILY,
--          INGEST_RUNS, WATERMARKS
```

### 4. Test Extraction (Optional)

Run standalone extraction to verify connectivity:
```bash
python scripts/run_extraction.py
```

This will extract 30 days of data for all configured stocks and load to Snowflake.

### 5. Start Airflow

```bash
astro dev start
```

Access Airflow UI at `http://localhost:8080` (credentials: `admin/admin`)

### 6. Run the DAG

1. Navigate to **DAGs** → **finance_pipeline_dag**
2. Toggle the DAG **ON**
3. Click **Trigger DAG** to run manually

**DAG Tasks:**
- `extract_yahoo_prices` - Extract OHLCV data
- `extract_yahoo_company_info` - Extract fundamentals
- `extract_yahoo_benchmark_series` - Extract S&P 500, VIX, TNX, sector ETFs
- `verify_data_quality` - Validate row counts and data freshness
- `transform_dbt` - Run dbt models (staging + marts)

### 7. Launch Streamlit Dashboard

```bash
streamlit run streamlit_app/app.py
```

Access dashboard at `http://localhost:8501`

## 📊 Data Models

### Raw Layer (COBRA Schema)

**STOCK_PRICES_DAILY**
- Daily OHLCV data for 20 stocks
- Fields: `symbol`, `date`, `open`, `high`, `low`, `close`, `adj_close`, `volume`

**COMPANY_INFO**
- Company fundamentals and profile
- Fields: `symbol`, `company_name`, `sector`, `industry`, `market_cap`, `pe_ratio`, etc.

**BENCHMARK_SERIES_DAILY**
- Market benchmarks and macro indicators
- Tickers: `^GSPC` (S&P 500), `^VIX` (VIX), `^TNX` (10Y Treasury), `XLK` (Tech), `XLF` (Finance)

### Staging Layer (COBRA_staging Schema)

**stg_stock_prices** - Deduplicated prices with calculated `daily_return` and `volatility`
**stg_company_info** - Latest company snapshot per symbol
**stg_benchmark_series** - Cleaned benchmarks with `pct_change`

### Analytics Layer (COBRA_analytics Schema)

**dim_stocks** - Stock dimension with company attributes
**fact_daily_metrics** - Daily metrics joined with benchmarks, includes:
- Price and volume metrics
- Daily returns
- Alpha vs S&P 500
- Market volatility (VIX)
- Interest rates (10Y Treasury)
- Market cap categories (Mega/Large/Mid/Small Cap)

## 🎯 Features

### Airflow DAG
- **Schedule:** Weekdays at 2 AM (`0 2 * * 1-5`)
- **Parallel extraction:** Prices, company info, and benchmarks run concurrently
- **Data validation:** Checks row counts and data freshness
- **Automatic dbt execution:** Transforms data after successful extraction
- **Metadata tracking:** All ingestion runs logged to `INGEST_RUNS` table

### dbt Transformations
- **Deduplication:** ROW_NUMBER() to handle duplicate records
- **Calculated metrics:** Daily returns, volatility, alpha
- **Market categorization:** Mega Cap (>$200B), Large ($10B-$200B), Mid ($2B-$10B), Small (<$2B)
- **Data quality tests:** 16 tests covering nulls, uniqueness, and referential integrity

### Streamlit Dashboard

**🏠 Home Page**
- Summary metrics (total stocks, latest data date, total records)
- Pipeline overview
- Feature descriptions

**🔍 Stock Screener**
- Filter by sector, market cap category, or individual stock
- 30-day price trend charts
- Performance summary table with average returns and alpha

**📈 Benchmark Analysis**
- Stock vs S&P 500 comparison
- Daily returns visualization
- Alpha metrics
- VIX volatility overlay

## 🔧 Configuration

### Stock Universe (`config/tickers.yaml`)

**Stocks (20):**
AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA, BRK-B, JPM, V, WMT, PG, JNJ, UNH, HD, MA, DIS, NFLX, BAC, ADBE

**Benchmarks (5):**
- `^GSPC` - S&P 500 Index
- `^VIX` - CBOE Volatility Index
- `^TNX` - 10-Year Treasury Yield
- `XLK` - Technology Select Sector SPDR Fund
- `XLF` - Financial Select Sector SPDR Fund

To modify the stock universe, edit `config/tickers.yaml` and redeploy the DAG.

## 🧪 Testing

### Test Snowflake Connection
```python
python -c "
import sys; sys.path.insert(0, 'src')
from common.profiles_reader import get_snowflake_connection_params
import snowflake.connector
conn = snowflake.connector.connect(**get_snowflake_connection_params())
print('✓ Snowflake Connection OK')
conn.close()
"
```

### Test dbt Models
```bash
cd dbt_finance
dbt run --profiles-dir ../include/finance_analysis_pipeline --target local
dbt test --profiles-dir ../include/finance_analysis_pipeline --target local
```

### Test Extraction
```bash
python scripts/run_extraction.py
```

## 📝 Development

### Adding New Stocks
1. Edit `config/tickers.yaml` → add tickers to `stocks` list
2. Redeploy: `astro dev restart`
3. Trigger DAG to extract new data

### Adding dbt Models
1. Create `.sql` file in `dbt_finance/models/staging/` or `dbt_finance/models/marts/`
2. Add schema definition in corresponding `schema.yml`
3. Run `dbt run` to build model
4. Add tests in schema file

### Modifying Streamlit Dashboard
1. Edit `streamlit_app/app.py`
2. Restart: `streamlit run streamlit_app/app.py`
3. Changes auto-reload on save

## 🐛 Troubleshooting

### Airflow DAG Import Errors
```bash
# Check DAG syntax
astro dev bash
python /usr/local/airflow/dags/finance_pipeline_dag.py
```

### Snowflake Connection Failures
- Verify `include/rsa_key.pem` has correct private key
- Check `profiles.yml` credentials (account, user, role, warehouse)
- Ensure TRAINING_ROLE has access to MLDS430.COBRA schema

### dbt Compilation Errors
- Run `dbt debug` to check connection
- Verify `profiles.yml` schema references
- Check source table names match Snowflake

### Streamlit Query Errors
- Verify COBRA_analytics schema exists
- Check dbt models have run successfully
- Ensure sufficient data in fact/dimension tables

## 📈 Maintenance

### Data Refresh
- **Automatic:** DAG runs weekdays at 2 AM
- **Manual:** Trigger `finance_pipeline_dag` in Airflow UI
- **Incremental:** Uses watermarks in `WATERMARKS` table to track last load

### Monitoring
- **Airflow UI:** `http://localhost:8080` - DAG run history, task logs
- **Snowflake:** Query `COBRA.INGEST_RUNS` for ingestion history
- **dbt:** Check `dbt_finance/target/run_results.json` for model execution stats

### Cleanup
```bash
# Stop Airflow
astro dev stop

# Remove containers and volumes
astro dev kill

# Clear dbt artifacts
cd dbt_finance
rm -rf target/ dbt_packages/
```

## 🔐 Security

- **Private keys:** Never commit `rsa_key.pem` to version control (`.gitignore` configured)
- **Credentials:** Use environment variables or secrets management for production
- **Snowflake:** Key-pair authentication (no passwords in code)
- **Network:** Airflow runs in Docker network, Snowflake connections encrypted

## 📚 Documentation

- **Architecture Details:** `assets/architecture.md`
- **Snowflake DDL:** `sql/setup_snowflake.sql`
- **dbt Docs:** Run `dbt docs generate && dbt docs serve` in `dbt_finance/`

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Test locally with `astro dev start`
4. Submit pull request

## 📄 License

This project is for educational purposes as part of ML/DS 430 coursework.

## 🙏 Acknowledgments

- **Yahoo Finance (yfinance):** Free financial data API
- **Astronomer:** Apache Airflow development platform
- **Snowflake:** Data warehousing
- **dbt Labs:** Data transformation framework
- **Streamlit:** Interactive web applications for data science

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
