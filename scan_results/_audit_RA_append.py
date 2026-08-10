"""Append/replace results in audit_results_RA*.json from a payload JSON file."""
import json, sys
from pathlib import Path

def main(out_path, payload_path):
    with open(payload_path, 'r', encoding='utf-8') as f:
        new_results = json.load(f)  # list of result dicts
    with open(out_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    existing = {r['id']: r for r in data['results']}
    for r in new_results:
        existing[r['id']] = r
    data['results'] = list(existing.values())
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Now {len(data['results'])} results in {Path(out_path).name}")

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
