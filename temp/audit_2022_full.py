"""Full audit: every party in every muni, our data vs kosningasaga, name-only matching.

Output: temp/audit_2022_full.md  (exhaustive table, no shortcuts)
"""
from __future__ import annotations
import re, json, sys, io, os, urllib.request, time, unicodedata, hashlib
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r'F:\Claude Projects\iceland-elections')

# ─── URL discovery ──────────────────────────────────────────────────────────
INDEX_HTML = open(ROOT / 'temp' / 'ksaga_index.html', encoding='utf-8').read()
URLS_2022 = sorted(set(re.findall(r'https://kosningasaga\.wordpress\.com/sveitarstjornarkosningar/[^"\s]+-2022/', INDEX_HTML)))

URL_BY_KSAGA_SLUG = {}
for u in URLS_2022:
    slug = u.rstrip('/').rsplit('/', 1)[-1].replace('-2022', '')
    URL_BY_KSAGA_SLUG[slug] = u

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
    'hornafjordur':                'sveitarfelagid-hornafjordur',
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
    'horgarsv':                    'horgarbyggd',
    'hunabyggd':                   'sameinad-sveitarfelag-i-austur-hunavatnssyslu',
    'hunathing':                   None,
    'skagafjordur':                'sameinad-sveitarfelag-i-skagafirdi',
    'skagastrond':                 'sveitarfelagid-skagastrond',
    'stykkisholmur':               'sameinad-sveitarfelag-stykkisholms-og-helgafellssveitar',
    'grundarfjordur':              'grundarfjordur',
    'bolungarvik':                 'bolungarvik',
    'sudavik':                     'sudavikurhreppur',
    'vesturbyggd':                 'vesturbyggd',
    'strandabyggd':                'strandabyggd',
    'reykholar':                   'reykholahreppur',
    'mulathing':                   'mulathing',
    'thingeyjarsveit':             'sameinad-sveitarfelag-thingeyjarsveitar-og-skutustadahrepps',
    'hvalfjardarsveit':            'hvalfjardarsveit',
    'snaefellsbaer':               'snaefellsbaer',
    'svalbardsstrond':             'svalbardsstrandarhreppur',
    'kjosarhreppur':               'kjosarhreppur',
    'vopnafjordur':                'vopnafjordur',
    'tjornes':                     'tjorneshreppur',
    'arneshr':                     'arneshreppur',
}

# ─── fetch ──────────────────────────────────────────────────────────────────
def fetch(url):
    cache = ROOT / 'temp' / 'ksaga_cache'
    cache.mkdir(parents=True, exist_ok=True)
    slug = url.rstrip('/').rsplit('/', 1)[-1].replace('-2022', '')[:40]
    h = hashlib.sha1(url.encode()).hexdigest()[:8]
    p = cache / f'{slug}_{h}.html'
    if p.exists():
        return p.read_text(encoding='utf-8')
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0)'})
    with urllib.request.urlopen(req, timeout=30) as r:
        text = r.read().decode('utf-8', errors='replace')
    p.write_text(text, encoding='utf-8')
    time.sleep(0.5)
    return text

# ─── kosningasaga parser ────────────────────────────────────────────────────
def parse_table(html):
    m = re.search(r'<div class="entry-content"[\s\S]*?</article>', html)
    body = m.group(0) if m else html
    body = re.sub(r'<br\s*/?>', '\n', body)
    body = re.sub(r'</tr>', '\n', body)
    text = re.sub(r'<[^>]+>', ' ', body)
    text = re.sub(r'[ \t]+', ' ', text)
    rows = []
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        # Pattern: "X-listi NAME (votes)? PCT% SEATS [diff_pct% diff_seats]"
        m = re.match(r'^([A-ZÁÉÍÓÚÝÞÆÖ])[\-–]listi\s+([^\d]+?)\s+(?:([\d,\.]+)\s+)?(\d{1,3}(?:[\.,]\d+)?)%\s+(\d+)\b', line)
        if m:
            letter, name, votes_s, pct_s, seats_s = m.group(1), m.group(2).strip(), m.group(3), m.group(4), m.group(5)
            try:
                pct = float(pct_s.replace(',', '.'))
            except:
                continue
            if pct > 100:
                continue
            try:
                votes = int(re.sub(r'[,\.]', '', votes_s)) if votes_s else None
            except:
                votes = None
            rows.append({'letter': letter, 'name': name, 'votes': votes, 'pct': pct, 'seats': int(seats_s)})
    # Dedup (same letter+name): keep first
    seen = set()
    out = []
    for r in rows:
        k = (r['letter'], r['name'])
        if k in seen: continue
        seen.add(k); out.append(r)
    return out

# ─── load our data ──────────────────────────────────────────────────────────
RJS = (ROOT / 'js' / 'data' / 'results2022.js').read_text(encoding='utf-8')
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

# ─── load names for our parties ─────────────────────────────────────────────
PJS = (ROOT / 'js' / 'data' / 'parties.js').read_text(encoding='utf-8')
PARTY_NAMES = {}
i = 0
while i < len(PJS):
    m = re.search(r"^\s+([A-Z][A-Z0-9]{0,5}):\s*\{", PJS[i:], re.M)
    if not m: break
    code = m.group(1)
    start = i + m.end() - 1
    depth = 0; j = start; in_str = None
    while j < len(PJS):
        c = PJS[j]
        if in_str:
            if c == '\\': j += 2; continue
            if c == in_str: in_str = None
            j += 1; continue
        if c in ("'", '"'): in_str = c; j += 1; continue
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: break
        j += 1
    blob = PJS[start:j+1]
    nm = re.search(r"name:\s*'((?:[^'\\]|\\.)+)'", blob)
    if nm:
        PARTY_NAMES[code] = nm.group(1)
    i = j + 1

# Also extract tagline for each (muni_id, party_code) from candidates.js
# This gives us the local list's display name (e.g. "Vinir Mosfellsbæjar")
CJS = (ROOT / 'js' / 'data' / 'candidates.js').read_text(encoding='utf-8')

# Map muni id -> const name in candidates.js
MUNI_TO_CONST = {}
m = re.search(r"const REAL_DATA = \{([^}]+)\}", CJS)
if m:
    for pm in re.finditer(r"(\w+):\s*([A-Z]+)", m.group(1)):
        MUNI_TO_CONST[pm.group(1)] = pm.group(2)

def find_const_block(src, const_name):
    m = re.search(r'^const ' + re.escape(const_name) + r'\s*=\s*\{', src, re.M)
    if not m: return None
    open_pos = m.end() - 1
    depth = 0; i = open_pos
    while i < len(src):
        c = src[i]
        if c == '/' and i+1 < len(src) and src[i+1] == '/':
            i = src.find('\n', i+2); i = i if i != -1 else len(src); continue
        if c == '/' and i+1 < len(src) and src[i+1] == '*':
            j = src.find('*/', i+2); i = (j+2) if j != -1 else len(src); continue
        if c in ("'", '"', '`'):
            q = c; i += 1
            while i < len(src):
                if src[i] == '\\': i += 2; continue
                if src[i] == q: i += 1; break
                i += 1
            continue
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: return open_pos+1, i
        i += 1
    return None

def get_tagline(muni_id, party_code):
    const = MUNI_TO_CONST.get(muni_id)
    if not const: return None
    span = find_const_block(CJS, const)
    if not span: return None
    body_start, body_end = span
    pat = re.compile(r'\n  ' + re.escape(party_code) + r'\s*:\s*\{')
    pm = pat.search(CJS, body_start, body_end)
    if not pm: return None
    # find tagline within next ~2000 chars
    chunk = CJS[pm.end():pm.end()+2000]
    tm = re.search(r"tagline:\s*'((?:[^'\\]|\\.)+)'", chunk)
    if tm:
        return tm.group(1).replace("\\'", "'").replace('\\\\', '\\')
    return None

# ─── name normalization + matching ──────────────────────────────────────────
def normalize(s):
    if not s: return ''
    s = unicodedata.normalize('NFC', s).lower()
    s = re.sub(r'[^a-záéíóúýþæöð\s]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

# Stop words to ignore in matching
STOP = {'og', 'í', 'fyrir', 'okkar', 'allra', 'óháðra', 'óháðir', 'samfélag', 'samfélagsins', 'list', 'listinn', 'listans', 'listi', 'fl', 'manna', 'flokks', 'flokkur', 'flokkurinn', 'félagsh', 'sveit', 'um', 'a', 'ad', 'að', 'við', 'á', 'er', 'sem', 'b', 'c', 'd', 'e', 'f'}

NATIONAL_KEYS = {
    'sjálfstæð': 'D',
    'framsókn':  'B',
    'samfylking':'S',
    'vinstri':   'V',
    'viðreisn':  'C',
    'miðflokk':  'M',
    'pírata':    'P',
    'pírat':     'P',
    'flokk fólks': 'F',
    'sósíalist': 'J',
    'jafnaðar':  'A',  # Sometimes Samfylking runs as A locally
    'gerum':     'G',  # local
    'okkar':     'O',  # local
}

def name_score(our_name, ks_name):
    on = normalize(our_name)
    kn = normalize(ks_name)
    if not on or not kn:
        return 0.0
    ot = set(on.split()) - STOP
    kt = set(kn.split()) - STOP
    if not ot or not kt:
        return 0.0
    inter = ot & kt
    # Distinctive keyword check
    bonus = 0.0
    for kw in NATIONAL_KEYS:
        if kw in on and kw in kn:
            bonus += 0.5
    return len(inter) / max(len(ot), len(kt)) + bonus

def best_match(our_name, ks_rows, code):
    if not ks_rows:
        return None, 0.0
    # 1) National-keyword shortcut
    on = normalize(our_name)
    for kw, letter in NATIONAL_KEYS.items():
        if kw in on:
            for r in ks_rows:
                if r['letter'] == letter:
                    return r, 1.0
    # 2) Letter-equal shortcut
    if len(code) == 1:
        for r in ks_rows:
            if r['letter'] == code:
                return r, 0.9
    # 3) Name similarity
    best = None; best_score = 0.0
    for r in ks_rows:
        s = name_score(our_name, r['name'])
        if s > best_score:
            best_score = s; best = r
    if best_score >= 0.5:
        return best, best_score
    return None, best_score

# ─── audit ──────────────────────────────────────────────────────────────────
results = []  # list of dicts
for our_id, our_parties in muni_blocks.items():
    ksaga_slug = JS_TO_KSAGA.get(our_id)
    ksaga_url = URL_BY_KSAGA_SLUG.get(ksaga_slug) if ksaga_slug else None
    ks_rows = []
    fetch_err = None
    if ksaga_slug is None:
        fetch_err = 'no kosningasaga page exists'
    elif not ksaga_url:
        fetch_err = f'slug "{ksaga_slug}" not found in kosningasaga URL index'
    else:
        try:
            html = fetch(ksaga_url)
            ks_rows = parse_table(html)
            if not ks_rows:
                fetch_err = 'page found but no result rows parseable'
        except Exception as e:
            fetch_err = f'fetch error: {e}'
    # For each of our parties
    for code, ours in our_parties.items():
        our_name = PARTY_NAMES.get(code, '')
        tagline = get_tagline(our_id, code) or ''
        # Use best of party name + tagline for matching
        match_name = our_name + ' ' + tagline
        ks, score = best_match(match_name, ks_rows, code) if ks_rows else (None, 0.0)
        results.append({
            'muni': our_id,
            'party_code': code,
            'our_name': our_name,
            'our_tagline': tagline[:80],
            'our_pct': ours['pct'],
            'our_seats': ours['seats'],
            'ks_letter': ks['letter'] if ks else '',
            'ks_name': ks['name'] if ks else '',
            'ks_pct': ks['pct'] if ks else None,
            'ks_seats': ks['seats'] if ks else None,
            'match_score': round(score, 2),
            'fetch_err': fetch_err if not ks_rows else '',
        })
    # Also list ksaga rows we didn't match to anything
    matched_ks = set()
    for r in results:
        if r['muni'] == our_id and r['ks_name']:
            matched_ks.add(r['ks_name'])
    for r in ks_rows:
        if r['name'] not in matched_ks:
            results.append({
                'muni': our_id,
                'party_code': '(in kosningasaga only)',
                'our_name': '',
                'our_tagline': '',
                'our_pct': None,
                'our_seats': None,
                'ks_letter': r['letter'],
                'ks_name': r['name'],
                'ks_pct': r['pct'],
                'ks_seats': r['seats'],
                'match_score': 0.0,
                'fetch_err': '',
            })

# ─── render ─────────────────────────────────────────────────────────────────
def status(r):
    if r['fetch_err']:
        return '⚠️ ' + r['fetch_err']
    if r['party_code'] == '(in kosningasaga only)':
        return '— kosningasaga has this list but our data does not'
    if r['ks_name'] == '':
        return '❓ no kosningasaga match found'
    if r['our_pct'] is None:
        return ''
    pct_eq = abs(r['our_pct'] - r['ks_pct']) <= 0.15
    seats_eq = r['our_seats'] == r['ks_seats']
    if pct_eq and seats_eq:
        return '✅ exact'
    parts = []
    if not pct_eq: parts.append(f'pct off by {abs(r["our_pct"] - r["ks_pct"]):.2f}pp')
    if not seats_eq: parts.append(f'seats differ ({r["our_seats"]} vs {r["ks_seats"]})')
    return '❌ ' + '; '.join(parts)

# Sort by muni then ours_pct desc
results.sort(key=lambda r: (r['muni'], -(r['our_pct'] or 0)))

out = ROOT / 'temp' / 'audit_2022_full.md'
with out.open('w', encoding='utf-8') as f:
    f.write('# Full 2022 results audit — every party, name-only matching\n\n')
    f.write(f'munis audited: {len(muni_blocks)}\n')
    n_exact = sum(1 for r in results if status(r) == '✅ exact')
    n_mismatch = sum(1 for r in results if status(r).startswith('❌'))
    n_unmatched = sum(1 for r in results if status(r).startswith('❓'))
    n_ksonly = sum(1 for r in results if status(r).startswith('—'))
    n_err = sum(1 for r in results if status(r).startswith('⚠️'))
    f.write(f'\n- ✅ exact match: {n_exact}\n')
    f.write(f'- ❌ mismatch: {n_mismatch}\n')
    f.write(f'- ❓ no kosningasaga match found: {n_unmatched}\n')
    f.write(f'- — kosningasaga has list, we don\'t: {n_ksonly}\n')
    f.write(f'- ⚠️ couldn\'t fetch / parse muni: {n_err} rows\n\n')
    f.write('## Per-row table\n\n')
    f.write('| muni | code | our list (name + tagline) | our pct/seats | ksaga (letter, name) | ksaga pct/seats | status |\n')
    f.write('|---|---|---|---|---|---|---|\n')
    cur_muni = None
    for r in results:
        if r['muni'] != cur_muni:
            cur_muni = r['muni']
        our_label = (r['our_name'] or '') + (' — ' + r['our_tagline'] if r['our_tagline'] else '')
        our_label = our_label.replace('|', '\\|')[:120]
        ks_label = (f'{r["ks_letter"]} — {r["ks_name"]}' if r['ks_name'] else '').replace('|', '\\|')[:120]
        our_v = (f"{r['our_pct']}% / {r['our_seats']}" if r['our_pct'] is not None else '—')
        ks_v = (f"{r['ks_pct']:.2f}% / {r['ks_seats']}" if r['ks_pct'] is not None else '—')
        f.write(f'| {r["muni"]} | {r["party_code"]} | {our_label} | {our_v} | {ks_label} | {ks_v} | {status(r)} |\n')

print(f'Wrote {out}')
print(f'  exact: {n_exact}')
print(f'  mismatch: {n_mismatch}')
print(f'  no match: {n_unmatched}')
print(f'  kosningasaga-only: {n_ksonly}')
print(f'  fetch err rows: {n_err}')
