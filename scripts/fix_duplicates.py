#!/usr/bin/env python3
"""
Fix duplicate party entries in candidates.js.
For each duplicate:
1. Add missing last candidate to first occurrence (if second has more)
2. Remove second occurrence entirely

Also adds the A party for Borgarbyggð which was added with invalid code BBD_A.
"""

import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = "F:/Claude Projects/iceland-elections"
CANDIDATES_JS = BASE + "/js/data/candidates.js"

with open(CANDIDATES_JS, encoding='utf-8') as f:
    content = f.read()

print(f"Loaded candidates.js ({len(content)} chars)")

def find_party_block(text, muni_var, party_code, occurrence=1):
    """
    Find the start and end positions of a party block within a municipality const.
    Returns (party_key_pos, party_block_end) or (None, None).
    occurrence=1 means first, occurrence=2 means second.
    """
    muni_start = text.find(f'\nconst {muni_var} = {{')
    if muni_start == -1:
        return None, None

    muni_end_search = text.find('\nconst ', muni_start + 1)
    if muni_end_search == -1:
        muni_end_search = len(text)

    muni_block = text[muni_start:muni_end_search]

    party_pat = re.compile(r'\n  ' + re.escape(party_code) + r'\s*:\s*\{')
    occs = list(party_pat.finditer(muni_block))

    if len(occs) < occurrence:
        return None, None

    occ = occs[occurrence - 1]
    # Find the closing }, of this party block
    # Start from the opening { of the party object
    block_start = muni_start + occ.start()  # position of \n  CODE : {

    # Find opening brace
    brace_pos = text.index('{', muni_start + occ.start())
    depth = 0
    pos = brace_pos
    in_string = False
    string_char = None
    while pos < len(text):
        c = text[pos]
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
                    # pos is now at closing } of party object
                    # The full entry is: \n  CODE: { ... },
                    # Find the comma and newline after }
                    end_pos = pos
                    # The block text (including newline+code+colon...) is:
                    block_text_start = muni_start + occ.start()  # position of leading \n
                    # end: pos + 1 (or pos + 2 for trailing comma)
                    # We want to find the position right after },
                    after = pos + 1
                    while after < len(text) and text[after] in (',', ' ', '\r'):
                        after += 1
                    return block_text_start, pos  # start of \n, end at }
        pos += 1
    return None, None


def find_list_in_party(text, muni_var, party_code, occurrence=1):
    """Find the list array within a party block (Nth occurrence)."""
    muni_start = text.find(f'\nconst {muni_var} = {{')
    if muni_start == -1:
        return None, None

    muni_end_search = text.find('\nconst ', muni_start + 1)
    if muni_end_search == -1:
        muni_end_search = len(text)

    muni_block = text[muni_start:muni_end_search]

    party_pat = re.compile(r'\n  ' + re.escape(party_code) + r'\s*:\s*\{')
    occs = list(party_pat.finditer(muni_block))

    if len(occs) < occurrence:
        return None, None

    occ = occs[occurrence - 1]
    search_from = muni_start + occ.end()

    # Find list: [
    list_pat = re.compile(r'\blist\s*:\s*\[')
    lm = list_pat.search(text, search_from)
    if not lm or lm.start() > muni_end_search + muni_start:
        return None, None

    bracket = lm.end() - 1
    depth = 0
    pos = bracket
    in_string = False
    string_char = None
    while pos < len(text):
        c = text[pos]
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
                    return bracket, pos
        pos += 1
    return None, None


def get_last_candidate(text, muni_var, party_code, occurrence=1):
    """Get the last candidate entry from a party list."""
    start, end = find_list_in_party(text, muni_var, party_code, occurrence)
    if start is None:
        return None
    list_text = text[start:end+1]
    entries = list(re.finditer(r'\[\s*(\d+)\s*,\s*[\'"]([^\'"]+)[\'"]', list_text))
    if not entries:
        return None
    last = entries[-1]
    return int(last.group(1)), last.group(2)


def add_candidate_to_first_occurrence(text, muni_var, party_code, ballot_order, name):
    """Add a missing candidate to the first occurrence of a party list."""
    start, end = find_list_in_party(text, muni_var, party_code, occurrence=1)
    if start is None:
        print(f"  ERROR: Cannot find list for {muni_var}.{party_code}")
        return text
    new_entry = f"\n      [{ballot_order}, '{name}', 'Frambjóðandi'],"
    new_text = text[:end] + new_entry + '\n    ' + text[end:]
    print(f"  Added #{ballot_order} '{name}' to {muni_var}.{party_code} (first occurrence)")
    return new_text


def remove_second_occurrence(text, muni_var, party_code):
    """Remove the second occurrence of a party block from a municipality."""
    muni_start = text.find(f'\nconst {muni_var} = {{')
    if muni_start == -1:
        print(f"  ERROR: Cannot find const {muni_var}")
        return text

    muni_end_search = text.find('\nconst ', muni_start + 1)
    if muni_end_search == -1:
        muni_end_search = len(text)

    muni_block = text[muni_start:muni_end_search]

    party_pat = re.compile(r'\n  ' + re.escape(party_code) + r'\s*:\s*\{')
    occs = list(party_pat.finditer(muni_block))

    if len(occs) < 2:
        print(f"  WARNING: {muni_var}.{party_code} has < 2 occurrences")
        return text

    # Second occurrence position in full text
    second_occ = occs[1]
    block_start_in_muni = second_occ.start()  # position of leading \n in muni_block
    block_start_in_text = muni_start + block_start_in_muni

    # Find the brace start
    brace_pos = text.index('{', block_start_in_text)
    depth = 0
    pos = brace_pos
    in_string = False
    string_char = None
    while pos < len(text):
        c = text[pos]
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

    # pos is at closing } of second occurrence
    # Remove from block_start_in_text to pos (inclusive)
    # Also remove trailing comma and whitespace until next \n
    end_pos = pos + 1  # after }
    if end_pos < len(text) and text[end_pos] == ',':
        end_pos += 1
    # Remove the block
    removed = text[block_start_in_text:end_pos]
    new_text = text[:block_start_in_text] + text[end_pos:]
    print(f"  Removed second occurrence of {muni_var}.{party_code} ({end_pos - block_start_in_text} chars)")
    return new_text


# ─── Duplicates to fix ─────────────────────────────────────────────────────────
# For each: check if second has more candidates, add missing one to first, then remove second
# Format: (muni_var, party_code, missing_candidate_if_any)
# missing_candidate = (ballot_order, name) or None if counts are equal

duplicates_to_fix = [
    # (muni_var, party_code, missing_ballot_order, missing_name)
    # AKU: AL - second has 20, first has 19. Missing: #20 Ingibjörg Margrét Þórhallsdóttir
    ('AKU', 'AL', 20, 'Ingibjörg Margrét Þórhallsdóttir'),
    # GAR: GB - second has 22, first has 21. Missing: #22 Þorvaldur Þorsteinsson
    ('GAR', 'GB', 22, 'Þorvaldur Þorsteinsson'),
    # SEL: SCS - second has 14, first has 13. Missing: #14 Guðmundur Ari Sigurjónsson
    ('SEL', 'SCS', 14, 'Guðmundur Ari Sigurjónsson'),
    # VOG: FYRS - second has 14, first has 13. Missing: #14 Anton Helgi Hermóðsson
    ('VOG', 'FYRS', 14, 'Anton Helgi Hermóðsson'),
    # VOG: VOE - second has 14, first has 13. Missing: #14 Þóra Bragadóttir
    ('VOG', 'VOE', 14, 'Þóra Bragadóttir'),
    # VOG: VOL - second has 14, first has 13. Missing: #14 Gísli Stefánsson
    ('VOG', 'VOL', 14, 'Gísli Stefánsson'),
    # NPG: NPM - second has 18, first has 17. Missing: #18 Guðmundur A. Hólmgeirsson
    ('NPG', 'NPM', 18, 'Guðmundur A. Hólmgeirsson'),
    # NPG: NPV - second has 18, first has 17. Missing: #18 Trausti Aðalsteinsson
    ('NPG', 'NPV', 18, 'Trausti Aðalsteinsson'),
    # HVG: OKH - second has 14, first has 13. Missing: #14 Sandra Sigurðardóttir
    ('HVG', 'OKH', 14, 'Sandra Sigurðardóttir'),
    # RTE: NRE - second has 14, first has 13. Missing: #14 Christiane Leonor Bahner
    ('RTE', 'NRE', 14, 'Christiane Leonor Bahner'),
    # MYR: MYA - second has 10, first has 9. Missing: #10 Þorgeir Guðnason
    ('MYR', 'MYA', 10, 'Þorgeir Guðnason'),
    # MYR: MYZ - second has 10, first has 9. Missing: #10 Páll Tómasson
    ('MYR', 'MYZ', 10, 'Páll Tómasson'),
    # BSG: BST - second has 14, first has 13. Missing: #14 Guðrún Svanhvít Magnúsdóttir
    ('BSG', 'BST', 14, 'Guðrún Svanhvít Magnúsdóttir'),
    # FHR: FLI - second has 10, first has 9. Missing: #10 Stefán Geirsson
    ('FHR', 'FLI', 10, 'Stefán Geirsson'),
    # FHR: FLT - second has 10, first has 9. Missing: #10 Guðrún Jónsdóttir
    ('FHR', 'FLT', 10, 'Guðrún Jónsdóttir'),
    # HMR: HRL - second has 10, first has 9. Missing: #10 Stefán G. Arngrímsson
    ('HMR', 'HRL', 10, 'Stefán G. Arngrímsson'),
    # GGR: GGA - both have 10 (no missing)
    ('GGR', 'GGA', None, None),
    # SGN: SGE - second has 10, first has 9. Missing: #10 Tanja Rún Jóhannsdóttir
    ('SGN', 'SGE', 10, 'Tanja Rún Jóhannsdóttir'),
    # SGN: SGL - both have 10 (no missing)
    ('SGN', 'SGL', None, None),
    # EJA: EJF - second has 14, first has 13. Missing: #14 Linda Margrét Sigurðardóttir
    ('EJA', 'EJF', 14, 'Linda Margrét Sigurðardóttir'),
    # EJA: EJK - second has 14, first has 13. Missing: #14 Ásta Arnbjörg Pétursdóttir
    ('EJA', 'EJK', 14, 'Ásta Arnbjörg Pétursdóttir'),
    # HGS: HGG - both have 10 (no missing)
    ('HGS', 'HGG', None, None),
    # HGS: HGH - both have 10 (no missing)
    ('HGS', 'HGH', None, None),
    # HNB: HBA - second has 18, first has 17. Missing: #18 Þorleifur Ingvarsson
    ('HNB', 'HBA', 18, 'Þorleifur Ingvarsson'),
    # HNT: NHV - second has 14, first has 13. Missing: #14 Guðmundur Haukur Sigurðsson
    ('HNT', 'NHV', 14, 'Guðmundur Haukur Sigurðsson'),
    # SFJ: SFL - both have 18 (no missing)
    ('SFJ', 'SFL', None, None),
    # STK: FLS - second has 14, first has 13. Missing: #14 Guðmundur Kolbeinn Björnsson
    ('STK', 'FLS', 14, 'Guðmundur Kolbeinn Björnsson'),
    # GFJ: GFB - second has 14, first has 13. Missing: #14 Guðni E. Hallgrímsson
    ('GFJ', 'GFB', 14, 'Guðni E. Hallgrímsson'),
    # GFJ: GFD - second has 14, first has 13. Missing: #14 Ásgeir Valdimársson
    ('GFJ', 'GFD', 14, 'Ásgeir Valdimársson'),
    # BLV: MMM - second has 14, first has 13. Missing: #14 Matthildur Guðmundsdóttir
    ('BLV', 'MMM', 14, 'Matthildur Guðmundsdóttir'),
    # BLV: BBK - second has 14, first has 13. Missing: #14 Hafþór Gunnarsson
    ('BLV', 'BBK', 14, 'Hafþór Gunnarsson'),
    # SDV: FJL - both have 10 (no missing)
    ('SDV', 'FJL', None, None),
    # SDV: FTL - second has 10, first has 9. Missing: #10 Friðrik Sigurðsson
    ('SDV', 'FTL', 10, 'Friðrik Sigurðsson'),
    # VBG: NYS - second has 14, first has 13. Missing: #14 Jóhann Pétur Ágústsson
    ('VBG', 'NYS', 14, 'Jóhann Pétur Ágústsson'),
    # VBG: STV - second has 14, first has 13. Missing: #14 Ásgeir Sveinsson
    ('VBG', 'STV', 14, 'Ásgeir Sveinsson'),
    # STD: VGV - second has 10, first has 9. Missing: #10 Pétur Matthíasson
    ('STD', 'VGV', 10, 'Pétur Matthíasson'),
    # STD: SBD - both have 10 (no missing)
    ('STD', 'SBD', None, None),
    # RKH: ROA - second has 10, first has 9. Missing: #10 Karl Kristjánsson
    ('RKH', 'ROA', 10, 'Karl Kristjánsson'),
    # THV: THVL - second has 14, first has 13. Missing: #14 Natalía Sól Jóhannsdóttir
    ('THV', 'THVL', 14, 'Natalía Sól Jóhannsdóttir'),
    # THV: THVN - second has 14, first has 13. Missing: #14 Halldór Þorlákur Sigurðsson
    ('THV', 'THVN', 14, 'Halldór Þorlákur Sigurðsson'),
    # HVF: HVA - second has 14, first has 13. Missing: #14 Andrea Ýr Arnarsdóttir
    ('HVF', 'HVA', 14, 'Andrea Ýr Arnarsdóttir'),
    # SVS: SVSS - second has 10, first has 9. Missing: #10 Waldemar Sienda
    # Wait - SVS.SVSS first has 9, but Excel H listi has 10. Second has 10.
    # But SVS already maps to 'SVSS' in municipalities.js
    # The Excel has two lists: H listi (10 cands) and Ö listi (10 cands, Icelandic letter)
    # SVSS was the existing code. We added a second SVSS for H listi.
    # Actually we need to check which list SVSS originally represented.
    # From municipalities.js: SVS partyIds: ['SVSS'] - only one party.
    # The Excel has Ö listi (Ströndungur) and H listi (Strönd til framtíðar).
    # SVSS was originally Ö listi (Ströndungur). The second SVSS is H listi.
    # So second SVSS is wrong - it's a different party.
    # We need to keep SVSS for Ö listi and add a different code for H listi.
    # Let's use 'SVSH' for H listi.
    # BUT: municipalities.js only has ['SVSS'] - we need to add SVSH there too.
    # For now, fix duplicate by renaming second SVSS -> SVSH
    # We'll handle this specially below.
    # KJO: KJA - second has 10, first has 9. Missing: #10 Sigurbjörn Hjaltason
    ('KJO', 'KJA', 10, 'Sigurbjörn Hjaltason'),
    # VPF: VOP - both have 14 (no missing)
    ('VPF', 'VOP', None, None),
    # TJR: TJN - both have 10 (no missing)
    ('TJR', 'TJN', None, None),
    # ARN: ARNS - second has 10, first has 9. Missing: #10 Eva Sigurbjörnsdóttir
    ('ARN', 'ARNS', 10, 'Eva Sigurbjörnsdóttir'),
]

# Also handle RVK which has massive duplication
# RVK duplicates: D, B, S, A, P, M, F, C, J
# These are all the big Reykjavik parties with rich data.
# The second occurrences were added by an earlier fix run.
# Let's check RVK carefully.

print("\n=== CHECKING RVK DUPLICATES ===")
rvk_parties = ['D', 'B', 'S', 'A', 'P', 'M', 'F', 'C', 'J']
for code in rvk_parties:
    start1, end1 = find_list_in_party(content, 'RVK', code, occurrence=1)
    start2, end2 = find_list_in_party(content, 'RVK', code, occurrence=2)
    if start1 is not None and start2 is not None:
        n1 = len(re.findall(r'\[\s*\d+\s*,', content[start1:end1+1]))
        n2 = len(re.findall(r'\[\s*\d+\s*,', content[start2:end2+1]))
        print(f"  RVK.{code}: occ1={n1}, occ2={n2}")

print("\n=== FIXING DUPLICATES ===")

# Process RVK first - just remove second occurrences
rvk_second_extra = {
    'D': None, 'B': None, 'S': None, 'A': None, 'P': None,
    'M': None, 'F': None, 'C': None, 'J': None
}
# Check if any RVK party needs a last candidate added
for code in rvk_parties:
    last1 = get_last_candidate(content, 'RVK', code, occurrence=1)
    last2 = get_last_candidate(content, 'RVK', code, occurrence=2)
    if last1 and last2 and last1[0] < last2[0]:
        rvk_second_extra[code] = (last2[0], last2[1])
        print(f"  RVK.{code}: need to add #{last2[0]} '{last2[1]}' before removing second occ")

# Add missing last candidates to RVK first occurrences
for code, extra in rvk_second_extra.items():
    if extra:
        content = add_candidate_to_first_occurrence(content, 'RVK', code, extra[0], extra[1])

# Remove second occurrences of RVK parties (must do in reverse to keep positions valid)
# Actually positions shift after each removal, so we remove one at a time
for code in rvk_parties:
    content = remove_second_occurrence(content, 'RVK', code)

# Now fix all the other duplicates
for muni_var, party_code, ballot_order, name in duplicates_to_fix:
    if ballot_order is not None:
        content = add_candidate_to_first_occurrence(content, muni_var, party_code, ballot_order, name)
    content = remove_second_occurrence(content, muni_var, party_code)

# Handle SVS.SVSS specially - second occurrence is a different party (H listi)
# We need to rename it from SVSS to SVSH
print("\n=== HANDLING SVS.SVSS SPECIAL CASE ===")
# Check what SVS looks like now (after removing SVSS duplicate above... wait we didn't add SVSS to the list)
# Let me check:
muni_start_svs = content.find('\nconst SVS = {')
muni_end_svs = content.find('\nconst ', muni_start_svs + 1)
svs_block = content[muni_start_svs:muni_end_svs]
svs_party_codes = re.findall(r'\n  ([A-Z][A-Z0-9]*)\s*:\s*\{', svs_block)
print(f"  SVS parties: {svs_party_codes}")

# Now handle SVS specially - it should have SVSS (Ö listi - Ströndungur)
# and SVSH (H listi - Strönd til framtíðar)
# The second SVSS was added by the fix script as "H listi - Strönd til framtíðar"
# We need to:
# 1. Add #10 Waldemar Sienda to the first SVSS
# 2. Rename second SVSS to SVSH

# First add missing candidate to first SVSS
start_svss1, end_svss1 = find_list_in_party(content, 'SVS', 'SVSS', occurrence=1)
if start_svss1:
    n1 = len(re.findall(r'\[\s*\d+\s*,', content[start_svss1:end_svss1+1]))
    print(f"  SVS.SVSS occ1 has {n1} candidates")
    if n1 < 10:
        content = add_candidate_to_first_occurrence(content, 'SVS', 'SVSS', 10, 'Waldemar Sienda')

# Count occurrences after potential add
muni_start_svs = content.find('\nconst SVS = {')
muni_end_svs = content.find('\nconst ', muni_start_svs + 1)
svs_block = content[muni_start_svs:muni_end_svs]
svss_occs = list(re.finditer(r'\n  SVSS\s*:\s*\{', svs_block))
print(f"  SVS.SVSS occurrences: {len(svss_occs)}")

if len(svss_occs) >= 2:
    # Check what the second SVSS is (should be H listi - Strönd til framtíðar)
    second_start = muni_start_svs + svss_occs[1].start()
    tagline_search = content.find('tagline:', second_start)
    tagline_end = content.find('\n', tagline_search)
    print(f"  Second SVSS tagline line: {content[tagline_search:tagline_end]}")

    # Rename second SVSS to SVSH
    # The second occurrence starts at second_start which is position of \n  SVSS:
    # We need to replace '\n  SVSS:' at that position with '\n  SVSH:'
    # But we need to be precise - only the second occurrence
    second_occ_text = svss_occs[1].group(0)  # \n  SVSS : {
    # Replace at exact position in full content
    replace_at = second_start
    old_prefix = content[replace_at:replace_at + len(second_occ_text)]
    if 'SVSS' in old_prefix:
        new_prefix = old_prefix.replace('SVSS', 'SVSH', 1)
        content = content[:replace_at] + new_prefix + content[replace_at + len(second_occ_text):]
        print(f"  Renamed second SVS.SVSS to SVSH")
    else:
        print(f"  WARNING: Could not find SVSS at expected position")

# Save
print(f"\nSaving modified candidates.js ({len(content)} chars)")
with open(CANDIDATES_JS, 'w', encoding='utf-8') as f:
    f.write(content)
print("Saved successfully!")

# Verify no more duplicates
import sys
muni_party_map = {}
current_muni = None
for line in content.split('\n'):
    m = re.match(r'^const ([A-Z]+) = \{', line)
    if m:
        current_muni = m.group(1)
        muni_party_map[current_muni] = []
    elif current_muni:
        m2 = re.match(r'^  ([A-Z][A-Z0-9]*)\s*:\s*\{', line)
        if m2:
            muni_party_map[current_muni].append(m2.group(1))

dups_remaining = []
for muni, parties in muni_party_map.items():
    seen = set()
    for p in parties:
        if p in seen:
            dups_remaining.append(f"{muni}.{p}")
        seen.add(p)

if dups_remaining:
    print(f"\nWARNING: Still {len(dups_remaining)} duplicate party entries remaining:")
    for d in dups_remaining:
        print(f"  {d}")
else:
    print("\nAll duplicates resolved!")
