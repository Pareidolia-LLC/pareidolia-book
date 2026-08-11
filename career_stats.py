# -*- coding: utf-8 -*-
"""Career Trading Stats for the Pareidolia book.

Reads one or more IBKR trade dumps ({"trades":[...]}) — pass file paths as args,
or set TRADES_GLOB below — dedupes by trade_id across the whole account history,
and prints a `career` JSON block to paste into data.json.

Everything it emits is dimensionless (rates, ratios, counts): NO dollar figures,
matching the book's confidentiality model. Realized closed-trade record only.

Usage:
    python career_stats.py path\\to\\trades_ytd.json path\\to\\trades_q4_2025.json
"""
import json, sys, glob, os
from collections import defaultdict

# Fallback if no args: adjust to wherever the weekly full-history pulls land.
TRADES_GLOB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "trades_*.json")

# Forecast/event contracts trade as FOP (futures options) on FORECASTX.
EVENT_SEC = {"FOP"}

def load(paths):
    seen = {}
    for p in paths:
        for t in json.load(open(p, encoding="utf-8")).get("trades", []):
            seen[t["trade_id"]] = t
    return list(seen.values())

def bucket(closers, pred):
    c = [t for t in closers if pred(t)]
    if not c:
        return None
    w = [t for t in c if t["realized_pnl"] > 0]
    gp = sum(t["realized_pnl"] for t in w)
    gl = sum(t["realized_pnl"] for t in c if t["realized_pnl"] < 0)
    pf = (gp / abs(gl)) if gl else float("inf")
    return {"closes": len(c), "win": round(len(w) / len(c) * 100, 1), "pf": round(pf, 2)}

def main():
    paths = sys.argv[1:] or glob.glob(TRADES_GLOB)
    if not paths:
        sys.exit("No trade files. Pass paths as args or populate " + TRADES_GLOB)
    tr = load(paths)
    tr.sort(key=lambda x: x["trade_time"])
    closers = [t for t in tr if abs(t["realized_pnl"]) > 1e-9]
    wins = [t for t in closers if t["realized_pnl"] > 0]
    losses = [t for t in closers if t["realized_pnl"] < 0]
    gp = sum(t["realized_pnl"] for t in wins)
    gl = sum(t["realized_pnl"] for t in losses)
    avg_w = gp / len(wins)
    avg_l = gl / len(losses)

    # monthly realized -> hit rate + current streak
    m = defaultdict(float)
    for t in closers:
        m[t["trade_time"][:7]] += t["realized_pnl"]
    months = sorted(m)
    green = sum(1 for k in months if m[k] > 0)
    streak = 0
    for k in reversed(months):
        s = 1 if m[k] > 0 else -1
        if streak == 0 or (streak > 0) == (s > 0):
            streak += s
        else:
            break

    opt = bucket(closers, lambda t: t["sec_type"] == "OPT")   # covered-call premium
    stk = bucket(closers, lambda t: t["sec_type"] == "STK")   # share legs
    fop = bucket(closers, lambda t: t["sec_type"] in EVENT_SEC)  # event contracts

    span0, span1 = tr[0]["trade_time"][:10], tr[-1]["trade_time"][:10]
    asof = span1
    career = {
        "asOf": asof,
        "since": span0,
        "headline": [
            {"k": "Closed trades", "v": f"{len(closers):,}", "m": "positions opened, closed & booked"},
            {"k": "Win rate", "v": f"{len(wins)/len(closers)*100:.1f}%", "m": f"{len(wins):,} won · {len(losses):,} lost"},
            {"k": "Profit factor", "v": f"{gp/abs(gl):.2f}", "m": "gross wins ÷ gross losses"},
            {"k": "Payoff ratio", "v": f"{avg_w/abs(avg_l):.2f}", "m": "avg win ÷ avg loss"},
            {"k": "Names traded", "v": f"{len(set(t['symbol'] for t in tr))}", "m": "distinct symbols"},
            {"k": "Profitable months", "v": f"{green} / {len(months)}", "m": "by realized P&L"},
        ],
        "buckets": [
            {"name": "Covered-call premium", "tag": "options", "win": opt["win"], "pf": opt["pf"], "closes": opt["closes"], "tone": "up", "note": "The engine — premium capture, managed and rolled."},
            {"name": "Share legs", "tag": "equity", "win": stk["win"], "pf": stk["pf"], "closes": stk["closes"], "tone": "down", "note": "Where losses cluster — a few oversized names."},
            {"name": "Event contracts", "tag": "forecast", "win": fop["win"], "pf": fop["pf"], "closes": fop["closes"], "tone": "warn", "note": "High-volume churn; near break-even, negative net of costs."},
        ],
        "insights": [
            f"Loss asymmetry: the average loss is {abs(avg_l)/avg_w:.1f}× the average win — selection is fine, loss-sizing is the leak.",
            f"Activity concentration: event contracts are {fop['closes']/len(closers)*100:.0f}% of all closes but sit near break-even — a lot of motion, little contribution.",
            f"The engine works: covered-call premium wins {opt['win']:.0f}% of the time at a {opt['pf']:.1f} profit factor — the rest of the book is management around it.",
            "Consistency: {g} of {n} months green on realized P&L; {run}.".format(
                g=green, n=len(months),
                run=("the current run is +%d month%s green" % (streak, "s" if streak != 1 else "")) if streak > 0
                    else ("the last %d month%s ran red" % (-streak, "s" if streak != -1 else ""))),
        ],
    }
    print(json.dumps(career, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
