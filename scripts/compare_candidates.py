#!/usr/bin/env python3
"""
Compare excel_ground_truth.json with candidates.js.
Extract all JS candidates and compare with ground truth.
Output to a file to avoid console encoding issues.
"""

import json
import re
import sys
import io
from pathlib import Path
from collections import defaultdict

BASE = Path("F:/Claude Projects/iceland-elections")
GROUND_TRUTH = BASE / "scripts/excel_ground_truth.json"
CANDIDATES_JS = BASE / "js/data/candidates.js"
OUTPUT = BASE / "scripts/comparison_output.txt"

out = io.open(str(OUTPUT), "w", encoding="utf-8")

def log(*args, **kwargs):
    print(*args, **kwargs, file=out)
    try:
        print(*args, **kwargs)  # also to stdout (may fail for some chars)
    except UnicodeEncodeError:
        pass

# ── Load ground truth ──────────────────────────────────────────────────────────
with open(GROUND_TRUTH, encoding="utf-8") as f:
    gt = json.load(f)

log(f"Ground truth: {len(gt)} municipalities")

# ── Parse candidates.js ────────────────────────────────────────────────────────
with open(CANDIDATES_JS, encoding="utf-8") as f:
    js_text = f.read()

# ── REAL_DATA mapping line ────────────────────────────────────────────────────
real_data_match = re.search(r'const REAL_DATA\s*=\s*\{([^}]+)\}', js_text)
if not real_data_match:
    log("ERROR: Could not find REAL_DATA")
    sys.exit(1)

real_data_text = real_data_match.group(1)
var_muni_map = {}  # var_name -> muni_id
for m in re.finditer(r'(\w+)\s*:\s*([A-Z_]+)', real_data_text):
    muni_id, var_name = m.group(1), m.group(2)
    var_muni_map[var_name] = muni_id

# ── Extract const VAR = { ... } blocks ────────────────────────────────────────
SKIP_VARS = {'DEFAULT_AGENDAS', 'REAL_DATA', 'ICELANDIC_NAMES_F', 'ICELANDIC_NAMES_M',
             'SURNAMES_F', 'SURNAMES_M', 'OCCUPATIONS'}

def extract_const_blocks(js_text):
    blocks = {}
    pattern = re.compile(r'^const\s+([A-Z_]+)\s*=\s*\{', re.MULTILINE)
    matches = list(pattern.finditer(js_text))

    for i, m in enumerate(matches):
        var_name = m.group(1)
        if var_name in SKIP_VARS or var_name.startswith('ICELANDIC') or var_name.startswith('SURNAMES') or var_name.startswith('OCCUPATIONS'):
            continue

        brace_start = m.end() - 1
        depth = 0
        pos = brace_start
        in_string = False
        string_char = None
        while pos < len(js_text):
            c = js_text[pos]
            if in_string:
                if c == '\\':
                    pos += 1
                elif c == string_char:
                    in_string = False
            else:
                if c in ('"', "'", '`'):
                    in_string = True
                    string_char = c
                elif c == '{':
                    depth += 1
                elif c == '}':
                    depth -= 1
                    if depth == 0:
                        break
            pos += 1
        blocks[var_name] = js_text[brace_start:pos+1]

    return blocks

const_blocks = extract_const_blocks(js_text)
log(f"Found {len(const_blocks)} const blocks")

# ── Extract party lists from each block ───────────────────────────────────────
def extract_party_lists(block_text):
    result = {}

    # Find party sections: KEY: { ... list: [...] ... }
    # Keys can be single or multi-letter: D, B, NPM, THVA, etc.
    party_pattern = re.compile(r'\n\s{2}([A-Z][A-Z0-9]*)\s*:\s*\{')
    party_matches = list(party_pattern.finditer(block_text))

    for i, pm in enumerate(party_matches):
        party_code = pm.group(1)

        if i + 1 < len(party_matches):
            section_text = block_text[pm.start():party_matches[i+1].start()]
        else:
            section_text = block_text[pm.start():]

        list_match = re.search(r'\blist\s*:\s*\[', section_text)
        if not list_match:
            continue

        # Find the list array boundaries within the FULL block_text
        list_bracket_pos = pm.start() + list_match.end() - 1  # position of [
        depth = 0
        pos = list_bracket_pos
        in_string = False
        string_char = None
        while pos < len(block_text):
            c = block_text[pos]
            if in_string:
                if c == '\\':
                    pos += 1
                elif c == string_char:
                    in_string = False
            else:
                if c in ('"', "'", '`'):
                    in_string = True
                    string_char = c
                elif c == '[':
                    depth += 1
                elif c == ']':
                    depth -= 1
                    if depth == 0:
                        break
            pos += 1

        list_text = block_text[list_bracket_pos:pos+1]

        # Extract entries: [ballotOrder, 'name', ...]
        candidates = []
        entry_pattern = re.compile(r'\[\s*(\d+)\s*,\s*[\'"]([^\'"]+)[\'"]')
        for em in entry_pattern.finditer(list_text):
            ballot_order = int(em.group(1))
            name = em.group(2)
            candidates.append((ballot_order, name))

        result[party_code] = candidates

    return result

# ── Build JS candidates dict: muni_id -> party_code -> [(order, name)] ────────
js_candidates = {}
for var_name, block_text in const_blocks.items():
    muni_id = var_muni_map.get(var_name)
    if not muni_id:
        continue
    party_lists = extract_party_lists(block_text)
    if party_lists:
        js_candidates[muni_id] = party_lists

log(f"Extracted JS candidates for {len(js_candidates)} municipalities")

# ── Ground truth municipality name -> JS ID mapping ───────────────────────────
excel_to_js = {
    "Akraneskaupstaður": "akranes",
    "Akureyrarbær": "akureyri",   # Akureyrarbær
    "Árneshreppur": "arneshr",
    "Ásahreppur": "asahr",
    "Bláskógabyggð": "blaskogabyggd",
    "Bolungarvíkurkaupstaður": "bolungarvik",
    "Borgarbyggð": "borgarbyggd",       # "Sameinað sveitarfélag Borgarbyggðar og Skorradalshrepps" variant
    "Sameinað sveitarfélag Borgarbyggðar og Skorradalshrepps": "borgarbyggd",
    "Dalabyggð": "dalabyggd",
    "Dalvíkurbyggð": "dalvikurbyggd",
    "Eyja- og Miklaholtshreppur": "eyjamiklaholts",
    "Eyjafjarðarsveit": "eyjafjardarsveit",
    "Fjarðabyggð": "fjardabyggd",
    "Fjallabyggð": "fjallabyggd",
    "Fljótsdalshreppur": "fljotsdalshr",
    "Flóahreppur": "floahreppur",
    "Garðabær": "gardabaer",
    "Grindavíkurbær": "grindavik",
    "Grímsnes- og Grafningshreppur": "grimsnesgrafningur",
    "Grundarfjarðarbær": "grundarfjordur",
    "Grýtubakkahreppur": "grytubakkar",
    "Hafnarfjarðarbær": "hafnarfjordur",   # Hafnarfjarðarbær
    "Hörgársveit": "horgarsv",
    "Hrunamannahreppur": "hrunamannahreppur",
    "Húnabyggð": "hunabyggd",
    "Húnaþing vestra": "hunathing",
    "Hvalfjarðarsveit": "hvalfjardarsveit",
    "Hveragerðisbær": "hveragerdi",
    "Ísafjarðarbær": "isafjordur",
    "Kaldrananeshreppur": "kaldrananes",
    "Kjósarhreppur": "kjosarhreppur",
    "Kjósarhreppur - sjálfkjörið": "kjosarhreppur",
    "Kópavogsbær": "kopavogur",
    "Langanesbyggð": "langanesbyggd",
    "Mosfellsbær": "mosfellsbaer",
    "Múlaþing": "mulathing",
    "Mýrdalshreppur": "myrdalshr",
    "Norðurþing": "nordurping",
    "Ölfus": "olfus",
    "Sveitarfélagið Ölfus": "olfus",
    "Rangárþing eystra": "rangarthingeystra",
    "Rangárþing ytra": "rangarthingytra",
    "Reykhólahreppur": "reykholar",
    "Reykjanesbær": "reykjanesbaer",
    "Reykjavíkurborg": "reykjavik",
    "Seltjarnarnesbær": "seltjarnarnes",
    "Skaftárhreppur": "skaftarhreppur",
    "Sveitarfélagið Skagafjörður": "skagafjordur",
    "Skagafjörður": "skagafjordur",
    "Sveitarfélagið Skagaströnd": "skagastrond",
    "Skeiða- og Gnúpverjahreppur": "skeidagnup",
    "Snæfellsbær": "snaefellsbaer",
    "Snæfellsbær - sjálfkjörið": "snaefellsbaer",
    "Strandabyggð": "strandabyggd",
    "Súðavíkurhreppur": "sudavik",
    "Suðurnesjabær": "sudurnesjabaer",
    "Sveitarfélagið Hornafjörður": "hornafjordur",
    "Sveitarfélagið Stykkishólmur": "stykkisholmur",
    "Sveitarfélagið Vogar": "vogar",
    "Sveitarfélagið Árborg": "arborg",
    "Svalbarðsstrandarhreppur": "svalbardsstrond",
    "Þingeyjarsveit": "thingeyjarsveit",
    "Tjörneshreppur": "tjornes",
    "Tjörneshreppur - sjálfkjörið": "tjornes",
    "Vesturbyggð": "vesturbyggd",
    "Vestmannaeyjakaupstaður": "vestmannaeyjar",
    "Vestmannaeyjabær": "vestmannaeyjar",
    "Vopnafjarðarhreppur": "vopnafjordur",
    "Vopnafjarðarhreppur - sjálfkjörið": "vopnafjordur",
}

# Parse excel keys to figure out the actual names (they appear mojibake in console but fine in file)
# Print them to file for inspection
log("\nGround truth municipality keys:")
for k in gt.keys():
    log(f"  '{k}'")

def list_name_to_code(list_name):
    # Handle Latin letter codes
    m = re.match(r'^([A-Za-z]+)\s+listi', list_name)
    if m:
        return m.group(1).upper()
    # Handle Icelandic letter codes: Á, Þ, Ö, Í, Ó
    m2 = re.match(r'^([ÁÞÖÍÓáþöíó])\s+listi', list_name)
    if m2:
        return m2.group(1).upper()
    return None

# ── Excel-to-JS party code overrides ──────────────────────────────────────────
# Some municipalities use multi-letter JS codes but single-letter Excel codes.
# Map: (muni_id, excel_code) -> js_code
PARTY_CODE_MAP = {
    ('vogar', 'FYRS'): 'FYRS',   # A listi -> FYRS
    ('vogar', 'A'): 'FYRS',
    ('vogar', 'E'): 'VOE',
    ('vogar', 'L'): 'VOL',
    ('nordurping', 'M'): 'NPM',
    ('nordurping', 'V'): 'NPV',
    ('nordurping', 'NBO'): 'NBO',
    ('nordurping', 'Ó'): 'NBO',
    ('hveragerdi', 'O'): 'OKH',
    ('rangarthingeystra', 'N'): 'NRE',
    ('rangarthingytra', 'Á'): 'RYA',
    ('rangarthingytra', 'A'): 'RYA',
    ('skaftarhreppur', 'Ö'): 'SKO',
    ('skaftarhreppur', 'O'): 'SKO',
    ('myrdalshr', 'A'): 'MYA',
    ('myrdalshr', 'Z'): 'MYZ',
    ('blaskogabyggd', 'Þ'): 'BSP',
    ('blaskogabyggd', 'T'): 'BST',
    ('floahreppur', 'I'): 'FLI',
    ('floahreppur', 'T'): 'FLT',
    ('grimsnesgrafningur', 'Ö'): 'GGO',
    ('grimsnesgrafningur', 'A'): 'GGA',
    ('skeidagnup', 'E'): 'SGE',
    ('skeidagnup', 'L'): 'SGL',
    ('eyjafjardarsveit', 'F'): 'EJF',
    ('eyjafjardarsveit', 'K'): 'EJK',
    ('horgarsv', 'G'): 'HGG',
    ('horgarsv', 'H'): 'HGH',
    ('hunabyggd', 'A'): 'HBA',
    ('hunathing', 'N'): 'NHV',
    ('skagafjordur', 'L'): 'SFL',
    ('stykkisholmur', 'Í'): 'IBU',
    ('stykkisholmur', 'H'): 'FLS',
    ('grundarfjordur', 'B'): 'GFB',
    ('grundarfjordur', 'D'): 'GFD',
    ('bolungarvik', 'K'): 'MMM',
    ('bolungarvik', 'O'): 'BBK',
    ('sudavik', 'A'): 'FJL',
    ('sudavik', 'E'): 'FTL',
    ('vesturbyggd', 'N'): 'NYS',
    ('vesturbyggd', 'V'): 'STV',
    ('strandabyggd', 'G'): 'VGV',
    ('strandabyggd', 'T'): 'SBD',
    ('reykholar', 'R'): 'ROA',
    ('thingeyjarsveit', 'L'): 'THVL',
    ('thingeyjarsveit', 'N'): 'THVN',
    ('thingeyjarsveit', 'Á'): 'THVA',
    ('thingeyjarsveit', 'A'): 'THVA',
    ('hvalfjardarsveit', 'Í'): 'HVB',
    ('hvalfjardarsveit', 'A'): 'HVA',
    ('svalbardsstrond', 'Ö'): 'SVSO',
    ('svalbardsstrond', 'H'): 'SVSH',
    ('svalbardsstrond', 'S'): 'SVSS',
    ('vopnafjordur', 'O'): 'VOP',
    ('tjornes', 'T'): 'TJN',
    ('arneshr', 'Á'): 'ARNA',
    ('arneshr', 'S'): 'ARNS',
    ('kjosarhreppur', 'A'): 'KJA',
    ('hrunamannahreppur', 'L'): 'HRL',
    ('seltjarnarnes', 'S'): 'SCS',
    ('gardabaer', 'G'): 'GB',
    ('akureyri', 'A'): 'AL',
    ('skagastrond', 'K'): 'K',
}

# ── Compare ────────────────────────────────────────────────────────────────────
log("\n\n=== DISCREPANCIES ===\n")
discrepancies = []

for excel_muni, excel_parties in gt.items():
    js_muni_id = excel_to_js.get(excel_muni)
    if not js_muni_id:
        log(f"WARNING: No JS mapping for Excel municipality '{excel_muni}'")
        continue

    js_muni_data = js_candidates.get(js_muni_id, {})

    for list_name, excel_cands in excel_parties.items():
        party_code = list_name_to_code(list_name)
        if not party_code:
            log(f"WARNING [{js_muni_id}]: Could not parse party code from '{list_name}'")
            continue

        # Map Excel party code to JS party code if needed
        js_party_code = PARTY_CODE_MAP.get((js_muni_id, party_code), party_code)

        # Skip self-elected (sjálfkjörið)
        is_selfchosen = all(
            'sjálfkjörið' in c.get('name', '').lower() or
            'sjálfkjörð' in c.get('name', '').lower()
            for c in excel_cands
        )
        if is_selfchosen:
            continue

        js_party_cands = js_muni_data.get(js_party_code)

        if js_party_cands is None:
            discrepancies.append({
                'type': 'MISSING_PARTY',
                'muni': js_muni_id,
                'excel_muni': excel_muni,
                'party': js_party_code,
                'excel_code': party_code,
                'list_name': list_name,
                'excel_cands': excel_cands,
            })
            continue

        excel_by_order = {c['ballotOrder']: c['name'].strip() for c in excel_cands}
        js_by_order = {order: name.strip() for order, name in js_party_cands}

        all_orders = sorted(set(excel_by_order.keys()) | set(js_by_order.keys()))

        for order in all_orders:
            excel_name = excel_by_order.get(order)
            js_name = js_by_order.get(order)

            if excel_name is None:
                discrepancies.append({
                    'type': 'EXTRA_IN_JS',
                    'muni': js_muni_id,
                    'party': js_party_code,
                    'order': order,
                    'js_name': js_name,
                })
            elif js_name is None:
                discrepancies.append({
                    'type': 'MISSING_IN_JS',
                    'muni': js_muni_id,
                    'party': js_party_code,
                    'order': order,
                    'excel_name': excel_name,
                })
            elif excel_name != js_name:
                discrepancies.append({
                    'type': 'NAME_MISMATCH',
                    'muni': js_muni_id,
                    'party': js_party_code,
                    'order': order,
                    'excel_name': excel_name,
                    'js_name': js_name,
                })

by_muni_party = defaultdict(list)
for d in discrepancies:
    key = (d['muni'], d.get('party', '?'))
    by_muni_party[key].append(d)

for (muni, party), issues in sorted(by_muni_party.items()):
    log(f"\n[{muni}] Party {party}:")
    for issue in issues:
        t = issue['type']
        if t == 'MISSING_PARTY':
            log(f"  MISSING_PARTY: {issue['list_name']} ({len(issue['excel_cands'])} candidates)")
            for c in issue['excel_cands']:
                log(f"    #{c['ballotOrder']}: {c['name']}")
        elif t == 'NAME_MISMATCH':
            log(f"  #{issue['order']}: JS='{issue['js_name']}' | EXCEL='{issue['excel_name']}'")
        elif t == 'MISSING_IN_JS':
            log(f"  #{issue['order']}: MISSING '{issue['excel_name']}'")
        elif t == 'EXTRA_IN_JS':
            log(f"  #{issue['order']}: EXTRA '{issue['js_name']}'")

log(f"\nTotal discrepancies: {len(discrepancies)}")
log(f"Affected municipality+party combinations: {len(by_muni_party)}")

# Save discrepancies to JSON for fixing
with open(BASE / "scripts/discrepancies.json", "w", encoding="utf-8") as f:
    json.dump(discrepancies, f, ensure_ascii=False, indent=2)
log("\nSaved discrepancies.json")
out.close()
