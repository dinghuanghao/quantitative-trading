from typing import Optional, Dict, List
from datetime import datetime
import logging

from .models.portfolio import Portfolio, PortfolioDay, CashHoldings, StockHoldings, Stock
from .utils.json_utils import load_portfolio, save_portfolio
from .services.stock_prices import update_stock_prices
from .services.exchange_rates import get_exchange_rates, get_historical_exchange_rates
from .config.settings import BASE_CURRENCY

logger = logging.getLogger(__name__)


class PortfolioManager:
    """Manager class for portfolio operations."""
    
    def __init__(self, portfolio_file: Optional[str] = None):
        """Initialize the portfolio manager."""
        self.portfolio = load_portfolio(portfolio_file)
        self.portfolio_file = portfolio_file
    
    def save(self) -> None:
        """Save the portfolio to file."""
        save_portfolio(self.portfolio, self.portfolio_file)
    
    def get_portfolio_day(self, date_str: Optional[str] = None) -> Optional[PortfolioDay]:
        """
        Get a portfolio day by date.
        
        Args:
            date_str: Date string in YYYY-MM-DD format, None for latest
            
        Returns:
            PortfolioDay object or None if not found
        """
        if date_str is None:
            result = self.portfolio.latest_day()
            return result[1] if result else None
        return self.portfolio.get_day(date_str)
    
    def create_portfolio_day(self, date_str: str) -> PortfolioDay:
        """
        Create a new portfolio day.
        
        Args:
            date_str: Date string in YYYY-MM-DD format
            
        Returns:
            New PortfolioDay object
        """
        # Check if day already exists
        existing_day = self.portfolio.get_day(date_str)
        if existing_day:
            return existing_day
        
        # Create new day
        new_day = PortfolioDay()
        self.portfolio.add_day(date_str, new_day)
        return new_day
    
    def update_cash(self, date_str: str, currency: str, amount: float) -> None:
        """
        Update cash holdings for a specific date and currency.
        
        Args:
            date_str: Date string in YYYY-MM-DD format
            currency: Currency code (USD, HKD, or CNY)
            amount: Cash amount
        """
        day = self.get_portfolio_day(date_str)
        if not day:
            day = self.create_portfolio_day(date_str)
        
        if currency == "USD":
            day.cash.USD = amount
        elif currency == "HKD":
            day.cash.HKD = amount
        elif currency == "CNY":
            day.cash.CNY = amount
        else:
            raise ValueError(f"Unsupported currency: {currency}")
    
    def add_stock(self, date_str: str, market: str, stock: Stock) -> None:
        """
        Add a stock to the portfolio.
        
        Args:
            date_str: Date string in YYYY-MM-DD format
            market: Market type ('AShares', 'USStocks', or 'HKStocks')
            stock: Stock object to add
        """
        day = self.get_portfolio_day(date_str)
        if not day:
            day = self.create_portfolio_day(date_str)
        
        if market == "AShares":
            day.stocks.AShares.append(stock)
        elif market == "USStocks":
            day.stocks.USStocks.append(stock)
        elif market == "HKStocks":
            day.stocks.HKStocks.append(stock)
        else:
            raise ValueError(f"Unknown market: {market}")
    
    def update_stock_prices(self, date_str: Optional[str] = None) -> None:
        """
        Update prices for all stocks in the portfolio.
        
        Args:
            date_str: Date string in YYYY-MM-DD format, None for latest prices
        """
        day = self.get_portfolio_day(date_str)
        if not day:
            if date_str is None:
                logger.warning("No portfolio data found for the latest date")
                return
            day = self.create_portfolio_day(date_str)
        
        # Update prices for each market
        update_stock_prices(day.stocks.AShares, "AShares", date_str)
        update_stock_prices(day.stocks.USStocks, "USStocks", date_str)
        update_stock_prices(day.stocks.HKStocks, "HKStocks", date_str)
    
    def update_total_assets(self, date_str: Optional[str] = None) -> None:
        """
        Update total assets calculation for a specific date.
        
        Args:
            date_str: Date string in YYYY-MM-DD format, None for latest
        """
        day = self.get_portfolio_day(date_str)
        if not day:
            if date_str is None:
                logger.warning("No portfolio data found for the latest date")
                return
            day = self.create_portfolio_day(date_str)
        
        # Get exchange rates
        if date_str is None:
            exchange_rates = get_exchange_rates()
        else:
            exchange_rates = get_historical_exchange_rates(date_str)
            
            # If historical rates are not available, use current rates
            if not exchange_rates:
                logger.warning(f"No historical exchange rates found for {date_str}, using current rates")
                exchange_rates = get_exchange_rates()
        
        # Update total assets
        day.update_total_assets(exchange_rates)
    
    def get_portfolio_summary(self, date_str: Optional[str] = None) -> Dict:
        """
        Get a summary of the portfolio for a specific date.
        
        Args:
            date_str: Date string in YYYY-MM-DD format, None for latest
            
        Returns:
            Dictionary with portfolio summary
        """
        day = self.get_portfolio_day(date_str)
        if not day:
            return {"error": "No portfolio data found for the specified date"}
        
        # Calculate stock values
        stock_values = day.stocks.total_value()
        
        # Create summary
        summary = {
            "date": date_str or "latest",
            "cash": {
                "USD": day.cash.USD,
                "HKD": day.cash.HKD,
                "CNY": day.cash.CNY
            },
            "stocks": {
                "AShares": {
                    "count": len(day.stocks.AShares),
                    "value": stock_values["AShares"]
                },
                "USStocks": {
                    "count": len(day.stocks.USStocks),
                    "value": stock_values["USStocks"]
                },
                "HKStocks": {
                    "count": len(day.stocks.HKStocks),
                    "value": stock_values["HKStocks"]
                }
            },
            "totalAssets": {
                "USD": day.totalAssets.USD,
                "HKD": day.totalAssets.HKD,
                "CNY": day.totalAssets.CNY
            }
        }
        
        return summary
