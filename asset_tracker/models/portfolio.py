from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union
from datetime import date


@dataclass
class Stock:
    name: str
    code: str
    quantity: float
    cost: float
    price: Optional[float] = None
    
    def market_value(self) -> Optional[float]:
        """Calculate the current market value of the stock."""
        if self.price is None:
            return None
        return self.quantity * self.price
    
    def profit_loss(self) -> Optional[float]:
        """Calculate the profit/loss for this stock."""
        if self.price is None:
            return None
        return (self.price - self.cost) * self.quantity


@dataclass
class CashHoldings:
    USD: float = 0.0
    HKD: float = 0.0
    CNY: float = 0.0
    
    def total_in_currency(self, currency: str, exchange_rates: Dict[str, float]) -> float:
        """
        Calculate total cash value in the specified currency.
        
        Args:
            currency: Target currency code (USD, HKD, CNY)
            exchange_rates: Dictionary of exchange rates with currency as key
                           and rate as value (relative to USD)
        
        Returns:
            Total cash value in the specified currency
        """
        if currency == "USD":
            return (self.USD + 
                    self.HKD / exchange_rates.get("HKD", 1) + 
                    self.CNY / exchange_rates.get("CNY", 1))
        elif currency == "HKD":
            return (self.HKD + 
                    self.USD * exchange_rates.get("HKD", 1) + 
                    self.CNY * exchange_rates.get("HKD", 1) / exchange_rates.get("CNY", 1))
        elif currency == "CNY":
            return (self.CNY + 
                    self.USD * exchange_rates.get("CNY", 1) + 
                    self.HKD * exchange_rates.get("CNY", 1) / exchange_rates.get("HKD", 1))
        else:
            raise ValueError(f"Unsupported currency: {currency}")


@dataclass
class TotalAssets:
    USD: Optional[float] = None
    HKD: Optional[float] = None
    CNY: Optional[float] = None


@dataclass
class StockHoldings:
    AShares: Dict[str, Stock] = field(default_factory=dict)
    USStocks: Dict[str, Stock] = field(default_factory=dict)
    HKStocks: Dict[str, Stock] = field(default_factory=dict)
    
    def total_value_by_market(self, market: str) -> Optional[float]:
        """Calculate the total value of stocks in a specific market."""
        if market == "AShares":
            stocks = self.AShares.values()
        elif market == "USStocks":
            stocks = self.USStocks.values()
        elif market == "HKStocks":
            stocks = self.HKStocks.values()
        else:
            raise ValueError(f"Unknown market: {market}")
            
        values = [stock.market_value() for stock in stocks]
        if None in values:
            return None
        return sum(values)
    
    def total_value(self) -> Dict[str, Optional[float]]:
        """Calculate the total value of all stocks by market."""
        return {
            "AShares": self.total_value_by_market("AShares"),
            "USStocks": self.total_value_by_market("USStocks"),
            "HKStocks": self.total_value_by_market("HKStocks")
        }


@dataclass
class PortfolioDay:
    cash: CashHoldings = field(default_factory=CashHoldings)
    totalAssets: TotalAssets = field(default_factory=TotalAssets)
    stocks: StockHoldings = field(default_factory=StockHoldings)
    
    def update_total_assets(self, exchange_rates: Dict[str, float]) -> None:
        """
        Update the total assets calculation based on current stock prices and exchange rates.
        
        Args:
            exchange_rates: Dictionary of exchange rates with currency as key
                           and rate as value (relative to USD)
        """
        # Calculate stock values in their native currencies
        stock_values = self.stocks.total_value()
        
        # Calculate total in USD
        usd_stocks = stock_values["USStocks"] or 0
        cny_in_usd = (stock_values["AShares"] or 0) / exchange_rates.get("CNY", 1)
        hkd_in_usd = (stock_values["HKStocks"] or 0) / exchange_rates.get("HKD", 1)
        
        # Add cash holdings
        usd_total = usd_stocks + cny_in_usd + hkd_in_usd + self.cash.total_in_currency("USD", exchange_rates)
        
        # Convert to other currencies
        cny_total = usd_total * exchange_rates.get("CNY", 1)
        hkd_total = usd_total * exchange_rates.get("HKD", 1)
        
        # Update total assets
        self.totalAssets.USD = usd_total
        self.totalAssets.CNY = cny_total
        self.totalAssets.HKD = hkd_total


@dataclass
class Portfolio:
    data: Dict[str, PortfolioDay] = field(default_factory=dict)
    
    def add_day(self, date_str: str, portfolio_day: PortfolioDay) -> None:
        """Add or update a portfolio day entry."""
        self.data[date_str] = portfolio_day
    
    def get_day(self, date_str: str) -> Optional[PortfolioDay]:
        """Get a portfolio day entry by date string."""
        return self.data.get(date_str)
    
    def latest_day(self) -> Optional[tuple[str, PortfolioDay]]:
        """Get the most recent portfolio day entry."""
        if not self.data:
            return None
        latest_date = max(self.data.keys())
        return latest_date, self.data[latest_date]
