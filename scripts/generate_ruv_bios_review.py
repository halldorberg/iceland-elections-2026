"""Render scan_results/ruv_bios.json into a self-contained review HTML page.

Output: ruv-bios-review.html  (with simple password lock, dark theme).
Group cards by municipality, party, ballot order. Each card shows:
  - Old bio (collapsed if exists)
  - New merged bio
  - Fact-check list (statement + verbatim RÚV quote)
  - Sources (linked, includes RÚV profile)
"""
from __future__ import annotations
import json, html, sys, io, os
from pathlib import Path
from datetime import date
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).parent.parent
INPUT  = ROOT / 'scan_results' / 'ruv_bios.json'
OUTPUT = ROOT / 'ruv-bios-review.html'

PASSWORD_HASH = '8d64f161a23d57eb3246757b05f70ac37174f7f7'  # 'happyhappy' sha1

# Pretty names per muni constant
MUNI_NAMES = {
    'RVK': 'Reykjavík', 'KOP': 'Kópavogur', 'HAF': 'Hafnarfjörður',
    'GAR': 'Garðabær', 'MOS': 'Mosfellsbær', 'AKU': 'Akureyri',
    'SEL': 'Seltjarnarnes', 'RNB': 'Reykjanesbær', 'VOG': 'Vogar',
    'GRN': 'Grindavík', 'SNB': 'Suðurnesjabær', 'ARB': 'Árborg',
    'VME': 'Vestmannaeyjar', 'NPG': 'Norðurþing', 'FJB': 'Fjallabyggð',
    'FJD': 'Fjarðabyggð', 'HFJ': 'Hornafjörður', 'AKR': 'Akranes',
    'BBD': 'Borgarbyggð', 'ISF': 'Ísafjörður', 'HVG': 'Hveragerði',
    'RTE': 'Rangárþing eystra', 'RTY': 'Rangárþing ytra',
    'OLF': 'Ölfus', 'SKR': 'Skaftárhreppur', 'MYR': 'Mýrdalshreppur',
    'BSG': 'Bláskógabyggð', 'FHR': 'Flóahreppur', 'HMR': 'Hrunamannahreppur',
    'GGR': 'Grímsnes- og Grafningshreppur', 'SGN': 'Skeiða- og Gnúpverjahreppur',
    'DVB': 'Dalvíkurbyggð', 'EJA': 'Eyjafjarðarsveit', 'HGS': 'Hörgársveit',
    'HNB': 'Húnabyggð', 'HNT': 'Húnaþing vestra', 'SFJ': 'Skagafjörður',
    'SST': 'Skagaströnd', 'STK': 'Stykkishólmur', 'GFJ': 'Grundarfjörður',
    'BLV': 'Bolungarvík', 'SDV': 'Súðavík', 'VBG': 'Vesturbyggð',
    'STD': 'Strandabyggð', 'RKH': 'Reykhólar', 'MUT': 'Múlaþing',
    'THV': 'Þingeyjarsveit', 'HVF': 'Hvalfjarðarsveit', 'SNF': 'Snæfellsbær',
    'SVS': 'Svalbarðsströnd', 'KJO': 'Kjósarhreppur', 'VPF': 'Vopnafjörður',
    'TJR': 'Tjörnes', 'ARN': 'Árneshreppur',
}

def render_sources(sources):
    if not sources:
        return ''
    parts = []
    for s in sources:
        url = s.get('url', '#')
        label = s.get('label', url)
        parts.append(f'<a class="source-link" href="{html.escape(url)}" target="_blank" rel="noopener">{html.escape(label)}</a>')
    return '<div class="sources-row">' + ' '.join(parts) + '</div>'

def render_facts(facts):
    if not facts:
        return '<div class="muted">(engar nýjar staðreyndir)</div>'
    rows = []
    for f in facts:
        stmt = html.escape(f.get('statement', ''))
        quote = html.escape(f.get('ruv_quote', ''))
        rows.append(
            f'<div class="fact-row">'
            f'<div class="fact-stmt">{stmt}</div>'
            f'<div class="fact-quote">RÚV: <em>{quote}</em></div>'
            f'</div>'
        )
    return '<div class="facts">' + ''.join(rows) + '</div>'

def render_card(entry):
    name = html.escape(entry['name'])
    muni = html.escape(MUNI_NAMES.get(entry['muni_const'], entry['muni_const']))
    party = html.escape(entry['party_code'])
    ballot = entry['ballot']
    rid = f'{entry["muni_const"]}.{party}.{ballot}'
    old = entry.get('old_bio')
    new_bio = entry.get('new_bio') or ''
    new_html = '<br><br>'.join(html.escape(p) for p in new_bio.split('\n\n') if p.strip())

    old_block = ''
    if old:
        old_html = '<br><br>'.join(html.escape(p) for p in old.split('\n\n') if p.strip())
        old_block = (
            '<details class="old-bio-block">'
            '<summary>Núverandi æviágrip</summary>'
            f'<div class="bio-text old-bio">{old_html}</div>'
            '</details>'
        )
    else:
        old_block = '<div class="muted small">(engin gömul ævisaga)</div>'

    facts_block = render_facts(entry.get('fact_check', []))
    sources_block = render_sources(entry.get('sources', []))

    return (
        f'<article class="card" id="{html.escape(rid)}">'
        f'  <header class="card-header">'
        f'    <div class="card-title">{ballot}. {name}</div>'
        f'    <div class="card-meta">'
        f'      <span class="badge">{html.escape(rid)}</span>'
        f'      <span class="tag">{muni}</span>'
        f'    </div>'
        f'  </header>'
        f'  {old_block}'
        f'  <div class="bio-block">'
        f'    <div class="bio-label">Nýtt sameinað æviágrip</div>'
        f'    <div class="bio-text">{new_html}</div>'
        f'  </div>'
        f'  <div class="facts-block">'
        f'    <div class="bio-label">Staðreyndapróf — bein tilvitnun úr RÚV svörum</div>'
        f'    {facts_block}'
        f'  </div>'
        f'  {sources_block}'
        f'</article>'
    )

def render():
    if not INPUT.exists():
        print(f'No input at {INPUT}')
        return
    data = json.load(open(INPUT, encoding='utf-8'))
    print(f'entries: {len(data)}')

    # Sort by muni name, then ballot
    data.sort(key=lambda e: (MUNI_NAMES.get(e['muni_const'], e['muni_const']), e['party_code'], int(e['ballot'])))

    # Group by muni
    by_muni = defaultdict(list)
    for e in data:
        by_muni[e['muni_const']].append(e)

    # Build TOC
    toc_links = []
    for muni in sorted(by_muni.keys(), key=lambda k: MUNI_NAMES.get(k, k)):
        n = len(by_muni[muni])
        toc_links.append(f'<a href="#muni-{muni}">{html.escape(MUNI_NAMES.get(muni, muni))} <span class="toc-count">({n})</span></a>')

    sections_html = []
    for muni in sorted(by_muni.keys(), key=lambda k: MUNI_NAMES.get(k, k)):
        cards = ''.join(render_card(e) for e in by_muni[muni])
        sections_html.append(
            f'<section id="muni-{muni}">'
            f'  <h2>{html.escape(MUNI_NAMES.get(muni, muni))} <span class="section-count">{len(by_muni[muni])}</span></h2>'
            f'  {cards}'
            f'</section>'
        )

    today = str(date.today())
    page = (
        '<!DOCTYPE html>\n<html lang="is"><head><meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>RÚV ævisögu-yfirferð — {today}</title>'
        '<style>'
        ':root{--bg:#0d1117;--surface:#161b22;--surface2:#21262d;--border:#30363d;'
        '--text:#e6edf3;--muted:#8b949e;--accent:#58a6ff;--green:#3fb950;'
        '--yellow:#d29922;--red:#f85149;--purple:#bc8cff;}'
        '*{box-sizing:border-box;margin:0;padding:0;}'
        'body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;font-size:14px;line-height:1.6;}'
        '#lock-screen{position:fixed;inset:0;background:var(--bg);display:flex;align-items:center;justify-content:center;z-index:9999;}'
        '.lock-box{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:40px;text-align:center;width:340px;}'
        '.lock-box h2{margin-bottom:8px;font-size:20px;}'
        '.lock-box p{color:var(--muted);margin-bottom:24px;font-size:13px;}'
        '.lock-box input{width:100%;padding:10px 14px;background:var(--bg);border:1px solid var(--border);border-radius:8px;color:var(--text);font-size:14px;margin-bottom:12px;outline:none;}'
        '.lock-box button{width:100%;padding:10px;background:var(--accent);color:#000;border:none;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;}'
        '.lock-error{color:var(--red);font-size:12px;margin-top:8px;display:none;}'
        '#main{display:none;max-width:1100px;margin:0 auto;padding:40px 20px 80px;}'
        '.page-header{margin-bottom:30px;border-bottom:1px solid var(--border);padding-bottom:24px;}'
        '.page-header h1{font-size:28px;font-weight:700;margin-bottom:8px;}'
        '.page-header p{color:var(--muted);}'
        '.toc{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:14px 20px;margin-bottom:32px;}'
        '.toc h3{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:8px;}'
        '.toc a{color:var(--accent);text-decoration:none;font-size:13px;display:inline-block;margin:2px 18px 2px 0;}'
        '.toc a:hover{text-decoration:underline;}'
        '.toc-count{color:var(--muted);font-size:11px;}'
        'h2{font-size:19px;font-weight:700;margin:48px 0 16px;padding-bottom:10px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:10px;}'
        '.section-count{background:var(--surface2);border:1px solid var(--border);border-radius:12px;padding:2px 10px;font-size:12px;font-weight:500;color:var(--muted);}'
        '.card{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:18px 20px;margin-bottom:14px;}'
        '.card-header{margin-bottom:12px;}'
        '.card-title{font-size:15px;font-weight:600;margin-bottom:6px;}'
        '.card-meta{display:flex;gap:6px;flex-wrap:wrap;align-items:center;}'
        '.badge{background:rgba(88,166,255,.12);color:var(--accent);border:1px solid rgba(88,166,255,.2);border-radius:12px;padding:2px 10px;font-size:11px;font-weight:500;font-family:ui-monospace,SFMono-Regular,Consolas,monospace;}'
        '.tag{background:var(--surface2);border:1px solid var(--border);border-radius:10px;padding:2px 8px;font-size:11px;color:var(--muted);}'
        '.bio-block,.facts-block{margin-top:12px;padding-top:12px;border-top:1px solid var(--border);}'
        '.bio-label{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin-bottom:6px;}'
        '.bio-text{color:var(--text);line-height:1.75;font-size:13.5px;}'
        '.bio-text.old-bio{color:var(--muted);}'
        '.old-bio-block{margin-bottom:10px;background:rgba(0,0,0,.18);border:1px solid var(--border);border-radius:8px;padding:8px 12px;}'
        '.old-bio-block summary{cursor:pointer;font-size:12px;color:var(--muted);}'
        '.old-bio-block[open] summary{margin-bottom:8px;padding-bottom:8px;border-bottom:1px solid var(--border);}'
        '.facts{display:grid;gap:8px;}'
        '.fact-row{padding:8px 10px;background:rgba(63,185,80,.05);border-left:3px solid var(--green);border-radius:6px;}'
        '.fact-stmt{color:var(--text);font-size:13px;line-height:1.55;margin-bottom:4px;}'
        '.fact-quote{color:var(--muted);font-size:11.5px;line-height:1.55;}'
        '.fact-quote em{color:var(--text);font-style:italic;}'
        '.sources-row{margin-top:14px;padding-top:12px;border-top:1px solid var(--border);display:flex;flex-wrap:wrap;gap:6px;}'
        '.source-link{color:var(--accent);font-size:11px;text-decoration:none;border:1px solid rgba(88,166,255,.3);border-radius:10px;padding:2px 8px;}'
        '.source-link:hover{background:rgba(88,166,255,.1);}'
        '.muted{color:var(--muted);}.small{font-size:12px;}'
        '</style></head><body>'
        '<div id="lock-screen"><div class="lock-box">'
        '<h2>Aðgangur</h2><p>Lykilorð þarf til að sjá yfirferðina.</p>'
        '<input type="password" id="pwd" autofocus>'
        '<button onclick="unlock()">Opna</button>'
        '<div id="lock-error" class="lock-error">Rangt lykilorð.</div>'
        '</div></div>'
        '<main id="main">'
        f'<header class="page-header"><h1>RÚV ævisögu-yfirferð</h1>'
        f'<p>{len(data)} frambjóðendur með RÚV-prófíla. Hvert kort sýnir gamla æviágripið (ef til), nýja sameinaða útgáfu, staðreyndapróf með beinum tilvitnunum úr RÚV svörum og heimildir.</p>'
        '</header>'
        '<div class="toc"><h3>Sveitarfélög</h3>'
        + ' '.join(toc_links)
        + '</div>'
        + '\n'.join(sections_html)
        + '</main>'
        '<script>'
        'async function sha1(s){const b=new TextEncoder().encode(s);const h=await crypto.subtle.digest("SHA-1",b);return Array.from(new Uint8Array(h)).map(x=>x.toString(16).padStart(2,"0")).join("");}'
        f'const HASH="{PASSWORD_HASH}";'
        'async function unlock(){const v=document.getElementById("pwd").value;const h=await sha1(v);if(h===HASH){document.getElementById("lock-screen").style.display="none";document.getElementById("main").style.display="block";sessionStorage.setItem("ruv_unlocked","1");}else{document.getElementById("lock-error").style.display="block";}}'
        'document.getElementById("pwd").addEventListener("keypress",e=>{if(e.key==="Enter")unlock();});'
        'if(sessionStorage.getItem("ruv_unlocked")==="1"){document.getElementById("lock-screen").style.display="none";document.getElementById("main").style.display="block";}'
        '</script></body></html>'
    )
    OUTPUT.write_text(page, encoding='utf-8')
    print(f'Wrote {OUTPUT}')

if __name__ == '__main__':
    render()
