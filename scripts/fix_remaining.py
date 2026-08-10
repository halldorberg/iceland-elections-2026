#!/usr/bin/env python3
"""Fix remaining discrepancies after fix_duplicates.py run."""

import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BACKSLASH = chr(92)

with open('F:/Claude Projects/iceland-elections/js/data/candidates.js', encoding='utf-8') as f:
    content = f.read()

print(f"Loaded ({len(content)} chars)")

changes = []


def find_list_in_muni(text, muni_var, party_code):
    """Find (start, end) of list array for given muni+party."""
    muni_start = text.find(f'\nconst {muni_var} = {{')
    if muni_start == -1:
        return None, None

    muni_end = text.find('\nconst ', muni_start + 1)
    if muni_end == -1:
        muni_end = len(text)

    party_pat = re.compile(r'\n  ' + re.escape(party_code) + r'\s*:\s*\{')
    pm = party_pat.search(text, muni_start, muni_end)
    if not pm:
        return None, None

    list_pat = re.compile(r'\blist\s*:\s*\[')
    lm = list_pat.search(text, pm.end(), muni_end)
    if not lm:
        return None, None

    bracket = lm.end() - 1
    depth = 0
    pos = bracket
    in_string = False
    string_char = None
    while pos < len(text):
        c = text[pos]
        if in_string:
            if c == BACKSLASH:
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
                    return bracket, pos
        pos += 1
    return None, None


def fix_name(text, muni_var, party_code, ballot_order, old_name, new_name):
    """Fix a candidate name."""
    start, end = find_list_in_muni(text, muni_var, party_code)
    if start is None:
        print(f"  ERROR: Cannot find {muni_var}.{party_code}")
        return text

    list_text = text[start:end+1]
    pattern = re.compile(
        r'(\[' + str(ballot_order) + r'\s*,\s*)[\'"]' + re.escape(old_name) + r'[\'"]'
    )
    m = pattern.search(list_text)
    if not m:
        # Try with double quotes
        pattern2 = re.compile(
            r'(\[' + str(ballot_order) + r'\s*,\s*)"' + re.escape(old_name) + r'"'
        )
        m = pattern2.search(list_text)

    if not m:
        print(f"  ERROR: #{ballot_order} '{old_name}' not found in {muni_var}.{party_code}")
        return text

    new_list = list_text[:m.start()] + m.group(1) + "'" + new_name + "'" + list_text[m.end():]
    print(f"  Fixed {muni_var}.{party_code} #{ballot_order}: '{old_name}' -> '{new_name}'")
    return text[:start] + new_list + text[end+1:]


def add_candidate(text, muni_var, party_code, ballot_order, name):
    """Add a candidate at end of list."""
    start, end = find_list_in_muni(text, muni_var, party_code)
    if start is None:
        print(f"  ERROR: Cannot find {muni_var}.{party_code}")
        return text

    new_entry = f"\n      [{ballot_order}, '{name}', 'Frambjóðandi'],"
    new_text = text[:end] + new_entry + '\n    ' + text[end:]
    print(f"  Added {muni_var}.{party_code} #{ballot_order}: '{name}'")
    return new_text


def fix_double_space(text, muni_var, party_code, ballot_order, old_name):
    """Fix double spaces in a name."""
    new_name = re.sub(r'  +', ' ', old_name).strip()
    if new_name != old_name:
        return fix_name(text, muni_var, party_code, ballot_order, old_name, new_name)
    return text


# ─── Name mismatches to fix ────────────────────────────────────────────────────
name_fixes = [
    # (muni_var, party_code, ballot_order, old_name, new_name)
    ('BSG', 'BST', 5, 'Kristján Einir Traustason', 'Kristján Einir Trautason'),
    ('BLV', 'MMM', 5, 'Hjörtur Traustason', 'Hjörtur Trautason'),
    ('EJA', 'EJK', 8, 'Valgerður Guðrún Valdimarsdóttir', 'Valgerður Guðrún Valdimársdóttir'),
    ('HVF', 'HVB', 7, 'Áskell Þórisson', 'Áskell Þórison'),
    ('MYR', 'MYA', 4, 'Kristína Hajniková', 'Kristína Hajnikova'),
    ('NPG', 'NPM', 11, 'Monika Zyvatkauskaité', 'Monika Zyvatkauskaitė'),
    ('SKR', 'SKO', 3, 'Gunnar Pétur Sigmarsson', 'Gunnar Pétur Sigmársson'),
    ('VOG', 'VOE', 3, 'Friðrik Valdimar Árnason', 'Friðrik Valdimár Árnason'),
    ('VOG', 'VOE', 13, 'Valdimar Pétursson', 'Valdimár Pétursson'),
    ('VOG', 'VOL', 3, 'Snædís Ósk Guðjóndóttir', 'Snædís Ósk Guðjondóttir'),
]

# Double space fixes
double_space_fixes = [
    ('SDV', 'FJL', 2, 'Ingibjörg Ásdís  Björnsdóttir'),
    ('SDV', 'FJL', 9, 'Eiríkur  Valgeir Scott'),
    ('SDV', 'FTL', 4, 'Jónþór  Eiríksson'),
    ('SDV', 'FTL', 9, 'Anna  Lind Ragnarsdóttir'),
    ('STK', 'IBU', 3, 'Kristján  Hildibrandsson'),
]

# Missing last candidates
missing_last = [
    ('ARN', 'ARNA', 10, 'Guðjón Stefán Kristinsson'),
    ('BSG', 'BSP', 14, 'Gylfi Þorkelsson'),
    ('GGR', 'GGO', 10, 'Guðjón Kjartansson'),
    ('HVF', 'HVB', 14, 'Anna Guðrún Torfadóttir'),
    ('NPG', 'NBO', 18, 'Stefán Leifur Rögnvaldsson'),
    ('RTY', 'RYA', 14, 'Pálína Kristinsdóttir'),
    ('SKR', 'SKO', 10, 'Þóranna Harðardóttir'),
    ('STK', 'IBU', 14, 'Guðmundur Valur Valtýsson'),
    ('THV', 'THVA', 14, 'Sigrún Jónsdóttir'),
]

print("\n=== FIXING NAME MISMATCHES ===")
for muni_var, party_code, ballot_order, old_name, new_name in name_fixes:
    content = fix_name(content, muni_var, party_code, ballot_order, old_name, new_name)

print("\n=== FIXING DOUBLE SPACES ===")
for muni_var, party_code, ballot_order, old_name in double_space_fixes:
    content = fix_double_space(content, muni_var, party_code, ballot_order, old_name)

print("\n=== ADDING MISSING LAST CANDIDATES ===")
for muni_var, party_code, ballot_order, name in missing_last:
    content = add_candidate(content, muni_var, party_code, ballot_order, name)

print(f"\nSaving ({len(content)} chars)")
with open('F:/Claude Projects/iceland-elections/js/data/candidates.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Saved successfully!")
