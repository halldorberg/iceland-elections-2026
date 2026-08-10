"""Append a single candidate result to audit_results_R04.json."""
import json
import sys
import os

OUT = r"F:\Claude Projects\iceland-elections\scan_results\audit_results_R04.json"


def append(result):
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"batch": "R04", "results": []}
    # Replace if same id exists
    rid = result.get("id")
    data["results"] = [r for r in data["results"] if r.get("id") != rid]
    data["results"].append(result)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Appended {rid} (total {len(data['results'])})")


if __name__ == "__main__":
    payload = json.loads(sys.stdin.read())
    append(payload)
