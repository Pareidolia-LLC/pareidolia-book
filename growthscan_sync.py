# -*- coding: utf-8 -*-
"""Pull the Quality Growth Scanner's latest run into the book repo.

The scanner lives at ../../growth-scanner/ which is OUTSIDE this repo, so its
output has to be copied in for the site to be reproducible from a fresh clone.
This trims the run to the fields the page renders and writes book/growthscan.json
for build.py to inline.

Run the scanner first, then this, then build.py:
    cd ../../growth-scanner && python scan.py --no-open
    cd - && python growthscan_sync.py && python build.py

The site publishes the compounder profile. Pass --profile emerging to the
scanner and re-sync if that is what should be on the page instead.
"""
import json, os, shutil, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "..", "growth-scanner", "data.json"))
OUT = os.path.join(HERE, "growthscan.json")

# Only what the page draws. `detail` is dropped - it is the per-component score
# arithmetic behind every pillar, worth ~250KB across the roster, and the
# scanner's own dashboard.html is where that belongs.
KEEP = ["ticker", "name", "sector", "industry", "price", "mcap", "score", "rank",
        "revGrowth", "revCagr3y", "epsCagr3y", "fcfCagr3y", "revYoyQ",
        "grossMargin", "opMargin", "opMarginDelta", "roe", "roic", "incRoic",
        "fcfMargin", "fcfConversion", "fcfYield", "currentRatio", "quickRatio",
        "cashRatio", "netDebtEbitda", "interestCover", "de", "runwayYears",
        "reinvestRate", "shareChange3y", "evEbitda", "evFcf", "evs", "forwardPe",
        "peg", "instHeld", "analysts", "ruleOf40", "flags", "pillars"]
INSIDER_KEEP = ["level", "buyers", "buyValue", "lastBuy", "pctOfCap"]


def main():
    if not os.path.exists(SRC):
        sys.exit("no scanner output at %s - run scan.py in growth-scanner first" % SRC)

    d = json.load(open(SRC, encoding="utf-8"))
    rows = d.get("rows") or []
    if not rows:
        sys.exit("scanner output has no rows - refusing to publish an empty screen")

    out_rows = []
    for r in rows:
        o = {k: r.get(k) for k in KEEP}
        ins = r.get("insider") or {}
        o["insider"] = {k: ins.get(k) for k in INSIDER_KEEP}
        out_rows.append(o)

    payload = {
        "generatedAt": d.get("generatedAt"),
        "syncedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "profile": d.get("profile"),
        "weights": d.get("weights", {}),
        "pillars": d.get("pillars", []),
        "criteria": d.get("criteria", {}),
        "universeHits": d.get("universeHits"),
        "rows": out_rows,
    }

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))

    hist = os.path.join(HERE, "history")
    os.makedirs(hist, exist_ok=True)
    stamp = (d.get("generatedAt") or "")[:10] or datetime.date.today().isoformat()
    shutil.copyfile(OUT, os.path.join(hist, "growthscan-%s-%s.json" % (payload["profile"], stamp)))

    acc = sum(1 for r in out_rows if "ACCRETIVE" in (r.get("flags") or []))
    print("synced %d names from the %s %s run (%d KB) | %d accretive"
          % (len(out_rows), payload["generatedAt"], payload["profile"],
             os.path.getsize(OUT) // 1024, acc))


if __name__ == "__main__":
    main()
