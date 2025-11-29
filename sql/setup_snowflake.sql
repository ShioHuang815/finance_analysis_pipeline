-- =====================================================
-- Snowflake DDL for Finance Analysis Pipeline (COBRA-only)
-- =====================================================
-- Requirement: ALL objects must be created inside the existing schema COBRA
-- Database: MLDS430 (exists)
-- Schema:   COBRA  (exists)
--
-- This script creates tables as: COBRA.<table_name>
-- No additional schemas (RAW/ANALYTICS/METADATA) are created.
-- =====================================================

USE ROLE TRAINING_ROLE;
USE WAREHOUSE TRAINING_WH;
USE DATABASE MLDS430;
USE SCHEMA COBRA;

-- Optional: tag session/query history
ALTER SESSION SET QUERY_TAG = 'finance_pipeline_cobra_setup';

-- =====================================================
-- 1) RAW-style landing tables (in COBRA)
-- =====================================================

-- Stock daily prices (OHLCV)
CREATE TABLE IF NOT EXISTS COBRA.STOCK_PRICES_DAILY (
    symbol          VARCHAR(10) NOT NULL,
    date            DATE        NOT NULL,
    open            FLOAT,
    high            FLOAT,
    low             FLOAT,
    close           FLOAT       NOT NULL,
    adj_close       FLOAT,
    volume          BIGINT,
    ingested_at     TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    source_run_id   VARCHAR(100)
)
COMMENT = 'COBRA-only: Daily OHLCV stock prices from Yahoo Finance (landing/raw)';

-- Company information and fundamentals
CREATE TABLE IF NOT EXISTS COBRA.COMPANY_INFO (
    symbol                  VARCHAR(10) NOT NULL,
    company_name            VARCHAR(500),
    sector                  VARCHAR(100),
    industry                VARCHAR(200),
    market_cap              BIGINT,
    enterprise_value        BIGINT,
    pe_ratio                FLOAT,
    forward_pe              FLOAT,
    peg_ratio               FLOAT,
    price_to_book           FLOAT,
    dividend_yield          FLOAT,
    beta                    FLOAT,
    fifty_two_week_high     FLOAT,
    fifty_two_week_low      FLOAT,
    fifty_day_average       FLOAT,
    two_hundred_day_average FLOAT,
    shares_outstanding      BIGINT,
    float_shares            BIGINT,
    employees               INTEGER,
    country                 VARCHAR(100),
    city                    VARCHAR(100),
    website                 VARCHAR(500),
    business_summary        TEXT,
    ingested_at             TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    source_run_id           VARCHAR(100),
    error                   VARCHAR(1000)
)
COMMENT = 'COBRA-only: Company profile and fundamentals from Yahoo Finance (landing/raw)';

-- Benchmark and macro series
CREATE TABLE IF NOT EXISTS COBRA.BENCHMARK_SERIES_DAILY (
    series_ticker   VARCHAR(20) NOT NULL,
    date            DATE        NOT NULL,
    value           FLOAT       NOT NULL,
    ingested_at     TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    source_run_id   VARCHAR(100)
)
COMMENT = 'COBRA-only: Benchmark indices and macro tickers (^GSPC, ^VIX, ^TNX, sector ETFs)';

-- =====================================================
-- 2) METADATA tables (in COBRA)
-- =====================================================

-- Ingestion run logs
CREATE TABLE IF NOT EXISTS COBRA.INGEST_RUNS (
    run_id          VARCHAR(100) PRIMARY KEY,
    dataset_name    VARCHAR(100) NOT NULL,
    table_name      VARCHAR(100) NOT NULL,
    run_timestamp   TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    records_loaded  INTEGER,
    status          VARCHAR(20),   -- started, completed, failed
    error_message   TEXT
)
COMMENT = 'COBRA-only: Log of all ingestion runs';

-- Watermarks for incremental loads
CREATE TABLE IF NOT EXISTS COBRA.WATERMARKS (
    dataset_name    VARCHAR(100) PRIMARY KEY,
    watermark_value VARCHAR(100),
    updated_at      TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
)
COMMENT = 'COBRA-only: Watermarks for tracking last loaded data points';

-- =====================================================
-- 3) Grants (optional - adjust as needed)
-- =====================================================

GRANT USAGE ON DATABASE MLDS430 TO ROLE TRAINING_ROLE;
GRANT USAGE ON SCHEMA COBRA TO ROLE TRAINING_ROLE;

GRANT ALL ON ALL TABLES IN SCHEMA COBRA TO ROLE TRAINING_ROLE;
GRANT ALL ON FUTURE TABLES IN SCHEMA COBRA TO ROLE TRAINING_ROLE;

-- =====================================================
-- 4) Verify setup (COBRA-only)
-- =====================================================

SHOW TABLES IN SCHEMA COBRA;

DESCRIBE TABLE COBRA.STOCK_PRICES_DAILY;
DESCRIBE TABLE COBRA.COMPANY_INFO;
DESCRIBE TABLE COBRA.BENCHMARK_SERIES_DAILY;
DESCRIBE TABLE COBRA.INGEST_RUNS;
DESCRIBE TABLE COBRA.WATERMARKS;
-- =====================================================