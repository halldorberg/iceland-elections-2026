"""One row per LIST in every municipality.
Pair our list with its kosningasaga counterpart by (pct, seats) tuple.
Show as: muni | our list | our pct/seats | ksaga letter+name | ksaga pct/seats | match?
"""
import re, sys, io, hashlib, urllib.request, time
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
    'reykjavik':'Reykjavík','kopavogur':'Kópavogur','hafnarfjordur':'Hafnarfjörður',
    'gardabaer':'Garðabær','mosfellsbaer':'Mosfellsbær','akureyri':'Akureyri',
    'seltjarnarnes':'Seltjarnarnes','reykjanesbaer':'Reykjanesbær','vogar':'Vogar',
    'grindavik':'Grindavík','sudurnesjabaer':'Suðurnesjabær','arborg':'Árborg',
    'vestmannaeyjar':'Vestmannaeyjar','nordurping':'Norðurþing','fjallabyggd':'Fjallabyggð',
    'fjardabyggd':'Fjarðabyggð','hornafjordur':'Hornafjörður','akranes':'Akranes',
    'borgarbyggd':'Borgarbyggð','isafjordur':'Ísafjörður','hveragerdi':'Hveragerði',
    'rangarthingeystra':'Rangárþing eystra','rangarthingytra':'Rangárþing ytra',
    'olfus':'Ölfus','skaftarhreppur':'Skaftárhreppur','myrdalshr':'Mýrdalshreppur',
    'blaskogabyggd':'Bláskógabyggð','floahreppur':'Flóahreppur',
    'hrunamannahreppur':'Hrunamannahreppur','grimsnesgrafningur':'Grímsnes- og Grafningshr.',
    'skeidagnup':'Skeiða- og Gnúpverjahr.','dalvikurbyggd':'Dalvíkurbyggð',
    'eyjafjardarsveit':'Eyjafjarðarsveit','horgarsv':'Hörgársveit','hunabyggd':'Húnabyggð',
    'hunathing':'Húnaþing vestra','skagafjordur':'Skagafjörður','skagastrond':'Skagaströnd',
    'stykkisholmur':'Stykkishólmur','grundarfjordur':'Grundarfjörður','bolungarvik':'Bolungarvík',
    'sudavik':'Súðavík','vesturbyggd':'Vesturbyggð','strandabyggd':'Strandabyggð',
    'reykholar':'Reykhólar','mulathing':'Múlaþing','thingeyjarsveit':'Þingeyjarsveit',
    'hvalfjardarsveit':'Hvalfjarðarsveit','snaefellsbaer':'Snæfellsbær',
    'svalbardsstrond':'Svalbarðsströnd','kjosarhreppur':'Kjósarhreppur',
    'vopnafjordur':'Vopnafjörður','tjornes':'Tjörnes','arneshr':'Árneshreppur',
}

def fetch(url):
    cache = ROOT / 'temp' / 'ksaga_cache'; cache.mkdir(parents=True, exist_ok=True)
    slug = url.rstrip('/').rsplit('/',1)[-1].replace('-2022','')[:40]
    h = hashlib.sha1(url.encode()).hexdigest()[:8]
    p = cache / f'{slug}_{h}.html'
    if p.exists(): return p.read_text(encoding='utf-8')
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    text = urllib.request.urlopen(req, timeout=30).read().decode('utf-8','replace')
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
    seen = set(); out = []
    for r in rows:
        k = (r['letter'], r['name'])
        if k in seen: continue
        seen.add(k); out.append(r)
    return out

# Load our data
RJS = (ROOT / 'js' / 'data' / 'results2022.js').read_text(encoding='utf-8')
muni_blocks = {}
for m in re.finditer(r"^\s*([a-zA-Z]+):\s*\{\s*$([\s\S]*?)^\s*\},?\s*$", RJS, re.M):
    name = m.group(1); body = m.group(2)
    if 'parties' not in body: continue
    parties = []
    for pm in re.finditer(r"([A-Z][A-Za-z0-9]*)\s*:\s*\{\s*pct:\s*([\d\.]+)\s*,\s*seats:\s*(\d+)", body):
        parties.append({'code': pm.group(1), 'pct': float(pm.group(2)), 'seats': int(pm.group(3))})
    if parties: muni_blocks[name] = parties

# Output: one row per list
print('| Municipality | Our list (code) | Our pct/seats | Kosningasaga (letter — name) | Ksaga pct/seats | Match? |')
print('|---|---|---|---|---|---|')

def pair_lists(ours_list, ks_rows):
    """Pair each of our parties with at most one ksaga row by (pct, seats) tuple.
    Tolerance: pct within 0.15pp AND seats equal. Greedy: closest pct wins.
    Returns list of (our_or_None, ks_or_None) pairs covering both sides."""
    used_ks = [False] * len(ks_rows)
    pairs = []
    # First pass: tight match (pct within 0.15)
    for o in ours_list:
        best_i = -1; best_diff = 999
        for i, r in enumerate(ks_rows):
            if used_ks[i]: continue
            if r['seats'] != o['seats']: continue
            d = abs(r['pct'] - o['pct'])
            if d < best_diff and d <= 0.15:
                best_diff = d; best_i = i
        if best_i >= 0:
            used_ks[best_i] = True
            pairs.append((o, ks_rows[best_i], 'tight'))
        else:
            pairs.append((o, None, 'unmatched'))
    # Add unmatched ksaga rows
    for i, r in enumerate(ks_rows):
        if not used_ks[i]:
            pairs.append((None, r, 'ks-only'))
    return pairs

for our_id in sorted(muni_blocks.keys(), key=lambda k: MUNI_NAMES.get(k, k)):
    name = MUNI_NAMES.get(our_id, our_id)
    parties = muni_blocks[our_id]
    ksaga_slug = JS_TO_KSAGA.get(our_id)
    ks_rows = []; err = None
    if ksaga_slug is None:
        err = 'no kosningasaga 2022 page'
    elif ksaga_slug not in URL_BY_SLUG:
        err = f'slug "{ksaga_slug}" not in index'
    else:
        try:
            html = fetch(URL_BY_SLUG[ksaga_slug])
            ks_rows = parse_ksaga(html)
            if not ks_rows: err = 'page exists but unparseable'
        except Exception as e:
            err = f'fetch err: {e}'

    pairs = pair_lists(parties, ks_rows)
    for our, ks, kind in pairs:
        # Cells
        if our:
            our_cell = our['code']
            our_v = f"{our['pct']}%/{our['seats']}"
        else:
            our_cell = '—'; our_v = '—'
        if ks:
            ks_cell = f"{ks['letter']} — {ks['name']}"
            ks_v = f"{ks['pct']:.2f}%/{ks['seats']}"
        else:
            ks_cell = '—' if not err else f'⚠️ {err}'
            ks_v = '—'
        if kind == 'tight':
            status = '✅'
        elif kind == 'unmatched':
            status = '⚠️ no match' if err else '❌ our list, no ksaga match'
        else:
            status = '— ksaga only'
        print(f'| {name} | {our_cell} | {our_v} | {ks_cell} | {ks_v} | {status} |')
