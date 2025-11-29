-- Fact table combining stock prices with benchmark data
-- Grain: symbol x date

WITH prices AS (
    SELECT
        symbol,
        date,
        close,
        adj_close,
        volume,
        daily_return,
        daily_volatility,
        price_change
    FROM {{ ref('stg_stock_prices') }}
),

company AS (
    SELECT
        symbol,
        sector,
        industry,
        market_cap
    FROM {{ ref('stg_company_info') }}
),

-- Pivot benchmarks to get one row per date
benchmarks_pivot AS (
    SELECT
        date,
        MAX(CASE WHEN series_ticker = '^GSPC' THEN value END) AS sp500_value,
        MAX(CASE WHEN series_ticker = '^GSPC' THEN pct_change END) AS sp500_return,
        MAX(CASE WHEN series_ticker = '^VIX' THEN value END) AS vix_value,
        MAX(CASE WHEN series_ticker = '^TNX' THEN value END) AS treasury_10y,
        MAX(CASE WHEN series_ticker = 'XLK' THEN value END) AS tech_sector_etf,
        MAX(CASE WHEN series_ticker = 'XLF' THEN value END) AS financial_sector_etf
    FROM {{ ref('stg_benchmark_series') }}
    GROUP BY date
),

joined AS (
    SELECT
        p.symbol,
        p.date,
        c.sector,
        c.industry,
        c.market_cap,
        p.close,
        p.adj_close,
        p.volume,
        p.daily_return,
        p.daily_volatility,
        p.price_change,
        b.sp500_value,
        b.sp500_return,
        b.vix_value,
        b.treasury_10y,
        b.tech_sector_etf,
        b.financial_sector_etf,
        
        -- Relative performance vs S&P 500
        COALESCE(p.daily_return, 0) - COALESCE(b.sp500_return, 0) AS alpha_vs_sp500,
        
        -- Market cap category
        CASE
            WHEN c.market_cap >= 200000000000 THEN 'Mega Cap'
            WHEN c.market_cap >= 10000000000 THEN 'Large Cap'
            WHEN c.market_cap >= 2000000000 THEN 'Mid Cap'
            WHEN c.market_cap >= 300000000 THEN 'Small Cap'
            ELSE 'Micro Cap'
        END AS market_cap_category
        
    FROM prices p
    LEFT JOIN company c ON p.symbol = c.symbol
    LEFT JOIN benchmarks_pivot b ON p.date = b.date
)

SELECT * FROM joined
