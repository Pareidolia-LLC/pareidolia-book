# PAREIDOLIA — Handoff

*A private book run under doctrine — pattern recognition in a hostile tape.*
**Site:** https://pareidoliatrading.com · **Repo:** Pareidolia-LLC/pareidolia-book · **Owner:** Pareidolia LLC, est. Oct 2025
**Status of this file:** corrected September 2026 from a second-model draft. The voice sections (§3, §5, §8–10) are that draft's, with its two self-contradictions fixed. §1–2, §4, §6–7 were rewritten against `build.py` and `data.json` and describe what is actually built.

---

## 1. What this is

A public-facing private trading book. One operator. The site is the ledger, the after-action file, and the research notebook in one place. Not a fund, not a newsletter, not a blog — a performance record with the hood open.

**Core promise:** transparent on performance, silent on size. Absolute balances, share counts, and dollar P&L are withheld by design. Everything else is visible, failures included.

## 2. Design system — what is actually there

### 2.1 Colourway is a build-time choice, not a user toggle

`build.py` sets two constants and stamps them on `<html>`:

```
COLOURWAY = "terminal"    -> <html data-cw="terminal">
PLATE     = "silver"      -> <html data-plate="silver">
```

There is **no runtime switch** in the page. To change the look you change the constant and rebuild. Three colourways are defined in the CSS:

| `data-cw` | Metaphor | Notes |
|---|---|---|
| *(default / unset)* | The banknote — cream ground, silver stock, engraving green, brushed-gold plates | |
| `terminal` | Amber phosphor on black — green up, red down | **This is what is live.** A block of JS gated on `data-cw === "terminal"` adds the terminal-only behaviour. |
| `night` | Dark variant with its own panel/border overrides | Defined, not currently shipped. |

`data-plate` is a separate axis (`silver` or `gold`) controlling the metallic plate used for section headers, independent of colourway.

### 2.2 Layout

- One HTML file, one request. ~560 KB with everything inline: CSS, JS, the `DATA` blob, and the three concept datasets. No external fonts, images, scripts, or calls after load.
- Seven tabs, JS-driven (`data-panel` buttons showing `#panel-*` divs). Not anchor links.
- Page padding `clamp(20px,4vw,56px)`. Cards are lighter sheets laid on the ground (`--panel` on `--bg`), never inversions.
- Every dark-theme override is guarded on `data-cw`; a new visual element must render correctly in the default and in `terminal` at minimum.

### 2.3 Banker formatting — non-negotiable

Unit in the column header, not the cell. Negatives in brackets `(3.6)`, positives unsigned. Missing = em dash `—`. Percentages one decimal. Multiples one decimal + `×`. Market cap `$1.2B` / `$450M`.

### 2.4 Stale-page guard

GitHub Pages serves `index.html` with `max-age=600` and cannot be told otherwise. `build.py` writes `version.json` (`{build, builtAt}`) and bakes the same hash into the page. On load the page fetches `version.json` uncached; on mismatch it reloads once with a cache-buster, and if that does not clear it, shows a "newer edition is published" bar rather than looping.

## 3. Voice and tone

Terse, objective, unsentimental. An after-action report written by someone who was there and does not need to impress anyone. Confident, never boastful. Honest about failure with the same rigour as success. First person for agency (*we take risk directly*), third person for mechanics (*the engine owns liquid names*). "We" for a single-operator book is a deliberate choice already made in The Story — keep it consistent.

**Cadence rules**

1. One thought, one sentence. Default to 20–25 words. Break long sentences — *except* in the weekly after-action notes, which deliberately stack clauses to build pressure before the punch. Do not flatten those.
2. Active voice for agency.
3. Fragments for punch, not confusion. *"The engine."* is an established label and is fine as an opener; the sentence after it must deliver.
4. No accidental echoes — the same word twice in close proximity.
5. End on the punch, not the qualification.
6. Semicolons are rare. This voice goes for the fist.
7. No jargon clunkers: *in build* → *under construction*; *plays into* → *serves*.

**Already applied (Sept 2026):** the three Desk cards, the control-framework echo, all "in build" copy, and the concept disclaimers. Do not re-litigate them.

## 4. Information architecture — the seven tabs

Tab labels are numbered in the terminal colourway. Internal panel ids in the second column.

| # | Tab | Panel | What it holds |
|---|---|---|---|
| 1 | **P&L** | `report` | Three return tiles · return curve with timeline selector · **Weekly After-Action** (card + history strip of every week since inception) · Service Record (career ledger) · Between the After-Actions (insights) |
| 2 | **The Story** | `story` | Origin, intent, contact. Rendered from `pages.story`. |
| 3 | **The Book** | `book` | Book summary + concept of operations + risk posture (from `book`) · allocation bars · positions ledger |
| 4 | **The Desk** | `approach` | The three strategy cards — **The Wheel / Forecast contracts / Outright** — with control lines · control framework · discipline blocks (from `pages.discipline`) · Mandate & Constraints (from `constraints`) |
| 5 | **The Mandate** | `concepts` | Doctrine: what we hold to be true · mental models · target set. Rendered from `pages.concepts`. |
| 6 | **Heroes & Dogs** | `record` | Accolades · Failures · Discipline tally · Best closes · Worst closes · By name · Event sleeve by contract · How to read this. From `record`. |
| 7 | **The Pipe** | `ideation` | The three research concepts, each a sub-tab: **01 Futuresight Index**, **02 Value Scanner**, **03 Quality Growth**. Not pipeline documentation. |

**Weekly after-action conventions.** One card per Monday–Friday week, dated the week's last trading day. Solid chip = graded live that Friday. Dashed chip marked *rebuilt* = reconstructed after the fact from the trade record (`recon: true`), badged on the card and carrying a basis note. Three dials — position size (20% cap), cash buffer (10% floor), event sleeve. **The event dial is omitted entirely in weeks with no forecast trades.** In reconstructed weeks it is graded on what the sleeve returned (closes, win rate, profit factor), not on today's rules. Since Aug 24 2026 the sleeve is sanctioned for data collection and the dial reports it without scoring it.

**Concept 01 rule:** no backtest, ever. The roster was chosen knowing what had happened; a historical curve would measure hindsight.

## 5. Content formats

**After-action card**

```
Week of Mon d – Fri d, YYYY · Grade · Week return
Dial 1 · Position size   pass|warn|fail · value · rule
Dial 2 · Cash buffer     pass|warn|fail · value · rule
Dial 3 · Event sleeve    (omitted if no forecast trades) · value · rule
Assessment: narrative
[Reconstructed cards append a basis note.]
```

**Concept:** `Concept 0N · status · tracking method` → name → thesis → honesty paragraph → methodology → table/matrix → disclaimer.

**Disclaimer, every concept, verbatim:**

> Research I run for myself, not advice. I am not a licensed financial advisor. *[the screen's specific limitation]*. Act on it and the risk is yours, not mine.

Short, explicit, punchy — all three on purpose. *"Not mine"* keeps the liability disclaim explicit.

## 6. Data — what actually drives the page

Two layers, both merged by `build.py` into one `index.html`.

### 6.1 `data.json` → embedded as `var DATA`

Top-level keys, exactly: `asOf · curveLabel · returns · reports · career · positions · constraints · book · pages · curve · record`.

```
asOf        "Sep 5, 2026"                 the page date; career.asOfLabel MUST equal it or build.py exits
curveLabel  str
returns     [{k, v, m}]                   v is a number (percent); m is the subtitle
reports     [{w, weekLabel, grade, weekRet, dials:[{key,state,value,rule}], note, now?, recon?}]
              oldest -> newest · state in pass|warn|fail · exactly one card has now:true
              recon:true marks a rebuilt week; a live card simply has NO recon key (there is no recon:false)
              dials may have 2 or 3 entries
career      {sinceLabel, asOfLabel, headline:[{k,v,m}], buckets:[{name,tag,tone,win,pf,closes,note}], insights:[str]}
              headline/bucket figures are script-owned (career_stats.py --write); insights and bucket notes are hand-written
positions   [{t, s, w, r}]                s in wheel|dir|cash · w,r percent · r null hides the return
constraints {title, permitted:[str], restricted:[str], note}
book        [{eyebrow, h?, p?:[str], ul?:[str]}]      three blocks
pages       {story:[block], concepts:[block], discipline:[block]}   same block shape
curve       {cps:[fraction], dates:["YYYYMMDD"]}      inception TWR series, parallel arrays
record      {accolades, failures, discipline:[{k,v,m}], wins, losses:[{t,d,s,v}], names, events:[{t,closes,win,pf,g,l}], notes:[str]}
              g/l are each name's share of ALL realized gains / losses; pf null or >50 renders as an em dash
```

Weekly refresh touches only `data.json` (returns, positions, a new report, curve tail, book prose) plus `career_stats.py --write`. Schema detail and the settlement check live in `README.md`.

### 6.2 Concept datasets — separate files, merged at build

These are **not** in `DATA`. `build.py` reads them and embeds them for The Pipe.

| File | Producer | Shape |
|---|---|---|
| `futuresight.json` | hand-maintained roster | `inception, basis, benchmarks, tierWeights, tierCounts, rosterCount, trackedCount, untracked, names:[{ticker,name,tier,factor,industry,weight,quote,track,role}]` |
| `futuresight_prices.json` | `futuresight_fetch.py` | `asOf, builtAt, navSeries, tierSeries{core,growth,spec}, factorSeries{AI,DATA,DEF,ENERGY,IND,MED,RATES,SW}, benchSeries{SPY,QQQ}, names[...], factorCorr{keys,m,window}, coverage{priced,tracked,roster}, untracked, failed, basisSlipped` |
| `valuescan.json` | `valuescan_sync.py` | `generatedAt, syncedAt, criteria, universeHits, zSafeCount, rows:[{rank,score,ticker,name,sector,industry,mcap,price,pb,ps,pe,fcfYield,roe,roic,de,currentRatio,revGrowth,divYield,chg52w,pctOffLow,insider,flags,fx,otc,...}]` |
| `growthscan.json` | `growthscan_sync.py` | `generatedAt, syncedAt, profile, weights{Growth,Returns,Cash,Balance,Capital,Value,Neglect}, pillars[7], criteria, universeHits, rows:[{... epsCagr3y, fcfCagr3y, incRoic, fcfConversion, evEbitda, evFcf, forwardPe, analysts, insider, flags ...}]` |

`build.py` prints what it merged: `built index.html (...) from data.json + futuresight (N priced) + valuescan (N names) + growthscan (N names)`. A missing file warns and renders that concept empty rather than failing the build.

## 7. Technical notes

- `noindex,nofollow` stays. No analytics, no cookies, no tracking.
- Deploy = `git push` → GitHub Pages serves `index.html` from the repo root (`CNAME` = pareidoliatrading.com).
- `build.py` is standard-library Python. It refuses to build if `career.asOfLabel != asOf`.
- Trade dumps and reconstruction working files live in `../data/`, outside the repo, because they contain dollars.
- Local preview: `.claude/launch.json` serves the folder with `python -m http.server`. Do not verify from `file://` — it snapshots stale renders.

## 8. Do

Preserve the voice. Fix cadence where it is off. Banker formatting everywhere. Every concept carries its limitation and its disclaimer. Anything visual works in the default and in `terminal`. New content goes in one of the seven tabs using the existing block/table patterns. Flag value traps, currency artefacts, and cyclical distortions — never quietly exclude them.

## 9. Do not

Soften the voice. Hide a loss. Add a backtest to Futuresight. Remove a disclaimer. Add a page, an external dependency, a custom font, or a tracker. Remove `noindex`. Rewrite the after-action notes for sentence length.

## 10. Before → after (applied Sept 2026)

**The Wheel** — *The engine. We own liquid retail-momentum names and sell calls against them, laddering expiries and buying the contracts back cheap. Premium is the carry. The shares are collateral — they earn while they wait.*

**Forecast contracts** — *Wound down in August. It had carried most of the account's turnover and almost none of its P&L. Reopened deliberately on Aug 24 to gather clean data for a systematic forecast strategy now under construction.*

**Outright** — *We take risk directly, and we take it rarely. These are investments, not trades. We hold them outright — no calls written against them. Thesis comes before size. We express conviction in the position and never talk it up after the fill.*

**Control framework** — *The limits are binding, not advisory — a breach goes into the weekly after-action whether or not the week made money.*

## 11. Footer

> Figures are time-weighted returns and portfolio weights. Absolute balances, share counts, and dollar P&L are withheld by design — transparent on performance, silent on size.
> PAREIDOLIA LLC · PRIVATE BOOK · FOR REVIEW ONLY · NOT AN OFFERING OR SOLICITATION · PAST PERFORMANCE IS NOT INDICATIVE OF FUTURE RESULTS
