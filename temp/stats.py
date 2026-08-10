"""Compute current site-wide coverage statistics."""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

src = open('js/data/candidates.js', encoding='utf-8').read()


def find_const_block(s, name):
    m = re.search(r'^const ' + re.escape(name) + r'\s*=\s*\{', s, re.M)
    if not m:
        return None
    op = m.end() - 1
    depth = 0
    i = op
    in_str = None
    while i < len(s):
        c = s[i]
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
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return op + 1, i
        i += 1


real_data_m = re.search(r"const REAL_DATA\s*=\s*\{([^}]+)\}", src)
munis = [pm.group(2) for pm in re.finditer(r'(\w+):\s*([A-Z][A-Z0-9_]*)', real_data_m.group(1))]

total_lists = 0
lists_with_agenda = 0
total_candidates = 0
candidates_with_bio = 0
candidates_with_photo = 0

for muni in munis:
    rng = find_const_block(src, muni)
    if not rng:
        continue
    cs, ce = rng
    body = src[cs:ce]
    # Find each party block
    for pm in re.finditer(r'\n  ([A-Z][A-Z0-9]*)\s*:\s*\{', body):
        # walk party block
        i = pm.end() - 1
        depth = 0
        in_str = None
        while i < len(body):
            c = body[i]
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
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        ptext = body[pm.end() - 1:i + 1]
        if 'list:' not in ptext:
            continue
        total_lists += 1
        # Agenda? Look for `agenda: [` followed by at least one `icon:`
        ag_m = re.search(r'agenda:\s*\[(.*?)\]\s*,?\s*(?:platformUrl|list|tagline|//)', ptext, re.S)
        if ag_m and 'icon:' in ag_m.group(1):
            lists_with_agenda += 1

        # Walk list: [ ... ] for candidate rows
        list_m = re.search(r'list:\s*\[', ptext)
        if not list_m:
            continue
        ls = list_m.end() - 1
        i2 = ls
        depth2 = 0
        in_str2 = None
        while i2 < len(ptext):
            c = ptext[i2]
            if in_str2:
                if c == '\\':
                    i2 += 2
                    continue
                if c == in_str2:
                    in_str2 = None
                i2 += 1
                continue
            if c in ("'", '"', '`'):
                in_str2 = c
                i2 += 1
                continue
            if c == '[':
                depth2 += 1
            elif c == ']':
                depth2 -= 1
                if depth2 == 0:
                    break
            i2 += 1
        list_body = ptext[ls + 1:i2]

        # Find each row [N, ...]
        j = 0
        while j < len(list_body):
            rm = re.search(r'\n\s+\[\s*(\d+)\s*,', list_body[j:])
            if not rm:
                break
            bracket_pos = list_body.find('[', j + rm.start())
            k = bracket_pos
            rdepth = 0
            rinstr = None
            while k < len(list_body):
                c = list_body[k]
                if rinstr:
                    if c == '\\':
                        k += 2
                        continue
                    if c == rinstr:
                        rinstr = None
                    k += 1
                    continue
                if c in ("'", '"', '`'):
                    rinstr = c
                    k += 1
                    continue
                if c == '[':
                    rdepth += 1
                elif c == ']':
                    rdepth -= 1
                    if rdepth == 0:
                        break
                k += 1
            row = list_body[bracket_pos:k + 1]
            total_candidates += 1
            # Has photo? `images/candidates/...`
            if re.search(r"'images/candidates/[^']+\.(?:jpg|jpeg|png|webp|avif)'", row):
                candidates_with_photo += 1
            # Has bio? Look for `bio: '` (non-null)
            if re.search(r"bio:\s*'(?:[^'\\]|\\.)+?'", row):
                candidates_with_bio += 1
            j = k + 1

pct = lambda n, d: f'{100*n/d:.1f}%' if d else 'n/a'
print('═══════════════════════════════════════')
print('SITE COVERAGE — current state on master')
print('═══════════════════════════════════════')
print()
print(f'  Lists with agenda:        {lists_with_agenda:>5} / {total_lists}   ({pct(lists_with_agenda, total_lists)})')
print(f'  Candidates with bio:      {candidates_with_bio:>5} / {total_candidates}  ({pct(candidates_with_bio, total_candidates)})')
print(f'  Candidates with photo:    {candidates_with_photo:>5} / {total_candidates}  ({pct(candidates_with_photo, total_candidates)})')
print()
print(f'  Total candidates:         {total_candidates}')
print(f'  Total lists:              {total_lists}')
print(f'  Total municipalities:     {len(munis)}')
