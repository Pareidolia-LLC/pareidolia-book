# -*- coding: utf-8 -*-
"""Career Trading Stats for the Pareidolia book.

Reads one or more IBKR trade dumps ({"trades":[...]}) — pass file paths as args,
or set TRADES_GLOB below — dedupes by trade_id across the whole account history,
and emits the `career` block for data.json.

Everything it emits is dimensionless (rates, ratios, counts): NO dollar figures,
matching the book's confidentiality model. Realized closed-trade record only.

Usage:
    python career_stats.py path\\to\\trades_ytd.json path\\to\\trades_q4_2025.json
    python career_stats.py --write path\\to\\trades_ytd.json ...

`--write` merges the generated figures straight into data.json — headline tiles,
bucket win/pf/closes, and the since/asOf labels — instead of printing a block to
paste by hand. It deliberately does NOT touch `insights` or the bucket prose:
those are hand-polished. It prints what moved, and the freshly generated
insights underneath, so you can see whether the hand-written ones still hold.
"""
import json, io, sys, glob, os
from collections import defaultdict

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def month_year(iso):
    """2025-10-20 -> Oct 2025"""
    y, m, _ = iso.split("-")
    return "%s %s" % (MONTHS[int(m) - 1], y)


def long_date(iso):
    """2026-08-14 -> Aug 14, 2026"""
    y, m, d = iso.split("-")
    return "%s %d, %s" % (MONTHS[int(m) - 1], int(d), y)

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

def merge(career, last_close):
    """Fold generated figures into data.json, preserving hand-written prose."""
    d = json.load(io.open(DATA, encoding="utf-8"))
    old = d.get("career", {})
    moved = []

    # The ledger is dated by the site's own as-of, NOT by the last close, so the
    # career record and the weekly report card always carry the same date. It
    # reads as a cutoff ("figures through Aug 14") and stays true even on a week
    # that booked no closes at all — which is common, since a week can be all
    # opens. build.py refuses to build if these two dates ever drift apart.
    career["asOfLabel"] = d["asOf"]

    def note(label, before, after):
        if str(before) != str(after):
            moved.append("  %-22s %s -> %s" % (label, before, after))

    note("as of", old.get("asOfLabel"), career["asOfLabel"])
    for a, b in zip(old.get("headline", []), career["headline"]):
        note(a["k"], a["v"], b["v"])
    for a, b in zip(old.get("buckets", []), career["buckets"]):
        for f in ("win", "pf", "closes"):
            note("%s %s" % (a["name"], f), a.get(f), b[f])

    # generated figures win; hand-polished prose is preserved
    for a, b in zip(old.get("buckets", []), career["buckets"]):
        b["name"], b["tag"], b["tone"], b["note"] = a["name"], a["tag"], a["tone"], a["note"]
    career["insights"] = old.get("insights", career["insights"])

    d["career"] = career
    json.dump(d, io.open(DATA, "w", encoding="utf-8", newline="\n"),
              ensure_ascii=False, indent=2)
    print("wrote career block to data.json")
    print("  dated %s, in step with the report card" % career["asOfLabel"])
    print("  last realized close was %s%s" % (
        long_date(last_close),
        "" if long_date(last_close) == career["asOfLabel"] else " — no closes booked since"))
    print("\n".join(moved) if moved else "  (no figures moved)")


def main():
    args = sys.argv[1:]
    write = "--write" in args
    paths = [a for a in args if not a.startswith("--")] or glob.glob(TRADES_GLOB)
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

    # The career record is a *closed-trade* record, so it is dated by the last
    # realized close — not the last execution. Zero-P&L fills (assignments,
    # expiries) carry a UTC timestamp that rolls past midnight and would
    # otherwise date the ledger a day ahead of the trading session.
    span0, span1 = tr[0]["trade_time"][:10], closers[-1]["trade_time"][:10]
    career = {
        "sinceLabel": month_year(span0),
        "asOfLabel": long_date(span1),
        "headline": [
            {"k": "Closed trades", "v": f"{len(closers):,}", "m": "Positions opened, closed & booked"},
            {"k": "Win rate", "v": f"{len(wins)/len(closers)*100:.1f}%", "m": f"{len(wins):,} won · {len(losses):,} lost"},
            {"k": "Profit factor", "v": f"{gp/abs(gl):.2f}", "m": "Gross wins ÷ gross losses"},
            {"k": "Payoff ratio", "v": f"{avg_w/abs(avg_l):.2f}", "m": "Avg win ÷ avg loss"},
            {"k": "Names traded", "v": f"{len(set(t['symbol'] for t in tr))}", "m": "Distinct symbols"},
            {"k": "Profitable months", "v": f"{green} / {len(months)}", "m": "By realized P&L"},
        ],
        "buckets": [
            {"name": "Covered-call premium", "tag": "wheel", "win": opt["win"], "pf": opt["pf"], "closes": opt["closes"], "tone": "up", "note": "The engine — premium capture, managed and rolled."},
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
    if write:
        generated = career["insights"]
        merge(career, span1)
        print("\ninsights in data.json are hand-polished and were left alone;")
        print("freshly generated for comparison:")
        for s in generated:
            print("  - " + s)
    else:
        print(json.dumps(career, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
