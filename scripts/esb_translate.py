# coding: utf-8
"""Translate translations/esb_is.json → esb_en.json + esb_pl.json via OpenAI.
Usage: python scripts/esb_translate.py   (key from OPENAI_API_KEY or argv[1])
Resume-safe: already-translated keys are skipped."""
import os, sys, json, time
from pathlib import Path
from openai import OpenAI

MODEL = 'gpt-5.4'
BATCH_SIZE = 20
LANGS = ['en', 'pl']

ROOT = Path(__file__).parent.parent
SRC = ROOT / 'translations' / 'esb_is.json'

SYSTEM_PROMPT = """\
You are a professional translator for an Icelandic civic-information website about the 2026
national referendum on resuming EU accession talks.
Translate the given Icelandic strings accurately and naturally into {lang}.

Rules:
- Keep proper nouns (people's names, party/movement names like Heimssýn, Evrópuhreyfingin,
  media names like Vísir, Morgunblaðið) in their original form — do NOT translate them.
- Political terms: JÁ/NEI sides may be rendered YES/NO in English, TAK/NIE in Polish.
- Preserve any quotes and factual numbers exactly.
- For English: natural English for a civic/political context.
- For Polish: natural Polish with correct grammar and diacritics.
- Return ONLY a valid JSON object with the same keys, values replaced by translations.
"""

LANG_NAMES = {'en': 'English', 'pl': 'Polish'}


def get_api_key():
    if len(sys.argv) > 1 and sys.argv[1].startswith('sk-'):
        return sys.argv[1]
    key = os.environ.get('OPENAI_API_KEY', '')
    if key:
        return key
    raise RuntimeError('No API key: set OPENAI_API_KEY or pass as argument.')


def load(path):
    if path.exists():
        return json.load(open(path, encoding='utf-8'))
    return {}


def save(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


def translate_batch(client, batch, lang):
    """Translate one batch; on failure bisect so one bad string can't block the rest."""
    prompt = SYSTEM_PROMPT.replace('{lang}', LANG_NAMES[lang])
    payload = json.dumps(batch, ensure_ascii=False)
    for attempt in range(2):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[{'role': 'system', 'content': prompt},
                          {'role': 'user', 'content': payload}],
                response_format={'type': 'json_object'},
                timeout=90,
            )
            result = json.loads(resp.choices[0].message.content)
            if set(result.keys()) == set(batch.keys()):
                return result
            print(f'  key mismatch (attempt {attempt+1})', flush=True)
        except Exception as e:
            print(f'  error: {type(e).__name__}: {str(e)[:120]} (attempt {attempt+1})', flush=True)
            time.sleep(3)
    keys = list(batch.keys())
    if len(keys) == 1:
        print(f'  SKIPPING unresolvable key: {keys[0]}', flush=True)
        return {}
    mid = len(keys) // 2
    print(f'  bisecting {len(keys)} → {mid} + {len(keys)-mid}', flush=True)
    out = {}
    out.update(translate_batch(client, {k: batch[k] for k in keys[:mid]}, lang))
    out.update(translate_batch(client, {k: batch[k] for k in keys[mid:]}, lang))
    return out


def main():
    client = OpenAI(api_key=get_api_key(), timeout=120.0, max_retries=2)
    strings = load(SRC)
    for lang in LANGS:
        out_path = ROOT / 'translations' / f'esb_{lang}.json'
        done = load(out_path)
        todo = {k: v for k, v in strings.items() if k not in done}
        print(f'[{lang}] {len(todo)} strings to translate ({len(done)} already done)')
        keys = list(todo.keys())
        for i in range(0, len(keys), BATCH_SIZE):
            batch = {k: todo[k] for k in keys[i:i+BATCH_SIZE]}
            result = translate_batch(client, batch, lang)
            done.update(result)
            save(out_path, done)
            print(f'[{lang}] {len(done)}/{len(strings)}')
    print('All done')


if __name__ == '__main__':
    main()
