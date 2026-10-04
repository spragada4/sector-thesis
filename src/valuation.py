import io
import time
import datetime as dt
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import yfinance as yf

from src.data import SECTORS

URL = ("https://www.ssga.com/us/en/individual/etf/library-content/products/"
       "fund-data/etfs/us/holdings-daily-us-en-{t}.xlsx")
SNAP_DIR = Path("data/snapshots")
HOLD_DIR = Path("data/raw/holdings")


def get_holdings(etf):
    """Download SPDR holdings. Falls back to a manually saved file."""
    path = HOLD_DIR / f"{etf}.xlsx"
    HOLD_DIR.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        r = requests.get(URL.format(t=etf.lower()),
                         headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        r.raise_for_status()
        path.write_bytes(r.content)
    df = pd.read_excel(path, skiprows=4)
    df = df[["Ticker", "Name", "Weight"]].copy()
    df["Weight"] = pd.to_numeric(df["Weight"], errors="coerce")
    df = df.dropna(subset=["Ticker", "Weight"])
    df["Ticker"] = df["Ticker"].astype(str).str.strip().str.replace(".", "-", regex=False)
    df = df[df["Ticker"].str.fullmatch(r"[A-Z0-9\-]{1,6}")]   # drops cash/footer rows
    df["etf"] = etf
    return df


def get_all_holdings():
    return pd.concat([get_holdings(e) for e in SECTORS], ignore_index=True)


def get_fundamentals(tickers, sleep=0.3):
    rows = []
    for i, t in enumerate(tickers):
        row = {"ticker": t}
        try:
            tk = yf.Ticker(t)
            info = tk.info
            row.update(
                trailing_pe=info.get("trailingPE"),
                forward_pe=info.get("forwardPE"),
                market_cap=info.get("marketCap"),
            )
            tr = tk.eps_trend   # rows: 0q,+1q,0y,+1y ; cols: current,7daysAgo,...
            for per in ["0y", "+1y"]:
                if per in tr.index:
                    cur, ago = tr.loc[per, "current"], tr.loc[per, "90daysAgo"]
                    if pd.notna(cur) and pd.notna(ago) and ago != 0:
                        row[f"rev90_{per}"] = cur / abs(ago) - (1 if ago > 0 else -1)
        except Exception as e:
            row["error"] = str(e)[:80]
        rows.append(row)
        if i % 25 == 0:
            print(f"{i}/{len(tickers)}")
        time.sleep(sleep)
    return pd.DataFrame(rows)


def run_snapshot():
    SNAP_DIR.mkdir(parents=True, exist_ok=True)
    hold = get_all_holdings()
    fund = get_fundamentals(hold["Ticker"].unique().tolist())
    out = hold.merge(fund, left_on="Ticker", right_on="ticker", how="left")
    stamp = dt.date.today().isoformat()
    out.to_csv(SNAP_DIR / f"fundamentals_{stamp}.csv", index=False)
    print("saved", stamp, len(out), "rows")


if __name__ == "__main__":
    run_snapshot()