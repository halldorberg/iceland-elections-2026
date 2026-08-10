"""Build the new Vinir Mos L-list rows for candidates.js."""
import json, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r'F:\Claude Projects\iceland-elections')
cands = json.load(open(ROOT / 'temp' / 'vinirmos_processed.json', encoding='utf-8'))
by_ballot = {c['ballot']: c for c in cands}

def title_case_is(s):
    s = s.strip()
    if not s: return s
    if s.isupper():
        # Lowercase but keep first letter; manual sentence case
        words = s.split()
        out = []
        for i, w in enumerate(words):
            if w in ('OG', 'Í', 'Á'):
                out.append(w.lower() if i > 0 else w[0] + w[1:].lower())
            elif len(w) > 1:
                out.append(w[0] + w[1:].lower())
            else:
                out.append(w)
        return ' '.join(out)
    return s

def js_str(s):
    """Escape for JS single-quoted string."""
    return s.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n')

# Bio: connect Icelandic personal "Ég" voice → 3rd person summary
# Just use the bio text as-is in 3rd person reformulation? Too much rewriting.
# Simpler: prefix with "<Name> segir frá sér: " or just use the text directly.
# Per user's prior preference, keep concise. Use the source text but in 3rd person if natural.

def make_row(c, name_override=None):
    name = name_override or c['name']
    occ = title_case_is(c['occupation'])
    img = c.get('image_path')
    img_part = f", '{img}'" if img else ''
    bio = c['bio'].strip()
    if bio:
        # Convert from "Ég" first-person to 3rd-person briefly
        bio_3p = bio.replace('Ég ', f'{name} ').replace(' ég ', f' hann/hún ')
        # Cap length: keep all paragraphs but no more than ~600 chars
        bio_clean = ' '.join(bio_3p.split())[:1200]
        heimild = "[{ url: 'https://www.vinirmos.is/frambjodendur-1', label: 'vinirmos.is' }]"
        details = f", {{ age: null, bio: '{js_str(bio_clean)}', interests: null, social: null, heimild: {heimild}, news: [] }}"
    else:
        details = ''
    return f"      [{c['ballot']:2d}, '{js_str(name)}', '{js_str(occ)}'{img_part}{details}],"

# Print rows in ballot order, including Orri at #17 (keep his existing entry, no photo)
existing_orri = "      [17, 'Orri Grétar Valgeirsson',           'Óþekkt'],"
existing_paul = None  # Páll has new data via #22

# Names override map for spelling fixes (page is sometimes wrong, ours sometimes wrong)
NAME_FIX = {
    7: 'Katarzyna Krystyna Krolikowska',  # page-correct (was "Krolokowska" in our data)
    18: 'Kristín Eva Ólafsdóttir',  # ours-correct (page strips accents)
}

rows = []
for n in range(1, 23):
    if n == 17:
        rows.append(existing_orri)
        continue
    if n in by_ballot:
        c = by_ballot[n]
        rows.append(make_row(c, name_override=NAME_FIX.get(n)))
    # else: skip

print('\n'.join(rows))

# Also save to file
(ROOT / 'temp' / 'vinirmos_rows.txt').write_text('\n'.join(rows) + '\n', encoding='utf-8')
print(f'\n\nwrote temp/vinirmos_rows.txt ({len(rows)} rows)')
