"""Build js/data/ruv_positions.js from temp/ruv_answers.json.

For each constituency we keep:
  - questions:  { qid: { title, slug, importance: { partyCode: count } } }
  - parties:    { partyCode: { qid: { mean, n, std } } }

`mean` is the average of candidates' Likert stances on a 1-4 scale
(A=1, B=2, C=3, D=4 per RÚV's coding: A=mjög ósammála, D=mjög sammála).
`n` is the count of answering candidates; `std` is the within-party spread.

Currently only Reykjavík is exported — extend the CONSTITUENCIES dict
when other munis pick up the strip.

Usage:
  python scripts/build_ruv_positions.py
"""
from __future__ import annotations
import json, sys, io, statistics
from collections import defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(__file__).resolve().parent.parent

# muni_id (matches MUNICIPALITIES[].id in JS) → RÚV constituencyId
CONSTITUENCIES = {
    'reykjavik': '0000',
}

# Likert mapping
LETTER_TO_NUM = {'A': 1, 'B': 2, 'C': 3, 'D': 4}

src = ROOT / 'temp' / 'ruv_answers.json'
out = ROOT / 'js' / 'data' / 'ruv_positions.js'

print(f'Reading {src} …')
data = json.loads(src.read_text(encoding='utf-8'))
all_questions = data['questions']
all_candidates = data['candidates']

result_by_muni = {}

for muni_id, constituency_id in CONSTITUENCIES.items():
    # Candidates in this constituency
    cands = [c for c in all_candidates if c.get('constituencyId') == constituency_id]
    if not cands:
        print(f'  [{muni_id}] no candidates for constituency {constituency_id}; skipping')
        continue

    # Questions applicable to this constituency — propositions only
    applicable_qids = set()
    for qid, q in all_questions.items():
        if q.get('type') != 'PROPOSITION':
            continue
        ac = q.get('applicableConstituencies')
        if ac is None or constituency_id in ac:
            applicable_qids.add(qid)

    # Collect raw stances per (party, qid)
    stances = defaultdict(lambda: defaultdict(list))  # party → qid → [nums]
    importance = defaultdict(lambda: defaultdict(int))  # qid → party → count

    for c in cands:
        pcode = c.get('partyCode')
        if not pcode:
            continue
        for ans in c.get('answers') or []:
            qid = ans.get('qid')
            if qid not in applicable_qids:
                continue
            v = ans.get('value')
            num = LETTER_TO_NUM.get(v)
            if num is None:
                continue
            stances[pcode][qid].append(num)
            if ans.get('important'):
                importance[qid][pcode] += 1

    # Build party positions
    parties_out = {}
    for pcode, by_q in stances.items():
        parties_out[pcode] = {}
        for qid, nums in by_q.items():
            mean = round(sum(nums) / len(nums), 3)
            std = round(statistics.pstdev(nums), 3) if len(nums) > 1 else 0.0
            parties_out[pcode][qid] = {'mean': mean, 'n': len(nums), 'std': std}

    # Question metadata — only include questions we have any party data for
    seen_qids = {qid for by_q in stances.values() for qid in by_q}
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
    print(f'  [{muni_id}] {len(cands)} candidates, {len(questions_out)} questions, '
          f'{len(parties_out)} parties → {sum(len(v) for v in parties_out.values())} (party,qid) entries')

# Emit JS module
out.parent.mkdir(parents=True, exist_ok=True)
body = (
    '// Auto-generated from temp/ruv_answers.json by scripts/build_ruv_positions.py.\n'
    '// DO NOT EDIT BY HAND — re-run the script and commit the regenerated file.\n'
    '//\n'
    '// Per-muni RÚV kosningapróf 2026 stances aggregated to party level.\n'
    '// Likert scale: 1=mjög ósammála, 2=ósammála, 3=sammála, 4=mjög sammála\n'
    '// (RÚV codes those as A, B, C, D respectively).\n'
    '//   questions[qid] = { title, slug, importance: { partyCode: candidateCount } }\n'
    '//   parties[code][qid] = { mean, n, std }\n'
    'export const RUV_POSITIONS = '
    + json.dumps(result_by_muni, ensure_ascii=False, indent=2)
    + ';\n'
)
out.write_text(body, encoding='utf-8')
print(f'Wrote {out} ({out.stat().st_size:,} bytes)')
