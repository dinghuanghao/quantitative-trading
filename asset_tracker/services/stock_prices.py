import requests
import pandas as pd
import akshare as ak
from typing import Dict, Optional, List
import logging
from datetime import datetime, timedelta

from ..models.portfolio import Stock

logger = logging.getLogger(__name__)


def get_ashare_price(code: str, date_str: Optional[str] = None) -> Optional[float]:
    """
    Get price for A-share stock using AKShare.
    
    Args:
        code: Stock code (e.g., '600519')
        date_str: Date string in YYYY-MM-DD format, None for latest price
        
    Returns:
        Stock price or None if not available
    """
    try:
        # Format date for AKShare
        if date_str is None:
            # Get the latest price
            df = ak.stock_zh_a_spot_em()
            # Filter by code
            df = df[df['代码'] == code]
            if not df.empty:
                return float(df['最新价'].iloc[0])
            return None
        else:
            # Get historical price
            # Convert date format from YYYY-MM-DD to YYYYMMDD
            start_date = datetime.strptime(date_str, "%Y-%m-%d")
            end_date = start_date + timedelta(days=1)
            
            start_date_str = start_date.strftime("%Y%m%d")
            end_date_str = end_date.strftime("%Y%m%d")
            
            df = ak.stock_zh_a_hist(symbol=code, period="daily", 
                                   start_date=start_date_str, 
                                   end_date=end_date_str, 
                                   adjust="")
            
            if not df.empty:
                # Get the closing price
                return float(df['收盘'].iloc[0])
            return None
    except Exception as e:
        logger.error(f"Error fetching A-share price for {code}: {e}")
        return None


def get_us_stock_price(code: str, date_str: Optional[str] = None) -> Optional[float]:
    """
    Get price for US stock using AKShare.
    
    Args:
        code: Stock code (e.g., 'AAPL')
        date_str: Date string in YYYY-MM-DD format, None for latest price
        
    Returns:
        Stock price or None if not available
    """
    try:
        if date_str is None:
            # Get real-time price
            df = ak.stock_us_spot_em()
            # Filter by code
            df = df[df['代码'] == code]
            if not df.empty:
                return float(df['最新价'].iloc[0])
            return None
        else:
            # Get historical price
            # Convert date format from YYYY-MM-DD to YYYYMMDD
            start_date = datetime.strptime(date_str, "%Y-%m-%d")
            end_date = start_date + timedelta(days=1)
            
            start_date_str = start_date.strftime("%Y%m%d")
            end_date_str = end_date.strftime("%Y%m%d")
            
            df = ak.stock_us_hist(symbol=code, period="daily", 
                                 start_date=start_date_str, 
                                 end_date=end_date_str, 
                                 adjust="qfq")
            
            if not df.empty:
                # Get the closing price
                return float(df['收盘'].iloc[0])
            return None
    except Exception as e:
        logger.error(f"Error fetching US stock price for {code}: {e}")
        return None


def get_hk_stock_price(code: str, date_str: Optional[str] = None) -> Optional[float]:
    """
    Get price for Hong Kong stock using AKShare.
    
    Args:
        code: Stock code (e.g., '00700')
        date_str: Date string in YYYY-MM-DD format, None for latest price
        
    Returns:
        Stock price or None if not available
    """
    try:
        if date_str is None:
            # Get real-time price
            df = ak.stock_hk_spot_em()
            # Filter by code
            df = df[df['代码'] == code]
            if not df.empty:
                return float(df['最新价'].iloc[0])
            return None
        else:
            # Get historical price
            # Convert date format from YYYY-MM-DD to YYYYMMDD
            start_date = datetime.strptime(date_str, "%Y-%m-%d")
            end_date = start_date + timedelta(days=1)
            
            start_date_str = start_date.strftime("%Y%m%d")
            end_date_str = end_date.strftime("%Y%m%d")
            
            df = ak.stock_hk_hist(symbol=code, period="daily", 
                                 start_date=start_date_str, 
                                 end_date=end_date_str, 
                                 adjust="")
            
            if not df.empty:
                # Get the closing price
                return float(df['收盘'].iloc[0])
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
