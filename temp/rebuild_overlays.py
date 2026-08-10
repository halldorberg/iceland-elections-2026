"""Rebuild EN/PL overlays from translations/strings_*.json with proper escaping."""
import json
import sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r'F:\Claude Projects\iceland-elections')


def esc(s):
    return (s.replace('\\', '\\\\')
             .replace('"', '\\"')
             .replace('\r', '\\r')
             .replace('\n', '\\n'))


def rebuild(lang):
    strings_path = ROOT / 'translations' / f'strings_{lang}.json'
    overlay_path = ROOT / 'js' / 'data' / f'candidates.{lang}.js'
    strings = json.load(open(strings_path, encoding='utf-8'))
    occ = strings.get('_occupations', {})
    main = {k: v for k, v in strings.items()
            if k != '_occupations' and isinstance(v, str)}
    lines = [
        '// AUTO-GENERATED — do not edit manually.',
        '// Source: translations/strings_is.json',
        '// Regenerate: python scripts/i18n_translate_bulk.py',
        '',
        f'export const TRANSLATIONS_{lang.upper()} = {{',
    ]
    for key in sorted(main):
        lines.append(f'  "{key}": "{esc(main[key] or "")}",')
    lines.append('')
    lines.append('  // Occupation lookup (deduplicated)')
    lines.append('  "_occupations": {')
    for occ_is, occ_tr in sorted(occ.items()):
        lines.append(f'    "{esc(occ_is)}": "{esc(occ_tr or occ_is)}",')
    lines.append('  },')
    lines.append('};')
    lines.append('')
    overlay_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f'Wrote {overlay_path}')


rebuild('en')
rebuild('pl')
