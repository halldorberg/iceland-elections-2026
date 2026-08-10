"""Append a candidate result to audit_results_15.json."""
import json
import sys

OUT = r"F:\Claude Projects\iceland-elections\scan_results\audit_results_15.json"

def main():
    payload_path = sys.argv[1]
    with open(payload_path, 'r', encoding='utf-8') as f:
        payload = json.load(f)
    with open(OUT, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Replace if same id present
    data["results"] = [r for r in data["results"] if r["id"] != payload["id"]]
    data["results"].append(payload)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Appended {payload['id']}; total={len(data['results'])}")

if __name__ == "__main__":
    main()
