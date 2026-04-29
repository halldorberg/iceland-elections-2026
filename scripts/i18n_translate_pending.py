"""
i18n_translate_pending.py
──────────────────────────
Translates everything in translations/pending.json, then merges the results
into the EN and PL overlay files and clears the pending list.

Run once a day (or whenever you want) after making edits.

Usage:
  OPENAI_API_KEY=sk-... python scripts/i18n_translate_pending.py

Or:
  python scripts/i18n_translate_pending.py sk-proj-...
"""

import os, sys, json, time
from pathlib import Path
from openai import OpenAI

# Load .env from project root if present
_env = Path(__file__).parent.parent / '.env'
if _env.exists():
    for _line in _env.read_text(encoding='utf-8').splitlines():
        if '=' in _line and not _line.startswith('#'):
            _k, _v = _line.split('=', 1)
            os.environ.setdefault(_k.strip(), _v.strip())

MODEL      = 'gpt-5.4'
BATCH_SIZE = 40

ROOT       = Path(__file__).parent.parent
PENDING    = ROOT / 'translations' / 'pending.json'
STRINGS_EN = ROOT / 'translations' / 'strings_en.json'
STRINGS_PL = ROOT / 'translations' / 'strings_pl.json'
OVERLAY_EN = ROOT / 'js' / 'data' / 'candidates.en.js'
OVERLAY_PL = ROOT / 'js' / 'data' / 'candidates.pl.js'

LANG_NAMES = {'en': 'English', 'pl': 'Polish'}

SYSTEM_PROMPT = """\
You are a professional translator for an Icelandic municipal elections website.
Translate the given Icelandic strings accurately and naturally into {lang}.

Rules:
- Keep proper nouns (people's names, Icelandic place names like Reykjavík, Kópavogur etc.) in Icelandic.
- Keep party abbreviations as-is.
- Return ONLY a valid JSON object mapping each key to its translation.
- No markdown, no explanations, just the JSON.
"""


def get_api_key():
    if len(sys.argv) > 1 and sys.argv[1].startswith('sk-'):
        return sys.argv[1]
    key = os.environ.get('OPENAI_API_KEY', '')
    if key:
        return key
    raise RuntimeError("No API key found.")


def load_json(path):
    if path.exists():
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def translate_batch(client, batch: dict, lang: str) -> dict:
    prompt = SYSTEM_PROMPT.replace('{lang}', LANG_NAMES[lang])
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {'role': 'system', 'content': prompt},
                    {'role': 'user',   'content': json.dumps(batch, ensure_ascii=False)},
                ],
                temperature=0.2,
                response_format={'type': 'json_object'},
            )
            return json.loads(resp.choices[0].message.content)
        except Exception as e:
            print(f"  Error (attempt {attempt+1}): {e}")
            time.sleep(4 ** attempt)
    return batch  # fallback to Icelandic


def rebuild_overlay(strings: dict, lang: str, path: Path):
    """Rewrite the overlay JS file from the strings dict."""
    lang_upper = lang.upper()
    occ = strings.get('_occupations', {})
    main = {k: v for k, v in strings.items()
            if k != '_occupations' and isinstance(v, str)}

    lines = [
        '// AUTO-GENERATED — do not edit manually.',
        '// Source: translations/strings_is.json',
        '// Regenerate: python scripts/i18n_translate_bulk.py',
        '',
        f'export const TRANSLATIONS_{lang_upper} = {{',
    ]
    for key in sorted(main):
        val = (main[key] or '').replace('\\', '\\\\').replace('"', '\\"')
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

    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def main():
    api_key = get_api_key()
    client  = OpenAI(api_key=api_key)

    pending = load_json(PENDING)
    if not pending:
        print("Nothing pending. No changes to translate.")
        return

    # Flatten all pending entries (all dates)
    all_entries = []
    for day_entries in pending.values():
        all_entries.extend(day_entries)

    # Filter to untranslated
    to_translate = [e for e in all_entries if e.get('en') is None or e.get('pl') is None]
    if not to_translate:
        print("All pending entries already translated.")
        return

    print(f"Found {len(to_translate)} pending strings to translate.")

    for lang in ['en', 'pl']:
        strings_path   = STRINGS_EN if lang == 'en' else STRINGS_PL
        overlay_path   = OVERLAY_EN if lang == 'en' else OVERLAY_PL
        existing       = load_json(strings_path)

        need = [e for e in to_translate if e.get(lang) is None]
        print(f"\nTranslating {len(need)} strings to {LANG_NAMES[lang]}...")

        keys = [e['key'] for e in need]
        vals = [e['is']  for e in need]

        for i in range(0, len(keys), BATCH_SIZE):
            chunk_keys = keys[i:i+BATCH_SIZE]
            chunk_vals = vals[i:i+BATCH_SIZE]
            batch      = dict(zip(chunk_keys, chunk_vals))
            translated = translate_batch(client, batch, lang)

            # Merge into existing strings
            for k, v in translated.items():
                if k.startswith('_occ:'):
                    occ_is = k[5:]
                    existing.setdefault('_occupations', {})[occ_is] = v
                else:
                    existing[k] = v

            # Mark entries as done
            for e in need:
                if e['key'] in translated:
                    e[lang] = translated[e['key']]

            print(f"  [{min(i+BATCH_SIZE, len(keys))}/{len(keys)}]")
            save_json(strings_path, existing)

        rebuild_overlay(existing, lang, overlay_path)
        print(f"  Overlay updated -> {overlay_path}")

    # Save updated pending (with translations filled in)
    save_json(PENDING, pending)

    # Clear fully-translated entries
    cleaned = {}
    for day, entries in pending.items():
        remaining = [e for e in entries if e.get('en') is None or e.get('pl') is None]
        if remaining:
            cleaned[day] = remaining
    save_json(PENDING, cleaned)

    print("\nDone. Pending file cleared.")


if __name__ == '__main__':
    main()
