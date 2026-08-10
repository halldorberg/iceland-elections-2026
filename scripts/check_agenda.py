#!/usr/bin/env python3
"""Diagnostic: list parties with no agenda items vs no platformUrl."""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
src = (ROOT / "js" / "data" / "candidates.js").read_text(encoding="utf-8")

muni_to_slug = {}
m = re.search(r"const REAL_DATA\s*=\s*\{(.*?)\};", src, re.DOTALL)
if m:
    for mm in re.finditer(r"(\w+)\s*:\s*([A-Z_]+)\s*,", m.group(1)):
        muni_to_slug[mm.group(2)] = mm.group(1)

lines = src.splitlines()
cur_const = None
cur_party = None
cur_state = None
parties_data = []
in_agenda = False

for line in lines:
    s = line.strip()
    cm = re.match(r"^const ([A-Z][A-Z0-9_]+)\s*=\s*\{", line)
    if cm:
        if cur_party and cur_const in muni_to_slug:
            parties_data.append((
                muni_to_slug[cur_const],
                cur_party,
                cur_state["agenda_items"] > 0,
                cur_state["platformUrl"],
                cur_state["tagline"],
            ))
            cur_party = None
        cur_const = cm.group(1) if cm.group(1) in muni_to_slug else None
        continue
    if cur_const is None:
        continue
    pm = re.match(r"^  ([A-Z][A-Z0-9]{0,3})\s*:\s*\{", line)
    if pm:
        if cur_party:
            parties_data.append((
                muni_to_slug[cur_const],
                cur_party,
                cur_state["agenda_items"] > 0,
                cur_state["platformUrl"],
                cur_state["tagline"],
            ))
        cur_party = pm.group(1)
        cur_state = {"agenda_items": 0, "platformUrl": False, "tagline": ""}
        in_agenda = False
        continue
    if cur_party:
        if re.search(r"platformUrl\s*:\s*'", line):
            cur_state["platformUrl"] = True
        tm = re.search(r"tagline\s*:\s*'((?:[^'\\]|\\.)*)'", line)
        if tm:
            cur_state["tagline"] = tm.group(1)
        if re.search(r"agenda\s*:\s*\[", line):
            in_agenda = True
            continue
        if in_agenda:
            if re.match(r"^\s*\{\s*icon\s*:", line):
                cur_state["agenda_items"] += 1
            if re.match(r"^    \],", line) or re.match(r"^    \]\s*$", line):
                in_agenda = False

if cur_party and cur_const in muni_to_slug:
    parties_data.append((
        muni_to_slug[cur_const],
        cur_party,
        cur_state["agenda_items"] > 0,
        cur_state["platformUrl"],
        cur_state["tagline"],
    ))

print(f"Total parties: {len(parties_data)}")
no_agenda = [p for p in parties_data if not p[2]]
no_url = [p for p in parties_data if not p[3]]
no_either = [p for p in parties_data if not p[2] or not p[3]]
print(f"No agenda: {len(no_agenda)}")
print(f"No platformUrl: {len(no_url)}")
print(f"No agenda OR no platformUrl: {len(no_either)}")
print()
print("Parties with NO agenda:")
for muni, code, _, url, tag in no_agenda[:40]:
    print(f"  {muni:20s} {code:5s} (url={url}) tag={tag[:60]}")
