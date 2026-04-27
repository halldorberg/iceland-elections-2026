"""
generate_heimild_manifest.py
Produces heimild_manifest.json: a list of candidates that have a bio
but no heimild field yet. Sorted by municipality population (descending).
"""

import re, json, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
CANDIDATES_JS = ROOT / "js" / "data" / "candidates.js"
OUT = ROOT / "heimild_manifest.json"

# Municipality order by approximate population (most populous first)
MUNI_ORDER = [
    "RVK", "KOP", "HAF", "GAR", "MOS", "AKU", "SEL", "RNB",
    "ARB", "VME", "FJB", "AKR", "BBD", "NPG", "ISF", "DVB",
    "HVG", "SST", "GRN", "FJD", "MUT", "RTE", "RTY", "OLF",
    "MYR", "HVF", "GGR", "FHR", "EJA", "BSG", "STK", "HNB",
    "KJO", "HFJ", "THV",
]

content = CANDIDATES_JS.read_text(encoding="utf-8")

# Split into per-municipality sections
sections = re.split(r'^const ([A-Z_]+) = \{', content, flags=re.MULTILINE)

# sections[0] = preamble, then pairs: [muni_id, section_body, ...]
muni_sections = {}
for i in range(1, len(sections) - 1, 2):
    muni_sections[sections[i]] = sections[i + 1]

# For each muni section, find candidates with bio but no heimild
# Candidate pattern: [ballotOrder, 'name', 'occupation', photo, { ... }]
# We need to find bio: '...' entries and check for heimild

results = []

for muni in MUNI_ORDER:
    sec = muni_sections.get(muni, "")
    if not sec:
        continue

    # Find all list entries with bio content
    # Strategy: find positions of "bio: '" (non-null bios)
    # and check if the surrounding object also has "heimild:"

    # Use a crude but reliable approach: scan for candidate name patterns
    # near bio fields

    # Find candidate array entries: [number, 'name', ...]
    cand_pattern = re.compile(
        r'\[(\d+),\s*\'([^\']+)\',\s*\'([^\']*)\',\s*(?:null|\'[^\']*\'),\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}',
        re.DOTALL
    )

    for m in cand_pattern.finditer(sec):
        ballot, name, occupation, inner = m.group(1), m.group(2), m.group(3), m.group(4)

        # Check for non-null bio
        bio_match = re.search(r"bio:\s*'([^']+)'", inner)
        if not bio_match:
            continue

        # Check for existing heimild
        if re.search(r'heimild:', inner):
            continue

        bio_text = bio_match.group(1)

        # Collect existing news URLs as potential heimild hints
        news_urls = re.findall(r"url:\s*'(https?://[^']+)'", inner)
        social_urls = re.findall(r"url:\s*'(https?://[^']+)'", inner)

        results.append({
            "muni": muni,
            "ballot": int(ballot),
            "name": name,
            "occupation": occupation,
            "bio": bio_text,
            "existing_urls": list(dict.fromkeys(news_urls)),  # deduplicated
        })

manifest = {
    "generated": "2026-04-27",
    "total": len(results),
    "candidates": results,
}

OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Written {len(results)} candidates to {OUT}")

# Summary by muni
from collections import Counter
counts = Counter(r["muni"] for r in results)
for muni in MUNI_ORDER:
    if counts[muni]:
        print(f"  {muni}: {counts[muni]}")
