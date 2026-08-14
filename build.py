# -*- coding: utf-8 -*-
"""Pareidolia book — static site generator.
Reads data.json, writes index.html (served by GitHub Pages).
Weekly refresh = overwrite data.json with a fresh broker pull, then run this."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(HERE, "data.json"), encoding="utf-8"))

TEMPLATE = r"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Pareidolia — The Book</title>
<style>
  :root{
    --bg:#F2ECDD; --panel:#FAF6EC; --panel-2:#EBE3D1; --line:#E0D6C0;
    --ink:#2B2517; --muted:#7D7159; --faint:#AAA089;
    --accent:#A9801F; --accent-soft:rgba(169,128,31,.16);
    --slate:#8A7E64; --up:#5F8A3C; --down:#B4552F;
    --grid:rgba(43,37,23,.10); --warn:#C46A1C; color-scheme:light;
    --serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,"Times New Roman",serif;
    --sans:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    --mono:"SFMono-Regular","SF Mono",ui-monospace,"Cascadia Mono","Segoe UI Mono",Menlo,Consolas,monospace;
  }
  *{box-sizing:border-box} body{margin:0}
  .wrap{background:var(--bg); color:var(--ink); font-family:var(--sans); min-height:100vh; padding:clamp(20px,4vw,56px); -webkit-font-smoothing:antialiased; line-height:1.5}
  .sheet{max-width:1120px; margin:0 auto}
  .masthead{display:flex; justify-content:space-between; align-items:flex-end; gap:24px; flex-wrap:wrap; border-bottom:1.5px solid var(--ink); padding-bottom:18px}
  .mark{font-family:var(--serif); font-size:clamp(34px,6vw,58px); line-height:.95; letter-spacing:.01em; font-weight:600; text-wrap:balance}
  .mark .dot{color:var(--accent)}
  .tag{font-size:12.5px; color:var(--muted); margin-top:9px; max-width:44ch; letter-spacing:.02em}
  .asof{font-family:var(--mono); font-size:11px; color:var(--faint); text-transform:uppercase; letter-spacing:.14em; text-align:right; white-space:nowrap}
  .asof b{color:var(--muted); font-weight:600}
  section{margin-top:clamp(30px,5vw,52px)}
  .eyebrow{font-family:var(--mono); font-size:10.5px; letter-spacing:.22em; text-transform:uppercase; color:var(--accent); margin:0 0 14px; display:flex; align-items:center; gap:12px}
  .eyebrow::after{content:""; flex:1; height:1px; background:var(--line)}
  h2{font-family:var(--serif); font-weight:600; font-size:22px; margin:0 0 4px}
  .stats{display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin-top:30px}
  .stat{background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:18px 20px 16px}
  .stat .k{font-family:var(--mono); font-size:10px; letter-spacing:.16em; text-transform:uppercase; color:var(--muted)}
  .stat .v{font-family:var(--mono); font-variant-numeric:tabular-nums; font-size:clamp(26px,4.4vw,34px); font-weight:600; margin-top:8px; letter-spacing:-.01em}
  .stat .m{font-size:11px; color:var(--faint); margin-top:3px}
  .asofline{font-family:var(--mono); font-size:10px; letter-spacing:.14em; text-transform:uppercase; color:var(--faint); text-align:right; margin:12px 2px 0}
  .asofline b{color:var(--muted); font-weight:600}
  .pos{color:var(--up)} .neg{color:var(--down)}
  .chart-card{background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:20px 20px 16px; margin-top:14px; position:relative}
  .ctip{position:absolute; display:none; pointer-events:none; z-index:6; transform:translate(-50%,-100%); background:var(--bg); border:1px solid var(--line); border-radius:7px; padding:4px 9px; font-family:var(--mono); font-size:11px; white-space:nowrap; box-shadow:0 3px 10px rgba(43,37,23,.18)}
  .ctip .tdate{color:var(--muted); margin-right:9px}
  .ctip .tval{font-weight:600}
  .chart-head{display:flex; justify-content:space-between; align-items:baseline; gap:16px; flex-wrap:wrap}
  .chart-head .sub{font-family:var(--mono); font-size:11px; color:var(--muted); letter-spacing:.04em}
  canvas#curve{display:block; width:100%; height:290px; margin-top:4px}
  .tlviews{display:flex; gap:6px; flex-wrap:wrap; margin-top:12px}
  .tlv{font-family:var(--mono); font-size:10.5px; letter-spacing:.06em; text-transform:uppercase; padding:5px 11px; border:1px solid var(--line); border-radius:20px; background:none; color:var(--muted); cursor:pointer; transition:border-color .15s, color .15s, background .15s}
  .tlv:hover{border-color:var(--accent); color:var(--ink)}
  .tlv.active{background:var(--accent-soft); border-color:var(--accent); color:var(--accent)}
  .tlv:focus-visible{outline:2px solid var(--accent); outline-offset:2px}
  .marks{display:flex; gap:22px; flex-wrap:wrap; margin-top:6px; padding-top:12px; border-top:1px solid var(--line); font-family:var(--mono); font-size:11px; color:var(--muted)}
  .marks span{display:inline-flex; gap:7px; align-items:center}
  .marks b{color:var(--ink); font-weight:600; font-variant-numeric:tabular-nums}
  .swatch{width:9px;height:9px;border-radius:2px;display:inline-block}
  .rc-head{display:flex; align-items:center; gap:16px; flex-wrap:wrap; margin-top:6px; margin-bottom:16px}
  .grade{font-family:var(--serif); font-weight:600; font-size:34px; line-height:1; padding:5px 16px; border-radius:10px; border:1.5px solid var(--down); color:var(--down)}
  .rc-head .wk{font-family:var(--mono); font-size:12px; color:var(--muted); line-height:1.7}
  .rc-head .wkret{font-weight:600}
  .dials{display:grid; grid-template-columns:repeat(3,1fr); gap:14px}
  .dial{background:var(--panel); border:1px solid var(--line); border-top:3px solid var(--line); border-radius:10px; padding:15px 16px 14px}
  .dial.pass{border-top-color:var(--up)} .dial.warn{border-top-color:var(--warn)} .dial.fail{border-top-color:var(--down)}
  .dial .dk{font-family:var(--mono); font-size:10px; letter-spacing:.13em; text-transform:uppercase; color:var(--muted)}
  .dial .dv{font-family:var(--mono); font-variant-numeric:tabular-nums; font-size:21px; font-weight:600; margin:9px 0 3px}
  .dial .rule{font-size:11.5px; color:var(--faint); line-height:1.45}
  .state{display:inline-block; font-family:var(--mono); font-size:10px; font-weight:600; letter-spacing:.09em; text-transform:uppercase; padding:3px 9px; border-radius:20px}
  .state.pass{color:var(--up); background:color-mix(in srgb,var(--up) 15%,transparent)}
  .state.warn{color:var(--warn); background:color-mix(in srgb,var(--warn) 17%,transparent)}
  .state.fail{color:var(--down); background:color-mix(in srgb,var(--down) 15%,transparent)}
  .rc-note{margin-top:15px; font-size:13px; color:var(--muted); line-height:1.6; max-width:78ch}
  .rc-note b{color:var(--ink); font-weight:600}
  .con{display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-top:14px}
  .con .box{background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:16px 18px}
  .con .box.ok{border-top:3px solid var(--up)}
  .con .box.no{border-top:3px solid var(--down)}
  .con .box h4{font-family:var(--mono); font-size:10px; letter-spacing:.14em; text-transform:uppercase; color:var(--muted); margin:0 0 10px}
  .con ul{margin:0; padding-left:18px} .con li{font-size:13px; margin:5px 0; color:var(--ink)}
  .hlabel{font-family:var(--mono); font-size:10px; letter-spacing:.14em; text-transform:uppercase; color:var(--muted); margin:20px 0 8px}
  .hist{display:flex; gap:10px; overflow-x:auto; padding-bottom:4px}
  .gcard{flex:0 0 auto; min-width:82px; background:var(--panel); border:1px solid var(--line); border-radius:9px; padding:10px 12px; text-align:center; cursor:pointer; font:inherit; color:inherit; transition:border-color .15s, box-shadow .15s}
  .gcard:hover{border-color:var(--accent)}
  .gcard:focus-visible{outline:2px solid var(--accent); outline-offset:2px}
  .gcard.active{border-color:var(--accent); box-shadow:inset 0 0 0 1px var(--accent)}
  .gnow{font-family:var(--mono); font-size:8px; letter-spacing:.12em; text-transform:uppercase; color:var(--accent); margin-top:3px}
  .gw{font-family:var(--mono); font-size:10px; color:var(--muted); letter-spacing:.04em}
  .gg{font-family:var(--serif); font-size:26px; font-weight:600; line-height:1.15; margin:3px 0}
  .gr{font-family:var(--mono); font-size:11px; font-variant-numeric:tabular-nums}
  .tabs{display:flex; flex-wrap:wrap; gap:2px 4px; margin-top:22px; border-bottom:1px solid var(--line); position:sticky; top:0; z-index:5; background:var(--bg)}
  .tab{flex:0 0 auto; background:none; border:0; cursor:pointer; font-family:var(--mono); font-size:11.5px; letter-spacing:.1em; text-transform:uppercase; color:var(--muted); padding:13px 16px; border-bottom:2px solid transparent; margin-bottom:-1px; transition:color .15s}
  .tab:hover{color:var(--ink)}
  .tab.active{color:var(--accent); border-bottom-color:var(--accent)}
  .tab:focus-visible{outline:2px solid var(--accent); outline-offset:-3px}
  .panel{display:none}
  .panel.active{display:block}
  .panel.active>section:first-child{margin-top:26px}
  .bars{display:flex; flex-direction:column; gap:9px}
  .bar{display:grid; grid-template-columns:74px 1fr 62px; align-items:center; gap:14px}
  .bar .name{font-family:var(--mono); font-weight:600; font-size:13px; letter-spacing:.02em}
  .bar .track{height:22px; background:var(--panel-2); border:1px solid var(--line); border-radius:5px; overflow:hidden; position:relative}
  .bar .fill{height:100%; border-radius:4px 0 0 4px; transform-origin:left; transform:scaleX(0); transition:transform .9s cubic-bezier(.22,.61,.36,1)}
  .bar .pct{font-family:var(--mono); font-variant-numeric:tabular-nums; font-size:12.5px; text-align:right; color:var(--muted)}
  .legend-strat{display:flex; gap:18px; flex-wrap:wrap; margin-top:16px; font-size:11.5px; color:var(--muted)}
  .legend-strat span{display:inline-flex; gap:7px; align-items:center}
  .tablewrap{overflow-x:auto; border:1px solid var(--line); border-radius:10px}
  table{width:100%; border-collapse:collapse; min-width:440px}
  thead th{font-family:var(--mono); font-size:10px; letter-spacing:.14em; text-transform:uppercase; color:var(--muted); text-align:left; padding:12px 16px; border-bottom:1px solid var(--line); font-weight:600}
  th.r,td.r{text-align:right}
  tbody td{padding:11px 16px; border-bottom:1px solid var(--line); font-size:13.5px}
  tbody tr:last-child td{border-bottom:0}
  td.tk{font-family:var(--mono); font-weight:600; letter-spacing:.02em}
  td.num{font-family:var(--mono); font-variant-numeric:tabular-nums}
  .chip{display:inline-block; font-family:var(--mono); font-size:10px; letter-spacing:.06em; text-transform:uppercase; padding:3px 8px; border-radius:20px; border:1px solid var(--line); color:var(--muted)}
  .chip.wheel{color:var(--accent); border-color:var(--accent-soft); background:var(--accent-soft)}
  .chip.dir{color:var(--slate); border-color:var(--line)}
  .cards{display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:14px}
  .appr{background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:18px 18px 16px}
  .appr h3{font-family:var(--serif); font-size:16px; margin:0 0 8px; font-weight:600}
  .appr h3 .idx{font-family:var(--mono); font-size:11px; color:var(--accent); margin-right:8px; letter-spacing:.05em}
  .appr p{margin:0; font-size:13px; color:var(--muted); line-height:1.55}
  .prose{font-size:14px; color:var(--muted); line-height:1.65; max-width:70ch; margin-top:9px}
  .proselist{margin:12px 0 0; padding-left:0; max-width:70ch; list-style:none}
  .proselist li{position:relative; font-size:13.5px; color:var(--ink); line-height:1.55; margin:9px 0; padding-left:18px}
  .proselist li::before{content:""; position:absolute; left:0; top:8px; width:5px; height:5px; border-radius:1px; background:var(--accent)}
  #booksummary>section:first-child{margin-top:26px}
  footer{margin-top:clamp(34px,5vw,54px); padding-top:18px; border-top:1px solid var(--line); font-size:11.5px; color:var(--faint); line-height:1.6}
  footer .meth{font-family:var(--mono); font-size:10.5px; letter-spacing:.03em}
  @media (max-width:560px){ .stats{grid-template-columns:1fr} .dials{grid-template-columns:1fr} .con{grid-template-columns:1fr} .bar{grid-template-columns:60px 1fr 50px; gap:10px} }
  @media (min-width:860px){
    .bookgrid{display:grid; grid-template-columns:1.15fr 1fr; gap:34px; align-items:start}
    .bookgrid>section{margin-top:26px}
    canvas#curve{height:330px}
  }
  @media (prefers-reduced-motion:reduce){ .bar .fill{transition:none} }
  /* centered editorial layout */
  .sheet{text-align:center}
  .masthead{flex-direction:column; align-items:center; text-align:center}
  .asof{text-align:center}
  .tag{margin-left:auto; margin-right:auto}
  .tabs{justify-content:center}
  .eyebrow{justify-content:center}
  .eyebrow::before{content:""; flex:1; height:1px; background:var(--line)}
  .chart-head{justify-content:center}
  .tlviews{justify-content:center}
  .marks{justify-content:center}
  .rc-head{justify-content:center}
  .hist{justify-content:safe center}
  .legend-strat{justify-content:center}
  .prose,.rc-note{margin-left:auto; margin-right:auto; max-width:none}
  section .tag{max-width:none}
  .proselist{max-width:none; margin-left:auto; margin-right:auto}
  .proselist li{padding-left:0; margin:12px 0}
  .proselist li::before{content:none}
  .con ul{list-style:none; padding-left:0}
  thead th,tbody td,th.r,td.r{text-align:center}
  .asofline{text-align:center}
  footer{text-align:center}
  .prose a,.rc-note a{color:var(--accent); text-decoration:underline; text-underline-offset:3px}
  /* broadsheet edition */
  .mark{font-weight:700; font-size:clamp(40px,7vw,72px); letter-spacing:.005em}
  .masthead{border-bottom:0; padding-bottom:10px; gap:8px}
  .dateline{display:flex; justify-content:space-between; align-items:center; gap:8px 22px; flex-wrap:wrap; font-family:var(--mono); font-size:10px; letter-spacing:.16em; text-transform:uppercase; color:var(--muted); padding:9px 2px; border-top:3px double var(--ink); border-bottom:1px solid var(--ink)}
  .dateline b{color:var(--ink); font-weight:600}
  .tag{font-family:var(--serif); font-style:italic; font-size:14px}
  section .tag{font-size:14.5px}
  h2{font-size:27px}
  .eyebrow{font-family:var(--serif); font-size:12px; font-weight:700; letter-spacing:.2em}
  .prose,.proselist li,.rc-note,.con li,.appr p,.dial .rule,.stat .m{font-family:var(--serif)}
  .prose{font-size:15.5px; color:var(--ink)}
  .proselist li{font-size:15px; line-height:1.6}
  .rc-note{font-size:14.5px}
  .con li{font-size:14px}
  .appr p{font-size:13.5px}
  .stat,.dial,.chart-card,.appr,.con .box,.tablewrap,.gcard,.tlv,.chip,.state,.bar .track,.bar .fill,.grade,.ctip{border-radius:0}
  footer{border-top:3px double var(--ink); font-family:var(--serif); font-style:italic; font-size:12.5px; color:var(--muted)}
  footer .meth{font-family:var(--mono); font-style:normal}
  @media (max-width:560px){ .dateline{justify-content:center} }
  /* justified body text + drop caps (blended edition) */
  .prose,.proselist li,.rc-note{text-align:justify; text-justify:inter-word; hyphens:auto}
  #panel-story section:first-of-type h2 + .prose::first-letter,
  #booksummary section:first-of-type h2 + .prose::first-letter,
  #page-discipline-inline section:first-of-type h2 + .prose::first-letter,
  #panel-concepts section:nth-of-type(2) .eyebrow + .prose::first-letter{
    float:left; font-family:var(--serif); font-size:3.4em; line-height:.82;
    font-weight:700; padding:8px 10px 0 0; color:var(--accent)}
  /* blacked section tabs */
  .tabs{background:var(--ink); border-bottom:1px solid var(--ink)}
  .tab{color:rgba(242,236,221,.62); padding:13px 18px; margin-bottom:0}
  .tab:hover{color:var(--bg)}
  .tab.active{color:color-mix(in srgb, var(--accent) 72%, #F2ECDD 28%); border-bottom-color:var(--accent)}
  .tab:focus-visible{outline-offset:-4px}
  /* performance page: returns + curve, report card below */
  .perfgrid{margin-top:26px}
  .perfgrid>div:first-child>section:first-child{margin-top:0}
</style></head>
<body>
<div class="wrap"><div class="sheet">
  <header class="masthead">
    <div>
      <div class="mark">Pareidolia<span class="dot">.</span></div>
      <div class="tag">A private multi-asset book — pattern recognition in market noise.</div>
    </div>
  </header>
  <div class="dateline"><span>Pareidolia LLC</span><span><b id="dlDate"></b></span><span>Est. October 2025</span></div>
  <nav class="tabs" role="tablist" aria-label="Sections">
    <button class="tab active" data-panel="report" role="tab">Performance</button>
    <button class="tab" data-panel="story" role="tab">Our Story</button>
    <button class="tab" data-panel="book" role="tab">The Book</button>
    <button class="tab" data-panel="approach" role="tab">Approach</button>
    <button class="tab" data-panel="concepts" role="tab">Concepts</button>
  </nav>
  <div class="panel active" id="panel-report">
  <div class="perfgrid">
  <div>
  <section aria-label="Headline returns"><div class="stats" id="stats"></div></section>
  <p class="asofline">Figures as of <b id="asof"></b></p>
  <section aria-label="Cumulative return">
    <p class="eyebrow">Return Curve</p>
    <div class="chart-card">
      <div class="chart-head"><h2>Cumulative return</h2><span class="sub" id="curvesub"></span></div>
      <div class="tlviews" id="tlviews" role="tablist" aria-label="Timeline range"></div>
      <canvas id="curve" role="img" aria-label="Cumulative time-weighted return over the selected timeline."></canvas>
      <div class="ctip" id="ctip"></div>
      <div class="marks" id="marks"></div>
    </div>
  </section>
  </div>
  <div>
  <section aria-label="Weekly report card">
    <p class="eyebrow">Weekly Report Card</p>
    <div class="rc-head" id="rchead"></div>
    <div class="dials" id="dials"></div>
    <p class="rc-note" id="rcnote"></p>
    <p class="hlabel">Grade history — select a week to read its card</p>
    <div class="hist" id="hist"></div>
  </section>
  </div>
  </div>
  <section aria-label="Career trading stats">
    <p class="eyebrow">Career Ledger · Cumulative</p>
    <h2>The record since inception</h2>
    <p class="tag" style="margin-top:6px" id="careersub"></p>
    <div class="stats" id="careerstats"></div>
    <div class="dials" id="careerbuckets" style="margin-top:14px"></div>
  </section>
  <section aria-label="Observations beyond the weekly cards">
    <p class="eyebrow">Between the Report Cards</p>
    <h2>What the weekly grades don't show</h2>
    <ul class="proselist" id="careerinsights"></ul>
    <p class="rc-note" id="careermeth"></p>
  </section>
  </div>
  <div class="panel" id="panel-book">
  <div id="booksummary"></div>
  <div class="bookgrid">
  <section aria-label="Allocation">
    <p class="eyebrow">The Book · Allocation by Weight</p>
    <h2>Where the capital sits</h2>
    <p class="tag" style="margin-top:6px;margin-bottom:18px">Weights as a share of net asset value. Totals may run slightly over 100% — modest margin.</p>
    <div class="bars" id="bars"></div>
    <div class="legend-strat">
      <span><i class="swatch" style="background:var(--accent)"></i>Wheel — covered-call equities</span>
      <span><i class="swatch" style="background:var(--slate)"></i>Directional — outright</span>
      <span><i class="swatch" style="background:var(--faint)"></i>Cash</span>
    </div>
  </section>
  <section aria-label="Holdings">
    <p class="eyebrow">Holdings</p>
    <div class="tablewrap"><table><thead><tr><th>Ticker</th><th>Strategy</th><th class="r">Weight</th><th class="r">Position return</th></tr></thead><tbody id="ledger"></tbody></table></div>
  </section>
  </div>
  </div>
  <div class="panel" id="panel-approach">
  <section aria-label="Approach">
    <p class="eyebrow">Approach</p>
    <h2>How the book is run</h2>
    <div class="cards" style="margin-top:16px">
      <div class="appr"><h3><span class="idx">A</span>The Wheel</h3><p>The engine. Own retail-momentum names and sell calls against them, laddering expiries and buying back cheap. Premium is the recurring return; the shares are the collateral.</p></div>
      <div class="appr"><h3><span class="idx">B</span>Event contracts <span class="tag">retired</span></h3><p>Short-dated, defined-risk positions on crypto ranges, FX fixings, and index closes. The sleeve was wound down in August 2026 — it accounted for most of the account's activity and almost none of its return. Nothing is open.</p></div>
      <div class="appr"><h3><span class="idx">C</span>Directional</h3><p>Selective outright holds with a written thesis and a hard stop. Used sparingly — conviction is sized, not indulged.</p></div>
    </div>
    <p class="tag" style="margin-top:16px">Risk framework: per-name position limits, a cash buffer, package-level stop-losses, and active drawdown management — the discipline that protects the engine from the punts.</p>
  </section>
  <div id="page-discipline-inline"></div>
  <section aria-label="Mandate and constraints">
    <p class="eyebrow">Mandate &amp; Constraints</p>
    <h2 id="con-title"></h2>
    <div class="con" id="con"></div>
    <p class="rc-note" id="connote"></p>
  </section>
  </div>
  <div class="panel" id="panel-concepts"></div>
  <div class="panel" id="panel-story"></div>
  <footer>
    <p>Figures are time-weighted returns and portfolio weights. Absolute balances, share counts, and dollar P&amp;L are withheld by design — transparent on performance, discreet on size.</p>
    <p class="meth">PAREIDOLIA LLC · PRIVATE BOOK · FOR REVIEW ONLY · NOT AN OFFERING OR SOLICITATION · PAST PERFORMANCE IS NOT INDICATIVE OF FUTURE RESULTS</p>
  </footer>
</div></div>
<script>
(function(){
  "use strict";
  var DATA = __DATA_JSON__;
  var MONTHS=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  var css=function(n){return getComputedStyle(document.documentElement).getPropertyValue(n).trim();};
  var fmt=function(v){return (v>=0?"+":"−")+Math.abs(v).toFixed(2)+"%";};
  var cls=function(v){return v>=0?"pos":"neg";};

  document.getElementById("asof").textContent=DATA.asOf;
  var dl=document.getElementById("dlDate"); if(dl) dl.textContent=DATA.asOf;
  document.getElementById("curvesub").textContent=DATA.curveLabel;

  (function(){
    var el=document.getElementById("stats");
    DATA.returns.forEach(function(s){
      var d=document.createElement("div"); d.className="stat";
      d.innerHTML='<div class="k">'+s.k+'</div><div class="v '+cls(s.v)+'">'+fmt(s.v)+'</div><div class="m">'+s.m+'</div>';
      el.appendChild(d);
    });
  })();

  (function(){
    var reports=DATA.reports; if(!reports||!reports.length) return;
    var head=document.getElementById("rchead"), dl=document.getElementById("dials"),
        note=document.getElementById("rcnote"), strip=document.getElementById("hist");
    function gcol(g){var t=g.charAt(0);return (t==="A")?"var(--up)":(t==="B")?"var(--accent)":(t==="C")?"var(--warn)":"var(--down)";}
    function card(rc){
      var c=gcol(rc.grade);
      head.innerHTML='<div class="grade" style="border-color:'+c+';color:'+c+'">'+rc.grade+'</div>'+
        '<div><div class="wk">'+rc.weekLabel+'</div>'+
        '<div class="wk">Return this week <span class="wkret '+cls(rc.weekRet)+'">'+fmt(rc.weekRet)+'</span></div></div>';
      dl.innerHTML="";
      rc.dials.forEach(function(d){
        var lbl={pass:"Pass",warn:"Watch",fail:"Breach"}[d.state];
        var el=document.createElement("div"); el.className="dial "+d.state;
        el.innerHTML='<div class="dk">'+d.key+'</div><div><span class="state '+d.state+'">'+lbl+'</span></div>'+
          '<div class="dv">'+d.value+'</div><div class="rule">'+d.rule+'</div>';
        dl.appendChild(el);
      });
      note.innerHTML='<b>Read:</b> '+rc.note;
    }
    function chips(active){
      strip.innerHTML="";
      reports.forEach(function(x,i){
        var b=document.createElement("button"); b.type="button"; b.className="gcard"+(i===active?" active":"");
        b.setAttribute("aria-label",x.weekLabel+", grade "+x.grade);
        b.innerHTML='<div class="gw">'+x.w+'</div><div class="gg" style="color:'+gcol(x.grade)+'">'+x.grade+'</div>'+
          '<div class="gr '+cls(x.weekRet)+'">'+fmt(x.weekRet)+'</div>'+(x.now?'<div class="gnow">now</div>':'');
        b.addEventListener("click",function(){ pick(i); });
        strip.appendChild(b);
      });
    }
    function pick(i){ card(reports[i]); chips(i); }
    var def=0; reports.forEach(function(x,i){ if(x.now) def=i; });
    pick(def);
  })();

  (function(){
    var c=DATA.career; if(!c) return;
    document.getElementById("careersub").textContent=
      "Realized, closed-trade record since inception ("+c.sinceLabel+") — every closing execution, deduplicated. "+
      "Refreshed with the weekly report card. Figures through "+c.asOfLabel+".";
    var st=document.getElementById("careerstats");
    c.headline.forEach(function(s){
      var d=document.createElement("div"); d.className="stat";
      d.innerHTML='<div class="k">'+s.k+'</div><div class="v">'+s.v+'</div><div class="m">'+s.m+'</div>';
      st.appendChild(d);
    });
    var TONE={up:"pass",warn:"warn",down:"fail"};
    var bk=document.getElementById("careerbuckets");
    c.buckets.forEach(function(b){
      var el=document.createElement("div"); el.className="dial "+(TONE[b.tone]||"");
      el.innerHTML='<div class="dk">'+b.name+'</div>'+
        '<div class="dv">'+b.win.toFixed(0)+'% win · '+b.pf.toFixed(2)+' PF</div>'+
        '<div class="rule">'+b.closes.toLocaleString("en-US")+' closes — '+b.note+'</div>';
      bk.appendChild(el);
    });
    var ul=document.getElementById("careerinsights");
    c.insights.forEach(function(x){
      var li=document.createElement("li"); li.textContent=x; ul.appendChild(li);
    });
    document.getElementById("careermeth").innerHTML=
      '<b>Method:</b> Counted per realized closing execution across the full account history, brokerage-reported. '+
      'Dollar figures are withheld by design — rates, ratios, and counts only.';
  })();

  (function(){
    var wrap=document.getElementById("bars");
    var max=Math.max.apply(null,DATA.positions.map(function(p){return p.w;}));
    DATA.positions.forEach(function(p){
      var col=p.s==="wheel"?"var(--accent)":p.s==="dir"?"var(--slate)":"var(--faint)";
      var row=document.createElement("div"); row.className="bar";
      row.innerHTML='<div class="name">'+p.t+'</div><div class="track"><div class="fill" data-w="'+(p.w/max)+'" style="background:'+col+'"></div></div><div class="pct">'+p.w.toFixed(1)+'%</div>';
      wrap.appendChild(row);
    });
    window.__animBars=function(){
      Array.prototype.forEach.call(wrap.querySelectorAll(".fill"),function(f){
        f.style.transform="scaleX(0)";
        requestAnimationFrame(function(){requestAnimationFrame(function(){f.style.transform="scaleX("+f.getAttribute("data-w")+")";});});
      });
    };
    window.__animBars();
  })();

  (function(){
    var tb=document.getElementById("ledger");
    var CHIP={wheel:'<span class="chip wheel">Wheel</span>',dir:'<span class="chip dir">Directional</span>',cash:'<span class="chip">Cash</span>',event:'<span class="chip">Event</span>'};
    DATA.positions.forEach(function(p){
      var ret=(p.r===null)?'<td class="num r" style="color:var(--faint)">—</td>':'<td class="num r '+cls(p.r)+'">'+fmt(p.r)+'</td>';
      var tr=document.createElement("tr");
      tr.innerHTML='<td class="tk">'+p.t+'</td><td>'+(CHIP[p.s]||'')+'</td><td class="num r">'+p.w.toFixed(1)+'%</td>'+ret;
      tb.appendChild(tr);
    });
  })();

  (function(){
    var c=DATA.constraints; if(!c) return;
    document.getElementById("con-title").textContent=c.title;
    document.getElementById("con").innerHTML=
      '<div class="box ok"><h4>Permitted</h4><ul>'+c.permitted.map(function(x){return "<li>"+x+"</li>";}).join("")+'</ul></div>'+
      '<div class="box no"><h4>Restricted by broker</h4><ul>'+c.restricted.map(function(x){return "<li>"+x+"</li>";}).join("")+'</ul></div>';
    document.getElementById("connote").innerHTML='<b>Note:</b> '+c.note;
  })();

  (function(){
    function blocks(el, arr){
      if(!el||!arr) return;
      arr.forEach(function(b){
        var s=document.createElement("section"), h="";
        if(b.eyebrow) h+='<p class="eyebrow">'+b.eyebrow+'</p>';
        if(b.h) h+='<h2>'+b.h+'</h2>';
        if(b.p) b.p.forEach(function(x){ h+='<p class="prose">'+x+'</p>'; });
        if(b.ul) h+='<ul class="proselist">'+b.ul.map(function(x){return "<li>"+x+"</li>";}).join("")+'</ul>';
        s.innerHTML=h; el.appendChild(s);
      });
    }
    blocks(document.getElementById("booksummary"), DATA.book);
    var pg=DATA.pages||{};
    blocks(document.getElementById("panel-concepts"), pg.concepts);
    blocks(document.getElementById("page-discipline-inline"), pg.discipline);
    blocks(document.getElementById("panel-story"), pg.story);
  })();

  var ALLC=DATA.curve.cps, ALLD=DATA.curve.dates, cv=document.getElementById("curve"), ctx=cv.getContext("2d");
  var reduce=window.matchMedia("(prefers-reduced-motion:reduce)").matches;
  var marksEl=document.getElementById("marks"), subEl=document.getElementById("curvesub");
  var vals=[], D=[], yMin=0, yMax=0, hoverIdx=-1, curGran="month";
  var PADL=8,PADR=44,PADT=14,PADB=22, tip=document.getElementById("ctip");
  function ticks(){
    var o=[];
    if(curGran==="day"){
      for(var i=0;i<D.length;i++){o.push({i:i,label:MONTHS[parseInt(D[i].slice(4,6),10)-1]+" "+parseInt(D[i].slice(6,8),10)});}
      return o;
    }
    var seen={};
    for(var j=0;j<D.length;j++){var yy=D[j].slice(2,4),mm=D[j].slice(4,6),m=parseInt(mm,10),k=yy+mm;
      if(!seen[k]){seen[k]=1;o.push({i:j,label:MONTHS[m-1]+(m===1?" '"+yy:"")});}}
    return o;
  }
  function draw(p){
    var dpr=window.devicePixelRatio||1, W=cv.clientWidth, H=cv.clientHeight;
    cv.width=W*dpr; cv.height=H*dpr; ctx.setTransform(dpr,0,0,dpr,0,0); ctx.clearRect(0,0,W,H);
    var padL=PADL,padR=PADR,padT=PADT,padB=PADB, n=vals.length;
    var mut=css("--muted"),grid=css("--grid"),acc=css("--accent"),dn=css("--down");
    var X=function(i){return padL+(n<2?0.5:i/(n-1))*(W-padL-padR);};
    var Y=function(v){return padT+(1-(v-yMin)/(yMax-yMin))*(H-padT-padB);};
    ctx.font="11px "+css("--mono"); ctx.textBaseline="middle";
    var step=(yMax-yMin)/4;
    for(var g=yMin; g<=yMax+0.001; g+=step){
      var y=Y(g); ctx.strokeStyle=grid; ctx.lineWidth=1;
      ctx.beginPath(); ctx.moveTo(padL,y); ctx.lineTo(W-padR,y); ctx.stroke();
      ctx.fillStyle=mut; ctx.textAlign="left"; ctx.fillText((g>0?"+":"")+Math.round(g)+"%", W-padR+7, y);
    }
    var z0=Y(0); ctx.strokeStyle=mut; ctx.lineWidth=1.25; ctx.beginPath(); ctx.moveTo(padL,z0); ctx.lineTo(W-padR,z0); ctx.stroke();
    ctx.textAlign="left"; ctx.textBaseline="middle"; ctx.fillStyle=mut; ctx.fillText("0%", W-padR+7, z0);
    ctx.textAlign="center"; ctx.textBaseline="alphabetic"; ctx.fillStyle=mut;
    var tk=ticks(), prevR=-1e9;
    for(var ti=0;ti<tk.length;ti++){
      var tx=X(tk[ti].i), tw=ctx.measureText(tk[ti].label).width,
          al=(ti===0)?"left":(ti===tk.length-1?"right":"center"),
          le=(al==="left")?tx:(al==="right")?tx-tw:tx-tw/2;
      if(le>=prevR+8){ ctx.textAlign=al; ctx.fillText(tk[ti].label, tx, H-5); prevR=le+tw; }
    }
    var last=Math.max(1,Math.floor(n*p)), zeroY=Y(0);
    var grad=ctx.createLinearGradient(0,padT,0,H-padB); grad.addColorStop(0,acc+"33"); grad.addColorStop(1,acc+"05");
    ctx.beginPath(); ctx.moveTo(X(0),zeroY);
    for(var i=0;i<last;i++){ctx.lineTo(X(i),Y(vals[i]));}
    ctx.lineTo(X(last-1),zeroY); ctx.closePath(); ctx.fillStyle=grad; ctx.fill();
    ctx.beginPath();
    for(var j=0;j<last;j++){var xx=X(j),yy=Y(vals[j]); j?ctx.lineTo(xx,yy):ctx.moveTo(xx,yy);}
    ctx.strokeStyle=acc; ctx.lineWidth=2; ctx.lineJoin="round"; ctx.stroke();
    if(p>=1){var ex=X(n-1),ey=Y(vals[n-1]); ctx.beginPath(); ctx.arc(ex,ey,4,0,Math.PI*2); ctx.fillStyle=css("--bg"); ctx.fill(); ctx.lineWidth=2; ctx.strokeStyle=dn; ctx.stroke();}
    if(hoverIdx>=0 && hoverIdx<n){
      var hx=X(hoverIdx), hy=Y(vals[hoverIdx]);
      ctx.setLineDash([3,3]); ctx.strokeStyle=css("--faint"); ctx.lineWidth=1;
      ctx.beginPath(); ctx.moveTo(hx,padT); ctx.lineTo(hx,H-padB); ctx.stroke(); ctx.setLineDash([]);
      ctx.beginPath(); ctx.arc(hx,hy,4.5,0,Math.PI*2); ctx.fillStyle=acc; ctx.fill();
      ctx.lineWidth=1.5; ctx.strokeStyle=css("--bg"); ctx.stroke();
    }
  }
  var start=null,DUR=850;
  function anim(ts){if(start===null)start=ts;var p=Math.min(1,(ts-start)/DUR);draw(p);if(p<1)requestAnimationFrame(anim);}
  function render(){ start=null; if(reduce){draw(1);}else{requestAnimationFrame(anim);} }
  window.__drawCurve=function(){draw(1);};
  function setView(v){
    hoverIdx=-1; if(tip){tip.style.display="none";}
    curGran=v.gran||"month";
    var base=ALLC[v.startIdx];
    D=ALLD.slice(v.startIdx);
    vals=ALLC.slice(v.startIdx).map(function(c){return ((1+c)/(1+base)-1)*100;});
    var lo=Math.min.apply(null,vals), hi=Math.max.apply(null,vals);
    yMin=Math.floor((lo-2)/5)*5; yMax=Math.ceil((hi+2)/5)*5; if(yMin===yMax){yMin-=5;yMax+=5;}
    marksEl.innerHTML='<span><i class="swatch" style="background:var(--up)"></i>Peak <b>'+fmt(hi)+'</b></span>'+
      '<span><i class="swatch" style="background:var(--down)"></i>Trough <b>'+fmt(lo)+'</b></span>'+
      '<span><i class="swatch" style="background:var(--accent)"></i>Current <b>'+fmt(vals[vals.length-1])+'</b></span>';
    if(subEl){ subEl.textContent="Time-weighted · "+v.sub; }
    render();
  }
  (function(){
    function idxFrom(th){for(var i=0;i<ALLD.length;i++){if(parseInt(ALLD[i],10)>=th)return i;}return ALLD.length-1;}
    function mBack(n){var d=ALLD[ALLD.length-1],y=parseInt(d.slice(0,4),10),m=parseInt(d.slice(4,6),10)-n;while(m<1){m+=12;y-=1;}return y*10000+m*100+1;}
    function dBack(n){var d=ALLD[ALLD.length-1],dt=new Date(parseInt(d.slice(0,4),10),parseInt(d.slice(4,6),10)-1,parseInt(d.slice(6,8),10));dt.setDate(dt.getDate()-n);return dt.getFullYear()*10000+(dt.getMonth()+1)*100+dt.getDate();}
    var VIEWS=[
      {label:"Inception",startIdx:0,sub:"Since inception, Oct 2025"},
      {label:"1Y",startIdx:idxFrom(mBack(12)),sub:"Trailing 12 months"},
      {label:"YTD",startIdx:idxFrom(20260101),sub:"Year to date, 2026"},
      {label:"6M",startIdx:idxFrom(mBack(6)),sub:"Trailing 6 months"},
      {label:"3M",startIdx:idxFrom(mBack(3)),sub:"Trailing 3 months"},
      {label:"1M",startIdx:idxFrom(mBack(1)),sub:"Trailing month",gran:"day"},
      {label:"45D",startIdx:idxFrom(dBack(45)),sub:"Trailing 45 days",gran:"day"},
      {label:"21D",startIdx:idxFrom(dBack(21)),sub:"Trailing 21 days",gran:"day"},
      {label:"7D",startIdx:idxFrom(dBack(7)),sub:"Trailing 7 days",gran:"day"},
      {label:"1D",startIdx:Math.max(0,ALLD.length-2),sub:"Latest trading day",gran:"day"}
    ];
    var host=document.getElementById("tlviews");
    VIEWS.forEach(function(v,i){
      var b=document.createElement("button"); b.type="button"; b.className="tlv"+(i===0?" active":""); b.textContent=v.label;
      b.addEventListener("click",function(){
        Array.prototype.forEach.call(host.children,function(c){c.classList.remove("active");});
        b.classList.add("active"); setView(v);
      });
      host.appendChild(b);
    });
    setView(VIEWS[0]);
  })();
  function fmtDate(s){return MONTHS[parseInt(s.slice(4,6),10)-1]+" "+parseInt(s.slice(6,8),10)+" '"+s.slice(2,4);}
  function tipAt(idx){
    var W=cv.clientWidth,H=cv.clientHeight,n=vals.length,plotW=W-PADL-PADR;
    var x=PADL+(n<2?0.5:idx/(n-1))*plotW, y=PADT+(1-(vals[idx]-yMin)/(yMax-yMin))*(H-PADT-PADB);
    tip.innerHTML='<span class="tdate">'+fmtDate(D[idx])+'</span><span class="tval '+cls(vals[idx])+'">'+fmt(vals[idx])+'</span>';
    tip.style.display="block"; tip.style.left=(cv.offsetLeft+x)+"px"; tip.style.top=(cv.offsetTop+y-12)+"px";
  }
  if(tip){
    cv.addEventListener("mousemove",function(e){
      var n=vals.length; if(!n) return;
      var plotW=cv.clientWidth-PADL-PADR;
      var idx=(n<2)?n-1:Math.round(((e.offsetX-PADL)/plotW)*(n-1));
      idx=Math.max(0,Math.min(n-1,idx));
      hoverIdx=idx; draw(1); tipAt(idx);
    });
    cv.addEventListener("mouseleave",function(){ hoverIdx=-1; draw(1); tip.style.display="none"; });
  }
  var rt; window.addEventListener("resize",function(){clearTimeout(rt);rt=setTimeout(function(){draw(1);},120);});
  new MutationObserver(function(){draw(1);}).observe(document.documentElement,{attributes:true,attributeFilter:["data-theme"]});
  if(window.matchMedia){window.matchMedia("(prefers-color-scheme:dark)").addEventListener("change",function(){draw(1);});}

  (function(){
    var tabs=Array.prototype.slice.call(document.querySelectorAll(".tab"));
    var ids=["report","book","approach","concepts","story"];
    var panels={}; ids.forEach(function(id){panels[id]=document.getElementById("panel-"+id);});
    function activate(id){
      tabs.forEach(function(t){t.classList.toggle("active",t.getAttribute("data-panel")===id);});
      ids.forEach(function(k){panels[k].classList.toggle("active",k===id);});
      if(id==="report" && window.__drawCurve) window.__drawCurve();
      if(id==="book" && window.__animBars) window.__animBars();
      window.scrollTo(0,0);
    }
    tabs.forEach(function(t){t.addEventListener("click",function(){activate(t.getAttribute("data-panel"));});});
  })();
})();
</script></body></html>"""

html = TEMPLATE.replace("__DATA_JSON__", json.dumps(data, ensure_ascii=False))
with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)
print("built index.html (" + str(len(html)) + " bytes) from data.json")
