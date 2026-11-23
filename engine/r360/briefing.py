"""Renders the Insight Briefing (Command Center feed) as one self-contained HTML file from the ledger.
No server needed: findings are embedded. Verdict buttons copy the exact command (or AiNxt chat line)
that records the verdict, so feedback flows back into ledger/verdicts.jsonl.
"""
from __future__ import annotations

import datetime as dt
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CSS = """
:root{--bg:#f7f7f5;--card:#fff;--ink:#16181d;--mute:#5d6470;--line:#e4e4df;--acc:#3d3dc4;
--ok:#1f7a4d;--okb:#e6f4ec;--warn:#9a5b00;--warnb:#fdf3e1;--bad:#b42318;--badb:#fdecea}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:14px/1.5 Inter,"Segoe UI",system-ui,sans-serif}
.num{font-family:"JetBrains Mono",Consolas,monospace;font-variant-numeric:tabular-nums}
header{padding:22px 32px 14px;border-bottom:1px solid var(--line);background:var(--card);display:flex;
justify-content:space-between;align-items:flex-end;gap:16px;flex-wrap:wrap}
h1{font-size:20px;margin:0}header p{margin:2px 0 0;color:var(--mute)}
.pill{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:2px 10px;font-size:12px;color:var(--mute)}
main{max-width:1080px;margin:0 auto;padding:24px 32px 60px}
.f{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin-bottom:16px}
.f h2{font-size:16px;margin:0 0 8px;line-height:1.4}
.meta{display:flex;gap:18px;flex-wrap:wrap;color:var(--mute);font-size:12.5px;margin-bottom:10px}
.badge{font-size:11px;font-weight:600;letter-spacing:.04em;padding:2px 8px;border-radius:6px}
.HIGH{background:var(--okb);color:var(--ok)}.MEDIUM{background:var(--warnb);color:var(--warn)}
.LOW,.NONE{background:var(--badb);color:var(--bad)}
details{border-top:1px solid var(--line);padding-top:8px;margin-top:8px}summary{cursor:pointer;color:var(--acc);font-weight:500}
table{border-collapse:collapse;width:100%;margin:8px 0;font-size:13px}td,th{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--mute);font-weight:500;font-size:12px}
.r-SUPPORTS{color:var(--ok);font-weight:600}.r-WEAKENS{color:var(--bad);font-weight:600}.r-INCONCLUSIVE,.r-INFO{color:var(--mute);font-weight:600}
ul.c{margin:6px 0 0 18px;padding:0;color:var(--mute)}pre{white-space:pre-wrap;background:#f2f2ee;padding:8px;border-radius:6px;font-size:11.5px}
.v{display:flex;gap:8px;margin-top:12px;flex-wrap:wrap}.v button{border:1px solid var(--line);background:var(--card);
border-radius:8px;padding:6px 12px;cursor:pointer;font:inherit}.v button:hover{border-color:var(--acc)}
.toast{position:fixed;bottom:20px;right:20px;background:var(--ink);color:#fff;padding:10px 14px;border-radius:8px;display:none;max-width:520px;font-size:12.5px}
.empty{color:var(--mute);padding:40px;text-align:center}
"""

JS = """
const F = __DATA__;
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const pct = x => (x>0?'+':'') + (x*100).toFixed(1) + '%';
const inr = x => '₹' + (x/1e5).toFixed(2) + ' L';
function test(t){return `<tr><td>${esc(t.test.replace('_',' '))}</td><td class="r-${t.reading}">${t.reading}</td>
<td>${esc(t.plain_english)}<details><summary>SQL and numbers</summary><pre>${esc(JSON.stringify(t.numbers,null,1))}\n\n${esc(t.sql)}</pre></details></td></tr>`}
function cand(c){return `<tr><td>${esc(c.type.replaceAll('_',' '))}</td><td class="num">${c.prior_score}</td>
<td>${esc(c.summary)}${(c.sources||[]).map(s=>`<div class="pill">${esc(s.document)} · ${esc(s.locator||'')}</div>`).join('')}
${c.tests?`<table>${c.tests.map(test).join('')}</table>`:''}</td></tr>`}
function card(f){const fl=f.flag, b=f.best_explanation, conf=b?b.confidence||'LOW':'NONE';
return `<section class="f"><h2>${esc(f.headline)}</h2>
<div class="meta"><span class="badge ${conf}">${conf==='NONE'?'UNEXPLAINED':conf+' CONFIDENCE'}</span>
<span class="num">Actual ${inr(fl.actual_spend)} vs expected ${inr(fl.expected_spend)} (${pct(fl.pct_change)})</span>
<span>${esc(f.merchant.category||'')}</span><span class="num">${esc(f.finding_id)}</span></div>
${f.narrative?`<p>${esc(f.narrative)}</p>`:''}
<details ${conf!=='NONE'?'open':''}><summary>Why we think so (${f.candidates.length} candidate cause${f.candidates.length===1?'':'s'} checked)</summary>
<table><tr><th>Type</th><th>Prior</th><th>Detail and tests</th></tr>${f.candidates.map(cand).join('')||'<tr><td colspan=3>No catalogued offer or proposition change fits.</td></tr>'}</table></details>
<details><summary>Cautions</summary><ul class="c">${f.critic_checks.map(x=>`<li>${esc(x)}</li>`).join('')}</ul></details>
<div class="v">${['CORRECT','PARTLY','WRONG'].map(v=>`<button onclick="verdict('${f.finding_id}','${v}')">${v==='CORRECT'?'Right':v==='PARTLY'?'Partly right':'Wrong'}</button>`).join('')}</div></section>`}
function verdict(id,v){const cmd=`python -m r360 verdict ${id} ${v} --note "..."`;
navigator.clipboard&&navigator.clipboard.writeText(cmd);const t=document.querySelector('.toast');
t.textContent='Copied. Paste in AiNxt chat ("Record verdict") or a terminal: '+cmd;t.style.display='block';setTimeout(()=>t.style.display='none',6000)}
document.getElementById('feed').innerHTML = F.length ? F.map(card).join('') : '<div class="empty">No findings yet.</div>';
"""


def render(ledger, out="app/briefing.html"):
    findings = ledger.findings()
    verdicts = {v["finding_id"]: v for v in ledger.verdicts()}
    for f in findings:
        f["analyst_verdict"] = verdicts.get(f["finding_id"], {}).get("verdict")
    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    findings.sort(key=lambda f: (order.get((f.get("best_explanation") or {}).get("confidence"), 3),
                                 f["flag"]["pct_change"]))
    data = json.dumps(findings, default=str).replace("</", "<\\/")
    weeks = sorted({f["flag"]["week_start"] for f in findings})
    page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>RuPay 360 · Insight Briefing</title><style>{CSS}</style></head><body>
<header><div><h1>Insight Briefing</h1><p>Unusual moves in spend, the likely cause from CVP, MITC and offers, and the evidence behind it.</p></div>
<div><span class="pill">Weeks: {html.escape(', '.join(weeks) or '-')}</span> <span class="pill">{len(findings)} findings</span>
<span class="pill">Built {dt.datetime.now():%d %b %Y %H:%M}</span></div></header>
<main id="feed"></main><div class="toast"></div><script>{JS.replace('__DATA__', data)}</script></body></html>"""
    p = Path(out)
    if not p.is_absolute():
        p = ROOT / p
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(page, encoding="utf-8")
    return p
