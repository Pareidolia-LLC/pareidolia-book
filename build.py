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

     The banker's colourway - brass on deep navy, green up, red down,
     steel blue for a comparison line - on the
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
    --bg:#0A101C; --panel:#101A2B; --panel-2:#16223A; --line:#26344F;
    --ink:#E8ECF3; --muted:#9AA7BC; --faint:#697690;
    --accent:#C9A227; --accent-soft:rgba(201,162,39,.14);
    --up:#3CC77E; --down:#E0484E; --warn:#C9A227; --compare:#5B9BD5;
    --slate:#7E8CA6; --grid:rgba(232,236,243,.09);
    --gold:#C9A227; --gold-lift:#E5C55A; --paper:#101A2B;
    --silver:#9AA7BC; --silver-lift:#C3CCDB;
    --engrave:#C9A227; --label:#C9A227;
    --plate:#0A101C; --plate-edge:#26344F; --plate-rule:#C9A227; --plate-ink:#9AA7BC;
    --pinstripe:rgba(232,236,243,.030); --pinstripe-gold:rgba(201,162,39,.06);
    --glow:4px 4px 0 var(--outline), 0 0 24px rgba(229,197,90,.30);
    --outline:#05080F; --oxblood:#7A2530; --bone:#F2EDE0;
    color-scheme:dark;
    --serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,"Times New Roman",serif;
    --display:Impact,Haettenschweiler,"Franklin Gothic Demi Cond","Arial Narrow Bold","Arial Black",sans-serif;
    --sans:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    --mono:"SFMono-Regular","SF Mono",ui-monospace,"Cascadia Mono","Segoe UI Mono",Menlo,Consolas,monospace;
    --pagepad:clamp(10px,1.2vw,18px);
    --cut:cubic-bezier(.76,0,.24,1);
    --ease-out:cubic-bezier(.22,.61,.36,1);
  }

  *{box-sizing:border-box}
  html,body{margin:0; background:var(--bg)}
  ::selection{background:var(--accent); color:#0A101C}

  .wrap{background:var(--bg); color:var(--ink); font-family:var(--mono);
    min-height:100vh; padding:var(--pagepad) var(--pagepad) 70px;
    line-height:1.5; -webkit-font-smoothing:antialiased; position:relative; overflow:hidden}
  /* FRAZETTA. One warm light from the top-left, an oxblood rim answering from
     the bottom-right, and the edges falling into shadow. Under it, canvas. */
  .wrap::before{content:""; position:fixed; inset:0; z-index:0; pointer-events:none; opacity:.05;
    background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='2' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 .55 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}
  .wrap::after{content:""; position:fixed; inset:0; z-index:0; pointer-events:none;
    background:
      radial-gradient(70% 55% at 10% -6%, rgba(229,197,90,.30), rgba(201,120,40,.12) 42%, transparent 70%),
      radial-gradient(55% 45% at 102% 108%, rgba(122,37,48,.30), transparent 62%),
      radial-gradient(ellipse at 50% 45%, transparent 48%, rgba(0,0,0,.62) 100%)}
  .sheet{max-width:none; margin:0; position:relative; z-index:1}
  .stage{position:relative}

  .panel{display:none}
  .panel.active{display:block}

  /* ---------- NAGEL masthead: flat planes, one diagonal, a poster face ---------- */
  .plate{position:relative; display:flex; align-items:flex-end; justify-content:space-between;
    gap:16px 30px; flex-wrap:wrap; padding:26px 26px 22px; overflow:hidden;
    background:var(--panel); box-shadow:inset 0 0 0 2px var(--line)}
  .plate::before{content:""; position:absolute; top:0; bottom:0; left:56%; right:0; z-index:0;
    background:var(--accent); clip-path:polygon(22% 0,100% 0,100% 100%,0 100%)}
  .plate::after{content:""; position:absolute; top:0; bottom:0; left:56%; right:0; z-index:0;
    background:var(--outline); clip-path:polygon(16% 0,22% 0,0 100%,-6% 100%)}
  .masthead{display:block; padding:0; position:relative; z-index:1}
  .mark{font-family:var(--display); font-weight:400;
    font-size:clamp(44px,7.4vw,104px); line-height:.92; letter-spacing:.015em;
    text-transform:uppercase; color:var(--bone); text-shadow:var(--glow)}
  .mark .dot{color:var(--up)}
  .tag{font-family:var(--mono); font-size:11px; letter-spacing:.16em;
    text-transform:uppercase; color:var(--muted); max-width:52ch; line-height:1.7; margin:14px 0 0}
  .rosette,.om{display:none}
  .dateline{position:relative; z-index:1; display:flex; flex-direction:column; align-items:flex-end; gap:6px;
    font-family:var(--mono); font-size:10px; font-weight:600; letter-spacing:.2em; text-align:right;
    text-transform:uppercase; color:#0A101C; padding:0}
  .dateline b{color:var(--accent); background:#0A101C; padding:3px 8px; font-weight:600}

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
    background:var(--panel-2); border-bottom:3px solid var(--accent);
    overflow-x:auto; scrollbar-width:none; margin:0 0 14px}
  .tabs::-webkit-scrollbar{display:none}
  .tab{appearance:none; background:none; border:0; cursor:pointer; font:inherit;
    font-family:var(--mono); font-size:11px; font-weight:600; letter-spacing:.13em;
    text-transform:uppercase; color:var(--muted); padding:14px 20px 12px;
    white-space:nowrap; position:relative; transition:color .14s, background .14s}
  .tab{border-right:2px solid var(--line)}
  .tab .fk{color:var(--accent); margin-right:9px; opacity:1; font-weight:600; font-size:9px;
    border:1px solid var(--line); padding:1px 5px; background:var(--bg)}
  .tab.active .fk{background:#0A101C; color:var(--accent); border-color:#0A101C; opacity:1}
  .tab:hover{color:var(--ink); background:rgba(201,162,39,.06)}
  .tab.active{color:#0A101C; background:var(--accent)}
  .tabink{display:none}
  .tab:focus-visible,.tlv:focus-visible,.cbtn:focus-visible,
  .fs-sort:focus-visible,.gcard:focus-visible{outline:2px solid var(--accent); outline-offset:-3px}
  .scrollprog{position:fixed; top:0; left:0; height:2px; background:var(--accent);
    z-index:30; width:0; opacity:0; transition:opacity .2s}
  .scrollprog.scrolled{opacity:1}

  /* ---------- section heads ---------- */
  section,.concept{position:relative; margin-top:14px; border:2px solid var(--line);
    background:var(--panel); padding:36px 16px 16px}
  section::before,.concept::before{content:""; position:absolute; top:-2px; right:-2px; width:26px; height:26px;
    background:linear-gradient(to bottom left, var(--bg) 50%, var(--line) 50%, var(--line) calc(50% + 2.8px), transparent calc(50% + 2.8px))}
  .concept::before{display:none}
  section:not(:has(> .eyebrow)){padding-top:16px}
  .panel.active>section:first-child,.panel.active>div:first-child section:first-child{margin-top:0}
  .bookgrid>section{margin-top:0}
  .eyebrow{position:absolute; top:-2px; left:-2px; margin:0; display:inline-flex; align-items:center;
    padding:6px 22px 5px 12px; background:var(--accent); color:#0A101C;
    clip-path:polygon(0 0,100% 0,calc(100% - 11px) 100%,0 100%);
    font-family:var(--mono); font-size:9px; font-weight:600; letter-spacing:.24em; text-transform:uppercase;
    white-space:nowrap; max-width:calc(100% + 2px); overflow:hidden; text-overflow:ellipsis}
  .eyebrow b,.eyebrow span{color:inherit}
  h2{font-family:var(--display); font-weight:400; font-size:clamp(22px,2.1vw,30px); line-height:1;
    letter-spacing:.02em; text-transform:uppercase; margin:0 0 10px; color:var(--bone);
    text-shadow:3px 3px 0 var(--outline)}
  h3{font-family:var(--mono); font-size:12px; font-weight:600; letter-spacing:.12em;
    text-transform:uppercase; color:var(--muted); margin:0 0 8px}

  /* ---------- headline numbers: phosphor lit ---------- */
  .stats{display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr));
    gap:2px; background:var(--line); border:2px solid var(--line); margin-top:12px}
  .stat{background:var(--panel); padding:22px 22px 20px; border-top:3px solid var(--line)}
  .stat:first-child{border-top-color:var(--accent)}
  .stat .k{font-family:var(--mono); font-size:9.5px; letter-spacing:.2em;
    text-transform:uppercase; color:var(--muted)}
  .stat .v{font-family:var(--display); font-weight:400;
    font-size:clamp(46px,5.6vw,72px); letter-spacing:.01em;
    line-height:.95; margin:14px 0 0; color:var(--accent); text-shadow:3px 3px 0 var(--outline), 0 0 18px rgba(201,162,39,.22)}
  .stat .m{font-family:var(--serif); font-size:12.5px; color:var(--faint); margin-top:10px; line-height:1.5}
  .pos{color:var(--up)} .neg{color:var(--down)}
  .stat .v.pos{color:var(--up); text-shadow:3px 3px 0 var(--outline), 0 0 18px rgba(60,199,126,.28)}
  .stat .v.neg{color:var(--down); text-shadow:3px 3px 0 var(--outline), 0 0 18px rgba(224,72,78,.28)}
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
  .tlv.active{background:var(--accent); color:#0A101C; font-weight:600}
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
  .grade{font-family:var(--display); font-weight:400; font-size:58px; line-height:.9;
    letter-spacing:0; padding:12px 22px 10px; background:var(--accent); color:#0A101C;
    clip-path:polygon(0 0,100% 0,100% calc(100% - 14px),calc(100% - 14px) 100%,0 100%)}
  .rc-head .wk{font-family:var(--mono); font-size:10.5px; letter-spacing:.14em;
    text-transform:uppercase; color:var(--muted); line-height:1.9}
  .rc-head .wkret{font-weight:600; font-variant-numeric:tabular-nums}
  .rbadge{display:inline-block; font-family:var(--mono); font-size:8.5px;
    letter-spacing:.18em; text-transform:uppercase; color:var(--faint);
    border:1px solid var(--line); padding:3px 8px; margin-top:7px}
  .dials{display:grid; grid-template-columns:repeat(auto-fit,minmax(215px,1fr));
    gap:1px; background:var(--line); border:1px solid var(--line)}
  .dial{background:var(--panel); padding:16px 17px 15px; border-top:4px solid var(--line)}
  .dial.pass{border-top-color:var(--up)}
  .dial.warn{border-top-color:var(--warn)}
  .dial.fail{border-top-color:var(--down)}
  .dial .dk{font-family:var(--mono); font-size:9px; letter-spacing:.19em;
    text-transform:uppercase; color:var(--muted)}
  .state{display:inline-block; font-family:var(--mono); font-size:8.5px; font-weight:600;
    letter-spacing:.18em; text-transform:uppercase; padding:3px 8px; margin-top:9px; color:#0A101C}
  .state.pass{background:var(--up)}
  .state.warn{background:var(--warn)}
  .state.fail{background:var(--down)}
  .dial .dv{font-family:var(--display); font-weight:400;
    font-size:32px; letter-spacing:.01em; line-height:1; margin:12px 0 6px; color:var(--bone); text-shadow:2px 2px 0 var(--outline)}
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
  .gg{font-family:var(--display); font-size:26px; font-weight:400; letter-spacing:.01em; line-height:1.1; margin:4px 0 2px; text-shadow:2px 2px 0 var(--outline)}
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
  .tablewrap{overflow-x:auto; border:2px solid var(--line); margin-top:12px}
  table{width:100%; border-collapse:collapse; font-family:var(--mono); font-size:11px}
  thead th{background:var(--panel-2); color:var(--accent); font-weight:600;
    font-size:9px; letter-spacing:.17em; text-transform:uppercase; text-align:left;
    padding:7px 10px; border-bottom:1px solid var(--accent); white-space:nowrap}
  td{padding:6px 10px; border-bottom:1px solid var(--line); color:var(--muted); font-variant-numeric:tabular-nums}
  tbody tr:last-child td{border-bottom:0}
  tbody tr:hover td{background:rgba(201,162,39,.07); color:var(--ink)}
  th.r,td.r,.num.r{text-align:right}
  .tk{color:var(--ink); font-weight:600; letter-spacing:.06em}
  .chip{display:inline-block; font-family:var(--mono); font-size:8.5px;
    letter-spacing:.15em; text-transform:uppercase; padding:2px 7px; border:1px solid var(--line); color:var(--faint)}
  .chip.wheel{color:var(--accent); border-color:rgba(201,162,39,.45)}
  .chip.dir{color:var(--compare); border-color:rgba(91,155,213,.4)}

  /* ---------- strategy cards ---------- */
  .cards{display:grid; grid-template-columns:repeat(auto-fit,minmax(270px,1fr));
    gap:1px; background:var(--line); border:1px solid var(--line); margin-top:14px}
  .appr{background:var(--panel); padding:20px; display:flex; flex-direction:column; border-top:4px solid var(--accent)}
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
  .con .box{background:var(--panel); padding:17px 18px; border-top:4px solid var(--line)}
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
  /* the switcher is a second tape: the keycaps crawl in a loop (doubled in JS so the
     -50% wrap is seamless), and stop dead under a pointer, a focus or a thumb */
  .cnav{position:relative; overflow:hidden; background:var(--line); border:1px solid var(--line); margin-bottom:14px;
    -webkit-mask-image:linear-gradient(90deg,transparent 0,#000 28px,#000 calc(100% - 28px),transparent 100%);
    mask-image:linear-gradient(90deg,transparent 0,#000 28px,#000 calc(100% - 28px),transparent 100%)}
  .ctrack{display:flex; width:max-content; animation:crawl 90s linear infinite}
  .cnav:hover .ctrack,.cnav:focus-within .ctrack,.cnav.hold .ctrack{animation-play-state:paused}
  .cbtn{appearance:none; background:var(--panel); border:0; margin-right:1px; cursor:pointer; font:inherit;
    font-family:var(--mono); font-size:9px; letter-spacing:.18em; text-transform:uppercase;
    color:var(--faint); padding:12px 18px; text-align:left; white-space:nowrap;
    display:flex; flex-direction:column; gap:5px; transition:.14s}
  @media (prefers-reduced-motion:reduce){
    .cnav{-webkit-mask-image:none; mask-image:none}
    .ctrack{animation:none; width:auto; flex-wrap:wrap; gap:1px}
    .cbtn{margin-right:0; flex:1 1 150px}
    .cbtn.dup{display:none}
  }
  .cbtn b{font-size:12px; letter-spacing:.05em; color:var(--muted); text-transform:none}
  .cbtn:hover{background:var(--panel-2)}
  .cbtn.on{background:rgba(201,162,39,.12)}
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
  .vs-flag.warn{color:var(--down); border-color:rgba(224,72,78,.5)}
  .vs-flag.more{border-style:dashed; cursor:help}
  .gs-flags{display:inline-flex; gap:4px; align-items:center}
  .gs-flags .vs-flag{margin:0}
  .vs-score{font-family:var(--mono); font-weight:600; color:var(--accent)}
  .vs-sub{font-family:var(--mono); font-size:9px; color:var(--faint); letter-spacing:.06em}
  .vs-ins{display:inline-block; font-family:var(--mono); font-size:8.5px; letter-spacing:.1em; padding:1px 6px; border:1px solid var(--line); color:var(--faint)}
  .vs-ins.heavy{background:var(--accent); color:#0A101C; border-color:var(--accent); font-weight:600}
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

  /* ---------- concept memos (04-05) ---------- */
  .concept>h3{margin-top:22px}
  .fc-eq{font-family:var(--mono); font-size:13px; letter-spacing:.04em; color:var(--bone);
    background:var(--panel-2); border:2px solid var(--line); padding:10px 14px; margin:12px 0;
    overflow-x:auto; white-space:nowrap}
  .fc-won{color:var(--up); font-weight:600}

  /* ---------- lab archive: working papers, 2022-2023 ---------- */
  .lab-meta{display:flex; flex-wrap:wrap; gap:6px 14px; align-items:center; margin:0 0 14px;
    font-family:var(--mono); font-size:10px; letter-spacing:.14em; text-transform:uppercase; color:var(--faint)}
  .lab-meta b{color:var(--accent); font-weight:600}
  .lab-badge{display:inline-block; background:var(--accent); color:#0A101C; padding:3px 14px 2px 8px; font-weight:600;
    clip-path:polygon(0 0,100% 0,calc(100% - 7px) 100%,0 100%)}
  .lab-verbatim{font-family:var(--mono); font-size:9.5px; letter-spacing:.14em; text-transform:uppercase;
    color:var(--faint); margin:-4px 0 18px}
  .lab-body .prose:first-child::first-letter{float:left; font-family:var(--display); font-size:3.4em;
    line-height:.8; padding:.06em .08em 0 0; color:var(--accent)}
  .lab-cites{margin-top:18px; border-top:2px solid var(--line); padding-top:12px}
  .lab-cites summary{font-family:var(--mono); font-size:10px; letter-spacing:.16em; text-transform:uppercase;
    color:var(--muted); cursor:pointer}
  .lab-cites ol{margin:12px 0 0; padding-left:20px; font-family:var(--serif); font-size:13px; line-height:1.6; color:var(--faint)}
  .lab-cites li{margin-bottom:6px; overflow-wrap:anywhere}

  /* ---------- concept 08: systematized capital management ---------- */
  .scm-flow{display:block; width:100%; max-width:640px; height:auto; margin:10px 0 6px}

  /* ---------- concept 07: s&p roulette ---------- */
  .rl-felt{display:grid; grid-template-columns:minmax(0,400px) minmax(0,1fr); gap:28px; align-items:start; margin:22px 0 26px}
  .rl-wheelbox{display:flex; flex-direction:column; align-items:center; gap:14px; min-width:0}
  canvas#rlWheel{display:block; width:100%; max-width:400px; aspect-ratio:1; height:auto}
  .rl-verdict{width:100%; max-width:400px; background:var(--panel-2); border:2px solid var(--line); border-top:3px solid var(--accent);
    padding:14px 16px; min-height:98px; display:flex; flex-direction:column; justify-content:center; gap:3px}
  .rl-vt{font-family:var(--display); font-size:34px; line-height:1; letter-spacing:.03em; color:var(--bone); text-shadow:3px 3px 0 var(--outline)}
  .rl-vn{font-family:var(--serif); font-size:15px; line-height:1.35; color:var(--muted)}
  .rl-vm{display:flex; gap:8px; flex-wrap:wrap; align-items:center; margin-top:7px}
  .rl-verdict.idle .rl-vt{font-family:var(--mono); font-size:12px; letter-spacing:.18em; text-transform:uppercase; color:var(--faint); text-shadow:none}
  .rl-rail{display:flex; flex-direction:column; gap:20px; min-width:0}
  .rl-block{display:flex; flex-direction:column; gap:10px; min-width:0}
  .rl-label{display:flex; justify-content:space-between; align-items:baseline; flex-wrap:wrap; gap:4px 12px;
    font-family:var(--mono); font-size:9.5px; font-weight:600; letter-spacing:.18em; text-transform:uppercase; color:var(--faint)}
  .rl-label span{color:var(--muted); font-weight:400; letter-spacing:.06em; text-transform:none}
  .rl-actions{display:flex; gap:8px; flex-wrap:wrap}
  .rl-actions.after{margin-top:12px}
  .rl-btn{appearance:none; cursor:pointer; font-family:var(--mono); font-size:10.5px; font-weight:600; letter-spacing:.16em;
    text-transform:uppercase; padding:11px 18px; border:2px solid var(--accent); background:none; color:var(--accent); transition:.14s}
  .rl-btn:hover:not(:disabled){background:var(--accent-soft)}
  .rl-btn.solid{background:var(--accent); color:#0A101C; padding-right:30px; clip-path:polygon(0 0,100% 0,calc(100% - 11px) 100%,0 100%)}
  .rl-btn.solid:hover:not(:disabled){background:var(--gold-lift)}
  .rl-btn.quiet{border-color:var(--line); color:var(--muted)}
  .rl-btn.quiet:hover:not(:disabled){border-color:var(--faint); color:var(--ink); background:none}
  .rl-btn:disabled{opacity:.42; cursor:not-allowed}
  .rl-seg{margin-top:0}
  .rl-odds{display:grid; grid-template-columns:repeat(auto-fill,minmax(150px,1fr)); gap:1px; background:var(--line); border:2px solid var(--line)}
  .rl-odd{appearance:none; cursor:pointer; font:inherit; background:var(--panel); border:0; padding:9px 11px; text-align:left;
    color:var(--ink); display:flex; flex-direction:column; gap:4px; transition:.14s}
  .rl-odd:hover{background:var(--panel-2)}
  .rl-odd[aria-pressed="false"]{opacity:.36}
  .rl-on{display:flex; align-items:center; gap:7px; font-family:var(--mono); font-size:10.5px; letter-spacing:.04em; line-height:1.25}
  .rl-op{font-family:var(--mono); font-size:9.5px; color:var(--faint); font-variant-numeric:tabular-nums; padding-left:15px}
  .rl-dot{display:inline-block; width:8px; height:8px; flex:none; background:var(--c,var(--faint))}
  .rl-stake{display:flex; gap:10px; align-items:center; flex-wrap:wrap}
  .rl-fl{font-family:var(--mono); font-size:9.5px; letter-spacing:.12em; text-transform:uppercase; color:var(--faint)}
  .rl-num{font-family:var(--mono); font-size:12px; background:var(--panel); color:var(--ink); border:1px solid var(--line); padding:7px 10px; width:90px}
  .rl-num:focus{outline:none; border-color:var(--accent)}
  .rl-tag{display:inline-flex; align-items:center; gap:6px; font-family:var(--mono); font-size:9.5px; letter-spacing:.06em; color:var(--muted); white-space:nowrap}
  .chip.rl-lg{color:var(--up); border-color:rgba(60,199,126,.45)}
  .chip.rl-md{color:var(--accent); border-color:rgba(201,162,39,.45)}
  .chip.rl-sm{color:var(--compare); border-color:rgba(91,155,213,.45)}
  .rl-slot{color:var(--faint); width:30px}
  .rl-co{min-width:160px; line-height:1.3}
  #rlBook tr.locked td{background:rgba(201,162,39,.12)}
  #rlBook td:nth-child(2),#rlBook td:nth-child(4),#rlBook td:nth-child(6){white-space:nowrap}
  .rl-rowbtns{display:flex; gap:5px; justify-content:flex-end}
  .rl-mini{appearance:none; cursor:pointer; font-family:var(--mono); font-size:8.5px; font-weight:600; letter-spacing:.1em;
    text-transform:uppercase; padding:4px 8px; border:1px solid var(--line); background:none; color:var(--faint)}
  .rl-mini:hover,.rl-mini[aria-pressed="true"]{border-color:var(--accent); color:var(--accent)}
  .rl-mini[aria-pressed="true"]{background:var(--accent-soft)}
  .rl-empty{padding:30px 16px; text-align:center; font-family:var(--serif); font-size:14px; color:var(--faint)}
  .rl-mix{display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:26px; margin-top:24px}
  .rl-bars{display:flex; flex-direction:column; gap:7px; margin-top:10px}
  .rl-brow{display:grid; grid-template-columns:132px minmax(0,1fr) 96px; gap:10px; align-items:center}
  .rl-bname{display:flex; align-items:center; gap:7px; min-width:0; font-family:var(--mono); font-size:10px; color:var(--muted)}
  .rl-nm{overflow:hidden; text-overflow:ellipsis; white-space:nowrap}
  .rl-track{position:relative; height:14px; background:var(--panel-2); overflow:hidden}
  .rl-fill{position:absolute; top:0; bottom:0; left:0; background:var(--c)}
  .rl-mark{position:absolute; top:0; bottom:0; width:2px; background:var(--bone); opacity:.7}
  .rl-bval{font-family:var(--mono); font-size:10px; color:var(--faint); text-align:right; white-space:nowrap; font-variant-numeric:tabular-nums}
  .rl-bval b{color:var(--ink); font-weight:600}
  .rl-legend{display:flex; align-items:center; gap:7px; margin-top:10px; font-family:var(--mono); font-size:9.5px; letter-spacing:.06em; color:var(--faint)}
  .rl-tick{display:inline-block; width:2px; height:11px; background:var(--bone); opacity:.7}
  @media (max-width:760px){ .rl-felt{grid-template-columns:1fr; gap:22px} }
  @media (max-width:520px){ .rl-brow{grid-template-columns:92px minmax(0,1fr) 78px; gap:8px} .rl-vt{font-size:28px} }

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
    color:#0A101C; font-family:var(--mono); font-size:10px; letter-spacing:.13em; text-transform:uppercase; padding:9px 14px; text-align:center}
  .stalebar button{font:inherit; margin-left:10px; background:none; cursor:pointer; border:1px solid rgba(10,16,28,.5); color:inherit; padding:3px 10px}

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
    0%  {opacity:0; text-shadow:none; transform:translate(-6px,-6px)}
    40% {opacity:1; text-shadow:none; transform:translate(-6px,-6px)}
    100%{opacity:1; text-shadow:var(--glow); transform:none}}
  @keyframes stamp{
    0%  {transform:scale(1.7); opacity:0}
    35% {transform:scale(1.7); opacity:1}
    100%{transform:scale(1);   opacity:1}}
  @keyframes flare{
    0%  {text-shadow:3px 3px 0 var(--outline), 0 0 34px rgba(229,197,90,.95), 0 0 90px rgba(201,162,39,.55)}
    100%{text-shadow:3px 3px 0 var(--outline), 0 0 18px rgba(201,162,39,.22)}}
  @keyframes breathe{0%,100%{opacity:.82}50%{opacity:1}}
  @keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}

  /* the tab slab: one amber plane that slides between the keys */
  .tabs.hasink{position:sticky}
  .tabs.hasink .tab{position:relative; z-index:1}
  .tabs.hasink .tab.active{background:transparent; transition:color .1s steps(2) .28s}
  .tabs.hasink .tab.active .fk{transition:color .1s steps(2) .28s}
  .tabs.hasink .tabink{display:block; position:absolute; left:0; top:0; height:100%; width:0;
    background:var(--accent); z-index:0; pointer-events:none;
    clip-path:polygon(0 0,100% 0,calc(100% - 12px) 100%,0 100%);
    transition:left .44s var(--cut), width .44s var(--cut), top .44s var(--cut)}

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

    /* --- a tab change: one slanted wipe reveals the panel in place, with a
       smear on the way in. The slab on the rail moves on the same clock. --- */
    @keyframes slant{
      0%  {clip-path:polygon(0 0,0 0,-16% 100%,-16% 100%); transform:translateX(36px) scaleX(1.04)}
      100%{clip-path:polygon(0 0,116% 0,100% 100%,0 100%); transform:none}}
    .panel.active{animation:slant .44s var(--cut) backwards; transform-origin:100% 50%}

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
    .mark{font-size:clamp(40px,12vw,58px); letter-spacing:.01em}
    .dateline{align-items:flex-start; text-align:left; color:var(--muted)}
    .dateline b{background:none; padding:0}
    .plate{flex-direction:column; align-items:flex-start; padding:18px 16px}
    .plate::before,.plate::after{display:none}
  }
</style></head>
<body>
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
    <nav class="cnav" id="cnav" role="tablist" aria-label="Concepts"><div class="ctrack" id="ctrack">
      <button type="button" class="cbtn on" data-c="riskmgmt" role="tab">Concept 01<b>Investment Risk</b></button>
      <button type="button" class="cbtn" data-c="riskfinal" role="tab">Concept 02<b>Risk Management Final</b></button>
      <button type="button" class="cbtn" data-c="starbucks" role="tab">Concept 03<b>Starbucks Banking Paper</b></button>
      <button type="button" class="cbtn" data-c="analytics" role="tab">Concept 04<b>Data Analytics</b></button>
      <button type="button" class="cbtn" data-c="insops" role="tab">Concept 05<b>Insurance Operations</b></button>
      <button type="button" class="cbtn" data-c="market" role="tab">Concept 06<b>Market Overview</b></button>
      <button type="button" class="cbtn" data-c="roulette" role="tab">Concept 07<b>S&amp;P Roulette</b></button>
      <button type="button" class="cbtn" data-c="scm" role="tab">Concept 08<b>Capital Management</b></button>
      <button type="button" class="cbtn" data-c="forecast" role="tab">Concept 09<b>Forecast Events</b></button>
      <button type="button" class="cbtn" data-c="xbox" role="tab">Concept 10<b>Xbox Takeover</b></button>
      <button type="button" class="cbtn" data-c="futuresight" role="tab">Concept 11<b>Futuresight Index</b></button>
      <button type="button" class="cbtn" data-c="value" role="tab">Concept 12<b>Value Scanner</b></button>
      <button type="button" class="cbtn" data-c="growth" role="tab">Concept 13<b>Quality Growth</b></button>
    </div></nav>

    <div class="concept active" id="con-riskmgmt">
      <div class="eyebrow">Concept 01 &middot; portfolio risk &middot; Nov 27, 2022</div>
      <h2>Investment Risk Management</h2>
      <div class="lab-meta"><span>Written <b>November 27, 2022</b></span><span>Portfolio risk taxonomy</span></div>
      <p class="fs-kicker">Written thirteen days after FTX filed for bankruptcy, working through the wreckage while it was still moving. Runs the full taxonomy — emerging, international, overdiversification and concentration, management, market, liquidity and credit — and does not stop at the abstract: the concentration section names the position sizing in the author's own account at the time.</p>
      <p class="lab-verbatim">Reproduced verbatim · figures and positions as of Nov 2022</p>
      <div class="lab-body">
        <p class="prose">Investments are the life blood of any corporate entity or individual pursuing wealth acquisition over a set time frame. There are a variety of investments the most common of which are traditionally stocks, real estate, bonds, certificate deposits and treasury bills (Finra). There are also alternatives for the more risk tolerant investor such as crypto, trading cards, shoes and anything in between that one expects to store value and potentially increase in monetary value. Naturally with any investment there is risk associated with any returns, these portfolio risks include emerging risk, governance risk, overdiversification risk, concentration risk, market risk, interest rate risk, liquidity risk, credit risk, international risk and of course price risk, while every investor may be affected by risk differently the tools in managing risk are quite similar based on the type of risk (Successfully Treating Risk units 8 and 9).</p>
        <p class="prose">In mitigating risk within a portfolio, investors must be forward thinking in order to predict, quantify or qualify holdings, in doing so investors will avoid financial headache of losing their shirts. Emerging risk as defined by Swiss Re are the risks which 'are newly developing or changing risks that are difficult to qualify" (Swiss Re). One of the most recent emerging risks which came to pass in February was the "Russian Special Military Operation" which led to many American companies ceasing operation in Russia as a result and to penalize the Russian economy. An eager eyed investor would have seen the opportunity that arose due to this black swan event in Ukraine but would soon be restricted after June 6th 2022 due to an executive order from President Biden (U.S Department of Treasury). In doing so Americans can no longer purchase Russian securities which would have been an emerging risk at the beginning of the year but somewhat foreseeable following the invasion. To properly manage emerging risk investors, governments and business entities must adapt to the new world depending on any or all currently known variables. For example, when managing a family member's retirement portfolio, one theoretically takes a varying risk averse approach dependent on the age of the account holder. In this hypothetical a 20-year-old son is managing one of his father's accounts which has a quarter million in total value distributed among cash, securities and bonds which are soon to mature. The boy has been investing for a while and assumes that it is in his best interest to grow and manage the account's value as he believes it is his inheritance. The emerging risk for the boy is whether or not he sees a penny of what he assumes is his inheritance but for father the risk is the boy's management of his capital, what happens when the boy realizes it is or is not his inheritance and overall long-term performance. Pertaining to risk overall in investing emerging risk may potentially be foreseeable but is just the tip of the iceberg of investment risk.</p>
        <p class="prose">With investing internationally investors need to be aware of international risk. International risk is made up of other risks which include political, economic or transfer risks pertaining to operating in a foreign nation like Iran, Ukraine, Brazil, Russia or any other foreign nation an investor or business entity is looking to invest in to expand their wealth or grow their operations (Santander). The most common of the international risk is political risk pertaining to the political environment of foreign nation and foreign exchange risk relating to the fluctuations in a currency's value, for example a major political risk could be the nationalization of a major industry or the similar to Exxon expanding its operations in Guyana where a variety of risks are at play ranging from terrorism, pirates and various other political risks (Huchzermeyer). As mentioned earlier leaving a nation to minimize political risk and to some extent product relations with existing domestic customers leaving a nation is optimal akin to pulling out of Russia like McDonalds, Visa and several companies which left outright or phased out of the nation following its invasion of Ukraine. Additionally, if there is a political and economic vacuum a cartel could arise and capture influence of a portion of a nation like what the Sinaloa Cartel has done and continues to grow outward from Mexico into Latin America and other regions, surely there is opportunity for a more risk inclined investor but the character of an investor or a business entity's ethics will be brought into question for why they participate in investing in countries which have a less savory sense of ethics, lack of control and for providing liquidity to what some call thugs, criminals and terrorists (Felbab-Brown). Lastly returning to foreign exchange risk there is also a component which is transfer risk, foreign exchange risk as I mentioned earlier relates to the fluctuation in a currency's value where transfer risk picks up the slack and is the potential for loss in changing one currency for another essentially acting as a premium depending on the value of the currency favored for a transaction (Successfully Treating Risk unit 8, Santander). Naturally investors must be aware of cash flows to be able to overview how capital is utilized and see the gains and losses due to foreign exchange fluctuations usually shown within a company's financial statements.</p>
        <p class="prose">Within a personal investment portfolio or portfolio of operations the risk of overdiversification and concentration are important to be aware of for all investment ventures. In this investors and business entities must be fully aware of portfolio makeup and restricting expansion of positions and operations in a nation, target market, asset or equity. The most recent financial disaster which was a warning about concentrating positions in various portfolios was the financial crisis and most recently the crypto-commodity broker FTX which has filed for bankruptcy during the second week of November 2022. In the case of the Financial Crisis several major banks and financial institutions such as Goldman Sachs, AIG, Lehman, Bank of America and along with several other firms were concentrated in collateralized loans, ninja loans and other debt instruments which were being overleveraged to increase profitability (Gethard). While it is important to recognize leverage and improper due diligence along with over lending to unworthy borrowers contributed to the crisis, selling and packaging the mortgages as new products and essentially playing roulette with mortgage-backed securities and betting on red while ball lands on black and the House always wins. On the individual level I am concentrated in one of my brokerage accounts with one of my positions where a software firm I believe has long term value which is not realized by the market is the core of the account making up roughly 38-44% of my portfolio depending on the day and market consensus however in addressing the volatility and concentration I am diversified to some regard where I have the rest of the portfolio with various stalwart and conservative firms such as Exxon, McDonalds, JPMorgan, and a two other financial institutions and a marginal and growing position in a defense firm as a speculative investment. While my approach may be inappropriate for an older individual, I believe this was the best approach for short term wealth acquisition for the near future whereas with my retirement account which is a Roth IRA. In my IRA I am perfectly diversified just by holding the Vanguard Total World Stock Index Fund which is globally diversified while holding a tiny position in other individual stocks which are not at the core focus or philosophy with that account which is long term wealth accumulation. A side effect of this is my investment management style which every investor and investment manager has and with that pertaining to investing introduces management risk.</p>
        <p class="prose">In investing as a firm, board or individual decisions must be made, justified and argued then financed or acted on. This could be anything ranging from increasing pay within the firm presumably increasing overhead, cutting a losing position which has underperformed for the last few quarters or cancelling a project due to unknown cost constraints previously unknown when the project was initially approved or cut due to a decision made by the board or management. In investing in any firm, a piece of due diligence which investors must be aware of or at least familiar with is the makeup and potentially character of management in order to address management risk and be confident in their competency to perform their duties, tackle issues and have a firm operating and growing properly while also maximizing shareholder value (Tong). While the crypto market may be a bloodbath with the loss of a firm valued at $32 billion and the $1billion in customer funds which were held with FTX is the best example in recent years of negligent management in addressing operational risks and the decisions made by the former Chief Executive Officer Sam Bankman-Fried leading to the firm's collapse and bankruptcy while more information on the firm's exploits flood the press since last week. To lose $1billion of customers funds is inexcusable especially for a firm which was one of if not the largest crypto firms in the world prior to its collapse. With the information available at the time of November 17th FTX was overleveraged, participating in highly volatile crypto derivatives and not holding enough stable-coins which are pegged to the dollar or simply did not have enough cash on hand to mitigate the risks they were taking and it blew up in their faces. The nuclear explosion that was FTX's bankruptcy is still being looked into by journalists, crypto hobbyists and yes-men, bankers, lawyers, Wall Street along with anyone with an interest in finance (David Yaffe-Bellany). It is a shame that one firm, person or group's management, decision making and actions can turn a firm or portfolio into a golden goose or become a nuclear explosion wiping out everyone and thing that was involved with it just like FTX and Enron did, perhaps the crypto market should have expected this outcome due to their immense risk tolerance and high-risk appetites.</p>
        <p class="prose">In portfolio management market risk is prevalent in the daily fluctuations and the volatility of a stock's price fluctuating with how market factors such as interest rates, the overall market and commodity prices (Risk.net). With market risk there are a variety of factors that could cause fluctuations or price volatility akin to how interest rates can improve or destroy returns depending on how low or high the Federal Reserve sets interest rates at a given time in order to stimulate or constrict the American economy. In the case for returns overall with higher interest rates, returns will be reduced if not eliminated depending on how high interest rates are for an investor or firm reducing their return on investment or return on debt eliminating any benefits of leverage and reducing the amount of leverage therefore reducing how much capital can be utilized during a recession or depression. Contrarily with lower interest rates firms and investors will borrow and be more leveraged as the cost of debt can be justified with the additional return to a firm's or investor's portfolio increasing their return on investment and return on debt justifying the cost of the leverage. While leverage is important it is a decision by management to utilize the acknowledgement of cost of debt and the cost of debt and return relationship is important to identify with varying interest rates to simulate different economic scenarios within a portfolio to project returns of a portfolio or project and plan and act on. While interest is important to address and act around when the state of the economy is varying firms like the ones in the oil industry and its investors must know the factors which fluctuate and go into gas production such as steel and the chemicals which go into the oil products during the treatment process and production of oil derivatives. In the case of oil, a variety of factors go into the pricing at the pump ranging from commodity traders betting on the price of a barrel of oil, price of steel, war and whether or not if a nation increases or constricts its production of oil in recent years it usually is Saudi Arabia. In my own personal scenario within my portfolio each individual position has a variety of factors I am aware and unaware of however with a more volatile investment I watch every little factor and opportunity like a hawk because I am hedging the rest of the portfolio against it. As a result, if that firm falls an additional 20%, I will sell off a good chunk of that position but my intrigue has the better of me and I feel like I need to know how this firm will position itself for the future and would love to see the long-term implications of an Enterprise data solutions firm whose products are industry agnostic. Simply put supply and demand are the primary motivators of a stock's price action however the demand for their goods is a baseline the demand of a firm's stock could also be overbought or oversold but does not necessarily equate to the firm being over or undervalued. The overall market pushes the consensus in the equity markets that translates to a stocks nominal 'price' and whether Elon Musk tweeted something relevant to Tesla or Twitter. Being informed on every factor involved with an investment is necessity in order to not be blindsided by the price action of equities or to reinvest, reduce, exit or cancel a project as the internal rate of return, net present value or any other factor the project is dependent on becomes far too expensive to upkeep.</p>
        <p class="prose">In managing leverage there are liquidity and credit risk, liquidity being the measure of how quickly assets can be turned to cash in a worst-case scenario while credit worthiness measures and can verify whether a firm is able to pay its debts based on the cashflows from operations and other assets and collateral that can be used to construct a loan and repayment agreement. A healthy number of firms and investors are leveraged but the real trick is to utilize it properly, there best examples to realize the failure of improper leverage utilization are best the Financial Crisis, the FTX implosion and within the portfolios of anonymous investors on investment forums across the web. In the case of the financial crisis as mentioned earlier a variety of financial institutions were improperly leveraged and operating improperly by loaning to unqualified individuals, securitizing mortgages and selling the securities back to the market until it was discovered it was all a fugazi and rocked the financial world in 2008-2009. The best misappropriation of funds and leverage recently was the FTX fiasco which is still unfolding but an important lesson on mismanagement of leverage, derivative and destroying involved and tied to the firm, the caveat with the Financial crisis was that the Federal government created the TARPS program which gave banks cash for preferred stock in order to secure the stability of the financial sector whilst also upholding safety and soundness of the banking system while some firms were acquired, dissolved or allowed to collapse like the Lehman Brothers. Additionally, the most interesting part of the financial crisis was that the banks which were overleveraged were loaning out what they could under the reserve requirements as their primary profit centers come from lending and since 2008 the reserve has grown and shrunk under different political administrations. Within personal finances varying on the individual credit risk exposure is most likely a credit card or mortgage which is subsidized by ones income stream(s) in order to not default and face the financial repercussions, whereas similarly when using margin in an investment portfolio one borrows against his own equities, securities and 'cash' held within the account and the repercussions for that would god forbid get margin called where a improper amount of due diligence or sheer lack of reasonable risk management skills occurred and will obliterate a portfolio assuming a portion of it is still around due to the ability a brokerage may sell securities which are held by any investor. The only way to mitigate liquidity is to hold assets and cash on hand while credit or leverage must be utilized within what a firm or investor can tolerate without it being a burden. Utilizing margin is like playing with fire and the financial horror stories and firms that have collapsed due to improper utilization of debt serve as a warning to me and many other younger and less experienced investors.</p>
        <p class="prose">Like history there are a variety of instances where risks had to be taken or mitigated, occasionally they are unavoidable or side effects of risk mitigation strategies like the accidental burning of the Library of Alexandria during the Civil War between Julius Caesar and Pompey (Mid-Continent Public Library). The actual ability to manage risk and properly mitigate it or exploit it shows preparation, adaptability and fortitude of an investor or the management within a firm to not jump ship when a situation turns for the worst but steering through the storm of improper risk management with investments and projects. Whether an Investor is a degenerate gambler or a sophisticated investor, it is paramount to be aware of any or all risks associated with an investment.</p>
      </div>
      <details class="lab-cites"><summary>Works cited · 12 sources</summary><ol><li>"Emerging Risks." Swiss Re Group, 15 Sept. 2022.</li><li>Felbab-Brown, Vanda. "The Foreign Policies of the Sinaloa Cartel and CJNG – Part I: In the Americas." Brookings, 22 July 2022.</li><li>"Frequently Asked Questions - Newly Added." U.S. Department of the Treasury, 6 June 2022. Accessed 8 Nov. 2022.</li><li>Gethard, Gregory. "Falling Giant: A Case Study of AIG." Investopedia, 27 Feb. 2022.</li><li>"Historical Libraries: The Library of Alexandria." Mid-Continent Public Library. Accessed 22 Nov. 2022.</li><li>Huchzermeyer, Laura. "Surging Crude Export Volumes Confront Record Freight Rates." S&amp;P Global Commodity Insights, 3 Nov. 2022.</li><li>"International Risk Management: Exchange Rate Risk and Insurance Management." Santandertrade.com. Accessed 8 Nov. 2022.</li><li>Investment products. Investment Products | FINRA.org. (n.d.). Retrieved October 31, 2022.</li><li>"Market Risk Definition." Risk.Net. Accessed 22 Nov. 2022.</li><li>Successfully Treating Risk, 1st edition (ARM 402) The Institutes Collegiate Edition.</li><li>Tong, Scott. "How Shareholders Jumped to First in Line for Profits." Marketplace, 25 Apr. 2022.</li><li>Yaffe-Bellany, David. "How Sam Bankman-Fried's FTX Crypto Empire Collapsed." The New York Times, 14 Nov. 2022.</li></ol></details>
      <p class="fs-note">Research I run for myself, not advice. I am not a licensed financial advisor. Reproduced word for word as submitted in November 2022, so its figures, forecasts and positions reflect that date rather than a current view. Act on it and the risk is yours, not mine.</p>
    </div><!-- /con-riskmgmt -->

    <div class="concept" id="con-riskfinal">
      <div class="eyebrow">Concept 02 &middot; risk appetite &middot; Dec 7, 2022</div>
      <h2>Risk Management Final</h2>
      <div class="lab-meta"><span>Written <b>December 7, 2022</b></span><span>Risk tolerance &amp; treatment</span><span class="lab-badge">Proto-Pareidolia</span></div>
      <p class="fs-kicker">The first place the operating rule appears in writing: <b>one concentrated high-risk position, the rest of the book deliberately hedging against it.</b> Written ten days after Concept 01, while still job hunting and saying so plainly. Runs from Amazon fulfillment floors to eBay shipping economics to the decision to move a YouTube channel off the author's own name — risk treatment as a practice rather than a subject.</p>
      <p class="lab-verbatim">Reproduced verbatim · written Dec 2022</p>
      <div class="lab-body">
        <p class="prose">In life there are a variety of risks. Risk can be as simple as trying something new or going with what someone already enjoys or loves like a Diet Coke or trying something a new limited time flavor Coke or alternative Cola. While these examples are marginal to risk overall application of risk management and treating or reducing it depends on each individual.</p>
        <p class="prose">In the application of risk management individuals must decide the course of action given a risk or set of risks (or variables) and plan a course of action. So, what is risk? Risk according to Merriam Webster is the "possibility of loss…" meaning that going to a casino means you most likely risk whatever money you have while you're at the blackjack table. Risk is a good and bad thing but also depends on the person who is asked and how a situation is going based on variable circumstance. In my case I like risk when the risk and reward are justified for instance if I could have a 50 percent chance that I can bet 10 dollars and get 15 back and get a 5-dollar profit while there's also a 50 percent chance that I lose 5 dollars and only get back 5 I would not take the gamble. Whereas if the probability for a 5-dollar profit was 60-80 percent and loss probability was 20-40% I would be more inclined to take the risk. In taking risk there should be some level of justification in order to warrant an action in a scenario, in my life the risks I am taking to secure a job in my field of interest are going to college, job hunting and networking which I am currently failing at in securing a job. In other cases, as a workaholic there are cases where far too many things are ongoing and this or that will fall through the cracks and the real risk treatment is how you go forward with unforeseen events and failures.</p>
        <p class="prose">I personally successfully and unsuccessfully actively and passively manage and treat risk in investment portfolios I manage for my parents and myself, when I worked at an Amazon Fulfillment Center during the summer of 2021 and while I was an active seller on eBay between early 2020 through the middle of 2022. Managing risk in an investment portfolio is very individualistic and relies on the type of account and the individual's risk tolerance and risk appetite. Naturally a 22-year-old man has a higher risk tolerance and risk appetite than a 61-year-old man and creating a portfolio to address each investors needs and goals is the magic of making a long-term portfolio. In managing risk in portfolios, it is best to diversify positions and have the total value of a portfolio distributed among cash, securities and bonds at varying times to maturity. I hedge my positions with my risk tolerance and acceptance due to a concentration in a certain position in my personal portfolio. In the case of my investment portfolio, I have a high-risk tolerance with a concentration in one high risk position while the rest of the portfolio is hedging against that position in lower risk equities and unrelated industries. In managing an elder's portfolio and my retirement portfolio the risk tolerance is a polar opposite since the goal is risk mitigation while chasing wealth accumulation.</p>
        <p class="prose">While I worked at Amazon risk treatment varied case by case as there were many factors which were uncontrollable like being understaffed, heat, when a fulfillment center associate received training and when a specific pallet had to move. In some cases, process assistants and managers would have to obtain fulfillment center associates from another lane or remove an employee from their position to aide with a variable process during a shift, the most popular processes which needed more employees on hand were the position of water spider and to aide in transportation and the loading of pallets onto freight trucks. Additionally, successfully treating and managing risk on an e-commerce front is far too variable due to the multiple risks and strategies needed to act upon to in order to maintain a good standing on e-bay and effectively with customers while also ensuring that goods are shipped and delivered in a timely fashion along managing cash to cover business and operation expenses. The most interesting part of risk management while running a e-Bay store front is all the little variables that are unknown before you start operating a storefront where risk treatment will vary based on the item sold. For example, when selling various trading cards from games like Pokémon and Magic the Gathering the cost to ship a card would vary based on the price the card sold at in my case if a card sold for less than 4 dollars, I would mail out the card since my expense to mail out the product was 70 cents, while if the card was worth more than 4 dollars, I would get a bubble envelope and mail a card out with tracking in order to know where a product is throughout the shipping process. There were other items which were interesting to ship such as an Xbox one and all its peripherals, a handful of video games, textbooks and other items and trinkets I no longer needed or saw as junk that I could probably sell to get some spending cash. The largest risk factor that occurred and influenced me in minimizing my usage of e-bay and removing all the items I had listed was e-bays expenses which used to be a smaller rate back in 2020 and grew for low-cost items which forced me into losing money or breaking even prior to the expense hike and oddly enough before the relationship with PayPal was severed when that relationship was very convenient for me as a seller. Lastly with risk management of a YouTube channel which initially was tied to my name I was contemplating my career risk when I wanted to start a podcast so I moved all of my book club videos and deleted or moved a variety of other content and videos relating to my portfolio over to the podcast's channel. I believed that was the appropriate risk mitigation strategy due to my variety of interests which I rather have a potential employer not see directly attached to my name. I believe there is nuance when creating opinions on art and literature and a one size fits all approach will never work so I use the channel as a creative outlet of ideas and to gather my thoughts weekly or whenever I am able to record a podcast episode, discuss my most recently read book and see where I can go without being too vulgar or edgy while trying to maintain a high level of authenticity. In these various cases of risk treatment and application of risk management I tend to take a variable or better put adaptive approach with the situation presented to me and allow my intuition, problem solving and management skills allowing me come up with a solutions and moving forward with the approach that is most practical, strategic or objective when it comes to a complex scenario or a situation that must be given more thought than the approach to life I have of doing all that I can, failing when I do and never failing at something again, a break it and fix it approach if you will while never giving up and getting better at anything I set my mind to.</p>
        <p class="prose">From the course I personally enjoyed learning about the variety of risks that exist the most intriguing one to me at the moment is credit risk and part of the reason I am taking Credit Analysis next semester. I will definitely be using a varied approach to a myriad of events that occur in my life as a result of taking the course and integrating it into my own risk tolerance or what I would consider my own personal risk profile which is made up of experiences, successes, failures, ones' finances and a variety of other variables that make up someone's risk appetite, tolerance and how and why someone has a certain approach to life and risk overall. I usually tend to take a hedging strategy now and in the near future and take an all or nothing approach as it seems the most appropriate for my risk tolerance and what I want to achieve career, investment and business goals and ultimately get what I want to feel satisfied with life through actively problem solving and managing risk.</p>
      </div>
      <details class="lab-cites"><summary>Works cited · 1 source</summary><ol><li>Definition of Risk. Merriam-Webster. Accessed 28 Nov. 2022.</li></ol></details>
      <p class="fs-note">Research I run for myself, not advice. I am not a licensed financial advisor. Reproduced word for word as submitted in December 2022, so its figures, forecasts and positions reflect that date rather than a current view. Act on it and the risk is yours, not mine.</p>
    </div><!-- /con-riskfinal -->

    <div class="concept" id="con-starbucks">
      <div class="eyebrow">Concept 03 &middot; float &amp; fintech &middot; Dec 10, 2022</div>
      <h2>Starbucks Banking Paper</h2>
      <div class="lab-meta"><span>Written <b>December 10, 2022</b></span><span>Bank management · corporate analysis</span></div>
      <p class="fs-kicker">Takes the "Starbucks is secretly a bank" claim seriously enough to actually test it against the 10-K, and then refuses it. <b>$1.596bn sitting in gift card balances, lent to the company at 0% by its own customers, throwing off $164.5m of breakage revenue</b> — a float business by any honest reading. The conclusion lands somewhere better than the premise: not a bank, a coffee shop that dabbles in fintech, and unregulated as such.</p>
      <p class="lab-verbatim">Reproduced verbatim · figures from FY2021 filings</p>
      <div class="lab-body">
        <p class="prose">Coffee a staple beverage fueling many Americans mornings, has grown in popularity since 1773 as a result of the Boston Tea Party dumping British Tea into the Boston harbor in retaliation of taxes in the interest of what would become the United States (Avey). The preparation of coffee varies on personal preference ranging anywhere from a simple cup of black coffee to a sugar filled treat which requires diligent preparation and ingredient-based instructions. The need for consistent and quality coffee on the go in America has solidified Starbucks as a staple firm which offers convenient and practical locations and products for their consumers, in sustaining their position Starbucks has become a bank in parity from it's mix of customer and brand loyalty, gift card program and investments that fuel expansion.</p>
        <p class="prose">Every business requires customer loyalty in order to maintain its control over segments of operation, in regards to banking banks must offer a variety of services and financial products to target and acquire new customers while maintaining existing customers (Koch 24-26). Starbucks may call itself "the premier roaster, marketer and retailer of specialty coffee in the world," which operates in 84 markets but it also acts like a bank with their variety of products and services (Starbucks Corporation 5). Starbucks has maintained its customer and brand loyalty through marketing, its popularity and various locations ranging from universities, airports and anywhere in between a customer and their destination ensuring loyalty via the customer experience and the variety premium products offered (Tim Murphy). The experience of any Starbucks has the sense of modernity and convenience that allows anyone to work remotely, enjoy a cup of coffee or meet for romantic or the business needs of its clientele. In order to maintain and grow their clientele Starbucks merged two of its programs to create what the Starbucks Rewards program is today (Starbucks). In the progress of doing so Starbucks customized the customer experience by personalizing orders and offers by gamifying purchases in stores or within and through the app (Formation).</p>
        <p class="prose">The necessity of customer loyalty is paramount for maintaining, growing and sustaining operations and cashflows which Starbucks has done an excellent job on the surface since 2009 with the fusion of its Starbucks Card Rewards and Gold loyalty programs (Starbucks). In 2021 alone there was a total of 1.596 billion in gift cards alone almost a 10% increase since 2020 and may be lower than usual following the business interruption of the Coronavirus outbreak (Starbucks 46). Interestingly, gift cards act as an obligation of a service or goods and balances do not decay but may expire at a given point in the future and presumably are reissued once expired repeating the process of a customer potentially forgetting to use their balance for a 100% profit if a balance is never used (Crockett). Additionally, roughly 25% of operating cashflows are reinvested in property, plant and equipment presumably fueling domestic and international expansion and it can be quickly shown how drastic of an impact coronavirus had on Starbucks' cashflows during 2020 where nearly 93% of operating cashflows were spent in the same category (Starbucks 47). Although Starbucks gift cards are not conventional deposits akin to how a bank would hold its clienteles' cash, one can see the parallels between the two when gift card balances are loaded onto a customer's app balance acting as a source of funds for either institution until used.</p>
        <p class="prose">In operation the similarities between Starbucks and a bank continue with the utilization of capital for investment, growth and to fuel expansion. In essence with gift cards, Starbucks acts reminiscent of a thrift where balances are lent to Starbucks at a 0% interest rate by customers while Starbucks earns breakage revenue on balances totaling to 164.5 million effectively making 10% on every dollar held in gift card balances for the fiscal year of 2021 (Starbucks 53). Since Starbucks predominantly sells coffee instead of financial products and services like a bank calling Starbucks a bank is incorrect and the gift card segment is more comparable to companies like PayPal and Visa with their own prepaid gift card products (Visa 9). While Visa and PayPal's profit drivers are their payment systems, their gift card segments are an added benefit just as it is with Starbucks to their coffee business. The similarities with Starbucks and banks ends when one starts to look at it as a fintech firm that sells coffee, fintech firms are not under as much scrutiny and regulation as banks acting as a modern financial medium with access to a larger variety of investments and services which can the open doors to expedient growth unavailable to banks due to capital use restrictions.</p>
        <p class="prose">In addressing the daily caffeine needs of many Americans Starbucks is in a stellar position. Starbucks creatively manipulated its former programs into their Rewards program every American knows of today. Although there are similarities with Starbucks and banks, Starbucks cannot be called a bank. If anything, it should be considered a coffee shop that dabbles in fintech services to bolster its bottom line.</p>
      </div>
      <details class="lab-cites"><summary>Works cited · 8 sources</summary><ol><li>Avey, Tori. "The Caffeinated History of Coffee." PBS, Public Broadcasting Service, 8 Apr. 2013.</li><li>Crockett, Zachary. "What Happens to Unused Gift Card Money?" The Hustle, 21 Oct. 2020.</li><li>Formation. "How Starbucks Became the Leader in Customer Loyalty." Formation.</li><li>Koch, Timothy W., and S. Scott MacDonald. Bank Management. Cengage Learning, 2015, pp 24-26.</li><li>Starbucks Corporation. 2021 Annual Report. November 12, 2021.</li><li>Starbucks Corporation. "Rewarding Our Customers." Starbucks Archive.</li><li>Murphy, Tim. "Customer Loyalty vs. Brand Loyalty: What's the Difference?" SearchCustomerExperience, TechTarget, 29 July 2022.</li><li>Visa Corporation. 2021 Annual Report. September 30, 2021.</li></ol></details>
      <p class="fs-note">Research I run for myself, not advice. I am not a licensed financial advisor. Reproduced word for word as submitted in December 2022, so its figures, forecasts and positions reflect that date rather than a current view. Act on it and the risk is yours, not mine.</p>
    </div><!-- /con-starbucks -->

    <div class="concept" id="con-analytics">
      <div class="eyebrow">Concept 04 &middot; analytics &amp; underwriting &middot; Apr 27, 2023</div>
      <h2>Data Analytics for Risk Management</h2>
      <div class="lab-meta"><span>Written <b>April 27, 2023</b></span><span>Insurance underwriting &amp; investment management</span></div>
      <p class="fs-kicker">Written in April 2023 — five months after ChatGPT, before the capital cycle that followed, and before most of the industry had priced any of it in. Argues predictive modeling, machine learning and artificial intelligence as the working instruments of both sides of an insurer: the underwriting desk and the investment arm that funds the claims. Closes on Oppenheimer.</p>
      <p class="lab-verbatim">Reproduced verbatim · forecasts as cited in Apr 2023</p>
      <div class="lab-body">
        <p class="prose">In our daily lives people will assess risks that they face and act accordingly by accepting, mitigating or eliminating a given risk based on their life experiences and financial circumstances. However, when it comes to insurance vast amounts of data must be analyzed in order to price a soon-to-be insured party's risks. In achieving proper risk management, underwriters and investment analysts must use data analytics tools such as predictive modeling, artificial intelligence, machine learning and other data analytic processes to analyze, develop and refine data.</p>
        <p class="prose">In order to properly assess risk, underwriters must review data and predictive models in order to properly apply data, cull irrelevant data, acquire new data, integrate and utilize in order to have the most reliable model available for risk management. In doing so underwriters will "focus on key aspects for risk selection", for example following various projections it can be discovered that a potential client may be exposed to the possibility of a nuclear power plant failure in severity similar to the Fukushima due to the plants' location. Upon discovering this information an underwriter would either continue on with the client and provide limited coverage due to the potential severity of the claim or reject the client and defer them to another broker or a pool which specializes in nuclear energy insurance such as NEIL, EMANI, ELINI and the UK national pool known as the Nuclear Risk Insurers Limited. The application of Data Analytics will be variate in nature due to the variable types of risks involved in various business entities across the world in order to obtain enterprise insight into operational intricacies which will exist. To discover risks, the utilization of predictive modeling is used to project and forecast the a risk, machine learning in order to have an algorithm or artificial intelligence learn through application and analysis of a model.</p>
        <p class="prose">For an insurer to maintain profitability alongside underwriting, insurer's must invest capital from earned and excess premiums. The earned and excess premiums are invested as a means to have enough capital in reserves to payout claims once an accident has occurred to a client and to fulfill their promise to pay. While insurers are restricted in how and what they can invest in insurers will have their own investment managers, hedge funds, private equity or even asset management arms similar to some banks like as Morgan Stanley's hedge fund Front Point Partners in the financial drama the Big Short. In order to maximize returns and attain investment income to guarantee that claims will be paid, investment managers must use Data Analytics processes just like underwriters but will focus on data for investment analysis and risk management while staying compliant to internal risk management requirements and compliant to federal requirements mandated by each state. The NAIC has a recommended "Investment of Insurers Model Act" (MDL-280) which outlines recommended regulations along approved and prohibited investments. Each state will have their own nuanced laws for example, the state of Texas' insurance code requires "all investments made by the insurer under this section (434.052) does not exceed five percent of the insurer's assets" making it a challenge to make investment profits in the lone star state creating the necessity for predictive modeling for investment analysis, machine learning or artificial intelligence in order to visualize statistics and returns and train the application and analysis of models for investment managers.</p>
        <p class="prose">To underwrite risk, accurate predictive models and analysis software is required to build risk assessment models, a few public data analytics and management firms that enable insurers and reinsurers to assess their own data such as Palantir with its' partnership with Swiss Re. These types of partnerships seek to improve efficiency, reduce risk and optimize workflow in order to have a lasting impact on the insurance industry through leveraging data. Both firms have their own software and data platforms for various business sectors to address risks while having their own nuances. What makes the Swiss Re- Palantir partnership interesting is that Swiss Re created an analytic data model: Stargate to pool data, predict and assess likeness of events such as climate change and implement strategies to mitigate unexpected events in the ever-changing world. In a changing world especially where black swan events occur more frequently as a result of geopolitical tensions, global outbreaks, economic shocks and unprecedented global risks, data has become gold and the integration of new and accurate data is a necessity in adapting with changes and helps mitigate or modify new and unseen risks. Like the paintbrush, canvas and paint is to an artist; the predictive model and data are to the underwriter (actuary and data scientist) in order to model, assess and determine whether to write a policy or potential covenants and specific performance to receive coverage.</p>
        <p class="prose">As an investment manager one's own analysis will drive investment decisions along with a firm's risk-taking allowances and restrictions placed on their investment teams. In order to view trends for investment capital allocation to hedge the risk of loss and as an additional revenue stream, predictive models will improve investment performance where an investment manager or his team missed during their own analyses or team conversations. A good investment manager and portfolio risk manager will stress test the firms variety of scenarios to optimize a portfolio and investment allocations to maximize return and minimize risk, additionally to adhere to internal risk management concerns and in order to be compliant with regulatory requirements. One financial data analysis project that was required to be done for an Investment Management course gave five years of monthly returns data to the students to come up with their own analysis to create their optimal portfolios and allocations within nine different assets (specifically securities and bonds). In essence, the project served as a means to show how a predictive model will assign distributions to maximize the Sharpe ratio (maximize return and minimize variance). Optimally a keen student that took the course would apply the same analysis to stress test their own portfolios in order to maximize risk management and reduce personal bias which contaminate portfolio returns, returning to an investment manager if there is market bias with a specific security which has corrected off of fear rather than financial results, industry data and the upper management of a target investment. An investment manager and his team should capitalize off of the discount the market is giving the team or reevaluate with the current market valuation which has been "priced in" like that which occurred during March following the collapse of Silicon Valley Bank and reallocation out of middle market and regional bank stocks like Zions Bancorporation (to cherry-pick) which fell to a market value of 60% of what it was prior to SVB's failure and is still trading around that value a month later. In order to integrate such volatility a conservative approach must be taken in to reasonably assess risk when financial modeling and realizing risks involved within an opportunity, risk must be known and continuously assessed in order to prevent failures, collapses or terrible investment decisions that could lead to a portfolio to cannibalize itself and disable excessive risk taking and mitigate any negative snowball effects on the investment managers' team and the insurer.</p>
        <p class="prose">In order to maintain competitive edge and aid in management decisions, underwriters utilize machine learning to automate data collection, cost identification for claims processing and artificial intelligence to improve underwriting processes through automation, workforce training- augmentation. In essence machine learning is the process a machine, system or algorithm learns through integration and immersion of data to examine and assess it to the needs of its' owner or operator. By utilizing machine learning, certain processes can be automated away which allows underwriters, actuaries and data analysts to be focused on inputs and tooling data models for more effective and time efficient results creating an interdependence of data for operations and with a firm's workforce. As a result of implementing machine learning processes to data models and internal programs will lead to network effects creating a machine augmented workforce which will be more efficient at their jobs while optimally reducing their amount of 'grunt' work in cost identification along with other claims processes. While machine learning is important, it is a component of artificial intelligence which is frontier technology that is industry agnostic for implementation. The industry is being heavily invested in by various firms with technology firms taking the lead such as Microsoft and IBM, the global AI market to grow to $407 billion in 2027 from 2022's $86.9 billion. The nature of artificial intelligence is quite agnostic to where it has enterprise-wide application and can be molded into a sophisticated tool as long as it is programmed, trained or coded to the hearts' content of an operator. In the case of underwriters, data scientists or analysts and actuaries artificial intelligence can analyze processes to train its' operator and itself through data analytics, processing data and being trained to become more efficient and effective at their jobs. Artificial intelligence in this case could be utilized to discover flaws in a network, manage a firms' operation and help visual effects of operations data to discover ESG efficiencies and inefficiencies while not destroying a firms' value. As a result, one would expect an artificial intelligence to have a firm's ethics values integrated into its' programming and hopefully constraints which prevent the artificial intelligence from 'going rouge' like in several science fiction stories. While pondering on artificial intelligence is scary at times the current state of artificial intelligence is nowhere near Terminator and hopefully the firms developing artificial intelligence place constraints to limit how far the technology it will develop while being able to understand how to measure and oversee the technology's self-improvement and development. The drawbacks to not implementing machine learning and artificial intelligence will impact customer attrition and retention, effective ratemaking and operations reactivity which would have all improved with the tech's implementation.</p>
        <p class="prose">Naturally since machine learning and artificial intelligence will be used to aide and automate underwriting functions currently and will expand in the future, the same can be said for determining investments as an investment manager. Just like underwriting, machine learning can automate investment actions and components of investment analysis which investment managers will want to automate to refine their investment teams' focus on pitching investments and provide value to the overall portfolio. In a way, investment managers could reduce the size of their teams while also maximizing the skills of the overall whole. By utilizing machine learning an investment manager could oversee inefficient stock trades, options, futures, swaps and other investment tools in order to supplement and bolster an insurer's profitability. By being able to visualize and eliminate inefficient investments, investment managers will be able to maximize the portfolio's return by risk reduction and eliminate risks that may have existed within a portfolio. While the investments stated may make up an investment manager's portfolio, investments are restricted dependent on the state of operation as each state has its' own legislation and restrictions on investing operations as an insurer. While the effects of machine learning are more tangible the overall implications of artificial intelligence are broad as the industry and technology are in their infancy. While certain applications of artificial intelligence are speculative an artificial intelligence can act as a financial advisor, automated "Robo" investor like Q.AI (which Forbes holds a stake in), conduct thorough research and a variety of other applications for investment managers and their teams. Naturally artificial intelligence will be able to analyze all available information faster than an analyst but it may overlook certain investments and opportunities where panic and chaos become "priced in" a soundly operating firm which potentially will lead to a lower return than a human would have while both would operate within their own allowances to control risk and portfolio allocation. While artificial intelligence may miss some no brainers during volatile markets it is still a necessary instrument in an investment managers' toolbox.</p>
        <p class="prose">Pandora's box has been opened and there is no going back with business necessity and implications of integrating artificial intelligence into a firms' operations. The application of predictive modeling, machine learning and data analytic applications are a necessity to insurers and their investment managers. While the artificial intelligence industry is only in its' infancy, it will remain in the publics' spectacle as a tool for rapid technological development and economic progress. We can only wait to see if the concerns with artificial intelligence are warranted due to potential mass labor displacement where some individuals fear we could go too far while their opposers see artificial intelligence as the next technological step. Either way reality will lie between the pessimists and optimists views and speculations of artificial intelligence as it is a digital nuclear bomb. It only feels appropriate to close with Oppenheimer "we knew the world would not be the same" and if artificial intelligence develops unconstrained, we will become our own destroyers.</p>
      </div>
      <details class="lab-cites"><summary>Works cited · 13 sources</summary><ol><li>Alpaydin, Ethem. Introduction to Machine Learning. 2nd ed., MIT Press, 2010.</li><li>Aslanyan, Tatev. "Fundamentals of Statistics for Data Scientists and Data Analysts." Towards Data Science, Medium, 25 June 2019.</li><li>ESMA. ESMA50-164-2458: EU-wide stress test 2021, 2 Sept. 2021.</li><li>EY - US. "Underwriting Transformation." EY, 2021.</li><li>"Insurance Companies Investing the Float to Create a Stream of Revenue." Gaap Dynamics, 8 Feb. 2022.</li><li>"Liability for Nuclear Damage." World Nuclear Association, 2021.</li><li>MarketsandMarkets. "Artificial Intelligence Market by Offering (Hardware, Software, Services), Technology (Machine Learning, Natural Language Processing), Deployment Mode (Cloud, On-Premises), Organization Size, Vertical, and Region - Global Forecast to 2025." MarketsandMarkets, 1 Apr. 2020.</li><li>Moody's Analytics. "ESG and Insurance Underwriting - Moody's Analytics." Moody's Analytics, n.d.</li><li>NAIC. "Model Law Regarding Credit for Reinsurance." NAIC, National Association of Insurance Commissioners, March 2011.</li><li>Palantir. "Swiss Re - Palantir." Palantir, Palantir Technologies, 2021.</li><li>"Texas Constitution and Statutes." Texas Constitution and Statutes, Texas Legislative Council, 2021.</li><li>Toronto School of Management. "Key Components of Data Analytics." Toronto School of Management Blog, 29 Mar. 2021.</li><li>World Nuclear Association. "Fukushima Daiichi Accident." World Nuclear Association, 12 Mar. 2021.</li></ol></details>
      <p class="fs-note">Research I run for myself, not advice. I am not a licensed financial advisor. Reproduced word for word as submitted in April 2023, so its figures, forecasts and positions reflect that date rather than a current view. Act on it and the risk is yours, not mine.</p>
    </div><!-- /con-analytics -->

    <div class="concept" id="con-insops">
      <div class="eyebrow">Concept 05 &middot; operating plan &middot; May 5, 2023</div>
      <h2>Insurance Operations Final</h2>
      <div class="lab-meta"><span>Written <b>May 5, 2023</b></span><span>Feasibility study · founder's brief</span><span class="lab-badge">Origin document</span></div>
      <p class="fs-kicker">The one that started it. The assignment was open-ended — design an insurance firm, go from there — and what came back was <b>three functions under one roof: underwriting, risk consulting, and a captive investment group</b>, with the investment arm free to become an asset and wealth management business if state law constrained it. That is the structure the firm ended up being built on. Written and signed as the founder two years before there was one, and the only paper in four years to come back with a 100 on it.</p>
      <p class="lab-verbatim">Reproduced verbatim · written May 2023</p>
      <div class="lab-body">
        <p class="prose">Being hired by a group of Bauer graduates who are private equity investors I have been assigned to study the feasibility of starting up a new insurance company offering personal lines' insurance products to current Cougar students and alumni, along with commercial insurance policies for small businesses run by UH alumni.</p>
        <p class="prose">Naturally when starting a business there are external and internal constraints and barriers of entry to achieve our goal of being a soundly operating insurer. Every business owner will face challenges and will need to find a way to conquer them or at minimum survive by being profitable. External constraints that any insurer will face are regulation, rating agencies such as Moody's and S&amp;P, public opinion, competition and economic conditions which all influence operations, financial performance and market share. Additionally, there the internal constraints of inefficiency, lack of experience, firm size, financial resources and other internal constraints such as a damaged brand reputation. In our case we need to be aware of both and the barriers to entry especially as a up and coming insurer including how we financially structure our firm so that we earn a profit, along with meeting customer needs, legal compliance, diversifying risk and fulfilling our duty to society.</p>
        <p class="prose">In being profitable there are a variety of ownership structures for an insurer to be formatted in, such as a proprietary or cooperative insurer along with pools and government insurers. Since we will be started from the ground up, I believe we should be a proprietary insurer in order to generate a return to the private equity investors along with receiving capital initially. By being owned by the private equity investors in part, we can utilize their existing networks to source talent and capital initially and potentially go to the public markets during capital crunches and raise capital when necessary. An additional benefit of being a stock insurer is that their investment value may appreciate with the stock value on top of any dividends (if a dividend is issued). Lastly the most beneficial part of being a proprietary insurer is that we could participate in an insurance exchange like the American Lloyds' to underwrite any insurance or reinsurance bought at the exchange. As a member there is the perk of limited liability, belonging to a syndicate along with the delegation of operations to a syndicate manager. For our licensing status we intend to be a licensed (admitted) insurer to operate in Texas, starting in Houston and expanding as we are able to.</p>
        <p class="prose">In order to stay in operation, maintain a market share and expand we will initially use independent agencies and brokers then shift over time into a combination of direct writing and exclusive agencies. This structure would be to expand initially then "lock in" insureds through perks, discounts and benefits to our existing clientele. In order to expand naturally and get into the eyes of potential insureds we need to advertise. In doing so we would run commercials, run ads in the Houston chronical, social media and the sort for personal lines and advertise through word of mouth, direct to consumer for small business owners, syndication through Lloyds along with group marketing and financial institutions for our commercial lines as we are targeting two different types of customers.</p>
        <p class="prose">To reach our goals we will financial and performance goals which we will measure through revenue from premiums and investment income. We will strive to beat or meet market returns annually on investments with what we are restricted in investing and holding while striving to have earned premiums, underwriting performance and operations efficiency grow by a rate of 2% for earned premiums and a rate of 5% or greater annually for the other components, this is to stay efficient and lean while expanding as needed. Metrics we would use to track performance would be return on investments/assets/equity, our enterprise growth rate, loss ratio, expense ratio, combined ratio, net income and internally review quarterly and annual financial audits to oversee any changes or outlier activities that may incur during operations. In our operations we would like to have a loss ratio below 80% and optimally as close to 50% once we are established to maximize shareholder and societal returns while being profitable and setting aside a portion of our profits for our reserves to pay claims and dividends.</p>
        <p class="prose">To differentiate ourselves we will have a risk consulting function along with a captive investment group or private equity function to capture additional profits via investment income and capital appreciation. It is important to have additional functions if the firm would like to start as an insurer, then grow and mature into a vertically integrated financial services group to capture our market of Houston while also not constraining ourselves to one type of business. Having three functions will not only benefit our shareholders but also our insureds build trust and reserves that no matter what happens to an insured we can guarantee coverage via our cash reserves, capital set aside for claims and allowing our quarterly and annual financials publicly accessible. Pricing will vary based on a firm's or individual's scenario and priced appropriately based on the all risks being underwritten, consulting will vary as well but initially be priced at either a flat fee of dependent on the size of a firm or 2% of the gross benefit a firm sees after implementing any or all recommendations, and the investment function will also vary but easily grow into an asset and wealth management arm if investment returns and opportunities are too constricted by Texas law and must pivoted.</p>
        <p class="prose">As an insurance firm based in Texas, we would be regulated by the Texas department of Insurance, to keep in mind the NAIC and other regulatory bodies for our supporting functions. Regulation is a necessary part of operating and important to keep us in check with regulatory requirements and for our insureds, if we fail everyone that relied on us loses. To get approval for policies we will work with our regulators along with our initial Cougar alum investors to start then operate on our own unless a regulatory conflict occurs. In the future the approval for rates and policy structures will depend on the state where we expand and the holistic view of the risk environment that comes with operating in the state, we would like to extend our services to. If we were to go insolvent, we would honor our claims and work with regulators to cover outstanding policies and get portions of our book acquired by a 'rival' firm to survive or even acquired above or near book value as our debt or claims expenses probably cannibalized our firm.</p>
        <p class="prose">To ensure compliance we will have our own guidelines which will be outlined in our own code of ethics and underwriting handbooks. These guidelines must be followed and adhered to in addition to state requirements. Naturally to oversee performance and financial results we would conduct premiums audits along with financial stress testing for liquidity purposes. In order to see whether we are appropriately pricing premiums we will conduct premium audits, the purpose for premium audits will seek to bolster our position in a competitive market along with showing that we audit ourselves and are transparent with the pricing of our premiums. On top of those metrics, we will measure our claims department's performance via claims diaries and logs, access security and authority levels and claims tracking systems. We will also have supervisor and manager reviews and audits to improve their performance. Lastly, we will perform claims audits (internal and external) to review and verify if claims were appropriately handled.</p>
        <p class="prose">For ratemaking we will generate rates through the pure premium, loss ratio and judgement methods. The combination of the three is appropriate as in order to offer our services we have to look at some of, as many or all the risks we can determine to acquire business in our appetite while keeping sustainable expansion in our view. We will not reinsure initially as it opens us up to more risks, but depending on circumstance we would consider syndicating and pooling risk but only as a participant and not spearheading the transaction. In the future if we are adequately liquid and capitalized, we would reinsure a niche market and specialize in energy as a Houstonian firm.</p>
        <p class="prose">To provide an overview of us a proposed insurer we would like to provide a Swot analysis on ourselves. A strength of our business is our enterprise vision, focus on our core insurance functions and commitment to insureds that their policies will be honored if we fail. One of the weaknesses we have is auditing and the regulatory environment and inflation eating away at profits. We believe that while necessary our own audits may hinder operations when they are occurring which may affect financial performance. An opportunity we have is horizontal integration which we could pursue as an insurer and grow into a financial services group to bolster our bottom line financially, grow and improve what services we can provide while reinvesting in ourselves. Naturally we are threatened by competition and want to stay competitive and become a stalwart and not disappear and solely compete away either of our profits. We seek to differentiate ourselves as a Houstonian customer obsessed insurer that becomes horizontally integrated to offer services like asset management, wealth management, potentially banking, risk consulting and a variety of necessary functions to solidify and diversify our services and revenue streams.</p>
        <p class="prose">As the founder of our firm, I wish we appropriately conveyed our vision and are seeking seed money and hopefully partners to help us achieve our enterprise goals, we believe it can be achieved in time through our focus on customers and expand into a goliath.</p>
      </div>
      <details class="lab-cites"><summary>Works cited · 1 source</summary><ol><li>Connecting the Business of Insurance Operations, 1st edition (CPCU 520) The Institutes Collegiate Edition.</li></ol></details>
      <p class="fs-note">Research I run for myself, not advice. I am not a licensed financial advisor. Reproduced word for word as submitted in May 2023, so its figures, forecasts and positions reflect that date rather than a current view. Act on it and the risk is yours, not mine.</p>
    </div><!-- /con-insops -->

    <div class="concept" id="con-market">
      <div class="eyebrow">Concept 06 &middot; market brief &middot; Aug 31, 2023</div>
      <h2>Market Overview</h2>
      <div class="lab-meta"><span>Written <b>August 31, 2023</b></span><span>Interview brief · RIA final round</span></div>
      <p class="fs-kicker">Written the night before a final-round interview with the C-suite of a registered investment advisor — nobody asked for it. Put together in one sitting so there would be something on the table besides answers. Kept here as a reference for what a market read looked like at the end of August 2023.</p>
      <p class="lab-verbatim">Reproduced verbatim · figures as of Aug 31, 2023</p>
      <div class="con">
        <div class="box"><h4>State of the Economy and Financial Markets</h4><ul><li>Higher than normal inflationary environment compared to the 10-year average of roughly 2% (actual 1.88%).</li><li>Federal Reserve is hiking rates in order to tame inflation currently the Federal Funds Effective rate is 5.25-5.5%, last month per Fed St. Louis was 5.12%.</li><li>Rate hikes will probably continue to until inflation is contained, as a result liquidity has been withdrawn from the market.</li></ul></div>
        <div class="box"><h4>How did we get here</h4><ul><li>Financial crisis of 2008.</li><li>Low to nearly nonexistent interest rates for nearly 15 years (sub 2% from 2008-2022, excluding 2019).</li><li>Covid globally constricted economic activities.</li><li>Quantitative easing during 2020, while warranted currently looks like only worked as a short-term fix to stimulate the US economy.</li></ul></div>
        <div class="box"><h4>Market trends and issues in 2023</h4><ul><li>Artificial Intelligence (A.I.) and its initial implementation in the market.</li><li>2023 Banking crisis (SVB, First Republic Bank, Signature Bank)</li><li>Rising geopolitical tensions with China and Russia.</li><li>Reshoring of manufacturing domestically (US).</li></ul></div>
        <div class="box"><h4>Personal concerns in the current market</h4><ul><li>Market outlooks and sentiment appear to take a short-term view only interested in the current and following quarter.</li><li>Rising consumer debt, "Credit card debt hits 1 trillion"</li><li>Rising National debt</li></ul></div>
        <div class="box" style="grid-column:1/-1"><h4>Questions I have for the team</h4><ul><li>What brought you to the firm?</li><li>Has there ever been an investment which looked great across an analysis but went completely sideways following building a position?</li><li>How do you determine and minimize overall exposure to an individual equity if you invest in multiple funds with some level of overlap in their holdings?</li><li>How should an analyst look at markets?</li></ul></div>
      </div>
      <p class="fs-note">Research I run for myself, not advice. I am not a licensed financial advisor. Reproduced word for word as submitted in August 2023, so its figures, forecasts and positions reflect that date rather than a current view. Act on it and the risk is yours, not mine.</p>
    </div><!-- /con-market -->

    <div class="concept" id="con-roulette">
      <div class="eyebrow">Concept 07 &middot; random-draw benchmark &middot; Jul 6, 2024</div>
      <h2>S&amp;P Roulette</h2>
      <p class="fs-kicker">A monkey with a dartboard, formalised.</p>
      <p class="prose">Spin the wheel and draw a name out of the S&amp;P 1500. The wheel is carved by sector at the index's own weights, so every company in the drum has exactly the same chance of coming up. No skill, no thesis, no edge: just the null hypothesis with a nicer interface. It is the bar every other concept in the Lab has to clear.</p>
      <p class="fs-note">Research I run for myself, not advice. I am not a licensed financial advisor. A random draw is a benchmark, not a strategy, and a wheel has no view on any company it lands on; the constituent list is a static snapshot, so a name here may since have left the index, merged away or been renamed. Act on it and the risk is yours, not mine.</p>

      <div class="rl-felt">
        <div class="rl-wheelbox">
          <canvas id="rlWheel" role="img" aria-label="Roulette wheel divided into eleven sector segments, each sized to that sector's share of the S&amp;P 1500."></canvas>
          <div class="rl-verdict idle" id="rlVerdict" role="status" aria-live="polite">
            <div class="rl-vt">No spin yet</div>
            <div class="rl-vn">Press spin. The wheel picks, you live with it.</div>
          </div>
        </div>
        <div class="rl-rail">
          <div class="rl-actions">
            <button type="button" class="rl-btn solid" id="rlSpin">Spin</button>
            <button type="button" class="rl-btn" id="rlDeal">Deal <span id="rlDealN">10</span></button>
            <button type="button" class="rl-btn quiet" id="rlClear">Clear table</button>
          </div>
          <div class="rl-block">
            <div class="rl-label">Index <span>which drums are in play</span></div>
            <div class="tlviews rl-seg" id="rlCaps" role="group" aria-label="Index tiers in play">
              <button type="button" class="tlv active" data-cap="0" aria-pressed="true">S&amp;P 500</button><button type="button" class="tlv active" data-cap="1" aria-pressed="true">Midcap 400</button><button type="button" class="tlv active" data-cap="2" aria-pressed="true">Smallcap 600</button>
            </div>
          </div>
          <div class="rl-block">
            <div class="rl-label">Sectors <span>click to take one off the board</span></div>
            <div class="rl-odds" id="rlOdds" role="group" aria-label="Sectors in play, with draw probability"></div>
          </div>
          <div class="rl-block">
            <div class="rl-label">Book size <span>equal weight, split across the draw</span></div>
            <div class="rl-stake">
              <label class="rl-fl" for="rlSize">Positions</label>
              <input type="number" class="rl-num" id="rlSize" value="10" min="1" max="30" step="1">
            </div>
          </div>
        </div>
      </div>

      <h3>The draw</h3>
      <p class="fs-cover" id="rlMeta"></p>
      <div class="tablewrap"><table><thead><tr>
        <th></th><th>Ticker</th><th>Company</th><th>Sector</th><th>Tier</th><th class="r">Weight</th><th class="r"></th>
      </tr></thead><tbody id="rlBook"></tbody></table>
      <div class="rl-empty" id="rlEmpty">Table's clean. Spin once for a single name, or deal a full book.</div></div>
      <div class="rl-actions after"><button type="button" class="rl-btn quiet" id="rlCopy">Copy tickers</button></div>

      <div class="rl-mix">
        <div>
          <div class="rl-label">Sector mix <span>drawn vs. index</span></div>
          <div class="rl-bars" id="rlBars"></div>
          <div class="rl-legend"><i class="rl-tick"></i> index weight in the live universe</div>
        </div>
        <div>
          <div class="rl-label">What the wheel just told you</div>
          <p class="prose" id="rlRead" style="margin-top:10px"></p>
        </div>
      </div>
      <p class="fs-cover">Constituents: a static snapshot of the S&amp;P 500, Midcap 400 and Smallcap 600 with GICS sector and tier. No prices, no fundamentals, no returns, and nothing fetched live.</p>
    </div><!-- /con-roulette -->

    <div class="concept" id="con-scm">
      <div class="eyebrow">Concept 08 &middot; memo &middot; capital management framework &middot; Aug 25, 2024</div>
      <h2>Systematized Capital Management</h2>
      <p class="fs-kicker">And liquidity automation. How do we manage money? Income comes in, expenses go out, and what is left is invested. Systematized capital management puts that on rails: a fixed set of accounts with money moving between them on its own, so the decisions that need a person shrink to almost nothing.</p>
      <h3>Personal capital management</h3>
      <p class="prose">Managed by hand, money follows three things: the mental models you bring to it, your cost of living, and the situation you are in.</p>
      <h3>Systematic capital management</h3>
      <p class="prose">Automation simplifies input needs. Set the flows once and the system handles the routine moves.</p>
      <h3>The system</h3>
      <svg class="scm-flow" viewBox="0 0 640 320" role="img" aria-label="Systematized capital management: the Spending Account feeds Investments in a Roth and a Float or Buffer; the Float feeds Savings; Savings feeds Investments and flows back to the Spending Account."><defs><marker id="scmHead" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker></defs><polygon points="20,20 210,20 210,77 115,98 20,77" style="fill:var(--panel-2);stroke:var(--line);stroke-width:2"/><text x="115" y="58" text-anchor="middle" style="fill:var(--bone);font:600 13px var(--mono);letter-spacing:.06em">SPENDING ACCOUNT</text><polygon points="430,20 620,20 620,77 525,98 430,77" style="fill:var(--panel-2);stroke:var(--line);stroke-width:2"/><text x="525" y="58" text-anchor="middle" style="fill:var(--bone);font:600 13px var(--mono);letter-spacing:.06em">INVESTMENTS | ROTH</text><polygon points="20,220 210,220 210,277 115,298 20,277" style="fill:var(--panel-2);stroke:var(--line);stroke-width:2"/><text x="115" y="258" text-anchor="middle" style="fill:var(--bone);font:600 13px var(--mono);letter-spacing:.06em">FLOAT / BUFFER</text><polygon points="430,220 620,220 620,277 525,298 430,277" style="fill:var(--panel-2);stroke:var(--line);stroke-width:2"/><text x="525" y="258" text-anchor="middle" style="fill:var(--bone);font:600 13px var(--mono);letter-spacing:.06em">SAVINGS</text><line x1="222" y1="52" x2="420" y2="52" style="stroke:var(--accent);stroke-width:3" marker-end="url(#scmHead)"/><line x1="115" y1="104" x2="115" y2="210" style="stroke:var(--accent);stroke-width:3" marker-end="url(#scmHead)"/><line x1="222" y1="252" x2="420" y2="252" style="stroke:var(--accent);stroke-width:3" marker-end="url(#scmHead)"/><line x1="525" y1="214" x2="525" y2="108" style="stroke:var(--accent);stroke-width:3" marker-end="url(#scmHead)"/><line x1="430" y1="232" x2="222" y2="96" style="stroke:var(--accent);stroke-width:3" marker-end="url(#scmHead)"/></svg>
      <ul class="proselist">
        <li><b>Spending Account</b> &rarr; Investments, held in a Roth.</li>
        <li><b>Spending Account</b> &rarr; Float / Buffer.</li>
        <li><b>Float / Buffer</b> &rarr; Savings.</li>
        <li><b>Savings</b> &rarr; Investments.</li>
        <li><b>Savings</b> &rarr; back to the Spending Account.</li>
      </ul>
      <p class="fs-note">Research I run for myself, not advice. I am not a licensed financial advisor. This is a personal framework sketched in August 2024, not a plan fitted to anyone else&rsquo;s income, taxes or accounts. Act on it and the risk is yours, not mine.</p>
    </div><!-- /con-scm -->

    <div class="concept" id="con-forecast">
      <div class="eyebrow">Concept 09 &middot; memo &middot; USD/JPY case study</div>
      <h2>A Case for Forecast Events</h2>
      <p class="fs-kicker">Replicate futures trading with forecast events. A forecast event is a Yes-or-No contract on a single number &mdash; will USD/JPY settle above 159.25 on Friday &mdash; and the Yes price is the market&rsquo;s probability, quoted in cents. A ladder of those strikes carries the same view as a futures position, with the most you can lose fixed at entry.</p>
      <h3>The data</h3>
      <p class="prose">Eighty-two daily sessions of USD/JPY to April 24, 2026: the intraday high-low, the open-close, and a regression of the close on the day&rsquo;s open, high and low.</p>
      <div class="fc-eq">Close = 0.0064 &minus; 0.7070 &times; Open + 0.6903 &times; High + 1.0182 &times; Low</div>
      <div class="stats"><div class="stat"><div class="k">Fit &middot; R&sup2;</div><div class="v">0.982</div><div class="m">82 sessions</div></div><div class="stat"><div class="k">Adjusted R&sup2;</div><div class="v">0.981</div><div class="m">Three inputs</div></div><div class="stat"><div class="k">Std error &middot; yen</div><div class="v">0.29</div><div class="m">Across the whole window</div></div></div>
      <h3>Reading the ladder</h3>
      <p class="prose">Visualizing gut feeling with data: the ForecastX ladders for April 23 and 24, set against where the pair actually closed.</p>
      <div class="tablewrap"><table><thead><tr><th>Session</th><th>Contract</th><th class="r">Yes, cents</th><th class="r">Close</th><th class="r">Settled</th></tr></thead><tbody>
        <tr><td class="tk">Apr 23, 2026</td><td>Above 159.00</td><td class="r">60</td><td class="r">159.73</td><td class="r"><span class="fc-won">Yes</span></td></tr>
        <tr><td class="tk">Apr 24, 2026</td><td>Above 159.25</td><td class="r">85</td><td class="r">159.37</td><td class="r"><span class="fc-won">Yes</span></td></tr>
      </tbody></table></div>
      <h3>Live application</h3>
      <ul class="proselist">
        <li><b>Proxy product.</b> The ladder stands in for a futures contract, with the downside written on the ticket.</li>
        <li><b>Gut feel against price action.</b> The regression gives a lean on a strike something to be checked against besides instinct.</li>
        <li><b>Applied statistics.</b> A trade only exists where the ladder and the model disagree.</li>
      </ul>
      <p class="fs-note">Research I run for myself, not advice. I am not a licensed financial advisor. The regression uses each session&rsquo;s own high and low, so it describes a finished day rather than forecasting the next one. Act on it and the risk is yours, not mine.</p>
    </div><!-- /con-forecast -->

    <div class="concept" id="con-xbox">
      <div class="eyebrow">Concept 10 &middot; memo &middot; game theory design project &middot; July 2026</div>
      <h2>Xbox Takeover</h2>
      <p class="fs-kicker">A refined vision for the brand: publisher first, studios merged by DNA, and an action plan for the IP vault. Xbox should be a game publisher and curator that happens to sell consoles.</p>
      <div class="stats"><div class="stat"><div class="k">Spent on ZeniMax + ABK</div><div class="v">$76.2B</div><div class="m">Two acquisitions, 2021 and 2023</div></div><div class="stat"><div class="k">Core first-party studios</div><div class="v">9</div><div class="m">Xbox Game Studios</div></div><div class="stat"><div class="k">Franchises owned</div><div class="v">93</div><div class="m">Every IP in the vault, A to Z</div></div><div class="stat"><div class="k">Roles cut</div><div class="v">3,200</div><div class="m">The July 2026 reset</div></div></div>
      <h3>Why this pitch</h3>
      <p class="prose">I grew up playing a variety of games, and I look at a business as an investor and independent trader &mdash; with an owner-operator&rsquo;s rationale. I got my first Xbox at ten. The thesis: a mismanaged brand that should be the home of gaming, built on Game Pass and a PC-native experience.</p>
      <h3>The trigger: the July 2026 reset</h3>
      <ul class="proselist">
        <li><b>Cuts.</b> 3,200 roles eliminated at Xbox, roughly 4,800 company-wide.</li>
        <li><b>Divestments.</b> Double Fine and Compulsion go independent with their IP. Ninja Theory and Undead Labs are sold, so Hellblade and State of Decay leave the vault.</li>
        <li><b>Cancellations.</b> The Halo live-service Project Ekur is cancelled; Everwild and Perfect Dark were already dead. ZeniMax is narrowed to Fallout and The Elder Scrolls.</li>
        <li><b>Platform elevation.</b> Minecraft and Candy Crush are treated as profit platforms, not games.</li>
      </ul>
      <h3>The strategy</h3>
      <ul class="proselist">
        <li><b>Make quality games people want to play.</b> The org already agrees: Minecraft and Candy Crush run alongside the console business. Content is core.</li>
        <li><b>Put exclusivity back in gear.</b> Divest studios but retain equity. Hardware is a venue; recapture brand identity and keep the IP on Xbox.</li>
        <li><b>Curation is king.</b> Xbox should be a quality brand that keeps customers inside its own ecosystem.</li>
      </ul>
      <h3>The $76B audit</h3>
      <div class="tablewrap"><table><thead><tr><th>Year</th><th>Event</th><th>What it meant</th></tr></thead><tbody>
        <tr><td class="tk">2021</td><td>ZeniMax / Bethesda, $7.5B</td><td>The Elder Scrolls, Fallout, Doom and Dishonored enter the vault</td></tr>
        <tr><td class="tk">2023</td><td>Activision Blizzard King, $68.7B</td><td>Call of Duty, Warcraft, Diablo, Candy Crush</td></tr>
        <tr><td class="tk">2024&ndash;25</td><td>The bill arrives</td><td>Tango, Arkane Austin, Alpha Dog and The Initiative closed; Perfect Dark and Everwild killed</td></tr>
        <tr><td class="tk">2026</td><td>The reset</td><td>Four studios out, 3,200 roles cut, Arkane Lyon in limbo</td></tr>
      </tbody></table></div>
      <p class="prose" style="margin-top:14px"><b>The verdict.</b> A schizophrenic, underused war chest of assets: talent and IP sit idle while studios are shut down. Trim the fat and take risk. Every IP should be in use, or on the market.</p>
      <h3>Merge by DNA</h3>
      <p class="prose">Good, profitable experiences built by merging the best talent into genre houses &mdash; one studio group per genre, with several teams running projects inside each. Imagine a Halo by id Software.</p>
      <div class="tablewrap"><table><thead><tr><th>House</th><th>Studios</th><th>Flagship IP</th></tr></thead><tbody>
        <tr><td class="tk">Shooter</td><td>Halo Studios, The Coalition, id, the Call of Duty studios</td><td>Halo, Call of Duty, Doom, Gears of War, Wolfenstein</td></tr>
        <tr><td class="tk">RPG</td><td>Bethesda Game Studios, Obsidian, inXile, Arkane</td><td>The Elder Scrolls, Fallout, Starfield, Fable, The Outer Worlds</td></tr>
        <tr><td class="tk">Racing</td><td>Playground, Turn 10</td><td>Forza, Project Gotham Racing</td></tr>
        <tr><td class="tk">Worlds &amp; Live</td><td>Mojang, Rare, Blizzard, King</td><td>Minecraft, Warcraft, Overwatch, Sea of Thieves, Candy Crush</td></tr>
        <tr><td class="tk">Strategy</td><td>World&rsquo;s Edge and the classic RTS teams</td><td>Age of Empires, StarCraft, Warcraft RTS</td></tr>
        <tr><td class="tk">Arcade &amp; Family</td><td>Revival specialists</td><td>Crash Bandicoot, Spyro, Banjo-Kazooie, Tony Hawk&rsquo;s Pro Skater</td></tr>
        <tr><td class="tk">New IP Lab</td><td>Elsewhere Entertainment and the archive</td><td>One sitting IP reinvented every year</td></tr>
      </tbody></table></div>
      <h3>The vault: use, sell or license</h3>
      <div class="tablewrap"><table><thead><tr><th>Path</th><th>Rule</th><th>Examples</th></tr></thead><tbody>
        <tr><td class="tk">Use</td><td>Quarterly cadence: rotate vault IP into production so something ships from the vault every quarter</td><td>Perfect Dark revival, Banjo-Kazooie, StarCraft to the Strategy House, Crackdown as a Game Pass live title</td></tr>
        <tr><td class="tk">Sell</td><td>No strategic fit: IP that will never anchor the brand becomes cash and goodwill in someone else&rsquo;s hands</td><td>Prototype, Singularity, the Sierra adventure catalog</td></tr>
        <tr><td class="tk">License</td><td>Partners build, Xbox owns &mdash; the Toys for Bob model</td><td>Spyro and Crash to platformer specialists, Guitar Hero to a rhythm-game developer</td></tr>
      </tbody></table></div>
      <h3>Moving forward</h3>
      <ul class="proselist">
        <li><b>Own the publisher identity.</b> Rebrand around the catalog and the console, with the focus on being a games company.</li>
        <li><b>Genre houses, no more silos.</b> Merge studios by DNA into verticals, with the best talent concentrated and every genre covered on purpose.</li>
        <li><b>A vault that ships quarterly.</b> Use, sell or license every IP. One vault revival in production at all times, so nothing sits on the shelf for a decade again.</li>
        <li><b>Build for volatility.</b> Studios and IP now enter and exit yearly. A modular brand system, with houses and franchises as sub-brands, flexes where a monolith breaks.</li>
      </ul>
      <p class="fs-note">Research I run for myself, not advice. I am not a licensed financial advisor. This is an outside-in design exercise built from public reporting, not inside knowledge of Microsoft&rsquo;s plans, and it is not a view on Microsoft stock. Act on it and the risk is yours, not mine.</p>
    </div><!-- /con-xbox -->

    <div class="concept" id="con-futuresight">
    <div class="eyebrow">Concept 11 &middot; opened Aug 2026 &middot; forward-tracked</div>
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
      <div class="eyebrow">Concept 12 &middot; deep value screen &middot; run <span id="vsRun"></span></div>
      <h2>Value Scanner</h2>
      <p class="fs-kicker">The opposite instinct to Futuresight. Futuresight buys a story; this buys a balance sheet nobody wants.</p>
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
      <div class="eyebrow">Concept 13 &middot; quality growth screen &middot; run <span id="gsRun"></span></div>
      <h2>Quality Growth</h2>
      <p class="fs-kicker">This one sits between Futuresight and the Value Scanner. Futuresight buys a story and the Value Scanner buys a balance sheet nobody wants; this one looks for a business that is already working and asks whether the market has noticed yet.</p>
      <p class="prose">A screen for companies expanding operations accretively &mdash; where capital newly put to work earns more than the capital already there &mdash; scored across seven pillars covering growth, margins and returns, cash generation, balance sheet and liquidity, capital allocation, valuation, and how thinly the name is held and covered. That last one is the tilt: a good business every fund already owns and twenty analysts already model is a worse idea than the same business nobody is writing about.</p>
      <p class="fs-note">Research I run for myself, not advice. I am not a licensed financial advisor. A screen ranks what is measurable in a filing, which is never the whole question &mdash; it cannot read a management team, a contract, or a competitor. Trailing fundamentals also cannot tell operating progress from a commodity cycle, which is why producers are flagged rather than quietly ranked. Act on it and the risk is yours, not mine.</p>
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
  var RL = __RL_JSON__;
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
            var bg=i===j?"var(--panel-2)":"rgba(201,162,39,"+(a*0.72).toFixed(3)+")";
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
    /* the tape: a second, inert copy of the keycaps rides behind the first so the loop never shows a seam */
    var track=document.getElementById("ctrack");
    [].slice.call(track.querySelectorAll(".cbtn")).forEach(function(b){
      var d=b.cloneNode(true);
      d.classList.add("dup"); d.setAttribute("aria-hidden","true"); d.setAttribute("tabindex","-1");
      track.appendChild(d);
    });
    /* a thumb holds the tape still long enough to land the tap */
    var hold;
    nav.addEventListener("touchstart",function(){ clearTimeout(hold); nav.classList.add("hold"); },{passive:true});
    nav.addEventListener("touchend",function(){
      clearTimeout(hold); hold=setTimeout(function(){ nav.classList.remove("hold"); },2600);
    },{passive:true});
    var btns=[].slice.call(nav.querySelectorAll(".cbtn"));
    btns.forEach(function(b){
      b.addEventListener("click",function(){
        var c=b.getAttribute("data-c");
        btns.forEach(function(x){x.classList.toggle("on",x.getAttribute("data-c")===c);});
        ["riskmgmt","riskfinal","starbucks","analytics","insops","market","roulette","scm","forecast","xbox","futuresight","value","growth"].forEach(function(k){
          var el=document.getElementById("con-"+k);
          if(el) el.classList.toggle("active",k===c);
        });
        if(c==="roulette" && window.__rlDraw) window.__rlDraw();
        if(c==="futuresight" && window.__fsDraw &&
           document.getElementById("fsv-track").classList.contains("active")) window.__fsDraw();
      });
    });
  })();

  /* ---------------- Concept 12: Value Scanner ---------------- */
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

  /* ---------------- Concept 13: Quality Growth ---------------- */
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

    /* A hard cut. The sections of the new panel cut in on twos; the slab on
       the key rail slides. Nothing covers the frame. */
    function activate(id){ swap(id); }
    tabs.forEach(function(t){t.addEventListener("click",function(){activate(t.getAttribute("data-panel"));});});
  })();


  /* ---------------- Concept 07: S&P Roulette ---------------- */
  (function(){
    if(!RL || !RL.rows || !RL.rows.length) return;
    var cv=document.getElementById("rlWheel"); if(!cv || !cv.getContext) return;
    /* eleven GICS sectors in GICS order - the order is the spectrum */
    var SEC=[["Energy","Enrg","#F2854A"],["Materials","Matl","#D9B45A"],["Industrials","Indu","#A3AC6C"],
             ["Consumer Discretionary","CDis","#F095B8"],["Consumer Staples","CStp","#4FC26A"],["Health Care","Hlth","#3FD6A0"],
             ["Financials","Finl","#5AA0F0"],["Information Technology","InfT","#9D8CF0"],["Communication Services","Comm","#C98CE0"],
             ["Utilities","Util","#4FC3D6"],["Real Estate","REst","#C0927A"]];
    var TIER=["Large","Mid","Small"], TCLS=["rl-lg","rl-md","rl-sm"];
    var U=RL.rows.map(function(r){return {tk:r[0],co:r[1],si:r[2],ci:r[3]};});
    var st={caps:[true,true,true], secs:SEC.map(function(){return true;}), book:[], spinning:false, angle:0};
    var $=function(id){return document.getElementById(id);};
    var fmt=function(n){return n.toLocaleString("en-US");};
    var pct=function(x){return (x*100).toFixed(1)+"%";};
    var esc=function(s){return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;");};
    var css=function(n){return getComputedStyle(document.documentElement).getPropertyValue(n).trim();};
    var TAU=Math.PI*2, POINTER=-Math.PI/2, segs=[];
    var reduced=!!(window.matchMedia && window.matchMedia("(prefers-reduced-motion:reduce)").matches);

    function live(){ return U.filter(function(c){return st.caps[c.ci]&&st.secs[c.si];}); }
    function free(extra){
      var t={}; st.book.concat(extra||[]).forEach(function(r){t[r.tk]=1;});
      return live().filter(function(c){return !t[c.tk];});
    }
    function any(pool){ return pool[Math.floor(Math.random()*pool.length)]; }
    function dot(i){ return "<i class='rl-dot' style='--c:"+SEC[i][2]+"'></i>"; }

    function layout(){
      var pool=live(), a=0; segs=[];
      SEC.forEach(function(s,i){
        var n=0; pool.forEach(function(c){ if(c.si===i) n++; });
        if(!n) return;
        var span=n/pool.length*TAU;
        segs.push({i:i,name:s[0],short:s[1],color:s[2],n:n,share:n/pool.length,a0:a,a1:a+span,mid:a+span/2});
        a+=span;
      });
    }

    /* the betting layout: sector odds, each one a switch */
    function renderOdds(){
      var pool=live(), box=$("rlOdds");
      box.innerHTML=SEC.map(function(s,i){
        var n=U.filter(function(c){return c.si===i&&st.caps[c.ci];}).length;
        var p=st.secs[i]&&pool.length?n/pool.length:0;
        return "<button type='button' class='rl-odd' data-s='"+i+"' aria-pressed='"+st.secs[i]+"'>"+
          "<span class='rl-on'>"+dot(i)+s[0]+"</span>"+
          "<span class='rl-op'>"+n+" \u00b7 "+(st.secs[i]?pct(p):"off the board")+"</span></button>";
      }).join("");
      [].forEach.call(box.querySelectorAll(".rl-odd"),function(b){
        b.addEventListener("click",function(){
          if(st.spinning) return;
          var i=+b.getAttribute("data-s");
          st.secs[i]=!st.secs[i];
          if(!live().length){ st.secs[i]=true; return; }   /* never empty the drum */
          refresh();
        });
      });
    }
    [].forEach.call($("rlCaps").querySelectorAll(".tlv"),function(b){
      b.addEventListener("click",function(){
        if(st.spinning) return;
        var i=+b.getAttribute("data-cap");
        st.caps[i]=!st.caps[i];
        if(!live().length){ st.caps[i]=true; return; }
        b.classList.toggle("active",st.caps[i]);
        b.setAttribute("aria-pressed",String(st.caps[i]));
        refresh();
      });
    });
    function refresh(){ layout(); renderOdds(); drawWheel(st.angle); renderMix(); }

    /* the wheel */
    function drawWheel(rot){
      var dpr=Math.min(window.devicePixelRatio||1,2);
      var w=cv.getBoundingClientRect().width;
      var S=Math.round(w>0?Math.min(w,460):320);
      cv.width=S*dpr; cv.height=S*dpr;
      var ctx=cv.getContext("2d");
      ctx.setTransform(dpr,0,0,dpr,0,0); ctx.clearRect(0,0,S,S);
      var cx=S/2, cy=S/2, rO=S*.47, rR=S*.435, rI=S*.215, rB=S*.325;
      var brass=css("--accent")||"#C9A227", bg=css("--bg")||"#0A101C", panel=css("--panel")||"#101A2B",
          bone=css("--bone")||"#F2EDE0", faint=css("--faint")||"#697690",
          mono=css("--mono")||"monospace", disp=css("--display")||"Impact,sans-serif";

      ctx.beginPath(); ctx.arc(cx,cy,rO,0,TAU); ctx.fillStyle=bg; ctx.fill();
      ctx.lineWidth=2; ctx.strokeStyle=brass; ctx.stroke();

      ctx.save(); ctx.translate(cx,cy); ctx.rotate(rot);
      segs.forEach(function(s){
        ctx.beginPath(); ctx.moveTo(0,0); ctx.arc(0,0,rR,s.a0,s.a1); ctx.closePath();
        ctx.fillStyle=s.color; ctx.fill(); ctx.lineWidth=2; ctx.strokeStyle=bg; ctx.stroke();
        if(s.a1-s.a0>0.14){
          /* labels stay upright: flip the ones that land on the left half */
          var ab=((s.mid+rot)%TAU+TAU)%TAU, flip=ab>Math.PI/2&&ab<Math.PI*1.5;
          ctx.save(); ctx.rotate(s.mid);
          if(flip){ ctx.rotate(Math.PI); ctx.textAlign="left"; } else ctx.textAlign="right";
          ctx.textBaseline="middle"; ctx.fillStyle="#0A101C";
          ctx.font="700 "+Math.max(9,S*.03).toFixed(1)+"px "+mono;
          ctx.fillText(s.short.toUpperCase(), flip?-(rR-S*.035):rR-S*.035, 0);
          ctx.restore();
        }
      });
      ctx.restore();

      ctx.beginPath(); ctx.arc(cx,cy,rI,0,TAU); ctx.fillStyle=panel; ctx.fill();
      ctx.lineWidth=2; ctx.strokeStyle=brass; ctx.stroke();
      ctx.textAlign="center"; ctx.textBaseline="alphabetic";
      ctx.fillStyle="#05080F"; ctx.font=(S*.095).toFixed(1)+"px "+disp;
      ctx.fillText(fmt(live().length),cx+2,cy+S*.02+2);
      ctx.fillStyle=bone; ctx.fillText(fmt(live().length),cx,cy+S*.02);
      ctx.fillStyle=faint; ctx.font="600 "+(S*.026).toFixed(1)+"px "+mono;
      ctx.fillText("IN THE DRUM",cx,cy+S*.07);

      var bx=cx+Math.cos(POINTER)*rB, by=cy+Math.sin(POINTER)*rB;
      ctx.beginPath(); ctx.arc(bx,by,S*.022,0,TAU); ctx.fillStyle=bone; ctx.fill();
      ctx.lineWidth=2; ctx.strokeStyle="#05080F"; ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(cx,cy-rO+S*.03); ctx.lineTo(cx-S*.02,cy-rO-S*.018); ctx.lineTo(cx+S*.02,cy-rO-S*.018);
      ctx.closePath(); ctx.fillStyle=brass; ctx.fill(); ctx.lineWidth=2; ctx.strokeStyle="#05080F"; ctx.stroke();
    }

    function angleFor(si){
      var s=null; segs.forEach(function(x){ if(x.i===si) s=x; });
      if(!s) return 0;
      var inset=(s.a1-s.a0)*.16;
      return POINTER-(s.a0+inset+Math.random()*((s.a1-s.a0)-inset*2));
    }
    function spinTo(pick,done){
      var from=st.angle, to=angleFor(pick.si);
      while(to<from) to+=TAU;
      to+=(4+Math.floor(Math.random()*2))*TAU;
      var ended=false, finish=function(){
        if(ended) return; ended=true;
        st.angle=to%TAU; drawWheel(st.angle); done();
      };
      if(reduced){ finish(); return; }
      var dur=2600+Math.random()*500, t0=null;
      /* a starved rAF (background tab) must not leave the table locked */
      setTimeout(finish,dur+600);
      (function frame(now){
        if(ended) return;
        if(t0===null) t0=now;
        var t=Math.min(1,(now-t0)/dur), e=1-Math.pow(1-t,4);
        st.angle=from+(to-from)*e; drawWheel(st.angle);
        if(t<1) requestAnimationFrame(frame); else finish();
      })(performance.now());
    }

    function announce(c){
      var v=$("rlVerdict"); v.classList.remove("idle");
      v.innerHTML="<div class='rl-vt'>"+esc(c.tk)+"</div><div class='rl-vn'>"+esc(c.co)+"</div>"+
        "<div class='rl-vm'><span class='rl-tag'>"+dot(c.si)+SEC[c.si][0]+"</span>"+
        "<span class='chip "+TCLS[c.ci]+"'>"+TIER[c.ci]+"</span></div>";
    }
    function busy(b){ st.spinning=b; ["rlSpin","rlDeal","rlClear"].forEach(function(id){ $(id).disabled=b; }); }
    function size(){ return Math.max(1,Math.min(30,parseInt($("rlSize").value,10)||10)); }

    $("rlSpin").addEventListener("click",function(){
      if(st.spinning) return;
      var pool=free(); if(!pool.length) return;
      var c=any(pool); busy(true);
      spinTo(c,function(){ announce(c); st.book.push({tk:c.tk,co:c.co,si:c.si,ci:c.ci,locked:false}); renderBook(); renderMix(); busy(false); });
    });
    $("rlDeal").addEventListener("click",function(){
      if(st.spinning) return;
      st.book=st.book.filter(function(r){return r.locked;});
      var need=size()-st.book.length, picks=[];
      for(var i=0;i<need;i++){ var pool=free(picks); if(!pool.length) break; picks.push(any(pool)); }
      if(!picks.length){ renderBook(); renderMix(); return; }
      busy(true);
      spinTo(picks[picks.length-1],function(){
        picks.forEach(function(p){ st.book.push({tk:p.tk,co:p.co,si:p.si,ci:p.ci,locked:false}); });
        announce(picks[picks.length-1]); renderBook(); renderMix(); busy(false);
      });
    });
    $("rlClear").addEventListener("click",function(){
      if(st.spinning) return;
      st.book=[];
      var v=$("rlVerdict"); v.classList.add("idle");
      v.innerHTML="<div class='rl-vt'>Table cleared</div><div class='rl-vn'>Spin again whenever you're ready.</div>";
      renderBook(); renderMix();
    });
    $("rlCopy").addEventListener("click",function(){
      if(!st.book.length) return;
      var b=$("rlCopy"), txt=st.book.map(function(r){return r.tk;}).join(", ");
      var back=function(){ setTimeout(function(){ b.textContent="Copy tickers"; },1600); };
      if(navigator.clipboard && navigator.clipboard.writeText){
        navigator.clipboard.writeText(txt).then(function(){ b.textContent="Copied"; back(); },
          function(){ b.textContent=txt.slice(0,40)+"\u2026"; back(); });
      } else { b.textContent=txt.slice(0,40)+"\u2026"; back(); }
    });
    $("rlSize").addEventListener("input",function(){ $("rlDealN").textContent=size(); });

    /* the draw: equal weight, no money on the table */
    function renderBook(){
      var n=st.book.length, w=n?1/n:0;
      $("rlEmpty").style.display=n?"none":"block";
      $("rlMeta").textContent=n?(n+" position"+(n===1?"":"s")+" \u00b7 "+pct(w)+" each"):"0 positions";
      var tb=$("rlBook");
      tb.innerHTML=st.book.map(function(r,i){
        return "<tr class='"+(r.locked?"locked":"")+"'>"+
          "<td class='rl-slot'>"+(i<9?"0":"")+(i+1)+"</td>"+
          "<td class='tk'>"+esc(r.tk)+"</td>"+
          "<td class='rl-co'>"+esc(r.co)+"</td>"+
          "<td><span class='rl-tag'>"+dot(r.si)+SEC[r.si][0]+"</span></td>"+
          "<td><span class='chip "+TCLS[r.ci]+"'>"+TIER[r.ci]+"</span></td>"+
          "<td class='num r'>"+pct(w)+"</td>"+
          "<td class='r'><div class='rl-rowbtns'>"+
            "<button type='button' class='rl-mini' data-lock='"+i+"' aria-pressed='"+r.locked+"'>"+(r.locked?"Held":"Hold")+"</button>"+
            "<button type='button' class='rl-mini' data-re='"+i+"'>Respin</button></div></td></tr>";
      }).join("");
      [].forEach.call(tb.querySelectorAll("[data-lock]"),function(b){
        b.addEventListener("click",function(){ var i=+b.getAttribute("data-lock"); st.book[i].locked=!st.book[i].locked; renderBook(); });
      });
      [].forEach.call(tb.querySelectorAll("[data-re]"),function(b){
        b.addEventListener("click",function(){
          if(st.spinning) return;
          var i=+b.getAttribute("data-re"), old=st.book[i];
          st.book.splice(i,1);
          var pool=free(); st.book.splice(i,0,old);
          if(!pool.length) return;
          var c=any(pool);
          st.book[i]={tk:c.tk,co:c.co,si:c.si,ci:c.ci,locked:false};
          announce(c); renderBook(); renderMix();
        });
      });
    }

    /* the mix: how far the draw drifted from the index */
    function renderMix(){
      var n=st.book.length;
      var rows=segs.map(function(s){
        var d=st.book.filter(function(r){return r.si===s.i;}).length;
        return {i:s.i,name:s.name,color:s.color,share:s.share,drawn:d,ds:n?d/n:0};
      }).sort(function(a,b){ return (b.ds-a.ds)||(b.share-a.share); });
      var max=.0001; rows.forEach(function(r){ max=Math.max(max,r.ds,r.share); });
      $("rlBars").innerHTML=rows.map(function(r){
        return "<div class='rl-brow'><span class='rl-bname'>"+dot(r.i)+"<span class='rl-nm'>"+r.name+"</span></span>"+
          "<span class='rl-track'><span class='rl-fill' style='--c:"+r.color+";width:"+(r.ds/max*100).toFixed(1)+"%'></span>"+
          "<span class='rl-mark' style='left:"+(r.share/max*100).toFixed(1)+"%'></span></span>"+
          "<span class='rl-bval'><b>"+(n?pct(r.ds):"\u2014")+"</b> / "+pct(r.share)+"</span></div>";
      }).join("");
      var ro=$("rlRead");
      if(!n){
        ro.textContent="Deal a book and this reads back how far the draw drifted from the index, which is the whole point. Ten names out of "+
          fmt(U.length)+" will miss the index mix badly and often, and seeing by how much is more instructive than any stock tip on this page.";
        return;
      }
      var over=rows.filter(function(r){return r.drawn;}).sort(function(a,b){return (b.ds-b.share)-(a.ds-a.share);})[0];
      var miss=rows.filter(function(r){return !r.drawn;}).sort(function(a,b){return b.share-a.share;});
      var tvd=rows.reduce(function(s,r){return s+Math.abs(r.ds-r.share);},0)/2;
      var tiers=[0,1,2].filter(function(c){return st.caps[c];}).map(function(c){
        return st.book.filter(function(r){return r.ci===c;}).length+" "+TIER[c].toLowerCase();
      }).join(", ");
      var bits=[n+" name"+(n===1?"":"s")+": "+tiers+"."];
      if(over && over.ds>over.share) bits.push("Heaviest tilt is <b>"+over.name+"</b> at "+pct(over.ds)+" against "+pct(over.share)+" of the drum.");
      if(miss.length) bits.push("Nothing at all from "+miss.length+" sector"+(miss.length===1?"":"s")+": "+
        miss.slice(0,3).map(function(m){return m.name;}).join(", ")+(miss.length>3?" and others":"")+".");
      bits.push("Total drift from the index mix: <b>"+pct(tvd)+"</b> of the book sitting in the wrong sector.");
      ro.innerHTML=bits.join(" ");
    }

    /* open in a working state: a dealt book, so the page shows what it does */
    layout(); renderOdds(); drawWheel(st.angle);
    var pool=live().slice();
    for(var i=0;i<10&&pool.length;i++){ var c=pool.splice(Math.floor(Math.random()*pool.length),1)[0]; st.book.push({tk:c.tk,co:c.co,si:c.si,ci:c.ci,locked:false}); }
    announce(st.book[st.book.length-1]); renderBook(); renderMix();

    window.__rlDraw=function(){ drawWheel(st.angle); };
    var rt; window.addEventListener("resize",function(){ clearTimeout(rt); rt=setTimeout(function(){ drawWheel(st.angle); },110); });
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
      return v>=0 ? "rgba(60,199,126,"+a.toFixed(3)+")" : "rgba(224,72,78,"+a.toFixed(3)+")";
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

    /* The viewport height, or 0 when it genuinely cannot be measured — which
       happens in a hidden or prerendered tab. Every caller below treats 0 as
       "show it" rather than "hide it": content being visible is the safe
       failure, an unrecoverable blank panel is not. */
    var vport=function(){
      return window.innerHeight || document.documentElement.clientHeight || 0;
    };

    /* --- the slab that sits under the active tab --- */
    var bar=document.querySelector(".tabs");
    if(bar){
      var ink=document.createElement("span");
      ink.className="tabink";
      bar.appendChild(ink);
      bar.classList.add("hasink");
      var place=function(){
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
        var h=document.documentElement.scrollHeight-vport();
        var p=h>0?Math.min(1,Math.max(0,window.scrollY/h)):0;
        prog.style.transform="scaleX("+p+")";
        if(window.__sweep) window.__sweep();
      };
      /* Coalesce to one run per scroll burst, but never depend on a frame
         arriving: requestAnimationFrame is paused in a background tab and in
         some throttled mobile browsers, and a sweep that never runs leaves
         every .reveal section clipped for the rest of the session. The timer
         is the guarantee; the frame is just the smooth path. Whichever lands
         first does the work and the other finds the flag already cleared. */
      var run=function(){ if(!tick) return; tick=false; upd(); };
      window.addEventListener("scroll",function(){
        if(tick) return;
        tick=true;
        requestAnimationFrame(run);
        setTimeout(run,120);
      },{passive:true});
      document.addEventListener("visibilitychange",function(){
        if(!document.hidden) upd();
      });
      upd();
    }

    /* --- sections below the fold settle in as they are reached ---
       Deliberately not an IntersectionObserver: elements added to a panel that
       was display:none a moment ago can be missed, and a missed element stays
       at opacity 0. This sweep runs on every scroll frame, so a section that
       is on screen is always visible. */
    var sweep=function(){
      var vh=vport() || 1e9;   /* unmeasurable: reveal rather than hide */
      [].forEach.call(document.querySelectorAll(".reveal:not(.seen)"),function(el){
        var r=el.getBoundingClientRect();
        if(r.top < vh*0.94 && r.bottom > 0) el.classList.add("seen");
      });
    };
    window.__sweep=sweep;
    window.__reveal=function(root){
      if(still) return;
      var h=vport();
      if(!h) return;            /* cannot measure: leave every section visible */
      var host=root||document;
      [].forEach.call(host.querySelectorAll("section, .chart-card"),function(el){
        if(el.dataset.rv) return;
        var r=el.getBoundingClientRect();
        if(r.top < h*0.94) return;                  /* already on screen: leave it */
        el.dataset.rv="1";
        el.classList.add("reveal");
      });
      sweep();
    };
    /* last resort: never leave anything hidden if the page is simply left alone */
    setTimeout(function(){
      [].forEach.call(document.querySelectorAll(".reveal:not(.seen)"),function(el){
        var r=el.getBoundingClientRect();
        if(r.top < (vport()||1e9)*1.6) el.classList.add("seen");
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
    print("warning: valuescan.json missing - run valuescan_sync.py; Concept 12 will render empty")
html = html.replace("__VS_JSON__", json.dumps(vs, ensure_ascii=False))

gs_path = os.path.join(HERE, "growthscan.json")
gs = json.load(open(gs_path, encoding="utf-8")) if os.path.exists(gs_path) else None
if gs is None:
    print("warning: growthscan.json missing - run growthscan_sync.py; Concept 13 will render empty")
html = html.replace("__GS_JSON__", json.dumps(gs, ensure_ascii=False))

rl_path = os.path.join(HERE, "roulette.json")
rl = json.load(open(rl_path, encoding="utf-8")) if os.path.exists(rl_path) else None
if rl is None:
    print("warning: roulette.json missing; Concept 07 will render empty")
html = html.replace("__RL_JSON__", json.dumps(rl, ensure_ascii=False, separators=(",", ":")))
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
