"""Preview each address strip in candidates.js with before/after, before
running the actual strip."""
import re, sys, io
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import strip_addresses as sa
from strip_addresses import strip_addresses, ADDRESS_PATTERN
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

src = (Path(__file__).parent.parent / "js" / "data" / "candidates.js").read_text(encoding="utf-8")
matches = list(re.finditer(r"bio:\s*'((?:[^'\\]|\\.)*)'", src))
print(f"Total bios in candidates.js: {len(matches)}")
for m in matches:
    raw = m.group(1)
    bio = raw.replace("\\'", "'")
    new, n = strip_addresses(bio)
    if n == 0:
        continue
    # candidate name lookup
    row_start = src.rfind("[", 0, m.start())
    nm = re.match(r"\[\s*\d+\s*,\s*'((?:[^'\\]|\\.)*)'", src[row_start:row_start+200])
    name = nm.group(1).replace("\\'", "'") if nm else "?"
    print(f"\n=== {name} (n={n})")
    # find each match span and show before/after context
    for am in ADDRESS_PATTERN.finditer(bio):
        s, e = am.start(), am.end()
        before = bio[max(0,s-50):e+50]
        print(f"  match: {am.group(0)!r}")
        print(f"  before: ...{before}...")
    print(f"  after: {new[:300]}...")
