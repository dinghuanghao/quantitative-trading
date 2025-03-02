import requests
import yfinance as yf
import pandas as pd
import pandas_datareader as pdr
from typing import Dict, Optional, List
import logging
from datetime import datetime, timedelta

from ..models.portfolio import Stock

logger = logging.getLogger(__name__)


def get_ashare_price(code: str, date_str: Optional[str] = None) -> Optional[float]:
    """
    Get price for A-share stock using Yahoo Finance.
    
    Args:
        code: Stock code (e.g., '600519')
        date_str: Date string in YYYY-MM-DD format, None for latest price
        
    Returns:
        Stock price or None if not available
    """
    try:
        # Convert code to Yahoo Finance format for A-shares
        # Shanghai: code.SS, Shenzhen: code.SZ
        yahoo_code = f"{code}.{'SS' if code.startswith('6') else 'SZ'}"
        
        if date_str is None:
            # Get real-time price
            ticker = yf.Ticker(yahoo_code)
            data = ticker.history(period="1d")
            if not data.empty:
                return float(data['Close'].iloc[-1])
            return None
        else:
            # Get historical price
            end_date = datetime.strptime(date_str, "%Y-%m-%d")
            start_date = end_date - timedelta(days=5)  # Get a few days before to ensure we have data
            
            data = yf.download(yahoo_code, start=start_date, end=end_date + timedelta(days=1))
            
            if not data.empty:
                # Find the closest date if exact date not available
                if date_str in data.index.strftime('%Y-%m-%d').tolist():
                    return float(data.loc[data.index.strftime('%Y-%m-%d') == date_str, 'Close'].iloc[0])
                else:
                    # Get the last available date before the requested date
                    available_dates = data.index[data.index <= pd.Timestamp(date_str)]
                    if not available_dates.empty:
                        return float(data.loc[available_dates[-1], 'Close'])
            return None
    except Exception as e:
        logger.error(f"Error fetching A-share price for {code}: {e}")
        return None


def get_us_stock_price(code: str, date_str: Optional[str] = None) -> Optional[float]:
    """
    Get price for US stock using Yahoo Finance.
    
    Args:
        code: Stock code (e.g., 'AAPL')
        date_str: Date string in YYYY-MM-DD format, None for latest price
        
    Returns:
        Stock price or None if not available
    """
    try:
        if date_str is None:
            # Get real-time price
            ticker = yf.Ticker(code)
            data = ticker.history(period="1d")
            if not data.empty:
                return float(data['Close'].iloc[-1])
            return None
        else:
            # Get historical price
            end_date = datetime.strptime(date_str, "%Y-%m-%d")
            start_date = end_date - timedelta(days=5)  # Get a few days before to ensure we have data
            
            data = yf.download(code, start=start_date, end=end_date + timedelta(days=1))
            
            if not data.empty:
                # Find the closest date if exact date not available
                if date_str in data.index.strftime('%Y-%m-%d').tolist():
                    return float(data.loc[data.index.strftime('%Y-%m-%d') == date_str, 'Close'].iloc[0])
                else:
                    # Get the last available date before the requested date
                    available_dates = data.index[data.index <= pd.Timestamp(date_str)]
                    if not available_dates.empty:
                        return float(data.loc[available_dates[-1], 'Close'])
            return None
    except Exception as e:
        logger.error(f"Error fetching US stock price for {code}: {e}")
        return None


def get_hk_stock_price(code: str, date_str: Optional[str] = None) -> Optional[float]:
    """
    Get price for Hong Kong stock using Yahoo Finance.
    
    Args:
        code: Stock code (e.g., '00700')
        date_str: Date string in YYYY-MM-DD format, None for latest price
        
    Returns:
        Stock price or None if not available
    """
    try:
        # Convert code to Yahoo Finance format for HK stocks
        yahoo_code = f"{code}.HK"
        
        if date_str is None:
            # Get real-time price
            ticker = yf.Ticker(yahoo_code)
            data = ticker.history(period="1d")
            if not data.empty:
                return float(data['Close'].iloc[-1])
            return None
        else:
            # Get historical price
            end_date = datetime.strptime(date_str, "%Y-%m-%d")
            start_date = end_date - timedelta(days=5)  # Get a few days before to ensure we have data
            
            data = yf.download(yahoo_code, start=start_date, end=end_date + timedelta(days=1))
            
            if not data.empty:
                # Find the closest date if exact date not available
                if date_str in data.index.strftime('%Y-%m-%d').tolist():
                    return float(data.loc[data.index.strftime('%Y-%m-%d') == date_str, 'Close'].iloc[0])
                else:
                    # Get the last available date before the requested date
                    available_dates = data.index[data.index <= pd.Timestamp(date_str)]
                    if not available_dates.empty:
                        return float(data.loc[available_dates[-1], 'Close'])
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
