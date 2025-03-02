import requests
import pandas as pd
from forex_python.converter import CurrencyRates
from typing import Dict, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Cache for exchange rates to avoid repeated API calls
_exchange_rate_cache = {}
_last_update = None


def get_exchange_rates(base_currency: str = "USD", force_refresh: bool = False) -> Dict[str, float]:
    """
    Fetch current exchange rates using forex-python.
    
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
        # Use forex-python to get exchange rates
        c = CurrencyRates()
        rates = {}
        
        # Get rates for supported currencies
        supported_currencies = ["USD", "CNY", "HKD"]
        
        for currency in supported_currencies:
            try:
                if currency == base_currency:
                    rates[currency] = 1.0
                else:
                    # Get rate from base_currency to currency
                    rates[currency] = c.get_rate(base_currency, currency)
            except Exception as e:
                logger.error(f"Error fetching {base_currency}/{currency} rate: {e}")
                # Fallback to default rates
                if base_currency == "USD" and currency == "CNY":
                    rates[currency] = 7.0
                    logger.warning(f"Using default USD/CNY rate: 7.0")
                elif base_currency == "USD" and currency == "HKD":
                    rates[currency] = 7.8
                    logger.warning(f"Using default USD/HKD rate: 7.8")
                elif currency == "USD":
                    rates[currency] = 1.0
                else:
                    # For other currency pairs, use approximate rates
                    if currency == "CNY":
                        rates[currency] = 7.0
                    elif currency == "HKD":
                        rates[currency] = 7.8
                    logger.warning(f"Using default rate for {base_currency}/{currency}")
        
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
    Fetch historical exchange rates for a specific date using forex-python.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        base_currency: Base currency for the exchange rates
        
    Returns:
        Dictionary of exchange rates with currency as key and rate as value
    """
    try:
        # Parse the date string
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        
        # Use forex-python to get historical rates
        c = CurrencyRates()
        rates = {}
        
        # Get rates for supported currencies
        supported_currencies = ["USD", "CNY", "HKD"]
        
        for currency in supported_currencies:
            try:
                if currency == base_currency:
                    rates[currency] = 1.0
                else:
                    # Get historical rate from base_currency to currency
                    rates[currency] = c.get_rate(base_currency, currency, date_obj)
            except Exception as e:
                logger.error(f"Error fetching historical {base_currency}/{currency} rate for {date_str}: {e}")
                # Fallback to current rates
                try:
                    rates[currency] = c.get_rate(base_currency, currency)
                    logger.warning(f"Using current rate for {base_currency}/{currency} as historical rate not available")
                except Exception as e2:
                    logger.error(f"Error fetching current {base_currency}/{currency} rate as fallback: {e2}")
                    # Use default rates
                    if base_currency == "USD" and currency == "CNY":
                        rates[currency] = 7.0
                        logger.warning(f"Using default USD/CNY rate for {date_str}: 7.0")
                    elif base_currency == "USD" and currency == "HKD":
                        rates[currency] = 7.8
                        logger.warning(f"Using default USD/HKD rate for {date_str}: 7.8")
                    elif currency == "USD":
                        rates[currency] = 1.0
                    else:
                        # For other currency pairs, use approximate rates
                        if currency == "CNY":
                            rates[currency] = 7.0
                        elif currency == "HKD":
                            rates[currency] = 7.8
                        logger.warning(f"Using default rate for {base_currency}/{currency} for {date_str}")
        
        return rates
            
    except Exception as e:
        logger.error(f"Error fetching historical exchange rates: {e}")
        # Return default rates
        return {"USD": 1.0, "CNY": 7.0, "HKD": 7.8}
