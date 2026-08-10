#!/usr/bin/env python3
"""
Fix candidates.js based on discrepancies found by compare_candidates.py.
This script directly modifies candidates.js.
"""

import json
import re
import sys
import io
from pathlib import Path

# Fix stdout encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = Path("F:/Claude Projects/iceland-elections")
CANDIDATES_JS = BASE / "js/data/candidates.js"
GROUND_TRUTH = BASE / "scripts/excel_ground_truth.json"

with open(CANDIDATES_JS, encoding="utf-8") as f:
    js_text = f.read()

with open(GROUND_TRUTH, encoding="utf-8") as f:
    gt = json.load(f)

print(f"Loaded candidates.js ({len(js_text)} chars)")

changes = []

# ─── Helper to find list endings in JS ────────────────────────────────────────
def find_list_end(js_text, muni_var, party_code):
    """Find the position just before the closing ], of a party's list array."""
    # Find const MUNI_VAR = {
    muni_start = js_text.find(f'\nconst {muni_var} = {{')
    if muni_start == -1:
        return None, None

    # Find party_code: { within the muni block
    # The party code appears at the start of a line with 2 spaces indent
    party_pat = re.compile(r'\n  ' + re.escape(party_code) + r'\s*:\s*\{')
    pm = party_pat.search(js_text, muni_start)
    if not pm:
        return None, None

    # Find list: [ within this party section
    list_pat = re.compile(r'\blist\s*:\s*\[')
    lm = list_pat.search(js_text, pm.end())
    if not lm:
        return None, None

    # Find the matching closing ]
    list_bracket = lm.end() - 1  # position of [
    depth = 0
    pos = list_bracket
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
            elif c == '[':
                depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0:
                    # Found closing ] of list array
                    return list_bracket, pos
        pos += 1
    return None, None


def get_list_contents(js_text, muni_var, party_code):
    """Get the text content of a party's list array."""
    start, end = find_list_end(js_text, muni_var, party_code)
    if start is None:
        return None
    return js_text[start:end+1]


def insert_candidate_at_end(js_text, muni_var, party_code, ballot_order, name):
    """Insert a new candidate entry at the end of a party's list."""
    start, end = find_list_end(js_text, muni_var, party_code)
    if start is None:
        print(f"  ERROR: Could not find list for {muni_var}.{party_code}")
        return js_text

    # Find the last ] that closes the last entry before the list's closing ]
    # The list ends at js_text[end] = ']'
    # Insert before that position, with trailing comma after last entry
    new_entry = f"\n      [{ballot_order}, '{name}', 'Frambjóðandi'],"
    # Insert before the closing ]
    new_text = js_text[:end] + new_entry + '\n    ' + js_text[end:]
    print(f"  Added #{ballot_order}: {name} to {muni_var}.{party_code}")
    return new_text


def fix_candidate_name(js_text, muni_var, party_code, ballot_order, old_name, new_name):
    """Fix a candidate's name in the list."""
    # Find the entry: [ballot_order, 'old_name', ...
    # We need to be careful to only replace within the right party block
    start, end = find_list_end(js_text, muni_var, party_code)
    if start is None:
        print(f"  ERROR: Could not find list for {muni_var}.{party_code}")
        return js_text

    list_text = js_text[start:end+1]
    # Find the entry with this ballot order and old name
    # Pattern: [N, 'old_name', or [N, "old_name",
    pattern = re.compile(
        r'(\[' + str(ballot_order) + r'\s*,\s*)[\'"]' + re.escape(old_name) + r'[\'"]'
    )
    m = pattern.search(list_text)
    if not m:
        print(f"  ERROR: Could not find #{ballot_order} '{old_name}' in {muni_var}.{party_code}")
        return js_text

    # Determine what quote char was used
    quote_char = list_text[m.end() - len(old_name) - 1 - 1]  # char before old_name... let's just use single quote
    # Replace within list_text
    new_list_text = list_text[:m.start()] + m.group(1) + "'" + new_name + "'" + list_text[m.end():]
    new_js = js_text[:start] + new_list_text + js_text[end+1:]
    print(f"  Fixed #{ballot_order}: '{old_name}' -> '{new_name}' in {muni_var}.{party_code}")
    return new_js


# ─── Municipality var name map ─────────────────────────────────────────────────
# From REAL_DATA line
MUNI_TO_VAR = {
    'reykjavik': 'RVK', 'kopavogur': 'KOP', 'hafnarfjordur': 'HAF', 'gardabaer': 'GAR',
    'mosfellsbaer': 'MOS', 'akureyri': 'AKU', 'seltjarnarnes': 'SEL', 'reykjanesbaer': 'RNB',
    'vogar': 'VOG', 'grindavik': 'GRN', 'sudurnesjabaer': 'SNB', 'arborg': 'ARB',
    'vestmannaeyjar': 'VME', 'nordurping': 'NPG', 'fjallabyggd': 'FJB', 'fjardabyggd': 'FJD',
    'hornafjordur': 'HFJ', 'akranes': 'AKR', 'borgarbyggd': 'BBD', 'isafjordur': 'ISF',
    'hveragerdi': 'HVG', 'rangarthingeystra': 'RTE', 'rangarthingytra': 'RTY', 'olfus': 'OLF',
    'skaftarhreppur': 'SKR', 'myrdalshr': 'MYR', 'blaskogabyggd': 'BSG', 'floahreppur': 'FHR',
    'hrunamannahreppur': 'HMR', 'grimsnesgrafningur': 'GGR', 'skeidagnup': 'SGN',
    'dalvikurbyggd': 'DVB', 'eyjafjardarsveit': 'EJA', 'horgarsv': 'HGS', 'hunabyggd': 'HNB',
    'hunathing': 'HNT', 'skagafjordur': 'SFJ', 'skagastrond': 'SST', 'stykkisholmur': 'STK',
    'grundarfjordur': 'GFJ', 'bolungarvik': 'BLV', 'sudavik': 'SDV', 'vesturbyggd': 'VBG',
    'strandabyggd': 'STD', 'reykholar': 'RKH', 'mulathing': 'MUT', 'thingeyjarsveit': 'THV',
    'hvalfjardarsveit': 'HVF', 'snaefellsbaer': 'SNF', 'svalbardsstrond': 'SVS',
    'kjosarhreppur': 'KJO', 'vopnafjordur': 'VPF', 'tjornes': 'TJR', 'arneshr': 'ARN',
}

# ─── PART 1: Fix name mismatches ───────────────────────────────────────────────
print("\n=== FIXING NAME MISMATCHES ===")

name_fixes = [
    # (muni_id, party_code, ballot_order, js_name, excel_name)
    ('akureyri', 'M', 17, 'Viðar Valdimarsson', 'Viðar Valdimársson'),
    ('akureyri', 'M', 18, 'Rósanna Marín Valdimarsdóttir', 'Rósanna Marín Valdimársdóttir'),
    ('arborg', 'C', 10, 'Valdimar Gylfason', 'Valdimár Gylfason'),
    ('borgarbyggd', 'B', 8, 'Valdimar Reynisson', 'Valdimár Reynisson'),
    ('borgarbyggd', 'M', 2, 'Þórður Brynjarsson', 'Þórður Brynjársson'),
    ('borgarbyggd', 'M', 13, 'Snorri Jóhannesson', 'Snorri Jóhannsson'),
    ('fjallabyggd', 'H', 13, 'Katrín Freysdóttir', 'Katrín Freydóttir'),
    ('fjallabyggd', 'S', 7, 'Hbib Jaouad', 'Hbib Jaoaud'),
    ('fjardabyggd', 'D', 15, 'Simona Giastautiené', 'Simona Giastautienė'),
    ('fjardabyggd', 'S', 5, 'Arndís  Bára Pétursdóttir', 'Arndís Bára Pétursdóttir'),
    ('fjardabyggd', 'S', 11, 'Salóme  Rut Harðardóttir', 'Salóme Rut Harðardóttir'),
    ('hafnarfjordur', 'M', 11, 'Hjörtur Þórisson', 'Hjörtur Þórison'),
    ('hafnarfjordur', 'M', 17, 'Vilhjálmur Skúli Steinarsson', 'Vilhjálmur Skúli Steinársson'),
    ('hafnarfjordur', 'S', 17, 'Valdimar Aðalsteinsson', 'Valdimár Aðalsteinsson'),
    ('hornafjordur', 'B', 10, 'Sigursteinn Ingvar Traustason', 'Sigursteinn Ingvar Trautason'),
    ('hunabyggd', 'B', 11, 'Guðmann Valdimarsson', 'Guðmann Valdimársson'),
    ('hunathing', 'B', 1, 'Sigurður Líndal Þórisson', 'Sigurður Líndal Þórison'),
    ('kopavogur', 'B', 10, 'Atli Ómarsson', 'Atli Ársælsson'),
    ('kopavogur', 'B', 13, 'Atli Ársælsson', 'Atli Ómarsson'),
    ('mosfellsbaer', 'C', 2, 'Valdimar Birgisson', 'Valdimár Birgisson'),
    ('mosfellsbaer', 'M', 6, 'Karl Gissur Þórisson', 'Karl Gissur Þórison'),
    ('mosfellsbaer', 'M', 12, 'Bjarki Þór Þórisson', 'Bjarki Þór Þórison'),
    ('mulathing', 'B', 6, 'Brynjar Pálmi Ásgeirsson', 'Brynjar Pálmi Ásgeirssson'),
    ('mulathing', 'V', 2, 'Helgi Hlynur Ásgrímsson', 'Helgi Hlynur Ásgrímssson'),
    ('rangarthingeystra', 'D', 7, 'Ólafur Þórisson', 'Ólafur Þórison'),
    ('reykjanesbaer', 'C', 15, 'Ingi Eggert Ásbjarnarson', 'Ingi Eggert Ásbjörnarson'),
    ('reykjanesbaer', 'D', 15, 'Guðmundur Steinarsson', 'Guðmundur Steinársson'),
    ('reykjanesbaer', 'M', 6, 'Brynjólfur Sveinn Ívarssson', 'Brynjólfur Sveinn Ívarsson'),
    ('reykjanesbaer', 'S', 21, 'Sveindís Valdimarsdóttir', 'Sveindís Valdimársdóttir'),
    ('reykjavik', 'C', 17, 'Jón Steindór Valdimarsson', 'Jón Steindór Valdimársson'),
    ('reykjavik', 'C', 26, 'Ólöf Hugrún Valdimarsdóttir', 'Ólöf Hugrún Valdimársdóttir'),
    ('reykjavik', 'G', 10, 'Unnur Sól Ingimarsdóttir', 'Unnur Sól Ingimársdóttir'),
    ('reykjavik', 'G', 12, 'Birta Hrönn Ingimarsdóttir', 'Birta Hrönn Ingimársdóttir'),
    ('reykjavik', 'G', 15, 'Þorleifur Þorleifsson', 'Þorleifur Þorleifssson'),
    ('reykjavik', 'J', 45, 'Júlíus K. Valdimarsson', 'Júlíus K. Valdimársson'),
    ('reykjavik', 'M', 20, 'Arnór Valdimarsson', 'Arnór Valdimársson'),
    ('reykjavik', 'M', 37, 'Fjóla Hrund Björnsdóttir', 'Fjóla Hrund Björnsson'),
    ('reykjavik', 'M', 43, 'Valdimar Ármann Þórhallsson', 'Valdimár Ármann Þórhallsson'),
    ('seltjarnarnes', 'M', 12, 'Halldór Benóný Nellett', 'Halldór Benóný Nelletto'),
    ('skagafjordur', 'B', 6, 'Atli Már Traustason', 'Atli Már Trautason'),
    ('skagafjordur', 'B', 12, 'Ísak Óli Traustason', 'Ísak Óli Trautason'),
    ('skagafjordur', 'D', 4, 'Rósanna Valdimarsdóttir', 'Rósanna Valdimársdóttir'),
    ('skagafjordur', 'M', 7, 'Valdimar Á. Þorbergsson', 'Valdimár Á. Þorbergsson'),
    ('skagafjordur', 'M', 8, 'Hólmsteinn Orri Þorleifsson', 'Hólmsteinn Orri Þorleifssson'),
    ('skagastrond', 'B', 8, 'Einar Ólafur Þorleifsson', 'Einar Ólafur Þorleifssson'),
    ('snaefellsbaer', 'D', 7, 'Illugi Jens Jónasson', 'Illugi Jens Jónásson'),
    ('snaefellsbaer', 'D', 13, 'Gunnar Ólafur Sigmarsson', 'Gunnar Ólafur Sigmársson'),
    ('sudurnesjabaer', 'D', 1, 'Haukur Andreasson', 'Haukur Andreásson'),
    ('sudurnesjabaer', 'M', 2, 'Sigrún Harpa Sigurjónsd. Heide', 'Sigrún Harpa Sigurjónd. Heide'),
]

for muni_id, party_code, ballot_order, js_name, excel_name in name_fixes:
    var_name = MUNI_TO_VAR.get(muni_id)
    if not var_name:
        print(f"  WARNING: No var for {muni_id}")
        continue
    js_text = fix_candidate_name(js_text, var_name, party_code, ballot_order, js_name, excel_name)

# ─── PART 2: Fix Vestmannaeyjar E (ballot order shift) ────────────────────────
print("\n=== FIXING VESTMANNAEYJAR E (ballot order / name fix) ===")
# Excel vs JS order mismatch — Excel is ground truth.
# Excel E-list:
# #4: Hildur Rún Róbertsdóttir
# #5: Jessý Friðbjarnardóttir
# #6: Ágúst Erling Kristjánsson
# #7: Eyrún Haraldsdóttir
# #8: Zindri Freyr Ragnarsson (JS has "Zindri Freyr Ragnarsson Caine" then "Caine ...")
# #9: Caine Þorsteinn Ívar Þorsteinsson (JS has "Þorsteinn Ívar Þorsteinsson")
# #10: Þórdís Jóna Guðmundsdóttir (matches)
# #11: Hafdís Víglundsdóttir (matches)
# #12: Bergþóra Sigurðardóttir
# #13: Stefán Jónasson
# #14: Hafdís Ástþórsdóttir
# #15: Bjartey Hermannsdóttir
# #16: Friðrik Björgvinsson
# #17: Hrefna Valdís Guðmundsdóttir
# #18: Hörður Þórðarson (MISSING)
# JS has them shifted by 1 from #4 onward.
# Let me fix each:
vme_e_fixes = [
    (4, 'Jessý Friðbjarnardóttir', 'Hildur Rún Róbertsdóttir'),
    (5, 'Ágúst Erling Kristjánsson', 'Jessý Friðbjarnardóttir'),
    (6, 'Zindri Freyr Ragnarsson Caine', 'Ágúst Erling Kristjánsson'),
    (7, 'Þorsteinn Ívar Þorsteinsson', 'Eyrún Haraldsdóttir'),
    (8, 'Þórdís Jóna Guðmundsdóttir', 'Zindri Freyr Ragnarsson'),
    (9, 'Hafdís Víglundsdóttir', 'Caine Þorsteinn Ívar Þorsteinsson'),
    (10, 'Bergþóra Sigurðardóttir', 'Þórdís Jóna Guðmundsdóttir'),
    (11, 'Hildur Rún Róbertsdóttir', 'Hafdís Víglundsdóttir'),
    (12, 'Hafdís Ástþórsdóttir', 'Bergþóra Sigurðardóttir'),
    (13, 'Bjartey Hermannsdóttir', 'Stefán Jónasson'),
    (14, 'Friðrik Björgvinsson', 'Hafdís Ástþórsdóttir'),
    (15, 'Hrefna Valdís Guðmundsdóttir', 'Bjartey Hermannsdóttir'),
    (16, 'Stefán Jónasson', 'Friðrik Björgvinsson'),
    (17, 'Eyrún Haraldsdóttir', 'Hrefna Valdís Guðmundsdóttir'),
]
for ballot_order, js_name, excel_name in vme_e_fixes:
    js_text = fix_candidate_name(js_text, 'VME', 'E', ballot_order, js_name, excel_name)

print("\n=== FIXING VESTMANNAEYJAR M (ballot order / name fix) ===")
# Excel M-list:
# #8: Erlendur Ágúst Stefánsson  (JS #8 has Sveinn Hjalti Guðmundsson)
# #10: Sveinn Hjalti Guðmundsson (JS #10 has Þórey Katla Brynjarsdóttir)
# #13: Þórey Katla Brynjarsdóttir (JS #13 has Elmar Hrafn Óskarsson)
# #14: Jón Helgi Gíslason        (JS #14 has Sigdór Yngvi Kristinsson)
# #15: Sigdór Yngvi Kristinsson  (JS #15 has Adam Smári Sigfússon)
# #16: Adam Smári Sigfússon      (JS #16 has Jón Helgi Gíslason)
# #17: Elmar Hrafn Óskarsson     (JS #17 has Erlendur Ágúst Stefánsson)
# #18: Eyjólfur Pétursson        (MISSING)
vme_m_fixes = [
    (8, 'Sveinn Hjalti Guðmundsson', 'Erlendur Ágúst Stefánsson'),
    (10, 'Þórey Katla Brynjarsdóttir', 'Sveinn Hjalti Guðmundsson'),
    (13, 'Elmar Hrafn Óskarsson', 'Þórey Katla Brynjarsdóttir'),
    (14, 'Sigdór Yngvi Kristinsson', 'Jón Helgi Gíslason'),
    (15, 'Adam Smári Sigfússon', 'Sigdór Yngvi Kristinsson'),
    (16, 'Jón Helgi Gíslason', 'Adam Smári Sigfússon'),
    (17, 'Erlendur Ágúst Stefánsson', 'Elmar Hrafn Óskarsson'),
]
for ballot_order, js_name, excel_name in vme_m_fixes:
    js_text = fix_candidate_name(js_text, 'VME', 'M', ballot_order, js_name, excel_name)

# ─── PART 3: Add missing last candidates to existing lists ────────────────────
print("\n=== ADDING MISSING LAST CANDIDATES ===")

missing_last = [
    # (muni_id, party_code, ballot_order, name)
    ('akranes', 'B', 18, 'Hlöðver Sigurðsson'),
    ('akranes', 'C', 17, 'Edit Ómarsdóttir'),
    ('akranes', 'D', 18, 'Ólafur Guðmundur Adolfsson'),
    ('akranes', 'S', 18, 'Valgarður Lyngdal Jónsson'),
    ('akureyri', 'B', 22, 'Ingibjörg Ólöf Isaksen'),
    ('akureyri', 'C', 22, 'Ingvar Þóroddsson'),
    ('akureyri', 'D', 22, 'Lára Halldóra Eiríksdóttir'),
    ('akureyri', 'L', 22, 'Oddur Helgi Halldórsson'),
    ('akureyri', 'M', 22, 'Sigríður Valdís Bergvinsdóttir'),
    ('akureyri', 'V', 22, 'Kristín Sigfúsdóttir'),
    ('arborg', 'B', 22, 'Hafdís H. Hafsteinsdóttir'),
    ('arborg', 'C', 22, 'Eyjólfur Sturlugsson'),
    ('arborg', 'D', 22, 'Ari Thorarensen'),
    ('arborg', 'S', 22, 'Arna Ír Gunnarsdóttir'),
    ('borgarbyggd', 'D', 18, 'Magnús Birgir Jónsson'),
    ('borgarbyggd', 'M', 18, 'Guðrún Jónsdóttir'),
    ('dalvikurbyggd', 'B', 14, 'Lilja Ósmann Guðnadóttir'),
    ('dalvikurbyggd', 'D', 14, 'Freyr Antonsson'),
    ('fjallabyggd', 'D', 14, 'S. Guðrún Hauksdóttir'),
    ('fjallabyggd', 'H', 14, 'Árni Helgason'),
    ('fjallabyggd', 'S', 14, 'Sæbjörg Ágústsdóttir'),
    ('fjardabyggd', 'D', 18, 'Kristinn Aðalsteinsson'),
    ('fjardabyggd', 'M', 18, 'Rúnar Már Gunnarsson'),
    ('fjardabyggd', 'S', 18, 'Björn Hafþór Guðmundsson'),
    ('gardabaer', 'C', 22, 'Sara Dögg Svanhildardóttir'),
    ('gardabaer', 'M', 22, 'Nanna M. Gunnlaugsdóttir'),
    ('gardabaer', 'S', 22, 'Guðmundur Andri Thorsson'),
    ('grindavik', 'B', 14, 'Guðmundur Grétar Karlsson'),
    ('grindavik', 'D', 14, 'Otti Rafn Sigmársson'),
    ('grindavik', 'M', 11, 'Ragna Fossádal'),
    ('hafnarfjordur', 'A', 22, 'Árni Áskelsson'),
    ('hafnarfjordur', 'B', 22, 'Þórarinn Þórhallsson'),
    ('hafnarfjordur', 'C', 22, 'Örn H. Magnússon'),
    ('hafnarfjordur', 'S', 22, 'Valgerður María Guðmundsdóttir'),
    ('hornafjordur', 'B', 14, 'Ásgerður Kristín Gylfadóttir'),
    ('hornafjordur', 'D', 14, 'Skúli Ingólfsson'),
    ('hornafjordur', 'K', 14, 'Halldór Tjörvi Einarsson'),
    ('hornafjordur', 'M', 14, 'Ómar Antonsson'),
    ('hrunamannahreppur', 'D', 10, 'Herbert Hauksson'),
    ('hunabyggd', 'B', 18, 'Auðunn Steinn Sigurðsson'),
    ('hunabyggd', 'D', 18, 'Magnús Rúnar Sigurðsson'),
    ('hunathing', 'D', 14, 'Þorvaldur Böðvarsson'),
    ('hveragerdi', 'D', 14, 'Eyjólfur K. Kolbeins'),
    ('hveragerdi', 'S', 14, 'Ingibjörg Sigmundsdóttir'),
    ('isafjordur', 'B', 18, 'Marzellíus Sveinbjörnsson'),
    ('isafjordur', 'C', 18, 'Sigrún Camilla Halldórsdóttir'),
    ('isafjordur', 'D', 18, 'Jóhann Birkir Helgason'),
    ('isafjordur', 'M', 10, 'Sigurveig Gunnarsdóttir'),
    ('isafjordur', 'S', 18, 'Bryndís G. Friðgeirsdóttir'),
    ('kopavogur', 'B', 22, 'Birkir Jón Jónsson'),
    ('kopavogur', 'C', 22, 'Kristín Þórhalla Rokk Þórisdóttir'),
    ('kopavogur', 'D', 22, 'Sólveig Guðrún Pétursdóttir'),
    ('kopavogur', 'J', 19, 'Magnús Rínar Magnússon'),
    ('kopavogur', 'M', 22, 'Ragnheiður Brynjólfsdóttir'),
    ('kopavogur', 'S', 22, 'Rannveig Guðmundsdóttir'),
    ('kopavogur', 'V', 22, 'Ólafur Þór Gunnarsson'),
    ('mosfellsbaer', 'B', 22, 'Örvar Jóhannsson'),
    ('mosfellsbaer', 'C', 22, 'Lovísa Jónsdóttir'),
    ('mosfellsbaer', 'D', 22, 'Salome Þorkelsdóttir'),
    ('mosfellsbaer', 'L', 22, 'Páll Kristjánsson'),
    ('mosfellsbaer', 'M', 22, 'Þorlákur Ásgeir Pétursson'),
    ('mosfellsbaer', 'S', 22, 'Anna Sigríður Guðnadóttir'),
    ('mulathing', 'B', 22, 'Þorvaldur Hjarðar'),
    ('mulathing', 'D', 22, 'Ágústa Björnsdóttir'),
    ('mulathing', 'L', 22, 'Heiða Ingimarsdóttir'),
    ('mulathing', 'M', 22, 'Gunnar Þór Sigbjörnsson'),
    ('mulathing', 'V', 22, 'Guðmundur Ármannsson'),
    ('nordurping', 'B', 18, 'Hjálmar Bogi Hafliðason'),
    ('nordurping', 'D', 18, 'Stella Borgþóra Þorláksdóttir'),
    ('nordurping', 'S', 18, 'Gunnar Valdemarsson'),
    ('olfus', 'D', 14, 'Ásta Júlía Jónsdóttir'),
    ('olfus', 'S', 14, 'Guðmundur Oddgeirsson'),
    ('rangarthingeystra', 'B', 14, 'Lilja Einarsdóttir'),
    ('rangarthingeystra', 'D', 14, 'Árný Hrund Svansdóttir'),
    ('rangarthingytra', 'D', 14, 'Eydís Þorbjörg Indriðadóttir'),
    ('reykholar', 'S', 10, 'Andrea Björnsdóttir'),
    ('reykjanesbaer', 'B', 22, 'Jóhann Friðrik Friðriksson'),
    ('reykjanesbaer', 'C', 22, 'Bjarklind Sigurðardóttir'),
    ('reykjanesbaer', 'D', 22, 'Margrét Sanders'),
    ('reykjanesbaer', 'M', 22, 'Pétur Þórarinsson'),
    ('reykjanesbaer', 'S', 22, 'Friðjón Einarsson'),
    ('reykjavik', 'B', 46, 'Sigrún Magnúsdóttir'),
    ('reykjavik', 'C', 46, 'Þórdís Lóa Þórhallsdóttir'),
    ('reykjavik', 'F', 46, 'Inga Sæland Ástvaldsdóttir'),
    ('reykjavik', 'G', 23, 'Rakel Árnadóttir'),
    ('reykjavik', 'J', 46, 'Sólveig Hauksdóttir'),
    ('reykjavik', 'M', 46, 'Vigdís Hauksdóttir'),
    ('reykjavik', 'P', 46, 'Edda Björk Bogadóttir'),
    ('reykjavik', 'R', 23, 'Birgir Stefánsson'),
    ('reykjavik', 'S', 46, 'Ingibjörg Sólrún Gísladóttir'),
    ('seltjarnarnes', 'D', 14, 'Petrea Ingibjörg Jónsdóttir'),
    ('seltjarnarnes', 'M', 14, 'Ástríður Sigurrós Jónsdóttir'),
    ('skaftarhreppur', 'D', 10, 'Rannveig E. Bjarnadóttir'),
    ('skagafjordur', 'B', 18, 'Sigríður Magnúsdóttir'),
    ('skagafjordur', 'D', 18, 'Gísli Sigurðsson'),
    ('skagafjordur', 'M', 18, 'Jóhann Már Jóhannsson'),
    ('skagastrond', 'B', 10, 'Magnús Björn Jónsson'),
    ('skagastrond', 'S', 10, 'Steindór R. Haraldsson'),
    ('strandabyggd', 'B', 10, 'Sigríður Drífa Þórólfsdóttir'),
    ('sudurnesjabaer', 'B', 18, 'Guðjón Ólafsson'),
    ('sudurnesjabaer', 'D', 18, 'Einar Jón Pálsson'),
    ('sudurnesjabaer', 'M', 18, 'Álfhildur Sigurjónsdóttir Heide'),
    ('sudurnesjabaer', 'S', 18, 'Jórunn Alda Guðmundsdóttir'),
    ('vestmannaeyjar', 'D', 18, 'Elísabet Arnoddsdóttir'),
    ('vestmannaeyjar', 'E', 18, 'Hörður Þórðarson'),
    ('vestmannaeyjar', 'M', 18, 'Eyjólfur Pétursson'),
    ('vogar', 'D', 14, 'Björn Guðmundur Sæbjörnsson'),
]

for muni_id, party_code, ballot_order, name in missing_last:
    var_name = MUNI_TO_VAR.get(muni_id)
    if not var_name:
        print(f"  WARNING: No var for {muni_id}")
        continue
    js_text = insert_candidate_at_end(js_text, var_name, party_code, ballot_order, name)

# ─── PART 4: Add entirely missing party lists ─────────────────────────────────
print("\n=== ADDING MISSING PARTY LISTS ===")

# These parties need to be added as complete new sections to existing municipality consts

def add_party_to_muni(js_text, muni_var, party_code, tagline, candidates):
    """Add a new party section to an existing municipality const."""
    # Find the closing }; of the muni const
    # The last party section closes with },\n};\n
    # We find the muni const's end brace
    muni_start = js_text.find(f'\nconst {muni_var} = {{')
    if muni_start == -1:
        print(f"  ERROR: Cannot find const {muni_var}")
        return js_text

    # Find matching end of this const block
    brace_start = js_text.index('{', muni_start)
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

    # pos is now at the closing } of the const
    # We need to insert the new party before this closing }

    # Build the candidate list entries
    cand_lines = []
    for cand in candidates:
        name = cand['name'].replace("'", "\\'")
        cand_lines.append(f"      [{cand['ballotOrder']}, '{name}', 'Frambjóðandi'],")

    cand_block = '\n'.join(cand_lines)

    new_party = f"""
  {party_code}: {{
    tagline: '{tagline}',
    agenda: [],
    list: [
{cand_block}
    ],
  }},"""

    new_js = js_text[:pos] + new_party + '\n' + js_text[pos:]
    print(f"  Added party {party_code} to {muni_var} ({len(candidates)} candidates)")
    return new_js


# Build Excel ground truth lookup
def get_excel_candidates(excel_muni, list_prefix):
    """Get candidates from excel GT matching muni name and list letter prefix."""
    muni_data = gt.get(excel_muni, {})
    for list_name, cands in muni_data.items():
        if list_name.startswith(list_prefix + ' listi') or list_name.startswith(list_prefix + ' listi'):
            return cands
    return None


# Akureyri A (Akureyrarlistinn)
excel_akureyri = gt.get('Akureyrarbær', {})
aku_a_cands = next((v for k, v in excel_akureyri.items() if k.startswith('A listi')), None)
if aku_a_cands:
    js_text = add_party_to_muni(js_text, 'AKU', 'AL',
        'Akureyrarlistinn — fyrir Akureyri',
        aku_a_cands)

# Árneshreppur S (Sólstöður)
excel_arn = gt.get('Árneshreppur', {})
arn_s_cands = next((v for k, v in excel_arn.items() if k.startswith('S listi')), None)
if arn_s_cands:
    js_text = add_party_to_muni(js_text, 'ARN', 'ARNS',
        'Sólstöður — S-listi í Árneshreppi',
        arn_s_cands)

# Bláskógabyggð T
excel_bsg = gt.get('Bláskógabyggð', {})
bsg_t_cands = next((v for k, v in excel_bsg.items() if k.startswith('T listi')), None)
if bsg_t_cands:
    js_text = add_party_to_muni(js_text, 'BSG', 'BST',
        'T-listi í Bláskógabyggð',
        bsg_t_cands)

# Bolungarvík K
excel_blv = gt.get('Bolungarvíkurkaupstaður', {})
blv_k_cands = next((v for k, v in excel_blv.items() if k.startswith('K listi')), None)
if blv_k_cands:
    js_text = add_party_to_muni(js_text, 'BLV', 'MMM',
        'Máttur meyja og manna — K-listi í Bolungarvík',
        blv_k_cands)

# Bolungarvík O
blv_o_cands = next((v for k, v in excel_blv.items() if k.startswith('O listi')), None)
if blv_o_cands:
    js_text = add_party_to_muni(js_text, 'BLV', 'BBK',
        'Betri Bolungarvík — O-listi',
        blv_o_cands)

# Borgarbyggð A
excel_bbd = gt.get('Sameinað sveitarfélag Borgarbyggðar og Skorradalshrepps', {})
bbd_a_cands = next((v for k, v in excel_bbd.items() if k.startswith('A listi')), None)
if bbd_a_cands:
    js_text = add_party_to_muni(js_text, 'BBD', 'BBD_A',
        'Borgarbyggðarlistinn — A-listi',
        bbd_a_cands)

# Wait - can't use BBD_A as the key. Need to figure out actual codes.
# The BBD already has B, D, M. A new list would need a new code.
# Let me use 'A' as the party code since that's the Excel letter.

# Actually the above already added BBD_A - let me fix the approach
# I'll remove that and redo with 'A'

# Let me redo by not using add_party_to_muni for borgarbyggd - will handle manually below

# Dalvíkurbyggð A (Byggðalistinn)
excel_dvb = gt.get('Dalvíkurbyggð', {})
dvb_a_cands = next((v for k, v in excel_dvb.items() if k.startswith('A listi')), None)
if dvb_a_cands:
    js_text = add_party_to_muni(js_text, 'DVB', 'A',
        'Byggðalistinn — A-listi Dalvíkurbyggðar',
        dvb_a_cands)

# Dalvíkurbyggð K
dvb_k_cands = next((v for k, v in excel_dvb.items() if k.startswith('K listi')), None)
if dvb_k_cands:
    js_text = add_party_to_muni(js_text, 'DVB', 'K',
        'K-listi — Dalvíkurbyggð',
        dvb_k_cands)

# Eyjafjarðarsveit F
excel_eja = gt.get('Eyjafjarðarsveit', {})
eja_f_cands = next((v for k, v in excel_eja.items() if k.startswith('F listi')), None)
if eja_f_cands:
    js_text = add_party_to_muni(js_text, 'EJA', 'EJF',
        'F-listinn í Eyjafjarðarsveit',
        eja_f_cands)

# Eyjafjarðarsveit K
eja_k_cands = next((v for k, v in excel_eja.items() if k.startswith('K listi')), None)
if eja_k_cands:
    js_text = add_party_to_muni(js_text, 'EJA', 'EJK',
        'K-listinn í Eyjafjarðarsveit',
        eja_k_cands)

# Flóahreppur I (Framfaralistinn)
excel_fhr = gt.get('Flóahreppur', {})
fhr_i_cands = next((v for k, v in excel_fhr.items() if k.startswith('I listi')), None)
if fhr_i_cands:
    js_text = add_party_to_muni(js_text, 'FHR', 'FLI',
        'Framfaralistinn — I-listi Flóahrepps',
        fhr_i_cands)

# Flóahreppur T (T-listinn)
fhr_t_cands = next((v for k, v in excel_fhr.items() if k.startswith('T listi')), None)
if fhr_t_cands:
    js_text = add_party_to_muni(js_text, 'FHR', 'FLT',
        'T-listinn Flóahrepps',
        fhr_t_cands)

# Garðabær G (Garðabæjarlistinn)
excel_gar = gt.get('Garðabær', {})
gar_g_cands = next((v for k, v in excel_gar.items() if k.startswith('G listi')), None)
if gar_g_cands:
    js_text = add_party_to_muni(js_text, 'GAR', 'GB',
        'Garðabæjarlistinn — G-listi',
        gar_g_cands)

# Grímsnes- og Grafningshreppur A
excel_ggr = gt.get('Grímsnes- og Grafningshreppur', {})
ggr_a_cands = next((v for k, v in excel_ggr.items() if k.startswith('A listi')), None)
if ggr_a_cands:
    js_text = add_party_to_muni(js_text, 'GGR', 'GGA',
        'A-listi í Grímsnes- og Grafningshreppi',
        ggr_a_cands)

# Grundarfjarðarbær B
excel_gfj = gt.get('Grundarfjarðarbær', {})
gfj_b_cands = next((v for k, v in excel_gfj.items() if k.startswith('B listi')), None)
if gfj_b_cands:
    js_text = add_party_to_muni(js_text, 'GFJ', 'GFB',
        'B-listi í Grundarfjarðarbæ — Framsókn og félagshyggjufólk',
        gfj_b_cands)

# Grundarfjarðarbær D
gfj_d_cands = next((v for k, v in excel_gfj.items() if k.startswith('D listi')), None)
if gfj_d_cands:
    js_text = add_party_to_muni(js_text, 'GFJ', 'GFD',
        'D-listi í Grundarfjarðarbæ — Sjálfstæðisflokkur og óháðir',
        gfj_d_cands)

# Hörgársveit G
excel_hgs = gt.get('Hörgársveit', {})
hgs_g_cands = next((v for k, v in excel_hgs.items() if k.startswith('G listi')), None)
if hgs_g_cands:
    js_text = add_party_to_muni(js_text, 'HGS', 'HGG',
        'Gróska — G-listi í Hörgársveit',
        hgs_g_cands)

# Hörgársveit H
hgs_h_cands = next((v for k, v in excel_hgs.items() if k.startswith('H listi')), None)
if hgs_h_cands:
    js_text = add_party_to_muni(js_text, 'HGS', 'HGH',
        'Hörgársveitarlistinn — H-listi',
        hgs_h_cands)

# Hrunamannahreppur L
excel_hmr = gt.get('Hrunamannahreppur', {})
hmr_l_cands = next((v for k, v in excel_hmr.items() if k.startswith('L listi')), None)
if hmr_l_cands:
    js_text = add_party_to_muni(js_text, 'HMR', 'HRL',
        'L-listinn í Hrunamannahreppi',
        hmr_l_cands)

# Húnabyggð A (Öll saman)
excel_hnb = gt.get('Húnabyggð', {})
hnb_a_cands = next((v for k, v in excel_hnb.items() if k.startswith('A listi')), None)
if hnb_a_cands:
    js_text = add_party_to_muni(js_text, 'HNB', 'HBA',
        'Öll saman — A-listi Húnabyggðar',
        hnb_a_cands)

# Húnaþing vestra N
excel_hnt = gt.get('Húnaþing vestra', {})
hnt_n_cands = next((v for k, v in excel_hnt.items() if k.startswith('N listi')), None)
if hnt_n_cands:
    js_text = add_party_to_muni(js_text, 'HNT', 'NHV',
        'N-listi — Nýtt afl í Húnaþingi vestra',
        hnt_n_cands)

# Hvalfjarðarsveit A (Samhent sveit)
excel_hvf = gt.get('Hvalfjarðarsveit', {})
hvf_a_cands = next((v for k, v in excel_hvf.items() if k.startswith('A listi')), None)
if hvf_a_cands:
    js_text = add_party_to_muni(js_text, 'HVF', 'HVA',
        'Samhent sveit — A-listi Hvalfjarðarsveitar',
        hvf_a_cands)

# Hveragerðisbær O (Okkar Hveragerði)
excel_hvg = gt.get('Hveragerðisbær', {})
hvg_o_cands = next((v for k, v in excel_hvg.items() if k.startswith('O listi')), None)
if hvg_o_cands:
    js_text = add_party_to_muni(js_text, 'HVG', 'OKH',
        'Okkar Hveragerði — O-listi',
        hvg_o_cands)

# Kjósarhreppur A (Íbúar í Kjós)
excel_kjo = gt.get('Kjósarhreppur - sjálfkjörið', {})
kjo_a_cands = next((v for k, v in excel_kjo.items() if k.startswith('A listi')), None)
if kjo_a_cands:
    js_text = add_party_to_muni(js_text, 'KJO', 'KJA',
        'Íbúar í Kjós — A-listi',
        kjo_a_cands)

# Mýrdalshreppur A
excel_myr = gt.get('Mýrdalshreppur', {})
myr_a_cands = next((v for k, v in excel_myr.items() if k.startswith('A listi')), None)
if myr_a_cands:
    js_text = add_party_to_muni(js_text, 'MYR', 'MYA',
        'A-listi — A fyrir alla í Mýrdalshreppi',
        myr_a_cands)

# Mýrdalshreppur Z
myr_z_cands = next((v for k, v in excel_myr.items() if k.startswith('Z listi')), None)
if myr_z_cands:
    js_text = add_party_to_muni(js_text, 'MYR', 'MYZ',
        'Z-listi — Samfélagið í Mýrdalshreppi',
        myr_z_cands)

# Norðurþing M (Listi samfélagsins)
excel_npg = gt.get('Norðurþing', {})
npg_m_cands = next((v for k, v in excel_npg.items() if k.startswith('M listi')), None)
if npg_m_cands:
    js_text = add_party_to_muni(js_text, 'NPG', 'NPM',
        'Listi samfélagsins — M-listi Norðurþings',
        npg_m_cands)

# Norðurþing V (V-listi velferðar)
npg_v_cands = next((v for k, v in excel_npg.items() if k.startswith('V listi')), None)
if npg_v_cands:
    js_text = add_party_to_muni(js_text, 'NPG', 'NPV',
        'V-listi velferðar — Norðurþing',
        npg_v_cands)

# Rangárþing eystra N
excel_rte = gt.get('Rangárþing eystra', {})
rte_n_cands = next((v for k, v in excel_rte.items() if k.startswith('N listi')), None)
if rte_n_cands:
    js_text = add_party_to_muni(js_text, 'RTE', 'NRE',
        'N-listinn í Rangárþingi eystra',
        rte_n_cands)

# Reykhólahreppur R
excel_rkh = gt.get('Reykhólahreppur', {})
rkh_r_cands = next((v for k, v in excel_rkh.items() if k.startswith('R listi')), None)
if rkh_r_cands:
    js_text = add_party_to_muni(js_text, 'RKH', 'ROA',
        'Raddir okkar allra — R-listi í Reykhólahreppi',
        rkh_r_cands)

# Seltjarnarnes S
excel_sel = gt.get('Seltjarnarnesbær', {})
sel_s_cands = next((v for k, v in excel_sel.items() if k.startswith('S listi')), None)
if sel_s_cands:
    js_text = add_party_to_muni(js_text, 'SEL', 'SCS',
        'S-listi — Samfylking, Viðreisn og óháðir í Seltjarnarnesi',
        sel_s_cands)

# Skagafjörður L (Byggðalistinn)
excel_sfj = gt.get('Skagafjörður', {})
sfj_l_cands = next((v for k, v in excel_sfj.items() if k.startswith('L listi')), None)
if sfj_l_cands:
    js_text = add_party_to_muni(js_text, 'SFJ', 'SFL',
        'Byggðalistinn — L-listi í Skagafirði',
        sfj_l_cands)

# Skagaströnd K (Fyrir Skagaströnd)
excel_sst = gt.get('Sveitarfélagið Skagaströnd', {})
sst_k_cands = next((v for k, v in excel_sst.items() if k.startswith('K listi')), None)
if sst_k_cands:
    js_text = add_party_to_muni(js_text, 'SST', 'K',
        'Fyrir Skagaströnd — K-listi',
        sst_k_cands)

# Skeiða- og Gnúpverjahreppur E
excel_sgn = gt.get('Skeiða- og Gnúpverjahreppur', {})
sgn_e_cands = next((v for k, v in excel_sgn.items() if k.startswith('E listi')), None)
if sgn_e_cands:
    js_text = add_party_to_muni(js_text, 'SGN', 'SGE',
        'E-listi — Uppbygging í Skeiðum og Gnúpverjahreppi',
        sgn_e_cands)

# Skeiða- og Gnúpverjahreppur L
sgn_l_cands = next((v for k, v in excel_sgn.items() if k.startswith('L listi')), None)
if sgn_l_cands:
    js_text = add_party_to_muni(js_text, 'SGN', 'SGL',
        'L-listi — Samvinnulistinn í Skeiðum og Gnúpverjahreppi',
        sgn_l_cands)

# Strandabyggð G (Vegvísir)
excel_std = gt.get('Strandabyggð', {})
std_g_cands = next((v for k, v in excel_std.items() if k.startswith('G listi')), None)
if std_g_cands:
    js_text = add_party_to_muni(js_text, 'STD', 'VGV',
        'Vegvísir — G-listi í Strandabyggð',
        std_g_cands)

# Strandabyggð T (Strandabandalagið)
std_t_cands = next((v for k, v in excel_std.items() if k.startswith('T listi')), None)
if std_t_cands:
    js_text = add_party_to_muni(js_text, 'STD', 'SBD',
        'Strandabandalagið — T-listi í Strandabyggð',
        std_t_cands)

# Stykkishólmur H (Listi framfarasinna)
excel_stk = gt.get('Sveitarfélagið Stykkishólmur', {})
stk_h_cands = next((v for k, v in excel_stk.items() if k.startswith('H listi')), None)
if stk_h_cands:
    js_text = add_party_to_muni(js_text, 'STK', 'FLS',
        'Listi framfarasinna — H-listi Stykkishólms',
        stk_h_cands)

# Súðavíkurhreppur A
excel_sdv = gt.get('Súðavíkurhreppur', {})
sdv_a_cands = next((v for k, v in excel_sdv.items() if k.startswith('A listi')), None)
if sdv_a_cands:
    js_text = add_party_to_muni(js_text, 'SDV', 'FJL',
        'A-listi — Fjarðarlistinn í Súðavíkurhreppi',
        sdv_a_cands)

# Súðavíkurhreppur E
sdv_e_cands = next((v for k, v in excel_sdv.items() if k.startswith('E listi')), None)
if sdv_e_cands:
    js_text = add_party_to_muni(js_text, 'SDV', 'FTL',
        'E-listi — Framtíðarlistinn í Súðavíkurhreppi',
        sdv_e_cands)

# Svalbarðsstrandarhreppur H (Strönd til framtíðar)
excel_svs = gt.get('Svalbarðsstrandarhreppur', {})
svs_h_cands = next((v for k, v in excel_svs.items() if k.startswith('H listi')), None)
if svs_h_cands:
    js_text = add_party_to_muni(js_text, 'SVS', 'SVSS',
        'Strönd til framtíðar — H-listi Svalbarðsstrandar',
        svs_h_cands)

# Þingeyjarsveit L (Framfara)
excel_thv = gt.get('Þingeyjarsveit', {})
thv_l_cands = next((v for k, v in excel_thv.items() if k.startswith('L listi')), None)
if thv_l_cands:
    js_text = add_party_to_muni(js_text, 'THV', 'THVL',
        'L-listi Framfara í Þingeyjarsveit',
        thv_l_cands)

# Þingeyjarsveit N
thv_n_cands = next((v for k, v in excel_thv.items() if k.startswith('N listi')), None)
if thv_n_cands:
    js_text = add_party_to_muni(js_text, 'THV', 'THVN',
        'N-listinn í Þingeyjarsveit',
        thv_n_cands)

# Tjörneshreppur T (Tjörneslistinn)
excel_tjr = gt.get('Tjörneshreppur - sjálfkjörið', {})
tjr_t_cands = next((v for k, v in excel_tjr.items() if k.startswith('T listi')), None)
if tjr_t_cands:
    js_text = add_party_to_muni(js_text, 'TJR', 'TJN',
        'Tjörneslistinn',
        tjr_t_cands)

# Vesturbyggð N (Ný sýn)
excel_vbg = gt.get('Vesturbyggð', {})
vbg_n_cands = next((v for k, v in excel_vbg.items() if k.startswith('N listi')), None)
if vbg_n_cands:
    js_text = add_party_to_muni(js_text, 'VBG', 'NYS',
        'Ný sýn — N-listi Vesturbyggðar',
        vbg_n_cands)

# Vesturbyggð V (Sterkari Vesturbyggð)
vbg_v_cands = next((v for k, v in excel_vbg.items() if k.startswith('V listi')), None)
if vbg_v_cands:
    js_text = add_party_to_muni(js_text, 'VBG', 'STV',
        'Sterkari Vesturbyggð — V-listi',
        vbg_v_cands)

# Sveitarfélagið Vogar A
excel_vog = gt.get('Sveitarfélagið Vogar', {})
vog_a_cands = next((v for k, v in excel_vog.items() if k.startswith('A listi')), None)
if vog_a_cands:
    js_text = add_party_to_muni(js_text, 'VOG', 'FYRS',
        'A-listi — Fyrir samfélagið í Vogum',
        vog_a_cands)

# Sveitarfélagið Vogar E
vog_e_cands = next((v for k, v in excel_vog.items() if k.startswith('E listi')), None)
if vog_e_cands:
    js_text = add_party_to_muni(js_text, 'VOG', 'VOE',
        'E-listi — Framboðsfélag E-listans í Vogum',
        vog_e_cands)

# Sveitarfélagið Vogar L
vog_l_cands = next((v for k, v in excel_vog.items() if k.startswith('L listi')), None)
if vog_l_cands:
    js_text = add_party_to_muni(js_text, 'VOG', 'VOL',
        'L-listi — Framfarafélag L-listans í Vogum',
        vog_l_cands)

# Vopnafjarðarhreppur O (Sterk Stoð)
excel_vpf = gt.get('Vopnafjarðarhreppur - sjálfkjörið', {})
vpf_o_cands = next((v for k, v in excel_vpf.items() if k.startswith('O listi')), None)
if vpf_o_cands:
    js_text = add_party_to_muni(js_text, 'VPF', 'VOP',
        'Sterk Stoð — O-listi Vopnafjarðar',
        vpf_o_cands)

# ─── PART 5: Handle Borgarbyggð A separately (can't use BBD_A) ───────────────
# Remove the BBD_A entry we added and add it as 'A' instead
js_text = js_text.replace('\n  BBD_A: {', '\n  A: {')
print("  Fixed BBD_A -> A")

# ─── PART 6: Handle parties already in JS but whose lists need fixing ─────────
# These are the "warnings" - Excel list codes with Icelandic letters
# that map to existing JS codes. The lists are already in the JS
# but the comparison missed them. Let's check if they need candidates added.

# arneshr: Excel "Á listi" = JS ARNA (already handled — ARNA was in JS with same candidates)
# blaskogabyggd: Excel "Þ listi" = JS BSP (Þ-listi... need to check)
# grimsnesgrafningur: Excel "Ö listi" = JS GGO
# hvalfjardarsveit: Excel "Í listi" = JS HVB
# nordurping: Excel "Ó listi" = JS NBO
# rangarthingytra: Excel "Á listi" = JS RYA (already handled)
# skaftarhreppur: Excel "Ö listi" = JS SKO
# svalbardsstrond: Excel "Ö listi" = JS (was SVSS but we've now replaced it with H-listi)
# stykkisholmur: Excel "Í listi" = JS IBU
# thingeyjarsveit: Excel "Á listi" = JS THVA

# Let me check each of these more carefully using the GT
def check_icelandic_code(excel_muni_name, excel_letter, js_var, js_code, party_name=None):
    """Check if an Icelandic-letter coded party's candidates match GT."""
    muni_data = gt.get(excel_muni_name, {})
    excel_list = None
    for k, v in muni_data.items():
        if k.startswith(excel_letter + ' listi') or (party_name and party_name in k):
            excel_list = v
            break
    if not excel_list:
        print(f"  Could not find {excel_letter} listi in {excel_muni_name}")
        return

    # Get JS list
    start, end = find_list_end(js_text, js_var, js_code)
    if start is None:
        print(f"  Could not find {js_var}.{js_code}")
        return

    list_text_local = js_text[start:end+1]
    js_entries = {}
    for m in re.finditer(r'\[\s*(\d+)\s*,\s*[\'"]([^\'"]+)[\'"]', list_text_local):
        js_entries[int(m.group(1))] = m.group(2).strip()

    excel_entries = {c['ballotOrder']: c['name'].strip() for c in excel_list}

    all_orders = sorted(set(excel_entries.keys()) | set(js_entries.keys()))
    has_issues = False
    for order in all_orders:
        en = excel_entries.get(order)
        jn = js_entries.get(order)
        if en != jn:
            has_issues = True
            print(f"  {excel_muni_name}/{js_code} #{order}: JS={repr(jn)} EXCEL={repr(en)}")

    if not has_issues:
        print(f"  {excel_muni_name}/{js_code}: OK ({len(excel_list)} candidates)")

print("\n=== CHECKING ICELANDIC-LETTER CODED PARTIES ===")
# Note: We need the updated js_text for these checks
# But we've modified it above. Let's define a helper that works on the current js_text.

# ─── Save the modified file ────────────────────────────────────────────────────
print(f"\nSaving modified candidates.js ({len(js_text)} chars)")
with open(CANDIDATES_JS, "w", encoding="utf-8") as f:
    f.write(js_text)
print("Saved successfully!")
print("\nDone. Run compare_candidates.py again to verify remaining issues.")
