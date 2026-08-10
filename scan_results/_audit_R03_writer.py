"""Append a result to audit_results_R03.json incrementally."""
import json
import os
import sys

OUT = r"F:\Claude Projects\iceland-elections\scan_results\audit_results_R03.json"

def add_result(result_path):
    with open(result_path, "r", encoding="utf-8") as f:
        result = json.load(f)
    with open(OUT, "r", encoding="utf-8") as f:
        data = json.load(f)
    # replace if same id else append
    rid = result["id"]
    data["results"] = [r for r in data["results"] if r["id"] != rid]
    data["results"].append(result)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {rid}. Total results: {len(data['results'])}")

if __name__ == "__main__":
    add_result(sys.argv[1])
