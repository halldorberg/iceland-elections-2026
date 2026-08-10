import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
src = open(r'F:\Claude Projects\iceland-elections\js\data\candidates.js', encoding='utf-8').read()

checks = [
    ('FJB.D.11', 'Why is it necessary to name his co-teachers?'),
    ('GRN.M.2', 'This should just be null'),
    ('HFJ.HFJK.5', 'En er heimild fyrir titlinu sérfræðingur?'),
    ('MOS.D.8', 'No accident in sources, but racing interest should be included'),
    ('RVK.C.20', 'Many unsourced statements but no rewrite — needs rewrite'),
    ('RVK.S.37', 'Drop "landssamtök heyrnarskertra stofnuð 1937" detail'),
    ('SNB.B.1', 'Find sources for occupation/details in the original bio'),
    ('SNB.B.2', 'Find sources for occupation/details in the original bio'),
    ('SNB.D.1', 'Find sources for occupation/details in the original bio'),
    ('SNB.S.1', 'Find sources for golf interest'),
    ('VOG.D.13', 'Education was not specifically pest control; mention electrician + flying + skipper instead'),
]

def find_row(src, const, party, ballot):
    m = re.search(r'^const ' + const + r' = \{', src, re.M)
    if not m: return None
    start = m.end()
    pm = re.search(r'\n  ' + party + r'\s*:\s*\{', src[start:])
    if not pm: return None
    ps = start + pm.end()
    rm = re.search(r'\n      \[' + str(ballot) + r'\s*,', src[ps:])
    if not rm: return None
    pos = ps + rm.start()
    bracket_pos = src.find('[', pos)
    depth = 0
    i = bracket_pos
    n = len(src)
    while i < n:
        c = src[i]
        if c in ("'", '"'):
            q = c; i += 1
            while i < n:
                if src[i] == '\\':
                    i += 2; continue
                if src[i] == q:
                    i += 1; break
                i += 1
            continue
        if c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                return src[bracket_pos:i+1]
        i += 1
    return None

for aid, comment in checks:
    parts = aid.split('.')
    const, party, ballot_s = parts[0], parts[1], parts[2]
    row = find_row(src, const, party, int(ballot_s))
    if not row:
        print(f'== {aid} ==  ROW NOT FOUND')
        continue
    bm = re.search(r"bio: '((?:[^'\\]|\\.)*)'", row)
    bio = bm.group(1) if bm else None
    hm = re.search(r"heimild: \[((?:[^\[\]]|\[[^\]]*\])*)\]", row)
    heimild = hm.group(1) if hm else None
    print(f'== {aid} == comment: {comment}')
    print(f'  bio: {(bio[:300] if bio else "NULL")}')
    if bio and len(bio) > 300:
        print(f'       ...{bio[-100:]}')
    print(f'  heimild: {(heimild[:200] if heimild else "NONE")}')
    print()
