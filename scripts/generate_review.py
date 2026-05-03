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


def _audit_html(audit: dict | None) -> str:
    """Render per-bio audit panel from parsed audit JSON entry."""
    if not audit or not audit.get('statements'):
        return ''
    s = audit.get('stats') or {}
    badges = (
        f'<span class="audit-badge ok">{s.get("verified",0)} ✅</span>'
        f'<span class="audit-badge flag">{s.get("flagged",0)} 🚩</span>'
        f'<span class="audit-badge unr">{s.get("unreachable",0)} ⚠️</span>'
    )
    rows = ''
    for st in audit['statements']:
        status_cls = st['status']  # 'verified' | 'rescued' | 'flagged' | 'unreachable'
        symbols = {
            'verified':    '✅',
            'rescued':     '✅ RESCUED',
            'flagged':     '🚩FLAG-UNSOURCED',
            'unreachable': '⚠️ SOURCE-UNREACHABLE',
        }
        symbol = symbols.get(status_cls, '· ' + status_cls)
        # 'rescued' renders like 'verified' (green) but with the RESCUED label
        if status_cls == 'rescued':
            status_cls = 'verified'
        quotes_html = ''
        for q in st.get('quotes', []) or []:
            quotes_html += f'<div class="audit-quote">› {e(q)}</div>'
        notes_html = f'<div class="audit-notes">{e(st["notes"])}</div>' if st.get('notes') else ''
        rewrite_html = ''
        if st.get('rewrite'):
            rewrite_html = f'<div class="audit-rewrite"><strong>Rewrite:</strong> {e(st["rewrite"])}</div>'
        rows += (
            f'<div class="audit-stmt {status_cls}">'
            f'<div class="audit-claim">{st["n"]}. {symbol} <em>"{e(st["claim"])}"</em></div>'
            f'{quotes_html}{notes_html}{rewrite_html}</div>'
        )
    rescue_html = ''
    rescue = audit.get('rescue')
    cid = audit.get('_cid', '')  # injected by caller
    if rescue and rescue.get('rewrite'):
        new_src_html = ''
        if rescue.get('new_sources'):
            new_src_html = '<div class="rescue-meta"><strong>New sources used in rescue:</strong><ul>' + ''.join(
                f'<li>{e(s)}</li>' for s in rescue['new_sources']
            ) + '</ul></div>'
        res_html = ''
        if rescue.get('resolutions'):
            def _res_li(r):
                if isinstance(r, dict):
                    return f'<li class="rescue-{r.get("kind","other")}">{e(r.get("text",""))}</li>'
                return f'<li>{e(str(r))}</li>'
            res_html = '<div class="rescue-meta"><strong>Per-claim resolution:</strong><ul>' + ''.join(
                _res_li(r) for r in rescue['resolutions']
            ) + '</ul></div>'
        applied_class = ' applied' if audit.get('applied') else ''
        applied_label = ' <span class="applied-tag">✅ APPLIED</span>' if audit.get('applied') else ''
        rescue_html = (
            f'<div class="rescue-block{applied_class}" data-cid="{e(cid)}">'
            f'<div class="rescue-label">📝 PROPOSED REWRITE'
            f' <span class="rescue-wc">({rescue.get("rewrite_words", "?")} orð)</span>'
            f'{applied_label}</div>'
            f'<div class="rescue-text">{e(rescue["rewrite"])}</div>'
            f'{new_src_html}{res_html}'
            '</div>'
        )
    return (
        '<details class="audit-panel" open><summary>'
        '<strong>🔍 Source audit</strong> ' + badges + '</summary>'
        + rows + rescue_html + '</details>'
    )


def bio_section(bios, audit_data=None):
    if not bios:
        return '<p style="color:var(--muted)">No bio results file found.</p>'
    audit_data = audit_data or {}
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

        cid = b.get('id', '')
        audit_entry = audit_data.get(cid)
        if audit_entry is not None:
            audit_entry = dict(audit_entry, _cid=cid)
        audit_panel = _audit_html(audit_entry)

        # Per-bio approve row — checkbox label & semantics depend on whether a
        # rewrite exists for this candidate.
        has_bio = bool(b.get('bio'))
        has_rewrite = bool(audit_entry and audit_entry.get('rescue', {}).get('rewrite'))
        is_applied = bool(audit_entry and audit_entry.get('applied'))
        if has_rewrite:
            approve_label = 'Approve rewrite (replaces current bio + heimild)'
            approve_kind = 'rewrite'
        elif has_bio:
            approve_label = 'Approve bio as-is (no changes needed)'
            approve_kind = 'as-is'
        else:
            approve_label = 'Approve skip (leave bio empty)'
            approve_kind = 'skip'
        applied_attr = ' disabled' if is_applied else ''
        applied_extra = ' <span class="applied-tag">✅ APPLIED</span>' if is_applied else ''
        approve_row = (
            f'<div class="approve-row" data-cid="{e(cid)}" data-kind="{approve_kind}">'
            f'<label class="approve-label">'
            f'<input type="checkbox" class="approve-cb" data-cid="{e(cid)}" data-kind="{approve_kind}"{applied_attr}>'
            f' {e(approve_label)}'
            f'</label>'
            f'{applied_extra}'
            f'</div>'
        )

        rows += f'''
    <div class="card" data-cid="{e(cid)}">
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
      {audit_panel}
      {approve_row}
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

    # Default scan_date: today, but fall back to the most recent date for which any
    # scan_results/{type}_YYYY-MM-DD*.json file exists (so an overnight scan
    # doesn't disappear the moment the calendar rolls over).
    scan_date = date.today().isoformat()
    explicit_date = False
    skip = set()
    for i, a in enumerate(args):
        if a == '--date' and i + 1 < len(args):
            scan_date = args[i + 1]
            explicit_date = True
        if a == '--skip' and i + 1 < len(args):
            skip.add(args[i + 1])

    if not explicit_date:
        import re as _re
        date_set = set()
        for p in SCAN_DIR.glob('*_2*.json'):
            m = _re.search(r'_(\d{4}-\d{2}-\d{2})', p.name)
            if m:
                date_set.add(m.group(1))
        if date_set and scan_date not in date_set:
            scan_date = max(date_set)
            print(f"  (no scan files for today; falling back to most recent: {scan_date})")

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

    # Optional per-bio source audit data, keyed by candidate id
    audit_data = load_json(SCAN_DIR / "audit_results.json") or {}

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
  .audit-panel { margin-top: 14px; padding: 10px 14px; background: rgba(0,0,0,.18); border: 1px solid var(--border); border-radius: 8px; }
  .audit-panel summary { cursor: pointer; padding: 4px 0; font-size: 12px; color: var(--muted); display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
  .audit-panel summary strong { color: var(--text); font-size: 13px; }
  .audit-panel[open] summary { margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px solid var(--border); }
  .audit-badge { font-size: 11px; padding: 2px 9px; border-radius: 10px; }
  .audit-badge.ok { background: rgba(63,185,80,.13); color: var(--green); }
  .audit-badge.flag { background: rgba(248,81,73,.13); color: var(--red); }
  .audit-badge.unr { background: rgba(210,153,34,.13); color: var(--yellow); }
  .audit-stmt { padding: 8px 10px; margin-bottom: 6px; border-radius: 6px; font-size: 12.5px; line-height: 1.55; border-left: 3px solid var(--border); }
  .audit-stmt.verified    { border-left-color: var(--green);  background: rgba(63,185,80,.04); }
  .audit-stmt.flagged     { border-left-color: var(--red);    background: rgba(248,81,73,.05); }
  .audit-stmt.unreachable { border-left-color: var(--yellow); background: rgba(210,153,34,.05); }
  .audit-claim { color: var(--text); margin-bottom: 4px; }
  .audit-claim em { color: var(--muted); font-style: italic; }
  .audit-quote { color: var(--muted); font-size: 11.5px; padding: 2px 0 2px 16px; border-left: 2px solid var(--border); margin-left: 2px; font-style: italic; }
  .audit-notes { color: var(--muted); font-size: 11.5px; margin-top: 4px; }
  .audit-rewrite { margin-top: 6px; padding: 5px 8px; background: rgba(88,166,255,.07); border-left: 2px solid var(--accent); font-size: 11.5px; color: var(--text); }
  .audit-rewrite strong { color: var(--accent); }
  .rescue-block { margin-top: 14px; padding: 14px 16px; background: rgba(88,166,255,.08); border: 1px solid rgba(88,166,255,.22); border-radius: 8px; }
  .rescue-label { font-size: 11px; font-weight: 700; color: var(--accent); letter-spacing: .07em; margin-bottom: 8px; }
  .rescue-wc { color: var(--muted); font-weight: 400; letter-spacing: 0; }
  .rescue-text { color: var(--text); font-size: 13.5px; line-height: 1.7; padding: 8px 12px; background: var(--bg); border-radius: 6px; border-left: 3px solid var(--accent); }
  .rescue-meta { margin-top: 10px; font-size: 11.5px; color: var(--muted); }
  .rescue-meta ul { margin: 4px 0 0 16px; padding: 0; }
  .rescue-meta li { margin: 2px 0; }
  .rescue-meta li.rescue-rescued { color: var(--green); }
  .rescue-meta li.rescue-dropped { color: var(--red); }
  .rescue-meta li.rescue-contradicted { color: var(--yellow); }
  .approve-row { margin-top: 14px; padding-top: 12px; border-top: 1px dashed var(--border); display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
  .approve-label { display: inline-flex; align-items: center; gap: 8px; padding: 6px 12px; background: var(--surface2); border: 1px solid var(--border); border-radius: 6px; font-size: 12px; cursor: pointer; user-select: none; }
  .approve-label:hover { border-color: var(--green); }
  .approve-cb { width: 16px; height: 16px; cursor: pointer; accent-color: var(--green); }
  .approve-row[data-kind="rewrite"] .approve-label { background: rgba(88,166,255,.12); border-color: rgba(88,166,255,.35); color: var(--accent); }
  .approve-row[data-kind="skip"] .approve-label { background: rgba(210,153,34,.10); border-color: rgba(210,153,34,.30); color: var(--yellow); }
  .card.is-approved { border-color: var(--green); box-shadow: 0 0 0 1px var(--green) inset; }
  .card.is-approved .approve-label { background: rgba(63,185,80,.18); border-color: var(--green); color: var(--green); font-weight: 600; }
  .rescue-block.is-approved { border-color: var(--green); background: rgba(63,185,80,.07); }
  .rescue-block.applied { opacity: 0.65; }
  .applied-tag { background: rgba(63,185,80,.18); color: var(--green); border: 1px solid var(--green); border-radius: 10px; padding: 2px 8px; font-size: 10px; font-weight: 700; letter-spacing: .05em; margin-left: 8px; }
  /* Floating approval counter */
  #approve-counter { position: fixed; top: 20px; right: 20px; z-index: 9999; background: var(--surface); border: 1px solid var(--green); border-radius: 10px; padding: 10px 16px; font-size: 13px; color: var(--text); cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,.4); transition: transform .15s; }
  #approve-counter:hover { transform: translateY(-1px); border-color: var(--green); }
  #approve-counter strong { color: var(--green); font-size: 16px; margin-right: 4px; }
  #approve-panel { position: fixed; top: 70px; right: 20px; z-index: 9999; background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 16px; width: 380px; max-height: 70vh; overflow-y: auto; display: none; box-shadow: 0 8px 24px rgba(0,0,0,.5); }
  /* Mobile: move counter to bottom-right (above virtual keyboard, easier thumb reach, away from browser chrome) */
  @media (max-width: 768px) {
    #approve-counter { top: auto; bottom: 16px; right: 12px; padding: 12px 18px; font-size: 14px; border-radius: 24px; box-shadow: 0 6px 16px rgba(0,0,0,.6); }
    #approve-counter strong { font-size: 18px; }
    #approve-panel { top: auto; bottom: 76px; right: 12px; left: 12px; width: auto; max-height: 60vh; }
  }
  #approve-panel.open { display: block; }
  #approve-panel h3 { font-size: 13px; font-weight: 700; margin-bottom: 10px; color: var(--text); }
  #approve-panel button { display: block; width: 100%; padding: 8px 12px; margin-bottom: 8px; background: var(--surface2); color: var(--text); border: 1px solid var(--border); border-radius: 6px; font-size: 12px; cursor: pointer; text-align: left; }
  #approve-panel button:hover { border-color: var(--accent); }
  #approve-panel button.danger:hover { border-color: var(--red); color: var(--red); }
  #approve-panel .id-list { background: var(--bg); border: 1px solid var(--border); border-radius: 6px; padding: 8px; font-family: monospace; font-size: 11px; word-break: break-all; max-height: 180px; overflow-y: auto; color: var(--muted); margin-top: 8px; }
  #approve-toast { position: fixed; top: 80px; right: 20px; z-index: 200; background: var(--green); color: #000; padding: 10px 16px; border-radius: 6px; font-size: 13px; font-weight: 600; opacity: 0; transition: opacity .25s; pointer-events: none; }
  #approve-toast.show { opacity: 1; }
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

// Approval UI
const APPROVE_KEY_PREFIX = 'approve:';
function listApproved() {
  const out = [];
  for (let i = 0; i < localStorage.length; i++) {
    const k = localStorage.key(i);
    if (k && k.startsWith(APPROVE_KEY_PREFIX) && localStorage.getItem(k) === '1') {
      out.push(k.slice(APPROVE_KEY_PREFIX.length));
    }
  }
  out.sort();
  return out;
}
function showToast(msg) {
  const t = document.getElementById('approve-toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2000);
}
function refreshCounter() {
  const ids = listApproved();
  const c = document.getElementById('approve-counter');
  if (c) c.innerHTML = '<strong>' + ids.length + '</strong> approved';
  const list = document.getElementById('approve-id-list');
  if (list) list.textContent = ids.length ? ids.join(', ') : '(none yet)';
  // Breakdown by kind
  let rw = 0, asis = 0, skip = 0;
  ids.forEach(id => {
    const k = localStorage.getItem(APPROVE_KEY_PREFIX + id + ':kind') || 'as-is';
    if (k === 'rewrite') rw++;
    else if (k === 'skip') skip++;
    else asis++;
  });
  const bd = document.getElementById('approve-breakdown');
  if (bd) bd.innerHTML = '<span style="color:var(--accent)">' + rw + ' rewrite</span> · '
    + '<span style="color:var(--green)">' + asis + ' as-is</span> · '
    + '<span style="color:var(--yellow)">' + skip + ' skip</span>';
}
function _markApproved(cid, on) {
  const card = document.querySelector('.card[data-cid="' + cid + '"]');
  if (card) card.classList.toggle('is-approved', on);
  const blk = document.querySelector('.rescue-block[data-cid="' + cid + '"]');
  if (blk) blk.classList.toggle('is-approved', on);
}
function applyStateToCheckboxes() {
  document.querySelectorAll('.approve-cb').forEach(cb => {
    const cid = cb.dataset.cid;
    if (localStorage.getItem(APPROVE_KEY_PREFIX + cid) === '1') {
      cb.checked = true;
      _markApproved(cid, true);
    }
  });
}
function onApproveChange(ev) {
  if (!ev.target.classList.contains('approve-cb')) return;
  const cid = ev.target.dataset.cid;
  if (ev.target.checked) {
    const kind = ev.target.dataset.kind || 'as-is';
    localStorage.setItem(APPROVE_KEY_PREFIX + cid, '1');
    localStorage.setItem(APPROVE_KEY_PREFIX + cid + ':kind', kind);
    _markApproved(cid, true);
  } else {
    localStorage.removeItem(APPROVE_KEY_PREFIX + cid);
    localStorage.removeItem(APPROVE_KEY_PREFIX + cid + ':kind');
    _markApproved(cid, false);
  }
  refreshCounter();
}
function copyApproved() {
  const ids = listApproved();
  if (!ids.length) { showToast('Nothing approved yet'); return; }
  const txt = ids.join(', ');
  navigator.clipboard.writeText(txt).then(() => showToast('Copied ' + ids.length + ' IDs to clipboard'));
}
function downloadApproved() {
  const ids = listApproved();
  const detailed = ids.map(id => ({
    id, kind: localStorage.getItem(APPROVE_KEY_PREFIX + id + ':kind') || 'as-is'
  }));
  const blob = new Blob([JSON.stringify({approved: detailed, ts: new Date().toISOString()}, null, 2)], {type: 'application/json'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'approvals.json'; a.click();
  URL.revokeObjectURL(url);
  showToast('Downloaded approvals.json');
}
function clearApprovals() {
  const ids = listApproved();
  if (!ids.length) { showToast('Nothing to clear'); return; }
  if (!confirm('Clear all ' + ids.length + ' approvals? This only affects the UI; applied rewrites stay applied.')) return;
  ids.forEach(id => localStorage.removeItem(APPROVE_KEY_PREFIX + id));
  document.querySelectorAll('.approve-cb').forEach(cb => { cb.checked = false; });
  document.querySelectorAll('.rescue-block.is-approved').forEach(b => b.classList.remove('is-approved'));
  refreshCounter();
  showToast('Cleared');
}
function togglePanel() {
  document.getElementById('approve-panel').classList.toggle('open');
}
document.addEventListener('change', onApproveChange);
window.addEventListener('load', () => {
  applyStateToCheckboxes();
  refreshCounter();
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

<div id="approve-counter" onclick="togglePanel()"><strong>0</strong> approved</div>
<div id="approve-panel">
  <h3>Approval actions</h3>
  <div id="approve-breakdown" style="font-size:11px;margin-bottom:10px"></div>
  <button onclick="copyApproved()">📋 Copy IDs to clipboard</button>
  <button onclick="downloadApproved()">📥 Download approvals.json</button>
  <button class="danger" onclick="clearApprovals()">🗑 Clear all approvals</button>
  <div style="font-size:11px;color:var(--muted);margin-top:8px">Approved candidate IDs (also stored in your browser):</div>
  <div id="approve-id-list" class="id-list">(none yet)</div>
</div>
<div id="approve-toast"></div>

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
  {('<div class="scan-note">🔍 Source-audit pilot live for ' + str(len(audit_data)) + ' bios. Look for the green/red/yellow audit panels under each bio (Ctrl-F <strong>FLAG-UNSOURCED</strong> to jump between flagged claims). Seven bios also have a <strong>📝 PROPOSED REWRITE</strong> block — strict source-grounded replacement after the rescue pass. Audited candidates: ' + ', '.join(sorted(audit_data.keys())) + '.</div>') if audit_data else ''}
  {bio_section(bios_list, audit_data)}

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
