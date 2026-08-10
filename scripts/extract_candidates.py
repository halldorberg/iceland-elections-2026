"""
extract_candidates.py
Parses candidates.js and outputs a summary of all municipality/party lists.
Fixed parser: end-of-list detection uses exact 4-space indentation match.
"""
import re
import json
import os

CANDIDATES_JS = os.path.join(os.path.dirname(__file__), '..', 'js', 'data', 'candidates.js')

# Matches:  [1, 'Name', 'Occupation', ...
CANDIDATE_RE = re.compile(r'^\s{6,8}\[(\d+),\s*[\'"]([^\'"]+)[\'"]')

# Matches party block start:  X: {  or  'X': {
PARTY_RE = re.compile(r"^\s{2}(?:'([A-Z0-9._-]+)'|([A-Z0-9._-]+)):\s*\{")

# Matches municipality const declaration: const MOS = {  or  const RVK_A = {
MUNI_RE = re.compile(r'^const\s+([A-Z][A-Z0-9_]*)\s*=\s*\{')

# Exactly 4 spaces before ], or ] — end of list array
ENDLIST_RE = re.compile(r'^    \],?\s*$')

# list: [ marker
LIST_START_RE = re.compile(r'^\s+list:\s*\[')

def parse():
    result = {}  # { muni_const: { party_code: [names] } }

    with open(CANDIDATES_JS, encoding='utf-8') as f:
        lines = f.readlines()

    current_muni = None
    current_party = None
    in_list = False
    depth = 0  # bracket depth inside the list array

    for i, line in enumerate(lines):
        stripped = line.rstrip('\n')

        # Detect municipality const
        m = MUNI_RE.match(stripped)
        if m:
            current_muni = m.group(1)
            current_party = None
            in_list = False
            if current_muni not in result:
                result[current_muni] = {}
            continue

        if current_muni is None:
            continue

        # Detect party block start (2-space indented)
        m = PARTY_RE.match(stripped)
        if m:
            current_party = m.group(1) or m.group(2)
            in_list = False
            if current_party not in result[current_muni]:
                result[current_muni][current_party] = []
            continue

        if current_party is None:
            continue

        # Detect list: [ start
        if not in_list and LIST_START_RE.match(stripped):
            in_list = True
            depth = 1
            continue

        if not in_list:
            continue

        # Track bracket depth to know when list ends
        # End-of-list: exactly 4 spaces + ], or ] (closing the list array)
        if ENDLIST_RE.match(stripped):
            in_list = False
            current_party = None
            continue

        # Extract candidate name
        m = CANDIDATE_RE.match(stripped)
        if m:
            ballot = int(m.group(1))
            name = m.group(2)
            result[current_muni][current_party].append((ballot, name))

    return result

def main():
    data = parse()

    # Save as JSON
    out = {}
    for muni, parties in data.items():
        out[muni] = {}
        for party, candidates in parties.items():
            out[muni][party] = [{"ballot": b, "name": n} for b, n in sorted(candidates)]

    out_path = os.path.join(os.path.dirname(__file__), '..', 'scan_results', 'current_candidates.json')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    # Print summary to file (avoids Windows console encoding issues)
    summary_path = os.path.join(os.path.dirname(__file__), '..', 'scan_results', 'current_candidates_summary.txt')
    with open(summary_path, 'w', encoding='utf-8') as f:
        total_munis = len(data)
        total_parties = sum(len(p) for p in data.values())
        total_candidates = sum(len(c) for p in data.values() for c in p.values())
        f.write(f"Municipalities: {total_munis}\n")
        f.write(f"Party lists: {total_parties}\n")
        f.write(f"Candidates: {total_candidates}\n\n")
        for muni in sorted(data.keys()):
            parties = data[muni]
            muni_total = sum(len(c) for c in parties.values())
            f.write(f"\n=== {muni} ({muni_total} candidates, {len(parties)} lists) ===\n")
            for party in sorted(parties.keys()):
                candidates = parties[party]
                f.write(f"  {party}: {len(candidates)} candidates\n")
                for ballot, name in sorted(candidates):
                    f.write(f"    {ballot}. {name}\n")

    print(f"Done. Municipalities: {total_munis}, Lists: {total_parties}, Candidates: {total_candidates}")
    print(f"Saved JSON to {out_path}")
    print(f"Saved summary to {summary_path}")

if __name__ == '__main__':
    main()
