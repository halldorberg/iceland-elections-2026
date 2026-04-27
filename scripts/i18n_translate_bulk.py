"""
i18n_translate_bulk.py
──────────────────────
Translates translations/strings_is.json → strings_en.json + strings_pl.json
using OpenAI, then writes the JS overlay files.

Usage:
  OPENAI_API_KEY=sk-... python scripts/i18n_translate_bulk.py

Or pass key as argument:
  python scripts/i18n_translate_bulk.py sk-proj-...

Options (edit below):
  MODEL      = which OpenAI model to use
  BATCH_SIZE = strings per API call
  RESUME     = skip already-translated keys (True = safe to restart)
"""

import os, sys, json, time, re
from pathlib import Path
from openai import OpenAI

# ── Config ────────────────────────────────────────────────────────────────────
MODEL       = 'gpt-5.4'
BATCH_SIZE  = 40      # strings per API call
RESUME      = True    # skip keys already translated
LANGS       = ['en', 'pl']

ROOT        = Path(__file__).parent.parent
STRINGS_IS  = ROOT / 'translations' / 'strings_is.json'
STRINGS_EN  = ROOT / 'translations' / 'strings_en.json'
STRINGS_PL  = ROOT / 'translations' / 'strings_pl.json'
OVERLAY_EN  = ROOT / 'js' / 'data' / 'candidates.en.js'
OVERLAY_PL  = ROOT / 'js' / 'data' / 'candidates.pl.js'

SYSTEM_PROMPT = """\
You are a professional translator for an Icelandic municipal elections website.
Translate the given Icelandic strings accurately and naturally into {lang}.

Rules:
- Keep proper nouns (people's names, place names like Reykjavík, Kópavogur, Akureyri, Hafnarfjörður, etc.) in their original Icelandic form — do NOT translate them.
- Keep party abbreviations (D, B, S, V, P, etc.) as-is.
- For English: use natural British/American English suitable for a civic/political context.
- For Polish: use natural Polish with correct grammar and diacritics.
- Return ONLY a valid JSON object with the same keys, values replaced by translations.
- Do not add explanations, markdown, or any text outside the JSON object.
"""

LANG_NAMES = {'en': 'English', 'pl': 'Polish'}


def get_api_key():
    if len(sys.argv) > 1 and sys.argv[1].startswith('sk-'):
        return sys.argv[1]
    key = os.environ.get('OPENAI_API_KEY', '')
    if key:
        return key
    raise RuntimeError("No API key found. Pass as argument or set OPENAI_API_KEY env var.")


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
    """Send one batch to OpenAI, return {key: translated_string}."""
    prompt = SYSTEM_PROMPT.replace('{lang}', LANG_NAMES[lang])
    payload = json.dumps(batch, ensure_ascii=False)

    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {'role': 'system', 'content': prompt},
                    {'role': 'user',   'content': payload},
                ],
                temperature=0.2,
                response_format={'type': 'json_object'},
            )
            result = json.loads(resp.choices[0].message.content)
            # Validate all keys came back
            missing = [k for k in batch if k not in result]
            if missing:
                print(f"    WARNING: {len(missing)} keys missing from response, retrying...")
                time.sleep(2)
                continue
            return result
        except Exception as e:
            print(f"    Error (attempt {attempt+1}): {e}")
            time.sleep(4 ** attempt)
    # Fallback: return Icelandic on failure
    print(f"    FAILED batch, keeping Icelandic as fallback")
    return batch


def run_translation(client, source: dict, existing: dict, lang: str) -> dict:
    """Translate all keys in source that are not already in existing."""
    result = dict(existing)

    # Separate occupations from main strings
    occupations_is = source.get('_occupations', {})
    main_strings   = {k: v for k, v in source.items()
                      if k != '_occupations' and v and isinstance(v, str)}

    # ── Phase 1: Occupations (deduped lookup) ──────────────────────────────
    occ_todo = {k: k for k in occupations_is if k not in result.get('_occupations', {})}
    if occ_todo:
        print(f"  Translating {len(occ_todo)} unique occupations...")
        occ_result = result.get('_occupations', {})
        keys = list(occ_todo.keys())
        for i in range(0, len(keys), BATCH_SIZE):
            chunk = {k: k for k in keys[i:i+BATCH_SIZE]}
            translated = translate_batch(client, chunk, lang)
            occ_result.update(translated)
            print(f"    occupations {i+1}–{min(i+BATCH_SIZE, len(keys))} / {len(keys)}")
        result['_occupations'] = occ_result
    else:
        print(f"  Occupations already translated, skipping.")

    # ── Phase 2: Main strings ──────────────────────────────────────────────
    todo = {k: v for k, v in main_strings.items() if k not in result}

    if not todo:
        print(f"  All {len(main_strings)} strings already translated, skipping.")
        return result

    print(f"  Translating {len(todo)} strings in batches of {BATCH_SIZE}...")
    keys  = list(todo.keys())
    total = len(keys)

    for i in range(0, total, BATCH_SIZE):
        chunk_keys = keys[i:i+BATCH_SIZE]
        chunk      = {k: todo[k] for k in chunk_keys}
        translated = translate_batch(client, chunk, lang)
        result.update(translated)

        done = min(i + BATCH_SIZE, total)
        pct  = done / total * 100
        print(f"    [{done:4d}/{total}] {pct:5.1f}%  — last key: {chunk_keys[-1][:50]}")

        # Save progress after every batch (safe to resume)
        save_json(STRINGS_EN if lang == 'en' else STRINGS_PL, result)

    return result


def write_overlay(data: dict, lang: str, path: Path):
    """Write js/data/candidates.{lang}.js from translated data."""
    lang_upper = lang.upper()
    lines = [
        f'// AUTO-GENERATED — do not edit manually.',
        f'// Source: translations/strings_is.json',
        f'// Regenerate: python scripts/i18n_translate_bulk.py',
        f'',
        f'export const TRANSLATIONS_{lang_upper} = {{',
    ]

    occ = data.get('_occupations', {})
    main = {k: v for k, v in data.items()
            if k != '_occupations' and isinstance(v, str)}

    for key in sorted(main):
        val = main[key].replace('\\', '\\\\').replace('"', '\\"')
        lines.append(f'  "{key}": "{val}",')

    # Append occupation lookup
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

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"  Overlay written -> {path}")


def main():
    api_key = get_api_key()
    client  = OpenAI(api_key=api_key)

    source = load_json(STRINGS_IS)
    if not source:
        print("strings_is.json not found. Run i18n_extract.py first.")
        sys.exit(1)

    print(f"Loaded {len(source)} keys from strings_is.json")
    print(f"Model: {MODEL}  |  Batch size: {BATCH_SIZE}  |  Resume: {RESUME}")
    print()

    for lang, out_path, overlay_path in [
        ('en', STRINGS_EN, OVERLAY_EN),
        ('pl', STRINGS_PL, OVERLAY_PL),
    ]:
        print(f"{'='*60}")
        print(f"Translating to {LANG_NAMES[lang]}...")
        existing = load_json(out_path) if RESUME else {}
        result   = run_translation(client, source, existing, lang)
        save_json(out_path, result)
        write_overlay(result, lang, overlay_path)
        print()

    print("Done! Overlay files written:")
    print(f"  {OVERLAY_EN}")
    print(f"  {OVERLAY_PL}")


if __name__ == '__main__':
    main()
