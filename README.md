# Sector Thesis

A research project that scores the 11 US GICS sectors using market data, macro sensitivity, valuation and analyst estimate revisions, with sentiment, geospatial data and an ML ranking model planned. The end product is a written report with theses on selected sectors.

**Status:** Stages 1-4 complete (data, baseline scorecard, valuation and revisions). Sentiment, geospatial, ML ranking and report writing are in progress.

## Scope

- Universe: 11 US sectors via the SPDR Select Sector ETFs (XLK, XLF, XLE, XLV, XLY, XLP, XLI, XLB, XLU, XLRE, XLC), benchmarked against SPY
- Horizon: 12 months
- Deliverable: a research report with theses (claim, drivers, evidence, valuation, risks, signposts, implementation)

## Methodology

Each sector gets a cross-sectional z-score on several blocks. A z-score of +1 means "one standard deviation above the average of the other sectors", not "strong in absolute terms".

| Block | Construction |
|---|---|
| Momentum | Relative strength vs SPY over 3m, 6m and 12m (12m skips the latest month), z-scored and averaged |
| Low risk | Realized volatility and max drawdown over the last 12 months (lower is better) |
| Macro fit | 3-year regression of weekly sector excess returns on changes in the yield curve, HY spread, USD and 10Y yield, combined with the standardized last 13 weeks of macro moves |
| Revisions | Change in consensus EPS estimates over 90 days (current and next fiscal year), aggregated from constituent stocks by index weight |
| Cheapness | Forward earnings yield (1/forward P/E), weight-averaged across constituents. Shown next to the composite but **not** included in it (see limitations) |

`composite_v2` is the equal-weighted average of momentum, low risk, macro fit and revisions.

### Data sources

- Prices: Yahoo Finance via `yfinance`
- Macro: FRED via `fredapi`
- Holdings and weights: SSGA (SPDR) daily holdings files
- Fundamentals and EPS trends: `yfinance`

## Repo structure

```
src/
  data.py          # prices and macro download
  valuation.py     # holdings + fundamentals + EPS-trend snapshot
notebooks/
  01_scorecard.ipynb   # momentum, risk, macro fit, composite
  02_valuation.ipynb   # valuation, revisions, scorecard v2
data/
  raw/             # downloaded data (git-ignored)
  processed/       # scorecards (git-ignored)
  snapshots/       # dated fundamentals snapshots (committed, irreplaceable history)
figures/           # charts used in the report
reports/           # sector theses (markdown)
```

## Reproduce

```bash
git clone https://github.com/YOUR_USERNAME/sector-thesis.git
cd sector-thesis
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# add your free FRED key (https://fred.stlouisfed.org/docs/api/api_key.html)
echo "FRED_API_KEY=your_key_here" > .env

python -m src.data                 # prices + macro -> data/raw/
python -m src.valuation            # holdings + fundamentals snapshot -> data/snapshots/
```

Then run the notebooks in order: `01_scorecard.ipynb`, then `02_valuation.ipynb`.

The valuation snapshot takes 15-30 minutes. If the SPDR download is blocked, save each ETF's holdings xlsx manually as `data/raw/holdings/<TICKER>.xlsx`.

### Weekly snapshot

Free sources have no history of sector valuations or estimate revisions, so this project builds its own. Re-run `python -m src.valuation` about once a week, on the same day, and commit the new file in `data/snapshots/`.

## Latest results

Snapshot date: 2026-10-04. See `figures/scorecard_v2.png`.

| Rank | Sector | composite_v2 |
|---|---|---|
| 1 | Energy | 1.11 |
| 2 | Health Care | 0.42 |
| 3 | Consumer Staples | 0.38 |
| ... | ... | ... |
| 11 | Consumer Discretionary | -0.61 |

Only the extremes are informative. The middle sectors are bunched within about 0.5 of zero and would reshuffle under different weights.

## Limitations

- **Small cross-section:** 11 sectors, so z-scores are sensitive to outliers
- **Equal weights** are a judgment call, not optimized
- **Overlap:** momentum and revisions are correlated, so the composite partly double-counts one idea
- **Valuation:** forward earnings yields are averaged and inverted, so implied P/Es differ from vendor headline figures. Compare sectors with each other, not against published numbers. Cheapness is excluded from the composite because it largely reflects permanent sector premiums
- **P/E does not apply well to Real Estate (use P/FFO) or Financials (use P/B)**
- **Revisions** are a single 90-day window per snapshot, clipped at ±50% per stock, and dominated by the largest holdings
- **Macro betas** from weekly data are noisy and assume recent macro direction persists. Treat them as a regime-fit indicator, not a forecast
- **No backtest yet:** the scorecard is descriptive. Predictive power is tested in the ML stage with walk-forward validation

## Roadmap

- [x] Stage 1-2: repo and market/macro data pipeline
- [x] Stage 3: baseline scorecard
- [x] Stage 4: valuation and EPS revisions
- [ ] Stage 5: sentiment (Google Trends, news tone, filings)
- [ ] Stage 6: geospatial data for 2-3 sectors
- [ ] Stage 7: LightGBM ranking model, walk-forward validation, SHAP
- [ ] Stage 8: sector theses in `reports/`

## Disclaimer

This is a research and educational project, not investment advice.