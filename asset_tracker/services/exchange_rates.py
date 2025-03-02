import requests
from typing import Dict, Optional
import logging
from datetime import datetime, timedelta

from ..config.settings import EXCHANGE_RATE_API_URL, ALPHA_VANTAGE_API_KEY, ALPHA_VANTAGE_BASE_URL

logger = logging.getLogger(__name__)

# Cache for exchange rates to avoid repeated API calls
_exchange_rate_cache = {}
_last_update = None


def get_exchange_rates(base_currency: str = "USD", force_refresh: bool = False) -> Dict[str, float]:
    """
    Fetch current exchange rates from the API.
    
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
        # Use the Exchange Rate API
        response = requests.get(f"{EXCHANGE_RATE_API_URL}/{base_currency}")
        response.raise_for_status()
        data = response.json()
        
        if data.get("result") == "success":
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
    Fetch historical exchange rates for a specific date.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        base_currency: Base currency for the exchange rates
        
    Returns:
        Dictionary of exchange rates with currency as key and rate as value
    """
    try:
        # Use Alpha Vantage for historical forex data
        # This is a simplified example - Alpha Vantage requires specific currency pairs
        # For a complete solution, you would need to make multiple requests for each pair
        
        # Example for USD/CNY
        params = {
            "function": "FX_DAILY",
            "from_symbol": base_currency,
            "to_symbol": "CNY",
            "apikey": ALPHA_VANTAGE_API_KEY,
            "outputsize": "compact"
        }
        
        response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Extract the rate for the specific date
        time_series = data.get("Time Series FX (Daily)", {})
        date_data = time_series.get(date_str, {})
        
        if date_data:
            # Use the closing price as the exchange rate
            rate = float(date_data.get("4. close", 0))
            return {"CNY": rate}
        else:
            logger.warning(f"No exchange rate data found for {date_str}")
            return {}
            
    except Exception as e:
        logger.error(f"Error fetching historical exchange rates: {e}")
        return {}
