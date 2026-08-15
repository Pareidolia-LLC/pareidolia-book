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

> Refresh the Pareidolia book. 1) Pull the brokerage account: get_account_positions, get_account_summary, get_account_balances, get_pa_performance_all_periods. **Before using any of it, run the settlement check below** — if it fails, re-pull after the close and use the second pull. 2) Recompute for `trading-system/book/data.json`: headline TWR returns (YTD, trailing-12M, last-7-days); the YTD `curve` (cps + dates arrays); each stock position's weight = market_value / net_liquidation (as %) and return = unrealized_pnl / (avg_price × shares) (as %), tagged `wheel` if it has short calls else `dir`; the report-card dials — Position size (fail if any name > 20% of NAV), Cash buffer (fail if cash < 10% of NAV), Event sleeve (watch if a banned name like JPUSD is active). Write a one-paragraph `note`. 3) Career stats: pull get_account_trades for YEAR_TO_DATE plus every completed quarter back to inception (Oct 2025), save the dumps to `trading-system/data/trades_*.json`, run `python career_stats.py <files>`, and update the `career` block (headline/buckets stay script-generated; hand-polish `insights` — keep them dollar-free). 4) `python build.py`. 5) `git add -A && git commit -m "book: weekly refresh" && git push`.

## Settlement check — run this before writing any figures

A pull taken while a Friday expiry is still settling reports the **pre-assignment** book: shares that have already been called away still show as held, and the cash from the strike hasn't landed. This happened on 2026-08-14 — the first pull read cash at 0.7% and gross at 1.09×, when NU had actually been assigned and the true figures were 16.7% and 0.92×. It flipped a report-card dial and the grade.

Three checks, all cheap:

1. **Reconcile cash.** `net_liquidation − Σ(position market_value)` should land within a few dollars of `total_cash_value`. Cross-check `total_cash_value` (summary) against `cash_balance` (balances) — they must agree.
2. **Scan for expiries dated today or earlier.** Any short call in the position list whose expiry has passed should already be gone. If one is still listed, the pull predates settlement.
3. **Check the trade feed.** `get_account_trades` with `DAYS_7` — an assignment appears as a SELL of the shares at exactly the strike, paired with a BUY of the short call at 0, both timestamped just after the close (UTC date is the *following* day).

If any check fails, re-pull after the close. Assignments book at `realized_pnl: 0` in the trade feed, so they do **not** move the career ledger — only positions, cash, leverage, and the cash-buffer dial.

## data.json schema

- `asOf` (str), `curveLabel` (str)
- `returns`: `[{k,v,m}]` — v is a percentage number (e.g. -6.55)
- `reports`: `[{w, weekLabel, grade, weekRet, dials:[{key,state,value,rule}], note, now?}]` — full weekly report cards, oldest→newest; state ∈ `pass|warn|fail`. Both the clickable grade-history strip and the card view render from this. Each refresh, **append** the new week's full card and move `now:true` to it; keep prior weeks. The card defaults to the `now` entry; clicking a chip shows that week.
- `career`: cumulative closed-trade record shown on the Performance tab under the weekly card. **Dollar-free by design — rates, ratios, counts only.** `sinceLabel`/`asOfLabel` (strs); `headline`: `[{k,v,m}]` stat tiles (v is a preformatted string); `buckets`: `[{name,tag,tone,win,pf,closes,note}]` — tone ∈ `up|warn|down` colors the card; `insights`: `[str]` — the "Between the Report Cards" observations. Regenerate with `python career_stats.py <trade dumps>` each refresh.
- `positions`: `[{t,s,w,r}]` — s ∈ `wheel|dir|cash`; w,r are percentages; r=null hides it from the ledger
- `curve`: `{cps:[fractions], dates:["YYYYMMDD"]}` — parallel arrays
