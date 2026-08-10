"""For each ❌ row where seat counts already match, propose updating our pct
to the kosningasaga pct value. Output a clear diff. Don't write yet."""
import re, sys, io, hashlib, urllib.request, time, json
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r'F:\Claude Projects\iceland-elections')

INDEX = (ROOT / 'temp' / 'ksaga_index.html').read_text(encoding='utf-8')
URLS = sorted(set(re.findall(r'https://kosningasaga\.wordpress\.com/sveitarstjornarkosningar/[^"\s]+-2022/', INDEX)))
URL_BY_SLUG = {u.rstrip('/').rsplit('/',1)[-1].replace('-2022',''): u for u in URLS}

JS_TO_KSAGA = {
    'reykjavik':'reykjavik','kopavogur':'kopavogur','hafnarfjordur':'hafnarfjordur',
    'gardabaer':'gardabaer','mosfellsbaer':'mosfellsbaer','akureyri':'akureyri',
    'seltjarnarnes':'seltjarnarnes','reykjanesbaer':'reykjanesbaer',
    'vogar':'sveitarfelagid-vogar','grindavik':'grindavik','sudurnesjabaer':'sudurnesjabaer',
    'arborg':'sveitarfelagid-arborg','vestmannaeyjar':'vestmannaeyjar','nordurping':'nordurthing',
    'fjallabyggd':'fjallabyggd','fjardabyggd':'fjardabyggd',
    'hornafjordur':'sveitarfelagid-hornafjordur','akranes':'akranes',
    'borgarbyggd':'borgarbyggd','isafjordur':'isafjardarbaer','hveragerdi':'hveragerdi',
    'rangarthingeystra':'rangarthing-eystra','rangarthingytra':'rangarthing-ytra',
    'olfus':'sveitarfelagid-olfus','skaftarhreppur':'skaftarhreppur','myrdalshr':'myrdalshreppur',
    'blaskogabyggd':'blaskogabyggd','floahreppur':'floahreppur','hrunamannahreppur':'hrunamannahreppur',
    'grimsnesgrafningur':'grimsnes-og-grafningshreppur','skeidagnup':'skeida-og-gnupverjahreppur',
    'dalvikurbyggd':'dalvikurbyggd','eyjafjardarsveit':'eyjafjardarsveit',
    'horgarsv':'horgarbyggd','hunabyggd':'sameinad-sveitarfelag-i-austur-hunavatnssyslu',
    'hunathing':None,'skagafjordur':'sameinad-sveitarfelag-i-skagafirdi',
    'skagastrond':'sveitarfelagid-skagastrond',
    'stykkisholmur':'sameinad-sveitarfelag-stykkisholms-og-helgafellssveitar',
    'grundarfjordur':'grundarfjordur','bolungarvik':'bolungarvik','sudavik':'sudavikurhreppur',
    'vesturbyggd':'vesturbyggd','strandabyggd':'strandabyggd','reykholar':'reykholahreppur',
    'mulathing':'mulathing','thingeyjarsveit':'sameinad-sveitarfelag-thingeyjarsveitar-og-skutustadahrepps',
    'hvalfjardarsveit':'hvalfjardarsveit','snaefellsbaer':'snaefellsbaer',
    'svalbardsstrond':'svalbardsstrandarhreppur','kjosarhreppur':'kjosarhreppur',
    'vopnafjordur':'vopnafjordur','tjornes':'tjorneshreppur','arneshr':'arneshreppur',
}
MUNI_NAMES = {
    'mosfellsbaer':'Mosfellsbær','arborg':'Árborg','vestmannaeyjar':'Vestmannaeyjar',
    'nordurping':'Norðurþing','fjallabyggd':'Fjallabyggð','fjardabyggd':'Fjarðabyggð',
    'hveragerdi':'Hveragerði','rangarthingeystra':'Rangárþing eystra','rangarthingytra':'Rangárþing ytra',
    'olfus':'Ölfus','dalvikurbyggd':'Dalvíkurbyggð','horgarsv':'Hörgársveit','mulathing':'Múlaþing',
    'gardabaer':'Garðabær','hrunamannahreppur':'Hrunamannahreppur','hunabyggd':'Húnabyggð',
}

def fetch(url):
    cache = ROOT / 'temp' / 'ksaga_cache'; cache.mkdir(parents=True, exist_ok=True)
    slug = url.rstrip('/').rsplit('/',1)[-1].replace('-2022','')[:40]
    h = hashlib.sha1(url.encode()).hexdigest()[:8]
    p = cache / f'{slug}_{h}.html'
    if p.exists(): return p.read_text(encoding='utf-8')
    text = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'}), timeout=30).read().decode('utf-8','replace')
    p.write_text(text, encoding='utf-8'); time.sleep(0.3)
    return text

def parse_ksaga(html):
    m = re.search(r'<div class="entry-content"[\s\S]*?</article>', html)
    body = m.group(0) if m else html
    body = re.sub(r'<br\s*/?>', '\n', body); body = re.sub(r'</tr>', '\n', body)
    text = re.sub(r'<[^>]+>', ' ', body); text = re.sub(r'[ \t]+', ' ', text)
    rows = []
    for line in text.split('\n'):
        line = line.strip()
        m = re.match(r'^([A-ZÁÉÍÓÚÝÞÆÖ])[\-–]listi\s+([^\d]+?)\s+(?:[\d,\.]+\s+)?(\d{1,3}(?:[\.,]\d+)?)%\s+(\d+)\b', line)
        if m:
            try:
                pct = float(m.group(3).replace(',','.'))
                if pct > 100: continue
                rows.append({'letter': m.group(1), 'name': m.group(2).strip(), 'pct': pct, 'seats': int(m.group(4))})
            except: pass
    seen=set(); out=[]
    for r in rows:
        k=(r['letter'],r['name'])
        if k in seen: continue
        seen.add(k); out.append(r)
    return out

# Same pairing logic as audit_paired.py
RJS = (ROOT / 'js' / 'data' / 'results2022.js').read_text(encoding='utf-8')
muni_blocks = {}
for m in re.finditer(r"^\s*([a-zA-Z]+):\s*\{\s*$([\s\S]*?)^\s*\},?\s*$", RJS, re.M):
    name = m.group(1); body = m.group(2)
    if 'parties' not in body: continue
    parties = []
    for pm in re.finditer(r"([A-Z][A-Za-z0-9]*)\s*:\s*\{\s*pct:\s*([\d\.]+)\s*,\s*seats:\s*(\d+)", body):
        parties.append({'code': pm.group(1), 'pct': float(pm.group(2)), 'seats': int(pm.group(3))})
    if parties: muni_blocks[name] = parties

PJS = (ROOT / 'js' / 'data' / 'parties.js').read_text(encoding='utf-8')
PARTY_NAMES = {}
i = 0
while i < len(PJS):
    m = re.search(r"^\s+([A-Z][A-Z0-9]{0,5}):\s*\{", PJS[i:], re.M)
    if not m: break
    code = m.group(1); start = i + m.end() - 1
    depth=0; j=start; in_str=None
    while j < len(PJS):
        c = PJS[j]
        if in_str:
            if c=='\\': j+=2; continue
            if c==in_str: in_str=None
            j+=1; continue
        if c in ("'",'"'): in_str=c; j+=1; continue
        if c=='{': depth+=1
        elif c=='}':
            depth-=1
            if depth==0: break
        j+=1
    blob = PJS[start:j+1]
    nm = re.search(r"name:\s*'((?:[^'\\]|\\.)+)'", blob)
    if nm: PARTY_NAMES[code] = nm.group(1)
    i = j + 1

CJS = (ROOT / 'js' / 'data' / 'candidates.js').read_text(encoding='utf-8')
MUNI_CONST = {}
m = re.search(r"const REAL_DATA = \{([^}]+)\}", CJS)
if m:
    for pm in re.finditer(r"(\w+):\s*([A-Z]+)", m.group(1)):
        MUNI_CONST[pm.group(1)] = pm.group(2)

def find_const(src, const):
    m = re.search(r'^const ' + re.escape(const) + r'\s*=\s*\{', src, re.M)
    if not m: return None
    open_pos = m.end() - 1
    depth=0; i=open_pos
    while i < len(src):
        c=src[i]
        if c in ("'",'"','`'):
            q=c; i+=1
            while i<len(src):
                if src[i]=='\\': i+=2; continue
                if src[i]==q: i+=1; break
                i+=1
            continue
        if c=='{': depth+=1
        elif c=='}':
            depth-=1
            if depth==0: return open_pos+1, i
        i+=1

def get_tagline(our_id, code):
    const = MUNI_CONST.get(our_id)
    if not const: return ''
    span = find_const(CJS, const)
    if not span: return ''
    body_start, body_end = span
    pat = re.compile(r'\n  ' + re.escape(code) + r'\s*:\s*\{')
    pm = pat.search(CJS, body_start, body_end)
    if not pm: return ''
    chunk = CJS[pm.end():pm.end()+1500]
    tm = re.search(r"tagline:\s*'((?:[^'\\]|\\.)+)'", chunk)
    return tm.group(1).replace("\\'","'").replace('\\\\','\\') if tm else ''

NATIONAL = [(r'sjálfstæðis','D'),(r'framsókn','B'),(r'samfylking','S'),(r'vinstri','V'),
            (r'viðreisn','C'),(r'miðflokk','M'),(r'pírat','P'),(r'sósíalist','J'),(r'flokk fólks','F')]
def candidate_letters(code, name, tagline):
    letters = []
    text = (name + ' ' + tagline).lower()
    for m in re.finditer(r"\b([a-záéíóúýþæöð])\s*[\-–]list", text):
        L = m.group(1).upper()
        if L not in letters: letters.append(L)
    for kw, L in NATIONAL:
        if kw in text and L not in letters: letters.append(L)
    if len(code) == 1 and code not in letters: letters.append(code)
    return letters

def pair(our_parties, ks_rows, our_id):
    used_ks = [False]*len(ks_rows); pair_map = {}
    enriched = [{**o, 'name': PARTY_NAMES.get(o['code'],''), 'tagline': get_tagline(our_id, o['code'])} for o in our_parties]
    for o in enriched:
        o['cands'] = candidate_letters(o['code'], o['name'], o['tagline'])
    # Pass 1: letter
    for oi, o in enumerate(enriched):
        for L in o['cands']:
            for i, r in enumerate(ks_rows):
                if used_ks[i]: continue
                if r['letter'] == L: used_ks[i]=True; pair_map[oi]=i; break
            if oi in pair_map: break
    # Pass 2: name keyword overlap
    def normalize(s):
        s = (s or '').lower(); s = re.sub(r'[^a-záéíóúýþæöð\s]', ' ', s)
        return [w for w in s.split() if len(w)>3 and w not in ('listi','listinn','listans','flokk','flokks','flokkur','flokkurinn','óháð','óháðir','óháðra','okkar','sveit','samfélag','samfélagsins')]
    for oi, o in enumerate(enriched):
        if oi in pair_map: continue
        words = set(normalize(o['name'])+normalize(o['tagline']))
        best_i = -1; best_score = 0
        for i, r in enumerate(ks_rows):
            if used_ks[i]: continue
            score = len(words & set(normalize(r['name'])))
            if score > best_score: best_score=score; best_i=i
        if best_score >= 1: used_ks[best_i]=True; pair_map[oi]=best_i
    # Pass 3: leftover greedy by seat count
    leftover_o = [oi for oi in range(len(enriched)) if oi not in pair_map]
    leftover_k = [i for i in range(len(ks_rows)) if not used_ks[i]]
    for oi in leftover_o:
        o = enriched[oi]; best_i=-1; best_d=999
        for i in leftover_k:
            if used_ks[i]: continue
            if ks_rows[i]['seats'] != o['seats']: continue
            d = abs(ks_rows[i]['pct'] - o['pct'])
            if d < best_d: best_d=d; best_i=i
        if best_i >= 0: used_ks[best_i]=True; pair_map[oi]=best_i
    return enriched, pair_map

# Build proposed updates
proposals = []  # list of {muni, code, old_pct, new_pct, ks_letter, ks_name}
for our_id, parties in muni_blocks.items():
    ks_slug = JS_TO_KSAGA.get(our_id)
    if not ks_slug or ks_slug not in URL_BY_SLUG: continue
    try:
        ks_rows = parse_ksaga(fetch(URL_BY_SLUG[ks_slug]))
    except Exception: continue
    if not ks_rows: continue
    enriched, pair_map = pair(parties, ks_rows, our_id)
    for oi, o in enumerate(enriched):
        if oi not in pair_map: continue
        r = ks_rows[pair_map[oi]]
        if o['seats'] != r['seats']: continue  # only fix when seats already match
        if abs(o['pct'] - r['pct']) <= 0.15: continue  # no fix needed
        proposals.append({
            'muni': our_id, 'code': o['code'], 'seats': o['seats'],
            'old_pct': o['pct'], 'new_pct': round(r['pct'], 2),
            'ks_letter': r['letter'], 'ks_name': r['name'],
        })

# Print proposed diff
print(f'\n{len(proposals)} proposed pct fixes (seat counts already match):\n')
print(f'{"Muni":<22} {"Code":<6} {"Old → New":<22} {"Δ":<8} ksaga ({"letter — name"})')
print('-'*100)
for p in sorted(proposals, key=lambda x: (x['muni'], x['code'])):
    delta = p['new_pct'] - p['old_pct']
    print(f'{p["muni"]:<22} {p["code"]:<6} {p["old_pct"]:>5}% → {p["new_pct"]:>6}%      {delta:+.2f}pp   {p["ks_letter"]} — {p["ks_name"]}')

json.dump(proposals, open(ROOT / 'temp' / 'fix_proposals.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'\nSaved {len(proposals)} proposals -> temp/fix_proposals.json')
