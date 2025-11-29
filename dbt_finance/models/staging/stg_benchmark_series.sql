-- Staging model for benchmark series
-- Deduplicates and adds period-over-period changes

WITH source AS (
    SELECT
        series_ticker,
        date,
        value,
        ingested_at,
        source_run_id,
        ROW_NUMBER() OVER (PARTITION BY series_ticker, date ORDER BY ingested_at DESC) as rn
    FROM {{ source('raw', 'benchmark_series_daily') }}
),

deduplicated AS (
    SELECT
        series_ticker,
        date,
        value,
        ingested_at,
        source_run_id
    FROM source
    WHERE rn = 1
),

with_changes AS (
    SELECT
        *,
        -- Daily change
        value - LAG(value) OVER (PARTITION BY series_ticker ORDER BY date) AS daily_change,
        
        -- Percent change
        (value - LAG(value) OVER (PARTITION BY series_ticker ORDER BY date)) / 
            NULLIF(LAG(value) OVER (PARTITION BY series_ticker ORDER BY date), 0) AS pct_change
    FROM deduplicated
)

SELECT * FROM with_changes
