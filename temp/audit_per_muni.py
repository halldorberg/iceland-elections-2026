"""One row per muni: full party list from our data | full from kosningasaga | match?"""
import re, sys, io, hashlib, urllib.request, time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r'F:\Claude Projects\iceland-elections')

INDEX = (ROOT / 'temp' / 'ksaga_index.html').read_text(encoding='utf-8')
URLS = sorted(set(re.findall(r'https://kosningasaga\.wordpress\.com/sveitarstjornarkosningar/[^"\s]+-2022/', INDEX)))
URL_BY_SLUG = {u.rstrip('/').rsplit('/', 1)[-1].replace('-2022', ''): u for u in URLS}

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
    'hrunamannahreppur':'Hrunamannahreppur','grimsnesgrafningur':'Grímsnes- og Grafningshreppur',
    'skeidagnup':'Skeiða- og Gnúpverjahreppur','dalvikurbyggd':'Dalvíkurbyggð',
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
    cache = ROOT / 'temp' / 'ksaga_cache'
    cache.mkdir(parents=True, exist_ok=True)
    slug = url.rstrip('/').rsplit('/', 1)[-1].replace('-2022', '')[:40]
    h = hashlib.sha1(url.encode()).hexdigest()[:8]
    p = cache / f'{slug}_{h}.html'
    if p.exists():
        return p.read_text(encoding='utf-8')
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    text = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
    p.write_text(text, encoding='utf-8'); time.sleep(0.3)
    return text

def parse_ksaga(html):
    m = re.search(r'<div class="entry-content"[\s\S]*?</article>', html)
    body = m.group(0) if m else html
    body = re.sub(r'<br\s*/?>', '\n', body)
    body = re.sub(r'</tr>', '\n', body)
    text = re.sub(r'<[^>]+>', ' ', body); text = re.sub(r'[ \t]+', ' ', text)
    rows = []
    for line in text.split('\n'):
        line = line.strip()
        m = re.match(r'^([A-ZÁÉÍÓÚÝÞÆÖ])[\-–]listi\s+([^\d]+?)\s+(?:[\d,\.]+\s+)?(\d{1,3}(?:[\.,]\d+)?)%\s+(\d+)\b', line)
        if m:
            try:
                pct = float(m.group(3).replace(',', '.'))
                if pct > 100: continue
                rows.append((m.group(1), m.group(2).strip(), pct, int(m.group(4))))
            except: pass
    seen = set(); out = []
    for r in rows:
        if (r[0], r[1]) not in seen:
            seen.add((r[0], r[1])); out.append(r)
    return out

# Load our results2022 data
RJS = (ROOT / 'js' / 'data' / 'results2022.js').read_text(encoding='utf-8')
muni_blocks = {}
for m in re.finditer(r"^\s*([a-zA-Z]+):\s*\{\s*$([\s\S]*?)^\s*\},?\s*$", RJS, re.M):
    name = m.group(1); body = m.group(2)
    if 'parties' not in body: continue
    parties = {}
    for pm in re.finditer(r"([A-Z][A-Za-z0-9]*)\s*:\s*\{\s*pct:\s*([\d\.]+)\s*,\s*seats:\s*(\d+)", body):
        parties[pm.group(1)] = (float(pm.group(2)), int(pm.group(3)))
    if parties: muni_blocks[name] = parties

def fmt_our(parties):
    items = sorted(parties.items(), key=lambda x: -x[1][0])
    return '; '.join(f'{c} {p:.1f}%/{s}' for c, (p, s) in items)

def fmt_ksaga(rows):
    rows_sorted = sorted(rows, key=lambda r: -r[2])
    return '; '.join(f'{r[0]} {r[2]:.1f}%/{r[3]}' for r in rows_sorted)

def match_status(parties_ours, rows_ks):
    """Check if every one of our parties has a ksaga row with matching pct (within 0.15) AND seats."""
    if not rows_ks:
        return '⚠️ no ksaga data'
    # Build sorted (pct, seats) tuples for both
    ours_set = sorted([(round(p, 1), s) for c, (p, s) in parties_ours.items()])
    ks_set = sorted([(round(r[2], 1), r[3]) for r in rows_ks])
    # Each of our (pct, seats) must appear (within tolerance) in ksaga
    used = [False] * len(ks_set)
    diffs = []
    for op, os in ours_set:
        found = -1
        for i, (kp, ks) in enumerate(ks_set):
            if used[i]: continue
            if abs(op - kp) <= 0.15 and os == ks:
                used[i] = True; found = i; break
        if found < 0:
            diffs.append(f'{op}/{os}')
    if not diffs:
        return '✅ Match'
    return f'❌ {len(diffs)} of {len(ours_set)} not found: ' + ', '.join(diffs)

# Build report
print('| # | Municipality | Our data (code pct/seats) | Kosningasaga data (letter pct/seats) | Match? |')
print('|---|---|---|---|---|')
for i, our_id in enumerate(sorted(muni_blocks.keys(), key=lambda k: MUNI_NAMES.get(k, k)), 1):
    parties = muni_blocks[our_id]
    name = MUNI_NAMES.get(our_id, our_id)
    ksaga_slug = JS_TO_KSAGA.get(our_id)
    rows_ks = []
    if ksaga_slug is None:
        ks_str = '⚠️ no kosningasaga 2022 page exists'
    elif ksaga_slug not in URL_BY_SLUG:
        ks_str = f'⚠️ slug "{ksaga_slug}" not in kosningasaga URL index'
    else:
        try:
            html = fetch(URL_BY_SLUG[ksaga_slug])
            rows_ks = parse_ksaga(html)
            ks_str = fmt_ksaga(rows_ks) if rows_ks else '⚠️ page found, no parseable rows'
        except Exception as e:
            ks_str = f'⚠️ fetch err: {e}'
    status = match_status(parties, rows_ks) if rows_ks else 'n/a'
    our_str = fmt_our(parties)
    print(f'| {i} | **{name}** | {our_str} | {ks_str} | {status} |')
