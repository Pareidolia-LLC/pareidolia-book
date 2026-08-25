# -*- coding: utf-8 -*-
"""Pull the Deep Value Scanner's latest run into the book repo.

The scanner lives at ../../value-scanner/ which is OUTSIDE this repo, so its
output has to be copied in for the site to be reproducible from a fresh clone.
This trims the run to the fields the page actually renders (about 115KB of the
158KB) and writes book/valuescan.json for build.py to inline.

Run the scanner first, then this, then build.py:
    cd ../../value-scanner && python scan.py --no-open
    cd - && python valuescan_sync.py && python build.py
"""
import json, os, shutil, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "..", "value-scanner", "data.json"))
OUT = os.path.join(HERE, "valuescan.json")

# Only what the dashboard on the site draws. `breakdown` is dropped (18KB of
# per-name score arithmetic that the site does not show); the scanner's own
# dashboard.html keeps it.
KEEP = ["ticker", "name", "sector", "industry", "price", "mcap", "chg52w",
        "ps", "pb", "evs", "pe", "de", "currentRatio", "roe", "profitMargin",
        "revGrowth", "fcfYield", "divYield", "pctOffLow", "zSafe", "flags",
        "score", "rank", "otc", "fx"]
INSIDER_KEEP = ["level", "buyers", "buyValue", "lastBuy", "topBuyer", "pctOfCap"]


def main():
    if not os.path.exists(SRC):
        sys.exit("no scanner output at %s - run scan.py in value-scanner first" % SRC)

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
        "criteria": d.get("criteria", {}),
        "universeHits": d.get("universeHits"),
        "zSafeCount": d.get("zSafeCount"),
        "rows": out_rows,
    }

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))

    hist = os.path.join(HERE, "history")
    os.makedirs(hist, exist_ok=True)
    stamp = (d.get("generatedAt") or "")[:10] or datetime.date.today().isoformat()
    shutil.copyfile(OUT, os.path.join(hist, "valuescan-%s.json" % stamp))

    heavy = sum(1 for r in out_rows if (r["insider"] or {}).get("level") == "heavy")
    print("synced %d names from the %s run (%d KB) | %d with heavy insider buying"
          % (len(out_rows), payload["generatedAt"], os.path.getsize(OUT) // 1024, heavy))


if __name__ == "__main__":
    main()
