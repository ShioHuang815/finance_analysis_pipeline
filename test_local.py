"""
Test script for local development
Run this to verify all components work before deploying to Airflow.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.common.logging import setup_logger
from src.common.profiles_reader import read_profiles, get_snowflake_connection_params
from src.extract.yahoo_prices import extract_yahoo_prices
from src.extract.yahoo_company_info import extract_yahoo_company_info
from src.extract.yahoo_benchmark_series import extract_yahoo_benchmark_series
from src.load.snowflake_loader import SnowflakeLoader
import yaml

logger = setup_logger(__name__)

def test_profiles():
    """Test reading dbt profiles."""
    logger.info("\n=== Testing Profiles Reader ===")
    try:
        # Adjust path for local testing
        local_path = "include/project_name/profiles.yml"
        profiles = read_profiles(local_path, "finance_analysis_pipeline")
        logger.info(f"✓ Successfully read profiles")
        logger.info(f"  Account: {profiles['account']}")
        logger.info(f"  Database: {profiles['database']}")
        logger.info(f"  Schema: {profiles['schema']}")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to read profiles: {e}")
        return False

def test_snowflake_connection():
    """Test Snowflake connection."""
    logger.info("\n=== Testing Snowflake Connection ===")
    try:
        # Use local path
        os.environ['PROFILES_PATH'] = 'include/project_name/profiles.yml'
        loader = SnowflakeLoader(profiles_path='include/project_name/profiles.yml')
        
        result = loader.execute_query(
            "SELECT CURRENT_VERSION() as version, CURRENT_USER() as user, CURRENT_ROLE() as role"
        )
        
        logger.info(f"✓ Successfully connected to Snowflake")
        logger.info(f"  Version: {result['VERSION'].iloc[0]}")
        logger.info(f"  User: {result['USER'].iloc[0]}")
        logger.info(f"  Role: {result['ROLE'].iloc[0]}")
        
        loader.close()
        return True
    except Exception as e:
        logger.error(f"✗ Failed to connect to Snowflake: {e}")
        return False

def test_extractors():
    """Test Yahoo Finance extractors."""
    logger.info("\n=== Testing Yahoo Finance Extractors ===")
    
    # Load small subset of tickers
    with open('config/tickers.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    test_stocks = config['stocks'][:3]  # First 3 stocks
    test_benchmarks = config['benchmarks'][:2]  # First 2 benchmarks
    
    try:
        # Test prices
        logger.info("Testing price extraction...")
        prices_df = extract_yahoo_prices(test_stocks, period="5d")
        logger.info(f"✓ Extracted {len(prices_df)} price records")
        
        # Test company info
        logger.info("Testing company info extraction...")
        company_df = extract_yahoo_company_info(test_stocks)
        logger.info(f"✓ Extracted {len(company_df)} company records")
        
        # Test benchmarks
        logger.info("Testing benchmark extraction...")
        benchmark_df = extract_yahoo_benchmark_series(test_benchmarks, period="5d")
        logger.info(f"✓ Extracted {len(benchmark_df)} benchmark records")
        
        return True
    except Exception as e:
        logger.error(f"✗ Extraction failed: {e}")
        return False

def test_full_pipeline():
    """Test full extract and load pipeline."""
    logger.info("\n=== Testing Full Pipeline (Extract + Load) ===")
    
    with open('config/tickers.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    test_stocks = config['stocks'][:2]  # Minimal test
    test_benchmarks = config['benchmarks'][:1]
    
    loader = None
    try:
        # Extract
        logger.info("Extracting data...")
        prices_df = extract_yahoo_prices(test_stocks, period="5d")
        company_df = extract_yahoo_company_info(test_stocks)
        benchmark_df = extract_yahoo_benchmark_series(test_benchmarks, period="5d")
        
        # Load
        logger.info("Loading to Snowflake...")
        loader = SnowflakeLoader(profiles_path='include/project_name/profiles.yml')
        
        result1 = loader.load_to_raw(prices_df, 'STOCK_PRICES_DAILY', 'test_prices')
        logger.info(f"✓ Loaded {result1['records_loaded']} price records")
        
        result2 = loader.load_to_raw(company_df, 'COMPANY_INFO', 'test_company')
        logger.info(f"✓ Loaded {result2['records_loaded']} company records")
        
        result3 = loader.load_to_raw(benchmark_df, 'BENCHMARK_SERIES_DAILY', 'test_benchmarks')
        logger.info(f"✓ Loaded {result3['records_loaded']} benchmark records")
        
        # Verify
        logger.info("Verifying data...")
        count_query = "SELECT COUNT(*) as count FROM RAW.STOCK_PRICES_DAILY"
        count_result = loader.execute_query(count_query)
        logger.info(f"✓ Total price records in Snowflake: {count_result['COUNT'].iloc[0]}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if loader:
            loader.close()

def main():
    """Run all tests."""
    logger.info("=" * 60)
    logger.info("Finance Analysis Pipeline - Component Tests")
    logger.info("=" * 60)
    
    results = {
        'Profiles': test_profiles(),
        'Snowflake Connection': test_snowflake_connection(),
        'Extractors': test_extractors(),
        'Full Pipeline': test_full_pipeline(),
    }
    
    logger.info("\n" + "=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    logger.info("=" * 60)
    
    if all_passed:
        logger.info("🎉 All tests passed! Ready to deploy to Airflow.")
        return 0
    else:
        logger.error("❌ Some tests failed. Fix issues before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
