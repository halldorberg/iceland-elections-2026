"""Coverage report: photos, news, agendas across the entire site."""
import re, sys, io, json
from pathlib import Path
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r'F:\Claude Projects\iceland-elections')

CJS = (ROOT / 'js' / 'data' / 'candidates.js').read_text(encoding='utf-8')

# Map muni id to const
m = re.search(r"const REAL_DATA = \{([^}]+)\}", CJS)
MUNI_TO_CONST = {}
CONST_TO_MUNI = {}
if m:
    for pm in re.finditer(r"(\w+):\s*([A-Z]+)", m.group(1)):
        MUNI_TO_CONST[pm.group(1)] = pm.group(2)
        CONST_TO_MUNI[pm.group(2)] = pm.group(1)

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

def find_const_block(src, const):
    m = re.search(r'^const ' + re.escape(const) + r'\s*=\s*\{', src, re.M)
    if not m: return None
    open_pos = m.end() - 1
    depth = 0; i = open_pos
    while i < len(src):
        c = src[i]
        if c == '/' and i+1<len(src) and src[i+1] == '/':
            i = src.find('\n', i+2); i = i if i != -1 else len(src); continue
        if c == '/' and i+1<len(src) and src[i+1] == '*':
            j = src.find('*/', i+2); i = (j+2) if j != -1 else len(src); continue
        if c in ("'", '"', '`'):
            q = c; i += 1
            while i < len(src):
                if src[i]=='\\': i+=2; continue
                if src[i]==q: i+=1; break
                i += 1
            continue
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: return open_pos+1, i
        i += 1

def party_blocks(src, const):
    span = find_const_block(src, const)
    if not span: return []
    body_start, body_end = span
    parties = []
    pat = re.compile(r'\n  ([A-Z][A-Za-z0-9]*)\s*:\s*\{')
    for pm in pat.finditer(src, body_start, body_end):
        code = pm.group(1)
        # find end of this party block
        i = pm.end() - 1; depth = 0; in_str = None
        while i < body_end:
            c = src[i]
            if in_str:
                if c == '\\': i+=2; continue
                if c == in_str: in_str = None
                i+=1; continue
            if c in ("'", '"', '`'): in_str = c; i+=1; continue
            if c == '{': depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0: break
            i += 1
        parties.append({'code': code, 'start': pm.end()-1, 'end': i+1})
    return parties

def parse_party(party_text):
    """Extract: agenda count, list rows (each with name, has_image, has_news)."""
    # Agenda
    am = re.search(r'agenda:\s*\[(.*?)\]\s*,?\s*(?:platformUrl|list)', party_text, re.S)
    agenda_count = 0
    if am:
        agenda_count = len(re.findall(r"\{\s*icon:", am.group(1)))
    # platformUrl
    pum = re.search(r"platformUrl:\s*'([^']+)'", party_text)
    platform_url = pum.group(1) if pum else None
    # tagline
    tlm = re.search(r"tagline:\s*'((?:[^'\\]|\\.)+)'", party_text)
    tagline = tlm.group(1) if tlm else ''
    # list block
    lm = re.search(r'list:\s*\[', party_text)
    if not lm:
        return {'agenda_count': agenda_count, 'platform_url': platform_url, 'tagline': tagline, 'rows': []}
    # Walk to matching ]
    list_start = lm.end() - 1
    i = list_start; depth = 0; in_str = None
    while i < len(party_text):
        c = party_text[i]
        if in_str:
            if c == '\\': i+=2; continue
            if c == in_str: in_str = None
            i+=1; continue
        if c in ("'", '"', '`'): in_str = c; i+=1; continue
        if c == '[': depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0: break
        i += 1
    list_text = party_text[list_start+1:i]
    # Find each row [N, ...]
    rows = []
    j = 0
    while j < len(list_text):
        rm = re.search(r'\n\s+\[\s*(\d+)\s*,', list_text[j:])
        if not rm: break
        row_start = j + rm.start() + len(rm.group(0)) - len(rm.group(0).lstrip())
        # Find the [ position
        bracket_pos = list_text.find('[', j + rm.start())
        # Walk to matching ]
        k = bracket_pos; rdepth = 0; rinstr = None
        while k < len(list_text):
            c = list_text[k]
            if rinstr:
                if c == '\\': k+=2; continue
                if c == rinstr: rinstr = None
                k+=1; continue
            if c in ("'", '"', '`'): rinstr = c; k+=1; continue
            if c == '[': rdepth += 1
            elif c == ']':
                rdepth -= 1
                if rdepth == 0: break
            k += 1
        row_text = list_text[bracket_pos:k+1]
        # Extract name (2nd element)
        nm = re.match(r"\[\s*(\d+)\s*,\s*'((?:[^'\\]|\\.)*)'", row_text)
        name = nm.group(2) if nm else '?'
        # Has image: a string like 'images/candidates/...' anywhere
        has_image = bool(re.search(r"'images/candidates/[^']+\.(?:jpg|jpeg|png|webp)'", row_text))
        # Has news: "news: [{ ... }" with at least one entry
        news_m = re.search(r'news:\s*\[(.*?)\]\s*\}\s*\]\s*$', row_text, re.S)
        if news_m:
            has_news = bool(re.search(r"\{\s*(title|url):", news_m.group(1)))
        else:
            # alt: news:[{}] inline
            has_news = 'news: [{' in row_text or "news: [ {" in row_text
        rows.append({'ballot': int(rm.group(1)), 'name': name, 'has_image': has_image, 'has_news': has_news})
        j = k + 1
    return {'agenda_count': agenda_count, 'platform_url': platform_url, 'tagline': tagline, 'rows': rows}

# Walk every muni → every party
muni_data = []
total_cands = 0; with_image = 0; with_news = 0
total_parties = 0; with_agenda = 0; without_agenda = []
party_stats = []
for muni_id, const in MUNI_TO_CONST.items():
    parties = party_blocks(CJS, const)
    for p in parties:
        ptext = CJS[p['start']:p['end']]
        d = parse_party(ptext)
        rows = d['rows']
        n = len(rows)
        if n == 0: continue
        total_parties += 1
        ag = d['agenda_count']
        if ag > 0: with_agenda += 1
        else: without_agenda.append((muni_id, const, p['code'], d['tagline'][:60]))
        total_cands += n
        ni = sum(1 for r in rows if r['has_image'])
        nn = sum(1 for r in rows if r['has_news'])
        with_image += ni; with_news += nn
        party_stats.append({
            'muni_id': muni_id, 'const': const, 'code': p['code'],
            'tagline': d['tagline'][:60], 'n': n, 'with_image': ni, 'with_news': nn,
            'agenda_count': ag, 'platform_url': d['platform_url'],
        })

print('===========================================')
print(f'TOTAL: {total_cands} candidates across {total_parties} party-lists in {len(MUNI_TO_CONST)} municipalities')
print('===========================================')
print(f'\nPHOTOS:    {with_image:>4}/{total_cands} ({100*with_image/total_cands:5.1f}%)  ·  no photo: {total_cands-with_image}')
print(f'NEWS:      {with_news:>4}/{total_cands} ({100*with_news/total_cands:5.1f}%)  ·  no news: {total_cands-with_news}')
print(f'AGENDA:    {with_agenda:>4}/{total_parties} ({100*with_agenda/total_parties:5.1f}%) of lists  ·  no agenda: {total_parties-with_agenda}')

# Save full breakdown
import json
with open(ROOT / 'temp' / 'coverage_breakdown.json', 'w', encoding='utf-8') as f:
    json.dump({'total_candidates': total_cands, 'with_image': with_image, 'with_news': with_news,
               'total_parties': total_parties, 'with_agenda': with_agenda,
               'without_agenda': without_agenda, 'party_stats': party_stats}, f, ensure_ascii=False, indent=2)

# Per-muni breakdown by photo coverage
print('\n=== PHOTO COVERAGE BY LIST (worst first, only those <100%) ===')
party_stats.sort(key=lambda p: (p['with_image']/p['n'] if p['n'] else 0, -p['n']))
for p in party_stats:
    pct = 100*p['with_image']/p['n']
    if pct >= 100: continue
    muni_name = MUNI_NAMES.get(p['muni_id'], p['muni_id'])
    print(f"  {muni_name:30s} {p['code']:6s}  {p['with_image']:>2}/{p['n']:<2} ({pct:5.1f}%) — {p['tagline'][:50]}")

print(f'\n=== NEWS COVERAGE: {with_news}/{total_cands} candidates have at least one news entry ===')
print('Lists with 0 news anywhere:')
for p in sorted(party_stats, key=lambda x: x['with_news']):
    if p['with_news'] > 0: continue
    muni_name = MUNI_NAMES.get(p['muni_id'], p['muni_id'])
    print(f"  {muni_name:30s} {p['code']:6s}  ({p['n']} cand) — {p['tagline'][:50]}")

print(f'\n=== {len(without_agenda)} LISTS WITHOUT AGENDA ===')
for muni_id, const, code, tag in sorted(without_agenda, key=lambda x: MUNI_NAMES.get(x[0], x[0])):
    print(f"  {MUNI_NAMES.get(muni_id, muni_id):30s} {code:6s} — {tag}")
