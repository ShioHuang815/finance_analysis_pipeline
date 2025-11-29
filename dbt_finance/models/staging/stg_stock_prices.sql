-- Staging model for stock prices
-- Deduplicates and adds calculated fields like daily returns

WITH source AS (
    SELECT
        symbol,
        date,
        open,
        high,
        low,
        close,
        adj_close,
        volume,
        ingested_at,
        source_run_id,
        ROW_NUMBER() OVER (PARTITION BY symbol, date ORDER BY ingested_at DESC) as rn
    FROM {{ source('raw', 'stock_prices_daily') }}
),

deduplicated AS (
    SELECT
        symbol,
        date,
        open,
        high,
        low,
        close,
        adj_close,
        volume,
        ingested_at,
        source_run_id
    FROM source
    WHERE rn = 1
),

with_metrics AS (
    SELECT
        *,
        -- Daily return calculation
        (close - LAG(close) OVER (PARTITION BY symbol ORDER BY date)) / 
            NULLIF(LAG(close) OVER (PARTITION BY symbol ORDER BY date), 0) AS daily_return,
        
        -- Volatility (high-low range as % of close)
        (high - low) / NULLIF(close, 0) AS daily_volatility,
        
        -- Price change
        close - open AS price_change,
        
        -- Volume moving average (5 day)
        AVG(volume) OVER (
            PARTITION BY symbol 
            ORDER BY date 
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ) AS volume_ma5
    FROM deduplicated
)

SELECT * FROM with_metrics
