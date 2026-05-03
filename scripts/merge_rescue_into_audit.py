"""Parse reports/audit_rescue.md and merge per-candidate rewrites into
scan_results/audit_results.json so the scan-review page can render them
inline next to the original audit panel."""
from __future__ import annotations
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
RESCUE_MD = ROOT / "reports" / "audit_rescue.md"
AUDIT_JSON = ROOT / "scan_results" / "audit_results.json"


def parse_rescue(md: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    sections = re.split(r"^## ", md, flags=re.MULTILINE)[1:]
    for sec in sections:
        first = sec.split("\n", 1)[0]
        m = re.match(r"([A-Z]+\.[A-Z0-9]+\.\d+)\s*[—-]\s*(.+)$", first)
        if not m:
            continue
        cid = m.group(1).strip()

        # Proposed rewrite block — captures the blockquote after "Proposed rewrite"
        rw_m = re.search(
            r"\*\*Proposed rewrite[^*]*\*\*\s*\n>\s*(.+?)(?=\n\n|\Z)",
            sec, re.DOTALL
        )
        rewrite = rw_m.group(1).strip() if rw_m else None

        # Word count from the heading "(N words, M sentences)"
        wc_m = re.search(r"\((\d+)\s*words?", sec)
        words = int(wc_m.group(1)) if wc_m else None

        # New sources used during rescue
        new_sources = []
        ns_m = re.search(r"\*\*New sources fetched[^*]*\*\*\s*\n((?:- .*\n?)+)", sec)
        if ns_m:
            for line in ns_m.group(1).splitlines():
                line = line.strip().lstrip("- ").strip()
                if line:
                    new_sources.append(line)

        # Resolutions block — short summary of what was rescued/dropped
        resolutions = []
        res_m = re.search(
            r"\*\*Original flagged claims[^*]*\*\*\s*\n((?:- .*\n?)+)",
            sec
        )
        if res_m:
            for line in res_m.group(1).splitlines():
                line = line.strip().lstrip("- ").strip()
                if not line:
                    continue
                # Classify by leading symbol after the original-claim part
                if "✅ **rescued**" in line or "✅ rescued" in line:
                    kind = "rescued"
                elif "**dropped**" in line or " dropped" in line:
                    kind = "dropped"
                elif "**contradicted" in line or "contradicted by source" in line:
                    kind = "contradicted"
                else:
                    kind = "other"
                resolutions.append({"kind": kind, "text": line})

        out[cid] = {
            "rewrite": rewrite,
            "rewrite_words": words,
            "new_sources": new_sources,
            "resolutions": resolutions,
        }
    return out


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    rescue = parse_rescue(RESCUE_MD.read_text(encoding="utf-8"))
    audit = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))

    merged = 0
    for cid, r in rescue.items():
        if cid in audit:
            audit[cid]["rescue"] = r
            merged += 1
            wc = r.get("rewrite_words", "?")
            print(f"  {cid}: rewrite={wc} words, {len(r['new_sources'])} new sources")
        else:
            print(f"  ⚠️ {cid} in rescue but not in audit")

    AUDIT_JSON.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[OK] Merged {merged} rescue rewrites into {AUDIT_JSON}")


if __name__ == "__main__":
    main()
