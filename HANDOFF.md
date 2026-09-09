# PAREIDOLIA — Handoff

*A private book run under pattern recognition.*
**Site:** https://pareidoliatrading.com · **Repo:** Pareidolia-LLC/pareidolia-book · **Owner:** Pareidolia LLC, est. Oct 2025
**Status of this file:** corrected September 2026 from a second-model draft. The voice sections (§3, §5, §8–10) are that draft's, with its two self-contradictions fixed. §1–2, §4, §6–7 were rewritten against `build.py` and `data.json` and describe what is actually built. Updated the same month for the **paper edition**: the redesign prototype's surfaces on the live build, four tabs, and a runtime colourway toggle.

---

## 1. What this is

A public-facing private trading book. One operator. The site is the ledger, the after-action file, and the research notebook in one place. Not a fund, not a newsletter, not a blog — a performance record with the hood open.

**Core promise:** transparent on performance, silent on size. Absolute balances, share counts, and dollar P&L are withheld by design. Everything else is visible, failures included.

## 2. Design system — what is actually there

### 2.1 Two colourways: paper by default, terminal on a toggle

The reader lands on **paper** and can switch to **terminal** with the button in the masthead. The choice is remembered.

| `data-cw` | Look | Notes |
|---|---|---|
| *(unset — the base `:root`)* | **Paper.** Warm off-white ground `#F5F1E8`, lighter cards `#FAF8F2`, engraving green `#1E5B3C` as the one accent, gold `#9C7B22` for plates and badges, rounded 11px surfaces, sans body with mono labels. | The default. This is the redesign prototype's palette applied as tokens to the live build. |
| `terminal` | Amber phosphor on black — green up, red down, tape, function keys, status line. | Unchanged from the "desk, 1987–2004" edition. Every paper override is scoped `:root:not([data-cw="terminal"])` so it does not touch this look. |
| `night` | Dark variant with its own panel/border overrides. | Defined, not shipped, not reachable from the toggle. |

**How the toggle works.** A one-line script in `<head>` reads `localStorage["pb-cw"]` and sets `data-cw` before first paint, so there is no flash. The masthead button (`#cwbtn`) is labelled with where it takes you — *Terminal* on paper, *Paper* on terminal. Clicking stores the choice and reloads, because the terminal chrome (tape, function keys) initialises on load. Build constants set the first-visit default: `COLOURWAY = ""` (paper), `PLATE = "gold"`, `ORNAMENT = "none"`.

**What was removed.** The banknote decoration — the asanoha/shippo rosette in the masthead, the guilloche pinstripes, the cream-and-silver stock — is gone from the paper look (ornament set to `none`, pinstripe tokens transparent, `.rosette` hidden). The generating code is still in `build.py` if it is ever wanted back.

`data-plate` (`gold` or `silver`) is a separate axis controlling the metallic header plate. Paper ships gold; terminal overrides the plate to its own dark gradient regardless.

### 2.2 Layout

- One HTML file, one request. ~550 KB with everything inline: CSS, JS, the `DATA` blob, and the three concept datasets. No external fonts, images, scripts, or calls after load.
- Four tabs, JS-driven (`data-panel` buttons showing `#panel-*` divs). Not anchor links. Content column is 960px on paper.
- Page padding `clamp(20px,4vw,56px)`. Cards are lighter sheets laid on the ground (`--panel` on `--bg`), never inversions. Section eyebrows sit centred between two hairlines; everything else is left-aligned.
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

## 4. Information architecture — the four tabs

The redesign prototype's skeleton. Tabs are numbered 01–04 on paper; the numbers are hidden on terminal, which draws its own function keys. Internal panel ids in the second column. The landing tab is The Book.

| # | Tab | Panel | What it holds, in order |
|---|---|---|---|
| 01 | **The Book** | `book` | Three return tiles · return curve with timeline selector · book summary, concept of operations, risk posture (from `book`) · allocation bars · positions ledger · the three strategy cards **The Wheel / Forecast contracts / Outright** with control lines and the control framework |
| 02 | **The Record** | `record` | **Weekly After-Action** (card + history strip of every week since inception) · Service Record (career ledger) · Between the After-Actions · Accolades · Failures · Discipline tally · Best closes · Worst closes · By name · Event sleeve by contract · How to read this |
| 03 | **The Lab** | `ideation` | The three research concepts, each a sub-tab: **01 Futuresight Index**, **02 Value Scanner**, **03 Quality Growth** |
| 04 | **The Story** | `story` | Origin, intent, contact (from `pages.story`, into `#story-blocks`) · doctrine — what we hold to be true, mental models, target set (from `pages.concepts`, into `#panel-concepts`, which is now a plain container, not a panel) · discipline blocks (from `pages.discipline`) · Mandate & Constraints (from `constraints`) |

The former P&L, The Desk and The Mandate panels no longer exist; their sections moved as listed. `blocks()` in the JS still targets `booksummary`, `panel-concepts`, `page-discipline-inline` and now `story-blocks`. The curve redraws on activating `book`; the allocation bars animate on `book`; the Futuresight chart draws on `ideation`.

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

Preserve the voice. Fix cadence where it is off. Banker formatting everywhere. Every concept carries its limitation and its disclaimer. Anything visual works in paper and in `terminal` — scope paper-only rules with `:root:not([data-cw="terminal"])`. New content goes in one of the four tabs using the existing block/table patterns. Flag value traps, currency artefacts, and cyclical distortions — never quietly exclude them.

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
