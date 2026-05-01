#!/usr/bin/env python3
"""
After a photo apply, the running scan agents may have appended further
entries to their result files. The renderer would then re-display already-
applied entries alongside new ones, confusing the next review cycle.

This script reads each `photos_<date>_*.json` file, drops any entry whose
`photo_local` is already present on the candidate's row in candidates.js,
and rewrites the file with only the still-pending entries.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCAN_DIR = ROOT / "scan_results"
CANDIDATES = ROOT / "js" / "data" / "candidates.js"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        print("usage: dedupe_photo_results.py <date>")
        sys.exit(1)
    date = sys.argv[1]
    src = CANDIDATES.read_text(encoding="utf-8")
    total_dropped = 0
    total_kept = 0
    for path in sorted(SCAN_DIR.glob(f"photos_{date}*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        before = len(data.get("results", []))
        kept = []
        for r in data.get("results", []):
            local = r.get("photo_local", "")
            if local and local in src:
                # already applied — drop
                continue
            kept.append(r)
        dropped = before - len(kept)
        total_dropped += dropped
        total_kept += len(kept)
        if dropped > 0 or len(kept) == 0:
            data["results"] = kept
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"  {path.name}: kept {len(kept)} of {before} (dropped {dropped} already-applied)")
        else:
            print(f"  {path.name}: kept all {len(kept)} (none already-applied)")
    print(f"\nTotal: {total_kept} pending, {total_dropped} already-applied removed.")


if __name__ == "__main__":
    main()
