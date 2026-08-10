"""Fetch every answering candidate's full profile from Kosningapróf and
save into a single compact JSON.

Reads the slug list from temp/ruv_candidates.json (output of
scripts/ruv_kosningaprof_collect.py), discovers the current Next.js
buildId from the live site, then pulls
  /_next/data/{buildId}/frambjodandi/{slug}.json
for each candidate.

Output: temp/ruv_answers.json
  {
    "discoveredAt": "...",
    "buildId":      "...",
    "questions":    { id: { title, type, slug, applicableConstituencies } },
    "candidates":   [
      { id, slug, fullName, image, motivateVote, partyCode, partyName,
        partySlug, partyListPosition, constituencyId, constituencyName,
        backgroundQuestion, answers: [
          { qid, value, stringValue, important, reasoning }
        ] }
    ]
  }

Question text/objects are pulled into a top-level `questions` dict so they
don't repeat per-candidate (saves ~2/3 of the file size).
"""
from __future__ import annotations
import json, sys, io, re, time, urllib.request, urllib.error
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

UA = {'User-Agent': 'Mozilla/5.0'}
ROOT = 'https://kosningaprof.ruv.is'

CAND_INDEX = Path('temp/ruv_candidates.json')
OUT = Path('temp/ruv_answers.json')

def fetch(url, retries=2):
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=25) as r:
                return r.read()
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            if attempt >= retries:
                raise
            time.sleep(0.6 * (attempt + 1))

# 1) buildId
home = fetch(ROOT + '/').decode('utf-8', errors='replace')
build_id = re.search(r'"buildId":"([^"]+)"', home).group(1)
print(f'buildId: {build_id}')

# 2) Load slug list
src = json.loads(CAND_INDEX.read_text(encoding='utf-8'))
slugs = src['candidates']
print(f'candidates to fetch: {len(slugs)}')

questions = {}     # qid → question metadata
out_candidates = []
fail = 0
t0 = time.time()

for i, c in enumerate(slugs, 1):
    slug = c['slug']
    url  = f'{ROOT}/_next/data/{build_id}/frambjodandi/{slug}.json'
    try:
        data = json.loads(fetch(url))
    except Exception as e:
        fail += 1
        print(f'  [{i:>4}/{len(slugs)}] {slug}: ERR {e}')
        continue
    pp = data.get('pageProps', {})
    cand = pp.get('candidate') or {}
    answers = []
    for a in cand.get('answers') or []:
        q = a.get('question') or {}
        qid = q.get('id')
        if qid and qid not in questions:
            questions[qid] = {
                'id':                       q.get('id'),
                'slug':                     q.get('slug'),
                'title':                    q.get('title'),
                'description':              q.get('description'),
                'type':                     q.get('type'),
                'applicableConstituencies': q.get('applicableConstituencies'),
            }
        answers.append({
            'qid':         a.get('questionId'),
            'value':       a.get('value'),
            'stringValue': a.get('stringValue'),
            'important':   a.get('important'),
            'reasoning':   a.get('reasoning'),
        })
    out_candidates.append({
        'id':                cand.get('id'),
        'slug':              slug,
        'fullName':          cand.get('fullName'),
        'image':             cand.get('image'),
        'motivateVote':      cand.get('motivateVote'),
        'partyCode':         cand.get('partyCode'),
        'partyName':         (cand.get('party') or {}).get('name'),
        'partySlug':         (cand.get('party') or {}).get('slug'),
        'partyListPosition': cand.get('partyListPosition'),
        'constituencyId':    (cand.get('constituency') or {}).get('id'),
        'constituencyName':  (cand.get('constituency') or {}).get('name'),
        'backgroundQuestion': cand.get('backgroundQuestion'),
        'answers':           answers,
        'profile_url':       f'{ROOT}/frambjodandi/{slug}/',
    })
    if i % 50 == 0 or i == len(slugs):
        rate = i / max(0.001, time.time() - t0)
        eta  = (len(slugs) - i) / max(0.001, rate)
        print(f'  [{i:>4}/{len(slugs)}] {rate:.1f} req/s  ETA {eta:5.0f}s')
    time.sleep(0.05)

print(f'\nDone. {len(out_candidates)} candidates, {fail} failures, {len(questions)} unique questions.')
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({
    'discoveredAt':   time.strftime('%Y-%m-%d %H:%M:%S'),
    'buildId':        build_id,
    'totalCandidates': len(out_candidates),
    'failedFetches':  fail,
    'questions':      questions,
    'candidates':     out_candidates,
}, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'  → {OUT}')
print(f'  size: {OUT.stat().st_size / 1024 / 1024:.1f} MB')
