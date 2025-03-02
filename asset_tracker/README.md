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

The Asset Tracker uses the following free and open-source libraries and APIs to fetch stock prices and exchange rates:

### 1. AKShare
- Used for stock prices across all markets (US, China, Hong Kong)
- Provides both real-time and historical data
- Free and open-source Python library
- Comprehensive support for Chinese markets (A-shares, Hong Kong)
- API documentation: [AKShare Documentation](https://akshare.akfamily.xyz/)
- Required for: Stock prices and exchange rates for all markets

Examples of AKShare usage:

```python
# Get A-share historical data
import akshare as ak
stock_zh_a_hist_df = ak.stock_zh_a_hist(
    symbol="000001", 
    period="daily", 
    start_date="20230301", 
    end_date="20230401", 
    adjust=""
)

# Get US stock historical data
stock_us_hist_df = ak.stock_us_hist(
    symbol="AAPL", 
    period="daily", 
    start_date="20230201", 
    end_date="20230301", 
    adjust="qfq"
)

# Get Hong Kong stock historical data
stock_hk_hist_df = ak.stock_hk_hist(
    symbol="00700", 
    period="daily", 
    start_date="20230101", 
    end_date="20230201", 
    adjust=""
)

# Get exchange rates
currency_data = ak.currency_boc_sina(symbol="USDCNY")
```

### 2. pandas-datareader
- Used as a backup for financial data
- Provides access to various data sources
- API documentation: [pandas-datareader Documentation](https://pandas-datareader.readthedocs.io/)
- Required for: Additional financial data sources

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
   pip install -r requirements.txt
   ```
3. No API keys are required as the implementation uses free and open-source libraries

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
