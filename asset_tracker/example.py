#!/usr/bin/env python3
"""
Example script demonstrating the asset tracking feature.
This script shows how to use the portfolio manager to track assets across different currencies and stocks.
"""

import logging
import json
from datetime import datetime

from asset_tracker.portfolio_manager import PortfolioManager
from asset_tracker.models.portfolio import Stock
from asset_tracker.utils.json_utils import portfolio_to_dict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    # Create a portfolio manager
    manager = PortfolioManager()
    
    # Get today's date in YYYY-MM-DD format
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Create a new portfolio day for today
    portfolio_day = manager.create_portfolio_day(today)
    
    # Update cash holdings
    manager.update_cash(today, "USD", 10000)
    manager.update_cash(today, "HKD", 10000)
    manager.update_cash(today, "CNY", 10000)
    
    # Add A-shares
    manager.add_stock(today, "AShares", Stock(
        name="贵州茅台",
        code="600519",
        quantity=100,
        cost=10
    ))
    manager.add_stock(today, "AShares", Stock(
        name="中证 2000ETF",
        code="563300",
        quantity=100,
        cost=0.5
    ))
    
    # Add US stocks
    manager.add_stock(today, "USStocks", Stock(
        name="特斯拉",
        code="TSLA",
        quantity=100,
        cost=100
    ))
    manager.add_stock(today, "USStocks", Stock(
        name="英伟达",
        code="NVDA",
        quantity=100,
        cost=100
    ))
    
    # Add HK stocks
    manager.add_stock(today, "HKStocks", Stock(
        name="腾讯控股",
        code="00700",
        quantity=100,
        cost=100
    ))
    
    # Update stock prices
    logger.info("Updating stock prices...")
    manager.update_stock_prices(today)
    
    # Update total assets
    logger.info("Calculating total assets...")
    manager.update_total_assets(today)
    
    # Save the portfolio
    manager.save()
    
    # Get and display portfolio summary
    summary = manager.get_portfolio_summary(today)
    logger.info("Portfolio Summary:")
    logger.info(json.dumps(summary, indent=4, ensure_ascii=False))
    
    # Display the full portfolio data
    portfolio_data = portfolio_to_dict(manager.portfolio)
    logger.info("Full Portfolio Data:")
    logger.info(json.dumps(portfolio_data, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()
