import os
import pandas as pd
import yfinance as yf
from fredapi import Fred
from dotenv import load_dotenv

load_dotenv()

SECTORS = {
    "XLK": "Technology", "XLF": "Financials", "XLE": "Energy",
    "XLV": "Health Care", "XLY": "Consumer Discretionary",
    "XLP": "Consumer Staples", "XLI": "Industrials", "XLB": "Materials",
    "XLU": "Utilities", "XLRE": "Real Estate", "XLC": "Communication Services",
}

def get_prices(start="2015-01-01"):
    tickers = list(SECTORS) + ["SPY"]
    px = yf.download(tickers, start=start, auto_adjust=True)["Close"]
    px.to_parquet("data/raw/prices.parquet")
    return px

def get_macro(start="2015-01-01"):
    fred = Fred(api_key=os.environ["FRED_API_KEY"])
    series = {
        "T10Y2Y": "yield_curve",
        "BAMLH0A0HYM2": "hy_spread",
        "DGS10": "ten_year",
        "DTWEXBGS": "usd_index",
        "VIXCLS": "vix",
    }
    df = pd.concat(
        {name: fred.get_series(code, observation_start=start) for code, name in series.items()},
        axis=1,
    )
    df.to_parquet("data/raw/macro.parquet")
    return df

if __name__ == "__main__":
    get_prices()
    get_macro() 