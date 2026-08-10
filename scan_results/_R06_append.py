"""Append a candidate result to audit_results_R06.json incrementally."""
import json, sys, os

OUT = r"F:\Claude Projects\iceland-elections\scan_results\audit_results_R06.json"

def append(entry):
    with open(OUT, encoding="utf-8") as f:
        data = json.load(f)
    # de-dup by id
    data["results"] = [r for r in data["results"] if r["id"] != entry["id"]]
    data["results"].append(entry)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Wrote {entry['id']}; total = {len(data['results'])}")

if __name__ == "__main__":
    payload_path = sys.argv[1]
    with open(payload_path, encoding="utf-8") as f:
        entry = json.load(f)
    append(entry)
