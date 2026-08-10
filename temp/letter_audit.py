"""Find every results2022.js entry where 2026 ballot letter ≠ kosningasaga 2022 letter.
Per the new rule: those entries should be removed (site shows N/A)."""
import re, sys, io, json, hashlib, urllib.request, time
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

def fetch(url):
    cache = ROOT / 'temp' / 'ksaga_cache'
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
        m = re.match(r'^([A-ZÁÉÍÓÚÝÞÆÖ])[\-–]list(?:inn|i)\s*([^\d]*?)\s+(?:[\d,\.]+\s+)?(\d{1,3}(?:[\.,]\d+)?)%\s+(\d+)\b', line)
        if m:
            try:
                pct = float(m.group(3).replace(',','.'))
                if pct > 100: continue
                rows.append({'letter': m.group(1), 'name': m.group(2).strip(), 'pct': pct, 'seats': int(m.group(4))})
            except: pass
    return rows

# Load results2022 entries
RJS = (ROOT / 'js' / 'data' / 'results2022.js').read_text(encoding='utf-8')
muni_blocks = {}
for m in re.finditer(r"^\s*([a-zA-Z]+):\s*\{\s*$([\s\S]*?)^\s*\},?\s*$", RJS, re.M):
    name = m.group(1); body = m.group(2)
    if 'parties' not in body: continue
    parties = []
    for pm in re.finditer(r"([A-Z][A-Za-z0-9]*)\s*:\s*\{\s*pct:\s*([\d\.]+)\s*,\s*seats:\s*(\d+)", body):
        parties.append({'code': pm.group(1), 'pct': float(pm.group(2)), 'seats': int(pm.group(3))})
    if parties: muni_blocks[name] = parties

# Load 2026 ballot letter from candidates.js taglines
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

def get_2026_letter(our_id, code):
    """Derive the 2026 ballot letter for the list."""
    if len(code) == 1:
        return code
    # Try parties.js name first (often "X-listi" / "X-listinn")
    name = PARTY_NAMES.get(code, '')
    m2 = re.search(r"\b([A-ZÁÉÍÓÚÝÞÆÖ])[\-–]list", name)
    if m2:
        return m2.group(1).upper()
    # Try tagline
    const = MUNI_CONST.get(our_id)
    if not const: return None
    span = find_const(CJS, const)
    if not span: return None
    body_start, body_end = span
    pat = re.compile(r'\n  ' + re.escape(code) + r'\s*:\s*\{')
    pm = pat.search(CJS, body_start, body_end)
    if not pm: return None
    chunk = CJS[pm.end():pm.end()+1500]
    tm = re.search(r"tagline:\s*'((?:[^'\\]|\\.)+)'", chunk)
    tagline = tm.group(1) if tm else ''
    m2 = re.search(r"\b([A-ZÁÉÍÓÚÝÞÆÖ])[\-–]list", tagline)
    if m2:
        return m2.group(1).upper()
    return None

# Audit
print('Letter-mismatch audit (2026 ballot letter vs 2022 kosningasaga letter):\n')
mismatches = []
for our_id, parties in muni_blocks.items():
    ks_slug = JS_TO_KSAGA.get(our_id)
    if not ks_slug or ks_slug not in URL_BY_SLUG: continue
    try:
        ks_rows = parse_ksaga(fetch(URL_BY_SLUG[ks_slug]))
    except Exception: continue
    ks_letters = set(r['letter'] for r in ks_rows)
    for p in parties:
        L_2026 = get_2026_letter(our_id, p['code'])
        if L_2026 is None: continue
        if L_2026 not in ks_letters:
            # The list letter doesn't exist in 2022 → either truly new OR we paired wrongly before
            mismatches.append({'muni': our_id, 'code': p['code'], 'our_pct': p['pct'], 'our_seats': p['seats'],
                                '2026_letter': L_2026, 'available_2022_letters': sorted(ks_letters)})

print(f'{len(mismatches)} entries with no 2022 row matching the 2026 ballot letter:\n')
for m in mismatches:
    print(f'  {m["muni"]:<22} {m["code"]:<6}  2026=L{m["2026_letter"]}  cur={m["our_pct"]}%/{m["our_seats"]}  ksaga letters: {m["available_2022_letters"]}')
