import json, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

data = json.load(open('scan_results/ruv_bios.json', encoding='utf-8'))
src = open('js/data/candidates.js', encoding='utf-8').read()

samples = 0
for e in data:
    if not e.get('ruv_id'):
        continue
    if samples >= 5:
        break
    muni, party, ballot, name = e['muni_const'], e['party_code'], e['ballot'], e['name']
    name_escaped = re.escape(name)
    m = re.search(r'\n\s+\[\s*' + str(ballot) + r"\s*,\s*'" + name_escaped + r"'", src)
    if not m:
        continue
    start = src.find('[', m.start())
    i = start
    depth = 0
    in_str = None
    while i < len(src):
        c = src[i]
        if in_str:
            if c == '\\':
                i += 2
                continue
            if c == in_str:
                in_str = None
            i += 1
            continue
        if c in ("'", '"', '`'):
            in_str = c
            i += 1
            continue
        if c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                break
        i += 1
    row = src[start:i + 1]

    print(f'{muni}.{party}.{ballot} ({name}):')
    h_m = re.search(r"heimild:\s*(\[[^\]]*\]|null)", row)
    print(f'  heimild: {h_m.group(1)[:120] if h_m else "MISSING/null"}')
    bio_m = re.search(r"bio:\s*'((?:[^'\\]|\\.)*)'", row)
    if bio_m:
        bio = bio_m.group(1)
        print(f'  bio length: {len(bio)}')
        print(f'  bio has paragraph breaks (\\n\\n): {chr(92)+chr(110)+chr(92)+chr(110) in bio}')
    print()
    samples += 1
