#!/usr/bin/env python3
"""
Full verification: for every municipality, every party list, every candidate —
print island.is names vs our DB names side by side.
"""

import json
import re
import sys

# ─── Load island.is data ─────────────────────────────────────────────────────

with open('island_candidates.json', encoding='utf-8') as f:
    island_data = json.load(f)

# ─── Municipality name → our ID ───────────────────────────────────────────────

MUNI_MAP = {
    'Reykjavíkurborg':                                                   'reykjavik',
    'Kópavogsbær':                                                        'kopavogur',
    'Hafnarfjarðarbær':                                                   'hafnarfjordur',
    'Garðabær':                                                           'gardabaer',
    'Mosfellsbær':                                                        'mosfellsbaer',
    'Akureyrarbær':                                                       'akureyri',
    'Seltjarnarnesbær':                                                   'seltjarnarnes',
    'Reykjanesbær':                                                       'reykjanesbaer',
    'Sveitarfélagið Vogar':                                               'vogar',
    'Grindavíkurbær':                                                     'grindavik',
    'Suðurnesjabær':                                                      'sudurnesjabaer',
    'Sveitarfélagið Árborg':                                              'arborg',
    'Vestmannaeyjabær':                                                   'vestmannaeyjar',
    'Norðurþing':                                                         'nordurping',
    'Fjallabyggð':                                                        'fjallabyggd',
    'Fjarðabyggð':                                                        'fjardabyggd',
    'Sveitarfélagið Hornafjörður':                                        'hornafjordur',
    'Akraneskaupstaður':                                                  'akranes',
    'Sameinað sveitarfélag Borgarbyggðar og Skorradalshrepps':            'borgarbyggd',
    'Ísafjarðarbær':                                                      'isafjordur',
    'Hveragerðisbær':                                                     'hveragerdi',
    'Rangárþing eystra':                                                  'rangarthingeystra',
    'Rangárþing ytra':                                                    'rangarthingytra',
    'Sveitarfélagið Ölfus':                                               'olfus',
    'Skaftárhreppur':                                                     'skaftarhreppur',
    'Mýrdalshreppur':                                                     'myrdalshr',
    'Bláskógabyggð':                                                      'blaskogabyggd',
    'Flóahreppur':                                                        'floahreppur',
    'Hrunamannahreppur':                                                  'hrunamannahreppur',
    'Grímsnes- og Grafningshreppur':                                      'grimsnesgrafningur',
    'Skeiða- og Gnúpverjahreppur':                                        'skeidagnup',
    'Dalvíkurbyggð':                                                      'dalvikurbyggd',
    'Eyjafjarðarsveit':                                                   'eyjafjardarsveit',
    'Hörgársveit':                                                        'horgarsv',
    'Húnabyggð':                                                          'hunabyggd',
    'Húnaþing vestra':                                                    'hunathing',
    'Skagafjörður':                                                       'skagafjordur',
    'Sveitarfélagið Skagaströnd':                                         'skagastrond',
    'Sveitarfélagið Stykkishólmur':                                       'stykkisholmur',
    'Grundarfjarðarbær':                                                  'grundarfjordur',
    'Bolungarvíkurkaupstaður':                                            'bolungarvik',
    'Súðavíkurhreppur':                                                   'sudavik',
    'Vesturbyggð':                                                        'vesturbyggd',
    'Strandabyggð':                                                       'strandabyggd',
    'Reykhólahreppur':                                                    'reykholar',
    'Múlaþing':                                                           'mulathing',
    'Þingeyjarsveit':                                                     'thingeyjarsveit',
    'Hvalfjarðarsveit':                                                   'hvalfjardarsveit',
    'Snæfellsbær - sjálfkjörið':                                          'snaefellsbaer',
    'Svalbarðsstrandarhreppur':                                           'svalbardsstrond',
    'Kjósarhreppur - sjálfkjörið':                                        'kjosarhreppur',
    'Vopnafjarðarhreppur - sjálfkjörið':                                  'vopnafjordur',
    'Tjörneshreppur - sjálfkjörið':                                       'tjornes',
    'Árneshreppur':                                                       'arneshr',
}

# ─── Parse candidates.js ──────────────────────────────────────────────────────

with open('../js/data/candidates.js', encoding='utf-8') as f:
    js_src = f.read()

real_data_match = re.search(r'const REAL_DATA\s*=\s*\{([^}]+)\}', js_src, re.DOTALL)
real_data_block = real_data_match.group(1)
muni_var_map = {}
for m in re.finditer(r'(\w+):\s*([A-Z]+)\b', real_data_block):
    muni_var_map[m.group(1)] = m.group(2)

var_data = {}
const_blocks = re.finditer(r'\bconst\s+([A-Z]{2,4})\s*=\s*\{', js_src)
for cb in const_blocks:
    var_name = cb.group(1)
    if var_name in ('REAL_DATA',):
        continue
    start = cb.end() - 1
    depth = 0
    pos = start
    while pos < len(js_src):
        if js_src[pos] == '{': depth += 1
        elif js_src[pos] == '}':
            depth -= 1
            if depth == 0: break
        pos += 1
    block = js_src[start:pos+1]
    party_data = {}
    party_matches = re.finditer(r'\b([A-Z]{1,5})\s*:\s*\{', block)
    for pm in party_matches:
        party_code = pm.group(1)
        p_start = pm.end() - 1
        depth2 = 0
        p_pos = p_start
        while p_pos < len(block):
            if block[p_pos] == '{': depth2 += 1
            elif block[p_pos] == '}':
                depth2 -= 1
                if depth2 == 0: break
            p_pos += 1
        party_block = block[p_start:p_pos+1]
        list_match = re.search(r'\blist\s*:\s*\[', party_block)
        if list_match:
            l_start = list_match.end() - 1
            depth3 = 0
            l_pos = l_start
            while l_pos < len(party_block):
                if party_block[l_pos] == '[': depth3 += 1
                elif party_block[l_pos] == ']':
                    depth3 -= 1
                    if depth3 == 0: break
                l_pos += 1
            list_block = party_block[l_start:l_pos+1]
            names = re.findall(r'\[\s*\d+\s*,\s*[\'"]([^\'"]+)[\'"]', list_block)
            party_data[party_code] = names
    if party_data:
        var_data[var_name] = party_data

def get_party_letter(list_name):
    m = re.match(r'^([A-ZÁÉÍÓÚÝÞÆÖÐ])\s+listi', list_name)
    return m.group(1) if m else None

# ─── Full verification report ─────────────────────────────────────────────────

lines_out = []
total_munis = 0
total_lists = 0
total_candidates = 0
total_ok = 0
total_mismatch = 0

for island_muni_name, island_parties in sorted(island_data.items()):
    if not island_parties:
        continue
    muni_id = MUNI_MAP.get(island_muni_name)
    if not muni_id:
        continue
    var_name = muni_var_map.get(muni_id)
    if not var_name:
        continue
    our_data = var_data.get(var_name, {})
    total_munis += 1

    lines_out.append('')
    lines_out.append('=' * 72)
    lines_out.append(f'MUNICIPALITY: {island_muni_name}')

    for list_name, island_names in island_parties.items():
        party_letter = get_party_letter(list_name)
        if not party_letter:
            continue

        our_names = our_data.get(party_letter, [])
        if not our_names:
            for code, names in our_data.items():
                if code.startswith(party_letter) and len(code) > 1:
                    our_names = names
                    break

        if not our_names:
            continue

        total_lists += 1
        island_set = set(island_names)
        our_set = set(our_names)
        only_island = island_set - our_set
        only_ours = our_set - island_set

        if only_island or only_ours:
            status = '❌ MISMATCH'
            total_mismatch += 1
        else:
            status = '✓ OK'
            total_ok += 1

        lines_out.append(f'  {list_name}  [{status}]  island.is={len(island_names)} ours={len(our_names)}')
        total_candidates += len(island_names)

        if only_island or only_ours:
            for n in sorted(only_island):
                lines_out.append(f'      + ISLAND ONLY: {n}')
            for n in sorted(only_ours):
                lines_out.append(f'      - OUR DB ONLY: {n}')
        else:
            # Print all matched candidates
            for name in island_names:
                lines_out.append(f'      ✓ {name}')

lines_out.insert(0, f'FULL VERIFICATION REPORT')
lines_out.insert(1, f'Municipalities checked: {total_munis}')
lines_out.insert(2, f'Party lists checked:    {total_lists}')
lines_out.insert(3, f'Candidates verified:    {total_candidates}')
lines_out.insert(4, f'Lists with mismatches:  {total_mismatch}')
lines_out.insert(5, f'Lists fully matching:   {total_ok}')
lines_out.insert(6, '')

report = '\n'.join(lines_out)

with open('full_verification_report.txt', 'w', encoding='utf-8') as f:
    f.write(report)

print('\n'.join(lines_out[:7]))
if total_mismatch == 0:
    print('\n✓ ALL LISTS MATCH ISLAND.IS EXACTLY\n')
else:
    print(f'\n❌ {total_mismatch} LISTS HAVE MISMATCHES — SEE full_verification_report.txt\n')
