"""Debug single-row apply for HAF.B.3 to find the bug."""
import re, sys, io, json
from pathlib import Path

sys.path.insert(0, 'temp')
import apply_all_ruv_bios as m

src = open('js/data/candidates.js', encoding='utf-8').read()
ruv = json.load(open('scan_results/ruv_bios.json', encoding='utf-8'))
arni = next(e for e in ruv if e.get('muni_const') == 'HAF' and e.get('party_code') == 'B' and e.get('ballot') == 3)

cs, ce = m.find_const_block(src, 'HAF')
print(f'HAF const: {cs}..{ce}')

ps, pe = m.find_party_block(src, cs, ce, 'B')
print(f'HAF.B party: {ps}..{pe}')

cand = m.find_candidate_row(src, ps, pe, 3)
print(f'Ballot 3 row: {cand}')
rs, re_pos = cand
row_text = src[rs:re_pos]
print(f'Row text length: {len(row_text)}')
print(f'Row text starts: {row_text[:200]!r}')
print(f'Row text ends: {row_text[-200:]!r}')

# Now apply update_bio_in_row
new_row = m.update_bio_in_row(row_text, arni['new_bio'])
print(f'\nNew row length: {len(new_row) if new_row else "None"}')
if new_row:
    print(f'New row ends: {new_row[-300:]!r}')
    # Check for any literal newline (unescaped) in new_row
    # Should only have newlines OUTSIDE quoted strings (between fields), not inside bio string
    # Find the bio string boundaries
    open('temp/arni_test.js', 'w', encoding='utf-8').write('const x = ' + new_row + ';\n')
    print('Wrote arni_test.js')
    bio_m = re.search(r"bio: '((?:[^'\\\\]|\\\\.)*)'", new_row)
    if bio_m:
        bio_str = bio_m.group(1)
        print(f'\nBio content length: {len(bio_str)}')
        print(f'Bio has literal \\n: {chr(10) in bio_str}')
        # Bio should have escaped \n as 2 chars
        print(f'Bio has \\\\n (escape): {chr(92) + chr(110) in bio_str}')
        # Try writing to file and verify it parses
        open('temp/arni_test.js', 'w', encoding='utf-8').write('const x = ' + new_row + ';\n')
        print(f'Wrote temp/arni_test.js')
    else:
        print('Could not extract bio')
