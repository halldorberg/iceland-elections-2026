"""
prep_bio_scan.py
────────────────
Builds scan_results/bios_to_research.json — a priority-ordered list of
candidates who have a photo but no/minimal bio. Used as the work-list for
research agents.

Sort key: muni population (desc), party_size_in_muni (desc), ballot (asc).

Usage:
    python scripts/prep_bio_scan.py
    python scripts/prep_bio_scan.py --top 100   # write only top N for next batch
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
OUT = ROOT / "scan_results" / "bios_to_research.json"

# 2024 Statistics Iceland populations (rough; only used for ordering).
MUNI_POP = {
    "reykjavik": 139875, "kopavogur": 40580, "hafnarfjordur": 32196,
    "reykjanesbaer": 22560, "akureyri": 20250, "gardabaer": 19003,
    "mosfellsbaer": 13917, "arborg": 11693, "akranes": 8419,
    "mulathing": 5221, "fjardabyggd": 5178, "vestmannaeyjar": 4617,
    "borgarbyggd": 4067, "isafjordur": 3853, "hveragerdi": 3279,
    "skagafjordur": 4242, "hornafjordur": 2510, "olfus": 2540,
    "rangarthingytra": 1801, "rangarthingeystra": 1819,
    "snaefellsbaer": 1750, "vogar": 1623, "nordurping": 3232,
    "dalvikurbyggd": 2017, "stykkisholmur": 1226, "fjallabyggd": 2014,
    "seltjarnarnes": 4757, "grindavik": 3614, "hvalfjardarsveit": 715,
    "bolungarvik": 904, "vesturbyggd": 1107, "blaskogabyggd": 1226,
    "skagastrond": 522, "thingeyjarsveit": 1042, "horgarsv": 690,
    "eyjafjardarsveit": 1126, "kjosarhreppur": 285, "myrdalshr": 933,
    "skaftarhreppur": 480, "hunabyggd": 985, "hunathing": 1248,
    "grundarfjordur": 853, "hrunamannahreppur": 916, "floahreppur": 776,
    "grimsnesgrafningur": 720, "skeidagnup": 631, "sudurnesjabaer": 4031,
    "strandabyggd": 463, "svalbardsstrond": 478, "reykholar": 268,
    "tjornes": 162, "vopnafjordur": 660, "arneshr": 51, "sudavik": 200,
}

# Reuse the parser
sys.path.insert(0, str(Path(__file__).parent))
from report_photo_no_bio import (  # noqa: E402
    CANDIDATES_JS, parse_real_data_map, find_const_blocks,
    parse_party_blocks, find_list_array, split_list_rows, parse_candidate_row,
    is_minimal_bio,
)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=0, help="If >0, also write a `_top<N>.json` slice")
    ap.add_argument("--max-len", type=int, default=220)
    args = ap.parse_args()

    src = CANDIDATES_JS.read_text(encoding="utf-8")
    const_to_slug = parse_real_data_map(src)
    const_blocks = find_const_blocks(src, set(const_to_slug.keys()))

    # Count party sizes per muni so we can rank parties
    party_sizes: dict[tuple[str, str], int] = {}
    candidates: list[dict] = []

    for const, (bs, be) in const_blocks.items():
        muni_slug = const_to_slug[const]
        for party_code, pbs, pbe in parse_party_blocks(src, bs, be):
            larr = find_list_array(src, pbs, pbe)
            if not larr:
                continue
            ls, le = larr
            rows = split_list_rows(src, ls, le)
            party_sizes[(muni_slug, party_code)] = len(rows)
            for rs, re_ in rows:
                row = parse_candidate_row(src, rs, re_)
                if not row:
                    continue
                if not row["has_photo"]:
                    continue
                bio = row["bio"]
                if bio is None or not bio.strip():
                    kind = "no_bio"
                elif is_minimal_bio(row["name"], row["occupation"], bio, args.max_len):
                    kind = "minimal"
                else:
                    continue
                candidates.append({
                    "id": f"{const}.{party_code}.{row['ballot']}",
                    "muni_slug": muni_slug,
                    "party_code": party_code,
                    "ballot": row["ballot"],
                    "name": row["name"],
                    "occupation": row["occupation"],
                    "kind": kind,
                    "current_bio": bio,
                })

    # Tiered priority: top-3 of every muni come first (sorted by muni population),
    # then top-5, then top-10, then top-15, then the rest. Within each tier, sort
    # by muni population (desc) → party size (desc) → ballot (asc).
    def ballot_tier(b: int) -> int:
        if b <= 3:  return 0  # leadership tier
        if b <= 5:  return 1
        if b <= 10: return 2
        if b <= 15: return 3
        return 4

    def sort_key(c):
        pop = MUNI_POP.get(c["muni_slug"], 0)
        psize = party_sizes.get((c["muni_slug"], c["party_code"]), 0)
        return (ballot_tier(c["ballot"]), -pop, -psize, c["ballot"], c["muni_slug"], c["party_code"])

    # Skip candidates already processed in any scan_results/bios_2026-*.json
    import glob
    already_processed: set[str] = set()
    for fn in glob.glob(str(ROOT / "scan_results" / "bios_2026-*.json")):
        if "to_research" in fn:
            continue
        try:
            data = json.loads(Path(fn).read_text(encoding="utf-8"))
        except Exception:
            continue
        for r in data.get("results", []) or []:
            if r.get("id"):
                already_processed.add(r["id"])
    if already_processed:
        before = len(candidates)
        candidates = [c for c in candidates if c["id"] not in already_processed]
        print(f"[INFO] Excluded {before - len(candidates)} already-processed candidates")

    candidates.sort(key=sort_key)

    # Add a numeric `priority` field for clarity
    for i, c in enumerate(candidates, 1):
        c["priority"] = i

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "total": len(candidates),
        "candidates": candidates,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Wrote {OUT}  ({len(candidates)} candidates)")

    if args.top > 0:
        top_path = OUT.parent / f"bios_to_research_top{args.top}.json"
        top_path.write_text(json.dumps({
            "total": min(args.top, len(candidates)),
            "candidates": candidates[:args.top],
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[OK] Wrote {top_path}")

    # Print top-25 preview
    print("\nTop 25 (highest priority):")
    for c in candidates[:25]:
        marker = "🚫" if c["kind"] == "no_bio" else "✏️"
        print(f"  {c['priority']:3d} {marker} {c['muni_slug']:20s} {c['party_code']:5s} #{c['ballot']:2d}  {c['name']}")


if __name__ == "__main__":
    main()
