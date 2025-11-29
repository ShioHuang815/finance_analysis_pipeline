# Architecture: Keyless Yahoo Finance → Snowflake → dbt → Airflow (Astro) → Streamlit

This architecture assumes you start from an **Astronomer Airflow scaffold** created by `astro init`.  
It uses **only keyless Yahoo Finance via `yfinance`** (no API keys), loads to **Snowflake**, transforms with **dbt**, optionally orchestrates with **Airflow** (extra credit), and serves results in **Streamlit**.

## 0) Scope (kept intentionally small)

### Datasets (exactly 3, all keyless)
1. **Stock daily prices (OHLCV)** — `yfinance.download(...)`
2. **Company profile / fundamentals** — `yfinance.Ticker(symbol).info`
3. **Benchmark / macro series (Yahoo tickers)** — ex: `^GSPC`, `^VIX`, `^TNX`, or a couple sector ETFs (e.g., `XLK`, `XLF`)

### Stock universe
- Start with ~20 tickers (config file controlled)

### Final output
- **Streamlit app** with at least 2 meaningful components (filters + chart/table)

---

## 1) Astro project folder structure (repo root == Airflow project)

After `astro init`, organize your repo like this (add the bolded folders as part of your implementation):

```
project-root/
├── dags/
│   └── finance_pipeline_dag.py
├── include/
│   ├── rsa_key.pem
│   └── <project_name>/
│       └── profiles.yml
├── plugins/                         # optional (usually empty)
├── tests/                           # optional
├── .astro/
├── Dockerfile
├── requirements.txt
├── packages.txt
├── airflow_settings.yaml
│
├── src/                              # your pipeline code (add)
│   ├── extract/
│   │   ├── yahoo_prices.py
│   │   ├── yahoo_company_info.py
│   │   └── yahoo_benchmark_series.py
│   ├── load/
│   │   └── snowflake_loader.py
│   └── common/
│       ├── logging.py
│       ├── state_store.py
│       └── profiles_reader.py
│
├── dbt_finance/                      # dbt project (add)
│   ├── dbt_project.yml
│   ├── models/
│   │   ├── staging/
│   │   └── marts/
│   └── tests/
│
└── streamlit_app/                    # Streamlit app (add)
    ├── app.py
    └── pages/
```

---

## 2) Credentials & where they live (single source of truth)

You said: **you will use a single `profiles.yml` template and only change the project name**.

### A) dbt profile (use your uploaded template)
- Location in repo: `include/<project_name>/profiles.yml`
- Location inside the Astro container: `/usr/local/airflow/include/<project_name>/profiles.yml`

**Only required edit**
- Change the very first YAML key in the file (the profile name) to `<project_name>:`.

Example (based on your template):
```yaml
<project_name>:
  outputs:
    dev:
      type: snowflake
      account: ...
      database: ...
      schema: ...
      role: ...
      warehouse: ...
      user: ...
      private_key_path: /usr/local/airflow/include/rsa_key.pem
  target: dev
```

### B) Snowflake private key
- Location in repo: `include/rsa_key.pem`
- Location inside the Astro container: `/usr/local/airflow/include/rsa_key.pem`

> Your template already uses `private_key_path: /usr/local/airflow/include/rsa_key.pem`, so keep the filename exactly `rsa_key.pem` and put it under `include/`.

### C) How other components should read credentials
To keep credentials “where they’re needed” and avoid duplication:
- **dbt** reads Snowflake settings from `include/<project_name>/profiles.yml` via `--profiles-dir`.
- **Python extract/load code** parses the same `profiles.yml` (recommended).
- **Airflow verify** can reuse the same parsing + key file (recommended).
- **Streamlit** can either parse the same profile (local dev) or use Streamlit secrets (deployment).

---

## 3) High-level architecture

```text
┌──────────────────────────────────────────────┐
│ Yahoo Finance (no API keys) via `yfinance`   │
│  - prices (OHLCV)                            │
│  - company info                              │
│  - benchmark/macro tickers                   │
└───────────────────────────┬──────────────────┘
                            ▼
┌──────────────────────────────────────────────┐
│ Airflow (Astro) DAG                           │
│ 1) extract_* (PythonOperators)                │
│ 2) run_dbt (BashOperator)                     │
│ 3) verify (PythonOperator recommended)        │
└───────────────────────────┬──────────────────┘
                            ▼
┌──────────────────────────────────────────────┐
│ Snowflake                                     │
│  - RAW schema: landing tables                 │
│  - ANALYTICS schema: dbt models               │
│  - METADATA schema: run logs + watermarks     │
└───────────────────────────┬──────────────────┘
                            ▼
┌──────────────────────────────────────────────┐
│ Streamlit                                     │
│  - queries ANALYTICS marts                    │
│  - screener + benchmark overlay               │
└──────────────────────────────────────────────┘
```

---

## 4) Snowflake design

### Database & schemas
- Database: `FINANCE_DW`
- Schemas:
  - `RAW` (append-only landing)
  - `ANALYTICS` (dbt output)
  - `METADATA` (ingestion logs, watermarks)

### RAW tables (minimum)
- `RAW.STOCK_PRICES_DAILY`
  - `symbol, date, open, high, low, close, adj_close, volume, ingested_at, source_run_id`
- `RAW.COMPANY_INFO`
  - `symbol, sector, industry, market_cap, pe_ratio, dividend_yield, ingested_at, source_run_id`
- `RAW.BENCHMARK_SERIES_DAILY`
  - `series_ticker, date, value, ingested_at, source_run_id`

### METADATA tables (recommended)
- `METADATA.INGEST_RUNS` (one row per extractor run)
- `METADATA.WATERMARKS` (e.g., last loaded date per dataset)

---

## 5) Python pipeline code (src/)

### Extract (Yahoo Finance / yfinance)
- `src/extract/yahoo_prices.py`
  - downloads OHLCV for tickers; normalizes columns; returns DataFrame
- `src/extract/yahoo_company_info.py`
  - loops tickers; calls `Ticker(symbol).info`; returns DataFrame
- `src/extract/yahoo_benchmark_series.py`
  - downloads benchmarks/macro series tickers; returns DataFrame

### Load (Snowflake)
- `src/load/snowflake_loader.py`
  - reads connection settings from `/usr/local/airflow/include/<project_name>/profiles.yml`
  - loads DataFrames to `RAW.*` (append-only)
  - writes run metadata to `METADATA.INGEST_RUNS`
  - updates watermarks in `METADATA.WATERMARKS`

### profiles reader (single source of truth)
- `src/common/profiles_reader.py`
  - reads YAML from `/usr/local/airflow/include/<project_name>/profiles.yml`
  - returns dict with: account, user, role, warehouse, database, schema, private_key_path

---

## 6) dbt project (dbt_finance/)

### dbt configuration
- In `dbt_finance/dbt_project.yml` set:
  - `profile: <project_name>` (must match the first YAML key in your `profiles.yml`)

### Models (minimum)
**Staging**
- `stg_stock_prices.sql` — dedupe + daily_return
- `stg_company_info.sql` — latest snapshot per symbol (if append-only)
- `stg_benchmark_series.sql` — series clean/dedupe

**Marts**
- `dim_stocks.sql` — symbol + sector/industry
- `fact_daily_metrics.sql` — grain `symbol × date`, join prices + company + benchmarks

### dbt tests (minimum)
- `unique` + `not_null` on `(symbol, date)` for main fact
- `not_null` on `symbol`, `date`, `close`

---

## 7) Airflow DAG (dags/finance_pipeline_dag.py)

### Task graph (linear, aligns with class demo)
1. `extract_yahoo_prices` (PythonOperator)
2. `extract_yahoo_company_info` (PythonOperator)
3. `extract_yahoo_benchmark_series` (PythonOperator)
4. `transform_dbt` (BashOperator)
5. `verify_snowflake` (PythonOperator recommended)

### dbt command (must point to include/<project_name>)
Use `--profiles-dir` pointing at the folder containing `profiles.yml`:

```bash
cd /usr/local/airflow/dbt_finance \
  && dbt run  --profiles-dir /usr/local/airflow/include/<project_name> \
  && dbt test --profiles-dir /usr/local/airflow/include/<project_name>
```

### Verification (recommended: PythonOperator)
To avoid maintaining separate Airflow connections:
- Implement verification using the same `profiles.yml` + `rsa_key.pem`
  - `COUNT(*) > 0` in your main mart table
  - no duplicates on `(symbol, date)`
  - recent `MAX(date)` (e.g., within last 7 days)

---

## 8) Streamlit app (streamlit_app/)

### What it reads
- Queries Snowflake **ANALYTICS** tables produced by dbt.

### Pages (minimum)
1. **Stock Screener**
   - filters: sector, market cap bins, ticker search
   - output: table + time series chart (Close & MA20)
2. **Benchmark Overlay**
   - pick a stock + benchmark (`^GSPC`, `^VIX`, etc.)
   - chart overlay for selected date range

### Credentials for Streamlit
For local dev, simplest is to parse the same dbt profile:
- read `include/<project_name>/profiles.yml`
- load key from `include/rsa_key.pem`

For deployment, move only the needed Snowflake fields to Streamlit secrets.

---

## 9) Copilot/Agent “Definition of Done”

### Phase A — Bootstrap
- `include/rsa_key.pem` present
- `include/<project_name>/profiles.yml` present and top key renamed to `<project_name>`
- Snowflake objects created (database + schemas + RAW tables)

### Phase B — Extract/Load
- Running extract scripts loads rows into `RAW.*`
- `METADATA.INGEST_RUNS` populated

### Phase C — dbt
- `dbt run` builds `ANALYTICS.*`
- `dbt test` passes

### Phase D — Airflow
- DAG runs end-to-end in Astro
- Verify task passes

### Phase E — Streamlit
- App queries Snowflake and shows 2 interactive pages

---

## 10) Notes on Yahoo Finance reliability
- Yahoo can throttle: implement retries + backoff and keep the ticker list small.
- Prefer batching tickers for `download()` rather than one request per symbol.
