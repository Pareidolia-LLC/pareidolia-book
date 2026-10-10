# -*- coding: utf-8 -*-
"""The annual after-action: the year's own cards, aggregated.

Written for the first anniversary of partnership trading — the book opened on
Oct 16, 2025 — and intended to run once a year on that date, alongside the
week's card rather than instead of it.

It deliberately invents no new rubric. The year is scored on the same five axes
as every weekly card, so the annual grade can be set beside any week of the
record and read the same way. Four of the five are simply the mean of what the
weeks themselves scored: they are process measures, and averaging a process
measure over a year is a meaningful thing to do.

**Performance is the exception.** A year's return is what compounded, not what
the weeks averaged — a book can post a positive mean weekly score and still
finish the year down, because losses compound differently from gains. So
Performance is scored on the figure the curve actually reports from inception
to the anniversary.

The weights change, and that is the only departure. A week is allowed to be
dominated by its return (40 of 100); a year is not. Over twelve months the
question is whether the book was run well, so Risk craft is lifted to equal
Wheel execution and Performance is cut to 30:

    weekly   perf 40  wheel 25  risk 20  liq 10  sleeve  5
    annual   perf 30  wheel 25  risk 25  liq 10  sleeve 10

Beneath the grade sits a `panel` of year-only facts, carried unscored: the
things a single week cannot show — the grade spread, how many weeks finished
green, the depth of the drawdown and whether it was recovered, and which of the
three lines actually made and lost the money.

Usage:
    python annual_stats.py [--write] [--through YYYYMMDD]
"""
import json, io, os, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data.json")

# the same axes as the weekly card, re-weighted for a year
WEIGHTS = {"perf": 30, "wheel": 25, "risk": 25, "liq": 10, "sleeve": 10}
LABEL = {"perf": "Performance", "wheel": "Wheel execution", "risk": "Risk craft",
         "liq": "Liquidity", "sleeve": "Event sleeve"}
LETTERS = [(85, "A"), (80, "A−"), (75, "B+"), (70, "B"), (65, "B−"),
           (60, "C+"), (55, "C"), (50, "C−"), (45, "D+"), (40, "D"), (35, "D−")]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def clamp(x, lo=0.0, hi=100.0):
    return max(lo, min(hi, x))


def letter(score):
    for cut, l in LETTERS:
        if score >= cut:
            return l
    return "F"


def long_date(ymd):
    s = ymd.replace("-", "")
    return "%s %d, %s" % (MONTHS[int(s[4:6]) - 1], int(s[6:8]), s[:4])


def pct(x, places=2):
    return ("%+." + str(places) + "f%%") % x


def drawdown(cps, dates):
    """Deepest peak-to-trough on the inception curve, and whether it recovered."""
    idx = [1.0 + c for c in cps]
    run_max, hi_date = idx[0], dates[0]
    dd, dd_from, dd_to = 0.0, dates[0], dates[0]
    for i, v in enumerate(idx):
        if v > run_max:
            run_max, hi_date = v, dates[i]
        draw = v / run_max - 1.0
        if draw < dd:
            dd, dd_from, dd_to = draw, hi_date, dates[i]
    peak = max(idx)
    return dd * 100, dd_from, dd_to, (idx[-1] / peak - 1.0) * 100


def main():
    args = sys.argv[1:]
    write = "--write" in args
    through = None
    if "--through" in args:
        through = args[args.index("--through") + 1]

    d = json.load(io.open(DATA, encoding="utf-8"))
    cps, dates = d["curve"]["cps"], d["curve"]["dates"]
    if through:
        n = max(i for i, x in enumerate(dates) if x <= through) + 1
        cps, dates = cps[:n], dates[:n]
    reports = d["reports"]

    # ---- the four process axes: the mean of what the weeks scored
    acc = collections.defaultdict(list)
    for r in reports:
        for c in r.get("components", []):
            for k, lbl in LABEL.items():
                if c["k"] == lbl:
                    acc[k].append(c["score"])
    parts = {k: sum(v) / len(v) for k, v in acc.items() if v}

    # ---- performance: what actually compounded, not what the weeks averaged.
    # +25% over a year scores 100 and -25% scores 0, so a flat year sits at 50.
    year_ret = cps[-1] * 100.0
    parts["perf"] = clamp(50 + 2.0 * year_ret)

    w = {k: v for k, v in WEIGHTS.items() if k in parts}
    total = sum(parts[k] * w[k] for k in parts) / sum(w.values())
    g = letter(total)

    detail = {
        "perf": "Compounded from inception, not averaged from the weeks",
        "wheel": "Mean of %d weekly scores" % len(acc.get("wheel", [])),
        "risk": "Mean of %d weekly scores" % len(acc.get("risk", [])),
        "liq": "Mean of %d weekly scores" % len(acc.get("liq", [])),
        "sleeve": "Mean of the %d weeks the sleeve traded" % len(acc.get("sleeve", [])),
    }
    components = [{"k": LABEL[k], "pts": round(parts[k] * w[k] / 100, 1), "max": w[k],
                   "score": round(parts[k]), "m": detail[k]}
                  for k in ("perf", "wheel", "risk", "liq", "sleeve") if k in parts]

    # ---- the year panel: what a single week cannot show
    spread = collections.Counter(r["grade"][0] for r in reports)
    green = sum(1 for r in reports if r["weekRet"] > 0)
    best = max(reports, key=lambda r: r["weekRet"])
    worst = min(reports, key=lambda r: r["weekRet"])
    dd, dd_from, dd_to, below = drawdown(cps, dates)
    buckets = {b["name"]: b for b in d["career"]["buckets"]}
    career = {t["k"]: t["v"] for t in d["career"]["headline"]}

    panel = [
        {"k": "Weeks graded", "v": str(len(reports)),
         "m": "%d green · %d red" % (green, len(reports) - green)},
        {"k": "Return for the year", "v": pct(year_ret),
         "m": "Time-weighted, %s to %s" % (long_date(dates[0]), long_date(dates[-1]))},
        {"k": "Deepest drawdown", "v": pct(dd),
         "m": "%s to %s" % (long_date(dd_from), long_date(dd_to))},
        {"k": "Still below the peak", "v": pct(below), "m": "Distance from the high-water mark"},
        {"k": "Best week", "v": pct(best["weekRet"]), "m": best["weekLabel"].replace("Week of ", "")},
        {"k": "Worst week", "v": pct(worst["weekRet"]), "m": worst["weekLabel"].replace("Week of ", "")},
        {"k": "The engine", "v": "%.2f pf" % buckets["Covered-call premium"]["pf"],
         "m": "Covered-call premium, %d closes" % buckets["Covered-call premium"]["closes"]},
        {"k": "The shares underneath", "v": "%.2f pf" % buckets["Share legs"]["pf"],
         "m": "Share legs, %d closes — where the year was lost" % buckets["Share legs"]["closes"]},
        {"k": "The sleeve", "v": "%.2f pf" % buckets["Event contracts"]["pf"],
         "m": "Event contracts, %d closes" % buckets["Event contracts"]["closes"]},
        {"k": "Payoff ratio", "v": career.get("Payoff ratio", "—"),
         "m": "Average win ÷ average loss — the standing leak"},
    ]

    annual = {
        "label": "Year One",
        "eyebrow": "Annual after-action · one year of partnership trading",
        "window": "%s – %s" % (long_date(dates[0]), long_date(dates[-1])),
        "grade": g,
        "score": round(total, 1),
        "ret": round(year_ret, 2),
        "components": components,
        "spread": [{"g": k, "n": spread[k]} for k in sorted(spread)],
        "panel": panel,
        "note": d.get("annual", {}).get("note", ""),   # hand-written, never generated
    }

    if write:
        d["annual"] = annual
        json.dump(d, io.open(DATA, "w", encoding="utf-8", newline="\n"),
                  ensure_ascii=False, indent=2)
        print("wrote annual block: %s (%.1f) over %d weeks, %s to %s"
              % (g, total, len(reports), dates[0], dates[-1]))
        if not annual["note"]:
            print("  note is empty and is hand-written — write it before building.")
    else:
        print("ANNUAL  %s  %.1f   %s to %s" % (g, total, dates[0], dates[-1]))
        for c in components:
            print("  %-16s %5.1f / %-3d  (%3d)  %s" % (c["k"], c["pts"], c["max"], c["score"], c["m"]))
        print("  spread: " + "  ".join("%s %d" % (k, spread[k]) for k in sorted(spread)))
        for p in panel:
            print("  %-22s %-10s %s" % (p["k"], p["v"], p["m"]))


if __name__ == "__main__":
    main()
