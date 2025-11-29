"""
Yahoo Finance - Stock Daily Prices Extractor
Downloads OHLCV data for configured stock tickers.
"""
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Optional
from src.common.logging import setup_logger

logger = setup_logger(__name__)


def extract_yahoo_prices(
    tickers: List[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    period: str = "1y"
) -> pd.DataFrame:
    """
    Extract daily OHLCV data from Yahoo Finance.
    
    Args:
        tickers: List of stock ticker symbols
        start_date: Start date (YYYY-MM-DD format). If None, uses period.
        end_date: End date (YYYY-MM-DD format). If None, uses today.
        period: Period to fetch if start_date is None (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
    
    Returns:
        DataFrame with columns: symbol, date, open, high, low, close, adj_close, volume
    """
    logger.info(f"Extracting price data for {len(tickers)} tickers")
    
    try:
        # Download data for all tickers at once (more efficient)
        if start_date and end_date:
            logger.info(f"Downloading data from {start_date} to {end_date}")
            data = yf.download(
                tickers,
                start=start_date,
                end=end_date,
                group_by='ticker',
                auto_adjust=False,
                progress=False,
                threads=True
            )
        else:
            logger.info(f"Downloading data for period: {period}")
            data = yf.download(
                tickers,
                period=period,
                group_by='ticker',
                auto_adjust=False,
                progress=False,
                threads=True
            )
        
        # Handle single ticker vs multiple tickers
        if len(tickers) == 1:
            # Single ticker returns different structure
            df = data.copy()
            df['symbol'] = tickers[0]
            df = df.reset_index()
        else:
            # Multiple tickers - need to reshape
            dfs = []
            for ticker in tickers:
                try:
                    ticker_data = data[ticker].copy()
                    ticker_data['symbol'] = ticker
                    ticker_data = ticker_data.reset_index()
                    dfs.append(ticker_data)
                except KeyError:
                    logger.warning(f"No data found for ticker: {ticker}")
                    continue
            
            if not dfs:
                logger.error("No data extracted for any ticker")
                return pd.DataFrame()
            
            df = pd.concat(dfs, ignore_index=True)
        
        # Normalize column names
        df.columns = df.columns.str.lower()
        
        # Rename columns to match our schema
        column_mapping = {
            'date': 'date',
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'adj close': 'adj_close',
            'volume': 'volume',
            'symbol': 'symbol'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Select and order columns
        final_columns = ['symbol', 'date', 'open', 'high', 'low', 'close', 'adj_close', 'volume']
        df = df[final_columns]
        
        # Add metadata
        df['ingested_at'] = datetime.now()
        
        # Remove rows with missing critical data
        df = df.dropna(subset=['close', 'volume'])
        
        logger.info(f"Successfully extracted {len(df)} price records")
        
        return df
    
    except Exception as e:
        logger.error(f"Error extracting price data: {str(e)}")
        raise


if __name__ == "__main__":
    # Test extraction
    import yaml
    
    # Load ticker config
    with open('config/tickers.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    tickers = config['stocks'][:5]  # Test with first 5 tickers
    
    df = extract_yahoo_prices(tickers, period="1mo")
    print(f"\nExtracted {len(df)} records")
    print(df.head(10))
    print(f"\nColumns: {df.columns.tolist()}")
    print(f"\nData types:\n{df.dtypes}")
