#!/usr/bin/env python3
"""Find all candidate rows whose photo URL is external (not /images/candidates/)."""
import re
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).parent.parent
src = (ROOT / "js" / "data" / "candidates.js").read_text(encoding="utf-8")

# Per-row regex matching just the first 4 fields:
#   [<ballot>, '<name>', '<occupation>', '<photo-url>'
pat = re.compile(
    r"\[\s*\d+\s*,\s*"
    r"'((?:[^'\\]|\\.)*?)'\s*,\s*"
    r"'(?:[^'\\]|\\.)*?'\s*,\s*"
    r"'(https?://[^']+)'"
)
matches = pat.findall(src)
print(f"External photo URLs: {len(matches)}")

hosts = Counter()
for _, url in matches:
    host = re.match(r"https?://([^/]+)", url).group(1)
    hosts[host] += 1
print("\nBy host:")
for host, n in hosts.most_common():
    print(f"  {n:>4}  {host}")

print("\nSample (first 6):")
for name, url in matches[:6]:
    print(f"  {name[:35]:<37} {url[:80]}")
