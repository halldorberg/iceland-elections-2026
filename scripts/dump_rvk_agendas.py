"""Dump all Reykjavík party agendas as plain text for analysis."""
import re, sys, io
from pathlib import Path

ROOT = Path(__file__).parent.parent
src = (ROOT / "js" / "data" / "candidates.js").read_text(encoding="utf-8")

lines = src.splitlines()
rvk_text = "\n".join(lines[6:1457])

parties = ['D','B','S','A','P','M','F','C','G','J','R']
ITEM_RE = re.compile(
    r"icon:\s*'([^']*)'\s*,\s*title:\s*'([^']*)'\s*,\s*text:\s*'((?:[^'\\]|\\.)*)'"
)

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
for code in parties:
    m = re.search(r"^  " + code + r": \{\n([\s\S]*?)^    list:", rvk_text, re.MULTILINE)
    if not m:
        print(f"-- {code} not found --"); continue
    body = m.group(1)
    tagline_m = re.search(r"tagline:\s*'([^']+)'", body)
    plat_m = re.search(r"platformUrl:\s*'([^']+)'", body)
    print(f"\n=== {code} | {tagline_m.group(1) if tagline_m else '(no tagline)'} ===")
    if plat_m:
        print(f"   platform: {plat_m.group(1)}")
    agenda_m = re.search(r"agenda:\s*\[([\s\S]*?)\n    \]", body)
    if not agenda_m:
        print("  (no agenda block)"); continue
    ag = agenda_m.group(1)
    for ic, t, tx in ITEM_RE.findall(ag):
        tx = tx.replace("\\'", "'")
        print(f" {ic} {t}")
        print(f"    {tx[:320]}")
