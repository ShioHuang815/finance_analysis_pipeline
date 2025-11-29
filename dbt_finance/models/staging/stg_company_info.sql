-- Staging model for company info
-- Takes the most recent record per symbol

WITH source AS (
    SELECT
        symbol,
        company_name,
        sector,
        industry,
        market_cap,
        enterprise_value,
        pe_ratio,
        forward_pe,
        peg_ratio,
        price_to_book,
        dividend_yield,
        beta,
        fifty_two_week_high,
        fifty_two_week_low,
        fifty_day_average,
        two_hundred_day_average,
        shares_outstanding,
        float_shares,
        employees,
        country,
        city,
        website,
        business_summary,
        ingested_at,
        source_run_id,
        ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY ingested_at DESC) as rn
    FROM {{ source('raw', 'company_info') }}
    WHERE error IS NULL  -- Exclude records with errors
),

latest_info AS (
    SELECT
        symbol,
        company_name,
        sector,
        industry,
        market_cap,
        enterprise_value,
        pe_ratio,
        forward_pe,
        peg_ratio,
        price_to_book,
        dividend_yield,
        beta,
        fifty_two_week_high,
        fifty_two_week_low,
        fifty_day_average,
        two_hundred_day_average,
        shares_outstanding,
        float_shares,
        employees,
        country,
        city,
        website,
        business_summary,
        ingested_at
    FROM source
    WHERE rn = 1
)

SELECT * FROM latest_info
