#!/usr/bin/env python3
"""
For every municipality where list sizes differ, compare our counts
against island.is (island_candidates.json).
"""
import re, json

with open('island_candidates.json', encoding='utf-8') as f:
    island_data = json.load(f)

with open('../js/data/candidates.js', encoding='utf-8') as f:
    js_src = f.read()

with open('../js/data/municipalities.js', encoding='utf-8') as f:
    muni_src = f.read()

# municipality name map
MUNI_MAP = {
    'Reykjavíkurborg': 'reykjavik', 'Kópavogsbær': 'kopavogur',
    'Hafnarfjarðarbær': 'hafnarfjordur', 'Garðabær': 'gardabaer',
    'Mosfellsbær': 'mosfellsbaer', 'Akureyrarbær': 'akureyri',
    'Seltjarnarnesbær': 'seltjarnarnes', 'Reykjanesbær': 'reykjanesbaer',
    'Sveitarfélagið Vogar': 'vogar', 'Grindavíkurbær': 'grindavik',
    'Suðurnesjabær': 'sudurnesjabaer', 'Sveitarfélagið Árborg': 'arborg',
    'Vestmannaeyjabær': 'vestmannaeyjar', 'Norðurþing': 'nordurping',
    'Fjallabyggð': 'fjallabyggd', 'Fjarðabyggð': 'fjardabyggd',
    'Sveitarfélagið Hornafjörður': 'hornafjordur', 'Akraneskaupstaður': 'akranes',
    'Sameinað sveitarfélag Borgarbyggðar og Skorradalshrepps': 'borgarbyggd',
    'Ísafjarðarbær': 'isafjordur', 'Hveragerðisbær': 'hveragerdi',
    'Rangárþing eystra': 'rangarthingeystra', 'Rangárþing ytra': 'rangarthingytra',
    'Sveitarfélagið Ölfus': 'olfus', 'Skaftárhreppur': 'skaftarhreppur',
    'Mýrdalshreppur': 'myrdalshr', 'Bláskógabyggð': 'blaskogabyggd',
    'Flóahreppur': 'floahreppur', 'Hrunamannahreppur': 'hrunamannahreppur',
    'Grímsnes- og Grafningshreppur': 'grimsnesgrafningur',
    'Skeiða- og Gnúpverjahreppur': 'skeidagnup', 'Dalvíkurbyggð': 'dalvikurbyggd',
    'Eyjafjarðarsveit': 'eyjafjardarsveit', 'Hörgársveit': 'horgarsv',
    'Húnabyggð': 'hunabyggd', 'Húnaþing vestra': 'hunathing',
    'Skagafjörður': 'skagafjordur', 'Sveitarfélagið Skagaströnd': 'skagastrond',
    'Sveitarfélagið Stykkishólmur': 'stykkisholmur',
    'Grundarfjarðarbær': 'grundarfjordur', 'Bolungarvíkurkaupstaður': 'bolungarvik',
    'Súðavíkurhreppur': 'sudavik', 'Vesturbyggð': 'vesturbyggd',
    'Strandabyggð': 'strandabyggd', 'Reykhólahreppur': 'reykholar',
    'Múlaþing': 'mulathing', 'Þingeyjarsveit': 'thingeyjarsveit',
    'Hvalfjarðarsveit': 'hvalfjardarsveit',
    'Snæfellsbær - sjálfkjörið': 'snaefellsbaer',
    'Svalbarðsstrandarhreppur': 'svalbardsstrond',
    'Kjósarhreppur - sjálfkjörið': 'kjosarhreppur',
    'Vopnafjarðarhreppur - sjálfkjörið': 'vopnafjordur',
    'Tjörneshreppur - sjálfkjörið': 'tjornes',
    'Árneshreppur': 'arneshr',
}
island_name_for = {v: k for k, v in MUNI_MAP.items()}

# Parse REAL_DATA
real_data_match = re.search(r'const REAL_DATA\s*=\s*\{([^}]+)\}', js_src, re.DOTALL)
muni_var_map = {}
for m in re.finditer(r'(\w+):\s*([A-Z]+)\b', real_data_match.group(1)):
    muni_var_map[m.group(1)] = m.group(2)

# Parse var_data
var_data = {}
for cb in re.finditer(r'\bconst\s+([A-Z]{2,4})\s*=\s*\{', js_src):
    var_name = cb.group(1)
    if var_name == 'REAL_DATA': continue
    start = cb.end() - 1
    depth, pos = 0, start
    while pos < len(js_src):
        if js_src[pos] == '{': depth += 1
        elif js_src[pos] == '}':
            depth -= 1
            if depth == 0: break
        pos += 1
    block = js_src[start:pos+1]
    party_data = {}
    for pm in re.finditer(r'\b([A-Z]{1,5})\s*:\s*\{', block):
        pc = pm.group(1)
        p_start = pm.end() - 1
        d2, pp = 0, p_start
        while pp < len(block):
            if block[pp] == '{': d2 += 1
            elif block[pp] == '}':
                d2 -= 1
                if d2 == 0: break
            pp += 1
        pb = block[p_start:pp+1]
        lm = re.search(r'\blist\s*:\s*\[', pb)
        if lm:
            ls = lm.end()-1; d3, lp = 0, ls
            while lp < len(pb):
                if pb[lp] == '[': d3 += 1
                elif pb[lp] == ']':
                    d3 -= 1
                    if d3 == 0: break
                lp += 1
            names = re.findall(r'\[\s*\d+\s*,\s*[\'"]([^\'"]+)[\'"]', pb[ls:lp+1])
            party_data[pc] = names
    if party_data:
        var_data[var_name] = party_data

# Parse partyIds
munis = []
for m in re.finditer(
    r'\{\s*id\s*:\s*[\'"](\w+)[\'"].*?name\s*:\s*[\'"]([^\'"]+)[\'"].*?partyIds\s*:\s*(\[[^\]]*\])',
    muni_src, re.DOTALL
):
    muni_id = m.group(1)
    name = m.group(2)
    party_ids = re.findall(r'[\'"]([^\'"]+)[\'"]', m.group(3))
    munis.append({'id': muni_id, 'name': name, 'partyIds': party_ids})

def get_letter(list_name):
    m = re.match(r'^([A-ZÁÉÍÓÚÝÞÆÖÐ])\s+listi', list_name)
    return m.group(1) if m else None

# Find outliers and compare
print('OUTLIER MUNICIPALITIES — counts differ across lists')
print('=' * 70)

for muni in munis:
    pid = muni['id']
    party_ids = muni['partyIds']
    if not party_ids:
        continue
    var_name = muni_var_map.get(pid)
    if not var_name:
        continue
    our_data = var_data.get(var_name, {})
    counts = {k: len(our_data.get(k, [])) for k in party_ids}

    all_counts = list(counts.values())
    if len(set(all_counts)) <= 1:
        continue  # uniform — skip

    # Get island.is data for this municipality
    island_name = island_name_for.get(pid)
    island_parties = island_data.get(island_name, {}) if island_name else {}
    island_by_letter = {}
    for ln, names in island_parties.items():
        l = get_letter(ln)
        if l:
            island_by_letter[l] = (ln, len(names))

    print(f'\n{muni["name"]}')
    print(f'  {"Key":<8} {"Ours":>6}   {"Island.is list":<45} {"Island.is":>10}')
    print(f'  {"-"*8} {"-"*6}   {"-"*45} {"-"*10}')

    for key in party_ids:
        our_n = counts[key]
        first_letter = key[0]
        # find best island.is match
        island_info = island_by_letter.get(first_letter)
        if not island_info:
            # try matching by overlap
            our_names = set(our_data.get(key, []))
            best = None
            best_overlap = 0
            for ln, inames in island_parties.items():
                overlap = len(our_names & set(inames))
                if overlap > best_overlap:
                    best_overlap = overlap
                    best = (ln, len(inames))
            island_info = best if best else None

        if island_info:
            island_list_name, island_n = island_info
            match = '✓' if our_n == island_n else f'❌ (diff {our_n - island_n:+d})'
            print(f'  {key:<8} {our_n:>6}   {island_list_name:<45} {island_n:>10}  {match}')
        else:
            print(f'  {key:<8} {our_n:>6}   {"(not in island.is JSON)":<45} {"?":>10}')
