#!/usr/bin/env python3
"""
For each ❓ list (compound key, first letter doesn't match island.is letter),
try to find which island.is list it actually corresponds to by name overlap,
then check if it matches.
"""
import json, re

with open('island_candidates.json', encoding='utf-8') as f:
    island_data = json.load(f)

with open('../js/data/candidates.js', encoding='utf-8') as f:
    js_src = f.read()

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

# Build island data indexed by muni_id
island_by_muni = {}
for muni_name, parties in island_data.items():
    muni_id = MUNI_MAP.get(muni_name)
    if muni_id:
        island_by_muni[muni_id] = parties  # list_name -> [candidate_names]

# Parse our DB
real_data_match = re.search(r'const REAL_DATA\s*=\s*\{([^}]+)\}', js_src, re.DOTALL)
muni_var_map = {}
for m in re.finditer(r'(\w+):\s*([A-Z]+)\b', real_data_match.group(1)):
    muni_var_map[m.group(1)] = m.group(2)

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
            ls = lm.end() - 1
            d3, lp = 0, ls
            while lp < len(pb):
                if pb[lp] == '[': d3 += 1
                elif pb[lp] == ']':
                    d3 -= 1
                    if d3 == 0: break
                lp += 1
            lb = pb[ls:lp+1]
            names = re.findall(r'\[\s*\d+\s*,\s*[\'"]([^\'"]+)[\'"]', lb)
            party_data[pc] = names
    if party_data:
        var_data[var_name] = party_data

def get_letter(list_name):
    m = re.match(r'^([A-ZÁÉÍÓÚÝÞÆÖÐ])\s+listi', list_name)
    return m.group(1) if m else None

# Cases already verified by original script or first unchecked_lists run:
VERIFIED_OK = {'akureyri/AL', 'gardabaer/GB', 'horgarsv/HGH', 'hunathing/NHV',
               'hveragerdi/OKH', 'rangarthingeystra/NRE', 'reykholar/ROA',
               'seltjarnarnes/SCS', 'svalbardsstrond/SVSS', 'vesturbyggd/NYS',
               'kjosarhreppur/KJA', 'snaefellsbaer/D', 'tjornes/TJN', 'vopnafjordur/VOP'}

lines = ['RESOLUTION OF ❓ LISTS (compound keys matched by name overlap)',
         '=' * 70, '']

for muni_id, var_name in sorted(muni_var_map.items()):
    our_data = var_data.get(var_name, {})
    island_parties = island_by_muni.get(muni_id, {})

    for party_code, our_names in sorted(our_data.items()):
        key = f'{muni_id}/{party_code}'
        if key in VERIFIED_OK:
            continue

        # Was it verified by original script?
        first_letter = party_code[0]
        by_letter = {}
        for ln, ns in island_parties.items():
            l = get_letter(ln)
            if l:
                by_letter[l] = (ln, ns)
        if first_letter in by_letter:
            continue  # already covered by original script comparison

        # ❓ case: try to find best-matching island.is list by name overlap
        our_set = set(our_names)
        best_match = None
        best_overlap = 0
        for list_name, island_names in island_parties.items():
            island_set = set(island_names)
            overlap = len(our_set & island_set)
            if overlap > best_overlap:
                best_overlap = overlap
                best_match = (list_name, island_names, island_set)

        lines.append(f'── {muni_id}  [{party_code}]  ({len(our_names)} candidates)')

        if not island_parties:
            lines.append(f'   ⚠️  NOT IN island_candidates.json — need live verification')
            lines.append(f'   Our names: {", ".join(our_names[:5])}{"..." if len(our_names)>5 else ""}')
        elif best_match is None or best_overlap == 0:
            lines.append(f'   ❌ NO OVERLAP with any island.is list')
            lines.append(f'   Island.is lists: {list(island_parties.keys())}')
            lines.append(f'   Our names: {", ".join(our_names[:5])}{"..." if len(our_names)>5 else ""}')
        else:
            list_name, island_names, island_set = best_match
            only_island = island_set - our_set
            only_ours = our_set - island_set
            pct = round(best_overlap / max(len(island_set), len(our_set)) * 100)
            status = '✓ MATCH' if not only_island and not only_ours else f'❌ MISMATCH ({pct}% overlap)'
            lines.append(f'   Best match: "{list_name}"  [{status}]')
            lines.append(f'   island.is={len(island_names)} ours={len(our_names)} overlap={best_overlap}')
            if only_island:
                for n in sorted(only_island): lines.append(f'      + ISLAND ONLY: {n}')
            if only_ours:
                for n in sorted(only_ours): lines.append(f'      - OUR DB ONLY: {n}')
            if not only_island and not only_ours:
                lines.append(f'      All {len(our_names)} candidates match ✓')
        lines.append('')

report = '\n'.join(lines)
with open('resolve_unknown_report.txt', 'w', encoding='utf-8') as f:
    f.write(report)
print(report)
