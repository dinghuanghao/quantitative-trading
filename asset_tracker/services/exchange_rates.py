import requests
import pandas as pd
import akshare as ak
from typing import Dict, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Cache for exchange rates to avoid repeated API calls
_exchange_rate_cache = {}
_last_update = None


def get_exchange_rates(base_currency: str = "USD", force_refresh: bool = False) -> Dict[str, float]:
    """
    Fetch current exchange rates using AKShare.
    
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
        # Use AKShare to get exchange rates
        rates = {}
        
        # Get USD/CNY rate
        try:
            df = ak.currency_boc_sina(symbol="USDCNY")
            if not df.empty:
                rates["CNY"] = float(df["中行卖出价"].iloc[0])
        except Exception as e:
            logger.error(f"Error fetching USD/CNY rate: {e}")
            
        # Get USD/HKD rate
        try:
            df = ak.currency_boc_sina(symbol="USDHKD")
            if not df.empty:
                rates["HKD"] = float(df["中行卖出价"].iloc[0])
        except Exception as e:
            logger.error(f"Error fetching USD/HKD rate: {e}")
        
        # Add USD/USD rate (1.0)
        rates["USD"] = 1.0
        
        # If base currency is not USD, convert all rates
        if base_currency != "USD" and base_currency in rates:
            base_rate = rates[base_currency]
            for currency, rate in rates.items():
                rates[currency] = rate / base_rate
        
        _exchange_rate_cache = rates
        _last_update = current_time
        return _exchange_rate_cache
            
    except Exception as e:
        logger.error(f"Error fetching exchange rates: {e}")
        return _exchange_rate_cache or {}


def get_historical_exchange_rates(date_str: str, base_currency: str = "USD") -> Dict[str, float]:
    """
    Fetch historical exchange rates for a specific date using AKShare.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        base_currency: Base currency for the exchange rates
        
    Returns:
        Dictionary of exchange rates with currency as key and rate as value
    """
    try:
        # Convert date format from YYYY-MM-DD to YYYYMMDD
        date = datetime.strptime(date_str, "%Y-%m-%d")
        date_str_formatted = date.strftime("%Y%m%d")
        
        rates = {}
        
        # Get USD/CNY historical rate
        try:
            df = ak.currency_history_sina(symbol="USDCNY", start_date=date_str_formatted, end_date=date_str_formatted)
            if not df.empty:
                rates["CNY"] = float(df["收盘价"].iloc[0])
        except Exception as e:
            logger.warning(f"Error fetching historical USD/CNY rate: {e}")
            # Fallback to current rate
            try:
                df = ak.currency_boc_sina(symbol="USDCNY")
                if not df.empty:
                    rates["CNY"] = float(df["中行卖出价"].iloc[0])
                    logger.info(f"Using current USD/CNY rate as fallback: {rates['CNY']}")
            except Exception as e2:
                logger.error(f"Error fetching current USD/CNY rate as fallback: {e2}")
        
        # Get USD/HKD historical rate
        try:
            df = ak.currency_history_sina(symbol="USDHKD", start_date=date_str_formatted, end_date=date_str_formatted)
            if not df.empty:
                rates["HKD"] = float(df["收盘价"].iloc[0])
        except Exception as e:
            logger.warning(f"Error fetching historical USD/HKD rate: {e}")
            # Fallback to current rate
            try:
                df = ak.currency_boc_sina(symbol="USDHKD")
                if not df.empty:
                    rates["HKD"] = float(df["中行卖出价"].iloc[0])
                    logger.info(f"Using current USD/HKD rate as fallback: {rates['HKD']}")
            except Exception as e2:
                logger.error(f"Error fetching current USD/HKD rate as fallback: {e2}")
        
        # Add USD/USD rate (1.0)
        rates["USD"] = 1.0
        
        # If base currency is not USD, convert all rates
        if base_currency != "USD" and base_currency in rates:
            base_rate = rates[base_currency]
            for currency, rate in rates.items():
                rates[currency] = rate / base_rate
        
        return rates
            
    except Exception as e:
        logger.error(f"Error fetching historical exchange rates: {e}")
        return {}
