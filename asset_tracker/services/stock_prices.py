import requests
import tushare as ts
from typing import Dict, Optional, List
import logging
from datetime import datetime

from ..config.settings import ALPHA_VANTAGE_API_KEY, ALPHA_VANTAGE_BASE_URL, TUSHARE_API_KEY
from ..models.portfolio import Stock

logger = logging.getLogger(__name__)

# Initialize Tushare
ts.set_token(TUSHARE_API_KEY)
pro = ts.pro_api()


def get_ashare_price(code: str, date_str: Optional[str] = None) -> Optional[float]:
    """
    Get price for A-share stock.
    
    Args:
        code: Stock code (e.g., '600519')
        date_str: Date string in YYYY-MM-DD format, None for latest price
        
    Returns:
        Stock price or None if not available
    """
    try:
        if date_str is None:
            # Get real-time price
            df = ts.get_realtime_quotes(code)
            if df is not None and not df.empty:
                return float(df.iloc[0]['price'])
            return None
        else:
            # Get historical price
            end_date = datetime.strptime(date_str, "%Y-%m-%d")
            start_date = end_date.strftime("%Y%m%d")
            end_date = end_date.strftime("%Y%m%d")
            
            df = pro.daily(ts_code=f"{code}.SH" if code.startswith('6') else f"{code}.SZ", 
                          start_date=start_date, 
                          end_date=end_date)
            
            if df is not None and not df.empty:
                return float(df.iloc[0]['close'])
            return None
    except Exception as e:
        logger.error(f"Error fetching A-share price for {code}: {e}")
        return None


def get_us_stock_price(code: str, date_str: Optional[str] = None) -> Optional[float]:
    """
    Get price for US stock.
    
    Args:
        code: Stock code (e.g., 'AAPL')
        date_str: Date string in YYYY-MM-DD format, None for latest price
        
    Returns:
        Stock price or None if not available
    """
    try:
        if date_str is None:
            # Get real-time price
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": code,
                "apikey": ALPHA_VANTAGE_API_KEY
            }
        else:
            # Get historical price
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": code,
                "apikey": ALPHA_VANTAGE_API_KEY,
                "outputsize": "compact"
            }
        
        response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        if date_str is None:
            # Extract real-time price
            quote = data.get("Global Quote", {})
            price_str = quote.get("05. price")
            return float(price_str) if price_str else None
        else:
            # Extract historical price
            time_series = data.get("Time Series (Daily)", {})
            date_data = time_series.get(date_str, {})
            
            if date_data:
                return float(date_data.get("4. close", 0))
            return None
            
    except Exception as e:
        logger.error(f"Error fetching US stock price for {code}: {e}")
        return None


def get_hk_stock_price(code: str, date_str: Optional[str] = None) -> Optional[float]:
    """
    Get price for Hong Kong stock.
    
    Args:
        code: Stock code (e.g., '00700')
        date_str: Date string in YYYY-MM-DD format, None for latest price
        
    Returns:
        Stock price or None if not available
    """
    try:
        # For HK stocks, we can use Tushare as well
        if date_str is None:
            # Get real-time price (using Tushare's HK quote API)
            df = ts.get_hk_quote(code)
            if df is not None and not df.empty:
                return float(df.iloc[0]['price'])
            return None
        else:
            # Get historical price
            end_date = datetime.strptime(date_str, "%Y-%m-%d")
            start_date = end_date.strftime("%Y%m%d")
            end_date = end_date.strftime("%Y%m%d")
            
            df = pro.hk_daily(ts_code=f"{code}.HK", 
                            start_date=start_date, 
                            end_date=end_date)
            
            if df is not None and not df.empty:
                return float(df.iloc[0]['close'])
            return None
    except Exception as e:
        logger.error(f"Error fetching HK stock price for {code}: {e}")
        return None


def update_stock_prices(stocks: List[Stock], market: str, date_str: Optional[str] = None) -> None:
    """
    Update prices for a list of stocks.
    
    Args:
        stocks: List of Stock objects to update
        market: Market type ('AShares', 'USStocks', or 'HKStocks')
        date_str: Date string in YYYY-MM-DD format, None for latest prices
    """
    for stock in stocks:
        if market == "AShares":
            stock.price = get_ashare_price(stock.code, date_str)
        elif market == "USStocks":
            stock.price = get_us_stock_price(stock.code, date_str)
        elif market == "HKStocks":
            stock.price = get_hk_stock_price(stock.code, date_str)
        else:
            logger.warning(f"Unknown market: {market}")
