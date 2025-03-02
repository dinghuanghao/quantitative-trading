# Asset Tracker

A feature for quantitative trading that records and calculates portfolio value across different currencies and stocks.

## Overview

The Asset Tracker is designed to help traders and investors track their portfolio across multiple markets and currencies. It provides functionality to:

- Record cash holdings in multiple currencies (CNY, USD, HKD)
- Track stock holdings across different markets (A-Shares, US Stocks, HK Stocks)
- Calculate total portfolio value with automatic currency conversion
- Store historical portfolio data with daily snapshots
- Fetch real-time or historical stock prices and exchange rates

## JSON Schema Structure

The portfolio data is stored in a JSON format with the following structure:

```json
{
    "YYYY-MM-DD": {
        "cash": {
            "USD": 10000,
            "HKD": 10000,
            "CNY": 10000
        },
        "totalAssets": {
            "USD": 50000,
            "HKD": 390000,
            "CNY": 320000
        },
        "stocks": {
            "AShares": [
                {
                    "name": "贵州茅台",
                    "code": "600519",
                    "quantity": 100,
                    "cost": 10,
                    "price": 2000
                },
                {
                    "name": "中证 2000ETF",
                    "code": "563300",
                    "quantity": 100,
                    "cost": 0.5,
                    "price": 1.2
                }
            ],
            "USStocks": [
                {
                    "name": "特斯拉",
                    "code": "TSLA",
                    "quantity": 100,
                    "cost": 100,
                    "price": 200
                },
                {
                    "name": "英伟达",
                    "code": "NVDA",
                    "quantity": 100,
                    "cost": 100,
                    "price": 150
                }
            ],
            "HKStocks": [
                {
                    "name": "腾讯控股",
                    "code": "00700",
                    "quantity": 100,
                    "cost": 100,
                    "price": 350
                }
            ]
        }
    }
}
```

Key features of the schema:
- Date as the top-level key in YYYY-MM-DD format
- Cash holdings in multiple currencies
- Total assets calculated in multiple currencies
- Stocks grouped by market (A-Shares, US Stocks, HK Stocks)
- Each stock includes name, code, quantity, cost basis, and current price

## External APIs and Data Sources

The Asset Tracker uses the following external APIs to fetch stock prices and exchange rates:

### 1. Alpha Vantage API
- Used for US stock prices and forex data
- Provides both real-time and historical data
- API documentation: [Alpha Vantage Documentation](https://www.alphavantage.co/documentation/)
- Required for: US stock prices, historical exchange rates

### 2. Tushare API
- Used for Chinese A-shares and Hong Kong stock data
- Provides comprehensive data for Chinese markets
- API documentation: [Tushare Documentation](https://tushare.pro/document/2)
- Required for: A-shares prices, Hong Kong stock prices

### 3. Exchange Rate API
- Used for current exchange rates
- Free and simple API for currency conversion
- API documentation: [Exchange Rate API Documentation](https://www.exchangerate-api.com/docs/free)
- Required for: Current exchange rates between currencies

## Directory Structure

```
asset_tracker/
├── __init__.py
├── config/
│   ├── __init__.py
│   └── settings.py         # Configuration settings and API keys
├── data/
│   ├── __init__.py
│   └── portfolio.json      # Default location for portfolio data
├── models/
│   ├── __init__.py
│   └── portfolio.py        # Data models for portfolio, stocks, etc.
├── services/
│   ├── __init__.py
│   ├── exchange_rates.py   # Service for fetching exchange rates
│   └── stock_prices.py     # Service for fetching stock prices
├── utils/
│   ├── __init__.py
│   └── json_utils.py       # Utilities for JSON serialization/deserialization
├── tests/
│   └── __init__.py         # Test directory for unit tests
├── portfolio_manager.py    # Main portfolio manager class
├── example.py              # Example script demonstrating usage
└── README.md               # This documentation file
```

## Installation and Usage

### Prerequisites
- Python 3.6+
- Required packages: `requests`, `tushare`

### Installation
1. Clone the repository
2. Install required packages:
   ```
   pip install requests tushare
   ```
3. Configure API keys in `asset_tracker/config/settings.py`

### Basic Usage

```python
from asset_tracker.portfolio_manager import PortfolioManager
from asset_tracker.models.portfolio import Stock

# Create a portfolio manager
manager = PortfolioManager()

# Get today's date
today = "2025-03-02"

# Update cash holdings
manager.update_cash(today, "USD", 10000)
manager.update_cash(today, "HKD", 10000)
manager.update_cash(today, "CNY", 10000)

# Add stocks
manager.add_stock(today, "USStocks", Stock(
    name="Tesla",
    code="TSLA",
    quantity=100,
    cost=100
))

# Update stock prices and calculate total assets
manager.update_stock_prices(today)
manager.update_total_assets(today)

# Save the portfolio
manager.save()

# Get portfolio summary
summary = manager.get_portfolio_summary(today)
print(summary)
```

For a complete example, see `example.py`.

## Behavior

- Cash amounts and stock quantities are manually input by the user
- Stock prices are automatically fetched:
  - Closing price for past dates
  - Real-time price for current date if market is open
- Total assets are automatically calculated based on:
  - Current stock prices
  - Current exchange rates
  - Sum of all cash holdings converted to the specified currency
