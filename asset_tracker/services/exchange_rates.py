import requests
import pandas as pd
import pandas_datareader.data as web
from typing import Dict, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Cache for exchange rates to avoid repeated API calls
_exchange_rate_cache = {}
_last_update = None


def get_exchange_rates(base_currency: str = "USD", force_refresh: bool = False) -> Dict[str, float]:
    """
    Fetch current exchange rates using the free exchangerate.host API.
    
    Args:
        base_currency: Base currency for the exchange rates
        force_refresh: Whether to force a refresh of the cache
        
    Returns:
        Dictionary of exchange rates with currency as key and rate as value
    """
    global _exchange_rate_cache, _last_update
    
    # Check if we need to refresh the cache
    current_time = datetime.now()
    if (not force_refresh and _last_update is not None and 
            current_time - _last_update < timedelta(hours=1) and 
            _exchange_rate_cache):
        return _exchange_rate_cache
    
    try:
        # Use the free exchangerate.host API
        url = f"https://api.exchangerate.host/latest?base={base_currency}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data.get("success", False):
            _exchange_rate_cache = data.get("rates", {})
            _last_update = current_time
            return _exchange_rate_cache
        else:
            logger.error(f"Failed to fetch exchange rates: {data}")
            return _exchange_rate_cache or {}
            
    except Exception as e:
        logger.error(f"Error fetching exchange rates: {e}")
        return _exchange_rate_cache or {}


def get_historical_exchange_rates(date_str: str, base_currency: str = "USD") -> Dict[str, float]:
    """
    Fetch historical exchange rates for a specific date using exchangerate.host.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        base_currency: Base currency for the exchange rates
        
    Returns:
        Dictionary of exchange rates with currency as key and rate as value
    """
    try:
        # Use the free exchangerate.host API for historical data
        url = f"https://api.exchangerate.host/{date_str}?base={base_currency}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data.get("success", False):
            return data.get("rates", {})
        else:
            # Fallback to pandas-datareader with Yahoo Finance data
            logger.warning(f"Falling back to pandas-datareader for historical exchange rates on {date_str}")
            
            # Convert date string to datetime
            date = datetime.strptime(date_str, "%Y-%m-%d")
            
            # Get exchange rates for major currencies
            rates = {}
            
            # Try to get USD/CNY rate
            try:
                df = web.DataReader(f"CNY{base_currency}=X", "yahoo", date, date + timedelta(days=1))
                if not df.empty:
                    rates["CNY"] = float(df["Close"].iloc[-1])
            except Exception as e:
                logger.error(f"Error fetching USD/CNY rate: {e}")
            
            # Try to get USD/HKD rate
            try:
                df = web.DataReader(f"HKD{base_currency}=X", "yahoo", date, date + timedelta(days=1))
                if not df.empty:
                    rates["HKD"] = float(df["Close"].iloc[-1])
            except Exception as e:
                logger.error(f"Error fetching USD/HKD rate: {e}")
            
            return rates
            
    except Exception as e:
        logger.error(f"Error fetching historical exchange rates: {e}")
        return {}
