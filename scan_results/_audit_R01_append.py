"""Append a result entry into audit_results_R01.json. Reads JSON from stdin."""
import json
import sys
import os

OUT = r"F:\Claude Projects\iceland-elections\scan_results\audit_results_R01.json"
IN_FILE = sys.argv[1] if len(sys.argv) > 1 else None

with open(OUT, encoding="utf-8") as f:
    data = json.load(f)

if IN_FILE:
    with open(IN_FILE, encoding="utf-8") as f:
        new_entry = json.load(f)
else:
    new_entry = json.load(sys.stdin)

# replace if same id, else append
existing = {r["id"]: i for i, r in enumerate(data["results"])}
if new_entry["id"] in existing:
    data["results"][existing[new_entry["id"]]] = new_entry
else:
    data["results"].append(new_entry)

tmp = OUT + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
os.replace(tmp, OUT)
print(f"OK ({len(data['results'])} results, id={new_entry['id']})")
