# -*- coding: utf-8 -*-
"""Pareidolia book — static site generator.
Reads data.json, writes index.html (served by GitHub Pages).
Weekly refresh = overwrite data.json with a fresh broker pull, then run this."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(HERE, "data.json"), encoding="utf-8"))

# The career ledger ships with the weekly report card, so it must carry the same
# date as the rest of the page. Refusing to build is the whole point: it catches
# a refresh that updated the returns and the card but skipped the career step.
_career_as_of = data.get("career", {}).get("asOfLabel")
if _career_as_of != data.get("asOf"):
    sys.exit(
        "career ledger is out of step with the page: career.asOfLabel is %r but "
        "asOf is %r.\nRe-pull the trade dumps and run:\n"
        "    python career_stats.py --write ../data/trades_ytd_2026.json ../data/trades_q4_2025.json"
        % (_career_as_of, data.get("asOf")))

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
  .dials{display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:14px}
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
  .hnote{font-family:var(--serif); font-style:italic; font-size:12.5px; color:var(--muted); margin:0 0 10px; line-height:1.55}
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
  .gcard.recon{opacity:.72; border-style:dashed}
  .gcard.recon:hover,.gcard.recon.active{opacity:1}
  .grecon{font-family:var(--mono); font-size:8px; letter-spacing:.1em; text-transform:uppercase; color:var(--muted); margin-top:3px}
  .rbadge{display:inline-block; font-family:var(--mono); font-size:9px; letter-spacing:.12em; text-transform:uppercase; color:var(--muted); border:1px solid var(--line); padding:3px 8px; margin-top:6px}
  .rbasis{font-family:var(--serif); font-style:italic; font-size:12.5px; color:var(--muted); margin-top:10px; line-height:1.55}
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
  #panel-record .bookgrid{grid-template-columns:repeat(auto-fit,minmax(270px,1fr))}
  #panel-record table{min-width:0}
  #panel-record .stats{grid-template-columns:repeat(auto-fit,minmax(210px,1fr))}
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
  .appr{background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:18px 18px 16px; display:flex; flex-direction:column}
  .appr h3{font-family:var(--serif); font-size:16px; margin:0 0 8px; font-weight:600}
  .appr h3 .idx{font-family:var(--mono); font-size:11px; color:var(--accent); margin-right:8px; letter-spacing:.05em}
  .appr p{margin:0; font-size:13px; color:var(--muted); line-height:1.55}
  .appr p:not(.ctl){padding-bottom:13px}
  .appr .ctl{margin-top:auto; padding-top:9px; border-top:1px solid var(--line); font-family:var(--mono); font-size:10.5px; letter-spacing:.09em; text-transform:uppercase; color:var(--muted)}
  .appr .ctl b{color:var(--accent); font-weight:600}
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

  /* Futuresight */
  .fs-note{border-left:2px solid var(--accent); padding:2px 0 2px 14px; color:var(--muted); font-size:13px; max-width:66ch; margin:16px auto; text-align:left}
  .fs-legend{display:flex; flex-wrap:wrap; gap:6px; margin:16px 0 6px; justify-content:center}
  .fs-fc{display:inline-flex; align-items:center; gap:7px; font-family:var(--mono); font-size:10.5px; letter-spacing:.06em; text-transform:uppercase; padding:5px 10px; border:1px solid var(--line); background:none; color:var(--muted); cursor:pointer}
  .fs-fc .sw{width:9px; height:9px; flex:none}
  .fs-fc:hover{border-color:var(--accent); color:var(--ink)}
  .fs-fc.active{background:var(--accent-soft); border-color:var(--accent); color:var(--ink)}
  .fs-fc:focus-visible{outline:2px solid var(--accent); outline-offset:2px}
  .fsview{display:none}
  .fsview.active{display:block}
  canvas#fscurve{display:block; width:100%; height:280px; margin-top:6px}
  .fs-corrwrap{overflow-x:auto; margin-top:10px}
  table.fs-corr{border-collapse:collapse; font-family:var(--mono); font-size:11px; min-width:520px}
  table.fs-corr td,table.fs-corr th{padding:7px 8px; text-align:center; border:1px solid var(--line); font-variant-numeric:tabular-nums}
  table.fs-corr th{font-weight:500; color:var(--muted); font-size:9.5px; letter-spacing:.06em; text-transform:uppercase; background:var(--panel-2)}
  table.fs-corr th.rh{text-align:right}
  .fs-ind{font-family:var(--mono); font-size:10px; color:var(--faint); letter-spacing:.06em; text-transform:uppercase}
  .fs-tier{display:inline-block; font-family:var(--mono); font-size:9.5px; letter-spacing:.06em; text-transform:uppercase; border:1px solid var(--line); padding:1px 5px; color:var(--muted); margin-left:7px}
  .fs-sw{display:inline-block; width:8px; height:8px; margin-right:6px; vertical-align:1px}
  #fsNames td:nth-child(4),#fsMovers td:nth-child(3),#fsFactors td:nth-child(1),#fsIndustries td:nth-child(3){white-space:nowrap}
  .fs-kicker{color:var(--muted); font-size:13px; max-width:64ch; margin:8px auto 0; font-style:italic}
  .fs-search{font-family:var(--mono); font-size:11.5px; padding:7px 10px; border:1px solid var(--line); background:var(--panel); color:var(--ink); min-width:220px; margin:14px 0 4px}
  .fs-search:focus-visible{outline:2px solid var(--accent); outline-offset:1px}
  .fs-sort{font:inherit; color:inherit; background:none; border:0; padding:0; cursor:pointer; letter-spacing:inherit; text-transform:inherit; display:inline-flex; align-items:center; gap:5px}
  .fs-sort:hover{color:var(--accent)}
  .fs-sort:focus-visible{outline:2px solid var(--accent); outline-offset:2px}
  .fs-sort .ar{font-size:8px; opacity:0; transition:opacity .12s}
  .fs-sort.on{color:var(--accent)}
  .fs-sort.on .ar{opacity:1}
  .fs-untracked{color:var(--faint); font-style:italic}
  .fs-cover{font-family:var(--mono); font-size:10.5px; color:var(--faint); letter-spacing:.05em; margin-top:10px}
</style></head>
<body>
<div class="wrap"><div class="sheet">
  <header class="masthead">
    <div>
      <div class="mark">Pareidolia<span class="dot">.</span></div>
      <div class="tag">A private book run under doctrine — pattern recognition in a hostile tape.</div>
    </div>
  </header>
  <div class="dateline"><span>Pareidolia LLC</span><span><b id="dlDate"></b></span><span>Est. October 2025</span></div>
  <nav class="tabs" role="tablist" aria-label="Sections">
    <button class="tab active" data-panel="report" role="tab">Performance</button>
    <button class="tab" data-panel="story" role="tab">Origin</button>
    <button class="tab" data-panel="book" role="tab">The Book</button>
    <button class="tab" data-panel="approach" role="tab">Operations</button>
    <button class="tab" data-panel="concepts" role="tab">Doctrine</button>
    <button class="tab" data-panel="record" role="tab">Best &amp; Worst</button>
    <button class="tab" data-panel="futuresight" role="tab">Ideation</button>
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
    <p class="eyebrow">Weekly After-Action</p>
    <div class="rc-head" id="rchead"></div>
    <div class="dials" id="dials"></div>
    <p class="rc-note" id="rcnote"></p>
    <p class="hlabel">Prior after-actions — select a week to read the full report</p>
    <p class="hnote">Dashed cards were rebuilt from the trade record after the fact; solid cards were graded live that week.</p>
    <div class="hist" id="hist"></div>
  </section>
  </div>
  </div>
  <section aria-label="Career trading stats">
    <p class="eyebrow">Service Record · Cumulative</p>
    <h2>Every engagement, booked</h2>
    <p class="tag" style="margin-top:6px" id="careersub"></p>
    <div class="stats" id="careerstats"></div>
    <div class="dials" id="careerbuckets" style="margin-top:14px"></div>
  </section>
  <section aria-label="Observations beyond the weekly cards">
    <p class="eyebrow">Between the After-Actions</p>
    <h2>What the weekly grade doesn't show</h2>
    <ul class="proselist" id="careerinsights"></ul>
    <p class="rc-note" id="careermeth"></p>
  </section>
  </div>
  <div class="panel" id="panel-book">
  <div id="booksummary"></div>
  <div class="bookgrid">
  <section aria-label="Allocation">
    <p class="eyebrow">The Book · Allocation by Weight</p>
    <h2>Where the capital is committed</h2>
    <p class="tag" style="margin-top:6px;margin-bottom:18px">Weights as a share of net asset value. Totals may exceed 100% when margin is in use.</p>
    <div class="bars" id="bars"></div>
    <div class="legend-strat">
      <span><i class="swatch" style="background:var(--accent)"></i>Wheel — covered-call securities</span>
      <span><i class="swatch" style="background:var(--slate)"></i>Outright — held, not collateralized</span>
      <span><i class="swatch" style="background:var(--faint)"></i>Cash</span>
    </div>
  </section>
  <section aria-label="Holdings">
    <p class="eyebrow">Positions</p>
    <div class="tablewrap"><table><thead><tr><th>Ticker</th><th>Strategy</th><th class="r">Weight</th><th class="r">Position return</th></tr></thead><tbody id="ledger"></tbody></table></div>
  </section>
  </div>
  </div>
  <div class="panel" id="panel-approach">
  <section aria-label="Approach">
    <p class="eyebrow">Operations</p>
    <h2>How the book is run</h2>
    <div class="cards" style="margin-top:16px">
      <div class="appr"><h3><span class="idx">A</span>The Wheel</h3><p>The engine. Own liquid retail-momentum names and sell calls against them, laddering expiries and buying the contracts back cheap. Premium is the carry; the shares are collateral that earns while it waits.</p><p class="ctl"><b>Limit</b> · 20% of NAV per name · tested weekly</p></div>
      <div class="appr"><h3><span class="idx">B</span>Event contracts <span class="tag">wound down</span></h3><p>Short-dated, defined-risk positions on crypto ranges, FX fixings, and index closes. Closed out in August 2026 — the sleeve carried most of the account's turnover and almost none of its P&amp;L. Turnover is not edge. The book is flat here.</p><p class="ctl"><b>Status</b> · closed · no exposure since Aug 6, 2026</p></div>
      <div class="appr"><h3><span class="idx">C</span>Outright</h3><p>Risk taken directly, and taken rarely — investments rather than trades. Held and not collateralized, so no calls are written against them. The thesis comes before the size, and conviction gets expressed in the position, never talked up after the fill.</p><p class="ctl"><b>Control</b> · thesis before size · held, not collateralized</p></div>
    </div>
    <p class="tag" style="margin-top:16px">Control framework: a hard 20% per-name limit, a 10% cash floor, stops marked before entry, and drawdowns cut rather than nursed. The limits are hard, not advisory — a breach is written into the weekly after-action whether or not the week made money.</p>
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
  <div class="panel" id="panel-record">
  <section aria-label="Accolades">
    <p class="eyebrow">Accolades</p>
    <h2>What went right</h2>
    <div class="stats" id="accolades"></div>
  </section>
  <section aria-label="Failures">
    <p class="eyebrow">Failures</p>
    <h2>What went wrong</h2>
    <div class="stats" id="failures"></div>
  </section>
  <section aria-label="Discipline record">
    <p class="eyebrow">Discipline · the tally</p>
    <h2>How often the limits actually held</h2>
    <div class="stats" id="disc"></div>
  </section>
  <div class="bookgrid">
  <section aria-label="Best executions">
    <p class="eyebrow">Best closes</p>
    <div class="tablewrap"><table><thead><tr><th>Ticker</th><th>Date</th><th>Type</th><th class="r">Share of NAV</th></tr></thead><tbody id="twins"></tbody></table></div>
  </section>
  <section aria-label="Worst executions">
    <p class="eyebrow">Worst closes</p>
    <div class="tablewrap"><table><thead><tr><th>Ticker</th><th>Date</th><th>Type</th><th class="r">Share of NAV</th></tr></thead><tbody id="tlosses"></tbody></table></div>
  </section>
  </div>
  <section aria-label="Where money was made and lost">
    <p class="eyebrow">By name · shares of the whole record</p>
    <h2>Where the money was made and lost</h2>
    <div class="tablewrap"><table><thead><tr><th>Name</th><th class="r">Closes</th><th class="r">Win</th><th class="r">Profit factor</th><th class="r">Share of gains</th><th class="r">Share of losses</th></tr></thead><tbody id="nmtbl"></tbody></table></div>
  </section>
  <section aria-label="Event contracts by name">
    <p class="eyebrow">Event sleeve · by contract</p>
    <div class="tablewrap"><table><thead><tr><th>Contract</th><th class="r">Closes</th><th class="r">Win</th><th class="r">Profit factor</th><th class="r">Share of gains</th><th class="r">Share of losses</th></tr></thead><tbody id="evtbl"></tbody></table></div>
  </section>
  <section aria-label="How to read this">
    <p class="eyebrow">How to read this</p>
    <ul class="proselist" id="recnotes"></ul>
  </section>
  </div>
  <div class="panel" id="panel-futuresight">
    <div class="eyebrow">Concept 01 &middot; opened Aug 2026 &middot; forward-tracked</div>
    <h2>Futuresight Index</h2>
    <p class="fs-kicker">Ideation is where a thesis gets written down, weighted, and then held to a public record before any of it is traded. Futuresight is the first concept in the series.</p>
    <p class="prose">A thematic basket built from the technology that science fiction got specific about &mdash; autonomous weapons, machine intelligence, cyberware, brain interfaces, seabed mining, the data brokers, and the petrochemical layer underneath all of it. Every company is listed once, in the industry it plays into most, and tagged with the risk factor that actually moves its price.</p>
    <p class="fs-note">Calling it what it is: this is speculation, and a basket built on sentiment is closer to gambling than investing. The bet is that the story gets more expensive, not that the cash flows show up. Roughly one name in five has no earnings underneath it. Tracked forward from the open on <b id="fsIncept"></b> at fixed weights, with no trading and no hindsight. There is deliberately no backtest here: the roster was picked in August 2026 knowing what had already happened, so a historical curve would measure hindsight rather than skill.</p>
    <div class="tlviews" id="fsviews" role="tablist" aria-label="Futuresight views"></div>

    <div class="fsview active" id="fsv-concept">
      <div class="fs-legend" id="fsLegend"></div>
      <div class="tablewrap"><table><thead><tr><th>Industry</th><th>Names</th><th>Dominant factor</th><th class="r">Weight</th></tr></thead><tbody id="fsIndustries"></tbody></table></div>
      <p class="fs-cover" id="fsCoverage"></p>
    </div>

    <div class="fsview" id="fsv-names">
      <input type="search" class="fs-search" id="fsQ" placeholder="Search ticker, company, industry…" aria-label="Search the roster">
      <div class="tablewrap"><table><thead><tr id="fsHead"><th><button type="button" class="fs-sort" data-k="ticker">Ticker</button></th><th><button type="button" class="fs-sort" data-k="name">Company</button></th><th><button type="button" class="fs-sort" data-k="industry">Industry</button></th><th><button type="button" class="fs-sort" data-k="factor">Factor</button></th><th class="r"><button type="button" class="fs-sort" data-k="weight">Weight</button></th><th class="r"><button type="button" class="fs-sort" data-k="ret">Return</button></th></tr></thead><tbody id="fsNames"></tbody></table></div>
      <p class="fs-cover" id="fsNamesCount"></p>
    </div>

    <div class="fsview" id="fsv-track">
      <div class="stats" id="fsStats"></div>
      <div class="chart-card" style="margin-top:14px">
        <div class="chart-head"><h2>Index vs benchmarks</h2><span class="sub" id="fsCurveSub"></span></div>
        <canvas id="fscurve" role="img" aria-label="Futuresight index against SPY and QQQ since inception."></canvas>
      </div>
      <h3 style="margin-top:22px">Movers since inception</h3>
      <div class="tablewrap"><table><thead><tr><th>Ticker</th><th>Company</th><th>Factor</th><th class="r">Weight</th><th class="r">Return</th></tr></thead><tbody id="fsMovers"></tbody></table></div>
    </div>

    <div class="fsview" id="fsv-factors">
      <p class="prose">Seventeen industries collapse into eight factors. The matrix below is the honest reason that matters: it is computed on trailing daily history, because correlation measures how these move together rather than how well they were picked.</p>
      <div class="fs-corrwrap" id="fsCorr"></div>
      <h3 style="margin-top:22px">Factor groups since inception</h3>
      <div class="tablewrap"><table><thead><tr><th>Factor</th><th>Names</th><th class="r">Weight</th><th class="r">Return</th></tr></thead><tbody id="fsFactors"></tbody></table></div>
    </div>
  </div>
  <div class="panel" id="panel-story"></div>
  <footer>
    <p>Figures are time-weighted returns and portfolio weights. Absolute balances, share counts, and dollar P&amp;L are withheld by design — transparent on performance, silent on size.</p>
    <p class="meth">PAREIDOLIA LLC · PRIVATE BOOK · FOR REVIEW ONLY · NOT AN OFFERING OR SOLICITATION · PAST PERFORMANCE IS NOT INDICATIVE OF FUTURE RESULTS</p>
  </footer>
</div></div>
<script>
(function(){
  "use strict";
  var DATA = __DATA_JSON__;
  var FS = __FS_JSON__;
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
        '<div class="wk">Return this week <span class="wkret '+cls(rc.weekRet)+'">'+fmt(rc.weekRet)+'</span></div>'+
        (rc.recon?'<div class="rbadge">Reconstructed · not graded live</div>':'')+'</div>';
      dl.innerHTML="";
      rc.dials.forEach(function(d){
        var lbl={pass:"Pass",warn:"Watch",fail:"Breach"}[d.state];
        var el=document.createElement("div"); el.className="dial "+d.state;
        el.innerHTML='<div class="dk">'+d.key+'</div><div><span class="state '+d.state+'">'+lbl+'</span></div>'+
          '<div class="dv">'+d.value+'</div><div class="rule">'+d.rule+'</div>';
        dl.appendChild(el);
      });
      note.innerHTML='<b>Assessment:</b> '+rc.note+
        (rc.recon?'<div class="rbasis">Rebuilt after the fact from the executed trade record and weekly closing prices, not written that Friday. '+
        'Position size is measured; the cash line is inferred from how much of net asset value the equity book took up, '+
        'so it is stated as a bound rather than a figure. Where stock alone exceeded net asset value, the book was on margin '+
        'and the floor was breached beyond doubt.</div>':'');
    }
    function chips(active){
      strip.innerHTML="";
      reports.forEach(function(x,i){
        var b=document.createElement("button"); b.type="button"; b.className="gcard"+(i===active?" active":"");
        b.setAttribute("aria-label",x.weekLabel+", grade "+x.grade);
        b.className+=(x.recon?" recon":"");
        b.innerHTML='<div class="gw">'+x.w+'</div><div class="gg" style="color:'+gcol(x.grade)+'">'+x.grade+'</div>'+
          '<div class="gr '+cls(x.weekRet)+'">'+fmt(x.weekRet)+'</div>'+
          (x.now?'<div class="gnow">now</div>':(x.recon?'<div class="grecon">rebuilt</div>':''));
        b.addEventListener("click",function(){ pick(i); });
        strip.appendChild(b);
      });
    }
    function pick(i,scroll){ card(reports[i]); chips(i);
      var el=strip.children[i];
      if(el&&scroll!==false) el.scrollIntoView({block:"nearest",inline:"center"}); }
    var def=0; reports.forEach(function(x,i){ if(x.now) def=i; });
    pick(def);
  })();

  (function(){
    var c=DATA.career; if(!c) return;
    document.getElementById("careersub").textContent=
      "Realized record since inception ("+c.sinceLabel+") — every closing execution, deduplicated, wins and losses alike. "+
      "Filed with the weekly after-action. Figures through "+c.asOfLabel+".";
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
    var R=DATA.record; if(!R) return;
    function tiles(id,arr){
      var el=document.getElementById(id); if(!el) return;
      arr.forEach(function(x){
        var v=document.createElement("div"); v.className="stat";
        var c = x.v.charAt(0)==="+" ? "pos" : (x.v.charAt(0)==="−"||x.v.charAt(0)==="-") ? "neg" : "";
        v.innerHTML='<div class="k">'+x.k+'</div><div class="v '+c+'">'+x.v+'</div><div class="m">'+x.m+'</div>';
        el.appendChild(v);
      });
    }
    tiles("accolades",R.accolades); tiles("failures",R.failures); tiles("disc",R.discipline);
    function trows(id,arr){
      var tb=document.getElementById(id); if(!tb) return;
      arr.forEach(function(x){
        var tr=document.createElement("tr");
        tr.innerHTML='<td class="tk">'+x.t+'</td><td>'+x.d+'</td><td>'+x.s+'</td>'+
          '<td class="num r '+cls(parseFloat(x.v))+'">'+x.v+'</td>';
        tb.appendChild(tr);
      });
    }
    trows("twins",R.wins); trows("tlosses",R.losses);
    function nrows(id,arr){
      var tb=document.getElementById(id); if(!tb) return;
      arr.forEach(function(x){
        var pf = (x.pf===null||x.pf>50) ? "—" : x.pf.toFixed(2);
        var tr=document.createElement("tr");
        tr.innerHTML='<td class="tk">'+x.t+'</td><td class="num r">'+x.closes+'</td>'+
          '<td class="num r">'+x.win+'%</td><td class="num r">'+pf+'</td>'+
          '<td class="num r pos">'+x.g.toFixed(1)+'%</td><td class="num r neg">'+x.l.toFixed(1)+'%</td>';
        tb.appendChild(tr);
      });
    }
    nrows("nmtbl",R.names); nrows("evtbl",R.events);
    var ul=document.getElementById("recnotes");
    if(ul) R.notes.forEach(function(t){ var li=document.createElement("li"); li.textContent=t; ul.appendChild(li); });
  })();

  (function(){
    var tb=document.getElementById("ledger");
    var CHIP={wheel:'<span class="chip wheel">Wheel</span>',dir:'<span class="chip dir">Outright</span>',cash:'<span class="chip">Cash</span>',event:'<span class="chip">Event</span>'};
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

  /* ---------------- Futuresight ---------------- */
  (function(){
    if(!FS || !FS.navSeries) return;
    var FC={AI:"#2a78d6",DEF:"#eb6834",IND:"#1baf7a",ENERGY:"#eda100",
            DATA:"#e87ba4",MED:"#008300",SW:"#4a3aa7",RATES:"#e34948"};
    var FL={AI:"AI capex",DEF:"Defense",IND:"Industrial",ENERGY:"Energy",
            DATA:"Data",MED:"Medtech",SW:"Software",RATES:"Rates"};
    var ORDER=["AI","DEF","IND","ENERGY","DATA","MED","SW","RATES"];
    var N=FS.names||[], activeF=null;
    var last=function(a){return a&&a.length?a[a.length-1].v:100;};
    var sig=function(v){return (v>=0?"+":"\u2212")+Math.abs(v).toFixed(2)+"%";};
    var kls=function(v){return v>=0?"pos":"neg";};

    document.getElementById("fsIncept").textContent=FS.inceptionLabel||FS.inception;

    /* sub-views */
    var VIEWS=[["concept","Concept"],["names","All names"],["track","Track"],["factors","Factors"]];
    var vh=document.getElementById("fsviews");
    VIEWS.forEach(function(v,i){
      var b=document.createElement("button");
      b.type="button"; b.className="tlv"+(i===0?" active":"");
      b.setAttribute("role","tab"); b.textContent=v[1];
      b.addEventListener("click",function(){
        [].forEach.call(vh.children,function(c){c.classList.remove("active");});
        b.classList.add("active");
        VIEWS.forEach(function(w){
          document.getElementById("fsv-"+w[0]).classList.toggle("active",w[0]===v[0]);
        });
        if(v[0]==="track") drawFS();
      });
      vh.appendChild(b);
    });

    /* concept: factor legend doubles as a filter */
    var lg=document.getElementById("fsLegend");
    ORDER.forEach(function(f){
      var n=N.filter(function(r){return r.factor===f;});
      if(!n.length) return;
      var b=document.createElement("button");
      b.type="button"; b.className="fs-fc";
      b.innerHTML='<span class="sw" style="background:'+FC[f]+'"></span>'+FL[f]+" \u00b7 "+n.length;
      b.addEventListener("click",function(){
        activeF=(activeF===f)?null:f;
        [].forEach.call(lg.children,function(c){c.classList.remove("active");});
        if(activeF) b.classList.add("active");
        paintHead();
    renderIndustries(); renderMovers(); renderNames();
      });
      lg.appendChild(b);
    });

    function pool(){return activeF?N.filter(function(r){return r.factor===activeF;}):N;}

    function renderIndustries(){
      var rows=pool(), by={};
      rows.forEach(function(r){
        var g=by[r.industry]||(by[r.industry]={n:0,w:0,f:{}});
        g.n++; g.w+=r.weight; g.f[r.factor]=(g.f[r.factor]||0)+1;
      });
      var out=Object.keys(by).map(function(k){
        var g=by[k];
        var dom=Object.keys(g.f).sort(function(a,b){return g.f[b]-g.f[a];})[0];
        return {k:k,n:g.n,w:g.w,dom:dom};
      }).sort(function(a,b){return b.n-a.n;});
      document.getElementById("fsIndustries").innerHTML=out.map(function(r){
        return "<tr><td>"+r.k+"</td><td>"+r.n+"</td><td><span class='fs-sw' style='background:"+
          FC[r.dom]+"'></span>"+FL[r.dom]+"</td><td class='r'>"+r.w.toFixed(2)+"%</td></tr>";
      }).join("");
      var c=FS.coverage||{};
      document.getElementById("fsCoverage").textContent=
        (c.priced||0)+" of "+(c.roster||0)+" names priced \u00b7 "+
        (FS.untracked||[]).length+" carried in the concept but not tracked \u00b7 built "+(FS.builtAt||"");
    }

    function renderMovers(){
      var rows=pool().filter(function(r){return r.ret!==null&&r.ret!==undefined;});
      rows.sort(function(a,b){return b.ret-a.ret;});
      var top=rows.slice(0,12), bot=rows.slice(-12).reverse();
      var seen={}, show=[];
      top.concat(bot).forEach(function(r){ if(!seen[r.ticker]){seen[r.ticker]=1; show.push(r);} });
      document.getElementById("fsMovers").innerHTML=show.map(function(r){
        return "<tr><td><b>"+r.ticker+"</b></td><td>"+r.name+
          "<span class='fs-tier'>"+r.tier+"</span></td>"+
          "<td><span class='fs-sw' style='background:"+FC[r.factor]+"'></span>"+FL[r.factor]+"</td>"+
          "<td class='r'>"+r.weight.toFixed(2)+"%</td>"+
          "<td class='r "+kls(r.ret)+"'>"+sig(r.ret)+"</td></tr>";
      }).join("");
    }

    /* track: headline stats */
    (function(){
      var idx=last(FS.navSeries)-100;
      var cards=[["Index \u00b7 since inception",idx,(FS.navSeries.length)+" session"+(FS.navSeries.length===1?"":"s")]];
      ["SPY","QQQ"].forEach(function(b){
        var s2=(FS.benchSeries||{})[b];
        if(s2) cards.push(["vs "+b, idx-(last(s2)-100), "relative, percentage points"]);
      });
      var tw=FS.tierWeights||{}, tc=FS.tierCounts||{};
      ["core","growth","spec"].forEach(function(t){
        var s2=(FS.tierSeries||{})[t];
        if(s2&&s2.length) cards.push([t.charAt(0).toUpperCase()+t.slice(1),last(s2)-100,
          (tc[t]||0)+" names \u00b7 "+(tw[t]||0)+"% of book"]);
      });
      document.getElementById("fsStats").innerHTML=cards.map(function(c){
        return "<div class='stat'><div class='k'>"+c[0]+"</div><div class='v "+kls(c[1])+"'>"+
          sig(c[1])+"</div><div class='m'>"+c[2]+"</div></div>";
      }).join("");
      document.getElementById("fsCurveSub").textContent=
        "Base 100 at the "+(FS.inceptionLabel||FS.inception)+" open \u00b7 as of "+FS.asOf;
    })();

    /* track: canvas curve */
    function drawFS(){
      var cv=document.getElementById("fscurve"); if(!cv) return;
      var ctx=cv.getContext("2d"), dpr=window.devicePixelRatio||1;
      var W=cv.clientWidth, H=cv.clientHeight;
      cv.width=W*dpr; cv.height=H*dpr; ctx.setTransform(dpr,0,0,dpr,0,0);
      ctx.clearRect(0,0,W,H);
      var css=function(n){return getComputedStyle(document.documentElement).getPropertyValue(n).trim();};
      var series=[{n:"Futuresight",c:css("--accent"),d:FS.navSeries,w:2.2}];
      ["SPY","QQQ"].forEach(function(b,i){
        var s2=(FS.benchSeries||{})[b];
        if(s2) series.push({n:b,c:i?css("--slate"):css("--muted"),d:s2,w:1.3,dash:[4,3]});
      });
      var all=[]; series.forEach(function(s2){s2.d.forEach(function(p){all.push(p.v);});});
      if(!all.length) return;
      var lo=Math.min.apply(null,all), hi=Math.max.apply(null,all);
      if(hi-lo<0.6){var m=(hi+lo)/2; lo=m-0.3; hi=m+0.3;}
      var pad=(hi-lo)*0.18; lo-=pad; hi+=pad;
      var L=44,R=12,T=14,B=26, pw=W-L-R, ph=H-T-B;
      var nmax=Math.max.apply(null,series.map(function(s2){return s2.d.length;}));
      var X=function(i){return L+(nmax<2?pw/2:pw*i/(nmax-1));};
      var Y=function(v){return T+ph*(1-(v-lo)/(hi-lo));};
      /* grid + baseline */
      ctx.strokeStyle=css("--grid"); ctx.lineWidth=1;
      for(var g=0;g<=4;g++){var y=T+ph*g/4; ctx.beginPath(); ctx.moveTo(L,y); ctx.lineTo(W-R,y); ctx.stroke();}
      ctx.fillStyle=css("--faint"); ctx.font="10px "+css("--mono").split(",")[0]; ctx.textAlign="right";
      for(var g2=0;g2<=4;g2++){
        var v=hi-(hi-lo)*g2/4;
        ctx.fillText((v-100>=0?"+":"\u2212")+Math.abs(v-100).toFixed(1)+"%",L-7,T+ph*g2/4+3);
      }
      ctx.setLineDash([2,3]); ctx.strokeStyle=css("--line");
      ctx.beginPath(); ctx.moveTo(L,Y(100)); ctx.lineTo(W-R,Y(100)); ctx.stroke(); ctx.setLineDash([]);
      series.forEach(function(s2){
        ctx.strokeStyle=s2.c; ctx.lineWidth=s2.w; ctx.setLineDash(s2.dash||[]);
        ctx.beginPath();
        s2.d.forEach(function(p,i){ i?ctx.lineTo(X(i),Y(p.v)):ctx.moveTo(X(i),Y(p.v)); });
        if(s2.d.length===1){ ctx.arc(X(0),Y(s2.d[0].v),2.6,0,Math.PI*2); ctx.fillStyle=s2.c; ctx.fill(); }
        ctx.stroke(); ctx.setLineDash([]);
      });
      ctx.textAlign="left"; ctx.font="10px "+css("--mono").split(",")[0];
      var lx=L+4;
      series.forEach(function(s2){
        ctx.fillStyle=s2.c; ctx.fillRect(lx,H-13,8,2.5);
        ctx.fillStyle=css("--muted"); ctx.fillText(s2.n,lx+12,H-9);
        lx+=ctx.measureText(s2.n).width+30;
      });
    }
    window.__fsDraw=drawFS;
    window.addEventListener("resize",function(){
      if(document.getElementById("fsv-track").classList.contains("active")) drawFS();
    });

    /* factors: correlation matrix + group returns */
    (function(){
      var fc=FS.factorCorr;
      if(fc&&fc.keys&&fc.keys.length){
        var h="<table class='fs-corr'><thead><tr><th></th>"+fc.keys.map(function(k){
          return "<th>"+(FL[k]||k)+"</th>";}).join("")+"</tr></thead><tbody>";
        fc.keys.forEach(function(k,i){
          h+="<tr><th class='rh'><span class='fs-sw' style='background:"+FC[k]+"'></span>"+(FL[k]||k)+"</th>";
          fc.m[i].forEach(function(v,j){
            var a=v===null?0:Math.max(0,Math.min(1,(v+0.2)/1.2));
            var bg=i===j?"var(--panel-2)":"rgba(169,128,31,"+(a*0.42).toFixed(3)+")";
            h+="<td style='background:"+bg+"'>"+(v===null?"\u2014":v.toFixed(2))+"</td>";
          });
          h+="</tr>";
        });
        h+="</tbody></table>";
        document.getElementById("fsCorr").innerHTML=h+
          "<p class='fs-cover'>Pearson correlation of daily log returns across "+
          (fc.window||0)+" trailing sessions. Darker means they move together.</p>";
      }
      var rows=ORDER.filter(function(f){return (FS.factorSeries||{})[f];}).map(function(f){
        var mem=N.filter(function(r){return r.factor===f;});
        return {f:f,n:mem.length,w:mem.reduce(function(a,b){return a+b.weight;},0),
                r:last(FS.factorSeries[f])-100};
      }).sort(function(a,b){return b.r-a.r;});
      document.getElementById("fsFactors").innerHTML=rows.map(function(r){
        return "<tr><td><span class='fs-sw' style='background:"+FC[r.f]+"'></span>"+FL[r.f]+
          "</td><td>"+r.n+"</td><td class='r'>"+r.w.toFixed(2)+"%</td>"+
          "<td class='r "+kls(r.r)+"'>"+sig(r.r)+"</td></tr>";
      }).join("");
    })();

    var qbox=document.getElementById("fsQ");
    qbox.addEventListener("input", renderNames);

    /* Sorting. Strings open A-Z, numbers open high-to-low, and clicking the
       column you are already on reverses it. Unpriced names sort last either
       way so a blank return never leads the table. */
    var TEXTKEY={ticker:1,name:1,industry:1,factor:1};
    var sortKey="ret", sortDir=-1;

    function sortRows(rows){
      var k=sortKey, d=sortDir;
      return rows.slice().sort(function(a,b){
        if(k==="ret"||k==="weight"){
          var av=a[k], bv=b[k];
          var an=(av===null||av===undefined), bn=(bv===null||bv===undefined);
          if(an&&bn) return a.ticker.localeCompare(b.ticker);
          if(an) return 1;
          if(bn) return -1;
          if(av===bv) return a.ticker.localeCompare(b.ticker);
          return (av-bv)*d;
        }
        var as=(k==="factor"?FL[a.factor]:a[k])||"";
        var bs=(k==="factor"?FL[b.factor]:b[k])||"";
        var c=as.localeCompare(bs,"en",{numeric:true,sensitivity:"base"});
        return (c||a.ticker.localeCompare(b.ticker,"en",{numeric:true}))*d;
      });
    }

    function paintHead(){
      [].forEach.call(document.querySelectorAll("#fsHead .fs-sort"),function(b){
        var on=b.getAttribute("data-k")===sortKey;
        b.classList.toggle("on",on);
        var ar=b.querySelector(".ar");
        if(!ar){ ar=document.createElement("span"); ar.className="ar"; b.appendChild(ar); }
        ar.textContent = on ? (sortDir===1?"\u25b2":"\u25bc") : "\u25bc";
        b.setAttribute("aria-sort", on ? (sortDir===1?"ascending":"descending") : "none");
      });
    }

    [].forEach.call(document.querySelectorAll("#fsHead .fs-sort"),function(b){
      b.addEventListener("click",function(){
        var k=b.getAttribute("data-k");
        if(k===sortKey){ sortDir=-sortDir; }
        else { sortKey=k; sortDir=TEXTKEY[k]?1:-1; }
        paintHead(); renderNames();
      });
    });

    function renderNames(){
      var q=(qbox.value||"").trim().toLowerCase();
      var rows=pool().filter(function(r){
        if(!q) return true;
        return (r.ticker+" "+r.name+" "+r.industry+" "+FL[r.factor]).toLowerCase().indexOf(q)>-1;
      });
      rows=sortRows(rows);
      document.getElementById("fsNames").innerHTML=rows.map(function(r){
        var ret = r.tracked===false
          ? "<span class='fs-untracked' title='"+(r.why||"")+"'>not tracked</span>"
          : (r.ret===null||r.ret===undefined ? "\u2014"
             : "<span class='"+kls(r.ret)+"'>"+sig(r.ret)+"</span>");
        return "<tr><td><b>"+r.ticker+"</b></td>"+
          "<td>"+r.name+"<span class='fs-tier'>"+r.tier+"</span></td>"+
          "<td class='fs-ind'>"+r.industry+"</td>"+
          "<td><span class='fs-sw' style='background:"+FC[r.factor]+"'></span>"+FL[r.factor]+"</td>"+
          "<td class='r'>"+(r.weight?r.weight.toFixed(2)+"%":"\u2014")+"</td>"+
          "<td class='r'>"+ret+"</td></tr>";
      }).join("");
      var tr=rows.filter(function(r){return r.tracked!==false;}).length;
      document.getElementById("fsNamesCount").textContent=
        rows.length+" of "+N.length+" names shown \u00b7 "+tr+" priced \u00b7 weights are fixed at inception and not rebalanced";
    }

    renderIndustries(); renderMovers(); renderNames();
  })();

    var ids=["report","book","approach","concepts","story","record","futuresight"];
    var panels={}; ids.forEach(function(id){panels[id]=document.getElementById("panel-"+id);});
    function activate(id){
      tabs.forEach(function(t){t.classList.toggle("active",t.getAttribute("data-panel")===id);});
      ids.forEach(function(k){panels[k].classList.toggle("active",k===id);});
      if(id==="report" && window.__drawCurve) window.__drawCurve();
      if(id==="book" && window.__animBars) window.__animBars();
      if(id==="futuresight" && window.__fsDraw) window.__fsDraw();
      window.scrollTo(0,0);
    }
    tabs.forEach(function(t){t.addEventListener("click",function(){activate(t.getAttribute("data-panel"));});});
  })();
})();
</script></body></html>"""

fs_path = os.path.join(HERE, "futuresight_prices.json")
fs = json.load(open(fs_path, encoding="utf-8")) if os.path.exists(fs_path) else None
if fs is None:
    print("warning: futuresight_prices.json missing - run futuresight_fetch.py; tab will render empty")

html = TEMPLATE.replace("__DATA_JSON__", json.dumps(data, ensure_ascii=False))
html = html.replace("__FS_JSON__", json.dumps(fs, ensure_ascii=False))
with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)
print("built index.html (" + str(len(html)) + " bytes) from data.json"
      + (" + futuresight (" + str(fs["coverage"]["priced"]) + " priced, as of "
         + fs["asOf"] + ")" if fs else " (no futuresight data)"))
