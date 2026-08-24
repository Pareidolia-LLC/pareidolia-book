# -*- coding: utf-8 -*-
"""Futuresight Index - price pull and forward tracker.

Reads futuresight.json (the locked roster), pulls daily bars from Yahoo for every
name plus the benchmarks, converts foreign listings to USD, and writes
futuresight_prices.json for build.py to inline.

Two separate things come out of this, and they are NOT the same kind of number:

  navSeries / tierSeries  - forward performance from the locked inception date.
                            Honest, because the roster was published before any
                            of these returns existed.
  factorCorr              - correlation between factor groups over trailing
                            history. Legitimate to compute from the past because
                            it measures co-movement, not picking skill.

There is deliberately no backtest of the basket's returns. The roster was chosen
in Aug 2026 with full knowledge of what already happened, so a historical return
curve would measure hindsight, not strategy.

Usage:  python futuresight_fetch.py [--range 2y]
"""
import json, os, sys, time, math, datetime
import urllib.request, urllib.error, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
CHART = "https://query1.finance.yahoo.com/v8/finance/chart/%s?range=%s&interval=1d"
PAUSE = 0.35
RETRIES = 3


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            if attempt == RETRIES - 1:
                raise
            time.sleep(1.5 * (attempt + 1))
    return None


def bars(ticker, rng):
    """-> (currency, {isodate: {'o':open,'c':close}}) using split/div-adjusted closes."""
    d = get_json(CHART % (urllib.parse.quote(ticker), rng))
    res = (d or {}).get("chart", {}).get("result")
    if not res:
        raise ValueError("no chart data")
    res = res[0]
    ts = res.get("timestamp") or []
    q = res["indicators"]["quote"][0]
    adj = (res["indicators"].get("adjclose") or [{}])[0].get("adjclose")
    cur = res.get("meta", {}).get("currency", "USD") or "USD"
    out = {}
    for i, t in enumerate(ts):
        c = (adj[i] if adj and i < len(adj) and adj[i] is not None else q["close"][i])
        o = q["open"][i]
        if c is None:
            continue
        day = datetime.datetime.utcfromtimestamp(t).strftime("%Y-%m-%d")
        out[day] = {"o": o if o is not None else c, "c": c}
    if not out:
        raise ValueError("no usable bars")
    return cur, out


def fx_series(cur, rng, cache):
    """Multiplier series converting `cur` into USD."""
    if cur == "USD":
        return None
    if cur in cache:
        return cache[cur]
    _, b = bars("%sUSD=X" % cur, rng)
    cache[cur] = {d: v["c"] for d, v in b.items()}
    return cache[cur]


def to_usd(series, fx):
    if fx is None:
        return series
    days = sorted(fx)
    out, last = {}, None
    for d in sorted(series):
        while days and days[0] <= d:
            last = fx[days.pop(0)]
        if last:
            out[d] = {"o": series[d]["o"] * last, "c": series[d]["c"] * last}
    return out


def pct(a, b):
    return (b / a - 1.0) * 100.0 if a else 0.0


def main():
    rng = "2y"
    if "--range" in sys.argv:
        rng = sys.argv[sys.argv.index("--range") + 1]

    roster = json.load(open(os.path.join(HERE, "futuresight.json"), encoding="utf-8"))
    incept = roster["inception"]
    names = [n for n in roster["names"] if n.get("track", True)]
    fxcache = {}

    px, failed = {}, []
    queue = ([(n["ticker"], n.get("quote") or n["ticker"]) for n in names] +
             [(b, b) for b in roster["benchmarks"]])
    total = len(queue)
    for i, (tk, sym) in enumerate(queue, 1):
        try:
            cur, b = bars(sym, rng)
            px[tk] = {"cur": cur, "sym": sym,
                      "bars": to_usd(b, fx_series(cur, rng, fxcache))}
            state = "ok" if sym == tk else "ok via %s" % sym
        except Exception as e:
            failed.append({"ticker": tk, "sym": sym, "why": str(e)[:90]})
            state = "FAIL %s" % str(e)[:40]
        sys.stdout.write("\r[%3d/%3d] %-10s %-22s" % (i, total, tk, state))
        sys.stdout.flush()
        time.sleep(PAUSE)
    print()

    live = [n for n in names if n["ticker"] in px]
    if not live:
        sys.exit("no prices fetched - aborting rather than writing an empty tracker")

    # Baseline: the inception open. If inception has no bar yet (holiday, pre-open,
    # or a listing that does not trade that day) fall back to the first bar on or
    # after inception and record that the basis slipped.
    slipped = []
    for n in live:
        b = px[n["ticker"]]["bars"]
        days = sorted(d for d in b if d >= incept)
        if not days:
            n["_base"] = None
            continue
        d0 = days[0]
        n["_base"] = b[d0]["o"] if d0 == incept else b[d0]["c"]
        n["_baseDay"] = d0
        if d0 != incept:
            slipped.append({"ticker": n["ticker"], "usedDay": d0})

    priced = [n for n in live if n.get("_base")]
    tradedays = sorted({d for n in priced for d in px[n["ticker"]]["bars"] if d >= incept})

    def group_series(members):
        """Weighted index (base 100) across `members`, re-normalised to what is priced."""
        w = sum(m["weight"] for m in members) or 1.0
        out = []
        for d in tradedays:
            acc, cov = 0.0, 0.0
            for m in members:
                b = px[m["ticker"]]["bars"].get(d)
                if not b or not m.get("_base"):
                    continue
                acc += (m["weight"] / w) * (b["c"] / m["_base"])
                cov += m["weight"] / w
            out.append({"d": d, "v": round(100.0 * acc / cov, 4) if cov else None})
        return [p for p in out if p["v"] is not None]

    nav = group_series(priced)
    tiers = {t: group_series([n for n in priced if n["tier"] == t])
             for t in ("core", "growth", "spec")}
    factors = {f: group_series([n for n in priced if n["factor"] == f])
               for f in sorted({n["factor"] for n in priced})}

    bench = {}
    for bmk in roster["benchmarks"]:
        if bmk not in px:
            continue
        b = px[bmk]["bars"]
        days = sorted(d for d in b if d >= incept)
        if not days:
            continue
        base = b[days[0]]["o"] if days[0] == incept else b[days[0]]["c"]
        bench[bmk] = [{"d": d, "v": round(100.0 * b[d]["c"] / base, 4)} for d in days]

    # Per-name detail
    detail = []
    for n in priced:
        b = px[n["ticker"]]["bars"]
        days = sorted(d for d in b if d >= incept)
        last = b[days[-1]]["c"] if days else None
        detail.append({
            "ticker": n["ticker"], "name": n["name"], "industry": n["industry"],
            "factor": n["factor"], "tier": n["tier"], "weight": n["weight"],
            "currency": px[n["ticker"]]["cur"], "quote": px[n["ticker"]]["sym"],
            "base": round(n["_base"], 4), "last": round(last, 4) if last else None,
            "ret": round(pct(n["_base"], last), 2) if last else None,
            "tracked": True,
        })

    # Names carried in the concept but not priced still belong in the roster view,
    # otherwise the site silently shows fewer companies than the index claims.
    for n in roster["names"]:
        if n.get("track", True):
            continue
        detail.append({
            "ticker": n["ticker"], "name": n["name"], "industry": n["industry"],
            "factor": n["factor"], "tier": n["tier"], "weight": 0.0,
            "currency": None, "quote": None, "base": None, "last": None,
            "ret": None, "tracked": False, "why": n.get("untrackedWhy", ""),
        })

    detail.sort(key=lambda r: (r["ret"] is None, -(r["ret"] or 0)))

    # ---- factor correlation, computed on TRAILING history (not a backtest) ----
    # Pin everything to the US session calendar and forward-fill. Without this the
    # day set is the union of every exchange, so on a Tokyo-open/US-closed day the
    # index is computed from a different membership than the day before, and that
    # composition churn - not the market - drives the correlation.
    cal_src = "SPY" if "SPY" in px else sorted(px)[0]
    hist_days = sorted(px[cal_src]["bars"])[-252:]

    def aligned_closes(tk):
        """Member closes forward-filled onto hist_days; None until it starts trading."""
        b = px[tk]["bars"]
        days = sorted(b)
        out, j, last_c = [], 0, None
        for d in hist_days:
            while j < len(days) and days[j] <= d:
                last_c = b[days[j]]["c"]
                j += 1
            out.append(last_c)
        return out

    closes = {n["ticker"]: aligned_closes(n["ticker"]) for n in live}

    frets = {}
    for f in sorted({n["factor"] for n in live}):
        members = [n["ticker"] for n in live if n["factor"] == f]
        r = []
        for i in range(1, len(hist_days)):
            day = []
            for tk in members:
                a, b2 = closes[tk][i - 1], closes[tk][i]
                if a and b2 and a > 0 and b2 > 0 and a != b2:
                    day.append(math.log(b2 / a))
            # Equal-weighted mean of member returns, not an average of price levels.
            r.append(sum(day) / len(day) if len(day) >= max(3, len(members) // 3) else None)
        frets[f] = r

    def corr(x, y):
        p = [(a, b2) for a, b2 in zip(x, y) if a is not None and b2 is not None]
        if len(p) < 30:
            return None
        n = len(p)
        mx = sum(a for a, _ in p) / n
        my = sum(b2 for _, b2 in p) / n
        sx = math.sqrt(sum((a - mx) ** 2 for a, _ in p))
        sy = math.sqrt(sum((b2 - my) ** 2 for _, b2 in p))
        if not sx or not sy:
            return None
        return round(sum((a - mx) * (b2 - my) for a, b2 in p) / (sx * sy), 3)

    keys = sorted(frets)
    fcorr = {"keys": keys, "m": [[corr(frets[a], frets[b2]) for b2 in keys] for a in keys],
             "window": len(hist_days)}

    payload = {
        "asOf": tradedays[-1] if tradedays else incept,
        "builtAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "inception": incept,
        "inceptionLabel": roster["inceptionLabel"],
        "tierWeights": roster["tierWeights"],
        "tierCounts": roster["tierCounts"],
        "navSeries": nav,
        "tierSeries": tiers,
        "factorSeries": factors,
        "benchSeries": bench,
        "names": detail,
        "factorCorr": fcorr,
        "coverage": {"priced": len(priced), "tracked": len(names),
                     "roster": roster.get("rosterCount", len(names))},
        "untracked": roster.get("untracked", []),
        "failed": failed,
        "basisSlipped": slipped,
    }

    with open(os.path.join(HERE, "futuresight_prices.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)

    hist = os.path.join(HERE, "history")
    os.makedirs(hist, exist_ok=True)
    snap = os.path.join(hist, "futuresight-%s.json" % datetime.datetime.now().strftime("%Y-%m-%d"))
    with open(snap, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)

    print("priced %d/%d | as of %s | index %.2f"
          % (len(priced), len(names), payload["asOf"], nav[-1]["v"] if nav else 100.0))
    if failed:
        print("failed (%d): %s" % (len(failed), ", ".join(x["ticker"] for x in failed)))
    if slipped:
        print("basis slipped off inception for %d names" % len(slipped))
    print("wrote futuresight_prices.json + %s" % os.path.basename(snap))


if __name__ == "__main__":
    main()
