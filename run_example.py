#!/usr/bin/env python3
"""
Script to run the asset tracker example with the provided sample data.
Uses AKShare for stock price and exchange rate data.
"""

import os
import sys
import json
import logging
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from asset_tracker.models.portfolio import Portfolio, PortfolioDay, CashHoldings, TotalAssets, StockHoldings, Stock
from asset_tracker.portfolio_manager import PortfolioManager
from asset_tracker.utils.json_utils import portfolio_to_dict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    # Create a portfolio manager
    manager = PortfolioManager()
    
    # Use the example date - using a current date for better data availability
    # AKShare may have issues with future dates
    date_str = datetime.now().strftime("%Y-%m-%d")
    logger.info(f"Using current date for example: {date_str}")
    
    # Create a new portfolio day
    portfolio_day = manager.create_portfolio_day(date_str)
    
    # Update cash holdings with the example data
    manager.update_cash(date_str, "USD", 10000)
    manager.update_cash(date_str, "HKD", 10000)
    manager.update_cash(date_str, "CNY", 10000)
    
    # Add A-shares from the example
    manager.add_stock(date_str, "AShares", Stock(
        name="贵州茅台",
        code="600519",
        quantity=100,
        cost=10
    ))
    manager.add_stock(date_str, "AShares", Stock(
        name="中证500ETF",  # Changed to a more common ETF that AKShare can find
        code="510500",
        quantity=100,
        cost=0.5
    ))
    
    # Add US stocks from the example
    manager.add_stock(date_str, "USStocks", Stock(
        name="特斯拉",
        code="TSLA",
        quantity=100,
        cost=100
    ))
    manager.add_stock(date_str, "USStocks", Stock(
        name="英伟达",
        code="NVDA",
        quantity=100,
        cost=100
    ))
    
    # Add HK stocks from the example
    manager.add_stock(date_str, "HKStocks", Stock(
        name="腾讯控股",
        code="00700",
        quantity=100,
        cost=100
    ))
    
    # Update stock prices
    logger.info("Updating stock prices using AKShare...")
    manager.update_stock_prices(date_str)
    
    # Update total assets
    logger.info("Calculating total assets...")
    manager.update_total_assets(date_str)
    
    # Save the portfolio
    manager.save()
    
    # Get and display portfolio summary
    summary = manager.get_portfolio_summary(date_str)
    logger.info("Portfolio Summary:")
    print(json.dumps(summary, indent=4, ensure_ascii=False))
    
    # Display the full portfolio data
    portfolio_data = portfolio_to_dict(manager.portfolio)
    logger.info("Full Portfolio Data:")
    print(json.dumps(portfolio_data, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()
