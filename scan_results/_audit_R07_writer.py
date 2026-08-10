"""Append/update an entry to audit_results_R07.json."""
import json, os, sys

RESULT_PATH = r"F:\Claude Projects\iceland-elections\scan_results\audit_results_R07.json"

def save(entry):
    if os.path.exists(RESULT_PATH):
        with open(RESULT_PATH, encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"batch": "R07", "results": []}
    data["results"] = [r for r in data["results"] if r.get("id") != entry["id"]]
    data["results"].append(entry)
    with open(RESULT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"saved {entry['id']} (total={len(data['results'])})")

if __name__ == "__main__":
    fp = sys.argv[1]
    with open(fp, encoding="utf-8") as f:
        payload = json.load(f)
    save(payload)
