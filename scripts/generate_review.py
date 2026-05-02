#!/usr/bin/env python3
"""
generate_review.py
──────────────────
Generates scan-review.html from today's scan result files.
Run after each scan session; the review page is password-protected
and meant for human review before anything is applied to the live site.

Usage:
    python scripts/generate_review.py [--date YYYY-MM-DD]
"""

import json
import html as htmllib
import sys
from pathlib import Path
from datetime import date

ROOT = Path(__file__).parent.parent
SCAN_DIR = ROOT / "scan_results"
OUT = ROOT / "scan-review.html"

MUNI = {
    'reykjavik': 'Reykjavík', 'kopavogur': 'Kópavogur', 'hafnarfjordur': 'Hafnarfjörður',
    'gardabaer': 'Garðabær', 'mosfellsbaer': 'Mosfellsbær', 'akureyri': 'Akureyri',
    'seltjarnarnes': 'Seltjarnarnes', 'reykjanesbaer': 'Reykjanesbær',
    'sudurnesjabaer': 'Suðurnesjabær', 'arborg': 'Árborg', 'vestmannaeyjar': 'Vestmannaeyjar',
    'fjardabyggd': 'Fjarðabyggð', 'akranes': 'Akranes', 'borgarbyggd': 'Borgarbyggð',
    'isafjordur': 'Ísafjörður', 'vogar': 'Vogar', 'skaftarhreppur': 'Skaftárhreppur',
    'hrunamannahreppur': 'Hrunamannahreppur', 'skeidagnup': 'Skeiða- og Gnúpverjahreppur',
    'horgarsv': 'Hörgársveit', 'hunathing': 'Húnaþing vestra', 'skagafjordur': 'Skagafjörður',
    'hornafjordur': 'Hornafjörður', 'nordurping': 'Norðurþing',
    'rangarthingytra': 'Rangárþing ytra', 'rangarthingeystra': 'Rangárþing eystra',
    'dalvikurbyggd': 'Dalvíkurbyggð', 'hvalfjardarsveit': 'Hvalfjarðarsveit',
    'svalbardsstrond': 'Svalbarðsströnd', 'skagastrond': 'Skagaströnd',
    'hveragerdi': 'Hveragerði',
}

def muni(slug):
    return MUNI.get(slug, slug)

def e(s):
    return htmllib.escape(str(s)) if s else ''


def load_json(path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding='utf-8'))


def bio_section(bios):
    if not bios:
        return '<p style="color:var(--muted)">No bio results file found.</p>'
    rows = ''
    for b in bios:
        age_tag = f'<span class="tag">Aldur {b["age"]}</span>' if b.get('age') else ''
        interests = ' '.join(f'<span class="tag">{e(i)}</span>' for i in (b.get('interests') or []))
        social = ''
        if b.get('social'):
            for k, v in b['social'].items():
                if v:
                    social += f'<a href="{e(v)}" target="_blank" class="social-link">{k}</a> '
        sources_html = ''
        for src in (b.get('sources') or b.get('heimild') or []):
            # Sources may be plain URL strings OR {url, label} dicts.
            if isinstance(src, dict):
                url   = src.get('url', '')
                label = src.get('label') or (url.split('/')[2] if url.startswith('http') else url)
            else:
                url   = src
                label = url.split('/')[2] if url.startswith('http') else url
            if url:
                sources_html += f'<a href="{e(url)}" target="_blank" class="source-link">🔗 {e(label)}</a> '
        skipped_reason = b.get('skipped_reason')
        if skipped_reason and not b.get('bio'):
            sources_html = f'<span style="color:var(--yellow);font-size:11px">⏭ skipped: {e(skipped_reason)}</span>'
        sources_row = f'<div class="sources-row">{sources_html}</div>' if sources_html else ''

        rows += f'''
    <div class="card">
      <div class="card-header">
        <div class="card-title">{e(b["name"])}</div>
        <div class="card-meta">
          <span class="badge">{e(muni(b["muni_slug"]))}</span>
          <span class="badge secondary">{e(b["party_code"])}</span>
          <span class="badge tertiary">#{b["ballot"]}</span>
          {age_tag}
        </div>
      </div>
      <div class="bio-text">{e(b.get("bio",""))}</div>
      <div class="tags-row">{interests}{social}</div>
      {sources_row}
    </div>'''
    return rows


def news_section(news):
    if not news:
        return '<p style="color:var(--muted)">No news results file found.</p>'
    rows = ''
    for r in news:
        arts = r.get('new_articles', [])
        if not arts:
            continue
        arts_html = ''
        for a in arts:
            arts_html += f'''
        <div class="article-item">
          <a href="{e(a["url"])}" target="_blank">{e(a["title"])}</a>
          <span class="source-tag">{e(a.get("source",""))}</span>
        </div>'''
        rows += f'''
    <div class="card">
      <div class="card-header">
        <div class="card-title">{e(r["name"])}</div>
        <div class="card-meta">
          <span class="badge">{e(muni(r["muni_slug"]))}</span>
          <span class="badge secondary">{e(r["party_code"])}</span>
          <span class="badge tertiary">#{r["ballot"]}</span>
          <span class="count-badge">{len(arts)} article{"s" if len(arts)>1 else ""}</span>
        </div>
      </div>
      <div class="articles-list">{arts_html}</div>
    </div>'''
    return rows


def policy_section(policies):
    if not policies:
        return '''<div class="scan-note" style="background:rgba(248,81,73,.08);border-color:rgba(248,81,73,.25);color:#f85149">
      ⚠️ Policy scan results have been removed pending a re-scan with stricter source verification.
      Only platforms with clearly verifiable online sources will be included.
    </div>'''
    rows = ''
    for p in policies:
        agenda_html = ''
        for item in p.get('agenda', []):
            quote = item.get('source_quote', '')
            verified = item.get('quote_verified')
            quote_html = ''
            if quote:
                # green border for verified, red for "couldn't find on page"
                if verified is False:
                    border, bg, mark = '#f85149', 'rgba(248,81,73,.06)', '⚠ not found on linked page'
                elif verified is True:
                    border, bg, mark = '#3fb950', 'rgba(63,185,80,.06)', '✓ verbatim from page'
                else:
                    border, bg, mark = 'var(--accent)', 'rgba(88,166,255,.06)', ''
                mark_html = (
                    f'<span style="float:right;font-size:10px;font-style:normal;color:{border}">{mark}</span>'
                    if mark else ''
                )
                quote_html = (
                    '<div style="margin-top:6px;padding:6px 10px;'
                    f'border-left:2px solid {border};background:{bg};'
                    'font-size:11.5px;color:var(--muted);font-style:italic;line-height:1.5">'
                    f'{mark_html}„{e(quote)}"'
                    '</div>'
                )
            agenda_html += f'''
        <div class="agenda-item">
          <span class="agenda-icon">{e(item.get("icon",""))}</span>
          <div style="flex:1">
            <strong>{e(item.get("title",""))}</strong>
            <div class="agenda-text">{e(item.get("text",""))}</div>
            {quote_html}
          </div>
        </div>'''
        # Audit row: status badge + per-entry rationale, if present.
        # Use verified_source_kind as source of truth — agents sometimes set
        # audit_status='OK' even for news-host URLs, but verified_source_kind
        # ("own-site" vs "news-with-rationale") is unambiguous.
        status = p.get('audit_status', '')
        note = p.get('audit_note', '')
        old_url = p.get('audit_old_url', '')
        kind = p.get('verified_source_kind', '')
        if status or kind:
            if kind == 'own-site':
                bg, fg, label = 'rgba(63,185,80,.12)', '#3fb950', '✓ Own party site'
            elif kind == 'news-with-rationale':
                bg, fg, label = 'rgba(210,153,34,.15)', '#d29922', '⚠ News source — see rationale'
            else:
                up = (status or '').upper()
                if up.startswith('REMOVED'):
                    bg, fg, label = 'rgba(248,81,73,.12)', '#f85149', '✗ REMOVED'
                else:
                    bg, fg, label = 'var(--surface2)', 'var(--muted)', e(status or 'unverified')
            old_url_html = ''
            if old_url:
                old_url_html = (
                    '<div style="font-size:11px;color:var(--muted);margin-top:4px">'
                    f'old: <a href="{e(old_url)}" target="_blank" style="color:var(--muted)">{e(old_url)}</a></div>'
                )
            note_html = ''
            if note:
                note_html = f'<div style="color:var(--text);margin-top:4px">{e(note)}</div>'
            audit_html = (
                '<div class="audit-row" style="margin-top:10px;padding:8px 12px;border-radius:6px;'
                f'background:{bg};border:1px solid {bg};color:{fg};font-size:12.5px;line-height:1.5">'
                f'<strong>{label}</strong>{note_html}{old_url_html}'
                '</div>'
            )
        else:
            audit_html = ''

        rows += f'''
    <div class="card">
      <div class="card-header">
        <div class="card-title">{e(p.get("tagline", p["id"]))}</div>
        <div class="card-meta">
          <span class="badge">{e(muni(p["muni_slug"]))}</span>
          <span class="badge secondary">{e(p["party_code"])}</span>
          <a href="{e(p.get("platform_url",""))}" target="_blank" class="source-link">🔗 Source</a>
        </div>
      </div>
      {f'<div class="agenda-grid">{agenda_html}</div>' if agenda_html else ""}
      {audit_html}
    </div>'''
    return rows


def photos_section(photos):
    if photos is None:
        return '''<div class="photos-placeholder" id="photos-area">
    <div class="spinner"></div>
    <div>Photo scan still in progress — this section will be updated when it completes.</div>
  </div>'''
    rows = ''
    for p in photos:
        # photo_local is a root-relative path; photo_url is the remote original
        img_src = p.get('photo_local') or p.get('photo_url') or ''
        photo_img = f'<img src="{e(img_src)}" alt="{e(p["name"])}" class="photo-thumb">' if img_src else ''
        # source field holds the page the photo came from
        source_url = p.get('source') or p.get('photo_source_url') or ''
        source_html = f'<a href="{e(source_url)}" target="_blank" class="source-link">🔗 Source</a>' if source_url else ''
        rows += f'''
    <div class="card photo-card">
      {photo_img}
      <div class="photo-info">
        <div class="card-title">{e(p["name"])}</div>
        <div class="card-meta">
          <span class="badge">{e(muni(p["muni_slug"]))}</span>
          <span class="badge secondary">{e(p.get("party_code",""))}</span>
          <span class="badge tertiary">#{p.get("ballot","?")}</span>
          {source_html}
        </div>
        {f'<div class="agenda-text" style="margin-top:6px">{e(p.get("photo_local",""))}</div>' if p.get("photo_local") else ""}
      </div>
    </div>'''
    return rows or '<p style="color:var(--muted)">No photos found.</p>'


CLEAR_PAGE = """<!DOCTYPE html>
<html lang="is">
<head>
<meta charset="UTF-8">
<title>Scan Review</title>
<style>body{background:#0d1117;color:#8b949e;font-family:sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;}div{text-align:center;}</style>
</head>
<body><div><p style="font-size:48px">✓</p><p>Review approved. No pending scan results.</p></div></body>
</html>"""


def main():
    args = sys.argv[1:]

    if '--clear' in args:
        OUT.write_text(CLEAR_PAGE, encoding='utf-8')
        print(f"Cleared: {OUT}")
        return

    scan_date = date.today().isoformat()
    skip = set()
    for i, a in enumerate(args):
        if a == '--date' and i + 1 < len(args):
            scan_date = args[i + 1]
        if a == '--skip' and i + 1 < len(args):
            skip.add(args[i + 1])

    bios_file    = SCAN_DIR / f"bios_{scan_date}.json"
    news_file    = SCAN_DIR / f"news_{scan_date}.json"
    policy_file  = SCAN_DIR / f"policy_{scan_date}.json"
    photos_file  = SCAN_DIR / f"photos_{scan_date}.json"

    # Combine all news_{date}*.json files (parallel agents may write _A, _B, _C, etc.)
    def merge_news(scan_date):
        results_by_id = {}
        for path in sorted(SCAN_DIR.glob(f"news_{scan_date}*.json")):
            data = load_json(path) or {}
            for r in data.get('results', []) or []:
                key = r.get('id') or f"{r.get('muni_slug')}.{r.get('party_code')}.{r.get('ballot')}"
                if key in results_by_id:
                    seen_urls = {a.get('url') for a in results_by_id[key].get('new_articles', [])}
                    for a in r.get('new_articles', []) or []:
                        if a.get('url') not in seen_urls:
                            results_by_id[key].setdefault('new_articles', []).append(a)
                            seen_urls.add(a.get('url'))
                else:
                    results_by_id[key] = dict(r)
        return list(results_by_id.values())

    # Combine all policy_{date}*.json files
    def merge_simple(scan_date, prefix):
        results_by_id = {}
        for path in sorted(SCAN_DIR.glob(f"{prefix}_{scan_date}*.json")):
            data = load_json(path) or {}
            for r in data.get('results', []) or []:
                # id ("FJA.D") collides between fjardabyggd and fjallabyggd —
                # use the canonical (muni_slug, party_code) key instead.
                key = f"{r.get('muni_slug')}.{r.get('party_code')}"
                results_by_id[key] = dict(r)
        return list(results_by_id.values())

    # Bios merged across parallel-agent slices, keyed by candidate name
    def merge_bios(scan_date):
        results_by_key = {}
        for path in sorted(SCAN_DIR.glob(f"bios_{scan_date}*.json")):
            data = load_json(path) or {}
            for r in data.get('results', []) or []:
                key = r.get('name') or f"{r.get('muni_slug')}.{r.get('party_code')}.{r.get('ballot')}"
                results_by_key[key] = dict(r)
        return list(results_by_key.values())

    # Photos merged across parallel-agent slices, keyed by candidate name + muni
    def merge_photos(scan_date):
        results_by_key = {}
        any_file = False
        for path in sorted(SCAN_DIR.glob(f"photos_{scan_date}*.json")):
            any_file = True
            data = load_json(path) or {}
            for r in data.get('results', []) or []:
                key = f"{r.get('muni_slug','')}.{r.get('name','')}"
                results_by_key[key] = dict(r)
        return list(results_by_key.values()) if any_file else None

    bios_list    = merge_bios(scan_date) if 'bios' not in skip else []
    news_list    = merge_news(scan_date) if 'news' not in skip else []
    policy_list  = merge_simple(scan_date, 'policy') if 'policy' not in skip else []
    photos_list  = merge_photos(scan_date) if 'photos' not in skip else None

    total_articles = sum(len(r.get('new_articles', [])) for r in news_list)
    news_cands = len([r for r in news_list if r.get('new_articles')])
    photo_count = len(photos_list) if photos_list is not None else 0
    photo_status = f'{photo_count} found' if photos_list is not None else 'scan running…'

    css = '''
  :root {
    --bg: #0d1117; --surface: #161b22; --surface2: #21262d;
    --border: #30363d; --text: #e6edf3; --muted: #8b949e;
    --accent: #58a6ff; --green: #3fb950; --yellow: #d29922; --red: #f85149;
    --purple: #bc8cff;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 14px; line-height: 1.6; }
  #lock-screen { position: fixed; inset: 0; background: var(--bg); display: flex; align-items: center; justify-content: center; z-index: 9999; }
  .lock-box { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 40px; text-align: center; width: 340px; }
  .lock-box h2 { margin-bottom: 8px; color: var(--text); font-size: 20px; }
  .lock-box p { color: var(--muted); margin-bottom: 24px; font-size: 13px; }
  .lock-box input { width: 100%; padding: 10px 14px; background: var(--bg); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 14px; margin-bottom: 12px; outline: none; }
  .lock-box input:focus { border-color: var(--accent); }
  .lock-box button { width: 100%; padding: 10px; background: var(--accent); color: #000; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; }
  .lock-box button:hover { opacity: 0.9; }
  .lock-error { color: var(--red); font-size: 12px; margin-top: 8px; display: none; }
  #main { display: none; max-width: 1100px; margin: 0 auto; padding: 40px 20px 80px; }
  .page-header { margin-bottom: 40px; border-bottom: 1px solid var(--border); padding-bottom: 24px; }
  .page-header h1 { font-size: 28px; font-weight: 700; margin-bottom: 8px; }
  .page-header p { color: var(--muted); }
  .stats-row { display: flex; gap: 12px; margin-top: 16px; flex-wrap: wrap; }
  .stat-chip { background: var(--surface2); border: 1px solid var(--border); border-radius: 20px; padding: 4px 14px; font-size: 12px; color: var(--muted); }
  .stat-chip strong { color: var(--text); }
  .scan-note { font-size: 12px; color: var(--muted); background: rgba(210,153,34,.08); border: 1px solid rgba(210,153,34,.2); border-radius: 8px; padding: 10px 14px; margin-top: 14px; }
  .toc { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 14px 20px; margin-bottom: 32px; }
  .toc h3 { font-size: 11px; text-transform: uppercase; letter-spacing: .08em; color: var(--muted); margin-bottom: 8px; }
  .toc a { color: var(--accent); text-decoration: none; font-size: 13px; display: inline-block; margin-right: 20px; }
  .toc a:hover { text-decoration: underline; }
  h2 { font-size: 19px; font-weight: 700; margin: 48px 0 16px; padding-bottom: 10px; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 10px; }
  h2 .section-count { background: var(--surface2); border: 1px solid var(--border); border-radius: 12px; padding: 2px 10px; font-size: 12px; font-weight: 500; color: var(--muted); }
  .card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 18px 20px; margin-bottom: 10px; transition: border-color .15s; }
  .card:hover { border-color: #444d56; }
  .card-header { margin-bottom: 12px; }
  .card-title { font-size: 15px; font-weight: 600; margin-bottom: 6px; }
  .card-meta { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }
  .badge { background: rgba(88,166,255,.12); color: var(--accent); border: 1px solid rgba(88,166,255,.2); border-radius: 12px; padding: 2px 10px; font-size: 11px; font-weight: 500; }
  .badge.secondary { background: rgba(63,185,80,.12); color: var(--green); border-color: rgba(63,185,80,.2); }
  .badge.tertiary { background: rgba(188,140,255,.12); color: var(--purple); border-color: rgba(188,140,255,.2); }
  .tag { background: var(--surface2); border: 1px solid var(--border); border-radius: 10px; padding: 2px 8px; font-size: 11px; color: var(--muted); }
  .tags-row { margin-top: 10px; display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }
  .bio-text { color: var(--text); line-height: 1.75; font-size: 13.5px; }
  .social-link { color: var(--accent); font-size: 11px; text-decoration: none; border: 1px solid rgba(88,166,255,.3); border-radius: 10px; padding: 2px 8px; }
  .sources-row { margin-top: 10px; display: flex; gap: 6px; flex-wrap: wrap; padding-top: 10px; border-top: 1px solid var(--border); }
  .count-badge { background: rgba(210,153,34,.15); color: var(--yellow); border: 1px solid rgba(210,153,34,.25); border-radius: 12px; padding: 2px 10px; font-size: 11px; }
  .articles-list { display: flex; flex-direction: column; gap: 8px; }
  .article-item { display: flex; align-items: flex-start; gap: 10px; padding: 8px 12px; background: var(--surface2); border-radius: 6px; }
  .article-item a { color: var(--accent); text-decoration: none; font-size: 13px; flex: 1; }
  .article-item a:hover { text-decoration: underline; }
  .source-tag { color: var(--muted); font-size: 11px; white-space: nowrap; border: 1px solid var(--border); border-radius: 8px; padding: 1px 7px; }
  .source-link { color: var(--accent); text-decoration: none; font-size: 12px; display: inline-flex; align-items: center; gap: 4px; border: 1px solid rgba(88,166,255,.3); border-radius: 10px; padding: 2px 10px; }
  .source-link:hover { background: rgba(88,166,255,.08); }
  .agenda-grid { display: grid; gap: 7px; }
  .agenda-item { display: flex; gap: 12px; padding: 9px 12px; background: var(--surface2); border-radius: 6px; }
  .agenda-icon { font-size: 18px; line-height: 1.4; flex-shrink: 0; }
  .agenda-text { color: var(--muted); font-size: 12.5px; margin-top: 2px; }
  .photos-placeholder { background: var(--surface); border: 2px dashed var(--border); border-radius: 10px; padding: 48px; text-align: center; color: var(--muted); }
  .spinner { display: inline-block; width: 22px; height: 22px; border: 2px solid var(--border); border-top-color: var(--accent); border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 14px; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .photo-card { display: flex; gap: 16px; align-items: flex-start; }
  .photo-thumb { width: 72px; height: 72px; object-fit: cover; border-radius: 8px; border: 1px solid var(--border); flex-shrink: 0; }
  .photo-info { flex: 1; }
'''

    js = r"""
const PW = 'happyhappy';
function unlock() {
  const v = document.getElementById('pw-input').value;
  if (v === PW) {
    document.getElementById('lock-screen').style.display = 'none';
    document.getElementById('main').style.display = 'block';
  } else {
    document.getElementById('pw-error').style.display = 'block';
    document.getElementById('pw-input').value = '';
  }
}
document.getElementById('pw-input').addEventListener('keydown', function(e) {
  if (e.key === 'Enter') unlock();
});
"""

    photos_html = photos_section(photos_list)
    photo_count_html = photo_status

    page = f"""<!DOCTYPE html>
<html lang="is">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Scan Review — {scan_date}</title>
<style>{css}</style>
</head>
<body>

<div id="lock-screen">
  <div class="lock-box">
    <div style="font-size:36px;margin-bottom:12px">\U0001f512</div>
    <h2>Scan Review</h2>
    <p>{scan_date} &middot; Lýðræðisveislan</p>
    <input type="password" id="pw-input" placeholder="Password">
    <button onclick="unlock()">Enter</button>
    <div class="lock-error" id="pw-error">Incorrect password</div>
  </div>
</div>

<div id="main">
  <div class="page-header">
    <h1>\U0001f5f3️ Scan Review — {scan_date}</h1>
    <p>All results from today’s scanning session, awaiting approval before being applied to the main site.</p>
    <div class="stats-row">
      <div class="stat-chip"><strong>{len(bios_list)}</strong> bios written</div>
      <div class="stat-chip"><strong>{total_articles}</strong> news articles across <strong>{news_cands}</strong> candidates</div>
      <div class="stat-chip"><strong>{len(policy_list)}</strong> party platforms found</div>
      <div class="stat-chip"><strong>{photo_status}</strong> photos</div>
    </div>
    <div class="scan-note">⚠️ Nothing has been applied to the live site yet. Review below, then give approval.</div>
  </div>

  <div class="toc">
    <h3>Jump to section</h3>
    <a href="#bios">\U0001f4dd Bios ({len(bios_list)})</a>
    <a href="#news">\U0001f4f0 News ({total_articles} articles)</a>
    <a href="#policy">\U0001f4cb Policy ({len(policy_list)})</a>
    <a href="#photos">\U0001f4f7 Photos</a>
  </div>

  <h2 id="bios">\U0001f4dd Biographies <span class="section-count">{len(bios_list)}</span></h2>
  {bio_section(bios_list)}

  <h2 id="news">\U0001f4f0 News Articles <span class="section-count">{total_articles} articles &middot; {news_cands} candidates</span></h2>
  {news_section(news_list)}

  <h2 id="policy">\U0001f4cb Party Platforms <span class="section-count">{len(policy_list)}</span></h2>
  {policy_section(policy_list)}

  <h2 id="photos">\U0001f4f7 Photos <span class="section-count">{photo_count_html}</span></h2>
  {photos_html}

</div>

<script>{js}</script>
</body>
</html>"""

    OUT.write_text(page, encoding='utf-8')
    print(f"Written: {OUT}")
    print(f"  Bios: {len(bios_list)}")
    print(f"  News: {total_articles} articles / {news_cands} candidates")
    print(f"  Policy: {len(policy_list)}")
    print(f"  Photos: {photo_status}")


if __name__ == '__main__':
    main()
