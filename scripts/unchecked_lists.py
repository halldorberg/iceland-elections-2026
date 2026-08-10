#!/usr/bin/env python3
"""
Find every party list in our DB that was NOT covered by the comparison script,
and explain why: compound key, not in island.is, or genuinely missing data.
"""

import json, re, sys

# ── Load island.is data ─────────────────────────────────────────────────────

with open('island_candidates.json', encoding='utf-8') as f:
    island_data = json.load(f)

# Build: island_muni_name -> { party_letter -> [names] }
island_by_letter = {}
def get_letter(list_name):
    m = re.match(r'^([A-ZÁÉÍÓÚÝÞÆÖÐ])\s+listi', list_name)
    return m.group(1) if m else None

for muni_name, parties in island_data.items():
    island_by_letter[muni_name] = {}
    for list_name, names in parties.items():
        letter = get_letter(list_name)
        if letter:
            island_by_letter[muni_name][letter] = (list_name, names)

# ── Parse candidates.js ──────────────────────────────────────────────────────

with open('../js/data/candidates.js', encoding='utf-8') as f:
    js_src = f.read()

# REAL_DATA: muniId -> varName
real_data_match = re.search(r'const REAL_DATA\s*=\s*\{([^}]+)\}', js_src, re.DOTALL)
real_data_block = real_data_match.group(1)
muni_var_map = {}
for m in re.finditer(r'(\w+):\s*([A-Z]+)\b', real_data_block):
    muni_var_map[m.group(1)] = m.group(2)

# Extract all const VARNAME = { PARTYKEY: { list: [...] } }
var_data = {}
for cb in re.finditer(r'\bconst\s+([A-Z]{2,4})\s*=\s*\{', js_src):
    var_name = cb.group(1)
    if var_name == 'REAL_DATA':
        continue
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
        party_code = pm.group(1)
        p_start = pm.end() - 1
        depth2, p_pos = 0, p_start
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
            depth3, l_pos = 0, l_start
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

# ── Reverse map: island.is muni name -> our muni ID ─────────────────────────

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

# ── Determine what was "checked" by old compare script ───────────────────────
# A list was checked if: muni in MUNI_MAP, var in REAL_DATA, and party_code
# is a single letter that matches an island.is list letter exactly.

checked = set()   # (muni_id, party_code)
for island_name, by_letter in island_by_letter.items():
    muni_id = MUNI_MAP.get(island_name)
    if not muni_id: continue
    var_name = muni_var_map.get(muni_id)
    if not var_name: continue
    our_data = var_data.get(var_name, {})
    for letter, (list_name, inames) in by_letter.items():
        if letter in our_data:
            checked.add((muni_id, letter))

# ── Find all our lists ────────────────────────────────────────────────────────

all_our_lists = []
for muni_id, var_name in sorted(muni_var_map.items()):
    our_data = var_data.get(var_name, {})
    for party_code, names in sorted(our_data.items()):
        all_our_lists.append((muni_id, var_name, party_code, names))

# ── Classify each unchecked list ─────────────────────────────────────────────

lines = []
lines.append('UNCHECKED LISTS ANALYSIS')
lines.append(f'Total lists in our DB: {len(all_our_lists)}')
lines.append(f'Lists verified by comparison script: {len(checked)}')
lines.append(f'Unchecked: {len(all_our_lists) - len(checked)}')
lines.append('')

unchecked_count = 0
for muni_id, var_name, party_code, our_names in all_our_lists:
    if (muni_id, party_code) in checked:
        continue
    unchecked_count += 1

    island_name = island_name_for.get(muni_id, '???')
    by_letter = island_by_letter.get(island_name, {})

    # What is the first letter of our party_code?
    first_letter = party_code[0]

    # Is there a matching island.is list by first letter?
    island_match = by_letter.get(first_letter)

    lines.append(f'── {muni_id}  [{var_name}/{party_code}]  ({len(our_names)} candidates)')

    if island_name == '???':
        lines.append(f'   STATUS: ⚠️  Municipality not in MUNI_MAP — cannot verify vs island.is')
    elif not by_letter:
        lines.append(f'   STATUS: ⚠️  Island.is has no lists for this municipality in our JSON')
        lines.append(f'          (municipality IS in island.is but island_candidates.json may be incomplete)')
    elif island_match is None:
        # No island.is list starting with that letter at all
        all_island_letters = sorted(by_letter.keys())
        lines.append(f'   STATUS: ❓  No island.is "{first_letter}" list — island.is letters: {all_island_letters}')
        lines.append(f'          Our names: {", ".join(our_names)}')
    else:
        # There IS a matching island.is list — it was just skipped because our
        # code uses a compound key. Compare now.
        island_list_name, island_names = island_match
        island_set = set(island_names)
        our_set = set(our_names)
        only_island = island_set - our_set
        only_ours = our_set - island_set

        if only_island or only_ours:
            status = '❌ MISMATCH'
        else:
            status = '✓ MATCH'

        lines.append(f'   Island.is list: "{island_list_name}"  [{status}]')
        lines.append(f'   island.is={len(island_names)} ours={len(our_names)}')
        if only_island:
            for n in sorted(only_island):
                lines.append(f'      + ISLAND ONLY: {n}')
        if only_ours:
            for n in sorted(only_ours):
                lines.append(f'      - OUR DB ONLY: {n}')
        if not only_island and not only_ours:
            for n in island_names:
                lines.append(f'      ✓ {n}')

    lines.append('')

report = '\n'.join(lines)
with open('unchecked_lists_report.txt', 'w', encoding='utf-8') as f:
    f.write(report)

print(report)
