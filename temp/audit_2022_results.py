"""Audit results2022.js against kosningasaga.wordpress.com.

For each muni in results2022.js:
  1. Find its 2022 kosningasaga page
  2. Parse the result table
  3. Compare each party's pct + seats
  4. Report discrepancies

Output: temp/audit_2022_report.md  (pretty markdown table)
"""
from __future__ import annotations
import re, json, sys, io, os, urllib.request, time, unicodedata
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r'F:\Claude Projects\iceland-elections')

# Load all 2022 URLs from kosningasaga index
INDEX_HTML = open(ROOT / 'temp' / 'ksaga_index.html', encoding='utf-8').read()
URLS_2022 = sorted(set(re.findall(r'https://kosningasaga\.wordpress\.com/sveitarstjornarkosningar/[^"\s]+-2022/', INDEX_HTML)))
print(f'discovered {len(URLS_2022)} 2022 URLs', file=sys.stderr)

# Map our muni id (results2022.js key) → kosningasaga URL slug
# slug is the last path segment minus '-2022'
URL_BY_KSAGA_SLUG = {}
for u in URLS_2022:
    slug = u.rstrip('/').rsplit('/', 1)[-1].replace('-2022', '')
    URL_BY_KSAGA_SLUG[slug] = u

# Map our key → kosningasaga slug
JS_TO_KSAGA = {
    'reykjavik':                   'reykjavik',
    'kopavogur':                   'kopavogur',
    'hafnarfjordur':               'hafnarfjordur',
    'gardabaer':                   'gardabaer',
    'mosfellsbaer':                'mosfellsbaer',
    'akureyri':                    'akureyri',
    'seltjarnarnes':               'seltjarnarnes',
    'reykjanesbaer':               'reykjanesbaer',
    'vogar':                       'sveitarfelagid-vogar',
    'grindavik':                   'grindavik',
    'sudurnesjabaer':              'sudurnesjabaer',
    'arborg':                      'sveitarfelagid-arborg',
    'vestmannaeyjar':              'vestmannaeyjar',
    'nordurping':                  'nordurthing',
    'fjallabyggd':                 'fjallabyggd',
    'fjardabyggd':                 'fjardabyggd',
    'hornafjordur':                'hornafjordur',
    'akranes':                     'akranes',
    'borgarbyggd':                 'borgarbyggd',
    'isafjordur':                  'isafjardarbaer',
    'hveragerdi':                  'hveragerdi',
    'rangarthingeystra':           'rangarthing-eystra',
    'rangarthingytra':             'rangarthing-ytra',
    'olfus':                       'sveitarfelagid-olfus',
    'skaftarhreppur':              'skaftarhreppur',
    'myrdalshr':                   'myrdalshreppur',
    'blaskogabyggd':               'blaskogabyggd',
    'floahreppur':                 'floahreppur',
    'hrunamannahreppur':           'hrunamannahreppur',
    'grimsnesgrafningur':          'grimsnes-og-grafningshreppur',
    'skeidagnup':                  'skeida-og-gnupverjahreppur',
    'dalvikurbyggd':               'dalvikurbyggd',
    'eyjafjardarsveit':            'eyjafjardarsveit',
    'horgarsv':                    'horgarbyggd',  # kosningasaga uses 'horgarbyggd' as URL slug for the 2022 page
    'hunabyggd':                   'sameinad-sveitarfelag-i-austur-hunavatnssyslu',  # 2022 was pre-merger
    'hunathing':                   None,  # Húnaþing vestra has no kosningasaga 2022 page
    'skagafjordur':                'sameinad-sveitarfelag-i-skagafirdi',
    'skagastrond':                 'sveitarfelagid-skagastrond',
    'stykkisholmur':               'sameinad-sveitarfelag-stykkisholms-og-helgafellssveitar',
    'grundarfjordur':              'grundarfjordur',
    'bolungarvik':                 'bolungarvik',
    'sudavik':                     'sudavik',
    'vesturbyggd':                 'vesturbyggd',
    'strandabyggd':                'strandabyggd',
    'reykholar':                   'reykholar',
    'mulathing':                   'mulathing',
    'thingeyjarsveit':             'thingeyjarsveit',
    'hvalfjardarsveit':            'hvalfjardarsveit',
    'snaefellsbaer':               'snaefellsbaer',
    'svalbardsstrond':             'svalbardsstrandarhreppur',
    'kjosarhreppur':               'kjosarhreppur',
    'vopnafjordur':                'vopnafjordur',
    'tjornes':                     'tjorneshreppur',
    'arneshr':                     'arneshreppur',
}

def fetch(url, cache_dir):
    import hashlib
    cache_dir.mkdir(parents=True, exist_ok=True)
    # use slug + short hash to avoid filename collisions
    slug = url.rstrip('/').rsplit('/', 1)[-1].replace('-2022', '')[:40]
    h = hashlib.sha1(url.encode()).hexdigest()[:8]
    fname = f'{slug}_{h}.html'
    path = cache_dir / fname
    if path.exists():
        return path.read_text(encoding='utf-8')
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0)'})
    with urllib.request.urlopen(req, timeout=30) as r:
        text = r.read().decode('utf-8', errors='replace')
    path.write_text(text, encoding='utf-8')
    time.sleep(0.5)
    return text

def parse_table(html):
    """Return list of {letter, name, votes, pct, seats}."""
    # focus on entry-content
    m = re.search(r'<div class="entry-content"[\s\S]*?</article>', html)
    body = m.group(0) if m else html
    body = re.sub(r'<br\s*/?>', '\n', body)
    body = re.sub(r'</tr>', '\n', body)
    text = re.sub(r'<[^>]+>', ' ', body)
    text = re.sub(r'[ \t]+', ' ', text)
    # Split lines, find rows that start with "X-listi" or "Listi X"
    rows = []
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        # Patterns: "B-listi Framsóknarflokks 1.811 32,20% 4 29,26% 4"
        # Or alt: "Framsóknarflokkurinn (B) 1.811 32,20% 4 ..."
        # Handle votes with comma OR dot thousands sep: "1,752" or "1.811"
        m = re.match(r'^([A-ZÁÉÍÓÚÝÞÆÖ])-listi\s+([^\d]+?)\s+(?:([\d,\.]+)\s+)?([\d,\.]+)%\s+(\d+)\b', line)
        if m:
            letter, name, votes_s, pct_s, seats_s = m.group(1), m.group(2).strip(), m.group(3), m.group(4), m.group(5)
            try:
                votes = int(re.sub(r'[,\.]', '', votes_s)) if votes_s else None
            except Exception:
                votes = None
            pct = float(pct_s.replace(',', '.'))
            seats = int(seats_s)
            # Sanity: pct must be 0-100
            if pct <= 100:
                rows.append({'letter': letter, 'name': name, 'votes': votes, 'pct': pct, 'seats': seats})
                continue
        # Variant: "X-listi Name pct% seats" (no votes column)
        m = re.match(r'^([A-ZÁÉÍÓÚÝÞÆÖ])-listi\s+([^\d]+?)\s+([\d,\.]+)%\s+(\d+)\s*$', line)
        if m:
            letter, name, pct_s, seats_s = m.group(1), m.group(2).strip(), m.group(3), m.group(4)
            rows.append({'letter': letter, 'name': name, 'votes': None, 'pct': float(pct_s.replace(',','.')), 'seats': int(seats_s)})
    return rows

# Load parties.js to get human-readable name per code
PJS = (ROOT / 'js' / 'data' / 'parties.js').read_text(encoding='utf-8')
PARTY_NAMES = {}
# Walk: find each `<CODE>: {` then capture until matching close brace
i = 0
n = len(PJS)
while i < n:
    m = re.search(r"^\s+([A-Z][A-Z0-9]{0,5}):\s*\{", PJS[i:], re.M)
    if not m:
        break
    code = m.group(1)
    start = i + m.end() - 1  # at {
    depth = 0
    j = start
    in_str = None
    while j < n:
        c = PJS[j]
        if in_str:
            if c == '\\': j += 2; continue
            if c == in_str: in_str = None
            j += 1; continue
        if c in ("'", '"'):
            in_str = c; j += 1; continue
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                break
        j += 1
    blob = PJS[start:j+1]
    nm = re.search(r"name:\s*'((?:[^'\\]|\\.)+)'", blob)
    if nm:
        PARTY_NAMES[code] = nm.group(1)
    i = j + 1
print(f'PARTY_NAMES loaded: {len(PARTY_NAMES)}', file=sys.stderr)

# Load results2022.js — extract the muni → parties map
RJS = (ROOT / 'js' / 'data' / 'results2022.js').read_text(encoding='utf-8')

# Quick parser: capture each muni block
muni_blocks = {}
for m in re.finditer(r"^\s*([a-zA-Z]+):\s*\{\s*$([\s\S]*?)^\s*\},?\s*$", RJS, re.M):
    name = m.group(1)
    body = m.group(2)
    if 'parties' not in body:
        continue
    parties = {}
    for pm in re.finditer(r"([A-Z][A-Za-z0-9]*)\s*:\s*\{\s*pct:\s*([\d\.]+)\s*,\s*seats:\s*(\d+)", body):
        parties[pm.group(1)] = {'pct': float(pm.group(2)), 'seats': int(pm.group(3))}
    if parties:
        muni_blocks[name] = parties
print(f'JS munis with parties: {len(muni_blocks)}', file=sys.stderr)

# Audit each
report = []
unmatched_munis = []
for our_id, our_parties in muni_blocks.items():
    ksaga_slug = JS_TO_KSAGA.get(our_id)
    if ksaga_slug is None:  # explicitly None means no kosningasaga page
        unmatched_munis.append((our_id, 'no kosningasaga page'))
        continue
    if not ksaga_slug:
        unmatched_munis.append((our_id, 'no slug map'))
        continue
    url = URL_BY_KSAGA_SLUG.get(ksaga_slug)
    if not url:
        unmatched_munis.append((our_id, f'no URL for slug "{ksaga_slug}"'))
        continue
    try:
        html = fetch(url, ROOT / 'temp' / 'ksaga_cache')
    except Exception as e:
        unmatched_munis.append((our_id, f'fetch err: {e}'))
        continue
    rows = parse_table(html)
    if not rows:
        unmatched_munis.append((our_id, 'no rows parsed'))
        continue
    by_letter = {r['letter']: r for r in rows}

    def normalize(s):
        s = (s or '').lower()
        s = re.sub(r'[^\w\sáéíóúýþæöð]', ' ', s)
        return re.sub(r'\s+', ' ', s).strip()

    # Helper: keyword-based match for national-party local lists
    NATIONAL_KEYWORDS = {
        'D': ['sjálfstæðis', 'sjálfstæðisflokks', 'sjálfstæðismanna'],
        'B': ['framsóknar', 'framsókn'],
        'S': ['samfylking'],
        'V': ['vinstri grænna', 'vg', 'vinstri-grænna'],
        'C': ['viðreisn'],
        'M': ['miðflokk'],
        'P': ['pírata'],
        'F': ['flokk fólks', 'flokks fólks'],
        'J': ['sósíalist'],
        'Y': [],  # local
        'L': [],  # local
        'K': [],  # local
        'N': [],  # local
    }

    def match_ks(code, ours):
        # 1) direct letter match
        if len(code) == 1 and code in by_letter:
            return by_letter[code], 'letter'
        # 2) name-based: get our party's display name
        our_name = PARTY_NAMES.get(code, '')
        if our_name:
            on = normalize(our_name)
            best = None; best_score = 0
            for r in rows:
                kn = normalize(r['name'])
                # token overlap
                ot = set(on.split())
                kt = set(kn.split())
                # weight by intersection size relative to smaller
                if not ot or not kt:
                    continue
                inter = ot & kt
                # discount common stopwords
                inter -= {'og', 'í', 'fyrir', 'okkar', 'allra', 'samfélag', 'samfélagsins', 'listinn', 'listans', 'listi'}
                score = len(inter) / max(1, min(len(ot), len(kt)))
                # Also consider keyword cues
                for letter, kws in NATIONAL_KEYWORDS.items():
                    if any(kw in on for kw in kws) and r['letter'] == letter:
                        score += 0.6  # boost
                if score > best_score:
                    best_score = score; best = r
            if best and best_score >= 0.3:
                return best, f'name (score {best_score:.2f})'
        # 3) seat-count fallback: if exactly one ksaga row has same seats and isn't already mapped
        if ours.get('seats', 0) > 0:
            cands = [r for r in rows if r['seats'] == ours['seats']]
            if len(cands) == 1:
                return cands[0], 'unique-seat'
        return None, 'no match'

    for code, ours in our_parties.items():
        ks, how = match_ks(code, ours)
        if not ks:
            report.append({'muni': our_id, 'party': code, 'our_name': PARTY_NAMES.get(code,''), 'our_pct': ours['pct'], 'our_seats': ours['seats'], 'ks_pct': None, 'ks_seats': None, 'ks_name': None, 'how': how, 'note': 'no row in kosningasaga'})
            continue
        ok_pct = abs(ours['pct'] - ks['pct']) <= 0.15
        ok_seats = ours['seats'] == ks['seats']
        if not ok_pct or not ok_seats:
            report.append({'muni': our_id, 'party': code, 'our_name': PARTY_NAMES.get(code,''), 'our_pct': ours['pct'], 'our_seats': ours['seats'], 'ks_pct': ks['pct'], 'ks_seats': ks['seats'], 'ks_name': ks['name'], 'ks_letter': ks['letter'], 'how': how, 'note': ('pct mismatch' if not ok_pct else '') + ('; seat mismatch' if not ok_seats else '')})

# Save report
out = ROOT / 'temp' / 'audit_2022_report.md'
with out.open('w', encoding='utf-8') as f:
    f.write('# 2022 result audit vs kosningasaga\n\n')
    f.write(f'audited munis: {len(muni_blocks)}\n')
    f.write(f'unaudited munis: {len(unmatched_munis)}\n\n')
    f.write('## Discrepancies\n\n')
    f.write('| muni | code | our name | our pct/seats | ksaga pct/seats | note | ksaga letter | ksaga name | matched-by |\n')
    f.write('|---|---|---|---|---|---|---|---|---|\n')
    for r in report:
        f.write(f'| {r["muni"]} | {r["party"]} | {r.get("our_name","")} | {r["our_pct"]}% / {r["our_seats"]} | '
                f'{("%.2f" % r["ks_pct"]) + "%" if r["ks_pct"] is not None else "—"} / '
                f'{r["ks_seats"] if r["ks_seats"] is not None else "—"} | {r["note"]} | {r.get("ks_letter","")} | {r.get("ks_name") or ""} | {r.get("how","")} |\n')
    f.write('\n## Unaudited munis\n\n')
    for u, reason in unmatched_munis:
        f.write(f'- **{u}** — {reason}\n')

print(f'\n=== Discrepancies: {len(report)} ===')
for r in report:
    print(r)
print(f'\n=== Unaudited: {len(unmatched_munis)} ===')
for u, reason in unmatched_munis:
    print(f' {u}: {reason}')
print(f'\nFull report: {out}')
