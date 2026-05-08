"""Fetch RÚV kosningapróf party-level results (one JSON per party in
each municipality), split into per-party files, and emit:

  temp/ruv_party_results/<party-slug>.json   — full per-party record
  temp/ruv_party_results_summary.json        — flat list, one row per
                                                (party, question)
  temp/ruv_questions.json                    — question id → metadata

Source: https://kosningaprof.ruv.is/_next/data/<buildId>/kjordaemi.json
The buildId rotates when RÚV redeploys, so we resolve it from the
landing page on every run.
"""
from __future__ import annotations
import json, re, sys, io, urllib.request
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).parent.parent
OUT_DIR = ROOT / 'temp' / 'ruv_party_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)

UA = 'Mozilla/5.0 (compatible; lydraedisveislan-scraper)'

def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

# 1. Resolve buildId by scraping the landing page
landing = fetch('https://kosningaprof.ruv.is/').decode('utf-8')
m = re.search(r'"buildId":"([^"]+)"', landing)
if not m:
    print('ERROR: could not find buildId in landing page', file=sys.stderr)
    sys.exit(1)
build_id = m.group(1)
print(f'buildId: {build_id}')

# 2. Fetch the kjordaemi snapshot (all parties)
url = f'https://kosningaprof.ruv.is/_next/data/{build_id}/kjordaemi.json'
print(f'GET {url}')
raw = fetch(url)
(ROOT / 'temp' / 'ruv_kjordaemi.json').write_bytes(raw)
data = json.loads(raw)
parties = data['pageProps']['parties']
print(f'Loaded {len(parties)} parties')

# 3. Split per-party files + build summary + questions
questions: dict[str, dict] = {}
summary_rows: list[dict] = []

for p in parties:
    slug = p['slug']
    (OUT_DIR / f'{slug}.json').write_text(
        json.dumps(p, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
    for ans in p.get('answers', []) or []:
        q = ans.get('question') or {}
        qid = ans.get('questionId') or q.get('id')
        if qid and qid not in questions:
            questions[qid] = {
                'id': qid,
                'type': ans.get('questionType') or q.get('type'),
                'slug': q.get('slug'),
                'title': q.get('title'),
                'description': q.get('description'),
            }
        summary_rows.append({
            'party_slug': slug,
            'party_name': p.get('name'),
            'party_color': p.get('color'),
            'party_abbrev': p.get('abbreviation'),
            'question_id': qid,
            'question_type': ans.get('questionType'),
            'question_title': q.get('title'),
            'value': ans.get('value'),
            'string_value': ans.get('stringValue'),
            'important': ans.get('important'),
            'reasoning': ans.get('reasoning'),
        })

(ROOT / 'temp' / 'ruv_party_results_summary.json').write_text(
    json.dumps(summary_rows, ensure_ascii=False, indent=2),
    encoding='utf-8',
)
(ROOT / 'temp' / 'ruv_questions.json').write_text(
    json.dumps(questions, ensure_ascii=False, indent=2),
    encoding='utf-8',
)

print(f'Wrote {len(parties)} per-party JSON files → {OUT_DIR}')
print(f'Wrote {len(summary_rows):,} summary rows → temp/ruv_party_results_summary.json')
print(f'Wrote {len(questions)} unique questions → temp/ruv_questions.json')
