"""Phase 1 prep: split the ~554 unaudited written bios into batches of ~25
for the audit-rescue-rewrite agent pipeline. Skipped bios (bio: null) are
excluded from auditing — they have nothing to verify.

Outputs:
  scan_results/audit_in_NN.json   (NN = 01..N)
"""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
BIOS_GLOB = "scan_results/bios_2026-05-02_*.json"
AUDIT_RESULTS = ROOT / "scan_results" / "audit_results.json"
OUT_DIR = ROOT / "scan_results"
BATCH_SIZE = 25


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    # 1. Load current audit_results to know which IDs are already audited
    audited: set[str] = set()
    if AUDIT_RESULTS.exists():
        try:
            audited = set(json.loads(AUDIT_RESULTS.read_text(encoding="utf-8")).keys())
        except Exception:
            pass
    print(f"  Already audited: {len(audited)} (will be skipped)")

    # 2. Collect all written bios (have non-empty bio text)
    candidates: list[dict] = []
    for f in sorted(ROOT.glob(BIOS_GLOB)):
        if "to_research" in f.name or "audit" in f.name:
            continue
        data = json.loads(f.read_text(encoding="utf-8"))
        for r in data.get("results", []):
            cid = r.get("id")
            if not cid or cid in audited:
                continue
            if not r.get("bio"):
                continue  # skipped bios have nothing to audit
            candidates.append({
                "id": cid,
                "name": r.get("name"),
                "muni_slug": r.get("muni_slug"),
                "party_code": r.get("party_code"),
                "ballot": r.get("ballot"),
                "occupation": r.get("occupation"),
                "bio": r["bio"],
                "sources": r.get("sources") or r.get("heimild") or [],
                "age": r.get("age"),
                "interests": r.get("interests"),
                "social": r.get("social"),
            })

    print(f"  Bios to audit: {len(candidates)}")

    # 3. Sort by source count (light first → faster early batches → faster feedback)
    candidates.sort(key=lambda c: (len(c["sources"]), c["id"]))

    # 4. Split into batches
    batches: list[list[dict]] = []
    for i in range(0, len(candidates), BATCH_SIZE):
        batches.append(candidates[i:i + BATCH_SIZE])

    # 5. Write batch files
    for i, batch in enumerate(batches, 1):
        out_file = OUT_DIR / f"audit_in_{i:02d}.json"
        out_file.write_text(json.dumps({
            "batch": i,
            "of": len(batches),
            "count": len(batch),
            "candidates": batch,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  audit_in_{i:02d}.json: {len(batch)} candidates")

    print(f"\n  Total: {len(batches)} batches × {BATCH_SIZE} = up to {len(batches) * BATCH_SIZE} bios")
    print(f"  Actual: {len(candidates)} bios in {len(batches)} files")


if __name__ == "__main__":
    main()
