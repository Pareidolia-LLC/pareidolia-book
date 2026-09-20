# -*- coding: utf-8 -*-
"""Best & Worst tab generator for the Pareidolia book.

Rebuilds the `record` block of data.json from the things that are already
true elsewhere: the inception curve, the weekly report cards, the career
buckets, and the raw trade dumps. It used to be assembled by hand from a
scratch file, which is why it went stale - the covered-call line still read
165 closes when the ledger had moved to 182.

Everything emitted is a rate, a ratio or a share of net asset value. No dollar
figures, in line with the rest of the site. Single-trade extremes are measured
against the account's net liquidation value **on the day the trade closed**,
which needs `../data/nav_series.json` - a file that lives outside this repo
because it is denominated in dollars.

`notes` is hand-written and is never touched.

Usage:
    python record_stats.py [--write] [trade dumps...]
"""
import json, io, os, sys, glob
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data.json")
NAV = os.path.join(HERE, "..", "data", "nav_series.json")
TRADES_GLOB = os.path.join(HERE, "..", "data", "trades_*.json")
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

EVENT_SEC = {"FOP"}
EVENT_EXCH = {"FORECASTX", "KALSHI"}


def is_event(t):
    return t.get("sec_type") in EVENT_SEC or t.get("exchange") in EVENT_EXCH


def long_date(ymd):
    """20260417 or 2026-04-17 -> Apr 17, 2026"""
    s = ymd.replace("-", "")
    return "%s %d, %s" % (MONTHS[int(s[4:6]) - 1], int(s[6:8]), s[:4])


def pct(x, places=2):
    return ("%+." + str(places) + "f%%") % x


def load_trades(paths):
    seen = {}
    for p in paths:
        for t in json.load(io.open(p, encoding="utf-8")).get("trades", []):
            seen[t["trade_id"]] = t
    return list(seen.values())


def curve_stats(curve):
    """Peak, drawdown and monthly extremes off the inception series."""
    dates, cps = curve["dates"], curve["cps"]
    idx = [1.0 + c for c in cps]

    peak_i = max(range(len(idx)), key=lambda i: idx[i])
    peak = {"v": pct(cps[peak_i] * 100), "on": long_date(dates[peak_i])}

    run_max, dd, dd_from, dd_to = idx[0], 0.0, dates[0], dates[0]
    hi_date = dates[0]
    for i, v in enumerate(idx):
        if v > run_max:
            run_max, hi_date = v, dates[i]
        draw = v / run_max - 1.0
        if draw < dd:
            dd, dd_from, dd_to = draw, hi_date, dates[i]
    drawdown = {"v": pct(dd * 100), "from": long_date(dd_from), "to": long_date(dd_to)}

    below = idx[-1] / max(idx) - 1.0

    # month ends -> compounded monthly returns
    last_of_month = {}
    for i, d in enumerate(dates):
        last_of_month[d[:6]] = i
    keys = sorted(last_of_month)
    months = []
    for n, k in enumerate(keys):
        i = last_of_month[k]
        prev = idx[last_of_month[keys[n - 1]]] if n else 1.0
        months.append((k, (idx[i] / prev - 1.0) * 100))
    best = max(months, key=lambda m: m[1])
    worst = min(months, key=lambda m: m[1])
    fmt = lambda k: "%s %s" % (MONTHS[int(k[4:6]) - 1], k[:4])
    return peak, drawdown, below * 100, (fmt(best[0]), best[1]), (fmt(worst[0]), worst[1])


def week_runs(reports):
    best = max(reports, key=lambda r: r["weekRet"])
    worst = min(reports, key=lambda r: r["weekRet"])
    green = red = bg = br = 0
    for r in reports:
        if r["weekRet"] > 0:
            green += 1; red = 0
        else:
            red += 1; green = 0
        bg, br = max(bg, green), max(br, red)
    return best, worst, bg, br


def week_end(report):
    """'Week of Sep 14 - Sep 18, 2026' -> Sep 18, 2026"""
    tail = report["weekLabel"].split("–")[-1].strip()
    return tail if "," in tail else report["w"]


def discipline(reports):
    over = sum(1 for r in reports if r["dials"][0]["state"] == "fail")
    margin = sum(1 for r in reports
                 if "margin" in r["dials"][1]["value"] or "borrowed" in r["dials"][1]["rule"])
    clean = sum(1 for r in reports
                if r["dials"][0]["state"] == "pass" and r["dials"][1]["state"] == "pass")
    return over, margin, clean, len(reports)


def main():
    args = sys.argv[1:]
    write = "--write" in args
    paths = [a for a in args if not a.startswith("--")] or sorted(glob.glob(TRADES_GLOB))
    d = json.load(io.open(DATA, encoding="utf-8"))
    nav = json.load(io.open(NAV, encoding="utf-8"))
    navby = dict(zip(nav["dates"], nav["nav"]))

    tr = load_trades(paths)
    closers = [t for t in tr if abs(t.get("realized_pnl") or 0) > 1e-9]
    gains = sum(t["realized_pnl"] for t in closers if t["realized_pnl"] > 0)
    losses = sum(-t["realized_pnl"] for t in closers if t["realized_pnl"] < 0)

    # single executions as a share of that day's net asset value
    def share(t):
        day = t["trade_time"][:10].replace("-", "")
        n = navby.get(day)
        return (t["realized_pnl"] / n * 100) if n else None

    scored = [(t, share(t)) for t in closers]
    scored = [(t, s) for t, s in scored if s is not None]
    wins = sorted([x for x in scored if x[1] > 0], key=lambda x: -x[1])[:5]
    lost = sorted([x for x in scored if x[1] < 0], key=lambda x: x[1])[:5]
    row = lambda t, s: {"t": t["symbol"], "d": long_date(t["trade_time"][:10]),
                        "s": "STK" if t["sec_type"] == "STK" else ("EVT" if is_event(t) else "OPT"),
                        "v": pct(s)}

    # per-symbol tables
    def table(rows, limit):
        agg = defaultdict(lambda: {"closes": 0, "w": 0, "g": 0.0, "l": 0.0})
        for t in rows:
            a = agg[t["symbol"]]
            a["closes"] += 1
            if t["realized_pnl"] > 0:
                a["w"] += 1; a["g"] += t["realized_pnl"]
            else:
                a["l"] += -t["realized_pnl"]
        out = []
        for sym, a in agg.items():
            pf = (a["g"] / a["l"]) if a["l"] else None
            out.append({"t": sym, "closes": a["closes"],
                        "win": round(a["w"] / a["closes"] * 100),
                        "pf": round(pf, 2) if pf is not None else None,
                        "g": round(a["g"] / gains * 100, 1) if gains else 0.0,
                        "l": round(a["l"] / losses * 100, 1) if losses else 0.0})
        out.sort(key=lambda r: -(r["g"] + r["l"]))
        return out[:limit]

    names = table([t for t in closers if not is_event(t)], 10)
    events = table([t for t in closers if is_event(t)], 6)

    reports = d["reports"]
    peak, dd, below, bestm, worstm = curve_stats(d["curve"])
    bw, ww, green_run, red_run = week_runs(reports)
    over, margin, clean, weeks = discipline(reports)
    engine = [b for b in d["career"]["buckets"] if b["name"] == "Covered-call premium"][0]

    record = {
        "accolades": [
            {"k": "Best week", "v": pct(bw["weekRet"]), "m": "Week ending " + week_end(bw)},
            {"k": "Best month", "v": pct(bestm[1]), "m": bestm[0]},
            {"k": "Peak of the record", "v": peak["v"], "m": "Cumulative, " + peak["on"]},
            {"k": "Longest green run", "v": "%d weeks" % green_run, "m": "Consecutive positive weeks"},
            {"k": "Largest single win", "v": row(*wins[0])["v"],
             "m": "%s · %s · share of NAV that day" % (wins[0][0]["symbol"], long_date(wins[0][0]["trade_time"][:10]))},
            {"k": "The engine", "v": "%.2f pf" % engine["pf"],
             "m": "Covered-call premium, %d%% of %d closes won" % (round(engine["win"]), engine["closes"])},
        ],
        "failures": [
            {"k": "Worst week", "v": pct(ww["weekRet"]), "m": "Week ending " + week_end(ww)},
            {"k": "Worst month", "v": pct(worstm[1]), "m": worstm[0]},
            {"k": "Deepest drawdown", "v": dd["v"], "m": "%s to %s" % (dd["from"], dd["to"])},
            {"k": "Longest red run", "v": "%d weeks" % red_run, "m": "Consecutive negative weeks"},
            {"k": "Largest single loss", "v": row(*lost[0])["v"],
             "m": "%s · %s · share of NAV that day" % (lost[0][0]["symbol"], long_date(lost[0][0]["trade_time"][:10]))},
            {"k": "Still below the peak", "v": pct(below), "m": "Distance from the high-water mark"},
        ],
        "discipline": [
            {"k": "Weeks over the 20% cap", "v": "%d / %d" % (over, weeks), "m": "Single-name concentration"},
            {"k": "Weeks carrying margin", "v": "%d / %d" % (margin, weeks), "m": "Stock value above net asset value"},
            {"k": "Weeks fully inside every limit", "v": "%d / %d" % (clean, weeks), "m": "Cap held and reserve intact"},
        ],
        "wins": [row(t, s) for t, s in wins],
        "losses": [row(t, s) for t, s in lost],
        "names": names,
        "events": events,
        "notes": d["record"]["notes"],          # hand-written, never regenerated
    }

    if write:
        old = d["record"]
        moved = []
        for sec in ("accolades", "failures", "discipline"):
            for a, b in zip(old[sec], record[sec]):
                if a["v"] != b["v"] or a["m"] != b["m"]:
                    moved.append("  %-32s %s -> %s" % (a["k"], a["v"], b["v"]))
        d["record"] = record
        json.dump(d, io.open(DATA, "w", encoding="utf-8", newline="\n"),
                  ensure_ascii=False, indent=2)
        print("wrote record block to data.json")
        print("\n".join(moved) if moved else "  (no tiles moved)")
        print("  names table: %d rows, events table: %d rows" % (len(names), len(events)))
    else:
        print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
