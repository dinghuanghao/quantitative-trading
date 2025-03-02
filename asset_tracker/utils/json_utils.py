import json
from typing import Dict, Any, Optional
from datetime import date
import os
from pathlib import Path

from ..models.portfolio import Portfolio, PortfolioDay, CashHoldings, TotalAssets, ExchangeRates, StockHoldings, Stock
from ..config.settings import DATA_DIR, PORTFOLIO_FILE


def portfolio_to_dict(portfolio: Portfolio) -> Dict[str, Any]:
    """Convert a Portfolio object to a dictionary for JSON serialization."""
    result = {}
    
    for date_str, day in portfolio.data.items():
        day_dict = {
            "cash": {
                "USD": day.cash.USD,
                "HKD": day.cash.HKD,
                "CNY": day.cash.CNY
            },
            "totalAssets": {
                "USD": day.totalAssets.USD,
                "HKD": day.totalAssets.HKD,
                "CNY": day.totalAssets.CNY
            },
            "exchangeRates": {
                "USD": day.exchangeRates.USD,
                "CNY": day.exchangeRates.CNY,
                "HKD": day.exchangeRates.HKD
            },
            "stocks": {
                "AShares": [
                    {
                        "name": stock.name,
                        "code": stock.code,
                        "quantity": stock.quantity,
                        "cost": stock.cost,
                        "price": stock.price
                    } for stock in day.stocks.AShares.values()
                ],
                "USStocks": [
                    {
                        "name": stock.name,
                        "code": stock.code,
                        "quantity": stock.quantity,
                        "cost": stock.cost,
                        "price": stock.price
                    } for stock in day.stocks.USStocks.values()
                ],
                "HKStocks": [
                    {
                        "name": stock.name,
                        "code": stock.code,
                        "quantity": stock.quantity,
                        "cost": stock.cost,
                        "price": stock.price
                    } for stock in day.stocks.HKStocks.values()
                ]
            }
        }
        result[date_str] = day_dict
    
    return result


def dict_to_portfolio(data: Dict[str, Any]) -> Portfolio:
    """Convert a dictionary to a Portfolio object."""
    portfolio = Portfolio()
    
    for date_str, day_data in data.items():
        # Create cash holdings
        cash_data = day_data.get("cash", {})
        cash = CashHoldings(
            USD=cash_data.get("USD", 0.0),
            HKD=cash_data.get("HKD", 0.0),
            CNY=cash_data.get("CNY", 0.0)
        )
        
        # Create total assets
        total_assets_data = day_data.get("totalAssets", {})
        total_assets = TotalAssets(
            USD=total_assets_data.get("USD"),
            HKD=total_assets_data.get("HKD"),
            CNY=total_assets_data.get("CNY")
        )
        
        # Create exchange rates
        exchange_rates_data = day_data.get("exchangeRates", {})
        exchange_rates = ExchangeRates(
            USD=exchange_rates_data.get("USD", 1.0),
            CNY=exchange_rates_data.get("CNY"),
            HKD=exchange_rates_data.get("HKD")
        )
        
        # Create stock holdings
        stocks_data = day_data.get("stocks", {})
        
        # A-shares
        a_shares = {}
        for stock_data in stocks_data.get("AShares", []):
            stock = Stock(
                name=stock_data.get("name", ""),
                code=stock_data.get("code", ""),
                quantity=stock_data.get("quantity", 0.0),
                cost=stock_data.get("cost", 0.0),
                price=stock_data.get("price")
            )
            a_shares[stock.code] = stock
        
        # US stocks
        us_stocks = {}
        for stock_data in stocks_data.get("USStocks", []):
            stock = Stock(
                name=stock_data.get("name", ""),
                code=stock_data.get("code", ""),
                quantity=stock_data.get("quantity", 0.0),
                cost=stock_data.get("cost", 0.0),
                price=stock_data.get("price")
            )
            us_stocks[stock.code] = stock
        
        # HK stocks
        hk_stocks = {}
        for stock_data in stocks_data.get("HKStocks", []):
            stock = Stock(
                name=stock_data.get("name", ""),
                code=stock_data.get("code", ""),
                quantity=stock_data.get("quantity", 0.0),
                cost=stock_data.get("cost", 0.0),
                price=stock_data.get("price")
            )
            hk_stocks[stock.code] = stock
        
        stocks = StockHoldings(
            AShares=a_shares,
            USStocks=us_stocks,
            HKStocks=hk_stocks
        )
        
        # Create portfolio day
        portfolio_day = PortfolioDay(
            cash=cash,
            totalAssets=total_assets,
            stocks=stocks,
            exchangeRates=exchange_rates
        )
        
        # Add to portfolio
        portfolio.add_day(date_str, portfolio_day)
    
    return portfolio


def save_portfolio(portfolio: Portfolio, file_path: Optional[str] = None) -> None:
    """Save a portfolio to a JSON file."""
    if file_path is None:
        # Create data directory if it doesn't exist
        data_dir = Path(DATA_DIR)
        data_dir.mkdir(exist_ok=True)
        file_path = data_dir / PORTFOLIO_FILE
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(portfolio_to_dict(portfolio), f, ensure_ascii=False, indent=4)


def load_portfolio(file_path: Optional[str] = None) -> Portfolio:
    """Load a portfolio from a JSON file."""
    if file_path is None:
        file_path = Path(DATA_DIR) / PORTFOLIO_FILE
    
    if not os.path.exists(file_path):
        return Portfolio()
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return dict_to_portfolio(data)
