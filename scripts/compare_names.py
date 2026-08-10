#!/usr/bin/env python3
"""
Compare candidate names between island.is (official source) and candidates.js (our DB).
Outputs discrepancies: names that exist in one but not the other.
"""

import json
import re
import sys

# ─── 1. Load island.is data ──────────────────────────────────────────────────

with open('island_candidates.json', encoding='utf-8') as f:
    island_data = json.load(f)

# ─── 2. Map island.is municipality names → our municipality IDs ──────────────

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

# ─── 3. Parse candidates.js to extract names per municipality+party ───────────

with open('../js/data/candidates.js', encoding='utf-8') as f:
    js_src = f.read()

# Find the REAL_DATA mapping to know which variable = which muni ID
real_data_match = re.search(r'const REAL_DATA\s*=\s*\{([^}]+)\}', js_src, re.DOTALL)
if not real_data_match:
    print("ERROR: Could not find REAL_DATA in candidates.js")
    sys.exit(1)

real_data_block = real_data_match.group(1)
# Parse: muniId: VARNAME pairs
muni_var_map = {}  # muniId -> varName
for m in re.finditer(r'(\w+):\s*([A-Z]+)\b', real_data_block):
    muni_id, var_name = m.group(1), m.group(2)
    muni_var_map[muni_id] = var_name

# For each variable, extract party -> names mapping
# Pattern: find const VARNAME = { ... };
var_data = {}  # varName -> { partyCode -> [name, ...] }

# Find all top-level const declarations
const_blocks = re.finditer(r'\bconst\s+([A-Z]{2,4})\s*=\s*\{', js_src)
for cb in const_blocks:
    var_name = cb.group(1)
    if var_name in ('REAL_DATA',):
        continue
    start = cb.end() - 1  # position of opening {
    # Find matching closing brace
    depth = 0
    pos = start
    while pos < len(js_src):
        if js_src[pos] == '{':
            depth += 1
        elif js_src[pos] == '}':
            depth -= 1
            if depth == 0:
                break
        pos += 1
    block = js_src[start:pos+1]

    # Within this block, find party codes: LETTER: { ... list: [ ... ] ... }
    party_data = {}
    party_matches = re.finditer(r'\b([A-Z]{1,5})\s*:\s*\{', block)
    for pm in party_matches:
        party_code = pm.group(1)
        p_start = pm.end() - 1
        depth2 = 0
        p_pos = p_start
        while p_pos < len(block):
            if block[p_pos] == '{':
                depth2 += 1
            elif block[p_pos] == '}':
                depth2 -= 1
                if depth2 == 0:
                    break
            p_pos += 1
        party_block = block[p_start:p_pos+1]

        # Find list: [ ... ]
        list_match = re.search(r'\blist\s*:\s*\[', party_block)
        if list_match:
            l_start = list_match.end() - 1
            depth3 = 0
            l_pos = l_start
            while l_pos < len(party_block):
                if party_block[l_pos] == '[':
                    depth3 += 1
                elif party_block[l_pos] == ']':
                    depth3 -= 1
                    if depth3 == 0:
                        break
                l_pos += 1
            list_block = party_block[l_start:l_pos+1]

            # Extract names: [N, 'NAME', ...]
            names = re.findall(r'\[\s*\d+\s*,\s*[\'"]([^\'"]+)[\'"]', list_block)
            party_data[party_code] = names

    if party_data:
        var_data[var_name] = party_data

# ─── 4. Map island.is party list letter → our party code ─────────────────────

def get_party_letter(list_name):
    """Extract letter from 'X listi - ...' """
    m = re.match(r'^([A-ZÁÉÍÓÚÝÞÆÖÐ])\s+listi', list_name)
    return m.group(1) if m else None

# ─── 5. Compare ───────────────────────────────────────────────────────────────

discrepancies = []
checked_munis = 0
checked_parties = 0

for island_muni_name, island_parties in island_data.items():
    if not island_parties:  # óbundnar/sjálfkjörið with no lists
        continue

    muni_id = MUNI_MAP.get(island_muni_name)
    if not muni_id:
        print(f"WARNING: No muni ID mapping for '{island_muni_name}'")
        continue

    var_name = muni_var_map.get(muni_id)
    if not var_name:
        # Municipality not in REAL_DATA — might use placeholder
        continue

    our_data = var_data.get(var_name, {})
    checked_munis += 1

    for list_name, island_names in island_parties.items():
        party_letter = get_party_letter(list_name)
        if not party_letter:
            continue

        our_names = our_data.get(party_letter, [])
        if not our_names:
            # Check for multi-char party codes that start with letter
            for code, names in our_data.items():
                if code.startswith(party_letter) and len(code) > 1:
                    our_names = names
                    break

        if not our_names:
            continue  # Party not in our data — skip

        checked_parties += 1

        # Compare name lists
        island_set = set(island_names)
        our_set = set(our_names)

        only_in_island = island_set - our_set
        only_in_ours = our_set - island_set

        if only_in_island or only_in_ours:
            discrepancies.append({
                'municipality': island_muni_name,
                'muni_id': muni_id,
                'party': list_name,
                'party_code': party_letter,
                'only_in_island': sorted(only_in_island),
                'only_in_ours': sorted(only_in_ours),
                'island_count': len(island_names),
                'our_count': len(our_names),
            })

# ─── 6. Output results ────────────────────────────────────────────────────────

print(f"Checked {checked_munis} municipalities, {checked_parties} party lists")
print(f"Found {len(discrepancies)} lists with discrepancies\n")

for d in discrepancies:
    print(f"{'='*70}")
    print(f"MUNICIPALITY: {d['municipality']} ({d['muni_id']})")
    print(f"PARTY LIST:   {d['party']}")
    print(f"COUNTS:       island.is={d['island_count']}, ours={d['our_count']}")

    if d['only_in_island']:
        print(f"\n  ON ISLAND.IS BUT NOT IN OUR DB ({len(d['only_in_island'])}):")
        for name in d['only_in_island']:
            print(f"    + {name}")

    if d['only_in_ours']:
        print(f"\n  IN OUR DB BUT NOT ON ISLAND.IS ({len(d['only_in_ours'])}):")
        for name in d['only_in_ours']:
            print(f"    - {name}")
    print()

# Save full report
with open('comparison_report.txt', 'w', encoding='utf-8') as f:
    f.write(f"Checked {checked_munis} municipalities, {checked_parties} party lists\n")
    f.write(f"Found {len(discrepancies)} lists with discrepancies\n\n")
    for d in discrepancies:
        f.write(f"{'='*70}\n")
        f.write(f"MUNICIPALITY: {d['municipality']} ({d['muni_id']})\n")
        f.write(f"PARTY LIST:   {d['party']}\n")
        f.write(f"COUNTS:       island.is={d['island_count']}, ours={d['our_count']}\n")
        if d['only_in_island']:
            f.write(f"\n  ON ISLAND.IS BUT NOT IN OUR DB:\n")
            for name in d['only_in_island']:
                f.write(f"    + {name}\n")
        if d['only_in_ours']:
            f.write(f"\n  IN OUR DB BUT NOT ON ISLAND.IS:\n")
            for name in d['only_in_ours']:
                f.write(f"    - {name}\n")
        f.write("\n")

print(f"\nFull report saved to comparison_report.txt")
