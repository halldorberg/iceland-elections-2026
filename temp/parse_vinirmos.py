"""Parse vinirmos.is page properly."""
import re, sys, io, json, html
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r'F:\Claude Projects\iceland-elections')
src = (ROOT / 'temp' / 'vinirmos.html').read_text(encoding='utf-8')

# The candidate data is embedded as JSON-encoded HTML in script tags or data attrs
# First, find the part where it's encoded with &quot; (HTML-attribute encoded JSON)
src_unescaped = src.replace('&quot;', '"').replace('&amp;', '&').replace('&#39;', "'").replace('&lt;', '<').replace('&gt;', '>')

# Pattern: each candidate item is a JSON object with title/description/image fields
# Match them flexibly
candidates = []
# Find all "title": "X. sæti | Name" with following description and image
# Use non-greedy match across small region
pattern = re.compile(
    r'"title":\s*"(\d+)\.\s*sæti\s*\|\s*([^"]+?)"'
    r'.*?'
    r'"description":\s*"((?:[^"\\]|\\.)*)"'
    r'.*?'
    r'"assetUrl":\s*"([^"]+)"',
    re.DOTALL
)

for m in pattern.finditer(src_unescaped):
    ballot = int(m.group(1))
    name = m.group(2).strip()
    desc_raw = m.group(3)
    img_url = m.group(4)
    # desc_raw is a JSON string content; unescape JSON escapes properly
    try:
        desc = json.loads('"' + desc_raw + '"')
    except Exception:
        # Fallback: manual unescape
        desc = desc_raw.replace('\\"', '"').replace('\\/', '/').replace('\\n', '\n').replace('\\t', '\t')
    # Now strip HTML
    desc = re.sub(r'<br\s*/?>', '\n', desc, flags=re.I)
    desc = re.sub(r'</p>', '\n\n', desc, flags=re.I)
    desc = re.sub(r'<[^>]+>', '', desc)
    desc = html.unescape(desc)
    desc = re.sub(r'[ \t]+', ' ', desc)
    desc = re.sub(r'\n{3,}', '\n\n', desc).strip()
    # Split into occupation (first line, often ALL CAPS) + bio paragraphs
    paragraphs = [p.strip() for p in desc.split('\n\n') if p.strip()]
    if not paragraphs:
        occupation = ''
        bio = ''
    else:
        first = paragraphs[0]
        if first.isupper() and len(first) < 80:
            occupation = first
            bio = '\n\n'.join(paragraphs[1:]).strip()
        else:
            # First line might be ALL CAPS but mixed
            lines = first.split('\n')
            if lines[0].isupper() and len(lines[0]) < 80:
                occupation = lines[0].strip()
                rest = '\n'.join(lines[1:]).strip()
                bio = (rest + '\n\n' + '\n\n'.join(paragraphs[1:])).strip()
            else:
                occupation = ''
                bio = '\n\n'.join(paragraphs).strip()
    candidates.append({'ballot': ballot, 'name': name, 'occupation': occupation, 'bio': bio, 'image_url': img_url})

candidates.sort(key=lambda c: c['ballot'])
print(f'extracted {len(candidates)} candidates\n')
seen = set()
unique = []
for c in candidates:
    if c['ballot'] in seen: continue
    seen.add(c['ballot']); unique.append(c)
candidates = unique
print(f'unique by ballot: {len(candidates)}\n')

for c in candidates:
    print(f'  [{c["ballot"]:2d}] {c["name"]}')
    print(f'       occ: {c["occupation"]}')
    print(f'       bio: {c["bio"][:200]}{"..." if len(c["bio"])>200 else ""}')
    print()

json.dump(candidates, open(ROOT / 'temp' / 'vinirmos_candidates.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'wrote temp/vinirmos_candidates.json ({len(candidates)} entries)')
