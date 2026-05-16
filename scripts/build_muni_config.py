#!/usr/bin/env python3
"""Build data/muni_config.json — the canonical per-municipality config used by
the election-night tooling (publish_live_results.py and the results backend).

Source of truth:
  - js/data/municipalities.js  → id, name, region, partyIds (2026 ballot lists)
  - js/data/results2022.js     → totalSeats (council size; stable 2022→2026)

Two munis are absent from results2022.js (no 2022 party-list election there):
their council size is hard-coded here and flagged `seatsUnverified` so we
double-check before election night.

Output schema (data/muni_config.json):
{
  "generatedAt": "2026-05-16T...Z",
  "munis": {
    "reykjavik": {
      "name": "Reykjavík",
      "region": "Höfuðborgarsvæðið",
      "totalSeats": 23,
      "partyIds": ["D","B","S","A","P","M","F","C","J","G","R"],
      "seatsUnverified": false
    },
    ...
  }
}

Re-run any time municipalities.js or results2022.js changes:
    python scripts/build_muni_config.py
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

for _s in (sys.stdout, sys.stderr):  # Windows cp1252 chokes on ⚠
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent.parent
MUNI_JS = ROOT / "js" / "data" / "municipalities.js"
R22_JS = ROOT / "js" / "data" / "results2022.js"
OUT = ROOT / "data" / "muni_config.json"

# Council sizes for contested munis missing from results2022.js.
# Flagged seatsUnverified=True so we confirm against kosning.is before the night.
# (langanesbyggd is uncontested in 2026 — no lists — so it's excluded entirely
#  and needs no fallback here.)
FALLBACK_SEATS = {
    "hornafjordur": 7,    # Sveitarfélagið Hornafjörður — bæjarstjórn
}


def parse_municipalities(src: str):
    """Yield (id, name, region, [partyIds]) for every muni block."""
    # Each block: { id: '...', name: '...', region: '...', ... partyIds: [...] }
    pat = re.compile(
        r"\{\s*id:\s*'([^']+)',\s*"
        r"name:\s*'([^']+)',\s*"
        r"region:\s*'([^']+)',"
        r".*?"
        r"partyIds:\s*\[([^\]]*)\]",
        re.S,
    )
    for m in pat.finditer(src):
        mid, name, region, pids = m.groups()
        letters = re.findall(r"'([^']+)'", pids)
        yield mid, name, region, letters


def parse_total_seats(src: str) -> dict[str, int]:
    """id -> totalSeats from results2022.js (handles the sjalkjorinn: true prefix)."""
    out: dict[str, int] = {}
    pat = re.compile(
        r"(\w[\w-]*):\s*\{\s*(?:sjalkjorinn:\s*true,\s*)?totalSeats:\s*(\d+)"
    )
    for m in pat.finditer(src):
        out[m.group(1)] = int(m.group(2))
    return out


def main() -> None:
    muni_src = MUNI_JS.read_text(encoding="utf-8")
    r22_src = R22_JS.read_text(encoding="utf-8")

    seats = parse_total_seats(r22_src)
    munis: dict[str, dict] = {}
    missing: list[str] = []

    for mid, name, region, letters in parse_municipalities(muni_src):
        if not letters:
            # No 2026 ballot lists → not part of live-results/coalitions.
            continue
        if mid in seats:
            total, unverified = seats[mid], False
        elif mid in FALLBACK_SEATS:
            total, unverified = FALLBACK_SEATS[mid], True
        else:
            total, unverified = 0, True
            missing.append(mid)
        munis[mid] = {
            "name": name,
            "region": region,
            "totalSeats": total,
            "partyIds": letters,
            "seatsUnverified": unverified,
        }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generatedAt": datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
        "munis": dict(sorted(munis.items())),
    }
    OUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    contested = len(munis)
    unver = [m for m, v in munis.items() if v["seatsUnverified"]]
    print(f"Wrote {OUT.relative_to(ROOT)} — {contested} contested munis.")
    if unver:
        print(f"  seatsUnverified ({len(unver)}): {', '.join(unver)}")
    if missing:
        print(f"  ⚠ NO seat count at all for: {', '.join(missing)} (set to 0)")


if __name__ == "__main__":
    main()
