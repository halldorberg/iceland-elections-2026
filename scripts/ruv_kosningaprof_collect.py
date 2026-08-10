"""Crawl every candidate profile that answered RÚV's Kosningapróf 2026.

Path:
  1. /_next/data/{buildId}/kjordaemi.json  → list of all 182 parties
  2. for each party:  /_next/data/{buildId}/flokkar/{slug}.json
     → partyCandidates: [{ slug, fullName, partyListPosition, constituency }]
  3. emit a single JSON of every candidate that *has* a profile, plus the
     `https://kosningaprof.ruv.is/frambjodandi/{slug}/` URL.

Usage:
  python scripts/ruv_kosningaprof_collect.py [--out=temp/ruv_candidates.json]

Auto-discovers the current Next.js buildId from the live site, so no manual
update is needed when RÚV redeploys.
"""
from __future__ import annotations
import argparse, json, sys, io, re, time, urllib.request
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

UA = {'User-Agent': 'Mozilla/5.0'}
ROOT = 'https://kosningaprof.ruv.is'

ap = argparse.ArgumentParser()
ap.add_argument('--out', default='temp/ruv_candidates.json')
args = ap.parse_args()
out_path = Path(args.out); out_path.parent.mkdir(parents=True, exist_ok=True)

def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()

print('1) Discover buildId from homepage…')
home = fetch(ROOT + '/').decode('utf-8', errors='replace')
m = re.search(r'"buildId":"([^"]+)"', home)
build_id = m.group(1)
print(f'   buildId: {build_id}')

print('2) Pull party list from /kjordaemi.json…')
data = json.loads(fetch(f'{ROOT}/_next/data/{build_id}/kjordaemi.json'))
parties = data['pageProps']['parties']
print(f'   parties: {len(parties)}')

candidates = []
party_index = []
for i, p in enumerate(parties, 1):
    slug = p['slug']
    party_url = f'{ROOT}/_next/data/{build_id}/flokkar/{slug}.json'
    try:
        pdata = json.loads(fetch(party_url))
    except Exception as e:
        print(f'   [{i:>3}/{len(parties)}] {slug} ERR {e}')
        continue
    pc = pdata['pageProps'].get('partyCandidates') or []
    party_index.append({
        'slug':         slug,
        'name':         p.get('name'),
        'abbreviation': p.get('abbreviation'),
        'color':        p.get('color'),
        'candidate_count': len(pc),
        'flokkar_url':  f'{ROOT}/flokkar/{slug}/',
    })
    for c in pc:
        candidates.append({
            'slug':              c['slug'],
            'fullName':          c.get('fullName'),
            'partyListPosition': c.get('partyListPosition'),
            'partySlug':         slug,
            'partyName':         p.get('name'),
            'partyAbbreviation': p.get('abbreviation'),
            'constituencyId':    (c.get('constituency') or {}).get('id'),
            'constituencyName':  (c.get('constituency') or {}).get('name'),
            'profile_url':       f'{ROOT}/frambjodandi/{c["slug"]}/',
        })
    print(f'   [{i:>3}/{len(parties)}] {slug}: {len(pc)} cand')
    time.sleep(0.05)

print(f'\nTotal candidates with Kosningapróf profile: {len(candidates)}')
out_path.write_text(json.dumps({
    'discoveredAt': time.strftime('%Y-%m-%d %H:%M:%S'),
    'buildId':      build_id,
    'totalParties': len(parties),
    'totalCandidates': len(candidates),
    'parties':      party_index,
    'candidates':   candidates,
}, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'  → {out_path}')
