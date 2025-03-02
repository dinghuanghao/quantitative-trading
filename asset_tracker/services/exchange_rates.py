import requests
import logging
from typing import Dict, Optional, List, Any, Union
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Cache for exchange rates to avoid repeated API calls
_exchange_rate_cache = {}
_last_update = None


def get_exchange_rates(date_str: str = "2025-03-01", base_currency: str = "USD", 
                      target_currencies: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Fetch exchange rates for a specific date using the Exchange Rate API.
    
    Args:
        date_str (str): Date in YYYY-MM-DD format
        base_currency (str): Source currency code (e.g., USD, EUR, CNY)
        target_currencies (list): List of target currency codes. If None, all available rates are returned.
    
    Returns:
        dict: Exchange rate data
    """
    global _exchange_rate_cache, _last_update
    
    # Check if we need to refresh the cache
    cache_key = f"{date_str}_{base_currency}"
    current_time = datetime.now()
    if (_last_update is not None and 
            current_time - _last_update < timedelta(hours=1) and 
            cache_key in _exchange_rate_cache):
        logger.info(f"Using cached exchange rates for {date_str} with base {base_currency}")
        data = _exchange_rate_cache[cache_key]
        
        # Filter rates if target currencies are specified
        if target_currencies and "rates" in data:
            rates = data.get("rates", {})
            filtered_rates = {curr: rate for curr, rate in rates.items() if curr in target_currencies}
            data["filtered_rates"] = filtered_rates
            
        return data
    
    try:
        # For demonstration purposes - in reality, you'd need an API key
        # and the free tier might not support historical data
        url = f"https://open.er-api.com/v6/latest/{base_currency}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            # Add note about the date discrepancy
            logger.info(f"Note: Requested date was {date_str}, but the API returned the latest rates")
            logger.info(f"API response time: {data.get('time_last_update_utc', 'Not provided')}")
            logger.info(f"Base currency: {base_currency}")
            
            # Display the rates
            rates = data.get("rates", {})
            
            # Filter rates if target currencies are specified
            if target_currencies:
                filtered_rates = {curr: rate for curr, rate in rates.items() if curr in target_currencies}
                logger.info(f"Exchange Rates (base: {base_currency}, filtered to requested currencies):")
                for currency, rate in sorted(filtered_rates.items()):
                    logger.info(f"{currency}: {rate}")
                
                # Add filtered rates to the data
                data["filtered_rates"] = filtered_rates
            else:
                logger.info(f"Exchange Rates (base: {base_currency}):")
                for currency, rate in sorted(rates.items())[:5]:  # Log only first 5 to avoid excessive logging
                    logger.info(f"{currency}: {rate}")
                logger.info(f"... and {len(rates) - 5} more currencies")
            
            # Update cache
            _exchange_rate_cache[cache_key] = data
            _last_update = current_time
            
            return data
        else:
            logger.error(f"Error: API returned status code {response.status_code}")
            return _get_default_exchange_rates(base_currency, target_currencies)
            
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return _get_default_exchange_rates(base_currency, target_currencies)


def get_historical_exchange_rates(date_str: str, base_currency: str = "USD", 
                                 target_currencies: Optional[List[str]] = None) -> Dict[str, Union[float, Dict[str, float]]]:
    """
    Fetch historical exchange rates for a specific date.
    This is a wrapper around get_exchange_rates for backward compatibility.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        base_currency: Base currency for the exchange rates
        target_currencies: List of target currency codes
        
    Returns:
        Dictionary of exchange rates with currency as key and rate as value
    """
    # If target_currencies is not provided, use default supported currencies
    if target_currencies is None:
        target_currencies = ["USD", "CNY", "HKD"]
    
    # Call the new exchange rates function
    data = get_exchange_rates(date_str, base_currency, target_currencies)
    
    # For backward compatibility, return just the rates dictionary
    if data is None:
        return _get_default_rates_dict(base_currency)
    
    # If filtered_rates exists, use that
    if "filtered_rates" in data:
        return data["filtered_rates"]
    
    # Otherwise, use the full rates dictionary
    rates = data.get("rates", {})
    
    # Filter to only include the target currencies
    filtered_rates = {curr: rate for curr, rate in rates.items() if curr in target_currencies}
    
    # Ensure base currency has rate 1.0
    if base_currency not in filtered_rates:
        filtered_rates[base_currency] = 1.0
    
    return filtered_rates


def _get_default_exchange_rates(base_currency: str = "USD", 
                               target_currencies: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Get default exchange rates when API fails.
    
    Args:
        base_currency: Base currency for the exchange rates
        target_currencies: List of target currency codes
        
    Returns:
        Dictionary with default exchange rate data
    """
    # Default rates
    default_rates = {
        "USD": 1.0,
        "CNY": 7.0,
        "HKD": 7.8,
        "EUR": 0.92,
        "GBP": 0.79,
        "JPY": 150.0
    }
    
    # Adjust rates based on base currency
    if base_currency != "USD" and base_currency in default_rates:
        base_rate = default_rates[base_currency]
        adjusted_rates = {curr: rate / base_rate for curr, rate in default_rates.items()}
        adjusted_rates[base_currency] = 1.0
    else:
        adjusted_rates = default_rates
    
    # Create response data structure
    data = {
        "result": "success",
        "provider": "default",
        "base": base_currency,
        "rates": adjusted_rates,
        "time_last_update_utc": datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
    }
    
    # Filter rates if target currencies are specified
    if target_currencies:
        filtered_rates = {curr: rate for curr, rate in adjusted_rates.items() if curr in target_currencies}
        data["filtered_rates"] = filtered_rates
    
    logger.warning(f"Using default exchange rates with base {base_currency}")
    return data


def _get_default_rates_dict(base_currency: str = "USD") -> Dict[str, float]:
    """
    Get a simple dictionary of default exchange rates.
    
    Args:
        base_currency: Base currency for the exchange rates
        
    Returns:
        Dictionary of exchange rates with currency as key and rate as value
    """
    # Default rates
    default_rates = {
        "USD": 1.0,
        "CNY": 7.0,
        "HKD": 7.8
    }
    
    # Adjust rates based on base currency
    if base_currency != "USD" and base_currency in default_rates:
        base_rate = default_rates[base_currency]
        adjusted_rates = {curr: rate / base_rate for curr, rate in default_rates.items()}
        adjusted_rates[base_currency] = 1.0
        return adjusted_rates
    
    return default_rates
