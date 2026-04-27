"""
i18n_track_changes.py
─────────────────────
Detects strings that changed in candidates.js since the last extraction
snapshot, and appends them to translations/pending.json.

Run automatically as a git post-commit hook, or manually after editing
candidates.js.

Usage:
  python scripts/i18n_track_changes.py

Install as git hook:
  echo "python scripts/i18n_track_changes.py" > .git/hooks/post-commit
  chmod +x .git/hooks/post-commit  (Linux/Mac only)
"""

import json, os, subprocess
from datetime import date
from pathlib import Path

ROOT       = Path(__file__).parent.parent
STRINGS_IS = ROOT / 'translations' / 'strings_is.json'
PENDING    = ROOT / 'translations' / 'pending.json'

sys_path_append = str(ROOT / 'scripts')
import sys; sys.path.insert(0, sys_path_append)
from i18n_extract import extract


def load_json(path):
    if path.exists():
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    candidates_js = ROOT / 'js' / 'data' / 'candidates.js'
    with open(candidates_js, encoding='utf-8') as f:
        content = f.read()

    # Re-extract current state
    current_strings, current_occs = extract(content)

    # Compare against last snapshot
    snapshot = load_json(STRINGS_IS)
    snapshot_main = {k: v for k, v in snapshot.items() if k != '_occupations'}
    snapshot_occs = snapshot.get('_occupations', {})

    changed = {}

    # Main strings: new or changed values
    for key, val in current_strings.items():
        if snapshot_main.get(key) != val:
            changed[key] = val

    # Occupations: new ones
    for occ in current_occs:
        if occ not in snapshot_occs:
            changed[f'_occ:{occ}'] = occ

    if not changed:
        print("i18n: no translatable changes detected.")
        return

    # Append to pending.json
    pending = load_json(PENDING)
    today   = str(date.today())
    if today not in pending:
        pending[today] = []

    for key, val in changed.items():
        # Avoid duplicates
        if not any(e['key'] == key for e in pending[today]):
            pending[today].append({'key': key, 'is': val, 'en': None, 'pl': None})

    save_json(PENDING, pending)

    # Update the snapshot
    current_strings['_occupations'] = {k: None for k in current_occs}
    save_json(STRINGS_IS, current_strings)

    print(f"i18n: {len(changed)} new/changed strings added to translations/pending.json")


if __name__ == '__main__':
    main()
