"""For each municipality (constituency) found in the RÚV kosningapróf data,
identify questions where the running parties are NOT in agreement —
"cleavage" topics — and write a per-muni report to temp/.

Definitions
-----------
PROPOSITION answers map A/B (disagree side) → 1/2 and C/D (agree side) → 3/4
                       on a 1–4 scale. We treat values < 2.5 as disagree,
                       > 2.5 as agree.

RANGE answers are already 1–5 numeric. Midpoint 3.

A question is a CLEAVAGE if:
  - at least 2 parties answered it,
  - at least one party falls on the disagree side and at least one
    falls on the agree side (true polar disagreement, not just spread
    within one side),
  - the answers also have a meaningful std-dev (≥ 0.7 on the
    normalised 1–4 scale) so we filter out cases where one party
    sits exactly on the midpoint and another is just one step away.

A question is a CONSENSUS if all parties land on the same side and
the std-dev is ≤ 0.5.

PRIORITY questions are reported separately as a "priority disagreement"
score (Jaccard distance averaged across party pairs) — high score =
parties picked very different priority sets.

Output
------
  temp/ruv_cleavages_by_muni.json        — per-muni full report
  temp/ruv_cleavages_by_muni_summary.txt — human-readable digest
"""
from __future__ import annotations
import json, sys, io
from collections import defaultdict
from pathlib import Path
from statistics import pstdev, mean
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).parent.parent
RAW = ROOT / 'temp' / 'ruv_kjordaemi.json'
data = json.loads(RAW.read_text(encoding='utf-8'))
parties = data['pageProps']['parties']

# Map A/B/C/D → 1..4 for PROPOSITION; treat "_" and missing as None
PROP_MAP = {'A': 1, 'B': 2, 'C': 3, 'D': 4}

def numeric(ans: dict) -> float | None:
    # Accept both `questionType` (raw RÚV) and `type` (our derived dict).
    t = ans.get('questionType') or ans.get('type')
    v = ans.get('value')
    if v in (None, '', '_'):
        return None
    if t == 'PROPOSITION':
        return PROP_MAP.get(v)
    if t == 'RANGE':
        try:
            return float(v)
        except (TypeError, ValueError):
            return None
    return None

def numeric_midpoint(t: str) -> float:
    if t == 'PROPOSITION':
        return 2.5
    if t == 'RANGE':
        return 3.0
    return 0

# --- group parties by constituency, infer muni slug from slugs ---
by_constit: dict[str, list[dict]] = defaultdict(list)
for p in parties:
    for c in p.get('runningInConstituencies', []):
        by_constit[c.get('id')].append(p)

def common_prefix_slug(slugs: list[str]) -> str:
    if not slugs: return ''
    if len(slugs) == 1:
        # Single-party muni — fall back to first hyphen-separated token
        return slugs[0].split('-')[0]
    a = sorted(slugs)
    first, last = a[0], a[-1]
    i = 0
    while i < min(len(first), len(last)) and first[i] == last[i]:
        i += 1
    pref = first[:i].rstrip('-')
    return pref or first.split('-')[0]

# --- compute cleavages per constituency ---
out_munis: list[dict] = []

for cid, party_list in sorted(by_constit.items()):
    muni_slug = common_prefix_slug([p['slug'] for p in party_list])
    if not muni_slug:
        muni_slug = f'constituency-{cid}'

    # Collect (party, question) records
    by_q: dict[str, list[dict]] = defaultdict(list)
    for p in party_list:
        for ans in p.get('answers', []) or []:
            qid = ans.get('questionId')
            if qid is None: continue
            by_q[qid].append({
                'party_name': p['name'],
                'party_slug': p['slug'],
                'party_abbrev': p.get('abbreviation'),
                'value': ans.get('value'),
                'type': ans.get('questionType'),
                'reasoning': ans.get('reasoning'),
                'important': ans.get('important'),
                'q_title': (ans.get('question') or {}).get('title'),
            })

    cleavages: list[dict] = []
    consensus: list[dict] = []
    priority_disagreements: list[dict] = []

    for qid, recs in by_q.items():
        # Skip if fewer than 2 parties answered
        if len(recs) < 2: continue
        qtype = recs[0]['type']
        title = recs[0]['q_title']

        if qtype in ('PROPOSITION', 'RANGE'):
            nums = [(r, numeric(r)) for r in recs]
            nums = [(r, v) for r, v in nums if v is not None]
            if len(nums) < 2: continue
            values = [v for _, v in nums]
            mp = numeric_midpoint(qtype)
            disagree = [r for r, v in nums if v < mp]
            agree    = [r for r, v in nums if v > mp]
            on_fence = [r for r, v in nums if v == mp]
            std = pstdev(values) if len(values) > 1 else 0.0
            spread = max(values) - min(values)
            avg = mean(values)

            shape = {
                'question_id': qid,
                'question_type': qtype,
                'question_title': title,
                'avg': round(avg, 2),
                'std': round(std, 2),
                'spread': round(spread, 2),
                'parties_answered': len(values),
                'disagree_count': len(disagree),
                'agree_count':    len(agree),
                'on_fence_count': len(on_fence),
                'parties': sorted([
                    {'name': r['party_name'], 'value': r['value'], 'reasoning': (r['reasoning'] or '').strip() or None}
                    for r, _ in nums
                ], key=lambda x: x['value']),
            }

            cleavage_threshold_std = 0.7 if qtype == 'PROPOSITION' else 0.85
            consensus_threshold_std = 0.5 if qtype == 'PROPOSITION' else 0.65

            if disagree and agree and std >= cleavage_threshold_std:
                cleavages.append(shape)
            elif std <= consensus_threshold_std and (
                len(disagree) == 0 or len(agree) == 0
            ):
                consensus.append(shape)

        elif qtype == 'PRIORITY':
            # parse value as a list (RÚV gives e.g. "[3,6,7]" or already a list)
            sets: list[set] = []
            party_picks = []
            for r in recs:
                v = r['value']
                if v in (None, '', '_'): continue
                if isinstance(v, str):
                    v = v.strip()
                    if v.startswith('['):
                        try:
                            v = json.loads(v)
                        except Exception:
                            v = [tok.strip() for tok in v.strip('[]').split(',') if tok.strip()]
                    else:
                        v = [v]
                if not isinstance(v, list): continue
                s = set(str(x).strip() for x in v if str(x).strip())
                if not s: continue
                sets.append(s)
                party_picks.append({'name': r['party_name'], 'picks': sorted(s), 'reasoning': (r['reasoning'] or '').strip() or None})
            if len(sets) < 2: continue
            # Average pairwise Jaccard distance
            dists = []
            for i in range(len(sets)):
                for j in range(i+1, len(sets)):
                    a, b = sets[i], sets[j]
                    union = a | b
                    if not union: continue
                    dists.append(1 - len(a & b) / len(union))
            jacc = mean(dists) if dists else 0.0
            priority_disagreements.append({
                'question_id': qid,
                'question_type': qtype,
                'question_title': title,
                'parties_answered': len(sets),
                'avg_jaccard_distance': round(jacc, 2),
                'parties': party_picks,
            })

    cleavages.sort(key=lambda c: (-c['std'], c['question_id']))
    consensus.sort(key=lambda c: (c['std'], c['question_id']))
    priority_disagreements.sort(key=lambda c: -c['avg_jaccard_distance'])

    out_munis.append({
        'constituency_id': cid,
        'muni_slug': muni_slug,
        'parties': [{'name': p['name'], 'slug': p['slug'], 'abbreviation': p.get('abbreviation')} for p in party_list],
        'parties_count': len(party_list),
        'cleavages': cleavages,
        'consensus': consensus,
        'priority_disagreements': priority_disagreements,
    })

out_munis.sort(key=lambda m: m['muni_slug'])

# --- write outputs ---
out_json = ROOT / 'temp' / 'ruv_cleavages_by_muni.json'
out_json.write_text(json.dumps(out_munis, ensure_ascii=False, indent=2), encoding='utf-8')

# digest
digest_lines = []
for m in out_munis:
    digest_lines.append(f'═══ {m["muni_slug"].upper()}  ({m["parties_count"]} parties)  ═══')
    digest_lines.append(f'  parties: {", ".join(p["name"] for p in m["parties"])}')
    if m['cleavages']:
        digest_lines.append(f'\n  CLEAVAGES ({len(m["cleavages"])}):')
        for c in m['cleavages'][:10]:
            digest_lines.append(f'    [std {c["std"]:.2f}, {c["disagree_count"]}↓ vs {c["agree_count"]}↑]  {c["question_title"]}')
    else:
        digest_lines.append('\n  CLEAVAGES: (none)')
    if m['priority_disagreements']:
        top = m['priority_disagreements'][0]
        digest_lines.append(f'\n  PRIORITY divergence (Jaccard avg): {top["avg_jaccard_distance"]:.2f}')
    digest_lines.append('')

(ROOT / 'temp' / 'ruv_cleavages_by_muni_summary.txt').write_text('\n'.join(digest_lines), encoding='utf-8')

# Stats summary
total_cleavages = sum(len(m['cleavages']) for m in out_munis)
total_consensus = sum(len(m['consensus']) for m in out_munis)
print(f'Munis processed: {len(out_munis)}')
print(f'Cleavage flags total: {total_cleavages}')
print(f'Consensus flags total: {total_consensus}')
print(f'Wrote {out_json}')
print(f'Wrote {ROOT / "temp" / "ruv_cleavages_by_muni_summary.txt"}')

# Show top cleavages by std for largest 5 munis
print('\n=== Sample: 3 munis with most parties ===')
for m in sorted(out_munis, key=lambda x: -x['parties_count'])[:3]:
    print(f'\n{m["muni_slug"]} ({m["parties_count"]} parties):')
    for c in m['cleavages'][:5]:
        print(f'  • [std {c["std"]:.2f}] {c["question_title"]}')
        for p in c['parties'][:6]:
            print(f'      {p["name"]:30s} → {p["value"]}')
