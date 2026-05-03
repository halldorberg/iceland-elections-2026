"""Parse reports/audit_pilot.md (or any audit_*.md) into a JSON dict keyed by
candidate id, for embedding into scan-review.html via generate_review.py."""
from __future__ import annotations
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
DEFAULT_INPUT = ROOT / "reports" / "audit_pilot.md"
DEFAULT_OUTPUT = ROOT / "scan_results" / "audit_results.json"


def parse_audit(md_text: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    # Split on '## ' candidate headings
    sections = re.split(r"^## ", md_text, flags=re.MULTILINE)[1:]
    for sec in sections:
        # Heading line: "RVK.M.2 — Kristín Kolbrún Kolbeinsdóttir"
        first_line = sec.split("\n", 1)[0]
        m = re.match(r"([A-Z]+\.[A-Z0-9]+\.\d+)\s*[—-]\s*(.+)$", first_line)
        if not m:
            continue
        cid = m.group(1).strip()
        body = sec[len(first_line):]

        # Extract bio block
        bio_m = re.search(r"\*\*Bio \(current\):\*\*\s*\n>\s*(.+?)(?=\n\n)", body, re.DOTALL)
        bio_text = bio_m.group(1).strip() if bio_m else None

        # Extract sources block
        sources = []
        src_m = re.search(r"\*\*Sources fetched:\*\*\s*\n(.*?)(?=\n\n)", body, re.DOTALL)
        if src_m:
            for line in src_m.group(1).splitlines():
                line = line.strip().lstrip("- ").strip()
                if line:
                    sources.append(line)

        # Extract statement-by-statement entries
        statements = []
        stmt_block_m = re.search(r"\*\*Statement-by-statement:\*\*(.*?)(?=\*\*Summary:\*\*|^---)", body, re.DOTALL | re.MULTILINE)
        if stmt_block_m:
            stmt_block = stmt_block_m.group(1)
            # Each stmt starts with "N. ✅" or "N. 🚩FLAG-UNSOURCED" or "N. ⚠️"
            entries = re.split(r"\n(?=\d+\.\s+[✅🚩⚠])", stmt_block)
            for ent in entries:
                ent = ent.strip()
                if not ent:
                    continue
                # First line: "N. SYMBOL **claim text**"
                head_m = re.match(r"(\d+)\.\s+(✅|🚩FLAG-UNSOURCED|⚠️)\s+\*\*(.+?)\*\*\s*\n?(.*)", ent, re.DOTALL)
                if not head_m:
                    continue
                num = int(head_m.group(1))
                symbol = head_m.group(2)
                if symbol == "✅":
                    status = "verified"
                elif symbol.startswith("🚩"):
                    status = "flagged"
                else:
                    status = "unreachable"
                claim = head_m.group(3).strip()
                rest = head_m.group(4).strip()

                # Extract the source quote(s) — lines starting with `> `
                quotes = re.findall(r"^>\s*(.+)$", rest, re.MULTILINE)
                # Extract proposed rewrite if present
                rewrite_m = re.search(r"\*\*Proposed rewrite:\*\*\s*(.+?)(?=\n\n|\Z)", rest, re.DOTALL)
                rewrite = rewrite_m.group(1).strip() if rewrite_m else None

                # Notes = the prose between (excluding quotes and rewrite line)
                notes = re.sub(r"^>\s.+$", "", rest, flags=re.MULTILINE)
                notes = re.sub(r"\*\*Proposed rewrite:\*\*.*", "", notes, flags=re.DOTALL).strip()

                statements.append({
                    "n": num,
                    "status": status,
                    "claim": claim,
                    "quotes": quotes,
                    "notes": notes if notes else None,
                    "rewrite": rewrite,
                })

        # Summary line
        summ_m = re.search(r"\*\*Summary:\*\*\s+(.+?)(?=\n|$)", body)
        summary = summ_m.group(1).strip() if summ_m else None

        out[cid] = {
            "bio": bio_text,
            "sources": sources,
            "statements": statements,
            "summary": summary,
            "stats": {
                "verified":   sum(1 for s in statements if s["status"] == "verified"),
                "flagged":    sum(1 for s in statements if s["status"] == "flagged"),
                "unreachable":sum(1 for s in statements if s["status"] == "unreachable"),
            },
        }
    return out


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    inp = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT
    md = inp.read_text(encoding="utf-8")
    data = parse_audit(md)
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Wrote {out_path} — {len(data)} candidates parsed")
    for cid, c in data.items():
        s = c["stats"]
        print(f"  {cid}: {s['verified']}✅ {s['flagged']}🚩 {s['unreachable']}⚠️")


if __name__ == "__main__":
    main()
