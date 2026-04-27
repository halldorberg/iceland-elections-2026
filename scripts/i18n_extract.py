"""
i18n_extract.py
───────────────
Parses candidates.js and extracts every translatable string into
translations/strings_is.json.

Output structure:
{
  "reykjavik.D.tagline": "Breytinga er þörf...",
  "reykjavik.D.agenda.0.title": "Húsnæði",
  "reykjavik.D.agenda.0.text": "...",
  "reykjavik.D.list.1.occupation": "Borgarstjóri",
  "reykjavik.D.list.1.bio": "...",
  "reykjavik.D.list.1.interests.0": "...",
  ...
  "_occupations": { "Kennari": null, "Bóndi": null, ... }  ← deduped lookup
}

Keys use ballot number (not array index) for candidates so they are stable
even if the list is reordered.
"""

import re, json, os

ROOT = os.path.join(os.path.dirname(__file__), '..')
CANDIDATES_JS  = os.path.join(ROOT, 'js', 'data', 'candidates.js')
OUT_JSON       = os.path.join(ROOT, 'translations', 'strings_is.json')

# ── Regexes ──────────────────────────────────────────────────────────────────

MUNI_CONST_RE  = re.compile(r'^const ([A-Z][A-Z0-9_]*)\s*=\s*\{')
REAL_DATA_RE   = re.compile(r'const REAL_DATA\s*=\s*\{([^}]+)\}')
PARTY_RE       = re.compile(r"^\s{2}([A-Z0-9]+):\s*\{")
TAGLINE_RE     = re.compile(r"^\s+tagline:\s*'((?:[^'\\]|\\.)+)'")
AGENDA_START   = re.compile(r'^\s+agenda:\s*\[')
AGENDA_END     = re.compile(r'^\s{4}\],?\s*$')
AGENDA_ITEM_RE = re.compile(r"^\s+\{\s*icon:\s*'[^']*',\s*title:\s*'((?:[^'\\]|\\.)+)',\s*text:\s*'((?:[^'\\]|\\.)+)'")
LIST_START_RE  = re.compile(r'^\s+list:\s*\[')
LIST_END_RE    = re.compile(r'^    \],?\s*$')
CAND_TUPLE_RE  = re.compile(r"^\s{6,8}\[(\d+),\s*'([^']+)',\s*'((?:[^'\\]|\\.)+)'")
OBJ_START_RE   = re.compile(r'^\s+\{$')
OBJ_INNER_RE   = re.compile(r'^\s+\{')   # opening { in same line as tuple
BIO_RE         = re.compile(r"^\s+bio:\s*'((?:[^'\\]|\\.)*)'")
INT_START_RE   = re.compile(r"^\s+interests:\s*\[")
INT_ITEM_RE    = re.compile(r"^\s+'((?:[^'\\]|\\.)+)'")
INT_END_RE     = re.compile(r"^\s+\],?\s*$")


def unescape(s):
    return s.replace("\\'", "'").replace('\\"', '"').replace('\\\\', '\\')


def build_var_to_muni(content):
    """Return {'RVK': 'reykjavik', 'KOP': 'kopavogur', ...}"""
    m = REAL_DATA_RE.search(content)
    if not m:
        raise RuntimeError("REAL_DATA mapping not found in candidates.js")
    mapping = {}
    for pair in re.finditer(r'(\w+):\s*([A-Z][A-Z0-9_]*)', m.group(1)):
        muni_id, var_name = pair.group(1), pair.group(2)
        mapping[var_name] = muni_id
    return mapping


def extract(content):
    var_to_muni = build_var_to_muni(content)
    strings = {}          # key → Icelandic string
    all_occupations = {}  # occupation string → None (deduped)

    lines = content.splitlines()

    current_var   = None
    current_muni  = None
    current_party = None

    in_agenda      = False
    agenda_idx     = 0
    in_list        = False
    in_cand_obj    = False
    in_interests   = False
    cand_ballot    = None
    cand_occ       = None
    interest_idx   = 0
    obj_depth      = 0   # bracket depth when inside a candidate object

    for line in lines:

        # ── Municipality const ──────────────────────────────────────────
        m = MUNI_CONST_RE.match(line)
        if m:
            var = m.group(1)
            current_var   = var
            current_muni  = var_to_muni.get(var)
            current_party = None
            in_agenda = in_list = in_cand_obj = in_interests = False
            continue

        if current_muni is None:
            continue

        # ── Party block ─────────────────────────────────────────────────
        m = PARTY_RE.match(line)
        if m and not in_list and not in_agenda:
            current_party = m.group(1)
            in_agenda = in_list = in_cand_obj = in_interests = False
            agenda_idx = 0
            continue

        if current_party is None:
            continue

        pfx = f"{current_muni}.{current_party}"

        # ── Tagline ─────────────────────────────────────────────────────
        m = TAGLINE_RE.match(line)
        if m and not in_list and not in_agenda:
            strings[f"{pfx}.tagline"] = unescape(m.group(1))
            continue

        # ── Agenda section ───────────────────────────────────────────────
        if not in_list and AGENDA_START.match(line):
            in_agenda  = True
            agenda_idx = 0
            continue

        if in_agenda:
            if AGENDA_END.match(line):
                in_agenda = False
                continue
            m = AGENDA_ITEM_RE.match(line)
            if m:
                strings[f"{pfx}.agenda.{agenda_idx}.title"] = unescape(m.group(1))
                strings[f"{pfx}.agenda.{agenda_idx}.text"]  = unescape(m.group(2))
                agenda_idx += 1
            continue

        # ── List section ─────────────────────────────────────────────────
        if LIST_START_RE.match(line):
            in_list        = True
            in_cand_obj    = False
            in_interests   = False
            cand_ballot    = None
            continue

        if not in_list:
            continue

        if LIST_END_RE.match(line) and not in_cand_obj:
            in_list = False
            continue

        # ── Inside candidate object ──────────────────────────────────────
        if in_cand_obj:
            # Track depth to know when the object closes
            obj_depth += line.count('{') - line.count('}')

            if obj_depth <= 0:
                in_cand_obj = False
                in_interests = False
                cand_ballot = None
                continue

            # Interests array
            if in_interests:
                if INT_END_RE.match(line) and 'interests' not in line:
                    in_interests = False
                    continue
                m = INT_ITEM_RE.match(line)
                if m:
                    val = unescape(m.group(1))
                    strings[f"{pfx}.list.{cand_ballot}.interests.{interest_idx}"] = val
                    interest_idx += 1
                continue

            if INT_START_RE.match(line):
                in_interests = True
                interest_idx = 0
                # Handle inline: interests: ['a', 'b']  (rare but possible)
                items = re.findall(r"'((?:[^'\\]|\\.)+)'", line.split('[', 1)[-1])
                if items and ']' in line:
                    for i, v in enumerate(items):
                        strings[f"{pfx}.list.{cand_ballot}.interests.{i}"] = unescape(v)
                    in_interests = False
                    interest_idx = len(items)
                continue

            m = BIO_RE.match(line)
            if m:
                bio = unescape(m.group(1))
                if bio:
                    strings[f"{pfx}.list.{cand_ballot}.bio"] = bio
                continue

            continue

        # ── Candidate tuple start ────────────────────────────────────────
        m = CAND_TUPLE_RE.match(line)
        if m:
            cand_ballot = int(m.group(1))
            occ         = unescape(m.group(3))
            cand_occ    = occ
            # Record occupation for deduplication
            if occ and occ != 'Frambjóðandi':
                all_occupations[occ] = None
            else:
                all_occupations[occ] = None
            strings[f"{pfx}.list.{cand_ballot}.occupation"] = occ

            # Does the object start on this same line?
            rest = line[m.end():]
            if '{' in rest:
                in_cand_obj  = True
                in_interests = False
                interest_idx = 0
                obj_depth    = rest.count('{') - rest.count('}')
            continue

    return strings, all_occupations


def main():
    with open(CANDIDATES_JS, encoding='utf-8') as f:
        content = f.read()

    strings, occupations = extract(content)

    # Store occupations as a separate lookup table
    result = dict(strings)
    result['_occupations'] = {k: None for k in sorted(occupations)}

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Stats
    taglines   = sum(1 for k in strings if k.endswith('.tagline'))
    agenda_t   = sum(1 for k in strings if '.agenda.' in k and k.endswith('.title'))
    agenda_x   = sum(1 for k in strings if '.agenda.' in k and k.endswith('.text'))
    bios       = sum(1 for k in strings if k.endswith('.bio'))
    interests  = sum(1 for k in strings if '.interests.' in k)
    occs       = len(occupations)
    total      = len(strings)

    print(f"Extracted {total:,} translatable strings:")
    print(f"  Taglines:        {taglines:4d}")
    print(f"  Agenda titles:   {agenda_t:4d}")
    print(f"  Agenda texts:    {agenda_x:4d}")
    print(f"  Bios:            {bios:4d}")
    print(f"  Interest items:  {interests:4d}")
    print(f"  Occupations:     {occs:4d}  (unique — deduplicated)")
    print(f"Written -> {OUT_JSON}")


if __name__ == '__main__':
    main()
