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
<title>Pareidolia</title>
<meta property="og:title" content="Pareidolia">
<meta property="og:site_name" content="Pareidolia">
<meta property="og:type" content="website">
<meta property="og:url" content="https://pareidoliatrading.com/">
<meta property="og:description" content="A private book run under pattern recognition.">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="Pareidolia">
<meta name="twitter:description" content="A private book run under pattern recognition.">
<meta name="description" content="A private book run under pattern recognition.">
<style>
  /* =====================================================================
     PAREIDOLIA - the desk, restruck.

     The terminal colourway that shipped before 9 September - amber phosphor
     on near-black, green up, red down, cyan for a comparison line - on the
     one-sheet architecture. The three references stay, translated into what
     a CRT can actually do:

     NAGEL        flat planes, one hot colour. The active tab, the grade and
                  the timeline pills are solid amber slabs with the ground
                  knocked out of them.
     FRAZETTA     one light source. Amber pools from the top-left and the
                  frame falls off into shadow at the edges - the vignette that
                  makes phosphor look like it sits behind glass.
     TARTAKOVSKY  the cut. Changing tab kills the picture to a phosphor line,
                  swaps the panel in the dark, and redraws it with a raster
                  bar. A hard shape, not a fade.

     One sheet. No colourway attribute, no override layers.
     ===================================================================== */

  :root{
    --bg:#07090A; --panel:#0D1113; --panel-2:#131A1D; --line:#242E33;
    --ink:#E8E4D9; --muted:#8B9AA1; --faint:#5E6C72;
    --accent:#FFB000; --accent-soft:rgba(255,176,0,.14);
    --up:#3DF07A; --down:#FF4B3E; --warn:#FFB000; --compare:#3AD4E8;
    --slate:#7E8C93; --grid:rgba(232,228,217,.09);
    --gold:#FFB000; --gold-lift:#FFC94D; --paper:#0D1113;
    --silver:#9AA7AE; --silver-lift:#C3CDD3;
    --engrave:#FFB000; --label:#FFB000;
    --plate:#07090A; --plate-edge:#242E33; --plate-rule:#FFB000; --plate-ink:#8B9AA1;
    --pinstripe:rgba(232,228,217,.030); --pinstripe-gold:rgba(255,176,0,.06);
    --glow:5px 5px 0 #0E4B54, 0 0 18px rgba(255,176,0,.35), 0 0 46px rgba(255,176,0,.14);
    color-scheme:dark;
    --serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,"Times New Roman",serif;
    --sans:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    --mono:"SFMono-Regular","SF Mono",ui-monospace,"Cascadia Mono","Segoe UI Mono",Menlo,Consolas,monospace;
    --pagepad:clamp(10px,1.2vw,18px);
    --cut:cubic-bezier(.76,0,.24,1);
    --ease-out:cubic-bezier(.22,.61,.36,1);
  }

  *{box-sizing:border-box}
  html,body{margin:0; background:var(--bg)}
  ::selection{background:var(--accent); color:#07090A}

  .wrap{background:var(--bg); color:var(--ink); font-family:var(--mono);
    min-height:100vh; padding:var(--pagepad) var(--pagepad) 70px;
    line-height:1.5; -webkit-font-smoothing:antialiased; position:relative; overflow:hidden}
  /* one light source, and glass: amber pools top-left, the edges fall away */
  .wrap::after{content:""; position:fixed; inset:0; z-index:0; pointer-events:none;
    background:
      radial-gradient(110% 80% at 8% -8%, rgba(255,176,0,.10), transparent 55%),
      radial-gradient(ellipse at 50% 42%, transparent 52%, rgba(0,0,0,.58) 100%)}
  .sheet{max-width:none; margin:0; position:relative; z-index:1}
  .stage{position:relative}

  /* ---------- the cut: tube off, swap in the dark, halves part ---------- */
  .wipe{position:fixed; left:0; top:0; width:100%; height:100%; z-index:60; pointer-events:none; visibility:hidden}
  .wipe.run{visibility:visible}
  .wipe .top,.wipe .bot{position:absolute; left:0; right:0; height:50%; background:#000;
    will-change:transform; transform:scaleY(0)}
  .wipe .top{top:0; transform-origin:50% 0;
    box-shadow:0 1px 0 0 var(--gold-lift), 0 0 16px 1px rgba(255,176,0,.55)}
  .wipe .bot{bottom:0; transform-origin:50% 100%;
    box-shadow:0 -1px 0 0 var(--gold-lift), 0 0 16px 1px rgba(255,176,0,.55)}
  .wipe .ln{position:absolute; left:0; right:0; top:50%; height:2px; margin-top:-1px;
    background:#fff; opacity:0; will-change:transform,opacity;
    box-shadow:0 0 8px 2px rgba(255,200,77,.9), 0 0 36px 10px rgba(255,176,0,.45)}
  @keyframes crtTop{
    0%  {transform:translateY(0) scaleY(0)}
    30% {transform:translateY(0) scaleY(1)}
    48% {transform:translateY(0) scaleY(1)}
    100%{transform:translateY(-100%) scaleY(1)}
  }
  @keyframes crtBot{
    0%  {transform:translateY(0) scaleY(0)}
    30% {transform:translateY(0) scaleY(1)}
    48% {transform:translateY(0) scaleY(1)}
    100%{transform:translateY(100%) scaleY(1)}
  }
  @keyframes crtLine{
    0%  {transform:scaleX(1);   opacity:0}
    22% {transform:scaleX(1);   opacity:1}
    32% {transform:scaleX(1);   opacity:1}
    46% {transform:scaleX(.015); opacity:1}
    50% {transform:scaleX(.015); opacity:0}
    100%{transform:scaleX(.015); opacity:0}
  }
  .wipe.run .top{animation:crtTop .56s var(--cut) both}
  .wipe.run .bot{animation:crtBot .56s var(--cut) both}
  .wipe.run .ln{animation:crtLine .56s var(--cut) both}

  .panel{display:none}
  .panel.active{display:block}
  @media (prefers-reduced-motion:reduce){ .wipe{display:none} }

  /* ---------- masthead: phosphor nameplate ---------- */
  .plate{display:flex; align-items:flex-end; justify-content:space-between; gap:16px 30px;
    flex-wrap:wrap; padding:6px 0 12px; border-bottom:2px solid var(--accent)}
  .masthead{display:block; padding:0}
  .mark{font-family:var(--mono); font-weight:600;
    font-size:clamp(26px,5.2vw,52px); line-height:1; letter-spacing:.30em;
    text-transform:uppercase; color:var(--accent); text-shadow:var(--glow)}
  .mark .dot{color:var(--up)}
  .tag{font-family:var(--mono); font-size:11px; letter-spacing:.16em;
    text-transform:uppercase; color:var(--muted); max-width:52ch; line-height:1.7; margin:8px 0 0}
  .rosette,.om{display:none}
  .dateline{display:flex; flex-direction:column; align-items:flex-end; gap:5px;
    font-family:var(--mono); font-size:9.5px; letter-spacing:.2em; text-align:right;
    text-transform:uppercase; color:var(--muted); padding:0 0 6px}
  .dateline b{color:var(--accent); font-weight:600}

  /* ---------- tape ---------- */
  .tape{display:block; overflow:hidden; position:relative;
    border-bottom:1px solid var(--line); background:var(--bg)}
  .tapetrack{display:inline-flex; gap:34px; white-space:nowrap; padding:7px 16px;
    font-family:var(--mono); font-size:10.5px; letter-spacing:.07em; color:var(--faint)}
  .tapetrack b{color:var(--muted); font-weight:600}
  .tapetrack .u{color:var(--up)} .tapetrack .d{color:var(--down)}
  .tapetrack .sep{color:var(--faint); opacity:.5}
  @keyframes crawl{from{transform:translateX(0)}to{transform:translateX(-50%)}}
  .tapetrack{animation:crawl 64s linear infinite}
  @media (prefers-reduced-motion:reduce){ .tapetrack{animation:none} }

  /* ---------- tabs: the function rail, active one an amber slab ---------- */
  .tabs{display:flex; gap:0; position:sticky; top:0; z-index:7;
    background:var(--panel-2); border-bottom:1px solid var(--line);
    overflow-x:auto; scrollbar-width:none; margin:0 0 14px}
  .tabs::-webkit-scrollbar{display:none}
  .tab{appearance:none; background:none; border:0; cursor:pointer; font:inherit;
    font-family:var(--mono); font-size:11px; font-weight:600; letter-spacing:.13em;
    text-transform:uppercase; color:var(--muted); padding:14px 20px 12px;
    white-space:nowrap; position:relative; transition:color .14s, background .14s}
  .tab{border-right:1px solid var(--line)}
  .tab .fk{color:var(--accent); margin-right:9px; opacity:1; font-weight:600; font-size:9px;
    border:1px solid var(--line); padding:1px 5px; background:var(--bg)}
  .tab.active .fk{background:#07090A; color:var(--accent); border-color:#07090A; opacity:1}
  .tab:hover{color:var(--ink); background:rgba(255,176,0,.06)}
  .tab.active{color:#07090A; background:var(--accent)}
  .tabink{display:none}
  .tab:focus-visible,.tlv:focus-visible,.cbtn:focus-visible,
  .fs-sort:focus-visible,.gcard:focus-visible{outline:2px solid var(--accent); outline-offset:-3px}
  .scrollprog{position:fixed; top:0; left:0; height:2px; background:var(--accent);
    z-index:30; width:0; opacity:0; transition:opacity .2s}
  .scrollprog.scrolled{opacity:1}

  /* ---------- section heads ---------- */
  section,.concept{position:relative; margin-top:14px; border:1px solid var(--line);
    background:var(--panel); padding:34px 14px 14px}
  section:not(:has(> .eyebrow)){padding-top:14px}
  .panel.active>section:first-child,.panel.active>div:first-child section:first-child{margin-top:0}
  .bookgrid>section{margin-top:0}
  .eyebrow{position:absolute; top:-1px; left:-1px; margin:0; display:inline-flex; align-items:center;
    padding:5px 11px 4px; background:var(--accent); color:#07090A;
    font-family:var(--mono); font-size:9px; font-weight:600; letter-spacing:.24em; text-transform:uppercase;
    white-space:nowrap; max-width:calc(100% + 2px); overflow:hidden; text-overflow:ellipsis}
  .eyebrow b,.eyebrow span{color:inherit}
  h2{font-family:var(--mono); font-weight:600; font-size:clamp(16px,1.6vw,21px);
    letter-spacing:.06em; text-transform:uppercase; margin:0 0 6px; color:var(--accent)}
  h3{font-family:var(--mono); font-size:12px; font-weight:600; letter-spacing:.12em;
    text-transform:uppercase; color:var(--muted); margin:0 0 8px}

  /* ---------- headline numbers: phosphor lit ---------- */
  .stats{display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr));
    gap:1px; background:var(--line); border:1px solid var(--line); margin-top:12px}
  .stat{background:var(--panel); padding:22px 22px 20px}
  .stat .k{font-family:var(--mono); font-size:9.5px; letter-spacing:.2em;
    text-transform:uppercase; color:var(--muted)}
  .stat .v{font-family:var(--mono); font-variant-numeric:tabular-nums;
    font-size:clamp(34px,4.8vw,52px); font-weight:600; letter-spacing:-.02em;
    line-height:1; margin:14px 0 0; color:var(--accent); text-shadow:0 0 14px rgba(255,176,0,.22)}
  .stat .m{font-family:var(--serif); font-size:12.5px; color:var(--faint); margin-top:10px; line-height:1.5}
  .pos{color:var(--up)} .neg{color:var(--down)}
  .stat .v.pos{color:var(--up); text-shadow:0 0 14px rgba(61,240,122,.25)}
  .stat .v.neg{color:var(--down); text-shadow:0 0 14px rgba(255,75,62,.25)}
  .asofline{font-family:var(--mono); font-size:9.5px; letter-spacing:.18em;
    text-transform:uppercase; color:var(--faint); margin:12px 0 0}
  .asofline b{color:var(--muted); font-weight:600}

  /* ---------- chart ---------- */
  .chart-card{background:var(--panel); border:0;
    padding:0 0 4px; margin-top:6px; position:relative;
    --accent:var(--gold); --slate:var(--compare)}
  .chart-head{display:flex; justify-content:space-between; align-items:baseline; gap:14px; flex-wrap:wrap}
  .chart-head .sub{font-family:var(--mono); font-size:10px; letter-spacing:.13em;
    text-transform:uppercase; color:var(--faint)}
  canvas#curve,canvas#fscurve{display:block; width:100%; height:320px; margin-top:10px}
  canvas#fscurve{height:280px}
  .tlviews{display:flex; gap:0; flex-wrap:wrap; margin-top:14px; border:1px solid var(--line); width:fit-content}
  .tlv{appearance:none; background:none; border:0; border-right:1px solid var(--line);
    cursor:pointer; font-family:var(--mono); font-size:9.5px; letter-spacing:.14em;
    text-transform:uppercase; color:var(--faint); padding:7px 13px; transition:.14s}
  .tlv:last-child{border-right:0}
  .tlv:hover{color:var(--ink); background:var(--panel-2)}
  .tlv.active{background:var(--accent); color:#07090A; font-weight:600}
  .marks{display:flex; gap:24px; flex-wrap:wrap; margin-top:12px; padding-top:12px;
    border-top:1px solid var(--line); font-family:var(--mono); font-size:10px;
    letter-spacing:.1em; text-transform:uppercase; color:var(--faint)}
  .marks span{display:inline-flex; gap:8px; align-items:center}
  .marks b{color:var(--ink); font-weight:600; font-variant-numeric:tabular-nums}
  .swatch,.sw{width:9px; height:9px; display:inline-block}
  .ctip{position:absolute; display:none; pointer-events:none; z-index:8;
    transform:translate(-50%,-100%); background:var(--bg); border:1px solid var(--accent);
    padding:5px 10px; font-family:var(--mono); font-size:10.5px; white-space:nowrap}
  .ctip .tdate{color:var(--muted); margin-right:10px}
  .ctip .tval{font-weight:600; color:var(--accent)}

  /* ---------- after-action: the grade is an amber slab ---------- */
  .rc-head{display:flex; align-items:center; gap:20px; flex-wrap:wrap; margin:14px 0 16px}
  .grade{font-family:var(--mono); font-weight:600; font-size:48px; line-height:.9;
    letter-spacing:-.02em; padding:12px 20px; background:var(--accent); color:#07090A}
  .rc-head .wk{font-family:var(--mono); font-size:10.5px; letter-spacing:.14em;
    text-transform:uppercase; color:var(--muted); line-height:1.9}
  .rc-head .wkret{font-weight:600; font-variant-numeric:tabular-nums}
  .rbadge{display:inline-block; font-family:var(--mono); font-size:8.5px;
    letter-spacing:.18em; text-transform:uppercase; color:var(--faint);
    border:1px solid var(--line); padding:3px 8px; margin-top:7px}
  .dials{display:grid; grid-template-columns:repeat(auto-fit,minmax(215px,1fr));
    gap:1px; background:var(--line); border:1px solid var(--line)}
  .dial{background:var(--panel); padding:16px 17px 15px; border-top:2px solid var(--line)}
  .dial.pass{border-top-color:var(--up)}
  .dial.warn{border-top-color:var(--warn)}
  .dial.fail{border-top-color:var(--down)}
  .dial .dk{font-family:var(--mono); font-size:9px; letter-spacing:.19em;
    text-transform:uppercase; color:var(--muted)}
  .state{display:inline-block; font-family:var(--mono); font-size:8.5px; font-weight:600;
    letter-spacing:.18em; text-transform:uppercase; padding:3px 8px; margin-top:9px; color:#07090A}
  .state.pass{background:var(--up)}
  .state.warn{background:var(--warn)}
  .state.fail{background:var(--down)}
  .dial .dv{font-family:var(--mono); font-variant-numeric:tabular-nums;
    font-size:23px; font-weight:600; letter-spacing:-.01em; margin:10px 0 5px; color:var(--ink)}
  .dial .rule{font-family:var(--serif); font-size:12.5px; color:var(--faint); line-height:1.55}
  .rc-note{margin-top:14px; font-family:var(--serif); font-size:15px; line-height:1.7;
    color:var(--muted)}
  .rc-note b{color:var(--accent); font-weight:600; font-family:var(--mono);
    font-size:10px; letter-spacing:.18em; text-transform:uppercase}
  .rbasis{font-family:var(--serif); font-style:italic; font-size:13px; color:var(--faint);
    margin-top:12px; line-height:1.65; }
  .hlabel{font-family:var(--mono); font-size:9.5px; letter-spacing:.19em;
    text-transform:uppercase; color:var(--faint); margin:26px 0 4px}
  .hnote{font-family:var(--mono); font-size:9.5px; letter-spacing:.06em; color:var(--faint); margin:0 0 10px}
  .hist{display:flex; gap:1px; overflow-x:auto; background:var(--line);
    border:1px solid var(--line); scrollbar-width:thin}
  .hist::-webkit-scrollbar{height:6px}
  .hist::-webkit-scrollbar-thumb{background:var(--line)}
  .gcard{flex:0 0 auto; min-width:80px; background:var(--panel); border:0; cursor:pointer;
    font:inherit; color:inherit; padding:11px 12px 10px; text-align:center; transition:background .14s}
  .gcard:hover{background:var(--panel-2)}
  .gcard.active{background:var(--accent-soft); box-shadow:inset 0 -2px 0 0 var(--accent)}
  .gcard.recon{opacity:.62}
  .gcard.recon:hover,.gcard.recon.active{opacity:1}
  .gw{font-family:var(--mono); font-size:9px; letter-spacing:.11em; text-transform:uppercase; color:var(--faint)}
  .gg{font-family:var(--mono); font-size:22px; font-weight:600; letter-spacing:-.02em; line-height:1.15; margin:4px 0 2px}
  .gr{font-family:var(--mono); font-size:10px; font-variant-numeric:tabular-nums}
  .gnow{font-family:var(--mono); font-size:7.5px; letter-spacing:.18em; text-transform:uppercase; color:var(--accent); margin-top:3px}
  .grecon{font-family:var(--mono); font-size:7.5px; letter-spacing:.14em; text-transform:uppercase; color:var(--faint); margin-top:3px}

  /* ---------- heatmap ---------- */
  .heat{display:grid; grid-template-columns:repeat(auto-fill,minmax(16px,1fr)); gap:2px; margin-top:12px}
  .heat i{display:block; aspect-ratio:1; background:var(--panel-2);
    border:1px solid transparent; cursor:pointer; transition:transform .1s}
  .heat i:hover{border-color:var(--ink); transform:scale(1.2); position:relative; z-index:2}
  .heat-scale{display:flex; align-items:center; gap:10px; margin-top:12px;
    font-family:var(--mono); font-size:9px; letter-spacing:.16em; text-transform:uppercase; color:var(--faint)}
  .heat-scale .ramp{display:flex; gap:2px}
  .heat-scale .ramp i{width:17px; height:9px; display:block}

  /* ---------- allocation ---------- */
  .bookgrid{display:grid; grid-template-columns:repeat(auto-fit,minmax(320px,1fr)); gap:14px; margin-top:14px}
  .bars{display:flex; flex-direction:column; gap:9px; margin-top:14px}
  .bar{display:grid; grid-template-columns:62px 1fr 58px; align-items:center; gap:13px}
  .bar .name{font-family:var(--mono); font-size:11px; font-weight:600; letter-spacing:.08em; color:var(--ink)}
  .bar .track{height:16px; background:var(--panel-2); border:1px solid var(--line); overflow:hidden; position:relative}
  .bar .fill{height:100%; transform-origin:left; transform:scaleX(0); transition:transform .85s var(--ease-out)}
  .bar .pct{font-family:var(--mono); font-variant-numeric:tabular-nums; font-size:11px; text-align:right; color:var(--muted)}
  .legend-strat{display:flex; gap:20px; flex-wrap:wrap; margin-top:16px;
    font-family:var(--mono); font-size:9.5px; letter-spacing:.13em; text-transform:uppercase; color:var(--faint)}
  .legend-strat span{display:inline-flex; gap:8px; align-items:center}

  /* ---------- tables ---------- */
  .tablewrap{overflow-x:auto; border:1px solid var(--line); margin-top:12px}
  table{width:100%; border-collapse:collapse; font-family:var(--mono); font-size:11px}
  thead th{background:var(--panel-2); color:var(--accent); font-weight:600;
    font-size:9px; letter-spacing:.17em; text-transform:uppercase; text-align:left;
    padding:7px 10px; border-bottom:1px solid var(--accent); white-space:nowrap}
  td{padding:6px 10px; border-bottom:1px solid var(--line); color:var(--muted); font-variant-numeric:tabular-nums}
  tbody tr:last-child td{border-bottom:0}
  tbody tr:hover td{background:rgba(255,176,0,.07); color:var(--ink)}
  th.r,td.r,.num.r{text-align:right}
  .tk{color:var(--ink); font-weight:600; letter-spacing:.06em}
  .chip{display:inline-block; font-family:var(--mono); font-size:8.5px;
    letter-spacing:.15em; text-transform:uppercase; padding:2px 7px; border:1px solid var(--line); color:var(--faint)}
  .chip.wheel{color:var(--accent); border-color:rgba(255,176,0,.45)}
  .chip.dir{color:var(--compare); border-color:rgba(58,212,232,.4)}

  /* ---------- strategy cards ---------- */
  .cards{display:grid; grid-template-columns:repeat(auto-fit,minmax(270px,1fr));
    gap:1px; background:var(--line); border:1px solid var(--line); margin-top:14px}
  .appr{background:var(--panel); padding:20px; display:flex; flex-direction:column; border-top:2px solid var(--accent)}
  .appr:nth-child(2){border-top-color:var(--warn)}
  .appr:nth-child(3){border-top-color:var(--compare)}
  .appr h3{font-family:var(--mono); font-size:12.5px; font-weight:600; letter-spacing:.1em;
    text-transform:uppercase; color:var(--ink); margin:0 0 11px; display:flex; align-items:baseline; gap:9px; flex-wrap:wrap}
  .appr .idx{color:var(--accent); font-size:10px; letter-spacing:.2em}
  .appr h3 .tag{font-family:var(--mono); font-size:8.5px; letter-spacing:.16em; color:var(--faint);
    border:1px solid var(--line); padding:2px 7px; text-transform:uppercase; margin:0}
  .appr p{margin:0; font-family:var(--serif); font-size:14px; line-height:1.65; color:var(--muted)}
  .appr p:not(.ctl){padding-bottom:14px}
  .appr .ctl{margin-top:auto; padding-top:11px; border-top:1px solid var(--line);
    font-family:var(--mono); font-size:9px; letter-spacing:.15em; text-transform:uppercase; color:var(--faint)}
  .appr .ctl b{color:var(--accent); font-weight:600}

  /* ---------- mandate ---------- */
  .con{display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr));
    gap:1px; background:var(--line); border:1px solid var(--line); margin-top:14px}
  .con .box{background:var(--panel); padding:17px 18px; border-top:2px solid var(--line)}
  .con .box.ok{border-top-color:var(--up)}
  .con .box.no{border-top-color:var(--down)}
  .con .box h4{font-family:var(--mono); font-size:9px; letter-spacing:.19em; text-transform:uppercase; color:var(--faint); margin:0 0 11px}
  .con ul{margin:0; padding-left:16px}
  .con li{font-family:var(--serif); font-size:14px; line-height:1.65; color:var(--muted); margin:6px 0}

  /* ---------- editorial prose ---------- */
  .prose{font-family:var(--serif); font-size:15px; line-height:1.7; color:var(--muted); margin:0 0 13px}
  .prose b,.prose strong{color:var(--ink); font-weight:600}
  .prose a{color:var(--accent); text-decoration:underline; text-underline-offset:3px}
  .proselist{margin:0 0 15px; padding-left:19px; }
  .proselist li{font-family:var(--serif); font-size:14px; line-height:1.65; color:var(--muted); margin:0 0 9px}
  .proselist li b{color:var(--ink); font-weight:600}

  /* ---------- concepts ---------- */
  .cnav{display:flex; gap:1px; background:var(--line); border:1px solid var(--line);
    overflow-x:auto; scrollbar-width:none; margin-bottom:14px}
  .cnav::-webkit-scrollbar{display:none}
  .cbtn{appearance:none; background:var(--panel); border:0; cursor:pointer; font:inherit;
    font-family:var(--mono); font-size:9px; letter-spacing:.18em; text-transform:uppercase;
    color:var(--faint); padding:12px 18px; text-align:left; white-space:nowrap;
    display:flex; flex-direction:column; gap:5px; transition:.14s}
  .cbtn b{font-size:12px; letter-spacing:.05em; color:var(--muted); text-transform:none}
  .cbtn:hover{background:var(--panel-2)}
  .cbtn.on{background:rgba(255,176,0,.12)}
  .cbtn.on b{color:var(--accent)}
  .concept{display:none}
  .concept.active{display:block; animation:push .34s var(--ease-out) both}
  .fsview{display:none}
  .fsview.active{display:block}
  .fs-kicker{font-family:var(--serif); font-style:italic; font-size:16px; line-height:1.65; color:var(--ink); margin:0 0 18px}
  .fs-note{font-family:var(--serif); font-size:14px; line-height:1.65; color:var(--faint);
    border-left:2px solid var(--accent); padding-left:16px; margin:18px 0}
  .fs-cover{font-family:var(--mono); font-size:9.5px; letter-spacing:.13em; text-transform:uppercase; color:var(--faint); margin-top:10px}
  .fs-legend{display:flex; flex-wrap:wrap; gap:6px; margin:16px 0 6px}
  .fs-sw{display:inline-block; width:8px; height:8px; margin-right:6px; vertical-align:1px}
  .fs-fc{display:inline-flex; align-items:center; gap:7px; appearance:none; cursor:pointer;
    font-family:var(--mono); font-size:9px; letter-spacing:.14em; text-transform:uppercase;
    background:none; border:1px solid var(--line); color:var(--faint); padding:5px 9px; transition:.14s}
  .fs-fc .sw{width:9px; height:9px; flex:none}
  .fs-fc:hover{border-color:var(--accent); color:var(--ink)}
  .fs-fc.active{background:var(--accent-soft); border-color:var(--accent); color:var(--ink)}
  .fs-search,.fs-q{font-family:var(--mono); font-size:11px; background:var(--panel);
    border:1px solid var(--line); color:var(--ink); padding:8px 11px; width:100%; max-width:280px; margin:14px 0}
  .fs-search:focus,.fs-q:focus{outline:none; border-color:var(--accent)}
  .fs-sort{appearance:none; background:none; border:0; cursor:pointer; font:inherit; color:inherit; display:inline-flex; align-items:center; gap:5px}
  .fs-sort .ar{font-size:8px; opacity:0; transition:opacity .12s}
  .fs-sort.asc .ar,.fs-sort:hover .ar{opacity:.8}
  .fs-corrwrap{overflow-x:auto; margin-top:14px}
  table.fs-corr{border-collapse:collapse; font-family:var(--mono); font-size:10.5px; min-width:520px; width:auto}
  table.fs-corr td,table.fs-corr th{padding:0; text-align:center; border:1px solid var(--bg);
    font-variant-numeric:tabular-nums; width:52px; height:34px}
  table.fs-corr th{font-weight:600; color:var(--faint); font-size:9px; letter-spacing:.1em;
    text-transform:uppercase; background:var(--bg); border-color:var(--bg)}
  table.fs-corr th.rh{text-align:right; padding-right:10px; width:auto}
  .fs-ind{font-family:var(--mono); font-size:9.5px; color:var(--faint); letter-spacing:.05em}
  .fs-tier{display:inline-block; border:1px solid var(--line); padding:1px 6px;
    font-family:var(--mono); font-size:9px; letter-spacing:.13em; text-transform:uppercase; color:var(--faint)}
  .fs-untracked{font-family:var(--mono); font-size:9px; letter-spacing:.13em; text-transform:uppercase; color:var(--faint)}
  .vs-flag,.gs-flags span{display:inline-block; font-family:var(--mono); font-size:8px;
    letter-spacing:.11em; text-transform:uppercase; border:1px solid var(--line); color:var(--faint); padding:1px 5px; margin:1px 2px 1px 0}
  .vs-flag.warn{color:var(--down); border-color:rgba(255,75,62,.5)}
  .vs-flag.more{border-style:dashed; cursor:help}
  .gs-flags{display:inline-flex; gap:4px; align-items:center}
  .gs-flags .vs-flag{margin:0}
  .vs-score{font-family:var(--mono); font-weight:600; color:var(--accent)}
  .vs-sub{font-family:var(--mono); font-size:9px; color:var(--faint); letter-spacing:.06em}
  .vs-ins{display:inline-block; font-family:var(--mono); font-size:8.5px; letter-spacing:.1em; padding:1px 6px; border:1px solid var(--line); color:var(--faint)}
  .vs-ins.heavy{background:var(--accent); color:#07090A; border-color:var(--accent); font-weight:600}
  .vs-ins.absent{opacity:.55}
  .dist{margin:20px 0 6px}
  .dist .dhead{display:flex; justify-content:space-between; align-items:baseline; gap:14px;
    font-family:var(--mono); font-size:9px; letter-spacing:.16em; text-transform:uppercase; color:var(--faint); margin-bottom:9px}
  .dist .bars{display:flex; align-items:flex-end; gap:2px; height:60px; flex-direction:row}
  .dist .bars i{flex:1 1 0; background:var(--accent); opacity:.28; min-height:1px}
  .dist .bars i.hot{opacity:1}
  .dist .axis{display:flex; justify-content:space-between; font-family:var(--mono); font-size:9px; color:var(--faint); margin-top:6px}
  .more{font-family:var(--mono); font-size:9.5px; letter-spacing:.12em; text-transform:uppercase; color:var(--faint); margin-top:10px}
  #fsNames td:nth-child(4),#fsMovers td:nth-child(3),#fsFactors td:nth-child(1),#fsIndustries td:nth-child(3){white-space:nowrap}
  #vsRows td:nth-child(1),#vsRows td:nth-child(10){white-space:nowrap}
  #gsHead th,#gsRows td:not(:last-child){white-space:nowrap}
  #gsRows td:nth-child(3){min-width:184px; white-space:normal}
  #gsRows td:last-child{white-space:nowrap; padding-right:12px}
  #gsPillars td:first-child{font-family:var(--serif); font-size:13px}

  /* ---------- status line ---------- */
  .statusbar{display:flex; position:fixed; left:0; right:0; bottom:0; z-index:20;
    gap:24px; flex-wrap:wrap; justify-content:center; background:var(--panel);
    border-top:1px solid var(--line); padding:7px 14px; font-family:var(--mono);
    font-size:9px; letter-spacing:.16em; text-transform:uppercase; color:var(--faint)}
  .statusbar b{color:var(--accent); font-weight:600}
  .statusbar .live{color:var(--up)}
  .statusbar::after{content:"_"; color:var(--accent); font-weight:600}

  /* ---------- footer ---------- */
  footer{margin-top:56px; padding-top:20px; border-top:1px solid var(--line)}
  footer p{font-family:var(--mono); font-size:9.5px; letter-spacing:.1em; color:var(--faint); line-height:1.9; margin:0 0 8px}
  footer .meth{font-size:8.5px; letter-spacing:.16em; text-transform:uppercase; opacity:.75}

  /* ---------- stale bar ---------- */
  .stalebar{position:fixed; left:0; right:0; bottom:30px; z-index:40; background:var(--accent);
    color:#07090A; font-family:var(--mono); font-size:10px; letter-spacing:.13em; text-transform:uppercase; padding:9px 14px; text-align:center}
  .stalebar button{font:inherit; margin-left:10px; background:none; cursor:pointer; border:1px solid rgba(7,9,10,.5); color:inherit; padding:3px 10px}

  /* =====================================================================
     MOTION. Three rules, from the three references.
     TARTAKOVSKY  nothing fades. Shapes are cut in with clip-path on
                  steps(), so everything moves on twos like a cel.
     NAGEL        the hot colour is a slab. It slides (the tab), stamps
                  (the grade), and snaps (the states) - never blends.
     FRAZETTA     one light. It breathes, and a
                  figure that has just landed flares before it settles.
     ===================================================================== */
  @keyframes cutIn{from{clip-path:inset(-60px 100% -60px -60px)}to{clip-path:inset(-60px)}}
  @keyframes snapOn{from{opacity:0}to{opacity:1}}
  @keyframes chOn{
    0%  {opacity:0; text-shadow:none}
    40% {opacity:1; text-shadow:0 0 28px rgba(255,201,77,.95), 0 0 80px rgba(255,176,0,.55)}
    100%{opacity:1; text-shadow:var(--glow)}}
  @keyframes stamp{
    0%  {transform:scale(1.7); opacity:0}
    35% {transform:scale(1.7); opacity:1}
    100%{transform:scale(1);   opacity:1}}
  @keyframes flare{
    0%  {text-shadow:0 0 34px rgba(255,201,77,.95), 0 0 90px rgba(255,176,0,.55)}
    100%{text-shadow:0 0 14px rgba(255,176,0,.22)}}
  @keyframes breathe{0%,100%{opacity:.82}50%{opacity:1}}
  @keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}

  /* the tab slab: one amber plane that slides between the keys */
  .tabs.hasink{position:sticky}
  .tabs.hasink .tab{position:relative; z-index:1}
  .tabs.hasink .tab.active{background:transparent; transition:color .1s steps(2) .28s}
  .tabs.hasink .tab.active .fk{transition:color .1s steps(2) .28s}
  .tabs.hasink .tabink{display:block; position:absolute; left:0; top:0; height:100%; width:0;
    background:var(--accent); z-index:0; pointer-events:none;
    transition:left .4s var(--cut), width .4s var(--cut), top .4s var(--cut)}

  /* hovers snap on twos */
  .tab,.tlv,.cbtn,.fs-fc,.gcard,.fs-sort{transition-timing-function:steps(2)}
  tbody tr td{transition:background .12s steps(2), color .12s steps(2), box-shadow .12s steps(2)}
  tbody tr:hover td:first-child{box-shadow:inset 3px 0 0 0 var(--accent)}
  .heat i{transition:transform .08s steps(2)}

  @media (prefers-reduced-motion:no-preference){
    :root{--boot:.25s}
    .booted{--boot:0s}

    /* --- boot: the desk powers up, key by key --- */
    .mark .ch{display:inline-block; animation:chOn .3s steps(3) both;
      animation-delay:calc(.08s + var(--i,0)*.032s)}
    .statusbar::after{animation:blink 1.1s steps(1) infinite}
    .tag{animation:snapOn .01s steps(1) both .5s}
    .dateline span{animation:snapOn .01s steps(1) both}
  .dateline span:nth-child(1){animation-delay:0.560s}
  .dateline span:nth-child(2){animation-delay:0.640s}
  .dateline span:nth-child(3){animation-delay:0.720s}
    .tab{animation:snapOn .01s steps(1) both}
    .tabs.hasink .tabink{animation:snapOn .01s steps(1) both .66s}
  .tab:nth-child(1){animation-delay:0.660s}
  .tab:nth-child(2){animation-delay:0.720s}
  .tab:nth-child(3){animation-delay:0.780s}
  .tab:nth-child(4){animation-delay:0.840s}
    .statusbar span{animation:snapOn .01s steps(1) both}
  .statusbar span:nth-child(1){animation-delay:0.850s}
  .statusbar span:nth-child(2){animation-delay:0.900s}
  .statusbar span:nth-child(3){animation-delay:0.950s}
  .statusbar span:nth-child(4){animation-delay:1.000s}
  .statusbar span:nth-child(5){animation-delay:1.050s}
  .statusbar span:nth-child(6){animation-delay:1.100s}

    /* --- the light --- */
    .wrap::after{animation:breathe 7s ease-in-out infinite}

    /* --- headline figures: cut in, count, then flare and settle --- */
    .stat{animation:cutIn .34s steps(6) backwards}
    .stat:nth-child(1){animation-delay:calc(var(--boot) + 0.55s)}
    .stat:nth-child(2){animation-delay:calc(var(--boot) + 0.62s)}
    .stat:nth-child(3){animation-delay:calc(var(--boot) + 0.69s)}
    .stat:nth-child(4){animation-delay:calc(var(--boot) + 0.76s)}
    .stat:nth-child(5){animation-delay:calc(var(--boot) + 0.83s)}
    .stat:nth-child(6){animation-delay:calc(var(--boot) + 0.90s)}
    .stat:nth-child(7){animation-delay:calc(var(--boot) + 0.97s)}
    .stat:nth-child(8){animation-delay:calc(var(--boot) + 1.04s)}
    .stat .v.lit{animation:flare .55s steps(4) both}

    /* --- sections arriving with a tab: cut in left to right on twos --- */
    @keyframes push{from{clip-path:inset(-60px 100% -60px -60px)}to{clip-path:inset(-60px)}}
    .panel.active>section,.panel.active>div>section,.panel.active>div{animation:push .42s steps(10) backwards}
    .panel.active>section:nth-child(2){animation-delay:.06s}
    .panel.active>section:nth-child(3){animation-delay:.12s}
    .panel.active>section:nth-child(4){animation-delay:.18s}
    .panel.active>section:nth-child(n+5){animation-delay:.22s}

    /* --- sections below the fold: the rule draws, then the block is cut --- */
    .reveal{clip-path:inset(-60px 100% -60px -60px)}
    .reveal.seen{clip-path:inset(-60px); transition:clip-path .5s steps(12)}
    .reveal.seen.done{clip-path:none}
    .reveal .eyebrow{opacity:0}
    .reveal.seen .eyebrow{opacity:1; transition:opacity .01s steps(1) .38s}
    .reveal h2{clip-path:inset(0 100% 0 0)}
    .reveal.seen h2{clip-path:inset(0); transition:clip-path .3s steps(6) .5s}

    /* --- allocation bars fill on twos, one after another --- */
    .bar .fill{transition:transform .6s steps(9)}
      .bar:nth-child(1) .fill{transition-delay:0.100s}
      .bar:nth-child(2) .fill{transition-delay:0.150s}
      .bar:nth-child(3) .fill{transition-delay:0.200s}
      .bar:nth-child(4) .fill{transition-delay:0.250s}
      .bar:nth-child(5) .fill{transition-delay:0.300s}
      .bar:nth-child(6) .fill{transition-delay:0.350s}
      .bar:nth-child(7) .fill{transition-delay:0.400s}
      .bar:nth-child(8) .fill{transition-delay:0.450s}
      .bar:nth-child(9) .fill{transition-delay:0.500s}
      .bar:nth-child(10) .fill{transition-delay:0.550s}
      .bar:nth-child(11) .fill{transition-delay:0.600s}
      .bar:nth-child(12) .fill{transition-delay:0.650s}
      .bar:nth-child(13) .fill{transition-delay:0.700s}
      .bar:nth-child(14) .fill{transition-delay:0.750s}
      .bar:nth-child(15) .fill{transition-delay:0.800s}
      .bar:nth-child(16) .fill{transition-delay:0.850s}

    /* --- the heat rasters in --- */
    .reveal .heat i{opacity:0}
    .reveal.seen .heat i{animation:snapOn .01s steps(1) both}
      .reveal.seen .heat i:nth-child(1){animation-delay:0.250s}
      .reveal.seen .heat i:nth-child(2){animation-delay:0.264s}
      .reveal.seen .heat i:nth-child(3){animation-delay:0.278s}
      .reveal.seen .heat i:nth-child(4){animation-delay:0.292s}
      .reveal.seen .heat i:nth-child(5){animation-delay:0.306s}
      .reveal.seen .heat i:nth-child(6){animation-delay:0.320s}
      .reveal.seen .heat i:nth-child(7){animation-delay:0.334s}
      .reveal.seen .heat i:nth-child(8){animation-delay:0.348s}
      .reveal.seen .heat i:nth-child(9){animation-delay:0.362s}
      .reveal.seen .heat i:nth-child(10){animation-delay:0.376s}
      .reveal.seen .heat i:nth-child(11){animation-delay:0.390s}
      .reveal.seen .heat i:nth-child(12){animation-delay:0.404s}
      .reveal.seen .heat i:nth-child(13){animation-delay:0.418s}
      .reveal.seen .heat i:nth-child(14){animation-delay:0.432s}
      .reveal.seen .heat i:nth-child(15){animation-delay:0.446s}
      .reveal.seen .heat i:nth-child(16){animation-delay:0.460s}
      .reveal.seen .heat i:nth-child(17){animation-delay:0.474s}
      .reveal.seen .heat i:nth-child(18){animation-delay:0.488s}
      .reveal.seen .heat i:nth-child(19){animation-delay:0.502s}
      .reveal.seen .heat i:nth-child(20){animation-delay:0.516s}
      .reveal.seen .heat i:nth-child(21){animation-delay:0.530s}
      .reveal.seen .heat i:nth-child(22){animation-delay:0.544s}
      .reveal.seen .heat i:nth-child(23){animation-delay:0.558s}
      .reveal.seen .heat i:nth-child(24){animation-delay:0.572s}
      .reveal.seen .heat i:nth-child(25){animation-delay:0.586s}
      .reveal.seen .heat i:nth-child(26){animation-delay:0.600s}
      .reveal.seen .heat i:nth-child(27){animation-delay:0.614s}
      .reveal.seen .heat i:nth-child(28){animation-delay:0.628s}
      .reveal.seen .heat i:nth-child(29){animation-delay:0.642s}
      .reveal.seen .heat i:nth-child(30){animation-delay:0.656s}
      .reveal.seen .heat i:nth-child(31){animation-delay:0.670s}
      .reveal.seen .heat i:nth-child(32){animation-delay:0.684s}
      .reveal.seen .heat i:nth-child(33){animation-delay:0.698s}
      .reveal.seen .heat i:nth-child(34){animation-delay:0.712s}
      .reveal.seen .heat i:nth-child(35){animation-delay:0.726s}
      .reveal.seen .heat i:nth-child(36){animation-delay:0.740s}
      .reveal.seen .heat i:nth-child(37){animation-delay:0.754s}
      .reveal.seen .heat i:nth-child(38){animation-delay:0.768s}
      .reveal.seen .heat i:nth-child(39){animation-delay:0.782s}
      .reveal.seen .heat i:nth-child(40){animation-delay:0.796s}
      .reveal.seen .heat i:nth-child(41){animation-delay:0.810s}
      .reveal.seen .heat i:nth-child(42){animation-delay:0.824s}
      .reveal.seen .heat i:nth-child(43){animation-delay:0.838s}
      .reveal.seen .heat i:nth-child(44){animation-delay:0.852s}
      .reveal.seen .heat i:nth-child(45){animation-delay:0.866s}
      .reveal.seen .heat i:nth-child(46){animation-delay:0.880s}
      .reveal.seen .heat i:nth-child(47){animation-delay:0.894s}
      .reveal.seen .heat i:nth-child(48){animation-delay:0.908s}
      .reveal.seen .heat i:nth-child(49){animation-delay:0.922s}
      .reveal.seen .heat i:nth-child(50){animation-delay:0.936s}
      .reveal.seen .heat i:nth-child(51){animation-delay:0.950s}
      .reveal.seen .heat i:nth-child(52){animation-delay:0.964s}
      .reveal.seen .heat i:nth-child(53){animation-delay:0.978s}
      .reveal.seen .heat i:nth-child(54){animation-delay:0.992s}
      .reveal.seen .heat i:nth-child(55){animation-delay:1.006s}
      .reveal.seen .heat i:nth-child(56){animation-delay:1.020s}
      .reveal.seen .heat i:nth-child(57){animation-delay:1.034s}
      .reveal.seen .heat i:nth-child(58){animation-delay:1.048s}
      .reveal.seen .heat i:nth-child(59){animation-delay:1.062s}
      .reveal.seen .heat i:nth-child(60){animation-delay:1.076s}

    /* --- the grade is stamped, the dials cut in, the states snap --- */
    .grade{animation:stamp .28s steps(3) both; transform-origin:50% 50%}
    .rc-head .wk{animation:snapOn .01s steps(1) both .2s}
    .dial{animation:cutIn .3s steps(5) backwards}
      .dial:nth-child(1){animation-delay:0.050s}
      .dial:nth-child(2){animation-delay:0.130s}
      .dial:nth-child(3){animation-delay:0.210s}
      .dial:nth-child(4){animation-delay:0.290s}
      .dial:nth-child(5){animation-delay:0.370s}
      .dial:nth-child(6){animation-delay:0.450s}
    .dial .state{animation:stamp .22s steps(3) both}
      .dial:nth-child(1) .state{animation-delay:0.300s}
      .dial:nth-child(2) .state{animation-delay:0.380s}
      .dial:nth-child(3) .state{animation-delay:0.460s}
      .dial:nth-child(4) .state{animation-delay:0.540s}
      .dial:nth-child(5) .state{animation-delay:0.620s}
      .dial:nth-child(6) .state{animation-delay:0.700s}
    .rc-note{animation:snapOn .01s steps(1) both .5s}

    /* --- table rows snap in, top to bottom, on the book and the record --- */
    #panel-book .reveal.seen tbody tr,#panel-record .reveal.seen tbody tr{animation:snapOn .01s steps(1) both}
    #panel-book .reveal.seen tbody tr:nth-child(1),#panel-record .reveal.seen tbody tr:nth-child(1){animation-delay:0.200s}
    #panel-book .reveal.seen tbody tr:nth-child(2),#panel-record .reveal.seen tbody tr:nth-child(2){animation-delay:0.235s}
    #panel-book .reveal.seen tbody tr:nth-child(3),#panel-record .reveal.seen tbody tr:nth-child(3){animation-delay:0.270s}
    #panel-book .reveal.seen tbody tr:nth-child(4),#panel-record .reveal.seen tbody tr:nth-child(4){animation-delay:0.305s}
    #panel-book .reveal.seen tbody tr:nth-child(5),#panel-record .reveal.seen tbody tr:nth-child(5){animation-delay:0.340s}
    #panel-book .reveal.seen tbody tr:nth-child(6),#panel-record .reveal.seen tbody tr:nth-child(6){animation-delay:0.375s}
    #panel-book .reveal.seen tbody tr:nth-child(7),#panel-record .reveal.seen tbody tr:nth-child(7){animation-delay:0.410s}
    #panel-book .reveal.seen tbody tr:nth-child(8),#panel-record .reveal.seen tbody tr:nth-child(8){animation-delay:0.445s}
    #panel-book .reveal.seen tbody tr:nth-child(9),#panel-record .reveal.seen tbody tr:nth-child(9){animation-delay:0.480s}
    #panel-book .reveal.seen tbody tr:nth-child(10),#panel-record .reveal.seen tbody tr:nth-child(10){animation-delay:0.515s}
    #panel-book .reveal.seen tbody tr:nth-child(11),#panel-record .reveal.seen tbody tr:nth-child(11){animation-delay:0.550s}
    #panel-book .reveal.seen tbody tr:nth-child(12),#panel-record .reveal.seen tbody tr:nth-child(12){animation-delay:0.585s}
    #panel-book .reveal.seen tbody tr:nth-child(13),#panel-record .reveal.seen tbody tr:nth-child(13){animation-delay:0.620s}
    #panel-book .reveal.seen tbody tr:nth-child(14),#panel-record .reveal.seen tbody tr:nth-child(14){animation-delay:0.655s}
    #panel-book .reveal.seen tbody tr:nth-child(15),#panel-record .reveal.seen tbody tr:nth-child(15){animation-delay:0.690s}
    #panel-book .reveal.seen tbody tr:nth-child(16),#panel-record .reveal.seen tbody tr:nth-child(16){animation-delay:0.725s}
  }

  /* ---------- responsive ---------- */
  @media (max-width:760px){
    .bookgrid{grid-template-columns:1fr; gap:26px}
    .grade{font-size:38px; padding:9px 15px}
    .bar{grid-template-columns:52px 1fr 48px; gap:10px}
    .statusbar{gap:12px; font-size:8px}
  }
  @media (max-width:520px){
    .stats{grid-template-columns:1fr}
    .dials{grid-template-columns:1fr}
    .con{grid-template-columns:1fr}
    .cards{grid-template-columns:1fr}
    .mark{font-size:clamp(22px,7.5vw,34px); letter-spacing:.18em}
    .dateline{align-items:flex-start; text-align:left}
    .plate{flex-direction:column; align-items:flex-start}
  }
</style></head>
<body>
<div class="wipe" id="wipe" aria-hidden="true"><i class="top"></i><i class="bot"></i><i class="ln"></i></div>
<div class="wrap"><div class="sheet">
  <div class="plate">
  <header class="masthead">
    <div>
      <div class="mark">Pareidolia<span class="dot">.</span></div>
      <div class="tag">A private book run under pattern recognition.</div>
      __ORNAMENT__
    </div>
  </header>
  <div class="dateline"><span>Pareidolia LLC</span><span><b id="dlDate"></b></span><span>Est. October 2025</span></div>
  </div>
  <div class="tape" id="tape" aria-hidden="true"><div class="tapetrack" id="tapetrack"></div></div>
  <nav class="tabs" role="tablist" aria-label="Sections">
    <button class="tab active" data-panel="book" role="tab">The Book</button>
    <button class="tab" data-panel="record" role="tab">The Record</button>
    <button class="tab" data-panel="ideation" role="tab">The Lab</button>
    <button class="tab" data-panel="story" role="tab">The Story</button>
  </nav>
  <div class="stage" id="stage">
  <div class="panel active" id="panel-book">
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
  
  <section aria-label="Approach">
    <p class="eyebrow">Operations</p>
    <h2>How the book is run</h2>
    <div class="cards" style="margin-top:16px">
      <div class="appr"><h3><span class="idx">A</span>The Wheel</h3><p>The engine. We own liquid retail-momentum names and sell calls against them, laddering expiries and buying the contracts back cheap. Premium is the carry. The shares are collateral — they earn while they wait.</p><p class="ctl"><b>Limit</b> · 20% of NAV per name · tested weekly</p></div>
      <div class="appr"><h3><span class="idx">B</span>Forecast contracts <span class="tag">data run</span></h3><p>Short-dated, defined-risk positions on crypto ranges, FX fixings, index and commodity closes, across ForecastX and Kalshi. Wound down in August. It had carried most of the account's turnover and almost none of its P&amp;L. Reopened deliberately on Aug 24 to gather clean data for a systematic forecast strategy now under construction. Sized small and run for the record it produces, not for the return.</p><p class="ctl"><b>Status</b> · open · sanctioned for data · not scored</p></div>
      <div class="appr"><h3><span class="idx">C</span>Outright</h3><p>We take risk directly, and we take it rarely. These are investments, not trades. We hold them outright — no calls written against them. Thesis comes before size. We express conviction in the position and never talk it up after the fill.</p><p class="ctl"><b>Control</b> · thesis before size · held, not collateralized</p></div>
    </div>
    <p class="tag" style="margin-top:16px">Control framework: a 20% per-name limit, a 10% cash floor, stops marked before entry, and drawdowns cut rather than nursed. The limits are binding, not advisory — a breach goes into the weekly after-action whether or not the week made money.</p>
  </section>
  </div>
  <div class="panel" id="panel-record">
  <section aria-label="Weekly report card">
    <p class="eyebrow">Weekly After-Action</p>
    <div class="rc-head" id="rchead"></div>
    <div class="dials" id="dials"></div>
    <p class="rc-note" id="rcnote"></p>
    <p class="hlabel">Prior after-actions — select a week to read the full report</p>
    <p class="hnote">Dashed cards were rebuilt from the trade record after the fact; solid cards were graded live that week.</p>
    <div class="hist" id="hist"></div>
  </section>
  <section aria-label="Weekly returns as heat">
    <p class="eyebrow">Every week since inception</p>
    <h2>The record as heat</h2>
    <p class="rc-note" style="margin-top:8px">One cell per Monday-to-Friday week, oldest first. Colour is the week's time-weighted return; the outline marks a week that breached a limit. Select a cell to open its after-action.</p>
    <div class="heat" id="heat"></div>
    <div class="heat-scale" id="heatscale"></div>
  </section>
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
  <div class="panel" id="panel-ideation">
    <nav class="cnav" id="cnav" role="tablist" aria-label="Concepts">
      <button type="button" class="cbtn on" data-c="futuresight" role="tab">Concept 01<b>Futuresight Index</b></button>
      <button type="button" class="cbtn" data-c="value" role="tab">Concept 02<b>Value Scanner</b></button>
      <button type="button" class="cbtn" data-c="growth" role="tab">Concept 03<b>Quality Growth</b></button>
    </nav>

    <div class="concept active" id="con-futuresight">
    <div class="eyebrow">Concept 01 &middot; opened Aug 2026 &middot; forward-tracked</div>
    <h2>Futuresight Index</h2>
    <p class="fs-kicker">Ideation is where a thesis gets written down, weighted, and then held to a public record before any of it is traded. Futuresight is the first concept in the series.</p>
    <p class="prose">A thematic basket built from the technology that science fiction got specific about &mdash; autonomous weapons, machine intelligence, cyberware, brain interfaces, seabed mining, the data brokers, and the petrochemical layer underneath all of it. Every company is listed once, in the industry it plays into most, and tagged with the risk factor that actually moves its price.</p>
    <p class="fs-note">Calling it what it is: this is speculation, and a basket built on sentiment is closer to gambling than investing. The bet is that the story gets more expensive, not that the cash flows show up. Roughly one name in five has no earnings underneath it. Tracked forward from the open on <b id="fsIncept"></b> at fixed weights, with no trading and no hindsight. There is deliberately no backtest here: the roster was picked in August 2026 knowing what had already happened, so a historical curve would measure hindsight rather than skill. Research I run for myself, not advice. I am not a licensed financial advisor. Act on it and the risk is yours, not mine.</p>
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

    </div><!-- /con-futuresight -->

    <div class="concept" id="con-value">
      <div class="eyebrow">Concept 02 &middot; deep value screen &middot; run <span id="vsRun"></span></div>
      <h2>Value Scanner</h2>
      <p class="fs-kicker">The second concept, and the opposite instinct to the first. Futuresight buys a story; this buys a balance sheet nobody wants.</p>
      <p class="prose">A screen of the entire US market for companies trading under 3&times; sales and under 1&times; book, ranked by cheapness against quality, with the value traps that fill a raw price-to-book list flagged rather than hidden. Everything comes from free data with no API key.</p>
      <p class="fs-note">Same footing as the first concept: research I run for myself, not advice. I am not a licensed financial advisor. A screen is a starting list, not a conclusion &mdash; it says a company is statistically cheap, never that it is a good business or that the cheapness is wrong. Cheap usually means the market knows something. Act on it and the risk is yours, not mine.</p>
      <div class="tlviews" id="vsviews" role="tablist" aria-label="Value scanner views"></div>

      <div class="fsview active" id="vsv-screen">
        <div class="stats" id="vsStats"></div>
        <div class="dist" id="vsDist"></div>
        <input type="search" class="fs-search" id="vsQ" placeholder="Search ticker, company, sector\u2026" aria-label="Search the screen">
        <div class="tablewrap"><table><thead><tr id="vsHead">
          <th class="r"><button type="button" class="fs-sort" data-k="score">Score</button></th>
          <th><button type="button" class="fs-sort" data-k="ticker">Ticker</button></th>
          <th><button type="button" class="fs-sort" data-k="name">Company</button></th>
          <th class="r"><button type="button" class="fs-sort" data-k="pb">P/B</button></th>
          <th class="r"><button type="button" class="fs-sort" data-k="ps">P/S</button></th>
          <th class="r"><button type="button" class="fs-sort" data-k="fcfYield">FCF yld <span class="u">%</span></button></th>
          <th class="r"><button type="button" class="fs-sort" data-k="roe">ROE <span class="u">%</span></button></th>
          <th class="r"><button type="button" class="fs-sort" data-k="roic">ROIC <span class="u">%</span></button></th>
          <th class="r"><button type="button" class="fs-sort" data-k="mcap">Mkt cap</button></th>
          <th><button type="button" class="fs-sort" data-k="insider">Insiders</button></th>
          <th>Flags</th>
        </tr></thead><tbody id="vsRows"></tbody></table></div>
        <p class="fs-cover" id="vsCount"></p>
      </div>

      <div class="fsview" id="vsv-method">
        <h3>What it does</h3>
        <p class="prose">One screener call filters the whole US market server-side on price-to-book, price-to-sales, market cap and volume, with a guard requiring positive book value per share &mdash; a company with negative equity also satisfies &quot;P/B under 1&quot;, and those are the first thing a naive screen fills up with. A second call re-runs the same filter with Altman Z above 1.8, and anything missing from that set gets flagged. Per-name fundamentals and Form 4 insider filings are then pulled for each survivor.</p>
        <h3 style="margin-top:20px">Score</h3>
        <p class="prose">Fixed scales, so a 70 this month means the same as a 70 next month. The weights below sum to more than a hundred on purpose: each name is scored only on the components it actually has data for, and those are rescaled to a hundred between them. For banks and insurers the Z-score, current-ratio, cash-flow and return-on-invested-capital components all drop out, because none of them mean anything against a balance sheet built that way.</p>
        <div class="tablewrap"><table><thead><tr><th class="r">Weight</th><th>Component</th><th>0 points</th><th>100 points</th></tr></thead><tbody id="vsWeights"></tbody></table></div>
        <h3 style="margin-top:20px">Flags</h3>
        <div class="tablewrap"><table><thead><tr><th>Flag</th><th>Meaning</th></tr></thead><tbody id="vsFlagDoc"></tbody></table></div>
        <h3 style="margin-top:20px">Insider column</h3>
        <p class="prose">Form 4 filings over the trailing 180 days. Roughly 60% of a raw transaction list is stock awards, gifts and option exercises &mdash; compensation, not conviction &mdash; so only rows labelled Purchase count, and only rows labelled Sale count against them. <b>Heavy</b> means three or more insiders bought at least $50k between them, or purchases worth over 0.1% of market cap, and buying exceeded selling. This sits beside the score rather than inside it, so the score keeps meaning the same thing run to run.</p>
        <h3 style="margin-top:20px">The currency trap</h3>
        <p class="prose">Yahoo divides a USD market cap by local-currency revenue and book value for foreign issuers, so a Korean utility reporting in won screens at 0.2&times; book and a Chinese lender at 0.07&times; sales. Those names dominate a naive screen and every one is an exchange-rate artifact. They are detected and excluded by default.</p>
        <h3 style="margin-top:20px">What this cannot tell you</h3>
        <p class="prose">Book value is a balance-sheet number, not a liquidation value: goodwill and intangibles inflate it, so check what the book is actually made of. Sub-1&times; book is the normal resting state for banks and insurers, not a signal. Ratios are trailing twelve months while book value is most recent quarter, so a company that just cratered looks better here than it is. And the data is Yahoo\u2019s &mdash; a stale share count after a merger produces a market cap, and therefore a P/S, that is badly wrong. Sanity-check any individual name before acting on it.</p>
      </div>
    </div><!-- /con-value -->

    <div class="concept" id="con-growth">
      <div class="eyebrow">Concept 03 &middot; quality growth screen &middot; run <span id="gsRun"></span></div>
      <h2>Quality Growth</h2>
      <p class="fs-kicker">The third concept sits between the first two. Futuresight buys a story and the Value Scanner buys a balance sheet nobody wants; this one looks for a business that is already working and asks whether the market has noticed yet.</p>
      <p class="prose">A screen for companies expanding operations accretively &mdash; where capital newly put to work earns more than the capital already there &mdash; scored across seven pillars covering growth, margins and returns, cash generation, balance sheet and liquidity, capital allocation, valuation, and how thinly the name is held and covered. That last one is the tilt: a good business every fund already owns and twenty analysts already model is a worse idea than the same business nobody is writing about.</p>
      <p class="fs-note">Same footing as the other two: research I run for myself, not advice. I am not a licensed financial advisor. A screen ranks what is measurable in a filing, which is never the whole question &mdash; it cannot read a management team, a contract, or a competitor. Trailing fundamentals also cannot tell operating progress from a commodity cycle, which is why producers are flagged rather than quietly ranked. Act on it and the risk is yours, not mine.</p>
      <div class="tlviews" id="gsviews" role="tablist" aria-label="Quality growth views"></div>

      <div class="fsview active" id="gsv-screen">
        <div class="stats" id="gsStats"></div>
        <div class="dist" id="gsDist"></div>
        <input type="search" class="fs-search" id="gsQ" placeholder="Search ticker, company, sector\u2026" aria-label="Search the screen">
        <div class="tablewrap"><table><thead><tr id="gsHead">
          <th class="r"><button type="button" class="fs-sort" data-k="score">Score</button></th>
          <th><button type="button" class="fs-sort" data-k="ticker">Ticker</button></th>
          <th><button type="button" class="fs-sort" data-k="name">Company</button></th>
          <th class="r"><button type="button" class="fs-sort" data-k="revCagr3y">Rev 3y <span class="u">%</span></button></th>
          <th class="r"><button type="button" class="fs-sort" data-k="roic">ROIC <span class="u">%</span></button></th>
          <th class="r"><button type="button" class="fs-sort" data-k="incRoic">Inc ROIC <span class="u">%</span></button></th>
          <th class="r"><button type="button" class="fs-sort" data-k="fcfMargin">FCF mgn <span class="u">%</span></button></th>
          <th class="r"><button type="button" class="fs-sort" data-k="netDebtEbitda">ND/EBITDA <span class="u">×</span></button></th>
          <th class="r"><button type="button" class="fs-sort" data-k="evEbitda">EV/EBITDA <span class="u">×</span></button></th>
          <th><button type="button" class="fs-sort" data-k="insider">Insiders</button></th>
          <th>Flags</th>
        </tr></thead><tbody id="gsRows"></tbody></table></div>
        <p class="fs-cover" id="gsCount"></p>
      </div>

      <div class="fsview" id="gsv-pillars">
        <p class="prose">Every name scored on each pillar out of 100, then weighted into the headline number. A component with no data is dropped and the remaining weights re-normalised, so a missing figure never quietly scores as a zero. Sort any column to see what the screen is actually rewarding.</p>
        <div class="tablewrap"><table><thead><tr id="gsPilHead"></tr></thead><tbody id="gsPillars"></tbody></table></div>
        <p class="fs-cover" id="gsPilNote"></p>
      </div>

      <div class="fsview" id="gsv-method">
        <h3>The gate</h3>
        <p class="prose">One screener call filters the whole US market server-side, so the gate costs a single request no matter how large the universe. The published profile wants a business already earning: revenue growing, return on equity above the threshold, free cash flow positive, interest covered several times over, debt under control, and a multiple that is not already heroic. A second profile inverts it for companies not yet profitable &mdash; fast growth at a high gross margin with a net-margin ceiling and a balance sheet that can fund the wait &mdash; because a screen that only ever finds finished companies never finds one early.</p>
        <div class="tablewrap"><table><thead><tr><th>Gate</th><th>Threshold</th></tr></thead><tbody id="gsGate"></tbody></table></div>
        <h3 style="margin-top:20px">Pillar weights</h3>
        <div class="tablewrap"><table><thead><tr><th class="r">Weight</th><th>Pillar</th><th>What it measures</th></tr></thead><tbody id="gsWeights"></tbody></table></div>
        <h3 style="margin-top:20px">Accretive expansion</h3>
        <p class="prose">The question a growth screen usually dodges is whether the growth was worth buying. The measure here is incremental return on invested capital: the change in after-tax operating profit divided by the change in invested capital over three years. If new capital out-earns the existing base, the company is compounding rather than just getting larger, and the row is flagged. It is only computed when invested capital actually moved more than 5% &mdash; on a flat capital base the ratio is dividing noise by noise. Growth paid for by issuing stock shows up as dilution; growth paid for out of cash while the share count falls shows up as a buyback.</p>
        <h3 style="margin-top:20px">Liquidity, and what a bank does to it</h3>
        <p class="prose">The acid test alongside current and cash ratios, interest coverage and net debt to EBITDA. On the pre-profit profile, cash runway carries most of the balance-sheet weight, because for a company still burning it is the number that decides whether the thesis gets time to play out. The regulatory bank measures &mdash; LCR, NSFR, CET1 &mdash; are in no free data source, and corporate liquidity ratios mean nothing against a bank balance sheet anyway, so for banks and insurers those components are dropped and the rest re-weighted rather than reported wrong.</p>
        <h3 style="margin-top:20px">Flags</h3>
        <div class="tablewrap"><table><thead><tr><th>Flag</th><th>Meaning</th></tr></thead><tbody id="gsFlagDoc"></tbody></table></div>
        <h3 style="margin-top:20px">The commodity problem</h3>
        <p class="prose">Left alone, this screen fills with gold and silver miners. Their three-year growth, margin expansion and returns on capital are all genuinely excellent, and all of it is the metal price rather than operating progress. Trailing fundamentals cannot tell those apart, so producers carry a flag instead of being quietly ranked as compounders. Read a flagged name as a snapshot of where the cycle is, not as a trend.</p>
        <h3 style="margin-top:20px">What this cannot tell you</h3>
        <p class="prose">Return on invested capital here uses operating income after a flat statutory tax against reported invested capital &mdash; a proxy, not a modelled cost-of-capital comparison. Compound growth rates come from four annual filings, so the window is three years at most and shorter for anything recently listed. Institutional ownership above 100% is a real artifact of securities lending rather than a bug. And the underlying data is Yahoo\u2019s: it is occasionally wrong on individual names, so verify before acting on any of it.</p>
      </div>
    </div><!-- /con-growth -->
  </div>
  <div class="panel" id="panel-story">
  <div id="story-blocks"></div>
  <div id="panel-concepts"></div>
  <div id="page-discipline-inline"></div>
  <section aria-label="Mandate and constraints">
    <p class="eyebrow">Mandate &amp; Constraints</p>
    <h2 id="con-title"></h2>
    <div class="con" id="con"></div>
    <p class="rc-note" id="connote"></p>
  </section>
  </div>
  </div>
  <footer>
    <p>Figures are time-weighted returns and portfolio weights. Absolute balances, share counts, and dollar P&amp;L are withheld by design — transparent on performance, silent on size.</p>
    <p class="meth">PAREIDOLIA LLC · PRIVATE BOOK · FOR REVIEW ONLY · NOT AN OFFERING OR SOLICITATION · PAST PERFORMANCE IS NOT INDICATIVE OF FUTURE RESULTS</p>
  </footer>
</div></div>
<div class="statusbar" id="statusbar" aria-hidden="true"></div>
<script>
(function(){
  "use strict";
  var DATA = __DATA_JSON__;
  var FS = __FS_JSON__;
  var VS = __VS_JSON__;
  var GS = __GS_JSON__;
  var MONTHS=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  /* Charts are drawn on paper surfaces, which re-declare the palette for their
     own subtree; read the variables from there rather than from the night root
     or every line comes out in the light-on-dark values. */
  var css=function(n){
    var ref=document.querySelector(".chart-card")||document.documentElement;
    return getComputedStyle(ref).getPropertyValue(n).trim();};
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
      head.innerHTML='<div class="grade" style="background:'+c+';box-shadow:0 0 26px -6px '+c+'">'+rc.grade+'</div>'+
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
    blocks(document.getElementById("story-blocks"), pg.story);
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
  window.__drawCurve=function(){render();};
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
    var FC={AI:"#5AA0F0",DEF:"#F2854A",IND:"#3FD6A0",ENERGY:"#F0BC3C",
            DATA:"#F095B8",MED:"#4FC26A",SW:"#9D8CF0",RATES:"#F06B6B"};
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
      /* Charts are drawn on paper surfaces, which re-declare the palette for their
     own subtree; read the variables from there rather than from the night root
     or every line comes out in the light-on-dark values. */
  var css=function(n){
    var ref=document.querySelector(".chart-card")||document.documentElement;
    return getComputedStyle(ref).getPropertyValue(n).trim();};
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
            var bg=i===j?"var(--panel-2)":"rgba(255,176,0,"+(a*0.72).toFixed(3)+")";
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


  /* ---------------- Ideation: concept switcher ---------------- */
  (function(){
    var nav=document.getElementById("cnav"); if(!nav) return;
    var btns=[].slice.call(nav.querySelectorAll(".cbtn"));
    btns.forEach(function(b){
      b.addEventListener("click",function(){
        var c=b.getAttribute("data-c");
        btns.forEach(function(x){x.classList.toggle("on",x===b);});
        ["futuresight","value","growth"].forEach(function(k){
          var el=document.getElementById("con-"+k);
          if(el) el.classList.toggle("active",k===c);
        });
        if(c==="futuresight" && window.__fsDraw &&
           document.getElementById("fsv-track").classList.contains("active")) window.__fsDraw();
      });
    });
  })();

  /* ---------------- Concept 02: Value Scanner ---------------- */
  (function(){
    if(!VS || !VS.rows || !VS.rows.length) return;
    var R=VS.rows;

    var WARN={"Z-RISK":1,"NEG-FCF":1,"LOSS":1,"DEBT":1,"TIGHT":1,"SHRINK":1,"NEG-REV":1};
    var FLAGDOC=[
      ["Z-RISK","Altman Z below 1.8 \u2014 the distress zone"],
      ["NEG-FCF","Burning cash over the trailing twelve months"],
      ["LOSS","Negative net margin"],
      ["DEBT","Debt to equity above 200% \u2014 the book value is mostly the creditors'"],
      ["TIGHT","Current ratio below 1"],
      ["SHRINK","Revenue down more than 10% year over year"],
      ["NEG-REV","Negative trailing revenue, typically a mortgage REIT \u2014 no meaningful P/S"],
      ["FX","Foreign issuer reporting in a non-USD currency"],
      ["OTC","Trades off the major exchanges"],
      ["FIN","Bank, insurer or REIT \u2014 P/B is the right yardstick, the solvency ratios are not"],
      ["NEAR-LOW","Within 10% of the 52-week low"]
    ];
    var WEIGHTS=[
      ["30","Price to book","1.0","0.2"],["20","Price to sales","3.0","0.2"],
      ["12","Free cash flow yield","0%","15%"],["10","Return on equity","0%","15%"],
      ["10","Return on invested capital","0%","15%"],
      ["10","Debt to equity","200%","30%"],["10","Revenue growth","\u221220%","+10%"],
      ["10","Altman Z above 1.8","no","yes"],["8","Current ratio","1.0","2.0"]
    ];
    var INS={heavy:3,normal:2,absent:1};

    var num=function(v,d){return (v===null||v===undefined||isNaN(v))?"\u2014":v.toFixed(d===undefined?2:d);};
    var pctf=function(v){return (v===null||v===undefined||isNaN(v))?"\u2014":(v*100).toFixed(1)+"%";};
    var capf=function(v){
      if(!v) return "\u2014";
      if(v>=1e9) return "$"+(v/1e9).toFixed(1)+"B";
      return "$"+Math.round(v/1e6)+"M";
    };
    /* Banker formatting: unit lives in the header, negatives take brackets,
       positives carry no sign, nothing available is an em dash. */
    var na="\u2014";
    var ibp=function(v){                       /* a rate, as a percentage */
      if(v===null||v===undefined||isNaN(v)) return na;
      var x=v*100;
      return x<0 ? "("+Math.abs(x).toFixed(1)+")" : x.toFixed(1);};
    var ibn=function(v,d){                     /* a multiple or a ratio */
      if(v===null||v===undefined||isNaN(v)) return na;
      d=(d===undefined)?1:d;
      return v<0 ? "("+Math.abs(v).toFixed(d)+")" : v.toFixed(d);};
    var esc=function(t){return String(t==null?"":t).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/"/g,"&quot;");};

    document.getElementById("vsRun").textContent=(VS.generatedAt||"").slice(0,10);

    /* sub-views */
    var VW=[["screen","Screen"],["method","Method"]];
    var vh=document.getElementById("vsviews");
    VW.forEach(function(v,i){
      var b=document.createElement("button");
      b.type="button"; b.className="tlv"+(i===0?" active":"");
      b.setAttribute("role","tab"); b.textContent=v[1];
      b.addEventListener("click",function(){
        [].forEach.call(vh.children,function(c){c.classList.remove("active");});
        b.classList.add("active");
        VW.forEach(function(w){document.getElementById("vsv-"+w[0]).classList.toggle("active",w[0]===v[0]);});
      });
      vh.appendChild(b);
    });


    /* Twenty buckets across the observed score range, with everything at or
       above the eightieth percentile lit, so the head of the list reads as a
       shape rather than being inferred from the first few rows. */
    function drawDist(host, rows, label){
      var el=document.getElementById(host); if(!el) return;
      var v=rows.map(function(r){return r.score;}).filter(function(x){
        return x!==null&&x!==undefined&&!isNaN(x);});
      if(v.length<8){el.style.display="none"; return;}
      var lo=Math.min.apply(null,v), hi=Math.max.apply(null,v);
      var N=20, span=(hi-lo)||1, b=[], i;
      for(i=0;i<N;i++) b.push(0);
      v.forEach(function(x){b[Math.min(N-1,Math.floor((x-lo)/span*N))]++;});
      var peak=Math.max.apply(null,b);
      var sorted=v.slice().sort(function(a,c){return a-c;});
      var p80=sorted[Math.floor(sorted.length*0.8)];
      var bars=b.map(function(c,j){
        var from=lo+span*j/N, to=lo+span*(j+1)/N;
        return "<i class='"+(from>=p80?"hot":"")+"' style='height:"+
          (peak?Math.round(c/peak*100):0)+"%' title='"+c+" name"+(c===1?"":"s")+
          " scoring "+Math.round(from)+"\u2013"+Math.round(to)+"'></i>";}).join("");
      el.innerHTML="<div class='dhead'><span>"+label+"</span><span>top fifth lit \u00b7 "+
        v.length+" names</span></div><div class='bars'>"+bars+
        "</div><div class='axis'><span>"+Math.round(lo)+"</span><span>"+
        Math.round((lo+hi)/2)+"</span><span>"+Math.round(hi)+"</span></div>";
    }
    /* headline */
    var heavy=R.filter(function(r){return (r.insider||{}).level==="heavy";}).length;
    var zsafe=R.filter(function(r){return r.zSafe;}).length;
    var clean=R.filter(function(r){return !(r.flags||[]).some(function(f){return WARN[f];});}).length;
    var c=VS.criteria||{};
    document.getElementById("vsStats").innerHTML=[
      [R.length,"Names on the screen","P/S under "+(c.ps||3)+", P/B under "+(c.pb||1)],
      [clean,"No red flag","Nothing in the distress set"],
      [zsafe,"Altman Z above 1.8","Out of the distress zone"],
      [heavy,"Heavy insider buying","Three or more real buyers"]
    ].map(function(x){
      return "<div class='stat'><div class='k'>"+x[1]+"</div><div class='v'>"+x[0]+
        "</div><div class='m'>"+x[2]+"</div></div>";
    }).join("");

    drawDist("vsDist", R, "Score distribution");

    /* method tables */
    document.getElementById("vsWeights").innerHTML=WEIGHTS.map(function(w){
      return "<tr><td class='r'>"+w[0]+"</td><td>"+w[1]+"</td><td>"+w[2]+"</td><td>"+w[3]+"</td></tr>";
    }).join("");
    document.getElementById("vsFlagDoc").innerHTML=FLAGDOC.map(function(f){
      return "<tr><td><span class='vs-flag"+(WARN[f[0]]?" warn":"")+"'>"+f[0]+"</span></td><td>"+f[1]+"</td></tr>";
    }).join("");

    /* sortable table */
    var TEXT={ticker:1,name:1};
    var sk="score", sd=-1;
    var qbox=document.getElementById("vsQ");

    function val(r,k){
      if(k==="insider") return INS[(r.insider||{}).level||"absent"]||0;
      return r[k];
    }
    function sorted(rows){
      return rows.slice().sort(function(a,b){
        if(TEXT[sk]){
          var c2=(a[sk]||"").localeCompare(b[sk]||"","en",{numeric:true,sensitivity:"base"});
          return (c2||a.ticker.localeCompare(b.ticker))*sd;
        }
        var av=val(a,sk), bv=val(b,sk);
        var an=(av===null||av===undefined||isNaN(av)), bn=(bv===null||bv===undefined||isNaN(bv));
        if(an&&bn) return a.ticker.localeCompare(b.ticker);
        if(an) return 1;
        if(bn) return -1;
        if(av===bv) return a.ticker.localeCompare(b.ticker);
        return (av-bv)*sd;
      });
    }
    function head(){
      [].forEach.call(document.querySelectorAll("#vsHead .fs-sort"),function(b){
        var on=b.getAttribute("data-k")===sk;
        b.classList.toggle("on",on);
        var ar=b.querySelector(".ar");
        if(!ar){ar=document.createElement("span");ar.className="ar";b.appendChild(ar);}
        ar.textContent="\u25bc";
        b.classList.toggle("asc", on && sd===1);
        b.setAttribute("aria-sort",on?(sd===1?"ascending":"descending"):"none");
      });
    }
    [].forEach.call(document.querySelectorAll("#vsHead .fs-sort"),function(b){
      b.addEventListener("click",function(){
        var k=b.getAttribute("data-k");
        if(k===sk){sd=-sd;} else {sk=k; sd=TEXT[k]?1:-1;}
        head(); renderVS();
      });
    });

    function renderVS(){
      var q=(qbox.value||"").trim().toLowerCase();
      var rows=R.filter(function(r){
        if(!q) return true;
        return ((r.ticker||"")+" "+(r.name||"")+" "+(r.sector||"")+" "+(r.industry||"")).toLowerCase().indexOf(q)>-1;
      });
      rows=sorted(rows);
      document.getElementById("vsRows").innerHTML=rows.map(function(r){
        var ins=r.insider||{}, lv=ins.level||"absent";
        var tip=lv==="absent"?"No open-market purchases in the window"
          :((ins.buyers||0)+" buyer"+(ins.buyers===1?"":"s")+
            (ins.buyValue?", $"+Math.round(ins.buyValue/1000)+"k":"")+
            (ins.lastBuy?", last "+ins.lastBuy:"")+
            (ins.topBuyer?" \u2014 "+ins.topBuyer:""));
        var flags=(r.flags||[]).map(function(f){
          return "<span class='vs-flag"+(WARN[f]?" warn":"")+"'>"+f+"</span>";}).join("");
        return "<tr>"+
          "<td class='r'><span class='vs-score'>"+num(r.score,0)+"</span></td>"+
          "<td><b>"+r.ticker+"</b></td>"+
          "<td>"+esc(r.name)+"<span class='vs-sub'>"+esc(r.sector||"")+"</span></td>"+
          "<td class='r'>"+ibn(r.pb,2)+"</td>"+
          "<td class='r'>"+ibn(r.ps,2)+"</td>"+
          "<td class='r'>"+ibp(r.fcfYield)+"</td>"+
          "<td class='r'>"+ibp(r.roe)+"</td>"+
          "<td class='r'>"+ibp(r.roic)+"</td>"+
          "<td class='r'>"+capf(r.mcap)+"</td>"+
          "<td><span class='vs-ins "+lv+"' title=\""+esc(tip)+"\">"+lv+"</span></td>"+
          "<td>"+(flags||"<span class='vs-flag'>clean</span>")+"</td></tr>";
      }).join("");
      document.getElementById("vsCount").textContent=
        rows.length+" of "+R.length+" shown \u00b7 screened from "+(VS.universeHits||"?")+
        " names that cleared the valuation filter \u00b7 run "+(VS.generatedAt||"");
    }
    qbox.addEventListener("input", renderVS);
    head(); renderVS();
  })();

  /* ---------------- Concept 03: Quality Growth ---------------- */
  (function(){
    if(!GS || !GS.rows || !GS.rows.length) return;
    var R=GS.rows, PIL=GS.pillars||[], W=GS.weights||{}, c=GS.criteria||{};

    var WARN={"DILUTING":1,"MARGIN-SQUEEZE":1,"DECEL":1,"LEVERED":1,"ACID-FAIL":1,
              "SHORT-RUNWAY":1,"BURN":1,"UNPROFITABLE":1,"FX":1};
    var GOOD={"ACCRETIVE":1,"BUYBACK":1,"NET-CASH":1,"RULE-40":1,"INSIDER-BUY":1};
    var FLAGDOC=[
      ["ACCRETIVE","New capital is out-earning the capital already in the business"],
      ["BUYBACK","Share count down 1% a year or more over three years"],
      ["NET-CASH","More cash than total debt \u2014 can fund expansion without asking anyone"],
      ["RULE-40","Revenue growth plus free cash flow margin of 40 or better"],
      ["INSIDER-BUY","Heavy open-market insider buying in the trailing 180 days"],
      ["NEGLECTED","Lightly held, thinly covered, or small enough that most funds cannot buy it"],
      ["DILUTING","Share count growing 4% a year or more \u2014 growth per share is worse than it looks"],
      ["MARGIN-SQUEEZE","Operating margin down three points or more over three years"],
      ["DECEL","Trailing growth running five points or more below the three-year rate"],
      ["LEVERED","Net debt above three times EBITDA"],
      ["ACID-FAIL","Quick ratio below 0.8 \u2014 current liabilities exceed liquid assets"],
      ["SHORT-RUNWAY","Under eighteen months of cash at the current burn"],
      ["BURN","Negative free cash flow over the trailing twelve months"],
      ["UNPROFITABLE","Negative net income in the most recent fiscal year"],
      ["CYCLICAL","Commodity producer \u2014 the growth is the underlying price, not operating progress"],
      ["FIN","Bank or insurer \u2014 returns and liquidity components dropped, the rest re-weighted"]
    ];
    var PILDOC={
      "Growth":"Three-year compound growth in revenue, earnings and free cash flow, plus the trailing and latest-quarter rates",
      "Returns":"Return on equity and on invested capital, gross and operating margin, and the three-year margin trend",
      "Cash":"Free cash flow margin, conversion of earnings into cash, cash flow yield, and consistency across four years",
      "Balance":"The acid test with current and cash ratios, net debt to EBITDA, interest coverage and cash runway",
      "Capital":"Incremental return on new capital, share count direction, reinvestment rate and capex growth",
      "Value":"Enterprise value against EBITDA, free cash flow and sales, with forward earnings and PEG",
      "Neglect":"Institutional ownership, analyst coverage, size, distance off the high, and insider buying"
    };
    var INS={heavy:3,normal:2,absent:1};
    /* Names here carry five or six flags each, which stacks the column six deep.
       Show three and hide the rest behind a count - warnings sort first, so what
       gets hidden is never a risk. */
    var FORDER={};
    ["ACID-FAIL","SHORT-RUNWAY","LEVERED","DILUTING","MARGIN-SQUEEZE","DECEL",
     "BURN","UNPROFITABLE","FX","ACCRETIVE","RULE-40","NET-CASH","BUYBACK",
     "INSIDER-BUY","NEGLECTED","CYCLICAL","FIN"].forEach(function(f,i){FORDER[f]=i;});
    var frank=function(f){var v=FORDER[f]; return v===undefined?99:v;};

    var num=function(v,d){return (v===null||v===undefined||isNaN(v))?"\u2014":v.toFixed(d===undefined?2:d);};
    var mult=function(v){return (v===null||v===undefined||isNaN(v))?"\u2014":v.toFixed(1)+"\u00d7";};
    var pctf=function(v){return (v===null||v===undefined||isNaN(v))?"\u2014":(v*100).toFixed(1)+"%";};
    var pctS=function(v){return (v===null||v===undefined||isNaN(v))?"\u2014":(v>=0?"+":"\u2212")+Math.abs(v*100).toFixed(1)+"%";};
    var capf=function(v){
      if(!v) return "\u2014";
      if(v>=1e9) return "$"+(v/1e9).toFixed(1)+"B";
      return "$"+Math.round(v/1e6)+"M";
    };
    /* Banker formatting: unit lives in the header, negatives take brackets,
       positives carry no sign, nothing available is an em dash. */
    var na="\u2014";
    var ibp=function(v){                       /* a rate, as a percentage */
      if(v===null||v===undefined||isNaN(v)) return na;
      var x=v*100;
      return x<0 ? "("+Math.abs(x).toFixed(1)+")" : x.toFixed(1);};
    var ibn=function(v,d){                     /* a multiple or a ratio */
      if(v===null||v===undefined||isNaN(v)) return na;
      d=(d===undefined)?1:d;
      return v<0 ? "("+Math.abs(v).toFixed(d)+")" : v.toFixed(d);};
    var esc=function(t){return String(t==null?"":t).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/"/g,"&quot;");};

    document.getElementById("gsRun").textContent=(GS.generatedAt||"").slice(0,10);

    /* sub-views */
    var VW=[["screen","Screen"],["pillars","Pillars"],["method","Method"]];
    var vh=document.getElementById("gsviews");
    VW.forEach(function(v,i){
      var b=document.createElement("button");
      b.type="button"; b.className="tlv"+(i===0?" active":"");
      b.setAttribute("role","tab"); b.textContent=v[1];
      b.addEventListener("click",function(){
        [].forEach.call(vh.children,function(x){x.classList.remove("active");});
        b.classList.add("active");
        VW.forEach(function(w){document.getElementById("gsv-"+w[0]).classList.toggle("active",w[0]===v[0]);});
      });
      vh.appendChild(b);
    });


    /* Twenty buckets across the observed score range, with everything at or
       above the eightieth percentile lit, so the head of the list reads as a
       shape rather than being inferred from the first few rows. */
    function drawDist(host, rows, label){
      var el=document.getElementById(host); if(!el) return;
      var v=rows.map(function(r){return r.score;}).filter(function(x){
        return x!==null&&x!==undefined&&!isNaN(x);});
      if(v.length<8){el.style.display="none"; return;}
      var lo=Math.min.apply(null,v), hi=Math.max.apply(null,v);
      var N=20, span=(hi-lo)||1, b=[], i;
      for(i=0;i<N;i++) b.push(0);
      v.forEach(function(x){b[Math.min(N-1,Math.floor((x-lo)/span*N))]++;});
      var peak=Math.max.apply(null,b);
      var sorted=v.slice().sort(function(a,c){return a-c;});
      var p80=sorted[Math.floor(sorted.length*0.8)];
      var bars=b.map(function(c,j){
        var from=lo+span*j/N, to=lo+span*(j+1)/N;
        return "<i class='"+(from>=p80?"hot":"")+"' style='height:"+
          (peak?Math.round(c/peak*100):0)+"%' title='"+c+" name"+(c===1?"":"s")+
          " scoring "+Math.round(from)+"\u2013"+Math.round(to)+"'></i>";}).join("");
      el.innerHTML="<div class='dhead'><span>"+label+"</span><span>top fifth lit \u00b7 "+
        v.length+" names</span></div><div class='bars'>"+bars+
        "</div><div class='axis'><span>"+Math.round(lo)+"</span><span>"+
        Math.round((lo+hi)/2)+"</span><span>"+Math.round(hi)+"</span></div>";
    }
    /* headline */
    var acc=R.filter(function(r){return (r.flags||[]).indexOf("ACCRETIVE")>-1;}).length;
    var neg=R.filter(function(r){return (r.flags||[]).indexOf("NEGLECTED")>-1;}).length;
    var clean=R.filter(function(r){return !(r.flags||[]).some(function(f){return WARN[f];});}).length;
    document.getElementById("gsStats").innerHTML=[
      [R.length,"Names on the screen","Revenue over "+(c.min_growth||8)+"%, ROE over "+(c.min_roe||12)+"%"],
      [acc,"Expanding accretively","New capital out-earning the old"],
      [clean,"No red flag","Nothing in the warning set"],
      [neg,"Lightly covered","Thin ownership or thin analyst coverage"]
    ].map(function(x){
      return "<div class='stat'><div class='k'>"+x[1]+"</div><div class='v'>"+x[0]+
        "</div><div class='m'>"+x[2]+"</div></div>";
    }).join("");

    drawDist("gsDist", R, "Score distribution");

    /* method tables */
    document.getElementById("gsGate").innerHTML=[
      ["Revenue growth","above "+(c.min_growth||8)+"%"],
      ["Return on equity","above "+(c.min_roe||12)+"%"],
      ["Free cash flow","positive"],
      ["Interest coverage","above 3\u00d7"],
      ["Net debt to EBITDA","below "+(c.max_net_debt||3.5)+"\u00d7"],
      ["Enterprise value to EBITDA","below "+(c.max_ev_ebitda||20)+"\u00d7"],
      ["Market cap","above $"+(c.min_cap||300)+"M"],
      ["Listing","US-domiciled, major exchanges, no REITs"]
    ].map(function(g){return "<tr><td>"+g[0]+"</td><td>"+g[1]+"</td></tr>";}).join("");

    document.getElementById("gsWeights").innerHTML=PIL.map(function(k){
      return "<tr><td class='r'>"+(W[k]||0)+"%</td><td>"+k+"</td><td>"+(PILDOC[k]||"")+"</td></tr>";
    }).join("");

    document.getElementById("gsFlagDoc").innerHTML=FLAGDOC.map(function(f){
      var cls=WARN[f[0]]?" warn":"";
      return "<tr><td><span class='vs-flag"+cls+"'>"+f[0]+"</span></td><td>"+f[1]+"</td></tr>";
    }).join("");

    /* pillar table header */
    document.getElementById("gsPilHead").innerHTML=
      "<th><button type='button' class='fs-sort' data-k='ticker'>Ticker</button></th>"+
      PIL.map(function(k){
        return "<th class='r'><button type='button' class='fs-sort' data-k='p_"+k+"'>"+k+"</button></th>";
      }).join("")+
      "<th class='r'><button type='button' class='fs-sort' data-k='score'>Score</button></th>";

    /* sorting shared by both tables */
    var TEXT={ticker:1,name:1};
    function val(r,k){
      if(k==="insider") return INS[(r.insider||{}).level||"absent"]||0;
      if(k.indexOf("p_")===0) return (r.pillars||{})[k.slice(2)];
      return r[k];
    }
    function sortRows(rows,sk,sd){
      return rows.slice().sort(function(a,b){
        if(TEXT[sk]){
          var c2=(a[sk]||"").localeCompare(b[sk]||"","en",{numeric:true,sensitivity:"base"});
          return (c2||a.ticker.localeCompare(b.ticker))*sd;
        }
        var av=val(a,sk), bv=val(b,sk);
        var an=(av===null||av===undefined||isNaN(av)), bn=(bv===null||bv===undefined||isNaN(bv));
        if(an&&bn) return a.ticker.localeCompare(b.ticker);
        if(an) return 1;
        if(bn) return -1;
        if(av===bv) return a.ticker.localeCompare(b.ticker);
        return (av-bv)*sd;
      });
    }
    function markHead(sel,sk,sd){
      [].forEach.call(document.querySelectorAll(sel+" .fs-sort"),function(b){
        var on=b.getAttribute("data-k")===sk;
        b.classList.toggle("on",on);
        var ar=b.querySelector(".ar");
        if(!ar){ar=document.createElement("span");ar.className="ar";b.appendChild(ar);}
        ar.textContent="\u25bc";
        b.classList.toggle("asc", on && sd===1);
        b.setAttribute("aria-sort",on?(sd===1?"ascending":"descending"):"none");
      });
    }

    /* screen table */
    var sk="score", sd=-1;
    var qbox=document.getElementById("gsQ");
    [].forEach.call(document.querySelectorAll("#gsHead .fs-sort"),function(b){
      b.addEventListener("click",function(){
        var k=b.getAttribute("data-k");
        if(k===sk){sd=-sd;} else {sk=k; sd=TEXT[k]?1:-1;}
        markHead("#gsHead",sk,sd); renderGS();
      });
    });
    function renderGS(){
      var q=(qbox.value||"").trim().toLowerCase();
      var rows=R.filter(function(r){
        if(!q) return true;
        return ((r.ticker||"")+" "+(r.name||"")+" "+(r.sector||"")+" "+(r.industry||"")).toLowerCase().indexOf(q)>-1;
      });
      rows=sortRows(rows,sk,sd);
      document.getElementById("gsRows").innerHTML=rows.map(function(r){
        var ins=r.insider||{}, lv=ins.level||"absent";
        var tip=lv==="absent"?"No open-market purchases in the window"
          :((ins.buyers||0)+" buyer"+(ins.buyers===1?"":"s")+
            (ins.buyValue?", $"+Math.round(ins.buyValue/1000)+"k":"")+
            (ins.lastBuy?", last "+ins.lastBuy:""));
        var all=(r.flags||[]).slice().sort(function(a,b){return frank(a)-frank(b);});
        var shown=all.slice(0,2), rest=all.length-shown.length;
        var flags=shown.map(function(f){
          return "<span class='vs-flag"+(WARN[f]?" warn":"")+"'>"+f+"</span>";}).join("");
        if(rest>0) flags+="<span class='vs-flag more' title=\""+esc(all.join(" \u00b7 "))+"\">+"+rest+"</span>";
        flags="<div class='gs-flags'>"+flags+"</div>";
        return "<tr>"+
          "<td class='r'><span class='vs-score'>"+num(r.score,0)+"</span></td>"+
          "<td><b>"+r.ticker+"</b></td>"+
          "<td>"+esc(r.name)+"<span class='vs-sub'>"+esc(r.sector||"")+"</span></td>"+
          "<td class='r'>"+ibp(r.revCagr3y)+"</td>"+
          "<td class='r'>"+ibp(r.roic)+"</td>"+
          "<td class='r'>"+ibp(r.incRoic)+"</td>"+
          "<td class='r'>"+ibp(r.fcfMargin)+"</td>"+
          "<td class='r'>"+ibn(r.netDebtEbitda)+"</td>"+
          "<td class='r'>"+ibn(r.evEbitda)+"</td>"+
          "<td><span class='vs-ins "+lv+"' title=\""+esc(tip)+"\">"+lv+"</span></td>"+
          "<td>"+(all.length?flags:"<div class='gs-flags'><span class='vs-flag'>clean</span></div>")+"</td></tr>";
      }).join("");
      document.getElementById("gsCount").textContent=
        rows.length+" of "+R.length+" shown \u00b7 screened from "+(GS.universeHits||"?")+
        " names that cleared the gate \u00b7 "+(GS.profile||"")+" profile \u00b7 run "+(GS.generatedAt||"");
    }

    /* pillar table */
    var pk="score", pd=-1;
    [].forEach.call(document.querySelectorAll("#gsPilHead .fs-sort"),function(b){
      b.addEventListener("click",function(){
        var k=b.getAttribute("data-k");
        if(k===pk){pd=-pd;} else {pk=k; pd=TEXT[k]?1:-1;}
        markHead("#gsPilHead",pk,pd); renderPil();
      });
    });
    function renderPil(){
      var rows=sortRows(R,pk,pd);
      document.getElementById("gsPillars").innerHTML=rows.map(function(r){
        var p=r.pillars||{};
        return "<tr><td><b>"+r.ticker+"</b></td>"+
          PIL.map(function(k){
            var v=p[k];
            return "<td class='r'>"+(v===null||v===undefined?"\u2014":v)+"</td>";
          }).join("")+
          "<td class='r'><span class='vs-score'>"+num(r.score,0)+"</span></td></tr>";
      }).join("");
      document.getElementById("gsPilNote").textContent=
        "Weighted "+PIL.map(function(k){return k+" "+(W[k]||0)+"%";}).join(" \u00b7 ")+".";
    }

    qbox.addEventListener("input", renderGS);
    markHead("#gsHead",sk,sd); renderGS();
    markHead("#gsPilHead",pk,pd); renderPil();
  })();

    var ids=["book","record","ideation","story"];
    var panels={}; ids.forEach(function(id){panels[id]=document.getElementById("panel-"+id);});
    /* The swap itself. Cheap, and safe to call at any point in the wipe. */
    function swap(id){
      tabs.forEach(function(t){t.classList.toggle("active",t.getAttribute("data-panel")===id);});
      ids.forEach(function(k){panels[k].classList.toggle("active",k===id);});
      if(id==="book" && window.__drawCurve) window.__drawCurve();
      if(id==="book" && window.__animBars) window.__animBars();
      if(id==="ideation" && window.__fsDraw) window.__fsDraw();
      window.scrollTo(0,0);
      if(window.__motion) window.__motion(panels[id]);
    }

    /* Three slabs cross the frame on a stagger. The panel is exchanged while
       the second one covers it, so the change is never seen happening - the
       cut does the work, the way a wipe does in an animated cut. */
    var wipe=document.getElementById("wipe"), running=false;
    var still=window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
    /* The cut is confined to the stage - the part of it on screen, below the
       key rail. The masthead and the keys stay lit while the tube goes off. */
    function fit(){
      var st=document.getElementById("stage"), tb=document.querySelector(".tabs");
      if(!st) return;
      var r=st.getBoundingClientRect(), kb=tb?tb.getBoundingClientRect().bottom:0;
      var top=Math.max(0,r.top,kb), bot=Math.min(window.innerHeight,r.bottom);
      wipe.style.top=top+"px"; wipe.style.left=r.left+"px";
      wipe.style.width=r.width+"px"; wipe.style.height=Math.max(0,bot-top)+"px";
    }
    function activate(id){
      var cur=document.querySelector(".panel.active");
      if(still||!wipe||(cur&&cur.id==="panel-"+id)){ swap(id); return; }
      if(running) return;
      running=true;
      fit();
      wipe.classList.remove("run"); void wipe.offsetWidth; wipe.classList.add("run");
      window.__inkHold=true;
      setTimeout(function(){ swap(id); }, 230);   /* the frame is dark 170-270ms */
      setTimeout(function(){ wipe.classList.remove("run"); running=false;
        window.__inkHold=false; if(window.__tabInk) window.__tabInk(); }, 590);
    }
    tabs.forEach(function(t){t.addEventListener("click",function(){activate(t.getAttribute("data-panel"));});});
  })();


  /* ---------------- the record as heat -------------------------------------
     46 weeks at a glance. Magnitude is scaled against the largest absolute
     week in the record, so the ramp uses its whole range instead of crushing
     everything into the middle. A dial in breach outlines the cell - the grade
     already says it, but the eye finds the clusters faster than the strip. */
  (function(){
    var host=document.getElementById("heat"); if(!host||!DATA.reports) return;
    var R=DATA.reports, max=0;
    R.forEach(function(r){ max=Math.max(max,Math.abs(r.weekRet||0)); });
    if(!max) max=1;
    function paint(v){
      var a=Math.min(1,Math.abs(v)/max)*0.82+0.10;
      return v>=0 ? "rgba(61,232,122,"+a.toFixed(3)+")" : "rgba(255,90,69,"+a.toFixed(3)+")";
    }
    var chips=document.querySelectorAll("#hist .gcard");
    R.forEach(function(r,i){
      var c=document.createElement("i");
      c.style.background=paint(r.weekRet);
      var breach=(r.dials||[]).some(function(d){return d.state==="fail";});
      if(breach) c.style.borderColor="var(--down)";
      c.title=r.weekLabel+"  "+r.grade+"  "+(r.weekRet>=0?"+":"\u2212")+
        Math.abs(r.weekRet).toFixed(2)+"%"+(breach?"  (limit breached)":"");
      c.addEventListener("click",function(){
        if(chips[i]){ chips[i].click(); chips[i].scrollIntoView({block:"nearest",inline:"center"}); }
      });
      host.appendChild(c);
    });
    var sc=document.getElementById("heatscale");
    if(sc){
      var ramp=[-max,-max*0.5,-max*0.15,max*0.15,max*0.5,max].map(function(v){
        return '<i style="background:'+paint(v)+'"></i>'; }).join("");
      sc.innerHTML='<span>\u2212'+max.toFixed(1)+'%</span><span class="ramp">'+ramp+
        '</span><span>+'+max.toFixed(1)+'%</span><span style="margin-left:auto">'+
        R.length+' weeks</span>';
    }
  })();

  /* ---------------- motion: tab marker, scroll line, reveals, counters ----- */
  (function(){
    var still = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;

    /* --- boot: the nameplate is struck a key at a time --- */
    if(!still){
      var mk=document.querySelector(".mark"), tx=mk&&mk.firstChild;
      if(tx&&tx.nodeType===3){
        var frag=document.createDocumentFragment(), t=tx.nodeValue;
        for(var ci=0;ci<t.length;ci++){
          var sp=document.createElement("span"); sp.className="ch"; sp.style.setProperty("--i",ci);
          sp.textContent=t.charAt(ci); frag.appendChild(sp);
        }
        mk.replaceChild(frag,tx);
        var dot=mk.querySelector(".dot"); if(dot){ dot.classList.add("ch"); dot.style.setProperty("--i",t.length); }
      }
      setTimeout(function(){ document.documentElement.classList.add("booted"); }, 1500);
      /* a revealed section gives its clip back so nothing inside is ever trapped */
      document.addEventListener("transitionend",function(e){
        var el=e.target; if(el&&el.classList&&el.classList.contains("reveal")&&e.propertyName==="clip-path") el.classList.add("done");
      });
    }

    /* --- the slab that sits under the active tab --- */
    var bar=document.querySelector(".tabs");
    if(bar){
      var ink=document.createElement("span");
      ink.className="tabink";
      bar.appendChild(ink);
      bar.classList.add("hasink");
      var place=function(){
        if(window.__inkHold) return;   /* the slab moves after the cut, in view */
        var on=bar.querySelector(".tab.active");
        if(!on){ink.style.opacity=0;return;}
        ink.style.opacity=1;
        ink.style.left=on.offsetLeft+"px";
        ink.style.width=on.offsetWidth+"px";
        ink.style.top=on.offsetTop+"px";
        ink.style.height=on.offsetHeight+"px";
      };
      window.__tabInk=place;
      place();
      window.addEventListener("resize",place);
      /* fonts landing late can shift tab widths */
      if(document.fonts&&document.fonts.ready) document.fonts.ready.then(place);
    }

    /* --- scroll position as a hairline --- */
    if(!still){
      var prog=document.createElement("div");
      prog.className="scrollprog";
      document.body.appendChild(prog);
      var tick=false;
      var upd=function(){
        var h=document.documentElement.scrollHeight-window.innerHeight;
        var p=h>0?Math.min(1,Math.max(0,window.scrollY/h)):0;
        prog.style.transform="scaleX("+p+")";
        if(window.__sweep) window.__sweep();
        tick=false;
      };
      window.addEventListener("scroll",function(){
        if(!tick){tick=true;requestAnimationFrame(upd);}
      },{passive:true});
      upd();
    }

    /* --- sections below the fold settle in as they are reached ---
       Deliberately not an IntersectionObserver: elements added to a panel that
       was display:none a moment ago can be missed, and a missed element stays
       at opacity 0. This sweep runs on every scroll frame, so a section that
       is on screen is always visible. */
    var sweep=function(){
      var vh=window.innerHeight;
      [].forEach.call(document.querySelectorAll(".reveal:not(.seen)"),function(el){
        var r=el.getBoundingClientRect();
        if(r.top < vh*0.94 && r.bottom > 0) el.classList.add("seen");
      });
    };
    window.__sweep=sweep;
    window.__reveal=function(root){
      if(still) return;
      var host=root||document;
      [].forEach.call(host.querySelectorAll("section, .chart-card"),function(el){
        if(el.dataset.rv) return;
        var r=el.getBoundingClientRect();
        if(r.top < window.innerHeight*0.94) return;  /* already on screen: leave it */
        el.dataset.rv="1";
        el.classList.add("reveal");
      });
      sweep();
    };
    /* last resort: never leave anything hidden if the page is simply left alone */
    setTimeout(function(){
      [].forEach.call(document.querySelectorAll(".reveal:not(.seen)"),function(el){
        var r=el.getBoundingClientRect();
        if(r.top < window.innerHeight*1.6) el.classList.add("seen");
      });
    },4000);

    /* --- count-up on the headline figures ---
       Only numbers that parse cleanly are animated, and the original text is
       written back verbatim at the end, so the figure on screen at rest is
       always exactly what was rendered. */
    var countable=function(txt){
      var m=/^([^\d\-\u2212]*)(-|\u2212)?(\d[\d,]*)(\.(\d+))?(.*)$/.exec(txt.trim());
      if(!m) return null;
      var whole=m[3].replace(/,/g,"");
      if(whole.length>9) return null;
      var dec=m[5]?m[5].length:0;
      var val=parseFloat(whole+(m[5]?"."+m[5]:""));
      if(!isFinite(val)) return null;
      return {pre:m[1]||"", neg:!!m[2], val:val, dec:dec, post:m[6]||"",
              group:m[3].indexOf(",")>-1};
    };
    var fmt=function(c,v){
      var t=v.toFixed(c.dec);
      if(c.group){
        var parts=t.split(".");
        parts[0]=parts[0].replace(/\B(?=(\d{3})+(?!\d))/g,",");
        t=parts.join(".");
      }
      return c.pre+(c.neg?"\u2212":"")+t+c.post;
    };
    window.__countUp=function(root){
      if(still) return;
      var host=root||document;
      [].forEach.call(host.querySelectorAll(".stat .v"),function(el){
        if(el.dataset.ct) return;
        var final=el.textContent;
        var c=countable(final);
        if(!c){el.dataset.ct="skip";return;}
        el.dataset.ct="1";
        var t0=null, dur=760;
        var step=function(ts){
          if(t0===null) t0=ts;
          var k=Math.min(1,(ts-t0)/dur);
          var e=1-Math.pow(1-k,3);
          el.textContent=fmt(c,c.val*e);
          if(k<1) requestAnimationFrame(step);
          else{ el.textContent=final; el.classList.add("lit"); }  /* restore the rendered string exactly, then flare */
        };
        requestAnimationFrame(step);
      });
    };

    /* --- a shadow on a table that is scrolled sideways --- */
    [].forEach.call(document.querySelectorAll(".tablewrap"),function(w){
      var f=function(){w.classList.toggle("scrolled",w.scrollLeft>2);};
      w.addEventListener("scroll",f,{passive:true});
    });

    window.__motion=function(root){
      if(window.__tabInk) window.__tabInk();
      if(window.__reveal) window.__reveal(root);
      if(window.__countUp) window.__countUp(root);
    };
    window.__motion();
  })();


  /* ---------------- desk chrome: tape, function keys, status line ---------- */
  (function(){
    var sign=function(v){return (v>=0?"+":"\u2212")+Math.abs(v).toFixed(2)+"%";};
    var cls=function(v){return v>=0?"u":"d";};

    /* --- the tape: the book itself, then the headline numbers --- */
    var track=document.getElementById("tapetrack");
    if(track){
      var bits=[];
      /* positions are {t,s,w,r}: ticker, strategy, weight %, return % */
      (DATA.positions||[]).forEach(function(p){
        if(p.r===null||p.r===undefined) return;
        bits.push("<span><b>"+p.t+"</b> <span class='"+cls(p.r)+"'>"+
          sign(p.r)+"</span> <span class='sep'>"+(p.w!=null?p.w.toFixed(1)+"%":"")+
          "</span></span>");
      });
      (DATA.returns||[]).forEach(function(r){
        bits.push("<span><b>"+String(r.k).toUpperCase().replace(/RETURN \u00b7 /,"")+
          "</b> <span class='"+cls(r.v)+"'>"+sign(r.v)+"</span></span>");
      });
      if(!bits.length){                       /* nothing to say - say nothing */
        document.getElementById("tape").style.display="none";
      } else {
        /* doubled so the -50% keyframe wraps seamlessly */
        track.innerHTML=bits.join("")+bits.join("");
      }
    }

    /* --- function rail: number the tabs and bind the digits --- */
    var tabs=[].slice.call(document.querySelectorAll(".tab"));
    tabs.forEach(function(t,i){
      if(i>8) return;
      t.insertAdjacentHTML("afterbegin","<span class='fk'>"+(i+1)+"</span>");
    });
    document.addEventListener("keydown",function(e){
      if(e.metaKey||e.ctrlKey||e.altKey) return;
      var tag=(e.target.tagName||"").toLowerCase();
      if(tag==="input"||tag==="textarea"||tag==="select") return;
      var k=parseInt(e.key,10);
      if(k>=1&&k<=tabs.length){ tabs[k-1].click(); }
    });

    /* --- status line --- */
    var sb=document.getElementById("statusbar");
    if(sb){
      var ytd=(DATA.returns&&DATA.returns[0])?DATA.returns[0].v:null;
      var names=(DATA.positions||[]).length;
      var cash=null, dials=(DATA.reports&&DATA.reports.length)?
        DATA.reports[DATA.reports.length-1].dials:null;
      /* dials are {key,state,value,rule} */
      if(dials) dials.forEach(function(d){
        var m=/([\d.]+)%/.exec(d.value||""); if(/cash/i.test(d.key||"")&&m) cash=m[1]+"%";});
      var row=[["session","<span class='live'>live</span>"],
               ["as of","<b>"+(DATA.asOf||"\u2014")+"</b>"],
               ["ytd","<b class='"+(ytd>=0?"live":"")+"'>"+(ytd==null?"\u2014":sign(ytd))+"</b>"],
               ["book","<b>"+names+" names</b>"]];
      if(cash) row.push(["cash","<b>"+cash+"</b>"]);
      row.push(["keys","<b>1\u20137</b>"]);
      sb.innerHTML=row.map(function(r){return "<span>"+r[0]+" "+r[1]+"</span>";}).join("");
    }
  })();
  /* ---------------- stale-page check ----------------
     Pages sends max-age=600 on index.html and cannot be told otherwise, so a
     reader can sit on a ten-minute-old copy after a refresh. version.json is
     fetched uncached and compared against the hash baked in at build time. */
  (function(){
    var BUILD="__BUILD_ID__";
    if(!window.fetch||BUILD.charAt(0)==="_") return;
    function notice(){
      var d=document.createElement("div");
      d.className="stalebar";
      d.innerHTML="A newer edition is published. <button type='button'>Reload</button>";
      d.querySelector("button").addEventListener("click",function(){
        location.replace(location.pathname+"?v="+Date.now());
      });
      document.body.appendChild(d);
    }
    fetch("version.json?t="+Date.now(),{cache:"no-store"}).then(function(r){
      return r.ok?r.json():null;
    }).then(function(j){
      if(!j||!j.build||j.build===BUILD) return;
      var k="pb-stale-"+j.build;
      try{
        if(!sessionStorage.getItem(k)){
          sessionStorage.setItem(k,"1");
          location.replace(location.pathname+"?v="+encodeURIComponent(j.build));
          return;
        }
      }catch(e){}
      notice();          /* one reload did not clear it - stop, do not loop */
    }).catch(function(){});
  })();
})();
</script></body></html>"""

fs_path = os.path.join(HERE, "futuresight_prices.json")
fs = json.load(open(fs_path, encoding="utf-8")) if os.path.exists(fs_path) else None
if fs is None:
    print("warning: futuresight_prices.json missing - run futuresight_fetch.py; tab will render empty")

# Colourway: "note" is the banknote - cream stock, engraving green, gold and
# silver metallics. "night" is the brown-black ground with the gold band.
ORNAMENTS = {
    'none': '',
    'asanoha': '<svg class="rosette" viewBox="0 0 120 120" aria-hidden="true" focusable="false"><defs><clipPath id="omclip"><circle cx="60" cy="60" r="52"/></clipPath></defs><g clip-path="url(#omclip)" class="om om-asanoha"><path d="M1.0 1.0L31.0 1.0M1.0 1.0L23.5 14.0M31.0 1.0L8.5 14.0M16.0 27.0L16.0 1.0M1.0 1.0L23.5 -12.0M31.0 1.0L8.5 -12.0M16.0 -25.0L16.0 1.0M31.0 1.0L61.0 1.0M31.0 1.0L53.5 14.0M61.0 1.0L38.5 14.0M46.0 27.0L46.0 1.0M31.0 1.0L53.5 -12.0M61.0 1.0L38.5 -12.0M46.0 -25.0L46.0 1.0M61.0 1.0L91.0 1.0M61.0 1.0L83.5 14.0M91.0 1.0L68.5 14.0M76.0 27.0L76.0 1.0M61.0 1.0L83.5 -12.0M91.0 1.0L68.5 -12.0M76.0 -25.0L76.0 1.0M91.0 1.0L121.0 1.0M91.0 1.0L113.5 14.0M121.0 1.0L98.5 14.0M106.0 27.0L106.0 1.0M91.0 1.0L113.5 -12.0M121.0 1.0L98.5 -12.0M106.0 -25.0L106.0 1.0M121.0 1.0L151.0 1.0M121.0 1.0L143.5 14.0M151.0 1.0L128.5 14.0M136.0 27.0L136.0 1.0M121.0 1.0L143.5 -12.0M151.0 1.0L128.5 -12.0M136.0 -25.0L136.0 1.0M151.0 1.0L181.0 1.0M151.0 1.0L173.5 14.0M181.0 1.0L158.5 14.0M166.0 27.0L166.0 1.0M151.0 1.0L173.5 -12.0M181.0 1.0L158.5 -12.0M166.0 -25.0L166.0 1.0M16.0 27.0L46.0 27.0M16.0 27.0L38.5 40.0M46.0 27.0L23.5 40.0M31.0 53.0L31.0 27.0M16.0 27.0L38.5 14.0M46.0 27.0L23.5 14.0M31.0 1.0L31.0 27.0M46.0 27.0L76.0 27.0M46.0 27.0L68.5 40.0M76.0 27.0L53.5 40.0M61.0 53.0L61.0 27.0M46.0 27.0L68.5 14.0M76.0 27.0L53.5 14.0M61.0 1.0L61.0 27.0M76.0 27.0L106.0 27.0M76.0 27.0L98.5 40.0M106.0 27.0L83.5 40.0M91.0 53.0L91.0 27.0M76.0 27.0L98.5 14.0M106.0 27.0L83.5 14.0M91.0 1.0L91.0 27.0M106.0 27.0L136.0 27.0M106.0 27.0L128.5 40.0M136.0 27.0L113.5 40.0M121.0 53.0L121.0 27.0M106.0 27.0L128.5 14.0M136.0 27.0L113.5 14.0M121.0 1.0L121.0 27.0M136.0 27.0L166.0 27.0M136.0 27.0L158.5 40.0M166.0 27.0L143.5 40.0M151.0 53.0L151.0 27.0M136.0 27.0L158.5 14.0M166.0 27.0L143.5 14.0M151.0 1.0L151.0 27.0M166.0 27.0L196.0 27.0M166.0 27.0L188.5 40.0M196.0 27.0L173.5 40.0M181.0 53.0L181.0 27.0M166.0 27.0L188.5 14.0M196.0 27.0L173.5 14.0M181.0 1.0L181.0 27.0M1.0 53.0L31.0 53.0M1.0 53.0L23.5 66.0M31.0 53.0L8.5 66.0M16.0 78.9L16.0 53.0M1.0 53.0L23.5 40.0M31.0 53.0L8.5 40.0M16.0 27.0L16.0 53.0M31.0 53.0L61.0 53.0M31.0 53.0L53.5 66.0M61.0 53.0L38.5 66.0M46.0 78.9L46.0 53.0M31.0 53.0L53.5 40.0M61.0 53.0L38.5 40.0M46.0 27.0L46.0 53.0M61.0 53.0L91.0 53.0M61.0 53.0L83.5 66.0M91.0 53.0L68.5 66.0M76.0 78.9L76.0 53.0M61.0 53.0L83.5 40.0M91.0 53.0L68.5 40.0M76.0 27.0L76.0 53.0M91.0 53.0L121.0 53.0M91.0 53.0L113.5 66.0M121.0 53.0L98.5 66.0M106.0 78.9L106.0 53.0M91.0 53.0L113.5 40.0M121.0 53.0L98.5 40.0M106.0 27.0L106.0 53.0M121.0 53.0L151.0 53.0M121.0 53.0L143.5 66.0M151.0 53.0L128.5 66.0M136.0 78.9L136.0 53.0M121.0 53.0L143.5 40.0M151.0 53.0L128.5 40.0M136.0 27.0L136.0 53.0M151.0 53.0L181.0 53.0M151.0 53.0L173.5 66.0M181.0 53.0L158.5 66.0M166.0 78.9L166.0 53.0M151.0 53.0L173.5 40.0M181.0 53.0L158.5 40.0M166.0 27.0L166.0 53.0M16.0 78.9L46.0 78.9M16.0 78.9L38.5 91.9M46.0 78.9L23.5 91.9M31.0 104.9L31.0 78.9M16.0 78.9L38.5 66.0M46.0 78.9L23.5 66.0M31.0 53.0L31.0 78.9M46.0 78.9L76.0 78.9M46.0 78.9L68.5 91.9M76.0 78.9L53.5 91.9M61.0 104.9L61.0 78.9M46.0 78.9L68.5 66.0M76.0 78.9L53.5 66.0M61.0 53.0L61.0 78.9M76.0 78.9L106.0 78.9M76.0 78.9L98.5 91.9M106.0 78.9L83.5 91.9M91.0 104.9L91.0 78.9M76.0 78.9L98.5 66.0M106.0 78.9L83.5 66.0M91.0 53.0L91.0 78.9M106.0 78.9L136.0 78.9M106.0 78.9L128.5 91.9M136.0 78.9L113.5 91.9M121.0 104.9L121.0 78.9M106.0 78.9L128.5 66.0M136.0 78.9L113.5 66.0M121.0 53.0L121.0 78.9M136.0 78.9L166.0 78.9M136.0 78.9L158.5 91.9M166.0 78.9L143.5 91.9M151.0 104.9L151.0 78.9M136.0 78.9L158.5 66.0M166.0 78.9L143.5 66.0M151.0 53.0L151.0 78.9M166.0 78.9L196.0 78.9M166.0 78.9L188.5 91.9M196.0 78.9L173.5 91.9M181.0 104.9L181.0 78.9M166.0 78.9L188.5 66.0M196.0 78.9L173.5 66.0M181.0 53.0L181.0 78.9M1.0 104.9L31.0 104.9M1.0 104.9L23.5 117.9M31.0 104.9L8.5 117.9M16.0 130.9L16.0 104.9M1.0 104.9L23.5 91.9M31.0 104.9L8.5 91.9M16.0 78.9L16.0 104.9M31.0 104.9L61.0 104.9M31.0 104.9L53.5 117.9M61.0 104.9L38.5 117.9M46.0 130.9L46.0 104.9M31.0 104.9L53.5 91.9M61.0 104.9L38.5 91.9M46.0 78.9L46.0 104.9M61.0 104.9L91.0 104.9M61.0 104.9L83.5 117.9M91.0 104.9L68.5 117.9M76.0 130.9L76.0 104.9M61.0 104.9L83.5 91.9M91.0 104.9L68.5 91.9M76.0 78.9L76.0 104.9M91.0 104.9L121.0 104.9M91.0 104.9L113.5 117.9M121.0 104.9L98.5 117.9M106.0 130.9L106.0 104.9M91.0 104.9L113.5 91.9M121.0 104.9L98.5 91.9M106.0 78.9L106.0 104.9M121.0 104.9L151.0 104.9M121.0 104.9L143.5 117.9M151.0 104.9L128.5 117.9M136.0 130.9L136.0 104.9M121.0 104.9L143.5 91.9M151.0 104.9L128.5 91.9M136.0 78.9L136.0 104.9M151.0 104.9L181.0 104.9M151.0 104.9L173.5 117.9M181.0 104.9L158.5 117.9M166.0 130.9L166.0 104.9M151.0 104.9L173.5 91.9M181.0 104.9L158.5 91.9M166.0 78.9L166.0 104.9M16.0 130.9L46.0 130.9M16.0 130.9L38.5 143.9M46.0 130.9L23.5 143.9M31.0 156.9L31.0 130.9M16.0 130.9L38.5 117.9M46.0 130.9L23.5 117.9M31.0 104.9L31.0 130.9M46.0 130.9L76.0 130.9M46.0 130.9L68.5 143.9M76.0 130.9L53.5 143.9M61.0 156.9L61.0 130.9M46.0 130.9L68.5 117.9M76.0 130.9L53.5 117.9M61.0 104.9L61.0 130.9M76.0 130.9L106.0 130.9M76.0 130.9L98.5 143.9M106.0 130.9L83.5 143.9M91.0 156.9L91.0 130.9M76.0 130.9L98.5 117.9M106.0 130.9L83.5 117.9M91.0 104.9L91.0 130.9M106.0 130.9L136.0 130.9M106.0 130.9L128.5 143.9M136.0 130.9L113.5 143.9M121.0 156.9L121.0 130.9M106.0 130.9L128.5 117.9M136.0 130.9L113.5 117.9M121.0 104.9L121.0 130.9M136.0 130.9L166.0 130.9M136.0 130.9L158.5 143.9M166.0 130.9L143.5 143.9M151.0 156.9L151.0 130.9M136.0 130.9L158.5 117.9M166.0 130.9L143.5 117.9M151.0 104.9L151.0 130.9M166.0 130.9L196.0 130.9M166.0 130.9L188.5 143.9M196.0 130.9L173.5 143.9M181.0 156.9L181.0 130.9M166.0 130.9L188.5 117.9M196.0 130.9L173.5 117.9M181.0 104.9L181.0 130.9M1.0 156.9L31.0 156.9M1.0 156.9L23.5 169.9M31.0 156.9L8.5 169.9M16.0 182.9L16.0 156.9M1.0 156.9L23.5 143.9M31.0 156.9L8.5 143.9M16.0 130.9L16.0 156.9M31.0 156.9L61.0 156.9M31.0 156.9L53.5 169.9M61.0 156.9L38.5 169.9M46.0 182.9L46.0 156.9M31.0 156.9L53.5 143.9M61.0 156.9L38.5 143.9M46.0 130.9L46.0 156.9M61.0 156.9L91.0 156.9M61.0 156.9L83.5 169.9M91.0 156.9L68.5 169.9M76.0 182.9L76.0 156.9M61.0 156.9L83.5 143.9M91.0 156.9L68.5 143.9M76.0 130.9L76.0 156.9M91.0 156.9L121.0 156.9M91.0 156.9L113.5 169.9M121.0 156.9L98.5 169.9M106.0 182.9L106.0 156.9M91.0 156.9L113.5 143.9M121.0 156.9L98.5 143.9M106.0 130.9L106.0 156.9M121.0 156.9L151.0 156.9M121.0 156.9L143.5 169.9M151.0 156.9L128.5 169.9M136.0 182.9L136.0 156.9M121.0 156.9L143.5 143.9M151.0 156.9L128.5 143.9M136.0 130.9L136.0 156.9M151.0 156.9L181.0 156.9M151.0 156.9L173.5 169.9M181.0 156.9L158.5 169.9M166.0 182.9L166.0 156.9M151.0 156.9L173.5 143.9M181.0 156.9L158.5 143.9M166.0 130.9L166.0 156.9"/></g><circle class="omring" cx="60" cy="60" r="52"/><circle class="omring2" cx="60" cy="60" r="47"/></svg>',
    'shippo': '<svg class="rosette" viewBox="0 0 120 120" aria-hidden="true" focusable="false"><defs><clipPath id="omclip"><circle cx="60" cy="60" r="52"/></clipPath></defs><g clip-path="url(#omclip)" class="om om-shippo"><circle cx="4.8" cy="4.8" r="13.0"/><circle cx="4.8" cy="23.2" r="13.0"/><circle cx="4.8" cy="41.6" r="13.0"/><circle cx="4.8" cy="60.0" r="13.0"/><circle cx="4.8" cy="78.4" r="13.0"/><circle cx="4.8" cy="96.8" r="13.0"/><circle cx="4.8" cy="115.2" r="13.0"/><circle cx="23.2" cy="4.8" r="13.0"/><circle cx="23.2" cy="23.2" r="13.0"/><circle cx="23.2" cy="41.6" r="13.0"/><circle cx="23.2" cy="60.0" r="13.0"/><circle cx="23.2" cy="78.4" r="13.0"/><circle cx="23.2" cy="96.8" r="13.0"/><circle cx="23.2" cy="115.2" r="13.0"/><circle cx="41.6" cy="4.8" r="13.0"/><circle cx="41.6" cy="23.2" r="13.0"/><circle cx="41.6" cy="41.6" r="13.0"/><circle cx="41.6" cy="60.0" r="13.0"/><circle cx="41.6" cy="78.4" r="13.0"/><circle cx="41.6" cy="96.8" r="13.0"/><circle cx="41.6" cy="115.2" r="13.0"/><circle cx="60.0" cy="4.8" r="13.0"/><circle cx="60.0" cy="23.2" r="13.0"/><circle cx="60.0" cy="41.6" r="13.0"/><circle cx="60.0" cy="60.0" r="13.0"/><circle cx="60.0" cy="78.4" r="13.0"/><circle cx="60.0" cy="96.8" r="13.0"/><circle cx="60.0" cy="115.2" r="13.0"/><circle cx="78.4" cy="4.8" r="13.0"/><circle cx="78.4" cy="23.2" r="13.0"/><circle cx="78.4" cy="41.6" r="13.0"/><circle cx="78.4" cy="60.0" r="13.0"/><circle cx="78.4" cy="78.4" r="13.0"/><circle cx="78.4" cy="96.8" r="13.0"/><circle cx="78.4" cy="115.2" r="13.0"/><circle cx="96.8" cy="4.8" r="13.0"/><circle cx="96.8" cy="23.2" r="13.0"/><circle cx="96.8" cy="41.6" r="13.0"/><circle cx="96.8" cy="60.0" r="13.0"/><circle cx="96.8" cy="78.4" r="13.0"/><circle cx="96.8" cy="96.8" r="13.0"/><circle cx="96.8" cy="115.2" r="13.0"/><circle cx="115.2" cy="4.8" r="13.0"/><circle cx="115.2" cy="23.2" r="13.0"/><circle cx="115.2" cy="41.6" r="13.0"/><circle cx="115.2" cy="60.0" r="13.0"/><circle cx="115.2" cy="78.4" r="13.0"/><circle cx="115.2" cy="96.8" r="13.0"/><circle cx="115.2" cy="115.2" r="13.0"/></g><circle class="omring" cx="60" cy="60" r="52"/><circle class="omring2" cx="60" cy="60" r="47"/></svg>',
}

# Plate above the tab band: "gold" or "silver".
# Masthead ornament: "asanoha" (hemp leaf) or "shippo" (interlocking circles).
ORNAMENT = "none"

html = TEMPLATE
html = html.replace("__ORNAMENT__", ORNAMENTS[ORNAMENT])
html = html.replace("__DATA_JSON__", json.dumps(data, ensure_ascii=False))
html = html.replace("__FS_JSON__", json.dumps(fs, ensure_ascii=False))

vs_path = os.path.join(HERE, "valuescan.json")
vs = json.load(open(vs_path, encoding="utf-8")) if os.path.exists(vs_path) else None
if vs is None:
    print("warning: valuescan.json missing - run valuescan_sync.py; Concept 02 will render empty")
html = html.replace("__VS_JSON__", json.dumps(vs, ensure_ascii=False))

gs_path = os.path.join(HERE, "growthscan.json")
gs = json.load(open(gs_path, encoding="utf-8")) if os.path.exists(gs_path) else None
if gs is None:
    print("warning: growthscan.json missing - run growthscan_sync.py; Concept 03 will render empty")
html = html.replace("__GS_JSON__", json.dumps(gs, ensure_ascii=False))
# Hash the finished page (placeholder still in it) so an unchanged rebuild keeps
# the same id and never triggers a pointless reload.
import hashlib, datetime as _dt
build_id = hashlib.sha1(html.encode("utf-8")).hexdigest()[:12]
html = html.replace("__BUILD_ID__", build_id)

# Layout invariant: one width for the whole page. Every ragged edge this site
# has had came from widening or narrowing individual elements, so the build
# refuses to ship a page that has started doing it again.
_broken = []
if "tablewrap bleed" in html:
    _broken.append("a .bleed opt-in is back in the markup")
if "--sbw" in html:
    _broken.append("scrollbar-width machinery is back")
if "max-width:1120px" in html:
    _broken.append("the sheet is capped again")
if "text-align:center}" in html and "thead th,tbody td,th.r,td.r{text-align:center}" in html:
    _broken.append("table cells are being centred again")
if _broken:
    sys.exit("layout invariant broken: " + "; ".join(_broken)
             + "\n  one width for the page - see README, Layout")

with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)
with open(os.path.join(HERE, "version.json"), "w", encoding="utf-8") as f:
    json.dump({"build": build_id,
               "builtAt": _dt.datetime.now().strftime("%Y-%m-%d %H:%M")}, f)
print("built index.html (" + str(len(html)) + " bytes) from data.json"
      + (" + futuresight (" + str(fs["coverage"]["priced"]) + " priced, as of "
         + fs["asOf"] + ")" if fs else " (no futuresight data)")
      + (" + valuescan (" + str(len(vs["rows"])) + " names, run "
         + str(vs.get("generatedAt")) + ")" if vs else " (no valuescan data)")
      + (" + growthscan (" + str(len(gs["rows"])) + " names, " + str(gs.get("profile"))
         + ", run " + str(gs.get("generatedAt")) + ")" if gs else " (no growthscan data)"))
