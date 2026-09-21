# -*- coding: utf-8 -*-
"""The weekly grade, scored rather than deducted.

Replaces the old rubric, where any single breach dragged the letter down and a
week in which the wheel worked across five names could still read as a D. This
one scores five components out of 100, weights them, and maps the total to a
letter. A breach costs points in its own component; it no longer decides the
grade on its own.

    Performance      40   the week's return
    Wheel execution  25   premium captured, calls written and rolled
    Risk craft       20   concentration and its direction, margin, adds below carry
    Liquidity        10   cash inside the 2-20% band at week end
    Event sleeve      5   what the sleeve returned, and whether it was sized sanely

Concentration is a band, not a cliff: a top name under 25% of net asset value
is clean, 25-35% is a watch, above 35% is a breach - and a covered name carries
5 points of extra room on each edge, because stock with calls written against
it is not the same risk as naked concentration. Direction counts too: a heavy
name being trimmed scores better than the same weight being added to.

The card also carries three lists - what worked, what to watch, what to do next
week - generated from the same component facts, so the reasoning is visible
rather than implied by a letter.

Usage:
    python grade_model.py [--write] [trade dumps...]
"""
import json, io, os, sys, glob, re
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data.json")
NAV = os.path.join(HERE, "..", "data", "nav_series.json")
CARDS = os.path.join(HERE, "..", "data", "weekly_cards.json")
TRADES_GLOB = os.path.join(HERE, "..", "data", "trades_*.json")
MONTHS = {m: i + 1 for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}

WEIGHTS = {"perf": 40, "wheel": 25, "risk": 20, "liq": 10, "sleeve": 5}
LETTERS = [(85, "A"), (80, "A−"), (75, "B+"), (70, "B"), (65, "B−"),
           (60, "C+"), (55, "C"), (50, "C−"), (45, "D+"), (40, "D"), (35, "D−")]

EVENT_SEC, EVENT_EXCH = {"FOP"}, {"FORECASTX", "KALSHI"}


def is_event(t):
    return t.get("sec_type") in EVENT_SEC or t.get("exchange") in EVENT_EXCH


def clamp(x, lo=0.0, hi=100.0):
    return max(lo, min(hi, x))


def letter(score):
    for cut, l in LETTERS:
        if score >= cut:
            return l
    return "F"


def cap_for(week_ret):
    """A hard week cannot read as a good one, however well the book was run.

    The rubric is holistic on purpose, but process credit has a ceiling: a week
    that loses more than 5% of the book caps at C-, and one that loses more
    than 10% caps at D+. Below those lines the letter reports the damage.
    """
    if week_ret <= -10:
        return 49.9
    if week_ret <= -5:
        return 54.9
    return None


def week_end_iso(report):
    """'Week of Sep 14 - Sep 18, 2026' -> 2026-09-18"""
    tail = report["weekLabel"].split("–")[-1].strip()
    m = re.match(r"([A-Za-z]{3})\s+(\d+),\s+(\d{4})", tail)
    if not m:
        raise SystemExit("cannot read week end from %r" % report["weekLabel"])
    return "%s-%02d-%02d" % (m.group(3), MONTHS[m.group(1)], int(m.group(2)))


def num(s):
    m = re.search(r"(\d+(?:\.\d+)?)", s or "")
    return float(m.group(1)) if m else None


def parse_dials(r):
    """Pull the facts the score needs out of the three dials."""
    top_name, top_w, cash, on_margin = None, None, None, False
    sleeve_pct, sleeve_pf, sleeve_stake, bound = None, None, None, None
    for d in r["dials"]:
        k, v, rule = d["key"], d["value"], d["rule"]
        if "Position size" in k:
            m = re.match(r"([A-Z.]+)\s", v)
            top_name = m.group(1) if m else None
            top_w = num(v)
        elif "Cash buffer" in k:
            if "margin" in v or "borrowed" in rule:
                on_margin = True
            cash = num(v)
            # reconstructed weeks state cash as a bound, not a figure
            bound = "upper" if v.startswith("≤") else ("lower" if v.startswith("≥") else None)
        elif "Event sleeve" in k:
            m = re.search(r"pf ([\d.]+)", v)
            sleeve_pf = float(m.group(1)) if m else (float("inf") if "∞" in v else None)
            m = re.search(r"net ([+−-][\d.]+)% of NAV", rule)
            if m:
                sleeve_pct = float(m.group(1).replace("−", "-").replace("+", ""))
            m = re.search(r"at ([\d.]+)% of NAV", rule)
            sleeve_stake = float(m.group(1)) if m else None
    return top_name, top_w, cash, on_margin, sleeve_pct, sleeve_pf, sleeve_stake, bound


def premium_by_week(paths, ends):
    """Covered-call premium realized, and calls written, per week ending."""
    seen = {}
    for p in paths:
        for t in json.load(io.open(p, encoding="utf-8")).get("trades", []):
            seen[t["trade_id"]] = t
    ends = sorted(ends)
    agg = defaultdict(lambda: {"pnl": 0.0, "written": 0, "names": set()})
    for t in seen.values():
        if t.get("sec_type") != "OPT" or is_event(t):
            continue
        day = t["trade_time"][:10]
        wk = next((e for e in ends if day <= e), None)
        if wk is None:
            continue
        a = agg[wk]
        a["pnl"] += t.get("realized_pnl") or 0.0
        if t["side"] == "SELL" and t["price"] > 0:
            a["written"] += 1
            a["names"].add(t["symbol"])
    return agg


def main():
    args = sys.argv[1:]
    write = "--write" in args
    paths = [a for a in args if not a.startswith("--")] or sorted(glob.glob(TRADES_GLOB))

    d = json.load(io.open(DATA, encoding="utf-8"))
    navby = {}
    if os.path.exists(NAV):
        n = json.load(io.open(NAV, encoding="utf-8"))
        navby = dict(zip(n["dates"], n["nav"]))
    extras = {}
    if os.path.exists(CARDS):
        for c in json.load(io.open(CARDS, encoding="utf-8")):
            extras[c["end"]] = c

    reports = d["reports"]
    ends = [week_end_iso(r) for r in reports]
    prem = premium_by_week(paths, ends)

    rows, prev_w = [], None
    for r, end in zip(reports, ends):
        top_name, top_w, cash, margin, sl_pct, sl_pf, sl_stake, bound = parse_dials(r)
        x = extras.get(end, {})
        nav = navby.get(end.replace("-", ""))
        p = prem.get(end, {"pnl": 0.0, "written": 0, "names": set()})
        prem_pct = (p["pnl"] / nav * 100) if nav else None
        # The covered-name allowance is only claimable where the holding is known to
        # carry calls, which the position list can only answer for the current week.
        # Historical weeks are scored on the naked band rather than assumed covered.
        covered = bool(r.get("now")) and top_name in {
            q["t"] for q in d.get("positions", []) if q.get("s") == "wheel"}

        # ---- performance: the week's return, on a scale where +3% is a strong week
        perf = clamp(50 + 8.0 * r["weekRet"])

        # ---- wheel execution: premium kept, and whether calls went back out
        if prem_pct is None:
            wheel = 50.0
        else:
            wheel = clamp(50 + 25.0 * prem_pct)
        if p["written"]:
            wheel = clamp(wheel + 10)
        elif prem_pct is not None and abs(prem_pct) < 0.01:
            wheel = clamp(wheel - 10)        # engine idle for a whole week

        # ---- risk craft: the band, its direction, margin, adds below carry
        risk, room = 100.0, 5.0 if covered else 0.0
        if top_w is not None:
            if top_w > 35 + room:
                risk -= 35 + min(20, (top_w - (35 + room)) * 0.5)
            elif top_w > 25 + room:
                risk -= 15
        if top_w is not None and prev_w is not None:
            if top_w <= prev_w - 2:
                risk += 8
            elif top_w >= prev_w + 2:
                risk -= 8
        if margin:
            risk -= 20
        if x.get("addlow"):
            risk -= 10
        risk = clamp(risk)

        # ---- liquidity: 2-20% is the band; idle cash is a mild fault, margin is not
        if margin:
            liq = 0.0
        elif cash is None:
            liq = 50.0
        elif bound == "upper":
            # "at most 3.9%" cannot be told apart from "0.4%", so it takes partial credit
            liq = 70.0 if cash >= 2 else 60.0
        elif bound == "lower":
            liq = 75.0 if cash > 20 else 100.0
        elif 2 <= cash <= 20:
            liq = 100.0
        elif cash < 2:
            liq = 60.0
        elif cash <= 35:
            liq = 75.0
        else:
            liq = 60.0

        # ---- event sleeve: what it returned, and whether it was sized sanely
        if sl_pct is not None:
            sleeve = clamp(50 + 50.0 * sl_pct * 2)
        elif sl_pf is not None:
            sleeve = 100.0 if sl_pf == float("inf") else clamp(50 + 50.0 * (sl_pf - 1))
        else:
            sleeve = None
        if sleeve is not None and sl_stake and sl_stake > 3:
            sleeve = clamp(sleeve - 15)

        parts = {"perf": perf, "wheel": wheel, "risk": risk, "liq": liq}
        w = dict(WEIGHTS)
        if sleeve is None:
            w.pop("sleeve")
        else:
            parts["sleeve"] = sleeve
        total = sum(parts[k] * w[k] for k in parts) / sum(w.values())
        cap = cap_for(r["weekRet"])
        if cap is not None:
            total = min(total, cap)
        rows.append((r, end, parts, w, total, dict(top_name=top_name, top_w=top_w, cash=cash,
                                                   margin=margin, prem_pct=prem_pct,
                                                   written=p["written"], names=sorted(p["names"]),
                                                   covered=covered, prev_w=prev_w, sl_pct=sl_pct,
                                                   sl_stake=sl_stake, bound=bound,
                                                   addlow=bool(x.get("addlow")))))
        prev_w = top_w

    # ---------------------------------------------------------------- emit
    LABEL = {"perf": "Performance", "wheel": "Wheel execution", "risk": "Risk craft",
             "liq": "Liquidity", "sleeve": "Event sleeve"}
    changed = []
    for r, end, parts, w, total, f in rows:
        g = letter(total)
        comp = [{"k": LABEL[k], "pts": round(parts[k] * w[k] / 100, 1), "max": w[k],
                 "score": round(parts[k])} for k in ("perf", "wheel", "risk", "liq", "sleeve")
                if k in parts]
        wins, watch, nxt = [], [], []

        if r["weekRet"] > 0:
            wins.append("Book up %.2f%% on the week." % r["weekRet"])
        else:
            watch.append("Book down %.2f%% on the week." % abs(r["weekRet"]))
        if f["prem_pct"] and f["prem_pct"] > 0.05:
            wins.append("Covered-call premium added %.2f%% of net asset value%s." % (
                f["prem_pct"], (" across %d name%s" % (len(f["names"]), "" if len(f["names"]) == 1 else "s"))
                if f["names"] else ""))
        if f["written"]:
            wins.append("Calls written or rolled on %d contracts%s." % (
                f["written"], (" · " + ", ".join(f["names"][:5])) if f["names"] else ""))
        elif f["prem_pct"] is not None and abs(f["prem_pct"]) < 0.01:
            watch.append("The engine sat idle: no premium written all week.")
            nxt.append("Write calls on the uncovered names - premium is the one line with a measured edge.")
        if f["top_w"] is not None:
            limit = 25 + (5 if f["covered"] else 0)
            hard = 35 + (5 if f["covered"] else 0)
            if f["top_w"] > hard:
                watch.append("%s at %.1f%% of net asset value, past the %d%% line." % (f["top_name"], f["top_w"], hard))
                nxt.append("Bring %s under %d%% before adding anywhere else." % (f["top_name"], hard))
            elif f["top_w"] > limit:
                watch.append("%s at %.1f%% of net asset value, inside the %d-%d%% watch band." % (
                    f["top_name"], f["top_w"], limit, hard))
            else:
                wins.append("Top name %s at %.1f%%, inside the %d%% line." % (f["top_name"], f["top_w"], limit))
            if f["prev_w"] is not None and f["top_w"] <= f["prev_w"] - 2:
                wins.append("Concentration coming down, %.1f%% to %.1f%%." % (f["prev_w"], f["top_w"]))
            elif f["prev_w"] is not None and f["top_w"] >= f["prev_w"] + 2:
                watch.append("Concentration rising, %.1f%% to %.1f%%." % (f["prev_w"], f["top_w"]))
        if f["margin"]:
            watch.append("Book carried borrowed money.")
            nxt.append("Come off margin before taking any new risk.")
        elif f["cash"] is not None and f["bound"] is None:
            if 2 <= f["cash"] <= 20:
                wins.append("Cash at %.1f%%, inside the 2-20%% band." % f["cash"])
            elif f["cash"] < 2:
                watch.append("Cash at %.1f%%, under the 2%% floor - nothing to deploy." % f["cash"])
                nxt.append("Leave a little dry powder at the close; 2% is the floor, not a target.")
            else:
                watch.append("Cash at %.1f%%, above the 20%% band - capital sitting idle." % f["cash"])
        if f["addlow"]:
            watch.append("Added to a position below its carry.")
        if f["sl_pct"] is not None:
            (wins if f["sl_pct"] > 0 else watch).append(
                "Event sleeve %s%.2f%% of net asset value%s." % (
                    "+" if f["sl_pct"] > 0 else "−", abs(f["sl_pct"]),
                    (" on %.1f%% staked" % f["sl_stake"]) if f["sl_stake"] else ""))
        if f["sl_stake"] and f["sl_stake"] > 3:
            nxt.append("Size the sleeve under 3% of net asset value a week.")

        if write:
            # the two hard dials move to the new bands: a verdict, then the detail
            # clauses the card already carried
            lim = 25 + (5 if f["covered"] else 0)
            hrd = 35 + (5 if f["covered"] else 0)
            if f["top_w"] is not None:
                st = "pass" if f["top_w"] <= lim else ("warn" if f["top_w"] <= hrd else "fail")
                verdict = ("Inside the %d%% band" % lim if st == "pass" else
                           "In the %d-%d%% watch band" % (lim, hrd) if st == "warn" else
                           "Past the %d%% line" % hrd)
                tail = r["dials"][0]["rule"].split(" · ", 1)
                r["dials"][0]["state"] = st
                r["dials"][0]["rule"] = verdict + (" · " + tail[1] if len(tail) > 1 else "")
            if f["margin"]:
                st, verdict = "fail", "On margin"
            elif f["cash"] is None:
                st, verdict = "warn", "Cash not recoverable for this week"
            elif 2 <= f["cash"] <= 20:
                st, verdict = "pass", "Inside the 2-20% band"
            elif f["cash"] < 2:
                st, verdict = "warn", "Under the 2% floor"
            else:
                st, verdict = "warn", "Above the 20% band"
            tail = r["dials"][1]["rule"].split(" · ", 1)
            r["dials"][1]["state"] = st
            r["dials"][1]["rule"] = verdict + (" · " + tail[1] if len(tail) > 1 else "")
            if r["grade"] != g:
                changed.append("  %-7s %-3s -> %-3s  (%.1f)" % (r["w"], r["grade"], g, total))
            r["grade"] = g
            r["score"] = round(total, 1)
            r["components"] = comp
            r["wins"], r["watch"], r["next"] = wins[:4], watch[:4], nxt[:3]

    if write:
        json.dump(d, io.open(DATA, "w", encoding="utf-8", newline="\n"),
                  ensure_ascii=False, indent=2)
        print("rescored %d cards on the weighted rubric" % len(rows))
        print("\n".join(changed) if changed else "  (no letters moved)")
        dist = defaultdict(int)
        for r, *_ in rows:
            dist[r["grade"][0]] += 1
        print("  spread: " + "  ".join("%s %d" % (k, dist[k]) for k in sorted(dist)))
    else:
        for r, end, parts, w, total, f in rows:
            print("%-7s %-3s %5.1f  %s" % (r["w"], letter(total), total,
                                           " ".join("%s %3.0f" % (k, parts[k]) for k in parts)))


if __name__ == "__main__":
    main()
