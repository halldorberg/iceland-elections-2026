"""Apply merged FJB.H bios to candidates.js.

For seats 1-9: replace the existing bio field inside the candidate
object literal. For seats 10, 11, 13, 14: extend the bare 4-element
row [seat, name, occ, photo] to include a full bio object.
"""
import re, json, sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r'F:\Claude Projects\iceland-elections')
JS = ROOT / 'js' / 'data' / 'candidates.js'
MERGE = ROOT / 'temp' / 'fjb_h_merge_output.json'

data = json.load(open(MERGE, encoding='utf-8'))

# Existing seats that already have a bio object - just replace bio
HAS_BIO = {1, 2, 3, 4, 5, 6, 7, 8, 9}
NEEDS_OBJ = {10, 11, 13, 14}

# Slugs for RÚV kosningapróf (lowercased, ascii)
RUV_SLUGS = {
    10: 'andri-vidar-viglundsson',
    11: 'adalbjorg-snorradottir',
    13: 'katrin-freysdottir',
    14: 'arni-helgason',
}

src = JS.read_text(encoding='utf-8')


def js_escape(s):
    """Escape for inside JS single-quote string."""
    return (s.replace('\\', '\\\\')
              .replace("'", "\\'")
              .replace('\n', '\\n'))


# Drive folder source
DRIVE_URL = 'https://drive.google.com/drive/folders/1Uzo2WqCXwKfIP7pKDrblKNLcvyDgnVVv'
DRIVE_LABEL = 'H-listinn — kynningar á Google Drive'

new_src = src
applied = 0

for d in data:
    seat = d['seat']
    name = d['name']
    bio = d['merged_bio']
    bio_escaped = js_escape(bio)

    if seat in HAS_BIO:
        # Match `bio: '...'` inside this seat's row. The bio appears after
        # the name + occupation + photo, then `age:`, then `bio:` — so we
        # find the row by seat+name, then find the next bio: '...' field.
        pat = re.compile(
            r"(\[" + str(seat) + r",\s*'" + re.escape(name) + r"',[^\[]*?bio:\s*')"
            r"(?:[^'\\]|\\.)+"
            r"(')",
            re.S)
        m = pat.search(new_src)
        if not m:
            print(f'  {seat:>2}  {name:<35}  BIO NOT FOUND')
            continue
        new_src = new_src[:m.start()] + m.group(1) + bio_escaped + m.group(2) + new_src[m.end():]
        applied += 1
        print(f'  {seat:>2}  {name:<35}  bio REPLACED ({len(bio)} chars)')

    elif seat in NEEDS_OBJ:
        # Match bare 4-element row [seat, 'name', 'occ', 'photo'] and extend to 5
        pat = re.compile(
            r"\[" + str(seat) + r",\s*'" + re.escape(name) + r"',\s*'([^']*)',\s*'(images/candidates/[^']+)'\]")
        m = pat.search(new_src)
        if not m:
            print(f'  {seat:>2}  {name:<35}  BARE ROW NOT FOUND')
            continue
        occ = m.group(1)
        photo = m.group(2)
        ruv_slug = RUV_SLUGS[seat]
        new_row = (
            f"[{seat}, '{name}', '{occ}', '{photo}', " "{ age: null, "
            f"bio: '{bio_escaped}', "
            f"heimild: [{{ url: '{DRIVE_URL}', label: '{DRIVE_LABEL}' }}, "
            f"{{ url: 'https://kosningaprof.ruv.is/frambjodandi/{ruv_slug}-6250-h-{seat}/', label: 'RÚV kosningapróf' }}], "
            "interests: null, social: null, news: [] }]"
        )
        new_src = new_src[:m.start()] + new_row + new_src[m.end():]
        applied += 1
        print(f'  {seat:>2}  {name:<35}  ROW EXTENDED ({len(bio)} chars)')

# Bracket sanity
braces = new_src.count('{') - new_src.count('}')
brackets = new_src.count('[') - new_src.count(']')
print(f'\nApplied {applied} bios')
print(f'braces: {braces}, brackets: {brackets}')

if braces == 0 and brackets == 0 and applied >= 13:
    JS.write_text(new_src, encoding='utf-8')
    print('Written.')
else:
    print('NOT WRITTEN — bracket sanity failed or applied count low.')
