"""Bump municipality.js and outreach.js version strings to bust Cloudflare cache."""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {'.claude', '.git', 'node_modules', 'scripts', 'reports', 'raw'}

REPLACEMENTS = [
    ('municipality.js?v=91', 'municipality.js?v=92'),
    ('outreach.js?v=1',      'outreach.js?v=2'),
]

count = 0
for dirpath, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in SKIP]
    for fname in files:
        if not fname.endswith('.html'):
            continue
        fpath = os.path.join(dirpath, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
            new = content
            for old, new_val in REPLACEMENTS:
                new = new.replace(old, new_val)
            if new != content:
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(new)
                count += 1
        except Exception:
            pass

print(f'Updated {count} files')
