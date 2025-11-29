"""
Yahoo Finance - Company Information Extractor
Fetches company profile and fundamental data.
"""
import pandas as pd
import yfinance as yf
from datetime import datetime
from typing import List
from src.common.logging import setup_logger
import time

logger = setup_logger(__name__)


def extract_yahoo_company_info(tickers: List[str]) -> pd.DataFrame:
    """
    Extract company information and fundamentals from Yahoo Finance.
    
    Args:
        tickers: List of stock ticker symbols
    
    Returns:
        DataFrame with company info: symbol, sector, industry, market_cap, pe_ratio, dividend_yield, etc.
    """
    logger.info(f"Extracting company info for {len(tickers)} tickers")
    
    records = []
    
    for ticker_symbol in tickers:
        try:
            logger.debug(f"Fetching info for {ticker_symbol}")
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            
            # Extract relevant fields
            record = {
                'symbol': ticker_symbol,
                'company_name': info.get('longName', info.get('shortName', ticker_symbol)),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'market_cap': info.get('marketCap'),
                'enterprise_value': info.get('enterpriseValue'),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'peg_ratio': info.get('pegRatio'),
                'price_to_book': info.get('priceToBook'),
                'dividend_yield': info.get('dividendYield'),
                'beta': info.get('beta'),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
                'fifty_day_average': info.get('fiftyDayAverage'),
                'two_hundred_day_average': info.get('twoHundredDayAverage'),
                'shares_outstanding': info.get('sharesOutstanding'),
                'float_shares': info.get('floatShares'),
                'employees': info.get('fullTimeEmployees'),
                'country': info.get('country'),
                'city': info.get('city'),
                'website': info.get('website'),
                'business_summary': info.get('longBusinessSummary'),
                'ingested_at': datetime.now()
            }
            
            records.append(record)
            
            # Be polite to Yahoo - small delay between requests
            time.sleep(0.1)
            
        except Exception as e:
            logger.warning(f"Error fetching info for {ticker_symbol}: {str(e)}")
            # Add a minimal record so we don't lose the ticker
            records.append({
                'symbol': ticker_symbol,
                'ingested_at': datetime.now(),
                'error': str(e)
            })
            continue
    
    df = pd.DataFrame(records)
    logger.info(f"Successfully extracted info for {len(df)} companies")
    
    return df


if __name__ == "__main__":
    # Test extraction
    import yaml
    
    with open('config/tickers.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    tickers = config['stocks'][:3]  # Test with first 3 tickers
    
    df = extract_yahoo_company_info(tickers)
    print(f"\nExtracted {len(df)} company records")
    print(df[['symbol', 'company_name', 'sector', 'industry', 'market_cap']].head())
    print(f"\nColumns: {df.columns.tolist()}")
