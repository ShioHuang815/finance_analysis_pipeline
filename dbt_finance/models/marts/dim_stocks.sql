-- Dimension table for stocks
-- Company information with sector/industry classification

SELECT
    symbol,
    company_name,
    sector,
    industry,
    market_cap,
    pe_ratio,
    dividend_yield,
    beta,
    country,
    employees,
    ingested_at AS last_updated
FROM {{ ref('stg_company_info') }}
