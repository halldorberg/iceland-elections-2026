"""Phase 3: merge per-batch agent outputs into the master audit_results.json
so the scan-review page renders them. Idempotent — can be run after every
agent completes.

Per-batch output schema (what agents write):
{
  "batch": 1,
  "results": [
    {
      "id": "RVK.X.5",
      "statements": [
        {"n": 1, "status": "verified|flagged|unreachable",
         "claim": "...", "quotes": ["..."],
         "notes": "...", "rewrite": null}
      ],
      "bio": "<original bio text>",
      "sources": ["url1", "url2"],
      "summary": "N verified, N flagged, N unreachable",
      "rescue": {
        "rewrite": "<rewritten bio>",
        "rewrite_words": 95,
        "new_sources": ["url"],
        "resolutions": [{"kind": "rescued|dropped|contradicted", "text": "..."}],
        "new_heimild": [{"url": "...", "label": "..."}]   // optional, replaces sources
      }
    }
  ]
}
"""
from __future__ import annotations
import glob, json, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
MASTER = ROOT / "scan_results" / "audit_results.json"
BATCH_GLOB = "scan_results/audit_results_*.json"


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    master: dict = {}
    if MASTER.exists():
        try:
            master = json.loads(MASTER.read_text(encoding="utf-8"))
        except Exception:
            master = {}

    merged_total = 0
    files_seen = 0
    for f in sorted(ROOT.glob(BATCH_GLOB)):
        if f.name == MASTER.name:
            continue
        files_seen += 1
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  ⚠ {f.name}: {e}")
            continue
        for r in data.get("results", []):
            cid = r.get("id")
            if not cid:
                continue
            entry = {
                "bio": r.get("bio"),
                "sources": r.get("sources", []),
                "statements": r.get("statements", []),
                "summary": r.get("summary"),
                "stats": {
                    "verified":    sum(1 for s in r.get("statements", []) if s.get("status") in ("verified", "rescued")),
                    "flagged":     sum(1 for s in r.get("statements", []) if s.get("status") == "flagged"),
                    "unreachable": sum(1 for s in r.get("statements", []) if s.get("status") == "unreachable"),
                },
            }
            rescue = r.get("rescue")
            if rescue:
                entry["rescue"] = rescue
            # Preserve applied flag if already set
            if cid in master and master[cid].get("applied"):
                entry["applied"] = True
            master[cid] = entry
            merged_total += 1

    MASTER.write_text(json.dumps(master, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Read {files_seen} batch file(s); merged {merged_total} entries into {MASTER.name}")
    print(f"  Total in master: {len(master)} candidates")


if __name__ == "__main__":
    main()
