"""For partial audit batches: pull every input candidate that doesn't yet
have a result, regroup into a fresh resume batch."""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SR = ROOT / "scan_results"


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    # Collect every ID in master audit_results
    master = json.loads((SR / "audit_results.json").read_text(encoding="utf-8"))
    done_ids = set(master.keys())

    remaining: list[dict] = []
    for in_file in sorted(SR.glob("audit_in_*.json")):
        data = json.loads(in_file.read_text(encoding="utf-8"))
        for c in data.get("candidates", []):
            if c.get("id") and c["id"] not in done_ids:
                remaining.append(c)

    print(f"  Total inputs unfinished: {len(remaining)}")

    # Split into batches of 25, naming them audit_in_R01, audit_in_R02, ...
    BATCH = 25
    for i in range(0, len(remaining), BATCH):
        chunk = remaining[i:i + BATCH]
        n = i // BATCH + 1
        out = SR / f"audit_in_R{n:02d}.json"
        out.write_text(json.dumps({
            "batch": f"R{n:02d}",
            "count": len(chunk),
            "candidates": chunk,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  audit_in_R{n:02d}.json: {len(chunk)} candidates")


if __name__ == "__main__":
    main()
