"""Build js/data/ruv_positions.js from RÚV kosningapróf API.

This script intentionally uses the **party-submitted** answer for each
question — the single A/B/C/D the party officially filled in — and NOT
an aggregate across candidate answers. That matches what RÚV itself
displays on its party pages (and per-question summary): a candidate
distribution can disagree with the official party position.

Output per muni:
  - questions:  { qid: { title, slug, importance: { partyCode: count } } }
  - parties:    { partyCode: { qid: { value, mean, n: 1, std: 0 } } }

`value` is the literal A/B/C/D the party answered. `mean` is the
numeric Likert equivalent (A=1, B=2, C=3, D=4). `n` is always 1 and
`std` is always 0 since it's a single official answer — these fields
are kept for backward compatibility with municipality.js scoreCoalition.

`importance` is aggregated from candidate-level answers (the only place
RÚV exposes the "important" flag) and indicates how many of a party's
candidates flagged the proposition as decisive for them.

Currently only Reykjavík is exported — extend the CONSTITUENCIES dict
when other munis pick up the strip.

Usage:
  python scripts/build_ruv_positions.py
"""
from __future__ import annotations
import json, sys, io, re, urllib.request
from collections import defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(__file__).resolve().parent.parent

# muni_id (matches MUNICIPALITIES[].id in JS) → RÚV constituencyId
CONSTITUENCIES = {
    'reykjavik': '0000',
}
# Party-page slugs on RÚV per (muni_id, party_code).
PARTY_SLUGS = {
    'reykjavik': {
        'A': 'reykjavik-vinstrid',
        'B': 'reykjavik-framsoknarflokkur',
        'C': 'reykjavik-vidreisn',
        'D': 'reykjavik-sjalfstaedisflokkur',
        'F': 'reykjavik-flokkur-folksins',
        'G': 'reykjavik-godan-daginn',
        'J': 'reykjavik-sosialistaflokkur-islands',
        'M': 'reykjavik-midflokkur',
        'P': 'reykjavik-piratar',
        'R': 'reykjavik-okkar-borg',
        'S': 'reykjavik-samfylkingin-jafnadarflokkur-islands',
    },
}

# Likert mapping
LETTER_TO_NUM = {'A': 1, 'B': 2, 'C': 3, 'D': 4}
UA = {'User-Agent': 'Mozilla/5.0'}
ROOT_URL = 'https://kosningaprof.ruv.is'

def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()

# Discover current buildId from the live site
print('Discovering buildId …')
home = fetch(ROOT_URL + '/').decode('utf-8', errors='replace')
build_id = re.search(r'"buildId":"([^"]+)"', home).group(1)
print(f'  buildId: {build_id}')

# Candidate-level data still needed for the "important" counts and the
# question catalogue. Use the existing dump if present, else fetch fresh.
candidate_src = ROOT / 'temp' / 'ruv_answers.json'
print(f'Reading candidate data from {candidate_src} …')
data = json.loads(candidate_src.read_text(encoding='utf-8'))
all_questions = data['questions']
all_candidates = data['candidates']

result_by_muni = {}

for muni_id, constituency_id in CONSTITUENCIES.items():
    cands = [c for c in all_candidates if c.get('constituencyId') == constituency_id]

    # Questions applicable to this constituency — propositions only
    applicable_qids = set()
    for qid, q in all_questions.items():
        if q.get('type') != 'PROPOSITION':
            continue
        ac = q.get('applicableConstituencies')
        if ac is None or constituency_id in ac:
            applicable_qids.add(qid)

    # Importance counts from candidate answers
    importance = defaultdict(lambda: defaultdict(int))  # qid → party → count
    for c in cands:
        pcode = c.get('partyCode')
        if not pcode:
            continue
        for ans in c.get('answers') or []:
            qid = ans.get('qid')
            if qid in applicable_qids and ans.get('important'):
                importance[qid][pcode] += 1

    # Pull each party's official answers
    parties_out = {}
    party_slugs = PARTY_SLUGS.get(muni_id, {})
    for pcode, pslug in party_slugs.items():
        url = f'{ROOT_URL}/_next/data/{build_id}/flokkar/{pslug}.json'
        try:
            pdata = json.loads(fetch(url))
        except Exception as e:
            print(f'  [{muni_id}/{pcode}] ERR {e}')
            continue
        party_answers = pdata['pageProps']['party'].get('answers') or []
        by_qid = {}
        for a in party_answers:
            qid = a.get('questionId')
            if qid not in applicable_qids:
                continue
            v = a.get('value')
            num = LETTER_TO_NUM.get(v)
            if num is None:
                continue
            by_qid[qid] = {'value': v, 'mean': float(num), 'n': 1, 'std': 0.0}
        parties_out[pcode] = by_qid
        print(f'  [{muni_id}/{pcode}] {pslug}: {len(by_qid)} answers')

    # Question metadata — only include questions any party answered
    seen_qids = {qid for by_q in parties_out.values() for qid in by_q}
    questions_out = {}
    for qid in sorted(seen_qids, key=int):
        q = all_questions[qid]
        questions_out[qid] = {
            'title': q.get('title', ''),
            'slug': q.get('slug', ''),
            'importance': dict(importance[qid]),
        }

    result_by_muni[muni_id] = {
        'questions': questions_out,
        'parties': parties_out,
    }
    print(f'  [{muni_id}] {len(questions_out)} questions, {len(parties_out)} parties '
          f'→ {sum(len(v) for v in parties_out.values())} (party,qid) entries')

# Emit JS module
out = ROOT / 'js' / 'data' / 'ruv_positions.js'
out.parent.mkdir(parents=True, exist_ok=True)
body = (
    '// Auto-generated by scripts/build_ruv_positions.py.\n'
    '// DO NOT EDIT BY HAND — re-run the script and commit the regenerated file.\n'
    '//\n'
    '// Per-muni RÚV kosningapróf 2026 stances. Uses the **party-submitted**\n'
    '// answer for each question (the official A/B/C/D the party filled in),\n'
    '// NOT an aggregate across candidate answers — same convention as RÚV\'s\n'
    '// own party pages. Likert scale: A=1 (mjög ósammála) → D=4 (mjög sammála).\n'
    '//\n'
    '//   questions[qid] = { title, slug, importance: { partyCode: candidateCount } }\n'
    '//   parties[code][qid] = { value, mean, n: 1, std: 0 }\n'
    '//\n'
    '// `mean` is just LETTER_TO_NUM[value]; the n/std fields are kept for\n'
    '// backward compatibility with municipality.js scoreCoalition.\n'
    'export const RUV_POSITIONS = '
    + json.dumps(result_by_muni, ensure_ascii=False, indent=2)
    + ';\n'
)
out.write_text(body, encoding='utf-8')
print(f'Wrote {out} ({out.stat().st_size:,} bytes)')
