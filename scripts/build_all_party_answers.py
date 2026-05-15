"""Build data/party_answers_all.json — every party's official RÚV
kosningapróf answers, in every municipality, in one file.

Source: /_next/data/{buildId}/kjordaemi.json which already returns
all 182 ballot lists with their submitted answers. No per-page fetch
needed.

The output JSON is shaped for the review page (review/party-answers/):

  {
    "discoveredAt": "2026-05-15T12:00:00Z",
    "buildId":      "RuJSd9akH1ZETBLqyvw1F",
    "questions":    { "35": { "title", "slug", "type" }, ... },
    "munis": {
      "reykjavik": {
        "name":           "Reykjavík",
        "constituencyId": "0000",
        "parties": [
          { "code", "name", "slug", "color",
            "answers": [ { "qid", "value", "important", "reasoning" }, ... ],
            "skipped": [qids] }
        ]
      },
      ...
    },
    "unmatched": [ { "constituencyId", "name", "parties": [...] } ]
  }
"""
from __future__ import annotations
import json, urllib.request, re, sys, io, datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(__file__).resolve().parent.parent
UA = {'User-Agent': 'Mozilla/5.0'}
ROOT_URL = 'https://kosningaprof.ruv.is'

# RÚV constituencyId → our muni_id. Built from the candidate dump and
# eyeballed against MUNICIPALITIES. Munis we don't have on the site
# (e.g. unbound-election communes with no parties) won't appear in
# either side and don't need a mapping.
MUNI_BY_CONSTITUENCY = {
    '0000': 'reykjavik',
    '1000': 'kopavogur',
    '1300': 'seltjarnarnes',
    '1400': 'gardabaer',
    '1604': 'mosfellsbaer',
    '1606': 'kjosarhreppur',
    '1100': 'hafnarfjordur',
    '2000': 'reykjanesbaer',
    '2300': 'grindavik',
    '2503': 'sudurnesjabaer',
    '2506': 'vogar',
    '3000': 'akranes',
    '3501': 'hvalfjardarsveit',
    '3506': 'snaefellsbaer',
    '3511': 'eyjamiklaholts',
    '3603': 'grundarfjordur',
    '3609': 'stykkisholmur',
    '3709': 'dalabyggd',
    '4100': 'reykholar',
    '4200': 'vesturbyggd',
    '4502': 'bolungarvik',
    '4604': 'sudavik',
    '4607': 'arneshr',
    '4609': 'kaldrananes',
    '4611': 'strandabyggd',
    '4609': 'kaldrananes',
    '4912': 'hunathing',
    '5200': 'hunabyggd',
    '5508': 'skagastrond',
    '5604': 'skagafjordur',
    '5706': 'horgarsv',
    '5708': 'dalvikurbyggd',
    '5604': 'skagafjordur',
    '5612': 'akureyri',
    '5710': 'eyjafjardarsveit',
    '5711': 'svalbardsstrond',
    '5712': 'grytubakkar',
    '6100': 'nordurping',
    '6250': 'tjornes',
    '6515': 'thingeyjarsveit',
    '6601': 'fljotsdalshr',
    '6602': 'mulathing',
    '6605': 'vopnafjordur',
    '6609': 'langanesbyggd',
    '6612': 'fjardabyggd',
    '7300': 'mulathing',
    '7505': 'hornafjordur',
    '7610': 'skaftarhreppur',
    '7613': 'myrdalshr',
    '7708': 'rangarthingeystra',
    '7710': 'rangarthingytra',
    '7716': 'asahr',
    '7901': 'skeidagnup',
    '7902': 'hrunamannahreppur',
    '7903': 'arborg',
    '7906': 'floahreppur',
    '7909': 'blaskogabyggd',
    '7912': 'grimsnesgrafningur',
    '7915': 'hveragerdi',
    '7918': 'olfus',
    '8000': 'vestmannaeyjar',
    '8200': 'arborg',
    '8500': 'rangarthingeystra',
    '8508': 'myrdalshr',
    '8614': 'rangarthingytra',
    # Akureyri / Eyjafjarðarsveit / Fjallabyggð / etc — confirmed below
    'AK01': 'akureyri',
    'fjb-h': 'fjallabyggd',
    # Resolved from kjordaemi slugs (slug prefix matches our muni_id)
    '8716': 'hveragerdi',
    '3714': 'snaefellsbaer',
    '7502': 'vopnafjordur',
    '6611': 'tjornes',
}

def fetch(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()

print('Discovering buildId …')
home = fetch(ROOT_URL + '/').decode('utf-8', errors='replace')
build_id = re.search(r'"buildId":"([^"]+)"', home).group(1)
print(f'  buildId: {build_id}')

print('Fetching kjordaemi.json …')
data = json.loads(fetch(f'{ROOT_URL}/_next/data/{build_id}/kjordaemi.json'))
parties = data['pageProps']['parties']
print(f'  {len(parties)} party entries')

# Question catalogue from the existing candidate dump (kjordaemi.json
# doesn't include question titles — only IDs).
cand_dump = json.loads((ROOT / 'temp' / 'ruv_answers.json').read_text(encoding='utf-8'))
questions_full = cand_dump['questions']

# Build constituencyId → muni info from candidate dump (authoritative
# name, since kjordaemi.json gives only the id).
ruv_const = {}
for c in cand_dump['candidates']:
    cid = c.get('constituencyId')
    if cid and cid not in ruv_const:
        ruv_const[cid] = c.get('constituencyName', '')

# Pull party slugs and our internal codes from existing data
own_munis_src = (ROOT / 'js' / 'data' / 'municipalities.js').read_text(encoding='utf-8')
own_munis = {}
for m in re.finditer(r"\{\s*id:\s*'([^']+)',\s*name:\s*'([^']+)'", own_munis_src):
    own_munis[m.group(1)] = m.group(2)

# Try to auto-resolve any constituencyId we didn't hand-map by name
def norm(s):
    s = s.lower()
    for prefix in ['sveitarfélagið ', 'byggðin ']:
        s = s.replace(prefix, '')
    for suffix in ['kaupstaður', 'bær', 'hreppur', 'sýsla']:
        if s.endswith(suffix): s = s[:-len(suffix)]
    return s.replace('-', '').replace(' ', '').replace('ð', 'd').replace('þ', 'th').replace('æ', 'ae').replace('ö', 'o').replace('á','a').replace('í','i').replace('ú','u').replace('é','e').replace('ó','o').replace('ý','y')

own_by_norm = { norm(name): muni_id for muni_id, name in own_munis.items() }
for cid, cn in ruv_const.items():
    if cid in MUNI_BY_CONSTITUENCY: continue
    n = norm(cn)
    if n in own_by_norm:
        MUNI_BY_CONSTITUENCY[cid] = own_by_norm[n]

# Aggregate parties by muni
result = {
    'discoveredAt': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
    'buildId':      build_id,
    'questions':    {qid: {'title': q['title'], 'slug': q.get('slug',''), 'type': q.get('type')} for qid, q in questions_full.items()},
    'munis':        {},
    'unmatched':    [],
}
unmatched_by_cid = {}

for p in parties:
    for c in p.get('runningInConstituencies', []) or []:
        cid = c['id'] if isinstance(c, dict) else c
        muni_id = MUNI_BY_CONSTITUENCY.get(cid)
        ruv_name = ruv_const.get(cid, '?')
        party_info = {
            'code':       p.get('abbreviation', ''),
            'name':       p.get('name', ''),
            'slug':       p.get('slug', ''),
            'color':      p.get('color', ''),
            'answers':    [{
                'qid':       a.get('questionId'),
                'value':     a.get('value'),
                'important': bool(a.get('important')),
                'reasoning': a.get('reasoning', ''),
            } for a in (p.get('answers') or [])],
        }
        if muni_id:
            result['munis'].setdefault(muni_id, {
                'name':           own_munis.get(muni_id, ruv_name),
                'ruvName':        ruv_name,
                'constituencyId': cid,
                'parties':        [],
            })['parties'].append(party_info)
        else:
            unmatched_by_cid.setdefault(cid, {
                'constituencyId': cid,
                'ruvName':        ruv_name,
                'parties':        [],
            })['parties'].append(party_info)

result['unmatched'] = list(unmatched_by_cid.values())

# Sort parties within each muni by ballot letter
for m in result['munis'].values():
    m['parties'].sort(key=lambda p: p['code'])

# Emit
out = ROOT / 'data' / 'party_answers_all.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')

print()
print(f'Munis covered:       {len(result["munis"])}')
print(f'Party entries kept:  {sum(len(m["parties"]) for m in result["munis"].values())}')
print(f'Unmatched entries:   {sum(len(u["parties"]) for u in result["unmatched"])}')
print(f'Unmatched constituency IDs: {[u["constituencyId"]+":"+(u["ruvName"] or "?") for u in result["unmatched"]]}')
print(f'Wrote {out} ({out.stat().st_size:,} bytes)')
