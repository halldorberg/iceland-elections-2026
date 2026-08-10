"""Walk candidates.js, find every party with a non-empty agenda,
and categorize the source of that agenda from its platformUrl.
"""
import re, json, sys, io
from urllib.parse import urlparse
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r'F:\Claude Projects\iceland-elections')
CJS = (ROOT / 'js' / 'data' / 'candidates.js').read_text(encoding='utf-8')

# Map muni const → muni name
MUNI_NAMES = {
    'RVK':'Reykjavík','KOP':'Kópavogur','HAF':'Hafnarfjörður','GAR':'Garðabær',
    'MOS':'Mosfellsbær','AKU':'Akureyri','SEL':'Seltjarnarnes','RNB':'Reykjanesbær',
    'VOG':'Vogar','GRN':'Grindavík','SNB':'Suðurnesjabær','ARB':'Árborg',
    'VME':'Vestmannaeyjar','NPG':'Norðurþing','FJB':'Fjallabyggð','FJD':'Fjarðabyggð',
    'HFJ':'Hornafjörður','AKR':'Akranes','BBD':'Borgarbyggð','ISF':'Ísafjörður',
    'HVG':'Hveragerði','RTE':'Rangárþing eystra','RTY':'Rangárþing ytra','OLF':'Ölfus',
    'SKR':'Skaftárhreppur','MYR':'Mýrdalshreppur','BSG':'Bláskógabyggð','FHR':'Flóahreppur',
    'HMR':'Hrunamannahreppur','GGR':'Grímsnes- og Grafningshr.','SGN':'Skeiða- og Gnúpverjahr.',
    'DVB':'Dalvíkurbyggð','EJA':'Eyjafjarðarsveit','HGS':'Hörgársveit','HNB':'Húnabyggð',
    'HNT':'Húnaþing vestra','SFJ':'Skagafjörður','SST':'Skagaströnd','STK':'Stykkishólmur',
    'GFJ':'Grundarfjörður','BLV':'Bolungarvík','SDV':'Súðavík','VBG':'Vesturbyggð',
    'STD':'Strandabyggð','RKH':'Reykhólar','MUT':'Múlaþing','THV':'Þingeyjarsveit',
    'HVF':'Hvalfjarðarsveit','SNF':'Snæfellsbær','SVS':'Svalbarðsströnd','KJO':'Kjósarhreppur',
    'VPF':'Vopnafjörður','TJR':'Tjörnes','ARN':'Árneshreppur',
}

# Walk top-level const blocks to find parties
def find_const_blocks():
    blocks = {}
    for m in re.finditer(r'^const ([A-Z][A-Z0-9]{0,5}) = \{', CJS, re.M):
        const = m.group(1)
        if const in MUNI_NAMES:
            open_pos = m.end() - 1
            depth = 0; i = open_pos; in_str = None
            while i < len(CJS):
                c = CJS[i]
                if in_str:
                    if c == '\\': i += 2; continue
                    if c == in_str: in_str = None
                    i += 1; continue
                if c in ("'", '"', '`'): in_str = c; i += 1; continue
                if c == '{': depth += 1
                elif c == '}':
                    depth -= 1
                    if depth == 0: break
                i += 1
            blocks[const] = (open_pos+1, i)
    return blocks

def find_party_blocks(src, body_start, body_end):
    parties = {}
    for pm in re.finditer(r'\n  ([A-Z][A-Za-z0-9_]*)\s*:\s*\{', src[body_start:body_end]):
        code = pm.group(1)
        if code in ('list', 'tagline', 'agenda', 'platformUrl'):
            continue
        i = body_start + pm.end() - 1
        depth = 0; in_str = None
        while i < body_end:
            c = src[i]
            if in_str:
                if c == '\\': i += 2; continue
                if c == in_str: in_str = None
                i += 1; continue
            if c in ("'", '"', '`'): in_str = c; i += 1; continue
            if c == '{': depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0: break
            i += 1
        parties[code] = (body_start + pm.end() - 1, i+1)
    return parties

def get_field(text, name):
    m = re.search(name + r":\s*'((?:[^'\\]|\\.)*)'", text)
    if not m: return None
    return m.group(1).replace("\\'","'").replace("\\\\", "\\")

def count_agenda(text):
    m = re.search(r'agenda:\s*\[((?:.|\n)*?)\]', text)
    if not m: return 0
    body = m.group(1)
    return len(re.findall(r'\{\s*icon:', body))

# Categorize URL
def categorize(url):
    if not url: return 'no platformUrl'
    p = urlparse(url.lower())
    h = p.hostname or ''
    path = p.path or ''
    # Heyzine / fliphtml5 (PDF flipbooks)
    if 'heyzine.com' in h: return 'official: heyzine flipbook'
    if 'fliphtml5.com' in h: return 'official: fliphtml5 flipbook'
    # Issuu (PDF)
    if 'issuu.com' in h: return 'official: issuu publication'
    # Facebook
    if 'facebook.com' in h or 'fb.com' in h:
        if '/groups/' in path: return 'official: FB group'
        return 'official: FB page/post'
    # Instagram
    if 'instagram.com' in h: return 'official: Instagram'
    # Wordpress / blog
    if 'wordpress.com' in h: return 'blog/news article'
    if 'blogspot' in h: return 'blog/news article'
    # Major news outlets — usually a candidate quote, not the party platform
    NEWS = ['ruv.is','kosningaprof.ruv.is','mbl.is','visir.is','dv.is','vb.is','heimildin.is',
            'kjarninn.is','stundin.is','frettabladid.is','frettatiminn.is','althingi.is',
            'kaffid.is','vikubladid.is','sunnlenska.is','austurfrett.is','bb.is','bbl.is',
            'austurglugginn.is','dfs.is','feykir.is','skessuhorn.is','vf.is','trolli.is',
            'aknoll.is']
    if h in NEWS or any(n in h for n in NEWS):
        return 'news article'
    # National party central sites
    PARTY_NATIONAL = {
        'xd.is':'D-listi (Sjálfstæðisflokkurinn)',
        'framsokn.is':'B-listi (Framsóknarflokkurinn)',
        'samfylkingin.is':'S-listi (Samfylkingin)',
        'vinstri.is':'V-listi (VG)',
        'vg.is':'V-listi (VG)',
        'vidreisn.is':'C-listi (Viðreisn)',
        'midflokkurinn.is':'M-listi (Miðflokkurinn)',
        'piratar.is':'P-listi (Píratar)',
        'sosialistaflokkurinn.is':'J-listi (Sósíalistaflokkurinn)',
        'flokkurfolksins.is':'F-listi (Flokkur fólksins)',
    }
    for dom, label in PARTY_NATIONAL.items():
        if dom in h: return f'official: national party site ({label})'
    # Local list sites typically have own .is domain
    if h.endswith('.is') and not any(n in h for n in NEWS):
        return 'official: local-list website'
    return f'unknown: {h}'

# Walk
rows = []
const_blocks = find_const_blocks()
for const, (s, e) in const_blocks.items():
    parties = find_party_blocks(CJS, s, e)
    for code, (ps, pe) in parties.items():
        block = CJS[ps:pe]
        n_agenda = count_agenda(block)
        if n_agenda == 0:
            continue
        platform_url = get_field(block, 'platformUrl')
        category = categorize(platform_url)
        rows.append({
            'muni': MUNI_NAMES.get(const, const),
            'code': code,
            'agenda_items': n_agenda,
            'platform_url': platform_url or '',
            'category': category,
        })

rows.sort(key=lambda r: (r['muni'], r['code']))

# Print summary
from collections import Counter
cat_counts = Counter(r['category'] for r in rows)
print(f'Parties with agendas: {len(rows)}\n')
print('=== category breakdown ===')
for cat, n in cat_counts.most_common():
    print(f'  {n:3d}  {cat}')
print()

# Save
json.dump(rows, open(ROOT / 'temp' / 'agenda_source_audit.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'wrote temp/agenda_source_audit.json ({len(rows)} rows)')
