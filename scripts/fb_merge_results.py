#!/usr/bin/env python3
"""
Merge probe results into fb_pages_2026-05-01.json (additive).
Reads:
  scan_results/_fb_probe_batch3_out.json  (the probe output)
  scan_worklist_policy_FB_2026-05-01.json (worklist with party metadata)
  scan_results/fb_pages_2026-05-01.json   (existing log)

Adds entries for ids not yet present in fb_pages, with platform_extracted=False.
"""
import json
import sys
import re

HERE = "F:/Claude Projects/iceland-elections"


def load(path):
    return json.load(open(path, encoding="utf-8"))


def main():
    probe = load(f"{HERE}/scan_results/_fb_probe_batch3_out.json")
    worklist = load(f"{HERE}/scan_worklist_policy_FB_2026-05-01.json")["missing_policy"]
    fb_log = load(f"{HERE}/scan_results/fb_pages_2026-05-01.json")
    have = set()
    for r in fb_log["results"]:
        have.add((r["muni_slug"], r["party_code"]))

    # build worklist index by id
    by_id = {}
    for w in worklist:
        # collisions on id (e.g. RAN.D appears twice for two munis); keep all
        by_id.setdefault(w["id"], []).append(w)

    # special id mappings: HUN.B/HUN.D appear twice (hunabyggd & hunathing).
    # The probe input uses HUN.B / HUN.D / HUN.B.HVE / HUN.D.HVE etc.
    # We've defined HUN.B.HVE → hunathing in our probe input so be careful.
    extra_id_map = {
        "HUN.B.HVE": ("hunathing", "B"),
        "HUN.D.HVE": ("hunathing", "D"),
        "SKA.S.SST": ("skagastrond", "B"),  # Framsókn í Skagaströnd
        "SKA.S.SS":  ("skagastrond", "S"),  # Samfylkingin í Skagaströnd
    }

    new_entries = []
    for p in probe:
        eid = p["id"]
        if eid in extra_id_map:
            muni_slug, party_code = extra_id_map[eid]
            party_label = next(
                (w["party_label"] for w in worklist
                 if w["muni_slug"] == muni_slug and w["party_code"] == party_code),
                ""
            )
        else:
            ws = by_id.get(eid, [])
            if not ws:
                continue
            # if multiple rows, pick first; we only have one probe row per id
            w = ws[0]
            muni_slug = w["muni_slug"]
            party_code = w["party_code"]
            party_label = w["party_label"]
        if (muni_slug, party_code) in have:
            continue
        found = p.get("found")
        slugs_tried = [t.get("slug") for t in p.get("tries", [])]
        if found:
            entry = {
                "muni_slug": muni_slug,
                "party_code": party_code,
                "party_label": party_label,
                "fb_url": f"https://www.facebook.com/{found['slug']}",
                "fb_page_name": found.get("pageName"),
                "platform_extracted": False,
                "external_links_seen": [],
                "note": f"Found via direct slug probe ({found['slug']}). Page sample: {(found.get('sample') or '')[:240]}"
            }
        else:
            entry = {
                "muni_slug": muni_slug,
                "party_code": party_code,
                "party_label": party_label,
                "fb_url": None,
                "fb_page_name": None,
                "platform_extracted": False,
                "external_links_seen": [],
                "note": f"No FB page found via direct slug probe. Slugs tried: {', '.join(slugs_tried)}"
            }
        new_entries.append(entry)
        have.add((muni_slug, party_code))

    fb_log["results"].extend(new_entries)
    with open(f"{HERE}/scan_results/fb_pages_2026-05-01.json", "w", encoding="utf-8") as f:
        json.dump(fb_log, f, ensure_ascii=False, indent=2)
    print(f"Added {len(new_entries)} entries; total now {len(fb_log['results'])}")


if __name__ == "__main__":
    main()
