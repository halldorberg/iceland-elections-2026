"""Regenerate candidates.en.js and candidates.pl.js from strings_en/pl.json."""
import json
from pathlib import Path

ROOT       = Path(r'F:\Claude Projects\iceland-elections')
STRINGS_EN = ROOT / 'translations' / 'strings_en.json'
STRINGS_PL = ROOT / 'translations' / 'strings_pl.json'
OVERLAY_EN = ROOT / 'js' / 'data' / 'candidates.en.js'
OVERLAY_PL = ROOT / 'js' / 'data' / 'candidates.pl.js'

def load_json(p):
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception as e:
        print(f'  WARNING: could not load {p}: {e}')
        return {}

def write_overlay(data, lang, path):
    lang_upper = lang.upper()
    lines = [
        '// AUTO-GENERATED — do not edit manually.',
        '// Source: translations/strings_is.json',
        '// Regenerate: python scripts/i18n_translate_bulk.py',
        '',
        f'export const TRANSLATIONS_{lang_upper} = {{',
    ]
    occ  = data.get('_occupations', {})
    main = {k: v for k, v in data.items() if k != '_occupations' and isinstance(v, str)}
    for key in sorted(main):
        val = main[key].replace('\\', '\\\\').replace('"', '\\"')
        lines.append(f'  "{key}": "{val}",')
    lines.append('')
    lines.append('  // Occupation lookup (deduplicated)')
    lines.append('  "_occupations": {')
    for occ_is, occ_tr in sorted(occ.items()):
        k = occ_is.replace('\\', '\\\\').replace('"', '\\"')
        v = (occ_tr or occ_is).replace('\\', '\\\\').replace('"', '\\"')
        lines.append(f'    "{k}": "{v}",')
    lines.append('  },')
    lines.append('};')
    lines.append('')
    path.write_text('\n'.join(lines), encoding='utf-8')
    print(f'  Written {len(main)} main + {len(occ)} occupations -> {path.name}')

if __name__ == '__main__':
    en = load_json(STRINGS_EN)
    pl = load_json(STRINGS_PL)
    print(f'EN: {len(en)} keys ({len(en.get("_occupations", {}))} occupations)')
    print(f'PL: {len(pl)} keys ({len(pl.get("_occupations", {}))} occupations)')
    write_overlay(en, 'en', OVERLAY_EN)
    write_overlay(pl, 'pl', OVERLAY_PL)
    print('Done.')
