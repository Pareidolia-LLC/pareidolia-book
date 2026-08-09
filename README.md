# Pareidolia — The Book

A static, self-updating showcase of the Pareidolia trading book: time-weighted returns, a cumulative-return curve, allocation by weight, holdings, and the weekly discipline report card. **Transparent on returns and weights; dollar balances, share counts, and dollar P&L are withheld by design.**

Served by **GitHub Pages** from `index.html` at the repo root.

## How it works

- **`data.json`** — the only file a refresh touches. Holds returns, the report card, positions, and the return curve.
- **`build.py`** — reads `data.json`, injects it into the HTML template, writes **`index.html`**. No dependencies (standard library only).
- **`index.html`** — the generated page. Do not edit by hand; it's overwritten by `build.py`.

## Manual refresh

```bash
python build.py     # after editing data.json
git add -A && git commit -m "book: refresh $(date +%F)" && git push
```

## Weekly auto-refresh (cloud routine)

Intended cadence: **Fridays 5:00 PM America/Chicago** (cron `0 23 * * 5` in UTC when CDT; `0 23` = 5 PM CDT). A cloud agent runs this prompt — **requires the brokerage MCP attached as a connector**:

> Refresh the Pareidolia book. 1) Pull the brokerage account: get_account_positions, get_account_summary, get_pa_performance_all_periods. 2) Recompute for `trading-system/book/data.json`: headline TWR returns (YTD, trailing-12M, last-7-days); the YTD `curve` (cps + dates arrays); each stock position's weight = market_value / net_liquidation (as %) and return = unrealized_pnl / (avg_price × shares) (as %), tagged `wheel` if it has short calls else `dir`; the report-card dials — Position size (fail if any name > 20% of NAV), Cash buffer (fail if cash < 10% of NAV), Event sleeve (watch if a banned name like JPUSD is active). Write a one-paragraph `note`. 3) `python build.py`. 4) `git add -A && git commit -m "book: weekly refresh" && git push`.

## data.json schema

- `asOf` (str), `curveLabel` (str)
- `returns`: `[{k,v,m}]` — v is a percentage number (e.g. -6.55)
- `reportCard`: `{grade, weekLabel, weekRet, dials:[{key,state,value,rule}], note}` — state ∈ `pass|warn|fail`
- `history`: `[{w,g,r,now?}]` — grade-trend strip, one entry per graded week (`w`=short label, `g`=letter grade, `r`=week return %). Each refresh, **append** the new week and move `now:true` to it; keep prior weeks.
- `positions`: `[{t,s,w,r}]` — s ∈ `wheel|dir|cash`; w,r are percentages; r=null hides it from the ledger
- `curve`: `{cps:[fractions], dates:["YYYYMMDD"]}` — parallel arrays
