"""
apply_heimild.py  —  patch heimild fields into candidates.js

Usage:
    python scripts/apply_heimild.py scan_results/heimild_RVK.json [--dry-run]

Each result file is a JSON array of objects:
    [
      {
        "muni": "RVK",
        "name": "Jón Jónsson",
        "ballot": 1,
        "heimild": [
          { "url": "https://...", "label": "Wikipedia" }
        ]
      },
      ...
    ]

The script finds the matching candidate in candidates.js (by muni section +
ballot number) and inserts/replaces the heimild field right after the bio line.
"""

import re, json, sys, shutil
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
CANDIDATES_JS = ROOT / "js" / "data" / "candidates.js"

def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    files = [a for a in args if not a.startswith("--")]

    if not files:
        print("Usage: python scripts/apply_heimild.py <result_file.json> [--dry-run]")
        sys.exit(1)

    content = CANDIDATES_JS.read_text(encoding="utf-8")
    changed = 0
    skipped = 0

    for fpath in files:
        results = json.loads(Path(fpath).read_text(encoding="utf-8"))
        print(f"\nProcessing {fpath} ({len(results)} entries)...")

        for entry in results:
            muni = entry["muni"]
            name = entry["name"]
            ballot = entry["ballot"]
            heimild = entry.get("heimild", [])

            if not heimild:
                skipped += 1
                continue

            # Build the heimild JS snippet
            items = ", ".join(
                f"{{ url: '{h['url']}', label: '{h['label']}' }}"
                for h in heimild
            )
            heimild_js = f"        heimild: [{items}],"

            # Find the candidate block: look for [ballot, 'name', ...] near a bio line
            # Strategy: find "ballot, 'name'" pattern, then insert heimild after bio:
            # We match the bio line and inject heimild right after it.

            # Pattern: bio: '...' (single line, possibly with escaped chars)
            # We'll search for the combination of ballot number + name to anchor,
            # then replace bio line with bio + heimild.

            # Anchor pattern: [ballot, 'name' — allow 1 or more spaces after comma
            anchor = re.escape(f"[{ballot},") + r"\s+" + re.escape(f"'{name}'")
            anchor_match = re.search(anchor, content)
            if not anchor_match:
                print(f"  WARN: could not find [{ballot}, '{name}'] in {muni}")
                skipped += 1
                continue

            # Find bio line after this anchor (within ~3000 chars)
            search_start = anchor_match.start()
            search_end = search_start + 3000
            chunk = content[search_start:search_end]

            # Check if heimild already present
            if re.search(r'heimild:', chunk):
                print(f"  SKIP (heimild exists): {name}")
                skipped += 1
                continue

            # Find the bio line
            bio_match = re.search(r"(        bio: '(?:[^'\\]|\\.)*',)", chunk)
            if not bio_match:
                print(f"  WARN: no bio line found near [{ballot}, '{name}']")
                skipped += 1
                continue

            old_bio_line = bio_match.group(1)
            new_bio_line = old_bio_line + "\n" + heimild_js

            # Replace only this occurrence (use the absolute position)
            abs_start = search_start + bio_match.start()
            abs_end = search_start + bio_match.end()

            if dry_run:
                print(f"  DRY: {name} ({muni}.{ballot}) -> {len(heimild)} source(s)")
            else:
                content = content[:abs_start] + new_bio_line + content[abs_end:]
                print(f"  OK:  {name} ({muni}.{ballot}) -> {len(heimild)} source(s)")
            changed += 1

    print(f"\nSummary: {changed} patched, {skipped} skipped.")

    if not dry_run and changed > 0:
        backup = CANDIDATES_JS.with_suffix(f".js.bak_{datetime.now():%Y%m%d_%H%M%S}")
        shutil.copy(CANDIDATES_JS, backup)
        CANDIDATES_JS.write_text(content, encoding="utf-8")
        print(f"Written to {CANDIDATES_JS}  (backup: {backup.name})")
    elif dry_run:
        print("(dry-run — no files written)")

if __name__ == "__main__":
    main()
