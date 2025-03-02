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
            # Try using forex_spot_quote for real-time forex data
            df = ak.forex_spot_quote()
            # Find USD/CNY rate
            usd_cny_row = df[df['代码'] == 'USDCNY']
            if not usd_cny_row.empty:
                rates["CNY"] = float(usd_cny_row['卖出'].iloc[0])
            else:
                # Fallback to a default rate if not found
                rates["CNY"] = 7.0  # Approximate USD/CNY rate
                logger.warning("Using default USD/CNY rate: 7.0")
        except Exception as e:
            logger.error(f"Error fetching USD/CNY rate: {e}")
            # Fallback to a default rate
            rates["CNY"] = 7.0
            logger.warning("Using default USD/CNY rate: 7.0")
            
        # Get USD/HKD rate
        try:
            # Try using forex_spot_quote for real-time forex data
            df = ak.forex_spot_quote()
            # Find USD/HKD rate
            usd_hkd_row = df[df['代码'] == 'USDHKD']
            if not usd_hkd_row.empty:
                rates["HKD"] = float(usd_hkd_row['卖出'].iloc[0])
            else:
                # Fallback to a default rate if not found
                rates["HKD"] = 7.8  # Approximate USD/HKD rate
                logger.warning("Using default USD/HKD rate: 7.8")
        except Exception as e:
            logger.error(f"Error fetching USD/HKD rate: {e}")
            # Fallback to a default rate
            rates["HKD"] = 7.8
            logger.warning("Using default USD/HKD rate: 7.8")
        
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
        # Return default rates if cache is empty
        if not _exchange_rate_cache:
            return {"USD": 1.0, "CNY": 7.0, "HKD": 7.8}
        return _exchange_rate_cache


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
        # For historical rates, we'll use current rates as AKShare doesn't have a direct
        # historical currency API that works reliably for all date ranges
        rates = {}
        
        # Get current rates as fallback
        try:
            # Try using forex_spot_quote for real-time forex data
            df = ak.forex_spot_quote()
            
            # Find USD/CNY rate
            usd_cny_row = df[df['代码'] == 'USDCNY']
            if not usd_cny_row.empty:
                rates["CNY"] = float(usd_cny_row['卖出'].iloc[0])
            else:
                # Fallback to a default rate if not found
                rates["CNY"] = 7.0  # Approximate USD/CNY rate
                logger.warning(f"Using default USD/CNY rate for {date_str}: 7.0")
                
            # Find USD/HKD rate
            usd_hkd_row = df[df['代码'] == 'USDHKD']
            if not usd_hkd_row.empty:
                rates["HKD"] = float(usd_hkd_row['卖出'].iloc[0])
            else:
                # Fallback to a default rate if not found
                rates["HKD"] = 7.8  # Approximate USD/HKD rate
                logger.warning(f"Using default USD/HKD rate for {date_str}: 7.8")
        except Exception as e:
            logger.error(f"Error fetching current rates as fallback: {e}")
            # Use default rates
            rates["CNY"] = 7.0
            rates["HKD"] = 7.8
            logger.warning(f"Using default rates for {date_str}: USD/CNY=7.0, USD/HKD=7.8")
        
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
        # Return default rates
        return {"USD": 1.0, "CNY": 7.0, "HKD": 7.8}
